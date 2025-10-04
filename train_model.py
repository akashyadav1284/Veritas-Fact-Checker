import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.metrics import accuracy_score
import joblib

# 1. Load and prepare the data
print("Loading data...")
# This is the NEW, correct code
fake_df = pd.read_csv('archive/Fake.csv')
true_df = pd.read_csv('archive/True.csv')

fake_df['label'] = 'FAKE'
true_df['label'] = 'REAL'

# Combine the datasets
df = pd.concat([fake_df, true_df], ignore_index=True)

# Combine title and text for better feature extraction
df['full_text'] = df['title'] + ' ' + df['text']

# Select features and labels
labels = df['label']
text = df['full_text']

# 2. Split the data
print("Splitting data...")
x_train, x_test, y_train, y_test = train_test_split(text, labels, test_size=0.2, random_state=42)

# 3. Create a TfidfVectorizer
print("Vectorizing text...")
# This turns text into numbers that the model can understand.
# We ignore common English stop words (like 'the', 'a', 'is').
vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7)
tfidf_train = vectorizer.fit_transform(x_train)
tfidf_test = vectorizer.transform(x_test)

# 4. Train the classifier
print("Training model...")
# PassiveAggressiveClassifier is a good choice for text classification.
pac = PassiveAggressiveClassifier(max_iter=50)
pac.fit(tfidf_train, y_train)

# 5. Evaluate the model
y_pred = pac.predict(tfidf_test)
score = accuracy_score(y_test, y_pred)
print(f"Model trained! Accuracy: {score*100:.2f}%")

# 6. Save the model and the vectorizer
print("Saving model and vectorizer...")
joblib.dump(pac, 'model.joblib')
joblib.dump(vectorizer, 'vectorizer.joblib')

print("Setup complete! You can now run the Flask app.")