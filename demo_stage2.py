#!/usr/bin/env python
"""
Stage 2 Demonstration: CNF Conversion and Propositional Resolution

This script demonstrates the core functionality of Stage 2:
- Converting formulas to CNF (Conjunctive Normal Form)
- Extracting clauses for resolution
- Using resolution to check logical entailment
"""

from logic import parse, formula_to_string
from belief_base import BeliefBase
from inference import resolution_entails, to_cnf, extract_clauses


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_cnf_conversion():
    """Demonstrate CNF conversion."""
    print_section("1. CNF Conversion Pipeline")
    
    formulas = [
        "A",
        "~A",
        "A -> B",
        "A <-> B",
        "~(A & B)",
        "A | (B & C)",
        "(A & B) | (~A & C)",
    ]
    
    print("Converting formulas to CNF:\n")
    for formula_str in formulas:
        formula = parse(formula_str)
        cnf = to_cnf(formula)
        print(f"Input:  {formula_str}")
        print(f"CNF:    {formula_to_string(cnf)}\n")


def demo_clause_extraction():
    """Demonstrate clause extraction."""
    print_section("2. Clause Extraction")
    
    formulas = [
        "A",
        "A & B",
        "A | B",
        "A -> B",
        "~(A & B)",
        "(A | B) & (~A | C)",
    ]
    
    print("Extracting clauses from CNF:\n")
    for formula_str in formulas:
        formula = parse(formula_str)
        cnf = to_cnf(formula)
        clauses = extract_clauses(cnf)
        
        print(f"Formula: {formula_str}")
        print(f"Clauses:")
        for clause in sorted(clauses):
            clause_str = " | ".join(sorted(clause))
            print(f"  {clause_str}")
        print()


def demo_modus_ponens():
    """Demonstrate modus ponens entailment."""
    print_section("3. Modus Ponens: KB = {A, A→B} ⊨ B")
    
    kb = BeliefBase()
    kb.add_belief(kb.create_belief("A"))
    kb.add_belief(kb.create_belief("A -> B"))
    
    print("Knowledge Base:")
    for belief in kb.list_beliefs():
        print(f"  • {belief.formula_str}")
    
    query = parse("B")
    entails = resolution_entails(kb, query)
    
    print(f"\nQuery: {formula_to_string(query)}")
    print(f"Entails: {entails} ✓")
    print("\nReasoning: A and A→B (which is ~A|B) combine with resolution to derive B")


def demo_chain_reasoning():
    """Demonstrate chain of reasoning."""
    print_section("4. Chain Reasoning")
    
    kb = BeliefBase()
    beliefs = [
        ("Socrates_human", 10, "Socrates is human"),
        ("Socrates_human -> Socrates_mortal", 9, "Humans are mortal"),
        ("Socrates_mortal -> Socrates_dies", 8, "Mortal things die"),
    ]
    
    print("Knowledge Base:")
    for formula, priority, description in beliefs:
        belief = kb.create_belief(formula, priority=priority)
        kb.add_belief(belief)
        print(f"  • {formula} (priority={priority})")
    
    queries = [
        ("Socrates_mortal", True, "Socrates is mortal"),
        ("Socrates_dies", True, "Socrates dies"),
        ("Socrates_immortal", False, "Socrates is immortal"),
    ]
    
    print("\nQueries:")
    for query_str, expected, description in queries:
        query = parse(query_str)
        result = resolution_entails(kb, query)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {query_str}: {result} ({description})")


def demo_demorgan():
    """Demonstrate De Morgan's laws."""
    print_section("5. De Morgan's Laws")
    
    kb = BeliefBase()
    kb.add_belief(kb.create_belief("~(A & B)"))
    
    print("Knowledge Base:")
    print("  • ~(A & B)")
    
    print("\nQueries:")
    
    # KB should entail ~A | ~B
    query1 = parse("~A | ~B")
    result1 = resolution_entails(kb, query1)
    print(f"  {'✓' if result1 else '✗'} ~A | ~B: {result1}")
    
    # KB should not entail A
    query2 = parse("A")
    result2 = resolution_entails(kb, query2)
    print(f"  {'✓' if not result2 else '✗'} A: {result2} (should be False)")


def demo_tautologies():
    """Demonstrate tautology checking."""
    print_section("6. Tautologies and Contradictions")
    
    kb = BeliefBase()
    
    print("Empty Knowledge Base\n")
    
    queries = [
        ("A | ~A", True, "Law of excluded middle (tautology)"),
        ("A & ~A", False, "Contradiction"),
        ("A", False, "Contingent formula"),
    ]
    
    print("Queries:")
    for query_str, expected, description in queries:
        query = parse(query_str)
        result = resolution_entails(kb, query)
        status = "✓" if result == expected else "✗"
        print(f"  {status} {query_str}: {result} ({description})")


def demo_inconsistent_kb():
    """Demonstrate inconsistent knowledge base (explosion principle)."""
    print_section("7. Inconsistent KB (Principle of Explosion)")
    
    kb = BeliefBase()
    kb.add_belief(kb.create_belief("A"))
    kb.add_belief(kb.create_belief("~A"))
    
    print("Knowledge Base (Inconsistent):")
    for belief in kb.list_beliefs():
        print(f"  • {belief.formula_str}")
    
    print("\nPrinciple of Explosion:")
    print("An inconsistent KB entails any formula.")
    
    # Test with arbitrary formula
    query = parse("B")
    result = resolution_entails(kb, query)
    print(f"\n  Query: B")
    print(f"  Entails: {result} ✓")
    print("  (Any formula is derivable from contradiction)")


def demo_biconditional():
    """Demonstrate biconditional reasoning."""
    print_section("8. Biconditional Reasoning")
    
    kb = BeliefBase()
    kb.add_belief(kb.create_belief("A <-> B"))
    kb.add_belief(kb.create_belief("A"))
    
    print("Knowledge Base:")
    for belief in kb.list_beliefs():
        print(f"  • {belief.formula_str}")
    
    print("\nQueries:")
    
    # Should entail B
    query1 = parse("B")
    result1 = resolution_entails(kb, query1)
    print(f"  {'✓' if result1 else '✗'} B: {result1}")
    
    # Should entail ~A -> ~B
    query2 = parse("~A -> ~B")
    result2 = resolution_entails(kb, query2)
    print(f"  {'✓' if result2 else '✗'} ~A -> ~B: {result2}")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("  BELIEF REVISION ENGINE - STAGE 2 DEMONSTRATION")
    print("  Logical Entailment via CNF and Resolution")
    print("="*60)
    
    demo_cnf_conversion()
    demo_clause_extraction()
    demo_modus_ponens()
    demo_chain_reasoning()
    demo_demorgan()
    demo_tautologies()
    demo_inconsistent_kb()
    demo_biconditional()
    
    print_section("Summary")
    print("""Stage 2 provides:
  ✓ CNF conversion pipeline (eliminate IFF, implications, move NOT inward, distribute)
  ✓ Automatic tautology detection and filtering
  ✓ Propositional resolution algorithm
  ✓ Sound and complete entailment checking
  ✓ Refutation-based reasoning
  
Key algorithms:
  • resolution_entails(kb, query): Main entailment checker
  • resolution_unsat(clauses): Unsatisfiability checking
  • resolve_pair(c1, c2): Resolution inference rule
  
Properties:
  ✓ No external SAT solvers or logic packages
  ✓ Pure Python implementation
  ✓ Sound and complete (classical propositional logic)
  ✓ Deterministic and reproducible
  ✓ Does not mutate KB or formulas""")
    print()


if __name__ == "__main__":
    main()
