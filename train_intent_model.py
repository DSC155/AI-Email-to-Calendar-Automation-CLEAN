import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import joblib

df = pd.read_csv("enron_500_labeled.csv")

X = df["message"]
y = df["label"]

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=30000,
    ngram_range=(1,2)
)

X_vec = vectorizer.fit_transform(X)

model = LogisticRegression(max_iter=1000)
model.fit(X_vec, y)

joblib.dump(model, "intent_model.pkl")
joblib.dump(vectorizer, "vectorizer.pkl")

print("✅ Intent model trained")
