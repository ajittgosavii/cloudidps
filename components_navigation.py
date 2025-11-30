"""
Main Navigation Component
"""

import streamlit as st
from core_session_manager import SessionManager

class Navigation:
    """Main application navigation"""
    
    @staticmethod
    def render():
        """Render main navigation tabs"""
        
        # Main tabs
        tabs = st.tabs([
            "🏠 Dashboard",
            "🏢 Accounts & Regions",
            "📦 Resource Inventory",
            "💰 FinOps",
            "📐 Design & Planning",
            "🚀 Provisioning",
            "⚙️ Operations",
            "🔒 Security",
            "🔄 Account Lifecycle"
        ])
        
        # Module 0: Dashboard
        with tabs[0]:
            from modules_dashboard import DashboardModule
            DashboardModule.render()
        
        # Module 1: Account Management
        with tabs[1]:
            from modules_account_management import AccountManagementModule
            AccountManagementModule.render()
        
        # Module 2: Resource Inventory
        with tabs[2]:
            from modules_resource_inventory import ResourceInventoryModule
            ResourceInventoryModule.render()
        
        # Module 3: FinOps
        with tabs[3]:
            from modules_finops import FinOpsModule
            FinOpsModule.render()
        
        # Module 4: Design & Planning
        with tabs[4]:
            from modules.design_planning import DesignPlanningModule
            DesignPlanningModule.render()
        
        # Module 5: Provisioning
        with tabs[5]:
            from modules.provisioning import ProvisioningModule
            ProvisioningModule.render()
        
        # Module 6: Operations
        with tabs[6]:
            from modules.operations import OperationsModule
            OperationsModule.render()
        
        # Module 7: Security
        with tabs[7]:
            from modules.security import SecurityModule
            SecurityModule.render()
        
        # Module 8: Account Lifecycle
        with tabs[8]:
            from modules.account_lifecycle_ui import AccountLifecycleUI
            AccountLifecycleUI.render()
