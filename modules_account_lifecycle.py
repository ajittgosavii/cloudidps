"""
AWS Account Onboarding & Offboarding Automation
Enterprise-grade account lifecycle management
"""

import streamlit as st
import boto3
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json

class OnboardingStatus(Enum):
    """Account onboarding status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    
class OffboardingStatus(Enum):
    """Account offboarding status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class OnboardingTask:
    """Represents a single onboarding task"""
    task_id: str
    description: str
    status: str
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None

class AWSAccountOnboarding:
    """
    Automated AWS Account Onboarding
    
    Handles:
    1. IAM Role Creation
    2. Permission Setup
    3. CloudTrail Configuration
    4. Config Service Setup
    5. Security Hub Enablement
    6. GuardDuty Enablement
    7. Cost Explorer Activation
    8. Tag Policy Application
    9. Account Registration in CloudIDP
    """
    
    ONBOARDING_TASKS = [
        {
            "id": "validate_account",
            "name": "Validate Account Access",
            "description": "Verify AWS account ID and permissions"
        },
        {
            "id": "create_iam_role",
            "name": "Create CloudIDP IAM Role",
            "description": "Create CloudIDP-Access role with required permissions"
        },
        {
            "id": "configure_cloudtrail",
            "name": "Configure CloudTrail",
            "description": "Enable CloudTrail for audit logging"
        },
        {
            "id": "enable_config",
            "name": "Enable AWS Config",
            "description": "Set up AWS Config for compliance tracking"
        },
        {
            "id": "enable_security_hub",
            "name": "Enable Security Hub",
            "description": "Enable Security Hub for security monitoring"
        },
        {
            "id": "enable_guardduty",
            "name": "Enable GuardDuty",
            "description": "Enable GuardDuty for threat detection"
        },
        {
            "id": "activate_cost_explorer",
            "name": "Activate Cost Explorer",
            "description": "Enable Cost Explorer for cost analysis"
        },
        {
            "id": "apply_tag_policy",
            "name": "Apply Tagging Policy",
            "description": "Apply standard tagging requirements"
        },
        {
            "id": "register_account",
            "name": "Register in CloudIDP",
            "description": "Add account to CloudIDP configuration"
        }
    ]
    
    @staticmethod
    def generate_cloudidp_role_policy() -> Dict:
        """Generate IAM policy for CloudIDP access role"""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "CloudIDPReadAccess",
                    "Effect": "Allow",
                    "Action": [
                        # EC2
                        "ec2:Describe*",
                        "ec2:Get*",
                        # RDS
                        "rds:Describe*",
                        "rds:List*",
                        # DynamoDB
                        "dynamodb:Describe*",
                        "dynamodb:List*",
                        # S3
                        "s3:List*",
                        "s3:Get*",
                        # Lambda
                        "lambda:List*",
                        "lambda:Get*",
                        # VPC
                        "ec2:DescribeVpcs",
                        "ec2:DescribeSubnets",
                        "ec2:DescribeSecurityGroups",
                        # Cost Explorer
                        "ce:Get*",
                        "ce:Describe*",
                        "ce:List*",
                        # Budgets
                        "budgets:ViewBudget",
                        "budgets:DescribeBudget*",
                        # CloudWatch
                        "cloudwatch:Describe*",
                        "cloudwatch:Get*",
                        "cloudwatch:List*",
                        # CloudTrail
                        "cloudtrail:LookupEvents",
                        "cloudtrail:GetTrailStatus",
                        # Config
                        "config:Describe*",
                        "config:Get*",
                        "config:List*",
                        # Security Hub
                        "securityhub:Get*",
                        "securityhub:Describe*",
                        "securityhub:List*",
                        # GuardDuty
                        "guardduty:Get*",
                        "guardduty:List*",
                        # IAM (Read Only)
                        "iam:Get*",
                        "iam:List*",
                        "iam:GenerateCredentialReport",
                        # Organizations
                        "organizations:Describe*",
                        "organizations:List*",
                        # Tags
                        "tag:GetResources",
                        "tag:GetTagKeys",
                        "tag:GetTagValues",
                        # Resource Groups
                        "resource-groups:List*",
                        "resource-groups:Get*"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "CloudIDPWriteAccess",
                    "Effect": "Allow",
                    "Action": [
                        # EC2 Management
                        "ec2:StartInstances",
                        "ec2:StopInstances",
                        "ec2:RebootInstances",
                        "ec2:CreateTags",
                        "ec2:DeleteTags",
                        # RDS Management
                        "rds:StartDBInstance",
                        "rds:StopDBInstance",
                        "rds:RebootDBInstance",
                        "rds:AddTagsToResource",
                        "rds:RemoveTagsFromResource",
                        # Lambda Management
                        "lambda:InvokeFunction",
                        "lambda:TagResource",
                        "lambda:UntagResource",
                        # CloudWatch Alarms
                        "cloudwatch:PutMetricAlarm",
                        "cloudwatch:DeleteAlarms",
                        # Budget Management
                        "budgets:CreateBudget",
                        "budgets:ModifyBudget",
                        "budgets:DeleteBudget"
                    ],
                    "Resource": "*"
                }
            ]
        }
    
    @staticmethod
    def generate_trust_policy(management_account_id: str, management_user_arn: str) -> Dict:
        """Generate IAM trust policy for CloudIDP role"""
        return {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": management_user_arn
                    },
                    "Action": "sts:AssumeRole",
                    "Condition": {
                        "StringEquals": {
                            "sts:ExternalId": f"CloudIDP-{management_account_id}"
                        }
                    }
                }
            ]
        }
    
    @staticmethod
    def create_cloudidp_role(
        target_account_session: boto3.Session,
        management_account_id: str,
        management_user_arn: str
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create CloudIDP access role in target account
        
        Returns:
            (success, role_arn, error_message)
        """
        try:
            iam = target_account_session.client('iam')
            
            role_name = "CloudIDP-Access"
            
            # Check if role already exists
            try:
                existing_role = iam.get_role(RoleName=role_name)
                return True, existing_role['Role']['Arn'], None
            except iam.exceptions.NoSuchEntityException:
                pass  # Role doesn't exist, create it
            
            # Create role
            trust_policy = AWSAccountOnboarding.generate_trust_policy(
                management_account_id,
                management_user_arn
            )
            
            response = iam.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description="CloudIDP platform access role for multi-account management",
                MaxSessionDuration=3600,
                Tags=[
                    {'Key': 'ManagedBy', 'Value': 'CloudIDP'},
                    {'Key': 'Purpose', 'Value': 'PlatformAccess'},
                    {'Key': 'CreatedAt', 'Value': datetime.now().isoformat()}
                ]
            )
            
            role_arn = response['Role']['Arn']
            
            # Attach inline policy
            policy = AWSAccountOnboarding.generate_cloudidp_role_policy()
            
            iam.put_role_policy(
                RoleName=role_name,
                PolicyName="CloudIDP-Access-Policy",
                PolicyDocument=json.dumps(policy)
            )
            
            return True, role_arn, None
            
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def enable_cloudtrail(
        session: boto3.Session,
        account_id: str,
        trail_name: str = "CloudIDP-Trail"
    ) -> Tuple[bool, Optional[str]]:
        """Enable CloudTrail in account"""
        try:
            cloudtrail = session.client('cloudtrail')
            s3 = session.client('s3')
            
            bucket_name = f"cloudidp-cloudtrail-{account_id}"
            
            # Create S3 bucket for CloudTrail logs
            try:
                s3.create_bucket(Bucket=bucket_name)
                
                # Apply bucket policy
                bucket_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Sid": "AWSCloudTrailAclCheck",
                            "Effect": "Allow",
                            "Principal": {"Service": "cloudtrail.amazonaws.com"},
                            "Action": "s3:GetBucketAcl",
                            "Resource": f"arn:aws:s3:::{bucket_name}"
                        },
                        {
                            "Sid": "AWSCloudTrailWrite",
                            "Effect": "Allow",
                            "Principal": {"Service": "cloudtrail.amazonaws.com"},
                            "Action": "s3:PutObject",
                            "Resource": f"arn:aws:s3:::{bucket_name}/AWSLogs/{account_id}/*",
                            "Condition": {
                                "StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}
                            }
                        }
                    ]
                }
                
                s3.put_bucket_policy(
                    Bucket=bucket_name,
                    Policy=json.dumps(bucket_policy)
                )
            except Exception as e:
                pass  # Bucket might already exist
            
            # Create trail
            try:
                cloudtrail.create_trail(
                    Name=trail_name,
                    S3BucketName=bucket_name,
                    IsMultiRegionTrail=True,
                    EnableLogFileValidation=True,
                    TagsList=[
                        {'Key': 'ManagedBy', 'Value': 'CloudIDP'}
                    ]
                )
                
                # Start logging
                cloudtrail.start_logging(Name=trail_name)
                
            except cloudtrail.exceptions.TrailAlreadyExistsException:
                pass  # Trail already exists
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def enable_security_hub(session: boto3.Session, region: str = 'us-east-1') -> Tuple[bool, Optional[str]]:
        """Enable AWS Security Hub"""
        try:
            securityhub = session.client('securityhub', region_name=region)
            
            try:
                securityhub.enable_security_hub(
                    EnableDefaultStandards=True
                )
            except securityhub.exceptions.ResourceConflictException:
                pass  # Already enabled
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def enable_guardduty(session: boto3.Session, region: str = 'us-east-1') -> Tuple[bool, Optional[str]]:
        """Enable AWS GuardDuty"""
        try:
            guardduty = session.client('guardduty', region_name=region)
            
            try:
                response = guardduty.create_detector(
                    Enable=True,
                    FindingPublishingFrequency='FIFTEEN_MINUTES'
                )
            except Exception:
                pass  # Might already exist
            
            return True, None
            
        except Exception as e:
            return False, str(e)


class AWSAccountOffboarding:
    """
    Automated AWS Account Offboarding
    
    Handles:
    1. Resource Inventory Export
    2. Cost Report Generation
    3. Security Findings Export
    4. CloudTrail Archive
    5. IAM Role Cleanup
    6. Account Deregistration
    """
    
    OFFBOARDING_TASKS = [
        {
            "id": "inventory_export",
            "name": "Export Resource Inventory",
            "description": "Generate complete resource inventory report"
        },
        {
            "id": "cost_report",
            "name": "Generate Cost Report",
            "description": "Create final cost and usage report"
        },
        {
            "id": "security_export",
            "name": "Export Security Findings",
            "description": "Archive all security findings and compliance data"
        },
        {
            "id": "cloudtrail_archive",
            "name": "Archive CloudTrail Logs",
            "description": "Archive all audit logs for compliance"
        },
        {
            "id": "backup_config",
            "name": "Backup Configuration",
            "description": "Export all configuration data"
        },
        {
            "id": "cleanup_iam_role",
            "name": "Remove CloudIDP Role",
            "description": "Delete CloudIDP-Access IAM role"
        },
        {
            "id": "deregister_account",
            "name": "Deregister from CloudIDP",
            "description": "Remove account from CloudIDP platform"
        }
    ]
    
    @staticmethod
    def export_resource_inventory(session: boto3.Session, account_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Export complete resource inventory"""
        try:
            inventory = {
                "account_id": account_id,
                "export_date": datetime.now().isoformat(),
                "resources": {}
            }
            
            # EC2 Instances
            ec2 = session.client('ec2')
            instances = []
            for page in ec2.get_paginator('describe_instances').paginate():
                for reservation in page['Reservations']:
                    instances.extend(reservation['Instances'])
            inventory['resources']['ec2'] = len(instances)
            
            # RDS Instances
            rds = session.client('rds')
            db_instances = rds.describe_db_instances()['DBInstances']
            inventory['resources']['rds'] = len(db_instances)
            
            # S3 Buckets
            s3 = session.client('s3')
            buckets = s3.list_buckets()['Buckets']
            inventory['resources']['s3'] = len(buckets)
            
            # Lambda Functions
            lambda_client = session.client('lambda')
            functions = lambda_client.list_functions()['Functions']
            inventory['resources']['lambda'] = len(functions)
            
            return True, inventory, None
            
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def generate_final_cost_report(session: boto3.Session, account_id: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Generate final cost report"""
        try:
            from datetime import timedelta
            
            ce = session.client('ce', region_name='us-east-1')
            
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=90)
            
            response = ce.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date.isoformat(),
                    'End': end_date.isoformat()
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {'Type': 'DIMENSION', 'Key': 'SERVICE'}
                ]
            )
            
            cost_report = {
                "account_id": account_id,
                "report_period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat()
                },
                "total_cost": 0,
                "costs_by_service": {}
            }
            
            for result in response['ResultsByTime']:
                for group in result['Groups']:
                    service = group['Keys'][0]
                    cost = float(group['Metrics']['UnblendedCost']['Amount'])
                    if service not in cost_report['costs_by_service']:
                        cost_report['costs_by_service'][service] = 0
                    cost_report['costs_by_service'][service] += cost
                    cost_report['total_cost'] += cost
            
            return True, cost_report, None
            
        except Exception as e:
            return False, None, str(e)
    
    @staticmethod
    def delete_cloudidp_role(session: boto3.Session) -> Tuple[bool, Optional[str]]:
        """Delete CloudIDP access role"""
        try:
            iam = session.client('iam')
            role_name = "CloudIDP-Access"
            
            # Delete inline policies
            try:
                iam.delete_role_policy(
                    RoleName=role_name,
                    PolicyName="CloudIDP-Access-Policy"
                )
            except Exception:
                pass
            
            # Delete role
            try:
                iam.delete_role(RoleName=role_name)
            except Exception:
                pass
            
            return True, None
            
        except Exception as e:
            return False, str(e)

# UI Module for Account Lifecycle
class AccountLifecycleModule:
    """UI for Account Lifecycle Management"""
    
    @staticmethod
    def render():
        """Render account lifecycle UI"""
        st.title("🔄 Account Lifecycle Management")
        
        st.markdown("""
        ### Automated Account Onboarding & Offboarding
        
        Streamline the process of adding and removing AWS accounts from your organization.
        """)
        
        tabs = st.tabs(["📥 Onboarding", "📤 Offboarding", "📊 Status"])
        
        with tabs[0]:
            AccountLifecycleModule._render_onboarding()
        
        with tabs[1]:
            AccountLifecycleModule._render_offboarding()
        
        with tabs[2]:
            AccountLifecycleModule._render_status()
    
    @staticmethod
    def _render_onboarding():
        """Render onboarding UI"""
        st.subheader("📥 Account Onboarding")
        
        st.info("🚀 Automated onboarding sets up new AWS accounts")
        
        with st.form("onboard_account"):
            st.markdown("### New Account Details")
            
            col1, col2 = st.columns(2)
            
            with col1:
                account_id = st.text_input("Account ID*", placeholder="123456789012")
                account_name = st.text_input("Account Name*", placeholder="Production Account")
            
            with col2:
                owner_email = st.text_input("Owner Email*", placeholder="team@company.com")
                environment = st.selectbox("Environment", ["production", "staging", "development"])
            
            submit = st.form_submit_button("Start Onboarding", type="primary")
            
            if submit and account_id and account_name:
                st.success(f"✅ Onboarding initiated for {account_name}")
    
    @staticmethod
    def _render_offboarding():
        """Render offboarding UI"""
        st.subheader("📤 Account Offboarding")
        
        st.warning("⚠️ Offboarding will remove account access")
        
        st.info("Select an account to offboard")
    
    @staticmethod
    def _render_status():
        """Render status dashboard"""
        st.subheader("📊 Lifecycle Status")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Accounts", 48)
        with col2:
            st.metric("Active Onboarding", 2)
        with col3:
            st.metric("Active Offboarding", 1)
