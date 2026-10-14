"""
Velora AI - Enhanced Dashboard v2
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from src.data.uploader import upload_file, UploadError
from src.data.loader import load_dataset, get_basic_info, DataLoadError
from src.data.cleaner import clean_dataset
from src.data.analyzer import full_analysis
from src.data.visualizer import generate_all_charts
from src.data.reporter import generate_report
from src.agent.agent import Agent

st.set_page_config(page_title="Velora AI", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stApp { background: linear-gradient(135deg, #0a1428 0%, #1a2f4a 50%, #0f1e35 100%); }
    [data-testid="stSidebar"] { background: rgba(10,20,40,0.95); border-right: 1px solid rgba(74,158,255,0.2); }
    h1, h2, h3 { color: #E8F0F8 !important; }
    p, label, span { color: #B8D4F0; }
    .welcome-title {
        font-size: 44px; font-weight: 700;
        background: linear-gradient(90deg, #4A9EFF, #7EB6FF, #4A9EFF);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; margin: 20px 0 10px 0;
    }
    .welcome-subtitle { color: #8DA9C4; text-align: center; font-size: 15px; margin-bottom: 30px; }
    .glass-box {
        background: rgba(30,58,95,0.4); backdrop-filter: blur(12px);
        border: 1px solid rgba(74,158,255,0.25);
        border-radius: 16px; padding: 20px; margin: 8px 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3); transition: all 0.3s ease;
    }
    .glass-box:hover {
        transform: translateY(-4px);
        border-color: rgba(74,158,255,0.6);
        box-shadow: 0 12px 40px rgba(74,158,255,0.25);
    }
    .stButton > button {
        background: linear-gradient(135deg, #1E88E5, #0D47A1);
        color: white; border: 1px solid #4A9EFF;
        border-radius: 10px; padding: 8px 20px; font-weight: 500;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2196F3, #1565C0);
        border-color: #7EB6FF;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

for k, v in {"df":None,"df_info":None,"analysis":None,"cleaning_report":None,
             "chart_paths":None,"report":None,"chat_history":[],"agent":None,
             "quick_prompt":None,"page_redirect":None,"current_page":"Home"}.items():
    if k not in st.session_state:
        st.session_state[k] = v

with st.sidebar:
    st.markdown('<h2 style="color:#7EB6FF;">🤖 Velora AI</h2>', unsafe_allow_html=True)
    st.markdown("---")
    
    options = ["Home", "Upload Data", "Clean", "Analyze", "Charts", "AI Chat", "Report"]
    labels = {"Home":"🏠 Home","Upload Data":"📁 Upload Data","Clean":"🧹 Clean",
              "Analyze":"📊 Analyze","Charts":"📈 Charts","AI Chat":"🤖 AI Chat","Report":"📄 Report"}
    
    if st.session_state.page_redirect:
        st.session_state.current_page = st.session_state.page_redirect
        st.session_state.page_redirect = None
    
    idx = 0
    if st.session_state.current_page in options:
        idx = options.index(st.session_state.current_page)
    
    page = st.radio("Navigation", options, index=idx,
                    format_func=lambda x: labels[x], label_visibility="collapsed")
    st.session_state.current_page = page
    
    st.markdown("---")
    if st.session_state.df is not None:
        st.markdown('<p style="font-size:12px; color:#4A9EFF;">✅ Dataset loaded<br>' + str(st.session_state.df.shape[0]) + " rows × " + str(st.session_state.df.shape[1]) + " cols</p>", unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:12px; color:#5A7A9A;">⚠️ No dataset loaded</p>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p style="font-size:12px; color:#8DA9C4;">💬 ' + str(len(st.session_state.chat_history)) + ' messages</p>', unsafe_allow_html=True)
    st.markdown('<p style="font-size:11px; color:#5A7A9A;">v2.0 · Enhanced</p>', unsafe_allow_html=True)

# HOME
if page == "Home":
    st.markdown("""
    <div style="text-align:center; margin: 20px 0 30px 0;">
        <div style="width:180px; height:180px; margin:0 auto; border-radius:50%;
            background: radial-gradient(circle at 35% 30%, #7EB6FF 0%, #4A9EFF 20%, #1a3a5c 60%, #0a1428 100%);
            box-shadow: 0 0 60px rgba(74,158,255,0.7), 0 0 120px rgba(74,158,255,0.4);
            animation: float 6s ease-in-out infinite; position: relative;">
            <div style="position:absolute; top:15%; left:20%; width:50px; height:50px;
                background: rgba(180,220,255,0.5); border-radius:50%; filter:blur(18px);"></div>
        </div>
        <style>@keyframes float {0%,100%{transform:translateY(0) rotate(0deg);}50%{transform:translateY(-20px) rotate(180deg);}}</style>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="welcome-title">Welcome Back Rolex!</h1>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-subtitle">Your AI-powered data analyst is ready.</p>', unsafe_allow_html=True)
    
    rows = st.session_state.df.shape[0] if st.session_state.df is not None else 0
    cols = st.session_state.df.shape[1] if st.session_state.df is not None else 0
    chats = len(st.session_state.chat_history)
    
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown('<div class="glass-box" style="text-align:center; padding:20px;"><div style="font-size:32px;">📁</div><h3 style="color:#7EB6FF;">' + str(rows) + '</h3><p>Rows</p></div>', unsafe_allow_html=True)
    with m2:
        st.markdown('<div class="glass-box" style="text-align:center; padding:20px;"><div style="font-size:32px;">📊</div><h3 style="color:#7EB6FF;">' + str(cols) + '</h3><p>Columns</p></div>', unsafe_allow_html=True)
    with m3:
        st.markdown('<div class="glass-box" style="text-align:center; padding:20px;"><div style="font-size:32px;">💬</div><h3 style="color:#7EB6FF;">' + str(chats) + '</h3><p>Messages</p></div>', unsafe_allow_html=True)
    with m4:
        st.markdown('<div class="glass-box" style="text-align:center; padding:20px;"><div style="font-size:32px;">🎤</div><h3 style="color:#7EB6FF;">ON</h3><p>Voice</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center; color:#E8F0F8;">✨ What can I do?</h2>', unsafe_allow_html=True)
    
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('<div class="glass-box" style="text-align:center; min-height:200px;"><div style="font-size:48px;">📁</div><h3 style="color:#7EB6FF;">Upload & Analyze</h3><p>CSV / Excel upload করে statistics দেখুন</p></div>', unsafe_allow_html=True)
    with f2:
        st.markdown('<div class="glass-box" style="text-align:center; min-height:200px;"><div style="font-size:48px;">📈</div><h3 style="color:#7EB6FF;">Visualize</h3><p>Histogram, correlation, boxplot — সব auto</p></div>', unsafe_allow_html=True)
    with f3:
        st.markdown('<div class="glass-box" style="text-align:center; min-height:200px;"><div style="font-size:48px;">🤖</div><h3 style="color:#7EB6FF;">AI Chat + Voice</h3><p>কথা বলে প্রশ্ন করুন, AI উত্তর দেবে</p></div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<h2 style="text-align:center; color:#E8F0F8;">🚀 Quick Start</h2>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📁 Upload Dataset", use_container_width=True, key="h_up"):
            st.session_state.page_redirect = "Upload Data"
            st.rerun()
    with c2:
        if st.button("🤖 Chat with AI", use_container_width=True, key="h_ch"):
            st.session_state.page_redirect = "AI Chat"
            st.rerun()
    with c3:
        if st.button("📄 Generate Report", use_container_width=True, key="h_rp"):
            st.session_state.page_redirect = "Report"
            st.rerun()

# UPLOAD
elif page == "Upload Data":
    st.markdown('<h1 class="welcome-title">Upload Dataset</h1>', unsafe_allow_html=True)
    uploaded = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded is not None:
        if st.button("🚀 Upload & Load"):
            try:
                tmp_dir = ROOT / "data" / "uploads"
                tmp_dir.mkdir(parents=True, exist_ok=True)
                tmp_path = tmp_dir / uploaded.name
                tmp_path.write_bytes(uploaded.getbuffer())
                info = upload_file(tmp_path)
                df = load_dataset(info.get("saved_path", str(tmp_path)))
                st.session_state.df = df
                st.session_state.df_info = get_basic_info(df)
                st.success("✅ Loaded " + str(df.shape[0]) + " rows × " + str(df.shape[1]) + " cols")
            except Exception as e:
                st.error("❌ " + str(e))
    if st.session_state.df is not None:
        st.markdown("### 📋 Preview")
        st.dataframe(st.session_state.df.head(20), use_container_width=True)

# CLEAN
elif page == "Clean":
    st.markdown('<h1 class="welcome-title">Clean Data</h1>', unsafe_allow_html=True)
    if st.session_state.df is None:
        st.warning("⚠️ Upload a dataset first.")
    else:
        if st.button("🧹 Run Cleaning"):
            try:
                result = clean_dataset(st.session_state.df)
                cleaned, report = result if isinstance(result, tuple) else (result, None)
                st.session_state.df = cleaned
                st.session_state.cleaning_report = report
                st.success("✅ Cleaning complete!")
            except Exception as e:
                st.error("❌ " + str(e))
        if st.session_state.cleaning_report:
            rep = st.session_state.cleaning_report
            st.json(rep.__dict__ if hasattr(rep, "__dict__") else str(rep))

# ANALYZE
elif page == "Analyze":
    st.markdown('<h1 class="welcome-title">Data Analysis</h1>', unsafe_allow_html=True)
    if st.session_state.df is None:
        st.warning("⚠️ Upload a dataset first.")
    else:
        if st.button("📊 Run Full Analysis"):
            with st.spinner("Analyzing..."):
                try:
                    st.session_state.analysis = full_analysis(st.session_state.df)
                    st.success("✅ Done!")
                except Exception as e:
                    st.error("❌ " + str(e))
        if st.session_state.analysis:
            a = st.session_state.analysis
            if "summary" in a:
                st.markdown("### 📈 Summary Statistics")
                st.dataframe(a["summary"], use_container_width=True)
            if "correlation" in a:
                st.markdown("### 🔗 Correlations")
                st.dataframe(a["correlation"], use_container_width=True)
            if "outliers" in a:
                st.markdown("### 🎯 Outliers")
                st.json(a["outliers"])

# CHARTS
elif page == "Charts":
    st.markdown('<h1 class="welcome-title">Charts</h1>', unsafe_allow_html=True)
    if st.session_state.df is None:
        st.warning("⚠️ Upload a dataset first.")
    else:
        if st.button("📈 Generate All Charts"):
            with st.spinner("Generating..."):
                try:
                    st.session_state.chart_paths = generate_all_charts(st.session_state.df)
                    st.success("✅ Charts ready!")
                except Exception as e:
                    st.error("❌ " + str(e))
        if st.session_state.chart_paths:
            for name, paths in st.session_state.chart_paths.items():
                st.markdown("### " + str(name))
                if isinstance(paths, list):
                    for p in paths:
                        st.image(str(p), use_container_width=True)
                elif paths:
                    st.image(str(paths), use_container_width=True)

# AI CHAT
elif page == "AI Chat":
    st.markdown('<h1 class="welcome-title">AI Chat Assistant</h1>', unsafe_allow_html=True)
    st.markdown('<p class="welcome-subtitle">Type or speak — AI uses tools automatically.</p>', unsafe_allow_html=True)
    
    if st.session_state.agent is None:
        try:
            with st.spinner("Initializing..."):
                st.session_state.agent = Agent()
        except Exception as e:
            st.error("❌ " + str(e))
            st.stop()
    
    components.html("""
    <div style="display:flex; gap:12px; align-items:center; padding:15px; border-radius:12px; background:rgba(30,58,95,0.4); border:1px solid rgba(74,158,255,0.3);">
        <button id="vBtn" style="background:linear-gradient(135deg,#1E88E5,#0D47A1); color:white; border:1px solid #4A9EFF; padding:10px 22px; border-radius:10px; font-size:15px; cursor:pointer; font-weight:600;">🎤 Start Voice</button>
        <button id="sBtn" style="background:linear-gradient(135deg,#1E88E5,#0D47A1); color:white; border:1px solid #4A9EFF; padding:10px 22px; border-radius:10px; font-size:15px; cursor:pointer; font-weight:600;">🔊 Speak Reply</button>
        <button id="stBtn" style="background:linear-gradient(135deg,#E53935,#B71C1C); color:white; border:none; padding:10px 18px; border-radius:10px; font-size:14px; cursor:pointer;">⏹️ Stop</button>
        <span id="vStatus" style="color:#8DA9C4; font-size:14px;">Click "Start Voice" to speak</span>
    </div>
    <script>
        const vBtn=document.getElementById('vBtn'), sBtn=document.getElementById('sBtn'), stBtn=document.getElementById('stBtn'), vStatus=document.getElementById('vStatus');
        const SR=window.SpeechRecognition||window.webkitSpeechRecognition;
        let recog=null, listening=false;
        if(!SR){vStatus.textContent="❌ Use Chrome/Edge"; vBtn.disabled=true; vBtn.style.opacity="0.5";}
        else{
            recog=new SR(); recog.lang='en-US';
            vBtn.onclick=()=>{
                if(!listening){recog.start(); vStatus.textContent="🎙️ Listening..."; vBtn.textContent="⏹️ Stop"; vBtn.style.background="linear-gradient(135deg,#E53935,#B71C1C)"; listening=true;}
                else{recog.stop();}
            };
            recog.onresult=(e)=>{
                const t=e.results[0][0].transcript;
                vStatus.textContent="✅ "+t;
                const doc=window.parent.document;
                const inp=doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
                if(inp){
                    const s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;
                    s.call(inp,t); inp.dispatchEvent(new Event('input',{bubbles:true})); inp.focus();
                }
            };
            recog.onerror=(e)=>{vStatus.textContent="❌ "+e.error; resetBtn();};
            recog.onend=resetBtn;
            function resetBtn(){vBtn.textContent="🎤 Start Voice"; vBtn.style.background="linear-gradient(135deg,#1E88E5,#0D47A1)"; listening=false;}
        }
        sBtn.onclick=()=>{
            const doc=window.parent.document;
            const msgs=doc.querySelectorAll('[data-testid="stChatMessage"]');
            if(msgs.length===0)return;
            let txt="";
            for(let i=msgs.length-1;i>=0;i--){txt=msgs[i].innerText; if(txt&&txt.trim())break;}
            if(!txt)return;
            window.speechSynthesis.cancel();
            const u=new SpeechSynthesisUtterance(txt); u.lang='en-US';
            u.onstart=()=>vStatus.textContent="🔊 Speaking...";
            u.onend=()=>vStatus.textContent="✅ Done";
            window.speechSynthesis.speak(u);
        };
        stBtn.onclick=()=>{window.speechSynthesis.cancel(); vStatus.textContent="⏹️ Stopped";};
    </script>
    """, height=85)
    
    st.markdown("---")
    
    if st.session_state.quick_prompt:
        p = st.session_state.quick_prompt
        st.session_state.quick_prompt = None
        st.session_state.chat_history.append({"role": "user", "content": p})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(p)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    r = st.session_state.agent.run(p)
                    ans = getattr(r, "final_answer", None) or "(No response)"
                except Exception as e:
                    ans = "❌ " + str(e)
            st.markdown(ans)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
        st.rerun()
    
    c1, c2 = st.columns([6, 1])
    with c2:
        if st.button("🗑️ Clear"):
            st.session_state.chat_history = []
            st.rerun()
    
    for msg in st.session_state.chat_history:
        av = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=av):
            st.markdown(msg["content"])
    
    user_msg = st.chat_input("Ask about your data...")
    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_msg)
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    r = st.session_state.agent.run(user_msg)
                    ans = getattr(r, "final_answer", None) or "(No response)"
                except Exception as e:
                    ans = "❌ " + str(e)
            st.markdown(ans)
        st.session_state.chat_history.append({"role": "assistant", "content": ans})
    
    st.markdown("---")
    st.markdown("### 💡 Quick Actions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("📋 Datasets", use_container_width=True, key="qa1"):
            st.session_state.quick_prompt = "List all available datasets"
            st.rerun()
    with q2:
        if st.button("📊 Summary", use_container_width=True, key="qa2"):
            st.session_state.quick_prompt = "Show summary statistics of the dataset"
            st.rerun()
    with q3:
        if st.button("🎯 Outliers", use_container_width=True, key="qa3"):
            st.session_state.quick_prompt = "Find outliers in the dataset"
            st.rerun()
    with q4:
        if st.button("📈 Charts", use_container_width=True, key="qa4"):
            st.session_state.quick_prompt = "Generate all charts for the dataset"
            st.rerun()

# REPORT
elif page == "Report":
    st.markdown('<h1 class="welcome-title">Generate Report</h1>', unsafe_allow_html=True)
    if st.session_state.df is None:
        st.warning("⚠️ Upload a dataset first.")
    else:
        fp = st.text_input("Dataset file path")
        if st.button("📄 Generate Report"):
            try:
                st.session_state.report = generate_report(fp)
                st.success("✅ Report generated!")
            except Exception as e:
                st.error("❌ " + str(e))
        if st.session_state.report:
            rep = st.session_state.report
            if isinstance(rep, dict):
                if "report_md" in rep:
                    st.markdown(rep["report_md"])
                if "report_path" in rep:
                    try:
                        with open(rep["report_path"], "r", encoding="utf-8") as f:
                            c = f.read()
                        st.download_button("⬇️ Download", c, file_name=Path(rep["report_path"]).name, mime="text/markdown")
                    except Exception:
                        pass

st.markdown("---")
st.markdown('<p style="text-align:center; color:#5A7A9A; font-size:12px;">🤖 Velora AI · v2.0</p>', unsafe_allow_html=True)