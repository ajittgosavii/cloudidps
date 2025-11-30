"""
Design & Planning Module - Blueprint Management & Standards
Infrastructure design, tagging, naming conventions, and IaC registry
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Optional
from core_account_manager import get_account_manager

class DesignPlanningModule:
    """Design & Planning functionality"""
    
    @staticmethod
    def render():
        """Main render method"""
        st.title("📐 Design & Planning")
        
        # Create tabs for sub-features
        tabs = st.tabs([
            "📋 Blueprints",
            "🏷️ Tagging Standards",
            "📛 Naming Conventions",
            "📦 Artifact Versioning",
            "📁 IaC Registry",
            "✅ Design Validation"
        ])
        
        with tabs[0]:
            DesignPlanningModule._render_blueprints()
        
        with tabs[1]:
            DesignPlanningModule._render_tagging()
        
        with tabs[2]:
            DesignPlanningModule._render_naming()
        
        with tabs[3]:
            DesignPlanningModule._render_versioning()
        
        with tabs[4]:
            DesignPlanningModule._render_iac_registry()
        
        with tabs[5]:
            DesignPlanningModule._render_validation()
    
    @staticmethod
    def _render_blueprints():
        """Blueprint library and creation"""
        st.subheader("📋 Architecture Blueprints")
        
        blueprint_tabs = st.tabs(["📚 Library", "➕ Create New"])
        
        with blueprint_tabs[0]:
            # Blueprint library
            st.markdown("### Blueprint Library")
            
            # Sample blueprints
            blueprints = [
                {
                    "name": "Three-Tier Web Application",
                    "category": "Web Application",
                    "version": "2.1.0",
                    "description": "Classic 3-tier architecture with VPC, ALB, EC2, and RDS",
                    "services": ["VPC", "EC2", "RDS", "ALB", "Route53"],
                    "cost": 850.00,
                    "deployments": 24
                },
                {
                    "name": "Serverless API Backend",
                    "category": "Serverless",
                    "version": "1.5.2",
                    "description": "API Gateway + Lambda + DynamoDB serverless stack",
                    "services": ["API Gateway", "Lambda", "DynamoDB", "CloudWatch"],
                    "cost": 120.00,
                    "deployments": 18
                },
                {
                    "name": "Data Lake Platform",
                    "category": "Data Analytics",
                    "version": "3.0.1",
                    "description": "S3-based data lake with Glue, Athena, and QuickSight",
                    "services": ["S3", "Glue", "Athena", "QuickSight", "EMR"],
                    "cost": 2100.00,
                    "deployments": 8
                },
                {
                    "name": "EKS Microservices",
                    "category": "Microservices",
                    "version": "2.3.0",
                    "description": "Production-grade EKS cluster with monitoring and CI/CD",
                    "services": ["EKS", "ECR", "ALB", "CloudWatch", "VPC"],
                    "cost": 1500.00,
                    "deployments": 15
                }
            ]
            
            # Filters
            col1, col2, col3 = st.columns(3)
            with col1:
                category_filter = st.selectbox("Category", 
                    ["All"] + list(set([b['category'] for b in blueprints])))
            with col2:
                sort_by = st.selectbox("Sort by", ["Name", "Deployments", "Cost"])
            with col3:
                search = st.text_input("Search", placeholder="Search blueprints...")
            
            # Display blueprints
            for bp in blueprints:
                if (category_filter == "All" or bp['category'] == category_filter):
                    with st.expander(f"📋 {bp['name']} v{bp['version']}"):
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.write(f"**Description:** {bp['description']}")
                            st.write(f"**Category:** {bp['category']}")
                            st.write(f"**AWS Services:** {', '.join(bp['services'])}")
                        
                        with col2:
                            st.metric("Deployments", bp['deployments'])
                            st.metric("Est. Cost/mo", f"${bp['cost']:.2f}")
                        
                        # Actions
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            if st.button("🚀 Deploy", key=f"deploy_{bp['name']}"):
                                st.success(f"Deploying {bp['name']}...")
                        with col2:
                            if st.button("📋 Clone", key=f"clone_{bp['name']}"):
                                st.info(f"Cloning {bp['name']}...")
                        with col3:
                            if st.button("✏️ Edit", key=f"edit_{bp['name']}"):
                                st.info("Edit mode enabled")
                        with col4:
                            if st.button("📥 Export", key=f"export_{bp['name']}"):
                                st.success("Blueprint exported")
        
        with blueprint_tabs[1]:
            # Create blueprint
            st.markdown("### Create New Blueprint")
            
            with st.form("create_blueprint"):
                col1, col2 = st.columns(2)
                
                with col1:
                    name = st.text_input("Blueprint Name*", placeholder="My Blueprint")
                    category = st.selectbox("Category*", [
                        "Web Application", "Serverless", "Data Analytics",
                        "Microservices", "Storage", "Network", "Security"
                    ])
                    version = st.text_input("Version*", value="1.0.0")
                
                with col2:
                    author = st.text_input("Author", placeholder="Your name")
                    estimated_cost = st.number_input("Monthly Cost ($)", min_value=0.0, value=500.0)
                
                description = st.text_area("Description*", 
                    placeholder="Describe your blueprint architecture...")
                
                services = st.multiselect("AWS Services", [
                    "VPC", "EC2", "RDS", "S3", "Lambda", "API Gateway", 
                    "DynamoDB", "EKS", "ECR", "ALB", "CloudWatch"
                ])
                
                environments = st.multiselect("Target Environments",
                    ["Development", "Staging", "Production", "DR"])
                
                template = st.text_area("IaC Template (Terraform/CloudFormation)",
                    placeholder="Paste your infrastructure code here...",
                    height=200)
                
                submit = st.form_submit_button("Create Blueprint")
                
                if submit:
                    if name and category and description:
                        st.success(f"✅ Blueprint '{name}' created successfully!")
                    else:
                        st.error("Please fill in all required fields")
    
    @staticmethod
    def _render_tagging():
        """Tagging standards"""
        st.subheader("🏷️ Tagging Standards")
        
        st.markdown("""
        ### Enforce Consistent Tagging Across Resources
        
        Define and enforce tagging policies for cost allocation, compliance, and governance.
        """)
        
        # Mandatory tags
        st.markdown("### Mandatory Tags")
        
        mandatory_tags = [
            {"Key": "Environment", "Values": ["dev", "staging", "prod", "dr"], "Required": True},
            {"Key": "CostCenter", "Values": ["Engineering", "Marketing", "Sales", "Operations"], "Required": True},
            {"Key": "Owner", "Values": ["team@company.com"], "Required": True},
            {"Key": "Project", "Values": ["ProjectName"], "Required": True},
            {"Key": "Compliance", "Values": ["PCI", "HIPAA", "GDPR", "None"], "Required": False}
        ]
        
        tags_df = pd.DataFrame(mandatory_tags)
        st.dataframe(tags_df, use_container_width=True)
        
        # Add new tag policy
        st.markdown("### Add Tag Policy")
        
        with st.form("add_tag_policy"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                tag_key = st.text_input("Tag Key", placeholder="Department")
            with col2:
                tag_values = st.text_input("Allowed Values (comma-separated)", 
                    placeholder="Finance,IT,HR")
            with col3:
                required = st.checkbox("Required", value=True)
            
            if st.form_submit_button("Add Tag Policy"):
                if tag_key:
                    st.success(f"✅ Tag policy for '{tag_key}' added")
                else:
                    st.error("Tag key is required")
    
    @staticmethod
    def _render_naming():
        """Naming conventions"""
        st.subheader("📛 Naming Conventions")
        
        st.markdown("""
        ### Resource Naming Standards
        
        Maintain consistent naming across all AWS resources for easy identification and management.
        """)
        
        # Naming patterns
        st.markdown("### Naming Patterns")
        
        patterns = [
            {"Resource": "VPC", "Pattern": "{env}-{region}-vpc", "Example": "prod-us-east-1-vpc"},
            {"Resource": "Subnet", "Pattern": "{env}-{az}-{type}-subnet", "Example": "prod-us-east-1a-public-subnet"},
            {"Resource": "EC2", "Pattern": "{env}-{app}-{role}-{num}", "Example": "prod-web-server-01"},
            {"Resource": "RDS", "Pattern": "{env}-{app}-{engine}-db", "Example": "prod-app-postgres-db"},
            {"Resource": "S3 Bucket", "Pattern": "{company}-{env}-{purpose}", "Example": "acme-prod-logs"},
            {"Resource": "Lambda", "Pattern": "{env}-{app}-{function}", "Example": "prod-api-auth"},
            {"Resource": "EKS Cluster", "Pattern": "{env}-{region}-eks", "Example": "prod-us-east-1-eks"}
        ]
        
        patterns_df = pd.DataFrame(patterns)
        st.dataframe(patterns_df, use_container_width=True)
        
        # Name generator
        st.markdown("### Name Generator")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            resource_type = st.selectbox("Resource Type", 
                ["VPC", "Subnet", "EC2", "RDS", "S3 Bucket", "Lambda", "EKS"])
        with col2:
            environment = st.selectbox("Environment", ["dev", "staging", "prod", "dr"])
        with col3:
            region = st.selectbox("Region", ["us-east-1", "us-west-2", "eu-west-1"])
        
        if st.button("Generate Name"):
            if resource_type == "VPC":
                name = f"{environment}-{region}-vpc"
            elif resource_type == "EC2":
                name = f"{environment}-app-server-01"
            else:
                name = f"{environment}-{resource_type.lower()}-resource"
            
            st.success(f"✅ Generated name: **{name}**")
    
    @staticmethod
    def _render_versioning():
        """Artifact versioning"""
        st.subheader("📦 Artifact Versioning")
        
        st.markdown("""
        ### Infrastructure Artifact Version Control
        
        Track and manage versions of infrastructure templates, configurations, and blueprints.
        """)
        
        # Version history
        st.markdown("### Version History")
        
        versions = [
            {"Version": "3.2.1", "Date": "2025-11-28", "Author": "platform-team", "Changes": "Security updates", "Status": "Latest"},
            {"Version": "3.2.0", "Date": "2025-11-15", "Author": "platform-team", "Changes": "Added monitoring", "Status": "Stable"},
            {"Version": "3.1.5", "Date": "2025-11-01", "Author": "dev-team", "Changes": "Bug fixes", "Status": "Deprecated"},
            {"Version": "3.1.0", "Date": "2025-10-15", "Author": "platform-team", "Changes": "Major release", "Status": "Deprecated"}
        ]
        
        versions_df = pd.DataFrame(versions)
        st.dataframe(versions_df, use_container_width=True)
        
        # Version comparison
        st.markdown("### Compare Versions")
        
        col1, col2 = st.columns(2)
        with col1:
            version_a = st.selectbox("Version A", ["3.2.1", "3.2.0", "3.1.5"])
        with col2:
            version_b = st.selectbox("Version B", ["3.2.0", "3.1.5", "3.1.0"])
        
        if st.button("Compare"):
            st.info(f"Comparing {version_a} with {version_b}...")
            st.code("""
