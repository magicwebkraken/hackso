// API Base URL
const API_BASE = '';

// State
let updateInterval = null;
let isScanning = false;

// DOM Elements
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const statusDot = statusIndicator.querySelector('.status-dot');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStatus();
    loadWallets();
    loadSearched();
    startAutoUpdate();
    
    startBtn.addEventListener('click', startScanning);
    stopBtn.addEventListener('click', stopScanning);
    
    const refreshBtn = document.getElementById('refreshSearched');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', loadSearched);
    }
    
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportKeys);
    }
    
    // Mode selector
    const modeRadios = document.querySelectorAll('input[name="scanMode"]');
    const sequentialSettings = document.getElementById('sequentialSettings');
    modeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'sequential') {
                sequentialSettings.style.display = 'block';
            } else {
                sequentialSettings.style.display = 'none';
            }
        });
    });
});

// API Functions
async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        return null;
    }
}

async function loadStatus() {
    const data = await fetchAPI('/api/status');
    if (!data) return;
    
    updateUI(data);
}

async function loadWallets() {
    const data = await fetchAPI('/api/wallets');
    if (!data || !data.wallets) return;
    
    displayWallets(data.wallets);
}

async function loadSearched() {
    const data = await fetchAPI('/api/searched');
    if (!data || !data.searched) return;
    
    displaySearched(data.searched);
}

function startAutoUpdate() {
    updateInterval = setInterval(() => {
        loadStatus();
        loadWallets();
        loadSearched();
    }, 2000); // Update every 2 seconds
}

// Control Functions
async function startScanning() {
    const delay = parseFloat(document.getElementById('delay').value) || 0.1;
    const maxKeys = document.getElementById('maxKeys').value;
    const mode = document.querySelector('input[name="scanMode"]:checked').value;
    const startKey = document.getElementById('startKey').value.trim();
    const endKey = document.getElementById('endKey').value.trim();
    const skipSearched = document.getElementById('skipSearched').checked;
    
    const requestData = {
        delay: delay,
        max_keys: maxKeys ? parseInt(maxKeys) : null,
        mode: mode,
        skip_searched: skipSearched
    };
    
    if (mode === 'sequential') {
        if (startKey) requestData.start_key = startKey;
        if (endKey) requestData.end_key = endKey;
    }
    
    const data = await fetchAPI('/api/start', {
        method: 'POST',
        body: JSON.stringify(requestData)
    });
    
    if (data && data.success) {
        isScanning = true;
        updateScanningState(true);
        const skipText = skipSearched ? 'skipping duplicates' : 'checking ALL keys';
        addActivity(`Scanning started (${mode} mode, ${skipText})`, 'success');
    } else if (data && data.message) {
        alert('Error: ' + data.message);
    }
}

async function stopScanning() {
    const data = await fetchAPI('/api/stop', {
        method: 'POST'
    });
    
    if (data && data.success) {
        isScanning = false;
        updateScanningState(false);
        addActivity('Scanning stopped');
    }
}

// UI Update Functions
function updateUI(data) {
    const stats = data.stats || {};
    
    // Update statistics
    document.getElementById('totalSearched').textContent = formatNumber(stats.total_searched || 0);
    document.getElementById('totalChecked').textContent = formatNumber(stats.checked || 0);
    document.getElementById('walletsWithBalance').textContent = formatNumber(stats.total_with_balance || 0);
    document.getElementById('totalBalance').textContent = formatBalance(stats.total_balance_found || 0);
    
    // Update scanning state
    updateScanningState(data.scanning || false);
    
    // Update progress with current address and private key
    updateProgress(stats, data.current_address, data.current_private_key);
    
    // Update sequential progress if in sequential mode
    if (data.sequential_progress) {
        updateSequentialProgress(data.sequential_progress);
    }
    
    // Check for new found wallet
    if (data.last_found) {
        showFoundAlert(data.last_found);
    }
}

