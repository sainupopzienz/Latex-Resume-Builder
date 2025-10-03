#!/bin/bash

echo "=== Kubernetes Connectivity Test ==="
echo

# Get node IP
NODE_IP=$(kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}')
echo "Node External IP: $NODE_IP"
echo

# Test backend health
echo "Testing Backend Health..."
kubectl exec deployment/resume-builder-backend -- curl -s http://localhost:5000/api/health
echo

# Test internal service connectivity
echo "Testing Internal Service Connectivity..."
kubectl exec deployment/resume-builder-frontend -- curl -s http://resume-builder-backend-service:5000/api/health
echo

# Test external access
echo "Testing External Access..."
echo "Frontend: http://$NODE_IP:30089"
echo "Backend: http://$NODE_IP:30090/api/health"
curl -s http://$NODE_IP:30090/api/health
echo

# Check current services
echo "Current Services:"
kubectl get services
echo

# Check pods status
echo "Current Pods:"
kubectl get pods
