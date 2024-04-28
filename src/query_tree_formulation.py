import spacy
import stanza

# Load models
nlp_spacy = spacy.load("en_core_web_sm")
stanza.download('en')
nlp_stanza = stanza.Pipeline(lang='en')

def parse_query(query):
    # Parse the query using both SpaCy and Stanza
    doc_spacy = nlp_spacy(query)
    doc_stanza = nlp_stanza(query)
    return doc_spacy, doc_stanza

def print_parse_trees(doc_spacy, doc_stanza):
    print("Spacy Parse Tree:")
    for token in doc_spacy:
        print(f"{token.text} ({token.dep_}) -> {token.head.text}")
    print("\nStanza Parse Tree:")
    for sent in doc_stanza.sentences:
        for word in sent.words:
            print(f"{word.text} ({word.deprel}) -> {sent.words[word.head-1].text if word.head > 0 else 'ROOT'}")

def doc_to_list(doc):
    # Determine if the document is from SpaCy or Stanza and convert accordingly
    if isinstance(doc, spacy.tokens.doc.Doc):
        # SpaCy document processing
        return [(token.text, token.dep_, token.head.i) for token in doc]
    elif isinstance(doc, stanza.models.common.doc.Document):
        # Stanza document processing
        return [(word.text, word.deprel, word.head - 1) for sent in doc.sentences for word in sent.words]
    else:
        raise TypeError("Unsupported document type.")


def adjust_tree(tokens):
    adjusted_trees = []
    length = len(tokens)
    for i in range(length):
        for j in range(length):
            if i != j:
                new_tree = tokens[:]
                token = new_tree.pop(i)
                new_tree.insert(j, token)
                adjusted_trees.append(new_tree)
    return adjusted_trees

import spacy

def is_valid_tree(tokens):
    """
    Enhanced validation to check if the tree conforms to more complex rules:
    Specifically, no verb should directly dominate a noun without a preposition or conjunction,
    unless it's an acceptable verb-noun construction (like direct actions).
    """
    # Dictionary of verbs that can directly govern a noun without a preposition
    direct_action_verbs = {'eat', 'see', 'write', 'modify', 'create', 'handle', 'return'}

    for i, (word, dep, head_idx) in enumerate(tokens):
        head_word, head_dep, _ = tokens[head_idx] if head_idx < len(tokens) and head_idx >= 0 else ('ROOT', 'root', -1)
        
        if dep == 'dobj' and head_dep == 'VERB':
            # Check if the verb directly governing a noun is in the list of direct action verbs
            if head_word.lower() not in direct_action_verbs:
                return False  # Not a valid tree because it's an inappropriate direct verb-noun governance
        
        if dep == 'nsubj' and head_dep == 'VERB':
            # Ensure verbs that need supportive prepositions or conjunctions have them
            if word.lower() in {'information', 'report', 'document'} and head_word.lower() in {'consist', 'comprise', 'include'}:
                # Check for preceding preposition or valid conjunction
                if not any((tokens[j][1] == 'prep' or tokens[j][1] == 'conj') for j in range(i)):
                    return False  # Not a valid tree due to missing preposition/conjunction
        
    return True


def hash_tree(tree):
    return hash("".join(f"{token[0]}-{token[1]}" for token in tree))

def reformulate_parse_trees(initial_trees, max_edits):
    from collections import deque

    queue = deque([(tree, 0) for tree in initial_trees])
    seen_trees = set()
    valid_trees = []

    while queue:
        current_tree, edits = queue.popleft()
        tree_hash = hash_tree(current_tree)
        
        if tree_hash in seen_trees or edits > max_edits:
            continue
        seen_trees.add(tree_hash)
        
        if is_valid_tree(current_tree):
            valid_trees.append(current_tree)
        
        if edits < max_edits:
            possible_trees = adjust_tree(current_tree)
            for tree in possible_trees:
                if not hash_tree(tree) in seen_trees:
                    queue.append((tree, edits + 1))
    
    return valid_trees[:max_edits]

if __name__ == "__main__":
    query = "Return the average number of publications by Bob each year."
    doc_spacy, doc_stanza = parse_query(query)

    print_parse_trees(doc_spacy, doc_stanza)

    initial_trees = [doc_to_list(doc_spacy), doc_to_list(doc_stanza)]
    top_trees = reformulate_parse_trees(initial_trees, max_edits=3)

    for tree in top_trees:
        print("Tree:")
        for node in tree:
            print(f"{node[0]} ({node[1]})")