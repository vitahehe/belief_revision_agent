"""Priority-based belief contraction for propositional belief bases."""

from typing import List, Tuple
from belief_base import BeliefBase
from belief_base.models import Belief
from logic.parser import parse, ParseError
from inference import resolution_entails
from logic.ast import Formula


def sort_beliefs_by_removability(beliefs: List[Belief]) -> List[Belief]:
    """Sort beliefs by how easily they should be removed during contraction.

    Lower priority beliefs are removed first. When priorities are equal, the newer
    belief (higher insertion_order) is removed before older ones.
    """
    return sorted(beliefs, key=lambda b: (b.priority, -b.insertion_order))


def would_still_entail_after_removal(kb: BeliefBase, belief_id: str, formula_ast: Formula) -> bool:
    """Return whether the KB still entails formula_ast after removing one belief.

    The original KB is not modified.
    """
    copied_kb = kb.copy_kb()
    copied_kb.remove_belief_by_id(belief_id)
    return resolution_entails(copied_kb, formula_ast)


def select_beliefs_for_removal(kb: BeliefBase, formula_ast: Formula) -> List[Belief]:
    """Select beliefs to remove so the KB no longer entails the target formula.

    If the KB does not entail formula_ast, no beliefs are selected. If removing
    all beliefs still does not eliminate entailment (for example, a tautology),
    the function returns an empty list to preserve the original KB.
    """
    if not resolution_entails(kb, formula_ast):
        return []

    working_kb = kb.copy_kb()
    beliefs_to_remove: List[Belief] = []
    sorted_beliefs = sort_beliefs_by_removability(working_kb.list_beliefs())

    for belief in sorted_beliefs:
        working_kb.remove_belief_by_id(belief.id)
        beliefs_to_remove.append(belief)

        if not resolution_entails(working_kb, formula_ast):
            return beliefs_to_remove

    # If every belief is removed and the formula is still entailed, this is a
    # tautology or an entailment that cannot be contracted by ordinary belief
    # removal. Return empty list to preserve the original KB.
    return []


def contract_with_summary(kb: BeliefBase, formula_text: str) -> Tuple[BeliefBase, List[Belief]]:
    """Contract the belief base and return the contracted base plus removed beliefs."""
    formula_ast = parse(formula_text)
    removed_beliefs = select_beliefs_for_removal(kb, formula_ast)

    contracted_kb = kb.copy_kb()
    for belief in removed_beliefs:
        contracted_kb.remove_belief_by_id(belief.id)

    return contracted_kb, removed_beliefs


def contract(kb: BeliefBase, formula_text: str) -> BeliefBase:
    """Return a contracted copy of the belief base that no longer entails formula_text.

    Contraction is done by removing beliefs according to epistemic entrenchment:
    lower-priority beliefs are removed first, and equal-priority beliefs are
    resolved by removing the newest belief first.
    """
    formula_ast = parse(formula_text)
    removed_beliefs = select_beliefs_for_removal(kb, formula_ast)

    contracted_kb = kb.copy_kb()
    for belief in removed_beliefs:
        contracted_kb.remove_belief_by_id(belief.id)

    return contracted_kb
