import React, { useState, useRef, useEffect } from 'react';

// Type for a single message
export interface Message {
  id: string;
  sender: 'user' | 'agent';
  text: string;
}

// Props for the ChatUI component
interface ChatUIProps {
  messages: Message[];
  onSendMessage: (messageText: string) => void;
}

const ChatUI: React.FC<ChatUIProps> = ({ messages, onSendMessage }) => {
  const [inputText, setInputText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = () => {
    if (inputText.trim()) {
      onSendMessage(inputText.trim());
      setInputText('');
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Prevent newline in input if that's desired
      handleSend();
    }
  };

  return (
    <div className="chat-ui-container">
      <h2 className="chat-ui-title">Chat</h2>
      <div className="message-list">
        {messages.map(msg => (
          <div
            key={msg.id}
            // Apply 'message' class and conditional 'user' or 'agent' class
            className={`message ${msg.sender === 'user' ? 'user' : 'agent'}`}
          >
            <div className="message-sender">
              {msg.sender === 'user' ? 'You' : 'Agent'}
            </div>
            <div>{msg.text}</div> {/* Ensure this div is direct child for styling if needed */}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div className="message-input-area">
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          className="message-input"
          placeholder="Type your message..."
        />
        <button
          onClick={handleSend}
          className="send-button"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatUI;
