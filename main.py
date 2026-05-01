from KnowledgeBase import KnowledgeBase, BeliefEntry
from Sentence import Atom, Not, Implies, And, Or, Biconditional


def _print_beliefs(title: str, beliefs: list[BeliefEntry]) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    if not beliefs:
        print("  (none)")
        return
    for b in beliefs:
        print(
            f"  {b.id}: formula={b.formula_str}, "
            f"priority={b.priority}, insertion_order={b.insertion_order}"
        )


def run_demo_basic() -> None:
    print("Belief Revision Engine Demo (Basic)")
    
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
    ]
    kb = KnowledgeBase(entries=entries)

    _print_beliefs("Initial belief base", kb.list_beliefs())
    print(f"\nInitial entailment checks:")
    print(f"  entails(B): {kb.entails(Atom('B'))}")
    print(f"  entails(~B): {kb.entails(Not(Atom('B')))}")

    phi = Not(Atom("B"))
    print(f"\nRevision request:")
    print(f"  phi = {phi}")
    print(f"  Using pipeline: KB * phi = (KB ÷ ~phi) + phi")
    print(f"  So contraction target is: ~phi = {Not(phi)}")

    revised_kb, removed, added = kb.revise(phi, priority=3)

    _print_beliefs("Removed during contraction", removed)
    _print_beliefs("Final belief base after revision", revised_kb.list_beliefs())

    print("\nRevision summary")
    
    if added is None:
        print("  Added belief: (none; phi already present)")
    else:
        print(f"  Added belief: {added.id} -> {added.formula_str}")

    print("\nPost-revision entailment checks:")
    print(f"  entails(phi = ~B): {revised_kb.entails(phi)}")
    print(f"  entails(B): {revised_kb.entails(Atom('B'))}")


def run_demo_advanced() -> None:
    print("\nBelief Revision Engine Demo (Advanced)")

    print("Scenario: larger KB with multiple support chains and mixed operators.")

    
    entries = [
        BeliefEntry(belief_id="b1", sentence=Atom("A"), priority=5, insertion_order=0),
        BeliefEntry(belief_id="b2", sentence=Implies(Atom("A"), Atom("B")), priority=3, insertion_order=1),
        BeliefEntry(belief_id="b3", sentence=Implies(Atom("B"), Atom("K")), priority=1, insertion_order=2),
        BeliefEntry(belief_id="b4", sentence=Atom("D"), priority=4, insertion_order=3),
        BeliefEntry(belief_id="b5", sentence=Implies(Atom("D"), Atom("E")), priority=2, insertion_order=4),
        BeliefEntry(belief_id="b6", sentence=Implies(Atom("E"), Atom("K")), priority=1, insertion_order=5),
        BeliefEntry(
            belief_id="b7",
            sentence=Biconditional(Atom("M"), Atom("N")),
            priority=2,
            insertion_order=6,
        ),
        BeliefEntry(
            belief_id="b8",
            sentence=Or(Not(Atom("M")), Atom("N")),
            priority=1,
            insertion_order=7,
        ),
        BeliefEntry(
            belief_id="b9",
            sentence=And(Atom("P"), Atom("Q")),
            priority=2,
            insertion_order=8,
        ),
    ]
    kb = KnowledgeBase(entries=entries)
    _print_beliefs("Initial advanced belief base", kb.list_beliefs())

    k = Atom("K")
    print("\nInitial entailment checks:")
    print(f"  entails(K): {kb.entails(k)}")
    print(f"  entails(~K): {kb.entails(Not(k))}")

    phi = Not(k)
    print("\nRevision request:")
    print(f"  phi = {phi}")
    print("  Goal: force KB to accept ~K while preserving high-priority beliefs when possible.")

    revised_kb, removed, added = kb.revise(phi, priority=4)

    _print_beliefs("Removed during advanced contraction", removed)
    _print_beliefs("Final advanced belief base", revised_kb.list_beliefs())

    print("\nAdvanced revision summary")
    print(f"  beliefs removed: {len(removed)}")
    if added is None:
        print("  added belief: (none; phi already present)")
    else:
        print(f"  added belief: {added.id} -> {added.formula_str}")

    print("\nPost-revision entailment checks:")
    print(f"  entails(~K): {revised_kb.entails(Not(k))}")
    print(f"  entails(K): {revised_kb.entails(k)}")


def run_demo() -> None:
    print("Choose demo mode:")
    print("  1) Basic")
    print("  2) Advanced")
    
    choice = input("Enter choice [1/2]: ").strip()

    if choice == "1":
        run_demo_basic()
    elif choice == "2":
        run_demo_advanced()
    else:
        print("\nInvalid choice. Running basic demo by default.\n")
        run_demo_basic()


if __name__ == "__main__":
    run_demo()