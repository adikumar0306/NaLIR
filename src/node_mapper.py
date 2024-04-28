import spacy
from spacy.tokens import Token
from dependency_parser import parse_query

def classify_node(token, sentence=None):
    if hasattr(token, 'deprel'):  # Handling Stanza tokens
        dep = token.deprel
        pos = token.upos
        if token.head > 0:
            head_token = sentence.words[token.head - 1]
            head_pos = head_token.upos
        else:
            head_pos = 'ROOT'
    else:  # Handling SpaCy tokens
        dep = token.dep_
        pos = token.pos_
        head_pos = token.head.pos_

    node_info = determine_node_type(dep, pos, head_pos)
    return {'node_type': node_info, 'head_text': token.head.text if hasattr(token.head, 'text') else 'ROOT'}



def determine_node_type(dep, pos, head_pos):
    if dep == 'root' and pos == 'VERB':
        return 'SN'  # SELECT Node, typically for verbs that are central actions
    elif dep in ['amod', 'acomp'] and head_pos == 'NOUN':
        return 'FN'  # Function Node, e.g., for adjectives modifying nouns
    elif pos == 'NUM':
        return 'VN'  # Value Node, for numeric values
    elif dep == 'nsubj' and pos == 'NOUN':
        return 'NN'  # Name Node, for subjects that are nouns
    elif pos in ['NOUN', 'PROPN'] and dep in ['pobj', 'dobj']:
        return 'NN'  # Also Name Node, for objects that are nouns or proper nouns
    elif any(word in pos.upper() for word in ['AND', 'OR', 'NOT']):
        return 'LN'  # Logic Node, for logical operators
    elif any(word in pos.upper() for word in ['ALL', 'ANY', 'EACH']):
        return 'QN'  # Quantifier Node, for quantifiers
    elif dep in ['prep', 'agent'] and head_pos == 'VERB':
        return 'ON'  # Operator Node, for prepositions or agents linked to verbs
    return 'Unknown'  # Default if no other type fits


def map_to_sql_component(info, token):
    node_type = info['node_type']
    head_text = info['head_text']
    sql_components = {
        'SN': 'SELECT',
        'FN': f"AVG({head_text})" if token.text.lower() == 'average' else 'FUNCTION',
        'NN': f"{token.text}",
        'VN': f"{token.text}",
        'QN': f"{token.text.upper()}",
        'LN': f"{token.text.upper()}",
        'ON': f"{token.text}" if token.text not in ['=', '<', '>'] else 'OPERATOR'
    }
    return sql_components.get(node_type, 'UNKNOWN')


def process_query(query):
    doc_spacy, doc_stanza = parse_query(query)
    
    print("Combined mapping results:")
    # Flatten the list of Stanza sentences to tokens
    stanza_tokens = [word for sentence in doc_stanza.sentences for word in sentence.words]

    # Ensure the length of tokens from both parsers are the same
    if len(doc_spacy) == len(stanza_tokens):
        for spacy_token, stanza_token in zip(doc_spacy, stanza_tokens):
            spacy_info = classify_node(spacy_token)
            
            # Find the sentence that contains the stanza_token
            # Assuming you have access to the sentence object directly or indirectly
            containing_sentence = next((s for s in doc_stanza.sentences if stanza_token in s.words), None)
            if containing_sentence is not None:
                stanza_info = classify_node(stanza_token, containing_sentence)
            else:
                stanza_info = {'node_type': 'Unknown', 'head_text': 'ROOT'}  # Fallback if sentence not found

            # Determine which info to use
            if stanza_info['node_type'] != 'Unknown':
                chosen_info = stanza_info
            elif spacy_info['node_type'] != 'Unknown':
                chosen_info = spacy_info
            else:
                chosen_info = stanza_info  # Default to Stanford if both are unknown

            sql_component = map_to_sql_component(chosen_info, stanza_token if chosen_info == stanza_info else spacy_token)
            print(f"Token: {stanza_token.text}, Type: {chosen_info['node_type']}, SQL: {sql_component}")
    else:
        print("Error: The number of tokens from SpaCy and Stanza do not match. Cannot combine results.")


# Example usage
if __name__ == "__main__":
    query = "Return the average number of publications by Bob each year."
    process_query(query)

#output:
"""
Token: Return, Type: SN, SQL: SELECT
Token: the, Type: Unknown, SQL: UNKNOWN
Token: average, Type: FN, SQL: AVG(ROOT)
Token: number, Type: NN, SQL: number
Token: of, Type: Unknown, SQL: UNKNOWN
Token: publications, Type: NN, SQL: publications
Token: by, Type: ON, SQL: by
Token: Bob, Type: NN, SQL: Bob
Token: each, Type: Unknown, SQL: UNKNOWN
Token: year, Type: Unknown, SQL: UNKNOWN
Token: ., Type: Unknown, SQL: UNKNOWN
"""