# Analytics Agent

Upload **Excel** or **CSV** files (including exports from **Power BI**) and chat with an AI data analyst that answers questions about your data.

## Power BI & Excel

- **Excel**: `.xlsx` and `.xls` are supported directly (all sheets are loaded).
- **Power BI**: `.pbix` files are not parsed by this app. **Export your data from Power BI to Excel or CSV**, then upload that file:
  - In Power BI: **Transform data** → open your query → **Close & Apply**, then use **File → Export** (or copy to Excel) for the table you need.
  - Or use **Analyze in Excel** and save the workbook, then upload the `.xlsx` here.

## Quick start

### 1. Backend (Python)

```bash
cd "Analytics Agent/backend"
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...
uvicorn main:app --reload --port 8000
```

### 2. Frontend

```bash
cd "Analytics Agent/frontend"
npm install
npm run dev
```

Open **http://localhost:5173**. Create a session (automatic), upload an Excel or CSV file, then ask questions in the chat (e.g. “What are the top 5 rows?”, “Summarize the Sales column”, “How many rows?”).

### 3. Optional: different API URL

If the backend runs on another host/port, set in the frontend:

```bash
# .env or .env.local in frontend/
VITE_API_URL=http://localhost:8000
```

## Project layout

- **backend/** – FastAPI app: session, file upload, parser (Excel/CSV), in-memory store, data analyst agent (OpenAI).
- **frontend/** – Vite + React: upload dropzone, chat UI.

## Environment

| Variable        | Description |
|----------------|-------------|
| `OPENAI_API_KEY` | Required for the data analyst. Get a key from [OpenAI](https://platform.openai.com/api-keys). |
| `CORS_ORIGINS` | Comma-separated origins (default includes `http://localhost:5173`). |

## Sharing with testers (not on your network)

To let someone test the app over the internet, you can either **tunnel** your local app or **deploy** it.

### Option A: Quick share with ngrok (tunnel)

Your backend and frontend must both be reachable at public URLs. Use two tunnels (free at [ngrok.com](https://ngrok.com)).

1. **Start the app locally** (backend on port 8000, frontend on port 5173).

2. **Tunnel the backend**
   ```bash
   ngrok http 8000
   ```
   Note the HTTPS URL (e.g. `https://abc123.ngrok-free.app`).

3. **Point the frontend at the public backend**
   - In `frontend/.env.local` (or `.env`) set:
     ```bash
     VITE_API_URL=https://abc123.ngrok-free.app
     ```
   - Restart the frontend dev server (`npm run dev`).

4. **Tunnel the frontend**
   ```bash
   ngrok http 5173
   ```
   Note this URL (e.g. `https://def456.ngrok-free.app`).

5. **Allow that frontend URL in the backend**
   - In `backend/.env` add or set:
     ```bash
     CORS_ORIGINS=http://localhost:5173,https://def456.ngrok-free.app
     ```
   - Restart the backend.

6. **Share the frontend ngrok URL** (e.g. `https://def456.ngrok-free.app`) with your tester. They open it in a browser; upload and chat will use your backend tunnel. Your machine must stay on and both ngrok terminals must stay running.

**Note:** The free ngrok URL changes each time you restart ngrok. For a stable link, use Option B.

### Option B: Deploy (permanent link)

**Easiest path:** follow **[HOSTING.md](HOSTING.md)** — step-by-step Render (backend) + Vercel (frontend) with copy-paste values.

After deployment, share the frontend URL (e.g. `https://your-app.vercel.app`) with testers.

---

## Security note

The agent runs pandas expressions from the LLM in the backend. For production, restrict what can be executed (e.g. allowlist of operations, no file/system access) or run in a sandbox.
