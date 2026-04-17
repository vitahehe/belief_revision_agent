# Belief Revision Engine

## Project goal

This project implements a **belief revision engine for propositional logic**.  
The engine stores beliefs as symbolic propositional formulas and updates the belief base when a new formula is received.

The assignment requires the following default pipeline:

1. design and implementation of a belief base  
2. design and implementation of a method for checking logical entailment  
3. implementation of contraction of the belief base based on a priority order on formulas  
4. implementation of expansion of the belief base  
5. output of the resulting/new belief base

The implementation is based on the course methods:
- propositional logic
- CNF form
- resolution
- AGM-style belief revision ideas
- contraction and expansion
- testing with the required AGM postulates

---

## Core design choice

We use the following overall design:

- the system is a **knowledge base of propositional sentences**
- formulas are parsed into a shared internal representation
- logical entailment is implemented by **refutation through CNF + propositional resolution**
- contraction removes beliefs according to **priority**
- revision is implemented as:
  - contract by the negation of the input formula
  - then expand by the input formula

This keeps the project aligned with the course logic material and gives a clean separation between:
- representation
- inference
- belief change
- testing and interface

---

## What everyone must agree on before coding

Nobody should code their part before the group agrees on the following.

### 1. Logic syntax

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
- `(A -> B)`
- `((A -> B) & A)`

### 2. Internal representation

All formulas must be parsed into a shared **AST** representation.

No module except the parser should work directly on raw strings unless it is only for input/output.

### 3. Belief priority convention

Each belief has an integer priority:

- higher number = more entrenched / harder to remove
- lower number = easier to remove during contraction

### 4. Tie-breaking rule

If two beliefs have the same priority, the tie is broken by insertion order.

**Group decision:** remove the **newest** belief first among equally ranked beliefs.

This must be used consistently in:
- contraction
- tests
- report examples

### 5. Clause format

Clauses are represented as sets of literals.

Recommended convention:

- literal: `"A"` or `"~A"`
- clause: `frozenset[str]`
- CNF formula: `set[frozenset[str]]`

Example clause:

```python
frozenset({"~A", "B"})
```

### 6. Revision policy

Revision by a formula `phi` is implemented as:

```text
KB * phi = (KB ÷ ~phi) + phi
```

That means:
1. contract the belief base by `~phi`
2. expand the result with `phi`

### 7. Main entailment method

The main inference engine is:

1. parse formula
2. convert formula(s) to CNF
3. test entailment by refutation using propositional resolution

A truth-table checker may exist only as a debugging helper for small examples. It is **not** the main algorithm. The current brute-force entailment function belongs in this helper category, not as the final default engine.

### 8. Duplicate handling rule

If the same formula is already in the belief base, expansion should not create an unnecessary duplicate belief unless the group intentionally wants duplicate tracking.

**Group decision:** formulas are treated as unique by normalized formula string. No duplicate formulas are inserted.

---


## Alignment with the current codebase

This README describes the **target project architecture** for the full assignment.  
The current codebase is **partially aligned** with that plan, but not fully there yet.

### What is already aligned

The current code already follows these important ideas:

- formulas are represented symbolically through sentence classes such as:
  - `Atom`
  - `Not`
  - `And`
  - `Or`
  - `Implies`
  - `Biconditional`
- formulas support:
  - evaluation in a world
  - atom collection
  - implication elimination
  - pushing negations inward
  - distribution toward CNF
- the knowledge base is represented as a collection of sentences
- a CNF conversion pipeline already exists through:
  - `eliminate_implications()`
  - `push_not()`
  - `distribute()`

So the current code is already close to the **representation** and **CNF preparation** parts of the plan.

### What is not yet aligned

The current code differs from the README plan in the following important ways:

#### 1. Entailment method
The current implementation uses:

```python
check_entailment_brute_force(left: Sentence, right: Sentence) -> bool
```

This is **truth-table / model enumeration**, not **resolution**.

That means:
- the current code is useful for correctness checking
- but it does **not** yet match the README decision that the **main inference engine** should be CNF + propositional resolution

#### 2. Clause representation
The current code still works mostly with recursive `Sentence` objects.

The README plan assumes that after CNF conversion, formulas are also transformed into an explicit clause format:

```python
frozenset[str]
set[frozenset[str]]
```

This explicit clause-set format is still missing from the current code.

#### 3. Literal storage
The current code has:

- `LiteralStats`
- `LiteralStore`

This looks like a useful helper structure for counting positive and negative occurrences of literals, but it is **not yet a full resolution engine** by itself.

So this structure can remain, but it should be understood as an internal helper rather than the finished entailment method.

#### 4. Belief base structure
The current `KnowledgeBase` stores:

- `sentences: list[Sentence]`

