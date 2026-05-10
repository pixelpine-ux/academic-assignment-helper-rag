import { Bot } from 'lucide-react';
import './TypingIndicator.css';

export default function TypingIndicator() {
  return (
    <div className="typing-indicator">
      <div className="typing-indicator-avatar">
        <Bot size={20} />
      </div>
      <div className="typing-indicator-content">
        <div className="typing-indicator-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </div>
  );
}
