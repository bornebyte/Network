# DarkNetwork - Social Network Application

A Django-based social network application with posts, comments, following, and user profiles.

## Features

- User authentication (login, logout, register)
- Create, edit, and delete posts with text and images
- Like and save posts
- Comment on posts
- Follow/unfollow users
- User profiles with profile pictures and cover images
- Paginated feeds (all posts, following feed, saved posts)

## Requirements

- Python 3.10 or higher
- pip (Python package manager)

## Installation & Setup

### 1. Clone or Download the Project

```bash
cd /home/shubham/dev/darkNetwork
```

### 2. Create a Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` to set your own values:
- `DJANGO_SECRET_KEY`: Generate a new secret key for production
- `DJANGO_DEBUG`: Set to `False` in production
- `DJANGO_ALLOWED_HOSTS`: Set your domain names

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser (Admin Account)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 7. Collect Static Files (For Production)

```bash
python manage.py collectstatic --noinput
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000/ in your browser.

## Production Deployment

### Using Gunicorn

```bash
gunicorn project4.wsgi:application --bind 0.0.0.0:8000
```

### Environment Variables for Production

Make sure to set these in production:

```bash
export DJANGO_SECRET_KEY="your-secret-production-key"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="yourdomain.com,www.yourdomain.com"
```

### Security Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use a strong, unique `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Use HTTPS in production
- [ ] Set up proper database backups
- [ ] Configure media file storage (e.g., AWS S3, CloudFlare R2)
- [ ] Set up proper logging
- [ ] Enable CSRF protection (already configured)

## Project Structure

```
darkNetwork/
├── network/              # Main application
│   ├── models.py        # Database models (User, Post, Comment, Follower)
│   ├── views.py         # View functions
│   ├── urls.py          # URL routing
│   ├── templates/       # HTML templates
│   ├── static/          # CSS, JavaScript, images
│   └── media/           # User-uploaded files
├── project4/            # Project configuration
│   ├── settings.py     # Django settings
│   ├── urls.py         # Main URL configuration
│   └── wsgi.py         # WSGI configuration
├── manage.py           # Django management script
├── requirements.txt    # Python dependencies
└── db.sqlite3         # SQLite database (dev)
```

## API Endpoints

- `GET /` - Homepage (all posts)
- `GET /n/following` - Following feed
- `GET /n/saved` - Saved posts
- `GET /<username>` - User profile
- `POST /n/createpost` - Create a new post
- `PUT /n/post/<id>/like` - Like a post
- `PUT /n/post/<id>/unlike` - Unlike a post
- `PUT /n/post/<id>/save` - Save a post
- `PUT /n/post/<id>/unsave` - Unsave a post
- `POST /n/post/<id>/write_comment` - Add a comment
- `GET /n/post/<id>/comments` - Get comments
- `POST /n/post/<id>/edit` - Edit a post
- `PUT /n/post/<id>/delete` - Delete a post
- `PUT /<username>/follow` - Follow a user
- `PUT /<username>/unfollow` - Unfollow a user

## Troubleshooting

### Issue: "No module named 'django'"
**Solution:** Make sure you've activated your virtual environment and installed requirements.

### Issue: Database errors
**Solution:** Run migrations again:
```bash
python manage.py makemigrations
python manage.py migrate
```

### Issue: Static files not loading
**Solution:** Run collectstatic:
```bash
python manage.py collectstatic --noinput
```

### Issue: Image upload errors
**Solution:** Make sure the media directories exist and have write permissions:
```bash
mkdir -p network/media/profile_pic network/media/covers network/media/posts
chmod 755 network/media -R
```

## Maintenance & Updates

### Keeping Dependencies Updated

```bash
# Check for outdated packages
pip list --outdated

# Update specific package
pip install --upgrade Django

# Update all packages (be careful!)
pip install --upgrade -r requirements.txt
```

### Database Backups

```bash
# Backup SQLite database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# Backup with Django dumpdata
python manage.py dumpdata > backup.json
```

## License

This project is for educational purposes.

## Support

For issues and questions, please check the error logs and ensure all dependencies are properly installed.
