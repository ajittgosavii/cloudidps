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
            "👥 Account Management",
            "📦 Resource Inventory",
            "🌐 Network (VPC)",
            "🏢 Organizations",
            "⚡ EKS Management",
            "🔒 Security & Compliance",
            "💰 FinOps & Cost",
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
        
        # Module 3: Network Management (VPC)
        with tabs[3]:
            from modules_network_management import NetworkManagementUI
            NetworkManagementUI.render()
        
        # Module 4: Organizations
        with tabs[4]:
            from modules_organizations import OrganizationsManagementUI
            OrganizationsManagementUI.render()
        
        # Module 5: EKS Management
        with tabs[5]:
            from modules_eks_management import EKSManagementModule
            EKSManagementModule.render()
        
        # Module 6: Security & Compliance
        with tabs[6]:
            from modules_security_compliance import SecurityComplianceUI
            SecurityComplianceUI.render()
        
        # Module 7: FinOps
        with tabs[7]:
            from modules_finops import FinOpsModule
            FinOpsModule.render()
        
        # Module 8: Account Lifecycle
        with tabs[8]:
            from modules_account_lifecycle import AccountLifecycleModule
            AccountLifecycleModule.render()
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
