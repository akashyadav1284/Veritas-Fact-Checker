import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import re

# --- INITIALIZE THE FLASK APP ---
app = Flask(__name__)
CORS(app)

# --- CONFIGURATION ---
# IMPORTANT: Paste your FREE Serper API Key here
SERPER_API_KEY = "YOUR_SERPER_API_KEY_HERE"

# --- HELPER FUNCTIONS ---

def scrape_text_from_url(url):
    """Fetches and cleans text from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        for script_or_style in soup(['script', 'style']):
            script_or_style.decompose()
        text = ' '.join(t.strip() for t in soup.stripped_strings)
        return re.sub(r'\s+', ' ', text)[:2000] # Limit text length for analysis
    except Exception:
        return "Error: Could not retrieve content from the URL."

def analyze_with_google_search(claim):
    """
    Uses Google Search (via Serper) to perform a multi-step fact-check.
    """
    if not SERPER_API_KEY or "YOUR_SERPER" in SERPER_API_KEY:
        return {
            "verdict": "Configuration Error",
            "summary": "Serper API key is not configured correctly."
        }

    headers = {'X-API-KEY': SERPER_API_KEY, 'Content-Type': 'application/json'}
    
    # --- Step 1: Proactive Debunking Search ---
    # We search for the claim along with words that indicate a fact-check.
    debunk_query = f'"{claim}" fact check OR hoax OR false OR debunked'
    try:
        response = requests.post('https://google.serper.dev/search', headers=headers, json={'q': debunk_query})
        response.raise_for_status()
        results = response.json().get('organic', [])
        
        for result in results[:3]: # Check the top 3 debunking results
            snippet = result.get('snippet', '').lower()
            title = result.get('title', '').lower()
            # If we find strong debunking language, we can be confident it's misleading.
            if any(word in snippet or word in title for word in ['false', 'hoax', 'misleading', 'incorrect', 'not true']):
                return {
                    "verdict": "Misleading",
                    "summary": f"Fact-checking sources indicate this claim is false or misleading. A top result from '{result.get('link')}' disputes the claim."
                }
    except Exception as e:
        print(f"Debunk search failed: {e}")
        # Continue to the next step even if this search fails

    # --- Step 2: Corroboration Search ---
    # If no debunking was found, we search for the claim on reputable news sites.
    corroboration_query = f'"{claim}" site:bbc.com OR site:reuters.com OR site:timesofindia.indiatimes.com OR site:thehindu.com'
    try:
        response = requests.post('https://google.serper.dev/search', headers=headers, json={'q': corroboration_query})
        response.raise_for_status()
        results = response.json().get('organic', [])
        
        if results: # If we find ANY result from these top-tier sources, it's likely factual.
            return {
                "verdict": "Likely Factual",
                "summary": f"The claim is supported by reports from reputable news sources, including '{results[0].get('link')}'."
            }
    except Exception as e:
        print(f"Corroboration search failed: {e}")
        # Fall through to the final verdict

    # --- Step 3: Fallback Verdict ---
    # If neither search provided a conclusive answer, the claim is unverified.
    return {
        "verdict": "Unverified Claim",
        "summary": "We could not find sufficient information from fact-checking or major news sources to verify this claim. Please proceed with caution."
    }

# --- MAIN API ENDPOINT ---
@app.route('/analyze', methods=['POST'])
def analyze():
    """Receives content from the frontend and uses Google Search for analysis."""
    data = request.get_json()
    content_type = data.get('type')
    content = data.get('content')
    
    analysis_text = ""
    if content_type == 'text':
        analysis_text = content
    elif content_type == 'link':
        analysis_text = scrape_text_from_url(content)
        if analysis_text.startswith("Error:"):
            return jsonify({"verdict": "Content Error", "confidence": "0%", "summary": analysis_text}), 400

    if not analysis_text or len(analysis_text.strip()) < 10:
        return jsonify({"verdict": "Input Error", "confidence": "0%", "summary": "Content is too short."}), 400

    result = analyze_with_google_search(analysis_text)
    
    # Add a confidence score based on the verdict
    if result["verdict"] == "Misleading":
        result["confidence"] = "95%"
    elif result["verdict"] == "Likely Factual":
        result["confidence"] = "92%"
    else: # Unverified or Error
        result["confidence"] = "50%"

    return jsonify(result)

# --- BASIC SERVER ROUTES ---
@app.route('/')
def index():
    return "Veritas Backend with Google Search is running!"

if __name__ == '__main__':
    app.run(debug=True)