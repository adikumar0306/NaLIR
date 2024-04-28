import spacy
import openai
import os

# Load the SpaCy model
nlp = spacy.load("en_core_web_trf")

def setup_openai_client():
    """
    Set up the OpenAI client using the API key from the environment variable.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")
    return openai

def parse_natural_language(query):
    """
    Use GPT-3.5 Turbo to parse a natural language query and extract key components using the chat completion model.
    Parameters:
        query (str): The natural language query from the user.
    Returns:
        str: The parsed query.
    """
    client = setup_openai_client()
    response = client.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a SQL assistant. Convert the following natural language statement into a SQL query."},
            {"role": "user", "content": query}
        ],
        max_tokens=150
    )
    return response['choices'][0]['message']['content'].strip()

def classify_node(token):
    return {'node_type': 'Unknown', 'head_text': token.head.text}

def create_query_trees(dependency_nodes, node_mappings):
    query_trees = []
    select_clause = "SELECT "
    from_clause = "FROM publications"
    where_clause = "WHERE "
    conditions = []

    # Constructing the SQL parts based on mappings
    for token, mapping in zip(dependency_nodes, node_mappings):
        if mapping['node_type'] == 'SN':
            select_clause += "publications.*"
        elif mapping['node_type'] == 'FN':
            select_clause = "SELECT AVG(" + token + ") "
        elif mapping['node_type'] == 'NN' and token.lower() == 'publications':
            from_clause = "FROM " + token
        elif mapping['node_type'] == 'ON':
            conditions.append(token + " = 'Bob'")
        elif mapping['node_type'] == 'VN' and token.isdigit():
            conditions.append("publication_count > " + token)

    where_clause += " AND ".join(conditions)
    full_query = select_clause + "\n" + from_clause + "\n" + (where_clause if conditions else "")
    query_trees.append(full_query)

    return query_trees

def present_query_trees(query_trees):
    descriptions = []
    for tree in query_trees:
        description = "Query Option:\n" + tree
        descriptions.append(description)
    return descriptions

def process_query(query):
    doc = nlp(query)
    dependency_nodes = [token.text for token in doc]  # Simplified example
    node_mappings = [{'node_type': 'Unknown'}] * len(doc)  

    query_trees = create_query_trees(dependency_nodes, node_mappings)
    gpt_query = parse_natural_language(query)  # Get GPT-3.5 Turbo parsed query
    query_trees.append(gpt_query)  # Add GPT-3 parsed query as an option

    natural_language_trees = present_query_trees(query_trees)
    
    for i, desc in enumerate(natural_language_trees, 1):
        print(f"Option {i}:\n{desc}\n")

    # Allow user to select an option
    choice = int(input("Select the query option number you find correct: "))
    chosen_query = natural_language_trees[choice - 1]
    print("\nYou selected:\n", chosen_query)

# Example usage
if __name__ == "__main__":
    query = "Return the average number of publications by Bob each year."
    process_query(query)