But the README plan assumes a richer belief-base format with metadata per belief:
- id
- formula string
- normalized formula
- parsed AST / sentence
- priority
- insertion order

This metadata is necessary for:
- contraction by priority
- deterministic tie-breaking
- clearer debugging and reporting

#### 5. Parser layer
The README plan assumes a separate parser module that converts strings into formulas.

In the current code snippet, the parser is not shown. The code appears to build formulas directly using sentence classes.

That is acceptable for early development, but for the final project the parser layer should still exist as the official entry point.

#### 6. Belief revision operations
The current code snippet does **not yet show**:
- expansion
- contraction
- revision

So the current code is still mainly the **logic representation + basic entailment** stage, not the full belief revision engine yet.

### Final interpretation

So the correct reading is:

- the README describes the **intended final architecture**
- the current code implements **part of that architecture**
- the biggest missing piece is that **brute-force entailment must later be replaced or wrapped by a resolution-based entailment engine**
- the belief base must later be extended with **priorities and belief metadata**
- contraction, expansion, and revision must still be added

### Group decision on how to interpret this

For the group, the safest interpretation is:

- keep the README as the **target specification**
- explicitly note that the current codebase is at an earlier stage
- treat brute-force entailment as a **temporary validation/debugging method**
- implement resolution as the final default entailment method
- extend the belief base with priorities before contraction is implemented

---

## Mapping from the current code to the planned architecture

### Current code piece -> Planned role

#### `Sentence`, `Atom`, `Not`, `And`, `Or`, `Implies`, `Biconditional`
Planned role:
- formula representation layer
- equivalent to the AST / sentence hierarchy in the README

#### `KnowledgeBase`
Planned role:
- early version of the belief base container

Needed upgrades:
- belief metadata
- priorities
- insertion order
- better public API for add/remove/list/copy

#### `to_cnf()`, `eliminate_implications()`, `push_not()`, `distribute()`
Planned role:
- CNF conversion pipeline

Needed upgrades:
- convert final CNF formula into explicit clause sets

#### `check_entailment_brute_force(...)`
Planned role:
- optional debugging checker only

Needed upgrade:
- add `resolution_entails(...)` as the main inference engine

#### `LiteralStore`
Planned role:
- optional helper for clause/literal bookkeeping

Needed clarification:
- this is not yet the full theorem prover

---

## Corrected implementation status

At the moment, the project status is best described as:

### Already implemented or mostly implemented
- symbolic sentence representation
- world-based formula evaluation
- atom collection
- implication elimination
- negation pushing
- CNF-style distribution
- basic knowledge base composition
- brute-force entailment checking

### Still required for full alignment with the README plan
- parser as the official input layer
- explicit CNF clause extraction
- propositional resolution engine
- belief metadata with priorities
- contraction
- expansion
- revision
- AGM postulate tests
- final integration runner

---

## Corrected ownership if the current codebase is used as the starting point

### Person 1
Should own:
- `Sentence` hierarchy
- parser layer
- final belief-base data model
- `KnowledgeBase` upgrades

### Person 2
Should own:
- CNF extraction into clause sets
- resolution-based entailment
- keep brute-force checker only as optional debugging support

### Person 3
Should own:
- priority-based contraction on top of the upgraded belief base

### Person 4
Should own:
- expansion
- revision
- tests
- interface / demo

---


## Shared API

All modules must use the following shared API.

## Core formula/parsing API

```python
parse_formula(text: str) -> Formula
formula_to_string(formula: Formula) -> str
get_symbols(formula: Formula) -> set[str]
negate(formula: Formula) -> Formula
```

## Belief base API

```python
create_belief(formula_text: str, priority: int) -> Belief
add_belief(kb: BeliefBase, belief: Belief) -> None
remove_belief_by_id(kb: BeliefBase, belief_id: str) -> None
list_beliefs(kb: BeliefBase) -> list[Belief]
copy_kb(kb: BeliefBase) -> BeliefBase
```

## CNF / inference API

```python
eliminate_iff(formula: Formula) -> Formula
eliminate_implies(formula: Formula) -> Formula
move_not_inwards(formula: Formula) -> Formula
distribute_or_over_and(formula: Formula) -> Formula
to_cnf(formula: Formula) -> set[frozenset[str]]

resolve(ci: frozenset[str], cj: frozenset[str]) -> set[frozenset[str]]
resolution_entails(kb: BeliefBase, query: Formula) -> bool
```

## Optional debugging API

```python
truth_table_entails(kb: BeliefBase, query: Formula) -> bool
```

## Belief change API

```python
expand(kb: BeliefBase, formula_text: str, priority: int) -> BeliefBase
contract(kb: BeliefBase, formula_text: str) -> BeliefBase
revise(kb: BeliefBase, formula_text: str, priority: int) -> BeliefBase
```

## Test API

