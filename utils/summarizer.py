"""
Summarizer utility for creating summaries from text content
"""

from typing import Optional
import re

class Summarizer:
    def __init__(self, ai_engine):
        self.ai_engine = ai_engine
        
    def summarize(self, text: str, max_length: int = 300, style: str = "concise") -> str:
        """
        Generate summary of given text
        
        Args:
            text: Text to summarize
            max_length: Maximum length of summary
            style: Summary style ('concise', 'detailed', 'bullet_points')
        """
        if not text or not text.strip():
            return "No content to summarize."
            
        # Clean and prepare text
        cleaned_text = self._clean_text(text)
        
        # If AI engine is available, use it for summarization
        if self.ai_engine and self.ai_engine.is_ready():
            return self._ai_summarize(cleaned_text, max_length, style)
        else:
            # Fallback to extractive summary
            return self._extractive_summarize(cleaned_text, max_length)
            
    def _ai_summarize(self, text: str, max_length: int, style: str) -> str:
        """Use AI to generate summary"""
        try:
            print(f"Starting AI summarization, text length: {len(text)}")
            
            # Truncate text if too long for better processing
            max_input_length = 1500  # Reduced for better reliability
            truncated_text = text
            if len(text) > max_input_length:
                truncated_text = text[:max_input_length] + "..."
                print(f"Text truncated to {len(truncated_text)} characters")
                
            # Build simplified summarization prompt
            if style == "bullet_points":
                prompt = f"Please summarize the following text as bullet points:\n\n{truncated_text}\n\nSummary as bullet points:"
            elif style == "detailed":
                prompt = f"Please provide a detailed summary of the following text:\n\n{truncated_text}\n\nDetailed summary:"
            else:  # concise
                prompt = f"Please provide a brief summary of the following text:\n\n{truncated_text}\n\nSummary:"
            
            print(f"Sending prompt to AI engine, prompt length: {len(prompt)}")
            
            # Check AI engine status
            if not self.ai_engine or not self.ai_engine.is_ready():
                raise Exception("AI engine is not ready or not available")
                
            summary = self.ai_engine.generate_response(prompt)
            print(f"AI response received, length: {len(summary) if summary else 0}")
            
            if not summary or summary.strip() == "":
                raise Exception("AI returned empty response")
                
            # Clean up the response
            summary = self._clean_summary(summary)
            
            # Ensure summary isn't too long
            if len(summary) > max_length * 2:  # Allow some flexibility
                summary = summary[:max_length * 2].rsplit('.', 1)[0] + "."
                
            print(f"AI summarization completed successfully, final length: {len(summary)}")
            return summary
            
        except Exception as e:
            print(f"AI summarization failed: {e}")
            print("Falling back to extractive summarization")
            return self._extractive_summarize(text, max_length)
            
    def _extractive_summarize(self, text: str, max_length: int) -> str:
        """Generate extractive summary (fallback method)"""
        try:
            # Split into sentences
            sentences = self._split_sentences(text)
            
            if len(sentences) <= 3:
                return text[:max_length] + ("..." if len(text) > max_length else "")
                
            # Score sentences based on various factors
            sentence_scores = self._score_sentences(sentences)
            
            # Select top sentences
            num_sentences = min(max(3, len(sentences) // 4), 5)
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
            
            # Sort selected sentences by original order
            selected_sentences = []
            for sentence, score in top_sentences:
                sentence_index = sentences.index(sentence)
                selected_sentences.append((sentence_index, sentence))
                
            selected_sentences.sort(key=lambda x: x[0])
            
            # Create summary
            summary = " ".join([sentence for _, sentence in selected_sentences])
            
            # Truncate if too long
            if len(summary) > max_length:
                summary = summary[:max_length].rsplit(' ', 1)[0] + "..."
                
            return summary
            
        except Exception as e:
            print(f"Extractive summarization failed: {e}")
            # Ultimate fallback: just truncate
            return text[:max_length] + ("..." if len(text) > max_length else "")
            
    def _clean_text(self, text: str) -> str:
        """Clean input text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page markers
        text = re.sub(r'--- Page \d+ ---', '', text)
        
        # Remove very short lines (likely headers/footers)
        lines = text.split('\n')
        cleaned_lines = [line.strip() for line in lines if len(line.strip()) > 10]
        
        return '\n'.join(cleaned_lines)
        
    def _split_sentences(self, text: str) -> list:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        
        # Clean and filter sentences
        clean_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20:  # Filter out very short sentences
                clean_sentences.append(sentence)
                
        return clean_sentences
        
    def _score_sentences(self, sentences: list) -> dict:
        """Score sentences for importance"""
        sentence_scores = {}
        
        # Get word frequency
        word_freq = self._get_word_frequency(sentences)
        
        for sentence in sentences:
            words = sentence.lower().split()
            score = 0
            
            # Score based on word frequency
            for word in words:
                if word in word_freq:
                    score += word_freq[word]
                    
            # Bonus for sentence length (not too short, not too long)
            word_count = len(words)
            if 10 <= word_count <= 25:
                score *= 1.2
            elif word_count > 30:
                score *= 0.8
                
            # Bonus for sentences with numbers (often important facts)
            if any(char.isdigit() for char in sentence):
                score *= 1.1
                
            # Bonus for sentences with keywords
            keywords = ['important', 'significant', 'key', 'main', 'primary', 'conclusion', 'result']
            if any(keyword in sentence.lower() for keyword in keywords):
                score *= 1.3
                
            sentence_scores[sentence] = score
            
        return sentence_scores
        
    def _get_word_frequency(self, sentences: list) -> dict:
        """Get word frequency for scoring"""
        word_freq = {}
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                # Clean word
                word = re.sub(r'[^\w]', '', word)
                if len(word) > 2 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
                    
        return word_freq
        
    def _clean_summary(self, summary: str) -> str:
        """Clean AI-generated summary"""
        if not summary or not isinstance(summary, str):
            return "Unable to generate summary."
            
        # Remove common AI response prefixes/patterns
        prefixes_to_remove = [
            "Here is a summary:",
            "Summary:",
            "The summary is:",
            "Here's a summary:",
            "Here is a concise summary:",
            "Concise summary:",
            "Detailed summary:",
            "Bullet-point summary:",
            "Brief summary:",
            "Please provide",
            "I'll provide",
            "Based on the text",
            "The text discusses"
        ]
        
        # Clean the summary
        cleaned = summary.strip()
        
        # Remove prefixes
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
                
        # Remove common suffixes that might indicate incomplete responses
        suffixes_to_remove = [
            "Error generating response:",
            "Error with llama-cpp generation:",
            "AI engine not ready",
        ]
        
        for suffix in suffixes_to_remove:
            if suffix.lower() in cleaned.lower():
                # If error message is found, return empty to trigger fallback
                return ""
                
        # Remove leading/trailing whitespace and newlines
        cleaned = cleaned.strip()
        
        # Remove multiple consecutive newlines
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)
        
        # Remove leading dashes or bullet points if it's not a bullet summary
        cleaned = re.sub(r'^[-•*]\s*', '', cleaned)
        
        # Ensure the summary ends properly (with punctuation)
        if cleaned and not cleaned.endswith(('.', '!', '?', ':')):
            cleaned += '.'
            
        # If summary is too short, it might be incomplete
        if len(cleaned.strip()) < 10:
            return ""
            
        return cleaned
        
    def create_notes(self, text: str, note_style: str = "structured") -> str:
        """
        Create structured notes from text
        
        Args:
            text: Input text
            note_style: Style of notes ('structured', 'outline', 'qa')
        """
        if not text or not text.strip():
            return "No content to create notes from."
            
        if self.ai_engine and self.ai_engine.is_ready():
            return self._ai_create_notes(text, note_style)
        else:
            return self._basic_create_notes(text)
            
    def _ai_create_notes(self, text: str, note_style: str) -> str:
        """Use AI to create structured notes"""
        try:
            if note_style == "outline":
                prompt = f"Create a detailed outline with main points and subpoints from the following text:\n\n{text}\n\nOutline:"
            elif note_style == "qa":
                prompt = f"Create a Q&A format summary with important questions and answers from the following text:\n\n{text}\n\nQ&A Summary:"
            else:  # structured
                prompt = f"Create structured notes with key points, important details, and main concepts from the following text:\n\n{text}\n\nStructured Notes:"
                
            notes = self.ai_engine.generate_response(prompt)
            return self._clean_summary(notes)
            
        except Exception as e:
            print(f"AI note creation failed: {e}")
            return self._basic_create_notes(text)
            
    def _basic_create_notes(self, text: str) -> str:
        """Create basic notes (fallback)"""
        # Simple extraction of key sentences
        sentences = self._split_sentences(text)
        sentence_scores = self._score_sentences(sentences)
        
        # Get top sentences
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:8]
        
        notes = "Key Points:\n\n"
        for i, (sentence, _) in enumerate(top_sentences, 1):
            notes += f"{i}. {sentence.strip()}\n\n"
            
        return notes