function updateScanningState(scanning) {
    isScanning = scanning;
    
    if (scanning) {
        statusDot.classList.add('scanning');
        statusText.textContent = 'Scanning...';
        startBtn.disabled = true;
        stopBtn.disabled = false;
    } else {
        statusDot.classList.remove('scanning');
        statusText.textContent = 'Stopped';
        startBtn.disabled = false;
        stopBtn.disabled = true;
    }
}

function updateProgress(stats, currentAddress, currentPrivateKey) {
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    const currentAddrDiv = document.getElementById('currentAddress');
    const currentAddrText = document.getElementById('currentAddrText');
    const currentKeyText = document.getElementById('currentKeyText');
    
    const checked = stats.checked || 0;
    const skipped = stats.skipped || 0;
    const withBalance = stats.with_balance || 0;
    const total = stats.total_searched || 0;
    
    if (isScanning) {
        progressText.innerHTML = `<strong>Checked:</strong> ${formatNumber(checked)} | <strong>Skipped:</strong> ${formatNumber(skipped)} | <strong>Found:</strong> ${formatNumber(withBalance)}`;
        
        // Show current private key and address being checked
        if (currentAddress || currentPrivateKey) {
            if (currentPrivateKey) {
                currentKeyText.textContent = currentPrivateKey;
                currentKeyText.setAttribute('data-key', currentPrivateKey);
                currentKeyText.onclick = () => copyToClipboard(currentPrivateKey);
            }
            if (currentAddress) {
                currentAddrText.textContent = currentAddress;
                // Update explorer links
                const etherscanLink = document.getElementById('currentEtherscanLink');
                const bscscanLink = document.getElementById('currentBscscanLink');
                const addrLinks = document.getElementById('currentAddrLinks');
                if (etherscanLink && bscscanLink && addrLinks) {
                    etherscanLink.href = `https://etherscan.io/address/${currentAddress}`;
                    bscscanLink.href = `https://bscscan.com/address/${currentAddress}`;
                    addrLinks.style.display = 'flex';
                    addrLinks.style.flexDirection = 'row';
                }
            }
            currentAddrDiv.style.display = 'block';
        } else {
            currentAddrDiv.style.display = 'none';
        }
        
        // Calculate progress percentage (if max keys is set)
        // For now, just show a pulsing animation
        progressBar.style.width = '100%';
        progressBar.style.animation = 'pulse 2s infinite';
    } else {
        progressText.innerHTML = `<strong>Total searched:</strong> ${formatNumber(total)} | <strong>Wallets with balance:</strong> ${formatNumber(stats.total_with_balance || 0)}`;
        progressBar.style.width = '0%';
        progressBar.style.animation = 'none';
        currentAddrDiv.style.display = 'none';
    }
}

