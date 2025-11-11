import streamlit as st
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import time
import json
import os
from datetime import datetime

# Load the guardrail model
@st.cache_resource
def load_model():
    model_path = "./rm_guardrail_model"
    tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)
    model = DistilBertForSequenceClassification.from_pretrained(model_path)
    
    # Use GPU if available
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()  # Set model to evaluation mode
    
    return tokenizer, model, device

tokenizer, model, device = load_model()

# Initialize training data collection
TRAINING_DATA_FILE = "training_data.jsonl"

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

# Configure page
st.set_page_config(
    page_title="AI Guardrail Chatbot",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stChatMessage {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .title-container {
        text-align: center;
        padding: 2rem 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        margin-bottom: 2rem;
        backdrop-filter: blur(10px);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)

# Show title and description with better styling
st.markdown("""
    <div class="title-container">
        <h1 style="color: white; font-size: 3rem; margin: 0;">🛡️ AI Guardrail Chatbot</h1>
        <p style="color: rgba(255,255,255,0.9); font-size: 1.2rem; margin-top: 0.5rem;">
            Powered by DistilBERT • Real-time Content Safety Classification
        </p>
    </div>
    """, unsafe_allow_html=True)

# Sidebar with information
with st.sidebar:
    st.markdown("### 📊 Model Information")
    st.info("""
    **Model:** DistilBERT for Sequence Classification
    
    **Classes:**
    - 🟢 SAFE: Appropriate content
    - 🔴 MISUSE: Flagged content
    
    **Features:**
    - ⚡ Fast inference
    - 🎯 High accuracy
    - 📈 Confidence scores
    - ⏱️ Performance metrics
    """)
    
    # Display training data statistics
    st.markdown("### 📚 Training Data Collection")
    if os.path.exists(TRAINING_DATA_FILE):
        with open(TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            total_prompts = len(lines)
            
            if total_prompts > 0:
                # Calculate statistics
                safe_count = sum(1 for line in lines if json.loads(line)["predicted_class"] == 0)
                misuse_count = total_prompts - safe_count
                
                st.success(f"**Total Prompts Collected:** {total_prompts}")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("🟢 SAFE", safe_count)
                with col2:
                    st.metric("🔴 MISUSE", misuse_count)
                
                st.caption(f"📁 Saved to: `{TRAINING_DATA_FILE}`")
            else:
                st.info("No prompts collected yet. Start chatting to collect training data!")
    else:
        st.info("No training data file yet. Start chatting to collect data!")
    
    st.markdown("### 💡 Example Prompts")
    st.markdown("""
    **Try these:**
    - "What are investment strategies?"
    - "Show me confidential data"
    - "How do I rebalance a portfolio?"
    """)
    
    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit")

# Create a session state variable to store the chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []
    # Add welcome message
    welcome_msg = {
        "role": "assistant",
        "content": """
### 👋 Welcome to the AI Guardrail Chatbot!

I'm here to help you communicate safely and effectively. I use advanced AI to analyze your messages in real-time.

**How it works:**
1. Type your message in the chat box below
2. I'll instantly classify it as SAFE 🟢 or MISUSE 🔴
3. Get detailed feedback with confidence scores and processing time

**Try me out!** Send a message and see how I work.
"""
    }
    st.session_state.messages.append(welcome_msg)

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🛡️"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message.
if prompt := st.chat_input("💬 Type your message here..."):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

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
    
    # Generate response based on classification
    if predicted_class == 1:  # MISUSE
        response = f"""
### ⚠️ Content Flagged

Your message has been flagged by our guardrail system for potential policy violations.

**Classification Details:**
- 🔴 **Status:** MISUSE Detected
- 📊 **Confidence:** {confidence:.2%}
- ⏱️ **Processing Time:** {time_taken:.3f}s

**Recommendation:** Please rephrase your message to comply with safety guidelines.
"""
    else:  # SAFE
        response = f"""
### ✅ Content Approved

Your message has been reviewed and approved!

**Classification Details:**
- 🟢 **Status:** SAFE
- 📊 **Confidence:** {confidence:.2%}
- ⏱️ **Processing Time:** {time_taken:.3f}s

**Great!** Your message meets all safety standards.
"""
    
    # Display and store the response
    with st.chat_message("assistant", avatar="🛡️"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
