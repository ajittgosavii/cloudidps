"""
EKS Cluster Management Module
Complete EKS cluster lifecycle management
"""

import streamlit as st
import pandas as pd
from typing import Dict, List
from config_settings import AppConfig
from core_account_manager import get_account_manager
from core_session_manager import SessionManager
from utils_helpers import Helpers

class EKSManagementModule:
    """EKS cluster management and operations"""
    
    @staticmethod
    def render():
        """Render EKS management module"""
        
        st.markdown("## ⎈ EKS Cluster Management")
        st.caption("Manage Kubernetes clusters across AWS accounts and regions")
        
        account_mgr = get_account_manager()
        if not account_mgr:
            st.error("❌ AWS account manager not configured")
            return
        
        tabs = st.tabs([
            "📋 Cluster Overview",
            "➕ Create Cluster",
            "⚙️ Manage Clusters",
            "🔧 Node Groups",
            "📦 Add-ons",
            "💰 Cost Analysis"
        ])
        
        with tabs[0]:
            EKSManagementModule._render_cluster_overview(account_mgr)
        
        with tabs[1]:
            EKSManagementModule._render_create_cluster(account_mgr)
        
        with tabs[2]:
            EKSManagementModule._render_manage_clusters(account_mgr)
        
        with tabs[3]:
            EKSManagementModule._render_node_groups(account_mgr)
        
        with tabs[4]:
            EKSManagementModule._render_addons(account_mgr)
        
        with tabs[5]:
            EKSManagementModule._render_cost_analysis(account_mgr)
    
    @staticmethod
    def _render_cluster_overview(account_mgr):
        """Render EKS cluster overview"""
        
        st.markdown("### 📊 EKS Clusters Across Accounts")
        
        accounts = AppConfig.load_aws_accounts()
        selected_account_ids = SessionManager.get_selected_accounts()
        
        if selected_account_ids != 'all':
            accounts = [a for a in accounts if a.account_id in selected_account_ids]
        
        all_clusters = []
        total_nodes = 0
        total_cost = 0
        
        with st.spinner("Loading EKS clusters..."):
            for acc in accounts:
                for region in acc.regions:
                    try:
                        session = account_mgr.assume_role(
                            acc.account_id,
                            acc.account_name,
                            acc.role_arn
                        )
                        
                        if session:
                            from aws_eks import EKSService
                            eks = EKSService(session.session, region)
                            result = eks.list_clusters()
                            
                            if result['success']:
                                for cluster in result['clusters']:
                                    # Get cost estimate
                                    cost_info = eks.get_cluster_cost_estimate(cluster['cluster_name'])
                                    cluster_cost = cost_info.get('total_monthly_cost', 0)
                                    cluster_nodes = cost_info.get('total_nodes', 0)
                                    
                                    all_clusters.append({
                                        'Cluster Name': cluster['cluster_name'],
                                        'Account': acc.account_name,
                                        'Region': region,
                                        'Version': cluster['version'],
                                        'Status': cluster['status'],
                                        'Node Groups': cluster['nodegroup_count'],
                                        'Total Nodes': cluster_nodes,
                                        'Monthly Cost': Helpers.format_currency(cluster_cost),
                                        'Created': Helpers.time_ago(cluster['created_at']) if cluster.get('created_at') else 'N/A'
                                    })
                                    
                                    total_nodes += cluster_nodes
                                    total_cost += cluster_cost
                    except:
                        pass
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Clusters", len(all_clusters))
        with col2:
            st.metric("Total Nodes", total_nodes)
        with col3:
            st.metric("Monthly Cost", Helpers.format_currency(total_cost))
        with col4:
            active_clusters = len([c for c in all_clusters if 'ACTIVE' in str(c.get('Status', ''))])
            st.metric("Active Clusters", active_clusters)
        
        st.markdown("---")
        
        if all_clusters:
            df = pd.DataFrame(all_clusters)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export option
            if st.button("📥 Export to CSV"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "eks_clusters.csv",
                    "text/csv"
                )
        else:
            st.info("No EKS clusters found. Create your first cluster in the 'Create Cluster' tab!")
    
    @staticmethod
    def _render_create_cluster(account_mgr):
        """Render EKS cluster creation wizard"""
        
        st.markdown("### ➕ Create New EKS Cluster")
        
        accounts = AppConfig.load_aws_accounts()
        
        with st.form("create_eks_cluster"):
            st.markdown("#### Basic Configuration")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Account selection
                selected_account = st.selectbox(
                    "Target Account *",
                    options=[f"{a.account_name} ({a.account_id})" for a in accounts]
                )
                
                account_id = selected_account.split('(')[1].split(')')[0]
                account = next((a for a in accounts if a.account_id == account_id), None)
                
                # Region selection
                selected_region = st.selectbox(
                    "Region *",
                    options=account.regions if account else ['us-east-1']
                )
                
                # Cluster name
                cluster_name = st.text_input(
                    "Cluster Name *",
                    placeholder="my-eks-cluster",
                    help="Name for your EKS cluster"
                )
            
            with col2:
                # Kubernetes version
                from aws_eks import EKSService
                temp_session = account_mgr.assume_role(
                    account.account_id,
                    account.account_name,
                    account.role_arn
                )
                
                if temp_session:
                    eks = EKSService(temp_session.session, selected_region)
                    k8s_versions = eks.get_available_kubernetes_versions()
                else:
                    k8s_versions = ['1.28', '1.29', '1.30']
                
                kubernetes_version = st.selectbox(
                    "Kubernetes Version *",
                    options=k8s_versions,
                    index=len(k8s_versions)-1  # Latest version
                )
                
                # Cluster role ARN
                cluster_role_arn = st.text_input(
                    "Cluster IAM Role ARN *",
                    placeholder="arn:aws:iam::123456789012:role/eks-cluster-role",
                    help="IAM role for EKS cluster"
                )
            
            st.markdown("#### Network Configuration")
            
            vpc_id = st.text_input(
                "VPC ID *",
                placeholder="vpc-xxxxxxxxx",
                help="VPC where cluster will be deployed"
            )
            
            subnet_ids = st.text_area(
                "Subnet IDs * (comma-separated)",
                placeholder="subnet-xxx, subnet-yyy, subnet-zzz",
                help="At least 2 subnets in different AZs"
            )
            
            st.markdown("#### Node Group Configuration")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if temp_session:
                    instance_types_by_category = eks.get_recommended_instance_types()
                    category = st.selectbox(
                        "Instance Category",
                        options=list(instance_types_by_category.keys())
                    )
                    instance_type = st.selectbox(
                        "Instance Type",
                        options=instance_types_by_category[category]
                    )
                else:
                    instance_type = st.selectbox(
                        "Instance Type",
                        options=['t3.medium', 't3.large', 'm5.large']
                    )
            
            with col2:
                desired_size = st.number_input("Desired Nodes", min_value=1, max_value=100, value=3)
                min_size = st.number_input("Min Nodes", min_value=1, max_value=100, value=1)
            
            with col3:
                max_size = st.number_input("Max Nodes", min_value=1, max_value=100, value=10)
                disk_size = st.number_input("Disk Size (GB)", min_value=20, max_value=1000, value=20)
            
            st.markdown("#### Additional Options")
            
            col1, col2 = st.columns(2)
            
            with col1:
                enable_logging = st.checkbox("Enable Control Plane Logging", value=True)
                public_access = st.checkbox("Enable Public API Access", value=True)
            
            with col2:
                private_access = st.checkbox("Enable Private API Access", value=True)
                node_role_arn = st.text_input(
                    "Node IAM Role ARN *",
                    placeholder="arn:aws:iam::123456789012:role/eks-node-role"
                )
            
            # Tags
            st.markdown("#### Tags")
            tags_text = st.text_area(
                "Tags (key=value, one per line)",
                placeholder="Environment=production\nManagedBy=CloudIDP\nProject=MyApp"
            )
            
            # Estimate cost
            if instance_type and desired_size:
                st.markdown("#### Cost Estimate")
                st.info(f"""
                **Estimated Monthly Cost:**
                - EKS Control Plane: $73.00
                - Worker Nodes ({desired_size}x {instance_type}): ~${desired_size * 30}.00
                - **Total: ~${73 + (desired_size * 30)}.00/month**
                
                *Note: Actual costs may vary based on data transfer and additional services*
                """)
            
            # Submit button
            submitted = st.form_submit_button("🚀 Create EKS Cluster", type="primary")
            
            if submitted:
                if not cluster_name or not cluster_role_arn or not vpc_id or not subnet_ids or not node_role_arn:
                    st.error("❌ Please fill in all required fields (marked with *)")
                else:
                    with st.spinner("Creating EKS cluster... This may take 10-15 minutes"):
                        # Parse subnets
                        subnets = [s.strip() for s in subnet_ids.split(',')]
                        
                        # Parse tags
                        tags = {}
                        if tags_text:
                            for line in tags_text.strip().split('\n'):
                                if '=' in line:
                                    key, value = line.split('=', 1)
                                    tags[key.strip()] = value.strip()
                        
                        # Add CloudIDP tag
                        tags['ManagedBy'] = 'CloudIDP'
                        
                        # Create VPC config
                        vpc_config = {
                            'subnetIds': subnets,
                            'endpointPublicAccess': public_access,
                            'endpointPrivateAccess': private_access
                        }
                        
                        try:
                            session = account_mgr.assume_role(
                                account.account_id,
                                account.account_name,
                                account.role_arn
                            )
                            
                            if session:
                                eks = EKSService(session.session, selected_region)
                                
                                # Create cluster
                                success, cluster_arn, error = eks.create_cluster(
                                    cluster_name=cluster_name,
                                    kubernetes_version=kubernetes_version,
                                    role_arn=cluster_role_arn,
                                    vpc_config=vpc_config,
                                    enable_logging=enable_logging,
                                    tags=tags
                                )
                                
                                if success:
                                    st.success(f"✅ EKS Cluster '{cluster_name}' creation initiated!")
                                    st.info(f"Cluster ARN: {cluster_arn}")
                                    
                                    # Create node group
                                    scaling_config = {
                                        'desiredSize': desired_size,
                                        'minSize': min_size,
                                        'maxSize': max_size
                                    }
                                    
                                    st.info("Creating managed node group...")
                                    ng_success, ng_error = eks.create_nodegroup(
                                        cluster_name=cluster_name,
                                        nodegroup_name=f"{cluster_name}-nodegroup",
                                        node_role_arn=node_role_arn,
                                        subnets=subnets,
                                        instance_types=[instance_type],
                                        scaling_config=scaling_config,
                                        disk_size=disk_size,
                                        tags=tags
                                    )
                                    
                                    if ng_success:
                                        st.success("✅ Node group creation initiated!")
                                        st.balloons()
                                        st.info("""
                                        **Next Steps:**
                                        1. Wait 10-15 minutes for cluster to become active
                                        2. Configure kubectl: `aws eks update-kubeconfig --name {}`
                                        3. Verify: `kubectl get nodes`
                                        """.format(cluster_name))
                                    else:
                                        st.warning(f"⚠️ Node group creation failed: {ng_error}")
                                else:
                                    st.error(f"❌ Cluster creation failed: {error}")
                            else:
                                st.error("❌ Failed to assume role in target account")
                                
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
    
    @staticmethod
    def _render_manage_clusters(account_mgr):
        """Render cluster management operations"""
        
        st.markdown("### ⚙️ Manage Existing Clusters")
        st.info("Select a cluster to perform operations")
    
    @staticmethod
    def _render_node_groups(account_mgr):
        """Render node group management"""
        
        st.markdown("### 🔧 Node Group Management")
        st.info("Manage EKS managed node groups")
    
    @staticmethod
    def _render_addons(account_mgr):
        """Render EKS addons management"""
        
        st.markdown("### 📦 EKS Add-ons")
        
        st.info("""
        **Available EKS Add-ons:**
        - vpc-cni - Amazon VPC CNI plugin
        - coredns - CoreDNS for service discovery
        - kube-proxy - Kubernetes network proxy
        - aws-ebs-csi-driver - EBS CSI driver
        - aws-efs-csi-driver - EFS CSI driver
        """)
    
    @staticmethod
    def _render_cost_analysis(account_mgr):
        """Render EKS cost analysis"""
        
        st.markdown("### 💰 EKS Cost Analysis")
        
        st.info("""
        **EKS Cost Components:**
        - **Control Plane:** $0.10/hour = $73/month per cluster
        - **Worker Nodes:** EC2 instance pricing
        - **Data Transfer:** Standard AWS data transfer rates
        - **EBS Volumes:** GP2/GP3 storage pricing
        - **Load Balancers:** ALB/NLB pricing if used
        """)
