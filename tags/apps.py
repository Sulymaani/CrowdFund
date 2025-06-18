from django.apps import AppConfig


class TagsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tags'
    verbose_name = 'Tags'
    
    def ready(self):
        """
        Perform initialization tasks when the app is ready.
        """
        pass  # Add any app startup code here if needed
