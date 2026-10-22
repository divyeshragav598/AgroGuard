# AgroGuard AI — Student Prototype

A beginner-friendly HTML/CSS/JavaScript frontend with a Python Flask API. The verification engine uses **fictional records only** to demonstrate three outcomes:

- `match`: submitted fields match a fictional record.
- `mismatch`: at least one submitted field conflicts with a fictional record.
- `insufficient_evidence`: a record or required information is missing.

A match is **not** real-world product approval, a crop diagnosis, or treatment advice. Do not add real pesticide instructions without a verified, maintained, authoritative data source and qualified review.

## Folder structure

```text
AgroGuardAI/
├── docs/
│   ├── index.html
│   ├── style.css
│   └── script.js
├── backend/
│   ├── app.py
│   ├── rules.json
│   └── requirements.txt
└── README.md
```

## 1. Run the backend locally

Install Python 3.10 or newer. Open a terminal in the `AgroGuardAI/backend` folder.

Windows:

```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, you can use the environment's Python directly:

```powershell
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python app.py
```

The API should run at `http://127.0.0.1:5000`.

Test the health endpoint by opening `http://127.0.0.1:5000/api/health` in your browser. Expected response:

```json
{"service":"AgroGuard AI demo API","status":"ok"}
```

## 2. Connect the frontend to your local backend

Open `docs/script.js`. Change:

```js
const API_BASE = "https://YOUR-RENDER-SERVICE.onrender.com";
```

to:

```js
const API_BASE = "http://127.0.0.1:5000";
```

Open `docs/index.html` in your browser, or use the VS Code Live Server extension. Use Live Server if possible.

## 3. Try the three result states

### Match example
- Crop: Tomato
- Stage: Vegetative growth
- Suspected problem: Possible early blight
- Product ID: `DEMO-TOMATO-01`
- Reference ID: `DEMO-REF-001`

Expected: `match`.

### Mismatch example
Use the match example, but change suspected problem to `Possible aphids`.

Expected: `mismatch`.

### Insufficient evidence example
- Product ID: `UNKNOWN-ITEM-99`

Expected: `insufficient_evidence`.

You can also choose `Not sure` for the growth stage or suspected problem to test uncertainty handling.

## 4. Push the project to GitHub

Create a new GitHub repository, for example `AgroGuardAI`.

From the project root:

```bash
git init
git add .
git commit -m "Build AgroGuard AI prototype"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/AgroGuardAI.git
git push -u origin main
```

Replace `YOUR-USERNAME` with your GitHub username. Do not paste passwords or access tokens into source code.

## 5. Deploy the backend on Render

1. Sign in to Render and create a **New Web Service**.
2. Connect your GitHub repository.
3. Set the **Root Directory** to `backend`.
4. Set **Build Command** to `pip install -r requirements.txt`.
5. Set **Start Command** to `gunicorn app:app`.
6. Choose a suitable free or low-cost instance if available to your account and deploy.
7. After deployment, open `https://YOUR-SERVICE.onrender.com/api/health`.
8. Copy your actual Render service URL.

Render may change its free-tier availability or limits. If a free service sleeps, its first request can take a little time.

## 6. Deploy the frontend on GitHub Pages

This project stores the static website in `docs/`, which GitHub Pages can publish directly.

1. Open your GitHub repository's **Settings → Pages**.
2. Under build and deployment, select **Deploy from a branch**.
3. Select branch `main` and folder `/docs`.
4. Click **Save** and wait for the deployment to finish.
5. Your website URL will be shown on the Pages settings screen.

### Important: point the frontend to Render

In `docs/script.js`, replace the placeholder API URL with your actual Render service URL, for example:

```js
const API_BASE = "https://your-real-service-name.onrender.com";
```

Commit and push the change. Do not include a trailing slash.

The backend currently allows cross-origin requests to make the student demo easy to test. Before public production use, restrict CORS to your actual GitHub Pages origin and add appropriate request limits and monitoring.

## 7. Common problems

- **CORS error:** confirm the backend is deployed and the API URL is correct. The provided Flask app enables CORS for `/api/*`.
- **404 at `/api/health`:** check Render's root directory is `backend` and start command is `gunicorn app:app`.
- **Module not found:** activate the virtual environment and run `pip install -r requirements.txt`.
- **Frontend says it cannot connect:** test `/api/health` first, then update `API_BASE`.
- **JSON error:** ensure `rules.json` remains in the same folder as `app.py`.
- **GitHub Pages shows a 404:** check Pages deployment status and whether it is publishing the correct folder.

## Next development steps

1. Replace fictional records only after finding current, authoritative agricultural sources.
2. Have an agricultural expert review the data and verification rules.
3. Track source title, publisher, publication/update date, jurisdiction, and expiry/review date.
4. Keep "not found" and "conflicting evidence" distinct from "safe".
5. Add image screening only as a separate uncertain signal; never let a model prediction alone approve a treatment.
