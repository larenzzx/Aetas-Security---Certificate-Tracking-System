"""
File upload validators for Aetas Security Certificate Tracking System.

Security validators for:
- Image uploads (profile photos)
- Document uploads (certificates)
- File type validation
- Content validation
- Size validation
"""

# Try to import python-magic, fall back to basic validation if not available
try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False

from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions
from PIL import Image
import io


def validate_file_extension(value, allowed_extensions):
    """
    Validate file extension against whitelist.

    Args:
        value: UploadedFile object
        allowed_extensions: List of allowed extensions (without dots)

    Raises:
        ValidationError: If extension not in whitelist
    """
    import os
    ext = os.path.splitext(value.name)[1][1:].lower()
    if ext not in allowed_extensions:
        raise ValidationError(
            f'Unsupported file extension: .{ext}. '
            f'Allowed extensions: {", ".join(allowed_extensions)}'
        )


def validate_file_size(value, max_size_mb=5):
    """
    Validate file size.

    Args:
        value: UploadedFile object
        max_size_mb: Maximum size in megabytes

    Raises:
        ValidationError: If file exceeds size limit
    """
    max_size = max_size_mb * 1024 * 1024  # Convert to bytes
    if value.size > max_size:
        raise ValidationError(
            f'File size exceeds {max_size_mb}MB limit. '
            f'Your file is {value.size / (1024 * 1024):.2f}MB.'
        )


def validate_image_file(value):
    """
    Comprehensive image file validation.

    Validates:
    - File extension (JPG, JPEG, PNG, WebP)
    - File size (max 5MB)
    - MIME type verification
    - Image dimensions (not too large)
    - Image file integrity

    Args:
        value: UploadedFile object

    Raises:
        ValidationError: If validation fails
    """
    # 1. Extension validation
    allowed_extensions = ['jpg', 'jpeg', 'png', 'webp']
    validate_file_extension(value, allowed_extensions)

    # 2. Size validation (5MB max)
    validate_file_size(value, max_size_mb=5)

    # 3. MIME type validation
    if MAGIC_AVAILABLE:
        try:
            # Read first 1024 bytes for magic number detection
            file_content = value.read(1024)
            value.seek(0)  # Reset file pointer

            # Detect MIME type
            mime = magic.from_buffer(file_content, mime=True)

            # Allowed MIME types
            allowed_mimes = [
                'image/jpeg',
                'image/png',
                'image/webp'
            ]

            if mime not in allowed_mimes:
                raise ValidationError(
                    f'Invalid image file. File appears to be: {mime}. '
                    f'Only JPG, PNG, and WebP images are allowed.'
                )

        except Exception as e:
            raise ValidationError(f'Could not validate file type: {str(e)}')
    else:
        # Fallback: Basic content-type check from uploaded file
        if hasattr(value, 'content_type'):
            allowed_content_types = [
                'image/jpeg',
                'image/jpg',
                'image/png',
                'image/webp'
            ]
            if value.content_type not in allowed_content_types:
                raise ValidationError(
                    f'Invalid image file type: {value.content_type}. '
                    f'Only JPG, PNG, and WebP images are allowed.'
                )

    # 4. Image dimensions validation
    try:
        width, height = get_image_dimensions(value)

        # Maximum dimensions (prevent massive images)
        max_width = 5000
        max_height = 5000

        if width > max_width or height > max_height:
            raise ValidationError(
                f'Image dimensions too large. Maximum: {max_width}x{max_height}px. '
                f'Your image: {width}x{height}px.'
            )

        # Minimum dimensions (prevent tiny images)
        min_width = 50
        min_height = 50

        if width < min_width or height < min_height:
            raise ValidationError(
                f'Image dimensions too small. Minimum: {min_width}x{min_height}px. '
                f'Your image: {width}x{height}px.'
            )

    except Exception as e:
        raise ValidationError(f'Could not read image dimensions: {str(e)}')

    # 5. Image file integrity validation
    try:
        # Try to open and verify the image
        img = Image.open(value)
        img.verify()
        value.seek(0)  # Reset file pointer after verify

    except Exception as e:
        raise ValidationError(f'Invalid or corrupted image file: {str(e)}')


def validate_certificate_document(value):
    """
    Comprehensive document file validation for certificates.

    Validates:
    - File extension (PDF, PNG, JPG, JPEG)
    - File size (max 10MB)
    - MIME type verification
    - File integrity

    Args:
        value: UploadedFile object

    Raises:
        ValidationError: If validation fails
    """
    # 1. Extension validation
    allowed_extensions = ['pdf', 'png', 'jpg', 'jpeg']
    validate_file_extension(value, allowed_extensions)

    # 2. Size validation (10MB max for certificates)
    validate_file_size(value, max_size_mb=10)

    # 3. MIME type validation
    try:
        # Read first 2048 bytes for magic number detection
        file_content = value.read(2048)
        value.seek(0)  # Reset file pointer

        # Detect MIME type
        mime = magic.from_buffer(file_content, mime=True)

        # Allowed MIME types
        allowed_mimes = [
            'application/pdf',
            'image/jpeg',
            'image/png'
        ]

        if mime not in allowed_mimes:
            raise ValidationError(
                f'Invalid document file. File appears to be: {mime}. '
                f'Only PDF and image files are allowed.'
            )

        # Additional PDF validation
        if mime == 'application/pdf':
            # Check for PDF signature
            value.seek(0)
            header = value.read(5)
            if header != b'%PDF-':
                raise ValidationError('Invalid PDF file structure.')
            value.seek(0)

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'Could not validate file type: {str(e)}')


def sanitize_filename(filename):
    """
    Sanitize uploaded filename to prevent directory traversal attacks.

    Removes:
    - Path separators (/, \)
    - Null bytes
    - Control characters
    - Leading dots

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    import re

    # Remove path separators
    filename = filename.replace('/', '').replace('\\', '')

    # Remove null bytes
    filename = filename.replace('\x00', '')

    # Remove control characters
    filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)

    # Remove leading dots (hidden files)
    filename = filename.lstrip('.')

    # If filename is empty after sanitization, use default
    if not filename:
        filename = 'unnamed_file'

    # Limit length
    max_length = 255
    name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
    if len(filename) > max_length:
        name = name[:max_length - len(ext) - 1]
        filename = f"{name}.{ext}" if ext else name

    return filename


class SecureFileUploadMixin:
    """
    Mixin for secure file upload handling in forms.

    Usage:
        class MyForm(SecureFileUploadMixin, forms.ModelForm):
            pass
    """

    def clean_file_field(self, field_name, validator_func):
        """
        Clean and validate a file field.

        Args:
            field_name: Name of the file field
            validator_func: Validation function to apply

        Returns:
            Cleaned file

        Raises:
            ValidationError: If validation fails
        """
        file = self.cleaned_data.get(field_name)

        if file:
            # Sanitize filename
            file.name = sanitize_filename(file.name)

            # Run validator
            validator_func(file)

        return file
