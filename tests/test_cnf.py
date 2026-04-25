"""Tests for CNF conversion."""

import pytest
from logic import parse, Atom, And, Or, Not, Implies, Biconditional
from inference.cnf import (
    eliminate_iff,
    eliminate_implies,
    move_not_inwards,
    distribute_or_over_and,
    to_cnf,
    extract_clauses,
    is_tautological_clause,
)


class TestEliminiateIff:
    """Test biconditional elimination."""
    
    def test_simple_biconditional(self):
        """Test A <-> B becomes (A -> B) & (B -> A)."""
        formula = Biconditional(Atom("A"), Atom("B"))
        result = eliminate_iff(formula)
        
        # Should be And node
        assert isinstance(result, And)
        # Both sides should be implications
        assert isinstance(result.left, Implies)
        assert isinstance(result.right, Implies)
    
    def test_nested_biconditionals(self):
        """Test nested biconditionals are eliminated."""
        formula = Biconditional(
            Atom("A"),
            Biconditional(Atom("B"), Atom("C"))
        )
        result = eliminate_iff(formula)
        
        # Should not contain any Biconditional nodes
        assert not contains_node_type(result, Biconditional)


class TestEliminateImplies:
    """Test implication elimination."""
    
    def test_simple_implication(self):
        """Test A -> B becomes ~A | B."""
        formula = Implies(Atom("A"), Atom("B"))
        result = eliminate_implies(formula)
        
        # Should be Or node
        assert isinstance(result, Or)
        # Left should be ~A
        assert isinstance(result.left, Not)
        # Right should be B
        assert isinstance(result.right, Atom)
    
    def test_nested_implications(self):
        """Test nested implications are eliminated."""
        formula = Implies(Atom("A"), Implies(Atom("B"), Atom("C")))
        result = eliminate_implies(formula)
        
        # Should not contain any Implies nodes
        assert not contains_node_type(result, Implies)


class TestMoveNotInwards:
    """Test moving negations inward."""
    
    def test_double_negation_elimination(self):
        """Test ~~A becomes A."""
        formula = Not(Not(Atom("A")))
        result = move_not_inwards(formula)
        
        # Should be just the atom
        assert isinstance(result, Atom)
        assert result.name == "A"
    
    def test_demorgan_and(self):
        """Test ~(A & B) becomes ~A | ~B."""
        formula = Not(And(Atom("A"), Atom("B")))
        result = move_not_inwards(formula)
        
        # Should be Or
        assert isinstance(result, Or)
        # Left should be ~A
        assert isinstance(result.left, Not)
        assert isinstance(result.left.child, Atom)
        # Right should be ~B
        assert isinstance(result.right, Not)
        assert isinstance(result.right.child, Atom)
    
    def test_demorgan_or(self):
        """Test ~(A | B) becomes ~A & ~B."""
        formula = Not(Or(Atom("A"), Atom("B")))
        result = move_not_inwards(formula)
        
        # Should be And
        assert isinstance(result, And)
        # Left should be ~A
        assert isinstance(result.left, Not)
        # Right should be ~B
        assert isinstance(result.right, Not)
    
    def test_nnf_result(self):
        """Test that result is in NNF (Not only above Atoms)."""
        formula = Not(And(Or(Atom("A"), Atom("B")), Atom("C")))
        result = move_not_inwards(formula)
        
        # Check that all Not nodes wrap Atoms
        assert is_nnf(result)


class TestDistributeOrOverAnd:
    """Test distribution of OR over AND."""
    
    def test_simple_distribution(self):
        """Test A | (B & C) becomes (A | B) & (A | C)."""
        formula = Or(Atom("A"), And(Atom("B"), Atom("C")))
        result = distribute_or_over_and(formula)
        
        # Should be And
        assert isinstance(result, And)
        # Both sides should be Or
        assert isinstance(result.left, Or)
        assert isinstance(result.right, Or)
    
    def test_reverse_distribution(self):
        """Test (A & B) | C becomes (A | C) & (B | C)."""
        formula = Or(And(Atom("A"), Atom("B")), Atom("C"))
        result = distribute_or_over_and(formula)
        
        # Should be And
        assert isinstance(result, And)
    
    def test_no_distribution_needed(self):
        """Test formulas already in proper form."""
        formula = And(
            Or(Atom("A"), Atom("B")),
            Or(Atom("C"), Atom("D"))
        )
        result = distribute_or_over_and(formula)
        
        # Should remain as And
        assert isinstance(result, And)


class TestToCNF:
    """Test full CNF conversion pipeline."""
    
    def test_atom_cnf(self):
        """Test Atom A is already in CNF."""
        formula = Atom("A")
        result = to_cnf(formula)
        
        assert isinstance(result, Atom)
    
    def test_negation_cnf(self):
        """Test ~A is in CNF."""
        formula = Not(Atom("A"))
        result = to_cnf(formula)
        
        assert isinstance(result, Not)
    
    def test_implication_cnf(self):
        """Test A -> B becomes ~A | B in CNF."""
        formula = Implies(Atom("A"), Atom("B"))
        result = to_cnf(formula)
        
        # Should be Or of literals
        assert isinstance(result, Or)
    
    def test_biconditional_cnf(self):
        """Test A <-> B becomes (~A | B) & (~B | A)."""
        formula = Biconditional(Atom("A"), Atom("B"))
        result = to_cnf(formula)
        
        # Should be And at top level
        assert isinstance(result, And)
    
    def test_complex_formula_cnf(self):
        """Test complex formula is converted to CNF."""
        formula = parse("(A -> B) & A")
        result = to_cnf(formula)
        
        # Result should have only And/Or/Not/Atom
        assert is_valid_cnf_structure(result)


