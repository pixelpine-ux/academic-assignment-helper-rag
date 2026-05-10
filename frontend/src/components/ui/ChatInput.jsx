import { useState, useRef, useEffect } from 'react';
import { Send, Paperclip } from 'lucide-react';
import './ChatInput.css';

export default function ChatInput({ onSend, disabled, onFileAttach }) {
  const [value, setValue] = useState('');
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '56px';
      const scrollHeight = textareaRef.current.scrollHeight;
      textareaRef.current.style.height = Math.min(scrollHeight, 200) + 'px';
    }
  }, [value]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (value.trim() && !disabled) {
      onSend(value);
      setValue('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="chat-input-wrapper">
      <div className="chat-input-disclaimer">
        <span className="chat-input-disclaimer-icon">⚠️</span>
        AI can make mistakes. Always verify important information and cross-check your answers before submission.
      </div>
      <form onSubmit={handleSubmit} className="chat-input-form">
        <button 
          type="button" 
          className="chat-input-attach"
          onClick={onFileAttach}
          title="Attach file"
        >
          <Paperclip size={20} />
        </button>
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask anything about your assignments..."
          disabled={disabled}
          className="chat-input-textarea"
          rows={1}
        />
        <button
          type="submit"
          disabled={disabled || !value.trim()}
          className="chat-input-send"
          title="Send message"
        >
          <Send size={20} />
        </button>
      </form>
    </div>
  );
}
