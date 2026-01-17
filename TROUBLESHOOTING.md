# Troubleshooting Guide

## Common Issues and Solutions

### "Network Error" When Uploading Files

**Symptoms**: Getting "Network Error" or "Upload failed" when trying to upload CSV files

**Possible Causes:**

1. **Backend server is not running**
   - Check if backend is accessible: http://localhost:8000/docs
   - If you see a page, backend is running
   - If you see "connection refused" or nothing, backend is not running

2. **Wrong API URL**
   - Frontend tries to connect to `http://localhost:8000` by default
   - If backend is on a different port/host, you need to set `VITE_API_URL`

3. **CORS issues**
   - Backend allows `http://localhost:5173` by default
   - If frontend is on different port, check CORS settings

**Solutions:**

#### If using Docker:
```bash
# Check if services are running
docker-compose ps

# Check backend logs
docker-compose logs backend

# Restart services
docker-compose restart backend frontend

# Or rebuild
docker-compose down
docker-compose up --build
```

#### If running manually:

**Check backend is running:**
```bash
# Backend should be on port 8000
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# Or check in browser
# Open: http://localhost:8000/docs
```

**Check frontend API URL:**
```bash
# In frontend directory, check environment
cd frontend
echo $VITE_API_URL
# Should be: http://localhost:8000 (or empty for default)
```

**Fix API URL:**
```bash
# If backend is on different port/host
export VITE_API_URL=http://localhost:8000
npm run dev
```

#### Quick Debug Steps:

1. **Test backend directly:**
   ```bash
   curl http://localhost:8000/health
   ```
   If this fails, backend is not running.

2. **Check browser console:**
   - Open browser Developer Tools (F12)
   - Go to Network tab
   - Try uploading file again
   - Check what URL it's trying to reach
   - Look for failed requests (usually red)

3. **Check browser console errors:**
   - Open Developer Tools (F12)
   - Go to Console tab
   - Look for errors like:
     - "Failed to fetch"
     - "Network request failed"
     - "CORS policy"
     - "Connection refused"

---

### "Could not determine file type from filename"

**Cause**: Filename doesn't contain required keywords

**Solution**: Rename your file to include one of:
- `gl` or `pnl` for P&L files (e.g., `gl_pnl_monthly.csv`)
- `payroll` or `pay` for payroll files (e.g., `payroll_summary.csv`)
- `vendor` or `spend` for vendor files (e.g., `vendor_spend.csv`)
- `revenue` or `segment` for revenue files (e.g., `revenue_by_segment.csv`)

---

### Backend Won't Start

**Check database connection:**
```bash
# If using Docker
docker-compose logs db
docker-compose logs backend

# If running manually
# Check PostgreSQL is running and accessible
psql -h localhost -U ai_consultant -d ai_consultant_db
```

**Check environment variables:**
```bash
# Backend needs these
echo $DATABASE_URL
echo $OPENAI_API_KEY
```

**Common issues:**
- Database not running
- Wrong DATABASE_URL
- Database not initialized

**Fix:**
```bash
# Reinitialize database
python -c "from app.storage.database import init_db; init_db()"
```

---

### Frontend Won't Start

**Check Node.js:**
```bash
node --version  # Should be 20+
npm --version
```

**Reinstall dependencies:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Check port conflicts:**
```bash
# Check if port 5173 is in use
lsof -i :5173  # macOS/Linux
netstat -ano | findstr :5173  # Windows
```

---

### Database Connection Errors

**Symptoms**: Backend logs show "could not connect to server"

**Solutions:**

1. **If using Docker:**
   ```bash
   # Restart database
   docker-compose restart db
   
   # Check database logs
   docker-compose logs db
   ```

2. **If using local PostgreSQL:**
   ```bash
   # Check PostgreSQL is running
   sudo systemctl status postgresql  # Linux
   brew services list | grep postgres  # macOS
   
   # Restart PostgreSQL
   sudo systemctl restart postgresql  # Linux
   brew services restart postgresql  # macOS
   ```

3. **Check connection string:**
   ```bash
   # Should be:
   # postgresql://ai_consultant:ai_consultant_password@localhost:5432/ai_consultant_db
   echo $DATABASE_URL
   ```

---

### OpenAI API Errors

**Symptoms**: "LLM API error" or initiatives not generating

**Check API key:**
```bash
# Should be set in .env file
cat .env | grep OPENAI_API_KEY

# Or environment variable
echo $OPENAI_API_KEY
```

**Verify API key works:**
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Common issues:**
- API key not set
- Invalid API key
- No API credits
- Rate limiting

**Fix:**
1. Get valid API key from https://platform.openai.com/api-keys
2. Add to `.env` file: `OPENAI_API_KEY=sk-your-key-here`
3. Restart backend

---

## Debug Checklist

When something doesn't work, check:

- [ ] Docker Desktop is running (if using Docker)
- [ ] All services are up: `docker-compose ps` shows all "Up"
- [ ] Backend is accessible: http://localhost:8000/health
- [ ] Frontend is accessible: http://localhost:5173
- [ ] Browser console shows no errors (F12 → Console)
- [ ] Network tab shows backend requests (F12 → Network)
- [ ] Environment variables are set (`.env` file exists)
- [ ] API key is valid (OpenAI dashboard)
- [ ] Database is running and accessible
- [ ] File names contain required keywords
- [ ] CSV files have correct format (check sample_data/)

---

## Getting More Help

1. **Check logs:**
   ```bash
   # Docker logs
   docker-compose logs backend
   docker-compose logs frontend
   docker-compose logs db
   
   # Or follow logs in real-time
   docker-compose logs -f backend
   ```

2. **Check API documentation:**
   - Open http://localhost:8000/docs
   - Try the `/health` endpoint
   - Try the `/ingest/upload` endpoint manually

3. **Verify setup:**
   - Read [SETUP.md](SETUP.md) for setup instructions
   - Read [QUICKSTART.md](QUICKSTART.md) for quick start guide
   - Check [CSV_FORMAT_GUIDE.md](CSV_FORMAT_GUIDE.md) for CSV format requirements
