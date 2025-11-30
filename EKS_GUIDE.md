# ⎈ CloudIDP v2.0 - EKS Provisioning Guide

## 🎉 **EKS SUPPORT ADDED!**

CloudIDP now includes complete **Amazon EKS (Elastic Kubernetes Service)** provisioning and management!

---

## 🚀 **EKS FEATURES**

### ✅ **Complete EKS Lifecycle Management**
- Create EKS clusters across accounts/regions
- Manage node groups (EC2 and Fargate)
- Configure EKS add-ons
- Update Kubernetes versions
- Delete clusters safely

### ✅ **Multi-Account EKS**
- View all EKS clusters across accounts
- Cost tracking per cluster
- Centralized cluster management
- Cross-account kubectl configuration

### ✅ **EKS Provisioning Wizard**
- Step-by-step cluster creation
- Automatic node group setup
- Network configuration
- IAM role configuration
- Cost estimation

### ✅ **EKS Cost Optimization**
- Per-cluster cost breakdown
- Node group cost analysis
- Right-sizing recommendations
- Spot instance support (coming soon)

---

## 📋 **EKS FEATURES OVERVIEW**

### **Cluster Overview Tab**
- View all EKS clusters across accounts
- Cluster status monitoring
- Node count tracking
- Monthly cost per cluster
- Quick cluster health checks

### **Create Cluster Tab**
- Interactive cluster creation wizard
- Multi-step configuration:
  - Basic settings (name, version, region)
  - Network configuration (VPC, subnets)
  - Node group configuration
  - IAM roles
  - Logging options
  - Tags
- Real-time cost estimation
- Automated node group creation

### **Manage Clusters Tab**
- Update Kubernetes version
- Scale node groups
- Update cluster configuration
- Delete clusters (with safety checks)

### **Node Groups Tab**
- Create managed node groups
- Configure auto-scaling
- Update instance types
- Manage node group lifecycle

### **Add-ons Tab**
- Install EKS add-ons:
  - VPC CNI
  - CoreDNS
  - kube-proxy
  - EBS CSI driver
  - EFS CSI driver

### **Cost Analysis Tab**
- Per-cluster cost breakdown
- Control plane costs
- Worker node costs
- Storage costs
- Optimization recommendations

---

## 🔧 **PREREQUISITES**

### **1. IAM Roles Required**

#### **EKS Cluster Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Attach Policies:**
- `AmazonEKSClusterPolicy`

#### **EKS Node Role:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

**Attach Policies:**
- `AmazonEKSWorkerNodePolicy`
- `AmazonEKS_CNI_Policy`
- `AmazonEC2ContainerRegistryReadOnly`

### **2. Network Requirements**

- VPC with at least 2 subnets in different AZs
- Subnets must have available IP addresses
- Internet gateway (for public subnets) or NAT gateway (for private)

### **3. CloudIDP Permissions**

Update your CloudIDP-Access role to include:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:*",
        "ec2:DescribeVpcs",
        "ec2:DescribeSubnets",
        "ec2:DescribeSecurityGroups",
        "iam:GetRole",
        "iam:ListRoles"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## 🚀 **CREATING YOUR FIRST EKS CLUSTER**

### **Step 1: Navigate to EKS Module**
1. Open CloudIDP
2. Click "⎈ EKS Clusters" tab
3. Go to "Create Cluster" sub-tab

### **Step 2: Configure Cluster**

**Basic Configuration:**
- **Target Account:** Select AWS account
- **Region:** us-east-1 (or your preferred region)
- **Cluster Name:** my-production-cluster
- **Kubernetes Version:** 1.30 (latest)
- **Cluster IAM Role:** arn:aws:iam::123456789012:role/eks-cluster-role

**Network Configuration:**
- **VPC ID:** vpc-xxxxxxxxx
- **Subnet IDs:** subnet-xxx, subnet-yyy (at least 2 in different AZs)
- **Public Access:** ✅ Enabled
- **Private Access:** ✅ Enabled

**Node Group Configuration:**
- **Instance Type:** t3.medium (or larger for production)
- **Desired Nodes:** 3
- **Min Nodes:** 1
- **Max Nodes:** 10
- **Disk Size:** 20 GB
- **Node IAM Role:** arn:aws:iam::123456789012:role/eks-node-role

