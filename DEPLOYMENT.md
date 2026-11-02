# SHTOR HOUSE deployment

## What this setup does and does not guarantee

GitHub stores the source code; it does not run this Django application. GitHub
Actions runs checks on every push and pull request. PythonAnywhere hosts the
Django app independently of the owner's computer.

The free PythonAnywhere plan is the simplest no-cost Django option for this
project, but it has resource and outbound-network restrictions and does not
provide a paid uptime guarantee. A free service cannot promise that the site
will never stop or encounter an error. The free account uses a
`your-username.pythonanywhere.com` address. Review the current plan limits before
relying on it for business-critical sales.

## 1. Put the source in a private GitHub repository

1. Create a **private** repository in your GitHub account.
2. From the project folder, review `git status` and confirm `.env`, `db.sqlite3`,
   `media/`, and `backups/` are not staged. `.gitignore` excludes these local
   files. Never commit OAuth, SMTP, or Django secrets.
3. Add, commit, and push only the application source. GitHub Actions will run
   Django's checks, the app tests, and the JavaScript syntax check.
4. Wait for the workflow to pass before deploying changes.

This workspace may not have a Git repository initialized yet. If so, initialize
Git in the project folder and add the GitHub repository as its remote before
the first push. Do not upload `.env`, the database, or the backup ZIP.

## 2. Create the free PythonAnywhere web app

1. Create a PythonAnywhere account and a manual web app using Python 3.11.
2. In a Bash console, clone your private GitHub repository using the SSH key
   configured for that account.
3. Create and activate a Python 3.11 virtual environment and install the
   pinned packages:

   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 shtor-house
   pip install -r ~/parda-proekt/requirements.txt
   ```

   Replace `parda-proekt` with the actual directory created by `git clone`.
4. Configure the web app's WSGI file to add the project directory to
   `sys.path`, set `DJANGO_SETTINGS_MODULE` to `config.settings`, then load
   `get_wsgi_application()`. Set the virtualenv and working directory in the
   PythonAnywhere Web tab.
5. In the Web tab's environment-variable section, configure:

   - `DJANGO_DEBUG=False`
   - `DJANGO_SECRET_KEY` — generate a new, private value; do not reuse the
     development fallback or put it in GitHub.
   - `DJANGO_ALLOWED_HOSTS=your-username.pythonanywhere.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://your-username.pythonanywhere.com`
   - `DJANGO_SECURE_SSL_REDIRECT=True`
   - SMTP variables if the chosen email service can send from this host.
   - Google OAuth variables only if Google login is configured; register the
     production callback URL
     `https://your-username.pythonanywhere.com/auth/google/callback/` with
     Google.

   Do not add any of these values to the repository or change the local `.env`.
   The production settings intentionally refuse to start if the required Django
   secret, hostname, or SMTP host/sender are missing.
   If the host's UI has no environment-variable editor, define the values in its
   generated WSGI file outside the GitHub repository before importing the
   Django application.
6. Install dependencies, run migrations, and collect static files:

   ```bash
   cd ~/parda-proekt
   python manage.py migrate
   python manage.py collectstatic --noinput
   python manage.py check --deploy
   ```

   In the PythonAnywhere Web tab, map `/static/` to the project's
   `staticfiles/` directory, then reload the web app.
7. Create a production administrator with `python manage.py createsuperuser`.
   Never use the local development password for a public website.

PythonAnywhere documents the exact WSGI, virtualenv, and static-file steps in
its [Django deployment guide](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject/)
and [static-file guide](https://help.pythonanywhere.com/pages/StaticFiles/).

## 3. Preserve the existing catalog and accounts (optional)

The GitHub repository intentionally does not contain the SQLite database,
uploaded product images, customer requests, or backup archives. To preserve
existing data, transfer a backup privately through the hosting account's file
upload or another secure channel, never through GitHub. Stop the web app before
replacing its database/media, extract the archive into the project directory,
check file ownership and permissions, then reload the app.

If existing data is not transferred, run migrations and create a new
administrator; the production catalog starts empty.

## 4. Keep production data backed up

The application files live under the PythonAnywhere account, independently of
the Windows computer. Configure a daily task in the PythonAnywhere Tasks tab to
run:

```bash
/home/YOUR_USERNAME/.virtualenvs/shtor-house/bin/python /home/YOUR_USERNAME/parda-proekt/manage.py backup_site
```

Replace `YOUR_USERNAME` and the project path. Verify that ZIP archives appear
under the project's `backups/` directory. Periodically download a copy to
storage separate from the hosting account; a backup stored only beside the
database is not protection against loss of the hosting account.

## 5. Deploy later GitHub changes

The free setup does not automatically deploy each push. After GitHub Actions
passes, pull the approved commit in the PythonAnywhere Bash console, install
requirements if they changed, run migrations when needed, run `collectstatic`
when assets changed, and reload the web app:

```bash
cd ~/parda-proekt
git pull
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
```

Do not run `git pull` while manually editing the same files on the host. A failed
deployment must be rolled back to the last passing commit and the web app
reloaded.

## Limits of the free option

- GitHub Actions checks code but cannot guarantee provider uptime or prevent all
  runtime errors.
- Free hosting has limited disk, compute, and external-network access. Large
  uploads may exceed provider or browser limits even though the application
  does not impose an upload-size limit.
- The site uses SQLite and files stored in the account. This is suitable only
  for a small, single-host deployment; do not add multiple app workers or move
  to a multi-instance service without moving the database and media to shared,
  persistent services.
- Password-reset emails and Google sign-in require external providers and valid
  production credentials. Test both on the actual host; free-tier network
  restrictions may block third-party services.
- If continuous availability, automatic deployment, or business-critical data
  durability is required, use a paid host with persistent storage, external
  database/media backups, and monitoring.
