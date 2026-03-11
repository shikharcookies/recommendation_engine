#!/bin/bash

echo "Starting Counterparty Recommendation Engine Frontend..."
echo ""
echo "Make sure you have:"
echo "1. Installed Node.js 18+"
echo "2. Installed Angular CLI: npm install -g @angular/cli"
echo "3. Installed dependencies: cd counterparty-ui && npm install"
echo ""
echo "Starting frontend at http://localhost:4200"
echo ""

cd counterparty-ui
npm start
