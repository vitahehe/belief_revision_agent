# Priority-based contraction (what was added)

this repo previously treated a knowledge base as just `list[Sentence]`.  
to support the assignment requirement “contraction based on priority order”, i added a lightweight belief-record layer on top of CNF + resolution.

# What changed (files)
- `KnowledgeBase.py`
  - Added `BeliefEntry` records (formula + metadata).
  - Upgraded `KnowledgeBase` to store `entries` (belief records) while keeping `sentences` (plain formulas) for backwards compatibility.
  - Added belief-change operations: `expand`, `contract`, `revise`.
  - Added helpers to expose CNF as a clause-set/list: `to_clause_set`, `to_clause_list`.
- `test/test_contraction.py`: unit tests for priority removal and tie-breaking.
- `test/test_postulates.py`: tests for core postulates (success/inclusion/vacuity/extensionality + revision success/consistency). (done on a whim dont know if it makes sense ^_^)

# data model added
Each stored belief is a `BeliefEntry`:
- `id`: e.g. `"b3"` (useful for reporting removals)
- `sentence` / `formula_ast`: the `Sentence` AST
- `priority`: higher = more entrenched (removed later)
- `insertion_order`: tie-breaker; if same priority, remove newest first
- `normalized_formula_str`: used to avoid duplicates on expansion

`KnowledgeBase` now has:
- `kb.entries: list[BeliefEntry]` (storage for belief change)
- `kb.sentences: list[Sentence]` (kept for inference modules/tests)

# Operations adde
- Entailment: `kb.entails(query)`  
  Uses existing resolution refutates (CNF → clauses → resolution). This supports indirect entailment (e.g. \(A, A→B ⊨ B\)).

- Expansion: `kb.expand(phi, priority)`  
  Adds `phi` unless it’s a duplicate.

- Contraction: `kb.contract(phi)`  
  If \(KB ⊨ φ\), remove beliefs until \(KB ⊭ φ\).  
  Removal order:
  1. lowest `priority` first
  2. tie-break: highest `insertion_order` first (newest first)

- Revision: `kb.revise(phi, priority)`  
  Implements Levi identity:
  \[
  KB * φ = (KB ÷ ¬φ) + φ
  \]

# Clause view (optional helper)
If you want the KB as explicit CNF clauses:
- `kb.to_clause_set() -> set[frozenset[str]]`
- `kb.to_clause_list() -> list[frozenset[str]]` (deterministic ordering)