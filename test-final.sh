#!/bin/bash

NODE_IP="54.152.194.43"
PROXY_PORT="30081"

echo "=== Final Connectivity Test ==="
echo "Frontend with Proxy: http://$NODE_IP:$PROXY_PORT"
echo "API through Proxy: http://$NODE_IP:$PROXY_PORT/api/health"
echo

echo "Testing API through proxy:"
curl -s http://$NODE_IP:$PROXY_PORT/api/health
echo

echo "Testing frontend:"
curl -s http://$NODE_IP:$PROXY_PORT/ | grep -o '<title>.*</title>'
echo

echo "✅ Setup Complete!"
echo "Access your application at: http://$NODE_IP:$PROXY_PORT"
