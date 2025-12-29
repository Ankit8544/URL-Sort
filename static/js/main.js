// Custom code toggle
document.getElementById('customCodeToggle')?.addEventListener('change', function() {
    const customCodeInput = document.getElementById('customCodeInput');
    if (this.checked) {
        customCodeInput.style.display = 'block';
        document.getElementById('custom_code').focus();
    } else {
        customCodeInput.style.display = 'none';
        document.getElementById('custom_code').value = '';
    }
});

// Form submission
document.getElementById('shortenForm')?.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const btn = document.getElementById('shortenBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<span>⏳ Processing...</span>';
    btn.disabled = true;
    
    const formData = {
        original_url: document.getElementById('original_url').value.trim(),
        custom_code: document.getElementById('custom_code').value.trim()
    };
    
    try {
        const response = await fetch('/api/shorten', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('✅ URL shortened successfully!', 'success');
            
            // Show result
            document.getElementById('shortened_url').value = data.short_url;
            document.getElementById('visitLink').href = '/' + data.short_code;
            document.getElementById('resultSection').style.display = 'block';
            
            // Scroll to result
            document.getElementById('resultSection').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'nearest' 
            });
            
            // Reset form
            document.getElementById('shortenForm').reset();
            document.getElementById('customCodeInput').style.display = 'none';
            document.getElementById('customCodeToggle').checked = false;
            
        } else {
            showAlert('❌ ' + data.error, 'error');
        }
    } catch (error) {
        showAlert('❌ Network error. Please try again.', 'error');
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
});

// Copy to clipboard
function copyToClipboard() {
    const input = document.getElementById('shortened_url');
    input.select();
    input.setSelectionRange(0, 99999); // For mobile
    
    navigator.clipboard.writeText(input.value).then(() => {
        const copyBtn = document.getElementById('copyBtn');
        const copyText = document.getElementById('copyText');
        const originalText = copyText.textContent;
        
        copyText.textContent = '✓ Copied!';
        copyBtn.style.background = '#059669';
        
        setTimeout(() => {
            copyText.textContent = originalText;
            copyBtn.style.background = '';
        }, 2000);
        
        showAlert('📋 Copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback
        document.execCommand('copy');
        showAlert('📋 Copied to clipboard!', 'success');
    });
}

// Show alert
function showAlert(message, type) {
    const alertContainer = document.getElementById('alertContainer');
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    alert.style.cssText = `
        padding: 16px 24px;
        margin-top: 20px;
        border-radius: 12px;
        font-weight: 500;
        animation: slideDown 0.3s ease;
        background: ${type === 'success' ? '#10b98120' : '#ef444420'};
        color: ${type === 'success' ? '#059669' : '#dc2626'};
        border-left: 4px solid ${type === 'success' ? '#10b981' : '#ef4444'};
    `;
    
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    
    setTimeout(() => {
        alert.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => alert.remove(), 300);
    }, 5000);
}

// Auto-hide result on new input
document.getElementById('original_url')?.addEventListener('input', function() {
    if (this.value.trim()) {
        document.getElementById('resultSection').style.display = 'none';
    }
});
