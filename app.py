from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import DebertaV2TokenizerFast, DebertaV2ForSequenceClassification
import torch
import time
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

import uuid

# Initialize training data collection
TRAINING_DATA_FILE = "training_data.jsonl"

# Load the guardrail model
def load_model():
    model_path = "./rm_guardrail_model"
    tokenizer = DebertaV2TokenizerFast.from_pretrained(model_path)
    model = DebertaV2ForSequenceClassification.from_pretrained(model_path)
    
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
    entry_id = str(uuid.uuid4())
    data_entry = {
        "id": entry_id,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "predicted_class": predicted_class,
        "label": "SAFE" if predicted_class == 0 else "MISUSE",
        "confidence": float(confidence),
        "processing_time": float(time_taken),
        "user_flagged_incorrect": False
    }
    
    # Append to JSONL file (one JSON object per line)
    with open(TRAINING_DATA_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(data_entry) + "\n")
    
    return entry_id

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
        entry_id = save_prompt_for_training(prompt, predicted_class, confidence, time_taken)
        
        return jsonify({
            'id': entry_id,
            'predicted_class': predicted_class,
            'label': label_map[predicted_class],
            'confidence': confidence,
            'processing_time': time_taken
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/flag', methods=['POST'])
def flag_classification():
    """Flag a classification as incorrect"""
    try:
        data = request.get_json()
        entry_id = data.get('id', '')
        
        if not entry_id:
            return jsonify({'error': 'No entry ID provided'}), 400
        
        # Read all entries
        entries = []
        if os.path.exists(TRAINING_DATA_FILE):
            with open(TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        
        # Find and update the entry
        updated = False
        for entry in entries:
            if entry.get('id') == entry_id:
                entry['user_flagged_incorrect'] = True
                updated = True
                break
        
        if not updated:
            return jsonify({'error': 'Entry not found'}), 404
        
        # Write back all entries
        with open(TRAINING_DATA_FILE, "w", encoding="utf-8") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
        
        return jsonify({'success': True, 'message': 'Classification flagged as incorrect'})
    
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
                flagged_count = sum(1 for line in lines if json.loads(line).get("user_flagged_incorrect", False))
                
                return jsonify({
                    'total_prompts': total_prompts,
                    'safe_count': safe_count,
                    'misuse_count': misuse_count,
                    'flagged_count': flagged_count
                })
            else:
                return jsonify({
                    'total_prompts': 0,
                    'safe_count': 0,
                    'misuse_count': 0,
                    'flagged_count': 0
                })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': 'DeBERTa v2',
        'device': str(device)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
