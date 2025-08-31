#!/usr/bin/env python3
"""
Test script for the Recommendation Engine
"""

import requests
import time
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is running")
            return True
        else:
            print("❌ API is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend is running.")
        return False

def test_data_generation():
    """Test data generation"""
    try:
        print("📊 Generating sample data...")
        response = requests.post(f"{BASE_URL}/generate-data")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generated {data['users_created']} users, {data['products_created']} products, {data['purchases_created']} purchases")
            return True
        else:
            print("❌ Failed to generate data")
            return False
    except Exception as e:
        print(f"❌ Error generating data: {e}")
        return False

def test_recommendations():
    """Test recommendation system"""
    try:
        # Get a user
        users_response = requests.get(f"{BASE_URL}/users?limit=1")
        if users_response.status_code != 200:
            print("❌ Cannot get users")
            return False
        
        users = users_response.json()
        if not users:
            print("❌ No users found")
            return False
        
        user_id = users[0]['id']
        print(f"👤 Testing recommendations for user: {users[0]['name']}")
        
        # Get recommendations
        rec_response = requests.get(f"{BASE_URL}/recommendations/{user_id}")
        if rec_response.status_code == 200:
            recommendations = rec_response.json()
            print(f"✅ Got {len(recommendations.get('recommendations', []))} recommendations")
            print(f"📋 Recommendation type: {recommendations.get('recommendation_type', 'unknown')}")
            return True
        else:
            print("❌ Failed to get recommendations")
            return False
    except Exception as e:
        print(f"❌ Error testing recommendations: {e}")
        return False

def test_persona_analysis():
    """Test persona analysis"""
    try:
        # Get a user
        users_response = requests.get(f"{BASE_URL}/users?limit=1")
        if users_response.status_code != 200:
            print("❌ Cannot get users")
            return False
        
        users = users_response.json()
        if not users:
            print("❌ No users found")
            return False
        
        user_id = users[0]['id']
        print(f"🔍 Analyzing persona for user: {users[0]['name']}")
        
        # Analyze persona
        analysis_response = requests.get(f"{BASE_URL}/persona/analyze/{user_id}")
        if analysis_response.status_code == 200:
            analysis = analysis_response.json()
            print(f"✅ Persona analysis complete")
            print(f"   Persona type: {analysis.get('persona_type', 'unknown')}")
            print(f"   Total purchases: {analysis.get('total_purchases', 0)}")
            print(f"   Total spent: ${analysis.get('total_spent', 0):.2f}")
            return True
        else:
            print("❌ Failed to analyze persona")
            return False
    except Exception as e:
        print(f"❌ Error testing persona analysis: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Recommendation Engine System")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        return
    
    # Test 2: Data generation
    if not test_data_generation():
        return
    
    # Wait a moment for data to be processed
    time.sleep(2)
    
    # Test 3: Recommendations
    if not test_recommendations():
        return
    
    # Test 4: Persona analysis
    if not test_persona_analysis():
        return
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed! The system is working correctly.")
    print("\n📱 You can now access:")
    print("   Frontend: http://localhost:3000")
    print("   API Docs: http://localhost:8000/docs")
    print("   MongoDB Express: http://localhost:8081")

if __name__ == "__main__":
    main()
