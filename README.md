# Multi-Chain Wallet Scanner

Automated private key scanner with web interface. Scans Ethereum and BNB wallets for balances.

## Features

- ✅ **Web Interface** - Modern dashboard with real-time updates
- ✅ **Sequential & Random Scanning** - Scan specific ranges or random keys
- ✅ **Database Tracking** - SQLite database tracks all searched keys
- ✅ **Fast Performance** - 100-200 wallets/minute with paid Alchemy RPCs
- ✅ **Private Key Display** - See all searched private keys with balances
- ✅ **Ethereum & BNB Only** - Focused on ETH and BNB balances

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the web interface:**
   ```bash
   python app.py
   ```
   Or double-click: `start_web.bat`

3. **Open browser:**
   Navigate to: **http://localhost:5000**

## Usage

### Web Interface

1. **Select scan mode:**
   - **Random Scan**: Generate random private keys
   - **Sequential Range Scan**: Scan a specific range

2. **Configure settings:**
   - **Delay**: 0.01s for 100-200/min (or 0 for max speed)
   - **Max Keys**: Optional limit

3. **Set range (Sequential mode):**
   - Start Key: `0x0000000000000000000000000000000000000000000000000000000000000000`
   - End Key: `0x9999999999999999999999999999999999999999999999999999999999999999`

4. **Start scanning** and watch real-time progress

## Configuration

### RPC Endpoints

Currently using paid Alchemy endpoints (configured in `config.py`):
- Ethereum: `https://eth-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC`
- BNB: `https://bnb-mainnet.g.alchemy.com/v2/8Ld0inzc-YClnrhCRRMaC`

To change endpoints, edit `config.py` or create `.env` file.

## File Structure

```
.
├── app.py                 # Flask web application
├── web_scanner.py         # Scanner engine
├── sequential_generator.py # Sequential key generator
├── key_generator.py       # Random key generator
├── balance_checker.py     # Balance checking (Ethereum & BNB)
├── database.py            # SQLite database
├── config.py              # Configuration
├── templates/             # Web interface HTML
├── static/                # CSS and JavaScript
├── requirements.txt       # Dependencies
└── wallet_scanner.db     # Database (auto-created)
```

## Performance

- **Speed**: 100-200 wallets/minute (with 0.01s delay)
- **Chains**: Ethereum (ETH) and BNB only
- **Parallel**: Checks both chains simultaneously
- **Database**: Tracks all searched keys (no duplicates)

## Security Notes

⚠️ **IMPORTANT:**
- Never share your private keys
- Keep `wallet_scanner.db` secure (contains private keys)
- Use on secure, trusted machines only

## License

Use at your own risk. Educational purposes only.
