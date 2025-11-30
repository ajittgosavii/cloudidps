"""
Module 2: Global Resource Inventory
Cross-account resource discovery and management
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from config_settings import AppConfig
from core_account_manager import get_account_manager
from core_session_manager import SessionManager
from utils_helpers import Helpers

class ResourceInventoryModule:
    """Global resource inventory across all accounts"""
    
    @staticmethod
    def render():
        """Render resource inventory module"""
        
        st.markdown("## 📦 Global Resource Inventory")
        st.caption("Search and manage resources across all AWS accounts and regions")
        
        # Load account manager
        account_mgr = get_account_manager()
        if not account_mgr:
            st.error("❌ AWS account manager not configured")
            return
        
        # Sub-tabs
        tabs = st.tabs([
            "🔍 Resource Search",
            "💻 EC2 Instances",
            "🗄️ RDS Databases",
            "📦 S3 Buckets",
            "⚡ Lambda Functions",
            "🔢 DynamoDB Tables"
        ])
        
        with tabs[0]:
            ResourceInventoryModule._render_resource_search(account_mgr)
        
        with tabs[1]:
            ResourceInventoryModule._render_ec2_instances(account_mgr)
        
        with tabs[2]:
            ResourceInventoryModule._render_rds_databases(account_mgr)
        
        with tabs[3]:
            ResourceInventoryModule._render_s3_buckets(account_mgr)
        
        with tabs[4]:
            ResourceInventoryModule._render_lambda_functions(account_mgr)
        
        with tabs[5]:
            ResourceInventoryModule._render_dynamodb_tables(account_mgr)
    
    @staticmethod
    def _render_resource_search(account_mgr):
        """Render global resource search"""
        
        st.markdown("### 🔍 Search All Resources")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            search_text = st.text_input(
                "Search",
                placeholder="Enter resource ID, name, or tag...",
                help="Search across all resource types"
            )
        
        with col2:
            resource_type = st.selectbox(
                "Resource Type",
                options=['All Types', 'EC2', 'RDS', 'S3', 'Lambda', 'DynamoDB']
            )
        
        with col3:
            search_scope = st.selectbox(
                "Search Scope",
                options=['All Accounts', 'Selected Account Only']
            )
        
        if st.button("🔍 Search", type="primary"):
            with st.spinner("Searching across accounts..."):
                results = ResourceInventoryModule._perform_global_search(
                    account_mgr,
                    search_text,
                    resource_type,
                    search_scope
                )
                
                if results:
                    st.success(f"✅ Found {len(results)} resources")
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No resources found matching your search criteria")
    
    @staticmethod
    def _perform_global_search(account_mgr, search_text, resource_type, scope):
        """Perform global resource search"""
        results = []
        
        accounts = AppConfig.load_aws_accounts()
        selected_accounts = SessionManager.get_selected_accounts()
        
        if scope == 'Selected Account Only' and selected_accounts != 'all':
            accounts = [a for a in accounts if a.account_id in selected_accounts]
        
        for acc in accounts[:3]:  # Limit to first 3 for performance
            try:
                session = account_mgr.assume_role(
                    acc.account_id,
                    acc.account_name,
                    acc.role_arn
                )
                
                if session and (resource_type == 'All Types' or resource_type == 'EC2'):
                    from aws_ec2 import EC2Service
                    ec2 = EC2Service(session.session, acc.regions[0])
                    ec2_result = ec2.list_instances()
                    
                    if ec2_result['success']:
                        for inst in ec2_result['instances']:
                            if not search_text or search_text.lower() in inst['instance_id'].lower():
                                results.append({
                                    'Resource Type': 'EC2',
                                    'Resource ID': inst['instance_id'],
                                    'Account': acc.account_name,
                                    'Region': acc.regions[0],
                                    'Status': inst['state'],
                                    'Tags': str(inst.get('tags', {}))
                                })
            except:
                pass
        
        return results
    
    @staticmethod
    def _render_ec2_instances(account_mgr):
        """Render EC2 instances inventory"""
        
        st.markdown("### 💻 EC2 Instances")
        
        accounts = AppConfig.load_aws_accounts()
        selected_account_ids = SessionManager.get_selected_accounts()
        
        if selected_account_ids != 'all':
            accounts = [a for a in accounts if a.account_id in selected_account_ids]
        
        all_instances = []
        
        with st.spinner("Loading EC2 instances..."):
            for acc in accounts:
                for region in acc.regions:
                    try:
                        session = account_mgr.assume_role(
                            acc.account_id,
                            acc.account_name,
                            acc.role_arn
                        )
                        
                        if session:
                            from aws_ec2 import EC2Service
                            ec2 = EC2Service(session.session, region)
                            result = ec2.list_instances()
                            
                            if result['success']:
                                for inst in result['instances']:
                                    all_instances.append({
                                        'Instance ID': inst['instance_id'],
                                        'Account': acc.account_name,
                                        'Region': region,
                                        'Type': inst['instance_type'],
                                        'State': inst['state'],
                                        'AZ': inst['availability_zone'],
                                        'Private IP': inst['private_ip'],
                                        'Public IP': inst['public_ip'],
                                        'Launch Time': Helpers.time_ago(inst['launch_time']),
                                        'Name': inst['tags'].get('Name', 'N/A')
                                    })
                    except:
                        pass
        
        if all_instances:
            st.success(f"✅ Found {len(all_instances)} EC2 instances")
            
            # Filter controls
            col1, col2 = st.columns(2)
            with col1:
                state_filter = st.multiselect(
                    "Filter by State",
                    options=['running', 'stopped', 'pending', 'terminated'],
                    default=['running']
                )
            
            # Apply filters
            filtered = [i for i in all_instances if i['State'] in state_filter]
            
            df = pd.DataFrame(filtered)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export option
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "ec2_inventory.csv",
                    "text/csv"
                )
        else:
            st.info("No EC2 instances found")
    
    @staticmethod
    def _render_rds_databases(account_mgr):
        """Render RDS databases inventory"""
        
        st.markdown("### 🗄️ RDS Databases")
        
        accounts = AppConfig.load_aws_accounts()
        all_databases = []
        
        with st.spinner("Loading RDS databases..."):
            for acc in accounts:
                for region in acc.regions:
                    try:
                        session = account_mgr.assume_role(
                            acc.account_id,
                            acc.account_name,
                            acc.role_arn
                        )
                        
                        if session:
                            from aws_rds import RDSService
                            rds = RDSService(session.session, region)
                            result = rds.list_db_instances()
                            
                            if result['success']:
                                for db in result['instances']:
                                    all_databases.append({
                                        'DB Instance ID': db['db_instance_id'],
                                        'Account': acc.account_name,
                                        'Region': region,
                                        'Engine': f"{db['engine']} {db['engine_version']}",
                                        'Class': db['db_instance_class'],
                                        'Status': db['status'],
                                        'Endpoint': db['endpoint'],
                                        'Multi-AZ': '✅' if db['multi_az'] else '❌',
                                        'Storage': f"{db['allocated_storage']} GB"
                                    })
                    except:
                        pass
        
        if all_databases:
            st.success(f"✅ Found {len(all_databases)} RDS databases")
            df = pd.DataFrame(all_databases)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No RDS databases found")
    
    @staticmethod
    def _render_s3_buckets(account_mgr):
        """Render S3 buckets inventory"""
        
        st.markdown("### 📦 S3 Buckets")
        
        accounts = AppConfig.load_aws_accounts()
        all_buckets = []
        
        with st.spinner("Loading S3 buckets..."):
            for acc in accounts:
                try:
                    session = account_mgr.assume_role(
                        acc.account_id,
                        acc.account_name,
                        acc.role_arn
                    )
                    
                    if session:
                        from aws_additional_services import S3Service
                        s3 = S3Service(session.session)
                        result = s3.list_buckets()
                        
                        if result['success']:
                            for bucket in result['buckets']:
                                all_buckets.append({
                                    'Bucket Name': bucket['bucket_name'],
                                    'Account': acc.account_name,
                                    'Region': bucket['region'],
                                    'Created': Helpers.time_ago(bucket['creation_date'])
                                })
                except:
                    pass
        
        if all_buckets:
            st.success(f"✅ Found {len(all_buckets)} S3 buckets")
            df = pd.DataFrame(all_buckets)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No S3 buckets found")
    
    @staticmethod
    def _render_lambda_functions(account_mgr):
        """Render Lambda functions inventory"""
        
        st.markdown("### ⚡ Lambda Functions")
        st.info("Lambda function inventory across accounts")
    
    @staticmethod
    def _render_dynamodb_tables(account_mgr):
        """Render DynamoDB tables inventory"""
        
        st.markdown("### 🔢 DynamoDB Tables")
        st.info("DynamoDB table inventory across accounts")
