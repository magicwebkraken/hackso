# How to Set Environment Variables in Vercel

## Step-by-Step Guide

### Method 1: Using Vercel Dashboard (Recommended)

#### Step 1: Access Your Project
1. Go to [https://vercel.com](https://vercel.com)
2. **Log in** to your Vercel account
3. Click on your **project name** (e.g., "hackso" or your project name)
4. You should see your project dashboard

#### Step 2: Navigate to Settings
1. Click on the **"Settings"** tab at the top of the page
   - It's usually next to "Deployments", "Analytics", etc.
2. In the left sidebar, click on **"Environment Variables"**
   - You'll see a section titled "Environment Variables"

#### Step 3: Add Environment Variables
For each variable, follow these steps:

1. **Click the "Add New" button** or **"Add" button**
2. You'll see a form with three fields:
   - **Key**: The variable name
   - **Value**: The variable value
   - **Environment**: Where to apply it (Production, Preview, Development)

3. **Add each variable one by one:**

   **Variable 1: ETHEREUM_RPC**
   - **Key**: `ETHEREUM_RPC`
   - **Value**: `https://eth-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC`
   - **Environment**: Select all three (Production, Preview, Development) ✓
   - Click **"Save"**

   **Variable 2: BSC_RPC**
   - **Key**: `BSC_RPC`
   - **Value**: `https://bnb-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC`
   - **Environment**: Select all three (Production, Preview, Development) ✓
   - Click **"Save"**

   **Variable 3: DATABASE_PATH**
   - **Key**: `DATABASE_PATH`
   - **Value**: `/tmp/wallet_scanner.db`
   - **Environment**: Select all three (Production, Preview, Development) ✓
   - Click **"Save"**

   **Variable 4: DOMAIN (Optional)**
   - **Key**: `DOMAIN`
   - **Value**: `hackso.vercel.app` (or your actual domain)
   - **Environment**: Select all three ✓
   - Click **"Save"**

   **Variable 5: ALLOWED_HOSTS (Optional)**
   - **Key**: `ALLOWED_HOSTS`
   - **Value**: `hackso.vercel.app,localhost,127.0.0.1`
   - **Environment**: Select all three ✓
   - Click **"Save"**

   **Variable 6: CORS_ORIGINS (Optional)**
   - **Key**: `CORS_ORIGINS`
   - **Value**: `*` (or your specific domain like `https://hackso.vercel.app`)
   - **Environment**: Select all three ✓
   - Click **"Save"**

   **Variable 7: DEBUG (Optional)**
   - **Key**: `DEBUG`
   - **Value**: `False`
   - **Environment**: Select all three ✓
   - Click **"Save"**

   **Variable 8: SECRET_KEY (Optional but Recommended)**
   - **Key**: `SECRET_KEY`
   - **Value**: Generate a random string (see below)
   - **Environment**: Select all three ✓
   - Click **"Save"**

#### Step 4: Generate SECRET_KEY (Optional)
If you want to set a SECRET_KEY:

**Option A: Using Python**
```bash
python -c "import secrets; print(secrets.token_hex(24))"
```

**Option B: Using Node.js**
```bash
node -e "console.log(require('crypto').randomBytes(24).toString('hex'))"
```

**Option C: Online Generator**
- Go to https://randomkeygen.com/
- Copy a "CodeIgniter Encryption Keys" value
- Use that as your SECRET_KEY

#### Step 5: Redeploy Your Project
After adding all environment variables:

1. Go to the **"Deployments"** tab
2. Find your latest deployment
3. Click the **three dots (⋯)** menu
4. Click **"Redeploy"**
5. Confirm the redeploy

**OR**

1. Make a small change to your code (add a comment)
2. Push to GitHub (if connected)
3. Vercel will auto-deploy with new environment variables

---

### Method 2: Using Vercel CLI

#### Step 1: Install Vercel CLI
```bash
npm install -g vercel
```

#### Step 2: Login
```bash
vercel login
```

#### Step 3: Link Your Project
```bash
vercel link
```

#### Step 4: Add Environment Variables
```bash
# Add each variable
vercel env add ETHEREUM_RPC
# When prompted, paste: https://eth-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC
# Select environments: Production, Preview, Development

vercel env add BSC_RPC
# When prompted, paste: https://bnb-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC
# Select environments: Production, Preview, Development

vercel env add DATABASE_PATH
# When prompted, paste: /tmp/wallet_scanner.db
# Select environments: Production, Preview, Development
```

#### Step 5: Pull Environment Variables (Optional)
```bash
vercel env pull .env.local
```

---

## Complete List of Environment Variables

Here's a complete list you can copy-paste:

### Required Variables:
```
ETHEREUM_RPC=https://eth-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC
BSC_RPC=https://bnb-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC
DATABASE_PATH=/tmp/wallet_scanner.db
```

### Optional but Recommended:
```
DOMAIN=hackso.vercel.app
ALLOWED_HOSTS=hackso.vercel.app,localhost,127.0.0.1
CORS_ORIGINS=*
DEBUG=False
SECRET_KEY=your_generated_secret_key_here
```

---

## Visual Guide (What You'll See)

### Environment Variables Page Layout:
```
┌─────────────────────────────────────────────────────────┐
│  Settings > Environment Variables                       │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Environment Variables                                  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Key: ETHEREUM_RPC                                │  │
│  │ Value: https://eth-mainnet.g.alchemy.com/v2/... │  │
│  │ Environment: ☑ Production ☑ Preview ☑ Development│  │
│  │                    [Save] [Cancel]               │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  [Add New]                                              │
│                                                         │
│  Existing Variables:                                    │
│  • ETHEREUM_RPC (Production, Preview, Development)     │
│  • BSC_RPC (Production, Preview, Development)         │
│  • DATABASE_PATH (Production, Preview, Development)     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Important Notes

### 1. Environment Selection
- **Production**: Used for your live site (hackso.vercel.app)
- **Preview**: Used for preview deployments (pull requests)
- **Development**: Used for local development with `vercel dev`

**Recommendation**: Select all three for consistency.

### 2. Variable Visibility
- Environment variables are **encrypted** and **hidden** in the dashboard
- They're only visible when you click "Edit"
- Never share your environment variables publicly

### 3. After Adding Variables
- **You must redeploy** for changes to take effect
- Existing deployments won't have the new variables
- New deployments will automatically include them

### 4. Variable Names
- Use **UPPERCASE** with underscores (e.g., `ETHEREUM_RPC`)
- No spaces allowed
- Case-sensitive

### 5. Special Characters
- Most special characters work in values
- If you have issues, try wrapping in quotes (though usually not needed)

---

## Troubleshooting

### Variables Not Working?
1. **Check spelling**: Variable names are case-sensitive
2. **Redeploy**: Make sure you redeployed after adding variables
3. **Check environment**: Ensure variables are set for the right environment
4. **Check logs**: Go to Deployments → Click deployment → View Function Logs

### How to Verify Variables Are Set?
1. Go to Settings → Environment Variables
2. You should see all your variables listed
3. Click on a variable to see/edit its value

### Variables Not Showing in Code?
- Make sure you're accessing them with `os.getenv('VARIABLE_NAME')`
- Restart/redeploy after adding variables
- Check that variable names match exactly

---

## Quick Checklist

- [ ] Logged into Vercel
- [ ] Opened project settings
- [ ] Navigated to Environment Variables
- [ ] Added ETHEREUM_RPC
- [ ] Added BSC_RPC
- [ ] Added DATABASE_PATH
- [ ] Selected all environments (Production, Preview, Development)
- [ ] Saved each variable
- [ ] Redeployed the project
- [ ] Tested the application

---

## Need Help?

If you're still having issues:
1. Check Vercel logs: Deployments → Your deployment → Function Logs
2. Verify variables are set: Settings → Environment Variables
3. Make sure you redeployed after adding variables
4. Check the Vercel documentation: https://vercel.com/docs/concepts/projects/environment-variables

