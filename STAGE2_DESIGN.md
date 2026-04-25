## Stage 2: Logical Entailment via CNF and Resolution

### Overview

This document describes Stage 2 of the belief revision engine: the implementation of logical entailment checking using Conjunctive Normal Form (CNF) conversion and propositional resolution.

The entailment check implements the **refutation principle**:
> **KB ⊨ query** iff **KB ∧ ¬query** is unsatisfiable

This module is self-contained and uses no external logic packages, SAT solvers, or theorem provers.

---

## Core Architecture

### 1. CNF Conversion Pipeline (inference/cnf.py)

The module converts arbitrary propositional logic formulas to CNF through a five-step pipeline:

#### Step 1: Eliminate Biconditionals
```
A <-> B  ≡  (A -> B) & (B -> A)
```
**Rule**: Replace all `Biconditional` nodes with conjunction of two implications.

#### Step 2: Eliminate Implications
```
A -> B  ≡  ~A | B
```
**Rule**: Replace all `Implies` nodes with disjunction of negated antecedent and consequent.

#### Step 3: Move Negations Inward (NNF)
Apply De Morgan's laws and double negation elimination:
```
~~A         ≡  A
~(A & B)    ≡  ~A | ~B
~(A | B)    ≡  ~A & ~B
```
**Result**: After this step, `Not` appears only directly above `Atom` nodes.

**Formal status**: This produces **Negation Normal Form (NNF)**.

#### Step 4: Distribute OR over AND
```
A | (B & C)    ≡  (A | B) & (A | C)
(A & B) | C    ≡  (A | C) & (B | C)
```
**Rule**: Recursively apply distribution until the formula is in CNF.

**Result**: A formula where:
- Top level is conjunction (`And`)
- Each conjunct is a clause (disjunction or literal)
- Each literal is an atom or negated atom

### 2. Clause Extraction (inference/cnf.py)

Converts a CNF formula (AST) into a set of clauses for resolution:

**Representation**:
- **Literal**: A string, either `"A"` or `"~A"`
- **Clause**: A `frozenset[str]` of literals (representing their disjunction)
- **CNF**: A `set[frozenset[str]]` of clauses (representing their conjunction)

**Examples**:
```python
A | B           →  frozenset({"A", "B"})
(A | B) & C     →  {frozenset({"A", "B"}), frozenset({"C"})}
~(A & B)        →  {frozenset({"~A", "~B"})}
```

**Optimization**: Tautological clauses (containing both `"A"` and `"~A"`) are automatically filtered because they don't constrain satisfiability.

### 3. Resolution Algorithm (inference/resolution.py)

Implements propositional resolution with the **refutation principle**:

#### The Resolution Rule
```
{A ∨ B}  and  {¬A ∨ C}  derive  {B ∨ C}
```

Formally: For clauses ci and cj:
- Find all complementary literal pairs between ci and cj
- Remove the complementary pair
- Union remaining literals
- The result is a **resolvent**

#### Resolution Algorithm: `resolution_unsat(clauses)`

**Input**: A set of clauses

**Algorithm**:
1. Initialize `known_clauses` with input clauses
2. **WHILE** new clauses can be derived:
   - For each pair of clauses (ci, cj):
     - Compute all resolvents via `resolve_pair(ci, cj)`
     - If empty clause `{}` is derived → **return True** (unsatisfiable)
     - Add non-tautological resolvents to known clauses
3. If no new clauses → **return False** (satisfiable)

**Termination**: Guaranteed because:
- Propositional variables are finite
- At most 2^n clauses possible for n atoms
- We track processed pairs to avoid redundant work

**Complexity**: O(2^n) in worst case (PSPACE-complete problem).

#### Top-level Entailment: `resolution_entails(kb, query)`

**Algorithm**:
1. Collect all beliefs from KB
2. Convert each belief to CNF and extract clauses → `KB_clauses`
3. Negate query: `¬query`
4. Convert to CNF and extract clauses → `query_clauses`
5. Combine: `all_clauses = KB_clauses ∪ query_clauses`
6. **Return** `resolution_unsat(all_clauses)`

