from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from engineering_os.config import ProjectPaths, load_runtime_config, load_settings
from engineering_os.knowledge import KnowledgeChunk, load_index, search_index
from engineering_os.llm import create_runtime, get_embedding_contract
from engineering_os.rag import (
    GroundingStatus,
    GroundingPolicy,
    RetrievalPolicy,
    INSUFFICIENT_EVIDENCE,
    answer_question,
)


@dataclass(frozen=True)
class EvaluationCase:
    name: str
    question: str
    expected_sources: tuple[str, ...] = ()
    expects_insufficient_evidence: bool = False


CASES = (
    EvaluationCase(
        "direct-factual",
        "What is the difference between state, status, and mode?",
        ("architect/lessions/Architecture_Notes_State_vs_Status_vs_Mode.md",),
    ),
    EvaluationCase(
        "multi-note-synthesis",
        "How do the EngineeringOS local AI architecture and runtime design keep "
        "providers replaceable while keeping model storage outside EngineeringOS?",
        (
            "architect/asr/ASR-0001-llm-model-selection-for-ollama-personal-pc.md",
            "architect/asr/ASR-0002-local-content-monitoring-with-n8n-and-ollama.md",
        ),
    ),
    EvaluationCase(
        "insufficient-evidence",
        "What is the exact quarterly revenue of EngineeringOS?",
        expects_insufficient_evidence=True,
    ),
    EvaluationCase(
        "insufficient-weather",
        "What is the current weather in Bangkok?",
        expects_insufficient_evidence=True,
    ),
    EvaluationCase(
        "insufficient-stock",
        "What is the current stock price of Tesla?",
        expects_insufficient_evidence=True,
    ),
    EvaluationCase(
        "insufficient-personal-fact",
        "What is my blood type?",
        expects_insufficient_evidence=True,
    ),
    EvaluationCase(
        "architecture-reasoning",
        "Why should EngineeringOS use a runtime abstraction instead of depending "
        "directly on Ollama HTTP?",
        ("architect/asr/ASR-0001-llm-model-selection-for-ollama-personal-pc.md",),
    ),
)


class FixedRuntime:
    def __init__(self, query_vector: list[float], generated: str) -> None:
        self.query_vector = query_vector
        self.generated = generated
        self.generation_calls = 0

    def embed(self, text: str) -> list[float]:
        return self.query_vector

    def generate(self, prompt: str, *, role: str = "rag") -> str:
        self.generation_calls += 1
        return self.generated


def run_grounding_evaluation() -> int:
    source = "knowledge/design.md#Decision"
    chunks = [
        KnowledgeChunk(
            "knowledge/design.md",
            "Decision",
            "The authoritative design decision.",
            [1.0, 0.0],
        )
    ]
    cases = (
        (
            "fully-supported",
            [1.0, 0.0],
            f"The authoritative design decision. [Source: {source}]",
            (GroundingStatus.SUPPORTED,),
            False,
        ),
        (
            "partially-supported",
            [1.0, 0.0],
            (
                f"The authoritative design decision. [Source: {source}]\n"
                f"The authoritative design decision improves security. [Source: {source}]"
            ),
            (GroundingStatus.SUPPORTED, GroundingStatus.PARTIALLY_SUPPORTED),
            False,
        ),
        (
            "tempting-unsupported-inference",
            [1.0, 0.0],
            f"EngineeringOS provides authentication. [Source: {source}]",
            (GroundingStatus.UNSUPPORTED,),
            True,
        ),
        (
            "insufficient-evidence",
            [0.0, 0.0],
            f"EngineeringOS provides authentication. [Source: {source}]",
            (),
            True,
        ),
    )

    failures = 0
    for name, vector, generated, expected_statuses, expects_no_answer in cases:
        runtime = FixedRuntime(vector, generated)
        response = answer_question(
            chunks,
            "What is the design decision?",
            runtime,
            runtime,
            top_k=1,
            min_relevance=0.5,
            confidence_threshold=0.5,
        )
        actual_statuses = tuple(claim.status for claim in response.grounding)
        status_ok = actual_statuses == expected_statuses
        answer_ok = (
            response.answer == INSUFFICIENT_EVIDENCE
            if expects_no_answer
            else bool(response.sources)
        )
        if name == "partially-supported":
            answer_ok = answer_ok and "security" not in response.answer
        generation_ok = (
            runtime.generation_calls == 0
            if name == "insufficient-evidence"
            else runtime.generation_calls == 1
        )
        failures += sum(not check for check in (status_ok, answer_ok, generation_ok))
        print(f"GROUNDING CASE {name}")
        for claim, expected in zip(response.grounding, expected_statuses):
            print(
                f"claim: {claim.claim} | evidence: {claim.sources} | "
                f"expected: {expected.value} | result: {claim.status.value}"
            )
        if not response.grounding:
            print(
                "claim: (none; retrieval rejected) | evidence: () | "
                "expected: INSUFFICIENT_EVIDENCE | result: "
                f"{response.answer}"
            )
        print(
            f"checks: statuses={status_ok}, answer={answer_ok}, "
            f"generation_calls={runtime.generation_calls}"
        )
        print()
    return failures


