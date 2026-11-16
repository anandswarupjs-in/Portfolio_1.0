# 🚀 ANAND ORIGINALS — Deployment Guide

**Traffic estimate:** ~10 visitors/week (very low usage — all free tiers easily handle this)

---

## 📋 Table of Contents
1. [Choosing a Free Lifetime MySQL Database](#-choosing-a-free-lifetime-mysql-database)
2. [Recommended Stack: TiDB Cloud + Render](#-recommended-deploy-tidb-cloud--render)
3. [Alternative Stack: Vercel + TiDB Cloud](#-alternative-deploy-vercel--tidb-cloud)
4. [Post-Deployment Setup](#-post-deployment-setup)
5. [Environment Variables Reference](#-environment-variables-reference)

---

## 🗄️ Choosing a Free Lifetime MySQL Database

For 10 visitors/week, database usage is essentially zero. Here are the **truly free, no credit card, no expiry** options:

| Provider | Storage | Free Forever? | Complexity | Best For |
|---|---|---|---|---|
| **TiDB Cloud Serverless** ✅ | 5 GB | Yes | Easy | Best overall choice |
| **Oracle MySQL HeatWave** ✅ | 50 GB | Yes (with account activity) | Complex setup | Maximum storage |
| `db4free.net` ❌ | 200 MB | Unreliable, testing only | Very easy | Do NOT use for portfolio |
| PlanetScale ❌ | — | Free tier removed 2024 | — | Discontinued free tier |

---

### ✅ Best Choice: TiDB Cloud Serverless (Recommended)

**Why TiDB Cloud?**
- ✅ **Truly free forever** — not a trial, no expiry date
- ✅ **5 GB storage** — your portfolio will use < 5 MB
- ✅ **50 million Request Units/month free** — 10 visitors/week = ~200 requests/month (essentially nothing)
- ✅ **100% MySQL compatible** — works directly with Django's MySQL engine
- ✅ No credit card required to start

**Setup Steps:**
1. Sign up at [tidbcloud.com](https://tidbcloud.com) (free, no card needed)
2. Click **Create Cluster** → choose **Serverless**
3. Select region: `AWS / Singapore` (closest to India)
4. Click **Create**
5. After creation, click **Connect** → choose **General** → copy:
   - **Host** (e.g., `gateway01.ap-southeast-1.prod.aws.tidbcloud.com`)
   - **Port** (`4000`)
   - **Username** (e.g., `xxxxxxx.root`)
   - **Password** (click *Generate Password* and save it)
   - **Database name** (`test` by default, or create a new one called `anand_originals`)

> [!IMPORTANT]
> TiDB Cloud requires SSL. Add `"ssl": {"ssl": True}` to your DB OPTIONS in settings.
> This is already handled in the settings.py for TiDB (see Environment Variables section).

---

### ✅ Alternative: Oracle Cloud Always Free MySQL

**Why Oracle Cloud?**
- ✅ **50 GB storage** — massively generous for a portfolio
- ✅ **Truly free forever** — Oracle's "Always Free" tier never expires
- ✅ Includes free ARM compute (you can host the Django app itself there too!)
- ⚠️ More complex to set up (VCN, subnets, security lists)
- ⚠️ Requires credit card at signup (but is NOT charged on Always Free)
- ⚠️ Oracle reclaims idle VMs if CPU < 20% — keep the app alive with a cron ping

**Setup:** [docs.oracle.com/always-free](https://www.oracle.com/cloud/free/)

---

## 🏆 Recommended Deploy: TiDB Cloud + Render

**Render** is the most developer-friendly free host for Django. Gunicorn runs natively, static files, media, migrations — all handled automatically.

### Step 1: Set Up TiDB Cloud Database (5 minutes)
1. Sign up at **[tidbcloud.com](https://tidbcloud.com)**
2. Create a **Serverless** cluster in `AWS / Singapore`
3. Click **Connect → General** and note down: Host, Port (4000), Username, Password

### Step 2: Push Code to GitHub
Your code is already pushed to: `https://github.com/anandswarupjs-in/Portfolio_1.0.git`

For future changes:
```bash
git add .
git commit -m "your message"
git push origin main
```

### Step 3: Deploy on Render
1. Go to **[render.com](https://render.com)** → sign up with GitHub
2. Click **New +** → **Web Service**
3. Select repo: **`anandswarupjs-in/Portfolio_1.0`**
4. Configure:
   - **Name:** `anand-originals`
   - **Region:** `Singapore` (closest)
   - **Branch:** `main`
   - **Runtime:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn config.wsgi:application`
   - **Instance Type:** `Free`

5. Under **Environment Variables**, add all variables from the table below
6. Click **Create Web Service** — Render auto-deploys on every `git push`!

> [!NOTE]
> Render's free tier sleeps after 15 minutes of inactivity and wakes on the next request (cold start ~30 seconds). For 10 visitors/week this is completely acceptable.

---

## ⚡ Alternative Deploy: Vercel + TiDB Cloud

Vercel runs Django as a serverless function. The `vercel.json` is already configured in your repo.

> [!WARNING]
> Vercel's serverless model means **no persistent file storage** — uploaded images/resumes will be lost on redeploy. Only use Vercel if you're okay with that limitation. Use **Render** for full media upload support.

1. Go to **[vercel.com](https://vercel.com)** → log in with GitHub
2. Click **Add New → Project** → Import `anandswarupjs-in/Portfolio_1.0`
3. Add Environment Variables (same as the table below)
4. Click **Deploy**

---

## 🔧 Post-Deployment Setup

After your app is live:

### 1. Seed Your Portfolio Data
In Render's **Shell** tab (or Terminal on your server):
```bash
python seed_data.py
```
This populates: profile, 6 projects, 13 skills, education — all in one command.

### 2. Create Admin Superuser
```bash
python manage.py createsuperuser
```
Then go to `https://your-app-url.com/admin/` to log in and manage content.

### 3. Upload Your Profile Photo & Resume
Inside the admin panel → Profile → upload your photo and resume PDF.

---

## 🔑 Environment Variables Reference

Add these in Render/Vercel dashboard under **Environment Variables**:

| Variable | Example Value | Description |
|---|---|---|
| `DJANGO_DEBUG` | `False` | Must be False in production |
| `DJANGO_SECRET_KEY` | `s3cr3t-50-char-random-string` | Generate at [djecrety.ir](https://djecrety.ir) |
| `DJANGO_ALLOWED_HOSTS` | `anand-originals.onrender.com` | Your app's domain |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://anand-originals.onrender.com` | Full HTTPS URL |
| `DB_ENGINE` | `mysql` | Use MySQL |
| `DB_HOST` | `gateway01.ap-southeast-1.prod.aws.tidbcloud.com` | From TiDB Connect screen |
| `DB_PORT` | `4000` | TiDB uses port 4000 |
| `DB_NAME` | `anand_originals` | Your DB name |
| `DB_USER` | `xxxxxxx.root` | From TiDB Connect screen |
| `DB_PASSWORD` | `yourPassword123` | From TiDB Connect screen |
| `PYTHON_VERSION` | `3.11.9` | Required for Render |

> [!CAUTION]
> Never commit your `.env` file to GitHub. The `.gitignore` already excludes it.
> Always set secrets through the platform dashboard, never hardcode them.

---

## 🔄 Updating Your Site After Deployment

Every time you make a change:
```bash
git add .
git commit -m "describe your change"
git push origin main
```
Render automatically redeploys within ~2 minutes of every push. ✅