**Semantic Behavior**:
- **Sound**: If returns True, KB truly entails query
- **Complete**: If KB entails query, will always return True
- **Explosion principle**: If KB is inconsistent, returns True for any query
- **Tautologies**: Empty KB only entails tautologies

### 4. Optional Model Checking (inference/model_check.py)

Implements truth table enumeration for debugging:

**Function**: `truth_table_entails(kb, query)`

- Enumerates all 2^n truth assignments
- Checks: whenever all KB formulas are true, is query also true?

**Important**: This is for **debugging only** due to exponential complexity. The default entailment method is resolution.

---

## Design Choices

### 1. Immutable Formula Transformation

**Choice**: Each transformation (eliminate_iff, move_not_inwards, etc.) returns a new formula without mutating the input.

**Rationale**:
- Formulas are frozen dataclasses (from Stage 1)
- Allows safe reuse and sharing
- Enables debugging intermediate steps
- No side effects

### 2. Clause Set Representation

**Choice**: Use `frozenset[str]` for immutable clauses.

**Rationale**:
- Clauses can be used as dictionary keys
- Supports set operations (union, intersection)
- Efficient duplicate detection
- Natural representation for disjunction (order-independent)

### 3. Tautology Filtering

**Choice**: Automatically detect and omit tautological clauses during extraction.

**Rationale**:
- Tautologies don't constrain satisfiability
- Reduces clause set size
- Speeds up resolution (fewer pairs to resolve)
- No loss of correctness

### 4. No External Packages

**Choice**: Implement resolution from scratch in pure Python.

**Rationale**:
- Assignment requirement: "implement it yourself"
- Transparency: complete control over algorithm
- Educational value: clear implementation
- No dependency on SAT solvers (z3, CaDiCaL, etc.)

---

## Formal Logic Foundation

### Soundness and Completeness

**Theorem**: The resolution algorithm is sound and complete for propositional logic.

- **Sound** (Res ⊢ □ implies ⊨ □): If resolution derives empty clause, the formula is unsatisfiable
- **Complete** (⊨ □ implies Res ⊢ □): If formula is unsatisfiable, resolution will derive empty clause

### Refutation Principle

**Theorem**: KB ⊨ query ⟺ KB ∧ ¬query ⊨ □

This is the basis for our entailment algorithm.

### CNF Equivalence

**Theorem**: Every formula in NNF can be converted to CNF while preserving satisfiability.

Each stage preserves logical equivalence:
1. eliminate_iff: Equisatisfiable with equality
2. eliminate_implies: Logically equivalent
3. move_not_inwards: Logically equivalent (applies valid laws)
4. distribute_or_over_and: Logically equivalent

---

## Implementation Details

### API Reference

#### CNF Module

```python
# Transformations (return new Formula)
eliminate_iff(formula: Formula) -> Formula
eliminate_implies(formula: Formula) -> Formula
move_not_inwards(formula: Formula) -> Formula
distribute_or_over_and(formula: Formula) -> Formula

# Pipeline
to_cnf(formula: Formula) -> Formula

# Extraction
extract_clauses(cnf_formula: Formula) -> set[frozenset[str]]

# Utility
is_tautological_clause(clause: frozenset[str]) -> bool
```

#### Resolution Module

```python
# Literals
negate_literal(lit: str) -> str
are_complementary(lit1: str, lit2: str) -> bool

# Resolution
resolve_pair(ci: frozenset[str], cj: frozenset[str]) -> Set[frozenset[str]]
resolution_unsat(clauses: Set[frozenset[str]]) -> bool

# Main API
resolution_entails(kb: BeliefBase, query: Formula) -> bool
```

### Example Workflow

```python
from belief_base import BeliefBase
from inference import resolution_entails
from logic import parse

# Create KB
kb = BeliefBase()
kb.add_belief(kb.create_belief("A"))
kb.add_belief(kb.create_belief("A -> B"))

# Query
query = parse("B")

# Check entailment
result = resolution_entails(kb, query)  # True
```

---

## Test Coverage

