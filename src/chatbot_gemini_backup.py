"""
Velora AI - Gemini Style Chatbot
Clean sidebar with chat history like Gemini.
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

st.set_page_config(
    page_title="Velora AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CSS - MINIMAL, NO SIDEBAR HIDING
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #020814 0%, #050e20 50%, #020814 100%);
    }
    
    /* Sidebar Style */
    section[data-testid="stSidebar"] {
        background: #0a1428 !important;
        border-right: 1px solid rgba(0, 217, 255, 0.15);
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 10px;
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
        width: 160px;
        height: 160px;
        margin: 30px auto;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 30%, #E0F4FF 0%, #00D9FF 18%, #4A7BE8 45%, #1a2050 75%, #020814 100%);
        box-shadow: 0 0 60px rgba(0, 217, 255, 0.7);
    }
    
    /* Chat messages */
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
    [data-testid="stChatMessage"] strong {
        color: #7EE5FF !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
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


# ============================================================
# SESSION STATE
# ============================================================
if "convs" not in st.session_state:
    saved_convs, saved_active = load_data()
    if saved_convs:
        st.session_state.convs = saved_convs
        st.session_state.active = saved_active if saved_active in saved_convs else list(saved_convs.keys())[0]
    else:
        st.session_state.convs = {
            "chat_1": {"title": "New Chat", "messages": []}
        }
        st.session_state.active = "chat_1"

if "counter" not in st.session_state:
    st.session_state.counter = len(st.session_state.convs)

if "agent" not in st.session_state:
    st.session_state.agent = None

if "quick" not in st.session_state:
    st.session_state.quick = None


# ============================================================
# SIDEBAR - GEMINI STYLE
# ============================================================
with st.sidebar:
    # Logo
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 18px 0;">
        <div style="font-size: 36px;">✨</div>
        <div style="
            background: linear-gradient(90deg, #00D9FF, #9B59FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 22px; font-weight: 800; margin: 4px 0 0 0;
        ">Velora AI</div>
        <div style="color:#6B8BA8; font-size:10px; letter-spacing:3px;">PREMIUM</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Clock
    now = datetime.now()
    st.markdown(f"""
    <div style="text-align:center; padding:10px; margin: 8px 0 15px 0; border-radius:12px; background:rgba(0,217,255,0.08); border:1px solid rgba(0,217,255,0.25);">
        <div style="font-size:20px; font-weight:800; background:linear-gradient(90deg,#00D9FF,#9B59FF); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">🕐 {now.strftime("%I:%M %p")}</div>
        <div style="color:#6B8BA8; font-size:10px; margin-top:3px; letter-spacing:1px;">{now.strftime("%A, %d %B %Y").upper()}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # NEW CHAT BUTTON - Big and prominent
    if st.button("➕  New Chat", use_container_width=True, key="new_chat_btn", type="primary"):
        st.session_state.counter += 1
        nid = f"chat_{st.session_state.counter}"
        st.session_state.convs[nid] = {"title": "New Chat", "messages": []}
        st.session_state.active = nid
        save_data()
        st.rerun()
    
    st.markdown("---")
    st.markdown('<p style="color:#8DB8D9; font-size:12px; font-weight:600; margin: 10px 0;">📚 Recent Chats</p>', unsafe_allow_html=True)
    
    # CHAT HISTORY LIST
    for cid, conv in list(st.session_state.convs.items())[::-1]:
        is_active = cid == st.session_state.active
        title = conv["title"][:24] + ("..." if len(conv["title"]) > 24 else "")
        
        if is_active:
            st.markdown(f"""
            <div style="
                padding: 10px 14px; margin: 4px 0; border-radius: 10px;
                background: linear-gradient(90deg, rgba(0,217,255,0.2), rgba(155,89,255,0.15));
                border: 1px solid rgba(0,217,255,0.4);
                color: #E0F4FF; font-size: 13px; font-weight: 600;
            ">🟢 {title}</div>
            """, unsafe_allow_html=True)
        else:
            if st.button(f"⚪ {title}", key=f"c_{cid}", use_container_width=True):
                st.session_state.active = cid
                save_data()
                st.rerun()
    
    st.markdown("---")
    
    # Actions
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
    
    # Export
    cur_msgs = st.session_state.convs[st.session_state.active]["messages"]
    if cur_msgs:
        txt = "\n\n".join([f"[{m['role'].upper()}]\n{m['content']}" for m in cur_msgs])
        st.download_button("📥 Export TXT", txt, file_name=f"{st.session_state.active}.txt",
                          mime="text/plain", use_container_width=True, key="export_txt")
    
    # Stats
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
# QUICK PROMPT
# ============================================================
if st.session_state.quick:
    p = st.session_state.quick
    st.session_state.quick = None
    t = datetime.now().strftime("%I:%M %p").lstrip("0")
    msgs.append({"role": "user", "content": p, "time": t})
    if len(msgs) == 1:
        conv["title"] = p[:30]
    with st.chat_message("user", avatar="🧑"):
        st.markdown(p)
    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            try:
                run = st.session_state.agent.run(p)
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
                run = st.session_state.agent.run(ui)
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
