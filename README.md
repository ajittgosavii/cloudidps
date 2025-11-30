# ☁️ CloudIDP v2.0 - Enterprise Multi-Account Cloud Platform

## 🎯 **WHAT IS CLOUDIDP V2.0?**

Enterprise-grade cloud infrastructure development platform with:
- ✅ **Multi-Account AWS Management** (unlimited accounts)
- ✅ **Multi-Region Support** (all AWS regions)
- ✅ **Real-Time Cost Optimization**
- ✅ **Security & Compliance Aggregation**
- ✅ **Automated Account Onboarding/Offboarding**
- ✅ **Infrastructure Automation**
- 🔮 **Azure & GCP Integration** (Phase 2)

---

## 📦 **MODULES INCLUDED**

### **Module 1: Account & Region Management**
- Multi-account dashboard
- IAM role assumption
- Connection health monitoring
- Account lifecycle management

### **Module 2: Global Resource Inventory**
- Cross-account resource search
- EC2, RDS, DynamoDB, S3, Lambda, VPC
- Advanced filtering & tagging
- Resource dependency mapping

### **Module 3: Multi-Account FinOps**
- Consolidated billing view
- Cost by account/region/service
- Budget management & alerts
- RI & Savings Plans recommendations
- Tag-based cost allocation

### **Module 4: Design & Planning**
- Multi-account architecture templates
- Network topology designer
- Cost estimation
- Compliance validation

### **Module 5: Multi-Account Provisioning**
- Cross-account deployment
- Infrastructure as Code (Terraform/CDK)
- Approval workflows
- Rollback capabilities

### **Module 6: Operations**
- Cross-account automation
- Scheduled operations
- Incident response
- Runbook execution

### **Module 7: Security & Compliance**
- Security Hub aggregation
- GuardDuty threat detection
- Config compliance rules
- CIS/PCI-DSS/HIPAA dashboards

### **Module 8: Automated Account Lifecycle** ⭐ NEW
- **Onboarding:** Automated IAM setup, security enablement, tagging
- **Offboarding:** Resource inventory, cost reports, cleanup

---

## 🏗️ **ARCHITECTURE**

### **Multi-Account Strategy**

```
CloudIDP Platform
└─ Management AWS Account
    └─ CloudIDP IAM User
        └─ AssumeRole (STS)
            ├─ Production Account → CloudIDP-Access Role
            ├─ Development Account → CloudIDP-Access Role
            ├─ Staging Account → CloudIDP-Access Role
            └─ [Unlimited Accounts...]
```

**Benefits:**
- ✅ Most secure (AWS best practice)
- ✅ Centralized credential management
- ✅ Audit trail via CloudTrail
- ✅ Time-limited sessions
- ✅ Easy to add/remove accounts

---

## 🚀 **QUICK START GUIDE**

### **Step 1: AWS Account Setup**

#### **1.1 Create Management IAM User**

In your management AWS account:

```bash
# Create IAM user for CloudIDP
aws iam create-user --user-name cloudidp-platform

# Create access keys
aws iam create-access-key --user-name cloudidp-platform
# Save the AccessKeyId and SecretAccessKey!

# Attach policy for role assumption
aws iam attach-user-policy \
  --user-name cloudidp-platform \
  --policy-arn arn:aws:iam::aws:policy/SecurityAudit

# Create custom policy for STS
cat > cloudidp-sts-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sts:AssumeRole",
        "organizations:ListAccounts",
        "organizations:DescribeOrganization"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-user-policy \
  --user-name cloudidp-platform \
  --policy-name CloudIDP-STS-Policy \
  --policy-document file://cloudidp-sts-policy.json
```

#### **1.2 Create CloudIDP Roles in Target Accounts**

For **EACH** AWS account you want to manage, create this role:

```bash
# In each target account (Production, Development, etc.)

# Option A: Use CloudIDP automated onboarding (recommended)
# - Go to CloudIDP → Account Lifecycle → Onboard Account
# - Provide temporary admin credentials
# - CloudIDP will create the role automatically

# Option B: Manual role creation
aws iam create-role \
  --role-name CloudIDP-Access \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::MANAGEMENT_ACCOUNT_ID:user/cloudidp-platform"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "CloudIDP-MANAGEMENT_ACCOUNT_ID"
        }
      }
    }]
  }'

# Attach the CloudIDP policy (see CLOUDIDP_POLICY.json)
aws iam put-role-policy \
  --role-name CloudIDP-Access \
  --policy-name CloudIDP-Access-Policy \
  --policy-document file://CLOUDIDP_POLICY.json
```

---

### **Step 2: Configure CloudIDP**

#### **2.1 Streamlit Secrets Configuration**

Create `.streamlit/secrets.toml`:

```toml
# CloudIDP v2.0 Configuration

[aws]
# Management account credentials
management_access_key_id = "AKIA..."
management_secret_access_key = "your-secret-key"
default_region = "us-east-1"

# Target accounts
[aws.accounts.production]
account_id = "111111111111"
account_name = "Production"
role_arn = "arn:aws:iam::111111111111:role/CloudIDP-Access"
regions = ["us-east-1", "us-west-2", "eu-west-1"]
environment = "production"
cost_center = "Engineering"
owner_email = "platform@company.com"

[aws.accounts.development]
account_id = "222222222222"
account_name = "Development"
role_arn = "arn:aws:iam::222222222222:role/CloudIDP-Access"
regions = ["us-east-1"]
environment = "development"
cost_center = "Engineering"
owner_email = "devops@company.com"

[aws.accounts.staging]
account_id = "333333333333"
account_name = "Staging"
role_arn = "arn:aws:iam::333333333333:role/CloudIDP-Access"
regions = ["us-east-1", "us-west-2"]
environment = "staging"
cost_center = "Engineering"
owner_email = "devops@company.com"
```

