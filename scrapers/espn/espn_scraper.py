"""
ESPN Fantasy Football Scraper with Gemini 3 Flash AI Vision
Main scraper engine with intelligent navigation
"""
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional, List
from playwright.sync_api import sync_playwright, Page, BrowserContext
import config
from gemini_client import GeminiVisionClient
from auth_manager import AuthManager, LoginHelper
from data_extraction import DataExtractor
from data_manager import DataManager


class ESPNFantasyScraper:
    """
    AI-powered ESPN Fantasy Football scraper
    Uses Gemini 3 Flash vision for intelligent data extraction
    """
    
    def __init__(self):
        """Initialize scraper components"""
        print("\n" + "="*60)
        print("ESPN Fantasy Football AI Scraper")
        print("Powered by Gemini 3 Flash Vision")
        print("="*60 + "\n")
        
        # Initialize components
        self.gemini = GeminiVisionClient()
        self.auth = AuthManager()
        self.extractor = DataExtractor(self)
        self.data_manager = DataManager()
        
        # Playwright objects (initialized in start())
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
        # Data storage
        self.scraped_data = {
            'league_id': config.LEAGUE_ID,
            'season_year': config.SEASON_YEAR,
            'scraped_at': datetime.now().isoformat(),
            'standings': [],
            'matchups': {},
            'rosters': {},
            'transactions': [],
            'player_stats': []
        }
        
        # Ensure data directories exist
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
    
    def start(self):
        """Start browser and set up authentication"""
        print("Starting browser...")
        
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.firefox.launch(
            headless=config.HEADLESS
        )
        
        # Create browser context
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        
        self.page = self.context.new_page()
        self.page.set_default_timeout(30000)  # 30 seconds for slower pages
        
        print("✓ Browser started\n")
    
    def authenticate(self) -> bool:
        """
        Handle authentication - load cookies or prompt for manual login
        
        Returns:
            True if authenticated successfully
        """
        print("Authenticating...")
        
        # Try to load saved cookies
        cookies = self.auth.load_cookies()
        
        if cookies:
            # Apply cookies to browser context
            self.auth.apply_cookies_to_context(self.context)
            
            # Navigate to league page to verify cookies work
            league_url = self._get_league_url()
            print(f"Navigating to: {league_url}")
            self.page.goto(league_url)
            time.sleep(3)
            
            # Check if we're logged in
            if self._is_logged_in():
                print("✓ Authentication successful (using saved cookies)\n")
                return True
            else:
                print("⚠ Saved cookies appear invalid, manual login required")
                self.auth.clear_cookies()
        
        # Need manual login
        return self._manual_login()
    
    def _manual_login(self) -> bool:
        """
        Prompt user to manually log in
        
        Returns:
            True if login successful
        """
        # Navigate to ESPN login
        league_url = self._get_league_url()
        print(f"Navigating to: {league_url}")
        self.page.goto(league_url)
        time.sleep(2)
        
        # Show login instructions
        LoginHelper.prompt_for_manual_login()
        
        # Verify login
        if not LoginHelper.verify_login_successful(self.page):
            print("✗ Login verification failed")
            return False
        
        # Save cookies for next time
        cookies = self.context.cookies()
        self.auth.save_cookies(cookies)
        
        print("✓ Authentication successful\n")
        return True
    
    def _is_logged_in(self) -> bool:
        """
        Check if currently logged into ESPN
        
        Returns:
            True if logged in
        """
        url = self.page.url
        
        # If we're on a login page, not logged in
        if 'login' in url.lower():
            return False
        
        # If we can see league content, we're logged in
        if 'fantasy.espn.com' in url and 'leagueId' in url:
            return True
        
        return False
    
    def _get_league_url(self, view: str = "") -> str:
        """
        Get ESPN league URL
        
        Args:
            view: Optional view parameter (scoreboard, roster, etc.)
            
        Returns:
            Full ESPN league URL
        """
        base = f"https://fantasy.espn.com/football/league"
        params = f"?leagueId={config.LEAGUE_ID}&seasonId={config.SEASON_YEAR}"
        
        if view:
            params += f"&view={view}"
        
        return base + params
    
    def take_screenshot(self, name: str = "screenshot") -> bytes:
        """
        Take a screenshot of current page
        
        Args:
            name: Name for screenshot file
            
        Returns:
            Screenshot as bytes
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_{timestamp}.png"
        filepath = os.path.join(config.SCREENSHOT_DIR, filename)
        
        screenshot_bytes = self.page.screenshot(path=filepath, full_page=False)
        print(f"  📸 Screenshot saved: {filename}")
        
        return screenshot_bytes
    
    def navigate_intelligently(self, goal: str) -> bool:
        """
        Use AI to navigate to desired page section
        
        Args:
            goal: Description of where to navigate
            
        Returns:
            True if navigation successful
        """
        print(f"🤖 AI Navigation: {goal}")
        
        # Take screenshot of current page
        screenshot = self.page.screenshot()
        
        # Ask Gemini what to click
        element_info = self.gemini.identify_clickable_element(screenshot, goal)
        
        element_text = element_info.get('element_text', '')
        confidence = element_info.get('confidence', 'unknown')
        reasoning = element_info.get('reasoning', '')
        
        print(f"  Found: '{element_text}' (confidence: {confidence})")
        print(f"  Reasoning: {reasoning}")
        
        # Try to click the element
        try:
            # Try exact text match first
            if self.page.get_by_text(element_text, exact=True).count() > 0:
                self.page.get_by_text(element_text, exact=True).first.click()
            else:
                # Try partial match
                self.page.get_by_text(element_text, exact=False).first.click()
            
            time.sleep(2)
            print(f"  ✓ Clicked '{element_text}'")
            return True
            
        except Exception as e:
            print(f"  ✗ Failed to click: {e}")
            return False
    
    def extract_with_vision(
        self,
        data_description: str,
        schema_hint: Optional[str] = None
    ) -> Dict[Any, Any]:
        """
        Extract data from current page using Gemini vision
        
        Args:
            data_description: What data to extract
            schema_hint: Optional JSON schema hint
            
        Returns:
            Extracted data as dict
        """
        print(f"🤖 Extracting: {data_description}")
        
        # Take screenshot
        screenshot = self.page.screenshot()
        
        # Use Gemini to extract structured data
        data = self.gemini.extract_json_from_screenshot(
            screenshot,
            data_description,
            schema_hint
        )
        
        print(f"  ✓ Extracted {len(data)} data fields")
        return data
    
    def verify_extraction(self, data: Dict[Any, Any]) -> Dict[str, Any]:
        """
        Use AI to verify extracted data is accurate
        
        Args:
            data: Data to verify
            
        Returns:
            Verification results
        """
        print(f"🤖 Verifying extracted data...")
        
        screenshot = self.page.screenshot()
        verification = self.gemini.verify_data_accuracy(screenshot, data)
        
        matches = verification.get('matches', False)
        confidence = verification.get('confidence', 'unknown')
        discrepancies = verification.get('discrepancies', [])
        
        if matches:
            print(f"  ✓ Data verified (confidence: {confidence})")
        else:
            print(f"  ⚠ Data verification issues (confidence: {confidence})")
            for disc in discrepancies:
                print(f"    - {disc}")
        
        return verification
    
    def get_current_page_info(self) -> str:
        """
        Get AI summary of current page
        
        Returns:
            Description of current page
        """
        screenshot = self.page.screenshot()
        summary = self.gemini.get_page_summary(screenshot)
        return summary
    
    def close(self):
        """Clean up resources"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("\n✓ Browser closed")


