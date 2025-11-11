# Production Deployment Guide - Neo-Guardrails

## Quick Overview: Where Your Files Go

**Your files are ALREADY on your computer. Here's what goes where:**

| Component | What | Where It Goes | How |
|-----------|------|---------------|-----|
| **React Frontend** | `src/`, `public/`, `package.json` | AWS Amplify pulls from GitHub | You push to GitHub, Amplify clones it |
| **Flask + Model** | `app.py`, `rm_guardrail_model/` (~2GB) | Docker image → AWS ECR → Lambda | Docker packages locally, you push image to ECR |
| **Backend Config** | `amplify/` directory | AWS (DynamoDB, AppSync) | Amplify CLI deploys from your local machine |

**TL;DR:**
- ✅ Model files stay local → packaged into Docker → uploaded to AWS ECR
- ✅ Frontend code stays in GitHub → Amplify clones it automatically
- ✅ Backend config deployed from local `amplify/` directory

---

## Deployment Flow

```
Step 1: Backend (DynamoDB + GraphQL)
-----------------------------------------
Your Computer (amplify/ directory)
    ↓ npx ampx deploy
AWS Amplify Service
    ↓ Creates
DynamoDB + AppSync API + Cognito

Step 2: Flask ML API
-----------------------------------------
Option A (Lambda):
Your Computer (app.py + rm_guardrail_model/)
    ↓ docker build (packages model into image)
Docker Image (~2-3GB on your computer)
    ↓ docker push
AWS ECR (Elastic Container Registry)
    ↓ Lambda pulls from ECR
Lambda Function (runs your Flask + model)
    ↓ Creates
Function URL (https://xyz.lambda-url.aws.com)

Option B (Elastic Beanstalk):
Your Computer (app.py + rm_guardrail_model/)
    ↓ eb create (zips entire directory)
S3 Bucket (temporary storage)
    ↓ EB extracts and deploys
EC2 Instances (runs your Flask + model)
    ↓ Creates
Load Balancer URL (http://xyz.elasticbeanstalk.com)

Step 3: React Frontend
-----------------------------------------
Your Computer
    ↓ git push
GitHub Repository (jacob-neosapients/chatbot)
    ↓ Amplify auto-clones
AWS Amplify Build Service
    ↓ npm install && npm run build
CloudFront CDN (global content delivery)
    ↓ Serves at
Your App URL (https://xyz.amplifyapp.com)
```

---

## Architecture Overview

**Hybrid Deployment:**
- Frontend: React on AWS Amplify
- Backend Data: DynamoDB (managed by Amplify)
- ML Inference: Flask API (separate deployment)

---

## Prerequisites Setup

### 1. Install AWS CLI (Required)

**macOS:**
```bash
# Using Homebrew (recommended)
brew install awscli

# Verify installation
aws --version
```

**Alternative (if no Homebrew):**
```bash
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

### 2. Configure AWS CLI (Required)

```bash
aws configure
```

You'll be prompted for:
- **AWS Access Key ID**: Get from AWS Console → IAM → Users → Security Credentials
- **AWS Secret Access Key**: Same location as above
- **Default region**: `us-east-1` (or your preferred region)
- **Default output format**: `json`

**To create AWS credentials:**
1. Go to [AWS Console](https://console.aws.amazon.com/)
2. IAM → Users → Your User → Security Credentials
3. Click "Create access key"
4. Choose "Command Line Interface (CLI)"
5. Copy the Access Key ID and Secret Access Key

### 3. Install Docker (Required for Lambda Option)

**macOS:**
```bash
# Using Homebrew
brew install --cask docker

