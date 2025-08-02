#!/usr/bin/env python3
import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    requirements = [
        'flask',
        'twilio',
        'requests',
        'python-dotenv'
    ]
    
    for req in requirements:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', req])

if __name__ == "__main__":
    install_requirements()
    print("✅ Setup complete! Don't forget to configure your .env file.")
