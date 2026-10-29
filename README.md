# Big Tic-Tac-Toe — Vercel + Render

Web adaptation of `big_tictactoe_gui.py`. Frontend: Vite/vanilla JavaScript; backend: Flask Python. Minimax/alpha-beta search remains on the Python server. No database required.

## 1. Run locally

Open two terminals from this project folder.

**Backend**
```bash
cd backend
python -m pip install -r requirements.txt
python app.py
```

**Frontend**
```bash
cd frontend
npm install
cp .env.example .env  # Windows PowerShell: Copy-Item .env.example .env
npm run dev
```
Open the local URL printed by Vite (typically `http://localhost:5173`).

## 2. Push to GitHub

Create a new GitHub repository, then push this **entire** extracted folder. Keep the `frontend` and `backend` folders separate.

## 3. Deploy Python backend on Render

1. Render dashboard → **New** → **Web Service** → connect the GitHub repository.
2. **Language / Runtime:** Python.
3. **Root Directory:** `backend`
4. **Build Command:** `pip install -r requirements.txt`
5. **Start Command:** `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Deploy. Copy your actual Render service URL, e.g. `https://YOUR-SERVICE.onrender.com`.
7. Verify `https://YOUR-SERVICE.onrender.com/api/health` returns `{"status":"ok"}`.

## 4. Deploy frontend on Vercel

1. Vercel dashboard → **Add New Project** → import the same GitHub repository.
2. **Root Directory:** `frontend`.
3. **Framework Preset:** Vite (or Other if not detected).
4. **Build Command:** `npm run build`.
5. **Output Directory:** `dist`.
6. **Environment Variable:** `VITE_API_URL` = your **actual** Render URL (without `/api` and without trailing slash).
7. Deploy. Open your Vercel URL to play.

**Important:** If you change `VITE_API_URL`, redeploy Vercel. Render's free instances may take time to wake up. The backend currently allows cross-origin API requests from any origin; for a production app, restrict Flask-CORS to your Vercel domain.

## Endpoints

- `GET /api/health`: status check.
- `POST /api/move`: body `{"board":["X", "", ...],"n":5,"k":4,"level":"Medium"}`. Board length must equal `n*n` and contain one more X than O.

## Notes

- Board sizes 4–7; win length 3–7 (clamped to board size).
- AI depth Easy=1, Medium=2, Hard=3; 6×6 and 7×7 cap search depth at 2, as in the original.
- Each game runs entirely in the browser except for AI move calculations. No user accounts or database.
