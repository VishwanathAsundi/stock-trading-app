#!/usr/bin/env python3
"""
AI Stock Trading Platform - Main Entry Point

This is the main entry point for the AI-powered stock trading application.
You can run different components of the system from here.

Usage:
    python main.py --mode api          # Run FastAPI server
    python main.py --mode trading     # Run trading engine only
    python main.py --mode frontend    # Run Streamlit frontend
    python main.py --mode all         # Run everything
"""

import argparse
import asyncio
import subprocess
import sys
import os
from multiprocessing import Process
import uvicorn

def run_api_server():
    """Run the FastAPI server"""
    print("🚀 Starting FastAPI server...")
    from api.main import app
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)

def run_trading_engine():
    """Run the trading engine"""
    print("🤖 Starting AI Trading Engine...")
    import asyncio
    from trading_engine import trading_engine
    
    async def start_engine():
        await trading_engine.start_trading()
    
    try:
        asyncio.run(start_engine())
    except KeyboardInterrupt:
        print("\n🛑 Trading engine stopped by user")

def run_streamlit_frontend():
    """Run the Streamlit frontend"""
    print("🎯 Starting Streamlit frontend...")
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", 
        "frontend/app.py", "--server.port=8501"
    ])

def setup_environment():
    """Setup the environment and install dependencies"""
    print("🔧 Setting up environment...")
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("📝 Creating .env file...")
        with open('.env', 'w') as f:
            f.write("""# AI Trading Platform Configuration
GEMINI_API_KEY=your_gemini_api_key_here
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key_here
REDIS_URL=redis://localhost:6379
DATABASE_URL=sqlite:///./trading_app.db
SECRET_KEY=your_secret_key_here
RISK_TOLERANCE=medium
MAX_POSITION_SIZE=0.1
TRADING_MODE=paper
""")
        print("✅ Created .env file. Please update with your API keys.")
    
    # Initialize database
    print("🗄️ Initializing database...")
    from models.database import create_tables
    create_tables()
    print("✅ Database initialized")

def main():
    parser = argparse.ArgumentParser(description="AI Stock Trading Platform")
    parser.add_argument(
        "--mode", 
        choices=["api", "trading", "frontend", "all", "setup"],
        default="setup",
        help="Mode to run the application"
    )
    
    args = parser.parse_args()
    
    if args.mode == "setup":
        setup_environment()
        print("\n🎉 Setup complete! You can now run:")
        print("  python main.py --mode api          # API server")
        print("  python main.py --mode frontend     # Web interface")
        print("  python main.py --mode trading      # Trading engine")
        print("  python main.py --mode all          # Everything")
        return
    
    if args.mode == "api":
        run_api_server()
    
    elif args.mode == "trading":
        run_trading_engine()
    
    elif args.mode == "frontend":
        run_streamlit_frontend()
    
    elif args.mode == "all":
        print("🚀 Starting all components...")
        
        # Start API server in a separate process
        api_process = Process(target=run_api_server)
        api_process.start()
        
        # Start Streamlit frontend in a separate process
        frontend_process = Process(target=run_streamlit_frontend)
        frontend_process.start()
        
        try:
            # Run trading engine in main process
            run_trading_engine()
        except KeyboardInterrupt:
            print("\n🛑 Shutting down all components...")
            api_process.terminate()
            frontend_process.terminate()
            api_process.join()
            frontend_process.join()
            print("✅ All components stopped")

if __name__ == "__main__":
    # Print banner
    print("""
🤖 AI Stock Trading Platform
=============================
Advanced AI-powered stock trading with multiple intelligent agents

Features:
  📊 Real-time market data analysis
  🧠 Multiple AI trading agents
  ⚠️ Risk management system
  💼 Portfolio management
  📈 Interactive web dashboard
  🔄 Automated trading engine

""")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1) 