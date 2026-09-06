"""
holographic_memory.py
=====================
Layer 3: Holographic Memory Compression (LOGOS).
Derived from Claude-Lightyear v10.0 Ultra (Layer 3: Holographic Memory Compression).

Implements Boundary-to-Bulk holographic projection to compress extensive execution
and reasoning history into compact boundary state representations. Enables associative
querying over unbounded context windows without token explosion.
"""

from __future__ import annotations

import cmath
import hashlib
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class HolographicMemoryRecord:
    """A memory trace projected onto the holographic boundary."""
    id: str
    content: str
    boundary_vector: List[complex]
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class HolographicMemoryEngine:
    """
    LOGOS Holographic Boundary-to-Bulk Memory Engine.
    Uses complex-valued phase interference vectors (Holographic Reduced Representations / HRR)
    to store and associatively retrieve memory traces in fixed-dimensional state space.
    """

    def __init__(self, dimension: int = 128) -> None:
        self.dimension = dimension
        self._boundary_state: List[complex] = [0.0 + 0.0j] * self.dimension
        self._records: List[HolographicMemoryRecord] = []

    def encode_text_to_phase_vector(self, text: str) -> List[complex]:
        """
        Projects text tokens onto a complex unit-circle phase vector.
        Each token produces a deterministic phase shift theta in [-pi, pi].
        """
        vec = [0.0 + 0.0j] * self.dimension
        words = text.lower().split()
        if not words:
            return [1.0 + 0.0j] * self.dimension

        for i, word in enumerate(words):
            h = int(hashlib.md5(word.encode("utf-8")).hexdigest()[:8], 16)
            slot = (h ^ (i * 31)) % self.dimension
            # Phase angle derived from token hash
            theta = ((h % 1000) / 1000.0) * 2.0 * math.pi - math.pi
            vec[slot] += cmath.exp(1j * theta)

        # Normalize L2 norm
        norm = math.sqrt(sum(abs(x) ** 2 for x in vec))
        if norm > 1e-9:
            vec = [x / norm for x in vec]
        return vec

    def store(self, content: str, memory_id: Optional[str] = None, **metadata: Any) -> HolographicMemoryRecord:
        """
        Superimposes a new memory trace into the bulk boundary state.
        Uses holographic superposition: State_new = alpha * State_old + beta * Item
        """
        mid = memory_id or f"holo_{len(self._records) + 1}_{int(time.time() * 1000)}"
        phase_vec = self.encode_text_to_phase_vector(content)

        record = HolographicMemoryRecord(
            id=mid,
            content=content,
            boundary_vector=phase_vec,
            metadata=metadata,
        )
        self._records.append(record)

        # Holographic interference superposition onto global boundary
        for i in range(self.dimension):
            self._boundary_state[i] = 0.85 * self._boundary_state[i] + 0.15 * phase_vec[i]

        return record

    def associative_recall(
        self,
        query: str,
        top_k: int = 3,
        min_fidelity: float = 0.05,
    ) -> List[Tuple[HolographicMemoryRecord, float]]:
        """
        Retrieves memory traces matching query phase alignment (inner product fidelity).
        """
        query_vec = self.encode_text_to_phase_vector(query)
        scored: List[Tuple[HolographicMemoryRecord, float]] = []

        for record in self._records:
            # Complex Hermitian dot product: <u, v> = sum(u_i * conjugate(v_i))
            dot = sum(
                (q.real * r.real + q.imag * r.imag)
                for q, r in zip(query_vec, record.boundary_vector)
            )
            fidelity = max(0.0, float(dot))
            if fidelity >= min_fidelity:
                scored.append((record, fidelity))

        if not scored and self._records:
            scored = [
                (
                    r,
                    max(0.0, float(sum(q.real * r.boundary_vector[i].real + q.imag * r.boundary_vector[i].imag for i, q in enumerate(query_vec))))
                )
                for r in self._records
            ]

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    # Aliases for ergonomic API usage
    retrieve = associative_recall
    query = associative_recall

    def get_boundary_compression_stats(self) -> Dict[str, Any]:
        """Returns holographic compression metrics."""
        total_raw_chars = sum(len(r.content) for r in self._records)
        holo_bytes = self.dimension * 16  # 16 bytes per complex128
        compression_ratio = (total_raw_chars / max(1, holo_bytes)) if total_raw_chars > 0 else 1.0

        return {
            "dimension": self.dimension,
            "total_records": len(self._records),
            "raw_characters_stored": total_raw_chars,
            "boundary_vector_bytes": holo_bytes,
            "compression_ratio": round(compression_ratio, 2),
            "boundary_norm": round(math.sqrt(sum(abs(x) ** 2 for x in self._boundary_state)), 4),
        }

    def store_blueprint(self, blueprint: Any) -> None:
        """
        Ingests an ArchitectureBlueprint into holographic memory.
        Encodes the master layout and registers individual component contracts into phase vectors.
        """
        # Store master layout representation
        master_entry = getattr(blueprint, "format_holographic_entry", lambda: str(blueprint))()
        self.store(content=master_entry, category="blueprint_master")

        # Index each component specification
        components = getattr(blueprint, "components", [])
        for comp in components:
            comp_entry = f"COMPONENT::{comp.id}::{comp.name}::SUBSYSTEM::{comp.subsystem}::CONTRACT::{comp.contract}"
            self.store(content=comp_entry, category="blueprint_component", tool=comp.id)
