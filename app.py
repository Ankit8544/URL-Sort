from flask import Flask, render_template, request, redirect, jsonify, url_for
import string
import random
import sqlite3
from datetime import datetime
import os
import json

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database setup
def init_db():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original_url TEXT NOT NULL,
                  short_code TEXT UNIQUE NOT NULL,
                  created_at TIMESTAMP,
                  clicks INTEGER DEFAULT 0,
                  last_clicked TIMESTAMP)''')
    conn.commit()
    conn.close()

def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        conn = sqlite3.connect('urls.db')
        c = conn.cursor()
        c.execute('SELECT short_code FROM urls WHERE short_code = ?', (code,))
        if not c.fetchone():
            conn.close()
            return code
        conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT short_code, original_url, clicks, created_at, last_clicked FROM urls ORDER BY created_at DESC LIMIT 50')
    urls = c.fetchall()
    
    c.execute('SELECT COUNT(*), SUM(clicks) FROM urls')
    stats = c.fetchone()
    conn.close()
    
    return render_template('dashboard.html', urls=urls, total_urls=stats[0] or 0, total_clicks=stats[1] or 0)

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('original_url', '').strip()
    custom_code = data.get('custom_code', '').strip()
    
    if not original_url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400
    
    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url
    
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    
    if custom_code:
        if len(custom_code) < 3:
            conn.close()
            return jsonify({'success': False, 'error': 'Custom code must be at least 3 characters'}), 400
        
        if not custom_code.isalnum():
            conn.close()
            return jsonify({'success': False, 'error': 'Custom code can only contain letters and numbers'}), 400
        
        c.execute('SELECT short_code FROM urls WHERE short_code = ?', (custom_code,))
        if c.fetchone():
            conn.close()
            return jsonify({'success': False, 'error': 'Custom code already taken'}), 400
        short_code = custom_code
    else:
        short_code = generate_short_code()
    
    created_at = datetime.now().isoformat()
    try:
        c.execute('INSERT INTO urls (original_url, short_code, created_at) VALUES (?, ?, ?)',
                  (original_url, short_code, created_at))
        conn.commit()
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500
    
    conn.close()
    
    short_url = request.host_url + short_code
    
    return jsonify({
        'success': True,
        'short_code': short_code,
        'short_url': short_url,
        'original_url': original_url,
        'created_at': created_at
    })

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('SELECT original_url, clicks, created_at, last_clicked FROM urls WHERE short_code = ?', (short_code,))
    result = c.fetchone()
    conn.close()
    
    if result:
        return jsonify({
            'success': True,
            'short_code': short_code,
            'original_url': result[0],
            'clicks': result[1],
            'created_at': result[2],
            'last_clicked': result[3]
        })
    
    return jsonify({'success': False, 'error': 'URL not found'}), 404

@app.route('/api/delete/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    c.execute('DELETE FROM urls WHERE short_code = ?', (short_code,))
    deleted = c.rowcount > 0
    conn.commit()
    conn.close()
    
    if deleted:
        return jsonify({'success': True, 'message': 'URL deleted successfully'})
    return jsonify({'success': False, 'error': 'URL not found'}), 404

@app.route('/<short_code>')
def redirect_to_url(short_code):
    conn = sqlite3.connect('urls.db')
    c = conn.cursor()
    
    c.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
    result = c.fetchone()
    
    if result:
        now = datetime.now().isoformat()
        c.execute('UPDATE urls SET clicks = clicks + 1, last_clicked = ? WHERE short_code = ?', (now, short_code))
        conn.commit()
        conn.close()
        return redirect(result[0])
    
    conn.close()
    return render_template('404.html'), 404

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

