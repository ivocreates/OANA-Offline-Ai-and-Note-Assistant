"""
PDF Parser utility for extracting text from PDF documents
"""

import os
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("PyMuPDF not available. PDF parsing will be limited.")

class PDFParser:
    def __init__(self):
        self.available = PYMUPDF_AVAILABLE
        
    def is_available(self):
        """Check if PDF parsing is available"""
        return self.available
        
    def extract_text(self, filepath):
        """Extract text from PDF file"""
        if not self.available:
            raise Exception("PyMuPDF not installed. Install with: pip install PyMuPDF")
            
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"PDF file not found: {filepath}")
            
        try:
            text_content = ""
            
            # Open PDF document
            pdf_document = fitz.open(filepath)
            
            # Extract text from each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text_content += page.get_text()
                text_content += f"\n--- Page {page_num + 1} ---\n"
                
            pdf_document.close()
            
            # Clean up text
            text_content = self._clean_text(text_content)
            
            return text_content
            
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
            
    def extract_metadata(self, filepath):
        """Extract metadata from PDF file"""
        if not self.available:
            return {}
            
        try:
            pdf_document = fitz.open(filepath)
            metadata = pdf_document.metadata
            pdf_document.close()
            
            return {
                'title': metadata.get('title', ''),
                'author': metadata.get('author', ''),
                'subject': metadata.get('subject', ''),
                'creator': metadata.get('creator', ''),
                'producer': metadata.get('producer', ''),
                'creation_date': metadata.get('creationDate', ''),
                'modification_date': metadata.get('modDate', ''),
                'pages': pdf_document.page_count if hasattr(pdf_document, 'page_count') else 0
            }
            
        except Exception as e:
            print(f"Failed to extract PDF metadata: {e}")
            return {}
            
    def _clean_text(self, text):
        """Clean extracted text"""
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                cleaned_lines.append(line)
                
        # Join lines with proper spacing
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive newlines
        while '\n\n\n' in cleaned_text:
            cleaned_text = cleaned_text.replace('\n\n\n', '\n\n')
            
        return cleaned_text
        
    def get_page_count(self, filepath):
        """Get number of pages in PDF"""
        if not self.available:
            return 0
            
        try:
            pdf_document = fitz.open(filepath)
            page_count = pdf_document.page_count
            pdf_document.close()
            return page_count
        except:
            return 0
