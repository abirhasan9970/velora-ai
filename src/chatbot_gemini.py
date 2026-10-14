"""
Velora AI - Enhanced Gemini Style
PDF Export + Chat Search + Pin Chats + Live Clock
"""
import sys
from pathlib import Path
from datetime import datetime
import pickle

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import streamlit.components.v1 as components
from src.agent.agent import Agent
from fpdf import FPDF

st.set_page_config(
    page_title="Velora AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #020814 0%, #050e20 50%, #020814 100%);
    }
    section[data-testid="stSidebar"] {
        background: #0a1428 !important;
        border-right: 1px solid rgba(0, 217, 255, 0.15);
    }
    h1, h2, h3 { color: #E0F4FF !important; }
    
    .header-box {
        background: rgba(10, 20, 45, 0.6);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 16px;
        padding: 18px 24px;
        margin-bottom: 18px;
    }
    .header-title {
        background: linear-gradient(90deg, #00D9FF, #9B59FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 22px;
        font-weight: 800;
        margin: 0;
    }
    .welcome-title {
        font-size: 44px;
        font-weight: 800;
        background: linear-gradient(90deg, #00D9FF, #9B59FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 20px 0 10px 0;
    }
    .welcome-sub {
        color: #8DB8D9;
        text-align: center;
        font-size: 15px;
        margin-bottom: 30px;
    }
    .orb {
        width: 160px; height: 160px; margin: 30px auto; border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, #E0F4FF 0%, #00D9FF 18%, #4A7BE8 45%, #1a2050 75%, #020814 100%);
        box-shadow: 0 0 60px rgba(0, 217, 255, 0.7);
    }
    [data-testid="stChatMessage"] {
        background: rgba(12, 22, 48, 0.65) !important;
        border: 1px solid rgba(0, 217, 255, 0.2) !important;
        border-radius: 14px !important;
        padding: 14px 18px !important;
        margin: 10px 0 !important;
    }
    [data-testid="stChatMessage"] p {
        color: #FFFFFF !important;
        font-size: 15px !important;
    }
    [data-testid="stChatMessage"] strong { color: #7EE5FF !important; }
    
    /* Pin badge styling */
    .pin-badge {
        display: inline-block;
        background: rgba(255, 200, 0, 0.2);
        color: #FFD700;
        padding: 1px 6px;
        border-radius: 4px;
        font-size: 10px;
        margin-left: 4px;
    }
    
    /* ============================================================
   FORCE MODERN COLORFUL THEME - OVERRIDE ALL WHITE
   ============================================================ */
   
   /* ==== GLOBAL BUTTON OVERRIDE ==== */
   button, .stButton > button, [data-testid="stBaseButton-secondary"] {
       background: linear-gradient(135deg, #0090B8 0%, #00D9FF 100%) !important;
       color: #020814 !important;
       border: 1px solid rgba(0, 217, 255, 0.6) !important;
       border-radius: 12px !important;
       font-weight: 800 !important;
       transition: all 0.3s !important;
       box-shadow: 0 4px 16px rgba(0, 217, 255, 0.4) !important;
   }
   button:hover, .stButton > button:hover {
       background: linear-gradient(135deg, #00D9FF 0%, #7EE5FF 100%) !important;
       transform: translateY(-2px) !important;
       box-shadow: 0 8px 28px rgba(0, 217, 255, 0.7) !important;
   }
   
   /* ==== Suggestion Buttons (Try asking) ==== */
   .stButton > button[kind="secondary"] {
       background: linear-gradient(135deg, 
           rgba(0, 217, 255, 0.15) 0%, 
           rgba(155, 89, 255, 0.15) 100%) !important;
       color: #E0F4FF !important;
       border: 1px solid rgba(0, 217, 255, 0.4) !important;
       font-weight: 700 !important;
       text-align: left !important;
       padding: 14px 20px !important;
   }
   .stButton > button[kind="secondary"]:hover {
       background: linear-gradient(135deg, 
           rgba(0, 217, 255, 0.35) 0%, 
           rgba(155, 89, 255, 0.35) 100%) !important;
       border-color: #00D9FF !important;
       box-shadow: 0 0 30px rgba(0, 217, 255, 0.5) !important;
   }
   
   /* ==== SIDEBAR Chat Buttons ==== */
   section[data-testid="stSidebar"] button {
       background: rgba(0, 217, 255, 0.1) !important;
       color: #E0F4FF !important;
       border: 1px solid rgba(0, 217, 255, 0.25) !important;
       font-weight: 600 !important;
       box-shadow: none !important;
   }
   section[data-testid="stSidebar"] button:hover {
       background: rgba(0, 217, 255, 0.25) !important;
       border-color: #00D9FF !important;
       box-shadow: 0 0 15px rgba(0, 217, 255, 0.4) !important;
   }
   
   /* ==== New Chat (Primary) ==== */
   section[data-testid="stSidebar"] button[kind="primary"] {
       background: linear-gradient(135deg, #FF4757, #FF6B9D) !important;
       color: #FFFFFF !important;
       border: 1px solid rgba(255, 107, 157, 0.7) !important;
       font-weight: 800 !important;
       box-shadow: 0 4px 20px rgba(255, 71, 87, 0.6) !important;
   }
   section[data-testid="stSidebar"] button[kind="primary"]:hover {
       background: linear-gradient(135deg, #FF6B9D, #FF4757) !important;
       box-shadow: 0 8px 32px rgba(255, 71, 87, 0.9) !important;
       transform: translateY(-2px) !important;
   }
   
   /* ==== EXPANDER (Attach Image) - Dark ==== */
   [data-testid="stExpander"] {
       background: rgba(10, 20, 45, 0.7) !important;
       border: 1px solid rgba(0, 217, 255, 0.3) !important;
       border-radius: 14px !important;
       overflow: hidden !important;
   }
   [data-testid="stExpander"] summary, 
   [data-testid="stExpander"] > details > summary {
       background: linear-gradient(90deg, 
           rgba(0, 217, 255, 0.12) 0%, 
           rgba(155, 89, 255, 0.12) 100%) !important;
       color: #E0F4FF !important;
       font-weight: 700 !important;
       padding: 14px 20px !important;
       border-radius: 14px !important;
   }
   [data-testid="stExpander"] summary:hover {
       background: linear-gradient(90deg, 
           rgba(0, 217, 255, 0.25) 0%, 
           rgba(155, 89, 255, 0.25) 100%) !important;
   }
   
   /* ==== TEXT INPUT (Search) - Dark ==== */
   input[type="text"], input[type="search"], 
   .stTextInput input, [data-testid="stTextInput"] input {
       background: rgba(10, 20, 45, 0.85) !important;
       color: #E0F4FF !important;
       border: 1.5px solid rgba(0, 217, 255, 0.35) !important;
       border-radius: 12px !important;
       font-weight: 600 !important;
       padding: 12px 16px !important;
   }
   input[type="text"]::placeholder, 
   .stTextInput input::placeholder {
       color: #6B8BA8 !important;
       font-weight: 500 !important;
   }
   input[type="text"]:focus, .stTextInput input:focus {
       border-color: #00D9FF !important;
       box-shadow: 0 0 25px rgba(0, 217, 255, 0.5) !important;
   }
   
   /* ==== CHAT INPUT ==== */
   textarea[data-testid="stChatInputTextArea"],
   .stChatInput textarea {
       background: rgba(10, 20, 45, 0.9) !important;
       color: #E0F4FF !important;
       border: 1.5px solid rgba(0, 217, 255, 0.4) !important;
       border-radius: 14px !important;
       font-size: 15px !important;
       font-weight: 500 !important;
   }
   textarea[data-testid="stChatInputTextArea"]::placeholder {
       color: #6B8BA8 !important;
   }
   textarea[data-testid="stChatInputTextArea"]:focus {
       border-color: #00D9FF !important;
       box-shadow: 0 0 30px rgba(0, 217, 255, 0.6) !important;
   }
   
   /* ==== FILE UPLOADER ==== */
   [data-testid="stFileUploader"], 
   [data-testid="stFileUploaderDropzone"] {
       background: rgba(10, 20, 45, 0.6) !important;
       border: 2px dashed rgba(0, 217, 255, 0.5) !important;
       border-radius: 14px !important;
   }
   [data-testid="stFileUploader"]:hover, 
   [data-testid="stFileUploaderDropzone"]:hover {
       border-color: #00D9FF !important;
       box-shadow: 0 0 25px rgba(0, 217, 255, 0.3) !important;
       background: rgba(10, 20, 45, 0.85) !important;
   }
   [data-testid="stFileUploader"] span, 
   [data-testid="stFileUploader"] p,
   [data-testid="stFileUploader"] small {
       color: #E0F4FF !important;
   }
   
   /* ==== DOWNLOAD BUTTONS (Export) ==== */
   [data-testid="stDownloadButton"] button {
       background: linear-gradient(135deg, #7C3AED 0%, #C77DFF 100%) !important;
       color: #FFFFFF !important;
       border: 1px solid rgba(199, 125, 255, 0.6) !important;
       font-weight: 800 !important;
       border-radius: 12px !important;
       box-shadow: 0 4px 18px rgba(124, 58, 237, 0.5) !important;
   }
   [data-testid="stDownloadButton"] button:hover {
       background: linear-gradient(135deg, #9B59FF 0%, #C77DFF 100%) !important;
       box-shadow: 0 8px 32px rgba(155, 89, 255, 0.8) !important;
       transform: translateY(-2px) !important;
   }
   
   /* ==== CHECKBOX / RADIO ==== */
   .stCheckbox, .stRadio {
       background: transparent !important;
   }
   .stCheckbox label, .stRadio label,
   .stCheckbox p, .stRadio p {
       color: #E0F4FF !important;
   }
   
   /* ==== SIDEBAR INPUT (Search) ==== */
   section[data-testid="stSidebar"] input {
       background: rgba(0, 217, 255, 0.08) !important;
       color: #E0F4FF !important;
       border: 1px solid rgba(0, 217, 255, 0.3) !important;
       border-radius: 10px !important;
   }
   section[data-testid="stSidebar"] input::placeholder {
       color: #6B8BA8 !important;
   }
   
   /* ==== METRIC / STATS ==== */
   [data-testid="stMetricValue"] {
       color: #7EE5FF !important;
       font-weight: 800 !important;
   }
   
   /* ==== SPINNER ==== */
   .stSpinner > div {
       border-top-color: #00D9FF !important;
   }
   
   /* ==== SCROLLBAR ==== */
   ::-webkit-scrollbar {
       width: 8px;
       height: 8px;
   }
   ::-webkit-scrollbar-track {
       background: rgba(10, 20, 45, 0.5);
   }
   ::-webkit-scrollbar-thumb {
       background: linear-gradient(135deg, #0090B8, #9B59FF);
       border-radius: 4px;
   }
   ::-webkit-scrollbar-thumb:hover {
       background: linear-gradient(135deg, #00D9FF, #C77DFF);
   }
   
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* ============================================================
       MODERN COLORFUL STYLES
       ============================================================ */
    
    /* ==== All Buttons (Main Content) - Gradient ==== */
    .stButton > button {
        background: linear-gradient(135deg, #0090B8 0%, #00D9FF 50%, #9B59FF 100%) !important;
        color: #020814 !important;
        border: 1px solid rgba(0, 217, 255, 0.5) !important;
        border-radius: 12px !important;
        padding: 10px 18px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 16px rgba(0, 217, 255, 0.3),
                    inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(0, 217, 255, 0.6),
                    inset 0 1px 0 rgba(255, 255, 255, 0.3) !important;
        border-color: #7EE5FF !important;
    }
    
    /* ==== Sidebar Buttons ==== */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(0, 217, 255, 0.1) !important;
        color: #E0F4FF !important;
        border: 1px solid rgba(0, 217, 255, 0.25) !important;
        box-shadow: none !important;
        font-size: 13px !important;
        padding: 8px 12px !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(0, 217, 255, 0.25) !important;
        border-color: #00D9FF !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.4) !important;
    }
    
    /* ==== New Chat Button (Primary) - Special ==== */
    section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF4757, #FF6B9D) !important;
        color: white !important;
        border: 1px solid rgba(255, 107, 157, 0.6) !important;
        font-weight: 800 !important;
        box-shadow: 0 4px 18px rgba(255, 71, 87, 0.5) !important;
    }
    section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #FF6B9D, #FF4757) !important;
        box-shadow: 0 8px 30px rgba(255, 71, 87, 0.8) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ==== Expander (Attach Image) - Dark Modern ==== */
    [data-testid="stExpander"] {
        background: rgba(10, 20, 45, 0.6) !important;
        border: 1px solid rgba(0, 217, 255, 0.25) !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        margin: 8px 0 !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(0, 217, 255, 0.5) !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.2) !important;
    }
    [data-testid="stExpander"] summary {
        background: linear-gradient(90deg, rgba(0,217,255,0.1), rgba(155,89,255,0.1)) !important;
        color: #E0F4FF !important;
        font-weight: 700 !important;
        padding: 12px 18px !important;
    }
    [data-testid="stExpander"] summary:hover {
        background: linear-gradient(90deg, rgba(0,217,255,0.2), rgba(155,89,255,0.2)) !important;
    }
    [data-testid="stExpander"] > div {
        background: transparent !important;
    }
    
    /* ==== Text Input (Search box) - Dark ==== */
    .stTextInput > div > div > input {
        background: rgba(10, 20, 45, 0.8) !important;
        color: #E0F4FF !important;
        border: 1px solid rgba(0, 217, 255, 0.3) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-size: 14px !important;
        transition: all 0.3s !important;
    }
    .stTextInput > div > div > input::placeholder {
        color: #6B8BA8 !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00D9FF !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.4) !important;
        background: rgba(10, 20, 45, 0.95) !important;
    }
    
    /* ==== File Uploader - Dark Modern ==== */
    [data-testid="stFileUploader"] {
        background: rgba(10, 20, 45, 0.6) !important;
        border: 2px dashed rgba(0, 217, 255, 0.4) !important;
        border-radius: 14px !important;
        padding: 15px !important;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #00D9FF !important;
        background: rgba(10, 20, 45, 0.8) !important;
        box-shadow: 0 0 25px rgba(0, 217, 255, 0.2) !important;
    }
    [data-testid="stFileUploader"] label {
        color: #E0F4FF !important;
    }
    [data-testid="stFileUploaderDropzone"] {
        background: rgba(0, 217, 255, 0.05) !important;
        border-radius: 10px !important;
    }
    [data-testid="stFileUploader"] button {
        background: linear-gradient(135deg, #0090B8, #00D9FF) !important;
        color: #020814 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
    }
    
    /* ==== Voice Panel Buttons - Glowing ==== */
    [data-testid="stMarkdownContainer"] button {
        transition: all 0.3s !important;
    }
    
    /* ==== Download Buttons ==== */
    [data-testid="stDownloadButton"] > button {
        background: linear-gradient(135deg, #7C3AED, #C77DFF) !important;
        color: white !important;
        border: 1px solid rgba(199, 125, 255, 0.5) !important;
        font-weight: 700 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4) !important;
    }
    [data-testid="stDownloadButton"] > button:hover {
        background: linear-gradient(135deg, #9B59FF, #C77DFF) !important;
        box-shadow: 0 8px 28px rgba(155, 89, 255, 0.7) !important;
        transform: translateY(-2px) !important;
    }
    
    /* ==== Radio / Checkbox ==== */
    .stCheckbox label, .stRadio label {
        color: #E0F4FF !important;
    }
    
    /* ==== Chat Input - Enhanced ==== */
    .stChatInput > div > div > textarea {
        background: rgba(10, 20, 45, 0.9) !important;
        border: 1.5px solid rgba(0, 217, 255, 0.4) !important;
        border-radius: 14px !important;
        color: #E0F4FF !important;
        font-size: 15px !important;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #00D9FF !important;
        box-shadow: 0 0 30px rgba(0, 217, 255, 0.5) !important;
    }
    
    /* ==== Spinner ==== */
    .stSpinner > div {
        border-color: #00D9FF !important;
        border-right-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================
CHAT_DIR = ROOT / "data" / "chats"
CHAT_DIR.mkdir(parents=True, exist_ok=True)


def save_data():
    try:
        with open(CHAT_DIR / "convs.pkl", "wb") as f:
            pickle.dump(st.session_state.convs, f)
        with open(CHAT_DIR / "active.txt", "w") as f:
            f.write(st.session_state.active)
    except Exception:
        pass


def load_data():
    convs = None
    active = None
    if (CHAT_DIR / "convs.pkl").exists():
        try:
            with open(CHAT_DIR / "convs.pkl", "rb") as f:
                convs = pickle.load(f)
        except Exception:
            pass
    if (CHAT_DIR / "active.txt").exists():
        try:
            active = (CHAT_DIR / "active.txt").read_text().strip()
        except Exception:
            pass
    return convs, active


def generate_pdf(messages, chat_title="Chat"):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 15, "Velora AI - Chat Export", ln=True, align="C")
        pdf.ln(2)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, f"Chat: {chat_title}", ln=True, align="C")
        pdf.cell(0, 8, f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align="C")
        pdf.ln(8)
        for m in messages:
            role = "You" if m["role"] == "user" else "Velora AI"
            pdf.set_font("Helvetica", "B", 12)
            if m["role"] == "user":
                pdf.set_text_color(0, 150, 255)
            else:
                pdf.set_text_color(100, 60, 200)
            pdf.cell(0, 8, role, ln=True)
            pdf.set_text_color(30, 30, 30)
            pdf.set_font("Helvetica", "", 11)
            c = m.get("content", "").replace("```", "")
            try:
                pdf.multi_cell(0, 7, c)
            except Exception:
                pdf.multi_cell(0, 7, c.encode("latin-1", "replace").decode("latin-1"))
            pdf.ln(4)
        return bytes(pdf.output())
    except Exception:
        return None


# ============================================================
# SESSION STATE
# ============================================================
if "convs" not in st.session_state:
    saved_convs, saved_active = load_data()
    if saved_convs:
        # Ensure pinned field exists
        for cid in saved_convs:
            if "pinned" not in saved_convs[cid]:
                saved_convs[cid]["pinned"] = False
        st.session_state.convs = saved_convs
        st.session_state.active = saved_active if saved_active in saved_convs else list(saved_convs.keys())[0]
    else:
        st.session_state.convs = {
            "chat_1": {"title": "New Chat", "messages": [], "pinned": False}
        }
        st.session_state.active = "chat_1"

if "counter" not in st.session_state:
    st.session_state.counter = len(st.session_state.convs)

if "agent" not in st.session_state:
    st.session_state.agent = None

if "quick" not in st.session_state:
    st.session_state.quick = None

if "search_query" not in st.session_state:
    st.session_state.search_query = ""


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 18px 0;">
        <div style="font-size: 36px;">✨</div>
        <div style="
            background: linear-gradient(90deg, #00D9FF, #9B59FF);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            font-size: 22px; font-weight: 800; margin: 4px 0 0 0;
        ">Velora AI</div>
        <div style="color:#6B8BA8; font-size:10px; letter-spacing:3px;">PREMIUM</div>
    </div>
    """, unsafe_allow_html=True)
    
    # LIVE CLOCK - JavaScript version (ticking every second)
    components.html("""
    <div style="
        text-align: center; padding: 14px 10px; margin: 8px 0 15px 0;
        border-radius: 14px;
        background: rgba(0, 217, 255, 0.08);
        border: 1px solid rgba(0, 217, 255, 0.25);
    ">
        <div id="sidebar-clock-time" style="
            font-size: 22px; font-weight: 800; letter-spacing: 1.5px;
            background: linear-gradient(90deg, #00D9FF, #9B59FF);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        ">--:--:--</div>
        <div id="sidebar-clock-date" style="
            color: #6B8BA8; font-size: 10px;
            margin-top: 4px; letter-spacing: 1.5px; font-weight: 600;
        ">Loading...</div>
    </div>
    <script>
        function updateSidebarClock() {
            var now = new Date();
            var t = now.toLocaleTimeString('en-US', {
                hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true
            });
            var d = now.toLocaleDateString('en-US', {
                weekday: 'short', day: '2-digit', month: 'short', year: 'numeric'
            }).toUpperCase();
            var tEl = document.getElementById('sidebar-clock-time');
            var dEl = document.getElementById('sidebar-clock-date');
            if (tEl) tEl.textContent = t;
            if (dEl) dEl.textContent = d;
        }
        updateSidebarClock();
        setInterval(updateSidebarClock, 1000);
    </script>
    """, height=100)
    
    # NEW CHAT BUTTON
    if st.button("➕  New Chat", use_container_width=True, key="new_chat_btn", type="primary"):
        st.session_state.counter += 1
        nid = f"chat_{st.session_state.counter}"
        st.session_state.convs[nid] = {"title": "New Chat", "messages": [], "pinned": False}
        st.session_state.active = nid
        save_data()
        st.rerun()
    
    # SEARCH BOX
    search = st.text_input("🔍 Search chats", placeholder="Type to search...", key="search_input",
                          label_visibility="collapsed")
    
    st.markdown("---")
    
    # PINNED CHATS
    pinned_chats = [(cid, c) for cid, c in st.session_state.convs.items() if c.get("pinned", False)]
    if pinned_chats:
        st.markdown('<p style="color:#FFD700; font-size:11px; font-weight:700; margin: 4px 0;">📌 PINNED</p>', unsafe_allow_html=True)
        for cid, conv in pinned_chats[::-1]:
            is_active = cid == st.session_state.active
            title = conv["title"][:20] + ("..." if len(conv["title"]) > 20 else "")
            icon = "🟡" if is_active else "🟠"
            if st.button(f"{icon} {title}", key=f"pin_{cid}", use_container_width=True):
                st.session_state.active = cid
                save_data()
                st.rerun()
        st.markdown("---")
    
    # RECENT CHATS
    st.markdown('<p style="color:#8DB8D9; font-size:12px; font-weight:600; margin: 4px 0;">📚 Recent Chats</p>', unsafe_allow_html=True)
    
    for cid, conv in list(st.session_state.convs.items())[::-1]:
        if conv.get("pinned", False):
            continue  # Skip pinned (already shown above)
        
        # Search filter
        if search:
            search_lower = search.lower()
            title_match = search_lower in conv["title"].lower()
            msg_match = any(search_lower in m.get("content", "").lower() for m in conv["messages"])
            if not (title_match or msg_match):
                continue
        
        is_active = cid == st.session_state.active
        title = conv["title"][:22] + ("..." if len(conv["title"]) > 22 else "")
        
        col1, col2 = st.columns([5, 1])
        with col1:
            if is_active:
                st.markdown(f"""
                <div style="
                    padding: 10px 12px; margin: 4px 0; border-radius: 10px;
                    background: linear-gradient(90deg, rgba(0,217,255,0.2), rgba(155,89,255,0.15));
                    border: 1px solid rgba(0,217,255,0.4);
                    color: #E0F4FF; font-size: 13px; font-weight: 600;
                    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
                ">🟢 {title}</div>
                """, unsafe_allow_html=True)
            else:
                if st.button(f"⚪ {title}", key=f"c_{cid}", use_container_width=True):
                    st.session_state.active = cid
                    save_data()
                    st.rerun()
        with col2:
            pin_icon = "📌" if conv.get("pinned", False) else "📍"
            if st.button(pin_icon, key=f"pbtn_{cid}", help="Pin/Unpin"):
                st.session_state.convs[cid]["pinned"] = not conv.get("pinned", False)
                save_data()
                st.rerun()
    
    st.markdown("---")
    
    # ACTIONS
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️", use_container_width=True, key="delete_chat", help="Delete chat"):
            if len(st.session_state.convs) > 1:
                del st.session_state.convs[st.session_state.active]
                st.session_state.active = list(st.session_state.convs.keys())[0]
                save_data()
                st.rerun()
    with c2:
        if st.button("🧹", use_container_width=True, key="clear_chat", help="Clear messages"):
            st.session_state.convs[st.session_state.active]["messages"] = []
            save_data()
            st.rerun()
    
    # EXPORT BUTTONS
    cur_msgs = st.session_state.convs[st.session_state.active]["messages"]
    if cur_msgs:
        cur_title = st.session_state.convs[st.session_state.active]["title"]
        txt = "\n\n".join([f"[{m['role'].upper()}]\n{m['content']}" for m in cur_msgs])
        st.download_button("📥 Export TXT", txt, file_name=f"{st.session_state.active}.txt",
                          mime="text/plain", use_container_width=True, key="export_txt")
        pdf_bytes = generate_pdf(cur_msgs, cur_title)
        if pdf_bytes:
            st.download_button("📄 Export PDF", pdf_bytes, file_name=f"{st.session_state.active}.pdf",
                              mime="application/pdf", use_container_width=True, key="export_pdf")
    
    # STATS
    total = sum(len(c["messages"]) for c in st.session_state.convs.values())
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center; color:#6B8BA8; font-size:11px; padding: 8px;">
        💬 {len(st.session_state.convs)} chats · ✉️ {total} messages
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# INIT AGENT
# ============================================================
if st.session_state.agent is None:
    try:
        with st.spinner("✨ Initializing AI..."):
            st.session_state.agent = Agent()
    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()


conv = st.session_state.convs[st.session_state.active]
msgs = conv["messages"]


# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="header-box">
    <div style="display:flex; justify-content:space-between; align-items:center;">
        <div style="display:flex; align-items:center; gap:14px;">
            <div style="
                width:46px; height:46px; border-radius:14px;
                background: linear-gradient(135deg, #00D9FF, #4A7BE8);
                display:flex; align-items:center; justify-content:center;
                font-size:22px;
            ">✨</div>
            <div>
                <h1 class="header-title">Velora AI</h1>
                <p style="color:#6B8BA8; margin:0; font-size:12px;">
                    Your intelligent assistant
                </p>
            </div>
        </div>
        <div style="color:#00FF88; font-size:13px; font-weight:700;">🟢 Online & Ready</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# VOICE
# ============================================================
components.html("""
<div style="display:flex; gap:10px; align-items:center; padding:10px 16px; 
            border-radius:12px; background:rgba(10,20,45,0.6);
            border:1px solid rgba(0,217,255,0.25);">
    <button id="vBtn" style="
        background:linear-gradient(135deg,#0090B8,#00D9FF);
        color:#020814; border:none; padding:8px 18px;
        border-radius:8px; font-size:13px; cursor:pointer; font-weight:700;
    ">🎤 Voice</button>
    <button id="sBtn" style="
        background:linear-gradient(135deg,#7C3AED,#9B59FF);
        color:white; border:none; padding:8px 18px;
        border-radius:8px; font-size:13px; cursor:pointer; font-weight:700;
    ">🔊 Read</button>
    <span id="st" style="color:#8DB8D9; font-size:13px;">Click 🎤 to speak</span>
</div>
<script>
    var vBtn=document.getElementById('vBtn'),sBtn=document.getElementById('sBtn'),st=document.getElementById('st');
    var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    var recog=null,listening=false;
    if(!SR){st.textContent='Voice needs Chrome';vBtn.disabled=true;}
    else{
        recog=new SR();recog.lang='en-US';
        vBtn.onclick=function(){
            if(!listening){recog.start();st.textContent='Listening...';listening=true;vBtn.textContent='Stop';}
            else recog.stop();
        };
        recog.onresult=function(e){
            var t=e.results[0][0].transcript;
            st.textContent='Heard: '+t;
            var d=window.parent.document;
            var i=d.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if(i){
                var s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
                s.call(i,t);
                i.dispatchEvent(new Event('input',{bubbles:true}));
                i.focus();
            }
        };
        recog.onerror=function(e){st.textContent='Error: '+e.error;reset();};
        recog.onend=reset;
        function reset(){vBtn.textContent='Voice';listening=false;}
    }
    sBtn.onclick=function(){
        var d=window.parent.document;
        var ms=d.querySelectorAll('[data-testid="stChatMessage"]');
        if(ms.length===0)return;
        var t='';
        for(var i=ms.length-1;i>=0;i--){t=ms[i].innerText;if(t&&t.trim().length>5)break;}
        if(!t)return;
        window.speechSynthesis.cancel();
        var u=new SpeechSynthesisUtterance(t);u.lang='en-US';
        window.speechSynthesis.speak(u);
    };
</script>
""", height=65)


# ============================================================
# IMAGE UPLOAD
# ============================================================
with st.expander("🖼️ Attach Image", expanded=False):
    st.markdown(
        '<p style="color:#8DB8D9; font-size:13px; margin-bottom:8px;">'
        'ছবি upload করো এবং নিচে description লিখো — AI সেই description ব্যবহার করবে।'
        '</p>',
        unsafe_allow_html=True,
    )
    uploaded_file = st.file_uploader(
        "Choose an image",
        type=["png", "jpg", "jpeg", "webp", "gif"],
        key="image_uploader",
        label_visibility="collapsed",
    )
    if uploaded_file is not None:
        # Preview
        col1, col2 = st.columns([1, 2])
        with col1:
            st.image(uploaded_file, caption="Preview", use_container_width=True)
        with col2:
            st.markdown(f"""
            <div style="background: rgba(0,217,255,0.08); border:1px solid rgba(0,217,255,0.25); 
                        border-radius: 10px; padding: 14px; margin-top: 10px;">
                <div style="color:#7EE5FF; font-size:13px; font-weight:700; margin-bottom:6px;">
                    📎 {uploaded_file.name}
                </div>
                <div style="color:#8DB8D9; font-size:12px;">
                    Size: {uploaded_file.size // 1024} KB<br>
                    Type: {uploaded_file.type}
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📎 Use with next message", key="use_image_btn", use_container_width=True):
                st.session_state.image_attached = {
                    "name": uploaded_file.name,
                    "size_kb": uploaded_file.size // 1024,
                }
                st.success(f"✅ '{uploaded_file.name}' পরবর্তী message এ পাঠানো হবে")

        # Show if attached
        if "image_attached" in st.session_state and st.session_state.image_attached:
            st.markdown(f"""
            <div style="background: rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.4); 
                        border-radius: 10px; padding: 10px; margin-top: 10px;">
                <span style="color:#00FF88; font-size:13px;">
                    📌 Attached: <b>{st.session_state.image_attached['name']}</b>
                </span>
            </div>
            """, unsafe_allow_html=True)
            if st.button("❌ Remove attachment", key="remove_img_btn"):
                st.session_state.image_attached = None
                st.rerun()


# ============================================================
# QUICK PROMPT
# ============================================================
if st.session_state.quick:
    p = st.session_state.quick
    st.session_state.quick = None
    msgs.append({"role": "user", "content": p})
    if len(msgs) == 1:
        conv["title"] = p[:30]
    with st.chat_message("user", avatar="🧑"):
        st.markdown(p)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                img_bytes = st.session_state.get("image_bytes") if hasattr(st.session_state, "image_bytes") else None
                img_mime = st.session_state.get("image_mime", "image/jpeg") if hasattr(st.session_state, "image_mime") else "image/jpeg"
                run = st.session_state.agent.run(p, image_bytes=img_bytes, image_mime=img_mime)
                st.session_state.image_bytes = None
                st.session_state.image_attached = None
                ans = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                ans = f"❌ {e}"
        st.markdown(ans)
    msgs.append({"role": "assistant", "content": ans})
    save_data()
    st.rerun()


# ============================================================
# WELCOME
# ============================================================
if len(msgs) == 0:
    st.markdown("""
    <div class="orb"></div>
    <h1 class="welcome-title">Hello, I'm Velora AI</h1>
    <p class="welcome-sub">Ask me anything · English · বাংলা · Coding · Math</p>
    """, unsafe_allow_html=True)
    
    st.markdown("### ✨ Try asking")
    suggs = [
        ("💻", "Python code", "Write a Python function to reverse a string"),
        ("🌌", "Explain concept", "Explain quantum computing in simple terms"),
        ("✍️", "Write poem", "Write a short poem about the stars"),
        ("🌏", "বাংলায় জিজ্ঞেস", "বাংলাদেশ সম্পর্কে ৫টি মজার তথ্য বলুন"),
        ("🧮", "Math", "What is 17 times 23?"),
        ("💡", "Advice", "How can I be more productive?"),
    ]
    cols = st.columns(3)
    for i, (icon, title, prompt) in enumerate(suggs):
        with cols[i % 3]:
            if st.button(f"{icon} {title}", use_container_width=True, key=f"s{i}"):
                st.session_state.quick = prompt
                st.rerun()


# ============================================================
# MESSAGES
# ============================================================
for m in msgs:
    avatar = "🧑" if m["role"] == "user" else "🤖"
    with st.chat_message(m["role"], avatar=avatar):
        st.markdown(m.get("content", ""))


# ============================================================
# INPUT
# ============================================================
ui = st.chat_input("✨ Type your message...")

if ui:
    msgs.append({"role": "user", "content": ui})
    if len(msgs) == 1:
        conv["title"] = ui[:30]
    with st.chat_message("user", avatar="🧑"):
        st.markdown(ui)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                img_bytes = st.session_state.get("image_bytes") if hasattr(st.session_state, "image_bytes") else None
                img_mime = st.session_state.get("image_mime", "image/jpeg") if hasattr(st.session_state, "image_mime") else "image/jpeg"
                run = st.session_state.agent.run(ui, image_bytes=img_bytes, image_mime=img_mime)
                # Clear image after use
                st.session_state.image_bytes = None
                st.session_state.image_attached = None
                ans = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                ans = f"❌ {e}"
        st.markdown(ans)
    msgs.append({"role": "assistant", "content": ans})
    save_data()
    st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#4A6B88; font-size:11px; letter-spacing:1.5px;">
    ✨ <strong style="color:#7EE5FF;">VELORA AI</strong> · PREMIUM · POWERED BY GEMINI
</p>
""", unsafe_allow_html=True)