class TestExtractClauses:
    """Test clause extraction from CNF formulas."""
    
    def test_single_atom(self):
        """Test extraction from single atom."""
        formula = Atom("A")
        clauses = extract_clauses(formula)
        
        assert clauses == {frozenset({"A"})}
    
    def test_single_negated_atom(self):
        """Test extraction from negated atom."""
        formula = Not(Atom("A"))
        clauses = extract_clauses(formula)
        
        assert clauses == {frozenset({"~A"})}
    
    def test_simple_clause(self):
        """Test extraction from simple disjunction."""
        formula = Or(Atom("A"), Not(Atom("B")))
        clauses = extract_clauses(formula)
        
        # A | ~B
        assert clauses == {frozenset({"A", "~B"})}
    
    def test_simple_cnf(self):
        """Test extraction from (A | B) & (~A | C)."""
        formula = And(
            Or(Atom("A"), Atom("B")),
            Or(Not(Atom("A")), Atom("C"))
        )
        clauses = extract_clauses(formula)
        
        expected = {
            frozenset({"A", "B"}),
            frozenset({"~A", "C"})
        }
        assert clauses == expected
    
    def test_tautology_omitted(self):
        """Test that tautological clauses are omitted."""
        # A | ~A is a tautology
        formula = Or(Atom("A"), Not(Atom("A")))
        clauses = extract_clauses(formula)
        
        # Tautological clause should be omitted
        assert clauses == set()
    
    def test_implication_cnf_extraction(self):
        """Test extraction from A -> B (becomes ~A | B)."""
        formula = to_cnf(Implies(Atom("A"), Atom("B")))
        clauses = extract_clauses(formula)
        
        assert clauses == {frozenset({"~A", "B"})}
    
    def test_biconditional_cnf_extraction(self):
        """Test extraction from A <-> B."""
        formula = to_cnf(Biconditional(Atom("A"), Atom("B")))
        clauses = extract_clauses(formula)
        
        expected = {
            frozenset({"~A", "B"}),
            frozenset({"~B", "A"})
        }
        assert clauses == expected
    
    def test_demorgan_extraction(self):
        """Test extraction from ~(A & B) becomes ~A | ~B."""
        formula = to_cnf(Not(And(Atom("A"), Atom("B"))))
        clauses = extract_clauses(formula)
        
        assert clauses == {frozenset({"~A", "~B"})}
    
    def test_distribution_extraction(self):
        """Test extraction from A | (B & C)."""
        formula = to_cnf(Or(Atom("A"), And(Atom("B"), Atom("C"))))
        clauses = extract_clauses(formula)
        
        expected = {
            frozenset({"A", "B"}),
            frozenset({"A", "C"})
        }
        assert clauses == expected


class TestIsTautologicalClause:
    """Test tautology detection."""
    
    def test_tautological_clause(self):
        """Test that A | ~A is tautological."""
        clause = frozenset({"A", "~A"})
        assert is_tautological_clause(clause)
    
    def test_non_tautological_clause(self):
        """Test that A | B is not tautological."""
        clause = frozenset({"A", "B"})
        assert not is_tautological_clause(clause)
    
    def test_tautological_with_multiple_literals(self):
        """Test tautology with multiple literals."""
        clause = frozenset({"A", "B", "~B", "C"})
        assert is_tautological_clause(clause)


# Helper functions

def contains_node_type(formula, node_type):
    """Check if formula contains a node of the given type."""
    from logic.ast import Formula
    
    if isinstance(formula, node_type):
        return True
    
    if isinstance(formula, Not):
        return contains_node_type(formula.child, node_type)
    elif isinstance(formula, And):
        return contains_node_type(formula.left, node_type) or contains_node_type(formula.right, node_type)
    elif isinstance(formula, Or):
        return contains_node_type(formula.left, node_type) or contains_node_type(formula.right, node_type)
    
    return False


def is_nnf(formula):
    """Check if formula is in negation normal form."""
    if isinstance(formula, Atom):
        return True
    
    elif isinstance(formula, Not):
        # Not should only wrap Atoms
        return isinstance(formula.child, Atom)
    
    elif isinstance(formula, And):
        return is_nnf(formula.left) and is_nnf(formula.right)
    
    elif isinstance(formula, Or):
        return is_nnf(formula.left) and is_nnf(formula.right)
    
    else:
        return False


def is_valid_cnf_structure(formula):
    """Check if formula has valid CNF structure."""
    if isinstance(formula, Atom):
        return True
    
    elif isinstance(formula, Not):
        # Not should only wrap Atoms
        return isinstance(formula.child, Atom)
    
    elif isinstance(formula, Or):
        # Or's children should be literals or atoms
        return is_clause(formula)
    
    elif isinstance(formula, And):
        # And's children should be clauses
        return is_clause(formula.left) and is_clause(formula.right) or \
               is_valid_cnf_structure(formula.left) and is_valid_cnf_structure(formula.right)
    
    else:
        return False


def is_clause(formula):
    """Check if formula is a clause (Or of literals)."""
    if isinstance(formula, Atom):
        return True
    
    elif isinstance(formula, Not):
        return isinstance(formula.child, Atom)
    
    elif isinstance(formula, Or):
        return is_clause(formula.left) and is_clause(formula.right)
    
    else:
        return False