```python
check_success_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_inclusion_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_vacuity_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_consistency_postulate(kb: BeliefBase, phi: str, priority: int) -> bool
check_extensionality_postulate(kb: BeliefBase, phi: str, psi: str, priority: int) -> bool
```

---

## Module responsibilities

### Person 1 — Formula language and belief-base core

This person owns the **representation layer**.

They implement:
- propositional syntax
- tokenizer and parser
- AST classes
- belief object
- belief base container
- basic helper utilities

### Functions owned by Person 1

```python
parse_formula
formula_to_string
get_symbols
negate
create_belief
add_belief
remove_belief_by_id
list_beliefs
copy_kb
```

### Deliverable files for Person 1

#### `logic/ast.py`
This file defines the internal formula representation.

It should contain AST classes for:
- symbol
- negation
- conjunction
- disjunction
- implication
- biconditional

**What we want from this file**
- a single stable formula representation for the whole project
- no other module invents its own formula structure

#### `logic/parser.py`
This file converts input strings into AST formulas.

It should contain:
- tokenizer
- parser with operator precedence
- syntax validation
- conversion from string to AST

**What we want from this file**
- every valid formula string parses into exactly one correct AST
- invalid syntax produces a clear error

#### `logic/utils.py`
This file contains shared helpers.

It should contain:
- formula pretty-printing
- symbol extraction
- negation helper
- normalization helper if needed

**What we want from this file**
- shared logic stays centralized and reusable

#### `belief_base/models.py`
This file defines the belief record structure.

Each belief should store:
- unique id
- original formula string
- normalized formula string
- parsed formula AST
- priority
- insertion order

**What we want from this file**
- one standard belief object that all other modules use

#### `belief_base/base.py`
This file defines the belief-base container.

It should contain:
- add/remove/list/copy operations
- deterministic storage behavior
- duplicate-handling rule
- optional helper lookup methods

**What we want from this file**
- a single KB implementation that everyone else can rely on

---

### Person 2 — CNF conversion and entailment engine

This person owns the **reasoning layer**.

They implement:
- formula normalization into CNF
- clause extraction
- resolution-based entailment
- optional truth-table checker for debugging

### Functions owned by Person 2

```python
eliminate_iff
eliminate_implies
move_not_inwards
distribute_or_over_and
to_cnf
resolve
resolution_entails
truth_table_entails   # optional
```

### Deliverable files for Person 2

#### `inference/cnf.py`
This file contains the CNF conversion pipeline.

It should implement:
1. eliminate biconditionals
2. eliminate implications
3. move negation inward
4. distribute disjunction over conjunction
5. extract clauses

**What we want from this file**
- any valid propositional formula can be transformed into a clause set usable by resolution

#### `inference/resolution.py`
This file contains the resolution theorem prover.

It should implement:
- complementary-literal detection
- resolvent generation
- duplicate cleanup if needed
- iterative resolution loop
- empty-clause detection

**What we want from this file**
- `resolution_entails(kb, alpha)` correctly checks whether `KB |= alpha`

#### `inference/model_check.py` (optional)
This file contains a truth-table entailment checker for debugging.

**What we want from this file**
- a secondary correctness check on small cases only

---

### Person 3 — Contraction based on priorities

This person owns the **belief-removal layer**.

They implement contraction of the belief base using:
- priority order on beliefs
- the agreed tie-breaking rule
- repeated entailment checks through Person 2’s API

### Functions owned by Person 3

```python
contract
select_beliefs_for_removal
sort_beliefs_by_removability
still_entails_after_removal
```

Only `contract()` must be public if the others are internal helpers.

### Deliverable files for Person 3

#### `revision/contraction.py`
This file contains the contraction algorithm.

It should implement:
- ordering beliefs by removability
- lower priority removed first
- newest removed first when priorities are equal
- repeated entailment checks after removals
- minimal or near-minimal removal strategy

**What we want from this file**
- after contraction by `phi`, the resulting KB should no longer entail `phi`
- contraction must respect priorities and be deterministic

**Important rule**
- Person 3 must not build a separate inference engine
- contraction must call Person 2’s entailment function

---

### Person 4 — Expansion, revision orchestration, tests, and interface

This person owns the **integration layer**.

They implement:
- expansion
- revision
- AGM postulate tests
- end-to-end integration tests
- the user-facing runner

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

### Deliverable files for Person 4

#### `revision/expansion.py`
This file contains the expansion operation.

It should implement:
- adding a new belief
- duplicate-handling policy
- priority assignment on insertion

**What we want from this file**
- expansion is clean, deterministic, and consistent with the KB format

#### `revision/revision.py`
This file contains the full revision pipeline.

It should implement:
- contract by `~phi`
- expand by `phi`
- return the new belief base
- optionally return a summary of changes

**What we want from this file**
- one top-level function representing belief revision

