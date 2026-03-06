"""
Load Testing for Welcome Link API
Simple performance tests using Python requests
"""
import asyncio
import time
import statistics
import sys
sys.path.insert(0, '..')

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("Install requests: pip install requests")

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False
    print("Install aiohttp: pip install aiohttp")

# Configuration
BASE_URL = "https://api.welcome-link.de"
CONCURRENT_USERS = 10
REQUESTS_PER_USER = 5


class LoadTestResult:
    """Track load test results"""
    def __init__(self):
        self.response_times = []
        self.success_count = 0
        self.error_count = 0
        self.status_codes = {}
    
    def add_result(self, status_code, response_time, success=True):
        self.response_times.append(response_time)
        self.status_codes[status_code] = self.status_codes.get(status_code, 0) + 1
        if success:
            self.success_count += 1
        else:
            self.error_count += 1
    
    def get_stats(self):
        if not self.response_times:
            return {"error": "No results"}
        
        return {
            "total_requests": len(self.response_times),
            "successful": self.success_count,
            "failed": self.error_count,
            "success_rate": f"{(self.success_count / len(self.response_times)) * 100:.1f}%",
            "avg_response_time": f"{statistics.mean(self.response_times):.0f}ms",
            "min_response_time": f"{min(self.response_times):.0f}ms",
            "max_response_time": f"{max(self.response_times):.0f}ms",
            "p50": f"{statistics.median(self.response_times):.0f}ms",
            "p95": f"{sorted(self.response_times)[int(len(self.response_times) * 0.95)]:.0f}ms" if len(self.response_times) > 20 else "N/A",
            "status_codes": self.status_codes
        }


def test_health_endpoint():
    """Test basic health endpoint"""
    print("\n=== Testing Health Endpoint ===")
    result = LoadTestResult()
    
    for i in range(10):
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/", timeout=10)
            elapsed = (time.time() - start) * 1000
            result.add_result(response.status_code, elapsed, response.status_code == 200)
            print(f"  Request {i+1}: {response.status_code} in {elapsed:.0f}ms")
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            result.add_result(0, elapsed, False)
            print(f"  Request {i+1}: ERROR - {str(e)[:50]}")
    
    return result


def test_auth_endpoint():
    """Test authentication endpoint"""
    print("\n=== Testing Auth Endpoint ===")
    result = LoadTestResult()
    
    # Test demo login
    for i in range(5):
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "demo@welcome-link.de", "password": "Demo123!"},
                timeout=10
            )
            elapsed = (time.time() - start) * 1000
            result.add_result(response.status_code, elapsed, response.status_code == 200)
            print(f"  Login {i+1}: {response.status_code} in {elapsed:.0f}ms")
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            result.add_result(0, elapsed, False)
            print(f"  Login {i+1}: ERROR - {str(e)[:50]}")
    
    # Test invalid login
    for i in range(5):
        start = time.time()
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": "invalid@test.com", "password": "wrong"},
                timeout=10
            )
            elapsed = (time.time() - start) * 1000
            result.add_result(response.status_code, elapsed, True)  # 401 is expected
            print(f"  Invalid login {i+1}: {response.status_code} in {elapsed:.0f}ms")
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            result.add_result(0, elapsed, False)
            print(f"  Invalid login {i+1}: ERROR - {str(e)[:50]}")
    
    return result


def test_guestview_endpoint():
    """Test guestview endpoint"""
    print("\n=== Testing Guestview Endpoint ===")
    result = LoadTestResult()
    
    # Valid token
    tokens = ["QEJHEXP1QF", "TEST123"]
    
    for i in range(10):
        start = time.time()
        try:
            response = requests.get(
                f"{BASE_URL}/api/guestview/{tokens[i % len(tokens)]}",
                timeout=10
            )
            elapsed = (time.time() - start) * 1000
            result.add_result(response.status_code, elapsed, response.status_code in [200, 404])
            print(f"  Guestview {i+1}: {response.status_code} in {elapsed:.0f}ms")
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            result.add_result(0, elapsed, False)
            print(f"  Guestview {i+1}: ERROR - {str(e)[:50]}")
    
    return result


