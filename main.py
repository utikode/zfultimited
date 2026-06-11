"""
Main Entry Point for Buku Besar Forex ZF V16.4-OMNI-WARROOM
"""

import sys
import os

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from forex_zf_app.core.zf_core import ZFCore
from forex_zf_app.gui.main_gui import run_gui

def main():
    print("="*60)
    print("BUKU BESAR FOREX ZF")
    print("Zuhri Formalism V16.4-OMNI-WARROOM")
    print("="*60)
    
    # Initialize Core Engine
    zf_core = ZFCore()
    
    try:
        # Launch GUI
        run_gui(zf_core)
    except KeyboardInterrupt:
        print("\nShutting down ZF-Core...")
    finally:
        print("ZF-Core shutdown complete.")
        print("Application closed.")

if __name__ == "__main__":
    main()
