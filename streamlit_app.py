import streamlit as st
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch

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

# Show title and description.
st.title("💬 Chatbot with Guardrail")
st.write(
    "This chatbot uses a local DistilBERT guardrail model to classify and respond to messages. "
    "The model evaluates input text for content safety and provides appropriate responses."
)

# Create a session state variable to store the chat messages.
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display the existing chat messages via `st.chat_message`.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Create a chat input field to allow the user to enter a message.
if prompt := st.chat_input("What is up?"):

    # Store and display the current prompt.
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Use the guardrail model to classify the input
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
    
    # Define label mapping
    label_map = {0: 'SAFE', 1: 'MISUSE'}
    
    # Generate response based on classification
    if predicted_class == 1:  # MISUSE
        response = f"⚠️ This content has been flagged by the guardrail model (confidence: {confidence:.2%}). Please rephrase your message."
    else:  # SAFE
        response = f"✅ Your message passed the guardrail check (confidence: {confidence:.2%}). This is a safe and appropriate message."
    
    # Display and store the response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
