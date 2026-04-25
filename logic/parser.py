"""
Parser for propositional logic formulas.

Converts a string representation of a propositional logic formula to an AST.
Supports the following syntax:
  - Atoms: identifiers starting with letter or underscore
  - Negation: ~A
  - Conjunction: A & B
  - Disjunction: A | B
  - Implication: A -> B
  - Biconditional: A <-> B
  - Parentheses: (A & B)

Operator precedence (highest to lowest):
  1. ~ (negation)
  2. & (conjunction)
  3. | (disjunction)
  4. -> (implication)
  5. <-> (biconditional)
"""

from typing import List, Tuple, Optional
from logic.ast import Formula, Atom, Not, And, Or, Implies, Biconditional


class ParseError(Exception):
    """Raised when a string cannot be parsed as a valid formula."""
    pass


class Tokenizer:
    """Tokenizes a formula string into a list of tokens."""
    
    def __init__(self, text: str):
        self.text = text
        self.position = 0
        self.tokens: List[Tuple[str, str]] = []
        self._tokenize()
        self.position = 0  # Reset position after tokenization for peek/consume
    
    def _tokenize(self):
        """Tokenize the input text."""
        while self.position < len(self.text):
            char = self.text[self.position]
            
            # Skip whitespace
            if char.isspace():
                self.position += 1
                continue
            
            # Multi-character operators
            if self.position + 1 < len(self.text):
                two_char = self.text[self.position:self.position + 2]
                if two_char == "->":
                    self.tokens.append(("IMPLIES", "->"))
                    self.position += 2
                    continue
                elif two_char == "<-":
                    # Check for <->
                    if self.position + 2 < len(self.text) and self.text[self.position + 2] == ">":
                        self.tokens.append(("BICONDITIONAL", "<->"))
                        self.position += 3
                        continue
            
            # Single-character operators and delimiters
            if char == "~":
                self.tokens.append(("NOT", "~"))
                self.position += 1
            elif char == "&":
                self.tokens.append(("AND", "&"))
                self.position += 1
            elif char == "|":
                self.tokens.append(("OR", "|"))
                self.position += 1
            elif char == "(":
                self.tokens.append(("LPAREN", "("))
                self.position += 1
            elif char == ")":
                self.tokens.append(("RPAREN", ")"))
                self.position += 1
            elif char.isalpha() or char == "_":
                # Identifier (atom name)
                start = self.position
                while self.position < len(self.text) and (
                    self.text[self.position].isalnum() or self.text[self.position] == "_"
                ):
                    self.position += 1
                atom_name = self.text[start:self.position]
                self.tokens.append(("ATOM", atom_name))
            else:
                raise ParseError(f"Invalid character '{char}' at position {self.position}")
    
    def peek(self, offset: int = 0) -> Optional[Tuple[str, str]]:
        """Peek at a token without consuming it."""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    def consume(self) -> Optional[Tuple[str, str]]:
        """Consume and return the current token."""
        token = self.peek()
        if token:
            self.position += 1
        return token
    
    def expect(self, token_type: str) -> str:
        """Consume a token of the expected type or raise an error."""
        token = self.consume()
        if token is None or token[0] != token_type:
            raise ParseError(f"Expected {token_type}, got {token}")
        return token[1]


class Parser:
    """Recursive descent parser for propositional logic formulas."""
    
    def __init__(self, text: str):
        self.tokenizer = Tokenizer(text)
    
    def parse(self) -> Formula:
        """Parse the formula and return the AST root."""
        formula = self._parse_biconditional()
        
        # Ensure we consumed all tokens
        if self.tokenizer.peek() is not None:
            raise ParseError(f"Unexpected token: {self.tokenizer.peek()}")
        
        return formula
    
    def _parse_biconditional(self) -> Formula:
        """Parse biconditional (lowest precedence, right-associative)."""
        left = self._parse_implication()
        
        if self.tokenizer.peek() and self.tokenizer.peek()[0] == "BICONDITIONAL":
            self.tokenizer.consume()
            right = self._parse_biconditional()  # Right-associative recursion
            return Biconditional(left, right)
        
        return left
    
    def _parse_implication(self) -> Formula:
        """Parse implication (right-associative)."""
        left = self._parse_disjunction()
        
        if self.tokenizer.peek() and self.tokenizer.peek()[0] == "IMPLIES":
            self.tokenizer.consume()
            right = self._parse_implication()  # Right-associative recursion
            return Implies(left, right)
        
        return left
    
    def _parse_disjunction(self) -> Formula:
        """Parse disjunction."""
        left = self._parse_conjunction()
        
        while self.tokenizer.peek() and self.tokenizer.peek()[0] == "OR":
            self.tokenizer.consume()
            right = self._parse_conjunction()
            left = Or(left, right)
        
        return left
    
    def _parse_conjunction(self) -> Formula:
        """Parse conjunction."""
        left = self._parse_negation()
        
        while self.tokenizer.peek() and self.tokenizer.peek()[0] == "AND":
            self.tokenizer.consume()
            right = self._parse_negation()
            left = And(left, right)
        
        return left
    
    def _parse_negation(self) -> Formula:
        """Parse negation (highest precedence for operators)."""
        if self.tokenizer.peek() and self.tokenizer.peek()[0] == "NOT":
            self.tokenizer.consume()
            child = self._parse_negation()
            return Not(child)
        
        return self._parse_primary()
    
    def _parse_primary(self) -> Formula:
        """Parse primary expressions (atoms or parenthesized formulas)."""
        token = self.tokenizer.peek()
        
        if token is None:
            raise ParseError("Unexpected end of input")
        
        if token[0] == "ATOM":
            self.tokenizer.consume()
            return Atom(token[1])
        
        elif token[0] == "LPAREN":
            self.tokenizer.consume()
            formula = self._parse_biconditional()
            self.tokenizer.expect("RPAREN")
            return formula
        
        else:
            raise ParseError(f"Expected atom or '(', got {token}")


def parse(text: str) -> Formula:
    """Parse a formula string and return the AST.
    
    Args:
        text: The formula string to parse.
    
    Returns:
        The root Formula node of the AST.
    
    Raises:
        ParseError: If the formula string is invalid.
    """
    parser = Parser(text)
    return parser.parse()
