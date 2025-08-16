const API_BASE_URL = 'http://localhost:8000';

export const fetchAvailableModels = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/models`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    return data.models;
  } catch (error) {
    console.error('Error fetching available models:', error);
    throw error;
  }
};

export const changeModel = async (modelFile) => {
  try {
    const formData = new FormData();
    formData.append('model_file', modelFile);
    
    const response = await fetch(`${API_BASE_URL}/change-model`, {
      method: 'POST',
      body: formData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Error changing model:', error);
    throw error;
  }
};
