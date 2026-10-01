# ⚡ Sparky Small — AI chatbot (web version)

A single-file AI chatbot with a browser chat UI, powered by OpenRouter.
Pure Python standard library — **zero dependencies, no build step**.

## Run locally

```bash
export OPENROUTER_API_KEY="sk-or-your-key"
python3 sparky_web.py
# open http://localhost:8000
```

## Deploy on Render.com (free)

1. Create a GitHub repo and push this folder's contents:
   ```bash
   git init && git add . && git commit -m "Sparky Small"
   git remote add origin https://github.com/YOUR-USER/sparky-small.git
   git push -u origin main
   ```
2. Go to [dashboard.render.com](https://dashboard.render.com) → **New** → **Web Service** → connect your repo.
3. Render detects `render.yaml` and configures everything automatically.
4. In the service's **Environment** tab, add:
   - `OPENROUTER_API_KEY` = your key from https://openrouter.ai/keys
5. Deploy. Render gives you a public URL like `https://sparky-small.onrender.com` — share it with your coworkers.

> **Note:** the free plan sleeps after 15 min of inactivity; the first visit after a
> nap takes ~30 seconds to wake up. That's normal.

## Configuration (environment variables)

| Variable | Default | Notes |
|---|---|---|
| `OPENROUTER_API_KEY` | — | **Required.** Keep it secret. |
| `SPARKY_MODEL` | `meta-llama/llama-3.3-70b-instruct` | Any model from openrouter.ai/models. Append `:free` for free-tier models. |
| `PORT` | `8000` | Set automatically by hosts like Render. |

## Cost & safety reminders

- Every chat message is billed (or rate-limited) against **your** OpenRouter key —
  set spend limits at https://openrouter.ai/settings/limits.
- Anyone with the URL can chat. For a wider audience, consider adding a password
  and/or switching to a `:free` model.
