from flask import Flask, render_template, request, redirect, jsonify
import string
import random
from datetime import datetime
import os
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import requests
from user_agents import parse

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# -------------------- MongoDB Setup --------------------
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "url_shortener")

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]
urls_collection = db.urls
analytics_collection = db.analytics  # New collection for click analytics

# Ensure unique short_code
urls_collection.create_index("short_code", unique=True)
analytics_collection.create_index("short_code")
analytics_collection.create_index("timestamp")

# -------------------- Helpers --------------------
def generate_short_code(length=6):
    characters = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choice(characters) for _ in range(length))
        if not urls_collection.find_one({"short_code": code}):
            return code

def get_client_ip():
    """Get real client IP address"""
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    elif request.headers.get('X-Real-IP'):
        ip = request.headers.get('X-Real-IP')
    else:
        ip = request.remote_addr
    return ip

def get_location_from_ip(ip_address):
    """Get location data from IP address using ip-api.com (free)"""
    try:
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return {
                'country': 'Local',
                'city': 'Localhost',
                'region': 'Dev',
                'isp': 'Local Network'
            }
        
        response = requests.get(f'http://ip-api.com/json/{ip_address}', timeout=2)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'isp': data.get('isp', 'Unknown'),
                    'lat': data.get('lat'),
                    'lon': data.get('lon')
                }
    except Exception as e:
        print(f"Location fetch error: {e}")
    
    return {
        'country': 'Unknown',
        'city': 'Unknown',
        'region': 'Unknown',
        'isp': 'Unknown'
    }

def get_device_info():
    """Extract device, browser, and OS information"""
    user_agent_string = request.headers.get('User-Agent', '')
    user_agent = parse(user_agent_string)
    
    # Device type
    if user_agent.is_mobile:
        device_type = 'Mobile'
    elif user_agent.is_tablet:
        device_type = 'Tablet'
    elif user_agent.is_pc:
        device_type = 'Desktop'
    else:
        device_type = 'Other'
    
    return {
        'device_type': device_type,
        'device_brand': user_agent.device.brand or 'Unknown',
        'device_model': user_agent.device.model or 'Unknown',
        'browser': user_agent.browser.family,
        'browser_version': user_agent.browser.version_string,
        'os': user_agent.os.family,
        'os_version': user_agent.os.version_string,
        'is_mobile': user_agent.is_mobile,
        'is_tablet': user_agent.is_tablet,
        'is_bot': user_agent.is_bot
    }

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

@app.route('/analytics/<short_code>')
def analytics_page(short_code):
    """Detailed analytics page for a specific short URL"""
    url_data = urls_collection.find_one({"short_code": short_code})
    
    if not url_data:
        return render_template('404.html'), 404
    
    # Get all click analytics for this short code
    clicks = list(analytics_collection.find({"short_code": short_code}).sort("timestamp", -1))
    
    # Aggregate analytics data
    analytics_data = {
        'total_clicks': len(clicks),
        'unique_ips': len(set(c.get('ip_address') for c in clicks)),
        'countries': {},
        'cities': {},
        'devices': {},
        'browsers': {},
        'os': {},
        'referrers': {},
        'recent_clicks': clicks[:20]  # Last 20 clicks
    }
    
    for click in clicks:
        # Country stats
        country = click.get('location', {}).get('country', 'Unknown')
        analytics_data['countries'][country] = analytics_data['countries'].get(country, 0) + 1
        
        # City stats
        city = click.get('location', {}).get('city', 'Unknown')
        analytics_data['cities'][city] = analytics_data['cities'].get(city, 0) + 1
        
        # Device stats
        device = click.get('device_info', {}).get('device_type', 'Unknown')
        analytics_data['devices'][device] = analytics_data['devices'].get(device, 0) + 1
        
        # Browser stats
        browser = click.get('device_info', {}).get('browser', 'Unknown')
        analytics_data['browsers'][browser] = analytics_data['browsers'].get(browser, 0) + 1
        
        # OS stats
        os_name = click.get('device_info', {}).get('os', 'Unknown')
        analytics_data['os'][os_name] = analytics_data['os'].get(os_name, 0) + 1
        
        # Referrer stats
        referrer = click.get('referrer', 'Direct')
        analytics_data['referrers'][referrer] = analytics_data['referrers'].get(referrer, 0) + 1
    
    return render_template(
        'analytics.html',
        url_data=url_data,
        analytics=analytics_data
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

    # Get click analytics summary
    click_count = analytics_collection.count_documents({"short_code": short_code})
    unique_ips = len(analytics_collection.distinct("ip_address", {"short_code": short_code}))

    return jsonify({
        'success': True,
        'short_code': short_code,
        'original_url': url["original_url"],
        'clicks': url.get("clicks", 0),
        'unique_visitors': unique_ips,
        'created_at': url.get("created_at"),
        'last_clicked': url.get("last_clicked")
    })

@app.route('/api/delete/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    result = urls_collection.delete_one({"short_code": short_code})
    
    # Also delete all analytics data for this URL
    analytics_collection.delete_many({"short_code": short_code})

    if result.deleted_count:
        return jsonify({'success': True, 'message': 'URL deleted successfully'})
    return jsonify({'success': False, 'error': 'URL not found'}), 404

@app.route('/<short_code>')
def redirect_to_url(short_code):
    url = urls_collection.find_one({"short_code": short_code})

    if not url:
        return render_template('404.html'), 404

    # Collect analytics data
    ip_address = get_client_ip()
    location_data = get_location_from_ip(ip_address)
    device_info = get_device_info()
    
    referrer = request.headers.get('Referer', 'Direct')
    timestamp = datetime.now().isoformat()
    
    # Store detailed analytics
    analytics_data = {
        "short_code": short_code,
        "timestamp": timestamp,
        "ip_address": ip_address,
        "location": location_data,
        "device_info": device_info,
        "referrer": referrer,
        "user_agent": request.headers.get('User-Agent', '')
    }
    
    try:
        analytics_collection.insert_one(analytics_data)
    except Exception as e:
        print(f"Analytics insert error: {e}")
    
    # Update URL click count
    urls_collection.update_one(
        {"short_code": short_code},
        {"$inc": {"clicks": 1}, "$set": {"last_clicked": timestamp}}
    )

    return redirect(url["original_url"])

# -------------------- Run --------------------
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

