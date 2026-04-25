"""Inference module for logical entailment checking."""

from inference.cnf import to_cnf, extract_clauses, is_tautological_clause
from inference.resolution import (
    resolution_entails,
    resolution_unsat,
    resolve_pair,
    negate_literal,
    are_complementary,
)
from inference.model_check import truth_table_entails, evaluate_formula

__all__ = [
    # CNF
    "to_cnf",
    "extract_clauses",
    "is_tautological_clause",
    # Resolution (main entailment method)
    "resolution_entails",
    "resolution_unsat",
    "resolve_pair",
    "negate_literal",
    "are_complementary",
    # Model checking (debugging only)
    "truth_table_entails",
    "evaluate_formula",
]
