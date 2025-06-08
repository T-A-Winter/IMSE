#!/bin/bash

# Start the MariaDB service
echo "Starting MariaDB service..."
sudo systemctl start mariadb

# Check if it started successfully
if systemctl is-active --quiet mariadb; then
    echo "✅ MariaDB is running."
else
    echo "❌ Failed to start MariaDB."
    exit 1
fi

# Open the MariaDB shell
echo "Opening MariaDB shell..."
sudo mariadb
