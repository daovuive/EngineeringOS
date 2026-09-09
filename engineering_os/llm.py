from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMError(RuntimeError):
    """Raised when a local LLM runtime cannot satisfy a request."""


EMBEDDING_CONTRACT_VERSION = "1.0"


class LLMRuntime(Protocol):
    id: str

    def list_models(self) -> list[str]:
        """Return model names available in the runtime."""

    def generate(
        self,
        prompt: str,
        *,
        role: str = "chat",
        max_tokens: int | None = None,
    ) -> str:
        """Generate text using a configured model role."""

    def embed(self, text: str) -> list[float]:
        """Create one embedding vector using the configured embedding model."""

    def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        role: str = "reasoning",
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """Generate a JSON object constrained by a supplied schema."""


@dataclass(frozen=True)
class ProviderDefinition:
    id: str
    type: str
    host: str
    timeout: int
    max_concurrent_requests: int | None = None


@dataclass(frozen=True)
class RuntimeOptions:
    temperature: float | None = None
    top_p: float | None = None
    max_tokens: int | None = None
    stream: bool = False

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> RuntimeOptions:
        options = config.get("options", {})
        if not isinstance(options, dict):
            raise LLMError("Runtime config 'options' must be an object.")

        return cls(
            temperature=_optional_number(options, "temperature"),
            top_p=_optional_number(options, "topP"),
            max_tokens=_optional_int(options, "maxTokens"),
            stream=_optional_bool(options, "stream") or False,
        )


@dataclass(frozen=True)
class ModelBinding:
    provider: str
    model: str
    dimensions: int | None = None


@dataclass(frozen=True)
class RuntimeDefinition:
    provider: ProviderDefinition
    models: dict[str, ModelBinding]
    options: RuntimeOptions

    def model_for(self, role: str) -> str:
        binding = self.models.get(role)
        if binding is None:
            raise LLMError(f"Model role '{role}' is not configured.")
        return binding.model


