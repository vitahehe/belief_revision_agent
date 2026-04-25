"""Tests for propositional resolution and entailment checking."""

import pytest
from logic import parse, Atom, And, Or, Not, Implies
from belief_base import BeliefBase
from inference.resolution import (
    negate_literal,
    are_complementary,
    is_tautological_clause,
    resolve_pair,
    resolution_unsat,
    resolution_entails,
)


class TestNegateLiteral:
    """Test literal negation."""
    
    def test_negate_positive_literal(self):
        """Test negating a positive literal."""
        assert negate_literal("A") == "~A"
    
    def test_negate_negative_literal(self):
        """Test negating a negative literal."""
        assert negate_literal("~A") == "A"
    
    def test_negate_complex_names(self):
        """Test negating atoms with complex names."""
        assert negate_literal("Var_1") == "~Var_1"
        assert negate_literal("~Var_1") == "Var_1"


class TestAreComplementary:
    """Test complementary literal detection."""
    
    def test_complementary_literals(self):
        """Test detecting complementary literals."""
        assert are_complementary("A", "~A")
        assert are_complementary("~A", "A")
    
    def test_non_complementary_literals(self):
        """Test that non-complementary literals are recognized."""
        assert not are_complementary("A", "B")
        assert not are_complementary("A", "A")
        assert not are_complementary("~A", "~B")


class TestIsTautologicalClause:
    """Test tautological clause detection."""
    
    def test_tautological_clause(self):
        """Test that clause containing A and ~A is tautological."""
        assert is_tautological_clause(frozenset({"A", "~A"}))
    
    def test_tautological_with_extra_literals(self):
        """Test tautology with additional literals."""
        assert is_tautological_clause(frozenset({"A", "B", "~A"}))
    
    def test_non_tautological_clause(self):
        """Test that regular clauses are not tautological."""
        assert not is_tautological_clause(frozenset({"A", "B"}))
        assert not is_tautological_clause(frozenset({"~A"}))


class TestResolvePair:
    """Test the resolution rule."""
    
    def test_simple_resolution(self):
        """Test resolving {A, B} and {~A, C} yields {B, C}."""
        ci = frozenset({"A", "B"})
        cj = frozenset({"~A", "C"})
        
        resolvents = resolve_pair(ci, cj)
        
        assert frozenset({"B", "C"}) in resolvents
    
    def test_resolution_multiple_complementary_pairs(self):
        """Test resolution with multiple complementary pairs.
        
        Resolvents on A and B would be tautological:
        - Resolve on A: {B, C} | {~B, D} = {B, C, ~B, D} (tautology, filtered)
        - Resolve on B: {A, C} | {~A, D} = {A, C, ~A, D} (tautology, filtered)
        
        So no valid resolvents are returned.
        """
        ci = frozenset({"A", "B", "C"})
        cj = frozenset({"~A", "~B", "D"})
        
        resolvents = resolve_pair(ci, cj)
        
        # Both possible resolvents are tautological, so should be filtered
        assert len(resolvents) == 0
    
    def test_no_resolution_without_complementary_pair(self):
        """Test that no resolution occurs without complementary pair."""
        ci = frozenset({"A", "B"})
        cj = frozenset({"C", "D"})
        
        resolvents = resolve_pair(ci, cj)
        
        assert len(resolvents) == 0
    
    def test_tautological_resolvent_excluded(self):
        """Test that tautological resolvents are excluded."""
        ci = frozenset({"A", "B"})
        cj = frozenset({"~A", "~B", "C"})
        
        resolvents = resolve_pair(ci, cj)
        
        # Resolvent on A: {B, ~B, C} is tautological - excluded
        # Resolvent on B: {A, ~A, C} is tautological - excluded
        # So we should get empty or only valid resolvents
        for r in resolvents:
            assert not is_tautological_clause(r)


class TestResolutionUnsat:
    """Test the main resolution algorithm for unsatisfiability."""
    
    def test_empty_set_satisfiable(self):
        """Test that empty clause set is satisfiable."""
        clauses = set()
        assert not resolution_unsat(clauses)
    
    def test_single_literal_satisfiable(self):
        """Test that single literal is satisfiable."""
        clauses = {frozenset({"A"})}
        assert not resolution_unsat(clauses)
    
    def test_contradiction_unsatisfiable(self):
        """Test that {A} and {~A} is unsatisfiable."""
        clauses = {frozenset({"A"}), frozenset({"~A"})}
        assert resolution_unsat(clauses)
    
    def test_modus_ponens_unsatisfiable(self):
        """Test {A, A->B, ~B} is unsatisfiable."""
        # A -> B is ~A | B
        clauses = {
            frozenset({"A"}),
            frozenset({"~A", "B"}),
            frozenset({"~B"})
        }
        assert resolution_unsat(clauses)
    
    def test_satisfiable_disjunction(self):
        """Test that {A | B} is satisfiable."""
        clauses = {frozenset({"A", "B"})}
        assert not resolution_unsat(clauses)


