"""
Professional AI Agent Dashboard
Combines old features with new dark theme design.
"""
import sys
from pathlib import Path

# ---- Fix import path so "from src.xxx" works ----
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd
from io import BytesIO

from src.data.uploader import upload_file, UploadError
from src.data.loader import load_dataset, get_basic_info, DataLoadError
from src.data.cleaner import clean_dataset
from src.data.analyzer import full_analysis, summary_statistics
from src.data.visualizer import generate_all_charts
from src.data.reporter import generate_report

# ============ PAGE CONFIG ============
st.set_page_config(
    page_title="Velora AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============ CUSTOM CSS (DARK THEME) ============
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
    p, label, span, div { color: #B8D4F0; }

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
    .metric-card {
        background: rgba(30, 58, 95, 0.5);
        border: 1px solid rgba(74, 158, 255, 0.3);
        border-radius: 12px;
        padding: 15px;
        text-align: center;
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


# ============ SESSION STATE ============
if "df" not in st.session_state:
    st.session_state.df = None
if "df_info" not in st.session_state:
    st.session_state.df_info = None
if "analysis" not in st.session_state:
    st.session_state.analysis = None
if "cleaning_report" not in st.session_state:
    st.session_state.cleaning_report = None
if "chart_paths" not in st.session_state:
    st.session_state.chart_paths = None
if "report" not in st.session_state:
    st.session_state.report = None


# ============ SIDEBAR ============
with st.sidebar:
    st.markdown('<h2 style="color:#7EB6FF;">🤖 Velora AI</h2>', unsafe_allow_html=True)
    st.markdown("---")

    page = st.radio(
        "📌 Navigation",
        ["🏠 Home", "📁 Upload Data", "🧹 Clean", "📊 Analyze", "📈 Charts", "📄 Report"],
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown(
        '<p style="font-size:12px; color:#5A7A9A;">v1.0 · Powered by your AI Agent</p>',
        unsafe_allow_html=True,
    )


# ============ HOME PAGE ============
if page == "🏠 Home":
    st.markdown('<h1 class="welcome-title">Welcome Back Rolex!</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="welcome-subtitle">Upload a dataset to begin your AI-powered analysis.</p>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="glass-box" style="text-align:center;">
            <div style="font-size:36px;">📁</div>
            <h3 style="color:#7EB6FF;">Upload</h3>
            <p>CSV or Excel files</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="glass-box" style="text-align:center;">
            <div style="font-size:36px;">📊</div>
            <h3 style="color:#7EB6FF;">Analyze</h3>
            <p>Stats, outliers, correlations</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="glass-box" style="text-align:center;">
            <div style="font-size:36px;">📈</div>
            <h3 style="color:#7EB6FF;">Visualize</h3>
            <p>Charts & reports</p>
        </div>
        """, unsafe_allow_html=True)

    if st.session_state.df is not None:
        st.success(f"✅ Dataset loaded: **{st.session_state.df.shape[0]} rows × {st.session_state.df.shape[1]} columns**")


# ============ UPLOAD PAGE ============
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
                df = load_dataset(info.get("saved_path", tmp_path))
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
            col1, col2, col3 = st.columns(3)
            col1.metric("Rows", info.get("rows", "—"))
            col2.metric("Columns", info.get("columns", "—"))
            col3.metric("Memory", f"{info.get('memory_mb', 0):.2f} MB")


# ============ CLEAN PAGE ============
elif page == "🧹 Clean":
    st.markdown('<h1 class="welcome-title">Clean Data</h1>', unsafe_allow_html=True)

    if st.session_state.df is None:
        st.warning("⚠️ Please upload a dataset first.")
    else:
        if st.button("🧹 Run Cleaning"):
            try:
                cleaned, report = clean_dataset(st.session_state.df)
                st.session_state.df = cleaned
                st.session_state.cleaning_report = report
                st.success("✅ Cleaning complete!")
            except Exception as e:
                st.error(f"❌ Cleaning failed: {e}")

        if st.session_state.cleaning_report:
            st.markdown("### 📋 Cleaning Report")
            rep = st.session_state.cleaning_report
            st.json(rep.__dict__ if hasattr(rep, "__dict__") else str(rep))
            st.markdown("### 📋 Cleaned Preview")
            st.dataframe(st.session_state.df.head(20), use_container_width=True)


# ============ ANALYZE PAGE ============
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

            st.markdown("### 📈 Summary Statistics")
            if "summary" in analysis:
                st.dataframe(analysis["summary"], use_container_width=True)

            st.markdown("### 🔗 Correlation Matrix")
            if "correlation" in analysis:
                st.dataframe(analysis["correlation"], use_container_width=True)

            st.markdown("### 🎯 Outliers")
            if "outliers" in analysis:
                st.json(analysis["outliers"])

            st.markdown("### 📊 Value Counts")
            if "value_counts" in analysis:
                for col, vals in analysis["value_counts"].items():
                    st.markdown(f"**{col}**")
                    st.dataframe(pd.DataFrame(vals), use_container_width=True)


# ============ CHARTS PAGE ============
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
            st.markdown("### 🖼️ Generated Charts")
            charts = st.session_state.chart_paths
            if isinstance(charts, dict):
                for name, paths in charts.items():
                    st.markdown(f"**{name}**")
                    if isinstance(paths, list):
                        for p in paths:
                            st.image(str(p), use_container_width=True)
                    elif paths:
                        st.image(str(paths), use_container_width=True)


# ============ REPORT PAGE ============
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
                    with open(rep["report_path"], "r", encoding="utf-8") as f:
                        content = f.read()
                    st.download_button(
                        "⬇️ Download Report",
                        content,
                        file_name=Path(rep["report_path"]).name,
                        mime="text/markdown",
                    )


# ============ FOOTER ============
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#5A7A9A; font-size:12px;">'
    '🤖 Velora AI · Built with Streamlit'
    '</p>',
    unsafe_allow_html=True,
)