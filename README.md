# ANAND ORIGINALS

Premium personal developer portfolio for **Anand Swarup J S** (CSE, IIIT Kottayam).
Django + SQLite (dev) / MySQL (production), Django templates, plain CSS and vanilla JavaScript.

Palette: black `#080808`, white `#FFFFFF`, red `#E50914`. Content is managed entirely from Django Admin.

## Quick start (local)

```bash
python -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt     # mysqlclient is only needed for MySQL; see note below
cp .env.example .env                # then edit .env (keep DJANGO_DEBUG=True locally)
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and the admin at http://127.0.0.1:8000/admin/.

> If `mysqlclient` fails to install locally, remove that line from `requirements.txt` for development; it is only used when `DB_ENGINE=mysql`.

## Admin account from environment

Instead of `createsuperuser`, you can run:

```bash
python manage.py ensure_admin
```

The command reads `DJANGO_SUPERUSER_USERNAME`, `DJANGO_SUPERUSER_EMAIL` and
`DJANGO_SUPERUSER_PASSWORD` from the environment (or your local `.env`), creates the
superuser if it does not exist, and updates the password if it does.

Add your real values to your local `.env` (which is git-ignored and **never** committed):

```
DJANGO_SUPERUSER_USERNAME=your_username
DJANGO_SUPERUSER_EMAIL=your_email@example.com
DJANGO_SUPERUSER_PASSWORD=a_very_strong_password
```

**Never put a real password in `.env.example`, a template, a test, or the README.**

## First content steps (Admin)

1. **Profile**: name, title, introduction, about, email, photo, resume (PDF), GitHub and LinkedIn. Only one profile can exist.
2. **Education**, **Skills**, **Projects** (with screenshots inline), **Achievements**, **Certifications**, **Gallery images**.
3. Use *Visibility*, *Featured* and *Display order* to control what appears. Hidden items never render publicly.
4. **Contact messages** are read-only in Admin.

Nothing is pre-filled except a fallback name/title shown until a Profile exists. No achievements, certifications or experience are invented.

## Tests and checks

```bash
python -m compileall -q .
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

## Environment variables

See `.env.example`. Key ones: `DJANGO_SECRET_KEY` (required), `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`,
`DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_ADMIN_URL`, `DB_ENGINE` (`sqlite`|`mysql`), `DB_NAME/USER/PASSWORD/HOST/PORT`.
Generate a secret key: `python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"`.

## Production deployment (Ubuntu + Nginx + Gunicorn + MySQL)

1. **Server packages**: `sudo apt install python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config nginx mysql-server`
2. **Database**:
   ```sql
   CREATE DATABASE anand_originals CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'anand'@'localhost' IDENTIFIED BY 'strong-password';
   GRANT ALL ON anand_originals.* TO 'anand'@'localhost';
   ```
3. **Code and env**: copy the project to `/srv/anand_originals`, create a venv, `pip install -r requirements.txt`,
   create `.env` with `DJANGO_DEBUG=False`, a real `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com`,
   `DJANGO_CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com`, `DB_ENGINE=mysql` and the DB credentials. Set a non-default `DJANGO_ADMIN_URL`.
4. **Migrate and collect**:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py collectstatic --noinput
   python manage.py check --deploy
   ```
5. **Gunicorn** (`/etc/systemd/system/anand.service`):
   ```ini
   [Unit]
   Description=ANAND ORIGINALS
   After=network.target
   [Service]
   User=www-data
   WorkingDirectory=/srv/anand_originals
   EnvironmentFile=/srv/anand_originals/.env
   ExecStart=/srv/anand_originals/venv/bin/gunicorn config.wsgi:application --bind unix:/run/anand.sock --workers 3
   [Install]
   WantedBy=multi-user.target
   ```
6. **Nginx** (static and media are served by Nginx, not Django, when DEBUG is off):
   ```nginx
   server {
     server_name yourdomain.com www.yourdomain.com;
     client_max_body_size 12M;
     location /static/ { alias /srv/anand_originals/staticfiles/; }
     location /media/  { alias /srv/anand_originals/media/; }
     location / {
       proxy_pass http://unix:/run/anand.sock;
       proxy_set_header Host $host;
       proxy_set_header X-Forwarded-Proto $scheme;
       proxy_set_header X-Real-IP $remote_addr;
     }
   }
   ```
   Then enable HTTPS with `sudo certbot --nginx`. Make sure `.cache/` and `media/` are writable by the service user.
7. **Backups**: back up the MySQL database and the `media/` folder.

### Deployment checklist

- [ ] `DJANGO_DEBUG=False`, unique secret key, hosts and CSRF origins set
- [ ] HTTPS active (the app redirects to HTTPS and sets secure cookies when DEBUG is off)
- [ ] `python manage.py check --deploy` is clean
- [ ] Superuser created with a strong password; admin URL changed
- [ ] `collectstatic` run; Nginx serves `/static/` and `/media/`
- [ ] Profile, education, skills and projects entered in Admin
- [ ] Contact form submitted once end-to-end
- [ ] Database and media backups scheduled

## Notes

- **Contact form protection**: CSRF, server-side validation, hidden honeypot field, and a per-IP rate limit (5 per hour, configurable in settings) backed by a file cache. Behind a proxy, ensure Nginx passes the real client address so the limit counts per visitor.
- **Uploads** are checked for extension and size (images 5 MB, PDFs 10 MB); images are also verified by Pillow.
- Fonts (Archivo, Newsreader) load from Google Fonts with system fallbacks.
- The footer line `netflix inspired` is intentionally kept at the bottom of every page.
