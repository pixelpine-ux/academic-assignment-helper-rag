# Troubleshooting Guide - Assignment Management API

## Quick Diagnostics

### Check Container Status
```bash
docker ps | grep academic
```

Expected output:
```
academic_api    Up X minutes    0.0.0.0:8000->8000/tcp
academic_db     Up X minutes    0.0.0.0:5432->5432/tcp
academic_n8n    Up X minutes    0.0.0.0:5678->5678/tcp
```

### Test API Health
```bash
curl http://localhost:8000/
```

Expected: `{"message":"Academic Assignment Helper Backend is Running",...}`

---

## Common Issues

### Issue: Container Exits Immediately

**Symptoms:**
```bash
docker ps -a | grep academic_api
# Shows "Exited (0)" or "Exited (1)"
```

**Diagnosis:**
```bash
docker logs academic_api --tail 50
```

**Common Causes:**

1. **Missing Dependencies**
   - Look for: `ModuleNotFoundError: No module named 'X'`
   - Solution: Add to `requirements.txt` and rebuild
   ```bash
   docker-compose down
   docker-compose build --no-cache backend
   docker-compose up -d
   ```

2. **Database Connection Failed**
   - Look for: `password authentication failed`
   - Solution: Reset database volumes
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

3. **Syntax Errors**
   - Look for: `SyntaxError` or `ImportError`
   - Solution: Check recent code changes, fix syntax

---

### Issue: "Connection Reset by Peer"

**Symptoms:**
```bash
curl http://localhost:8000/
# curl: (56) Recv failure: Connection reset by peer
```

**Diagnosis:**
```bash
docker logs academic_api 2>&1 | tail -30
```

**Common Causes:**

1. **Application Crash on Startup**
   - Check logs for Python exceptions
   - Fix the error and restart

2. **Wrong Port**
   - Verify port mapping: `docker ps | grep 8000`
   - Check docker-compose.yml ports section

---

### Issue: Database Authentication Failed

**Error:**
```
sqlalchemy.exc.OperationalError: password authentication failed for user "postgres"
```

**Solution:**
```bash
# Remove old database volume
docker-compose down -v

# Start fresh
docker-compose up -d

# Wait for database to initialize
sleep 10

# Test
curl http://localhost:8000/health/db
```

---

### Issue: Pydantic Validation Errors

**Error:**
```
pydantic.errors.PydanticUserError: `regex` is removed. use `pattern` instead
```

**Solution:**
Update all Pydantic Field definitions:
```python
# Wrong (Pydantic v1)
Field(None, regex="pattern")

# Correct (Pydantic v2)
Field(None, pattern="pattern")
```

---

### Issue: Bcrypt Password Error

**Error:**
```
ValueError: password cannot be longer than 72 bytes
```

**Solution:**
Ensure bcrypt version is pinned in requirements.txt:
```
bcrypt==4.0.1
passlib==1.7.4
```

Then rebuild:
```bash
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

---

### Issue: Docker Compose KeyError

**Error:**
```
KeyError: 'ContainerConfig'
```

**Workaround:**
```bash
# Don't use single service rebuild
# docker-compose up -d --build backend  # ❌ Causes error

# Instead, use full rebuild
docker-compose down
docker-compose build backend
docker-compose up -d
```

---

### Issue: Network Not Found

**Error:**
```
could not translate host name "db" to address
```

**Solution:**
Ensure all containers are on the same network:
```bash
# Stop everything
docker-compose down

# Start with compose (creates network automatically)
docker-compose up -d

# Verify network
docker network ls | grep academic
```

---

## Recovery Procedures

### Full Reset (Nuclear Option)
```bash
# Stop and remove everything
docker-compose down -v

# Remove images
docker rmi academic-assignment-helper-rag_backend

# Rebuild from scratch
docker-compose build --no-cache

# Start fresh
docker-compose up -d

# Wait for startup
sleep 15

# Test
curl http://localhost:8000/
```

### Rebuild Backend Only
```bash
docker-compose down
docker-compose build backend
docker-compose up -d
```

### Reset Database Only
```bash
docker-compose down -v
docker-compose up -d
```

---

## Debugging Commands

### View Real-time Logs
```bash
docker-compose logs -f backend
```

### Execute Commands in Container
```bash
docker exec -it academic_api bash
```

### Check Environment Variables
```bash
docker exec academic_api env | grep DATABASE
```

### Test Database Connection
```bash
docker exec academic_db psql -U postgres -d academic_rag -c "SELECT 1;"
```

### Check Network Configuration
```bash
docker network inspect academic-assignment-helper-rag_default
```

---

## Performance Issues

### Slow API Response

**Check:**
1. Database connection pool
2. Query performance
3. Container resources

**Solution:**
```bash
# Check container stats
docker stats academic_api

# Increase resources in docker-compose.yml if needed
```

### High Memory Usage

**Check:**
```bash
docker stats
```

**Solution:**
- Add memory limits in docker-compose.yml
- Optimize database queries
- Review application code for memory leaks

---

## Prevention Checklist

Before deploying changes:
- [ ] Pin all dependency versions
- [ ] Test in clean environment
- [ ] Check logs for warnings
- [ ] Verify all endpoints work
- [ ] Test authentication flow
- [ ] Backup database if needed
- [ ] Document any configuration changes

---

## Getting Help

1. Check logs first: `docker logs academic_api`
2. Review this troubleshooting guide
3. Check GitHub issues for similar problems
4. Verify environment variables in `.env`
5. Test with minimal configuration
6. Document the issue with logs and steps to reproduce
