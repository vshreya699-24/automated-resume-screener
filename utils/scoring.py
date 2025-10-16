# utils/scoring.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_match_score(jd_text, resume_text):
    """
    Calculate the similarity score between the Job Description and Resume text.
    Returns a percentage (0–100).
    """
    if not jd_text or not resume_text:
        return 0

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf = vectorizer.fit_transform([jd_text, resume_text])
    similarity = cosine_similarity(tfidf[0:1], tfidf[1:2])[0][0]

    # Convert to percentage (0–100)
    percentage_score = round(similarity * 100, 2)
    return percentage_score
