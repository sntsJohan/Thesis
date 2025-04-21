import os
import joblib
import torch
import numpy as np
from transformers import BertTokenizer, BertModel
from utils import get_resource_path # Import the helper function

# Define model paths using the helper function
SVM_MODEL_PATH = get_resource_path(os.path.join("models", "model", "svm_model.pkl"))
MBERT_MODEL_DIR = get_resource_path(os.path.join("models", "model", "cyberbullying_model"))
BERT_BASE_MODEL = "bert-base-multilingual-cased"  # Base model to use if weights not found locally

# Ensure the directories exist before trying to load from them
if not os.path.exists(SVM_MODEL_PATH):
    raise FileNotFoundError(f"SVM model not found at: {SVM_MODEL_PATH}")
if not os.path.isdir(MBERT_MODEL_DIR):
    print(f"Warning: Local mBERT directory not found at: {MBERT_MODEL_DIR}. Will attempt to use base model.")
    # You might want to handle this more gracefully, e.g., by downloading if necessary
    # or raising an error if local weights are mandatory.

print("Loading SVM model...")
svm_classifier = joblib.load(SVM_MODEL_PATH)
print("SVM model loaded successfully.")

# Function to generate embeddings using mBERT
def generate_embedding(text):
    """Generate embeddings for text using mBERT"""
    tokenizer = None
    model = None
    # Prioritize loading local model/tokenizer if the directory exists
    if os.path.isdir(MBERT_MODEL_DIR):
        try:
            tokenizer = BertTokenizer.from_pretrained(MBERT_MODEL_DIR)
            print("Using locally trained tokenizer")
            try:
                model = BertModel.from_pretrained(MBERT_MODEL_DIR)
                print("Using locally trained model weights")
            except Exception as e_model:
                print(f"Local model weights failed to load ({e_model}), falling back to {BERT_BASE_MODEL} weights")
        except Exception as e_tokenizer:
            print(f"Local tokenizer failed to load ({e_tokenizer}), falling back to {BERT_BASE_MODEL}")

    # Fallback to base model if local loading failed or directory didn't exist
    if tokenizer is None or model is None:
        print(f"Using {BERT_BASE_MODEL} tokenizer and model.")
        tokenizer = BertTokenizer.from_pretrained(BERT_BASE_MODEL)
        model = BertModel.from_pretrained(BERT_BASE_MODEL)
    
    with torch.no_grad():
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512) # Added max_length
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