# OR download from https://www.docker.com/products/docker-desktop/
```

Start Docker Desktop after installation.

### 4. Install Amplify CLI (Required)

```bash
npm install -g @aws-amplify/backend-cli
```

### 5. Already Installed

You should already have:
- ✅ Node.js 18+ (check: `node --version`)
- ✅ Python 3.8+ (check: `python3 --version`)

---

## Do You NEED All This?

| Tool | Required For | Can Skip If... |
|------|--------------|----------------|
| **AWS CLI** | All deployments | ❌ No - absolutely required |
| **Docker** | Lambda deployment only | ✅ Yes - if using Elastic Beanstalk instead |
| **Amplify CLI** | Backend deployment | ❌ No - needed for DynamoDB/GraphQL |

**Simplest path if you don't want Docker:**
Use **Elastic Beanstalk** (Option B) for Flask deployment - no Docker needed!

**Installation check:**
```bash
# Check AWS CLI
aws --version  # Should show: aws-cli/2.x.x

# Check Docker (only if using Lambda)
docker --version  # Should show: Docker version 24.x.x

# Check Amplify CLI
ampx --version  # Should show: @aws-amplify/backend-cli version

# Check Node & Python (you should have these)
node --version  # v18.x or higher
python3 --version  # 3.8.x or higher
```

---

## Quickest Path to Production (No Docker)

**If you just want to deploy fast without learning Docker:**

1. **Install only AWS CLI** (5 minutes)
   ```bash
   brew install awscli
   aws configure  # Enter your AWS credentials
   ```

2. **Deploy Backend** (10 minutes)
   ```bash
   cd /Users/jacoblazar/repo-2/jailbreaker-repo/chatbot
   npx ampx deploy --branch main
   # Save the GraphQL endpoint and API key
   ```

3. **Deploy Flask with Elastic Beanstalk** (15 minutes)
   ```bash
   pip install awsebcli
   eb init neo-guardrails-ml --platform python-3.11 --region us-east-1
   eb create production
   # Save the URL
   ```

4. **Deploy Frontend** (10 minutes)
   - Push code to GitHub
   - Connect repository in Amplify Console
   - Add environment variables
   - Done!

**Total time: ~40 minutes (no Docker needed!)**

---

## Step 1: Deploy Amplify Backend (DynamoDB + GraphQL API)

### 1.1 Deploy Backend

```bash
npx ampx deploy --branch main
```

This creates:
- DynamoDB table for TrainingData
- AppSync GraphQL API
- Cognito authentication
- API Key for public access

**Deployment time:** ~5-10 minutes

### 1.2 Save Your Outputs

After deployment completes, note these values:

```
GraphQL Endpoint: https://xxxxx.appsync-api.us-east-1.amazonaws.com/graphql
API Key: da2-xxxxxxxxxxxxxxxxxxxxxxxxxx
Region: us-east-1
```

### 1.3 Optional: Disable DynamoDB Backups

If you want minimal backups:

1. Go to AWS Console → DynamoDB → Tables
2. Select `TrainingData-xxxxx` table
3. Backups tab → Disable "Point-in-time recovery"

---

## Step 2: Deploy Flask Backend (ML Inference)

### Important: Model Files Are Already Local

**Your model files are in:** `rm_guardrail_model/` directory in your project
- You don't need to upload them anywhere separately
- Docker will package them INTO the container image
- The container image is then uploaded to AWS ECR (Elastic Container Registry)
- Lambda downloads the container from ECR when it runs

### Option A: AWS Lambda with Container (Recommended)

**Why Lambda?**
- Auto-scaling
- Pay per request
- No server management
- Integrates with Amplify

**Steps:**

1. **Create Dockerfile in your project root:**

Create a file named `Dockerfile` (no extension) in `/Users/jacoblazar/repo-2/jailbreaker-repo/chatbot/`

```dockerfile
FROM public.ecr.aws/lambda/python:3.11

# Install dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install -r requirements.txt

# Copy model files from your local rm_guardrail_model/ directory into the container
# This packages ~2GB of model files into the Docker image
COPY rm_guardrail_model/ ${LAMBDA_TASK_ROOT}/rm_guardrail_model/

