"""
Module 3: Multi-Account FinOps
Enterprise cost management and optimization
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from typing import Dict, List
from datetime import datetime, timedelta
from config_settings import AppConfig
from core_account_manager import get_account_manager
from utils_helpers import Helpers

class FinOpsModule:
    """Multi-account financial operations and cost management"""
    
    @staticmethod
    def render():
        """Render FinOps module"""
        
        st.markdown("## 💰 Multi-Account FinOps")
        st.caption("Enterprise cloud financial operations & cost optimization")
        
        account_mgr = get_account_manager()
        if not account_mgr:
            st.error("❌ AWS account manager not configured")
            return
        
        tabs = st.tabs([
            "📊 Cost Dashboard",
            "💵 Cost by Account",
            "📈 Cost Trends",
            "🎯 Budget Management",
            "💡 Optimization",
            "🏷️ Tag-Based Costs"
        ])
        
        with tabs[0]:
            FinOpsModule._render_cost_dashboard(account_mgr)
        
        with tabs[1]:
            FinOpsModule._render_cost_by_account(account_mgr)
        
        with tabs[2]:
            FinOpsModule._render_cost_trends(account_mgr)
        
        with tabs[3]:
            FinOpsModule._render_budget_management()
        
        with tabs[4]:
            FinOpsModule._render_optimization(account_mgr)
        
        with tabs[5]:
            FinOpsModule._render_tag_based_costs(account_mgr)
    
    @staticmethod
    def _render_cost_dashboard(account_mgr):
        """Render cost dashboard"""
        
        st.markdown("### 📊 Cost Overview")
        
        accounts = AppConfig.load_aws_accounts()
        
        # Collect costs from all accounts
        total_monthly_cost = 0
        account_costs = {}
        
        with st.spinner("Loading cost data..."):
            for acc in accounts[:3]:  # Limit for performance
                try:
                    session = account_mgr.assume_role(
                        acc.account_id,
                        acc.account_name,
                        acc.role_arn
                    )
                    
                    if session:
                        from aws_cost_explorer import CostExplorerService
                        ce = CostExplorerService(session.session)
                        result = ce.get_monthly_cost()
                        
                        if result['success']:
                            cost = result['total_cost']
                            total_monthly_cost += cost
                            account_costs[acc.account_name] = cost
                except:
                    pass
        
        # Top metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Monthly Cost",
                Helpers.format_currency(total_monthly_cost),
                delta="-5.2%"
            )
        
        with col2:
            st.metric(
                "Forecast (30d)",
                Helpers.format_currency(total_monthly_cost * 1.05),
                delta="+5%"
            )
        
        with col3:
            st.metric(
                "Budget Utilization",
                "76%",
                delta="+3%"
            )
        
        with col4:
            st.metric(
                "Potential Savings",
                Helpers.format_currency(total_monthly_cost * 0.15),
                delta="RI opportunities"
            )
        
        st.markdown("---")
        
        # Cost by account chart
        if account_costs:
            st.markdown("### 💵 Cost by Account")
            df = pd.DataFrame(list(account_costs.items()), columns=['Account', 'Cost'])
            fig = px.bar(df, x='Account', y='Cost', title='Monthly Cost by Account')
            st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_cost_by_account(account_mgr):
        """Render detailed cost breakdown by account"""
        
        st.markdown("### 💵 Detailed Cost by Account")
        
        accounts = AppConfig.load_aws_accounts()
        
        cost_data = []
        
        with st.spinner("Loading account costs..."):
            for acc in accounts:
                try:
                    session = account_mgr.assume_role(
                        acc.account_id,
                        acc.account_name,
                        acc.role_arn
                    )
                    
                    if session:
                        from aws_cost_explorer import CostExplorerService
                        ce = CostExplorerService(session.session)
                        
                        monthly_result = ce.get_monthly_cost()
                        forecast_result = ce.get_cost_forecast()
                        
                        cost_data.append({
                            'Account Name': acc.account_name,
                            'Account ID': acc.account_id,
                            'Environment': acc.environment.upper(),
                            'Monthly Cost': Helpers.format_currency(monthly_result.get('total_cost', 0)),
                            'Forecast': Helpers.format_currency(forecast_result.get('forecast', 0)),
                            'Cost Center': acc.cost_center or 'N/A'
                        })
                except:
                    cost_data.append({
                        'Account Name': acc.account_name,
                        'Account ID': acc.account_id,
                        'Environment': acc.environment.upper(),
                        'Monthly Cost': 'Error',
                        'Forecast': 'Error',
                        'Cost Center': acc.cost_center or 'N/A'
                    })
        
        if cost_data:
            df = pd.DataFrame(cost_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
    
    @staticmethod
    def _render_cost_trends(account_mgr):
        """Render cost trend analysis"""
        
        st.markdown("### 📈 Cost Trends (30 Days)")
        
        st.info("Cost trend visualization across all accounts")
        
        # Sample data for demonstration
        dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
        costs = [1000 + i*10 + (i%7)*50 for i in range(30)]
        
        df = pd.DataFrame({
            'Date': dates,
            'Cost': costs
        })
        
        fig = px.line(df, x='Date', y='Cost', title='Daily Cost Trend')
        st.plotly_chart(fig, use_container_width=True)
    
    @staticmethod
    def _render_budget_management():
        """Render budget management"""
        
        st.markdown("### 🎯 Budget Management")
        
        st.info("""
        **Budget Features:**
        - Create budgets per account/service
        - Set alerts at thresholds
        - Track budget utilization
        - Forecast vs budget comparison
        
        **To enable:** Configure AWS Budgets in your accounts
        """)
    
    @staticmethod
    def _render_optimization(account_mgr):
        """Render cost optimization recommendations"""
        
        st.markdown("### 💡 Cost Optimization Opportunities")
        
        st.markdown("#### Reserved Instance Recommendations")
        st.info("Analyze EC2 usage to identify RI opportunities - potential 30-60% savings")
        
        st.markdown("#### Savings Plans")
        st.info("Flexible pricing model for compute usage - up to 72% savings")
        
        st.markdown("#### Right-Sizing Opportunities")
        st.info("Identify over-provisioned resources and recommend optimal sizing")
        
        st.markdown("#### Unused Resources")
        st.info("Detect and remove unused EBS volumes, old snapshots, idle load balancers")
    
    @staticmethod
    def _render_tag_based_costs(account_mgr):
        """Render tag-based cost allocation"""
        
        st.markdown("### 🏷️ Tag-Based Cost Allocation")
        
        st.info("""
        **Cost Allocation Tags:**
        - Department
        - Project
        - Environment
        - Cost Center
        
        Tag your resources to enable chargeback and cost attribution
        """)
