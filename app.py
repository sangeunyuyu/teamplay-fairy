import streamlit as st
import sqlite3
import random
import time
import io
import os
import socket
import qrcode
from datetime import datetime

# ==========================================
# Page Configuration & Metadata
# ==========================================
st.set_page_config(
    page_title="Jet Send Star | 초고속 무로그인 우주 파일 전송",
    page_icon="✦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

DB_PATH = "jetsend.db"

# ==========================================
# Database Operations (SQLite3)
# ==========================================
def init_db():
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            code TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            filesize INTEGER NOT NULL,
            filetype TEXT NOT NULL,
            data BLOB NOT NULL,
            created_at REAL NOT NULL,
            expires_at REAL NOT NULL,
            burn_after_download INTEGER DEFAULT 0,
            downloads_count INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def cleanup_expired():
    try:
        now = time.time()
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE expires_at < ?", (now,))
        conn.commit()
        conn.close()
    except Exception:
        pass

def generate_unique_code():
    cleanup_expired()
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    while True:
        code = f"{random.randint(1000, 9999)}"
        cursor.execute("SELECT 1 FROM files WHERE code = ?", (code,))
        if not cursor.fetchone():
            conn.close()
            return code

def save_file_to_db(code, filename, filesize, filetype, data_bytes, duration_minutes, burn=False):
    cleanup_expired()
    now = time.time()
    expires_at = now + (duration_minutes * 60)
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO files (code, filename, filesize, filetype, data, created_at, expires_at, burn_after_download, downloads_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, 0)
    """, (code, filename, filesize, filetype, data_bytes, now, expires_at, 1 if burn else 0))
    conn.commit()
    conn.close()
    return expires_at

def get_file_from_db(code):
    cleanup_expired()
    now = time.time()
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT code, filename, filesize, filetype, data, created_at, expires_at, burn_after_download, downloads_count
        FROM files
        WHERE code = ?
    """, (code,))
    row = cursor.fetchone()
    conn.close()
    if row:
        if row[6] < now:
            delete_file_from_db(code)
            return None
        return {
            "code": row[0],
            "filename": row[1],
            "filesize": row[2],
            "filetype": row[3],
            "data": row[4],
            "created_at": row[5],
            "expires_at": row[6],
            "burn_after_download": bool(row[7]),
            "downloads_count": row[8]
        }
    return None

def record_download_in_db(code):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("SELECT burn_after_download FROM files WHERE code = ?", (code,))
        row = cursor.fetchone()
        if row:
            burn = bool(row[0])
            if burn:
                cursor.execute("DELETE FROM files WHERE code = ?", (code,))
            else:
                cursor.execute("UPDATE files SET downloads_count = downloads_count + 1 WHERE code = ?", (code,))
            conn.commit()
        conn.close()
    except Exception:
        pass

def delete_file_from_db(code):
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10.0)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM files WHERE code = ?", (code,))
        conn.commit()
        conn.close()
    except Exception:
        pass

# Initialize database
init_db()

# ==========================================
# Utility Helpers
# ==========================================
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return 'localhost'

def format_size(bytes_size):
    if bytes_size is None or bytes_size < 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def get_file_meta_info(filename):
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
    if ext in ['ppt', 'pptx', 'key']:
        return "📊", "프레젠테이션 슬라이드", "#f97316"
    elif ext in ['pdf']:
        return "📕", "PDF 문서", "#ef4444"
    elif ext in ['doc', 'docx', 'hwp', 'txt']:
        return "📝", "텍스트 / 워드 문서", "#3b82f6"
    elif ext in ['zip', 'rar', '7z', 'tar', 'gz']:
        return "📦", "압축 파일", "#a855f7"
    elif ext in ['png', 'jpg', 'jpeg', 'gif', 'webp', 'svg']:
        return "🖼️", "이미지 파일", "#10b981"
    elif ext in ['mp4', 'mov', 'avi', 'mkv']:
        return "🎬", "동영상 미디어", "#ec4899"
    elif ext in ['mp3', 'wav', 'm4a', 'flac']:
        return "🎵", "오디오 파일", "#06b6d4"
    else:
        return "📁", "일반 파일", "#64748b"

