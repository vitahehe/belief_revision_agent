#VITA CHANGES

## Purpose
code now provides the logical reasoning engine that converts formulas to conjunctive normal form (CNF), extracts clauses, and uses resolution to check entailment.

The existing AST in Sentence.py was preserved, including all the Sentence subclasses (Atom, Not, And, Or, Implies, Biconditional) and their methods like to_cnf(), eliminate_implications(), push_not(), and distribute(). The existing KnowledgeBase.py structure was preserved as much as possible, with only a small addition to expose the new entailment method. The existing brute-force checker in KnowledgeBase.py was not deleted and remains available for debugging. ToCnfTest.py was preserved and still checks CNF tree structure using the AST.

## Files added
- `inference/__init__.py`: Initializes the inference module for organizing CNF and resolution code.
- `inference/cnf.py`: Contains functions for the CNF pipeline, including elimination of implications and biconditionals, negation pushing, distribution, and most importantly, clause extraction to convert CNF AST into the official set[frozenset[str]] format.
- `inference/resolution.py`: Implements the resolution algorithm, including clause resolution, unsatisfiability checking via recursive resolution, and the main resolution_entails function for entailment checking.
- `inference/model_check.py`: Provides a wrapper around the existing brute-force truth-table entailment checker for optional debugging on small examples.
- `tests/__init__.py`: Initializes the tests module for the new unit tests.
- `tests/test_cnf.py`: Tests the clause extraction functionality, verifying that various formulas (atoms, implications, biconditionals, complex AND/OR structures) are correctly converted to the official clause format.
- `tests/test_resolution.py`: Tests the resolution engine, including basic resolution, unsatisfiability detection, and entailment checking on knowledge bases with implications, biconditionals, and contradictions.

## Files modified
- `KnowledgeBase.py`: Added an `entails(query)` method that uses the new `inference.resolution.resolution_entails` function to provide a clean API for entailment checking on knowledge bases.

##tests
- `ToCnfTest.py` if i understand, checks whether CNF has the correct nested Sentence/AST structure after conversion, ensuring the tree is properly formed with And at the top and Ors inside.
- `tests/test_cnf.py` checks whether CNF can be extracted into the official clause format: set[frozenset[str]], verifying that the AST is correctly parsed into clauses and literals.
- `tests/test_resolution.py` checks whether the system can actually prove entailment using resolution, testing the full pipeline from knowledge base to boolean entailment result.

## Official clause format
The agreed format for clauses is:

- positive literal: "A"
- negative literal: "~A"
- clause: frozenset[str]
- CNF: set[frozenset[str]]

Example: (A -> B) becomes {frozenset({"~A", "B"})}

## Resolution entailment
Resolution entailment works by refutation: KB entails phi iff KB union {not phi} is unsatisfiable.

Mathematically: KB |= phi iff KB ∪ {¬phi} ⊨ contradiction

The code implements this by converting all formulas to CNF, extracting clauses, adding the negated query as clauses, and running resolution to derive the empty clause (which indicates contradiction/unsatisfiability).

## Alignment with assignment
This completes the assignment's logical entailment component using propositional logic, CNF conversion, and resolution, all implemented without external logic packages. Contraction and expansion are not implemented here because they belong to Person 3 and Person 4.

## Tests run
The following commands were used to verify the implementation:

```
python -m pytest ToCnfTest.py -v
python -m pytest tests/test_cnf.py -v
python -m pytest tests/test_resolution.py -v
python -m pytest ToCnfTest.py tests/ -v
python -m py_compile inference/cnf.py inference/resolution.py inference/model_check.py tests/test_cnf.py tests/test_resolution.py
```

## Notes for person 2,3
- Person 3 should use `resolution_entails` from `inference/resolution.py` for checking entailment during contraction; do not implement a second inference engine.
- Person 4 can use the same entailment function for AGM postulate tests and integration.
- The brute-force checker in `KnowledgeBase.py` is only for debugging small examples and should not be used as the main entailment method.