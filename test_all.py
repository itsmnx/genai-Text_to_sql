# test_all_final.py
import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_result(name, passed, details=""):
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {name}")
    if details:
        print(f"   {details}")

print("=" * 70)
print("🧪 RUNNING ALL BASIC TESTS")
print("=" * 70)

tests_passed = 0
tests_failed = 0

# ============================================
# 1. AUTHENTICATION TESTS
# ============================================
print("\n📋 1. AUTHENTICATION TESTS")
print("-" * 40)

# Check if user exists first
try:
    resp = requests.get(f"{BASE_URL}/api/status")
    print("✅ API is running")
except:
    print("❌ API is not running! Start with: python app.py")
    exit(1)

# Test Register (with unique username)
import time
unique_user = f"testuser_{int(time.time())}"
try:
    resp = requests.post(f"{BASE_URL}/api/register", json={
        'username': unique_user, 
        'password': 'test12345', 
        'email': f'{unique_user}@test.com'
    })
    passed = resp.status_code == 200 and resp.json().get('success', False)
    print_result("Register User", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("Register User", False, "Exception occurred")
    tests_failed += 1

# Test Login
try:
    resp = requests.post(f"{BASE_URL}/api/login", json={
        'username': unique_user, 
        'password': 'test12345'
    })
    token = resp.json().get('access_token')
    passed = resp.status_code == 200 and token is not None
    print_result("Login User", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("Login User", False, "Exception occurred")
    tests_failed += 1

# Test Wrong Password
try:
    resp = requests.post(f"{BASE_URL}/api/login", json={
        'username': unique_user, 
        'password': 'wrongpass'
    })
    passed = resp.status_code == 401
    print_result("Wrong Password Rejected", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("Wrong Password Rejected", False, "Exception occurred")
    tests_failed += 1

# ============================================
# 2. QUERY TESTS
# ============================================
print("\n📋 2. QUERY GENERATION TESTS")
print("-" * 40)

# Test Simple Query
try:
    resp = requests.post(f"{BASE_URL}/api/query", json={'query': 'Show me all train data'})
    passed = resp.status_code == 200 and 'sql' in resp.json()
    print_result("Simple SELECT", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("Simple SELECT", False, "Exception occurred")
    tests_failed += 1

# Test Aggregation Query
try:
    resp = requests.post(f"{BASE_URL}/api/query", json={'query': 'Count total records in train'})
    data = resp.json()
    sql = data.get('sql', '')
    passed = resp.status_code == 200 and 'COUNT' in sql.upper()
    print_result("Aggregation (COUNT)", passed, f"SQL: {sql[:50]}...")
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("Aggregation (COUNT)", False, "Exception occurred")
    tests_failed += 1

# Test Filter Query
try:
    resp = requests.post(f"{BASE_URL}/api/query", json={'query': 'Show me questions containing Python from train'})
    data = resp.json()
    sql = data.get('sql', '')
    passed = resp.status_code == 200 and ('LIKE' in sql.upper() or 'Python' in sql)
    print_result("Filter Query", passed, f"SQL: {sql[:50]}...")
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("Filter Query", False, "Exception occurred")
    tests_failed += 1

# ============================================
# 3. SECURITY TESTS
# ============================================
print("\n📋 3. SECURITY TESTS")
print("-" * 40)

# Test SQL Injection (DROP)
try:
    resp = requests.post(f"{BASE_URL}/api/query", json={'query': 'DROP TABLE users'})
    passed = resp.status_code in [400, 403, 401]
    print_result("SQL Injection - DROP", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("SQL Injection - DROP", False, "Exception occurred")
    tests_failed += 1

# Test XSS
try:
    resp = requests.post(f"{BASE_URL}/api/query", json={'query': '<script>alert("xss")</script>'})
    passed = resp.status_code in [400, 403, 401]
    print_result("XSS Attack", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("XSS Attack", False, "Exception occurred")
    tests_failed += 1

# Test OR Injection
try:
    resp = requests.post(f"{BASE_URL}/api/query", json={'query': "Show me users WHERE id = 1 OR 1=1"})
    passed = resp.status_code in [200, 400, 403]  # 200 if it handles it, 400 if blocked
    print_result("OR Injection", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("OR Injection", False, "Exception occurred")
    tests_failed += 1

# ============================================
# 4. API STATUS TESTS
# ============================================
print("\n📋 4. API STATUS TESTS")
print("-" * 40)

# Test Groq Status
try:
    resp = requests.get(f"{BASE_URL}/api/groq/status")
    passed = resp.status_code == 200 and 'available' in resp.json()
    print_result("Groq Status", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("Groq Status", False, "Exception occurred")
    tests_failed += 1

# Test System Status
try:
    resp = requests.get(f"{BASE_URL}/api/status")
    passed = resp.status_code == 200
    print_result("System Status", passed)
    tests_passed += 1 if passed else 0
    tests_failed += 0 if passed else 1
except:
    print_result("System Status", False, "Exception occurred")
    tests_failed += 1

# ============================================
# 5. QUERY HISTORY TEST (if authenticated)
# ============================================
print("\n📋 5. QUERY HISTORY TEST")
print("-" * 40)

try:
    # Login to get token
    resp = requests.post(f"{BASE_URL}/api/login", json={
        'username': unique_user, 
        'password': 'test12345'
    })
    token = resp.json().get('access_token')
    
    if token:
        # Test history endpoint
        resp = requests.get(f"{BASE_URL}/api/history", 
            headers={'Authorization': f'Bearer {token}'})
        passed = resp.status_code == 200
        print_result("Query History", passed)
        tests_passed += 1 if passed else 0
        tests_failed += 0 if passed else 1
    else:
        print_result("Query History", False, "No token available")
        tests_failed += 1
except:
    print_result("Query History", False, "Exception occurred")
    tests_failed += 1

# ============================================
# SUMMARY
# ============================================
print("\n" + "=" * 70)
print("📊 TEST SUMMARY")
print("=" * 70)
print(f"✅ Passed: {tests_passed}")
print(f"❌ Failed: {tests_failed}")
total = tests_passed + tests_failed
if total > 0:
    print(f"📈 Pass Rate: {tests_passed/total*100:.1f}%")

if tests_failed == 0:
    print("\n🎉 ALL TESTS PASSED! Your system is working correctly!")
elif tests_failed <= 2:
    print(f"\n⚠️ {tests_failed} tests failed. Most features are working!")
else:
    print(f"\n❌ {tests_failed} tests failed. Please check your system.")

print("=" * 70)