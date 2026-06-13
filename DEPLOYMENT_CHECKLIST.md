# Production Deployment Checklist

## ✅ Pre-Deployment (You're Here)

### Backend Ready
- [x] FastAPI with JWT authentication
- [x] PostgreSQL + pgvector integration
- [x] Rate limiting (Redis-backed)
- [x] CORS configuration
- [x] File upload handling (PDF, DOCX, TXT)
- [x] RAG query system
- [x] Plagiarism detection
- [x] User profile management
- [x] Sentry error monitoring integration
- [x] Health check endpoints

### Frontend Ready
- [x] React 19 + Vite 8
- [x] Authentication (login/register)
- [x] Document upload interface
- [x] Chat interface (RAG queries)
- [x] Assignments management
- [x] Plagiarism checker UI
- [x] User profile page
- [x] Responsive design
- [x] Loading states
- [x] Error handling

### Missing (Optional for MVP)
- [ ] Async file processing (can add later)
- [ ] Query result caching (add when costs matter)
- [ ] Email notifications (nice to have)

---

## 🚀 Deployment Steps (Render.com - FREE)

### Step 1: Sign Up for Services (15 min)

#### Sentry (Error Monitoring)
1. ✅ Go to https://sentry.io/signup/
2. ✅ Sign up with GitHub
3. ✅ Create project: "academic-rag-backend"
4. ✅ Copy your DSN
5. ✅ Follow [SENTRY_SETUP.md](SENTRY_SETUP.md)

#### Render.com (Hosting)
1. ✅ Go to https://render.com
2. ✅ Sign up with GitHub (no credit card needed)
3. ✅ Connect your GitHub repository

---

### Step 2: Deploy Database (5 min)

1. ✅ Render Dashboard → New → PostgreSQL
2. ✅ Name: `academic-rag-db`
3. ✅ Plan: **Free**
4. ✅ PostgreSQL Version: **16**
5. ✅ Click "Create Database"
6. ✅ Wait for provisioning (~2 min)
7. ✅ Go to Shell tab, run: `CREATE EXTENSION vector;`
8. ✅ Copy "Internal Database URL"

---

### Step 3: Deploy Redis (2 min)

1. ✅ Render Dashboard → New → Redis
2. ✅ Name: `academic-rag-redis`
3. ✅ Plan: **Free**
4. ✅ Click "Create Redis"
5. ✅ Copy "Internal Redis URL"

---

### Step 4: Deploy Backend (10 min)

1. ✅ Render Dashboard → New → Web Service
2. ✅ Connect GitHub repo
3. ✅ Configuration:
   - Name: `academic-rag-backend`
   - Root Directory: `backend`
   - Environment: `Python 3`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Plan: **Free**

4. ✅ Environment Variables (click "Add Environment Variable"):
   ```
   DATABASE_URL = <paste PostgreSQL Internal URL>
   REDIS_URL = <paste Redis Internal URL>
   OPENAI_API_KEY = sk-your-actual-key
   SECRET_KEY = <generate random 32+ char string>
   SENTRY_DSN = <your Sentry DSN>
   ENVIRONMENT = production
   ALGORITHM = HS256
   ACCESS_TOKEN_EXPIRE_MINUTES = 30
   ```

5. ✅ Click "Create Web Service"
6. ✅ Wait for deployment (~3-5 min)
7. ✅ Copy your backend URL (e.g., `https://academic-rag-backend.onrender.com`)
8. ✅ Test: Visit `https://your-backend-url.onrender.com/docs`

---

### Step 5: Deploy Frontend (5 min)

1. ✅ Render Dashboard → New → Static Site
2. ✅ Connect same GitHub repo
3. ✅ Configuration:
   - Name: `academic-rag-frontend`
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `dist`
   - Plan: **Free**

4. ✅ Environment Variable:
   ```
   VITE_API_URL = <your backend URL from Step 4>
   ```

5. ✅ Click "Create Static Site"
6. ✅ Wait for deployment (~2-3 min)
7. ✅ Copy your frontend URL (e.g., `https://academic-rag.onrender.com`)

---

### Step 6: Configure CORS (2 min)

1. ✅ Update backend environment variables on Render:
   ```
   FRONTEND_URL = <your frontend URL from Step 5>
   ```

2. ✅ Render will auto-redeploy backend

---

### Step 7: Test Everything (10 min)

Visit your frontend URL and test:

- [x] **Registration**: Create a new account
- [x] **Login**: Sign in with credentials
- [x] **Document Upload**: Upload a PDF/DOCX
- [x] **RAG Query**: Ask a question about the document
- [x] **Plagiarism Check**: Run plagiarism detection
- [x] **Create Assignment**: Add a test assignment
- [x] **User Profile**: View profile and stats
- [x] **Password Change**: Update password

---

## 🐛 Troubleshooting

### Backend won't start
- **Check logs** in Render dashboard
- **Verify env vars** are set correctly
- **Test locally**: `docker-compose up` should work first

### "CORS error" in browser
- **Add frontend URL** to backend CORS settings
- **Check FRONTEND_URL** env var is set
- **Restart backend** service

### "Database connection failed"
- **Verify DATABASE_URL** is the Internal URL (not External)
- **Check pgvector extension**: Run `CREATE EXTENSION vector;` in DB shell

### "Rate limit exceeded immediately"
- **Check REDIS_URL** is set correctly
- **Verify Redis is running** (check Render Redis dashboard)

### Cold starts (first load slow)
- **Expected behavior** on free tier
- First request after 15 min takes ~30 seconds
- **Solution**: Use UptimeRobot to ping every 14 min (keeps it warm)

---

## 📊 Monitoring

### Sentry Dashboard
- Check for errors: https://sentry.io/
- Set up email alerts for critical errors
- Connect GitHub for commit tracking

### Render Dashboard
- Monitor service status
- Check logs for warnings
- View deployment history

---

## 🎉 You're Live!

**Backend**: https://your-backend.onrender.com/docs  
**Frontend**: https://your-frontend.onrender.com  
**Status**: Production-ready MVP

### Share your app:
- Add to portfolio
- Share with friends/colleagues
- Test with real users
- Collect feedback

---

## 🔄 Future Upgrades (When You Have Budget)

### When you hit free tier limits:
1. **Railway** ($5-10/month)
   - No cold starts
   - Persistent database (no 90-day limit)
   
2. **DigitalOcean** ($20/month)
   - Full VPS control
   - Better performance
   
3. **AWS** ($30-50/month)
   - Production-grade
   - Scales infinitely

### Features to add next:
- [ ] Async file processing (BackgroundTasks or Celery)
- [ ] Redis caching layer (for query results)
- [ ] Email notifications (SendGrid free tier)
- [ ] User avatars (Cloudinary free tier)
- [ ] Export assignments to PDF

---

## 📝 Post-Deployment

- [x] Test all features in production
- [ ] Set up Sentry alerts
- [ ] Create backup script for database (before 90-day expiration)
- [ ] Monitor OpenAI API costs
- [ ] Collect user feedback
- [ ] Plan next features

---

**Total Cost: $0/month**  
**Total Time: ~45 minutes**  
**Status: Production-Ready ✅**

Need help? Check the troubleshooting section or reach out! 🚀
