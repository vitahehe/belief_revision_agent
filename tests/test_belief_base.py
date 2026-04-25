"""
Tests for the BeliefBase module.

Tests insertion, manipulation, and copying of beliefs.
"""

import pytest
from belief_base import BeliefBase, Belief
from logic.parser import parse, ParseError


class TestBeliefCreation:
    """Test creating beliefs."""
    
    def test_create_simple_belief(self):
        """Test creating a simple belief from a formula."""
        kb = BeliefBase()
        belief = kb.create_belief("P & Q", priority=1)
        
        assert belief.formula_str == "P & Q"
        assert belief.priority == 1
        assert belief.id is not None
        assert belief.insertion_order == 0
    
    def test_create_belief_with_explicit_insertion_order(self):
        """Test creating a belief with explicit insertion order."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P", priority=0, insertion_order=5)
        belief2 = kb.create_belief("Q", priority=0, insertion_order=10)
        
        assert belief1.insertion_order == 5
        assert belief2.insertion_order == 10
    
    def test_create_belief_auto_insertion_order(self):
        """Test that insertion order is auto-assigned sequentially."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P", priority=0)
        belief2 = kb.create_belief("Q", priority=0)
        belief3 = kb.create_belief("R", priority=0)
        
        assert belief1.insertion_order == 0
        assert belief2.insertion_order == 1
        assert belief3.insertion_order == 2
    
    def test_create_belief_with_invalid_formula(self):
        """Test that creating a belief with invalid formula raises ParseError."""
        kb = BeliefBase()
        with pytest.raises(ParseError):
            kb.create_belief("P & & Q")
    
    def test_create_belief_with_complex_formula(self):
        """Test creating a belief with a complex formula."""
        kb = BeliefBase()
        belief = kb.create_belief("(P -> Q) & (Q -> R) -> (P -> R)", priority=10)
        
        assert belief.priority == 10
        assert "->>" not in belief.normalized_formula_str


class TestBeliefAddition:
    """Test adding beliefs to the belief base."""
    
    def test_add_belief_returns_true(self):
        """Test that adding a new belief returns True."""
        kb = BeliefBase()
        belief = kb.create_belief("P", priority=1)
        result = kb.add_belief(belief)
        
        assert result is True
    
    def test_add_belief_updates_size(self):
        """Test that adding a belief increases the size."""
        kb = BeliefBase()
        assert kb.size() == 0
        
        belief1 = kb.create_belief("P", priority=1)
        kb.add_belief(belief1)
        assert kb.size() == 1
        
        belief2 = kb.create_belief("Q", priority=2)
        kb.add_belief(belief2)
        assert kb.size() == 2
    
    def test_list_beliefs_maintains_insertion_order(self):
        """Test that list_beliefs returns beliefs in insertion order."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P", priority=1)
        belief2 = kb.create_belief("Q", priority=2)
        belief3 = kb.create_belief("R", priority=3)
        
        kb.add_belief(belief1)
        kb.add_belief(belief2)
        kb.add_belief(belief3)
        
        beliefs = kb.list_beliefs()
        assert len(beliefs) == 3
        assert beliefs[0].formula_str == "P"
        assert beliefs[1].formula_str == "Q"
        assert beliefs[2].formula_str == "R"
    
    def test_add_multiple_different_beliefs(self):
        """Test adding multiple different beliefs."""
        kb = BeliefBase()
        formulas = ["P", "Q", "P & Q", "P | Q", "P -> Q"]
        
        for formula in formulas:
            belief = kb.create_belief(formula, priority=0)
            kb.add_belief(belief)
        
        assert kb.size() == 5
        beliefs = kb.list_beliefs()
        assert [b.formula_str for b in beliefs] == formulas


class TestDuplicateDetection:
    """Test that duplicate formulas are not inserted."""
    
    def test_duplicate_formula_returns_false(self):
        """Test that adding a duplicate formula returns False."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P & Q", priority=1)
        kb.add_belief(belief1)
        
        belief2 = kb.create_belief("P & Q", priority=2)
        result = kb.add_belief(belief2)
        
        assert result is False
        assert kb.size() == 1
    
    def test_duplicate_with_whitespace_variation(self):
        """Test that formulas with different whitespace are recognized as duplicates."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P & Q", priority=1)
        kb.add_belief(belief1)
        
        belief2 = kb.create_belief("P&Q", priority=2)
        result = kb.add_belief(belief2)
        
        assert result is False
        assert kb.size() == 1
    
    def test_duplicate_with_extra_parentheses(self):
        """Test that extra parentheses don't create duplicates."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P & Q", priority=1)
        kb.add_belief(belief1)
        
        belief2 = kb.create_belief("(P & Q)", priority=2)
        result = kb.add_belief(belief2)
        
        assert result is False
        assert kb.size() == 1
    
    def test_duplicate_detection_based_on_normalized_form(self):
        """Test that duplicate detection uses normalized form."""
        kb = BeliefBase()
        
        # Add first formula
        belief1 = kb.create_belief("(P & Q) | R", priority=1)
        kb.add_belief(belief1)
        
        # Try to add equivalent formula with different parenthesization
        belief2 = kb.create_belief("P & Q | R", priority=2)
        result = kb.add_belief(belief2)
        
        # Should be detected as same (depending on normalization)
        # If parser associates left, they're the same
        assert kb.size() == 1
    
    def test_non_duplicate_similar_formulas(self):
        """Test that similar but different formulas are not duplicates."""
        kb = BeliefBase()
        
        belief1 = kb.create_belief("P & Q", priority=1)
        kb.add_belief(belief1)
        
        belief2 = kb.create_belief("P | Q", priority=1)
        result = kb.add_belief(belief2)
        
        assert result is True
        assert kb.size() == 2


