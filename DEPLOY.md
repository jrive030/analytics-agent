# Set up a permanent URL for Analytics Agent

**Use the easiest guide:** **[HOSTING.md](HOSTING.md)** — Render (backend) + Vercel (frontend) with copy-paste steps and values.

---

## Notes

- **Render free tier:** The backend may sleep after ~15 minutes of no traffic. The first request after that can take 30–60 seconds to wake it; later requests are fast.
- **OpenAI:** Usage is billed to the OpenAI account whose key you set in the backend.
- **HTTPS:** Both Render and Vercel use HTTPS; the app will work over HTTPS only.
