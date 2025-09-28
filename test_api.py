#!/usr/bin/env python3
"""Test script for the Multimodal Content Generator API."""

import requests
import json
import time
import sys

API_BASE = "http://localhost:8000"

def test_health():
    """Test API health endpoint."""
    print("Testing API health...")
    try:
        response = requests.get(f"{API_BASE}/")
        if response.status_code == 200:
            print("✅ API is healthy")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check failed: {e}")
        return False

def test_generate():
    """Test content generation endpoint."""
    print("\nTesting content generation...")
    
    payload = {
        "title": "Summer Sale 2024",
        "brief": "50% off all items, limited time offer",
        "brand_profile_id": "demo",
        "channels": ["email", "instagram", "facebook"]
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Content generation initiated")
            print(f"Job ID: {result['job_id']}")
            print(f"Status: {result['status']}")
            print(f"Progress: {result['progress']}%")
            return result['job_id']
        else:
            print(f"❌ Content generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Content generation failed: {e}")
        return None

def test_job_status(job_id):
    """Test job status endpoint."""
    print(f"\nTesting job status for {job_id}...")
    
    try:
        response = requests.get(f"{API_BASE}/jobs/{job_id}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Job status retrieved")
            print(f"Status: {result['status']}")
            print(f"Progress: {result['progress']}%")
            
            if result['result']:
                print("\n📄 Generated Content:")
                if 'copy' in result['result']:
                    print("Copy:")
                    for i, copy in enumerate(result['result']['copy']):
                        print(f"  {i+1}. {copy[:100]}...")
                
                if 'images' in result['result']:
                    print("\nImages:")
                    for i, image in enumerate(result['result']['images']):
                        print(f"  {i+1}. {image}")
                
                if 'meta' in result['result'] and 'score' in result['result']['meta']:
                    score = result['result']['meta']['score']
                    print(f"\n📊 Content Score: {score}")
            
            return result
        else:
            print(f"❌ Job status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Job status check failed: {e}")
        return None

def test_with_different_brands():
    """Test with different brand profiles."""
    print("\nTesting with different brand profiles...")
    
    brands = [
        {
            "title": "Tech Innovation",
            "brief": "Revolutionary AI-powered solution",
            "brand_profile_id": "tech_startup",
            "channels": ["twitter", "linkedin"]
        },
        {
            "title": "Fashion Week",
            "brief": "New collection launch",
            "brand_profile_id": "fashion_brand",
            "channels": ["instagram", "facebook"]
        }
    ]
    
    for i, brand in enumerate(brands, 1):
        print(f"\n--- Test {i}: {brand['brand_profile_id']} ---")
        
        try:
            response = requests.post(
                f"{API_BASE}/generate",
                json=brand,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Generated content for {brand['brand_profile_id']}")
                
                # Wait a moment and check status
                time.sleep(2)
                job_result = test_job_status(result['job_id'])
                if job_result and job_result['result']:
                    print(f"Brand-specific content generated successfully")
            else:
                print(f"❌ Failed to generate content for {brand['brand_profile_id']}")
        except Exception as e:
            print(f"❌ Error testing {brand['brand_profile_id']}: {e}")

def main():
    """Run all tests."""
    print("🚀 Starting Multimodal Content Generator API Tests")
    print("=" * 50)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ API is not running. Please start the server with:")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    
    # Test 2: Basic content generation
    job_id = test_generate()
    if not job_id:
        print("\n❌ Content generation failed. Exiting.")
        sys.exit(1)
    
    # Test 3: Check job status
    time.sleep(2)  # Wait for processing
    job_result = test_job_status(job_id)
    
    # Test 4: Different brand profiles
    test_with_different_brands()
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    
    if job_result and job_result.get('result'):
        print("\n📋 Summary:")
        print(f"- Generated {len(job_result['result'].get('copy', []))} copy variations")
        print(f"- Generated {len(job_result['result'].get('images', []))} images")
        if 'meta' in job_result['result'] and 'score' in job_result['result']['meta']:
            score = job_result['result']['meta']['score']
            print(f"- Content quality score: {score.get('overall_score', 'N/A')}")

if __name__ == "__main__":
    main()