---

### **Step 3: Deploy CloudIDP**

#### **3.1 Local Development**

```bash
# Clone repository
git clone https://github.com/your-org/cloudidp-v2.git
cd cloudidp-v2

# Install dependencies
pip install -r requirements.txt

# Configure secrets
mkdir .streamlit
# Edit .streamlit/secrets.toml (see above)

# Run locally
streamlit run app.py
```

#### **3.2 Deploy to Streamlit Cloud**

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Initial CloudIDP v2.0 deployment"
git remote add origin https://github.com/your-org/cloudidp-v2.git
git push -u origin main

# 2. Go to https://share.streamlit.io
# 3. Click "New app"
# 4. Select your repository
# 5. Main file: app.py
# 6. Add secrets from secrets.toml to Streamlit Cloud

# 7. Deploy!
```

---

## 📊 **WHAT YOU'LL SEE**

### **Home Dashboard**

```
┌─────────────────────────────────────────────────────────┐
│  CloudIDP v2.0 - Enterprise Cloud Platform             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Account: [All Accounts ▼]  Region: [All Regions ▼]    │
│                                                          │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ Accounts │ │Resources │ │ Monthly  │ │Compliance│  │
│  │    3     │ │   342    │ │ $124.5K  │ │   98%    │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                          │
│  Cost by Account (Last 30 Days)                         │
│  ┌────────────────────────────────────────┐            │
│  │ Production    ████████████████ $95.2K  │            │
│  │ Development   ████ $18.3K              │            │
│  │ Staging       ███ $11.0K               │            │
│  └────────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
```

### **Account Management**

```
Connected Accounts: 3
Last Sync: 2 minutes ago

┌──────────────────────────────────────────────┐
│ ✅ Production (111111111111)                 │
│ Regions: us-east-1, us-west-2, eu-west-1    │
│ Resources: 156 EC2, 12 RDS, 45 Lambda       │
│ Monthly Cost: $95,234                        │
│ [View Details] [Refresh] [Offboard]         │
└──────────────────────────────────────────────┘

[+ Onboard New Account]
```

### **Resource Inventory**

```
Search: [                                    ] 🔍
Filters: Account: [Production ▼]  Region: [us-east-1 ▼]  Type: [All ▼]

Results: 156 resources

Resource ID          Type    Status    Region      Cost/mo
i-0a1b2c3d4e5f6789  EC2     running   us-east-1   $73
db-instance-prod    RDS     available us-west-2   $145
lambda-api-handler  Lambda  ready     us-east-1   $12
```

---

## 🎯 **KEY FEATURES**

### **Automated Account Onboarding**

```
Onboarding Steps:
1. ✅ Validate Account Access
2. ✅ Create CloudIDP IAM Role
3. ✅ Configure CloudTrail
4. ✅ Enable AWS Config
5. ✅ Enable Security Hub
6. ✅ Enable GuardDuty
7. ✅ Activate Cost Explorer
8. ✅ Apply Tagging Policy
9. ✅ Register in CloudIDP

Duration: ~5-10 minutes
```

### **Automated Account Offboarding**

```
Offboarding Steps:
1. ✅ Export Resource Inventory
2. ✅ Generate Final Cost Report
3. ✅ Export Security Findings
4. ✅ Archive CloudTrail Logs
5. ✅ Backup Configuration
6. ✅ Remove CloudIDP Role
7. ✅ Deregister from CloudIDP

Duration: ~3-5 minutes
```

---

## 🔒 **SECURITY**

### **IAM Permissions**

CloudIDP uses **least-privilege access**:
- ✅ Read-only for most operations
- ✅ Write access only for approved actions
- ✅ No destructive operations without confirmation
- ✅ All actions logged in CloudTrail

### **Credential Management**

- ✅ Credentials stored in Streamlit secrets (encrypted)
- ✅ IAM role assumption with temporary credentials
- ✅ Sessions expire after 1 hour
- ✅ External ID for additional security

---

## 📈 **PERFORMANCE**

- ⚡ **Caching**: Aggressive caching for fast page loads
- ⚡ **Pagination**: Handle thousands of resources
- ⚡ **Parallel API calls**: Fetch from multiple accounts simultaneously
- ⚡ **Lazy loading**: Load data only when needed

---

## 🧪 **TESTING**

```bash
# Run tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Integration tests (requires AWS credentials)
pytest tests/integration/
```

---

## 📚 **DOCUMENTATION**

Full documentation available in `/docs`:
- Architecture Guide
- API Reference
- Best Practices
- Troubleshooting

---

## 🤝 **SUPPORT**

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: cloudidp-support@company.com

---

## 📅 **ROADMAP**

### **Phase 1: AWS Multi-Account** ✅ (Current)
- Multi-account management
- Resource inventory
- FinOps & cost optimization
- Security & compliance
- Account lifecycle

### **Phase 2: Azure Integration** (Q2 2024)
- Azure subscription management
- Cross-cloud cost comparison
- Unified security posture

### **Phase 3: GCP Integration** (Q3 2024)
- GCP project management
- Multi-cloud orchestration
- Unified billing

### **Phase 4: Advanced Features** (Q4 2024)
- AI-powered cost optimization
- Predictive scaling
- Auto-remediation
- Advanced analytics

---

## 🎉 **GETTING STARTED**

1. **Set up AWS accounts** (see Step 1 above)
2. **Configure secrets** (see Step 2 above)
3. **Deploy CloudIDP** (see Step 3 above)
4. **Onboard your first account!**

---

**Ready to transform your multi-account AWS management?** 🚀

**Questions? Open an issue or contact us!**
