"""
Main Entry Point - Buku Besar Forex ZF V16.4-OMNI-WARROOM
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import config
from core import ZFCore
from gui.main_gui import MainApp

def main():
    """Main function to run the application"""
    print("=" * 60)
    print("BUKU BESAR FOREX ZF")
    print("Zuhri Formalism V16.4-OMNI-WARROOM")
    print("=" * 60)
    
    # Load configuration from file if exists
    config_file = os.path.join(config.BASE_DIR, "config", "settings.json")
    if os.path.exists(config_file):
        loaded_config = config.load_from_file(config_file)
        # Update global config
        for key, value in vars(loaded_config).items():
            if not key.startswith('_'):
                setattr(config, key, value)
    
    # Initialize ZF Core
    zf_core = ZFCore(config)
    
    try:
        # Initialize core components
        zf_core.initialize()
        
        # Start GUI
        app = MainApp(zf_core)
        app.mainloop()
        
    except KeyboardInterrupt:
        print("\nShutting down by user request...")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        zf_core.shutdown()
        print("Application closed.")

if __name__ == "__main__":
    main()
