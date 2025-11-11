import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import ChatMessage from './components/ChatMessage';
import Sidebar from './components/Sidebar';

function App() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState({ total_prompts: 0, safe_count: 0, misuse_count: 0, flagged_count: 0 });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Add welcome message
    const welcomeMsg = {
      role: 'assistant',
      content: `### 👋 Welcome to the AI Guardrail Chatbot!

I'm here to help you communicate safely and effectively. I use advanced AI to analyze your messages in real-time.

**How it works:**
1. Type your message in the chat box below
2. I'll instantly classify it as SAFE 🟢 or MISUSE 🔴
3. Get detailed feedback with confidence scores and processing time

**Try me out!** Send a message and see how I work.`
    };
    setMessages([welcomeMsg]);

    // Fetch initial stats
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await axios.get('/api/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const flagClassification = async (classificationId) => {
    try {
      await axios.post('/api/flag', { id: classificationId });
      // Optionally show a success message or update the message
      alert('Classification flagged as incorrect. Thank you for your feedback!');
    } catch (error) {
      console.error('Error flagging classification:', error);
      alert('Error flagging classification. Please try again.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: inputValue
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/classify', {
        prompt: inputValue
      });

      const { id, predicted_class, label, confidence, processing_time } = response.data;

      let assistantContent;
      if (predicted_class === 1) { // MISUSE
        assistantContent = `### ⚠️ Content Flagged

Your message has been flagged by our guardrail system for potential policy violations.

**Classification Details:**
- 🔴 **Status:** MISUSE Detected
- 📊 **Confidence:** ${(confidence * 100).toFixed(2)}%
- ⏱️ **Processing Time:** ${processing_time.toFixed(3)}s

**Recommendation:** Please rephrase your message to comply with safety guidelines.`;
      } else { // SAFE
        assistantContent = `### ✅ Content Approved

Your message has been reviewed and approved!

**Classification Details:**
- 🟢 **Status:** SAFE
- 📊 **Confidence:** ${(confidence * 100).toFixed(2)}%
- ⏱️ **Processing Time:** ${processing_time.toFixed(3)}s

**Great!** Your message meets all safety standards.`;
      }

      const assistantMessage = {
        role: 'assistant',
        content: assistantContent,
        classificationId: id,
        predictedClass: predicted_class
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Refresh stats after classification
      fetchStats();
    } catch (error) {
      console.error('Error classifying message:', error);
      const errorMessage = {
        role: 'assistant',
        content: '❌ **Error:** Unable to classify message. Please try again.'
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <Sidebar stats={stats} />
      <div className="main-content">
        <div className="title-container">
          <h1>🛡️ AI Guardrail Chatbot</h1>
          <p>Powered by DeBERTa v2 • Real-time Content Safety Classification</p>
        </div>

        <div className="chat-container">
          <div className="messages-container">
            {messages.map((message, index) => (
              <ChatMessage key={index} message={message} onFlag={flagClassification} />
            ))}
            {isLoading && (
              <div className="loading-indicator">
                <span className="loading-dot"></span>
                <span className="loading-dot"></span>
                <span className="loading-dot"></span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="input-container">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="💬 Type your message here..."
              disabled={isLoading}
              className="chat-input"
            />
            <button type="submit" disabled={isLoading || !inputValue.trim()} className="send-button">
              Send
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default App;