### CNF Tests (28 tests)

- **Elimination**: IFF, implications
- **Normalization**: De Morgan's laws, double negation
- **Distribution**: OR over AND
- **Extraction**: Clause conversion, tautology filtering
- **Integration**: Full pipeline testing

### Resolution Tests (33 tests)

- **Literals**: Negation, complementarity
- **Resolution rule**: Resolving clause pairs
- **Unsat checking**: Core algorithm
- **Entailment**: Main API
  - Modus ponens
  - Non-entailment cases
  - Contradictory KB
  - Empty KB
  - Tautologies
  - Chain reasoning
  - Biconditionals
- **Correctness**: Soundness and completeness
- **Invariants**: No KB mutation

**Total**: 61 Stage 2 tests (in addition to 80 Stage 1 tests)

---

## Compatibility with Future Stages

### Stage 3: Contraction

- Resolution provides entailment checking for consistency verification
- Can verify which set of beliefs remains consistent after removal
- Priority order can guide which beliefs to contract

### Stage 4: Expansion

- Resolution ensures new beliefs maintain consistency (if possible)
- Can detect inconsistencies early

### Stage 5: AGM

- Full entailment checking supports AGM postulates
- Enables verification of revision and contraction operations

---

## Key Properties

✓ **Sound**: No false positives for entailment

✓ **Complete**: Never misses true entailments

✓ **Deterministic**: Same KB and query always give same result

✓ **Non-mutating**: KB and formulas unchanged after checking

✓ **Handles edge cases**:
- Empty KB: Only tautologies entailed
- Inconsistent KB: Everything entailed (explosion)
- Tautologies: Always entailed
- Contradictions: Never entailed

✓ **Efficient optimizations**:
- Tautology filtering
- Pair memoization
- Minimal clause tracking

---

## Algorithm Examples

### Example 1: Modus Ponens

```
KB = {A, A → B}
Query: B

Clauses:
  From A:       {frozenset({"A"})}
  From A → B:   {frozenset({"~A", "B"})}
  From ¬B:      {frozenset({"~B"})}

Resolution:
  1. {A} and {~A, B}  →  {B}
  2. {B} and {~B}     →  {}  (empty clause)
  
Result: Unsatisfiable → KB ⊨ B ✓
```

### Example 2: Non-Entailment

```
KB = {A | B}
Query: A

Clauses:
  From A | B:  {frozenset({"A", "B"})}
  From ¬A:     {frozenset({"~A"})}

Resolution:
  {A, B} and {~A}  →  {B}
  No empty clause derived after fixed point

Result: Satisfiable → KB ⊭ A ✓
```

### Example 3: Inconsistent KB

```
KB = {A, ¬A}
Query: B (any formula)

Clauses:
  From A:     {frozenset({"A"})}
  From ¬A:    {frozenset({"~A"})}
  From ¬B:    {frozenset({"~B"})}

Resolution:
  {A} and {~A}  →  {}  (empty clause)
  
Result: Unsatisfiable → KB ⊨ B ✓ (explosion)
```

---

## Performance Characteristics

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| CNF conversion | O(2^n) worst case | Distribution step is exponential |
| Clause extraction | O(n) | Linear in formula size |
| Single resolution | O(k²) | k = clause size (literals) |
| resolution_unsat | O(2^n) | PSPACE-complete in general |
| resolution_entails | O(2^n) | Dominated by resolution |

**Practical**: For reasonable problem sizes (< 20 atoms), very fast.

---

## Running Tests

```bash
# All tests
python -m pytest tests/ -v

# Stage 2 tests only
python -m pytest tests/test_cnf.py tests/test_resolution.py -v

# With coverage
python -m pytest tests/ --cov=inference --cov=logic --cov=belief_base
```

---

## Future Enhancements

- **Heuristics**: Clause selection strategies (shortest clause first, etc.)
- **Unit propagation**: Faster contradiction detection
- **Pure literal elimination**: Remove variables that appear with one polarity
- **Database indexing**: Fast clause lookup by literal
- **Incremental SAT**: Reuse computation across multiple queries
