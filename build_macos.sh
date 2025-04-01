#!/bin/bash

# Exit on error
set -e

echo "Building Pokemon Quiz for MacOS..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

# Install required packages
echo "Installing required packages..."
pip3 install -r requirements.txt
pip3 install pyinstaller

# Ensure CSV file exists
if [ ! -f "pokemon_names.csv" ]; then
    echo "Error: pokemon_names.csv file not found!"
    exit 1
else
    echo "Found pokemon_names.csv file."
fi

# Create spec file for MacOS
echo "Creating PyInstaller spec file..."
cat > pokemon_quiz.spec << 'EOL'
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['pokemon_quiz.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('img', 'img'),
        ('pokemon_names.csv', '.'),  # Include the CSV file
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PokemonQuiz',
    debug=True,  # Enable debug mode to see more output
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Change to True for debugging
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)

app = BUNDLE(
    exe,
    name='PokemonQuiz.app',
    icon=None,
    bundle_identifier='com.pokemonquiz.app',
    info_plist={
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHighResolutionCapable': 'True',
    }
)
EOL

# Build the application
echo "Building application..."
pyinstaller pokemon_quiz.spec

# Clean up
echo "Cleaning up..."
rm -rf build
rm pokemon_quiz.spec

echo "Build complete! The application can be found in dist/PokemonQuiz.app" 