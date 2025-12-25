"""
Setup script for ESPN Fantasy Football Scraper
Validates environment and dependencies
"""
import sys
import os
import subprocess

def check_python_version():
    """Ensure Python 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("✗ Python 3.8+ required")
        print(f"  Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro}")
    return True


def check_env_file():
    """Check if .env file exists"""
    if not os.path.exists('.env'):
        print("⚠ .env file not found")
        print("  Creating from .env.example...")
        
        if os.path.exists('.env.example'):
            # User needs to manually copy since .env is in gitignore
            print("\n  Please run: cp .env.example .env")
            print("  Then edit .env with your API key and league info")
            return False
        else:
            print("✗ .env.example not found")
            return False
    print("✓ .env file exists")
    return True


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling Python dependencies...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt', '--quiet'
        ])
        print("✓ Python dependencies installed")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to install dependencies")
        return False


def install_playwright():
    """Install Playwright browsers"""
    print("\nInstalling Playwright browser...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'playwright', 'install', 'chromium'
        ])
        print("✓ Playwright chromium installed")
        return True
    except subprocess.CalledProcessError:
        print("⚠ Playwright installation issue (may need manual installation)")
        return True  # Non-critical


def check_directories():
    """Ensure required directories exist"""
    dirs = ['data', 'data/screenshots', 'templates']
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
            print(f"✓ Created directory: {d}")
        else:
            print(f"✓ Directory exists: {d}")
    return True


def test_imports():
    """Test if required packages can be imported"""
    print("\nTesting package imports...")
    packages = [
        ('playwright', 'playwright.sync_api'),
        ('google.generativeai', 'genai'),
        ('flask', 'flask'),
        ('PIL', 'pillow'),
    ]
    
    all_ok = True
    for package, display_name in packages:
        try:
            __import__(package)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} (not installed)")
            all_ok = False
    
    return all_ok


def main():
    """Run setup validation"""
    print("="*60)
    print("ESPN Fantasy Football Scraper - Setup")
    print("="*60)
    print()
    
    checks = [
        ("Python version", check_python_version),
        ("Directories", check_directories),
        ("Dependencies", install_dependencies),
        ("Playwright", install_playwright),
        ("Imports", test_imports),
        ("Environment", check_env_file),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{name}:")
        results.append(check_func())
    
    print("\n" + "="*60)
    if all(results[:-1]):  # All except .env check
        print("✓ Setup complete!")
        print("\nNext steps:")
        if not results[-1]:  # .env missing
            print("  1. Copy .env.example to .env")
            print("  2. Add your Gemini API key to .env")
            print("  3. Add your ESPN league ID to .env")
            print("  4. Run: python espn_scraper.py")
        else:
            print("  1. Verify your .env settings")
            print("  2. Run: python espn_scraper.py")
    else:
        print("✗ Setup incomplete")
        print("  Please fix errors above and run setup.py again")
    print("="*60)


if __name__ == "__main__":
    main()

