from __future__ import annotations

import math
import re
from dataclasses import dataclass
from pathlib import Path


TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9_]+")


@dataclass
class RetrievedChunk:
    source: str
    chunk_id: str
    text: str
    score: float


@dataclass
class IndexedChunk:
    source: str
    chunk_id: str
    text: str
    term_weights: dict[str, float]
    norm: float


def _tokenize(text: str) -> list[str]:
    return [t.lower() for t in TOKEN_PATTERN.findall(text)]


def _vectorize(text: str) -> tuple[dict[str, float], float]:
    tokens = _tokenize(text)
    if not tokens:
        return {}, 0.0

    counts: dict[str, int] = {}
    for token in tokens:
        counts[token] = counts.get(token, 0) + 1

    length = float(len(tokens))
    vector = {term: count / length for term, count in counts.items()}
    norm = math.sqrt(sum(weight * weight for weight in vector.values()))
    return vector, norm


def _cosine_similarity(
    query_vector: dict[str, float],
    query_norm: float,
    chunk_vector: dict[str, float],
    chunk_norm: float,
) -> float:
    if query_norm == 0.0 or chunk_norm == 0.0:
        return 0.0

    shared_terms = set(query_vector).intersection(chunk_vector)
    dot_product = sum(query_vector[term] * chunk_vector[term] for term in shared_terms)
    return dot_product / (query_norm * chunk_norm)


class LocalRAGService:
    def __init__(self, knowledge_dir: Path, chunk_size: int = 700):
        self.knowledge_dir = knowledge_dir
        self.chunk_size = chunk_size
        self._index: list[IndexedChunk] = []

    def refresh_index(self) -> None:
        self._index = []
        if not self.knowledge_dir.exists():
            return

        for path in sorted(self.knowledge_dir.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".md", ".txt"}:
                continue

            content = path.read_text(encoding="utf-8")
            chunks = self._chunk_text(content)
            rel_source = str(path.relative_to(self.knowledge_dir.parent))
            for idx, chunk in enumerate(chunks, start=1):
                vector, norm = _vectorize(chunk)
                chunk_id = f"{path.stem}-{idx}"
                self._index.append(
                    IndexedChunk(
                        source=rel_source,
                        chunk_id=chunk_id,
                        text=chunk,
                        term_weights=vector,
                        norm=norm,
                    )
                )

    def retrieve(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        if not self._index:
            return []

        query_vector, query_norm = _vectorize(query)
        scored: list[RetrievedChunk] = []
        for chunk in self._index:
            score = _cosine_similarity(
                query_vector=query_vector,
                query_norm=query_norm,
                chunk_vector=chunk.term_weights,
                chunk_norm=chunk.norm,
            )
            if score <= 0.0:
                continue
            scored.append(
                RetrievedChunk(
                    source=chunk.source,
                    chunk_id=chunk.chunk_id,
                    text=chunk.text,
                    score=round(min(max(score, 0.0), 1.0), 4),
                )
            )

        scored.sort(key=lambda item: item.score, reverse=True)
        return scored[:top_k]

    def _chunk_text(self, content: str) -> list[str]:
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        if not paragraphs:
            return []

        chunks: list[str] = []
        current = ""
        for paragraph in paragraphs:
            candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
            if len(candidate) <= self.chunk_size:
                current = candidate
                continue

            if current:
                chunks.append(current)
            current = paragraph

        if current:
            chunks.append(current)
        return chunks
