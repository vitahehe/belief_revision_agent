import pytest

from Sentence import Atom, Implies
from KnowledgeBase import KnowledgeBase, BeliefEntry


def test_contract_no_entailment_no_change():
    kb = KnowledgeBase([Atom("A")])
    new_kb, removed = kb.contract(Atom("B"))
    assert removed == []
    assert [repr(s) for s in new_kb.sentences] == [repr(s) for s in kb.sentences]


def test_priority_based_contraction_removes_low_priority_first():
    # KB entails B from {A, (A -> B)}.
    # Contract by B: to break entailment, we should remove the lowest-priority belief first.
    a = Atom("A")
    a_implies_b = Implies(Atom("A"), Atom("B"))

    entries = [
        BeliefEntry(belief_id="b1", sentence=a, priority=5, insertion_order=0),
        BeliefEntry(belief_id="b2", sentence=a_implies_b, priority=1, insertion_order=1),
    ]
    kb = KnowledgeBase(entries=entries)

    new_kb, removed = kb.contract(Atom("B"))

    assert [e.id for e in removed] == ["b2"]
    assert new_kb.entails(Atom("B")) is False


def test_contraction_tie_breaker_removes_newest_first():
    # Same priority beliefs; newest should be removed first.
    # KB entails B from {A, (A -> B)}. We'll provide two different ways to support B,
    # and make the newest one the first candidate for removal.
    a = Atom("A")
    a_implies_b = Implies(Atom("A"), Atom("B"))

    entries = [
        BeliefEntry(belief_id="b1", sentence=a, priority=1, insertion_order=0),
        BeliefEntry(belief_id="b2", sentence=a_implies_b, priority=1, insertion_order=1),  # newest among ties
    ]
    kb = KnowledgeBase(entries=entries)

    new_kb, removed = kb.contract(Atom("B"))

    assert [e.id for e in removed] == ["b2"]
    assert new_kb.entails(Atom("B")) is False

