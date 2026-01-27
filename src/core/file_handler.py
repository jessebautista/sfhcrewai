"""
File handler for uploading and processing attachments.
Handles images and PDFs with Supabase Storage backend.
"""
import os
import uuid
from io import BytesIO
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()


class FileWrapper:
    """Wrapper to make bytes/attachments compatible with FileHandler interface."""
    
    def __init__(self, filename: str, data: bytes, content_type: str):
        self.name = filename
        self._data = data
        self.type = content_type
        self.size = len(data)
    
    def read(self):
        """Return file data (mimics UploadedFile.read())."""
        return self._data


class FileAdapter:
    """Adapt various file sources to FileHandler interface."""
    
    @staticmethod
    def from_slack_file(filename: str, data: bytes, content_type: str):
        """Create from Slack downloaded file."""
        return FileWrapper(filename, data, content_type)
    
    @staticmethod
    def from_email_attachment(filename: str, data: bytes, content_type: str):
        """Create from email attachment."""
        return FileWrapper(filename, data, content_type)
    
    @staticmethod
    def from_bytes(filename: str, data: bytes, content_type: str = "application/octet-stream"):
        """Generic byte conversion."""
        return FileWrapper(filename, data, content_type)


class FileHandler:
    """Handle file uploads, validation, and processing."""
    
    # File size limit in bytes (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    # Allowed file types
    ALLOWED_IMAGE_TYPES = ['.jpg', '.jpeg', '.png', '.webp']
    ALLOWED_DOC_TYPES = ['.pdf']
    ALLOWED_DATA_TYPES = ['.csv']
    ALLOWED_TYPES = ALLOWED_IMAGE_TYPES + ALLOWED_DOC_TYPES + ALLOWED_DATA_TYPES
    
    def __init__(self):
        from supabase import create_client
        
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        self.client = create_client(url, key)
        self.bucket_name = "attachments"
    
    def validate_file(self, file, max_size_mb: int = 10) -> tuple[bool, str]:
        """
        Validate file type and size.
        
        Args:
            file: Streamlit UploadedFile object
            max_size_mb: Maximum file size in MB
        
        Returns:
            (is_valid, error_message)
        """
        # Check file extension
        file_ext = os.path.splitext(file.name)[1].lower()
        if file_ext not in self.ALLOWED_TYPES:
            return False, f"File type {file_ext} not allowed. Allowed: {', '.join(self.ALLOWED_TYPES)}"
        
        # Check file size
        file_size = file.size
        max_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_bytes:
            size_mb = file_size / (1024 * 1024)
            return False, f"File too large ({size_mb:.2f}MB). Max size: {max_size_mb}MB"
        
        return True, ""
    
    def upload_to_supabase(self, file_data: bytes, filename: str, content_type: str = "application/octet-stream") -> Optional[str]:
        """
        Upload file to Supabase Storage.
        
        Args:
            file_data: File bytes
            filename: Original filename
            content_type: MIME type
        
        Returns:
            Public URL of uploaded file, or None if failed
        """
        try:
            # Generate unique filename to avoid collisions
            file_ext = os.path.splitext(filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_ext}"
            
            # Upload to Supabase
            response = self.client.storage.from_(self.bucket_name).upload(
                path=unique_filename,
                file=file_data,
                file_options={"content-type": content_type}
            )
            
            # Get public URL
            public_url = self.client.storage.from_(self.bucket_name).get_public_url(unique_filename)
            
            print(f"✅ Uploaded {filename} → {unique_filename}")
            return public_url
            
        except Exception as e:
            print(f"❌ Upload failed for {filename}: {e}")
            return None
    
    def extract_pdf_text(self, pdf_bytes: bytes, max_pages: int = 10) -> str:
        """
        Extract text from PDF file.
        
        Args:
            pdf_bytes: PDF file bytes
            max_pages: Maximum pages to process
        
        Returns:
            Extracted text
        """
        try:
            import pdfplumber
            
            text_content = []
            
            with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
                # Limit pages to avoid processing huge PDFs
                pages_to_process = min(len(pdf.pages), max_pages)
                
                for i in range(pages_to_process):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text:
                        text_content.append(text)
            
            full_text = "\n\n".join(text_content)
            print(f"✅ Extracted {len(full_text)} characters from PDF")
            
            return full_text
            
        except Exception as e:
            print(f"❌ PDF extraction failed: {e}")
            return ""
    
    def extract_csv_data(self, csv_bytes: bytes, max_rows: int = 100) -> str:
        """
        Extract and format data from CSV file.
        
        Args:
            csv_bytes: CSV file bytes
            max_rows: Maximum rows to process
        
        Returns:
            Formatted CSV data as string
        """
        try:
            import csv
            from io import StringIO
            
            # Decode bytes to string
            csv_text = csv_bytes.decode('utf-8')
            csv_reader = csv.reader(StringIO(csv_text))
            
            # Read rows
            rows = []
            for i, row in enumerate(csv_reader):
                if i >= max_rows:
                    break
                rows.append(row)
            
            if not rows:
                return ""
            
            # Format as markdown table
            output = "\n**CSV Data:**\n\n"
            
            # Header
            if rows:
                output += "| " + " | ".join(rows[0]) + " |\n"
                output += "| " + " | ".join(["---"] * len(rows[0])) + " |\n"
            
            # Data rows (limit to 20 for readability)
            display_rows = min(len(rows) - 1, 20)
            for row in rows[1:display_rows + 1]:
                output += "| " + " | ".join(str(cell) for cell in row) + " |\n"
            
            if len(rows) > display_rows + 1:
                output += f"\n... and {len(rows) - display_rows - 1} more rows\n"
            
            output += f"\nTotal rows: {len(rows) - 1}\n"
            
            print(f"✅ Extracted {len(rows) - 1} rows from CSV")
            return output
            
        except Exception as e:
            print(f"❌ CSV extraction failed: {e}")
            return ""
    
    def optimize_image(self, image_bytes: bytes, max_width: int = 1920) -> bytes:
        """
        Optimize image (resize if too large, compress).
        
        Args:
            image_bytes: Image file bytes
            max_width: Maximum width in pixels
        
        Returns:
            Optimized image bytes
        """
        try:
            from PIL import Image
            
            # Open image
            img = Image.open(BytesIO(image_bytes))
            
            # Resize if too large
            if img.width > max_width:
                ratio = max_width / img.width
                new_height = int(img.height * ratio)
                img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                print(f"✅ Resized image to {max_width}x{new_height}")
            
            # Convert to RGB if needed (for JPEG)
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            # Save optimized
            output = BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            return output.read()
            
        except Exception as e:
            print(f"⚠️ Image optimization failed, using original: {e}")
            return image_bytes
    
    def process_attachments(self, uploaded_files: List, progress_callback=None) -> Dict:
        """
        Process multiple uploaded files in parallel.
        
        Args:
            uploaded_files: List of Streamlit UploadedFile objects
            progress_callback: Optional function(current, total, message) for progress updates
        
        Returns:
            {
                'images': [list of image URLs],
                'pdf_text': 'extracted text from PDFs',
                'errors': [list of error messages]
            }
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        result = {
            'images': [],
            'pdf_text': '',
            'errors': []
        }
        
        # Limit to 3 files
        files_to_process = uploaded_files[:3]
        total_files = len(files_to_process)
        
        if progress_callback:
            progress_callback(0, total_files, "Starting file processing...")
        
        # Process files in parallel
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all files for processing
            future_to_file = {
                executor.submit(self._process_single_file, file): file 
                for file in files_to_process
            }
            
            # Collect results as they complete
            completed = 0
            for future in as_completed(future_to_file):
                file = future_to_file[future]
                completed += 1
                
                try:
                    file_result = future.result()
                    
                    # Merge results
                    if file_result['image_url']:
                        result['images'].append(file_result['image_url'])
                    
                    if file_result['text']:
                        result['pdf_text'] += file_result['text']
                    
                    if file_result['error']:
                        result['errors'].append(file_result['error'])
                    
                    # Update progress
                    if progress_callback:
                        progress_callback(completed, total_files, f"Processed {file.name}")
                
                except Exception as e:
                    result['errors'].append(f"{file.name}: {str(e)}")
                    if progress_callback:
                        progress_callback(completed, total_files, f"Error: {file.name}")
        
        if progress_callback:
            progress_callback(total_files, total_files, "Processing complete!")
        
        return result
    
    def _process_single_file(self, file) -> Dict:
        """
        Process a single file (called by ThreadPoolExecutor).
        
        Returns:
            {
                'image_url': str or None,
                'text': str or None,
                'error': str or None
            }
        """
        result = {
            'image_url': None,
            'text': None,
            'error': None
        }
        
        try:
            # Validate file
            is_valid, error_msg = self.validate_file(file)
            if not is_valid:
                result['error'] = f"{file.name}: {error_msg}"
                return result
            
            # Read file data
            file_data = file.read()
            file_ext = os.path.splitext(file.name)[1].lower()
            
            # Process based on type
            if file_ext in self.ALLOWED_IMAGE_TYPES:
                # Smart optimization: only optimize large images
                if len(file_data) > 2 * 1024 * 1024:  # > 2MB
                    optimized_data = self.optimize_image(file_data)
                else:
                    optimized_data = file_data  # Skip optimization for small files
                
                url = self.upload_to_supabase(optimized_data, file.name, file.type)
                
                if url:
                    result['image_url'] = url
                else:
                    result['error'] = f"{file.name}: Upload failed"
            
            elif file_ext == '.pdf':
                # Extract text from PDF (limit to 5 pages for speed)
                text = self.extract_pdf_text(file_data, max_pages=5)
                
                if text:
                    result['text'] = f"\n\n--- {file.name} ---\n\n{text}"
                else:
                    result['error'] = f"{file.name}: Text extraction failed"
            
            elif file_ext == '.csv':
                # Extract data from CSV (limit to 50 rows for speed)
                csv_data = self.extract_csv_data(file_data, max_rows=50)
                
                if csv_data:
                    result['text'] = f"\n\n--- {file.name} ---\n\n{csv_data}"
                else:
                    result['error'] = f"{file.name}: Data extraction failed"
        
        except Exception as e:
            result['error'] = f"{file.name}: {str(e)}"
        
        return result


# Convenience function for easy import
def process_files(uploaded_files, progress_callback=None) -> Dict:
    """
    Simple wrapper for processing uploaded files.
    
    Args:
        uploaded_files: Streamlit uploaded files
        progress_callback: Optional callback(current, total, message)
    
    Usage:
        result = process_files(uploaded_files, progress_callback=my_callback)
        image_urls = result['images']
        pdf_content = result['pdf_text']
    """
    handler = FileHandler()
    return handler.process_attachments(uploaded_files, progress_callback=progress_callback)