# Copy Flask app
COPY app.py ${LAMBDA_TASK_ROOT}/

# Add Mangum for Lambda handler (converts Flask to Lambda-compatible)
RUN pip install mangum

# Create handler wrapper
RUN echo "from mangum import Mangum\nfrom app import app\nhandler = Mangum(app)" > ${LAMBDA_TASK_ROOT}/lambda_handler.py

CMD ["lambda_handler.handler"]
```

**What this does:**
- Packages your entire `rm_guardrail_model/` directory (all model files) into the Docker image
- Includes `app.py` with your Flask API code
- Creates a ~2-3GB Docker image that contains everything Lambda needs to run

2. **Build Docker image locally and push to AWS ECR:**

Run these commands from your project directory:

```bash
# Navigate to project directory (if not already there)
cd /Users/jacoblazar/repo-2/jailbreaker-repo/chatbot

# Set variables
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1
IMAGE_NAME=neo-guardrails-ml

# Create ECR repository (AWS's Docker registry)
aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${AWS_REGION}

# Build Docker image locally (this packages your model files)
# This will take 5-10 minutes as it copies ~2GB of model files
docker build -t ${IMAGE_NAME} .

# Login to AWS ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Tag the image for ECR
docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest

# Push image to ECR (uploads your Docker image with model files to AWS)
# This will take 10-20 minutes to upload ~2-3GB
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest
```

**What happens:**
- `docker build`: Packages everything (code + model) into a single Docker image on your computer
- `docker push`: Uploads that image to AWS ECR (like GitHub but for Docker images)
- Lambda will download this image from ECR when it needs to run

3. **Create Lambda function (tells AWS to use your uploaded image):**

```bash
# Set variables
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=us-east-1
IMAGE_NAME=neo-guardrails-ml

# Create ECR repository
aws ecr create-repository --repository-name ${IMAGE_NAME} --region ${AWS_REGION}

**What happens:**
- `docker build`: Packages everything (code + model) into a single Docker image on your computer
- `docker push`: Uploads that image to AWS ECR (like GitHub but for Docker images)
- Lambda will download this image from ECR when it needs to run

3. **Create Lambda function (tells AWS to use your uploaded image):**

```bash
# Create execution role (one-time setup)
aws iam create-role \
  --role-name neo-guardrails-lambda-role \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "lambda.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Give Lambda permission to write logs
aws iam attach-role-policy \
  --role-name neo-guardrails-lambda-role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create Lambda function pointing to your ECR image
aws lambda create-function \
  --function-name neo-guardrails-ml \
  --package-type Image \
  --code ImageUri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest \
  --role arn:aws:iam::${AWS_ACCOUNT_ID}:role/neo-guardrails-lambda-role \
  --memory-size 3008 \
  --timeout 60 \
  --environment Variables="{AMPLIFY_GRAPHQL_ENDPOINT=<your-endpoint>,AMPLIFY_API_KEY=<your-key>}"
```

**Note:** Replace `<your-endpoint>` and `<your-key>` with values from Step 1.2, or leave as placeholders for now.

**Note:** Replace `<your-endpoint>` and `<your-key>` with values from Step 1.2, or leave as placeholders for now.

4. **Create Function URL (makes Lambda accessible via HTTP):**

```bash
# Create a public URL for your Lambda function
aws lambda create-function-url-config \
  --function-name neo-guardrails-ml \
  --auth-type NONE \
  --cors '{"AllowOrigins": ["*"], "AllowMethods": ["POST", "GET", "OPTIONS"], "AllowHeaders": ["*"]}'

# Get the Function URL
aws lambda get-function-url-config --function-name neo-guardrails-ml
```

**Save the Function URL output:** `https://xxxxx.lambda-url.us-east-1.on.aws/`

You'll use this URL in Step 3 for `REACT_APP_FLASK_API_URL`

