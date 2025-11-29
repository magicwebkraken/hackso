# How to Run the Wallet Scanner

## Quick Start (Easiest Method)

### Option 1: Double-Click (Windows)
1. **Double-click** `start_web.bat`
2. Wait for the server to start
3. Open your browser to: **http://localhost:5000**

### Option 2: Command Line

1. **Open Command Prompt or PowerShell**
2. **Navigate to the project folder:**
   ```bash
   cd "E:\coin trading bot\Private bot"
   ```

3. **Install dependencies (first time only):**
   ```bash
   python -m pip install -r requirements.txt
   ```
   Or double-click `install.bat`

4. **Start the web server:**
   ```bash
   python app.py
   ```

5. **Open your browser:**
   - Go to: **http://localhost:5000**
   - The web interface will load automatically

## Step-by-Step Instructions

### First Time Setup

1. **Make sure Python is installed:**
   - Check by running: `python --version`
   - Should show Python 3.x

2. **Install dependencies:**
   ```bash
   python -m pip install -r requirements.txt
   ```
   Or double-click `install.bat`

3. **Start the server:**
   ```bash
   python app.py
   ```

4. **You should see:**
   ```
   ============================================================
   Wallet Scanner Web Interface
   ============================================================
   Starting server on http://localhost:5000
   Press Ctrl+C to stop
   ============================================================
   ```

5. **Open browser:**
   - Go to: **http://localhost:5000**
   - The dashboard will appear

### Using the Interface

1. **Select scan mode:**
   - Random Scan (default)
   - Sequential Range Scan

2. **Configure settings:**
   - Delay: 0.01s (for 100-200 wallets/min)
   - Max Keys: Optional limit

3. **For Sequential mode:**
   - Start Key: `0x0000000000000000000000000000000000000000000000000000000000000000`
   - End Key: `0x9999999999999999999999999999999999999999999999999999999999999999`

4. **Click "Start Scanning"**

5. **Watch the progress:**
   - Real-time statistics
   - Current private key being checked
   - Searched keys list
   - Wallets with balance

### Stopping the Server

- Press `Ctrl+C` in the terminal
- Or close the terminal window

## Troubleshooting

### "Python not found"
- Make sure Python is installed
- Try `python3` instead of `python`
- Add Python to your system PATH

### "Module not found"
- Run: `python -m pip install -r requirements.txt`
- Or double-click `install.bat`

### "Port 5000 already in use"
- Close other applications using port 5000
- Or edit `app.py` and change `port=5000` to another port (e.g., `port=5001`)

### "Can't connect to RPC"
- Check your internet connection
- The Alchemy endpoints are configured in `config.py`
- Make sure the API keys are correct

## Files You Need

- `app.py` - Main web application
- `requirements.txt` - Dependencies
- `start_web.bat` - Quick start script (Windows)
- `install.bat` - Install dependencies (Windows)

## What Happens When You Run

1. Server starts on port 5000
2. Database is created automatically (`wallet_scanner.db`)
3. Web interface is accessible at http://localhost:5000
4. You can start scanning immediately

## Next Steps

After starting:
1. Open http://localhost:5000 in your browser
2. Configure your scan settings
3. Click "Start Scanning"
4. Monitor progress in real-time
5. View all searched private keys and balances

That's it! The scanner is ready to use.

