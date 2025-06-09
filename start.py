#!/usr/bin/env python3
"""
Simple startup script for the AI Stock Trading Platform
"""

import os
import sys
import subprocess

def main():
    print("🤖 AI Stock Trading Platform - Quick Start")
    print("==========================================")
    
    if len(sys.argv) > 1:
        mode = sys.argv[1]
    else:
        print("\nAvailable modes:")
        print("  setup    - Initialize the application")
        print("  api      - Start API server only")
        print("  frontend - Start web interface only") 
        print("  all      - Start everything")
        print()
        mode = input("Choose mode (setup/api/frontend/all): ").strip().lower()
    
    if mode not in ['setup', 'api', 'frontend', 'all']:
        print("Invalid mode. Use: setup, api, frontend, or all")
        return
    
    # Run the main application
    subprocess.run([sys.executable, "main.py", "--mode", mode])

if __name__ == "__main__":
    main() 