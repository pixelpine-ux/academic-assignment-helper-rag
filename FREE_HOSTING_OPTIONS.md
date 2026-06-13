# Free Hosting Options ($0/month)

## 🎯 Best Options for Your Stack

Your app needs:
- FastAPI backend (Python)
- PostgreSQL database with pgvector
- Redis (for rate limiting)
- React frontend
- File uploads (PDFs, docs)

---

## Option 1: Render.com ⭐ **RECOMMENDED**

### What You Get (FREE)
- ✅ Web service (FastAPI backend)
- ✅ PostgreSQL database with pgvector support
- ✅ Redis instance
- ✅ Static site (React frontend)
- ✅ HTTPS automatic
- ✅ Auto-deploy from GitHub

### Limitations
- Backend spins down after 15 min inactivity (cold start ~30 seconds)
- 750 hours/month free (enough for one service always-on OR multiple services with downtime)
- PostgreSQL: 90 day expiration (must recreate - but free again)
- 100GB bandwidth/month

### Setup Time: ~20 minutes

### Step-by-Step

#### 1. Sign up
- Go to https://render.com
- Sign up with GitHub (free, no credit card)

#### 2. Create PostgreSQL Database
- Dashboard → New → PostgreSQL
- Name: `academic-rag-db`
- Plan: **Free**
- PostgreSQL version: **16** (for pgvector)
- Click "Create Database"
- **Copy the Internal Database URL** (looks like: `postgresql://user:pass@...`)

#### 3. Enable pgvector Extension
- Once DB is created, go to Shell tab
- Run: `CREATE EXTENSION vector;`

#### 4. Create Redis Instance
- Dashboard → New → Redis
- Name: `academic-rag-redis`
- Plan: **Free**
- Click "Create Redis"
- **Copy the Internal Redis URL**

#### 5. Deploy Backend
- Dashboard → New → Web Service
- Connect your GitHub repo
- Settings:
  - **Name**: `academic-rag-backend`
  - **Root Directory**: `backend`
  - **Environment**: `Python 3`
  - **Build Command**: `pip install -r requirements.txt`
  - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - **Plan**: **Free**

- Add Environment Variables:
  ```
  DATABASE_URL=<paste PostgreSQL internal URL>
  REDIS_URL=<paste Redis internal URL>
  OPENAI_API_KEY=sk-your-key
  SECRET_KEY=generate-random-string-here
  SENTRY_DSN=<your sentry DSN>
  ENVIRONMENT=production
  ```

#### 6. Deploy Frontend
- Dashboard → New → Static Site
- Connect your GitHub repo
- Settings:
  - **Name**: `academic-rag-frontend`
  - **Root Directory**: `frontend`
  - **Build Command**: `npm install && npm run build`
  - **Publish Directory**: `dist`
  - **Plan**: **Free**

- Add Environment Variable:
  ```
  VITE_API_URL=<your backend URL from step 5>
  ```

### Pros
- ✅ Everything you need in one place
- ✅ PostgreSQL with pgvector works out of the box
- ✅ Auto HTTPS + custom domains
- ✅ GitHub auto-deploy
- ✅ No credit card needed

### Cons
- ⚠️ Cold starts (first request after 15 min takes ~30s)
- ⚠️ Database expires after 90 days (must backup & recreate)

---

## Option 2: Railway ⚡ (With Free Credits)

### What You Get
- $5 free credit/month (hobby projects stay under this)
- All services (backend, DB, Redis, frontend)
- NO COLD STARTS (big advantage)
- PostgreSQL persists forever

### Setup
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# In your project directory
railway init
railway up
```

### Limitations
- Credit card required (but won't charge if under $5/month)
- Light usage = free, heavy usage = paid

### Best for
- If you hate cold starts
- If you want persistent PostgreSQL

---

## Option 3: Koyeb (New Player)

### What You Get (FREE)
- 1 web service (backend)
- PostgreSQL addon (free)
- No cold starts on first service
- HTTPS + custom domains

### Setup
- Sign up: https://koyeb.com
- Deploy from Docker or GitHub
- Select "Nano" instance (free)

### Limitations
- No free Redis (you'd need Upstash free tier separately)
- Smaller community

---

## Option 4: Fly.io + Free Tier Services

### What You Get (FREE)
- 3 shared VMs (1GB RAM each)
- 3GB persistent storage
- PostgreSQL via Supabase (free tier)
- Redis via Upstash (free tier)

### Setup Complexity: Medium
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Deploy backend
flyctl launch
flyctl deploy

# Deploy frontend separately or use Vercel
```

