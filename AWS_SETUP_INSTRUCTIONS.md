# 🔧 AWS Setup Instructions for KOR.AI Deployment

## 📋 **Required AWS Services & Permissions**

### **Step 1: Create IAM User for Deployment**

1. **Login to AWS Console**: https://console.aws.amazon.com/
   - Account ID: 6969-2713-8278
   - Alias: kor-ai-test
   - Password: Therav1

2. **Go to IAM Service** → Users → Create User
   - Username: `kor-ai-deployment`
   - Access type: ✅ Programmatic access

3. **Attach Policies** (Select these existing AWS policies):
   ```
   ✅ AWSLambdaFullAccess
   ✅ AmazonAPIGatewayAdministrator  
   ✅ IAMFullAccess
   ✅ AmazonS3FullAccess
   ✅ CloudWatchFullAccess
   ✅ AWSCertificateManagerFullAccess
   ✅ AmazonRoute53FullAccess
   ```

4. **Download Credentials**:
   - Access Key ID: `AKIA...` (save this)
   - Secret Access Key: `...` (save this)

### **Step 2: Create SSL Certificates**

1. **Go to Certificate Manager** (ACM) in EU-West-1 region
2. **Request Certificate** → Request a public certificate
3. **Domain names**:
   ```
   *.korinsic.com
   korinsic.com
   ```
4. **Validation method**: DNS validation
5. **Copy CNAME records** from AWS and add them to Namecheap DNS

### **Step 3: GitHub Secrets Configuration**

Add these secrets to your GitHub repository:
```
Repository Settings → Secrets and Variables → Actions → New repository secret
```

**Required Secrets:**
```
AWS_ACCESS_KEY_ID = [from Step 1]
AWS_SECRET_ACCESS_KEY = [from Step 1]
```

### **Step 4: Namecheap DNS Configuration**

**In your Namecheap DNS settings, add these CNAME records:**

| Type | Host | Value | TTL |
|------|------|-------|-----|
| CNAME | api-staging | [Lambda API Gateway URL] | 300 |
| CNAME | api | [Lambda API Gateway URL] | 300 |
| CNAME | staging | [Amplify URL] | 300 |
| CNAME | www | [Amplify URL] | 300 |

*Note: The actual URLs will be provided after deployment*

## 🚀 **Deployment Commands**

### **Local Testing (Optional)**
```bash
# Install Serverless Framework
npm install -g serverless@3

# Configure AWS credentials locally
serverless config credentials --provider aws --key YOUR_ACCESS_KEY --secret YOUR_SECRET_KEY

# Deploy staging
serverless deploy --stage staging

# Deploy production  
serverless deploy --stage production
```

### **GitHub Deployment (Automated)**
```bash
# Push to staging
git push origin develop

# Push to production
git push origin main
```

## 📊 **Expected AWS Resources**

**After deployment, you'll have:**
- ✅ Lambda Function: `kor-ai-surveillance-api-staging-api`
- ✅ API Gateway: REST API with custom domain
- ✅ CloudWatch Logs: For monitoring
- ✅ IAM Roles: Auto-created by Serverless

## 💰 **Expected Monthly Costs**
- Lambda: $0-10 (depending on usage)
- API Gateway: $0-5
- Certificate Manager: Free
- Route 53: $0.50/month per hosted zone (if used)

**Total: ~$1-15/month for staging + production**

## 🔍 **Verification Steps**

**After deployment, test these URLs:**
- Health check: `https://api-staging.korinsic.com/health`
- API endpoint: `https://api-staging.korinsic.com/api/v1/analyze`

## ❗ **Troubleshooting**

**Common Issues:**
1. **Certificate validation**: Ensure CNAME records are added to Namecheap
2. **Permission errors**: Verify IAM policies are attached
3. **Region mismatch**: Ensure everything is in eu-west-1

**Support Commands:**
```bash
# Check deployment status
serverless info --stage staging

# View logs
serverless logs -f api --stage staging

# Remove deployment (if needed)
serverless remove --stage staging
```