class OllamaRuntime:
    def __init__(
        self,
        definition: RuntimeDefinition,
        *,
        http_client: OllamaHttpClient | None = None,
    ) -> None:
        self.id = definition.provider.id
        self.definition = definition
        self._http = http_client or OllamaHttpClient(definition.provider)

    def list_models(self) -> list[str]:
        payload = self._http.request_json("GET", "/api/tags")
        models = payload.get("models", [])
        if not isinstance(models, list):
            return []

        names = []
        for model in models:
            if isinstance(model, dict) and isinstance(model.get("name"), str):
                names.append(model["name"])
        return names

    def generate(
        self,
        prompt: str,
        *,
        role: str = "chat",
        max_tokens: int | None = None,
    ) -> str:
        if max_tokens is not None and (
            not isinstance(max_tokens, int)
            or isinstance(max_tokens, bool)
            or max_tokens < 1
        ):
            raise LLMError("Generation max_tokens must be a positive integer.")
        payload = {
            "model": self.definition.model_for(role),
            "prompt": prompt,
            "stream": self.definition.options.stream,
        }
        options = _to_ollama_options(self.definition.options)
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if options:
            payload["options"] = options

        if self.definition.options.stream:
            return self._generate_stream(payload)

        response = self._http.request_json("POST", "/api/generate", payload).get("response")
        if not isinstance(response, str):
            raise LLMError("Ollama response did not include text output.")
        return response

    def generate_structured(
        self,
        prompt: str,
        schema: dict[str, Any],
        *,
        role: str = "reasoning",
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        if not isinstance(schema, dict) or not schema:
            raise LLMError("Structured generation requires a JSON schema.")
        if max_tokens is not None and (
            not isinstance(max_tokens, int)
            or isinstance(max_tokens, bool)
            or max_tokens < 1
        ):
            raise LLMError("Generation max_tokens must be a positive integer.")
        payload: dict[str, Any] = {
            "model": self.definition.model_for(role),
            "prompt": prompt,
            "stream": self.definition.options.stream,
            "format": schema,
        }
        options = _to_ollama_options(self.definition.options)
        if max_tokens is not None:
            options["num_predict"] = max_tokens
        if options:
            payload["options"] = options

        if self.definition.options.stream:
            raw = self._generate_stream(payload)
        else:
            response = self._http.request_json("POST", "/api/generate", payload).get(
                "response"
            )
            if not isinstance(response, str):
                raise LLMError("Ollama response did not include text output.")
            raw = response
        try:
            result = json.loads(raw)
        except json.JSONDecodeError as error:
            raise LLMError("Ollama returned invalid structured JSON.") from error
        if not isinstance(result, dict):
            raise LLMError("Ollama structured response was not a JSON object.")
        return result

    def embed(self, text: str) -> list[float]:
        payload = self._http.request_json(
            "POST",
            "/api/embed",
            {
                "model": self.definition.model_for("embedding"),
                "input": text,
            },
        )

        embeddings = payload.get("embeddings")
        if (
            isinstance(embeddings, list)
            and embeddings
            and isinstance(embeddings[0], list)
        ):
            return self._validate_embedding_dimensions(_coerce_embedding(embeddings[0]))

        embedding = payload.get("embedding")
        if isinstance(embedding, list):
            return self._validate_embedding_dimensions(_coerce_embedding(embedding))

        raise LLMError("Ollama response did not include an embedding vector.")

    def _validate_embedding_dimensions(self, embedding: list[float]) -> list[float]:
        expected = self.definition.models.get("embedding")
        if expected is not None and expected.dimensions is not None:
            if len(embedding) != expected.dimensions:
                raise LLMError(
                    "Embedding dimensions do not match configuration: "
                    f"expected {expected.dimensions}, got {len(embedding)}."
                )
        return embedding

    def _generate_stream(self, payload: dict[str, Any]) -> str:
        output = []
        for chunk in self._http.request_json_lines("POST", "/api/generate", payload):
            response = chunk.get("response")
            if isinstance(response, str):
                output.append(response)
        return "".join(output)


class OllamaHttpClient:
    def __init__(self, provider: ProviderDefinition) -> None:
        self.provider = provider

    def request_json(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        raw = self._request(method, path, data)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as error:
            raise LLMError("Ollama returned invalid JSON.") from error

        if not isinstance(payload, dict):
            raise LLMError("Ollama returned an unexpected response shape.")
        return payload

    def request_json_lines(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        raw = self._request(method, path, data)
        payloads = []
        for line in raw.splitlines():
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as error:
                raise LLMError("Ollama returned invalid streaming JSON.") from error
            if not isinstance(payload, dict):
                raise LLMError("Ollama returned an unexpected streaming response shape.")
            payloads.append(payload)
        return payloads

    def _request(
        self,
        method: str,
        path: str,
        data: dict[str, Any] | None,
    ) -> str:
        body = None
        headers = {"Accept": "application/json"}

        if data is not None:
            body = json.dumps(data).encode("utf-8")
            headers["Content-Type"] = "application/json"

        request = Request(
            f"{self.provider.host}{path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=self.provider.timeout) as response:
                return response.read().decode("utf-8")
        except HTTPError as error:
            raise LLMError(f"Ollama request failed with HTTP {error.code}.") from error
        except URLError as error:
            raise LLMError(
                f"Cannot connect to Ollama at {self.provider.host}: {error.reason}"
            ) from error
        except TimeoutError as error:
            raise LLMError(f"Ollama request timed out after {self.provider.timeout}s.") from error


def create_runtime(config: dict[str, Any]) -> LLMRuntime:
    definition = get_default_runtime_definition(config)
    if definition.provider.type == "ollama":
        return OllamaRuntime(definition)
    raise LLMError(
        f"Provider '{definition.provider.id}' is configured but no adapter is implemented."
    )


def get_default_runtime_definition(config: dict[str, Any]) -> RuntimeDefinition:
    provider = get_default_provider(config)
    models = config.get("models", {})
    if not isinstance(models, dict):
        raise LLMError("AI config 'models' must be an object.")

    normalized_models: dict[str, ModelBinding] = {}
    for role, binding in models.items():
        if not isinstance(role, str) or not isinstance(binding, dict):
            continue
        binding_provider = binding.get("provider", provider.id)
        model = binding.get("model")
        if not isinstance(binding_provider, str) or not binding_provider:
            raise LLMError(f"Model role '{role}' does not define a provider.")
        if binding_provider != provider.id:
            raise LLMError(
                f"Model role '{role}' is bound to provider '{binding_provider}', "
                f"but default provider is '{provider.id}'."
            )
        if not isinstance(model, str) or not model:
            raise LLMError(f"Model role '{role}' does not define a model.")
        dimensions = binding.get("dimensions")
        if dimensions is not None and (
            not isinstance(dimensions, int)
            or isinstance(dimensions, bool)
            or dimensions < 1
        ):
            raise LLMError(
                f"Model role '{role}' dimensions must be a positive integer."
            )
        normalized_models[role] = ModelBinding(binding_provider, model, dimensions)

    return RuntimeDefinition(
        provider=provider,
        models=normalized_models,
        options=RuntimeOptions.from_config(config),
    )


def get_default_provider(config: dict[str, Any]) -> ProviderDefinition:
    provider_id = config.get("defaultProvider")
    providers = config.get("providers", {})
    if not isinstance(provider_id, str) or not provider_id:
        raise LLMError("AI config must define 'defaultProvider'.")
    if not isinstance(providers, dict):
        raise LLMError("AI config 'providers' must be an object.")

    provider = providers.get(provider_id)
    if not isinstance(provider, dict):
        raise LLMError(f"Default provider '{provider_id}' is not configured.")

    provider_type = provider.get("type")
    if not isinstance(provider_type, str) or not provider_type:
        raise LLMError(f"Provider '{provider_id}' does not define a type.")

    host = provider.get("endpoint")
    if not isinstance(host, str) or not host:
        raise LLMError(f"Provider '{provider_id}' does not define an endpoint.")

    endpoint_env = provider.get("endpointEnv")
    if endpoint_env is not None:
        if not isinstance(endpoint_env, str) or not endpoint_env:
            raise LLMError(f"Provider '{provider_id}' endpointEnv must be a string.")
        host = os.environ.get(endpoint_env, host)
        if not isinstance(host, str) or not host:
            raise LLMError(f"Provider '{provider_id}' endpoint must not be empty.")

    timeout = provider.get("timeout", 300)
    if not isinstance(timeout, int):
        raise LLMError(f"Provider '{provider_id}' timeout must be an integer.")

    max_concurrent_requests = provider.get("maxConcurrentRequests")
    if max_concurrent_requests is not None and not isinstance(
        max_concurrent_requests,
        int,
    ):
        raise LLMError(
            f"Provider '{provider_id}' maxConcurrentRequests must be an integer."
        )

    # This layer is synchronous and creates one request per CLI call. Higher-level
    # RAG/agent orchestration should enforce this when it introduces concurrency.
    return ProviderDefinition(
        id=provider_id,
        type=provider_type,
        host=host.rstrip("/"),
        timeout=timeout,
        max_concurrent_requests=max_concurrent_requests,
    )


def get_model(config: dict[str, Any], role: str) -> str:
    return get_default_runtime_definition(config).model_for(role)


def get_embedding_contract(config: dict[str, Any]) -> dict[str, Any]:
    definition = get_default_runtime_definition(config)
    binding = definition.models.get("embedding")
    if binding is None:
        raise LLMError("AI config must define an embedding model.")
    if binding.dimensions is None:
        raise LLMError("Embedding model configuration must define dimensions.")

    return {
        "contractVersion": EMBEDDING_CONTRACT_VERSION,
        "provider": binding.provider,
        "model": binding.model,
        "dimensions": binding.dimensions,
    }


def build_pull_commands(config: dict[str, Any]) -> list[str]:
    definition = get_default_runtime_definition(config)
    if definition.provider.type != "ollama":
        raise LLMError("Pull commands are currently available only for Ollama.")

    commands = []
    seen = set()
    for binding in definition.models.values():
        if binding.model in seen:
            continue
        commands.append(f"ollama pull {binding.model}")
        seen.add(binding.model)
    return commands


def _to_ollama_options(options: RuntimeOptions) -> dict[str, Any]:
    mapped: dict[str, Any] = {}
    if options.temperature is not None:
        mapped["temperature"] = options.temperature
    if options.top_p is not None:
        mapped["top_p"] = options.top_p
    if options.max_tokens is not None:
        mapped["num_predict"] = options.max_tokens
    return mapped


def _optional_number(options: dict[str, Any], key: str) -> float | None:
    value = options.get(key)
    if value is None:
        return None
    if isinstance(value, int | float) and not isinstance(value, bool):
        return float(value)
    raise LLMError(f"Runtime option '{key}' must be a number.")


def _optional_int(options: dict[str, Any], key: str) -> int | None:
    value = options.get(key)
    if value is None:
        return None
    if isinstance(value, int) and not isinstance(value, bool):
        return value
    raise LLMError(f"Runtime option '{key}' must be an integer.")


def _optional_bool(options: dict[str, Any], key: str) -> bool | None:
    value = options.get(key)
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise LLMError(f"Runtime option '{key}' must be a boolean.")


def _coerce_embedding(values: list[Any]) -> list[float]:
    embedding = []
    for value in values:
        if not isinstance(value, int | float) or isinstance(value, bool):
            raise LLMError("Ollama embedding vector contains a non-numeric value.")
        embedding.append(float(value))
    return embedding
