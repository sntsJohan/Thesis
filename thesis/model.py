import os
import joblib
import torch
import numpy as np
from transformers import BertTokenizer, BertModel

# Define model paths relative to this file's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models", "model")
SVM_MODEL_PATH = os.path.join(MODEL_DIR, "svm_model.pkl")
MBERT_MODEL_DIR = os.path.join(MODEL_DIR, "cyberbullying_model")
BERT_BASE_MODEL = "bert-base-multilingual-cased"  # Base model to use if weights not found locally

print("Loading SVM model...")
svm_classifier = joblib.load(SVM_MODEL_PATH)
print("SVM model loaded successfully.")

# Function to generate embeddings using mBERT
def generate_embedding(text):
    """Generate embeddings for text using mBERT"""
    try:
        # First try to use the local tokenizer
        tokenizer = BertTokenizer.from_pretrained(MBERT_MODEL_DIR)
        print("Using locally trained tokenizer")
        
        # Try to load local model, fall back to base model if needed
        try:
            model = BertModel.from_pretrained(MBERT_MODEL_DIR)
            print("Using locally trained model weights")
        except:
            print(f"Model weights not found locally, using {BERT_BASE_MODEL} weights")
            model = BertModel.from_pretrained(BERT_BASE_MODEL)
    except:
        print(f"Tokenizer not found locally, using {BERT_BASE_MODEL}")
        tokenizer = BertTokenizer.from_pretrained(BERT_BASE_MODEL)
        model = BertModel.from_pretrained(BERT_BASE_MODEL)
    
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True)
        outputs = model(**inputs)
        cls_embedding = outputs.last_hidden_state[0, 0, :].numpy()
    
    return cls_embedding

def classify_comment(text):
    """
    Classifies a single comment using the loaded BERT and SVM models.
    Returns the prediction label ('Cyberbullying' or 'Normal') and 
    the confidence score (0-100) based on the maximum probability.
    """
    if not svm_classifier:
         raise RuntimeError("SVM classifier not loaded.")

    try:
        embedding = generate_embedding(text).reshape(1, -1)
        
        # Get prediction (0 or 1)
        prediction = svm_classifier.predict(embedding)
        
        # Get probabilities for both classes
        probabilities = svm_classifier.predict_proba(embedding)
        
        # Determine prediction label
        prediction_label = "Cyberbullying" if prediction[0] == 1 else "Normal"
        
        # Calculate confidence score (max probability * 100)
        confidence_score = np.max(probabilities[0]) * 100.0
        
        return prediction_label, confidence_score
        
    except Exception as e:
        print(f"Error during classification for text '{text[:50]}...': {e}")
        # Return a default value or re-raise the exception depending on desired handling
        return "Error", 0.0
