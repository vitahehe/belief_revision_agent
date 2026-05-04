# Belief Revision Engine

## Overall Project

This repository implements a belief revision engine for propositional logic, based on the AGM (Alchourrón, Gärdenfors, Makinson) postulates. The engine supports managing a belief base, checking logical entailment, and performing belief changes through contraction, expansion, and revision operations. It's modular, separating representation, reasoning, and belief change for clarity and maintainability.

The project is written in Python and uses resolution-based entailment for efficiency. It includes demos, tests, and a structured codebase with classes for sentences, knowledge bases, and inference.

## How to Run It

1. Ensure you have Python 3 installed.
2. Clone or navigate to the repository.
3. Run the demo script:
   ```
   python main.py
   ```
4. Choose a demo mode (Basic or Advanced) when prompted. The demo will show initial beliefs, entailment checks, and the results of revision operations.

For testing, run individual test files in the `test/` directory, e.g., `python -m pytest test/test_integration.py` (if pytest is installed).

## Belief Base

The belief base stores propositional formulas with metadata. Each belief includes:
- An ID for identification.
- The formula string (e.g., "A", "~A", "(A & B)").
- A normalized string for duplicate checking.
- An AST representation for processing.
- A priority level (higher numbers mean more entrenched beliefs).
- An insertion order for tie-breaking.

Beliefs are managed in a `KnowledgeBase` class, which prevents duplicates and supports adding, removing, and listing beliefs.

## Logical Entailment Checking

Entailment checks whether a query formula logically follows from the belief base. The engine uses:
1. Conversion to Conjunctive Normal Form (CNF).
2. Clause extraction.
3. Propositional resolution to prove entailment.

The main method is `resolution_entails(kb, query)`, which returns `True` if the query is entailed. A truth-table checker is available for small cases as a debugging tool.

## Contraction Based on Priority Order

Contraction removes beliefs to eliminate entailment of a target formula while minimizing changes. It follows priority: lower-priority beliefs are removed first. If priorities are equal, newer beliefs (higher insertion order) are removed first.

The process iteratively removes beliefs and checks if entailment still holds, ensuring the result is consistent and respects the AGM postulates.

## Expansion

Expansion adds a new belief to the base without removing existing ones, as long as it doesn't create duplicates. The new belief is assigned a priority and insertion order. This operation is straightforward and always succeeds, maintaining consistency.

## Revision

Revision combines contraction and expansion: contract by the negation of the new formula, then expand by the formula. This ensures the belief base accepts the new information while preserving as much as possible.

The engine satisfies AGM postulates like Success, Inclusion, Vacuity, Consistency, and Extensionality, verified through tests.

For more details, explore the code in `KnowledgeBase.py`, `inference/`, and `test/` directories.
