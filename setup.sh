#!/bin/sh

# Upgrade pip
python -m pip install --upgrade pip

# Install required packages
pip install -r requirements.txt

# Install SSL certificates
python -m certifi