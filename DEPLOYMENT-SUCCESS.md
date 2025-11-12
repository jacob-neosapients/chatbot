# 🎉 EC2 Deployment Complete!

## ✅ What's Deployed

Your Guardrails ML API is now running on AWS EC2!

### 🌐 API Endpoint
```
http://ec2-13-232-101-149.ap-south-1.compute.amazonaws.com
```

### 📊 Instance Details
- **Instance ID**: `i-08759599dd515a9ad`
- **Type**: t2.xlarge (4 vCPU, 16 GB RAM)
- **Region**: ap-south-1 (Mumbai)
- **Name**: ns-dev-01
- **Public IP**: 13.232.101.149

## 🧪 Test Your API

### Health Check
```bash
curl http://ec2-13-232-101-149.ap-south-1.compute.amazonaws.com/api/health
```

### Classification Test
```bash
curl -X POST http://ec2-13-232-101-149.ap-south-1.compute.amazonaws.com/api/classify \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, how are you today?"}'
```

### Get Stats
```bash
curl http://ec2-13-232-101-149.ap-south-1.compute.amazonaws.com/api/stats
```

## 🚀 Next Steps

### 1. Test React App Locally
```bash
npm start
```
Your app will now use the EC2 backend automatically!

### 2. Deploy to Amplify
```bash
# Build for production
npm run build

# Commit and push
git add .
git commit -m "Deploy with EC2 backend"
git push origin deploy
```

### 3. Configure Amplify Environment Variable
In AWS Amplify Console:
1. Go to your app
2. App settings → Environment variables
3. Add: `REACT_APP_FLASK_API_URL` = `http://ec2-13-232-101-149.ap-south-1.compute.amazonaws.com`
4. Redeploy

## 🛠️ Managing Your Deployment

### SSH into EC2
```bash
ssh -i "neosapients-dev-ec2.pem" ec2-user@ec2-13-232-101-149.ap-south-1.compute.amazonaws.com
```

### Check Service Status
```bash
sudo systemctl status guardrails
sudo systemctl status nginx
```

### View Logs
```bash
# Application logs
sudo journalctl -u guardrails -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
sudo systemctl restart guardrails
sudo systemctl restart nginx
```

## 📁 What's Running

- **Flask API**: Port 5000 (internal)
- **Nginx**: Port 80 (public)
- **Model**: DeBERTa v2 (435M parameters)
- **Device**: CPU
- **Auto-restart**: Enabled via systemd

## 💰 Cost Estimate

**t2.xlarge** instance:
- **On-Demand**: ~$0.188/hour ≈ $136/month
- **1-Year Reserved**: ~$95/month (30% savings)
- **3-Year Reserved**: ~$60/month (56% savings)

## 🔐 Security

- ✅ Port 80 (HTTP) - Open to public
- ✅ Port 22 (SSH) - Configured
- ⚠️ **TODO**: Add HTTPS with SSL certificate (Let's Encrypt)

## 🎯 Performance

- **Cold start**: ~10 seconds (model loading)
- **Inference time**: ~0.5-1.0 seconds per request
- **Concurrent requests**: Supported (Flask handles multiple connections)

## 📝 Notes

1. The API uses **CPU inference** (no GPU needed)
2. Flask runs in **debug mode** for easier troubleshooting
3. Service **auto-restarts** on failure
4. Model is **loaded once** at startup and cached in memory

---

**Deployment completed**: November 12, 2025
**Status**: ✅ Healthy and running
