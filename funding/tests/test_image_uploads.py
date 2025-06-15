from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from funding.models import Organisation, Campaign
from accounts.models import CustomUser
import io
from PIL import Image


class OrganisationImageTests(TestCase):
    """Test image upload limits for Organisation model"""
    
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Test Organisation")
    
    def create_test_image(self, width, height, format='JPEG', quality=90):
        """Helper to create a test image with specific dimensions and format"""
        file = io.BytesIO()
        image = Image.new('RGB', (width, height), color='red')
        image.save(file, format=format, quality=quality)
        file.name = f'test.{format.lower()}'
        file.seek(0)
        return file
    
    def create_large_file(self, size_mb=3):
        """Helper to create a file of specific size in MB"""
        # Create a file slightly bigger than the limit (e.g., 3.1 MB for 3 MB limit)
        size_bytes = int(size_mb * 1024 * 1024 * 1.1)
        return SimpleUploadedFile("large.jpg", b"x" * size_bytes)
    
    def test_organisation_logo_size_limit(self):
        """Test that organisation logo rejects files over 2MB"""
        # Create a large file (over 2MB)
        large_file = self.create_large_file(2)
        
        # Try to set as logo
        self.organisation.logo = large_file
        
        # Should raise ValidationError during clean
        with self.assertRaises(ValidationError):
            self.organisation.full_clean()
    
    def test_organisation_logo_dimensions_limit(self):
        """Test that organisation logo rejects images over 800x800"""
        # Create an oversized image
        oversized = self.create_test_image(900, 900)
        
        # Try to set as logo
        self.organisation.logo = oversized
        
        # Should raise ValidationError during clean
        with self.assertRaises(ValidationError):
            self.organisation.full_clean()
    
    def test_organisation_logo_valid_image(self):
        """Test that a valid logo image is accepted"""
        # Create a valid image
        valid_img = self.create_test_image(750, 750)
        
        # Set as logo
        self.organisation.logo = valid_img
        
        # Should not raise any errors
        self.organisation.full_clean()
    
    def test_organisation_banner_size_limit(self):
        """Test that organisation banner rejects files over 3MB"""
        # Create a large file (over 3MB)
        large_file = self.create_large_file(3)
        
        # Try to set as banner
        self.organisation.banner = large_file
        
        # Should raise ValidationError during clean
        with self.assertRaises(ValidationError):
            self.organisation.full_clean()
    
    def test_organisation_banner_dimensions_limit(self):
        """Test that organisation banner rejects images over 1920x480"""
        # Create an oversized image
        oversized = self.create_test_image(2000, 500)
        
        # Try to set as banner
        self.organisation.banner = oversized
        
        # Should raise ValidationError during clean
        with self.assertRaises(ValidationError):
            self.organisation.full_clean()
    
    def test_organisation_banner_valid_image(self):
        """Test that a valid banner image is accepted"""
        # Create a valid image
        valid_img = self.create_test_image(1920, 480)
        
        # Set as banner
        self.organisation.banner = valid_img
        
        # Should not raise any errors
        self.organisation.full_clean()


class CampaignImageTests(TestCase):
    """Test image upload limits for Campaign model"""
    
    def setUp(self):
        self.organisation = Organisation.objects.create(name="Test Organisation")
        self.campaign = Campaign.objects.create(
            organisation=self.organisation,
            title="Test Campaign",
            goal=1000
        )
    
    def create_test_image(self, width, height, format='JPEG', quality=90):
        """Helper to create a test image with specific dimensions and format"""
        file = io.BytesIO()
        image = Image.new('RGB', (width, height), color='red')
        image.save(file, format=format, quality=quality)
        file.name = f'test.{format.lower()}'
        file.seek(0)
        return file
    
    def create_large_file(self, size_mb=5):
        """Helper to create a file of specific size in MB"""
        # Create a file slightly bigger than the limit
        size_bytes = int(size_mb * 1024 * 1024 * 1.1)
        return SimpleUploadedFile("large.jpg", b"x" * size_bytes)
    
    def test_campaign_cover_size_limit(self):
        """Test that campaign cover image rejects files over 5MB"""
        # Create a large file (over 5MB)
        large_file = self.create_large_file(5)
        
        # Try to set as cover image
        self.campaign.cover_image = large_file
        
        # Should raise ValidationError during clean
        with self.assertRaises(ValidationError):
            self.campaign.full_clean()
    
    def test_campaign_cover_dimensions_limit(self):
        """Test that campaign cover image rejects images over 1920x1080"""
        # Create an oversized image
        oversized = self.create_test_image(2000, 1200)
        
        # Try to set as cover image
        self.campaign.cover_image = oversized
        
        # Should raise ValidationError during clean
        with self.assertRaises(ValidationError):
            self.campaign.full_clean()
    
    def test_campaign_cover_valid_image(self):
        """Test that a valid cover image is accepted"""
        # Create a valid image
        valid_img = self.create_test_image(1920, 1080)
        
        # Set as cover image
        self.campaign.cover_image = valid_img
        
        # Should not raise any errors
        self.campaign.full_clean()
