"""Tests for Stage 3 belief contraction."""

import pytest
from belief_base import BeliefBase
from logic.parser import parse
from inference import resolution_entails
from revision import contract


def build_kb(formulas):
    kb = BeliefBase()
    for formula_text, priority, insertion_order in formulas:
        belief = kb.create_belief(formula_text, priority=priority, insertion_order=insertion_order)
        kb.add_belief(belief)
    return kb


class TestContraction:
    def test_non_entailment_vacuity(self):
        kb = build_kb([("A", 0, 0)])

        contracted = contract(kb, "B")

        assert contracted.size() == 1
        assert contracted.list_beliefs()[0].formula_str == "A"
        assert kb.size() == 1

    def test_direct_belief_contraction(self):
        kb = build_kb([("A", 0, 0)])

        contracted = contract(kb, "A")

        assert contracted.size() == 0
        assert not resolution_entails(contracted, parse("A"))

    def test_indirect_entailment_contraction(self):
        kb = build_kb([("A", 0, 0), ("A -> B", 0, 1)])

        contracted = contract(kb, "B")

        assert not resolution_entails(contracted, parse("B"))

    def test_priority_decides_removal_lower_priority_removed(self):
        kb = build_kb([("A", 1, 0), ("A -> B", 10, 1)])

        contracted = contract(kb, "B")

        assert contracted.size() == 1
        remaining = contracted.list_beliefs()[0]
        assert remaining.formula_str == "A -> B"

    def test_priority_decides_removal_higher_priority_removed(self):
        kb = build_kb([("A", 10, 0), ("A -> B", 1, 1)])

        contracted = contract(kb, "B")

        assert contracted.size() == 1
        remaining = contracted.list_beliefs()[0]
        assert remaining.formula_str == "A"

    def test_tie_breaking_by_newest_first(self):
        kb = build_kb([("A", 5, 0), ("A -> B", 5, 1)])

        contracted = contract(kb, "B")

        assert contracted.size() == 1
        assert contracted.list_beliefs()[0].formula_str == "A"

    def test_tie_breaking_by_newest_first_reversed(self):
        kb = build_kb([("A", 5, 1), ("A -> B", 5, 0)])

        contracted = contract(kb, "B")

        assert contracted.size() == 1
        assert contracted.list_beliefs()[0].formula_str == "A -> B"

    def test_chain_reasoning_contraction(self):
        kb = build_kb([("A", 0, 0), ("A -> B", 0, 1), ("B -> C", 0, 2)])

        contracted = contract(kb, "C")

        assert not resolution_entails(contracted, parse("C"))
        assert contracted.size() <= 2

    def test_original_kb_is_not_mutated(self):
        kb = build_kb([("A", 0, 0), ("A -> B", 0, 1)])
        original_ids = [belief.id for belief in kb.list_beliefs()]

        contract(kb, "B")

        assert [belief.id for belief in kb.list_beliefs()] == original_ids
        assert kb.size() == 2

    def test_empty_kb_returns_empty(self):
        kb = BeliefBase()

        contracted = contract(kb, "A")

        assert contracted.size() == 0

    def test_tautology_contraction_remains_unchanged(self):
        kb = build_kb([("A", 0, 0)])

        contracted = contract(kb, "A | ~A")

        assert contracted.size() == 1
        assert contracted.list_beliefs()[0].formula_str == "A"

    def test_inconsistent_kb_contraction(self):
        kb = build_kb([("A", 0, 0), ("~A", 0, 1)])

        contracted = contract(kb, "B")

        assert not resolution_entails(contracted, parse("B"))
        assert contracted.size() <= 1
