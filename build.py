#!/usr/bin/env python3
"""
Automated build script for Greedy Gardens
Extracts version from main.py and builds the executable with correct naming
Creates release folder with all necessary files for distribution
"""

import os
import re
import subprocess
import sys
import shutil
import platform
from PIL import Image

def extract_version_from_main():
    """Extract version number from main.py"""
    try:
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for the version_number line
        version_match = re.search(r"self\.version_number\s*=\s*['\"]([^'\"]+)['\"]", content)
        if version_match:
            version = version_match.group(1)
            # Remove 'v' prefix if present for cleaner exe name
            clean_version = version.lstrip('v')
            return clean_version
        else:
            print("❌ Could not find version number in main.py")
            return None
    except FileNotFoundError:
        print("❌ main.py not found. Make sure you're in the project root directory.")
        return None
    except Exception as e:
        print(f"❌ Error reading main.py: {e}")
        return None

def convert_png_to_ico():
    """Convert PNG icon to ICO format for better Windows compatibility"""
    png_path = "assets/graphics/icon.png"
    ico_path = "assets/graphics/icon.ico"
    
    if not os.path.exists(png_path):
        return None
    
    # Check if ICO already exists and is newer than PNG
    if os.path.exists(ico_path):
        png_time = os.path.getmtime(png_path)
        ico_time = os.path.getmtime(ico_path)
        if ico_time >= png_time:
            return ico_path  # ICO is up to date
    
    try:
        print("🎨 Converting PNG icon to ICO format...")
        img = Image.open(png_path)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Save as ICO with multiple sizes for better Windows support
        img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
        print("✅ Icon converted successfully")
        return ico_path
        
    except Exception as e:
        print(f"⚠️  Icon conversion failed: {e}")
        return png_path  # Fall back to PNG

def convert_png_to_icns():
    """Convert PNG icon to ICNS format for macOS compatibility"""
    png_path = "assets/graphics/icon.png"
    icns_path = "assets/graphics/icon.icns"

    if not os.path.exists(png_path):
        return None

    # Check if ICNS already exists and is newer than PNG
    if os.path.exists(icns_path):
        png_time = os.path.getmtime(png_path)
        icns_time = os.path.getmtime(icns_path)
        if icns_time >= png_time:
            return icns_path  # ICNS is up to date

    try:
        print("🎨 Converting PNG icon to ICNS format...")
        img = Image.open(png_path)

        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # Save as ICNS (requires py2icns or similar tool installed)
        temp_icns = "temp_icon.icns"
        img.save(temp_icns, format="ICNS")
        shutil.move(temp_icns, icns_path)
        print("✅ Icon converted successfully")
        return icns_path

    except Exception as e:
        print(f"⚠️  Icon conversion failed: {e}")
        return png_path  # Fall back to PNG

def get_platform_name():
    """Get the platform name for release folder"""
    system = platform.system()
    if system == "Windows":
        return "Windows"
    elif system == "Linux":
        return "Linux"
    elif system == "Darwin":
        return "macOS"
    else:
        return system

def create_release_folder(version, exe_name):
    """Create release folder structure and copy all necessary files"""
    platform_name = get_platform_name()
    release_folder = f"release/GreedyGardens-v{version}-{platform_name}"
    
    print(f"📁 Creating release folder: {release_folder}")
    
    # Create release directory
    os.makedirs(release_folder, exist_ok=True)
    
    # Copy executable
    exe_extension = ".exe" if platform_name == "Windows" else ""
    src_exe = f"dist/{exe_name}{exe_extension}"
    dst_exe = f"{release_folder}/PlayGreedyGardens-v{version}{exe_extension}"
    
    if os.path.exists(src_exe):
        shutil.copy2(src_exe, dst_exe)
        print(f"✅ Copied executable")
    else:
        print(f"❌ Executable not found: {src_exe}")
        return False
    
    # Copy assets folder
    if os.path.exists("assets"):
        dst_assets = f"{release_folder}/assets"
        if os.path.exists(dst_assets):
            shutil.rmtree(dst_assets)
        shutil.copytree("assets", dst_assets)
        print(f"✅ Copied assets folder")
    else:
        print("⚠️  Assets folder not found")
    
    # Copy CREDITS.txt
    if os.path.exists("CREDITS.txt"):
        shutil.copy2("CREDITS.txt", f"{release_folder}/CREDITS.txt")
        print(f"✅ Copied CREDITS.txt")
    else:
        print("⚠️  CREDITS.txt not found")
    
    # Copy LICENSE
    if os.path.exists("LICENSE"):
        shutil.copy2("LICENSE", f"{release_folder}/LICENSE")
        print(f"✅ Copied LICENSE")
    else:
        print("⚠️  LICENSE file not found")
    
    return release_folder

