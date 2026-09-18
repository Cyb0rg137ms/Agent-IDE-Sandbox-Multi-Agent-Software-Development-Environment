"""
agent_core.logos
================
Claude-Lightyear v10.0 Ultra & LOGOS Cognitive Architecture Suite.
Integrates:
  - Level 0: MasterIndexDecomposer & Subquestion Taxonomy
  - Level 1 & 2: DualFrameworkConvergenceEngine & Backward Chaining
  - Layer 1: AxiomaticEngine (Axiom DB & Consistency Checker)
  - Layer 2: FractalReasoningEngine (MERA Multiscale Coarse-Graining)
  - Layer 3: HolographicMemoryEngine (Boundary-to-Bulk Projection)
  - Layer 4: NASTopologyEngine (Dynamic Cognitive Topology Synthesis)
  - Layer 5: DynamicAxiomRetriever (External Web/Corpus Retrieval)
  - Layer 6: PonderingEngine (Horizontal Thinking & 95%+ Confidence Filtering)
  - BlueprintEngine & RigorousAuditor
"""

from agent_core.logos.decomposition import MasterIndexDecomposer, Subquestion
from agent_core.logos.axiomatic_engine import Axiom, AxiomaticEngine, DerivationStep
from agent_core.logos.fractal_mera import FractalReasoningEngine, MERANode
from agent_core.logos.holographic_memory import HolographicMemoryEngine, HolographicMemoryRecord
from agent_core.logos.nas_topology import NASTopologyEngine, CognitiveTopology, TopologyType
from agent_core.logos.dynamic_retrieval import DynamicAxiomRetriever, SearchResult
from agent_core.logos.pondering_engine import PonderingEngine, PonderingAngle, PonderingSynthesis
from agent_core.logos.convergence import (
    DualFrameworkConvergenceEngine,
    FrameworkAnalysisResult,
    PropertyAlignmentEntry,
)
from agent_core.logos.blueprint_engine import BlueprintEngine, ArchitectureBlueprint, BlueprintComponent
from agent_core.logos.recursive_auditor import RigorousAuditor, AuditReport

# Backward compatibility alias
TopologyConfig = CognitiveTopology

__all__ = [
    "MasterIndexDecomposer",
    "Subquestion",
    "Axiom",
    "AxiomaticEngine",
    "DerivationStep",
    "FractalReasoningEngine",
    "MERANode",
    "HolographicMemoryEngine",
    "HolographicMemoryRecord",
    "NASTopologyEngine",
    "CognitiveTopology",
    "TopologyConfig",
    "TopologyType",
    "DynamicAxiomRetriever",
    "SearchResult",
    "PonderingEngine",
    "PonderingAngle",
    "PonderingSynthesis",
    "DualFrameworkConvergenceEngine",
    "FrameworkAnalysisResult",
    "PropertyAlignmentEntry",
    "BlueprintEngine",
    "ArchitectureBlueprint",
    "BlueprintComponent",
    "RigorousAuditor",
    "AuditReport",
]
