"""
Velora AI - General Chatbot
A clean, modern, general-purpose AI assistant with voice support.
"""
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
from fpdf import FPDF
import streamlit.components.v1 as components
import json

from src.agent.agent import Agent

# ============================================================
# AUTO-SAVE HELPERS
# ============================================================
import pickle


def generate_pdf(messages):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 15, "Velora AI - Chat Export", ln=True, align="C")
        pdf.ln(3)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 8, "Exported: " + datetime.now().strftime('%Y-%m-%d %H:%M'), ln=True, align="C")
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
            content = msg.get("content", "").replace("`", "")
            try:
                pdf.multi_cell(0, 7, content)
            except Exception:
                pdf.multi_cell(0, 7, content.encode("latin-1", "replace").decode("latin-1"))
            pdf.ln(4)
        return bytes(pdf.output())
    except Exception as e:
        print("PDF error: " + str(e))
        return None
def save_conversations(conversations):
    """Save all conversations to disk."""
    try:
        with open(CHAT_SAVE_DIR / "conversations.pkl", "wb") as f:
            pickle.dump(conversations, f)
        return True
    except Exception as e:
        print(f"Save error: {e}")
        return False

def load_conversations():
    """Load conversations from disk."""
    save_file = CHAT_SAVE_DIR / "conversations.pkl"
    if save_file.exists():
        try:
            with open(save_file, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Load error: {e}")
    return None

def save_active_chat_id(chat_id):
    """Save active chat id."""
    try:
        with open(CHAT_SAVE_DIR / "active_chat.txt", "w", encoding="utf-8") as f:
            f.write(chat_id)
    except Exception:
        pass

def load_active_chat_id():
    """Load active chat id."""
    active_file = CHAT_SAVE_DIR / "active_chat.txt"
    if active_file.exists():
        try:
            return active_file.read_text(encoding="utf-8").strip()
        except Exception:
            pass
    return None

# ============================================================
# AUTO-SAVE DIRECTORY
# ============================================================
CHAT_SAVE_DIR = ROOT / "data" / "chats"
CHAT_SAVE_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Velora AI Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS - PURPLE DARK THEME
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0a1f 0%, #1a1040 50%, #0f0a25 100%);
    }
    [data-testid="stSidebar"] {
        background: rgba(15, 10, 40, 0.95);
        border-right: 1px solid rgba(150, 100, 255, 0.2);
    }
    h1, h2, h3 { color: #E8D5FF !important; }
    p, label, span { color: #C4B5E8; }

    /* Chat messages */
    [data-testid="stChatMessage"] {
        background: transparent;
        padding: 4px 0;
    }

    /* Welcome hero */
    .hero-title {
        font-size: 42px;
        font-weight: 700;
        background: linear-gradient(90deg, #9B59FF, #C77DFF, #FF6EC7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 40px 0 10px 0;
    }
    .hero-subtitle {
        color: #B8A5D8;
        text-align: center;
        font-size: 16px;
        margin-bottom: 30px;
    }
    .hero-icon {
        font-size: 80px;
        text-align: center;
        margin-bottom: 10px;
        animation: float 4s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-15px); }
    }

    /* Suggestion chips */
    .chip {
        display: inline-block;
        padding: 10px 18px;
        background: rgba(155, 89, 255, 0.15);
        border: 1px solid rgba(155, 89, 255, 0.4);
        border-radius: 20px;
        color: #E8D5FF;
        margin: 5px;
        font-size: 14px;
        cursor: pointer;
        transition: all 0.2s;
    }
    .chip:hover {
        background: rgba(155, 89, 255, 0.3);
        border-color: #C77DFF;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #7C3AED, #9B59FF);
        color: white;
        border: 1px solid #9B59FF;
        border-radius: 10px;
        padding: 8px 18px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #9B59FF, #B87DFF);
        border-color: #C77DFF;
        transform: translateY(-1px);
    }

    /* Chat input */
    .stChatInput > div > div > textarea {
        background: rgba(30, 20, 60, 0.6) !important;
        border: 1px solid rgba(155, 89, 255, 0.4) !important;
        border-radius: 14px !important;
        color: #E8D5FF !important;
        font-size: 15px !important;
    }

    /* Hide default */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Conversation list */
    .conv-item {
        padding: 8px 12px;
        border-radius: 8px;
        margin: 4px 0;
        cursor: pointer;
        color: #C4B5E8;
        font-size: 13px;
        border: 1px solid transparent;
        transition: all 0.2s;
    }
    .conv-item:hover {
        background: rgba(155, 89, 255, 0.15);
        border-color: rgba(155, 89, 255, 0.3);
    }
    .conv-active {
        background: rgba(155, 89, 255, 0.25);
        border-color: #9B59FF;
        color: #E8D5FF;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
if "conversations" not in st.session_state:
    st.session_state.conversations = {
        "chat_1": {
            "title": "New Chat",
            "messages": [],
            "created": datetime.now().isoformat(),
        }
    }
if "active_chat" not in st.session_state:
    st.session_state.active_chat = "chat_1"
if "chat_counter" not in st.session_state:
    st.session_state.chat_counter = 1
if "agent" not in st.session_state:
    st.session_state.agent = None
if "quick_prompt" not in st.session_state:
    st.session_state.quick_prompt = None
if "voice_enabled" not in st.session_state:
    st.session_state.voice_enabled = True


# ============================================================
# SIDEBAR - CONVERSATIONS
# ============================================================
with st.sidebar:
    st.markdown('<h2 style="color:#C77DFF;">💬 Velora AI</h2>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:12px; color:#8B7AA8;">General-purpose AI Assistant</p>', unsafe_allow_html=True)
    st.markdown("---")

    # New chat button
    if st.button("➕ New Chat", use_container_width=True, key="new_chat"):
        st.session_state.chat_counter += 1
        new_id = f"chat_{st.session_state.chat_counter}"
        st.session_state.conversations[new_id] = {
            "title": "New Chat",
            "messages": [],
            "created": datetime.now().isoformat(),
        }
        st.session_state.active_chat = new_id
        st.rerun()

    st.markdown("### 📚 Conversations")

    # List conversations
    for cid, conv in list(st.session_state.conversations.items())[::-1]:
        is_active = cid == st.session_state.active_chat
        title = conv["title"]
        # Truncate title
        if len(title) > 25:
            title = title[:22] + "..."

        icon = "🟣" if is_active else "⚪"
        if st.button(f"{icon} {title}", key=f"conv_{cid}", use_container_width=True):
            st.session_state.active_chat = cid
            st.rerun()

    st.markdown("---")

    # Delete current chat
    if len(st.session_state.conversations) > 1:
        if st.button("🗑️ Delete Current", use_container_width=True, key="del_chat"):
            del st.session_state.conversations[st.session_state.active_chat]
            st.session_state.active_chat = list(st.session_state.conversations.keys())[0]
            st.rerun()

    # Clear current chat
    if st.button("🧹 Clear Messages", use_container_width=True, key="clear_msgs"):
        st.session_state.conversations[st.session_state.active_chat]["messages"] = []
        st.rerun()

    # Export chat
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

    # Voice toggle
    st.markdown("### 🎤 Voice Settings")
    st.session_state.voice_enabled = st.checkbox(
        "Enable Voice Input",
        value=st.session_state.voice_enabled,
    )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:11px; color:#6B5B8A;">v1.0 · General Chatbot</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# INITIALIZE AGENT
# ============================================================
if st.session_state.agent is None:
    try:
        with st.spinner("Initializing AI..."):
            st.session_state.agent = Agent()
    except Exception as e:
        st.error(f"❌ Failed to initialize AI Agent: {e}")
        st.stop()


# ============================================================
# GET CURRENT CONVERSATION
# ============================================================
current_conv = st.session_state.conversations[st.session_state.active_chat]
messages = current_conv["messages"]


# ============================================================
# MAIN HEADER
# ============================================================
col1, col2 = st.columns([8, 2])
with col1:
    st.markdown(
        '<h2 style="color:#C77DFF; margin: 0;">💬 Velora AI Chatbot</h2>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<p style="text-align:right; color:#8B7AA8; font-size:12px; margin-top:12px;">'
        f'{len(messages)} messages</p>',
        unsafe_allow_html=True,
    )

st.markdown("---")


# ============================================================
# VOICE CONTROL PANEL
# ============================================================
if st.session_state.voice_enabled:
    components.html("""
    <div style="display: flex; gap: 10px; align-items: center; margin-bottom: 12px;">
        <button id="voiceBtn" style="
            background: linear-gradient(135deg, #7C3AED, #9B59FF);
            color: white; border: none;
            padding: 10px 20px; border-radius: 10px;
            font-size: 14px; cursor: pointer; font-weight: 600;
        ">🎤 Voice Input</button>
        <button id="speakBtn" style="
            background: linear-gradient(135deg, #9B59FF, #C77DFF);
            color: white; border: none;
            padding: 10px 20px; border-radius: 10px;
            font-size: 14px; cursor: pointer; font-weight: 600;
        ">🔊 Read Last Reply</button>
        <button id="stopBtn" style="
            background: rgba(220, 50, 100, 0.9);
            color: white; border: none;
            padding: 10px 16px; border-radius: 10px;
            font-size: 13px; cursor: pointer;
        ">⏹️ Stop</button>
        <span id="status" style="color: #B8A5D8; font-size: 13px;">
            Click 🎤 to speak
        </span>
    </div>

    <script>
        const vBtn = document.getElementById('voiceBtn');
        const sBtn = document.getElementById('speakBtn');
        const stBtn = document.getElementById('stopBtn');
        const status = document.getElementById('status');

        const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recog = null, listening = false;

        if (!SR) {
            status.textContent = "❌ Voice requires Chrome or Edge";
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
                    status.textContent = "🎙️ Listening... speak now";
                    vBtn.textContent = "⏹️ Stop";
                    vBtn.style.background = "linear-gradient(135deg, #E53935, #B71C1C)";
                    listening = true;
                } else {
                    recog.stop();
                }
            };

            recog.onresult = (e) => {
                const text = e.results[0][0].transcript;
                status.textContent = "✅ Heard: " + text;
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

            recog.onerror = (e) => {
                status.textContent = "❌ Error: " + e.error;
                reset();
            };
            recog.onend = reset;

            function reset() {
                vBtn.textContent = "🎤 Voice Input";
                vBtn.style.background = "linear-gradient(135deg, #7C3AED, #9B59FF)";
                listening = false;
            }
        }

        sBtn.onclick = () => {
            const doc = window.parent.document;
            const msgs = doc.querySelectorAll('[data-testid="stChatMessage"]');
            if (msgs.length === 0) {
                status.textContent = "No messages to speak";
                return;
            }
            let text = "";
            for (let i = msgs.length - 1; i >= 0; i--) {
                text = msgs[i].innerText;
                if (text && text.trim().length > 5) break;
            }
            if (!text) return;
            window.speechSynthesis.cancel();
            const utt = new SpeechSynthesisUtterance(text);
            utt.lang = 'en-US';
            utt.rate = 1.0;
            utt.onstart = () => status.textContent = "🔊 Speaking...";
            utt.onend = () => status.textContent = "✅ Done";
            window.speechSynthesis.speak(utt);
        };

        stBtn.onclick = () => {
            window.speechSynthesis.cancel();
            status.textContent = "⏹️ Stopped";
        };
    </script>
    """, height=80)


# ============================================================
# HANDLE QUICK PROMPT (from suggestion chips)
# ============================================================
if st.session_state.quick_prompt:
    prompt = st.session_state.quick_prompt
    st.session_state.quick_prompt = None
    messages.append({"role": "user", "content": prompt})

    # Update conversation title if first message
    if len(messages) == 1:
        current_conv["title"] = prompt[:30]

    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                run = st.session_state.agent.run(prompt)
                answer = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                answer = f"❌ Error: {e}"
        st.markdown(answer)

    messages.append({"role": "assistant", "content": answer})


    save_conversations(st.session_state.conversations)


    save_active_chat_id(st.session_state.active_chat)
    st.rerun()


# ============================================================
# WELCOME SCREEN (when no messages)
# ============================================================
if len(messages) == 0:
    st.markdown("""
    <div style="text-align:center; margin-top: 40px;">
        <div class="hero-icon">🤖</div>
        <h1 class="hero-title">Hello, I'm Velora AI</h1>
        <p class="hero-subtitle">Your friendly, always-ready AI assistant.<br>
        Ask me anything — in English or বাংলা.</p>
    </div>
    """, unsafe_allow_html=True)

    # Suggestion chips
    st.markdown("### 💡 Try asking:")

    suggestions = [
        ("💻 Write code", "Write a Python function to reverse a string"),
        ("📚 Explain", "Explain quantum computing in simple terms"),
        ("✍️ Write", "Write a short poem about the moon"),
        ("🌏 Bangla", "বাংলাদেশ সম্পর্কে ৫টি মজার তথ্য বলুন"),
        ("🧮 Math", "What is 17 × 23?"),
        ("🎯 Advice", "How can I improve my productivity?"),
    ]

    cols = st.columns(3)
    for i, (label, prompt) in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(label, use_container_width=True, key=f"sugg_{i}"):
                st.session_state.quick_prompt = prompt
                st.rerun()

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        '<p style="text-align:center; color:#6B5B8A; font-size:12px;">'
        '💬 Type a message below or use 🎤 Voice Input</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================
for msg in messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])


# ============================================================
# CHAT INPUT
# ============================================================
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message
    messages.append({"role": "user", "content": user_input})

    # Update conversation title if first message
    if len(messages) == 1:
        current_conv["title"] = user_input[:30]

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    # Get AI response
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                run = st.session_state.agent.run(user_input)
                answer = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                answer = f"❌ Error: {e}"
        st.markdown(answer)

    messages.append({"role": "assistant", "content": answer})


    save_conversations(st.session_state.conversations)


    save_active_chat_id(st.session_state.active_chat)
    st.rerun()


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#5A4A7A; font-size:11px;">'
    '💬 Velora AI · General Chatbot · Powered by your AI Agent</p>',
    unsafe_allow_html=True,
)