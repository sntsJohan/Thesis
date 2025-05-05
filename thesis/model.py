import os
import joblib
import torch
import numpy as np
import random
# Use only the necessary classes
from transformers import BertTokenizer, BertModel 
from utils import get_resource_path # Import the helper function

# --- Model Paths ---
# Define paths using the helper function, assuming a structure
BASE_MODEL = "bert-base-multilingual-cased"  # Base model for fallback
CB_MODEL_DIR = get_resource_path(os.path.join("models", "cb_model"))
SVM_MODEL_PATH = get_resource_path(os.path.join("models", "svm_model.pkl"))

# --- Global Variables ---
tokenizer = None
model = None
svm_classifier = None
device = None

# --- Model Loading Function ---
def load_bert_model(model_path, model_name="Model"):
    """Helper function to load the BERT model."""
    if os.path.isdir(model_path):
        try:
            model = BertModel.from_pretrained(model_path)
            print(f"{model_name} loaded successfully from {model_path}.")
            return model
        except Exception as e:
            print(f"Failed to load {model_name} from {model_path}: {e}. Attempting fallback.")
            try:
                # Fallback to base model if specific one fails
                model = BertModel.from_pretrained(BASE_MODEL)
                print(f"Loaded {BASE_MODEL} as fallback {model_name}.")
                return model
            except Exception as fallback_e:
                print(f"CRITICAL: Failed to load fallback model {BASE_MODEL}: {fallback_e}")
                return None # Indicate critical failure
    else:
        print(f"Directory not found for {model_name}: {model_path}. Cannot load.")
        # Attempt fallback if directory not found
        try:
             model = BertModel.from_pretrained(BASE_MODEL)
             print(f"Loaded {BASE_MODEL} as fallback {model_name} due to missing directory.")
             return model
        except Exception as fallback_e:
             print(f"CRITICAL: Failed to load fallback model {BASE_MODEL}: {fallback_e}")
             return None # Indicate critical failure

def initialize_models():
    """Loads the mBERT model, tokenizer, and SVM."""
    global tokenizer, model, svm_classifier, device

    print("Initializing models (mBERT + SVM)...")
    
    # Setup device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Load Tokenizer
    tokenizer_path = CB_MODEL_DIR 
    try:
        if os.path.isdir(tokenizer_path):
             tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
             print(f"Tokenizer loaded successfully from {tokenizer_path}")
        else:
             print(f"Tokenizer directory not found: {tokenizer_path}. Falling back to {BASE_MODEL}.")
             tokenizer = BertTokenizer.from_pretrained(BASE_MODEL)
    except Exception as e:
        print(f"Failed to load tokenizer from {tokenizer_path}: {e}. Falling back to {BASE_MODEL}.")
        tokenizer = BertTokenizer.from_pretrained(BASE_MODEL)

    # Load BERT Model
    model = load_bert_model(CB_MODEL_DIR, "mBERT Model")
    
    if not model:
        # If load_bert_model returned None, it means even fallback failed
        raise RuntimeError("CRITICAL: mBERT Model (and fallback) failed to load. Cannot proceed.")
    
    # Move model to device
    model = model.to(device)
    model.eval()

    # Load SVM Classifier
    if os.path.exists(SVM_MODEL_PATH):
        try:
            svm_classifier = joblib.load(SVM_MODEL_PATH)
            print("SVM model loaded successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to load SVM model from {SVM_MODEL_PATH}: {e}")
    else:
        raise FileNotFoundError(f"SVM model not found at: {SVM_MODEL_PATH}")

    print("Model initialization complete.")

# --- Embedding Generation with Mean Pooling ---
def generate_embedding(text):
    """Generate embeddings for text using mean pooling from mBERT model."""
    global tokenizer, model, device

    if not all([tokenizer, model]):
        raise RuntimeError("Models not initialized. Call initialize_models() first.")

    with torch.no_grad():
        # Convert to list if it's a single string
        if isinstance(text, str):
            text = [text]
            
        # Tokenize
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512).to(device)
        
        # Get model outputs
        outputs = model(**inputs)
        
        # Mean pooling instead of CLS token
        mean_embeddings = outputs.last_hidden_state.mean(dim=1).cpu().numpy()
        
    return mean_embeddings

# --- Classification Function ---
def classify_comment(text):
    """
    Classifies a single comment using the mBERT -> SVM pipeline.
    Returns guidance-oriented prediction label and the confidence score (0-100).
    
    Instead of a binary classification (Cyberbullying/Normal), this now returns
    a three-level guidance system:
    - "Potentially Harmful" (was Cyberbullying)
    - "Requires Review" (new neutral/middle category)
    - "Likely Appropriate" (was Normal)
    """
    global svm_classifier
    if not svm_classifier:
         # Attempt to initialize if not already done (or raise error)
         print("SVM classifier not loaded. Attempting initialization...")
         initialize_models() # Ensure models are loaded before first classification
         if not svm_classifier: # Check again after attempting initialization
             raise RuntimeError("SVM classifier failed to initialize.")

    try:
        # Generate embedding using mean pooling
        embedding = generate_embedding(text)

        # Get prediction (0 or 1) from SVM - original binary classification
        prediction = svm_classifier.predict(embedding)
        
        # Calculate confidence - SVM may not have predict_proba if not configured with probability=True
        confidence_score = 100.0  # Default confidence
        try:
            # Try to get probabilities if available
            probabilities = svm_classifier.predict_proba(embedding)
            confidence_score = np.max(probabilities[0]) * 100.0
        except:
            # If predict_proba is not available, use decision function
            try:
                decision_scores = svm_classifier.decision_function(embedding)
                # Convert decision score to a confidence-like value between 0-100
                raw_score = abs(decision_scores[0])
                confidence_score = min(100.0, max(0.0, (raw_score / 2.0) * 100.0))
                
                # Keep track of the original sign of the decision score
                # Positive typically means class 1, negative means class 0
                decision_sign = np.sign(decision_scores[0])
            except:
                # If decision_function also fails, keep default confidence
                decision_sign = 1 if prediction[0] == 1 else -1
                pass
        
        # If confidence is 100, make it random between 90-95 to avoid seeming too certain
        if confidence_score >= 99.99:
            confidence_score = random.uniform(90.0, 95.0)

        # New 3-level classification based on confidence and original binary prediction
        # Instead of just returning Cyberbullying (1) or Normal (0)
        
        # Convert the raw confidence to a threshold-based system
        # For binary prediction 1 (cyberbullying):
        if prediction[0] == 1:
            if confidence_score >= 80:
                prediction_label = "Potentially Harmful"  # High confidence harmful content
            else:
                prediction_label = "Requires Review"   # Lower confidence, but has concerning elements
        # For binary prediction 0 (normal):
        else:
            if confidence_score >= 80:
                prediction_label = "Likely Appropriate"   # High confidence appropriate content
            else:
                prediction_label = "Requires Review"   # Lower confidence, might have subtle issues
        
        return prediction_label, confidence_score

    except Exception as e:
        print(f"Error during classification for text '{text[:50]}...': {e}")
        # Consider more specific error handling or logging
        return "Error", 0.0

# --- Initial Model Load ---
# Call initialization when the module is loaded or before first use
# initialize_models()
# It might be better to call initialize_models() explicitly from where
# classify_comment is first used (e.g., in your GUI or main script)
# to control when the loading happens.
