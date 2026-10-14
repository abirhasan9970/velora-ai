"""
Velora AI - Premium Edition
Modern glassmorphism chatbot with premium UI.
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

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Velora AI · Premium",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PREMIUM CSS - GLASSMORPHISM
# ============================================================
st.markdown("""
<style>
    /* ==== Background with Cosmic Glow ==== */
    .stApp {
        background: 
            radial-gradient(ellipse at 15% 25%, rgba(0, 217, 255, 0.18) 0%, transparent 40%),
            radial-gradient(ellipse at 85% 75%, rgba(155, 89, 255, 0.22) 0%, transparent 40%),
            radial-gradient(ellipse at 50% 50%, rgba(30, 100, 200, 0.15) 0%, transparent 60%),
            linear-gradient(135deg, #020814 0%, #050e20 50%, #020814 100%);
        background-attachment: fixed;
    }
    
    /* ==== Glassmorphism Sidebar ==== */
    [data-testid="stSidebar"] { background: rgba(8, 16, 36, 0.75); }
    [data-testid="stSidebar"] * {
        color: #E0F4FF;
    }
    
    /* ==== Main Container ==== */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
    
    /* ==== Headings ==== */
    h1, h2, h3 { 
        color: #E0F4FF !important;
        font-weight: 700 !important;
    }
    
    /* ==== Premium Header ==== */
    .premium-header {
        background: rgba(10, 20, 45, 0.5);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 18px;
        padding: 20px 28px;
        margin-bottom: 20px;
        box-shadow: 
            0 8px 32px rgba(0, 0, 0, 0.4),
            inset 0 1px 0 rgba(255, 255, 255, 0.05);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .premium-header h1 {
        margin: 0;
        background: linear-gradient(90deg, #00D9FF, #7EE5FF, #9B59FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 26px;
        font-weight: 800;
        letter-spacing: -0.02em;
    }
    .online-status {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #7EE5FF;
        font-size: 13px;
        font-weight: 600;
    }
    .online-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #00FF88;
        box-shadow: 0 0 12px #00FF88;
        animation: pulse 2s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50% { opacity: 0.6; transform: scale(1.2); }
    }
    
    /* ==== Hero Title ==== */
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        background: linear-gradient(90deg, #00D9FF, #9B59FF, #00D9FF);
        background-size: 200% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s linear infinite;
        text-align: center;
        margin: 20px 0 10px 0;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        100% { background-position: 200% 50%; }
    }
    .hero-subtitle {
        color: #8DB8D9;
        text-align: center;
        font-size: 15px;
        margin-bottom: 40px;
    }
    
    /* ==== Glowing Orb ==== */
    .orb {
        width: 180px;
        height: 180px;
        margin: 30px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, 
            #E0F4FF 0%, 
            #00D9FF 18%, 
            #4A7BE8 45%, 
            #1a2050 75%, 
            #020814 100%);
        box-shadow: 
            0 0 60px rgba(0, 217, 255, 0.7),
            0 0 120px rgba(74, 123, 232, 0.5),
            inset -25px -25px 60px rgba(0, 0, 0, 0.6),
            inset 15px 15px 40px rgba(126, 229, 255, 0.3);
        animation: orbFloat 5s ease-in-out infinite;
        position: relative;
    }
    @keyframes orbFloat {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-15px) scale(1.05); }
    }
    .orb::after {
        content: '';
        position: absolute;
        top: 18%;
        left: 22%;
        width: 40px;
        height: 40px;
        background: rgba(255, 255, 255, 0.6);
        border-radius: 50%;
        filter: blur(20px);
    }
    
    /* ==== Chat Messages - GLASS STYLE ==== */
    [data-testid="stChatMessage"] {
        background: rgba(15, 25, 55, 0.55) !important;
        backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 217, 255, 0.2) !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin: 10px 0 !important;
        animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
    }
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* ==== Chat Text - BRIGHT AND BOLD ==== */
    [data-testid="stChatMessage"] p,
    [data-testid="stChatMessage"] li,
    [data-testid="stChatMessage"] span {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        line-height: 1.7 !important;
    }
    [data-testid="stChatMessage"] strong,
    [data-testid="stChatMessage"] b {
        color: #7EE5FF !important;
        font-weight: 700 !important;
    }
    [data-testid="stChatMessage"] ol,
    [data-testid="stChatMessage"] ul {
        padding-left: 25px !important;
    }
    [data-testid="stChatMessage"] ol li,
    [data-testid="stChatMessage"] ul li {
        margin-bottom: 6px !important;
    }
    
    /* ==== Chat Input - Glass ==== */
    .stChatInput > div > div > textarea {
        background: rgba(10, 20, 45, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        border: 1px solid rgba(0, 217, 255, 0.35) !important;
        border-radius: 16px !important;
        color: #E0F4FF !important;
        font-size: 15px !important;
        padding: 14px 18px !important;
        transition: all 0.3s;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #00D9FF !important;
        box-shadow: 0 0 25px rgba(0, 217, 255, 0.5) !important;
    }
    
    /* ==== Buttons - Premium ==== */
    .stButton > button {
        background: linear-gradient(135deg, #0090B8, #00D9FF) !important;
        color: #020814 !important;
        border: 1px solid rgba(0, 217, 255, 0.6) !important;
        border-radius: 12px !important;
        padding: 10px 20px !important;
        font-weight: 700 !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 
            0 4px 15px rgba(0, 217, 255, 0.35),
            inset 0 0 15px rgba(0, 217, 255, 0.15);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 
            0 8px 25px rgba(0, 217, 255, 0.6),
            inset 0 0 25px rgba(0, 217, 255, 0.3) !important;
        border-color: #7EE5FF !important;
    }
    
    /* ==== Timestamp ==== */
    .msg-time {
        font-size: 11px;
        color: #6B8BA8;
        margin-top: 6px;
        letter-spacing: 0.3px;
        font-weight: 500;
    }
    
    /* ==== Sidebar Logo ==== */
    .sidebar-logo {
        text-align: center;
        padding: 15px 0;
        border-bottom: 1px solid rgba(0, 217, 255, 0.15);
        margin-bottom: 20px;
    }
    .sidebar-logo .logo-icon {
        font-size: 36px;
        margin-bottom: 8px;
    }
    .sidebar-logo .logo-title {
        background: linear-gradient(90deg, #00D9FF, #9B59FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 22px;
        font-weight: 800;
        margin: 0;
    }
    .sidebar-logo .logo-sub {
        color: #6B8BA8;
        font-size: 10px;
        letter-spacing: 2px;
        font-weight: 600;
        margin-top: 4px;
    }
    
    /* ==== Hide Streamlit ==== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ==== Divider ==== */
    hr {
        border-color: rgba(0, 217, 255, 0.15);
        margin: 20px 0;
    }
    
    /* ==== Code Blocks ==== */
    code {
        background: rgba(0, 217, 255, 0.15) !important;
        color: #7EE5FF !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    pre {
        background: rgba(5, 15, 35, 0.9) !important;
        border: 1px solid rgba(0, 217, 255, 0.3) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 20px rgba(0, 217, 255, 0.15);
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA
# ============================================================
CHAT_SAVE_DIR = ROOT / "data" / "chats"
CHAT_SAVE_DIR.mkdir(parents=True, exist_ok=True)


def save_conversations(convs):
    try:
        with open(CHAT_SAVE_DIR / "conversations.pkl", "wb") as f:
            pickle.dump(convs, f)
        return True
    except Exception:
        return False


def load_conversations():
    f = CHAT_SAVE_DIR / "conversations.pkl"
    if f.exists():
        try:
            with open(f, "rb") as fp:
                return pickle.load(fp)
        except Exception:
            return None
    return None


def save_active_chat_id(cid):
    try:
        with open(CHAT_SAVE_DIR / "active_chat.txt", "w", encoding="utf-8") as f:
            f.write(cid)
    except Exception:
        pass


def load_active_chat_id():
    f = CHAT_SAVE_DIR / "active_chat.txt"
    if f.exists():
        try:
            return f.read_text(encoding="utf-8").strip()
        except Exception:
            return None
    return None


def generate_pdf(messages):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 15, "Velora AI - Chat Export", ln=True, align="C")
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "Exported: " + datetime.now().strftime("%Y-%m-%d %H:%M"), ln=True, align="C")
        pdf.ln(8)
        for msg in messages:
            role = "You" if msg["role"] == "user" else "Velora AI"
            pdf.set_font("Helvetica", "B", 12)
            if msg["role"] == "user":
                pdf.set_text_color(0, 150, 255)
            else:
                pdf.set_text_color(100, 60, 200)
            pdf.cell(0, 8, role, ln=True)
            pdf.set_text_color(30, 30, 30)
            pdf.set_font("Helvetica", "", 11)
            content = msg.get("content", "").replace("```", "")
            try:
                pdf.multi_cell(0, 7, content)
            except Exception:
                pdf.multi_cell(0, 7, content.encode("latin-1", "replace").decode("latin-1"))
            pdf.ln(4)
        return bytes(pdf.output())
    except Exception:
        return None


def ts():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


# ============================================================
# SESSION STATE
# ============================================================
if "conversations" not in st.session_state:
    s = load_conversations()
    st.session_state.conversations = s if s else {
        "chat_1": {"title": "New Chat", "messages": [], "created": datetime.now().isoformat()}
    }

if "active_chat" not in st.session_state:
    sid = load_active_chat_id()
    if sid and sid in st.session_state.conversations:
        st.session_state.active_chat = sid
    else:
        st.session_state.active_chat = list(st.session_state.conversations.keys())[0]

if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = len(st.session_state.conversations)

if "agent" not in st.session_state:
    st.session_state.agent = None

if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None

if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # ==== SIDEBAR LOGO ====
    st.markdown("""
    <div class="sidebar-logo">
        <div class="logo-icon">✨</div>
        <p class="logo-title">Velora AI</p>
        <p class="logo-sub">PREMIUM</p>
    </div>
    """, unsafe_allow_html=True)

    # ==== LIVE CLOCK ====
    st.markdown(f'<div style="text-align:center;padding:12px;margin:10px 0;border-radius:12px;background:rgba(0,217,255,0.08);border:1px solid rgba(0,217,255,0.25);"><div style="font-size:22px;font-weight:800;background:linear-gradient(90deg,#00D9FF,#9B59FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">🕐 {__import__("datetime").datetime.now().strftime("%I:%M %p")}</div><div style="color:#6B8BA8;font-size:10px;margin-top:4px;letter-spacing:1.5px;">{__import__("datetime").datetime.now().strftime("%A, %d %B %Y").upper()}</div></div>', unsafe_allow_html=True)

    # ==== NEW CHAT BUTTON ====
    if st.button("➕  New Chat", use_container_width=True, key="new_chat_btn"):
        st.session_state.chat_counter += 1
        nid = f"chat_{st.session_state.chat_counter}"
        st.session_state.conversations[nid] = {
            "title": "New Chat",
            "messages": [],
            "created": datetime.now().isoformat(),
        }
        st.session_state.active_chat = nid
        save_conversations(st.session_state.conversations)
        save_active_chat_id(nid)
        st.rerun()

    st.markdown("##### 💬 Conversations")

    # ==== CONVERSATIONS LIST ====
    for cid, conv in list(st.session_state.conversations.items())[::-1]:
        is_active = cid == st.session_state.active_chat
        title = conv["title"][:22] + ("..." if len(conv["title"]) > 22 else "")
        icon = "🟢" if is_active else "⚪"
        if st.button(f"{icon} {title}", key=f"conv_{cid}", use_container_width=True):
            st.session_state.active_chat = cid
            save_active_chat_id(cid)
            st.rerun()

    st.markdown("---")

    # ==== DELETE / CLEAR ====
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Delete", use_container_width=True, key="del_btn"):
            if len(st.session_state.conversations) > 1:
                del st.session_state.conversations[st.session_state.active_chat]
                st.session_state.active_chat = list(st.session_state.conversations.keys())[0]
                save_conversations(st.session_state.conversations)
                st.rerun()
    with c2:
        if st.button("🧹 Clear", use_container_width=True, key="clr_btn"):
            st.session_state.conversations[st.session_state.active_chat]["messages"] = []
            save_conversations(st.session_state.conversations)
            st.rerun()

    # ==== EXPORT BUTTONS ====
    cur = st.session_state.conversations[st.session_state.active_chat]["messages"]
    if cur:
        txt = "\n\n".join([f"[{m['role'].upper()}]\n{m['content']}" for m in cur])
        st.download_button("⬇️  Export TXT", txt, file_name=f"chat_{st.session_state.active_chat}.txt",
                          mime="text/plain", use_container_width=True)
        pdf = generate_pdf(cur)
        if pdf:
            st.download_button("📄  Export PDF", pdf, file_name=f"chat_{st.session_state.active_chat}.pdf",
                              mime="application/pdf", use_container_width=True)

    st.markdown("---")

    # ==== VOICE TOGGLE ====
    st.markdown("##### 🎤 Voice")
    st.session_state.voice_enabled = st.checkbox("Enable Voice", value=st.session_state.voice_enabled)

    st.markdown("---")

    # ==== STATS ====
    total = sum(len(c["messages"]) for c in st.session_state.conversations.values())
    st.markdown(
        f'<p style="text-align:center; color:#6B8BA8; font-size:12px;">'
        f'💬 {len(st.session_state.conversations)} chats · ✉️ {total} messages</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="text-align:center; color:#4A6B88; font-size:10px; letter-spacing:2px;">'
        'V3.0 · PREMIUM</p>',
        unsafe_allow_html=True,
    )
# ============================================================
# INIT AGENT
# ============================================================
if st.session_state.agent is None:
    try:
        with st.spinner("✨ Initializing..."):
            st.session_state.agent = Agent()
    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()


current_conv = st.session_state.conversations[st.session_state.active_chat]
messages = current_conv["messages"]


# ============================================================
# PREMIUM HEADER
# ============================================================
st.markdown("""
<div class="premium-header">
    <div style="display:flex; align-items:center; gap:15px;">
        <div style="
            width:48px; height:48px; border-radius:14px;
            background: linear-gradient(135deg, #00D9FF, #4A7BE8);
            display:flex; align-items:center; justify-content:center;
            font-size:24px;
            box-shadow: 0 0 25px rgba(0, 217, 255, 0.5);
        ">✨</div>
        <div>
            <h1 style="margin:0; font-size:22px;">Velora AI · Premium</h1>
            <p style="color:#6B8BA8; margin:0; font-size:12px;">
                Your intelligent agent · Analyze · Create · Assist
            </p>
        </div>
    </div>
    <div class="online-status">
        <span class="online-dot"></span>
        <span>Online & Ready</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# VOICE CONTROL
# ============================================================
if st.session_state.voice_enabled:
    components.html("""
    <div style="display: flex; gap: 10px; align-items: center; padding: 14px 18px; 
                border-radius: 14px; 
                background: rgba(10, 20, 45, 0.55);
                backdrop-filter: blur(15px);
                border: 1px solid rgba(0, 217, 255, 0.25);">
        <button id="vBtn" style="
            background: linear-gradient(135deg, #0090B8, #00D9FF);
            color: #020814; border: none;
            padding: 10px 22px; border-radius: 10px;
            font-size: 14px; cursor: pointer; font-weight: 700;
            box-shadow: 0 4px 15px rgba(0, 217, 255, 0.4);
        ">🎤 Voice</button>
        <button id="sBtn" style="
            background: linear-gradient(135deg, #7C3AED, #9B59FF);
            color: white; border: none;
            padding: 10px 22px; border-radius: 10px;
            font-size: 14px; cursor: pointer; font-weight: 700;
        ">🔊 Read</button>
        <button id="stBtn" style="
            background: linear-gradient(135deg, #E53935, #B71C1C);
            color: white; border: none;
            padding: 10px 18px; border-radius: 10px;
            font-size: 13px; cursor: pointer; font-weight: 600;
        ">⏹️ Stop</button>
        <span id="st" style="color: #8DB8D9; font-size: 13px;">Click 🎤 to speak</span>
    </div>
    <script>
        const vBtn=document.getElementById('vBtn'),sBtn=document.getElementById('sBtn'),
              stBtn=document.getElementById('stBtn'),st=document.getElementById('st');
        const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
        let recog=null,listening=false;
        if(!SR){st.textContent="❌ Use Chrome/Edge";vBtn.disabled=true;vBtn.style.opacity="0.5";}
        else{
            recog=new SR();recog.lang='en-US';
            vBtn.onclick=()=>{
                if(!listening){recog.start();st.textContent="🎙️ Listening...";
                vBtn.textContent="⏹️ Stop";vBtn.style.background="linear-gradient(135deg,#E53935,#B71C1C)";listening=true;}
                else recog.stop();
            };
            recog.onresult=(e)=>{
                const t=e.results[0][0].transcript;st.textContent="✅ "+t;
                const d=window.parent.document;
                const i=d.querySelector('textarea[data-testid="stChatInputTextArea"]');
                if(i){const s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
                s.call(i,t);i.dispatchEvent(new Event('input',{bubbles:true}));i.focus();}
            };
            recog.onerror=(e)=>{st.textContent="❌ "+e.error;reset();};
            recog.onend=reset;
            function reset(){vBtn.textContent="🎤 Voice";vBtn.style.background="linear-gradient(135deg,#0090B8,#00D9FF)";listening=false;}
        }
        sBtn.onclick=()=>{
            const d=window.parent.document;
            const ms=d.querySelectorAll('[data-testid="stChatMessage"]');
            if(ms.length===0)return;
            let t="";
            for(let i=ms.length-1;i>=0;i--){t=ms[i].innerText;if(t&&t.trim().length>5)break;}
            if(!t)return;
            window.speechSynthesis.cancel();
            const u=new SpeechSynthesisUtterance(t);u.lang='en-US';
            u.onstart=()=>st.textContent="🔊 Speaking...";
            u.onend=()=>st.textContent="✅ Done";
            window.speechSynthesis.speak(u);
        };
        stBtn.onclick=()=>{window.speechSynthesis.cancel();st.textContent="⏹️ Stopped";};
    </script>
    """, height=85)


# ============================================================
# QUICK PROMPT
# ============================================================
if st.session_state.quick_prompt:
    p = st.session_state.quick_prompt
    st.session_state.quick_prompt = None
    t = ts()
    messages.append({"role": "user", "content": p, "time": t})
    if len(messages) == 1:
        current_conv["title"] = p[:30]
    with st.chat_message("user", avatar="🧑"):
        st.markdown(p)
        st.markdown(f'<div class="msg-time">🕐 {t}</div>', unsafe_allow_html=True)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("💭 Thinking..."):
            try:
                run = st.session_state.agent.run(p)
                ans = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                ans = f"❌ {e}"
        st.markdown(ans)
        t2 = ts()
        st.markdown(f'<div class="msg-time">🕐 {t2}</div>', unsafe_allow_html=True)
    messages.append({"role": "assistant", "content": ans, "time": t2})
    save_conversations(st.session_state.conversations)
    save_active_chat_id(st.session_state.active_chat)
    st.rerun()


# ============================================================
# WELCOME
# ============================================================
if len(messages) == 0:
    st.markdown("""
    <div style="text-align:center; padding: 30px 0;">
        <div class="orb"></div>
    </div>
    <h1 class="hero-title">Hello, I'm Velora AI</h1>
    <p class="hero-subtitle">
        Your intelligent companion · Ready to help with anything<br>
        <span style="font-size:13px; color:#6B8BA8;">English · বাংলা · Coding · Math · Life Advice</span>
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### ✨ Try asking")

    suggs = [
        ("💻", "Write a Python function", "Write a Python function to reverse a string"),
        ("🌌", "Explain a concept", "Explain quantum computing in simple terms"),
        ("✍️", "Write a poem", "Write a short poem about the stars"),
        ("🌏", "বাংলায় জিজ্ঞেস", "বাংলাদেশ সম্পর্কে ৫টি মজার তথ্য বলুন"),
        ("🧮", "Math problem", "What is 17 × 23? Show your steps."),
        ("💡", "Life advice", "How can I be more productive every day?"),
    ]

    cols = st.columns(3)
    for i, (icon, title, prompt) in enumerate(suggs):
        with cols[i % 3]:
            if st.button(f"{icon} {title}", use_container_width=True, key=f"s{i}"):
                st.session_state.quick_prompt = prompt
                st.rerun()


# ============================================================
# MESSAGES
# ============================================================
for msg in messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        t = msg.get("time", "")
        if t:
            st.markdown(f'<div class="msg-time">🕐 {t}</div>', unsafe_allow_html=True)


# ============================================================
# INPUT
# ============================================================
ui = st.chat_input("✨ Type your message...")

if ui:
    t = ts()
    messages.append({"role": "user", "content": ui, "time": t})
    if len(messages) == 1:
        current_conv["title"] = ui[:30]
    with st.chat_message("user", avatar="🧑"):
        st.markdown(ui)
        st.markdown(f'<div class="msg-time">🕐 {t}</div>', unsafe_allow_html=True)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("💭 Thinking..."):
            try:
                run = st.session_state.agent.run(ui)
                ans = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                ans = f"❌ {e}"
        st.markdown(ans)
        t2 = ts()
        st.markdown(f'<div class="msg-time">🕐 {t2}</div>', unsafe_allow_html=True)
    messages.append({"role": "assistant", "content": ans, "time": t2})
    save_conversations(st.session_state.conversations)
    save_active_chat_id(st.session_state.active_chat)
    st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#4A6B88; font-size:11px; letter-spacing:1px;">
    ✨ <strong style="color:#7EE5FF;">VELORA AI</strong> · PREMIUM EDITION · POWERED BY GEMINI
</p>
""", unsafe_allow_html=True)