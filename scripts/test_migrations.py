"""
Script to test database migrations in a safe environment before applying to production.
This creates a temporary database, applies all migrations, and reports any issues.

Usage:
    python scripts/test_migrations.py
"""
import os
import sys
import tempfile
import shutil
import subprocess
from pathlib import Path

# Add the project root to the path
sys.path.append(str(Path(__file__).resolve().parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crowdfund.settings')

def main():
    # Create a temporary directory for the test database
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, 'test_migrations.sqlite3')
    
    try:
        print("Testing migrations with temporary database...")
        print(f"Database path: {temp_db_path}")
        
        # Set environment variables for the test
        test_env = os.environ.copy()
        test_env['TEST_DB_PATH'] = temp_db_path
        
        # Show migration plan without applying
        print("\n=== Migration Plan ===")
        subprocess.run(
            ['python', 'manage.py', 'showmigrations'],
            env=test_env,
            check=True
        )
        
        # Run migrations on the test database
        print("\n=== Applying Migrations ===")
        migration_result = subprocess.run(
            ['python', 'manage.py', 'migrate', '--settings=crowdfund.settings.test_migrations'],
            env=test_env,
            capture_output=True,
            text=True
        )
        
        if migration_result.returncode == 0:
            print("✅ Migrations applied successfully!")
            print(migration_result.stdout)
        else:
            print("❌ Migration failed!")
            print("Error output:")
            print(migration_result.stderr)
            return 1
        
        # Run basic model validation
        print("\n=== Validating Models ===")
        validation_result = subprocess.run(
            ['python', 'manage.py', 'check', '--settings=crowdfund.settings.test_migrations'],
            env=test_env,
            capture_output=True,
            text=True
        )
        
        if validation_result.returncode == 0:
            print("✅ Model validation passed!")
        else:
            print("❌ Model validation failed!")
            print(validation_result.stderr)
            return 1
            
        return 0
        
    finally:
        # Clean up temporary directory
        shutil.rmtree(temp_dir)
        print(f"\nTemporary test database removed: {temp_dir}")

if __name__ == "__main__":
    sys.exit(main())
