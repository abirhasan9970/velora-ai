"""
Velora AI - Fresh Clean Version
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
    [data-testid="stSidebar"] {
        background: rgba(8, 16, 36, 0.95) !important;
        border-right: 1px solid rgba(0, 217, 255, 0.25) !important;
    }
    [data-testid="stSidebar"] * { color: #E0F4FF !important; }
    h1, h2, h3 { color: #E0F4FF !important; }
    p, span, label { color: #E0F4FF; }
    
    .header-box {
        background: rgba(10, 20, 45, 0.6);
        border: 1px solid rgba(0, 217, 255, 0.3);
        border-radius: 18px;
        padding: 20px 26px;
        margin-bottom: 20px;
    }
    .header-title {
        background: linear-gradient(90deg, #00D9FF, #9B59FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 24px;
        font-weight: 800;
        margin: 0;
    }
    .online-badge {
        color: #00FF88;
        font-size: 13px;
        font-weight: 700;
    }
    .clock-box {
        text-align: center;
        padding: 14px 10px;
        margin: 10px 0;
        border-radius: 14px;
        background: rgba(0, 217, 255, 0.08);
        border: 1px solid rgba(0, 217, 255, 0.25);
    }
    .clock-time {
        font-size: 24px;
        font-weight: 800;
        background: linear-gradient(90deg, #00D9FF, #9B59FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .clock-date {
        color: #6B8BA8;
        font-size: 10px;
        margin-top: 4px;
        letter-spacing: 1.5px;
    }
    .logo-box {
        text-align: center;
        padding: 15px 0;
        border-bottom: 1px solid rgba(0, 217, 255, 0.2);
        margin-bottom: 15px;
    }
    .logo-icon {
        font-size: 40px;
        margin-bottom: 5px;
    }
    .logo-title {
        background: linear-gradient(90deg, #00D9FF, #9B59FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 22px;
        font-weight: 800;
        margin: 0;
    }
    .logo-sub {
        color: #6B8BA8;
        font-size: 10px;
        letter-spacing: 3px;
        margin-top: 4px;
    }
    .welcome-title {
        font-size: 46px;
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
        width: 180px;
        height: 180px;
        margin: 30px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, 
            #E0F4FF 0%, #00D9FF 18%, #4A7BE8 45%, #1a2050 75%, #020814 100%);
        box-shadow: 0 0 60px rgba(0, 217, 255, 0.7), 0 0 120px rgba(74, 123, 232, 0.5);
        animation: float 4s ease-in-out infinite;
    }
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-15px); }
    }
    [data-testid="stChatMessage"] {
        background: rgba(12, 22, 48, 0.65) !important;
        border: 1px solid rgba(0, 217, 255, 0.22) !important;
        border-radius: 16px !important;
        padding: 14px 18px !important;
        margin: 10px 0 !important;
    }
    [data-testid="stChatMessage"] p {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        font-size: 15px !important;
    }
    .msg-time {
        font-size: 11px;
        color: #6B8BA8;
        margin-top: 6px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# HELPERS
# ============================================================
CHAT_DIR = ROOT / "data" / "chats"
CHAT_DIR.mkdir(parents=True, exist_ok=True)


def save_convs(c):
    try:
        with open(CHAT_DIR / "convs.pkl", "wb") as f:
            pickle.dump(c, f)
    except Exception:
        pass


def load_convs():
    f = CHAT_DIR / "convs.pkl"
    if f.exists():
        try:
            with open(f, "rb") as fp:
                return pickle.load(fp)
        except Exception:
            return None
    return None


def save_active(cid):
    try:
        with open(CHAT_DIR / "active.txt", "w") as f:
            f.write(cid)
    except Exception:
        pass


def load_active():
    f = CHAT_DIR / "active.txt"
    if f.exists():
        try:
            return f.read_text().strip()
        except Exception:
            return None
    return None


def gen_pdf(msgs):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 12, "Velora AI - Chat Export", ln=True, align="C")
        pdf.ln(5)
        for m in msgs:
            role = "You" if m["role"] == "user" else "Velora AI"
            pdf.set_font("Helvetica", "B", 12)
            pdf.cell(0, 8, role, ln=True)
            pdf.set_font("Helvetica", "", 11)
            c = m.get("content", "").replace("```", "")
            try:
                pdf.multi_cell(0, 7, c)
            except Exception:
                pdf.multi_cell(0, 7, c.encode("latin-1", "replace").decode("latin-1"))
            pdf.ln(3)
        return bytes(pdf.output())
    except Exception:
        return None


def ts():
    return datetime.now().strftime("%I:%M %p").lstrip("0")


# ============================================================
# SESSION
# ============================================================
if "convs" not in st.session_state:
    s = load_convs()
    st.session_state.convs = s if s else {
        "chat_1": {"title": "New Chat", "messages": []}
    }

if "active" not in st.session_state:
    a = load_active()
    st.session_state.active = a if a and a in st.session_state.convs else list(st.session_state.convs.keys())[0]

if "counter" not in st.session_state:
    st.session_state.counter = len(st.session_state.convs)

if "agent" not in st.session_state:
    st.session_state.agent = None

if "quick" not in st.session_state:
    st.session_state.quick = None


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("""
    <div class="logo-box">
        <div class="logo-icon">✨</div>
        <p class="logo-title">Velora AI</p>
        <p class="logo-sub">PREMIUM</p>
    </div>
    """, unsafe_allow_html=True)

    now = datetime.now()
    st.markdown(f"""
    <div class="clock-box">
        <div class="clock-time">🕐 {now.strftime("%I:%M %p")}</div>
        <div class="clock-date">{now.strftime("%A, %d %B %Y").upper()}</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕  New Chat", use_container_width=True, key="nc"):
        st.session_state.counter += 1
        nid = f"chat_{st.session_state.counter}"
        st.session_state.convs[nid] = {"title": "New Chat", "messages": []}
        st.session_state.active = nid
        save_convs(st.session_state.convs)
        save_active(nid)
        st.rerun()

    st.markdown("##### 💬 Conversations")
    for cid, conv in list(st.session_state.convs.items())[::-1]:
        is_active = cid == st.session_state.active
        title = conv["title"][:20] + ("..." if len(conv["title"]) > 20 else "")
        icon = "🟢" if is_active else "⚪"
        if st.button(f"{icon} {title}", key=f"c_{cid}", use_container_width=True):
            st.session_state.active = cid
            save_active(cid)
            st.rerun()

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🗑️ Delete", use_container_width=True, key="del"):
            if len(st.session_state.convs) > 1:
                del st.session_state.convs[st.session_state.active]
                st.session_state.active = list(st.session_state.convs.keys())[0]
                save_convs(st.session_state.convs)
                st.rerun()
    with c2:
        if st.button("🧹 Clear", use_container_width=True, key="clr"):
            st.session_state.convs[st.session_state.active]["messages"] = []
            save_convs(st.session_state.convs)
            st.rerun()

    cur = st.session_state.convs[st.session_state.active]["messages"]
    if cur:
        txt = "\n\n".join([f"[{m['role'].upper()}]\n{m['content']}" for m in cur])
        st.download_button("⬇️ Export TXT", txt, file_name=f"{st.session_state.active}.txt",
                          mime="text/plain", use_container_width=True)
        pdf = gen_pdf(cur)
        if pdf:
            st.download_button("📄 Export PDF", pdf, file_name=f"{st.session_state.active}.pdf",
                              mime="application/pdf", use_container_width=True)

    st.markdown("---")
    total = sum(len(c["messages"]) for c in st.session_state.convs.values())
    st.markdown(
        f'<p style="text-align:center; color:#6B8BA8; font-size:12px;">'
        f'💬 {len(st.session_state.convs)} chats · ✉️ {total} messages</p>',
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
        <div style="display:flex; align-items:center; gap:15px;">
            <div style="
                width:48px; height:48px; border-radius:14px;
                background: linear-gradient(135deg, #00D9FF, #4A7BE8);
                display:flex; align-items:center; justify-content:center;
                font-size:24px;
            ">✨</div>
            <div>
                <h1 class="header-title">Velora AI</h1>
                <p style="color:#6B8BA8; margin:0; font-size:12px;">
                    Your intelligent assistant
                </p>
            </div>
        </div>
        <div class="online-badge">🟢 Online & Ready</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================
# VOICE PANEL
# ============================================================
components.html("""
<div style="display:flex; gap:10px; align-items:center; padding:12px 18px; 
            border-radius:14px; background:rgba(10,20,45,0.6);
            border:1px solid rgba(0,217,255,0.25);">
    <button id="vBtn" style="
        background:linear-gradient(135deg,#0090B8,#00D9FF);
        color:#020814; border:none; padding:10px 20px;
        border-radius:10px; font-size:14px; cursor:pointer; font-weight:700;
    ">🎤 Voice</button>
    <button id="sBtn" style="
        background:linear-gradient(135deg,#7C3AED,#9B59FF);
        color:white; border:none; padding:10px 20px;
        border-radius:10px; font-size:14px; cursor:pointer; font-weight:700;
    ">🔊 Read</button>
    <button id="stBtn" style="
        background:linear-gradient(135deg,#E53935,#B71C1C);
        color:white; border:none; padding:10px 16px;
        border-radius:10px; font-size:13px; cursor:pointer;
    ">⏹️ Stop</button>
    <span id="st" style="color:#8DB8D9; font-size:13px;">Click 🎤 to speak</span>
</div>
<script>
    var vBtn=document.getElementById('vBtn'),sBtn=document.getElementById('sBtn'),
        stBtn=document.getElementById('stBtn'),st=document.getElementById('st');
    var SR=window.SpeechRecognition||window.webkitSpeechRecognition;
    var recog=null,listening=false;
    if(!SR){
        st.textContent='Voice needs Chrome/Edge';
        vBtn.disabled=true;vBtn.style.opacity='0.5';
    } else {
        recog=new SR();recog.lang='en-US';
        vBtn.onclick=function(){
            if(!listening){
                recog.start();
                st.textContent='Listening...';
                vBtn.textContent='Stop';
                vBtn.style.background='linear-gradient(135deg,#E53935,#B71C1C)';
                listening=true;
            } else recog.stop();
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
        function reset(){
            vBtn.textContent='Voice';
            vBtn.style.background='linear-gradient(135deg,#0090B8,#00D9FF)';
            listening=false;
        }
    }
    sBtn.onclick=function(){
        var d=window.parent.document;
        var ms=d.querySelectorAll('[data-testid="stChatMessage"]');
        if(ms.length===0) return;
        var t='';
        for(var i=ms.length-1;i>=0;i--){t=ms[i].innerText;if(t&&t.trim().length>5)break;}
        if(!t) return;
        window.speechSynthesis.cancel();
        var u=new SpeechSynthesisUtterance(t);
        u.lang='en-US';
        window.speechSynthesis.speak(u);
    };
    stBtn.onclick=function(){window.speechSynthesis.cancel();st.textContent='Stopped';};
</script>
""", height=75)


# ============================================================
# QUICK PROMPT
# ============================================================
if st.session_state.quick:
    p = st.session_state.quick
    st.session_state.quick = None
    t = ts()
    msgs.append({"role": "user", "content": p, "time": t})
    if len(msgs) == 1:
        conv["title"] = p[:30]
    with st.chat_message("user", avatar="🧑"):
        st.markdown(p)
        st.markdown(f'<div class="msg-time">🕐 {t}</div>', unsafe_allow_html=True)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                run = st.session_state.agent.run(p)
                ans = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                ans = f"❌ {e}"
        st.markdown(ans)
        t2 = ts()
        st.markdown(f'<div class="msg-time">🕐 {t2}</div>', unsafe_allow_html=True)
    msgs.append({"role": "assistant", "content": ans, "time": t2})
    save_convs(st.session_state.convs)
    save_active(st.session_state.active)
    st.rerun()


# ============================================================
# WELCOME
# ============================================================
if len(msgs) == 0:
    st.markdown("""
    <div class="orb"></div>
    <h1 class="welcome-title">Hello, I'm Velora AI</h1>
    <p class="welcome-sub">
        Your intelligent companion · Ready to help with anything<br>
        English · বাংলা · Coding · Math · Life Advice
    </p>
    """, unsafe_allow_html=True)

    st.markdown("### ✨ Try asking")
    suggs = [
        ("💻", "Write Python code", "Write a Python function to reverse a string"),
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
        t = m.get("time", "")
        if t:
            st.markdown(f'<div class="msg-time">🕐 {t}</div>', unsafe_allow_html=True)


# ============================================================
# INPUT
# ============================================================
ui = st.chat_input("✨ Type your message...")

if ui:
    t = ts()
    msgs.append({"role": "user", "content": ui, "time": t})
    if len(msgs) == 1:
        conv["title"] = ui[:30]
    with st.chat_message("user", avatar="🧑"):
        st.markdown(ui)
        st.markdown(f'<div class="msg-time">🕐 {t}</div>', unsafe_allow_html=True)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                run = st.session_state.agent.run(ui)
                ans = getattr(run, "final_answer", None) or "(No response)"
            except Exception as e:
                ans = f"❌ {e}"
        st.markdown(ans)
        t2 = ts()
        st.markdown(f'<div class="msg-time">🕐 {t2}</div>', unsafe_allow_html=True)
    msgs.append({"role": "assistant", "content": ans, "time": t2})
    save_convs(st.session_state.convs)
    save_active(st.session_state.active)
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