def main():
    """Main entry point for scraper"""
    scraper = ESPNFantasyScraper()
    
    try:
        # Start browser
        scraper.start()
        
        # Authenticate
        if not scraper.authenticate():
            print("✗ Authentication failed")
            return
        
        # Get page info
        print("\nAnalyzing current page...")
        page_info = scraper.get_current_page_info()
        print(f"Current page: {page_info}\n")
        
        # Extract all data
        print("\n" + "="*60)
        print("Starting comprehensive data extraction...")
        print("="*60)
        
        scraper.scraped_data = scraper.extractor.extract_all_data()
        
        # Add metadata
        scraper.scraped_data['league_id'] = config.LEAGUE_ID
        scraper.scraped_data['season_year'] = config.SEASON_YEAR
        scraper.scraped_data['scraped_at'] = datetime.now().isoformat()
        
        # Save data
        scraper.data_manager.save_all(scraper.scraped_data)
        
        print("\n✓ Data extraction complete!")
        print(f"  - Standings: {len(scraper.scraped_data.get('standings', []))} teams")
        print(f"  - Matchups: {len(scraper.scraped_data.get('matchups', {}))} weeks")
        print(f"  - Rosters: {len(scraper.scraped_data.get('rosters', []))} teams")
        print(f"  - Transactions: {len(scraper.scraped_data.get('transactions', []))} entries")
        print(f"  - Player Stats: {len(scraper.scraped_data.get('player_stats', []))} players")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Scraping interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.close()


if __name__ == "__main__":
    main()

