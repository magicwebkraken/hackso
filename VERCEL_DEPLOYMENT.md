# Vercel Deployment Guide

## Important Note About Vercel

⚠️ **Vercel is a serverless platform** - it doesn't support long-running processes. The wallet scanner needs to run continuously, which has limitations on Vercel:

1. **Function Timeout**: Vercel functions have a 10-second timeout (Hobby) or 60 seconds (Pro)
2. **No Persistent State**: Each request may use a different serverless function instance
3. **Cold Starts**: Functions may need to initialize on each request

## Current Solution

The code has been updated to use **lazy initialization** to work better with Vercel, but there are still limitations:

- Scanning will work, but may be interrupted by function timeouts
- Database needs to be stored in a persistent location (not in `/tmp`)
- For production use, consider a VPS or dedicated server instead

## Deployment Steps

### 1. Install Vercel CLI

```bash
npm install -g vercel
```

### 2. Login to Vercel

```bash
vercel login
```

### 3. Deploy

```bash
# From your project directory
vercel
```

Or connect your GitHub repository to Vercel for automatic deployments.

### 4. Environment Variables

Set these in Vercel Dashboard → Settings → Environment Variables:

```
ETHEREUM_RPC=https://eth-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC
BSC_RPC=https://bnb-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC
DOMAIN=yourdomain.vercel.app
ALLOWED_HOSTS=yourdomain.vercel.app,localhost,127.0.0.1
CORS_ORIGINS=*
DEBUG=False
SECRET_KEY=your_random_secret_key
```

### 5. Database Storage

⚠️ **Important**: Vercel's filesystem is read-only except `/tmp`, which is cleared between deployments.

**Options:**

1. **Use External Database**: 
   - PostgreSQL (Vercel Postgres, Supabase, Railway)
   - MongoDB Atlas
   - Update `database.py` to use external DB

2. **Use Vercel Blob Storage** for database file

3. **Use `/tmp` directory** (data will be lost on cold starts)

### 6. Update Database Path (if using SQLite)

If you want to use SQLite on Vercel (not recommended for production), update the database path:

```python
# In web_scanner.py or database.py
db_file = os.getenv('DATABASE_PATH', '/tmp/wallet_scanner.db')
```

## Limitations

1. **Scanning Interruptions**: Long scans may timeout
2. **Cold Starts**: First request after inactivity may be slow
3. **State Persistence**: In-memory state may be lost between requests
4. **Database**: SQLite on serverless is not ideal

## Better Alternatives for Production

For a production wallet scanner that needs to run continuously:

1. **VPS/Cloud Server** (DigitalOcean, Linode, AWS EC2)
   - Full control, persistent processes
   - See `DEPLOYMENT.md` for instructions

2. **Railway** or **Render**
   - Better for long-running processes
   - Persistent storage support

3. **Hybrid Approach**
   - Frontend on Vercel
   - Backend API on VPS/Railway
   - Update API endpoints in frontend

## Troubleshooting

### "Scanner not initialized" Error

- Check that all dependencies are in `requirements.txt`
- Verify environment variables are set
- Check Vercel function logs

### Database Errors

- SQLite may not work well on Vercel
- Consider using external database
- Or use `/tmp` directory (temporary)

### Timeout Errors

- Vercel Hobby plan: 10-second timeout
- Upgrade to Pro for 60-second timeout
- Or use external service for scanning

## Quick Fix for Current Error

The "Scanner not initialized" error should be fixed with the lazy initialization. After deploying:

1. Check Vercel logs: `vercel logs`
2. Verify environment variables are set
3. Test the `/api/status` endpoint

If issues persist, the scanner may need to be refactored to use external services or a different deployment platform.

