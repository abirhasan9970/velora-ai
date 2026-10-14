"""
Velora AI - Pro Edition
Stunning visual chatbot with animations and premium feel.
"""
import sys
from pathlib import Path
from datetime import datetime
import pickle
import json

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
    page_title="Velora AI · Pro",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# PREMIUM CSS
# ============================================================
st.markdown("""
<style>
    /* ==== Root Styles ==== */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* ==== Animated Gradient Background ==== */
    .stApp {
        background: linear-gradient(-45deg, #0a1a2f, #0f2a4a, #1a3a5c, #0a1525);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* ==== Sidebar ==== */
    [data-testid="stSidebar"] {
        background: rgba(10, 20, 40, 0.85);
        backdrop-filter: blur(20px);
        border-right: 1px solid rgba(74, 158, 255, 0.25);
    }
    [data-testid="stSidebar"] * {
        color: #D5E8FF;
    }
    
    /* ==== Headings ==== */
    h1, h2, h3 { 
        color: #D5E8FF !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    
    /* ==== Animated Hero Title ==== */
    .hero-container {
        text-align: center;
        padding: 30px 20px 20px 20px;
    }
    .hero-icon {
        font-size: 80px;
        display: inline-block;
        animation: floatIcon 4s ease-in-out infinite;
        filter: drop-shadow(0 0 30px rgba(74, 158, 255, 0.8));
    }
    @keyframes floatIcon {
        0%, 100% { transform: translateY(0) rotate(0deg); }
        50% { transform: translateY(-15px) rotate(5deg); }
    }
    .hero-title {
        font-size: 56px;
        font-weight: 800;
        background: linear-gradient(90deg, #4A9EFF, #7EB6FF, #4DD0E1, #4A9EFF);
        background-size: 300% 100%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientText 4s linear infinite;
        margin: 20px 0 10px 0;
        letter-spacing: -0.03em;
    }
    @keyframes gradientText {
        0% { background-position: 0% 50%; }
        100% { background-position: 300% 50%; }
    }
    .hero-subtitle {
        color: #A5C8E8;
        font-size: 17px;
        margin-bottom: 40px;
        font-weight: 400;
    }
    
    /* ==== Glowing Orb ==== */
    .orb {
        width: 140px;
        height: 140px;
        margin: 20px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, 
            #7EB6FF 0%, #1E88E5 30%, #2a1050 70%, #0a0a1f 100%);
        box-shadow: 
            0 0 60px rgba(74, 158, 255, 0.7),
            0 0 120px rgba(74, 158, 255, 0.4),
            0 0 200px rgba(74, 158, 255, 0.2),
            inset -20px -20px 60px rgba(0, 0, 0, 0.6);
        position: relative;
        animation: orbFloat 6s ease-in-out infinite;
    }
    @keyframes orbFloat {
        0%, 100% { transform: translateY(0) scale(1); }
        50% { transform: translateY(-20px) scale(1.05); }
    }
    .orb::after {
        content: '';
        position: absolute;
        top: 15%;
        left: 20%;
        width: 40px;
        height: 40px;
        background: rgba(255, 255, 255, 0.5);
        border-radius: 50%;
        filter: blur(20px);
    }
    
    /* ==== Suggestion Cards ==== */
    .sugg-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 12px;
        margin: 20px 0;
    }
    .sugg-card {
        background: linear-gradient(135deg, 
            rgba(74, 158, 255, 0.15), 
            rgba(199, 125, 255, 0.08));
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 16px;
        padding: 18px 20px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        backdrop-filter: blur(10px);
    }
    .sugg-card:hover {
        background: linear-gradient(135deg, 
            rgba(74, 158, 255, 0.35), 
            rgba(199, 125, 255, 0.2));
        border-color: #7EB6FF;
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(74, 158, 255, 0.4);
    }
    .sugg-icon {
        font-size: 28px;
        margin-bottom: 8px;
    }
    .sugg-title {
        color: #D5E8FF;
        font-size: 15px;
        font-weight: 600;
    }
    
    /* ==== Chat Bubbles ==== */
    [data-testid="stChatMessage"] {
        animation: slideIn 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        padding: 10px 14px !important;
        border-radius: 14px !important;
        margin: 8px 0 !important;
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* ==== Chat Input ==== */
    .stChatInput > div > div > textarea {
        background: rgba(30, 20, 60, 0.75) !important;
        border: 1px solid rgba(74, 158, 255, 0.5) !important;
        border-radius: 16px !important;
        color: #D5E8FF !important;
        font-size: 15px !important;
        padding: 14px 18px !important;
        transition: all 0.3s;
    }
    .stChatInput > div > div > textarea:focus {
        border-color: #7EB6FF !important;
        box-shadow: 0 0 20px rgba(199, 125, 255, 0.4) !important;
    }
    
    /* ==== Buttons ==== */
    .stButton > button {
        background: linear-gradient(135deg, #1E88E5, #4A9EFF);
        color: white;
        border: 1px solid rgba(199, 125, 255, 0.5);
        border-radius: 12px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #4A9EFF, #B87DFF);
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(74, 158, 255, 0.5);
        border-color: #7EB6FF;
    }
    
    /* ==== Time Stamp ==== */
    .msg-time {
        font-size: 11px;
        color: #8B7AA8;
        margin-top: 4px;
        letter-spacing: 0.5px;
    }
    
    /* ==== Metrics / Stats ==== */
    [data-testid="stMetricValue"] {
        color: #7EB6FF !important;
        font-weight: 700 !important;
    }
    
    /* ==== Hide Streamlit default ==== */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* ==== Divider ==== */
    hr {
        border-color: rgba(74, 158, 255, 0.2);
        margin: 25px 0;
    }
    
    /* ==== Code blocks ==== */
    code {
        background: rgba(74, 158, 255, 0.15) !important;
        color: #7EB6FF !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
    }
    pre {
        background: rgba(20, 10, 40, 0.8) !important;
        border: 1px solid rgba(74, 158, 255, 0.3) !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# DATA STORAGE
# ============================================================
CHAT_SAVE_DIR = ROOT / "data" / "chats"
CHAT_SAVE_DIR.mkdir(parents=True, exist_ok=True)


def save_conversations(conversations):
    try:
        with open(CHAT_SAVE_DIR / "conversations.pkl", "wb") as f:
            pickle.dump(conversations, f)
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
                pdf.set_text_color(70, 130, 200)
            else:
                pdf.set_text_color(150, 80, 200)
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


def get_time_str():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


# ============================================================
# SESSION STATE
# ============================================================
if "conversations" not in st.session_state:
    saved = load_conversations()
    if saved:
        st.session_state.conversations = saved
    else:
        st.session_state.conversations = {
            "chat_1": {
                "title": "New Chat",
                "messages": [],
                "created": datetime.now().isoformat(),
            }
        }

if "active_chat" not in st.session_state:
    saved_id = load_active_chat_id()
    if saved_id and saved_id in st.session_state.conversations:
        st.session_state.active_chat = saved_id
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
    st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <div style="font-size: 42px; margin-bottom: 5px;">✨</div>
        <h2 style="
            background: linear-gradient(90deg, #7EB6FF, #4DD0E1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0;
            font-size: 24px;
        ">Velora AI</h2>
        <p style="color: #8B7AA8; font-size: 11px; margin: 5px 0;">
            PRO EDITION
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    if st.button("➕ New Chat", use_container_width=True, key="new_chat"):
        st.session_state.chat_counter += 1
        new_id = f"chat_{st.session_state.chat_counter}"
        st.session_state.conversations[new_id] = {
            "title": "New Chat",
            "messages": [],
            "created": datetime.now().isoformat(),
        }
        st.session_state.active_chat = new_id
        save_conversations(st.session_state.conversations)
        save_active_chat_id(new_id)
        st.rerun()

    st.markdown("### 📚 Conversations")

    for cid, conv in list(st.session_state.conversations.items())[::-1]:
        is_active = cid == st.session_state.active_chat
        title = conv["title"]
        if len(title) > 22:
            title = title[:19] + "..."
        icon = "🟣" if is_active else "⚪"
        if st.button(f"{icon} {title}", key=f"conv_{cid}", use_container_width=True):
            st.session_state.active_chat = cid
            save_active_chat_id(cid)
            st.rerun()

    st.markdown("---")

    if len(st.session_state.conversations) > 1:
        if st.button("🗑️ Delete Current", use_container_width=True, key="del_chat"):
            del st.session_state.conversations[st.session_state.active_chat]
            st.session_state.active_chat = list(st.session_state.conversations.keys())[0]
            save_conversations(st.session_state.conversations)
            save_active_chat_id(st.session_state.active_chat)
            st.rerun()

    if st.button("🧹 Clear Messages", use_container_width=True, key="clear_msgs"):
        st.session_state.conversations[st.session_state.active_chat]["messages"] = []
        save_conversations(st.session_state.conversations)
        st.rerun()

    current_msgs = st.session_state.conversations[st.session_state.active_chat]["messages"]
    if current_msgs:
        chat_text = "\n\n".join([
            f"[{m['role'].upper()}]\n{m['content']}" for m in current_msgs
        ])
        st.download_button(
            "⬇️ Export as TXT",
            chat_text,
            file_name=f"chat_{st.session_state.active_chat}.txt",
            mime="text/plain",
            use_container_width=True,
        )
        pdf_bytes = generate_pdf(current_msgs)
        if pdf_bytes:
            st.download_button(
                "📄 Export as PDF",
                pdf_bytes,
                file_name=f"chat_{st.session_state.active_chat}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    st.markdown("---")
    st.markdown("### 🎤 Voice")
    st.session_state.voice_enabled = st.checkbox(
        "Enable Voice Input",
        value=st.session_state.voice_enabled,
    )

    st.markdown("---")

    # Stats
    total_msgs = sum(len(c["messages"]) for c in st.session_state.conversations.values())
    st.markdown(f"""
    <div style="text-align: center; color: #8B7AA8; font-size: 12px;">
        <div>💬 {len(st.session_state.conversations)} chats</div>
        <div>✉️ {total_msgs} messages</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<p style="text-align:center; color:#6B5B8A; font-size:11px;">v2.0 · Pro Edition</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# INIT AGENT
# ============================================================
if st.session_state.agent is None:
    try:
        with st.spinner("✨ Initializing AI..."):
            st.session_state.agent = Agent()
    except Exception as e:
        st.error(f"❌ Failed to initialize: {e}")
        st.stop()


current_conv = st.session_state.conversations[st.session_state.active_chat]
messages = current_conv["messages"]


# ============================================================
# HEADER
# ============================================================
col1, col2 = st.columns([8, 2])
with col1:
    st.markdown("""
    <h2 style="
        background: linear-gradient(90deg, #7EB6FF, #4DD0E1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        padding: 10px 0;
        font-size: 28px;
    ">✨ Velora AI · Pro</h2>
    """, unsafe_allow_html=True)
with col2:
    st.markdown(f"""
    <p style="text-align:right; color:#8B7AA8; font-size:13px; margin-top:18px;">
        {len(messages)} messages
    </p>
    """, unsafe_allow_html=True)

st.markdown("---")


# ============================================================
# VOICE CONTROL
# ============================================================
if st.session_state.voice_enabled:
    components.html("""
    <div style="display: flex; gap: 10px; align-items: center; padding: 12px; border-radius: 14px; 
                background: rgba(30, 20, 60, 0.5); backdrop-filter: blur(10px);
                border: 1px solid rgba(74, 158, 255, 0.3);">
        <button id="vBtn" style="
            background: linear-gradient(135deg, #1E88E5, #4A9EFF);
            color: white; border: 1px solid rgba(199, 125, 255, 0.5);
            padding: 10px 22px; border-radius: 10px;
            font-size: 14px; cursor: pointer; font-weight: 600;
            box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3);
        ">🎤 Voice Input</button>
        <button id="sBtn" style="
            background: linear-gradient(135deg, #4A9EFF, #7EB6FF);
            color: white; border: 1px solid rgba(199, 125, 255, 0.5);
            padding: 10px 22px; border-radius: 10px;
            font-size: 14px; cursor: pointer; font-weight: 600;
        ">🔊 Read Reply</button>
        <button id="stBtn" style="
            background: linear-gradient(135deg, #E53935, #B71C1C);
            color: white; border: none;
            padding: 10px 18px; border-radius: 10px;
            font-size: 13px; cursor: pointer;
        ">⏹️ Stop</button>
        <span id="st" style="color: #A5C8E8; font-size: 13px;">
            Click 🎤 to speak
        </span>
    </div>

    <script>
        const vBtn = document.getElementById('vBtn');
        const sBtn = document.getElementById('sBtn');
        const stBtn = document.getElementById('stBtn');
        const st = document.getElementById('st');
        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recog = null, listening = false;

        if (!SR) {
            st.textContent = "❌ Voice requires Chrome/Edge";
            vBtn.disabled = true;
            vBtn.style.opacity = "0.5";
        } else {
            recog = new SR();
            recog.lang = 'en-US';
            recog.continuous = false;
            recog.interimResults = false;

            vBtn.onclick = () => {
                if (!listening) {
                    recog.start();
                    st.textContent = "🎙️ Listening... speak now";
                    vBtn.textContent = "⏹️ Stop";
                    vBtn.style.background = "linear-gradient(135deg, #E53935, #B71C1C)";
                    listening = true;
                } else {
                    recog.stop();
                }
            };
            recog.onresult = (e) => {
                const text = e.results[0][0].transcript;
                st.textContent = "✅ " + text;
                const doc = window.parent.document;
                const inp = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
                if (inp) {
                    const setter = Object.getOwnPropertyDescriptor(
                        window.HTMLTextAreaElement.prototype, 'value'
                    ).set;
                    setter.call(inp, text);
                    inp.dispatchEvent(new Event('input', { bubbles: true }));
                    inp.focus();
                }
            };
            recog.onerror = (e) => { st.textContent = "❌ " + e.error; reset(); };
            recog.onend = reset;
            function reset() {
                vBtn.textContent = "🎤 Voice Input";
                vBtn.style.background = "linear-gradient(135deg, #1E88E5, #4A9EFF)";
                listening = false;
            }
        }

        sBtn.onclick = () => {
            const doc = window.parent.document;
            const msgs = doc.querySelectorAll('[data-testid="stChatMessage"]');
            if (msgs.length === 0) { st.textContent = "No messages"; return; }
            let txt = "";
            for (let i = msgs.length - 1; i >= 0; i--) {
                txt = msgs[i].innerText;
                if (txt && txt.trim().length > 5) break;
            }
            if (!txt) return;
            window.speechSynthesis.cancel();
            const u = new SpeechSynthesisUtterance(txt);
            u.lang = 'en-US';
            u.rate = 1.0;
            u.onstart = () => st.textContent = "🔊 Speaking...";
            u.onend = () => st.textContent = "✅ Done";
            window.speechSynthesis.speak(u);
        };
        stBtn.onclick = () => {
            window.speechSynthesis.cancel();
            st.textContent = "⏹️ Stopped";
        };
    </script>
    """, height=75)


# ============================================================
# HANDLE QUICK PROMPT
# ============================================================
if st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None
    messages.append({
        "role": "user",
        "content": prompt,
        "time": get_time_str(),
    })
    if len(messages) == 1:
        current_conv["title"] = prompt[:30]

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)
        st.markdown(f'<div class="msg-time">🕐 {get_time_str()}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("💭 Thinking..."):
            try:
                run = st.session_state.agent.run(prompt)
                answer = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                answer = f"❌ Error: {e}"
        st.markdown(answer)
        st.markdown(f'<div class="msg-time">🕐 {get_time_str()}</div>', unsafe_allow_html=True)

    messages.append({
        "role": "assistant",
        "content": answer,
        "time": get_time_str(),
    })
    save_conversations(st.session_state.conversations)
    save_active_chat_id(st.session_state.active_chat)
    st.rerun()


# ============================================================
# WELCOME SCREEN
# ============================================================
if len(messages) == 0:
    st.markdown("""
    <div class="hero-container">
        <div class="orb"></div>
        <h1 class="hero-title">Hello, I'm Velora AI</h1>
        <p class="hero-subtitle">
            Your intelligent companion · Ready to help with anything<br>
            <span style="font-size: 14px;">English · বাংলা · Coding · Math · Life Advice</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ✨ Try asking me:")

    suggestions = [
        ("💻", "Write a Python function", "Write a Python function to reverse a string"),
        ("🌌", "Explain a concept", "Explain quantum computing in simple terms"),
        ("✍️", "Write a poem", "Write a short poem about the stars"),
        ("🌏", "বাংলায় জিজ্ঞেস", "বাংলাদেশ সম্পর্কে ৫টি মজার তথ্য বলুন"),
        ("🧮", "Math problem", "What is 17 × 23? Show your steps."),
        ("💡", "Life advice", "How can I be more productive every day?"),
    ]

    cols = st.columns(3)
    for i, (icon, title, prompt) in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(f"{icon} {title}", use_container_width=True, key=f"sugg_{i}"):
                st.session_state.quick_prompt = prompt
                st.rerun()


# ============================================================
# DISPLAY MESSAGES
# ============================================================
for msg in messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        t = msg.get("time", "")
        if t:
            st.markdown(f'<div class="msg-time">🕐 {t}</div>', unsafe_allow_html=True)


# ============================================================
# CHAT INPUT
# ============================================================
user_input = st.chat_input("✨ Type your message...")

if user_input:
    ts = get_time_str()
    messages.append({
        "role": "user",
        "content": user_input,
        "time": ts,
    })
    if len(messages) == 1:
        current_conv["title"] = user_input[:30]

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)
        st.markdown(f'<div class="msg-time">🕐 {ts}</div>', unsafe_allow_html=True)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("💭 Thinking..."):
            try:
                run = st.session_state.agent.run(user_input)
                answer = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                answer = f"❌ Error: {e}"
        st.markdown(answer)
        st.markdown(f'<div class="msg-time">🕐 {get_time_str()}</div>', unsafe_allow_html=True)

    messages.append({
        "role": "assistant",
        "content": answer,
        "time": get_time_str(),
    })
    save_conversations(st.session_state.conversations)
    save_active_chat_id(st.session_state.active_chat)
    st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<p style="text-align:center; color:#6B5B8A; font-size:12px;">
    ✨ <strong>Velora AI · Pro Edition</strong> · Powered by Gemini
</p>
""", unsafe_allow_html=True)