class TestContaintsFormula:
    """Test contains_formula method."""
    
    def test_contains_formula_true(self):
        """Test that contains_formula returns True for added formulas."""
        kb = BeliefBase()
        belief = kb.create_belief("P -> Q", priority=1)
        kb.add_belief(belief)
        
        assert kb.contains_formula("P -> Q") is True
    
    def test_contains_formula_false(self):
        """Test that contains_formula returns False for non-existent formulas."""
        kb = BeliefBase()
        assert kb.contains_formula("P & Q") is False
    
    def test_contains_formula_with_whitespace_variation(self):
        """Test contains_formula with whitespace variation."""
        kb = BeliefBase()
        belief = kb.create_belief("P & Q", priority=1)
        kb.add_belief(belief)
        
        assert kb.contains_formula("P&Q") is True
        assert kb.contains_formula("P  &  Q") is True
    
    def test_contains_formula_with_invalid_formula(self):
        """Test that contains_formula raises ParseError for invalid formulas."""
        kb = BeliefBase()
        with pytest.raises(ParseError):
            kb.contains_formula("P & & Q")


class TestBeliefRemoval:
    """Test removing beliefs from the base."""
    
    def test_remove_belief_by_id_returns_true(self):
        """Test that removing a belief returns True."""
        kb = BeliefBase()
        belief = kb.create_belief("P", priority=1)
        kb.add_belief(belief)
        
        result = kb.remove_belief_by_id(belief.id)
        assert result is True
        assert kb.size() == 0
    
    def test_remove_belief_by_id_returns_false(self):
        """Test that removing non-existent belief returns False."""
        kb = BeliefBase()
        result = kb.remove_belief_by_id("non-existent-id")
        assert result is False
    
    def test_remove_belief_updates_size(self):
        """Test that removing a belief decreases the size."""
        kb = BeliefBase()
        belief = kb.create_belief("P", priority=1)
        kb.add_belief(belief)
        
        assert kb.size() == 1
        kb.remove_belief_by_id(belief.id)
        assert kb.size() == 0
    
    def test_remove_belief_allows_readding_same_formula(self):
        """Test that after removing a belief, the same formula can be added again."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P", priority=1)
        kb.add_belief(belief1)
        
        kb.remove_belief_by_id(belief1.id)
        
        belief2 = kb.create_belief("P", priority=2)
        result = kb.add_belief(belief2)
        
        assert result is True
        assert kb.size() == 1
    
    def test_remove_one_belief_does_not_affect_others(self):
        """Test that removing one belief doesn't affect others."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P", priority=1)
        belief2 = kb.create_belief("Q", priority=2)
        belief3 = kb.create_belief("R", priority=3)
        
        kb.add_belief(belief1)
        kb.add_belief(belief2)
        kb.add_belief(belief3)
        
        kb.remove_belief_by_id(belief2.id)
        
        beliefs = kb.list_beliefs()
        assert len(beliefs) == 2
        assert beliefs[0].formula_str == "P"
        assert beliefs[1].formula_str == "R"


