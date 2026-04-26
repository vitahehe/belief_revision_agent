# Belief Revision Agent

Python implementation of a propositional belief revision engine.

This project follows the assignment sequence:

1. design and implementation of a belief base;
2. design and implementation of logical entailment, implemented ourselves;
3. implementation of contraction based on priority order;
4. implementation of expansion;
5. FULL REVISION
6. testing the system using the required AGM postulates.

So far, parts 1, 2, and 3 are implemented and tested. The remaining group work is Stage 4 expansion and 5. the final AGM postulate tests.

---

## so far

The engine currently works with propositional logic in symbolic form.

It can:

- parse propositional formulas into an immutable AST;
- store formulas as beliefs with metadata;
- prevent duplicate beliefs using normalized formula strings;
- convert formulas into CNF;
- extract CNF clauses;
- check entailment using propositional resolution;
- contract a belief base by removing beliefs until a target formula is no longer entailed;
- use belief priorities during contraction;
- preserve the original belief base by returning modified copies.


1. BELIEF BASE

Each believe stores the following below. this is important for contraction. Higher priority means the belief is more entrenched and harder to remove. Lower priority means the belief should be removed earlier if contraction requires removing something.
id
formula_str
normalized_formula_str
formula_ast
priority
insertion_order


2.  implement a method for checking logical entailment ourselves, without using existing packages. We therefore use propositional resolution.

The entailment method is: KB entails phi iff KB and not-phi is unsatisfiable.

In code, the main API is: resolution_entails(kb, query)
Pipeline ; formula AST
→ eliminate biconditionals
→ eliminate implications
→ push negations inward
→ distribute OR over AND
→ extract clauses
→ apply resolution

3. Contraction implemented. 
contract(kb, formula_text)

This matches the assignment requirement that the system should be based on propositional logic, CNF form, resolution, AGM-style belief change, and priority-based contraction.

Russell and Norvig describe a knowledge base as a set of formal sentences. Our project follows that idea, but extends each sentence with extra metadata needed for belief revision: priority, insertion order, identifier, original formula string, normalized formula string, and parsed AST.


TO DO:
4. implementation of expansion of belief base
maybe use API; expand(kb, formula_text, priority) -> BeliefBase
file: revision/expansion.py
Test should include; tests/test_expansion.py
adding a new belief.
trying to add a duplicate,
preserving the original belief base,
adding with correct priority,
insertion order increasing correctly,
expansion followed by entailment.

5. FULL REVISION
The standard AGM-style revision pipeline can use the Levi identity:

KB * phi = (KB ÷ ~phi) + phi

use api: revise(kb, formula_text, priority) -> BeliefBase
in revision/revision.py

Test; revising with a consistent formula;
revising with a formula that contradicts lower-priority beliefs;
checking that the new formula is included after revision;
checking that the original belief base is not mutated.

6. AGM postulate tests

The assignment specifically asks us to test the algorithm using AGM postulates, especially:
Success;
Inclusion;
Vacuity;
Consistency;
Extensionalit

DO IT IN FILE: tests/test_agm.py

## Project structure

belief_revision_agent/
├── logic/
│   ├── __init__.py
│   ├── ast.py
│   ├── parser.py
│   └── utils.py
├── belief_base/
│   ├── __init__.py
│   ├── models.py
│   └── base.py
├── inference/
│   ├── __init__.py
│   ├── cnf.py
│   ├── resolution.py
│   └── model_check.py
├── revision/
│   ├── __init__.py
│   └── contraction.py
├── tests/
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_belief_base.py
│   ├── test_cnf.py
│   ├── test_resolution.py
│   └── test_contraction.py
├── README.md
└── .gitignore