### Option B: Elastic Beanstalk (Simplest - No Docker Required)

**Your files stay local, EB packages them automatically:**

```bash
# Install EB CLI
pip install awsebcli

# Navigate to project directory
cd /Users/jacoblazar/repo-2/jailbreaker-repo/chatbot

# Initialize (creates .elasticbeanstalk/ config directory locally)
eb init neo-guardrails-ml --platform python-3.11 --region us-east-1

# Create environment and deploy (EB will zip and upload your entire directory including rm_guardrail_model/)
eb create production \
  --envvars AMPLIFY_GRAPHQL_ENDPOINT=<your-endpoint>,AMPLIFY_API_KEY=<your-key>

# This command:
# 1. Zips your entire project directory (including rm_guardrail_model/)
# 2. Uploads to S3
# 3. Deploys to EC2 instances
# Takes 10-15 minutes

# Get your app URL
eb status
```

**What happens:**
- EB automatically packages your local directory (code + model files)
- Uploads to S3 as a zip file
- Extracts and runs on EC2 instances
- No Docker knowledge needed!

**Save the URL:** `http://neo-guardrails-ml-env.eba-xxxxx.us-east-1.elasticbeanstalk.com`

You'll use this URL in Step 3 for `REACT_APP_FLASK_API_URL`

### Option C: EC2 / ECS

See AWS documentation for EC2/ECS deployment with Docker.

---

## Step 3: Deploy Frontend to Amplify

### Important: Your Code Stays in GitHub

**Amplify pulls from your Git repository:**
- You don't upload files to Amplify manually
- Amplify connects to your GitHub/GitLab/Bitbucket
- Amplify automatically pulls code from your repository
- Builds and deploys on every git push

### 3.1 Push Your Code to GitHub (if not already done)

```bash
cd /Users/jacoblazar/repo-2/jailbreaker-repo/chatbot

# Add all files
git add .

# Commit changes
git commit -m "Ready for production deployment"

# Push to your repository
git push origin react-conversion
# or
git push origin main
```

**Your code is now in:** `https://github.com/jacob-neosapients/chatbot`

### 3.2 Connect Repository to Amplify Console

