# How to Fix "Network Error"

A "Network Error" means the frontend can't connect to the backend API. Here's how to diagnose and fix it:

## Quick Checks

### 1. Is the Backend Running?

**Check if backend is accessible:**
- Open: http://localhost:8000/docs
- Or: http://localhost:8000/health

**If you see a page:** ✅ Backend is running  
**If you see "connection refused" or nothing:** ❌ Backend is not running

### 2. Check Browser Developer Tools

1. Open browser Developer Tools (Press F12)
2. Go to **Console** tab
3. Look for errors like:
   - "Failed to fetch"
   - "Network request failed"
   - "ERR_CONNECTION_REFUSED"
   - CORS errors

4. Go to **Network** tab
5. Try uploading a file again
6. Look for the `/ingest/upload` request:
   - Is it red/failed?
   - What's the exact error?
   - What URL is it trying to reach?

### 3. Check Service Status (Docker)

If using Docker:

```bash
# Check all services are running
docker-compose ps

# You should see:
# - ai-consultant-db-1     Up
# - ai-consultant-backend-1  Up  
# - ai-consultant-frontend-1  Up
```

**If services are down:**
```bash
# Start services
docker-compose up -d

# Or rebuild if needed
docker-compose up --build
```

### 4. Check Backend Logs

```bash
# View backend logs
docker-compose logs backend

# Or follow logs in real-time
docker-compose logs -f backend
```

Look for errors like:
- Database connection errors
- Import errors
- Port already in use

### 5. Check API URL Configuration

The frontend needs to know where the backend is:

**Default:** `http://localhost:8000`

**If backend is on different port/host:**

1. Create `.env` file in `frontend/` directory:
   ```env
   VITE_API_URL=http://localhost:8000
   ```

2. Or set environment variable:
   ```bash
   export VITE_API_URL=http://localhost:8000
   npm run dev
   ```

**If using Docker:**
- The `docker-compose.yml` sets `VITE_API_URL: http://localhost:8000`
- This should work if services are on same host

### 6. Check CORS Settings

The backend must allow requests from the frontend URL.

**Default CORS allows:**
- `http://localhost:5173` (frontend default port)
- `http://localhost:3000`

**If frontend is on different port:**
- Check `backend/app/core/config.py`
- Add your frontend URL to `cors_origins` list

## Step-by-Step Fix

### Fix 1: Start Services

**If using Docker:**
```bash
cd /Users/sidkancharapu/AI-Consultant
docker-compose up --build
```

**If running manually:**
```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
uvicorn app.api.main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend
npm run dev
```

### Fix 2: Verify Backend is Accessible

```bash
# Test backend health endpoint
curl http://localhost:8000/health

# Should return: {"status": "healthy"}
```

### Fix 3: Check Browser Console

1. Open http://localhost:5173 in browser
2. Press F12 to open Developer Tools
3. Go to Console tab
4. Look for any errors
5. Try uploading a file
6. Check Network tab for failed requests

### Fix 4: Test Backend API Directly

```bash
# Test if upload endpoint exists
curl -X POST http://localhost:8000/ingest/upload \
  -F "files=@sample_data/gl_pnl_monthly.csv"

# Or check API docs
# Open: http://localhost:8000/docs
```

## Common Scenarios

### Scenario 1: "Connection Refused"

**Meaning:** Backend is not running or not accessible

**Fix:**
1. Start backend: `docker-compose up` or `uvicorn app.api.main:app --reload`
2. Check port 8000 is not blocked
3. Check firewall settings

### Scenario 2: CORS Error

**Meaning:** Backend is rejecting requests from frontend

**Fix:**
1. Check `backend/app/core/config.py`
2. Ensure frontend URL is in `cors_origins`
3. Restart backend after changes

### Scenario 3: "Failed to Fetch"

**Meaning:** Network request failed (could be CORS, connection, or server error)

**Fix:**
1. Check backend logs: `docker-compose logs backend`
2. Check browser Network tab for exact error
3. Verify API URL is correct

### Scenario 4: Timeout

**Meaning:** Request takes too long (usually database or LLM API issue)

**Fix:**
1. Check database is accessible
2. Check OpenAI API key is valid
3. Check backend logs for errors

## Still Not Working?

1. **Check all logs:**
   ```bash
   docker-compose logs
   ```

2. **Restart everything:**
   ```bash
   docker-compose down -v
   docker-compose up --build
   ```

3. **Try accessing backend directly:**
   - Open http://localhost:8000/docs in browser
   - Try the `/health` endpoint
   - Try the `/ingest/upload` endpoint manually

4. **Check environment variables:**
   ```bash
   # Backend needs these (if not using .env)
   echo $DATABASE_URL
   echo $OPENAI_API_KEY
   ```

5. **Verify file format:**
   - Check filename contains required keywords
   - Check CSV format matches sample data
   - Try uploading one of the sample files from `sample_data/`

## What I Changed

I've also fixed a potential issue where the frontend was manually setting `Content-Type: multipart/form-data` header, which can cause problems. Axios should set this automatically for FormData objects.

Try uploading again after making sure the backend is running!
