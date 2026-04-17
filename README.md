# Belief Revision Engine — Group README

## Purpose of this README

This README is the group contract for the project.


- what we are building,
- what design choices we have agreed on,
- how the project is split into 4 modules,
- which person owns which module,
- what each person must deliver,
- which data formats and APIs must stay consistent across the whole project.

This file should be treated as the **single shared reference** before people start coding separately.

---

## What we are building

We are building a **belief revision engine for propositional logic**.

The engine must support the assignment pipeline:

1. belief base
2. logical entailment checking
3. contraction based on priority order
4. expansion
5. output of the resulting belief base

The project should be modular, so that:
- representation is separated from reasoning,
- reasoning is separated from belief change,
- belief change is separated from testing and the user interface.

---

# What we agree on

These are the shared group decisions. Everyone must follow them.

## 1. Logic and syntax agreement

We use **propositional logic only**.

We use exactly this syntax:

- negation: `~A`
- conjunction: `A & B`
- disjunction: `A | B`
- implication: `A -> B`
- biconditional: `A <-> B`

Examples:
- `A`
- `~A`
- `(A & B)`
- `(A | B)`
- `(A -> B)`
- `(A <-> B)`
- `((A -> B) & A)`

### Agreement
- everyone uses the same operators
- parentheses are used whenever needed to avoid ambiguity
- no one invents a second syntax

---

## 2. Internal representation agreement

All formulas must be represented internally in one shared structure.

### Agreement
We use an **AST / sentence-tree representation** with nodes such as:
- Atom
- Not
- And
- Or
- Implies
- Biconditional

No module except the parser should rely on raw strings for logic operations.

---

## 3. Belief-base agreement

The belief base is not just a list of formulas.  
Each stored belief must carry metadata needed later for contraction and revision.

### Agreement
Each belief record must contain:
- `id`
- `formula_str`
- `normalized_formula_str`
- `formula_ast`
- `priority`
- `insertion_order`

### Priority convention
- larger number = more entrenched / harder to remove
- smaller number = easier to remove first

### Tie-breaking convention
If two beliefs have the same priority:
- remove the **newest** one first

This must stay consistent in:
- contraction
- tests
- examples
- report

---

## 4. Entailment agreement

The main entailment method of the final system is:

1. convert formulas to CNF
2. transform CNF into clauses
3. use propositional resolution

### Agreement
The **default / final** entailment method is:
```python
resolution_entails(kb, query)
```

A brute-force truth-table style checker may exist only as:
- a debugging tool
- a validation tool on small examples

but it is **not** the main final inference engine.

---

## 5. CNF and clause-format agreement

After CNF conversion, formulas must be representable as clauses.

### Agreement
Literal format:
- `"A"`
- `"~A"`

Clause format:
```python
frozenset[str]
```

CNF format:
```python
set[frozenset[str]]
```

Example:
```python
frozenset({"~A", "B"})
```

No one should use a second incompatible clause format.

---

## 6. Revision-policy agreement

Revision by a formula `phi` is implemented as:

```text
KB * phi = (KB ÷ ~phi) + phi
```

That means:
1. contract by the negation of `phi`
2. then expand by `phi`

### Agreement
This is the official revision pipeline used in:
- the code
- the tests
- the report

---

## 7. Duplicate-handling agreement

### Agreement
The belief base should not store duplicate formulas.

Two formulas are treated as duplicates if they have the same normalized formula string.

So expansion should not insert the same formula twice.

---

## 8. Testing agreement

We must test the postulates required in the assignment:

- Success
- Inclusion
- Vacuity
- Consistency
- Extensionality

### Agreement
These tests belong to the final integrated system and must use:
- the agreed syntax
- the agreed priority convention
- the agreed tie-breaking rule
- the agreed revision pipeline

---

# Shared data formats

These formats must stay the same across all modules.

## Formula input format

Examples:
- `A`
- `~A`
- `(A & B)`
- `(A | B)`
- `(A -> B)`
- `(A <-> B)`

## Literal format

- positive literal: `"A"`
- negative literal: `"~A"`

## Clause format

```python
frozenset({"A", "~B", "C"})
```

## CNF format

```python
set[frozenset[str]]
```

## Belief format

Recommended structure:

```python
{
    "id": "b7",
    "formula_str": "(A -> B)",
    "normalized_formula_str": "(A -> B)",
    "formula_ast": ...,
    "priority": 3,
    "insertion_order": 7
}
```

## Revision output format

Recommended structure:

```python
{
    "operation": "revision",
    "input_formula": "B",
    "removed_beliefs": ["b2"],
    "added_beliefs": ["b9"],
    "resulting_belief_base": [...]
}
```

---

# Shared API agreement

All modules must code against the same API.

## Formula/parsing API

