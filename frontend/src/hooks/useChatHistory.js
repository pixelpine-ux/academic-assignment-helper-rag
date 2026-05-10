import { useState, useEffect, useCallback } from 'react';

const STORAGE_KEY = 'chat_history';
const MAX_HISTORY_ITEMS = 50;

export function useChatHistory() {
  const [history, setHistory] = useState([]);

  // Load history from localStorage on mount
  useEffect(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        setHistory(parsed);
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  }, []);

  // Save history to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    } catch (error) {
      console.error('Failed to save chat history:', error);
    }
  }, [history]);

  // Create a new chat session
  const createChat = useCallback((title = 'New Chat') => {
    const newChat = {
      id: Date.now().toString(),
      title,
      messages: [],
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    setHistory(prev => {
      const updated = [newChat, ...prev];
      // Limit history size
      return updated.slice(0, MAX_HISTORY_ITEMS);
    });

    return newChat;
  }, []);

  // Update an existing chat
  const updateChat = useCallback((chatId, updates) => {
    setHistory(prev => 
      prev.map(chat => 
        chat.id === chatId 
          ? { 
              ...chat, 
              ...updates, 
              updatedAt: new Date().toISOString() 
            }
          : chat
      )
    );
  }, []);

  // Add a message to a chat
  const addMessage = useCallback((chatId, message) => {
    setHistory(prev => 
      prev.map(chat => {
        if (chat.id === chatId) {
          const updatedMessages = [...chat.messages, message];
          // Auto-generate title from first user message
          const title = chat.title === 'New Chat' && message.role === 'user'
            ? message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '')
            : chat.title;
          
          return {
            ...chat,
            messages: updatedMessages,
            title,
            updatedAt: new Date().toISOString(),
          };
        }
        return chat;
      })
    );
  }, []);

  // Delete a chat
  const deleteChat = useCallback((chatId) => {
    setHistory(prev => prev.filter(chat => chat.id !== chatId));
  }, []);

  // Clear all history
  const clearHistory = useCallback(() => {
    if (confirm('Are you sure you want to clear all chat history? This cannot be undone.')) {
      setHistory([]);
      localStorage.removeItem(STORAGE_KEY);
      return true;
    }
    return false;
  }, []);

  // Get a specific chat
  const getChat = useCallback((chatId) => {
    return history.find(chat => chat.id === chatId);
  }, [history]);

  return {
    history,
    createChat,
    updateChat,
    addMessage,
    deleteChat,
    clearHistory,
    getChat,
  };
}
