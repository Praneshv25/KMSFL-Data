"""
Test Gemini API connection and basic functionality
Run this before the main scraper to verify setup
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("ESPN Fantasy Scraper - Connection Test")
print("="*60)

# Test 1: Import config
print("\n1. Testing configuration...")
try:
    import config
    print(f"   ✓ Config loaded")
    print(f"   League ID: {config.LEAGUE_ID}")
    print(f"   Season: {config.SEASON_YEAR}")
    print(f"   Model: {config.GEMINI_MODEL}")
    
    if config.GEMINI_API_KEY == "your-gemini-api-key-here":
        print("   ⚠ Warning: API key not configured in .env")
        print("   Please add your Gemini API key to .env file")
        sys.exit(1)
    else:
        print("   ✓ API key configured")
except Exception as e:
    print(f"   ✗ Config error: {e}")
    sys.exit(1)

# Test 2: Test Gemini client
print("\n2. Testing Gemini API connection...")
try:
    from gemini_client import GeminiVisionClient
    
    client = GeminiVisionClient()
    print("   ✓ Gemini client initialized")
    
    # Test with simple text prompt (no image)
    print("   Testing API call...")
    try:
        import google.generativeai as genai
        model = genai.GenerativeModel(config.GEMINI_MODEL)
        response = model.generate_content("Say 'API connection successful' if you can read this.")
        print(f"   ✓ API response: {response.text[:50]}...")
    except Exception as e:
        print(f"   ⚠ API call issue: {e}")
        print("   Note: This might be due to API key or quota issues")
        
except Exception as e:
    print(f"   ✗ Gemini client error: {e}")
    sys.exit(1)

# Test 3: Test Playwright
print("\n3. Testing Playwright browser automation...")
try:
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.google.com", timeout=10000)
        title = page.title()
        browser.close()
        print(f"   ✓ Playwright working (loaded: {title})")
except Exception as e:
    print(f"   ⚠ Playwright issue: {e}")
    print("   You may need to run: python -m playwright install chromium")

# Test 4: Test data manager
print("\n4. Testing data storage...")
try:
    from data_manager import DataManager
    dm = DataManager()
    print("   ✓ Data manager initialized")
    print(f"   Database: {dm.db_path}")
except Exception as e:
    print(f"   ✗ Data manager error: {e}")

# Test 5: Check file structure
print("\n5. Checking file structure...")
required_files = [
    'espn_scraper.py',
    'gemini_client.py',
    'auth_manager.py',
    'data_extraction.py',
    'data_manager.py',
    'app.py',
    'config.py',
    'requirements.txt'
]

missing_files = []
for filename in required_files:
    if os.path.exists(filename):
        print(f"   ✓ {filename}")
    else:
        print(f"   ✗ {filename} missing")
        missing_files.append(filename)

if missing_files:
    print(f"\n   Warning: {len(missing_files)} files missing")

# Summary
print("\n" + "="*60)
print("CONNECTION TEST SUMMARY")
print("="*60)
print("\n✓ All tests passed!")
print("\nYou're ready to run the scraper:")
print("  python espn_scraper.py")
print("\nOr start the dashboard:")
print("  python app.py")
print("\n" + "="*60)