function displayWallets(wallets) {
    const walletsList = document.getElementById('walletsList');
    
    if (wallets.length === 0) {
        walletsList.innerHTML = '<p class="empty-state">No wallets with balance found yet. Start scanning to begin!</p>';
        return;
    }
    
    walletsList.innerHTML = wallets.map(wallet => {
        const balances = wallet.balances || [];
        const privateKey = wallet.private_key || 'N/A';
        const chainBadges = balances.map(bal => {
            const hasBalance = parseFloat(bal.balance_eth) > 0;
            return `
                <span class="chain-badge ${hasBalance ? 'has-balance' : ''}">
                    ${bal.chain.toUpperCase()}: ${formatBalance(bal.balance_eth)} ${bal.symbol}
                </span>
            `;
        }).join('');
        
        const privateKeyEscaped = privateKey.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
        return `
            <div class="wallet-item">
                <div class="wallet-header">
                    <div style="flex: 1;">
                        <div style="margin-bottom: 12px; padding: 12px; background: rgba(245, 158, 11, 0.1); border-radius: 6px; border-left: 3px solid var(--warning-color);">
                            <div style="margin-bottom: 6px;">
                                <strong style="color: var(--warning-color); font-size: 0.9rem;">🔑 PRIVATE KEY (Click to Copy):</strong>
                            </div>
                            <div>
                                <span class="private-key-text" style="font-family: monospace; cursor: pointer; color: var(--warning-color); font-size: 1rem; word-break: break-all; display: block;" 
                                      title="Click to copy" data-key="${privateKeyEscaped}">${privateKey}</span>
                            </div>
                        </div>
                        <div style="margin-top: 8px;">
                            <strong style="color: var(--primary-color);">Address:</strong>
                            <div style="display: flex; gap: 10px; margin-top: 5px; flex-wrap: wrap; align-items: center;">
                                <a href="https://etherscan.io/address/${wallet.address}" target="_blank" 
                                   class="explorer-link etherscan-link"
                                   title="View on Etherscan">
                                   🔍 Etherscan
                                </a>
                                <a href="https://bscscan.com/address/${wallet.address}" target="_blank" 
                                   class="explorer-link bscscan-link"
                                   title="View on BSCScan">
                                   🔍 BSCScan
                                </a>
                                <span class="wallet-address" style="font-family: monospace; color: var(--primary-color); word-break: break-all;">${wallet.address}</span>
                            </div>
                        </div>
                    </div>
                    <div class="wallet-balance">${formatBalance(wallet.total_balance)}</div>
                </div>
                <div class="wallet-chains">
                    ${chainBadges}
                </div>
                <div style="margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
                    Last checked: ${formatDate(wallet.last_checked)}
                </div>
            </div>
        `;
    }).join('');
    
    // Add click handlers for copy functionality
    walletsList.querySelectorAll('.private-key-text').forEach(el => {
        el.addEventListener('click', function() {
            const key = this.getAttribute('data-key');
            copyToClipboard(key);
        });
    });
}

function showFoundAlert(wallet) {
    const alert = document.getElementById('foundAlert');
    const info = document.getElementById('foundWalletInfo');
    
    info.innerHTML = `
        <p><strong>Address:</strong> <span style="font-family: monospace;">${wallet.address}</span></p>
        <p><strong>Private Key:</strong> <span style="font-family: monospace; color: var(--warning-color);">${wallet.private_key}</span></p>
        <p><strong>Total Balance:</strong> <span style="color: var(--success-color); font-size: 1.2rem; font-weight: bold;">${formatBalance(wallet.total_balance)}</span></p>
    `;
    
    alert.style.display = 'block';
    
    // Scroll to alert
    alert.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    
    // Auto-hide after 30 seconds
    setTimeout(() => {
        alert.style.display = 'none';
    }, 30000);
}

function addActivity(message, type = '') {
    const activityLog = document.getElementById('activityLog');
    
    if (activityLog.querySelector('.empty-state')) {
        activityLog.innerHTML = '';
    }
    
    const time = new Date().toLocaleTimeString();
    const item = document.createElement('div');
    item.className = `activity-item ${type}`;
    item.textContent = `[${time}] ${message}`;
    
    activityLog.insertBefore(item, activityLog.firstChild);
    
    // Keep only last 50 items
    while (activityLog.children.length > 50) {
        activityLog.removeChild(activityLog.lastChild);
    }
}

// Utility Functions
function formatNumber(num) {
    return new Intl.NumberFormat().format(num);
}

function formatBalance(balance) {
    return parseFloat(balance).toFixed(6);
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleString();
}

function formatTimestamp(timestamp) {
    if (!timestamp) return 'N/A';
    // Handle both timestamp (number) and date string
    const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp);
    return date.toLocaleString();
}

