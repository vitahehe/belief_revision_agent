"""
Tests for the parser module.

Tests parsing of atoms, negations, conjunctions, disjunctions, implications, and biconditionals.
Also tests operator precedence and parenthesization.
"""

import pytest
from logic.ast import Atom, Not, And, Or, Implies, Biconditional, Formula
from logic.parser import parse, ParseError


class TestParseAtoms:
    """Test parsing of atomic propositions."""
    
    def test_parse_simple_atom(self):
        """Test parsing a simple atom."""
        result = parse("P")
        assert isinstance(result, Atom)
        assert result.name == "P"
    
    def test_parse_atom_with_underscores(self):
        """Test parsing atoms with underscores."""
        result = parse("P_1")
        assert isinstance(result, Atom)
        assert result.name == "P_1"
    
    def test_parse_atom_with_numbers(self):
        """Test parsing atoms with alphanumeric characters."""
        result = parse("Proposition123")
        assert isinstance(result, Atom)
        assert result.name == "Proposition123"
    
    def test_parse_lowercase_atom(self):
        """Test parsing lowercase atoms."""
        result = parse("p")
        assert isinstance(result, Atom)
        assert result.name == "p"


class TestParseNegation:
    """Test parsing negation expressions."""
    
    def test_parse_simple_negation(self):
        """Test parsing negation of an atom."""
        result = parse("~P")
        assert isinstance(result, Not)
        assert isinstance(result.child, Atom)
        assert result.child.name == "P"
    
    def test_parse_double_negation(self):
        """Test parsing double negation."""
        result = parse("~~P")
        assert isinstance(result, Not)
        assert isinstance(result.child, Not)
        assert isinstance(result.child.child, Atom)
        assert result.child.child.name == "P"
    
    def test_parse_negation_of_conjunction(self):
        """Test parsing negation of a conjunction."""
        result = parse("~(P & Q)")
        assert isinstance(result, Not)
        assert isinstance(result.child, And)


class TestParseConjunction:
    """Test parsing conjunction expressions."""
    
    def test_parse_simple_conjunction(self):
        """Test parsing a simple conjunction."""
        result = parse("P & Q")
        assert isinstance(result, And)
        assert isinstance(result.left, Atom)
        assert isinstance(result.right, Atom)
        assert result.left.name == "P"
        assert result.right.name == "Q"
    
    def test_parse_multiple_conjunctions(self):
        """Test parsing multiple conjunctions are left-associative."""
        result = parse("P & Q & R")
        # P & (Q & R) with left-associativity becomes (P & Q) & R
        assert isinstance(result, And)
        assert isinstance(result.left, And)
        assert isinstance(result.right, Atom)
        assert result.left.left.name == "P"
        assert result.left.right.name == "Q"
        assert result.right.name == "R"


class TestParseDisjunction:
    """Test parsing disjunction expressions."""
    
    def test_parse_simple_disjunction(self):
        """Test parsing a simple disjunction."""
        result = parse("P | Q")
        assert isinstance(result, Or)
        assert isinstance(result.left, Atom)
        assert isinstance(result.right, Atom)
        assert result.left.name == "P"
        assert result.right.name == "Q"
    
    def test_parse_multiple_disjunctions(self):
        """Test parsing multiple disjunctions."""
        result = parse("P | Q | R")
        assert isinstance(result, Or)
        assert isinstance(result.left, Or)
        assert isinstance(result.right, Atom)


class TestParseImplication:
    """Test parsing implication expressions."""
    
    def test_parse_simple_implication(self):
        """Test parsing a simple implication."""
        result = parse("P -> Q")
        assert isinstance(result, Implies)
        assert isinstance(result.left, Atom)
        assert isinstance(result.right, Atom)
        assert result.left.name == "P"
        assert result.right.name == "Q"
    
    def test_parse_implication_right_associative(self):
        """Test that implications are right-associative."""
        result = parse("P -> Q -> R")
        assert isinstance(result, Implies)
        assert isinstance(result.left, Atom)
        assert isinstance(result.right, Implies)
        assert result.right.left.name == "Q"
        assert result.right.right.name == "R"


class TestParseBiconditional:
    """Test parsing biconditional expressions."""
    
    def test_parse_simple_biconditional(self):
        """Test parsing a simple biconditional."""
        result = parse("P <-> Q")
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Atom)
        assert isinstance(result.right, Atom)
        assert result.left.name == "P"
        assert result.right.name == "Q"
    
    def test_parse_multiple_biconditionals(self):
        """Test parsing multiple biconditionals are right-associative."""
        result = parse("P <-> Q <-> R")
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Atom)
        assert isinstance(result.right, Biconditional)


