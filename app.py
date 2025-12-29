from flask import Flask, render_template, request, redirect, jsonify
import string
import random
from datetime import datetime
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# -------------------- MongoDB Setup --------------------
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "url_shortener")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
urls_collection = db.urls

# Ensure unique short_code
urls_collection.create_index("short_code", unique=True)

# -------------------- Helpers --------------------
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        if not urls_collection.find_one({"short_code": code}):
            return code

# -------------------- Routes --------------------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    urls = list(
        urls_collection.find(
            {},
            {"_id": 0, "short_code": 1, "original_url": 1, "clicks": 1, "created_at": 1, "last_clicked": 1}
        )
        .sort("created_at", -1)
        .limit(50)
    )

    stats = urls_collection.aggregate([
        {
            "$group": {
                "_id": None,
                "total_urls": {"$sum": 1},
                "total_clicks": {"$sum": "$clicks"}
            }
        }
    ])

    stats = next(stats, {"total_urls": 0, "total_clicks": 0})

    return render_template(
        'dashboard.html',
        urls=[(
            u["short_code"],
            u["original_url"],
            u.get("clicks", 0),
            u.get("created_at"),
            u.get("last_clicked")
        ) for u in urls],
        total_urls=stats["total_urls"],
        total_clicks=stats["total_clicks"]
    )

@app.route('/api/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    original_url = data.get('original_url', '').strip()
    custom_code = data.get('custom_code', '').strip()

    if not original_url:
        return jsonify({'success': False, 'error': 'URL is required'}), 400

    if not original_url.startswith(('http://', 'https://')):
        original_url = 'https://' + original_url

    if custom_code:
        if len(custom_code) < 3:
            return jsonify({'success': False, 'error': 'Custom code must be at least 3 characters'}), 400
        if not custom_code.isalnum():
            return jsonify({'success': False, 'error': 'Custom code can only contain letters and numbers'}), 400
        if urls_collection.find_one({"short_code": custom_code}):
            return jsonify({'success': False, 'error': 'Custom code already taken'}), 400
        short_code = custom_code
    else:
        short_code = generate_short_code()

    created_at = datetime.now().isoformat()

    try:
        urls_collection.insert_one({
            "original_url": original_url,
            "short_code": short_code,
            "created_at": created_at,
            "clicks": 0,
            "last_clicked": None
        })
    except DuplicateKeyError:
        return jsonify({'success': False, 'error': 'Short code already exists'}), 400

    return jsonify({
        'success': True,
        'short_code': short_code,
        'short_url': request.host_url + short_code,
        'original_url': original_url,
        'created_at': created_at
    })

@app.route('/api/stats/<short_code>')
def get_stats(short_code):
    url = urls_collection.find_one({"short_code": short_code})

    if not url:
        return jsonify({'success': False, 'error': 'URL not found'}), 404

    return jsonify({
        'success': True,
        'short_code': short_code,
        'original_url': url["original_url"],
        'clicks': url.get("clicks", 0),
        'created_at': url.get("created_at"),
        'last_clicked': url.get("last_clicked")
    })

@app.route('/api/delete/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    result = urls_collection.delete_one({"short_code": short_code})

    if result.deleted_count:
        return jsonify({'success': True, 'message': 'URL deleted successfully'})
    return jsonify({'success': False, 'error': 'URL not found'}), 404

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url = urls_collection.find_one({"short_code": short_code})

    if not url:
        return render_template('404.html'), 404

    now = datetime.now().isoformat()
    urls_collection.update_one(
        {"short_code": short_code},
        {"$inc": {"clicks": 1}, "$set": {"last_clicked": now}}
    )

    return redirect(url["original_url"])

# -------------------- Run --------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