+ Added: Enhanced security groups
+ Added: CloudWatch alarms
- Removed: Legacy configurations
~ Modified: VPC CIDR blocks
            """)
    
    @staticmethod
    def _render_iac_registry():
        """IaC registry"""
        st.subheader("📁 Infrastructure as Code Registry")
        
        st.markdown("""
        ### Centralized IaC Template Repository
        
        Store, version, and share infrastructure templates across teams.
        """)
        
        # Registry
        st.markdown("### Template Registry")
        
        templates = [
            {"Name": "vpc-standard", "Type": "Terraform", "Version": "2.0.0", "Downloads": 145, "Stars": 28},
            {"Name": "eks-cluster", "Type": "Terraform", "Version": "1.8.3", "Downloads": 98, "Stars": 42},
            {"Name": "rds-postgres", "Type": "CloudFormation", "Version": "1.5.1", "Downloads": 67, "Stars": 19},
            {"Name": "lambda-api", "Type": "SAM", "Version": "1.2.0", "Downloads": 156, "Stars": 35}
        ]
        
        templates_df = pd.DataFrame(templates)
        st.dataframe(templates_df, use_container_width=True)
        
        # Template details
        if templates:
            selected = st.selectbox("View Template", 
                [t['Name'] for t in templates])
            
            if selected:
                st.markdown(f"### Template: {selected}")
                st.code("""
