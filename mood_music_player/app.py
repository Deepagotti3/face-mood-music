import streamlit as st
import cv2
import numpy as np
from deepface import DeepFace
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import base64
import time
import os
from PIL import Image
import io

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="MoodTunes",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Load Custom CSS ────────────────────────────────────────────────────────────
with open("style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# ─── Spotify Setup ──────────────────────────────────────────────────────────────
SPOTIPY_CLIENT_ID     = os.getenv("SPOTIPY_CLIENT_ID", "YOUR_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "YOUR_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI  = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8501")

SCOPE = "user-modify-playback-state user-read-playback-state streaming user-read-email user-read-private"

# Mood → Spotify search query mapping
MOOD_CONFIG = {
    "happy":    {"query": "happy upbeat feel good",    "emoji": "😄", "color": "#FFD93D", "label": "Happy"},
    "sad":      {"query": "sad emotional heartbreak",  "emoji": "😢", "color": "#6C9BCF", "label": "Sad"},
    "angry":    {"query": "angry intense metal rage",  "emoji": "😠", "color": "#FF6B6B", "label": "Angry"},
    "surprise": {"query": "exciting surprise energetic","emoji": "😲", "color": "#C77DFF", "label": "Surprised"},
    "fear":     {"query": "calm peaceful meditation",  "emoji": "😨", "color": "#74C69D", "label": "Fearful"},
    "disgust":  {"query": "alternative indie rock",    "emoji": "🤢", "color": "#95D5B2", "label": "Disgusted"},
    "neutral":  {"query": "chill lofi study beats",   "emoji": "😐", "color": "#ADB5BD", "label": "Neutral"},
}


# ─── Helper Functions ───────────────────────────────────────────────────────────

def get_spotify_client():
    """Return an authenticated Spotipy client stored in session state."""
    if "sp" not in st.session_state:
        try:
            auth_manager = SpotifyOAuth(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri=SPOTIPY_REDIRECT_URI,
                scope=SCOPE,
                cache_path=".spotify_cache",
                open_browser=False,
            )
            st.session_state.sp = spotipy.Spotify(auth_manager=auth_manager)
        except Exception as e:
            st.session_state.sp = None
            st.session_state.spotify_error = str(e)
    return st.session_state.sp


def analyze_emotion(frame_rgb: np.ndarray) -> str:
    """Run DeepFace emotion analysis and return dominant emotion."""
    try:
        result = DeepFace.analyze(
            frame_rgb,
            actions=["emotion"],
            enforce_detection=False,
            silent=True,
        )
        if isinstance(result, list):
            result = result[0]
        dominant = result["dominant_emotion"].lower()
        return dominant if dominant in MOOD_CONFIG else "neutral"
    except Exception:
        return "neutral"


def search_tracks(sp, mood: str, limit: int = 5):
    """Search Spotify for tracks matching the mood query."""
    query = MOOD_CONFIG[mood]["query"]
    try:
        results = sp.search(q=query, type="track", limit=limit)
        tracks = results["tracks"]["items"]
        return tracks
    except Exception as e:
        st.error(f"Spotify search error: {e}")
        return []


def play_track(sp, track_uri: str):
    """Start playback of a track on the user's active device."""
    try:
        devices = sp.devices()
        if not devices["devices"]:
            st.warning("⚠️ No active Spotify device found. Open Spotify on any device first.")
            return False
        device_id = devices["devices"][0]["id"]
        sp.start_playback(device_id=device_id, uris=[track_uri])
        return True
    except Exception as e:
        st.error(f"Playback error: {e}")
        return False


def img_to_base64(img_array: np.ndarray) -> str:
    pil_img = Image.fromarray(img_array)
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


# ─── Session State Defaults ─────────────────────────────────────────────────────
for key, default in {
    "detected_mood": None,
    "tracks": [],
    "current_track_idx": 0,
    "snapshot": None,
    "sp": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


# ─── UI ─────────────────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-title">🎵 MoodTunes</div>
    <div class="hero-sub">Let your face choose your playlist</div>
</div>
""", unsafe_allow_html=True)

# ── Spotify Auth Section ────────────────────────────────────────────────────────
sp = get_spotify_client()

col_cam, col_result = st.columns([1, 1], gap="large")

with col_cam:
    st.markdown('<div class="section-title">📸 Capture Your Mood</div>', unsafe_allow_html=True)
    st.markdown('<p class="section-desc">Allow camera access and click the button below to detect your current emotion.</p>', unsafe_allow_html=True)

    camera_image = st.camera_input("", label_visibility="collapsed")

    if camera_image is not None:
        # Convert to numpy array
        bytes_data = camera_image.getvalue()
        nparr = np.frombuffer(bytes_data, np.uint8)
        frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        st.session_state.snapshot = frame_rgb

        with st.spinner("🔍 Analyzing your expression..."):
            mood = analyze_emotion(frame_rgb)
            st.session_state.detected_mood = mood
            st.session_state.current_track_idx = 0

            if sp:
                tracks = search_tracks(sp, mood, limit=6)
                st.session_state.tracks = tracks
            else:
                st.session_state.tracks = []

with col_result:
    st.markdown('<div class="section-title">🎭 Detected Mood</div>', unsafe_allow_html=True)

    mood = st.session_state.detected_mood

    if mood:
        cfg = MOOD_CONFIG[mood]
        st.markdown(f"""
        <div class="mood-card" style="border-color:{cfg['color']}; box-shadow: 0 0 40px {cfg['color']}33;">
            <div class="mood-emoji">{cfg['emoji']}</div>
            <div class="mood-label" style="color:{cfg['color']}">{cfg['label']}</div>
            <div class="mood-desc">Playing music for your vibe...</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="mood-card empty-mood">
            <div class="mood-emoji">🎭</div>
            <div class="mood-label">Waiting...</div>
            <div class="mood-desc">Capture a photo to detect your mood</div>
        </div>
        """, unsafe_allow_html=True)

# ── Tracks Section ──────────────────────────────────────────────────────────────
if st.session_state.tracks:
    st.markdown("---")
    st.markdown('<div class="section-title">🎵 Recommended Tracks</div>', unsafe_allow_html=True)

    tracks = st.session_state.tracks
    cols = st.columns(len(tracks))

    for i, (col, track) in enumerate(zip(cols, tracks)):
        with col:
            album_img = track["album"]["images"][0]["url"] if track["album"]["images"] else ""
            artist    = track["artists"][0]["name"]
            name      = track["name"]
            uri       = track["uri"]
            preview   = track.get("preview_url", "")
            ext_url   = track["external_urls"]["spotify"]

            st.markdown(f"""
            <div class="track-card">
                <img src="{album_img}" class="album-art" />
                <div class="track-name">{name[:22]}{"…" if len(name)>22 else ""}</div>
                <div class="track-artist">{artist[:18]}{"…" if len(artist)>18 else ""}</div>
            </div>
            """, unsafe_allow_html=True)

            # 30-sec preview player
            if preview:
                st.audio(preview, format="audio/mp3")

            # Open in Spotify button
            st.markdown(f'<a href="{ext_url}" target="_blank" class="spotify-btn">▶ Open in Spotify</a>', unsafe_allow_html=True)

            # Play on active device button
            if sp:
                if st.button(f"▶ Play", key=f"play_{i}"):
                    play_track(sp, uri)

elif st.session_state.detected_mood and not sp:
    st.info("🔑 Connect Spotify in the sidebar to get personalized track recommendations and playback control.")

# ── Spotify Setup Instructions (sidebar) ────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔧 Setup Guide")
    st.markdown("""
**Step 1:** Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)

**Step 2:** Create an App → Copy `Client ID` & `Client Secret`

**Step 3:** Set Redirect URI to:
```
http://localhost:8501
```

**Step 4:** Add to `.env` file:
```
SPOTIPY_CLIENT_ID=your_id
SPOTIPY_CLIENT_SECRET=your_secret
SPOTIPY_REDIRECT_URI=http://localhost:8501
```

**Step 5:** Run the app:
```bash
streamlit run app.py
```
    """)

    st.markdown("---")
    st.markdown("### 🎭 Mood → Music Map")
    for m, cfg in MOOD_CONFIG.items():
        st.markdown(f"{cfg['emoji']} **{cfg['label']}** → {cfg['query']}")

# ── Footer ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer">
    Built with ❤️ using DeepFace + Spotify API + Streamlit &nbsp;|&nbsp
</div>
""", unsafe_allow_html=True)
