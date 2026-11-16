# 🚀 ANAND ORIGINALS — Deployment Guide

This guide covers step-by-step instructions for deploying your Django portfolio website to **Render** or **Vercel**, connecting it to a **free online MySQL database**, and running the initial data setup.

---

## 📋 Table of Contents
1. [Step 1: Set Up Free Online MySQL Database](#step-1-set-up-free-online-mysql-database)
2. [Step 2: Deploy to Render (Recommended for Django)](#step-2-deploy-to-render-recommended)
3. [Step 3: Deploy to Vercel (Alternative Serverless Option)](#step-3-deploy-to-vercel-serverless)
4. [Step 4: Post-Deployment Data Setup](#step-4-post-deployment-data-setup)
5. [Environment Variables Reference](#environment-variables-reference)

---

## Step 1: Set Up Free Online MySQL Database

Django needs a persistent database in production. You can use any free MySQL cloud provider:

### Option A: Aiven (Free MySQL Cloud)
1. Sign up at [aiven.io](https://aiven.io).
2. Create a new service: select **MySQL** (Free tier / Trial).
3. Under service overview, copy:
   - **Host** (e.g., `mysql-xxxx.aivencloud.com`)
   - **Port** (e.g., `12345`)
   - **User** (e.g., `avnadmin`)
   - **Password**
   - **Database Name** (default: `defaultdb`)

### Option B: TiDB Cloud (Free Serverless MySQL compatible)
1. Sign up at [tidbcloud.com](https://tidbcloud.com).
2. Create a free **Serverless Cluster**.
3. Under Connect, select **General** / **MySQL CLI** to copy the Host, Port, User, and Password.

---

## Step 2: Deploy to Render (Recommended)

Render is the most reliable, fully-featured host for Django applications.

### 1. Push your repository to GitHub
Make sure your project is committed and pushed to your GitHub repository:
`https://github.com/anandswarupjs-in/Portfolio_1.0.git`

### 2. Create a New Web Service on Render
1. Go to [render.com](https://render.com) and log in with your GitHub account.
2. Click **New +** → **Web Service**.
3. Select your repository: `anandswarupjs-in/Portfolio_1.0`.
4. Configure service settings:
   * **Name**: `anand-originals` (or any name you like)
   * **Region**: Nearest to you (e.g., *Singapore* or *Frankfurt*)
   * **Branch**: `main`
   * **Root Directory**: Leave blank (or `.` for project root)
   * **Runtime**: `Python 3`
   * **Build Command**: `./build.sh` (or `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`)
   * **Start Command**: `gunicorn config.wsgi:application`
   * **Instance Type**: `Free`

### 3. Add Environment Variables
Under the **Environment Variables** tab in your Render service, add:

| Key | Value |
|---|---|
| `DJANGO_DEBUG` | `False` |
| `DJANGO_SECRET_KEY` | *(Generate a 50+ character random string)* |
| `DJANGO_ALLOWED_HOSTS` | `*.onrender.com, your-custom-domain.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://*.onrender.com` |
| `DB_ENGINE` | `mysql` |
| `DB_NAME` | *(Your cloud database name)* |
| `DB_USER` | *(Your cloud database username)* |
| `DB_PASSWORD` | *(Your cloud database password)* |
| `DB_HOST` | *(Your cloud database host address)* |
| `DB_PORT` | `3306` *(or your provider's custom port)* |
| `PYTHON_VERSION` | `3.11.9` |

### 4. Deploy!
Click **Create Web Service**. Render will automatically clone your code, install dependencies, run migrations, compile static files, and start Gunicorn.

---

## Step 3: Deploy to Vercel (Serverless)

Vercel runs Django as serverless functions.

### 1. Requirements for Vercel
* Vercel requires an external database (SQLite is read-only on serverless). **You must configure MySQL from Step 1**.
* The repository includes [vercel.json](file:///e:/PROJECTS/ANAND_ORIGINALS_F1/ANAND_ORIGINALS/vercel.json) and an updated [wsgi.py](file:///e:/PROJECTS/ANAND_ORIGINALS_F1/ANAND_ORIGINALS/config/wsgi.py).

### 2. Deploy Steps
1. Go to [vercel.com](https://vercel.com) and log in with GitHub.
2. Click **Add New** → **Project**.
3. Import `anandswarupjs-in/Portfolio_1.0`.
4. Expand **Environment Variables** and add:
   * `DJANGO_DEBUG`: `False`
   * `DJANGO_SECRET_KEY`: *(random long secret string)*
   * `DJANGO_ALLOWED_HOSTS`: `.vercel.app`
   * `DJANGO_CSRF_TRUSTED_ORIGINS`: `https://*.vercel.app`
   * `DB_ENGINE`: `mysql`
   * `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_PORT`: *(your MySQL details)*
5. Click **Deploy**.

---

## Step 4: Post-Deployment Data Setup

Once your app is live and connected to your MySQL database:

### 1. Seed Initial Portfolio Data
To quickly populate your profile, projects, and skills into your new online database:
* **On Render**: Open the **Shell** tab in your dashboard and run:
  ```bash
  python seed_data.py
  ```
* **Locally connected to MySQL**: Change `.env` to point to your online MySQL database and run:
  ```bash
  python seed_data.py
  ```

### 2. Create Your Admin Superuser
In the shell or terminal:
```bash
python manage.py createsuperuser
```
Then log in to your live site at:
`https://your-app-url.com/admin/`

---

## 🔒 Notes on Media Files (Uploaded Photos & Resumes)
* On free tiers of Render and Vercel, the local filesystem is ephemeral (resets on new deploy).
* For permanent production image uploads, you can connect **Cloudinary** or **AWS S3** via `django-storages` whenever you are ready!