function displaySearched(searched) {
    const searchedList = document.getElementById('searchedList');
    
    if (!searched || searched.length === 0) {
        searchedList.innerHTML = '<p class="empty-state">No keys searched yet. Start scanning to see progress!</p>';
        return;
    }
    
    searchedList.innerHTML = `
        <table class="searched-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>🔑 Private Key</th>
                    <th>Address</th>
                    <th>Balance</th>
                    <th>Status</th>
                    <th>Time</th>
                </tr>
            </thead>
            <tbody>
                ${searched.map((item, index) => {
                    const hasBalance = item.has_balance || parseFloat(item.total_balance || 0) > 0;
                    const balance = parseFloat(item.total_balance || 0);
                    const privateKey = item.private_key || 'N/A';
                    const privateKeyEscaped = privateKey.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
                    return `
                        <tr class="${hasBalance ? 'has-balance-row' : ''}">
                            <td>${index + 1}</td>
                            <td class="private-key-cell">
                                <span class="private-key-text" title="Click to copy" data-key="${privateKeyEscaped}">${privateKey}</span>
                            </td>
                            <td class="address-cell">
                                <div style="display: flex; flex-direction: column; gap: 5px;">
                                    <div style="display: flex; gap: 5px; flex-wrap: wrap;">
                                        <a href="https://etherscan.io/address/${item.address}" target="_blank" 
                                           class="explorer-link-table etherscan-link"
                                           title="View on Etherscan">
                                           Etherscan
                                        </a>
                                        <a href="https://bscscan.com/address/${item.address}" target="_blank" 
                                           class="explorer-link-table bscscan-link"
                                           title="View on BSCScan">
                                           BSCScan
                                        </a>
                                    </div>
                                    <span class="address-text">${item.address}</span>
                                </div>
                            </td>
                            <td class="balance-cell">
                                ${hasBalance ? `<span class="balance-found">${formatBalance(balance)}</span>` : '<span class="no-balance">0.000000</span>'}
                            </td>
                            <td>
                                ${hasBalance ? '<span class="status-badge success">💰 Has Balance</span>' : '<span class="status-badge">Empty</span>'}
                            </td>
                            <td class="time-cell">${formatTimestamp(item.timestamp || item.searched_at)}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
    
    // Add click handlers for copy functionality
    searchedList.querySelectorAll('.private-key-text').forEach(el => {
        el.addEventListener('click', function() {
            const key = this.getAttribute('data-key');
            copyToClipboard(key);
        });
    });
}

// Sequential progress update
function updateSequentialProgress(progress) {
    const progressDiv = document.getElementById('sequentialProgress');
    if (progressDiv) {
        progressDiv.style.display = 'block';
        document.getElementById('seqPercent').textContent = progress.percent.toFixed(4);
        document.getElementById('seqScanned').textContent = formatNumber(progress.scanned);
        document.getElementById('seqTotal').textContent = formatNumber(progress.total);
        document.getElementById('seqCurrent').textContent = progress.current;
    }
}

// Export keys function
async function exportKeys() {
    const exportBtn = document.getElementById('exportBtn');
    const exportStatus = document.getElementById('exportStatus');
    
    if (exportBtn) {
        exportBtn.disabled = true;
        exportBtn.textContent = '⏳ Exporting...';
    }
    
    const data = await fetchAPI('/api/export');
    
    if (data && data.success) {
        if (exportStatus) {
            exportStatus.style.display = 'block';
            exportStatus.innerHTML = `✅ Successfully exported ${formatNumber(data.count)} keys to <strong>${data.filename}</strong>`;
            exportStatus.style.color = 'var(--success-color)';
        }
        addActivity(`Exported ${data.count} keys to ${data.filename}`, 'success');
    } else {
        if (exportStatus) {
            exportStatus.style.display = 'block';
            exportStatus.textContent = `❌ Error: ${data?.error || 'Export failed'}`;
            exportStatus.style.color = 'var(--danger-color)';
        }
    }
    
    if (exportBtn) {
        exportBtn.disabled = false;
        exportBtn.textContent = '💾 Export to TXT';
    }
    
    // Hide status after 5 seconds
    if (exportStatus) {
        setTimeout(() => {
            exportStatus.style.display = 'none';
        }, 5000);
    }
}

// Copy to clipboard function
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Show temporary notification
        const notification = document.createElement('div');
        notification.style.cssText = 'position: fixed; top: 20px; right: 20px; background: var(--success-color); color: white; padding: 15px 20px; border-radius: 8px; z-index: 10000; box-shadow: 0 4px 12px rgba(0,0,0,0.3);';
        notification.textContent = '✅ Private key copied to clipboard!';
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.remove();
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy:', err);
    });
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (updateInterval) {
        clearInterval(updateInterval);
    }
});

