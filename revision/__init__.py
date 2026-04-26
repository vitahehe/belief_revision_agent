"""Belief revision utilities for the belief revision agent."""

from revision.contraction import (
    contract,
    contract_with_summary,
    select_beliefs_for_removal,
    sort_beliefs_by_removability,
    would_still_entail_after_removal,
)

__all__ = [
    "contract",
    "contract_with_summary",
    "select_beliefs_for_removal",
    "sort_beliefs_by_removability",
    "would_still_entail_after_removal",
]
