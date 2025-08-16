const API_BASE_URL = 'http://localhost:8000';

export const fetchDocuments = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/documents`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.documents;
  } catch (error) {
    console.error('Error fetching documents:', error);
    throw error;
  }
};

export const fetchDocumentDetails = async (documentId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/document-status/${documentId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error fetching document details for ${documentId}:`, error);
    throw error;
  }
};

export const uploadDocument = async (file) => {
  try {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', file.name.split('.')[0]); // Use filename without extension as title
    
    const response = await fetch(`${API_BASE_URL}/upload-document`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.document_id;
  } catch (error) {
    console.error('Error uploading document:', error);
    throw error;
  }
};

export const deleteDocument = async (documentId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/document/${documentId}`, {
      method: 'DELETE',
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`Error deleting document ${documentId}:`, error);
    throw error;
  }
};

export const getDocumentTopics = async (documentId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/topics/${documentId}`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.topics;
  } catch (error) {
    console.error(`Error fetching topics for document ${documentId}:`, error);
    throw error;
  }
};

export const summarizeDocument = async (documentId, section = null) => {
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
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.summary;
  } catch (error) {
    console.error(`Error summarizing document ${documentId}:`, error);
    throw error;
  }
};

export const sendChatMessage = async (documentId, query, history = []) => {
  try {
    const formData = new FormData();
    formData.append('doc_id', documentId);
    formData.append('query', query);
    
    if (history.length > 0) {
      formData.append('history', JSON.stringify(history));
    }
    
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.response;
  } catch (error) {
    console.error(`Error sending chat message for document ${documentId}:`, error);
    throw error;
  }
};
