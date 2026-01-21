import streamlit as st
import json
from dotenv import load_dotenv
load_dotenv()


from github_utils import fetch_github_issue
from hf import analyze_issue_with_ai
from cache_utils import get_cached_analysis, cache_analysis

# Page configuration
st.set_page_config(
    page_title="Issue Analyzer - SeedlingLabs",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for page navigation
if "page" not in st.session_state:
    st.session_state.page = "home"
if "result" not in st.session_state:
    st.session_state.result = None
if "repo_url" not in st.session_state:
    st.session_state.repo_url = ""
if "issue_number" not in st.session_state:
    st.session_state.issue_number = 0

# Unique Modern CSS with SeedlingLabs branding - Industrial Level Design
st.markdown("""
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 25%, #0d2d3d 50%, #1a1f3a 75%, #0a0e27 100%);
            min-height: 100vh;
            background-attachment: fixed;
        }
        
        .main { 
            background: transparent !important;
            padding: 10px !important;
        }
        
        /* Hero Header */
        .hero-container {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 76, 58, 0.95) 100%);
            border-radius: 20px;
            padding: 30px 30px;
            margin-bottom: 15px;
            margin-top: 10px;
            border: 2px solid rgba(6, 182, 212, 0.3);
            box-shadow: 0 8px 32px rgba(6, 182, 212, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            text-align: center;
            backdrop-filter: blur(10px);
        }
        
        .hero-container h1 {
            font-size: 2.8em;
            font-weight: 900;
            background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        
        .hero-container h2 {
            font-size: 1.8em;
            font-weight: 800;
            background: linear-gradient(135deg, #06b6d4 0%, #10b981 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        
        .hero-container p {
            font-size: 1.2em;
            color: #cbd5e1;
            font-weight: 300;
            letter-spacing: 0.5px;
            margin-bottom: 10px;
        }
        
        .welcome-text {
            font-size: 1.1em;
            color: #a0aec0;
            font-weight: 400;
            letter-spacing: 0.3px;
            line-height: 1.8;
            margin-top: 15px;
        }
        
        .brand-tag {
            display: inline-block;
            background: rgba(6, 182, 212, 0.2);
            color: #06b6d4;
            padding: 6px 16px;
            border-radius: 25px;
            font-size: 0.85em;
            margin-top: 15px;
            border: 1px solid rgba(6, 182, 212, 0.4);
            font-weight: 600;
        }
        
        /* Logo Container */
        .logo-container {
            text-align: center;
            margin-bottom: 15px;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .logo-container img {
            max-width: 180px;
            height: auto;
            filter: drop-shadow(0 4px 15px rgba(6, 182, 212, 0.2));
        }
        
        /* Input Section */
        .input-container {
            background: rgba(30, 41, 59, 0.9);
            backdrop-filter: blur(10px);
            border: 2px solid rgba(6, 182, 212, 0.3);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 15px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        
        .input-label {
            color: #cbd5e1;
            font-weight: 700;
            font-size: 0.95em;
            margin-bottom: 10px;
            display: block;
            letter-spacing: 0.5px;
        }
        
        /* Result Card */
        .result-card {
            background: rgba(15, 23, 42, 0.95);
            border: 2px solid rgba(6, 182, 212, 0.3);
            border-radius: 16px;
            padding: 28px;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.05);
            margin-bottom: 20px;
        }
        
        .result-card:hover {
            border-color: rgba(6, 182, 212, 0.6);
            transform: translateY(-3px);
            box-shadow: 0 12px 40px rgba(6, 182, 212, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        }
        
        .result-card.summary {
            background: rgba(6, 182, 212, 0.08);
            border: 2px solid rgba(6, 182, 212, 0.4);
        }
        
        .result-card h3 {
            color: #06b6d4;
            font-size: 1.15em;
            margin-bottom: 12px;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .result-card p {
            color: #e2e8f0;
            line-height: 1.7;
            font-size: 0.95em;
        }
        
        /* Button Styles */
        .stButton > button {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
            color: white !important;
            border: none !important;
            border-radius: 10px !important;
            padding: 12px 28px !important;
            font-weight: 700 !important;
            font-size: 0.95em !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.3) !important;
            letter-spacing: 0.5px !important;
        }
        
        .stButton > button:hover {
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(6, 182, 212, 0.5) !important;
        }
        
        .stButton > button:active {
            transform: translateY(-1px) !important;
        }
        
        /* Footer */
        .footer-container {
            margin-top: 30px;
            padding-top: 15px;
            border-top: 2px solid rgba(6, 182, 212, 0.2);
            text-align: center;
            color: #64748b;
        }
        
        .seedlinglabs-logo {
            font-size: 1.2em;
            font-weight: 800;
            color: #06b6d4;
            margin-bottom: 15px;
            letter-spacing: 1px;
        }
        
        .footer-text {
            font-size: 0.9em;
            color: #94a3b8;
            line-height: 1.8;
            display: inline;
        }
        
        hr {
            border: none;
            border-top: 2px solid rgba(6, 182, 212, 0.2);
            margin: 20px 0;
        }
        
        /* Input field styling */
        .stTextInput > div > div > input,
        .stNumberInput > div > div > input {
            background-color: rgba(15, 23, 42, 0.8) !important;
            color: #e2e8f0 !important;
            border: 2px solid rgba(6, 182, 212, 0.3) !important;
            border-radius: 8px !important;
            padding: 12px 16px !important;
            font-size: 1em !important;
        }
        
        .stTextInput > div > div > input:focus,
        .stNumberInput > div > div > input:focus {
            border-color: rgba(6, 182, 212, 0.8) !important;
            box-shadow: 0 0 0 3px rgba(6, 182, 212, 0.2) !important;
        }
    </style>
""", unsafe_allow_html=True)

# PAGE 1: HOME PAGE (Welcome Page)
if st.session_state.page == "home":
    # Logo - Centered using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("seedlings-logo.png", width=150)
    
    # Hero Header
    st.markdown("""
        <div class="hero-container">
            <h1>GITHUB ISSUE ANALYZER</h1>
            <p class=\"welcome-text\">Intelligent GitHub Issue Classification & Analysis Platform</p>\n            <div class=\"brand-tag\">Powered by SeedlingLabs</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Centered Start Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚀 I want to Analyze", use_container_width=True, key="home_start"):
            st.session_state.page = "input"
            st.rerun()

    # Footer
    st.markdown("""
        <div class="footer-container">
            <hr>
            <div class="seedlings-logo">SeedlingLabs</div>
            <div class="footer-text">Intelligent Issue Analysis Platform • Powered by AI • Built with Purpose • © 2026 SeedlingLabs. All rights reserved.</div>
        </div>
    """, unsafe_allow_html=True)

# PAGE 2: INPUT PAGE (Enter URL and Issue Number)
elif st.session_state.page == "input":
    # Logo - Centered using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("seedlings-logo.png", width=150)
    
    # Hero Header
    st.markdown("""
        <div class="hero-container">
            <h2>GITHUB ISSUE ANALYZER</h2>
            <p>Enter Repository Details</p>
        </div>
    """, unsafe_allow_html=True)

    # Input Section
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    
    st.markdown('<label class="input-label">GitHub Repository URL</label>', unsafe_allow_html=True)
    repo_url = st.text_input(
        "label",
        placeholder="https://github.com/facebook/react",
        label_visibility="collapsed",
        key="input_repo_url"
    )

    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown('<label class="input-label">Issue Number</label>', unsafe_allow_html=True)
    issue_number = st.number_input(
        "number",
        min_value=1,
        step=1,
        label_visibility="collapsed",
        key="input_issue_number"
    )

    st.markdown('</div>', unsafe_allow_html=True)
    
    # Centered Analyze Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        analyze_button = st.button("🔍 Analyze", use_container_width=True, key="input_analyze")

    # Handle Analysis
    if analyze_button:
        if not repo_url or not issue_number:
            st.error("❌ Please enter both repository URL and issue number.")
        else:
            result = None
            # Check cache first
            cached_result = get_cached_analysis(repo_url, issue_number)
            if cached_result:
                result = cached_result
            else:
                with st.spinner("⏳ Fetching issue..."):
                    issue_data = fetch_github_issue(repo_url, issue_number)

                if "error" in issue_data:
                    st.error(f"❌ Error: {issue_data['error']}")
                else:
                    with st.spinner("🤖 Analyzing with AI..."):
                        result = analyze_issue_with_ai(issue_data)
                    
                    if result and "error" not in result:
                        cache_analysis(repo_url, issue_number, result)

            if result and "error" not in result:
                st.session_state.result = result
                st.session_state.repo_url = repo_url
                st.session_state.issue_number = issue_number
                st.session_state.page = "results"
                st.rerun()


    # Back Button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("← Back to Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

    # Footer
    st.markdown("""
        <div class="footer-container">
            <hr>
            <div class="seedlings-logo">SeedlingLabs</div>
            <div class="footer-text">Intelligent Issue Analysis Platform • Powered by AI • Built with Purpose • © 2026 SeedlingLabs. All rights reserved.</div>
        </div>
    """, unsafe_allow_html=True)

# PAGE 3: RESULTS PAGE (Display Analysis Output)
elif st.session_state.page == "results":
    # Logo - Centered using columns
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("seedlings-logo.png", width=150)
    
    # Hero Header
    st.markdown("""
        <div class="hero-container">
            <h2>GITHUB ISSUE ANALYZER</h2>
            <p>Analysis Results</p>
        </div>
    """, unsafe_allow_html=True)

    # Issue Information
    st.markdown(f"""
        <div class="result-card summary">
            <h3>📦 Repository</h3>
            <p>{st.session_state.repo_url}</p>
            <p style='margin-top: 12px; font-size: 0.9em; color: #a0aec0;'>Issue #{st.session_state.issue_number}</p>
        </div>
    """, unsafe_allow_html=True)

    # Display Analysis Output
    st.markdown("""
        <div class="result-card">
            <h3>📊 Analysis Output (JSON)</h3>
        </div>
    """, unsafe_allow_html=True)
    
    st.json(st.session_state.result)

    # Action Buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("📝 New Issue", use_container_width=True):
            st.session_state.page = "input"
            st.session_state.result = None
            st.rerun()
    with col2:
        if st.button("🏠 Back to Home", use_container_width=True, key="results_home"):
            st.session_state.page = "home"
            st.session_state.result = None
            st.rerun()

    # Footer
    st.markdown("""
        <div class="footer-container">
            <hr>
            <div class="seedlings-logo">SeedlingLabs</div>
            <div class="footer-text">Intelligent Issue Analysis Platform • Powered by AI • Built with Purpose • © 2026 SeedlingLabs. All rights reserved.</div>
        </div>
    """, unsafe_allow_html=True)
