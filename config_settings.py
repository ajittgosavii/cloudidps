"""
Application Configuration and Settings
"""

import streamlit as st
from typing import Dict, List, Optional
from dataclasses import dataclass
import json

@dataclass
class AWSAccountConfig:
    """Configuration for a single AWS account"""
    account_id: str
    account_name: str
    role_arn: str
    regions: List[str]
    environment: str  # production, development, staging, etc.
    cost_center: Optional[str] = None
    owner_email: Optional[str] = None
    status: str = "active"  # active, suspended, offboarding

class AppConfig:
    """Global application configuration"""
    
    # Application metadata
    APP_NAME = "CloudIDP v2.0"
    APP_VERSION = "2.0.0"
    
    # AWS Configuration
    DEFAULT_REGIONS = [
        "us-east-1",
        "us-east-2", 
        "us-west-1",
        "us-west-2",
        "eu-west-1",
        "eu-central-1",
        "ap-southeast-1",
        "ap-northeast-1"
    ]
    
    # Cache TTL (seconds)
    CACHE_TTL_ACCOUNTS = 300  # 5 minutes
    CACHE_TTL_RESOURCES = 60  # 1 minute
    CACHE_TTL_COSTS = 3600    # 1 hour
    CACHE_TTL_SECURITY = 300  # 5 minutes
    
    # Pagination
    DEFAULT_PAGE_SIZE = 50
    MAX_PAGE_SIZE = 500
    
    # Cost thresholds
    COST_WARNING_THRESHOLD = 0.8  # 80% of budget
    COST_CRITICAL_THRESHOLD = 0.95  # 95% of budget
    
    @staticmethod
    def load_aws_accounts() -> List[AWSAccountConfig]:
        """Load AWS account configurations from Streamlit secrets"""
        accounts = []
        
        try:
            # Load from st.secrets
            if "aws" in st.secrets and "accounts" in st.secrets["aws"]:
                for account_key, account_data in st.secrets["aws"]["accounts"].items():
                    accounts.append(AWSAccountConfig(
                        account_id=account_data["account_id"],
                        account_name=account_data.get("account_name", account_key),
                        role_arn=account_data["role_arn"],
                        regions=account_data.get("regions", AppConfig.DEFAULT_REGIONS[:2]),
                        environment=account_data.get("environment", "production"),
                        cost_center=account_data.get("cost_center"),
                        owner_email=account_data.get("owner_email"),
                        status=account_data.get("status", "active")
                    ))
        except Exception as e:
            st.error(f"Error loading AWS account configuration: {e}")
        
        return accounts
    
    @staticmethod
    def get_management_credentials() -> Optional[Dict[str, str]]:
        """Get management account credentials for role assumption"""
        try:
            if "aws" in st.secrets:
                return {
                    "access_key_id": st.secrets["aws"].get("management_access_key_id"),
                    "secret_access_key": st.secrets["aws"].get("management_secret_access_key"),
                    "region": st.secrets["aws"].get("default_region", "us-east-1")
                }
        except Exception:
            pass
        return None
    
    @staticmethod
    def get_supported_services() -> List[str]:
        """List of AWS services supported by CloudIDP"""
        return [
            "ec2",
            "rds",
            "dynamodb",
            "s3",
            "lambda",
            "ecs",
            "eks",
            "elasticache",
            "elasticsearch",
            "vpc",
            "elb",
            "elbv2",
            "cloudfront",
            "route53",
            "iam",
            "kms",
            "secretsmanager",
            "cloudwatch",
            "cloudtrail",
            "config",
            "securityhub",
            "guardduty"
        ]
    
    @staticmethod
    def get_compliance_frameworks() -> List[str]:
        """List of supported compliance frameworks"""
        return [
            "CIS AWS Foundations Benchmark",
            "PCI-DSS",
            "HIPAA",
            "SOC 2",
            "ISO 27001",
            "NIST 800-53",
            "GDPR"
        ]