### Pros
- ✅ No cold starts
- ✅ More control
- ✅ Generous free tier

### Cons
- ⚠️ Requires credit card
- ⚠️ More complex setup (multiple services)

---

## Option 5: PythonAnywhere (Backend Only)

### What You Get (FREE)
- Python web app hosting
- No cold starts
- Always-on (no sleep)

### Limitations
- ❌ No PostgreSQL with pgvector (only MySQL/SQLite)
- ❌ No Redis
- ❌ Not suitable for your stack

**Verdict**: Skip this, doesn't support your needs.

---

## Option 6: Free Tier Combo (Advanced)

Mix and match free tiers:

| Service | Provider | Limit |
|---------|----------|-------|
| Backend | Render.com | 750h/month |
| PostgreSQL | Supabase.com | 500MB, 2GB transfer |
| Redis | Upstash.com | 10K commands/day |
| Frontend | Vercel.com | Unlimited |
| File Storage | Cloudflare R2 | 10GB free |

### Pros
- ✅ Best of each service
- ✅ More permanent (no 90-day DB expiration)
- ✅ Can scale individual pieces

### Cons
- ⚠️ More complex to set up
- ⚠️ Managing 4-5 different platforms

---

## My Recommendation for You ($0 Budget)

### **Start with Render.com** (Option 1)

**Why**:
1. **Zero cost, zero credit card**
2. Everything in one place (less to manage)
3. pgvector support out of the box
4. Setup in 20 minutes
5. Perfect for portfolio/demo

**Accept these trade-offs**:
- First request after 15 min is slow (cold start)
- Database resets after 90 days (export data, recreate)

**When it works**:
- Building portfolio
- Showing to potential employers/users
- Low traffic testing
- MVP validation

**When to upgrade** (later, when you have money):
- Consistent traffic (cold starts annoy users)
- Need persistent database >90 days
- → Move to Railway ($5/month) or AWS/DigitalOcean

---

## Quick Setup Checklist (Render.com)

```
□ Sign up at render.com (no credit card)
□ Create PostgreSQL database (free)
□ Enable pgvector extension
□ Create Redis instance (free)
□ Deploy backend web service (free)
  - Set environment variables (DATABASE_URL, REDIS_URL, etc.)
  - Set start command: uvicorn main:app --host 0.0.0.0 --port $PORT
□ Deploy frontend static site (free)
  - Set VITE_API_URL to backend URL
□ Test: Upload a document, ask a question
□ Done! ✅
```

**Total cost: $0/month**  
**Total time: 20-30 minutes**

---

## Avoiding Cold Starts (Free)

### Option A: Keep It Warm
Use a free uptime monitor to ping your backend every 14 minutes:

- **UptimeRobot.com** (free)
  - Monitor your backend URL
  - Check interval: 14 minutes
  - Prevents it from sleeping

### Option B: Accept It
- Tell users: "First load may take 30 seconds (free hosting)"
- Most users understand

---

## When You Have Money (Future)

**Best upgrade path**:
1. **Railway** ($5-10/month) → No cold starts, persistent DB
2. **DigitalOcean** ($20/month) → Full VPS control
3. **AWS** ($30-50/month) → Production-grade

But for now? **Render.com is perfect for $0.**

---

## Need Help?

**Render.com docs**: https://render.com/docs  
**Render community**: https://community.render.com

**Common issues**:
- **pgvector not found**: Run `CREATE EXTENSION vector;` in DB shell
- **Backend won't start**: Check logs for missing env vars
- **CORS errors**: Add frontend URL to backend CORS settings

---

**Let me know which option you choose, happy to help with deployment!** 🚀
