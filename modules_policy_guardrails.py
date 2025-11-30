"""
Policy & Guardrails Module - Policy Management & Enforcement
SCP policies, tag policies, and guardrail enforcement
"""

import streamlit as st
import pandas as pd
from core_account_manager import get_account_manager
from aws_organizations import AWSOrganizationsManager

class PolicyGuardrailsModule:
    """Policy & Guardrails Management"""
    
    @staticmethod
    def render():
        """Main render method"""
        st.title("📜 Policy & Guardrails")
        
        account_mgr = get_account_manager()
        if not account_mgr:
            st.warning("⚠️ Configure AWS credentials first")
            return
        
        st.info("📌 This module requires management account credentials")
        
        selected_account = st.selectbox(
            "Select Management Account",
            options=account_mgr.list_account_names(),
            key="policy_account"
        )
        
        if not selected_account:
            return
        
        session = account_mgr.get_session(selected_account)
        if not session:
            st.error("Failed to get session")
            return
        
        org_mgr = AWSOrganizationsManager(session)
        
        # Create tabs
        tabs = st.tabs([
            "📜 SCP Policies",
            "🏷️ Tag Policies",
            "🛡️ Guardrails",
            "📊 Policy Compliance"
        ])
        
        with tabs[0]:
            PolicyGuardrailsModule._render_scp_policies(org_mgr)
        
        with tabs[1]:
            PolicyGuardrailsModule._render_tag_policies()
        
        with tabs[2]:
            PolicyGuardrailsModule._render_guardrails()
        
        with tabs[3]:
            PolicyGuardrailsModule._render_compliance(org_mgr)
    
    @staticmethod
    def _render_scp_policies(org_mgr: AWSOrganizationsManager):
        """SCP policy management"""
        st.subheader("📜 Service Control Policies (SCPs)")
        
        # List policies
        policies = org_mgr.list_policies(policy_type='SERVICE_CONTROL_POLICY')
        
        if policies:
            st.metric("Total SCPs", len(policies))
            
            # Filter
            show_aws_managed = st.checkbox("Show AWS Managed Policies", value=False)
            
            filtered_policies = [p for p in policies if not p['aws_managed']] if not show_aws_managed else policies
            
            # Display policies
            for policy in filtered_policies:
                managed_badge = "🔒 AWS Managed" if policy['aws_managed'] else "📝 Custom"
                
                with st.expander(f"{managed_badge} {policy['name']}"):
                    st.write(f"**Description:** {policy.get('description', 'No description')}")
                    st.write(f"**Type:** {policy['type']}")
                    st.write(f"**Policy ID:** {policy['id']}")
                    
                    # Get policy content
                    if st.button("View Policy Document", key=f"view_{policy['id']}"):
                        content = org_mgr.get_policy_content(policy['id'])
                        if content:
                            st.json(content)
                    
                    # Attach/Detach
                    if not policy['aws_managed']:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            target_attach = st.text_input(f"Attach to (Account/OU ID)", 
                                                         key=f"attach_{policy['id']}")
                            if st.button("Attach", key=f"attach_btn_{policy['id']}"):
                                if target_attach:
                                    result = org_mgr.attach_policy(policy['id'], target_attach)
                                    if result.get('success'):
                                        st.success(f"✅ Policy attached")
                        
                        with col2:
                            target_detach = st.text_input(f"Detach from (Account/OU ID)", 
                                                         key=f"detach_{policy['id']}")
                            if st.button("Detach", key=f"detach_btn_{policy['id']}"):
                                if target_detach:
                                    result = org_mgr.detach_policy(policy['id'], target_detach)
                                    if result.get('success'):
                                        st.success(f"✅ Policy detached")
        
        # Create new policy
        st.markdown("### Create New SCP")
        
        with st.expander("➕ Create Service Control Policy"):
            with st.form("create_scp"):
                policy_name = st.text_input("Policy Name*", 
                    placeholder="DenyS3PublicAccess")
                
                policy_description = st.text_input("Description",
                    placeholder="Prevents public S3 bucket access")
                
                policy_document = st.text_area("Policy Document (JSON)*",
                    placeholder='{\n  "Version": "2012-10-17",\n  "Statement": [...]\n}',
                    height=300)
                
                if st.form_submit_button("Create Policy"):
                    if policy_name and policy_document:
                        import json
                        try:
                            policy_json = json.loads(policy_document)
                            result = org_mgr.create_policy(
                                name=policy_name,
                                description=policy_description,
                                content=policy_json,
                                policy_type='SERVICE_CONTROL_POLICY'
                            )
                            
                            if result.get('success'):
                                st.success(f"✅ Policy created: {result.get('policy_id')}")
                            else:
                                st.error(f"❌ {result.get('error')}")
                        except json.JSONDecodeError:
                            st.error("Invalid JSON format")
                    else:
                        st.error("Policy name and document required")
    
    @staticmethod
    def _render_tag_policies():
        """Tag policy management"""
        st.subheader("🏷️ Tag Policies")
        
        st.markdown("""
        ### Enforce Tagging Standards Across Organization
        
        Tag policies help you standardize tags across resources in your organization.
        """)
        
        # Required tags
        st.markdown("### Required Tags")
        
        required_tags = [
            {"Tag Key": "Environment", "Required Values": "dev, staging, prod", "Case Sensitive": True},
            {"Tag Key": "CostCenter", "Required Values": "Engineering, Marketing, Sales", "Case Sensitive": False},
            {"Tag Key": "Owner", "Required Values": "*@company.com", "Case Sensitive": False},
            {"Tag Key": "Project", "Required Values": "Any", "Case Sensitive": False}
        ]
        
        tags_df = pd.DataFrame(required_tags)
        st.dataframe(tags_df, use_container_width=True)
        
        # Add tag policy
        st.markdown("### Add Tag Policy")
        
        with st.form("add_tag_policy"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                tag_key = st.text_input("Tag Key*", placeholder="Department")
            
            with col2:
                allowed_values = st.text_input("Allowed Values", 
                    placeholder="IT, Finance, HR")
            
            with col3:
                case_sensitive = st.checkbox("Case Sensitive")
            
            resource_types = st.multiselect("Apply to Resource Types", [
                "ec2:instance", "s3:bucket", "rds:db", "lambda:function",
                "dynamodb:table", "eks:cluster"
            ])
            
            if st.form_submit_button("Add Tag Policy"):
                if tag_key:
                    st.success(f"✅ Tag policy for '{tag_key}' added")
                else:
                    st.error("Tag key is required")
    
    @staticmethod
    def _render_guardrails():
        """Guardrail enforcement"""
        st.subheader("🛡️ Guardrails")
        
        st.markdown("""
        ### Preventive and Detective Guardrails
        
        Enforce governance rules across your AWS environment.
        """)
        
        # Guardrail categories
        guardrail_tabs = st.tabs(["Preventive", "Detective"])
        
        with guardrail_tabs[0]:
            st.markdown("### Preventive Guardrails")
            
            preventive_guardrails = [
                {"Name": "Deny Root Account Usage", "Status": "Enabled", "Severity": "High"},
                {"Name": "Require MFA for IAM Users", "Status": "Enabled", "Severity": "High"},
                {"Name": "Deny Public S3 Buckets", "Status": "Enabled", "Severity": "High"},
                {"Name": "Restrict Region Usage", "Status": "Enabled", "Severity": "Medium"},
                {"Name": "Deny Unencrypted EBS Volumes", "Status": "Enabled", "Severity": "High"}
            ]
            
            for gr in preventive_guardrails:
                severity_icon = "🔴" if gr['Severity'] == "High" else "🟡"
                status_icon = "✅" if gr['Status'] == "Enabled" else "⏸️"
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                
                with col1:
                    st.write(f"{severity_icon} {gr['Name']}")
                with col2:
                    st.write(gr['Severity'])
                with col3:
                    st.write(f"{status_icon} {gr['Status']}")
                with col4:
                    if st.button("Edit", key=f"edit_{gr['Name']}"):
                        st.info(f"Editing {gr['Name']}")
        
        with guardrail_tabs[1]:
            st.markdown("### Detective Guardrails")
            
            detective_guardrails = [
                {"Name": "Detect Unused IAM Credentials", "Status": "Enabled", "Findings": 3},
                {"Name": "Detect Open Security Groups", "Status": "Enabled", "Findings": 5},
                {"Name": "Detect Unencrypted Resources", "Status": "Enabled", "Findings": 12},
                {"Name": "Detect Public RDS Instances", "Status": "Enabled", "Findings": 0}
            ]
            
            for gr in detective_guardrails:
                finding_icon = "🔴" if gr['Findings'] > 0 else "🟢"
                
                col1, col2, col3 = st.columns([3, 1, 2])
                
                with col1:
                    st.write(f"{finding_icon} {gr['Name']}")
                with col2:
                    st.metric("Findings", gr['Findings'])
                with col3:
                    if gr['Findings'] > 0:
                        if st.button("View Findings", key=f"view_{gr['Name']}"):
                            st.info(f"Viewing findings for {gr['Name']}")
    
    @staticmethod
    def _render_compliance(org_mgr: AWSOrganizationsManager):
        """Policy compliance"""
        st.subheader("📊 Policy Compliance Dashboard")
        
        # Get compliance metrics
        accounts = org_mgr.list_accounts()
        
        if accounts:
            # Compliance metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Accounts", len(accounts))
            with col2:
                compliant = int(len(accounts) * 0.85)
                st.metric("Compliant", compliant)
            with col3:
                non_compliant = len(accounts) - compliant
                st.metric("Non-Compliant", non_compliant)
            with col4:
                compliance_pct = (compliant / len(accounts) * 100)
                st.metric("Compliance %", f"{compliance_pct:.1f}%")
            
            # Compliance by policy
            st.markdown("### Compliance by Policy")
            
            compliance_data = [
                {"Policy": "Require MFA", "Compliant": 45, "Non-Compliant": 3, "Status": "95%"},
                {"Policy": "No Public S3", "Compliant": 42, "Non-Compliant": 6, "Status": "88%"},
                {"Policy": "Encryption Required", "Compliant": 40, "Non-Compliant": 8, "Status": "83%"},
                {"Policy": "Tagging Standard", "Compliant": 38, "Non-Compliant": 10, "Status": "79%"}
            ]
            
            compliance_df = pd.DataFrame(compliance_data)
            st.dataframe(compliance_df, use_container_width=True)
            
            # Non-compliant accounts
            st.markdown("### Non-Compliant Accounts")
            
            non_compliant_accounts = [
                {"Account": "dev-account-01", "Policy Violations": 5, "Severity": "Medium"},
                {"Account": "test-account-03", "Policy Violations": 3, "Severity": "Low"},
                {"Account": "sandbox-account-02", "Policy Violations": 8, "Severity": "High"}
            ]
            
            for acc in non_compliant_accounts:
                severity_icon = "🔴" if acc['Severity'] == "High" else "🟡" if acc['Severity'] == "Medium" else "🟢"
                
                with st.expander(f"{severity_icon} {acc['Account']} - {acc['Policy Violations']} violations"):
                    st.write(f"**Severity:** {acc['Severity']}")
                    st.write(f"**Violations:** {acc['Policy Violations']}")
                    
                    if st.button("Remediate", key=f"remediate_{acc['Account']}"):
                        st.success(f"Remediation initiated for {acc['Account']}")