def main() -> int:
    root = ROOT
    config = load_runtime_config(ProjectPaths(root=root))
    settings = load_settings(ProjectPaths(root=root))
    policy = RetrievalPolicy.from_settings(settings)
    grounding_policy = GroundingPolicy.from_settings(settings)
    runtime = create_runtime(config)
    index = load_index(
        root / "runtime/index/knowledge.json",
        embedding_contract=get_embedding_contract(config),
    )

    failures = 0
    negative_cases = [case for case in CASES if case.expects_insufficient_evidence]
    negative_false_accepts = 0
    for case in CASES:
        retrieval_limit = 3 * policy.overfetch_factor
        matches = search_index(index, case.question, runtime, limit=retrieval_limit)
        retrieved_paths = tuple(chunk.path for _, chunk in matches)
        retrieved_sources = tuple(
            f"{chunk.path}#{chunk.heading}" for _, chunk in matches
        )
        top_score = matches[0][0] if matches else 0.0
        response = answer_question(
            index,
            case.question,
            runtime,
            runtime,
            top_k=3,
            min_relevance=policy.candidate_min_score,
            confidence_threshold=policy.confidence_threshold,
            overfetch_factor=policy.overfetch_factor,
            role="rag",
            grounding_policy=grounding_policy,
        )
        response_paths = tuple(source.split("#", 1)[0] for source in response.sources)
        response_source_ids = response.sources

        if case.expects_insufficient_evidence:
            if response.sources or response.answer != INSUFFICIENT_EVIDENCE:
                negative_false_accepts += 1
            retrieval_relevant = top_score < policy.confidence_threshold
            answer_behavior = response.answer == INSUFFICIENT_EVIDENCE
            source_correct = not response.sources
        else:
            retrieval_relevant = all(
                source in retrieved_paths for source in case.expected_sources
            )
            answer_behavior = bool(response.answer.strip())
            source_correct = bool(response.sources) and all(
                source in retrieved_sources for source in response_source_ids
            ) and all(
                claim.status is GroundingStatus.SUPPORTED
                and claim.sources
                and all(source in retrieved_sources for source in claim.sources)
                for claim in response.grounding
                if claim.status is GroundingStatus.SUPPORTED
            )

        checks = {
            "retrieval_relevance": retrieval_relevant,
            "source_correctness": source_correct,
            "answer_behavior": answer_behavior,
        }
        failures += sum(not passed for passed in checks.values())

        print(f"CASE {case.name}")
        print(f"question: {case.question}")
        print(f"retrieved: {retrieved_paths}")
        print(f"scores: {[round(score, 4) for score, _ in matches]}")
        print(f"sources: {response.sources}")
        print(
            "grounding: "
            f"{[(claim.status.value, claim.sources) for claim in response.grounding]}"
        )
        print(f"checks: {checks}")
        print(f"answer: {response.answer}")
        print("manual_review: assess factual fidelity and unsupported claims")
        print()

    print(f"baseline_failures={failures}")
    false_accept_rate = (
        negative_false_accepts / len(negative_cases) if negative_cases else 0.0
    )
    print(
        "negative_false_accept_rate="
        f"{negative_false_accepts}/{len(negative_cases)} "
        f"({false_accept_rate:.1%})"
    )
    grounding_failures = run_grounding_evaluation()
    print(f"grounding_failures={grounding_failures}")
    print("evaluation_status=COMPLETE")
    return 1 if failures or grounding_failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
