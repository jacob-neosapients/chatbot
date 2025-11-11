from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import time
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize training data collection
TRAINING_DATA_FILE = "training_data.jsonl"

# Load the guardrail model
def load_model():
    model_path = "./rm_guardrail_model"
    tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    
    # Use GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()  # Set model to evaluation mode
    
    return tokenizer, model, device

print("Loading model...")
tokenizer, model, device = load_model()
print(f"Model loaded successfully on {device}")

def save_prompt_for_training(prompt, predicted_class, confidence, time_taken):
    """Save prompt data in JSONL format for future model training"""
    data_entry = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "predicted_class": predicted_class,
        "label": "SAFE" if predicted_class == 0 else "MISUSE",
        "confidence": float(confidence),
        "processing_time": float(time_taken)
    }
    
    # Append to JSONL file (one JSON object per line)
    with open(TRAINING_DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data_entry) + "\n")

@app.route('/api/classify', methods=['POST'])
def classify_prompt():
    """Classify a user prompt using the guardrail model"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        # Use the guardrail model to classify the input
        start_time = time.time()
        
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, padding=True)
        
        # Move inputs to the correct device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        # Get model prediction (no gradients needed)
        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            predicted_class = torch.argmax(logits, dim=-1).item()
            probabilities = torch.nn.functional.softmax(logits, dim=-1)
            confidence = probabilities[0][predicted_class].item()
        
        # Calculate time taken
        time_taken = time.time() - start_time
        
        # Define label mapping
        label_map = {0: 'SAFE', 1: 'MISUSE'}
        
        # Save prompt for future training
        save_prompt_for_training(prompt, predicted_class, confidence, time_taken)
        
        return jsonify({
            'predicted_class': predicted_class,
            'label': label_map[predicted_class],
            'confidence': confidence,
            'processing_time': time_taken
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get training data statistics"""
    try:
        if not os.path.exists(TRAINING_DATA_FILE):
            return jsonify({
                'total_prompts': 0,
                'safe_count': 0,
                'misuse_count': 0
            })
        
        with open(TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            total_prompts = len(lines)
            
            if total_prompts > 0:
                # Calculate statistics
                safe_count = sum(1 for line in lines if json.loads(line)["predicted_class"] == 0)
                misuse_count = total_prompts - safe_count
                
                return jsonify({
                    'total_prompts': total_prompts,
                    'safe_count': safe_count,
                    'misuse_count': misuse_count
                })
            else:
                return jsonify({
                    'total_prompts': 0,
                    'safe_count': 0,
                    'misuse_count': 0
                })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'DistilBERT',
        'device': str(device)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
