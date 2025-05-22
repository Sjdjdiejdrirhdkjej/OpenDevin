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
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', border: '1px solid #ccc', borderRadius: '8px', padding: '10px', backgroundColor: '#f9f9f9' }}>
      <h2 style={{ textAlign: 'center', marginTop: 0, marginBottom: '10px', color: '#333' }}>Chat</h2>
      <div style={{ flexGrow: 1, overflowY: 'auto', marginBottom: '10px', padding: '5px' }}>
        {messages.map(msg => (
          <div 
            key={msg.id} 
            style={{ 
              marginBottom: '10px', 
              padding: '8px 12px', 
              borderRadius: '15px',
              maxWidth: '70%',
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              backgroundColor: msg.sender === 'user' ? '#007bff' : '#e9ecef',
              color: msg.sender === 'user' ? 'white' : 'black',
              marginLeft: msg.sender === 'user' ? 'auto' : '0',
              marginRight: msg.sender === 'agent' ? 'auto' : '0',
            }}
          >
            <div style={{ fontWeight: 'bold', marginBottom: '3px', fontSize: '0.8em' }}>
              {msg.sender === 'user' ? 'You' : 'Agent'}
            </div>
            <div>{msg.text}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <div style={{ display: 'flex' }}>
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={handleKeyPress}
          style={{ flexGrow: 1, padding: '10px', borderRadius: '20px', border: '1px solid #ddd', marginRight: '10px' }}
          placeholder="Type your message..."
        />
        <button 
          onClick={handleSend}
          style={{ padding: '10px 20px', borderRadius: '20px', border: 'none', backgroundColor: '#007bff', color: 'white', cursor: 'pointer' }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatUI;
