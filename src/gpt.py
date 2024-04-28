import openai
import os
import spacy

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
            {"role": "system", "content": "You are a SQL assistant with expertise in natural language and NLP dependency parsing."},
            {"role": "user", "content": f"Parse the following natural language statement: {query} into a SQL query. Just write the query"}
        ],
        max_tokens=150,
        temperature=0.3,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )
    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    query = input("Enter your query: ")
    parsed_query = parse_natural_language(query)
    print(parsed_query)