def test_concurrent_requests():
    """Test concurrent requests"""
    print(f"\n=== Testing Concurrent Requests ({CONCURRENT_USERS} users, {REQUESTS_PER_USER} requests each) ===")
    result = LoadTestResult()
    
    import concurrent.futures
    
    def make_request(user_id, request_id):
        start = time.time()
        try:
            response = requests.get(f"{BASE_URL}/api/", timeout=10)
            elapsed = (time.time() - start) * 1000
            return {"status": response.status_code, "time": elapsed, "success": True}
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return {"status": 0, "time": elapsed, "success": False, "error": str(e)}
    
    start_total = time.time()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        futures = []
        for user in range(CONCURRENT_USERS):
            for req in range(REQUESTS_PER_USER):
                futures.append(executor.submit(make_request, user, req))
        
        for i, future in enumerate(concurrent.futures.as_completed(futures)):
            res = future.result()
            result.add_result(res["status"], res["time"], res["success"])
            print(f"  Request {i+1}: {res['status']} in {res['time']:.0f}ms")
    
    total_time = (time.time() - start_total) * 1000
    result.total_time = total_time
    
    return result


def print_summary(results):
    """Print test summary"""
    print("\n" + "=" * 60)
    print("LOAD TEST SUMMARY")
    print("=" * 60)
    
    total_requests = 0
    total_success = 0
    all_times = []
    
    for name, result in results.items():
        stats = result.get_stats()
        print(f"\n{name}:")
        print(f"  Total: {stats.get('total_requests', 0)}")
        print(f"  Success: {stats.get('successful', 0)} ({stats.get('success_rate', 'N/A')})")
        print(f"  Failed: {stats.get('failed', 0)}")
        print(f"  Avg Time: {stats.get('avg_response_time', 'N/A')}")
        print(f"  Min Time: {stats.get('min_response_time', 'N/A')}")
        print(f"  Max Time: {stats.get('max_response_time', 'N/A')}")
        print(f"  P50: {stats.get('p50', 'N/A')}")
        print(f"  P95: {stats.get('p95', 'N/A')}")
        print(f"  Status Codes: {stats.get('status_codes', {})}")
        
        total_requests += stats.get('total_requests', 0)
        total_success += stats.get('successful', 0)
        all_times.extend(result.response_times)
    
    print("\n" + "-" * 60)
    print(f"OVERALL: {total_requests} requests, {total_success} successful")
    if all_times:
        print(f"Avg Response Time: {statistics.mean(all_times):.0f}ms")
        print(f"Median Response Time: {statistics.median(all_times):.0f}ms")
    print("=" * 60)


def main():
    """Run all load tests"""
    if not HAS_REQUESTS:
        print("Error: requests library not installed")
        print("Run: pip install requests")
        return
    
    print("=" * 60)
    print("Welcome Link API - Load Testing")
    print(f"Target: {BASE_URL}")
    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    results = {}
    
    # Run tests
    results["Health Endpoint"] = test_health_endpoint()
    results["Auth Endpoint"] = test_auth_endpoint()
    results["Guestview Endpoint"] = test_guestview_endpoint()
    results["Concurrent Requests"] = test_concurrent_requests()
    
    # Print summary
    print_summary(results)
    
    # Performance assessment
    print("\n" + "=" * 60)
    print("PERFORMANCE ASSESSMENT")
    print("=" * 60)
    
    health_avg = statistics.mean(results["Health Endpoint"].response_times) if results["Health Endpoint"].response_times else 0
    
    if health_avg < 500:
        print("✅ Health Endpoint: EXCELLENT (<500ms)")
    elif health_avg < 1000:
        print("✅ Health Endpoint: GOOD (<1s)")
    elif health_avg < 2000:
        print("⚠️  Health Endpoint: ACCEPTABLE (<2s)")
    else:
        print("❌ Health Endpoint: SLOW (>2s)")
    
    concurrent_avg = statistics.mean(results["Concurrent Requests"].response_times) if results["Concurrent Requests"].response_times else 0
    
    if concurrent_avg < 1000:
        print("✅ Concurrent Requests: GOOD (<1s average)")
    elif concurrent_avg < 2000:
        print("⚠️  Concurrent Requests: ACCEPTABLE (<2s)")
    else:
        print("❌ Concurrent Requests: SLOW (>2s)")
    
    success_rate = results["Concurrent Requests"].success_count / max(len(results["Concurrent Requests"].response_times), 1) * 100
    
    if success_rate >= 99:
        print(f"✅ Success Rate: {success_rate:.1f}% (EXCELLENT)")
    elif success_rate >= 95:
        print(f"✅ Success Rate: {success_rate:.1f}% (GOOD)")
    elif success_rate >= 90:
        print(f"⚠️  Success Rate: {success_rate:.1f}% (ACCEPTABLE)")
    else:
        print(f"❌ Success Rate: {success_rate:.1f}% (POOR)")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()