def build_executable(version):
    """Build the executable using PyInstaller"""
    exe_name = f"PlayGreedyGardens-{version}"
    
    print(f"🔨 Building executable: {exe_name}")
    print(f"📦 Version: {version}")
    
    # Handle icon conversion and selection
    png_icon = "assets/graphics/icon.png"
    ico_icon = "assets/graphics/icon.ico"
    
    icon_path = None
    if os.path.exists(png_icon):
        # Try to convert PNG to ICO for better Windows compatibility
        converted_icon = convert_png_to_ico()
        if converted_icon and os.path.exists(converted_icon):
            icon_path = converted_icon
            print(f"🎨 Using converted ICO icon: {icon_path}")
        else:
            icon_path = png_icon
            print(f"🎨 Using PNG icon: {icon_path}")
    elif os.path.exists(ico_icon):
        icon_path = ico_icon
        print(f"🎨 Using existing ICO icon: {icon_path}")
    
    # Build PyInstaller command
    if icon_path:
        cmd = [
            "pyinstaller",
            "--onefile",
            "--noconsole", 
            "--name", exe_name,
            "--icon", icon_path,
            "main.py"
        ]
    else:
        print("⚠️  No icon found, building without icon")
        cmd = [
            "pyinstaller",
            "--onefile",
            "--noconsole", 
            "--name", exe_name,
            "main.py"
        ]
    
    print(f"🚀 Running: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print(f"📁 Executable created: dist/{exe_name}.exe")
        
        # Set executable permissions on Linux
        if platform.system() == "Linux":
            ensure_executable_permissions(f"dist/{exe_name}")
        
        return exe_name
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code {e.returncode}")
        
        # Check for common issues
        if "PIL" in e.stderr or "Pillow" in e.stderr:
            print("💡 Tip: Install Pillow for PNG icon support: pip install Pillow")
        elif "icon" in e.stderr.lower():
            print("💡 Tip: Try converting icon.png to icon.ico or remove --icon flag")
        
        print(f"Error output: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
        return None

def build_mac_app(version):
    """Build a macOS .app bundle using PyInstaller"""
    exe_name = f"PlayGreedyGardens-{version}"

    print(f"🔨 Building macOS .app bundle: {exe_name}")
    print(f"📦 Version: {version}")

    # Handle icon conversion and selection
    png_icon = "assets/graphics/icon.png"
    icns_icon = "assets/graphics/icon.icns"

    icon_path = None
    if os.path.exists(png_icon):
        # Try to convert PNG to ICNS for macOS compatibility
        converted_icon = convert_png_to_icns()
        if converted_icon and os.path.exists(converted_icon):
            icon_path = converted_icon
            print(f"🎨 Using converted ICNS icon: {icon_path}")
        else:
            icon_path = png_icon
            print(f"🎨 Using PNG icon: {icon_path}")
    elif os.path.exists(icns_icon):
        icon_path = icns_icon
        print(f"🎨 Using existing ICNS icon: {icon_path}")

    # Build PyInstaller command for macOS .app
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", exe_name,
        "--icon", icon_path if icon_path else "",
        "main.py"
    ]

    print(f"🚀 Running: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ Build completed successfully!")
        print(f"📁 .app bundle created: dist/{exe_name}.app")
        return exe_name
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
        return None
    except FileNotFoundError:
        print("❌ PyInstaller not found. Please install it with: pip install pyinstaller")
        return None

def ensure_executable_permissions(file_path):
    """Ensure the output file has executable permissions on Linux"""
    try:
        if platform.system() == "Linux":
            os.chmod(file_path, 0o755)
            print(f"✅ Set executable permissions for {file_path}")
    except Exception as e:
        print(f"⚠️  Failed to set executable permissions: {e}")

def main():
    """Main build function"""
    print("🎮 Greedy Gardens Build Script")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists('main.py'):
        print("❌ main.py not found. Please run this script from the project root directory.")
        sys.exit(1)
    
    # Extract version
    version = extract_version_from_main()
    if not version:
        sys.exit(1)
    
    exe_name = None
    # Build executable or macOS app
    if platform.system() == "Darwin":
        exe_name = build_mac_app(version)
    else:
        exe_name = build_executable(version)
    
    if not exe_name:
        print("\n💥 Build failed!")
        sys.exit(1)
    
    # Create release folder and copy files
    print("\n📦 Creating release package...")
    release_folder = create_release_folder(version, exe_name)
    
    if release_folder:
        print(f"\n🎉 Release package created successfully!")
        print(f"📁 Release folder: {release_folder}")
        print(f"🎮 Ready for distribution!")
    else:
        print("\n💥 Release package creation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
