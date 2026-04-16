# 🎵 MoodTunes — Mood-Based Music Player

> Detects your facial emotion via webcam and plays Spotify songs that match your vibe.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?style=flat-square&logo=streamlit)
![DeepFace](https://img.shields.io/badge/DeepFace-AI-green?style=flat-square)
![Spotify](https://img.shields.io/badge/Spotify-API-1DB954?style=flat-square&logo=spotify)

---

## 📸 Features

- 🎭 **Real-time emotion detection** using DeepFace (happy, sad, angry, surprised, fearful, disgusted, neutral)
- 🎵 **Spotify integration** — searches & plays songs matching your current mood
- 🔊 **30-second audio previews** built directly into the app
- ▶️ **One-click playback** on any active Spotify device
- 🌙 **Sleek dark UI** with animated mood cards and album art

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| Emotion AI | DeepFace + TensorFlow |
| Music API | Spotify Web API (Spotipy) |
| Computer Vision | OpenCV |
| Deployment | Streamlit Cloud |

---

## ⚙️ Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/mood-music-player.git
cd mood-music-player
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Spotify API

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Click **"Create App"**
3. Fill in:
   - App Name: `MoodTunes`
   - Redirect URI: `http://localhost:8501`
4. Copy your **Client ID** and **Client Secret**

### 5. Configure Environment
```bash
cp .env.example .env
```

Edit `.env`:
```
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://localhost:8501
```

### 6. Run the App
```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🚀 Deploy on Streamlit Cloud (Free)

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **"New app"** → select your repo → set `app.py` as main file
4. Go to **"Advanced settings" → "Secrets"** and add:

```toml
SPOTIPY_CLIENT_ID = "your_client_id"
SPOTIPY_CLIENT_SECRET = "your_client_secret"
SPOTIPY_REDIRECT_URI = "https://your-app-name.streamlit.app"
```

5. Update your Spotify app's Redirect URI to match your Streamlit Cloud URL

---

## 🎭 Emotion → Music Mapping

| Emotion | Music Style |
|---|---|
| 😄 Happy | Upbeat feel-good tracks |
| 😢 Sad | Emotional, heartbreak songs |
| 😠 Angry | Intense metal / rock |
| 😲 Surprised | Exciting energetic bangers |
| 😨 Fearful | Calm, peaceful meditation |
| 🤢 Disgusted | Alternative indie rock |
| 😐 Neutral | Chill lo-fi study beats |

---

## 📁 Project Structure

```
mood-music-player/
├── app.py                  # Main Streamlit application
├── style.css               # Custom dark theme CSS
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .gitignore
├── .streamlit/
│   ├── config.toml         # Streamlit theme config
│   └── secrets.toml        # (NOT committed) secrets for cloud
└── README.md
```

---

## 🔑 Notes

- **DeepFace models** are auto-downloaded on first run (~500MB). This happens once.
- **Active Spotify device** is required for playback control. Open Spotify on phone/desktop first.
- **30-second previews** work without an active device (no Premium needed).
- Camera access must be allowed in your browser.

---

## 👨‍💻 Built By

Made with ❤️ as a BCA Final Year Project  
Stack: Python · DeepFace · Spotipy · Streamlit
```

---

## 📄 License

MIT License — free to use and modify.
