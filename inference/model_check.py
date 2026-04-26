from KnowledgeBase import check_entailment_brute_force


def truth_table_entails(kb, query):
    """Check entailment using brute-force truth table method."""
    # For now, assume kb has a method to get the combined sentence
    # Since KnowledgeBase has convert_to_cnf, but brute force takes two sentences
    # We need to combine KB sentences
    if hasattr(kb, "convert_to_cnf"):
        kb_cnf = kb.convert_to_cnf()
        return check_entailment_brute_force(kb_cnf, query)
    else:
        raise ValueError("Unsupported KB format for truth table entailment")