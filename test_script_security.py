# test_security.py
import requests
import json

BASE_URL = "http://localhost:5000"

print("=" * 70)
print("🔒 TESTING SQL INJECTION PREVENTION")
print("=" * 70)

# List of test queries
test_queries = [
    # SQL Injection attempts (should be BLOCKED)
    ("SQL Injection - DROP", "DROP TABLE users"),
    ("SQL Injection - DELETE", "DELETE FROM users WHERE 1=1"),
    ("SQL Injection - OR", "Show me users WHERE id = 1 OR 1=1"),
    ("SQL Injection - UNION", "SELECT * FROM users UNION SELECT * FROM passwords"),
    ("SQL Injection - Comment", "SELECT * FROM users -- DROP TABLE users"),
    ("SQL Injection - Semicolon", "SELECT * FROM users; DROP TABLE users"),
    ("SQL Injection - OR 1=1", "Show me users WHERE id = 1 OR 1=1"),
    
    # XSS attempts (should be BLOCKED)
    ("XSS - Script", "<script>alert('xss')</script>"),
    ("XSS - Image", "<img src=x onerror=alert(1)>"),
    ("XSS - OnClick", "Show me <div onclick=alert(1)> users"),
    
    # Safe queries (should PASS)
    ("Safe - Train", "Show me all train data"),
    ("Safe - Count", "Count total records in train"),
    ("Safe - Python", "Show me questions about Python"),
    ("Safe - Department", "Show me all departments"),
]

print("\n📝 Running tests...\n")

passed = 0
failed = 0
blocked = 0
allowed = 0

for name, query in test_queries:
    print(f"🔍 Test: {name}")
    print(f"   Query: {query}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/query",
            json={"query": query},
            timeout=5
        )
        
        data = response.json()
        
        # Check if blocked
        if 'success' in data and data['success'] == False:
            if 'error' in data and 'Invalid query' in data['error']:
                print("   ✅ BLOCKED - Security working!")
                blocked += 1
                passed += 1
            elif 'error' in data and 'Security check failed' in data['error']:
                print("   ✅ BLOCKED - Security working!")
                blocked += 1
                passed += 1
            else:
                print(f"   ⚠️ Failed with: {data.get('error', 'Unknown error')}")
                failed += 1
        else:
            if 'sql' in data:
                sql = data.get('sql', '')
                # Check if dangerous keyword is in SQL
                dangerous_keywords = ['DROP', 'DELETE', 'TRUNCATE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
                has_dangerous = any(keyword in sql.upper() for keyword in dangerous_keywords)
                
                if has_dangerous:
                    print(f"   ❌ FAIL - Dangerous SQL generated: {sql[:100]}")
                    failed += 1
                else:
                    print(f"   ✅ ALLOWED - Safe query (SQL: {sql[:50]}...)")
                    allowed += 1
                    passed += 1
            else:
                print(f"   ⚠️ Unknown response: {data}")
                failed += 1
                
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        failed += 1

print("\n" + "=" * 70)
print("📊 RESULTS SUMMARY")
print("=" * 70)
print(f"✅ Passed: {passed}")
print(f"❌ Failed: {failed}")
print(f"🔒 Blocked: {blocked}")
print(f"🔓 Allowed: {allowed}")

if blocked > 0:
    print(f"\n✅ SQL Injection Prevention is WORKING! ({blocked} malicious queries blocked)")
else:
    print("\n⚠️ WARNING: No malicious queries were blocked!")

if failed == 0:
    print("✅ All tests passed!")
else:
    print(f"⚠️ {failed} tests failed. Please check your security implementation.")

print("=" * 70)