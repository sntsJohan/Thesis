import os
import joblib
import torch
import numpy as np
# Use only the necessary classes
from transformers import BertTokenizer, BertForSequenceClassification 
from utils import get_resource_path # Import the helper function

# --- Model Paths ---
# Define paths using the helper function, assuming a structure
BASE_MODEL = "bert-base-multilingual-cased"  # Base model for fallback
# DAPT_MODEL_DIR = get_resource_path(os.path.join("models", "dapt_model")) # No longer needed
# TAPT_MODEL_DIR = get_resource_path(os.path.join("models", "tapt_model")) # No longer needed
CB_MODEL_DIR = get_resource_path(os.path.join("models", "cb_model")) 
SVM_MODEL_PATH = get_resource_path(os.path.join("models", "svm_model.pkl"))

# --- Global Variables ---
tokenizer = None
# dapt_model = None # No longer needed
# tapt_model = None # No longer needed
cb_model = None
svm_classifier = None

# --- Model Loading Function (Simplified) ---
def load_final_model(model_path, model_name="Model", model_type=BertForSequenceClassification):
    """Helper function to load the final sequence classification model."""
    if os.path.isdir(model_path):
        try:
            model = model_type.from_pretrained(model_path)
            print(f"{model_name} loaded successfully from {model_path}.")
            return model
        except Exception as e:
            print(f"Failed to load {model_name} from {model_path}: {e}. Attempting fallback.")
            try:
                # Fallback to base sequence classification model if specific one fails
                model = BertForSequenceClassification.from_pretrained(BASE_MODEL)
                print(f"Loaded {BASE_MODEL} as fallback {model_name}.")
                return model
            except Exception as fallback_e:
                print(f"CRITICAL: Failed to load fallback model {BASE_MODEL}: {fallback_e}")
                return None # Indicate critical failure
    else:
        print(f"Directory not found for {model_name}: {model_path}. Cannot load.")
        # Attempt fallback if directory not found
        try:
             model = BertForSequenceClassification.from_pretrained(BASE_MODEL)
             print(f"Loaded {BASE_MODEL} as fallback {model_name} due to missing directory.")
             return model
        except Exception as fallback_e:
             print(f"CRITICAL: Failed to load fallback model {BASE_MODEL}: {fallback_e}")
             return None # Indicate critical failure

def initialize_models():
    """Loads the final CB model, tokenizer, and SVM."""
    global tokenizer, cb_model, svm_classifier

    print("Initializing models (Simplified: CB + SVM)...")

    # Load Tokenizer (use the tokenizer associated with the CB model)
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

    # Load ONLY the CB Model using the correct class
    cb_model = load_final_model(CB_MODEL_DIR, "CB Model", BertForSequenceClassification)
    
    if not cb_model:
        # If load_final_model returned None, it means even fallback failed
        raise RuntimeError("CRITICAL: CB Model (and fallback) failed to load. Cannot proceed.")

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

# --- Embedding Generation (Simplified: Direct from CB Model) ---
def generate_final_embedding(text):
    """Generate embeddings for text using ONLY the final CB model."""
    global tokenizer, cb_model

    if not all([tokenizer, cb_model]):
        raise RuntimeError("Models not initialized. Call initialize_models() first.")

    with torch.no_grad():
        # Initial tokenization
        inputs = tokenizer(text, return_tensors='pt', padding=True, truncation=True, max_length=512)
        
        # --- Process directly through CB Model (BertForSequenceClassification) ---
        cb_outputs = cb_model(**inputs, output_hidden_states=True)
        
        # Extract the [CLS] token embedding from the final hidden state
        # Note: BertForSequenceClassification output structure might differ slightly,
        # but hidden_states should still be available if output_hidden_states=True.
        # Accessing the last layer's hidden states [-1], then the CLS token [:, 0, :]
        final_cls_embedding = cb_outputs.hidden_states[-1][:, 0, :].numpy()
        
    return final_cls_embedding

# --- Classification Function (Unchanged, uses the new embedding) ---
def classify_comment(text):
    """
    Classifies a single comment using the CB -> SVM pipeline.
    Returns the prediction label ('Cyberbullying' or 'Normal') and
    the confidence score (0-100).
    """
    global svm_classifier
    if not svm_classifier:
         # Attempt to initialize if not already done (or raise error)
         print("SVM classifier not loaded. Attempting initialization...")
         initialize_models() # Ensure models are loaded before first classification
         if not svm_classifier: # Check again after attempting initialization
             raise RuntimeError("SVM classifier failed to initialize.")

    try:
        # Generate embedding using the new simplified pipeline
        embedding = generate_final_embedding(text).reshape(1, -1)

        # Get prediction (0 or 1) using SVM
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
        # Consider more specific error handling or logging
        return "Error", 0.0

# --- Initial Model Load ---
# Call initialization when the module is loaded or before first use
# initialize_models()
# It might be better to call initialize_models() explicitly from where
# classify_comment is first used (e.g., in your GUI or main script)
# to control when the loading happens.