# Example Terraform Template
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = var.vpc_name
    Environment = var.environment
    ManagedBy   = "CloudIDP"
  }
}
                """, language="hcl")
    
    @staticmethod
    def _render_validation():
        """Design validation"""
        st.subheader("✅ Design Validation")
        
        st.markdown("""
        ### Validate Infrastructure Designs
        
        Check designs against best practices, compliance requirements, and cost constraints.
        """)
        
        # Validation rules
        st.markdown("### Validation Rules")
        
        rules = [
            {"Rule": "VPC must have public and private subnets", "Severity": "Error", "Enabled": True},
            {"Rule": "RDS must have Multi-AZ enabled in production", "Severity": "Error", "Enabled": True},
            {"Rule": "S3 buckets must have encryption enabled", "Severity": "Error", "Enabled": True},
            {"Rule": "Security groups should not allow 0.0.0.0/0 on SSH", "Severity": "Warning", "Enabled": True},
            {"Rule": "Cost should not exceed budget threshold", "Severity": "Warning", "Enabled": True}
        ]
        
        rules_df = pd.DataFrame(rules)
        st.dataframe(rules_df, use_container_width=True)
        
        # Run validation
        st.markdown("### Run Validation")
        
        template_to_validate = st.text_area("Paste Infrastructure Template",
            placeholder="Paste your Terraform or CloudFormation template...",
            height=200)
        
        if st.button("Validate Design"):
            if template_to_validate:
                st.success("✅ Validation passed!")
                
                st.markdown("### Validation Results")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Errors", 0)
                with col2:
                    st.metric("Warnings", 2)
                with col3:
                    st.metric("Score", "95/100")
                
                st.warning("⚠️ Warning: Security group allows SSH from 0.0.0.0/0")
                st.warning("⚠️ Warning: Estimated cost exceeds $1000/month")
            else:
                st.error("Please provide a template to validate")
