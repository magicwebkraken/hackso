# Vercel CSS and Static Files Fix

## Issues Fixed

1. **CSS Not Loading**: Updated HTML to use absolute paths instead of `url_for()`
2. **Static Files Routing**: Updated `vercel.json` to properly route static files
3. **Flask Static Serving**: Added explicit route handler for static files

## Changes Made

### 1. HTML Template (`templates/index.html`)
- Changed from: `{{ url_for('static', filename='style.css') }}`
- Changed to: `/static/style.css`
- Changed from: `{{ url_for('static', filename='script.js') }}`
- Changed to: `/static/script.js`

### 2. Vercel Configuration (`vercel.json`)
- Simplified routing to ensure static files are served correctly
- Added proper rewrites for all routes

### 3. Flask App (`app.py`)
- Added explicit static file route handler
- Configured Flask with explicit static folder path

## Deployment Steps

1. **Commit and Push Changes**:
```bash
git add .
git commit -m "Fix CSS and static files for Vercel"
git push
```

2. **Redeploy on Vercel**:
   - Vercel will auto-deploy if connected to GitHub
   - Or manually trigger: Go to Vercel Dashboard → Deployments → Redeploy

3. **Verify**:
   - Check that CSS loads: View page source and click on `/static/style.css` link
   - Check browser console for any 404 errors
   - Verify JavaScript loads: Check Network tab in browser dev tools

## Troubleshooting

### If CSS Still Not Loading:

1. **Check Vercel Build Logs**:
   - Go to Vercel Dashboard → Your Project → Deployments
   - Click on latest deployment
   - Check "Build Logs" for errors

2. **Verify Static Files Are Deployed**:
   - Check that `static/` folder exists in your repository
   - Verify `static/style.css` and `static/script.js` are present

3. **Check Browser Console**:
   - Open browser dev tools (F12)
   - Go to Network tab
   - Reload page
   - Look for failed requests to `/static/style.css` or `/static/script.js`

4. **Clear Browser Cache**:
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear browser cache completely

### If Bot Still Not Running:

1. **Check Environment Variables**:
   - Verify all required variables are set in Vercel
   - See `VERCEL_ENV_SETUP.md` for details

2. **Check Function Logs**:
   - Go to Vercel Dashboard → Deployments → Latest → Function Logs
   - Look for "Scanner not initialized" or other errors

3. **Verify Database Path**:
   - Ensure `DATABASE_PATH=/tmp/wallet_scanner.db` is set
   - Check that database can be created in `/tmp`

## Expected Behavior After Fix

✅ CSS styles should load and apply correctly
✅ JavaScript should load and execute
✅ Scanner should initialize properly
✅ All API endpoints should work
✅ Static files should be served with proper caching headers

## Testing Locally

Before deploying, test locally:

```bash
python app.py
```

Then visit `http://localhost:5000` and verify:
- CSS loads correctly
- JavaScript executes
- Scanner initializes
- No console errors

