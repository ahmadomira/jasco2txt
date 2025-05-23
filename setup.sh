#!/bin/bash

# Setup script for Jasco2TXT Converter
# This script creates the conda environment and installs all necessary packages

echo "Setting up Jasco2TXT Converter environment..."

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Error: Conda is not installed or not in PATH"
    echo "Please install Miniconda or Anaconda first"
    exit 1
fi

# Create conda environment from environment.yml
echo "Creating conda environment 'jasco2txt'..."
conda env create -f environment.yml

# Check if environment creation was successful
if [ $? -eq 0 ]; then
    echo "✓ Environment created successfully!"
else
    echo "✗ Environment creation failed!"
    exit 1
fi

# Activate the environment and install additional packages
echo "Activating environment and installing packages..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate jasco2txt

# Install packages from requirements.txt (in case of any updates)
pip install -r requirements.txt

echo "✓ Setup complete!"
echo ""
echo "To use the environment:"
echo "  conda activate jasco2txt"
echo ""
echo "To run the application:"
echo "  python jasco2txt_gui.py"
echo ""
echo "To build the executable:"
echo "  ./build.sh"
