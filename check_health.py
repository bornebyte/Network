#!/usr/bin/env python3
"""
Django Project Health Check Script
This script checks your Django project for common issues and provides recommendations.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_success(text):
    print(f"✓ {text}")

def print_warning(text):
    print(f"⚠ {text}")

def print_error(text):
    print(f"✗ {text}")

def check_python_version():
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print_success(f"Python {version.major}.{version.minor}.{version.micro} (Good!)")
    elif version.major == 3 and version.minor >= 8:
        print_warning(f"Python {version.major}.{version.minor}.{version.micro} (Consider upgrading to 3.10+)")
    else:
        print_error(f"Python {version.major}.{version.minor}.{version.micro} (Upgrade recommended!)")

def check_virtual_environment():
    print_header("Checking Virtual Environment")
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_success("Running in a virtual environment")
    else:
        print_warning("Not running in a virtual environment (recommended for isolation)")

def check_dependencies():
    print_header("Checking Dependencies")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--outdated", "--format=json"],
            capture_output=True,
            text=True,
            check=True
        )
        outdated = json.loads(result.stdout)
        if outdated:
            print_warning(f"Found {len(outdated)} outdated packages:")
            for pkg in outdated[:5]:  # Show first 5
                print(f"  - {pkg['name']}: {pkg['version']} → {pkg['latest_version']}")
            if len(outdated) > 5:
                print(f"  ... and {len(outdated) - 5} more")
        else:
            print_success("All packages are up to date")
    except Exception as e:
        print_error(f"Could not check dependencies: {e}")

def check_django_config():
    print_header("Checking Django Configuration")
    try:
        # Add project to path
        project_dir = Path(__file__).parent
        sys.path.insert(0, str(project_dir))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project4.settings')
        
        import django
        django.setup()
        
        from django.conf import settings
        
        # Check DEBUG
        if settings.DEBUG:
            print_warning("DEBUG is True (should be False in production)")
        else:
            print_success("DEBUG is False (good for production)")
        
        # Check SECRET_KEY
        default_key = '13kl@xtukpwe&xj2xoysxe9_6=tf@f8ewxer5n&ifnd46+6$%8'
        if settings.SECRET_KEY == default_key:
            print_error("Using default SECRET_KEY (MUST change in production!)")
        else:
            print_success("Using custom SECRET_KEY")
        
        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            print_warning("ALLOWED_HOSTS not configured properly")
        else:
            print_success(f"ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}")
        
        # Check middleware
        required_middleware = [
            'django.middleware.security.SecurityMiddleware',
            'whitenoise.middleware.WhiteNoiseMiddleware',
        ]
        for mw in required_middleware:
            if mw in settings.MIDDLEWARE:
                print_success(f"{mw.split('.')[-1]} enabled")
            else:
                print_warning(f"{mw} not found in MIDDLEWARE")
                
    except Exception as e:
        print_error(f"Could not check Django config: {e}")

def check_database():
    print_header("Checking Database")
    try:
        import django
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM django_migrations")
            count = cursor.fetchone()[0]
            print_success(f"Database connected ({count} migrations applied)")
    except Exception as e:
        print_error(f"Database issue: {e}")

def check_security():
    print_header("Security Check")
    try:
        result = subprocess.run(
            [sys.executable, "manage.py", "check", "--deploy"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print_success("No security issues found")
        else:
            print_warning("Security issues detected:")
            print(result.stdout)
    except Exception as e:
        print_error(f"Could not run security check: {e}")

def check_static_files():
    print_header("Checking Static Files")
    static_root = Path("staticfiles")
    media_root = Path("network/media")
    
    if static_root.exists():
        print_success(f"Static root exists: {static_root}")
    else:
        print_warning(f"Static root not found (run 'collectstatic')")
    
    if media_root.exists():
        print_success(f"Media root exists: {media_root}")
    else:
        print_warning(f"Media root not found")

def main():
    print("\n" + "🔍 Django Project Health Check 🔍".center(60))
    
    check_python_version()
    check_virtual_environment()
    check_dependencies()
    check_django_config()
    check_database()
    check_security()
    check_static_files()
    
    print_header("Summary")
    print("Health check complete!")
    print("\nRecommendations:")
    print("1. Keep dependencies updated regularly")
    print("2. Review Django security checklist before deployment")
    print("3. Use environment variables for sensitive settings")
    print("4. Enable HTTPS in production")
    print("5. Set up automated backups")
    print("\n")

if __name__ == "__main__":
    main()
