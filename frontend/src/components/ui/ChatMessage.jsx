import { motion } from 'framer-motion';
import { User, Bot, Copy, ThumbsUp, ThumbsDown } from 'lucide-react';
import './ChatMessage.css';

export default function ChatMessage({ message, onCopy, onFeedback }) {
  const isUser = message.role === 'user';

  return (
    <motion.div
      className={`chat-message ${isUser ? 'chat-message-user' : 'chat-message-ai'}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
    >
      <div className="chat-message-avatar">
        {isUser ? <User size={20} /> : <Bot size={20} />}
      </div>
      <div className="chat-message-content">
        <div className="chat-message-text">{message.content}</div>
        {message.sources && message.sources.length > 0 && (
          <div className="chat-message-sources">
            Sources: Document IDs {message.sources.join(', ')} ({message.chunks_used} chunks)
          </div>
        )}
        {!isUser && (
          <div className="chat-message-actions">
            <button className="chat-action-btn" onClick={() => onCopy?.(message.content)} title="Copy">
              <Copy size={16} />
            </button>
            <button className="chat-action-btn" onClick={() => onFeedback?.('up')} title="Good response">
              <ThumbsUp size={16} />
            </button>
            <button className="chat-action-btn" onClick={() => onFeedback?.('down')} title="Bad response">
              <ThumbsDown size={16} />
            </button>
          </div>
        )}
      </div>
    </motion.div>
  );
}
