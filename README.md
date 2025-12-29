# 🔗 Advanced URL Shortener

A modern, feature-rich URL shortener built with Flask, featuring a beautiful UI, analytics dashboard, and click tracking.

## ✨ Features

- 🎨 **Modern Glassmorphism UI** - Beautiful gradient backgrounds with glass effects
- 📊 **Analytics Dashboard** - Track clicks, view statistics, and manage all your shortened URLs
- 🎯 **Custom Short Codes** - Create memorable custom short links
- 📱 **Fully Responsive** - Works perfectly on all devices
- ⚡ **Real-time Updates** - Instant feedback and smooth animations
- 🔒 **URL Validation** - Smart URL validation and auto-correction
- 📈 **Click Tracking** - Monitor how many times your links are clicked
- 🗑️ **Link Management** - Delete unwanted shortened URLs
- 🌙 **Dark Theme** - Eye-friendly dark interface

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/url-shortener.git
   cd url-shortener
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## 🌐 Deploy to Render

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Deploy on Render**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure:
     - **Name**: your-shortener
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`
   - Click "Create Web Service"

3. **Your app will be live at**: `https://your-shortener.onrender.com`

## 📁 Project Structure

```
url-shortener/
│
├── templates/
│   ├── index.html          # Home page with URL shortener
│   ├── dashboard.html      # Analytics dashboard
│   └── 404.html           # Custom 404 page
│
├── static/
│   ├── css/
│   │   └── style.css      # All styling
│   └── js/
│       └── main.js        # JavaScript functionality
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Procfile              # Render deployment config
├── .gitignore            # Git ignore rules
└── README.md             # This file
```

## 🎯 Usage

### Shorten a URL

1. Go to the home page
2. Enter your long URL
3. (Optional) Enter a custom short code
4. Click "Shorten URL"
5. Copy and share your short link!

### View Analytics

1. Click "Dashboard" in the navigation
2. See all your shortened URLs
3. View click counts and creation dates
4. Delete URLs you no longer need

### API Endpoints

**Shorten URL:**
```bash
POST /api/shorten
Content-Type: application/json

{
  "original_url": "https://example.com/very-long-url",
  "custom_code": "mylink"  // optional
}
```

**Get Stats:**
```bash
GET /api/stats/<short_code>
```

**Delete URL:**
```bash
DELETE /api/delete/<short_code>
```

## 🎨 Customization

### Change Colors

Edit `static/css/style.css` and modify the CSS variables:
```css
:root {
    --primary: #667eea;
    --secondary: #764ba2;
    --success: #10b981;
    --danger: #ef4444;
}
```

### Change Database

By default, SQLite is used. For production with persistent storage, consider PostgreSQL:

1. Install psycopg2: `pip install psycopg2-binary`
2. Update database connection in `app.py`

## 🔒 Security Notes

- Change `SECRET_KEY` in production
- Use environment variables for sensitive data
- Consider rate limiting for public deployments
- Validate and sanitize all user inputs

## 📝 License

MIT License - feel free to use this project however you like!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

If you have any questions or issues, please open an issue on GitHub.

---

Made with ❤️ using Flask