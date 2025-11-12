# EC2 Deployment Guide for Guardrails ML API

## Prerequisites
- AWS Account with EC2 access
- Your EC2 SSH key file (`neosapients-dev-ec2.pem`) in this directory

## Step 1: Launch EC2 Instance

### Using AWS Console:
1. Go to [EC2 Console](https://ap-south-1.console.aws.amazon.com/ec2)
2. Click **"Launch Instance"**
3. Configure:
   - **Name**: `guardrails-ml-api`
   - **Region**: Asia Pacific (Mumbai) - `ap-south-1`
   - **AMI**: Ubuntu Server 22.04 LTS
   - **Instance type**: `t3.medium` (2 vCPU, 4 GB RAM) or `t3.large` for better performance
   - **Key pair**: Select your existing key or create new one
   - **Storage**: 20 GB gp3

4. **Security Group** - Configure these inbound rules:
   - SSH (22) - Your IP
   - HTTP (80) - Anywhere (0.0.0.0/0)
   - Custom TCP (5000) - Anywhere (0.0.0.0/0) [for direct Flask access]

5. Click **"Launch Instance"**

### Using AWS CLI:
```bash
# Create security group
aws ec2 create-security-group \
    --group-name guardrails-ml-sg \
    --description "Security group for Guardrails ML API" \
    --region ap-south-1

# Add inbound rules
aws ec2 authorize-security-group-ingress \
    --group-name guardrails-ml-sg \
    --protocol tcp --port 22 --cidr YOUR_IP/32 \
    --region ap-south-1

aws ec2 authorize-security-group-ingress \
    --group-name guardrails-ml-sg \
    --protocol tcp --port 80 --cidr 0.0.0.0/0 \
    --region ap-south-1

# Launch instance
aws ec2 run-instances \
    --image-id ami-0dee22c13ea7a9a67 \
    --instance-type t3.medium \
    --key-name YOUR_KEY_NAME \
    --security-groups guardrails-ml-sg \
    --region ap-south-1 \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=guardrails-ml-api}]'
```

## Step 2: Deploy Application

Once your EC2 instance is running:

1. **Get the Public DNS/IP** from EC2 console
   - Example: `ec2-13-232-xxx-xxx.ap-south-1.compute.amazonaws.com`

2. **Run deployment script**:
```bash
./deploy-ec2.sh ec2-13-232-xxx-xxx.ap-south-1.compute.amazonaws.com
```

This script will:
- ✅ Upload your Flask app and model
- ✅ Install Python and dependencies
- ✅ Set up systemd service for auto-restart
- ✅ Configure Nginx as reverse proxy with CORS
- ✅ Start the API

**Deployment takes ~3-5 minutes**

## Step 3: Verify Deployment

Test the API:
```bash
# Health check
curl http://YOUR_EC2_HOST/health

# Test classification
curl -X POST http://YOUR_EC2_HOST/api/classify \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you?"}'
```

## Step 4: Update React App

Update your React app to use the EC2 backend:

```bash
# Create .env.local file
echo "REACT_APP_FLASK_API_URL=http://YOUR_EC2_HOST" > .env.local

# Test locally
npm start

# Build for production
npm run build
```

## Step 5: Deploy to Amplify

```bash
# Push to GitHub
git add .
git commit -m "Update API endpoint for EC2"
git push origin deploy

# Amplify will auto-deploy from your repo
```

Or manually deploy:
```bash
npx ampx deploy
```

## Managing the EC2 Instance

### SSH into EC2:
```bash
ssh -i neosapients-dev-ec2.pem ubuntu@YOUR_EC2_HOST
```

### Check service status:
```bash
sudo systemctl status guardrails
```

### View logs:
```bash
sudo journalctl -u guardrails -f
```

### Restart service:
```bash
sudo systemctl restart guardrails
```

### Update application:
```bash
# Re-run deployment script
./deploy-ec2.sh YOUR_EC2_HOST
```

## Cost Estimate

**t3.medium** (recommended):
- On-Demand: ~$0.042/hour = ~$30/month
- With 1-year Reserved Instance: ~$20/month

**t3.large** (for better performance):
- On-Demand: ~$0.083/hour = ~$60/month
- With 1-year Reserved Instance: ~$40/month

## Troubleshooting

### API not responding:
```bash
ssh -i neosapients-dev-ec2.pem ubuntu@YOUR_EC2_HOST
sudo journalctl -u guardrails -n 50
```

### Check if Flask is running:
```bash
curl http://localhost:5000/health
```

### Check Nginx:
```bash
sudo systemctl status nginx
sudo nginx -t  # Test config
```

### Redeploy:
```bash
./deploy-ec2.sh YOUR_EC2_HOST
```

## Next Steps

1. (Optional) Set up **Elastic IP** for persistent IP address
2. (Optional) Set up **SSL certificate** with Let's Encrypt
3. (Optional) Set up **CloudWatch** monitoring
4. (Optional) Create **AMI backup** of configured instance

---

**Ready to deploy?** Run:
```bash
./deploy-ec2.sh YOUR_EC2_PUBLIC_DNS
```
