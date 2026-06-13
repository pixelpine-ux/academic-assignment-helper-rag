# Sentry Error Monitoring Setup

## What Sentry Does
- **Tracks errors**: Every crash, exception, and error in production
- **Stack traces**: See exactly what code failed and why
- **Performance monitoring**: Slow API endpoints, database queries
- **Release tracking**: Connect errors to specific deployments
- **Alerts**: Email/Slack when errors spike

## Setup (5 minutes)

### 1. Create Free Sentry Account
1. Go to https://sentry.io/signup/
2. Sign up with GitHub (easiest)
3. Choose **"Developer" plan** (FREE - 5K errors/month)

### 2. Create Project
1. Click "Create Project"
2. Select **"FastAPI"** as platform
3. Name it: `academic-rag-backend`
4. Copy your **DSN** (looks like: `https://abc123@o123.ingest.sentry.io/456`)

### 3. Add DSN to Environment
```bash
# In your .env file
SENTRY_DSN=https://your-actual-dsn-here@sentry.io/project-id
ENVIRONMENT=production  # or development
```

### 4. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Test It Works
```bash
# Start your backend
uvicorn main:app --reload

# In another terminal, trigger a test error:
curl http://localhost:8000/sentry-debug
```

Check Sentry dashboard - you should see the error appear!

## What Gets Tracked

### Automatic (No code changes needed)
- ✅ All unhandled exceptions
- ✅ HTTP errors (500, 404, etc.)
- ✅ Slow database queries
- ✅ API endpoint performance
- ✅ User IP, request headers, stack traces

### Example Error in Sentry Dashboard
```
PlagiarismCheckError: OpenAI API rate limit exceeded
  File "/app/api/plagiarism.py", line 45, in check_plagiarism
    embeddings = get_embeddings(text)
  File "/app/services/embeddings.py", line 23, in get_embeddings
    response = openai.Embedding.create(...)

User: user@example.com
Environment: production
Request: POST /api/plagiarism/check
Timestamp: 2024-01-15 14:23:11 UTC
```

## Sentry Features You Get (Free Tier)

| Feature | Free Limit | Enough For |
|---------|-----------|------------|
| Errors tracked | 5,000/month | ~170/day → plenty for MVP |
| Performance traces | 10,000/month | Track slow endpoints |
| Data retention | 30 days | Recent error history |
| Team members | Unlimited | Collaborate with others |
| Integrations | GitHub, Slack | Auto-link commits, alerts |

## Production Best Practices

### 1. Don't Track PII (Personally Identifiable Info)
```python
# Already configured - Sentry scrubs passwords, tokens, etc.
# But be careful with custom logging
```

### 2. Set Up Alerts
1. Go to Sentry → Alerts → Create Alert
2. Trigger: "Error rate increases by 50%"
3. Action: Send email

### 3. Link GitHub Commits
1. Sentry → Settings → Integrations → GitHub
2. Connect your repo
3. Now errors show which commit introduced the bug!

## Cost Breakdown

**Free forever if**:
- <5K errors/month (you won't hit this starting out)
- <10K performance traces/month

**If you exceed**:
- $26/month for Team plan (50K errors)
- But honestly, if you're hitting 5K errors/month, you have bigger problems 😅

## Disable Sentry for Local Dev

Sentry only runs if `SENTRY_DSN` is set:

```bash
# .env (local development)
# SENTRY_DSN=  # Leave commented/empty

# .env (production)
SENTRY_DSN=https://your-dsn@sentry.io/123
```

## Test Error Tracking

Add this endpoint to test (already in main.py):
```python
@app.get("/sentry-debug")
def trigger_error():
    division_by_zero = 1 / 0
```

Visit: `http://localhost:8000/sentry-debug`  
→ Check Sentry dashboard for the error!

## Useful Sentry Queries

### In Sentry Dashboard Search:
```
# All errors from specific user
user.email:user@example.com

# All database errors
transaction:/api/documents/*

# All 500 errors
http.status_code:500

# Errors in last hour
age:-1h
```

## Next Steps After Setup

1. ✅ Set up email alerts
2. ✅ Connect GitHub repo
3. ✅ Add teammates (if any)
4. ✅ Configure Slack notifications (optional)
5. ✅ Test in production deployment

---

**That's it!** Sentry is now silently watching your app and will email you when things break. 🎉
