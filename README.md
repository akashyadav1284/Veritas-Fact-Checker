## Veritas – Misinformation Detector

Veritas is a web application that helps users quickly assess whether news content is likely to be **fake (misinformation)** or **likely factual**.  
It combines a modern Tailwind‑based frontend with a Flask backend and a locally trained machine‑learning model on the widely used Fake/Real news dataset.

---

### Features

- **Text & URL analysis** – Paste raw article text or a link; the backend scrapes (for URLs) and analyzes the news content.
- **ML‑based classification** – Uses TF‑IDF + `PassiveAggressiveClassifier` trained on Fake/Real news data.
- **Clear verdicts** – Returns:
  - `Misinformation` (red banner) for likely fake content.
  - `Likely Factual` (green banner) for likely true content.
  - Warning states (yellow banner) for errors / uncertain cases.
- **Modern UI** – Single‑page interface built with Tailwind CSS, responsive and mobile‑friendly.

---

### Project Structure

- `app.py` – Flask API server that:
  - Loads `model.joblib` and `vectorizer.joblib`.
  - Exposes `POST /analyze` for content classification.
  - Scrapes article text when given a URL.
- `train_model.py` – Script to train the news classifier on Fake/Real datasets and save:
  - `model.joblib` – trained `PassiveAggressiveClassifier`.
  - `vectorizer.joblib` – fitted `TfidfVectorizer`.
- `index.html` – Frontend UI that calls the backend and displays verdicts.
- `requirements.txt` – Python dependencies (for local dev and Render deployment).

---

### 1. Local Setup

#### 1.1 Clone and enter the project

```bash
git clone <your-repo-url>
cd VeritasProject
```

#### 1.2 Create & activate a virtual environment (recommended)

On Windows (PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate
```

#### 1.3 Install dependencies

```bash
pip install -r requirements.txt
```

#### 1.4 Train the model (one‑time or when retraining)

Make sure the Fake/Real news CSVs are in `archive/Fake.csv` and `archive/True.csv`, then run:

```bash
python train_model.py
```

This will create `model.joblib` and `vectorizer.joblib` in the project root.

---

### 2. Run the App Locally

#### 2.1 Start the Flask backend

```bash
python app.py
```

You should see console output indicating that the model/vectorizer were loaded and that the app is running on `http://127.0.0.1:5000/`.

- Health check: open `http://127.0.0.1:5000/` in a browser – you should see a simple “Veritas Backend…” message.
- The main API endpoint is `POST /analyze` (used by the frontend; it will not respond to GET in the browser).

#### 2.2 Open the frontend

Option A – open the file directly:

1. Open `index.html` in your browser (double‑click or “Open with…”).
2. Use the **Text** or **Link** tab, paste content, and click **Analyze Content**.

Option B – serve via a simple local server:

```bash
python -m http.server 8000
```

Then open `http://127.0.0.1:8000/index.html` in your browser.

---

### 3. Deployment to Render (overview)

1. **Push this project to GitHub** (including `requirements.txt`, `model.joblib`, `vectorizer.joblib`, and code).
2. **Create a Web Service (backend)** on Render:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
3. Note the backend URL from Render, e.g. `https://veritas-backend.onrender.com`.
4. In `index.html`, update the fetch call to use that URL:

```javascript
const response = await fetch('https://veritas-backend.onrender.com/analyze', {
```

5. **Create a Static Site (frontend)** on Render pointing to this repo, with `index.html` in the root.

After both services are live, visiting the Static Site URL will give you the live Veritas app backed by the Render API.

---

### 4. API Reference

#### `POST /analyze`

**Request body (JSON):**

```json
{
  "type": "text",   // "text" or "link"
  "content": "Full news article text or a URL"
}
```

**Successful response (200):**

```json
{
  "verdict": "Misinformation | Likely Factual",
  "confidence": "92%",
  "summary": "Human-readable explanation"
}
```

On errors (invalid input, scraping failure, model not loaded), the response also includes an `error` field and may use status codes like 400 or 500.

---

### 5. Notes & Limitations

- This is a **pattern‑based classifier**, not a ground‑truth oracle; it judges similarity to known fake/real news in the training data.
- Always cross‑check important information with trusted sources, even if the model labels it “Likely Factual”.
- For best results, provide **full article text**, not just headlines or very short snippets.

