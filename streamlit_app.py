import streamlit as st
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# Load the guardrail model
@st.cache_resource
def load_model():
    model_path = "./rm_guardrail_model"
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    return tokenizer, model

tokenizer, model = load_model()

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
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        predicted_class = torch.argmax(probabilities, dim=-1).item()
        confidence = probabilities[0][predicted_class].item()
    
    # Generate response based on classification
    if predicted_class == 0:
        response = f"⚠️ This content has been flagged by the guardrail model (confidence: {confidence:.2%}). Please rephrase your message."
    else:
        response = f"✅ Your message passed the guardrail check (confidence: {confidence:.2%}). This is a safe and appropriate message."
    
    # Display and store the response
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
