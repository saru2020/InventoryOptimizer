# setup_precommit.py
# Script to setup pre-commit hooks for the inventory optimization project

import subprocess
import sys
import os

def install_precommit():
    """Install pre-commit if not already installed."""
    try:
        import pre_commit
        print("✓ pre-commit is already installed")
    except ImportError:
        print("Installing pre-commit...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pre-commit"])
        print("✓ pre-commit installed successfully")

def install_additional_tools():
    """Install additional tools for code quality."""
    tools = ["flake8", "isort", "black"]
    
    for tool in tools:
        try:
            __import__(tool)
            print(f"✓ {tool} is already installed")
        except ImportError:
            print(f"Installing {tool}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", tool])
            print(f"✓ {tool} installed successfully")

def setup_hooks():
    """Setup pre-commit hooks."""
    print("Setting up pre-commit hooks...")
    subprocess.check_call(["pre-commit", "install"])
    print("✓ Pre-commit hooks installed successfully")

def run_initial_check():
    """Run initial check on all files."""
    print("Running initial check on all files...")
    subprocess.check_call(["pre-commit", "run", "--all-files"])
    print("✓ Initial check completed successfully")

def main():
    """Main setup function."""
    print("="*60)
    print(" SETTING UP PRE-COMMIT HOOKS FOR INVENTORY OPTIMIZATION")
    print("="*60)
    
    try:
        # Install pre-commit
        install_precommit()
        
        # Install additional tools
        install_additional_tools()
        
        # Setup hooks
        setup_hooks()
        
        # Run initial check
        run_initial_check()
        
        print("\n" + "="*60)
        print(" PRE-COMMIT SETUP COMPLETE! ✓")
        print("="*60)
        print("All commits will now run tests automatically.")
        print("To run tests manually: python test_inventory_optimization.py")
        print("To run pre-commit on all files: pre-commit run --all-files")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
