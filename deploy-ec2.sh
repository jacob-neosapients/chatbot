#!/bin/bash

# Quick EC2 Deployment Script for Guardrails ML API
# This script will set up everything on your EC2 instance

set -e

echo "=================================="
echo "EC2 Deployment for Guardrails ML"
echo "=================================="

# Check if EC2_HOST is provided
if [ -z "$1" ]; then
    echo "Usage: ./deploy-ec2.sh <EC2_PUBLIC_IP_OR_DNS>"
    echo "Example: ./deploy-ec2.sh ec2-13-232-xxx-xxx.ap-south-1.compute.amazonaws.com"
    exit 1
fi

EC2_HOST=$1
EC2_USER="ubuntu"
KEY_FILE="neosapients-dev-ec2.pem"

echo "Deploying to: $EC2_HOST"
echo ""

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "Error: SSH key file '$KEY_FILE' not found!"
    echo "Please place your EC2 key file in this directory."
    exit 1
fi

# Set correct permissions
chmod 400 "$KEY_FILE"

# Create deployment package
echo "📦 Creating deployment package..."
tar -czf app-package.tar.gz \
    app.py \
    requirements.txt \
    rm_guardrail_model/ \
    --exclude='__pycache__' \
    --exclude='*.pyc'

echo "✅ Package created"
echo ""

# Copy files to EC2
echo "📤 Uploading files to EC2..."
scp -i "$KEY_FILE" -o StrictHostKeyChecking=no app-package.tar.gz "$EC2_USER@$EC2_HOST:~/"

echo "✅ Files uploaded"
echo ""

# Setup script to run on EC2
echo "🚀 Setting up EC2 instance..."
ssh -i "$KEY_FILE" -o StrictHostKeyChecking=no "$EC2_USER@$EC2_HOST" << 'ENDSSH'
set -e

echo "Installing system dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx

echo "Creating application directory..."
mkdir -p ~/guardrails-app
cd ~/guardrails-app

echo "Extracting application..."
tar -xzf ~/app-package.tar.gz
rm ~/app-package.tar.gz

echo "Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Testing Flask app..."
python3 app.py &
APP_PID=$!
sleep 5

# Test if app is running
if curl -s http://localhost:5000/health > /dev/null; then
    echo "✅ Flask app is running!"
    kill $APP_PID
else
    echo "❌ Flask app failed to start"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

echo "Creating systemd service..."
sudo tee /etc/systemd/system/guardrails.service > /dev/null << 'EOF'
[Unit]
Description=Guardrails ML API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/guardrails-app
Environment="PATH=/home/ubuntu/guardrails-app/venv/bin"
ExecStart=/home/ubuntu/guardrails-app/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/guardrails > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;

    # CORS headers
    add_header 'Access-Control-Allow-Origin' '*' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    add_header 'Access-Control-Allow-Headers' 'Content-Type' always;

    location / {
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*';
            add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS';
            add_header 'Access-Control-Allow-Headers' 'Content-Type';
            add_header 'Content-Length' 0;
            return 204;
        }

        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        
        # Longer timeouts for ML inference
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/guardrails /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable guardrails
sudo systemctl start guardrails
sudo systemctl restart nginx

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Testing API endpoint..."
sleep 3

if curl -s http://localhost/health | grep -q "healthy"; then
    echo "✅ API is responding correctly!"
else
    echo "⚠️  API might still be starting up. Check logs with:"
    echo "   sudo journalctl -u guardrails -f"
fi

ENDSSH

# Clean up local package
rm app-package.tar.gz

echo ""
echo "=================================="
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "=================================="
echo ""
echo "Your API is now running at: http://$EC2_HOST"
echo ""
echo "Test it with:"
echo "  curl http://$EC2_HOST/health"
echo ""
echo "To check logs:"
echo "  ssh -i $KEY_FILE $EC2_USER@$EC2_HOST"
echo "  sudo journalctl -u guardrails -f"
echo ""
echo "Next step: Update your React app to use this URL"
echo "  export REACT_APP_FLASK_API_URL=http://$EC2_HOST"
echo ""
