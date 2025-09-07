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
            # Build summarization prompt based on style
            if style == "bullet_points":
                prompt = f"Create a bullet-point summary of the following text in {max_length} words or less:\n\n{text}\n\nBullet-point summary:"
            elif style == "detailed":
                prompt = f"Create a detailed summary of the following text in {max_length} words or less, preserving key details and context:\n\n{text}\n\nDetailed summary:"
            else:  # concise
                prompt = f"Create a concise summary of the following text in {max_length} words or less:\n\n{text}\n\nConcise summary:"
                
            # Truncate text if too long
            max_input_length = 2000
            if len(text) > max_input_length:
                text = text[:max_input_length] + "..."
                prompt = prompt.replace(text, text[:max_input_length] + "...")
                
            summary = self.ai_engine.generate_response(prompt)
            
            # Clean up the response
            summary = self._clean_summary(summary)
            
            return summary
            
        except Exception as e:
            print(f"AI summarization failed: {e}")
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
        # Remove common AI response prefixes
        prefixes_to_remove = [
            "Here is a summary:",
            "Summary:",
            "The summary is:",
            "Here's a summary:",
            "Here is a concise summary:",
            "Concise summary:",
            "Detailed summary:",
            "Bullet-point summary:"
        ]
        
        for prefix in prefixes_to_remove:
            if summary.lower().startswith(prefix.lower()):
                summary = summary[len(prefix):].strip()
                
        # Remove leading/trailing whitespace and newlines
        summary = summary.strip()
        
        # Remove multiple consecutive newlines
        summary = re.sub(r'\n{3,}', '\n\n', summary)
        
        return summary
        
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
