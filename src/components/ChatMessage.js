import React from 'react';
import ReactMarkdown from 'react-markdown';

function ChatMessage({ message }) {
  const avatar = message.role === 'user' ? '👤' : '🛡️';
  
  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-avatar">{avatar}</div>
      <div className="message-content">
        <ReactMarkdown>{message.content}</ReactMarkdown>
      </div>
    </div>
  );
}

export default ChatMessage;
