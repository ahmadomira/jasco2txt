#!/bin/bash

# Build script for Jasco2TXT Converter
# This script builds the application using PyInstaller

echo "Building Jasco2TXT Converter..."

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo "PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build the application
echo "Building executable..."
pyinstaller --clean -y --distpath ./dist --workpath ./build jasco2txt_gui.spec

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✓ Build successful!"
    echo "Executable location: ./dist/"
    
    # List the contents of dist directory
    echo "Built files:"
    ls -la ./dist/
    
    # For macOS, show the app bundle
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macOS app bundle created: ./dist/Jasco2TXT-Converter.app"
    fi
else
    echo "✗ Build failed!"
    exit 1
fi

echo "Build complete!"
