"""
Operations Module - On-Demand Operations & Automation
Instance management, automation, scaling, and operational tasks
"""

import streamlit as st
import pandas as pd
from core_account_manager import get_account_manager, get_account_names
from aws_ec2 import EC2Service
from aws_ssm import SystemsManagerManager

class OperationsModule:
    """Operations & Automation functionality"""
    
    @staticmethod
    def render():
        """Main render method"""
        st.title("⚙️ Operations & Automation")
        
        account_mgr = get_account_manager()
        if not account_mgr:
            st.warning("⚠️ Configure AWS credentials first")
            st.info("👉 Go to the 'Account Management' tab to add your AWS accounts first.")
            return
        
        # Get account names
        account_names = get_account_names()
        
        if not account_names:
            st.warning("⚠️ No AWS accounts configured")
            st.info("👉 Go to the 'Account Management' tab to add your AWS accounts first.")
            return
        
        selected_account = st.selectbox(
            "Select AWS Account",
            options=account_names,
            key="operations_account"
        )
        
        if not selected_account:
            return
        
        session = account_mgr.get_session(selected_account)
        if not session:
            st.error("Failed to get session")
            return
        
        ec2_svc = EC2Service(session)
        ssm_mgr = SystemsManagerManager(session)
        
        # Create tabs
        tabs = st.tabs([
            "💻 Instance Operations",
            "🔄 Automation",
            "📊 Scaling",
            "🔧 Maintenance",
            "📦 Patch Management"
        ])
        
        with tabs[0]:
            OperationsModule._render_instance_ops(ec2_svc)
        
        with tabs[1]:
            OperationsModule._render_automation(ssm_mgr)
        
        with tabs[2]:
            OperationsModule._render_scaling()
        
        with tabs[3]:
            OperationsModule._render_maintenance(ssm_mgr)
        
        with tabs[4]:
            OperationsModule._render_patch_management(ssm_mgr)
    
    @staticmethod
    def _render_instance_ops(ec2_svc: EC2Service):
        """Instance operations"""
        st.subheader("💻 Instance Operations")
        
        # List instances
        instances = ec2_svc.list_instances()
        
        if not instances:
            st.info("No EC2 instances found")
            return
        
        st.metric("Total Instances", len(instances))
        
        # Bulk operations
        st.markdown("### Bulk Operations")
        
        selected_instances = st.multiselect(
            "Select Instances",
            options=[f"{i['instance_id']} ({i['name']})" for i in instances]
        )
        
        if selected_instances:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("▶️ Start Selected"):
                    st.success(f"Starting {len(selected_instances)} instance(s)")
            
            with col2:
                if st.button("⏸️ Stop Selected"):
                    st.warning(f"Stopping {len(selected_instances)} instance(s)")
            
            with col3:
                if st.button("🔄 Reboot Selected"):
                    st.info(f"Rebooting {len(selected_instances)} instance(s)")
            
            with col4:
                if st.button("🗑️ Terminate Selected"):
                    st.error(f"Terminating {len(selected_instances)} instance(s)")
        
        # Instance list with actions
        st.markdown("### Instance List")
        
        for instance in instances:
            status_icon = "🟢" if instance['state'] == "running" else "🔴" if instance['state'] == "stopped" else "🟡"
            
            with st.expander(f"{status_icon} {instance['name']} ({instance['instance_id']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Instance ID:** {instance['instance_id']}")
                    st.write(f"**Type:** {instance['instance_type']}")
                    st.write(f"**State:** {instance['state']}")
                
                with col2:
                    st.write(f"**AZ:** {instance['availability_zone']}")
                    st.write(f"**Private IP:** {instance['private_ip']}")
                    st.write(f"**Public IP:** {instance.get('public_ip', 'N/A')}")
                
                with col3:
                    st.write(f"**Launch Time:** {instance['launch_time']}")
                
                # Quick actions
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    if instance['state'] == 'stopped':
                        if st.button("▶️ Start", key=f"start_{instance['instance_id']}"):
                            st.success("Instance starting...")
                    elif instance['state'] == 'running':
                        if st.button("⏸️ Stop", key=f"stop_{instance['instance_id']}"):
                            st.warning("Instance stopping...")
                
                with col2:
                    if st.button("🔄 Reboot", key=f"reboot_{instance['instance_id']}"):
                        st.info("Instance rebooting...")
                
                with col3:
                    if st.button("📊 Monitor", key=f"monitor_{instance['instance_id']}"):
                        st.info("Opening CloudWatch metrics...")
                
                with col4:
                    if st.button("🔗 Connect", key=f"connect_{instance['instance_id']}"):
                        st.info("Opening Session Manager...")
    
    @staticmethod
    def _render_automation(ssm_mgr: SystemsManagerManager):
        """Automation workflows"""
        st.subheader("🔄 Automation Workflows")
        
        # List automation documents
        documents = ssm_mgr.list_documents(
            document_filter_list=[{'Key': 'Owner', 'Values': ['Self', 'Amazon']}]
        )
        
        if documents:
            st.metric("Available Automation Documents", len(documents))
            
            # Common automation tasks
            st.markdown("### Quick Automation Tasks")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Restart All Web Servers"):
                    st.success("Automation initiated: Restart web servers")
                
                if st.button("📦 Update All Packages"):
                    st.success("Automation initiated: Package updates")
                
                if st.button("🔐 Rotate Access Keys"):
                    st.success("Automation initiated: Key rotation")
            
            with col2:
                if st.button("💾 Create AMI Snapshots"):
                    st.success("Automation initiated: AMI creation")
                
                if st.button("🧹 Cleanup Old Snapshots"):
                    st.success("Automation initiated: Snapshot cleanup")
                
                if st.button("📊 Generate Compliance Report"):
                    st.success("Automation initiated: Compliance report")
            
            # Recent automation executions
            st.markdown("### Recent Executions")
            
            executions = ssm_mgr.describe_automation_executions(max_results=10)
            
            if executions:
                exec_df = pd.DataFrame(executions)
                st.dataframe(exec_df[['execution_id', 'document_name', 'status']], 
                           use_container_width=True)
        else:
            st.info("No automation documents available")
    
    @staticmethod
    def _render_scaling():
        """Scaling operations"""
        st.subheader("📊 Auto Scaling")
        
        st.markdown("""
        ### Manage Auto Scaling Groups
        
        Configure and monitor auto scaling for your applications.
        """)
        
        # Sample auto scaling groups
        asg_data = [
            {"Name": "web-servers-asg", "Desired": 4, "Min": 2, "Max": 10, "Current": 4, "Status": "Healthy"},
            {"Name": "api-servers-asg", "Desired": 6, "Min": 3, "Max": 15, "Current": 6, "Status": "Healthy"},
            {"Name": "worker-nodes-asg", "Desired": 2, "Min": 1, "Max": 5, "Current": 2, "Status": "Healthy"}
        ]
        
        for asg in asg_data:
            with st.expander(f"📊 {asg['Name']} - {asg['Status']}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Desired", asg['Desired'])
                with col2:
                    st.metric("Current", asg['Current'])
                with col3:
                    st.metric("Min", asg['Min'])
                with col4:
                    st.metric("Max", asg['Max'])
                
                # Scaling actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    new_desired = st.number_input(f"Set Desired Capacity",
                                                 min_value=asg['Min'],
                                                 max_value=asg['Max'],
                                                 value=asg['Desired'],
                                                 key=f"desired_{asg['Name']}")
                
                with col2:
                    if st.button("Apply", key=f"apply_{asg['Name']}"):
                        st.success(f"Scaling {asg['Name']} to {new_desired} instances")
                
                with col3:
                    if st.button("Refresh", key=f"refresh_{asg['Name']}"):
                        st.info("Refreshing...")
    
    @staticmethod
    def _render_maintenance(ssm_mgr: SystemsManagerManager):
        """Maintenance windows"""
        st.subheader("🔧 Maintenance Windows")
        
        st.markdown("""
        ### Schedule Maintenance Tasks
        
        Define maintenance windows for automated tasks and updates.
        """)
        
        # Maintenance windows
        maintenance_windows = [
            {"Name": "Weekly Patching", "Schedule": "Every Sunday 2:00 AM UTC", "Duration": "4 hours", "Enabled": True},
            {"Name": "Monthly AMI Creation", "Schedule": "First Sunday 1:00 AM UTC", "Duration": "2 hours", "Enabled": True},
            {"Name": "Quarterly DR Test", "Schedule": "First Saturday of Quarter", "Duration": "8 hours", "Enabled": False}
        ]
        
        for mw in maintenance_windows:
            status_icon = "✅" if mw['Enabled'] else "⏸️"
            
            with st.expander(f"{status_icon} {mw['Name']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Schedule:** {mw['Schedule']}")
                    st.write(f"**Duration:** {mw['Duration']}")
                
                with col2:
                    st.write(f"**Status:** {'Enabled' if mw['Enabled'] else 'Disabled'}")
                
                if st.button("Edit", key=f"edit_{mw['Name']}"):
                    st.info(f"Editing {mw['Name']}")
    
    @staticmethod
    def _render_patch_management(ssm_mgr: SystemsManagerManager):
        """Patch management"""
        st.subheader("📦 Patch Management")
        
        # Patch baselines
        baselines = ssm_mgr.describe_patch_baselines()
        
        if baselines:
            st.metric("Patch Baselines", len(baselines))
            
            baselines_df = pd.DataFrame(baselines)
            st.dataframe(baselines_df[['baseline_name', 'operating_system', 'default_baseline']], 
                        use_container_width=True)
        
        # Available patches
        st.markdown("### Available Patches")
        
        patches = ssm_mgr.describe_available_patches(max_results=20)
        
        if patches:
            st.write(f"**Available Patches:** {len(patches)}")
            
            # Group by classification
            classifications = {}
            for patch in patches:
                classification = patch.get('classification', 'Unknown')
                classifications[classification] = classifications.get(classification, 0) + 1
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Security", classifications.get('Security', 0))
            with col2:
                st.metric("Critical", classifications.get('Critical', 0))
            with col3:
                st.metric("Important", classifications.get('Important', 0))