def generate_qr_image(url_string):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(url_string)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b0f19", back_color="#ffffff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()

# ==========================================
# Apple-Grade Cosmic Glassmorphism CSS
# ==========================================
COSMIC_CSS = """
<style>
/* Reset & Base Fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap');

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Plus Jakarta Sans", Roboto, Helvetica, Arial, sans-serif;
    color: #f8fafc;
}

/* Deep Space Animated Canvas / Background */
.stApp {
    background: radial-gradient(ellipse at 50% 100%, #0d1224 0%, #060813 50%, #020308 100%) !important;
    background-attachment: fixed !important;
    min-height: 100vh;
}

header[data-testid="stHeader"] {
    background: transparent !important;
}

/* Cosmic Milky Way / Nebula Layers */
.cosmic-nebula {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}

.nebula-glow-1 {
    position: absolute;
    width: 650px;
    height: 650px;
    top: -120px;
    left: -120px;
    background: radial-gradient(circle, rgba(99, 102, 241, 0.20) 0%, rgba(99, 102, 241, 0) 70%);
    border-radius: 50%;
    filter: blur(60px);
    animation: driftSlow 18s ease-in-out infinite alternate;
}

.nebula-glow-2 {
    position: absolute;
    width: 750px;
    height: 750px;
    bottom: -160px;
    right: -120px;
    background: radial-gradient(circle, rgba(168, 85, 247, 0.18) 0%, rgba(168, 85, 247, 0) 70%);
    border-radius: 50%;
    filter: blur(70px);
    animation: driftSlow 22s ease-in-out infinite alternate-reverse;
}

.nebula-glow-3 {
    position: absolute;
    width: 550px;
    height: 550px;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: radial-gradient(circle, rgba(56, 189, 248, 0.12) 0%, rgba(56, 189, 248, 0) 70%);
    border-radius: 50%;
    filter: blur(80px);
}

@keyframes driftSlow {
    0% { transform: translate(0px, 0px) scale(1); }
    50% { transform: translate(40px, 30px) scale(1.1); }
    100% { transform: translate(-20px, 50px) scale(0.95); }
}

/* Animated Shooting Stars */
.shooting-star-1, .shooting-star-2, .shooting-star-3 {
    position: fixed;
    height: 2px;
    background: linear-gradient(90deg, #ffffff, rgba(255, 255, 255, 0.8), transparent);
    border-radius: 999px;
    filter: drop-shadow(0 0 8px rgba(186, 230, 253, 1));
    pointer-events: none;
    z-index: 0;
    opacity: 0;
}

.shooting-star-1 {
    top: 15%;
    left: 70%;
    width: 140px;
    transform: rotate(-35deg);
    animation: shoot1 8s linear infinite;
}

.shooting-star-2 {
    top: 45%;
    left: 85%;
    width: 110px;
    transform: rotate(-38deg);
    animation: shoot2 12s linear infinite 4s;
}

.shooting-star-3 {
    top: 8%;
    left: 30%;
    width: 160px;
    transform: rotate(-32deg);
    animation: shoot3 15s linear infinite 7s;
}

@keyframes shoot1 {
    0% { transform: translate(0, 0) rotate(-35deg); opacity: 0; }
    2% { opacity: 1; }
    8% { transform: translate(-300px, 210px) rotate(-35deg); opacity: 0; }
    100% { transform: translate(-300px, 210px) rotate(-35deg); opacity: 0; }
}

@keyframes shoot2 {
    0% { transform: translate(0, 0) rotate(-38deg); opacity: 0; }
    2% { opacity: 1; }
    7% { transform: translate(-250px, 195px) rotate(-38deg); opacity: 0; }
    100% { transform: translate(-250px, 195px) rotate(-38deg); opacity: 0; }
}

@keyframes shoot3 {
    0% { transform: translate(0, 0) rotate(-32deg); opacity: 0; }
    2% { opacity: 1; }
    6% { transform: translate(-350px, 218px) rotate(-32deg); opacity: 0; }
    100% { transform: translate(-350px, 218px) rotate(-32deg); opacity: 0; }
}

/* Twinkling Starfield */
.stars-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 0;
    background-image: 
        radial-gradient(1.5px 1.5px at 20px 30px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.2px 1.2px at 90px 140px, #e2e8f0, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 150px 70px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 230px 210px, #cbd5e1, rgba(0,0,0,0)),
        radial-gradient(1.8px 1.8px at 310px 110px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.2px 1.2px at 420px 260px, #93c5fd, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 530px 90px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 640px 180px, #e0e7ff, rgba(0,0,0,0)),
        radial-gradient(1.5px 1.5px at 750px 290px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(2.2px 2.2px at 860px 80px, #f8fafc, rgba(0,0,0,0)),
        radial-gradient(1.2px 1.2px at 930px 210px, #93c5fd, rgba(0,0,0,0)),
        radial-gradient(1.8px 1.8px at 1040px 140px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1px 1px at 1150px 310px, #cbd5e1, rgba(0,0,0,0)),
        radial-gradient(2px 2px at 1270px 170px, #ffffff, rgba(0,0,0,0)),
        radial-gradient(1.3px 1.3px at 1380px 250px, #e0e7ff, rgba(0,0,0,0));
    background-repeat: repeat;
    background-size: 550px 450px;
    animation: starsTwinkle 4s ease-in-out infinite alternate;
}

@keyframes starsTwinkle {
    0% { opacity: 0.65; }
    50% { opacity: 0.95; }
    100% { opacity: 0.70; }
}

/* Main Container */
.main .block-container {
    max-width: 740px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
    position: relative;
    z-index: 1;
}

/* Apple Header */
.apple-header {
    text-align: center;
    margin-bottom: 1.6rem;
    padding: 1.2rem 1rem;
}

.logo-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 16px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.14);
    backdrop-filter: blur(16px);
    font-size: 0.8rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: #e2e8f0;
    text-transform: uppercase;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    margin-bottom: 0.8rem;
}

.logo-badge-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #38bdf8;
    box-shadow: 0 0 10px #38bdf8;
}

.brand-title {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    color: #ffffff;
    margin: 0;
    line-height: 1.15;
    text-shadow: 0 0 40px rgba(255, 255, 255, 0.3);
}

.brand-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    margin-top: 0.7rem;
    font-weight: 400;
    letter-spacing: -0.01em;
    line-height: 1.55;
}

/* Glassmorphism Card Style */
.glass-card {
    background: rgba(15, 23, 42, 0.65);
    backdrop-filter: blur(28px) saturate(180%);
    -webkit-backdrop-filter: blur(28px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 24px;
    padding: 1.8rem;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.15);
    margin-bottom: 1.2rem;
    position: relative;
    overflow: hidden;
}

.glass-card::before {
    content: "";
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
}

/* 4-Digit Cosmic Code Presentation */
.code-display-wrap {
    text-align: center;
    padding: 1.2rem 0.5rem;
}

.code-boxes {
    display: inline-flex;
    gap: 14px;
    justify-content: center;
    align-items: center;
    margin: 1rem 0;
}

.code-digit {
    width: 70px;
    height: 86px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.08);
    border: 1.5px solid rgba(255, 255, 255, 0.25);
    border-radius: 18px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.2rem;
    font-weight: 800;
    color: #ffffff;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35), inset 0 2px 4px rgba(255, 255, 255, 0.2);
    text-shadow: 0 0 18px rgba(56, 189, 248, 0.7);
}

/* Meta Pill Badges */
.pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 999px;
    background: rgba(255, 255, 255, 0.07);
    border: 1px solid rgba(255, 255, 255, 0.12);
    font-size: 0.85rem;
    color: #cbd5e1;
    font-weight: 500;
}

.pill-badge-warning {
    background: rgba(245, 158, 11, 0.15);
    border-color: rgba(245, 158, 11, 0.35);
    color: #fde68a;
}

.pill-badge-success {
    background: rgba(16, 185, 129, 0.15);
    border-color: rgba(16, 185, 129, 0.35);
    color: #a7f3d0;
}

/* File Info Row */
.file-info-box {
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 1.2rem;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    margin-top: 1rem;
}

.file-icon-box {
    font-size: 2.2rem;
    width: 58px;
    height: 58px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: rgba(255, 255, 255, 0.06);
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

/* Centered PIN input */
div[data-testid="stTextInput"] input {
    text-align: center !important;
    letter-spacing: 12px !important;
    font-size: 1.8rem !important;
    font-weight: 800 !important;
    font-family: 'JetBrains Mono', monospace !important;
    background: rgba(255, 255, 255, 0.06) !important;
    border: 1.5px solid rgba(255, 255, 255, 0.2) !important;
    border-radius: 18px !important;
    color: #ffffff !important;
    padding: 0.9rem !important;
}

div[data-testid="stTextInput"] input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 20px rgba(56, 189, 248, 0.4) !important;
}

/* Streamlit Button Styling */
.stButton>button {
    width: 100%;
    border-radius: 16px !important;
    padding: 0.75rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    border: 1px solid rgba(255, 255, 255, 0.2) !important;
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.5) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 15px 35px -5px rgba(99, 102, 241, 0.7) !important;
    border-color: rgba(255, 255, 255, 0.35) !important;
}

.stDownloadButton>button {
    width: 100%;
    border-radius: 16px !important;
    padding: 0.9rem 1.5rem !important;
    font-weight: 700 !important;
    font-size: 1.15rem !important;
    background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255, 255, 255, 0.25) !important;
    box-shadow: 0 10px 30px -5px rgba(16, 185, 129, 0.5) !important;
    transition: all 0.25s ease !important;
}

.stDownloadButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 16px 40px -5px rgba(16, 185, 129, 0.7) !important;
}

/* File Uploader Custom Dark Glass */
[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1.5px dashed rgba(255, 255, 255, 0.2) !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
    transition: all 0.2s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #38bdf8 !important;
    background: rgba(56, 189, 248, 0.04) !important;
}

/* Hide streamlit default chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>

<!-- Animated Cosmic Background Elements -->
<div class="cosmic-nebula">
    <div class="nebula-glow-1"></div>
    <div class="nebula-glow-2"></div>
    <div class="nebula-glow-3"></div>
    <div class="stars-overlay"></div>
    <div class="shooting-star-1"></div>
    <div class="shooting-star-2"></div>
    <div class="shooting-star-3"></div>
</div>
"""

