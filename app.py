"""
Flask Web Application for Wallet Scanner
"""
import os
import sys
from datetime import datetime

# Check for required dependencies
try:
    from flask import Flask, render_template, jsonify, request
    from flask_cors import CORS
except ImportError as e:
    print("ERROR: Missing required dependencies!")
    print(f"Please run: python -m pip install -r requirements.txt")
    print(f"Missing: {e}")
    sys.exit(1)

try:
    from web_scanner import WebScanner
except ImportError as e:
    print("ERROR: Could not import web_scanner!")
    print(f"Error: {e}")
    print("Please ensure all dependencies are installed:")
    print("python -m pip install -r requirements.txt")
    sys.exit(1)

app = Flask(__name__)

# Domain configuration
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
DOMAIN = os.getenv('DOMAIN', '')
SECRET_KEY = os.getenv('SECRET_KEY', os.urandom(24).hex())

# Configure CORS
cors_origins = os.getenv('CORS_ORIGINS', '*')
if cors_origins and cors_origins != '*':
    cors_origins = [origin.strip() for origin in cors_origins.split(',')]
    CORS(app, origins=cors_origins)
else:
    CORS(app)  # Allow all origins

# Security headers
@app.after_request
def after_request(response):
    """Add security headers"""
    if DOMAIN:
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Initialize scanner (lazy initialization for Vercel/serverless)
scanner = None

def get_scanner():
    """Lazy initialization of scanner for serverless compatibility"""
    global scanner
    if scanner is None:
        try:
            scanner = WebScanner()
        except Exception as e:
            print(f"WARNING: Could not initialize scanner: {e}")
            print("The web interface will start but scanning may not work.")
            scanner = None
    return scanner

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current scanning status and statistics"""
    scanner_instance = get_scanner()
    if scanner_instance is None:
        return jsonify({'error': 'Scanner not initialized'}), 500
    return jsonify(scanner_instance.get_status())

@app.route('/api/wallets')
def get_wallets():
    """Get all wallets with balance"""
    scanner_instance = get_scanner()
    if scanner_instance is None:
        return jsonify({'wallets': []})
    wallets = scanner_instance.get_wallets_with_balance()
    return jsonify({'wallets': wallets})

@app.route('/api/start', methods=['POST'])
def start_scanning():
    """Start scanning"""
    scanner_instance = get_scanner()
    if scanner_instance is None:
        return jsonify({'success': False, 'message': 'Scanner not initialized'}), 500
    
    data = request.get_json() or {}
    max_keys = data.get('max_keys')
    delay = data.get('delay', 0.1)
    mode = data.get('mode', 'random')  # 'random' or 'sequential'
    start_key = data.get('start_key')
    end_key = data.get('end_key')
    skip_searched = data.get('skip_searched', True)  # Default to True for backward compatibility
    
    if max_keys:
        max_keys = int(max_keys)
    
    try:
        success = scanner_instance.start_scanning(
            max_keys=max_keys, 
            delay=float(delay),
            mode=mode,
            start_key=start_key,
            end_key=end_key,
            skip_searched=skip_searched
        )
        
        return jsonify({
            'success': success,
            'message': 'Scanning started' if success else 'Already scanning'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error starting scan: {str(e)}'
        }), 400

@app.route('/api/stop', methods=['POST'])
def stop_scanning():
    """Stop scanning"""
    scanner_instance = get_scanner()
    if scanner_instance is None:
        return jsonify({'success': False, 'message': 'Scanner not initialized'}), 500
    scanner_instance.stop_scanning()
    return jsonify({'success': True, 'message': 'Scanning stopped'})

@app.route('/api/statistics')
def get_statistics():
    """Get database statistics"""
    scanner_instance = get_scanner()
    if scanner_instance is None:
        return jsonify({'error': 'Scanner not initialized'}), 500
    stats = scanner_instance.database.get_statistics()
    return jsonify(stats)

@app.route('/api/export')
def export_keys():
    """Export all searched private keys and addresses to text file"""
    scanner_instance = get_scanner()
    if scanner_instance is None:
        return jsonify({'error': 'Scanner not initialized'}), 500
    
    try:
        # Get all wallets from database
        all_wallets = scanner_instance.database.get_all_wallets()
        
        # Create export file
        filename = 'searched_keys_export.txt'
        filepath = os.path.join(os.getcwd(), filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("SEARCHED PRIVATE KEYS AND ADDRESSES EXPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Keys Searched: {len(all_wallets)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, wallet in enumerate(all_wallets, 1):
                f.write(f"#{i}\n")
                f.write(f"Private Key: {wallet['private_key']}\n")
                f.write(f"Address:     {wallet['address']}\n")
                f.write(f"Has Balance: {'Yes' if wallet['has_balance'] else 'No'}\n")
                if wallet['has_balance']:
                    f.write(f"Total Balance: {wallet['total_balance']:.6f}\n")
                f.write(f"Searched At: {wallet.get('searched_at', 'N/A')}\n")
                f.write("-" * 80 + "\n\n")
        
        return jsonify({
            'success': True,
            'message': f'Exported {len(all_wallets)} keys to {filename}',
            'filename': filename,
            'count': len(all_wallets)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/searched')
def get_searched():
    """Get list of recently searched wallets"""
    scanner_instance = get_scanner()
    if scanner_instance is None:
        return jsonify({'searched': []})
    
    # Get from scanner's recent searches
    recent = scanner_instance.get_recent_searches(limit=100)
    
    # Also get from database for older searches
    db_recent = scanner_instance.database.get_recent_searches(limit=100)
    
    # Combine and deduplicate
    seen_addresses = set()
    combined = []
    
    for item in recent:
        if item['address'] not in seen_addresses:
            combined.append(item)
            seen_addresses.add(item['address'])
    
    for item in db_recent:
        if item['address'] not in seen_addresses:
            combined.append({
                'private_key': item.get('private_key', ''),
                'address': item['address'],
                'has_balance': item['has_balance'],
                'total_balance': item['total_balance'],
                'timestamp': item.get('searched_at') or item.get('last_checked')
            })
            seen_addresses.add(item['address'])
    
    return jsonify({'searched': combined[:100]})

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Get configuration from environment
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    domain = os.getenv('DOMAIN', '')
    
    print("\n" + "="*60)
    print("Wallet Scanner Web Interface")
    print("="*60)
    if domain:
        print(f"Domain: {domain}")
        print(f"Access at: http://{domain}:{port}")
    else:
        print(f"Starting server on http://{host}:{port}")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")
    
    try:
        app.run(host=host, port=port, debug=debug, threaded=True)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")
    finally:
        scanner_instance = get_scanner()
        if scanner_instance:
            scanner_instance.close()