class TestOperatorPrecedence:
    """Test that operators have correct precedence."""
    
    def test_negation_higher_than_conjunction(self):
        """Test that negation binds tighter than conjunction."""
        # ~P & Q should parse as (~P) & Q not ~(P & Q)
        result = parse("~P & Q")
        assert isinstance(result, And)
        assert isinstance(result.left, Not)
        assert isinstance(result.right, Atom)
    
    def test_conjunction_higher_than_disjunction(self):
        """Test that conjunction binds tighter than disjunction."""
        # P & Q | R should parse as (P & Q) | R not P & (Q | R)
        result = parse("P & Q | R")
        assert isinstance(result, Or)
        assert isinstance(result.left, And)
        assert isinstance(result.right, Atom)
    
    def test_disjunction_higher_than_implication(self):
        """Test that disjunction binds tighter than implication."""
        # P | Q -> R should parse as (P | Q) -> R
        result = parse("P | Q -> R")
        assert isinstance(result, Implies)
        assert isinstance(result.left, Or)
    
    def test_implication_higher_than_biconditional(self):
        """Test that implication binds tighter than biconditional."""
        # P -> Q <-> R should parse as (P -> Q) <-> R
        result = parse("P -> Q <-> R")
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Implies)
    
    def test_complex_precedence(self):
        """Test complex precedence with multiple operators."""
        # ~P & Q | R -> S <-> T
        result = parse("~P & Q | R -> S <-> T")
        assert isinstance(result, Biconditional)
        assert isinstance(result.left, Implies)
        assert isinstance(result.left.left, Or)
        assert isinstance(result.left.left.left, And)
        assert isinstance(result.left.left.left.left, Not)


class TestParentheses:
    """Test that parentheses override precedence."""
    
    def test_parentheses_override_conjunction_disjunction(self):
        """Test parentheses override precedence of & and |."""
        result = parse("P | (Q & R)")
        assert isinstance(result, Or)
        assert isinstance(result.right, And)
    
    def test_parentheses_override_negation(self):
        """Test parentheses around negated formula."""
        result = parse("~(P & Q)")
        assert isinstance(result, Not)
        assert isinstance(result.child, And)
    
    def test_nested_parentheses(self):
        """Test nested parentheses."""
        result = parse("((P & Q) | R)")
        assert isinstance(result, Or)
        assert isinstance(result.left, And)


class TestWhitespace:
    """Test parsing with various whitespace."""
    
    def test_no_whitespace(self):
        """Test parsing with no whitespace."""
        result = parse("P&Q|R")
        assert isinstance(result, Or)
    
    def test_extra_whitespace(self):
        """Test parsing with extra whitespace."""
        result = parse("P  &  Q  |  R")
        assert isinstance(result, Or)
    
    def test_whitespace_around_operators(self):
        """Test parsing with whitespace around operators."""
        result = parse("P & Q -> R <-> S")
        assert isinstance(result, Biconditional)


class TestInvalidFormulas:
    """Test that invalid formulas raise ParseError."""
    
    def test_empty_string(self):
        """Test that empty string raises ParseError."""
        with pytest.raises(ParseError):
            parse("")
    
    def test_only_operator(self):
        """Test that only an operator raises ParseError."""
        with pytest.raises(ParseError):
            parse("&")
    
    def test_missing_right_operand(self):
        """Test that missing right operand raises ParseError."""
        with pytest.raises(ParseError):
            parse("P &")
    
    def test_missing_left_operand(self):
        """Test that missing left operand raises ParseError."""
        with pytest.raises(ParseError):
            parse("& P")
    
    def test_unmatched_left_paren(self):
        """Test that unmatched left parenthesis raises ParseError."""
        with pytest.raises(ParseError):
            parse("(P & Q")
    
    def test_unmatched_right_paren(self):
        """Test that unmatched right parenthesis raises ParseError."""
        with pytest.raises(ParseError):
            parse("P & Q)")
    
    def test_invalid_character(self):
        """Test that invalid characters raise ParseError."""
        with pytest.raises(ParseError):
            parse("P & Q $")
    
    def test_consecutive_operators(self):
        """Test that consecutive operators raise ParseError."""
        with pytest.raises(ParseError):
            parse("P & & Q")
    
    def test_empty_parentheses(self):
        """Test that empty parentheses raise ParseError."""
        with pytest.raises(ParseError):
            parse("()")
    
    def test_trailing_operator(self):
        """Test that trailing operator raises ParseError."""
        with pytest.raises(ParseError):
            parse("P -> Q ->")


class TestComplexFormulas:
    """Test parsing of complex realistic formulas."""
    
    def test_deMorgans_law_1(self):
        """Test parsing De Morgan's law: ~(P & Q) equiv (~P | ~Q)."""
        formula1 = parse("~(P & Q)")
        formula2 = parse("~P | ~Q")
        assert isinstance(formula1, Not)
        assert isinstance(formula2, Or)
    
    def test_conditional_with_nested_disjunction(self):
        """Test parsing (P | Q) -> R."""
        result = parse("(P | Q) -> R")
        assert isinstance(result, Implies)
        assert isinstance(result.left, Or)
    
    def test_biconditional_definition(self):
        """Test parsing (P -> Q) & (Q -> P) equiv (P <-> Q)."""
        result = parse("(P -> Q) & (Q -> P)")
        assert isinstance(result, And)
        assert isinstance(result.left, Implies)
        assert isinstance(result.right, Implies)
    
    def test_hypothetical_syllogism(self):
        """Test parsing (P -> Q) & (Q -> R) -> (P -> R)."""
        result = parse("(P -> Q) & (Q -> R) -> (P -> R)")
        assert isinstance(result, Implies)
        assert isinstance(result.left, And)
        assert isinstance(result.right, Implies)
