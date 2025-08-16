const API_BASE_URL = 'http://localhost:8000';

// Generate flashcards from a document
export const generateFlashcards = async (documentId, count = 10) => {
  try {
    const formData = new FormData();
    formData.append('doc_id', documentId);
    formData.append('query', `Generate ${count} flashcards in JSON format with 'question' and 'answer' fields based on this document`);

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    try {
      // Try to parse the LLM response to extract the JSON
      const textResponse = data.response;
      const jsonMatch = textResponse.match(/```json\n([\s\S]*?)\n```/) || 
                        textResponse.match(/```\n([\s\S]*?)\n```/) ||
                        textResponse.match(/\[([\s\S]*?)\]/);
      
      if (jsonMatch && jsonMatch[1]) {
        const flashcards = JSON.parse(jsonMatch[1].startsWith('[') ? jsonMatch[1] : '[' + jsonMatch[1] + ']');
        return flashcards;
      } else {
        // Fallback if no JSON was found in the response
        throw new Error('Could not parse flashcards from response');
      }
    } catch (parseError) {
      console.error('Error parsing flashcards:', parseError);
      // Return the raw response as a fallback
      return {
        rawResponse: data.response,
        error: 'Failed to parse structured flashcards'
      };
    }
  } catch (error) {
    console.error('Error generating flashcards:', error);
    throw error;
  }
};

// Generate a quiz from a document
export const generateQuiz = async (documentId, questionCount = 5) => {
  try {
    const formData = new FormData();
    formData.append('doc_id', documentId);
    formData.append('query', `Generate a ${questionCount}-question multiple-choice quiz in JSON format with 'question', 'options' (array), and 'correctAnswer' (index of correct option) fields based on this document`);

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    try {
      // Try to parse the LLM response to extract the JSON
      const textResponse = data.response;
      const jsonMatch = textResponse.match(/```json\n([\s\S]*?)\n```/) || 
                        textResponse.match(/```\n([\s\S]*?)\n```/) ||
                        textResponse.match(/\[([\s\S]*?)\]/);
      
      if (jsonMatch && jsonMatch[1]) {
        const quiz = JSON.parse(jsonMatch[1].startsWith('[') ? jsonMatch[1] : '[' + jsonMatch[1] + ']');
        return quiz;
      } else {
        // Fallback if no JSON was found in the response
        throw new Error('Could not parse quiz from response');
      }
    } catch (parseError) {
      console.error('Error parsing quiz:', parseError);
      // Return the raw response as a fallback
      return {
        rawResponse: data.response,
        error: 'Failed to parse structured quiz'
      };
    }
  } catch (error) {
    console.error('Error generating quiz:', error);
    throw error;
  }
};

// Generate a mind map or concept map for studying
export const generateConceptMap = async (documentId) => {
  try {
    const formData = new FormData();
    formData.append('doc_id', documentId);
    formData.append('query', 'Generate a concept map in JSON format with nodes and links that represents the main concepts and their relationships in this document');

    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error generating concept map:', error);
    throw error;
  }
};

// Save study notes for a document
export const saveStudyNotes = (documentId, notes) => {
  try {
    // Get existing notes
    const allNotes = getStudyNotes();
    allNotes[documentId] = notes;
    localStorage.setItem('studyNotes', JSON.stringify(allNotes));
    return true;
  } catch (error) {
    console.error('Error saving study notes:', error);
    return false;
  }
};

// Get study notes for a document
export const getStudyNotes = (documentId = null) => {
  try {
    const notes = localStorage.getItem('studyNotes');
    const allNotes = notes ? JSON.parse(notes) : {};
    return documentId ? (allNotes[documentId] || '') : allNotes;
  } catch (error) {
    console.error('Error retrieving study notes:', error);
    return documentId ? '' : {};
  }
};
