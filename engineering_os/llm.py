from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LLMError(RuntimeError):
    """Raised when a local LLM runtime cannot satisfy a request."""


class LLMRuntime(Protocol):
    id: str

    def list_models(self) -> list[str]:
        """Return model names available in the runtime."""

    def generate(self, prompt: str, *, role: str = "chat") -> str:
        """Generate text using a configured model role."""

    def embed(self, text: str) -> list[float]:
        """Create one embedding vector using the configured embedding model."""


@dataclass(frozen=True)
class RuntimeEndpoint:
    id: str
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

    def to_ollama_options(self) -> dict[str, Any]:
        mapped: dict[str, Any] = {}
        if self.temperature is not None:
            mapped["temperature"] = self.temperature
        if self.top_p is not None:
            mapped["top_p"] = self.top_p
        if self.max_tokens is not None:
            mapped["num_predict"] = self.max_tokens
        return mapped


@dataclass(frozen=True)
class RuntimeDefinition:
    endpoint: RuntimeEndpoint
    models: dict[str, str]
    options: RuntimeOptions

    def model_for(self, role: str) -> str:
        model = self.models.get(role)
        if not isinstance(model, str) or not model:
            raise LLMError(f"Model role '{role}' is not configured.")
        return model


class OllamaRuntime:
    def __init__(
        self,
        definition: RuntimeDefinition,
        *,
        http_client: OllamaHttpClient | None = None,
    ) -> None:
        self.id = definition.endpoint.id
        self.definition = definition
        self._http = http_client or OllamaHttpClient(definition.endpoint)

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

    def generate(self, prompt: str, *, role: str = "chat") -> str:
        payload = {
            "model": self.definition.model_for(role),
            "prompt": prompt,
            "stream": self.definition.options.stream,
        }
        options = self.definition.options.to_ollama_options()
        if options:
            payload["options"] = options

        if self.definition.options.stream:
            return self._generate_stream(payload)

        response = self._http.request_json("POST", "/api/generate", payload).get("response")
        if not isinstance(response, str):
            raise LLMError("Ollama response did not include text output.")
        return response

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
            return _coerce_embedding(embeddings[0])

        embedding = payload.get("embedding")
        if isinstance(embedding, list):
            return _coerce_embedding(embedding)

        raise LLMError("Ollama response did not include an embedding vector.")

    def _generate_stream(self, payload: dict[str, Any]) -> str:
        output = []
        for chunk in self._http.request_json_lines("POST", "/api/generate", payload):
            response = chunk.get("response")
            if isinstance(response, str):
                output.append(response)
        return "".join(output)


class OllamaHttpClient:
    def __init__(self, endpoint: RuntimeEndpoint) -> None:
        self.endpoint = endpoint

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
            f"{self.endpoint.host}{path}",
            data=body,
            headers=headers,
            method=method,
        )

        try:
            with urlopen(request, timeout=self.endpoint.timeout) as response:
                return response.read().decode("utf-8")
        except HTTPError as error:
            raise LLMError(f"Ollama request failed with HTTP {error.code}.") from error
        except URLError as error:
            raise LLMError(
                f"Cannot connect to Ollama at {self.endpoint.host}: {error.reason}"
            ) from error
        except TimeoutError as error:
            raise LLMError(f"Ollama request timed out after {self.endpoint.timeout}s.") from error


def create_runtime(config: dict[str, Any]) -> LLMRuntime:
    definition = get_default_runtime_definition(config)
    if definition.endpoint.id == "ollama":
        return OllamaRuntime(definition)
    raise LLMError(
        f"Runtime '{definition.endpoint.id}' is configured but no adapter is implemented."
    )


def get_default_runtime_definition(config: dict[str, Any]) -> RuntimeDefinition:
    endpoint = get_default_runtime(config)
    models = config.get("models", {})
    if not isinstance(models, dict):
        raise LLMError("Runtime config 'models' must be an object.")

    normalized_models = {}
    for role, model in models.items():
        if isinstance(role, str) and isinstance(model, str) and model:
            normalized_models[role] = model

    return RuntimeDefinition(
        endpoint=endpoint,
        models=normalized_models,
        options=RuntimeOptions.from_config(config),
    )


def get_default_runtime(config: dict[str, Any]) -> RuntimeEndpoint:
    runtime_id = config.get("defaultRuntime")
    runtimes = config.get("runtimes", [])
    if not isinstance(runtime_id, str) or not runtime_id:
        raise LLMError("Runtime config must define 'defaultRuntime'.")
    if not isinstance(runtimes, list):
        raise LLMError("Runtime config 'runtimes' must be an array.")

    for runtime in runtimes:
        if not isinstance(runtime, dict):
            continue
        if runtime.get("id") == runtime_id and runtime.get("enabled", False):
            host = runtime.get("host")
            if not isinstance(host, str) or not host:
                raise LLMError(f"Runtime '{runtime_id}' does not define a host.")

            timeout = runtime.get("timeout", 300)
            if not isinstance(timeout, int):
                raise LLMError(f"Runtime '{runtime_id}' timeout must be an integer.")

            max_concurrent_requests = runtime.get("maxConcurrentRequests")
            if max_concurrent_requests is not None and not isinstance(
                max_concurrent_requests,
                int,
            ):
                raise LLMError(
                    f"Runtime '{runtime_id}' maxConcurrentRequests must be an integer."
                )

            # This layer is synchronous and creates one request per CLI call. Higher-level
            # RAG/agent orchestration should enforce this when it introduces concurrency.
            return RuntimeEndpoint(
                id=runtime_id,
                host=host.rstrip("/"),
                timeout=timeout,
                max_concurrent_requests=max_concurrent_requests,
            )

    raise LLMError(f"Default runtime '{runtime_id}' is not enabled or not configured.")


def get_model(config: dict[str, Any], role: str) -> str:
    return get_default_runtime_definition(config).model_for(role)


def build_pull_commands(config: dict[str, Any]) -> list[str]:
    definition = get_default_runtime_definition(config)
    if definition.endpoint.id != "ollama":
        raise LLMError("Pull commands are currently available only for Ollama.")

    commands = []
    seen = set()
    for model in definition.models.values():
        if model in seen:
            continue
        commands.append(f"ollama pull {model}")
        seen.add(model)
    return commands


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
