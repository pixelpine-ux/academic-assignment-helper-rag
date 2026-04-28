// API Service - Centralized backend communication

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Get authentication token from localStorage
 */
const getToken = () => {
  return localStorage.getItem('token');
};

/**
 * Save authentication token to localStorage
 */
const setToken = (token) => {
  localStorage.setItem('token', token);
};

/**
 * Remove authentication token from localStorage
 */
const removeToken = () => {
  localStorage.removeItem('token');
};

/**
 * Generic API request handler
 * Handles authentication, errors, and JSON parsing
 */
const apiRequest = async (endpoint, options = {}) => {
  const token = getToken();
  
  // Build headers
  const headers = {
    ...options.headers,
  };
  
  // Add auth token if available
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  // Add Content-Type for JSON requests (unless it's FormData)
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }
  
  try {
    const response = await fetch(`${API_URL}${endpoint}`, {
      ...options,
      headers,
    });
    
    // Handle non-JSON responses (like 204 No Content)
    const contentType = response.headers.get('content-type');
    const data = contentType && contentType.includes('application/json')
      ? await response.json()
      : null;
    
    // Handle errors
    if (!response.ok) {
      throw {
        status: response.status,
        message: data?.detail || data?.message || 'Something went wrong',
        data,
      };
    }
    
    return data;
  } catch (error) {
    // Network errors or thrown errors
    if (error.status) {
      throw error; // Already formatted
    }
    throw {
      status: 0,
      message: 'Network error. Please check your connection.',
      data: null,
    };
  }
};

// ============================================
// Authentication API
// ============================================

export const auth = {
  /**
   * Register a new user
   */
  register: async (email, password) => {
    const data = await apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    return data;
  },
  
  /**
   * Login user and store token
   */
  login: async (email, password) => {
    const data = await apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    // Store token
    if (data.access_token) {
      setToken(data.access_token);
    }
    
    return data;
  },
  
  /**
   * Logout user (clear token)
   */
  logout: () => {
    removeToken();
  },
  
  /**
   * Check if user is authenticated
   */
  isAuthenticated: () => {
    return !!getToken();
  },
};

// ============================================
// Documents API
// ============================================

export const documents = {
  /**
   * Get all documents for current user
   */
  list: async () => {
    return await apiRequest('/documents/');
  },
  
  /**
   * Upload a new document
   */
  upload: async (file, assignmentId = null) => {
    const formData = new FormData();
    formData.append('file', file);
    if (assignmentId) {
      formData.append('assignment_id', assignmentId);
    }
    
    return await apiRequest('/documents/upload', {
      method: 'POST',
      body: formData,
    });
  },
  
  /**
   * Get a specific document
   */
  get: async (documentId) => {
    return await apiRequest(`/documents/${documentId}`);
  },
  
  /**
   * Delete a document
   */
  delete: async (documentId) => {
    return await apiRequest(`/documents/${documentId}`, {
      method: 'DELETE',
    });
  },
};

// ============================================
// Query API (Q&A)
// ============================================

export const query = {
  /**
   * Ask a question about a document
   */
  ask: async (documentId, question) => {
    return await apiRequest('/query/ask', {
      method: 'POST',
      body: JSON.stringify({
        document_id: documentId,
        question,
      }),
    });
  },
};

// ============================================
// Health Check
// ============================================

export const health = {
  /**
   * Check if backend is running
   */
  check: async () => {
    return await apiRequest('/health');
  },
};

// Default export with all services
export default {
  auth,
  documents,
  query,
  health,
};