```python
parse_formula(text: str) -> Formula
formula_to_string(formula: Formula) -> str
get_symbols(formula: Formula) -> set[str]
negate(formula: Formula) -> Formula
normalize_formula(formula: Formula) -> str
```

## Belief-base API

```python
create_belief(formula_text: str, priority: int, insertion_order: int) -> Belief
add_belief(kb: BeliefBase, belief: Belief) -> None
remove_belief_by_id(kb: BeliefBase, belief_id: str) -> None
list_beliefs(kb: BeliefBase) -> list[Belief]
copy_kb(kb: BeliefBase) -> BeliefBase
contains_formula(kb: BeliefBase, normalized_formula: str) -> bool
```

## CNF / inference API

```python
eliminate_iff(formula: Formula) -> Formula
eliminate_implies(formula: Formula) -> Formula
move_not_inwards(formula: Formula) -> Formula
distribute_or_over_and(formula: Formula) -> Formula
to_cnf(formula: Formula) -> Formula
extract_clauses(cnf_formula: Formula) -> set[frozenset[str]]

resolve(ci: frozenset[str], cj: frozenset[str]) -> set[frozenset[str]]
resolution_entails(kb: BeliefBase, query: Formula) -> bool
truth_table_entails(kb: BeliefBase, query: Formula) -> bool   # optional helper only
```

## Belief-change API

```python
expand(kb: BeliefBase, formula_text: str, priority: int) -> BeliefBase
contract(kb: BeliefBase, formula_text: str) -> BeliefBase
revise(kb: BeliefBase, formula_text: str, priority: int) -> BeliefBase
```

## Testing API

```python
check_success_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_inclusion_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_vacuity_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_consistency_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_extensionality_postulate(kb: BeliefBase, phi: str, psi: str, priority: int) -> bool
```

---

# 1, 2, 3, 4 Module agreement

This is the official project split.

---

## Module 1 — Formula language and belief-base core  
**Owner: Person 1**

Person 1 owns the **representation layer**.

### Module 1 agreement

This person is responsible for:
- propositional formula representation
- parser
- formula utilities
- belief object
- belief base container

### Functions owned by Person 1

```python
parse_formula
formula_to_string
get_symbols
negate
normalize_formula
create_belief
add_belief
remove_belief_by_id
list_beliefs
copy_kb
contains_formula
```

### Deliverables for Module 1

#### `logic/ast.py`
This file must define the shared internal formula representation.

It should contain classes for:
- Atom
- Not
- And
- Or
- Implies
- Biconditional

**Expected result**
- one stable formula structure used by all modules

#### `logic/parser.py`
This file must convert input strings into formulas.

It should contain:
- tokenizer
- parser with operator precedence
- syntax checking

**Expected result**
- valid input strings become formulas
- invalid input gives clear errors

#### `logic/utils.py`
This file must contain shared helper logic.

It should contain:
- symbol collection
- formula pretty-printing
- normalization helper
- negation helper

**Expected result**
- reusable utility logic centralized in one place

#### `belief_base/models.py`
This file must define the belief record.

Each belief should contain:
- id
- formula string
- normalized formula string
- AST
- priority
- insertion order

**Expected result**
- standard belief metadata for the whole project

#### `belief_base/base.py`
This file must define the belief-base container.

It should contain:
- add/remove/list/copy methods
- duplicate checking
- deterministic storage behavior

**Expected result**
- a clean KB object the rest of the group can build on

---

## Module 2 — CNF conversion and entailment engine  
**Owner: Person 2**

Person 2 owns the **reasoning layer**.

### Module 2 agreement

This person is responsible for:
- CNF conversion
- clause extraction
- resolution
- main entailment engine

### Functions owned by Person 2

```python
eliminate_iff
eliminate_implies
move_not_inwards
distribute_or_over_and
to_cnf
extract_clauses
resolve
resolution_entails
truth_table_entails   # optional helper only
```

### Deliverables for Module 2

#### `inference/cnf.py`
This file must implement the CNF pipeline.

It should contain:
1. biconditional elimination
2. implication elimination
3. negation pushing
4. distribution
5. conversion to clause-set form

**Expected result**
- any formula can be turned into a consistent CNF clause representation

#### `inference/resolution.py`
This file must implement the theorem prover.

It should contain:
- complementary-literal detection
- resolvent construction
- iterative resolution loop
- empty-clause detection

**Expected result**
- `resolution_entails(kb, query)` is the main inference function

#### `inference/model_check.py` (optional)
This file may contain a truth-table checker.

**Expected result**
- small-case debugging only
- not the main engine

### Important rule for Module 2
Person 2 defines the official clause format used by the whole project.

---

## Module 3 — Contraction based on priorities  
**Owner: Person 3**

Person 3 owns the **belief-removal layer**.

### Module 3 agreement

This person is responsible for:
- contraction
- priority-based belief removal
- deterministic tie-breaking
- using entailment checks to know when contraction succeeded

