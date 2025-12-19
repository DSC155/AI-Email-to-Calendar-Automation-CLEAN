import joblib

model = joblib.load("intent_model.pkl")
vectorizer = joblib.load("vectorizer.pkl")

def predict_intent(text):
    X = vectorizer.transform([text])
    label = model.predict(X)[0]
    confidence = max(model.predict_proba(X)[0])
    return label, confidence
