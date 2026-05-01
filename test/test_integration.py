from Sentence import Atom, Not, Implies
from KnowledgeBase import KnowledgeBase, BeliefEntry
from inference.cnf import to_cnf, extract_clauses
from inference.resolution import resolution_entails


def test_end_to_end_entailment_contract_expand_revision_flow():
    
    kb = KnowledgeBase([Atom("A"), Implies(Atom("A"), Atom("B"))])
    b = Atom("B")

    
    clause_set = kb.to_clause_set()
    assert frozenset({"A"}) in clause_set
    assert frozenset({"~A", "B"}) in clause_set

    
    assert resolution_entails(kb, b) is True

    
    contracted, removed = kb.contract(b)
    assert len(removed) >= 1
    assert contracted.entails(b) is False

    
    c = Atom("C")
    expanded = contracted.expand(c, priority=2)
    assert expanded.entails(c) is True

    
    revised, _, _ = expanded.revise(b, priority=3)
    assert revised.entails(b) is True


def test_end_to_end_contraction_priority_and_tie_breaking():
   
    entries = [
        BeliefEntry(
            belief_id="b1",
            sentence=Atom("A"),
            priority=5,
            insertion_order=0,
        ),
        BeliefEntry(
            belief_id="b2",
            sentence=Implies(Atom("A"), Atom("B")),
            priority=1,
            insertion_order=1,
        ),
        BeliefEntry(
            belief_id="b3",
            sentence=Implies(Atom("A"), Atom("B")),
            priority=1,
            insertion_order=2,  
        ),
    ]
    kb = KnowledgeBase(entries=entries)

    contracted, removed = kb.contract(Atom("B"))

    
    assert removed[0].id == "b3"
    
    assert removed[1].id == "b2"
    
    assert any(e.id == "b1" for e in contracted.entries)
    assert contracted.entails(Atom("B")) is False


def test_end_to_end_duplicate_handling_and_revision_summary():
    kb = KnowledgeBase([Atom("A")])

    
    expanded_same = kb.expand(Atom("A"), priority=10)
    assert len(expanded_same.entries) == len(kb.entries)
    assert [e.id for e in expanded_same.entries] == [e.id for e in kb.entries]

    
    revised, removed, added = kb.revise(Atom("B"), priority=4)
    assert revised.entails(Atom("B")) is True
    assert isinstance(removed, list)
    assert added is not None
    assert added.formula_str == repr(Atom("B"))

    
    neg_b_clauses = extract_clauses(to_cnf(Not(Atom("B"))))
    assert neg_b_clauses == {frozenset({"~B"})}


def test_end_to_end_inconsistent_kb_and_revision_determinism():
    
    kb = KnowledgeBase([Atom("A"), Not(Atom("A"))])
    query = Atom("B")
    assert kb.entails(query) is True

    
    revised, removed, added = kb.revise(query, priority=2)
    assert revised.entails(query) is True
    assert isinstance(removed, list)
    assert added is not None
    assert revised.contains_sentence(query) is True


def test_end_to_end_repeated_revision_is_duplicate_stable():
    kb = KnowledgeBase([Atom("A")])
    b = Atom("B")

    revised_once, _, _ = kb.revise(b, priority=3)
    count_after_once = sum(1 for e in revised_once.entries if e.normalized_formula_str == "B")
    assert count_after_once == 1

    revised_twice, _, _ = revised_once.revise(b, priority=3)
    count_after_twice = sum(1 for e in revised_twice.entries if e.normalized_formula_str == "B")
    assert count_after_twice == 1

    
    assert len(revised_twice.entries) == len(revised_once.entries)