class TestBeliefCopying:
    """Test copying the belief base."""
    
    def test_copy_kb_returns_new_instance(self):
        """Test that copy_kb returns a different BeliefBase instance."""
        kb1 = BeliefBase()
        kb2 = kb1.copy_kb()
        
        assert kb1 is not kb2
    
    def test_copy_kb_preserves_beliefs(self):
        """Test that copying preserves all beliefs."""
        kb1 = BeliefBase()
        belief1 = kb1.create_belief("P", priority=1)
        belief2 = kb1.create_belief("Q", priority=2)
        kb1.add_belief(belief1)
        kb1.add_belief(belief2)
        
        kb2 = kb1.copy_kb()
        
        assert kb2.size() == 2
        beliefs = kb2.list_beliefs()
        assert beliefs[0].formula_str == "P"
        assert beliefs[1].formula_str == "Q"
    
    def test_copy_kb_is_independent(self):
        """Test that modifying the copy doesn't affect the original."""
        kb1 = BeliefBase()
        belief1 = kb1.create_belief("P", priority=1)
        kb1.add_belief(belief1)
        
        kb2 = kb1.copy_kb()
        
        # Modify the copy
        belief_to_add = kb2.create_belief("Q", priority=2)
        kb2.add_belief(belief_to_add)
        
        assert kb1.size() == 1
        assert kb2.size() == 2
    
    def test_copy_kb_preserves_insertion_order(self):
        """Test that copying preserves insertion order."""
        kb1 = BeliefBase()
        belief1 = kb1.create_belief("A", priority=1)
        belief2 = kb1.create_belief("B", priority=2)
        belief3 = kb1.create_belief("C", priority=3)
        
        kb1.add_belief(belief1)
        kb1.add_belief(belief2)
        kb1.add_belief(belief3)
        
        kb2 = kb1.copy_kb()
        beliefs = kb2.list_beliefs()
        
        assert beliefs[0].insertion_order == 0
        assert beliefs[1].insertion_order == 1
        assert beliefs[2].insertion_order == 2
        assert beliefs[0].formula_str == "A"
        assert beliefs[1].formula_str == "B"
        assert beliefs[2].formula_str == "C"
    
    def test_copy_empty_kb(self):
        """Test copying an empty belief base."""
        kb1 = BeliefBase()
        kb2 = kb1.copy_kb()
        
        assert kb2.size() == 0
    
    def test_removing_from_original_after_copy(self):
        """Test that removing from original doesn't affect copy."""
        kb1 = BeliefBase()
        belief1 = kb1.create_belief("P", priority=1)
        belief2 = kb1.create_belief("Q", priority=2)
        kb1.add_belief(belief1)
        kb1.add_belief(belief2)
        
        kb2 = kb1.copy_kb()
        
        # Modify the original
        kb1.remove_belief_by_id(belief1.id)
        
        assert kb1.size() == 1
        assert kb2.size() == 2


