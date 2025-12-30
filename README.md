# 🔗 Advanced URL Shortener

A modern, feature-rich URL shortener built with Flask and **MongoDB**, featuring a beautiful UI, analytics dashboard, and click tracking.

---

## ✨ Features

* 🎨 **Modern Glassmorphism UI** – Beautiful gradient backgrounds with glass effects
* 📊 **Analytics Dashboard** – Track clicks, view statistics, and manage shortened URLs
* 🎯 **Custom Short Codes** – Create memorable custom short links
* 📱 **Fully Responsive** – Works perfectly on all devices
* ⚡ **Real-time Updates** – Instant feedback and smooth animations
* 🔒 **URL Validation** – Smart URL validation and auto-correction
* 📈 **Click Tracking** – Monitor how many times your links are clicked
* 🗑️ **Link Management** – Delete unwanted shortened URLs
* 🌙 **Dark Theme** – Eye-friendly dark interface
* ☁️ **MongoDB Atlas Backend** – Scalable, production-ready cloud database

---

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

4. **Create `.env` file**

   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   MONGO_DB_NAME=url_shortener
   SECRET_KEY=your-secret-key
   PORT=5000
   ```

5. **Run the application**

   ```bash
   python app.py
   ```

6. **Open in browser**

   ```
   http://localhost:5000
   ```

---

## 🌐 Deploy to Render

### 1️⃣ Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main
```

---

### 2️⃣ Create Web Service on Render

* Go to 👉 [https://render.com](https://render.com)
* Click **New + → Web Service**
* Connect your GitHub repository

**Configuration:**

| Setting       | Value                             |
| ------------- | --------------------------------- |
| Environment   | Python 3                          |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn app:app`                |

---

### 3️⃣ Add Environment Variables on Render

Render → **Environment → Environment Variables**

```
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGO_DB_NAME=url_shortener
SECRET_KEY=your-production-secret
PORT=5000
```

⚠️ **Important**

* Username & password must be inside `MONGO_URI`
* MongoDB Atlas Network Access must allow `0.0.0.0/0`

---

### 4️⃣ Deploy 🎉

Your app will be live at:

```
https://your-shortener.onrender.com
```

---

## 📁 Project Structure

```
url-shortener/
│
├── templates/
│   ├── index.html          # Home page
│   ├── dashboard.html      # Analytics dashboard
│   └── 404.html            # Custom 404 page
│
├── static/
│   ├── css/
│   │   └── style.css       # Styling
│   └── js/
│       └── main.js         # Frontend logic
│
├── app.py                  # Flask app (MongoDB backend)
├── requirements.txt        # Dependencies
├── Procfile                # Render start config
├── .gitignore
└── README.md
```

---

## 🎯 Usage

### Shorten a URL

1. Open home page
2. Enter long URL
3. (Optional) Custom short code
4. Click **Shorten URL**
5. Copy and share 🎉

---

### View Analytics

1. Open **Dashboard**
2. View all shortened URLs
3. Check click counts & timestamps
4. Delete URLs if needed

---

## 🔌 API Endpoints

### ➤ Shorten URL

```http
POST /api/shorten
Content-Type: application/json

{
  "original_url": "https://example.com/very-long-url",
  "custom_code": "mylink"
}
```

---

### ➤ Get Stats

```http
GET /api/stats/<short_code>
```

---

### ➤ Delete URL

```http
DELETE /api/delete/<short_code>
```

---

## 🛠️ Customization

### Change Colors

Edit `static/css/style.css`:

```css
:root {
  --primary: #667eea;
  --secondary: #764ba2;
  --success: #10b981;
  --danger: #ef4444;
}
```

---

## 🗄️ Database

* **MongoDB Atlas (Cloud)**
* Auto-scaling & production ready
* Unique index on `short_code`
* No local database files required

❌ SQLite
❌ Local `.db` files

---

## 🔒 Security Notes

* Always change `SECRET_KEY` in production
* Never hardcode MongoDB credentials
* Use environment variables only
* Enable MongoDB IP restrictions if possible
* Consider rate limiting for public usage

---

## 📝 License

MIT License – free to use and modify.

---

## 🤝 Contributing

Pull requests are welcome.
For major changes, please open an issue first.

---

## 📧 Support

For issues or suggestions, open a GitHub issue.

---

**Made with ❤️ using Flask + MongoDB**
