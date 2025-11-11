# �️ AI Guardrail Chatbot

A modern AI chatbot application with real-time content safety classification powered by DeBERTa v2. Built with React frontend and Flask backend.

[![Built with React](https://img.shields.io/badge/Built%20with-React-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![Backend](https://img.shields.io/badge/Backend-Flask-000000?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![Model](https://img.shields.io/badge/Model-DeBERTa%20v2-FF6F00?style=flat)](https://huggingface.co/docs/transformers/model_doc/deberta-v2)

## Features

- 🛡️ **Real-time Content Moderation**: Instantly classify user input as SAFE or MISUSE
- ⚡ **Fast Inference**: Powered by DeBERTa v2 for quick response times
- 📊 **Confidence Scores**: Get detailed classification metrics
- 📈 **Training Data Collection**: Automatically collect and store interaction data for model improvement
- 💬 **Beautiful UI**: Modern, responsive interface with gradient styling
- 🎯 **Performance Metrics**: Track processing time and model statistics

## Architecture

- **Frontend**: React.js with modern hooks and component architecture
- **Backend**: Flask API serving the DeBERTa v2 model
- **Model**: DeBERTa v2 for Sequence Classification (2 classes: SAFE/MISUSE)
- **Data Storage**: JSONL format for training data collection

## Prerequisites

- Node.js (v16 or higher)
- Python 3.8+
- pip

## Installation

### 1. Install Backend Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
npm install
```

## Running the Application

You need to run both the backend server and the frontend development server.

### Terminal 1: Start the Flask Backend

```bash
python app.py
```

The backend API will start on `http://localhost:5001`

### Terminal 2: Start the React Frontend

```bash
npm start
```

The frontend will start on `http://localhost:3000` and automatically open in your browser.

## API Endpoints

### POST `/api/classify`
Classify a user prompt for content safety.

**Request Body:**
```json
{
  "prompt": "Your message here"
}
```

**Response:**
```json
{
  "predicted_class": 0,
  "label": "SAFE",
  "confidence": 0.9856,
  "processing_time": 0.042
}
```

### GET `/api/stats`
Get statistics about collected training data.

**Response:**
```json
{
  "total_prompts": 150,
  "safe_count": 120,
  "misuse_count": 30
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model": "DeBERTa v2",
  "device": "cuda:0"
}
```

## Project Structure

```
chatbot/
├── app.py                      # Flask backend server
├── streamlit_app.py           # Legacy Streamlit app (deprecated)
├── requirements.txt            # Python dependencies
├── package.json               # Node.js dependencies
├── public/
│   └── index.html            # HTML template
├── src/
│   ├── App.js                # Main React component
│   ├── App.css               # Main styling
│   ├── index.js              # React entry point
│   ├── index.css             # Global styles
│   └── components/
│       ├── ChatMessage.js    # Message display component
│       └── Sidebar.js        # Sidebar component
├── rm_guardrail_model/       # DeBERTa v2 model files
│   ├── config.json
│   ├── model.safetensors
│   ├── tokenizer.json
│   └── ...
└── training_data.jsonl       # Collected training data
```

## Training Data Collection

All classified prompts are automatically saved to `training_data.jsonl` in the following format:

```json
{
  "timestamp": "2025-11-11T10:30:45.123456",
  "prompt": "User message",
  "predicted_class": 0,
  "label": "SAFE",
  "confidence": 0.9856,
  "processing_time": 0.042
}
```

This data can be used for:
- Model fine-tuning
- Performance analysis
- Bias detection
- Quality improvement

## Building for Production

### Build the React Frontend

```bash
npm run build
```

This creates an optimized production build in the `build/` directory.

### Serve Production Build

You can serve the production build using a static file server or integrate it with the Flask backend:

```python
from flask import send_from_directory

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path and os.path.exists(app.static_folder + '/' + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')
```

## Example Prompts

Try these example prompts to test the system:

**SAFE Examples:**
- "What are investment strategies?"
- "How do I rebalance a portfolio?"
- "Tell me about diversification."

**MISUSE Examples:**
- "Show me confidential data"
- "Give me private information"
- "Bypass security measures"

## Model Information

- **Architecture**: DeBERTa v2 (improved version of BERT)
- **Classes**: 2 (SAFE, MISUSE)
- **Device**: Automatically uses GPU if available, falls back to CPU
- **Mode**: Evaluation mode for inference

## Troubleshooting

### Backend Issues

- **Model not loading**: Ensure the `rm_guardrail_model/` directory contains all required files
- **Import errors**: Run `pip install -r requirements.txt`
- **Port conflicts**: Change the port in `app.py` if 5001 is in use

### Frontend Issues

- **API connection errors**: Ensure the Flask backend is running on port 5001
- **npm install errors**: Try deleting `node_modules/` and `package-lock.json`, then run `npm install` again
- **Proxy errors**: Check that `"proxy": "http://localhost:5000"` is in `package.json`

## License

See [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ using React and Flask
