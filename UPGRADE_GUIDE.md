# Upgrade and Maintenance Guide

## What Was Fixed

This document outlines all the changes made to modernize and future-proof the DarkNetwork project.

### 1. Django Version Upgrade
- **Before:** Django 4.0.2 (2022, had security vulnerabilities)
- **After:** Django 5.1.x (2025, latest stable LTS)
- **Why:** Security patches, performance improvements, and 5+ years of future support

### 2. Dependencies Updated
All packages upgraded to latest stable versions:
- `gunicorn` 20.1.0 → 23.0.0
- `Pillow` (implicit) → 11.0.0
- Added `whitenoise` 6.7.0 for static file serving
- Added `python-decouple` 3.8 for environment variable management
- `requests` 2.27.1 → 2.32.3
- `beautifulsoup4` 4.10.0 → 4.12.3

### 3. Removed Deprecated Packages
- **django-heroku**: No longer maintained, functionality replaced with native Django + whitenoise
- **django-autoslug**: Not needed for this project
- **django-tinymce**: Not used in the project
- **autopep8, cffi, comtypes, certifi, charset-normalizer**: Unnecessary dependencies

### 4. Settings.py Modernization

#### Added:
- `DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'` (required in Django 3.2+)
- Environment variable support for:
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG`
  - `DJANGO_ALLOWED_HOSTS`
- WhiteNoise middleware for static file serving
- Production security settings (SSL, secure cookies, XSS protection)
- Path object usage instead of `os.path.join`

#### Removed:
- `USE_L10N` (deprecated in Django 4.0, removed in 5.0)
- `django_heroku.settings()` call
- Duplicate `BASE_DIR` definition

### 5. Models Improvements

**User Model:**
- Made `profile_pic` nullable (`null=True, blank=True`)
- Made `cover` nullable (`null=True`)
- Added fallback in `serialize()` for missing profile pictures
- Prevents errors when users don't upload profile images

### 6. Views Improvements

**Error Handling:**
- Added try-except blocks for all database queries
- Proper 404 responses when users/posts don't exist
- Proper HTTP status codes (405 for wrong methods, 403 for unauthorized, 500 for server errors)
- Removed all debug `print()` statements

**Security:**
- Added authorization checks (users can only edit/delete their own posts)
- Better exception handling with meaningful error messages
- Consistent error responses

**Bug Fixes:**
- Fixed profile view crash when Follower object doesn't exist
- Fixed potential issues with missing profile pictures
- Improved comment handling

### 7. Project Structure

**New Files:**
- `.gitignore` - Prevents committing sensitive files
- `.env.example` - Template for environment variables
- `README.md` - Comprehensive documentation
- `check_health.py` - Health check and maintenance script
- `network/static/network/default_profile.svg` - Default profile image

### 8. Migration Updates
- Auto-generated migration for:
  - BigAutoField primary keys (future-proof for large datasets)
  - Nullable profile_pic and cover fields

## How to Keep the Project Updated

### Regular Maintenance (Every 3-6 Months)

1. **Update Dependencies:**
   ```bash
   pip list --outdated
   pip install --upgrade Django gunicorn whitenoise Pillow
   pip freeze > requirements.txt
   ```

2. **Check for Security Issues:**
   ```bash
   python manage.py check --deploy
   ```

3. **Run Health Check:**
   ```bash
   python check_health.py
   ```

4. **Test After Updates:**
   ```bash
   python manage.py test
   python manage.py runserver
   # Test major features manually
   ```

### Django Version Upgrade Strategy

When a new Django version is released:

1. **Read Release Notes:**
   - https://docs.djangoproject.com/en/stable/releases/

2. **Check Deprecation Warnings:**
   ```bash
   python -Wa manage.py test
   ```

3. **Update Django:**
   ```bash
   pip install --upgrade 'Django>=5.2,<6.0'
   ```

4. **Run Migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Test Thoroughly:**
   - Authentication
   - Post creation/editing/deletion
   - Comments
   - Following/unfollowing
   - Image uploads
   - Profile pages

### Long-Term Sustainability (10+ Years)

To ensure the project remains runnable:

1. **Use Docker (Recommended):**
   Create a `Dockerfile` to freeze the entire environment:
   ```dockerfile
   FROM python:3.13-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["gunicorn", "project4.wsgi:application"]
   ```

2. **Document Dependencies:**
   - Keep `requirements.txt` updated
   - Document Python version in README
   - Note any OS-level dependencies

3. **Database Migrations:**
   - Always commit migration files
   - Test migrations on a copy of production data
   - Keep backups before major changes

4. **Static Files:**
   - Consider using CDN for media files (images)
   - Use cloud storage (S3, CloudFlare R2) for user uploads in production

5. **Environment Variables:**
   - Never commit `.env` file
   - Document all required variables in `.env.example`
   - Use a secrets manager in production

## Breaking Changes to Be Aware Of

### From Django 4.0 to 5.1:
1. `USE_L10N` removed - locale formatting always enabled
2. Primary key type changed to BigAutoField
3. Some query optimizations may change behavior

### Python 3.13 Compatibility:
- All dependencies now support Python 3.13
- No breaking changes from Python 3.8+

## Testing Checklist

After updates, test these features:

- [ ] User registration with profile picture
- [ ] User registration without profile picture
- [ ] Login/logout
- [ ] Create post with image
- [ ] Create post with text only
- [ ] Edit post
- [ ] Delete post
- [ ] Like/unlike post
- [ ] Save/unsave post
- [ ] Add comment
- [ ] Follow/unfollow user
- [ ] View user profile
- [ ] View following feed
- [ ] View saved posts
- [ ] Pagination works
- [ ] Admin panel accessible
- [ ] Static files load correctly
- [ ] Media files upload and display

## Common Issues and Solutions

### Issue: Migrations fail
```bash
# Solution: Reset migrations (development only!)
rm -rf network/migrations/__pycache__
python manage.py migrate --fake network zero
python manage.py migrate
```

### Issue: Static files not loading
```bash
# Solution: Collect static files
python manage.py collectstatic --noinput
```

### Issue: Permission denied on media files
```bash
# Solution: Fix permissions
chmod -R 755 network/media
```

### Issue: Old Python version
```bash
# Solution: Use pyenv to manage Python versions
pyenv install 3.13.3
pyenv local 3.13.3
```

## Future Improvements to Consider

1. **API Endpoints:** Add Django REST Framework for mobile app support
2. **Real-time Updates:** WebSockets for live notifications
3. **Search:** Full-text search for posts and users
4. **Moderation:** Admin tools for content moderation
5. **Analytics:** Track user engagement
6. **Email:** Email notifications for follows, comments
7. **Testing:** Add automated tests (pytest, selenium)
8. **CI/CD:** Automated testing and deployment
9. **Monitoring:** Error tracking (Sentry), performance monitoring
10. **Caching:** Redis for session storage and caching

## Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)
- [Twelve-Factor App](https://12factor.net/)

## Changelog

### 2026-01-07 - Major Modernization
- Upgraded to Django 5.1.x
- Updated all dependencies
- Removed deprecated settings
- Added comprehensive error handling
- Added security improvements
- Created documentation and maintenance tools
