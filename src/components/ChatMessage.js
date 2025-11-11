import React from 'react';
import ReactMarkdown from 'react-markdown';

function ChatMessage({ message, onFlag }) {
  const avatar = message.role === 'user' ? '👤' : '🛡️';
  
  const handleFlag = () => {
    if (message.classificationId && onFlag) {
      onFlag(message.classificationId);
    }
  };
  
  return (
    <div className={`chat-message ${message.role}`}>
      <div className="message-avatar">{avatar}</div>
      <div className="message-content">
        <ReactMarkdown>{message.content}</ReactMarkdown>
        {message.role === 'assistant' && message.classificationId && (
          <div className="flag-container">
            <button onClick={handleFlag} className="flag-button" title="Flag this classification as incorrect">
              🚩 Flag as Incorrect
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default ChatMessage;
