from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from core.validators import validate_file_size, validate_image_dimensions, validate_image_format
import io
from PIL import Image


class ValidatorTests(TestCase):
    """
    Tests for the image validator functions
    """
    
    def create_test_image(self, width, height, format='JPEG'):
        """Helper method to create test images of specified dimensions"""
        file = io.BytesIO()
        image = Image.new('RGB', (width, height), color='red')
        image.save(file, format=format)
        file.name = f'test.{format.lower()}'
        file.seek(0)
        return file
    
    def test_file_size_validator_accepts_small_files(self):
        """Test that files smaller than the limit pass validation"""
        # Create a small file (under 1MB)
        file = SimpleUploadedFile("small.jpg", b"x" * 500000)  # 500KB
        
        # Should not raise error
        validate_file_size(1)(file)  # 1MB limit
    
    def test_file_size_validator_rejects_large_files(self):
        """Test that files larger than the limit are rejected"""
        # Create a file just over 1MB
        file = SimpleUploadedFile("large.jpg", b"x" * 1100000)  # 1.1MB
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            validate_file_size(1)(file)  # 1MB limit
    
    def test_image_dimensions_validator_accepts_small_images(self):
        """Test that images within dimensions pass validation"""
        # Create an image with dimensions within limits
        file = self.create_test_image(800, 600)
        
        # Should not raise error
        validate_image_dimensions(1000, 800)(file)
    
    def test_image_dimensions_validator_rejects_wide_images(self):
        """Test that images wider than the limit are rejected"""
        # Create a wide image
        file = self.create_test_image(1200, 600)
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            validate_image_dimensions(1000, 800)(file)
    
    def test_image_dimensions_validator_rejects_tall_images(self):
        """Test that images taller than the limit are rejected"""
        # Create a tall image
        file = self.create_test_image(800, 1000)
        
        # Should raise ValidationError
        with self.assertRaises(ValidationError):
            validate_image_dimensions(1000, 800)(file)
    
    def test_image_format_validator_accepts_valid_formats(self):
        """Test that images with allowed formats pass validation"""
        # Create a JPEG image
        jpeg_file = self.create_test_image(100, 100, format='JPEG')
        
        # Should not raise error
        validate_image_format(['JPEG', 'PNG'])(jpeg_file)
        
        # Create a PNG image
        png_file = self.create_test_image(100, 100, format='PNG')
        
        # Should not raise error
        validate_image_format(['JPEG', 'PNG'])(png_file)
    
    def test_image_format_validator_rejects_invalid_formats(self):
        """Test that images with disallowed formats are rejected"""
        # Create a JPEG image
        jpeg_file = self.create_test_image(100, 100, format='JPEG')
        
        # Should raise ValidationError when only PNG is allowed
        with self.assertRaises(ValidationError):
            validate_image_format(['PNG'])(jpeg_file)
