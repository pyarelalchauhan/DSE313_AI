#!/bin/bash

# DSE313 AI Course - Environment Setup Script

# Create virtual environment with Python 3.10
echo "Creating virtual environment 'dse313_venv' with Python 3.10..."
uv venv dse313_venv --python 3.10

# Activate the virtual environment
echo "Activating virtual environment..."
source dse313_venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
uv pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
uv pip install -r requirements.txt

# Force reinstall ipykernel
echo "Reinstalling ipykernel..."
uv pip install ipykernel -U --force-reinstall

# Install Jupyter kernel
echo "Installing Jupyter kernel 'dse313'..."
uv run ipython kernel install --user --name=dse313 --display-name="DSE313 AI"

echo ""
echo "Setup complete!"
echo "To activate the environment, run: source dse313_venv/bin/activate"
