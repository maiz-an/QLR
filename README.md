### Step 1: Create a GitHub Repository

1. **Go to [github.com](https://github.com)**
2. **Create new repository**: `qatar-living-auto-refresh`
3. **Make it PUBLIC** (required for free Actions)

### Step 2: Prepare Your Files

Create these files in your project:

**1. `refresh_post.py`** (your main script - use the one below)
**2. `requirements.txt`**
```
requests==2.31.0
beautifulsoup4==4.12.2
lxml==4.9.3
```

**3. `.github/workflows/auto-refresh.yml`** (GitHub Actions workflow)

### Step 3: Updated Python Script for GitHub Actions

```python
import requests
import time
import random
import logging
from datetime import datetime
import re
from bs4 import BeautifulSoup
import os
import sys
import json

# ========================================
# GITHUB ACTIONS CONFIGURATION
# ========================================
# Check if running on GitHub Actions
IS_GITHUB_ACTIONS = 'GITHUB_ACTIONS' in os.environ

if IS_GITHUB_ACTIONS:
    print("🚀 Running on GitHub Actions")
    # Get cookies from environment variable (GitHub Secrets)
    COOKIES_JSON = os.getenv('QATAR_COOKIES')
    if COOKIES_JSON:
        COOKIES = json.loads(COOKIES_JSON)
    else:
        print("❌ No cookies found in environment variables")
        sys.exit(1)
else:
    print("💻 Running locally")
    # Local cookies (for testing)
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

MAX_RETRIES = 3
MAX_WAIT = 15

# ========================================
# LOGGING SETUP
# ========================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # GitHub Actions captures stdout
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
// 5. Copy the JSON output and add to GitHub Secrets

var cookies = document.cookie.split(';');
var cookieObj = {};
console.log('🔐 Found ' + cookies.length + ' cookies:');
console.log('='.repeat(50));

cookies.forEach((cookie) => {
    var [name, value] = cookie.trim().split('=');
    var displayValue = value ? (value.length > 50 ? value.substring(0, 50) + '...' : value) : '(empty)';
    console.log('📌 ' + name + ' = ' + displayValue);
    cookieObj[name] = value || '';
});

console.log('='.repeat(50));
console.log('📋 JSON for GitHub Secrets:');
console.log(JSON.stringify(cookieObj, null, 2));

// Copy JSON to clipboard
var temp = document.createElement('textarea');
temp.value = JSON.stringify(cookieObj);
document.body.appendChild(temp);
temp.select();
document.execCommand('copy');
document.body.removeChild(temp);

console.log('✅ JSON copied to clipboard!');
console.log('💡 Add this to GitHub Secrets as QATAR_COOKIES');
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
        if not IS_GITHUB_ACTIONS:
            print("-" * 50)
            print("🔄 Need fresh cookies? Run this in browser console:")
            print(COOKIE_FINDER_SCRIPT)
        sys.exit(1)
    else:
        print("🔄 Proceeding with bump...")
        if refresh_post():
            print("🎉 Refresh completed successfully!")
            sys.exit(0)
        else:
            print("💥 Refresh failed")
            sys.exit(1)

    print("-" * 50)
    print(f"🕒 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
```

### Step 4: Create GitHub Actions Workflow

Create file `.github/workflows/auto-refresh.yml`:

```yaml
name: Qatar Living Auto Refresh

on:
  schedule:
    # Run at 9 AM, 12 PM, 3 PM, 6 PM Qatar time (6 AM, 9 AM, 12 PM, 3 PM UTC)
    - cron: '0 6,9,12,15 * * *'
  workflow_dispatch:  # Allow manual triggers

jobs:
  refresh:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run Qatar Living Auto Refresh
      env:
        QATAR_COOKIES: ${{ secrets.QATAR_COOKIES }}
      run: |
        python refresh_post.py
```

### Step 5: Set up GitHub Secrets

1. **Go to your repository Settings**
2. **Click "Secrets and variables" → "Actions"**
3. **Click "New repository secret"**
4. **Name**: `QATAR_COOKIES`
5. **Value**: Get this using the updated Cookie Finder:

**Run this in browser console:**
```javascript
// Updated Cookie Finder for GitHub
var cookies = document.cookie.split(';');
var cookieObj = {};
cookies.forEach((cookie) => {
    var [name, value] = cookie.trim().split('=');
    cookieObj[name] = value || '';
});
console.log('Copy this JSON to GitHub Secrets:');
console.log(JSON.stringify(cookieObj));
copy(JSON.stringify(cookieObj));
console.log('✅ JSON copied to clipboard!');
```

### Step 6: Push to GitHub

```bash
git add .
git commit -m "Add Qatar Living auto-refresh with GitHub Actions"
git push
```

## Benefits of This Setup:

✅ **Runs 3 times daily** (Run at 6:30 AM, 12 PM, 3 PM, Qatar time)
✅ **Completely free**  
✅ **Easy cookie updates** via GitHub Secrets  
✅ **Manual triggers** available  
✅ **Email notifications** on failure  
✅ **Full logs** in GitHub Actions  
✅ **Version controlled**  

## How to Update Cookies Later:

1. Get fresh cookies using the Cookie Finder
2. Go to Repository → Settings → Secrets → Actions
3. Update the `QATAR_COOKIES` secret
4. That's it! Next run will use new cookies

## Viewing Results:

- **Go to Actions tab** to see run history
- **Click on any run** to see detailed logs
- **Set up email notifications** for failures

This is much better than PythonAnywhere and completely free! 🚀
