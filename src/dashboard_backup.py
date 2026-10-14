"""
Velora AI - Professional AI Agent Dashboard with Voice Control
Data analysis + AI chat + dark theme + voice input/output.
"""
import sys
from pathlib import Path

# Fix import path
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

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Velora AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS - DARK THEME
# ============================================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a1428 0%, #1a2f4a 50%, #0f1e35 100%);
    }
    [data-testid="stSidebar"] {
        background: rgba(10, 20, 40, 0.95);
        border-right: 1px solid rgba(74, 158, 255, 0.2);
    }
    h1, h2, h3 { color: #E8F0F8 !important; }
    p, label, span { color: #B8D4F0; }

    .welcome-title {
        font-size: 44px;
        font-weight: 700;
        background: linear-gradient(90deg, #4A9EFF, #7EB6FF, #4A9EFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 20px 0 10px 0;
    }
    .welcome-subtitle {
        color: #8DA9C4;
        text-align: center;
        font-size: 15px;
        margin-bottom: 30px;
    }
    .glass-box {
        background: rgba(30, 58, 95, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 16px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #1E88E5, #0D47A1);
        color: white;
        border: 1px solid #4A9EFF;
        border-radius: 10px;
        padding: 8px 20px;
        font-weight: 500;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #2196F3, #1565C0);
        border-color: #7EB6FF;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "df": None,
    "df_info": None,
    "analysis": None,
    "cleaning_report": None,
    "chart_paths": None,
    "report": None,
    "chat_history": [],
    "agent": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown('<h2 style="color:#7EB6FF;">🤖 Velora AI</h2>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "📌 Navigation",
        ["🏠 Home", "📁 Upload Data", "🧹 Clean", "📊 Analyze", "📈 Charts", "🤖 AI Chat", "📄 Report"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:12px; color:#5A7A9A;">v1.1 · Voice Enabled</p>',
        unsafe_allow_html=True,
    )


# ============================================================
# HOME PAGE
# ============================================================
if page == "🏠 Home":
    st.markdown('<h1 class="welcome-title">Welcome Back Rolex!</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="welcome-subtitle">Upload a dataset to begin your AI-powered analysis.</p>',
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="glass-box" style="text-align:center;">
            <div style="font-size:36px;">📁</div>
            <h3 style="color:#7EB6FF;">Upload</h3>
            <p>CSV or Excel files</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="glass-box" style="text-align:center;">
            <div style="font-size:36px;">📊</div>
            <h3 style="color:#7EB6FF;">Analyze</h3>
            <p>Stats, outliers, correlations</p>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="glass-box" style="text-align:center;">
            <div style="font-size:36px;">🎙️</div>
            <h3 style="color:#7EB6FF;">Voice Chat</h3>
            <p>Talk to your AI agent</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.df is not None:
        st.success(f"✅ Dataset loaded: **{st.session_state.df.shape[0]} rows × {st.session_state.df.shape[1]} columns**")


# ============================================================
# UPLOAD PAGE
# ============================================================
elif page == "📁 Upload Data":
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
                saved_path = info.get("saved_path", str(tmp_path))
                df = load_dataset(saved_path)
                df_info = get_basic_info(df)

                st.session_state.df = df
                st.session_state.df_info = df_info
                st.success(f"✅ Loaded **{df.shape[0]}** rows and **{df.shape[1]}** columns.")
            except (UploadError, DataLoadError) as e:
                st.error(f"❌ Failed to load: {e}")
            except Exception as e:
                st.error(f"❌ Unexpected error: {e}")

    if st.session_state.df is not None:
        st.markdown("### 📋 Preview")
        st.dataframe(st.session_state.df.head(20), use_container_width=True)

        if st.session_state.df_info:
            st.markdown("### ℹ️ Info")
            info = st.session_state.df_info
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows", info.get("rows", "—"))
            c2.metric("Columns", info.get("columns", "—"))
            c3.metric("Memory (MB)", f"{info.get('memory_mb', 0):.2f}")


# ============================================================
# CLEAN PAGE
# ============================================================
elif page == "🧹 Clean":
    st.markdown('<h1 class="welcome-title">Clean Data</h1>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        if st.button("🧹 Run Cleaning"):
            try:
                result = clean_dataset(st.session_state.df)
                if isinstance(result, tuple):
                    cleaned, report = result
                else:
                    cleaned, report = result, None
                st.session_state.df = cleaned
                st.session_state.cleaning_report = report
                st.success("✅ Cleaning complete!")
            except Exception as e:
                st.error(f"❌ Cleaning failed: {e}")

        if st.session_state.cleaning_report:
            st.markdown("### 📋 Cleaning Report")
            rep = st.session_state.cleaning_report
            if hasattr(rep, "__dict__"):
                st.json(rep.__dict__)
            else:
                st.write(rep)
            st.markdown("### 📋 Cleaned Preview")
            st.dataframe(st.session_state.df.head(20), use_container_width=True)


# ============================================================
# ANALYZE PAGE
# ============================================================
elif page == "📊 Analyze":
    st.markdown('<h1 class="welcome-title">Data Analysis</h1>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        if st.button("📊 Run Full Analysis"):
            with st.spinner("Analyzing..."):
                try:
                    st.session_state.analysis = full_analysis(st.session_state.df)
                    st.success("✅ Analysis complete!")
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")

        if st.session_state.analysis:
            analysis = st.session_state.analysis

            if "summary" in analysis:
                st.markdown("### 📈 Summary Statistics")
                st.dataframe(analysis["summary"], use_container_width=True)

            if "correlation" in analysis:
                st.markdown("### 🔗 Correlation Matrix")
                st.dataframe(analysis["correlation"], use_container_width=True)

            if "outliers" in analysis:
                st.markdown("### 🎯 Outliers")
                st.json(analysis["outliers"])

            if "value_counts" in analysis:
                st.markdown("### 📊 Value Counts")
                for col, vals in analysis["value_counts"].items():
                    st.markdown(f"**{col}**")
                    try:
                        st.dataframe(pd.DataFrame(vals), use_container_width=True)
                    except Exception:
                        st.write(vals)


# ============================================================
# CHARTS PAGE
# ============================================================
elif page == "📈 Charts":
    st.markdown('<h1 class="welcome-title">Charts</h1>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        if st.button("📈 Generate All Charts"):
            with st.spinner("Generating charts..."):
                try:
                    charts = generate_all_charts(st.session_state.df)
                    st.session_state.chart_paths = charts
                    st.success("✅ Charts generated!")
                except Exception as e:
                    st.error(f"❌ Chart generation failed: {e}")

        if st.session_state.chart_paths:
            charts = st.session_state.chart_paths
            if isinstance(charts, dict):
                for name, paths in charts.items():
                    st.markdown(f"### {name}")
                    if isinstance(paths, list):
                        for p in paths:
                            st.image(str(p), use_container_width=True)
                    elif paths:
                        st.image(str(paths), use_container_width=True)


# ============================================================
# AI CHAT PAGE - WITH VOICE CONTROL
# ============================================================
elif page == "🤖 AI Chat":
    st.markdown('<h1 class="welcome-title">AI Chat Assistant</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="welcome-subtitle">Type or speak — AI will use tools automatically.</p>',
        unsafe_allow_html=True,
    )

    # Initialize agent once
    if st.session_state.agent is None:
        try:
            with st.spinner("Initializing AI Agent..."):
                st.session_state.agent = Agent()
        except Exception as e:
            st.error(f"❌ Failed to initialize AI Agent: {e}")
            st.stop()

    # ============ VOICE CONTROL PANEL ============
    components.html("""
    <div style="
        display: flex; gap: 12px; align-items: center;
        padding: 15px; border-radius: 12px;
        background: rgba(30, 58, 95, 0.4);
        border: 1px solid rgba(74, 158, 255, 0.3);
        font-family: sans-serif;
    ">
        <button id="voiceBtn" style="
            background: linear-gradient(135deg, #1E88E5, #0D47A1);
            color: white; border: 1px solid #4A9EFF;
            padding: 10px 22px; border-radius: 10px;
            font-size: 15px; cursor: pointer; font-weight: 600;
            transition: all 0.3s;
        ">🎤 Start Voice</button>

        <button id="speakBtn" style="
            background: linear-gradient(135deg, #1E88E5, #0D47A1);
            color: white; border: 1px solid #4A9EFF;
            padding: 10px 22px; border-radius: 10px;
            font-size: 15px; cursor: pointer; font-weight: 600;
            transition: all 0.3s;
        ">🔊 Speak Last Reply</button>

        <button id="stopSpeakBtn" style="
            background: linear-gradient(135deg, #E53935, #B71C1C);
            color: white; border: 1px solid #EF5350;
            padding: 10px 18px; border-radius: 10px;
            font-size: 14px; cursor: pointer; font-weight: 500;
        ">⏹️ Stop</button>

        <span id="voiceStatus" style="
            color: #8DA9C4; font-size: 14px; margin-left: 8px;
        ">Click "Start Voice" to speak</span>
    </div>

    <script>
        const voiceBtn = document.getElementById('voiceBtn');
        const speakBtn = document.getElementById('speakBtn');
        const stopSpeakBtn = document.getElementById('stopSpeakBtn');
        const voiceStatus = document.getElementById('voiceStatus');

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        let isListening = false;

        // ---- SPEECH RECOGNITION ----
        if (!SpeechRecognition) {
            voiceStatus.textContent = "❌ Voice not supported. Use Chrome or Edge.";
            voiceBtn.disabled = true;
            voiceBtn.style.opacity = "0.5";
        } else {
            recognition = new SpeechRecognition();
            recognition.lang = 'en-US';
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;

            voiceBtn.onclick = () => {
                if (!isListening) {
                    try {
                        recognition.start();
                        voiceStatus.textContent = "🎙️ Listening... speak now";
                        voiceBtn.textContent = "⏹️ Stop Listening";
                        voiceBtn.style.background = "linear-gradient(135deg, #E53935, #B71C1C)";
                        isListening = true;
                    } catch (e) {
                        voiceStatus.textContent = "❌ Error starting: " + e.message;
                    }
                } else {
                    recognition.stop();
                }
            };

            recognition.onresult = (event) => {
                const text = event.results[0][0].transcript;
                voiceStatus.textContent = "✅ Heard: \"" + text + "\"";
                fillStreamlitChat(text);
            };

            recognition.onerror = (event) => {
                voiceStatus.textContent = "❌ Error: " + event.error;
                resetBtn();
            };

            recognition.onend = () => {
                resetBtn();
                if (voiceStatus.textContent.includes("Listening")) {
                    voiceStatus.textContent = "Done. Try again or type manually.";
                }
            };

            function resetBtn() {
                voiceBtn.textContent = "🎤 Start Voice";
                voiceBtn.style.background = "linear-gradient(135deg, #1E88E5, #0D47A1)";
                isListening = false;
            }
        }

        // ---- FILL STREAMLIT CHAT INPUT ----
        function fillStreamlitChat(text) {
            const doc = window.parent.document;
            const chatInput = doc.querySelector('textarea[data-testid="stChatInputTextArea"]');
            if (chatInput) {
                const nativeSetter = Object.getOwnPropertyDescriptor(
                    window.HTMLTextAreaElement.prototype, 'value'
                ).set;
                nativeSetter.call(chatInput, text);
                chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                chatInput.focus();
                voiceStatus.textContent = "✅ Filled! Press Enter to send.";
            } else {
                voiceStatus.textContent = "✅ Heard: " + text + " (paste manually)";
            }
        }

        // ---- TEXT TO SPEECH ----
        speakBtn.onclick = () => {
            const doc = window.parent.document;
            const msgs = doc.querySelectorAll('[data-testid="stChatMessage"]');
            if (msgs.length === 0) {
                voiceStatus.textContent = "No messages to speak";
                return;
            }
            // Find last assistant message
            let lastText = "";
            for (let i = msgs.length - 1; i >= 0; i--) {
                lastText = msgs[i].innerText;
                if (lastText && lastText.trim().length > 0) break;
            }
            if (!lastText) return;

            window.speechSynthesis.cancel();
            const utt = new SpeechSynthesisUtterance(lastText);
            utt.lang = 'en-US';
            utt.rate = 1.0;
            utt.pitch = 1.0;
            utt.volume = 1.0;
            utt.onstart = () => voiceStatus.textContent = "🔊 Speaking...";
            utt.onend = () => voiceStatus.textContent = "✅ Done speaking";
            window.speechSynthesis.speak(utt);
        };

        stopSpeakBtn.onclick = () => {
            window.speechSynthesis.cancel();
            voiceStatus.textContent = "⏹️ Stopped";
        };
    </script>
    """, height=85)

    st.markdown("---")

    # Clear button
    c1, c2 = st.columns([6, 1])
    with c2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    # Render chat history
    for msg in st.session_state.chat_history:
        avatar = "🧑" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # Handle quick-action messages (from session state)
    if "pending_msg" in st.session_state and st.session_state.pending_msg:
        pending = st.session_state.pending_msg
        st.session_state.pending_msg = None
        st.session_state.chat_history.append({"role": "user", "content": pending})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(pending)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    run = st.session_state.agent.run(pending)
                    answer = getattr(run, "final_answer", None) or "(No response)"
                    called = getattr(run, "_called_tools", None)
                except Exception as e:
                    answer = f"❌ Error: {e}"
                    called = None
            st.markdown(answer)
            if called:
                st.caption(f"🔧 Tools used: {', '.join(called)}")
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.rerun()

    # Chat input
    user_msg = st.chat_input("Ask about your data (or use voice)...")

    if user_msg:
        st.session_state.chat_history.append({"role": "user", "content": user_msg})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(user_msg)

        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                try:
                    run = st.session_state.agent.run(user_msg)
                    answer = getattr(run, "final_answer", None) or "(No response)"
                    called = getattr(run, "_called_tools", None)
                except Exception as e:
                    answer = f"❌ Error: {e}"
                    called = None
            st.markdown(answer)
            if called:
                st.caption(f"🔧 Tools used: {', '.join(called)}")

        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    # Quick actions
    st.markdown("---")
    st.markdown("### 💡 Quick Actions")
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        if st.button("📋 List datasets"):
            st.session_state.pending_msg = "List all available datasets"
            st.rerun()
    with q2:
        if st.button("📊 Summary stats"):
            st.session_state.pending_msg = "Show summary statistics of the current dataset"
            st.rerun()
    with q3:
        if st.button("🎯 Find outliers"):
            st.session_state.pending_msg = "Find outliers in the current dataset"
            st.rerun()
    with q4:
        if st.button("📈 Generate charts"):
            st.session_state.pending_msg = "Generate all charts for the current dataset"
            st.rerun()


# ============================================================
# REPORT PAGE
# ============================================================
elif page == "📄 Report":
    st.markdown('<h1 class="welcome-title">Generate Report</h1>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        file_input = st.text_input("Dataset file path (relative or absolute)")

        if st.button("📄 Generate Report"):
            try:
                report = generate_report(file_input)
                st.session_state.report = report
                st.success("✅ Report generated!")
            except Exception as e:
                st.error(f"❌ Report failed: {e}")

        if st.session_state.report:
            rep = st.session_state.report
            if isinstance(rep, dict):
                if "report_md" in rep:
                    st.markdown(rep["report_md"])
                if "report_path" in rep:
                    try:
                        with open(rep["report_path"], "r", encoding="utf-8") as f:
                            content = f.read()
                        st.download_button(
                            "⬇️ Download Report",
                            content,
                            file_name=Path(rep["report_path"]).name,
                            mime="text/markdown",
                        )
                    except Exception as e:
                        st.warning(f"Could not read report file: {e}")


# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#5A7A9A; font-size:12px;">'
    '🤖 Velora AI · Voice Enabled · Built with Streamlit'
    '</p>',
    unsafe_allow_html=True,
)