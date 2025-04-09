import os
import joblib
import torch
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

def classify_comment(comment):
    """Classify a comment as cyberbullying or not"""
    try:
        # Generate embeddings using mBERT
        comment_embedding = generate_embedding(comment).reshape(1, -1)
        
        # Predict using SVM
        prediction = svm_classifier.predict(comment_embedding)
        
        # Get confidence score
        confidence_score = svm_classifier.decision_function(comment_embedding)[0]
        
        # Format result
        result = "Cyberbullying" if prediction[0] == 1 else "Not Cyberbullying"
        
        return result, float(confidence_score)
    
    except Exception as e:
        print(f"Error during prediction: {e}")
        return "Error", 0.0