class TestResolutionEntails:
    """Test the main entailment checking function."""
    
    def test_modus_ponens(self):
        """Test modus ponens: {A, A->B} entails B."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A"))
        kb.add_belief(kb.create_belief("A -> B"))
        
        query = parse("B")
        assert resolution_entails(kb, query)
    
    def test_non_entailment(self):
        """Test non-entailment: {A | B} does not entail A."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A | B"))
        
        query = parse("A")
        assert not resolution_entails(kb, query)
    
    def test_contradictory_kb(self):
        """Test contradictory KB entails any formula (explosion)."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A"))
        kb.add_belief(kb.create_belief("~A"))
        
        query = parse("B")
        # Inconsistent KB entails anything
        assert resolution_entails(kb, query)
    
    def test_empty_kb(self):
        """Test empty KB only entails tautologies."""
        kb = BeliefBase()
        
        # Empty KB doesn't entail A
        query_not_tautology = parse("A")
        assert not resolution_entails(kb, query_not_tautology)
    
    def test_tautology_query(self):
        """Test that empty KB entails tautologies."""
        kb = BeliefBase()
        
        query_tautology = parse("A | ~A")
        assert resolution_entails(kb, query_tautology)
    
    def test_chain_entailment(self):
        """Test chain of implications."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A"))
        kb.add_belief(kb.create_belief("A -> B"))
        kb.add_belief(kb.create_belief("B -> C"))
        
        query = parse("C")
        assert resolution_entails(kb, query)
    
    def test_biconditional_entailment(self):
        """Test entailment with biconditionals."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A <-> B"))
        kb.add_belief(kb.create_belief("A"))
        
        query = parse("B")
        assert resolution_entails(kb, query)
    
    def test_demorgan_entailment(self):
        """Test De Morgan's law entailment."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("~(A & B)"))
        
        query = parse("~A | ~B")
        assert resolution_entails(kb, query)
    
    def test_does_not_mutate_kb(self):
        """Test that resolution doesn't mutate the KB."""
        kb = BeliefBase()
        b1 = kb.create_belief("A")
        b2 = kb.create_belief("B")
        kb.add_belief(b1)
        kb.add_belief(b2)
        
        original_size = kb.size()
        original_beliefs = [b.formula_str for b in kb.list_beliefs()]
        
        # Call entailment checking
        query = parse("C")
        resolution_entails(kb, query)
        
        # KB should be unchanged
        assert kb.size() == original_size
        assert [b.formula_str for b in kb.list_beliefs()] == original_beliefs
    
    def test_complex_scenario(self):
        """Test complex scenario with multiple rules."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("Socrates_human"))
        kb.add_belief(kb.create_belief("Socrates_human -> Socrates_mortal"))
        kb.add_belief(kb.create_belief("Socrates_mortal -> Socrates_dies"))
        
        query = parse("Socrates_dies")
        assert resolution_entails(kb, query)


class TestEdgeCases:
    """Test edge cases and special scenarios."""
    
    def test_self_referential_not_entailed(self):
        """Test that a formula doesn't trivially entail itself without it being in KB."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A"))
        
        # Query the same formula - should be true
        query = parse("A")
        assert resolution_entails(kb, query)
    
    def test_negation_of_query(self):
        """Test entailment with negated query."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A"))
        
        query = parse("~A")
        assert not resolution_entails(kb, query)
    
    def test_disjunction_entailment(self):
        """Test entailment of disjunctions."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A"))
        
        query = parse("A | B")
        assert resolution_entails(kb, query)
    
    def test_complex_formula_parsing(self):
        """Test entailment with complex formula parsing."""
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("(A & B) -> C"))
        kb.add_belief(kb.create_belief("A & B"))
        
        query = parse("C")
        assert resolution_entails(kb, query)


class TestResolutionConsistency:
    """Test that resolution results are consistent."""
    
    def test_resolution_is_sound(self):
        """Test that resolution algorithm is sound.
        
        If resolution says KB entails Q, it should be correct.
        """
        kb = BeliefBase()
        kb.add_belief(kb.create_belief("A -> B"))
        kb.add_belief(kb.create_belief("B -> C"))
        kb.add_belief(kb.create_belief("A"))
        
        # Resolution says KB entails C
        query = parse("C")
        assert resolution_entails(kb, query)
        
        # Resolution should say KB doesn't entail D (not in chain)
        query_false = parse("D")
        assert not resolution_entails(kb, query_false)
    
    def test_resolution_is_complete(self):
        """Test that resolution algorithm is complete.
        
        If KB logically entails Q, resolution should find it.
        """
        # Test several scenarios where entailment should hold
        scenarios = [
            (["A"], "A", True),
            (["A"], "~B", False),
            (["A", "A -> B"], "B", True),
            (["A | B", "~A"], "B", True),
        ]
        
        for beliefs_strs, query_str, expected in scenarios:
            kb = BeliefBase()
            for belief_str in beliefs_strs:
                kb.add_belief(kb.create_belief(belief_str))
            
            query = parse(query_str)
            result = resolution_entails(kb, query)
            assert result == expected, f"Scenario failed: {beliefs_strs} ⊨ {query_str} = {result}, expected {expected}"
