const API_BASE_URL = 'http://localhost:8000';

// Retrieve conversation history from localStorage
export const getConversationHistory = () => {
  try {
    const history = localStorage.getItem('chatHistory');
    return history ? JSON.parse(history) : {};
  } catch (error) {
    console.error('Error retrieving chat history:', error);
    return {};
  }
};

// Save conversation history to localStorage
export const saveConversationHistory = (documentId, history) => {
  try {
    const allHistory = getConversationHistory();
    allHistory[documentId] = history;
    localStorage.setItem('chatHistory', JSON.stringify(allHistory));
    return true;
  } catch (error) {
    console.error('Error saving chat history:', error);
    return false;
  }
};

// Get conversation history for a specific document
export const getDocumentConversation = (documentId) => {
  const allHistory = getConversationHistory();
  return allHistory[documentId] || [];
};

// Send a chat message to the backend
export const sendChatMessage = async (query, documentId, history = []) => {
  try {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('doc_id', documentId);
    
    if (history && history.length > 0) {
      formData.append('history', JSON.stringify(history));
    }

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    
    // Update conversation history
    const newMessage = { role: 'user', content: query };
    const newResponse = { role: 'assistant', content: data.response };
    const updatedHistory = [...history, newMessage, newResponse];
    
    // Save to localStorage
    saveConversationHistory(documentId, updatedHistory);
    
    return {
      response: data.response,
      history: updatedHistory
    };
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

// Send a chat message and save the conversation on the server
export const sendChatMessageWithConversation = async (query, documentId, conversationId = null, conversationTitle = null) => {
  try {
    const formData = new FormData();
    formData.append('query', query);
    formData.append('doc_id', documentId);
    
    if (conversationId) {
      formData.append('conversation_id', conversationId);
    }
    
    if (conversationTitle) {
      formData.append('conversation_title', conversationTitle);
    }

    const response = await fetch(`${API_BASE_URL}/chat-conversation`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message with conversation:', error);
    throw error;
  }
};

// Get all conversations from the server
export const fetchServerConversations = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversations`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error fetching conversations from server:', error);
    throw error;
  }
};

// Get a specific conversation from the server
export const fetchConversationById = async (conversationId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversation/${conversationId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching conversation ${conversationId}:`, error);
    throw error;
  }
};

// Delete a conversation from the server
export const deleteConversation = async (conversationId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/conversation/${conversationId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error deleting conversation ${conversationId}:`, error);
    throw error;
  }
};

// Get document summary
export const getDocumentSummary = async (documentId, section = null) => {
  try {
    const formData = new FormData();
    formData.append('doc_id', documentId);
    
    if (section) {
      formData.append('section', section);
    }

    const response = await fetch(`${API_BASE_URL}/summarize`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting document summary:', error);
    throw error;
  }
};

// Get study tips based on a document
export const getStudyTips = async (documentId, subject) => {
  try {
    const formData = new FormData();
    formData.append('doc_id', documentId);
    formData.append('query', `Generate study tips for this ${subject} material`);

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error getting study tips:', error);
    throw error;
  }
};
