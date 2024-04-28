import spacy
import torch
import stanza

print(torch.__version__)

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

stanza.download('en') 

#load standord parse model
nlp2 = stanza.Pipeline(lang='en')

def parse_query(query):
    """
    Parse the natural language query and return the dependency parse tree.
    
    Args:
    query (str): A natural language query.

    Returns:
    doc (spacy.tokens.Doc): A SpaCy Doc object containing the parsed query.
    """
    # Parse the query using SpaCy
    doc = nlp(query)
    doc2 = nlp2(query)
    return doc, doc2

def print_parse_tree(doc):
    """
    Print the dependency parse tree of the query.
    
    Args:
    doc (spacy.tokens.Doc): A SpaCy Doc object containing the parsed query.
    """
    for token in doc:
        print(f"{token.text} ({token.dep_}) -> {token.head.text}")

def print_stanza_parse_tree(doc):
    """
    Print the dependency parse tree of the query for Stanza output.
    
    Args:
    doc (stanza.models.common.doc.Document): A Stanza Document object containing the parsed query.
    """
    for sent in doc.sentences:
        for word in sent.words:
            print(f"{word.text} ({word.deprel}) -> {sent.words[word.head-1].text if word.head > 0 else 'ROOT'}")


# Example usage
if __name__ == "__main__":
    query = "Return the average number of publications by Bob each year."
    doc, doc2 = parse_query(query)
    print("Here is the output for spaCy: ")
    print_parse_tree(doc)
    print("Here is the output for Stanford Parser: ")
    print_stanza_parse_tree(doc2)