st.markdown(COSMIC_CSS, unsafe_allow_html=True)

# ==========================================
# State Management & URL Parameters
# ==========================================
url_code = ""
if "code" in st.query_params:
    raw_code = st.query_params.get("code")
    if raw_code and len(raw_code) == 4 and raw_code.isdigit():
        url_code = raw_code

if "current_mode" not in st.session_state:
    st.session_state.current_mode = "📥 파일 받기 (Receive)" if url_code else "🚀 파일 보내기 (Send)"

if "sent_code" not in st.session_state:
    st.session_state.sent_code = None

if "sent_file_meta" not in st.session_state:
    st.session_state.sent_file_meta = None

# ==========================================
# Apple-Inspired Sleek Header
# ==========================================
st.markdown("""
<div class="apple-header">
    <div class="logo-badge">
        <span class="logo-badge-dot"></span>
        <span>Zero-Login Secure Transfer</span>
    </div>
    <h1 class="brand-title">✦ JET SEND STAR</h1>
    <p class="brand-subtitle">
        우주처럼 빠르고 가벼운 1회용 무로그인 파일 전송<br>
        USB나 이메일 로그인 없이, <b>4자리 코드</b>나 <b>QR</b>로 발표 컴퓨터에서 즉시 다운로드하세요.
    </p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# Mode Selection (Segmented Control)
# ==========================================
mode_options = ["🚀 파일 보내기 (Send)", "📥 파일 받기 (Receive)"]
default_idx = 1 if url_code or st.session_state.current_mode == "📥 파일 받기 (Receive)" else 0

selected_mode = st.segmented_control(
    "전송 모드 선택",
    mode_options,
    default=mode_options[default_idx],
    label_visibility="collapsed"
)

if selected_mode:
    st.session_state.current_mode = selected_mode

# ==========================================
# 1. SEND MODE (파일 보내기)
# ==========================================
if st.session_state.current_mode == "🚀 파일 보내기 (Send)":
    
    # If a file was just sent and still active in session
    if st.session_state.sent_code:
        meta = st.session_state.sent_file_meta
        active_code = st.session_state.sent_code
        
        # Verify still in db
        db_file = get_file_from_db(active_code)
        if not db_file:
            st.session_state.sent_code = None
            st.session_state.sent_file_meta = None
            st.rerun()
            
        remaining_seconds = max(0, int(meta["expires_at"] - time.time()))
        rem_min = remaining_seconds // 60
        rem_sec = remaining_seconds % 60
        
        icon, cat_name, _ = get_file_meta_info(meta["filename"])
        local_ip = get_local_ip()
        transfer_url = f"http://{local_ip}:8501/?code={active_code}"
        qr_bytes = generate_qr_image(transfer_url)
        
        st.markdown(f"""
        <div class="glass-card">
            <div style="text-align: center;">
                <span class="pill-badge pill-badge-success">✨ 우주 전송 준비 완료</span>
                <h2 style="font-size: 1.6rem; margin: 0.8rem 0 0.3rem 0; color: #ffffff;">4자리 전송 코드 발급</h2>
                <p style="color: #94a3b8; font-size: 0.95rem; margin-bottom: 0.8rem;">
                    수신자 컴퓨터에서 아래 4자리 코드를 입력하거나 스마트폰 QR로 즉시 다운로드하세요.
                </p>
            </div>
            
            <div class="code-display-wrap">
                <div class="code-boxes">
                    <div class="code-digit">{active_code[0]}</div>
                    <div class="code-digit">{active_code[1]}</div>
                    <div class="code-digit">{active_code[2]}</div>
                    <div class="code-digit">{active_code[3]}</div>
                </div>
                <div style="margin-top: 0.5rem;">
                    <span class="pill-badge pill-badge-warning">
                        ⏱️ 만료까지 남은 시간: {rem_min:02d}분 {rem_sec:02d}초
                    </span>
                </div>
            </div>
            
            <div class="file-info-box">
                <div class="file-icon-box">{icon}</div>
                <div style="flex: 1; overflow: hidden;">
                    <div style="font-weight: 600; color: #f8fafc; font-size: 1.05rem; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">
                        {meta["filename"]}
                    </div>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 3px;">
                        {cat_name} • {format_size(meta["filesize"])} • {meta["duration"]}분 유효
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # QR Code and direct link
        col_qr, col_info = st.columns([1, 1], gap="medium")
        
        with col_qr:
            st.markdown("""
            <div style="text-align: center; margin-bottom: 0.5rem; color: #cbd5e1; font-weight: 500; font-size: 0.9rem;">
                📱 모바일 / 발표 PC 카메라 스캔
            </div>
            """, unsafe_allow_html=True)
            st.image(qr_bytes, caption="QR 코드로 빠른 접속", use_container_width=True)
            
        with col_info:
            st.markdown("""
            <div style="padding-top: 0.8rem;">
                <div style="font-weight: 600; color: #e2e8f0; font-size: 0.95rem; margin-bottom: 0.5rem;">
                    🔗 발표 PC 다이렉트 링크
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.code(transfer_url, language="bash")
            st.caption(f"로컬 테스트 링크: http://localhost:8501/?code={active_code}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ 전송 취소 및 즉시 파기", use_container_width=True):
                delete_file_from_db(active_code)
                st.session_state.sent_code = None
                st.session_state.sent_file_meta = None
                st.toast("파일이 영구적으로 파기되었습니다.", icon="🗑️")
                time.sleep(0.5)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 다른 새 파일 전송하기", use_container_width=True):
            st.session_state.sent_code = None
            st.session_state.sent_file_meta = None
            st.rerun()

    else:
        # File Upload UI
        st.markdown("""
        <div class="glass-card">
            <h3 style="font-size: 1.3rem; margin-top: 0; margin-bottom: 0.5rem; color: #ffffff;">
                📤 보낼 파일 선택
            </h3>
            <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.2rem;">
                프레젠테이션 PPT, PDF, 압축파일, 이미지 등 어떤 파일이든 드래그하여 놓으세요.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "파일을 드래그하거나 클릭하여 업로드",
            type=None,
            help="최대 500MB까지 초고속 전송 지원",
            label_visibility="collapsed"
        )
        
        if uploaded_file is not None:
            icon, cat_name, _ = get_file_meta_info(uploaded_file.name)
            
            st.markdown(f"""
            <div class="file-info-box" style="margin-bottom: 1.2rem;">
                <div class="file-icon-box">{icon}</div>
                <div style="flex: 1; overflow: hidden;">
                    <div style="font-weight: 600; color: #ffffff; font-size: 1.05rem;">
                        {uploaded_file.name}
                    </div>
                    <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 3px;">
                        {cat_name} • {format_size(uploaded_file.size)}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Transmission settings
            st.markdown("""
            <div style="color: #e2e8f0; font-size: 0.95rem; font-weight: 600; margin-bottom: 0.5rem;">
                ⚙️ 보안 및 유효 시간 설정
            </div>
            """, unsafe_allow_html=True)
            
            duration_choice = st.radio(
                "보관 유효 시간",
                options=[10, 5, 30, 60],
                format_func=lambda x: {
                    5: "⚡ 5분 (초단기 보안 전송)",
                    10: "⭐ 10분 (발표 시작 전 권장)",
                    30: "⏱️ 30분 (강의 / 세미나용)",
                    60: "⏳ 1시간 (장시간 회의)"
                }[x],
                index=0,
                horizontal=True,
                label_visibility="collapsed"
            )
            
            burn_choice = st.checkbox(
                "🔥 1회 다운로드 즉시 영구 파기 (공공장소 PC 보안 극대화)",
                value=False,
                help="수신자가 파일을 1회 다운로드 완료하는 즉시 서버와 DB에서 영구 삭제됩니다."
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✦ 우주로 초고속 발사 (코드 & QR 생성)", use_container_width=True):
                with st.spinner("우주 전송 채널 암호화 및 4자리 코드 생성 중..."):
                    file_bytes = uploaded_file.getvalue()
                    code = generate_unique_code()
                    expires_at = save_file_to_db(
                        code=code,
                        filename=uploaded_file.name,
                        filesize=uploaded_file.size,
                        filetype=uploaded_file.type or "application/octet-stream",
                        data_bytes=file_bytes,
                        duration_minutes=duration_choice,
                        burn=burn_choice
                    )
                    
                    st.session_state.sent_code = code
                    st.session_state.sent_file_meta = {
                        "filename": uploaded_file.name,
                        "filesize": uploaded_file.size,
                        "duration": duration_choice,
                        "expires_at": expires_at,
                        "burn": burn_choice
                    }
                    
                    st.toast("파일이 성공적으로 우주에 등록되었습니다! 🚀", icon="✦")
                    time.sleep(0.4)
                    st.rerun()

# ==========================================
# 2. RECEIVE MODE (파일 받기)
# ==========================================
elif st.session_state.current_mode == "📥 파일 받기 (Receive)":
    
    st.markdown("""
    <div class="glass-card">
        <h3 style="font-size: 1.3rem; margin-top: 0; margin-bottom: 0.5rem; color: #ffffff;">
            📥 파일 수신 (로그인 없음)
        </h3>
        <p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 1.2rem;">
            전송자가 알려준 <b>4자리 숫자 코드</b>를 입력하여 즉시 안전하게 다운로드하세요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input field for 4-digit code
    initial_val = url_code if url_code else ""
    code_input = st.text_input(
        "4자리 전송 코드 입력",
        value=initial_val,
        max_chars=4,
        placeholder="----",
        help="숫자 4자리를 입력하세요"
    )
    
    target_code = code_input.strip()
    
    if target_code and len(target_code) == 4 and target_code.isdigit():
        file_record = get_file_from_db(target_code)
        
        if file_record:
            rem_sec = max(0, int(file_record["expires_at"] - time.time()))
            rem_m = rem_sec // 60
            rem_s = rem_sec % 60
            
            icon, cat_name, _ = get_file_meta_info(file_record["filename"])
            burn_tag = "🔥 1회 다운로드 즉시 파기 파일" if file_record["burn_after_download"] else "⏳ 시간 만료 시 자동 파기"
            
            st.markdown(f"""
            <div class="glass-card" style="border-color: rgba(56, 189, 248, 0.35);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                    <span class="pill-badge pill-badge-success">✅ 파일 발견</span>
                    <span class="pill-badge pill-badge-warning">⏱️ {rem_m:02d}분 {rem_s:02d}초 후 만료</span>
                </div>
                
                <div class="file-info-box" style="margin-top: 0.5rem;">
                    <div class="file-icon-box">{icon}</div>
                    <div style="flex: 1; overflow: hidden;">
                        <div style="font-weight: 700; color: #ffffff; font-size: 1.2rem; text-overflow: ellipsis; white-space: nowrap; overflow: hidden;">
                            {file_record["filename"]}
                        </div>
                        <div style="color: #94a3b8; font-size: 0.9rem; margin-top: 4px;">
                            {cat_name} • <b>{format_size(file_record["filesize"])}</b>
                        </div>
                    </div>
                </div>
                
                <div style="margin-top: 1rem; font-size: 0.85rem; color: #cbd5e1; display: flex; align-items: center; gap: 8px;">
                    <span>🛡️ {burn_tag}</span>
                    <span>•</span>
                    <span>다운로드 횟수: {file_record["downloads_count"]}회</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Download Button
            download_clicked = st.download_button(
                label=f"⬇️ '{file_record['filename']}' 다운로드 시작",
                data=file_record["data"],
                file_name=file_record["filename"],
                mime=file_record["filetype"],
                use_container_width=True,
                key=f"dl_{target_code}"
            )
            
            if download_clicked:
                record_download_in_db(target_code)
                if file_record["burn_after_download"]:
                    st.balloons()
                    st.success("🎉 다운로드가 완료되었으며, 보안 설정에 따라 파일이 우주에서 즉시 파기되었습니다!")
                else:
                    st.balloons()
                    st.success("🎉 다운로드가 시작되었습니다! 성공적인 프레젠테이션 되세요.")
                    
        else:
            st.markdown(f"""
            <div class="glass-card" style="border-color: rgba(239, 68, 68, 0.4); text-align: center;">
                <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🌌</div>
                <h4 style="color: #f87171; margin-top: 0; font-size: 1.15rem;">파일을 찾을 수 없습니다</h4>
                <p style="color: #94a3b8; font-size: 0.9rem; margin: 0.5rem 0 0 0;">
                    코드 [<b>{target_code}</b>]에 해당하는 파일이 없거나, 유효시간이 만료되어 우주 너머로 안전하게 파기되었습니다.<br>
                    4자리 코드를 다시 확인해 주세요.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    elif target_code and len(target_code) < 4:
        st.info("💡 4자리 숫자를 모두 입력하시면 자동으로 파일이 조회됩니다.")

# ==========================================
# Apple-style Minimal Footer
# ==========================================
st.markdown("""
<div style="text-align: center; margin-top: 3.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.08); color: #64748b; font-size: 0.8rem; letter-spacing: -0.01em;">
    <div style="display: flex; justify-content: center; gap: 16px; margin-bottom: 0.6rem; color: #94a3b8; font-weight: 500;">
        <span>🔒 No Logins</span>
        <span>•</span>
        <span>⏱️ Auto-Destruct</span>
        <span>•</span>
        <span>📱 Mobile QR Ready</span>
        <span>•</span>
        <span>⚡ Pure SQLite3</span>
    </div>
    Jet Send Star © 2026 • Designed for Frictionless Presentations
</div>
""", unsafe_allow_html=True)
