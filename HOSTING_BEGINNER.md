# Get a link to share your chatbot (no coding experience needed)

This guide gets your Analytics Agent chatbot on the internet so you can send one link to anyone. You’ll use three free websites: **GitHub** (to store your project), **Render** (to run the “brain” of the app), and **Vercel** (to show the upload and chat page). You only need to follow the steps and type or paste where it says.

---

## What you need before you start

1. **Your Analytics Agent project** on your computer (the folder with `backend` and `frontend` inside it).
2. **A GitHub account** (free). If you don’t have one: go to [github.com](https://github.com), click **Sign up**, and create an account.
3. **An OpenAI API key** (so the chatbot can answer questions). If you don’t have one: go to [platform.openai.com/api-keys](https://platform.openai.com/api-keys), sign in, click **Create new secret key**, copy the key, and save it somewhere safe (you’ll paste it later).

---

## Part 1: Put your project on GitHub

**Why:** Render and Vercel need to see your project. They can only see it if it’s on GitHub.

### Step 1.1: Create a new “repo” on GitHub

1. Open your web browser and go to: **https://github.com/new**
2. If GitHub asks you to sign in, sign in.
3. You’ll see a page “Create a new repository.”
4. In the box **Repository name**, type something like: `analytics-agent` (no spaces).
5. Leave everything else as it is. Click the green **Create repository** button at the bottom.
6. After the page loads, you’ll see a URL at the top that looks like: `https://github.com/YOUR_USERNAME/analytics-agent`  
   **Write down or copy YOUR_USERNAME** (that’s your GitHub username). You’ll need it in the next step.

### Step 1.2: Upload your project from your computer to GitHub

You’ll use an app called **Terminal** (Mac) or **Command Prompt** (Windows). It’s a window where you type short commands; you can copy-paste the lines below.

**On Mac:**

1. Open **Terminal**: press the **Command** key and the **Space** key, type **Terminal**, then press **Enter**.
2. Copy this line exactly (including the quotes), paste it into Terminal, and press **Enter**:
   ```text
   cd "/Users/jonathanrivera/Desktop/Apps/Analytics Agent"
   ```
3. Then copy and paste these lines **one at a time**, pressing **Enter** after each:
   ```text
   git init
   ```
   ```text
   git add .
   ```
   ```text
   git commit -m "Analytics Agent"
   ```
4. Now you need to connect to *your* GitHub repo. Copy the next line, but **replace YOUR_USERNAME** with your real GitHub username and **YOUR_REPO** with the repo name you used (e.g. `analytics-agent`):
   ```text
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   ```
   Example: if your username is `jane` and your repo is `analytics-agent`, the line would be:
   ```text
   git remote add origin https://github.com/jane/analytics-agent.git
   ```
5. Paste that line into Terminal and press **Enter**.
6. Paste this and press **Enter**:
   ```text
   git branch -M main
   ```
7. Paste this and press **Enter**:
   ```text
   git push -u origin main
   ```
   If it asks for your GitHub username and password, use your username and a **Personal Access Token** (not your normal password). To create one: GitHub → your profile picture → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)** → **Generate new token**. Give it a name, check **repo**, generate, then copy the token and use it as the password when Terminal asks.

When it finishes without errors, your project is on GitHub. You can close Terminal.

---

## Part 2: Set up Render (the “brain” of your app)

**Why:** Render will run the part that reads Excel/CSV files and talks to OpenAI. It will give you a **backend URL** (a link that the chat page will use behind the scenes).

### Step 2.1: Create a Render account and start a new service

1. Go to: **https://render.com**
2. Click **Get Started** (or **Sign In** if you already have an account).
3. Choose **Sign up with GitHub** and follow the steps so Render can see your GitHub account.
4. Once you’re in the Render dashboard, click the **New +** button (top right), then click **Web Service**.

### Step 2.2: Connect your GitHub project

1. You’ll see “Create a new Web Service.” Under **Connect a repository**, you should see GitHub. If it says “Connect account,” connect GitHub and allow Render to see your repos.
2. In the list of repositories, find the one you created (e.g. `analytics-agent`) and click **Connect** next to it.

### Step 2.3: Fill in the settings

You’ll see a form. Fill it in like this (you can copy-paste the values that are in quotes):

| What you see on the page | What to enter |
|--------------------------|----------------|
| **Name** | `analytics-agent-api` |
| **Region** | Leave as is (e.g. Oregon). |
| **Branch** | `main` (usually already set). |
| **Root Directory** | This tells Render which folder has the server code. Click **Edit** next to it. If your GitHub repo contains *only* the Analytics Agent project (only the folder with `backend` and `frontend` inside), type: `backend` . If your repo is a *bigger* folder and “Analytics Agent” is *inside* it, type: `Analytics Agent/backend` . Then click **Continue**. |
| **Runtime** | **Python 3** (choose from the dropdown). |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

### Step 2.4: Add your OpenAI key (secret)

1. Scroll down to the **Environment** section.
2. Click **Add Environment Variable**.
3. In **Key**, type exactly: `OPENAI_API_KEY`
4. In **Value**, paste the OpenAI API key you saved earlier (the one that starts with `sk-`).
5. Click **Create Web Service** at the bottom.

### Step 2.5: Wait and copy your backend URL

1. Render will build and start your app. Wait until the status at the top says **Live** (can take 1–2 minutes).
2. At the top of the page you’ll see a URL like: `https://analytics-agent-api.onrender.com`  
   **Copy that whole URL** and save it in a note or document. This is your **BACKEND URL**. You’ll paste it into Vercel in Part 3.

---

## Part 3: Set up Vercel (the page people will open)

**Why:** Vercel will host the upload and chat screen. It will give you a **frontend URL** — that’s the link you’ll send to people.

### Step 3.1: Create a Vercel account and start a new project

1. Go to: **https://vercel.com**
2. Click **Sign Up** or **Log In** and choose **Continue with GitHub** so Vercel can see your repos.
3. Once you’re in the Vercel dashboard, click **Add New…** and then **Project**.

### Step 3.2: Import the same GitHub repo

1. You’ll see a list of your GitHub repositories. Find the same repo you used for Render (e.g. `analytics-agent`) and click **Import** next to it.

### Step 3.3: Set the folder and the backend link

1. **Root Directory:** Click **Edit** next to it. You need to tell Vercel which folder has the chat/upload page.  
   - If your repo is *only* the Analytics Agent project, type: `frontend`  
   - If your repo is a *bigger* folder and “Analytics Agent” is *inside* it, type: `Analytics Agent/frontend`  
   Then click **Continue**.
2. **Environment Variables:** You need to tell the page where the “brain” (Render) lives.  
   - Click **Add** or **Add Environment Variable**.  
   - **Name:** type exactly: `VITE_API_URL`  
   - **Value:** paste the **BACKEND URL** you copied from Render (e.g. `https://analytics-agent-api.onrender.com`).  
   - Do **not** add a slash at the end.
3. Click **Deploy** at the bottom.

### Step 3.4: Wait and copy your frontend URL

1. Vercel will build and deploy. Wait until you see **Congratulations** or **Your project has been deployed** (usually 1–2 minutes).
2. You’ll see a URL like: `https://analytics-agent-xxx.vercel.app`  
   **Copy that whole URL** and save it. This is your **FRONTEND URL** — **this is the link you will send to people.**

---

## Part 4: Let the “brain” talk to the page (one more setting)

**Why:** By default, the server on Render won’t accept requests from your Vercel page. You fix that by adding one more “secret” on Render that says: “requests from my Vercel link are allowed.”

1. Go back to **Render** in your browser: **https://dashboard.render.com**
2. Click on your **analytics-agent-api** service (the one you created in Part 2).
3. In the left sidebar, click **Environment**.
4. Click **Add Environment Variable**.
5. **Key:** type exactly: `CORS_ORIGINS`
6. **Value:** paste your **FRONTEND URL** from Part 3 (e.g. `https://analytics-agent-xxx.vercel.app`).
7. Click **Save Changes**. Render will redeploy; wait about 1 minute.

---

## You’re done

**The link you send to anyone is your FRONTEND URL** (the Vercel link from Part 3).

Example: `https://analytics-agent-xxx.vercel.app`

When they open that link, they’ll see the upload and chat screen. They can upload an Excel or CSV file and ask questions; your app (on Render) and your OpenAI key will do the rest.

---

## Quick reminder: which Root Directory?

- **“My GitHub repo is only the Analytics Agent folder”**  
  → On Render use: `backend`  
  → On Vercel use: `frontend`

- **“My GitHub repo is a bigger folder and Analytics Agent is inside it”**  
  → On Render use: `Analytics Agent/backend`  
  → On Vercel use: `Analytics Agent/frontend`

---

## If something doesn’t work

- **Render says “Build failed”:** Check that Root Directory is correct and that the **Start Command** is exactly: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Vercel build fails:** Check that Root Directory is correct and that you added `VITE_API_URL` with your Render URL (no slash at the end).
- **Chat doesn’t answer / “Could not reach API”:** Make sure you did Part 4 (CORS). Wait a minute after saving and try again. Also check that `OPENAI_API_KEY` is set on Render and that your OpenAI account has credits.
