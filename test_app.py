#!/usr/bin/env python3
"""
Test script for the AI Stock Trading Platform
"""

import asyncio
import requests
import time

def test_api_server():
    """Test if the API server is responding"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ API Server is running")
            return True
        else:
            print(f"❌ API Server responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Server is not accessible: {e}")
        return False

def test_streamlit():
    """Test if Streamlit is running"""
    try:
        response = requests.get("http://localhost:8501/", timeout=5)
        if response.status_code == 200:
            print("✅ Streamlit Frontend is running")
            return True
        else:
            print(f"❌ Streamlit responded with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Streamlit is not accessible: {e}")
        return False

def test_database():
    """Test database connection"""
    try:
        from models.database import get_db, Portfolio
        db = next(get_db())
        
        # Try to query the database
        portfolios = db.query(Portfolio).all()
        print(f"✅ Database is working (found {len(portfolios)} portfolios)")
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_data_service():
    """Test data service"""
    try:
        from services.data_service import data_service
        
        async def test_async():
            # Test getting stock data
            price_data = await data_service.get_real_time_price("AAPL")
            if price_data and 'price' in price_data:
                print(f"✅ Data Service is working (AAPL price: ${price_data['price']:.2f})")
                return True
            else:
                print("❌ Data Service returned invalid data")
                return False
        
        return asyncio.run(test_async())
    except Exception as e:
        print(f"❌ Data Service error: {e}")
        return False

def test_portfolio_service():
    """Test portfolio service"""
    try:
        from services.portfolio_service import portfolio_service
        
        async def test_async():
            # Test getting portfolio summary
            portfolio = await portfolio_service.get_portfolio_summary()
            if portfolio and 'total_value' in portfolio:
                print(f"✅ Portfolio Service is working (Total value: ${portfolio['total_value']:.2f})")
                return True
            else:
                print("❌ Portfolio Service returned invalid data")
                return False
        
        return asyncio.run(test_async())
    except Exception as e:
        print(f"❌ Portfolio Service error: {e}")
        return False

def test_trading_agents():
    """Test trading agents"""
    try:
        from agents.technical_agent import TechnicalAgent
        from agents.sentiment_agent import SentimentAgent
        
        print("✅ Trading Agents imported successfully")
        
        # Test creating agents
        tech_agent = TechnicalAgent()
        sentiment_agent = SentimentAgent()
        
        print(f"✅ Created agents: {tech_agent.name}, {sentiment_agent.name}")
        return True
    except Exception as e:
        print(f"❌ Trading Agents error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing AI Stock Trading Platform Components\n")
    
    tests = [
        ("Database", test_database),
        ("Portfolio Service", test_portfolio_service),
        ("Data Service", test_data_service),
        ("Trading Agents", test_trading_agents),
        ("API Server", test_api_server),
        ("Streamlit Frontend", test_streamlit),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The application is working correctly.")
        print("\n🚀 You can now access:")
        print("   📊 API Documentation: http://localhost:8000/docs")
        print("   🎯 Web Interface: http://localhost:8501")
    else:
        print("⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main() 