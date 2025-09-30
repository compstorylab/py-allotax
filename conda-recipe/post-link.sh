#!/bin/bash

# Post-link script to install Node.js dependencies after conda install
# This runs automatically when the conda package is installed

MESSAGES_FILE="${PREFIX}/.messages.txt"

# Function to log to both stderr (for errors) and .messages.txt
log_message() {
    echo "$1" >> "$MESSAGES_FILE"
}

log_message ""
log_message "==========================================  "
log_message "Installing Node.js dependencies for py-allotax..."
log_message "==========================================  "

# Find the py_allotax package directory with proper glob expansion
shopt -s nullglob
PACKAGE_DIRS=("${PREFIX}"/lib/python*/site-packages/py_allotax)

if [ ${#PACKAGE_DIRS[@]} -eq 0 ]; then
    log_message "⚠ Warning: Could not find py_allotax package directory"
    exit 0
fi

PACKAGE_DIR="${PACKAGE_DIRS[0]}"
log_message "Package directory: $PACKAGE_DIR"

# Navigate to the package directory and run npm install
cd "$PACKAGE_DIR" || {
    log_message "⚠ Error: Could not cd to $PACKAGE_DIR"
    exit 1
}

if [ ! -f "package.json" ]; then
    log_message "⚠ Warning: package.json not found"
    exit 0
fi

log_message "Running npm install..."

# Run npm install and capture output
if npm install --production > /tmp/npm-install.log 2>&1; then
    if [ -d "node_modules" ]; then
        log_message "✓ Node.js dependencies installed successfully!"
        log_message ""
    else
        log_message "⚠ Warning: npm install completed but node_modules not found"
        log_message "  Manual install: cd $PACKAGE_DIR && npm install"
        log_message ""
    fi
else
    log_message "⚠ Error: npm install failed"
    log_message "  See /tmp/npm-install.log for details"
    log_message "  Manual install: cd $PACKAGE_DIR && npm install"
    log_message ""
fi

exit 0
