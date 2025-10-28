import requests
import time
import random
import logging
from datetime import datetime
import re
from bs4 import BeautifulSoup
import os
import sys

# ========================================
# PYTHONANYWHERE CONFIGURATION
# ========================================
# Detect if we're running on PythonAnywhere
IS_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ

# Set appropriate paths
if IS_PYTHONANYWHERE:
    LOG_FILE = "/home/maizan/qatar_refresh/refresh.log"
    print("🚀 Running on PythonAnywhere")
else:
    LOG_FILE = "refresh.log"
    print("💻 Running locally")

# ========================================
# APPLICATION CONFIGURATION
# ========================================
BUMP_URL = "https://www.qatarliving.com/bump/node/46590548"
DESTINATION = "/jobseeker/maizan/it-support"
FULL_BUMP_URL = f"{BUMP_URL}?destination={DESTINATION}"

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121 Safari/537.36",
]

# ========================================
# COOKIES - UPDATE USING THE COOKIE FINDER BELOW
# ========================================
COOKIES = {
    "_gcl_au": "1.1.1685154002.1760987933",
    "_fbp": "fb.1.1760987933585.784645597794972293",
    "qatarliving-sso-token": "10169288",
    "qat": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3d3dy5xYXRhcmxpdmluZy5jb20iLCJhdWQiOiJodHRwczovL3d3dy5xYXRhcmxpdmluZy5jb20iLCJpYXQiOjE3NjEwMjYyNDIsImV4cCI6MTc2MzAxMzQ0MiwidXNlciI6eyJzdGF0dXMiOiIxIiwibGFuZ3VhZ2UiOiIiLCJjcmVhdGVkIjoiMTc1OTY3NDA0MyIsImFjY2VzcyI6IjE3NjA4Nzc2NTMiLCJsb2dpbiI6MTc2MTAyNjI0MiwiaW5pdCI6Iml0c21haXphbkBnbWFpbC5jb20iLCJ0aW1lem9uZSI6bnVsbCwidWlkIjoiMTAxNjkyODgiLCJxbG5leHRfdXNlcl9pZCI6MCwibmFtZSI6Im1haXphbiIsImFsaWFzIjoibWFpemFuIiwiZW1haWwiOiJpdHNtYWl6YW5AZ21haWwuY29tIiwicGhvbmUiOiIrOTc0MzAyNjQ3NjAiLCJwYXRoIjoidXNlci9tYWl6YW4iLCJpbWFnZSI6Imh0dHBzOi8vZmlsZXMucWF0YXJsaXZpbmcuY29tL3VzZXJzLzIwMjUvMTAvMTEvUFJPRjFfMTF6b24ucG5nIiwiaXNfYWRtaW4iOmZhbHNlLCJwZXJtaXNzaW9ucyI6W10sInJvbGVzIjpbInZlcmlmaWVkX3VzZXIiXWSic2hvd3Jvb21faW5mbyI6W10sInN1YnNjcmlwdGlvbiI6bnVsbH19.N9JLLAMzie7d7P5E0Ds1epUOgOU_LfkrXBDUItZOxGI",
    "intercom-device-id-vxga6d2h": "016af7de-9c51-468c-ae17-45881cda3abe",
    "_gid": "GA1.2.2115110935.1761575642",
    "has_js": "1",
    "_gat": "1",
    "_ga_L8G5Y1WPNH": "GS2.1.s1761647270$o17$g1$t1761647271$j59$l0$h0",
    "_ga": "GA1.1.102102702.1760987933",
    "intercom-session-vxga6d2h": "MEhkREl4Y1EyTlh3ckx1eG9kNmptK0dVTSs1by91by8zZ2tLZ0lybmNBRkYyeUdCM2JQWVBhRWdmRjg2bUdzSzNLSCtJdTIyYVZSQ3dZb3J6Y0R4RUw3V3ZxK0FObi9yb1dJS3gxNXNUaUE9LS02MGplTUYzYkdKYVdaaFpFMlM4bnJRPT0"
}

MAX_RETRIES = 3
MAX_WAIT = 15

# ========================================
# LOGGING SETUP
# ========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)  # Also print to console
    ]
)

session = requests.Session()

# ========================================
# COOKIE FINDER - RUN THIS IN BROWSER CONSOLE
# ========================================
COOKIE_FINDER_SCRIPT = """// === QATAR LIVING COOKIE FINDER ===
// 1. Go to https://www.qatarliving.com
// 2. Make sure you're logged in
// 3. Press F12 → Console
// 4. Paste this code and press Enter
// 5. Copy the output below and replace COOKIES above

var cookies = document.cookie.split(';');
console.log('🔐 Found ' + cookies.length + ' cookies:');
console.log('='.repeat(50));

var pythonCode = "COOKIES = {\\n";
cookies.forEach((cookie, index) => {
    var [name, value] = cookie.trim().split('=');
    var displayValue = value ? (value.length > 50 ? value.substring(0, 50) + '...' : value) : '(empty)';
    console.log('📌 ' + name + ' = ' + displayValue);
    pythonCode += '    "' + name + '": "' + (value || '') + '"';
    if (index < cookies.length - 1) pythonCode += ',';
    pythonCode += '\\n';
});
pythonCode += '}';

// Copy to clipboard
var temp = document.createElement('textarea');
temp.value = pythonCode;
document.body.appendChild(temp);
temp.select();
document.execCommand('copy');
document.body.removeChild(temp);

console.log('='.repeat(50));
console.log('✅ Python code copied to clipboard!');
console.log('📋 Now replace the COOKIES in your Python script with:');
console.log(pythonCode);
"""

