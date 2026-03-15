import sys
import os

# When running as a frozen exe, set CWD to the exe's directory
# so that relative paths (./output etc.) resolve next to the exe.
if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
else:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.app import EasyTaxApp

if __name__ == "__main__":
    app = EasyTaxApp()
    app.mainloop()
