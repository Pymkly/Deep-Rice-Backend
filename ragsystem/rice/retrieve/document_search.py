import textwrap

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# import spacy
# import nltk

# nltk.download('wordnet')
# from nltk.corpus import wordnet
# from collections import Counter
# import numpy as np

# Load spaCy model
# nlp = spacy.load("en_core_web_sm")


def find_best_match_keyword_search(query, db_records):
    best_score = 0
    best_record = None
    query_keywords = set(query.lower().split())
    # Iterate through each record in db_records
    for record in db_records:
        # Split the record into keywords
        record_keywords = set(record.lower().split())
        # Calculate the number of common keywords
        common_keywords = query_keywords.intersection(record_keywords)
        current_score = len(common_keywords)
        # Update the best score and record if the current score is higher
        if current_score > best_score:
            best_score = current_score
            best_record = record
    return best_score, best_record

def search_documents(question, db, limit=5):
    collection = db["rice_pdf_documents"]
    collection.create_index([("content", "text")])
    query = {"$text": {"$search": question}}
    results = collection.find(query).limit(limit)
    # for document in results:
    #     print(document)
    return [doc["content"] for doc in results]

def calculate_cosine_similarity(text1, text2):
    vectorizer = TfidfVectorizer(
        stop_words='english',
        use_idf=True,
        norm='l2',
        ngram_range=(1, 2), # Use unigrams and bigrams
        sublinear_tf=True, # Apply sublinear TF scaling
        analyzer='word', # You could also experiment with 'char' or 'char_wb' for character-level features
    )
    tfidf = vectorizer.fit_transform([text1, text2])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])
    return similarity[0][0]

def print_formatted_response(response):
    # Define the width for wrapping the text
    wrapper = textwrap.TextWrapper(width=80)  # Set to 80 columns wide, but adjust as needed
    wrapped_text = wrapper.fill(text=response)
    # Print the formatted response with a header and footer
    print("Response:")
    print("---------------")
    print(wrapped_text)
    print("---------------\n")