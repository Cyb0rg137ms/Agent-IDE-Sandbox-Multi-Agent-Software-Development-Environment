"""
test_blueprint_engine.py
========================
Tests for BlueprintEngine, component todo list decomposition,
and holographic memory ingestion.
"""

import pytest
from agent_core.logos.blueprint_engine import BlueprintEngine, ArchitectureBlueprint, BlueprintComponent
from agent_core.logos.holographic_memory import HolographicMemoryEngine
from agent_core.operator_interface import SandboxOperatorInterface, SandboxSessionReport


class TestBlueprintEngine:
    def test_game_decomposition(self):
        engine = BlueprintEngine()
        blueprint = engine.generate_blueprint("full working code for temple run (beautiful)")

        assert isinstance(blueprint, ArchitectureBlueprint)
        assert blueprint.total_components >= 5
        assert "Canvas" in blueprint.system_layout or "Animation" in blueprint.system_layout

        # Verify key subsystems
        subsystem_names = [c.subsystem for c in blueprint.components]
        assert any("Player" in s for s in subsystem_names)
        assert any("Obstacle" in s for s in subsystem_names)
        assert any("Collision" in s for s in subsystem_names)

        # Verify holographic serialization
        holo_entry = blueprint.format_holographic_entry()
        assert "BLUEPRINT::" in holo_entry
        assert "COMPONENTS" in holo_entry

    def test_math_decomposition(self):
        engine = BlueprintEngine()
        blueprint = engine.generate_blueprint("Write a safe division function 'divide(a, b)' that handles zero divisor inputs.")

        assert isinstance(blueprint, ArchitectureBlueprint)
        assert blueprint.total_components >= 4
        comp_names = [c.name for c in blueprint.components]
        assert any("Validation" in n or "Contract" in n for n in comp_names)
        assert any("Singularity" in n or "Preemption" in n for n in comp_names)

    def test_holographic_memory_blueprint_ingestion(self):
        engine = BlueprintEngine()
        blueprint = engine.generate_blueprint("build a flappy bird game")

        mem = HolographicMemoryEngine(dimension=128)
        mem.store_blueprint(blueprint)

        stats = mem.get_boundary_compression_stats()
        assert stats["total_records"] >= len(blueprint.components) + 1
        assert stats["raw_characters_stored"] > 100

        # Query retrieval
        results = mem.query("collision detection player", top_k=2)
        assert len(results) >= 1

    def test_operator_interface_includes_blueprint(self):
        operator = SandboxOperatorInterface(provider_name="mock", enable_logos=True)
        report = operator.solve_task("write a divide function")

        assert isinstance(report, SandboxSessionReport)
        assert report.blueprint is not None
        assert "components" in report.blueprint
        assert len(report.blueprint["components"]) >= 3
        data = report.to_dict()
        assert "blueprint" in data
