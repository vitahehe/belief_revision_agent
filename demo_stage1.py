#!/usr/bin/env python
"""
Stage 1 Demonstration: Belief Base System

This script demonstrates the core functionality of Stage 1:
- Parsing formulas
- Creating and managing beliefs
- Duplicate detection
- Copying and independence
"""

from logic import parse, formula_to_string, get_symbols, normalize_formula
from belief_base import BeliefBase


def print_section(title):
    """Print a formatted section header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def demo_parsing():
    """Demonstrate formula parsing and AST manipulation."""
    print_section("1. Formula Parsing")
    
    formulas = [
        "P",
        "~P",
        "P & Q",
        "P | Q",
        "P -> Q",
        "P <-> Q",
        "(P & Q) | R",
        "P -> Q -> R",
        "~(P & Q) <-> (~P | ~Q)",
    ]
    
    print("Parsing formulas:")
    for formula_str in formulas:
        try:
            ast = parse(formula_str)
            print(f"  ✓ {formula_str:25} → AST: {ast}")
        except Exception as e:
            print(f"  ✗ {formula_str:25} → Error: {e}")


def demo_normalization():
    """Demonstrate formula normalization."""
    print_section("2. Formula Normalization & Deduplication")
    
    equivalent_pairs = [
        ("P & Q", "P&Q"),
        ("P & Q", "(P & Q)"),
        ("P | Q & R", "(P | (Q & R))"),
        ("P -> Q -> R", "P -> (Q -> R)"),
    ]
    
    print("Normalization ensures equivalent formulas are recognized:")
    for f1, f2 in equivalent_pairs:
        ast1 = parse(f1)
        ast2 = parse(f2)
        norm1 = normalize_formula(ast1)
        norm2 = normalize_formula(ast2)
        match = "✓" if norm1 == norm2 else "✗"
        print(f"  {match} {f1:20} and {f2:20}")
        print(f"      → {norm1} (identical: {norm1 == norm2})")


def demo_belief_base_basics():
    """Demonstrate basic belief base operations."""
    print_section("3. Belief Base: Creation and Management")
    
    kb = BeliefBase()
    print(f"Created empty belief base (size: {kb.size()})\n")
    
    # Add beliefs with different priorities
    beliefs_data = [
        ("P", 5, "Basic fact P"),
        ("Q", 8, "More entrenched fact Q"),
        ("P & Q -> R", 10, "Highly entrenched rule"),
        ("S | T", 1, "Weakly held disjunction"),
    ]
    
    print("Adding beliefs with priorities:")
    for formula, priority, description in beliefs_data:
        belief = kb.create_belief(formula, priority=priority)
        kb.add_belief(belief)
        print(f"  ✓ Added: {formula:15} (priority={priority:2}) - {description}")
    
    print(f"\nBelief base size: {kb.size()}")
    
    print("\nAll beliefs (in insertion order):")
    for belief in kb.list_beliefs():
        print(f"  • Formula: {belief.formula_str:20} Priority: {belief.priority:2} Order: {belief.insertion_order}")


def demo_duplicate_detection():
    """Demonstrate duplicate detection."""
    print_section("4. Duplicate Detection")
    
    kb = BeliefBase()
    
    print("Adding belief: 'P & Q'")
    belief1 = kb.create_belief("P & Q", priority=5)
    result1 = kb.add_belief(belief1)
    print(f"  Result: {result1} (size: {kb.size()})\n")
    
    duplicate_attempts = [
        ("P&Q", "Same formula, no whitespace"),
        ("P  &  Q", "Same formula, extra whitespace"),
        ("(P & Q)", "Same formula, extra parentheses"),
    ]
    
    print("Attempting to add duplicates:")
    for formula, reason in duplicate_attempts:
        belief = kb.create_belief(formula, priority=10)
        result = kb.add_belief(belief)
        status = "✓ Detected as duplicate" if not result else "✗ Allowed (BUG)"
        print(f"  {status}: '{formula}' ({reason})")
        print(f"       Size unchanged: {kb.size()}")
    
    print("\nAdding different formula: 'P | Q'")
    belief_new = kb.create_belief("P | Q", priority=7)
    result_new = kb.add_belief(belief_new)
    print(f"  Result: {result_new} (size now: {kb.size()}) ✓")


def demo_copying():
    """Demonstrate independent copying."""
    print_section("5. Independent Copying (Copy-on-Write)")
    
    kb1 = BeliefBase()
    
    # Add some beliefs
    beliefs = [("A", 1), ("B", 2), ("C", 3)]
    for formula, priority in beliefs:
        b = kb1.create_belief(formula, priority=priority)
        kb1.add_belief(b)
    
    print(f"Original KB size: {kb1.size()}")
    print(f"Original beliefs: {[b.formula_str for b in kb1.list_beliefs()]}\n")
    
    # Make a copy
    kb2 = kb1.copy_kb()
    print(f"Copied KB size: {kb2.size()}")
    print(f"Copied beliefs: {[b.formula_str for b in kb2.list_beliefs()]}\n")
    
    # Modify the copy
    belief_to_remove = kb2.list_beliefs()[0]
    kb2.remove_belief_by_id(belief_to_remove.id)
    print(f"Removed '{belief_to_remove.formula_str}' from copy")
    print(f"Copy size now: {kb2.size()}")
    print(f"Original KB size: {kb1.size()} ✓ (unchanged)\n")
    
    print("Independence verified:")
    print(f"  Original: {[b.formula_str for b in kb1.list_beliefs()]}")
    print(f"  Copy:     {[b.formula_str for b in kb2.list_beliefs()]}")


def demo_utils():
    """Demonstrate utility functions."""
    print_section("6. Utility Functions")
    
    formulas = [
        "~(P & Q)",
        "(P -> Q) & (Q -> R)",
        "P | Q | R | S",
    ]
    
    print("Formula analysis utilities:\n")
    for formula_str in formulas:
        ast = parse(formula_str)
        symbols = get_symbols(ast)
        normalized = normalize_formula(ast)
        
        print(f"Formula: {formula_str}")
        print(f"  Symbols: {sorted(symbols)}")
        print(f"  Normalized: {normalized}\n")


def demo_priority_system():
    """Demonstrate priority-based entrenchment."""
    print_section("7. Priority-Based Entrenchment")
    
    kb = BeliefBase()
    
    formulas_with_priorities = [
        ("I", 100, "Core fact - very hard to revise"),
        ("M", 90, "Mathematical truth - highly entrenched"),
        ("S", 80, "Scientific fact - well-established"),
        ("P", 20, "Personal preference - easily revised"),
        ("T", 5, "Tentative - very weakly held"),
    ]
    
    print("Adding beliefs with different entrenchment levels:\n")
    for formula, priority, description in formulas_with_priorities:
        belief = kb.create_belief(formula, priority=priority)
        kb.add_belief(belief)
        entrenchment = "█" * (priority // 10) + "░" * (10 - priority // 10)
        print(f"  Priority {priority:3} [{entrenchment}] {formula:3} - {description}")
    
    print("\nWhen contracting, lower priority beliefs would be removed first.")


def main():
    """Run all demonstrations."""
    print("\n" + "="*60)
    print("  BELIEF REVISION ENGINE - STAGE 1 DEMONSTRATION")
    print("="*60)
    
    demo_parsing()
    demo_normalization()
    demo_belief_base_basics()
    demo_duplicate_detection()
    demo_copying()
    demo_utils()
    demo_priority_system()
    
    print_section("Summary")
    print("""Stage 1 provides:
  ✓ Propositional logic parsing with full operator support
  ✓ Immutable AST representation
  ✓ Deterministic formula normalization
  ✓ Efficient duplicate detection
  ✓ Priority-based belief entrenchment
  ✓ Copy-on-write semantics for non-destructive revisions
  
All components are compatible with future stages (CNF, Resolution, 
Contraction, Expansion, and AGM belief revision operations).""")
    print()


if __name__ == "__main__":
    main()