#### `tests/test_agm.py`
This file contains tests for the required postulates:
- success
- inclusion
- vacuity
- consistency
- extensionality

**What we want from this file**
- direct evidence that the engine behaves according to the assignment requirements

#### `tests/test_integration.py`
This file contains end-to-end tests combining:
- parser
- CNF conversion
- resolution
- contraction
- expansion
- revision

**What we want from this file**
- catch interface mismatches between modules early

#### `main.py` or `cli.py`
This file provides the runnable project entry point.

It should support:
- predefined examples and/or
- command-line interaction

**What we want from this file**
- the grader can run the project easily
- the output is readable and consistent

---

## Ownership summary by function

### Person 1
```python
parse_formula
formula_to_string
get_symbols
negate
create_belief
add_belief
remove_belief_by_id
list_beliefs
copy_kb
```

### Person 2
```python
eliminate_iff
eliminate_implies
move_not_inwards
distribute_or_over_and
to_cnf
resolve
resolution_entails
truth_table_entails   # optional
```

### Person 3
```python
contract
select_beliefs_for_removal
sort_beliefs_by_removability
still_entails_after_removal
```

### Person 4
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

## Integration rules

These rules are mandatory.

1. Only Person 1’s parser may create AST formulas from raw strings.
2. Only Person 2’s CNF module may define clause-set output format.
3. Person 3 must not implement separate inference logic; contraction must use Person 2’s entailment function.
4. Person 4 must not reimplement contraction or entailment; revision must compose existing functions.
5. All tests must use the same syntax, priority convention, duplicate-handling rule, and tie-breaking rule as the main system.

---

## File and data formats

### Formula input format
Examples:
- `A`
- `~A`
- `(A & B)`
- `(A | B)`
- `(A -> B)`
- `(A <-> B)`
- `((A -> B) & A)`

### Literal format
- positive literal: `"A"`
- negated literal: `"~A"`

### Clause format
```python
frozenset({"A", "~B", "C"})
```

### CNF format
```python
set[frozenset[str]]
```

### Belief object format
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

### Revision output format
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

## Recommended repository structure

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

## Deliverables for the final submission

The final submission to DTU Learn must contain:

1. **PDF report**
2. **PDF declaration of division of labour**
3. **ZIP file with source code and README**

### What the source-code ZIP should contain
- all Python source files
- this README
- test files
- requirements file if relevant
- example input files if used

---

## What each person should hand over to the group

### Person 1 hands over
- parser works on agreed syntax
- AST classes are stable
- belief base supports add/remove/list/copy
- all functions documented
- unit tests for parsing and belief-base behavior

### Person 2 hands over
- CNF pipeline works end-to-end
- resolution prover works on clause sets
- entailment function callable by other modules
- unit tests for CNF and resolution
- optional truth-table checker for debugging

### Person 3 hands over
- contraction respects priorities
- contraction uses Person 2’s entailment function
- deterministic tie-breaking
- tests showing contraction behavior on examples

### Person 4 hands over
- expansion and revision pipeline work
- AGM postulate tests run
- integration tests pass
- main runner / CLI works
- readable output format for demo and grading

---

## Example development order

### Step 1
Freeze:
- syntax
- AST design
- clause format
- priority convention
- tie-breaking rule
- duplicate rule

### Step 2
Parallel work:
- Person 1 builds parser + KB
- Person 2 builds CNF + resolution
- Person 3 builds contraction
- Person 4 builds expansion + revision + tests skeleton

### Step 3
Integrate:
- Person 3 connects contraction to Person 2 entailment
- Person 4 connects revision to contraction and expansion
- group runs integration tests

### Step 4
Prepare submission:
- report
- labour declaration
- final ZIP with source code and README

---

## Final consistency checklist

Before submitting, confirm:

- all modules use the agreed syntax
- all formulas go through the same parser
- all CNF clauses use the same format
- contraction uses priorities consistently
- ties are broken by newest-first removal
- duplicate formulas are not inserted
- revision is implemented as contract-by-negation then expand
- AGM tests run and are included in the codebase
- README matches the actual code

---

## Short summary

This project is a propositional belief revision engine with four clean layers:

- Person 1: representation
- Person 2: inference
- Person 3: contraction
- Person 4: expansion, revision, tests, integration

Everyone must code against the shared API and shared data formats.  
No one should silently redefine formula syntax, clause format, priorities, or inference behavior.

The goal is that any group member can read this README and know:
- what the project is
- what architecture we are following
- which file they own
- which functions they own
- what output their code must produce
- how all parts fit together


## Short note for the group

If you are coding directly from the current codebase, read this README as a **target specification plus status report**. The architecture and APIs remain the intended final design, but the present implementation is still in the intermediate stage where symbolic formulas and brute-force entailment exist before full resolution-based belief revision is completed.