### Functions owned by Person 3

```python
contract
select_beliefs_for_removal
sort_beliefs_by_removability
still_entails_after_removal
```

### Deliverables for Module 3

#### `revision/contraction.py`
This file must implement contraction.

It should contain:
- ordering beliefs by removability
- lower priority removed first
- newest removed first if priorities are equal
- repeated entailment checking after removals
- minimal or near-minimal removal strategy

**Expected result**
- after contracting by `phi`, the new KB no longer entails `phi`
- the result is deterministic and respects priorities

### Important rule for Module 3
Person 3 must use Person 2’s entailment function.  
Module 3 must not build a second inference engine.

---

## Module 4 — Expansion, revision, tests, and interface  
**Owner: Person 4**

Person 4 owns the **integration layer**.

### Module 4 agreement

This person is responsible for:
- expansion
- revision
- AGM postulate tests
- integration tests
- user-facing runner / demo

### Functions owned by Person 4

```python
expand
revise
check_success_postulate
check_inclusion_postulate
check_vacuity_postulate
check_consistency_postulate
check_extensionality_postulate
run_demo
```

### Deliverables for Module 4

#### `revision/expansion.py`
This file must implement expansion.

It should contain:
- add new belief to KB
- duplicate handling
- priority handling on insert

**Expected result**
- expansion is deterministic and consistent with KB format

#### `revision/revision.py`
This file must implement the full revision pipeline.

It should contain:
- contract by `~phi`
- expand by `phi`
- return the new belief base
- optional change summary

**Expected result**
- one top-level revision function for the whole project

#### `tests/test_agm.py`
This file must implement the required postulate tests:
- success
- inclusion
- vacuity
- consistency
- extensionality

**Expected result**
- direct evidence that the system satisfies the assignment requirements

#### `tests/test_integration.py`
This file must implement end-to-end tests that combine:
- parser
- belief base
- CNF conversion
- resolution
- contraction
- expansion
- revision

**Expected result**
- interface mismatches are caught early

#### `main.py` or `cli.py`
This file must provide the runnable entry point.

It should support:
- predefined examples and/or
- command-line interaction

**Expected result**
- the grader can run the project easily

---

# Ownership summary

## Person 1
```python
parse_formula
formula_to_string
get_symbols
negate
normalize_formula
create_belief
add_belief
remove_belief_by_id
list_beliefs
copy_kb
contains_formula
```

## Person 2
```python
eliminate_iff
eliminate_implies
move_not_inwards
distribute_or_over_and
to_cnf
extract_clauses
resolve
resolution_entails
truth_table_entails   # optional helper
```

## Person 3
```python
contract
select_beliefs_for_removal
sort_beliefs_by_removability
still_entails_after_removal
```

## Person 4
```python
expand
revise
check_success_postulate
check_inclusion_postulate
check_vacuity_postulate
check_consistency_postulate
check_extensionality_postulate
run_demo
```

---


# Recommended repository structure

```text
belief-revision-engine/
├── README.md
├── main.py
├── cli.py
├── requirements.txt
├── logic/
│   ├── ast.py
│   ├── parser.py
│   └── utils.py
├── belief_base/
│   ├── base.py
│   └── models.py
├── inference/
│   ├── cnf.py
│   ├── resolution.py
│   └── model_check.py
├── revision/
│   ├── contraction.py
│   ├── expansion.py
│   └── revision.py
├── tests/
│   ├── test_parser.py
│   ├── test_cnf.py
│   ├── test_resolution.py
│   ├── test_contraction.py
│   ├── test_expansion.py
│   ├── test_agm.py
│   └── test_integration.py
└── examples/
    ├── example1.txt
    ├── example2.txt
    └── demo_cases.md
```

---

# What each person must hand over

## Person 1 hands over
- parser
- AST
- belief model
- belief base
- unit tests for parser / belief base

## Person 2 hands over
- CNF pipeline
- clause extraction
- resolution engine
- unit tests for CNF / resolution
- optional brute-force checker for debugging

## Person 3 hands over
- contraction implementation
- deterministic priority handling
- tests for contraction examples

## Person 4 hands over
- expansion
- revision
- AGM tests
- integration tests
- runnable entry point


# Final checklist

Before submission, confirm:

- one syntax only
- one AST only
- one belief format only
- one clause format only
- priorities handled consistently
- tie-breaking is newest-first
- duplicates are not inserted
- main entailment is resolution-based
- revision is contract-by-negation then expand
- AGM tests are implemented
- README matches the actual code

---

# Short summary

We are building one propositional belief revision engine with four agreed modules:

1. representation and belief base  
2. CNF and entailment  
3. contraction  
4. expansion, revision, tests, and interface

This README is the shared plan.  
Everyone should code so their part fits these agreements exactly.
