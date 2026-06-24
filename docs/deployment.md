# CraveAI Deployment Guide

This guide covers how to deploy the decoupled architecture of **CraveAI**:
- **Backend (FastAPI + Groq)** deployed on **Railway**
- **Frontend (Vanilla HTML/JS)** deployed on **Vercel**

---

## 1. Preparing the Codebase for Split Deployment

Currently, the backend serves the frontend statically on `localhost:8000`. To separate them, we need to update the frontend to point to the production API.

1. **Update the API URL in the Frontend:**
   Open `src/ui/static/index.html` and locate the `fetch` call inside the `form.addEventListener('submit', async (e) => { ... })` function.
   Change:
   ```javascript
   const response = await fetch('http://localhost:8000/recommendations', {
   ```
   To your future Railway domain (or leave it as localhost for now and update it after Step 2):
   ```javascript
   // Replace with your actual Railway domain later
   const response = await fetch('https://your-railway-app.up.railway.app/recommendations', {
   ```

2. **Commit and Push:**
   Commit this change to your `main` branch and push it to GitHub.

---

## 2. Deploying the Backend on Railway

Railway is excellent for Python/FastAPI backend apps. It automatically detects `requirements.txt` and starts a Python environment.

### Steps:
1. Go to [Railway.app](https://railway.app/) and log in with your GitHub account.
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select your `Zomato-Recommendation` repository.
4. **Add Variables:**
   Before the deployment finishes, go to the **Variables** tab for your service and add your API key:
   - `GROQ_API_KEY` = `your_actual_groq_api_key_here`
5. **Configure the Start Command:**
   By default, Railway might not know how to start the app. Go to the **Settings** tab of your service, find **Start Command**, and enter:
   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port $PORT
   ```
6. **Generate Domain:**
   In the **Settings** tab, go to **Networking** and click **Generate Domain**. 
   *Copy this domain URL (e.g., `https://craveai-production.up.railway.app`)* — you will need this for the frontend!

---

## 3. Deploying the Frontend on Vercel

Vercel is perfect for serving static HTML/JS files globally at the edge.

### Steps:
1. First, make sure you updated `src/ui/static/index.html` to point to the Railway URL you just generated!
2. Go to [Vercel.com](https://vercel.com/) and log in with your GitHub account.
3. Click **Add New...** -> **Project**.
4. Import your `Zomato-Recommendation` repository.
5. **Configure the Build Details:**
   Since Vercel serves the root directory by default, but our frontend is inside `src/ui/static`, you need to tell Vercel where the root directory is.
   - Open the **Root Directory** setting and select `src/ui/static`.
   - **Framework Preset**: Leave as `Other`
   - **Build Command**: Leave empty
   - **Install Command**: Leave empty
6. Click **Deploy**.

---

## 4. Final Security Check (CORS)

By default, the FastAPI app (`src/api/main.py`) has `allow_origins=["*"]` configured in CORS. This allows Vercel to communicate with Railway seamlessly. 

For strict production security, you can update `src/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-vercel-app-url.vercel.app"], # Restrict to Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

- **500 Internal Server Error:** Check the **Deploy Logs** on Railway. This almost always means the `GROQ_API_KEY` environment variable wasn't set properly in Railway.
- **Network / CORS Error in Browser:** Open your Browser DevTools (F12). If the API call fails, double-check that the URL in `index.html` exactly matches your Railway domain and uses `https://`.
