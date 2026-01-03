"""
Authentication Manager for ESPN Fantasy
Handles cookie-based authentication with persistence
"""
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import config


class AuthManager:
    """
    Manages ESPN authentication cookies
    Saves and loads cookies for persistent sessions
    """
    
    def __init__(self, cookies_file: Optional[str] = None):
        """
        Initialize auth manager
        
        Args:
            cookies_file: Path to cookies JSON file
        """
        self.cookies_file = cookies_file or config.COOKIES_FILE
        self.cookies = []
        self.authenticated = False
    
    def save_cookies(self, cookies: List[Dict]) -> bool:
        """
        Save cookies to file
        
        Args:
            cookies: List of cookie dicts from Playwright
            
        Returns:
            True if successful
        """
        try:
            # Filter out unnecessary cookies, keep ESPN-related ones
            espn_cookies = [
                cookie for cookie in cookies
                if 'espn' in cookie.get('domain', '').lower()
            ]
            
            # Add metadata
            cookie_data = {
                'cookies': espn_cookies,
                'saved_at': datetime.now().isoformat(),
                'domain': 'fantasy.espn.com'
            }
            
            with open(self.cookies_file, 'w') as f:
                json.dump(cookie_data, f, indent=2)
            
            print(f"✓ Saved {len(espn_cookies)} cookies to {self.cookies_file}")
            self.cookies = espn_cookies
            self.authenticated = True
            return True
            
        except Exception as e:
            print(f"✗ Failed to save cookies: {e}")
            return False
    
    def load_cookies(self) -> Optional[List[Dict]]:
        """
        Load cookies from file
        
        Returns:
            List of cookie dicts or None if file doesn't exist
        """
        if not os.path.exists(self.cookies_file):
            print(f"ℹ No saved cookies found at {self.cookies_file}")
            return None
        
        try:
            with open(self.cookies_file, 'r') as f:
                cookie_data = json.load(f)
            
            cookies = cookie_data.get('cookies', [])
            saved_at = cookie_data.get('saved_at', 'unknown')
            
            print(f"✓ Loaded {len(cookies)} cookies (saved: {saved_at})")
            self.cookies = cookies
            self.authenticated = True
            return cookies
            
        except Exception as e:
            print(f"✗ Failed to load cookies: {e}")
            return None
    
    def clear_cookies(self) -> bool:
        """
        Delete saved cookies file
        
        Returns:
            True if successful
        """
        try:
            if os.path.exists(self.cookies_file):
                os.remove(self.cookies_file)
                print(f"✓ Deleted cookies file: {self.cookies_file}")
            
            self.cookies = []
            self.authenticated = False
            return True
            
        except Exception as e:
            print(f"✗ Failed to delete cookies: {e}")
            return False
    
    def is_authenticated(self) -> bool:
        """
        Check if we have valid cookies
        
        Returns:
            True if cookies exist
        """
        return self.authenticated and len(self.cookies) > 0
    
    def apply_cookies_to_context(self, context) -> bool:
        """
        Apply saved cookies to Playwright browser context
        
        Args:
            context: Playwright browser context
            
        Returns:
            True if cookies were applied
        """
        if not self.cookies:
            return False
        
        try:
            context.add_cookies(self.cookies)
            print(f"✓ Applied {len(self.cookies)} cookies to browser context")
            return True
        except Exception as e:
            print(f"✗ Failed to apply cookies: {e}")
            return False
    
    def requires_manual_login(self) -> bool:
        """
        Check if manual login is needed
        
        Returns:
            True if no valid cookies exist
        """
        return not self.is_authenticated()


class LoginHelper:
    """
    Helper for interactive login process
    """
    
    @staticmethod
    def prompt_for_manual_login():
        """
        Display instructions for manual login
        """
        print("\n" + "="*60)
        print("MANUAL LOGIN REQUIRED")
        print("="*60)
        print("\nA browser window has opened to ESPN Fantasy Football.")
        print("\nPlease:")
        print("  1. Log in with your ESPN credentials")
        print("  2. Navigate to your league (if not already there)")
        print("  3. Wait until you can see your league's main page")
        print("  4. Press Enter in this terminal to continue")
        print("\nYour session will be saved for future runs.")
        print("="*60 + "\n")
        
        input("Press Enter when you're logged in and ready to continue... ")
        print("\n✓ Continuing with scrape...\n")
    
    @staticmethod
    def verify_login_successful(page) -> bool:
        """
        Check if we're successfully logged into ESPN
        
        Args:
            page: Playwright page object
            
        Returns:
            True if login appears successful
        """
        try:
            url = page.url
            
            # Check if we're on an ESPN fantasy page
            if 'fantasy.espn.com' in url:
                print("✓ Login verified - on ESPN Fantasy page")
                return True
            
            print("⚠ Warning: Not on ESPN Fantasy page")
            print(f"  Current URL: {url}")
            return False
            
        except Exception as e:
            print(f"✗ Error verifying login: {e}")
            return False


if __name__ == "__main__":
    # Test auth manager
    auth = AuthManager()
    
    print("Testing AuthManager...")
    print(f"  Cookies file: {auth.cookies_file}")
    print(f"  Is authenticated: {auth.is_authenticated()}")
    
    if auth.load_cookies():
        print(f"  Loaded cookies: {len(auth.cookies)}")
    else:
        print("  No saved cookies found (this is normal on first run)")

