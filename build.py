import PyInstaller.__main__
import os
from playwright.sync_api import sync_playwright
import shutil
import sys
from pathlib import Path
import playwright

# Set PLAYWRIGHT_BROWSERS_PATH=0 before installing browser
os.environ['PLAYWRIGHT_BROWSERS_PATH'] = '0'
os.system('playwright install chromium')

# Get playwright browser directory
with sync_playwright() as p:
    browser_path = p.chromium.executable_path
    browser_dir = os.path.dirname(browser_path)

# Get the playwright package directory
playwright_dir = os.path.dirname(playwright.__file__)

# Create the command for PyInstaller
command = [
    'meulade.py',
    'gui.py',
    'browser.py',
    'languages.py',
    'logger.py',
    '--onefile',
    '--name=Meulade',
    '--clean',
    '--add-data=config.json;.',
    f'--add-binary={browser_dir}/*;.',
    '--collect-all=playwright',
    '--collect-all=pygame',
    '--hidden-import=pygame',
    '--hidden-import=winsound',
    '--hidden-import=playwright.sync_api',
    '--hidden-import=playwright.async_api',
    '--hidden-import=playwright._impl._api_types',
    '--hidden-import=playwright._impl.sync_api',
    '--hidden-import=playwright._impl.async_api',
]

# Run PyInstaller
PyInstaller.__main__.run(command)

# Optional: Clean up build artifacts
if os.path.exists('build'):
    shutil.rmtree('build') 