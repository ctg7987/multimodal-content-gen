#!/usr/bin/env python3
"""Comprehensive test for the full Multimodal Content Generator system."""

import requests
import json
import time
import sys
from typing import Dict, Any

API_BASE = "http://localhost:8000"
FRONTEND_BASE = "http://localhost:3000"

def test_system_health():
    """Test that both backend and frontend are running."""
    print("Testing system health...")
    
    # Test backend
    try:
        backend_response = requests.get(f"{API_BASE}/", timeout=5)
        if backend_response.status_code == 200:
            print("✓ Backend is running")
        else:
            print(f"✗ Backend health check failed: {backend_response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Backend is not running: {e}")
        return False
    
    # Test frontend
    try:
        frontend_response = requests.get(f"{FRONTEND_BASE}/", timeout=5)
        if frontend_response.status_code == 200 and "Multimodal Marketing Content Generator" in frontend_response.text:
            print("✓ Frontend is running")
        else:
            print(f"✗ Frontend health check failed: {frontend_response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Frontend is not running: {e}")
        return False
    
    return True

def test_content_generation_workflow():
    """Test the complete content generation workflow."""
    print("\nTesting content generation workflow...")
    
    test_cases = [
        {
            "name": "Basic Email Campaign",
            "payload": {
                "title": "Black Friday Sale",
                "brief": "50% off everything, limited time offer",
                "brand_profile_id": "demo",
                "channels": ["email"]
            }
        },
        {
            "name": "Multi-Channel Campaign",
            "payload": {
                "title": "Product Launch",
                "brief": "Introducing our revolutionary new product",
                "brand_profile_id": "tech_startup",
                "channels": ["instagram", "facebook", "twitter"]
            }
        },
        {
            "name": "Fashion Brand Campaign",
            "payload": {
                "title": "Spring Collection",
                "brief": "New seasonal fashion line",
                "brand_profile_id": "fashion_brand",
                "channels": ["instagram", "facebook"]
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test_case['name']} ---")
        
        try:
            # Submit generation request
            response = requests.post(
                f"{API_BASE}/generate",
                json=test_case['payload'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✓ Generation initiated: {result['job_id']}")
                
                # Wait for completion
                time.sleep(2)
                
                # Check job status
                status_response = requests.get(f"{API_BASE}/jobs/{result['job_id']}")
                if status_response.status_code == 200:
                    job_result = status_response.json()
                    print(f"✓ Job completed: {job_result['status']}")
                    
                    if job_result['result']:
                        copy_count = len(job_result['result'].get('copy', []))
                        image_count = len(job_result['result'].get('images', []))
                        score = job_result['result'].get('meta', {}).get('score', {})
                        
                        print(f"  Results: {copy_count} copies, {image_count} images")
                        print(f"  Quality Score: {score.get('overall_score', 'N/A')}")
                        
                        results.append({
                            "test_case": test_case['name'],
                            "success": True,
                            "copy_count": copy_count,
                            "image_count": image_count,
                            "score": score.get('overall_score', 0)
                        })
                    else:
                        print("⚠️  No results generated")
                        results.append({
                            "test_case": test_case['name'],
                            "success": False,
                            "error": "No results"
                        })
                else:
                    print(f"❌ Job status check failed: {status_response.status_code}")
                    results.append({
                        "test_case": test_case['name'],
                        "success": False,
                        "error": f"Status check failed: {status_response.status_code}"
                    })
            else:
                print(f"❌ Generation failed: {response.status_code}")
                print(f"Response: {response.text}")
                results.append({
                    "test_case": test_case['name'],
                    "success": False,
                    "error": f"Generation failed: {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Test case failed: {e}")
            results.append({
                "test_case": test_case['name'],
                "success": False,
                "error": str(e)
            })
    
    return results

def test_api_endpoints():
    """Test all API endpoints."""
    print("\n🔌 Testing API endpoints...")
    
    endpoints = [
        ("GET", "/", "Root endpoint"),
        ("GET", "/docs", "API documentation"),
        ("GET", "/openapi.json", "OpenAPI schema")
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
            else:
                response = requests.post(f"{API_BASE}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                print(f"✅ {description}: {response.status_code}")
            else:
                print(f"⚠️  {description}: {response.status_code}")
        except Exception as e:
            print(f"❌ {description}: {e}")

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🛡️  Testing error handling...")
    
    # Test invalid job ID
    try:
        response = requests.get(f"{API_BASE}/jobs/invalid-job-id")
        if response.status_code == 404:
            print("✅ Invalid job ID handled correctly")
        else:
            print(f"⚠️  Invalid job ID response: {response.status_code}")
    except Exception as e:
        print(f"❌ Invalid job ID test failed: {e}")
    
    # Test malformed request
    try:
        response = requests.post(
            f"{API_BASE}/generate",
            json={"invalid": "data"},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code in [400, 422]:
            print("✅ Malformed request handled correctly")
        else:
            print(f"⚠️  Malformed request response: {response.status_code}")
    except Exception as e:
        print(f"❌ Malformed request test failed: {e}")

def generate_test_report(results: list):
    """Generate a comprehensive test report."""
    print("\n" + "="*60)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("="*60)
    
    total_tests = len(results)
    successful_tests = sum(1 for r in results if r['success'])
    failed_tests = total_tests - successful_tests
    
    print(f"📈 Overall Results:")
    print(f"   Total Tests: {total_tests}")
    print(f"   Successful: {successful_tests}")
    print(f"   Failed: {failed_tests}")
    print(f"   Success Rate: {(successful_tests/total_tests)*100:.1f}%")
    
    if successful_tests > 0:
        avg_score = sum(r.get('score', 0) for r in results if r['success']) / successful_tests
        total_copies = sum(r.get('copy_count', 0) for r in results if r['success'])
        total_images = sum(r.get('image_count', 0) for r in results if r['success'])
        
        print(f"\n📊 Content Generation Metrics:")
        print(f"   Average Quality Score: {avg_score:.2f}")
        print(f"   Total Copies Generated: {total_copies}")
        print(f"   Total Images Generated: {total_images}")
    
    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        print(f"   {status} {result['test_case']}")
        if not result['success'] and 'error' in result:
            print(f"      Error: {result['error']}")
    
    print(f"\n🎯 System Status:")
    if successful_tests == total_tests:
        print("   🎉 ALL TESTS PASSED - System is fully operational!")
    elif successful_tests > 0:
        print("   ⚠️  PARTIAL SUCCESS - Some features working")
    else:
        print("   ❌ SYSTEM FAILURE - No tests passed")
    
    return successful_tests == total_tests

def main():
    """Run comprehensive system tests."""
    print("Multimodal Content Generator - Comprehensive System Test")
    print("="*60)
    
    # Test 1: System Health
    if not test_system_health():
        print("\n❌ System health check failed. Please ensure both backend and frontend are running.")
        print("Backend: uvicorn app.main:app --reload")
        print("Frontend: cd web && npm run dev")
        sys.exit(1)
    
    # Test 2: API Endpoints
    test_api_endpoints()
    
    # Test 3: Content Generation Workflow
    results = test_content_generation_workflow()
    
    # Test 4: Error Handling
    test_error_handling()
    
    # Generate Report
    all_passed = generate_test_report(results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 SYSTEM TEST COMPLETED SUCCESSFULLY!")
        print("The Multimodal Content Generator is fully operational.")
    else:
        print("⚠️  SYSTEM TEST COMPLETED WITH ISSUES")
        print("Some features may not be working correctly.")
    
    print("\n📝 Next Steps:")
    print("1. Configure API keys in .env file for full functionality")
    print("2. Access the web interface at http://localhost:3000")
    print("3. Test the API at http://localhost:8000/docs")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