class TestBeliefRetrieval:
    """Test retrieving beliefs from the base."""
    
    def test_get_belief_by_id(self):
        """Test retrieving a belief by id."""
        kb = BeliefBase()
        belief = kb.create_belief("P", priority=1)
        kb.add_belief(belief)
        
        retrieved = kb.get_belief_by_id(belief.id)
        assert retrieved is belief
    
    def test_get_belief_by_id_not_found(self):
        """Test retrieving non-existent belief by id returns None."""
        kb = BeliefBase()
        retrieved = kb.get_belief_by_id("non-existent-id")
        assert retrieved is None
    
    def test_get_belief_by_formula(self):
        """Test retrieving a belief by formula."""
        kb = BeliefBase()
        belief = kb.create_belief("P & Q", priority=1)
        kb.add_belief(belief)
        
        retrieved = kb.get_belief_by_formula("P & Q")
        assert retrieved is belief
    
    def test_get_belief_by_formula_not_found(self):
        """Test retrieving non-existent belief by formula returns None."""
        kb = BeliefBase()
        retrieved = kb.get_belief_by_formula("P & Q")
        assert retrieved is None
    
    def test_get_belief_by_formula_with_whitespace(self):
        """Test retrieving belief by formula with different whitespace."""
        kb = BeliefBase()
        belief = kb.create_belief("P & Q", priority=1)
        kb.add_belief(belief)
        
        retrieved = kb.get_belief_by_formula("P&Q")
        assert retrieved is belief


class TestPriority:
    """Test priority handling."""
    
    def test_beliefs_with_different_priorities(self):
        """Test creating beliefs with different priorities."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P", priority=5)
        belief2 = kb.create_belief("Q", priority=10)
        belief3 = kb.create_belief("R", priority=1)
        
        assert belief1.priority == 5
        assert belief2.priority == 10
        assert belief3.priority == 1
    
    def test_priority_preserved_after_adding(self):
        """Test that priority is preserved when adding to base."""
        kb = BeliefBase()
        belief = kb.create_belief("P", priority=42)
        kb.add_belief(belief)
        
        retrieved = kb.get_belief_by_formula("P")
        assert retrieved.priority == 42
    
    def test_priority_preserved_after_copying(self):
        """Test that priority is preserved when copying base."""
        kb1 = BeliefBase()
        belief1 = kb1.create_belief("P", priority=42)
        kb1.add_belief(belief1)
        
        kb2 = kb1.copy_kb()
        retrieved = kb2.get_belief_by_formula("P")
        assert retrieved.priority == 42


class TestEdgeCases:
    """Test edge cases and corner scenarios."""
    
    def test_add_belief_with_duplicate_id_raises_error(self):
        """Test that adding a belief with duplicate id raises ValueError."""
        kb = BeliefBase()
        belief1 = kb.create_belief("P", priority=1)
        kb.add_belief(belief1)
        
        # Try to manually add a belief with the same id
        belief2_copy = Belief(
            id=belief1.id,  # Same id
            formula_str="Q",
            normalized_formula_str="Q",
            formula_ast=parse("Q"),
            priority=2,
            insertion_order=1
        )
        
        with pytest.raises(ValueError):
            kb.add_belief(belief2_copy)
    
    def test_large_belief_base(self):
        """Test creating and managing a large belief base."""
        kb = BeliefBase()
        n = 100
        
        for i in range(n):
            belief = kb.create_belief(f"P{i}", priority=i % 10)
            kb.add_belief(belief)
        
        assert kb.size() == n
        beliefs = kb.list_beliefs()
        assert len(beliefs) == n
    
    def test_belief_with_very_complex_formula(self):
        """Test handling very complex formulas."""
        kb = BeliefBase()
        # Build a deeply nested formula
        complex_formula = "((((P -> Q) & (Q -> R)) | S) <-> (T & (U | (V & W))))"
        belief = kb.create_belief(complex_formula, priority=1)
        kb.add_belief(belief)
        
        assert kb.size() == 1
        assert kb.contains_formula(complex_formula)
