# Easiest setup: Render + Vercel

**No coding experience?** Use **[HOSTING_BEGINNER.md](HOSTING_BEGINNER.md)** — same steps explained in plain language, with no jargon.

Do these in order. You need: GitHub repo with this project, OpenAI API key.

---

## A. Get the code on GitHub

If it’s not there yet:

1. Create a new repo on [github.com](https://github.com/new) (e.g. `analytics-agent`).
2. In Terminal:

```bash
cd "/Users/jonathanrivera/Desktop/Apps/Analytics Agent"
git init
git add .
git commit -m "Analytics Agent"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` and `YOUR_REPO` with your GitHub username and repo name.

---

## B. Render (backend)

1. Go to **[render.com](https://render.com)** → sign in (or sign up with GitHub).
2. **New +** → **Web Service**.
3. Connect GitHub and select the repo you pushed.
4. Fill in:

| Field | Value |
|-------|--------|
| **Name** | `analytics-agent-api` |
| **Root Directory** | `backend` (if repo root is the `Analytics Agent` folder) **or** `Analytics Agent/backend` (if repo root is the parent of `Analytics Agent`) |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

5. **Environment** → **Add Environment Variable**:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** your OpenAI API key (from [platform.openai.com/api-keys](https://platform.openai.com/api-keys))
6. **Create Web Service**. Wait until status is **Live**.
7. Copy the service URL (e.g. `https://analytics-agent-api.onrender.com`) → **save as BACKEND URL**.

---

## C. Vercel (frontend)

1. Go to **[vercel.com](https://vercel.com)** → sign in (or sign up with GitHub).
2. **Add New…** → **Project**.
3. Import the **same** GitHub repo.
4. Fill in:

| Field | Value |
|-------|--------|
| **Root Directory** | `frontend` (if repo root is `Analytics Agent`) **or** `Analytics Agent/frontend` (if repo root is parent of `Analytics Agent`) |
| **Environment Variable** | Name: `VITE_API_URL` → Value: **BACKEND URL** from step B (no `/` at the end) |

5. **Deploy**. Wait until it’s done.
6. Copy the project URL (e.g. `https://analytics-agent-xxx.vercel.app`) → **save as FRONTEND URL**.

---

## D. Allow frontend in backend (CORS)

1. In **Render** → open your `analytics-agent-api` service.
2. **Environment** → **Add Environment Variable**:
   - **Key:** `CORS_ORIGINS`
   - **Value:** **FRONTEND URL** from step C (e.g. `https://analytics-agent-xxx.vercel.app`)
3. **Save Changes**. Wait for redeploy (~1 min).

---

## Done

**Link to send users:** your **FRONTEND URL** (from step C).

Example: `https://analytics-agent-xxx.vercel.app`

---

**Root Directory reminder**

- Repo = only the `Analytics Agent` folder → use `backend` and `frontend`.
- Repo = something like `Apps` or `MyProjects` that *contains* `Analytics Agent` → use `Analytics Agent/backend` and `Analytics Agent/frontend`.
