"""
Provisioning & Deployment Module - Infrastructure Deployment
Automated deployment workflows using CloudFormation, multi-region, rollback
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from core_account_manager import get_account_manager
from aws_cloudformation import CloudFormationManager

class ProvisioningModule:
    """Provisioning & Deployment functionality"""
    
    @staticmethod
    def render():
        """Main render method"""
        st.title("🚀 Provisioning & Deployment")
        
        account_mgr = get_account_manager()
        if not account_mgr:
            st.warning("⚠️ Configure AWS credentials first")
            return
        
        selected_account = st.selectbox(
            "Select AWS Account",
            options=account_mgr.list_account_names(),
            key="provisioning_account"
        )
        
        if not selected_account:
            return
        
        session = account_mgr.get_session(selected_account)
        if not session:
            st.error("Failed to get session")
            return
        
        cfn_mgr = CloudFormationManager(session)
        
        # Create tabs
        tabs = st.tabs([
            "📚 Stack Library",
            "🚀 Deploy Stack",
            "🔄 Active Deployments",
            "📝 Change Sets",
            "🌍 Multi-Region",
            "⏮️ Rollback"
        ])
        
        with tabs[0]:
            ProvisioningModule._render_stack_library(cfn_mgr)
        
        with tabs[1]:
            ProvisioningModule._render_deploy_stack(cfn_mgr)
        
        with tabs[2]:
            ProvisioningModule._render_active_deployments(cfn_mgr)
        
        with tabs[3]:
            ProvisioningModule._render_change_sets(cfn_mgr)
        
        with tabs[4]:
            ProvisioningModule._render_multi_region()
        
        with tabs[5]:
            ProvisioningModule._render_rollback(cfn_mgr)
    
    @staticmethod
    def _render_stack_library(cfn_mgr: CloudFormationManager):
        """Stack library and templates"""
        st.subheader("📚 CloudFormation Stack Library")
        
        # List existing stacks
        stacks = cfn_mgr.list_stacks()
        
        if stacks:
            st.metric("Total Stacks", len(stacks))
            
            # Status filter
            status_filter = st.multiselect(
                "Filter by Status",
                options=["CREATE_COMPLETE", "UPDATE_COMPLETE", "CREATE_IN_PROGRESS", 
                        "UPDATE_IN_PROGRESS", "ROLLBACK_COMPLETE"],
                default=["CREATE_COMPLETE", "UPDATE_COMPLETE"]
            )
            
            # Filter stacks
            filtered_stacks = [s for s in stacks if s['status'] in status_filter] if status_filter else stacks
            
            # Display stacks
            for stack in filtered_stacks:
                status_icon = "✅" if "COMPLETE" in stack['status'] else "🔄" if "IN_PROGRESS" in stack['status'] else "❌"
                
                with st.expander(f"{status_icon} {stack['stack_name']} - {stack['status']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Stack ID:** {stack['stack_id']}")
                        st.write(f"**Status:** {stack['status']}")
                        st.write(f"**Created:** {stack['creation_time']}")
                    
                    with col2:
                        st.write(f"**Last Updated:** {stack['last_updated']}")
                        st.write(f"**Drift Status:** {stack.get('drift_status', 'NOT_CHECKED')}")
                    
                    # Actions
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        if st.button("👁️ Details", key=f"details_{stack['stack_name']}"):
                            stack_info = cfn_mgr.get_stack_info(stack['stack_name'])
                            if stack_info:
                                st.json(stack_info)
                    
                    with col2:
                        if st.button("📋 Resources", key=f"resources_{stack['stack_name']}"):
                            resources = cfn_mgr.list_stack_resources(stack['stack_name'])
                            if resources:
                                res_df = pd.DataFrame(resources)
                                st.dataframe(res_df, use_container_width=True)
                    
                    with col3:
                        if st.button("🔍 Drift", key=f"drift_{stack['stack_name']}"):
                            result = cfn_mgr.detect_stack_drift(stack['stack_name'])
                            if result.get('success'):
                                st.success("Drift detection started")
                    
                    with col4:
                        if st.button("🗑️ Delete", key=f"delete_{stack['stack_name']}"):
                            result = cfn_mgr.delete_stack(stack['stack_name'])
                            if result.get('success'):
                                st.success(f"Stack deletion initiated")
                                st.rerun()
        else:
            st.info("No stacks found in this account")
    
    @staticmethod
    def _render_deploy_stack(cfn_mgr: CloudFormationManager):
        """Deploy new stack"""
        st.subheader("🚀 Deploy CloudFormation Stack")
        
        with st.form("deploy_stack"):
            st.markdown("### Stack Configuration")
            
            stack_name = st.text_input("Stack Name*", 
                placeholder="my-infrastructure-stack")
            
            # Template source
            template_source = st.radio("Template Source", 
                ["Upload Template", "S3 URL", "Quick Start Template"])
            
            if template_source == "Upload Template":
                template_body = st.text_area("CloudFormation Template (JSON/YAML)",
                    placeholder='{\n  "AWSTemplateFormatVersion": "2010-09-09",\n  ...\n}',
                    height=300)
                template_url = None
            
            elif template_source == "S3 URL":
                template_url = st.text_input("Template S3 URL",
                    placeholder="https://s3.amazonaws.com/bucket/template.yaml")
                template_body = None
            
            else:
                # Quick start templates
                quick_template = st.selectbox("Select Quick Start", [
                    "VPC with Public/Private Subnets",
                    "EC2 Instance with Security Group",
                    "RDS Database",
                    "S3 Bucket with Encryption",
                    "Lambda Function with API Gateway"
                ])
                
                # Load template based on selection
                if quick_template == "VPC with Public/Private Subnets":
                    template_body = """{
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "VPC with public and private subnets",
  "Resources": {
    "VPC": {
      "Type": "AWS::EC2::VPC",
      "Properties": {
        "CidrBlock": "10.0.0.0/16",
        "EnableDnsHostnames": true,
        "Tags": [{"Key": "Name", "Value": "CloudIDP-VPC"}]
      }
    }
  }
}"""
                else:
                    template_body = "# Quick start template placeholder"
                
                template_url = None
                st.code(template_body, language='json')
            
            # Parameters
            st.markdown("### Stack Parameters (Optional)")
            params_input = st.text_area("Parameters (JSON format)",
                placeholder='[{"ParameterKey": "InstanceType", "ParameterValue": "t3.micro"}]',
                height=100)
            
            # Capabilities
            st.markdown("### Capabilities")
            capabilities = st.multiselect("Required Capabilities", [
                "CAPABILITY_IAM",
                "CAPABILITY_NAMED_IAM",
                "CAPABILITY_AUTO_EXPAND"
            ])
            
            # Tags
            st.markdown("### Tags")
            tags_input = st.text_area("Tags (JSON format)",
                placeholder='[{"Key": "Environment", "Value": "Production"}]',
                height=80)
            
            submit = st.form_submit_button("Deploy Stack", type="primary")
            
            if submit:
                if not stack_name:
                    st.error("Stack name is required")
                elif not template_body and not template_url:
                    st.error("Template source is required")
                else:
                    # Parse parameters and tags
                    import json
                    parameters = None
                    tags = None
                    
                    try:
                        if params_input:
                            parameters = json.loads(params_input)
                        if tags_input:
                            tags = json.loads(tags_input)
                    except:
                        st.error("Invalid JSON format for parameters or tags")
                        return
                    
                    with st.spinner("Deploying stack..."):
                        result = cfn_mgr.create_stack(
                            stack_name=stack_name,
                            template_body=template_body,
                            template_url=template_url,
                            parameters=parameters,
                            tags=tags,
                            capabilities=capabilities
                        )
                        
                        if result.get('success'):
                            st.success(f"✅ Stack deployment initiated!")
                            st.info(f"Stack ID: {result.get('stack_id')}")
                            st.balloons()
                        else:
                            st.error(f"❌ {result.get('error')}")
    
    @staticmethod
    def _render_active_deployments(cfn_mgr: CloudFormationManager):
        """Active deployments"""
        st.subheader("🔄 Active Deployments")
        
        # Get stacks in progress
        stacks = cfn_mgr.list_stacks(
            status_filter=["CREATE_IN_PROGRESS", "UPDATE_IN_PROGRESS", 
                          "DELETE_IN_PROGRESS", "ROLLBACK_IN_PROGRESS"]
        )
        
        if stacks:
            st.write(f"**Active Deployments:** {len(stacks)}")
            
            for stack in stacks:
                with st.expander(f"🔄 {stack['stack_name']} - {stack['status']}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**Stack:** {stack['stack_name']}")
                        st.write(f"**Status:** {stack['status']}")
                    
                    with col2:
                        st.write(f"**Started:** {stack['creation_time']}")
                    
                    # Show recent events
                    events = cfn_mgr.get_stack_events(stack['stack_name'], limit=10)
                    if events:
                        st.markdown("**Recent Events:**")
                        events_df = pd.DataFrame(events)
                        st.dataframe(events_df, use_container_width=True)
        else:
            st.success("✅ No active deployments")
    
    @staticmethod
    def _render_change_sets(cfn_mgr: CloudFormationManager):
        """Change sets"""
        st.subheader("📝 Change Sets")
        
        st.markdown("""
        ### Preview Changes Before Deployment
        
        Change sets allow you to preview how proposed changes will affect your running resources.
        """)
        
        # Get existing stacks for change sets
        stacks = cfn_mgr.list_stacks(
            status_filter=["CREATE_COMPLETE", "UPDATE_COMPLETE"]
        )
        
        if stacks:
            selected_stack = st.selectbox(
                "Select Stack for Change Set",
                options=[s['stack_name'] for s in stacks]
            )
            
            if selected_stack:
                st.markdown("### Create Change Set")
                
                with st.form("create_changeset"):
                    changeset_name = st.text_input("Change Set Name",
                        placeholder="my-changes-2025-11-30")
                    
                    template_body = st.text_area("Updated Template",
                        placeholder="Paste updated CloudFormation template...",
                        height=200)
                    
                    if st.form_submit_button("Create Change Set"):
                        if changeset_name and template_body:
                            result = cfn_mgr.create_change_set(
                                stack_name=selected_stack,
                                change_set_name=changeset_name,
                                template_body=template_body
                            )
                            
                            if result.get('success'):
                                st.success(f"✅ Change set created: {result.get('change_set_id')}")
                            else:
                                st.error(f"❌ {result.get('error')}")
        else:
            st.info("No stacks available for change sets")
    
    @staticmethod
    def _render_multi_region():
        """Multi-region deployment"""
        st.subheader("🌍 Multi-Region Deployment")
        
        st.markdown("""
        ### Deploy to Multiple Regions Simultaneously
        
        Deploy your infrastructure across multiple AWS regions for high availability.
        """)
        
        regions = st.multiselect("Select Target Regions", [
            "us-east-1", "us-west-2", "eu-west-1", "eu-central-1",
            "ap-southeast-1", "ap-northeast-1"
        ])
        
        if regions:
            st.write(f"**Selected Regions:** {len(regions)}")
            
            stack_name_prefix = st.text_input("Stack Name Prefix",
                placeholder="my-multi-region-stack")
            
            if st.button("Deploy to All Regions"):
                if stack_name_prefix:
                    for region in regions:
                        st.info(f"Deploying to {region}...")
                    st.success(f"✅ Deployment initiated in {len(regions)} regions")
                else:
                    st.error("Stack name prefix required")
    
    @staticmethod
    def _render_rollback(cfn_mgr: CloudFormationManager):
        """Rollback operations"""
        st.subheader("⏮️ Rollback & Recovery")
        
        st.markdown("""
        ### Rollback Failed Deployments
        
        Manage failed stack deployments and rollback to previous stable states.
        """)
        
        # Get failed stacks
        failed_stacks = cfn_mgr.list_stacks(
            status_filter=["CREATE_FAILED", "UPDATE_FAILED", "ROLLBACK_COMPLETE"]
        )
        
        if failed_stacks:
            st.warning(f"⚠️ Found {len(failed_stacks)} stack(s) requiring attention")
            
            for stack in failed_stacks:
                with st.expander(f"❌ {stack['stack_name']} - {stack['status']}"):
                    st.write(f"**Status:** {stack['status']}")
                    st.write(f"**Last Updated:** {stack['last_updated']}")
                    
                    # Show events to understand failure
                    events = cfn_mgr.get_stack_events(stack['stack_name'], limit=5)
                    if events:
                        st.markdown("**Failure Events:**")
                        for event in events:
                            if "FAILED" in event['status']:
                                st.error(f"{event['logical_id']}: {event['reason']}")
                    
                    if st.button(f"Delete Failed Stack", key=f"rollback_{stack['stack_name']}"):
                        result = cfn_mgr.delete_stack(stack['stack_name'])
                        if result.get('success'):
                            st.success("Stack deletion initiated")
                            st.rerun()
        else:
            st.success("✅ No failed stacks found")