# ========================================
# STEP 1: Test Authentication
# ========================================
def test_cookies():
    try:
        profile_url = "https://www.qatarliving.com/user/maizan"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml",
            "Referer": "https://www.qatarliving.com/"
        }
        response = session.get(profile_url, headers=headers, cookies=COOKIES, timeout=15)
        if response.status_code == 200 and ("maizan" in response.text.lower() or "logout" in response.text.lower()):
            print("✅ Cookies test: PASSED - Authenticated as maizan")
            return True
        else:
            print("❌ Cookies test: FAILED - Not logged in")
            return False
    except Exception as e:
        print(f"❌ Cookies test error: {e}")
        return False

# ========================================
# STEP 2: Get CSRF Token from Job Page
# ========================================
def get_csrf_token():
    try:
        job_page_url = "https://www.qatarliving.com/jobseeker/maizan/it-support"
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html",
            "Referer": "https://www.qatarliving.com/classifieds"
        }
        response = session.get(job_page_url, headers=headers, timeout=15)
        if response.status_code != 200:
            print(f"❌ Failed to load job page: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')

        # Look for form_token in hidden input
        token_input = soup.find("input", {"name": "form_token"})
        if token_input and token_input.get("value"):
            token = token_input["value"]
            print(f"🔑 CSRF Token found: {token[:20]}...")
            return token

        # Alternative: look for form_build_id
        build_id = soup.find("input", {"name": "form_build_id"})
        if build_id and build_id.get("value"):
            print(f"🔑 Form Build ID found: {build_id['value'][:20]}...")
            return build_id["value"]

        print("❌ No CSRF token or form_build_id found")
        return None

    except Exception as e:
        print(f"❌ Error fetching CSRF: {e}")
        return None

# ========================================
# STEP 3: Perform Bump (POST with CSRF)
# ========================================
def refresh_post():
    csrf_token = get_csrf_token()
    if not csrf_token:
        print("💥 Cannot proceed without CSRF token")
        return False

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Referer": "https://www.qatarliving.com/jobseeker/maizan/it-support",
                "Origin": "https://www.qatarliving.com",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Content-Type": "application/x-www-form-urlencoded",
            }

            # Try POST first
            data = {
                "form_id": "classified_bump_form",
                "form_token": csrf_token,
                "form_build_id": csrf_token,  # sometimes reused
                "bump": "Bump to top",
                "destination": DESTINATION
            }

            print(f"🔄 Attempt {attempt}/{MAX_RETRIES} (POST bump)...")
            response = session.post(
                BUMP_URL,
                headers=headers,
                data=data,
                timeout=30,
                allow_redirects=True
            )

            print(f"📊 Status: {response.status_code}")
            print(f"📍 Final URL: {response.url}")

            if response.status_code in [200, 302]:
                if "bumped" in response.text.lower() or "success" in response.text.lower():
                    print("✅ SUCCESS: Post bumped via POST!")
                    logging.info("Post bumped successfully via POST")
                    return True
                if DESTINATION in response.url:
                    print("✅ SUCCESS: Redirected to job page after bump")
                    logging.info("Redirected to job page - bump likely succeeded")
                    return True

            # Fallback: Try GET if POST fails
            if attempt == 1:
                print("⚠️ POST failed, trying GET fallback...")
                get_response = session.get(FULL_BUMP_URL, headers=headers, timeout=30)
                if "bumped" in get_response.text.lower() or DESTINATION in get_response.url:
                    print("✅ SUCCESS: Post bumped via GET fallback!")
                    return True

        except Exception as e:
            print(f"❌ Error on attempt {attempt}: {e}")
            logging.error(f"Attempt {attempt} failed: {e}")

        if attempt < MAX_RETRIES:
            wait = random.uniform(5, MAX_WAIT)
            print(f"⏳ Waiting {wait:.1f}s before retry...")
            time.sleep(wait)

    print("🚫 All attempts failed")
    return False

# ========================================
# SHOW COOKIE FINDER INSTRUCTIONS
# ========================================
def show_cookie_finder_instructions():
    print("🔄 Need fresh cookies? Here's how:")
    print("1. Go to: https://www.qatarliving.com")
    print("2. Make sure you're LOGGED IN")
    print("3. Press F12 → Console tab")
    print("4. Paste this code and press Enter:")
    print("\n" + "="*50)
    print(COOKIE_FINDER_SCRIPT)
    print("="*50)
    print("\n5. Copy the output and replace the COOKIES above")

# ========================================
# MAIN
# ========================================
if __name__ == "__main__":
    print("🔁 Qatar Living Auto-Refresh Job Started")
    print(f"🕒 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"👤 User: maizan")
    print(f"🎯 Target: {FULL_BUMP_URL}")
    print("-" * 50)

    # Set cookies globally
    for name, value in COOKIES.items():
        session.cookies.set(name, value, domain=".qatarliving.com")

    if not test_cookies():
        print("💥 Authentication failed - cookies may be expired")
        print("-" * 50)
        show_cookie_finder_instructions()
        # Log the error
        logging.error("Authentication failed - cookies may be expired")
        # Exit with error code for scheduled tasks
        sys.exit(1)
    else:
        print("🔄 Proceeding with bump...")
        if refresh_post():
            print("🎉 Refresh completed successfully!")
            logging.info("SUCCESS: Post bumped successfully")
            sys.exit(0)  # Success exit code
        else:
            print("💥 Refresh failed")
            logging.error("FAILED: Post bump failed")
            sys.exit(1)  # Error exit code

    print("-" * 50)
    print(f"🕒 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
