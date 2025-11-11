import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';
import ChatMessage from './components/ChatMessage.js';
import Sidebar from './components/Sidebar.js';
import './amplifyConfig.js';
import { generateClient } from 'aws-amplify/api';

const client = generateClient();

// Flask API URL - uses environment variable or defaults to localhost
const FLASK_API_URL = process.env.REACT_APP_FLASK_API_URL || 'http://localhost:5001';

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
    // Check if Amplify is configured (has real endpoint, not placeholder)
    const hasAmplify = process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT && 
                      !process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT.includes('your-amplify-endpoint');

    if (hasAmplify) {
      try {
        const result = await client.graphql({
          query: `
            query GetStats {
              stats(dummy: "stats") {
                totalPrompts
                safeCount
                misuseCount
                flaggedCount
              }
            }
          `
        });
        
        const statsData = result.data.stats;
        setStats({
          total_prompts: statsData.totalPrompts,
          safe_count: statsData.safeCount,
          misuse_count: statsData.misuseCount,
          flagged_count: statsData.flaggedCount
        });
        return;
      } catch (error) {
        console.error('Error fetching stats from Amplify:', error);
        // Fall through to Flask
      }
    }

    // Use Flask API
    try {
      const response = await axios.get(`${FLASK_API_URL}/api/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Error fetching stats from Flask:', error);
    }
  };

  const flagClassification = async (classificationId) => {
    // Check if Amplify is configured
    const hasAmplify = process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT && 
                      !process.env.REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT.includes('your-amplify-endpoint');

    if (hasAmplify) {
      try {
        await client.graphql({
          query: `
            mutation UpdateTrainingData($input: UpdateTrainingDataInput!) {
              updateTrainingData(input: $input) {
                id
                userFlaggedIncorrect
              }
            }
          `,
          variables: {
            input: {
              id: classificationId,
              userFlaggedIncorrect: true
            }
          }
        });
        
        alert('Classification flagged as incorrect. Thank you for your feedback!');
        fetchStats();
        return;
      } catch (error) {
        console.error('Error flagging in Amplify:', error);
        // Fall through to Flask
      }
    }

    // Use Flask API
    try {
      await axios.post(`${FLASK_API_URL}/api/flag`, { id: classificationId });
      alert('Classification flagged as incorrect. Thank you for your feedback!');
      fetchStats();
    } catch (error) {
      console.error('Error flagging in Flask:', error);
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
      const response = await axios.post(`${FLASK_API_URL}/api/classify`, {
        prompt: inputValue
      });

      const { id, predicted_class, confidence, processing_time } = response.data;

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
          <h1>Neo-Guardrails</h1>
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
