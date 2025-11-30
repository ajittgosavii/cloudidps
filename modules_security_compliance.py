"""
Security & Compliance Module - Security Hub, GuardDuty, Config, CloudWatch
UI for security monitoring and compliance tracking
"""

import streamlit as st
import pandas as pd
from core_account_manager import get_account_manager, get_account_names
from aws_security import SecurityManager
from aws_cloudwatch import CloudWatchManager

class SecurityComplianceUI:
    """UI for Security & Compliance Management"""
    
    @staticmethod
    def render():
        """Main render method"""
        st.title("🔒 Security & Compliance")
        
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
            key="security_account"
        )
        
        if not selected_account:
            return
        
        session = account_mgr.get_session(selected_account)
        if not session:
            st.error(f"Failed to get session")
            return
        
        # Initialize managers
        security_mgr = SecurityManager(session)
        cw_mgr = CloudWatchManager(session)
        
        # Tabs
        tabs = st.tabs([
            "🛡️ Security Dashboard",
            "🔍 Security Findings",
            "⚠️ GuardDuty Threats",
            "✅ Config Compliance",
            "📊 CloudWatch Alarms",
            "📝 CloudWatch Logs"
        ])
        
        with tabs[0]:
            SecurityComplianceUI._render_security_dashboard(security_mgr)
        
        with tabs[1]:
            SecurityComplianceUI._render_security_findings(security_mgr)
        
        with tabs[2]:
            SecurityComplianceUI._render_guardduty(security_mgr)
        
        with tabs[3]:
            SecurityComplianceUI._render_config_compliance(security_mgr)
        
        with tabs[4]:
            SecurityComplianceUI._render_cloudwatch_alarms(cw_mgr)
        
        with tabs[5]:
            SecurityComplianceUI._render_cloudwatch_logs(cw_mgr)
    
    @staticmethod
    def _render_security_dashboard(security_mgr: SecurityManager):
        """Security overview dashboard"""
        st.subheader("🛡️ Security Dashboard")
        
        # Get security score
        score_data = security_mgr.get_security_score()
        
        # Display score
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            score = score_data.get('score', 0)
            st.metric("Security Score", f"{score}/100", delta=score_data.get('grade'))
        with col2:
            st.metric("Total Findings", score_data.get('total_findings', 0))
        with col3:
            st.metric("Critical", score_data.get('critical_findings', 0))
        with col4:
            st.metric("Compliance", f"{score_data.get('compliance_percentage', 0):.1f}%")
        
        # Security Hub summary
        st.markdown("### Security Hub Status")
        sh_summary = security_mgr.get_security_hub_summary()
        
        if sh_summary.get('total_findings', 0) > 0:
            severity_counts = sh_summary.get('severity_counts', {})
            
            # Bar chart of findings by severity
            severity_df = pd.DataFrame([
                {'Severity': k, 'Count': v} 
                for k, v in severity_counts.items()
            ])
            st.bar_chart(severity_df.set_index('Severity'))
        else:
            st.info("No security findings found")
    
    @staticmethod
    def _render_security_findings(security_mgr: SecurityManager):
        """Security Hub findings"""
        st.subheader("🔍 Security Findings")
        
        # Filter by severity
        severity_filter = st.selectbox(
            "Filter by Severity",
            options=["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"],
            key="findings_severity"
        )
        
        severity = None if severity_filter == "ALL" else severity_filter
        
        # Get findings
        findings = security_mgr.list_security_findings(severity=severity, limit=100)
        
        if not findings:
            st.success("✅ No security findings!")
            return
        
        st.write(f"**Total Findings:** {len(findings)}")
        
        # Display findings
        for finding in findings:
            severity_color = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '🟢',
                'INFORMATIONAL': '⚪'
            }.get(finding['severity'], '⚪')
            
            with st.expander(f"{severity_color} {finding['title']} - {finding['severity']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Resource Type:**", finding['resource_type'])
                    st.write("**Resource ID:**", finding['resource_id'])
                    st.write("**Status:**", finding['workflow_status'])
                with col2:
                    st.write("**Compliance:**", finding['compliance_status'])
                    st.write("**Created:**", finding['created_at'])
                    st.write("**Updated:**", finding['updated_at'])
                
                st.write("**Description:**", finding['description'])
                if finding.get('remediation'):
                    st.write("**Remediation:**", finding['remediation'])
    
    @staticmethod
    def _render_guardduty(security_mgr: SecurityManager):
        """GuardDuty findings"""
        st.subheader("⚠️ GuardDuty Threat Detection")
        
        detector_id = security_mgr.get_guardduty_detector()
        
        if not detector_id:
            st.warning("GuardDuty not enabled")
            if st.button("Enable GuardDuty"):
                result = security_mgr.enable_guardduty()
                if result.get('success'):
                    st.success("✅ GuardDuty enabled")
                    st.rerun()
            return
        
        # Get findings
        findings = security_mgr.list_guardduty_findings(detector_id)
        
        if not findings:
            st.success("✅ No threat findings!")
            return
        
        st.write(f"**Total Findings:** {len(findings)}")
        
        # Display findings
        for finding in findings:
            severity_icon = "🔴" if finding['severity'] >= 7 else "🟡" if finding['severity'] >= 4 else "🟢"
            
            with st.expander(f"{severity_icon} {finding['title']} (Severity: {finding['severity']})"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Type:**", finding['type'])
                    st.write("**Resource:**", finding['resource_type'])
                    st.write("**Region:**", finding['region'])
                with col2:
                    st.write("**Created:**", finding['created_at'])
                    st.write("**Updated:**", finding['updated_at'])
                    st.write("**Count:**", finding['count'])
                
                st.write("**Description:**", finding['description'])
    
    @staticmethod
    def _render_config_compliance(security_mgr: SecurityManager):
        """AWS Config compliance"""
        st.subheader("✅ Config Compliance")
        
        # Get compliance summary
        summary = security_mgr.get_compliance_summary()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Rules", summary.get('total_rules', 0))
        with col2:
            st.metric("Compliant", summary.get('compliance_counts', {}).get('COMPLIANT', 0))
        with col3:
            st.metric("Non-Compliant", summary.get('compliance_counts', {}).get('NON_COMPLIANT', 0))
        with col4:
            compliance_pct = summary.get('compliance_percentage', 0)
            st.metric("Compliance %", f"{compliance_pct:.1f}%")
        
        # Config rules
        st.markdown("### Config Rules")
        rules = security_mgr.list_config_rules()
        
        if rules:
            rules_df = pd.DataFrame(rules)
            st.dataframe(rules_df[['name', 'source', 'state']], use_container_width=True)
        
        # Non-compliant resources
        st.markdown("### Non-Compliant Resources")
        non_compliant = security_mgr.get_non_compliant_resources()
        
        if non_compliant:
            nc_df = pd.DataFrame(non_compliant)
            st.dataframe(nc_df, use_container_width=True)
        else:
            st.success("✅ All resources compliant!")
    
    @staticmethod
    def _render_cloudwatch_alarms(cw_mgr: CloudWatchManager):
        """CloudWatch alarms"""
        st.subheader("📊 CloudWatch Alarms")
        
        # Filter by state
        state_filter = st.selectbox(
            "Filter by State",
            options=["ALL", "ALARM", "OK", "INSUFFICIENT_DATA"],
            key="alarms_state"
        )
        
        state = None if state_filter == "ALL" else state_filter
        
        # Get alarms
        alarms = cw_mgr.list_alarms(state_value=state)
        
        if not alarms:
            st.info("No alarms found")
            return
        
        # Metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Alarms", len(alarms))
        with col2:
            alarm_count = sum(1 for a in alarms if a['state'] == 'ALARM')
            st.metric("In ALARM", alarm_count)
        with col3:
            ok_count = sum(1 for a in alarms if a['state'] == 'OK')
            st.metric("OK", ok_count)
        
        # Display alarms
        for alarm in alarms:
            state_icon = "🔴" if alarm['state'] == 'ALARM' else "🟢" if alarm['state'] == 'OK' else "🟡"
            
            with st.expander(f"{state_icon} {alarm['alarm_name']} - {alarm['state']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Metric:**", alarm['metric_name'])
                    st.write("**Namespace:**", alarm['namespace'])
                    st.write("**Statistic:**", alarm['statistic'])
                with col2:
                    st.write("**Threshold:**", alarm['threshold'])
                    st.write("**Comparison:**", alarm['comparison_operator'])
                    st.write("**Actions Enabled:**", alarm['actions_enabled'])
                
                if alarm.get('state_reason'):
                    st.write("**Reason:**", alarm['state_reason'])
    
    @staticmethod
    def _render_cloudwatch_logs(cw_mgr: CloudWatchManager):
        """CloudWatch logs"""
        st.subheader("📝 CloudWatch Logs")
        
        # List log groups
        log_groups = cw_mgr.list_log_groups()
        
        if not log_groups:
            st.info("No log groups found")
            return
        
        st.metric("Total Log Groups", len(log_groups))
        
        # Select log group
        selected_lg = st.selectbox(
            "Select Log Group",
            options=[lg['log_group_name'] for lg in log_groups],
            key="selected_log_group"
        )
        
        if selected_lg:
            # List streams
            streams = cw_mgr.list_log_streams(selected_lg)
            
            if streams:
                st.write(f"**Log Streams:** {len(streams)}")
                
                selected_stream = st.selectbox(
                    "Select Log Stream",
                    options=[s['log_stream_name'] for s in streams],
                    key="selected_stream"
                )
                
                if selected_stream and st.button("Get Recent Events"):
                    events = cw_mgr.get_log_events(selected_lg, selected_stream, limit=50)
                    
                    if events:
                        for event in events:
                            st.text(f"{event['timestamp']}: {event['message']}")
                    else:
                        st.info("No events found")
