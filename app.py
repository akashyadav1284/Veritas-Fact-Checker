import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re
import joblib
import numpy as np
from flask import send_from_directory


# --- INITIALIZE THE FLASK APP ---
app = Flask(__name__)
CORS(app)

# --- MODEL LOADING ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.joblib")
VECTORIZER_PATH = os.path.join(BASE_DIR, "vectorizer.joblib")

classifier = None
vectorizer = None

try:
    classifier = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    print("✅ Loaded classification model and vectorizer.")
except Exception as e:
    print(f"⚠️ Could not load model/vectorizer: {e}")

# --- HELPER FUNCTIONS ---

def scrape_text_from_url(url):
    """Fetches and cleans text from a URL."""
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/58.0.3029.110 Safari/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        for script_or_style in soup(["script", "style"]):
            script_or_style.decompose()
        text = " ".join(t.strip() for t in soup.stripped_strings)
        # Limit text length for analysis so it doesn't blow up the vectorizer
        return re.sub(r"\s+", " ", text)[:2000]
    except Exception:
        return "Error: Could not retrieve content from the URL."


def analyze_with_model(content_text: str):
    """
    Uses the locally trained TF-IDF + PassiveAggressive model
    to classify news as REAL or FAKE, and maps that to a
    human-friendly verdict.
    """
    if classifier is None or vectorizer is None:
        return {
            "verdict": "Configuration Error",
            "confidence": "0%",
            "summary": (
                "The classification model is not available. "
                "Please run 'python train_model.py' to train it "
                "and then restart the Flask server."
            ),
            "error": "Model or vectorizer not loaded.",
        }

    try:
        features = vectorizer.transform([content_text])
        label = classifier.predict(features)[0]  # 'FAKE' or 'REAL'

        # Estimate confidence from the decision function
        try:
            decision = classifier.decision_function(features)[0]
            # Map margin -> (50% .. 100%) style confidence
            raw_conf = 1.0 / (1.0 + np.exp(-abs(decision)))
            confidence_pct = int(raw_conf * 100)
        except Exception:
            # Fallback if decision_function is unavailable
            confidence_pct = 90

        if label == "FAKE":
            verdict = "Misinformation"
            summary = (
                "The content closely matches patterns seen in known fake news "
                "from the training data. Treat this as likely false or misleading."
            )
        else:
            verdict = "Likely Factual"
            summary = (
                "The content is stylistically similar to reliable news articles "
                "in the training data, but you should still cross-check with "
                "trusted sources for important decisions."
            )

        return {
            "verdict": verdict,
            "confidence": f"{confidence_pct}%",
            "summary": summary,
        }
    except Exception as e:
        return {
            "verdict": "Analysis Error",
            "confidence": "0%",
            "summary": "An error occurred while analyzing the content.",
            "error": str(e),
        }

# --- MAIN API ENDPOINT ---
@app.route('/analyze', methods=['POST'])
def analyze():
    """Receives content from the frontend and uses the ML model for analysis."""
    data = request.get_json()
    content_type = data.get('type')
    content = data.get('content')
    
    analysis_text = ""
    if content_type == 'text':
        analysis_text = content
    elif content_type == 'link':
        analysis_text = scrape_text_from_url(content)
        if analysis_text.startswith("Error:"):
            return jsonify({
                "verdict": "Content Error",
                "confidence": "0%",
                "summary": analysis_text,
                "error": analysis_text
            }), 400

    if not analysis_text or len(analysis_text.strip()) < 10:
        msg = "Content is too short for meaningful analysis."
        return jsonify({
            "verdict": "Input Error",
            "confidence": "0%",
            "summary": msg,
            "error": msg
        }), 400

    result = analyze_with_model(analysis_text)

    # If the model reported a configuration or analysis error, surface that clearly
    if result.get("verdict") in {"Configuration Error", "Analysis Error"}:
        return jsonify(result), 500

    return jsonify(result)

# --- BASIC SERVER ROUTES ---
@app.route("/")
def home():
    return send_from_directory(".", "index.html")

if __name__ == '__main__':
    app.run(debug=True)