**Additional Options:**
- **Enable Logging:** ✅ (recommended)
- **Tags:** Environment=production, ManagedBy=CloudIDP

### **Step 3: Review & Create**

CloudIDP will show:
- **Estimated Monthly Cost:** ~$163/month
  - Control Plane: $73
  - 3x t3.medium nodes: ~$90

Click "🚀 Create EKS Cluster"

### **Step 4: Wait for Cluster**

- Cluster creation: ~10-15 minutes
- CloudIDP will show creation progress
- Status will change from CREATING → ACTIVE

### **Step 5: Configure kubectl**

Once active, configure kubectl:

```bash
aws eks update-kubeconfig \
  --region us-east-1 \
  --name my-production-cluster

# Verify
kubectl get nodes
```

---

## 💰 **EKS COST BREAKDOWN**

### **Monthly Costs:**

**Control Plane:**
- $0.10/hour = **$73/month** per cluster

**Worker Nodes (Examples):**
- t3.small: $0.0208/hr = $15.18/month
- t3.medium: $0.0416/hr = $30.37/month
- t3.large: $0.0832/hr = $60.74/month
- m5.large: $0.096/hr = $70.08/month
- m5.xlarge: $0.192/hr = $140.16/month

**Example Cluster:**
- Control Plane: $73
- 3x t3.medium nodes: $91
- **Total: ~$164/month**

---

## 🎯 **BEST PRACTICES**

### **Security:**
- ✅ Use private API endpoint for production
- ✅ Enable control plane logging
- ✅ Use IAM roles for service accounts (IRSA)
- ✅ Enable network policies
- ✅ Use AWS Secrets Manager for secrets

### **High Availability:**
- ✅ Deploy nodes across multiple AZs
- ✅ Use multiple node groups
- ✅ Configure pod disruption budgets
- ✅ Use cluster autoscaler

### **Cost Optimization:**
- ✅ Use Spot instances for non-critical workloads
- ✅ Right-size your nodes
- ✅ Use cluster autoscaler
- ✅ Consider Fargate for serverless workloads
- ✅ Delete unused clusters

### **Operations:**
- ✅ Tag all resources
- ✅ Enable CloudWatch Container Insights
- ✅ Use AWS Load Balancer Controller
- ✅ Keep Kubernetes version updated
- ✅ Regular backups with Velero

---

## 📊 **EKS IN CLOUDIDP DASHBOARD**

### **Cluster Overview Shows:**
- Total clusters across accounts
- Total worker nodes
- Total monthly cost
- Active vs creating/deleting status
- Kubernetes versions in use

### **Per-Cluster Details:**
- Cluster name and status
- Kubernetes version
- Node group count
- Total nodes
- Monthly cost estimate
- Creation date
- Account and region

---

## 🔄 **EKS LIFECYCLE OPERATIONS**

### **Update Kubernetes Version:**
1. Select cluster in "Manage Clusters"
2. Choose new version
3. Click "Update Version"
4. Wait for update to complete (~20-30 min)

### **Scale Node Group:**
1. Go to "Node Groups" tab
2. Select node group
3. Adjust desired/min/max nodes
4. Save changes

### **Delete Cluster:**
1. Go to "Manage Clusters"
2. Select cluster
3. Click "Delete Cluster"
4. Confirm deletion
5. CloudIDP will:
   - Delete all node groups first
   - Then delete cluster
   - Clean up resources

---

## 🎉 **YOU NOW HAVE COMPLETE EKS SUPPORT!**

**Features:**
- ✅ Multi-account EKS management
- ✅ Cluster creation wizard
- ✅ Node group management
- ✅ Cost tracking
- ✅ EKS add-ons
- ✅ Version updates
- ✅ Safe cluster deletion

**Navigate to: ⎈ EKS Clusters tab to get started!**

---

## 📚 **ADDITIONAL RESOURCES**

- [AWS EKS Documentation](https://docs.aws.amazon.com/eks/)
- [EKS Best Practices Guide](https://aws.github.io/aws-eks-best-practices/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)

---

**Happy Kubernetes clustering! ⎈**