1. Go to [AWS Amplify Console](https://console.aws.amazon.com/amplify/)
2. Click **"New app"** → **"Host web app"**
3. Select **"GitHub"** (or your Git provider)
4. Authorize AWS Amplify to access your repositories
5. Select repository: **`jacob-neosapients/chatbot`**
6. Select branch: **`react-conversion`** or **`main`**
7. Amplify will auto-detect:
   - Build command: `npm run build`
   - Build output directory: `build`
   - No changes needed!
8. Click **"Save and deploy"**

**What happens:**
- Amplify clones your GitHub repository
- Runs `npm install` and `npm run build`
- Deploys the built React app to CloudFront CDN
- Takes 5-10 minutes for first deployment

**What happens:**
- Amplify clones your GitHub repository
- Runs `npm install` and `npm run build`
- Deploys the built React app to CloudFront CDN
- Takes 5-10 minutes for first deployment

### 3.3 Configure Environment Variables

**Before the build completes**, add environment variables:

In Amplify Console → Your App → **App Settings** → **Environment Variables**, click **"Manage variables"** and add:

| Key | Value | Example |
|-----|-------|---------|
| `REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT` | From Step 1.2 | `https://abc123.appsync-api.us-east-1.amazonaws.com/graphql` |
| `REACT_APP_AWS_REGION` | Your AWS region | `us-east-1` |
| `REACT_APP_AMPLIFY_API_KEY` | From Step 1.2 | `da2-xxxxxxxxxxxxxxxxxx` |
| `REACT_APP_FLASK_API_URL` | From Step 2 (Lambda or EB) | `https://xyz.lambda-url.us-east-1.on.aws` |

Click **"Save"**

### 3.4 Trigger Rebuild (if already deployed)

If the build already completed before you added env vars:

1. Go to your app in Amplify Console
2. Click **"Redeploy this version"**
3. Wait for build to complete (~5 minutes)

**Your app will be live at:** `https://react-conversion.d123456.amplifyapp.com` (or similar)

---

## Step 4: Update CORS Configuration

### 4.1 Update app.py

Edit `app.py` line 14-16 to include your Amplify domain:

```python
CORS(app, origins=[
    "https://main.d123456.amplifyapp.com",  # Your Amplify URL
    "http://localhost:3000"  # Keep for local dev
])
```

### 4.2 Redeploy Flask Backend

**Lambda:**
```bash
docker build -t ${IMAGE_NAME} .
docker tag ${IMAGE_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest
aws lambda update-function-code \
  --function-name neo-guardrails-ml \
  --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${IMAGE_NAME}:latest
```

**Elastic Beanstalk:**
```bash
eb deploy
```

---

## Step 5: Test Production Deployment

### 5.1 Test GraphQL API

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "x-api-key: <YOUR_API_KEY>" \
  -d '{"query":"{ listTrainingDatas { items { id prompt label } } }"}' \
  <YOUR_GRAPHQL_ENDPOINT>
```

### 5.2 Test Flask API

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"prompt":"Test message"}' \
  <YOUR_FLASK_URL>/api/classify
```

### 5.3 Test Frontend

1. Visit your Amplify URL
2. Submit a test prompt
3. Verify classification works
4. Check stats display
5. Test flag functionality

---

## Environment Variables Reference

### Frontend (.env for Amplify)
```bash
REACT_APP_AMPLIFY_GRAPHQL_ENDPOINT=https://xxxxx.appsync-api.us-east-1.amazonaws.com/graphql
REACT_APP_AWS_REGION=us-east-1
REACT_APP_AMPLIFY_API_KEY=da2-xxxxxxxxxxxxxxxxxx
REACT_APP_FLASK_API_URL=https://xxxxx.lambda-url.us-east-1.on.aws
```

### Backend (Flask environment variables)
```bash
AMPLIFY_GRAPHQL_ENDPOINT=https://xxxxx.appsync-api.us-east-1.amazonaws.com/graphql
AMPLIFY_API_KEY=da2-xxxxxxxxxxxxxxxxxx
```

---

## Monitoring & Maintenance

### CloudWatch Logs

**Amplify Frontend:**
- Amplify Console → Hosting → Build logs

**Lambda Backend:**
- CloudWatch → Log Groups → `/aws/lambda/neo-guardrails-ml`

**DynamoDB:**
- DynamoDB Console → Tables → Metrics

### Cost Optimization

**DynamoDB:**
- Use on-demand billing mode (default)
- Disable backups if not needed

**Lambda:**
- Monitor cold starts (usually ~5s for model loading)
- Consider provisioned concurrency for production traffic
- Review memory allocation vs. execution time

**Amplify Hosting:**
- Free tier: 1000 build minutes/month, 15 GB served
- After: ~$0.01 per build minute, ~$0.15 per GB served

### Estimated Monthly Costs

**Light Usage (100 requests/day):**
- DynamoDB: $0-1
- Lambda: $0-5
- Amplify: $0-5
- **Total: ~$0-10/month**

**Medium Usage (1000 requests/day):**
- DynamoDB: $1-3
- Lambda: $10-20
- Amplify: $5-10
- **Total: ~$15-35/month**

---

## Troubleshooting

### "Unable to classify message"
- Check Flask backend URL in environment variables
- Verify Flask API is running: `curl <FLASK_URL>/api/health`
- Check CORS configuration in app.py

### GraphQL mutations fail
- Verify API key hasn't expired (30 days default)
- Check API key is set in environment variables
- Review CloudWatch logs for errors

### Model loading fails (Lambda)
- Increase memory to 3008 MB (Lambda limit)
- Increase timeout to 60 seconds
- Check model files are included in Docker image

### CORS errors
- Update app.py with correct Amplify domain
- Redeploy Flask backend
- Clear browser cache

---

## CI/CD Setup (Optional)

### GitHub Actions for Lambda

Create `.github/workflows/deploy-lambda.yml`:

```yaml
name: Deploy Lambda
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Deploy to Lambda
        run: |
          docker build -t neo-guardrails-ml .
          # ... push to ECR and update Lambda
```

### Amplify Auto-Deploy

Amplify automatically deploys on git push if connected via Console.

---

## Security Best Practices

1. **API Keys:** Rotate every 30 days or use Cognito auth
2. **CORS:** Restrict to your domain only in production
3. **Secrets:** Use AWS Secrets Manager for sensitive data
4. **IAM:** Use least-privilege roles
5. **VPC:** Consider placing Lambda in VPC for database access

---

## Scaling Considerations

### DynamoDB
- Auto-scales automatically (on-demand mode)
- Consider provisioned capacity for predictable traffic

### Lambda
- Concurrent execution limit: 1000 (request increase if needed)
- Use provisioned concurrency to eliminate cold starts
- Consider SageMaker for very high traffic (>10k req/day)

### Amplify
- Auto-scales with CDN (CloudFront)
- No configuration needed

---

## Custom Domain (Optional)

### Add Custom Domain to Amplify

1. Amplify Console → App Settings → Domain management
2. Add domain: `guardrails.yourdomain.com`
3. Follow DNS configuration steps
4. SSL certificate auto-provisioned

### Update CORS

After adding custom domain, update `app.py`:

```python
CORS(app, origins=[
    "https://guardrails.yourdomain.com",
    "https://main.d123456.amplifyapp.com",
    "http://localhost:3000"
])
```

---

## Backup & Recovery

### DynamoDB
- Point-in-time recovery (optional): Up to 35 days
- On-demand backups: Manual snapshots

### Lambda
- Code stored in ECR (container image registry)
- Version your Docker images with tags

### Amplify
- Code stored in GitHub
- Build artifacts cached by Amplify

---

## Support Resources

- **Amplify Docs:** https://docs.amplify.aws/
- **Lambda Docs:** https://docs.aws.amazon.com/lambda/
- **DynamoDB Docs:** https://docs.aws.amazon.com/dynamodb/
- **AWS Support:** https://console.aws.amazon.com/support/

---

## Summary: What You Actually Do

### For Flask Backend (Lambda):
1. Create `Dockerfile` in project root
2. Run `docker build` - packages model files locally
3. Run `docker push` - uploads image to AWS ECR
4. Run `aws lambda create-function` - tells Lambda to use your image
5. Get Function URL - use this in frontend env vars

### For React Frontend (Amplify):
1. Push code to GitHub: `git push origin react-conversion`
2. Connect GitHub to Amplify Console (web UI)
3. Add environment variables in Amplify Console
4. Amplify auto-builds and deploys

### For Backend Data (Amplify):
1. Run `npx ampx deploy --branch main` from project directory
2. Save GraphQL endpoint and API key
3. Use these in Flask and Frontend env vars

**No manual file uploads needed!** Everything is automated through:
- GitHub (for frontend code)
- Docker + ECR (for Flask + model)
- Amplify CLI (for backend infrastructure)

---

## Quick Reference Commands

```bash
# Deploy Amplify backend
npx ampx deploy --branch main

# Update Lambda function
aws lambda update-function-code --function-name neo-guardrails-ml --image-uri <IMAGE_URI>

# View Lambda logs
aws logs tail /aws/lambda/neo-guardrails-ml --follow

# Amplify status
aws amplify list-apps

# DynamoDB table info
aws dynamodb describe-table --table-name TrainingData-xxxxx
```

---

**🚀 You're Ready for Production!**

Questions? Check AWS documentation or CloudWatch logs for debugging.
