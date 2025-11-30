"""
CloudIDP v2.0 - Enterprise Multi-Account Cloud Infrastructure Development Platform
Multi-Account | Multi-Region | Real-Time AWS Integration
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from config_settings import AppConfig
from core_session_manager import SessionManager
from components_navigation_complete import Navigation
from components_sidebar import GlobalSidebar

# Page configuration
st.set_page_config(
    page_title="CloudIDP v2.0 - Enterprise Cloud Platform",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main theme */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Account badge */
    .account-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        background: #f0f2f6;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    /* Status indicators */
    .status-healthy { color: #00c851; }
    .status-warning { color: #ffbb33; }
    .status-error { color: #ff4444; }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
    
    /* Resource table */
    .resource-table {
        font-size: 0.875rem;
    }
    
    /* Header */
    .app-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 0.5rem;
        margin-bottom: 2rem;
    }
    
    /* Navigation tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application entry point"""
    
    # Initialize session
    SessionManager.initialize()
    
    # Render header
    st.markdown("""
    <div class="app-header">
        <h1>☁️ CloudIDP v2.0</h1>
        <p>Enterprise Multi-Account Cloud Infrastructure Development Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Render global sidebar
    GlobalSidebar.render()
    
    # Render main navigation
    Navigation.render()
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    with col2:
        st.caption(f"🔗 Connected Accounts: {SessionManager.get_active_account_count()}")
    with col3:
        st.caption("🚀 CloudIDP v2.0 - Enterprise Edition")

if __name__ == "__main__":
    main()
