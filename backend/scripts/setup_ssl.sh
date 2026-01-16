#!/bin/bash
# SSL/HTTPS Setup Script using Let's Encrypt

echo "SSL/HTTPS Setup with Let's Encrypt"
echo "===================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (sudo)"
    exit 1
fi

# Check if domain is provided
if [ -z "$1" ]; then
    echo "Usage: sudo ./setup_ssl.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1
EMAIL=${2:-admin@$DOMAIN}

echo "Domain: $DOMAIN"
echo "Email: $EMAIL"

# Install Certbot
echo "Installing Certbot..."
apt-get update
apt-get install -y certbot python3-certbot-nginx

# Check if Nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "Nginx is not installed. Installing..."
    apt-get install -y nginx
fi

# Backup Nginx config
echo "Backing up Nginx configuration..."
cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup

# Create Nginx config for domain
echo "Creating Nginx configuration..."
cat > /etc/nginx/sites-available/$DOMAIN <<EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test Nginx config
echo "Testing Nginx configuration..."
nginx -t

if [ $? -ne 0 ]; then
    echo "Nginx configuration error!"
    exit 1
fi

# Reload Nginx
systemctl reload nginx

# Obtain SSL certificate
echo "Obtaining SSL certificate..."
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $EMAIL

if [ $? -eq 0 ]; then
    echo "SSL certificate obtained successfully!"

    # Setup auto-renewal
    echo "Setting up auto-renewal..."
    systemctl enable certbot.timer
    systemctl start certbot.timer

    # Test renewal
    certbot renew --dry-run

    echo ""
    echo "SSL setup completed!"
    echo "Your site is now available at:"
    echo "https://$DOMAIN"
    echo ""
    echo "Certificate auto-renewal is configured."
    echo "Certificates will be renewed automatically before expiration."
else
    echo "Error obtaining SSL certificate!"
    exit 1
fi

# Update Django settings reminder
echo ""
echo "Don't forget to update your Django settings:"
echo "1. Set ALLOWED_HOSTS = ['$DOMAIN', 'www.$DOMAIN']"
echo "2. Set SECURE_SSL_REDIRECT = True"
echo "3. Set SESSION_COOKIE_SECURE = True"
echo "4. Set CSRF_COOKIE_SECURE = True"
