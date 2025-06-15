from django.core.exceptions import ValidationError
from django.core.validators import BaseValidator
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible
from PIL import Image
import os

@deconstructible
class FileSizeValidator(BaseValidator):
    """
    Validates that the file is not larger than the specified limit in MB
    """
    message = _('File size must not exceed %(limit_value)s MB. Current size is %(show_value)s MB.')
    code = 'file_too_large'
    
    def __init__(self, limit_value_mb):
        self.limit_value = limit_value_mb
        # Convert MB to bytes for internal comparison
        self._limit_bytes = limit_value_mb * 1024 * 1024
    
    def compare(self, file_size, limit_value_mb):
        # Compare file size in bytes to the limit in bytes
        return file_size > self._limit_bytes
    
    def clean(self, file):
        # Check if it's a file-like object with size attribute
        if hasattr(file, 'size'):
            return file.size
        return 0
        
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.limit_value == other.limit_value and
            self.message == other.message and
            self.code == other.code
        )


@deconstructible
class ImageDimensionsValidator:
    """
    Validates that the image dimensions do not exceed the specified limits
    """
    message_width = _('Image width must not exceed %(max_width)s px. Current width is %(width)s px.')
    message_height = _('Image height must not exceed %(max_height)s px. Current height is %(height)s px.')
    message_invalid = _('Uploaded file is not a valid image.')
    code = 'invalid_image_dimensions'
    
    def __init__(self, max_width, max_height):
        self.max_width = max_width
        self.max_height = max_height
    
    def __call__(self, file):
        if not file:
            return
            
        try:
            # Reset file pointer
            file.seek(0)
            img = Image.open(file)
            width, height = img.size
            
            if width > self.max_width:
                raise ValidationError(
                    self.message_width,
                    code=self.code,
                    params={'max_width': self.max_width, 'width': width}
                )
                
            if height > self.max_height:
                raise ValidationError(
                    self.message_height,
                    code=self.code,
                    params={'max_height': self.max_height, 'height': height}
                )
                
            # Reset file pointer again for other validators
            file.seek(0)
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # If Pillow can't open it, it's probably not a valid image
            if "cannot identify image file" in str(e):
                raise ValidationError(self.message_invalid, code=self.code)
            else:
                raise ValidationError(f'Error validating image: {e}', code=self.code)
    
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.max_width == other.max_width and
            self.max_height == other.max_height
        )


@deconstructible
class ImageFormatValidator:
    """
    Validates that the image is in one of the allowed formats
    """
    message = _('Image must be in one of these formats: %(allowed_formats)s. Current format is %(format)s.')
    message_invalid = _('Uploaded file is not a valid image.')
    code = 'invalid_image_format'
    
    def __init__(self, allowed_formats=None):
        if allowed_formats is None:
            allowed_formats = ['JPEG', 'PNG']
        self.allowed_formats = allowed_formats
    
    def __call__(self, file):
        if not file:
            return
            
        try:
            # Reset file pointer
            file.seek(0)
            img = Image.open(file)
            if img.format not in self.allowed_formats:
                raise ValidationError(
                    self.message,
                    code=self.code,
                    params={
                        'allowed_formats': ', '.join(self.allowed_formats),
                        'format': img.format or 'unknown'
                    }
                )
                
            # Reset file pointer again for other validators
            file.seek(0)
        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            # If Pillow can't open it, it's probably not a valid image
            if "cannot identify image file" in str(e):
                raise ValidationError(self.message_invalid, code=self.code)
            else:
                raise ValidationError(f'Error validating image format: {e}', code=self.code)
    
    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.allowed_formats == other.allowed_formats
        )
