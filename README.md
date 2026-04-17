# Belief Revision Engine

## Goal

This project implements a propositional belief revision engine for a knowledge-based agent. The engine stores beliefs as symbolic propositional formulas and updates them when a new formula is received.

The implementation follows the course topics on propositional logic, knowledge bases, CNF conversion, and resolution-based entailment. In the spirit of a knowledge-based agent, the system separates:
- representation of beliefs,
- inference over beliefs,
- belief change operations.

The belief base is treated as a set of propositional sentences. Logical entailment is implemented through refutation: to test whether a query `alpha` follows from the belief base `KB`, we test whether `KB ∧ ¬alpha` is unsatisfiable using CNF conversion and propositional resolution.

## Project scope

The default pipeline of the engine is:

1. Design and implementation of a belief base
2. Design and implementation of logical entailment checking
3. Implementation of contraction based on formula priorities
4. Implementation of expansion
5. Revision of beliefs by combining contraction and expansion
6. Testing using the AGM postulates required in the assignment

## Things the group must agree on before coding separately

Before we start implementing our own part, the whole group must agree on the following:

### 1. Formula syntax
We use the following syntax:
- Negation: `~A`
- Conjunction: `A & B`
- Disjunction: `A | B`
- Implication: `A -> B`
- Biconditional: `A <-> B`

Examples:
- `A`
- `~A`
- `(A & B)`
- `(A -> B)`
- `((A -> B) & A)`

### 2. Internal formula representation
All formulas are parsed into a shared AST representation. No module should operate directly on raw strings except the parser.

### 3. Belief priority convention
Each belief has an integer priority.
- Higher number = more entrenched / harder to remove
- Lower number = easier to remove during contraction

### 4. Clause format
CNF clauses are represented as:
- one clause = `frozenset[str]`
- one CNF formula = `set[frozenset[str]]`

Literal examples:
- `"A"`
- `"~A"`

Clause example:
- `frozenset({"~A", "B"})`

### 5. Tie-breaking rule
If two beliefs have the same priority, ties are broken by insertion order.
The group must agree whether the system removes:
- newest first, or
- oldest first

### 6. Revision policy
Revision by a formula `phi` is implemented as:
- contract the belief base by `~phi`
- expand the result by `phi`

### 7. Test conventions
All tests go into the `tests/` folder.
Each module must include unit tests, and the final engine must include scenario tests for AGM postulates.

## Module responsibilities

### Person 1: Formula language and belief base
Responsible for:
- AST classes
- parser
- formula normalization / pretty-printing
- belief base container

Files:
- `logic/ast.py`
- `logic/parser.py`
- `belief_base/base.py`
- `belief_base/models.py`

### Person 2: CNF and entailment
Responsible for:
- implication/biconditional elimination
- negation normal form
- CNF conversion
- clause extraction
- resolution-based entailment

Files:
- `inference/cnf.py`
- `inference/resolution.py`
- optional `inference/model_check.py`

### Person 3: Contraction
Responsible for:
- contraction algorithm
- priority-based removal
- minimal-removal strategy
- deterministic tie-breaking

Files:
- `revision/contraction.py`

### Person 4: Expansion, revision, AGM tests, integration
Responsible for:
- expansion
- revision pipeline
- CLI / main runner
- AGM postulate tests
- final integration

Files:
- `revision/expansion.py`
- `revision/revision.py`
- `main.py` or `cli.py`
- `tests/test_agm.py`

## Shared API

The following interfaces must stay stable across the project:

```python
parse_formula(text: str) -> Formula
to_cnf(formula: Formula) -> set[frozenset[str]]
entails(kb: BeliefBase, query: Formula) -> bool
expand(kb: BeliefBase, formula: Formula, priority: int) -> BeliefBase
contract(kb: BeliefBase, formula: Formula) -> BeliefBase
revise(kb: BeliefBase, formula: Formula, priority: int) -> BeliefBase
