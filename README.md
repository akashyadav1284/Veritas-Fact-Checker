Veritas – Misinformation Detector--
Veritas is a machine-learning–powered web application that helps users determine whether news content is likely misinformation or factually reliable.
It combines a Flask backend, Tailwind-based frontend, and a TF-IDF + PassiveAggressiveClassifier model trained on Fake/Real news datasets.



Features--
1.Analyze article text or URLs
2.ML-based classification using TF-IDF vectorization
3.Clear verdicts:
4.Misinformation
5.Likely Factual
6.Simple single-page responsive UI
7.URL content scraping support

Tech Stack--
1.Python
2.Flask
3.Scikit-learn
4.BeautifulSoup
5.Tailwind CSS
6.HTML / JavaScript


project structure--

app.py              # Flask backend API
train_model.py      # Model training script
index.html          # Frontend UI
requirements.txt    # Dependencies
model.joblib        # Trained classifier
vectorizer.joblib   # TF-IDF vectorizer
archive/            # Fake/True dataset CSV files


create virtual enviornment--
python -m venv venv
.\venv\Scripts\Activate


Install dependencies--
pip install -r requirements.txt

train model--
python train_model.py



summary--
Veritas – Misinformation Detector is a machine-learning–powered web application designed to help users quickly determine whether news content is likely misinformation or factually reliable. The project combines a Flask backend, a responsive Tailwind-based frontend, and a locally trained ML model using TF-IDF vectorization with a PassiveAggressiveClassifier trained on Fake and Real news datasets. Users can analyze either raw article text or a URL, where the backend scrapes the article content and classifies it as Misinformation or Likely Factual, along with a confidence score and summary explanation. The project includes key components such as app.py for the API server, train_model.py for training the classifier, index.html for the user interface, and saved model files (model.joblib and vectorizer.joblib). To run locally, users can clone the repository, create a virtual environment, install dependencies from requirements.txt, optionally retrain the model, start the Flask server using python app.py, and open the frontend in a browser. The application exposes a POST /analyze API endpoint that accepts text or link input and returns a prediction result. While Veritas provides helpful automated analysis, it is a pattern-based classifier and should be used as a support tool rather than a definitive source of truth, and important information should always be verified using trusted sources.




