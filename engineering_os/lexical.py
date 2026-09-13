"""Persistable local BM25 statistics for exact technical retrieval."""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import PurePosixPath
from typing import Any, Iterable, Protocol


TOKENIZER_VERSION = "1.0"
DEFAULT_K1 = 1.5
DEFAULT_B = 0.75
_TOKEN_PATTERN = re.compile(r"[A-Za-z0-9]+(?:[._:/-][A-Za-z0-9_]+)*|[A-Za-z_][A-Za-z0-9_]*")


class LexicalChunk(Protocol):
    path: str
    heading: str
    heading_path: tuple[str, ...]
    text: str
    tags: tuple[str, ...]
    chunk_id: str


def tokenize(value: str) -> tuple[str, ...]:
    """Tokenize without destroying filenames, IDs, config keys, or acronyms."""
    tokens: list[str] = []
    for raw in _TOKEN_PATTERN.findall(value):
        normalized = raw.casefold()
        tokens.append(normalized)
        if any(separator in normalized for separator in (".", "/", ":", "-")):
            tokens.extend(
                part for part in re.split(r"[./:-]+", normalized) if part
            )
        camel_parts = re.findall(r"[A-Z]+(?=[A-Z][a-z]|\d|\b)|[A-Z]?[a-z]+|\d+", raw)
        if len(camel_parts) > 1:
            tokens.extend(part.casefold() for part in camel_parts)
    return tuple(tokens)


def chunk_key(chunk: LexicalChunk) -> str:
    if chunk.chunk_id:
        return chunk.chunk_id
    return f"legacy:{chunk.path}#{chunk.heading}:{hash_text(chunk.text)}"


def hash_text(value: str) -> str:
    import hashlib

    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:24]


def lexical_text(chunk: LexicalChunk) -> str:
    return "\n".join(
        value
        for value in (
            chunk.path,
            PurePosixPath(chunk.path).name,
            chunk.heading,
            " / ".join(chunk.heading_path),
            " ".join(chunk.tags),
            chunk.text,
        )
        if value
    )


def build_lexical_index(chunks: Iterable[LexicalChunk]) -> dict[str, Any]:
    frequencies: dict[str, dict[str, int]] = {}
    lengths: dict[str, int] = {}
    document_frequencies: Counter[str] = Counter()
    for chunk in chunks:
        key = chunk_key(chunk)
        counts = Counter(tokenize(lexical_text(chunk)))
        frequencies[key] = dict(sorted(counts.items()))
        lengths[key] = sum(counts.values())
        document_frequencies.update(counts.keys())
    document_count = len(frequencies)
    average = sum(lengths.values()) / document_count if document_count else 0.0
    return {
        "tokenizerVersion": TOKENIZER_VERSION,
        "documentCount": document_count,
        "averageDocumentLength": average,
        "documentFrequencies": dict(sorted(document_frequencies.items())),
        "termFrequencies": frequencies,
        "documentLengths": lengths,
    }


def validate_lexical_index(value: Any, chunks: Iterable[LexicalChunk]) -> dict[str, Any]:
    chunks = list(chunks)
    if not isinstance(value, dict) or value.get("tokenizerVersion") != TOKENIZER_VERSION:
        return build_lexical_index(chunks)
    required = {
        "documentCount",
        "averageDocumentLength",
        "documentFrequencies",
        "termFrequencies",
        "documentLengths",
    }
    if not required.issubset(value):
        return build_lexical_index(chunks)
    expected_keys = {chunk_key(chunk) for chunk in chunks}
    if (
        value.get("documentCount") != len(chunks)
        or set(value.get("termFrequencies", {})) != expected_keys
        or set(value.get("documentLengths", {})) != expected_keys
    ):
        return build_lexical_index(chunks)
    return value


def bm25_scores(
    chunks: Iterable[LexicalChunk],
    lexical_index: dict[str, Any],
    query: str,
    *,
    k1: float = DEFAULT_K1,
    b: float = DEFAULT_B,
) -> dict[str, float]:
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return {}
    document_count = int(lexical_index.get("documentCount", 0))
    average = float(lexical_index.get("averageDocumentLength", 0.0)) or 1.0
    dfs = lexical_index.get("documentFrequencies", {})
    frequencies = lexical_index.get("termFrequencies", {})
    lengths = lexical_index.get("documentLengths", {})
    scores: dict[str, float] = {}
    for chunk in chunks:
        key = chunk_key(chunk)
        terms = frequencies.get(key, {})
        length = float(lengths.get(key, 0))
        score = 0.0
        for term, query_frequency in query_terms.items():
            frequency = float(terms.get(term, 0))
            if frequency <= 0:
                continue
            document_frequency = int(dfs.get(term, 0))
            inverse_frequency = math.log(
                1.0 + (document_count - document_frequency + 0.5) / (document_frequency + 0.5)
            )
            denominator = frequency + k1 * (1.0 - b + b * length / average)
            score += query_frequency * inverse_frequency * frequency * (k1 + 1.0) / denominator
        if score > 0:
            scores[key] = score
    return scores
