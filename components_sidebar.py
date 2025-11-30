"""
Global Sidebar Component
"""

import streamlit as st
from core_session_manager import SessionManager
from config_settings import AppConfig
from datetime import datetime

class GlobalSidebar:
    """Global sidebar with filters and controls"""
    
    @staticmethod
    def render():
        """Render global sidebar"""
        
        with st.sidebar:
            st.markdown("### 🎛️ Global Filters")
            
            # Load accounts
            accounts = AppConfig.load_aws_accounts()
            active_accounts = [acc for acc in accounts if acc.status == 'active']
            
            # Account selector
            account_options = ['All Accounts'] + [f"{acc.account_name} ({acc.account_id})" for acc in active_accounts]
            selected_account = st.selectbox(
                "Account",
                options=account_options,
                key='account_filter',
                help="Select AWS account to filter resources"
            )
            
            # Update session state
            if selected_account == 'All Accounts':
                SessionManager.set('selected_accounts', 'all')
            else:
                # Extract account ID from selection
                account_id = selected_account.split('(')[1].split(')')[0]
                SessionManager.set('selected_accounts', account_id)
            
            # Region selector
            region_options = ['All Regions'] + AppConfig.DEFAULT_REGIONS
            selected_region = st.selectbox(
                "Region",
                options=region_options,
                key='region_filter',
                help="Select AWS region"
            )
            
            # Update session state
            if selected_region == 'All Regions':
                SessionManager.set('selected_regions', 'all')
            else:
                SessionManager.set('selected_regions', selected_region)
            
            # Environment filter
            env_options = ['All Environments', 'Production', 'Development', 'Staging', 'Sandbox']
            selected_env = st.selectbox(
                "Environment",
                options=env_options,
                key='env_filter'
            )
            
            SessionManager.set('selected_environment', 
                             'all' if selected_env == 'All Environments' else selected_env.lower())
            
            st.markdown("---")
            
            # Time range for analytics
            st.markdown("### 📅 Time Range")
            time_range = st.selectbox(
                "Period",
                options=['Last 24 Hours', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days'],
                index=2,
                key='time_range'
            )
            
            SessionManager.set('time_range', time_range)
            
            st.markdown("---")
            
            # Refresh controls
            st.markdown("### 🔄 Data Refresh")
            
            last_refresh = SessionManager.get('last_refresh', datetime.now())
            st.caption(f"Last refresh: {last_refresh.strftime('%H:%M:%S')}")
            
            if st.button("🔄 Refresh Now", use_container_width=True):
                SessionManager.trigger_refresh()
                st.cache_data.clear()
                st.rerun()
            
            auto_refresh = st.checkbox("Auto-refresh (5 min)", value=False)
            if auto_refresh:
                import time
                time.sleep(300)  # 5 minutes
                st.rerun()
            
            st.markdown("---")
            
            # Platform stats
            st.markdown("### 📊 Platform Stats")
            st.metric("Connected Accounts", len(active_accounts))
            st.metric("Active Regions", len(AppConfig.DEFAULT_REGIONS))
            
            # Account health
            st.markdown("### 🏥 Account Health")
            for acc in active_accounts[:3]:  # Show first 3
                status_icon = "✅" if acc.status == "active" else "❌"
                st.caption(f"{status_icon} {acc.account_name}")
            
            if len(active_accounts) > 3:
                st.caption(f"... and {len(active_accounts) - 3} more")
