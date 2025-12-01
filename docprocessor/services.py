import os
import tempfile
from .models import Document, ProcessedResult
from .utils import (
    extract_text_from_file, summarize_text, generate_answers, 
    analyze_text, translate_text
)

class DocumentService:
    @staticmethod
    def process_document(document, options=None):
        """
        Process a document based on its processing_type and options.
        Returns the created ProcessedResult object.
        """
        options = options or {}
        selected_model = options.get('model', 'gpt-3.5-turbo')
        
        # Create a temporary file from database content for text extraction
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=f".{document.document_type}", delete=False) as temp_file:
                temp_file.write(document.file_content)
                temp_file_path = temp_file.name
            
            # Extract text from the temporary file
            extracted_text = extract_text_from_file(temp_file_path, document.document_type)
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
        # Parse options
        target_words = options.get('target_words')
        max_tokens = options.get('max_tokens')
        preset_param = options.get('preset')
        
        # Process the text based on the selected processing type
        if document.processing_type == 'summarize':
            result_text = summarize_text(extracted_text, target_words=target_words, max_tokens=max_tokens, preset=preset_param, model=selected_model)
        elif document.processing_type == 'generate':
            result_text = generate_answers(extracted_text, target_words=target_words, max_tokens=max_tokens, preset=preset_param, model=selected_model)
        elif document.processing_type == 'analyze':
            result_text = analyze_text(extracted_text, target_words=target_words, max_tokens=max_tokens, preset=preset_param, model=selected_model)
        elif document.processing_type == 'translate':
            # Default to English translation if not specified, though usually handled by specific view
            result_text = translate_text(extracted_text, 'English', max_tokens=max_tokens, model=selected_model)
        else:
            result_text = "Unknown processing type"
        
        # Save the processed result
        processed_result = ProcessedResult.objects.create(
            document=document,
            result_text=result_text
        )
        
        return processed_result, extracted_text
