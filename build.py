#!/usr/bin/env python3
"""
Automated build script for Greedy Gardens
- Extracts version from main.py
- Builds platform-specific executable/bundle with correct icon
- Creates /release/<name> folder with all required files
- Tries to minimize Gatekeeper issues on macOS (ad-hoc sign, quarantine strip)

Tested with:
- Windows 10/11 (PyInstaller + .ico)
- macOS 12+ (PyInstaller + .icns via iconutil)
- Linux (PyInstaller, sets exec perms)
"""

import os
import re
import subprocess
import sys
import shutil
import platform
import tempfile
from pathlib import Path

try:
    from PIL import Image
except Exception:
    Image = None

# ---------------------------
# Utility helpers
# ---------------------------

ROOT = Path(__file__).resolve().parent

def log(s: str):
    print(s, flush=True)

def run_ok(cmd, check=True, **kwargs):
    log(f"🚀 Running: {' '.join(map(str, cmd))}")
    return subprocess.run(cmd, check=check, **kwargs)

def which(tool: str) -> bool:
    return shutil.which(tool) is not None

def is_macos() -> bool:
    return platform.system() == "Darwin"

def is_windows() -> bool:
    return platform.system() == "Windows"

def is_linux() -> bool:
    return platform.system() == "Linux"

# ---------------------------
# Version extraction
# ---------------------------

def extract_version_from_main() -> str | None:
    """Extracts version string from main.py looking for: self.version_number = 'vX.Y.Z'"""
    main_py = ROOT / "main.py"
    if not main_py.exists():
        log("❌ main.py not found. Make sure you're in the project root directory.")
        return None

    try:
        content = main_py.read_text(encoding="utf-8")
        m = re.search(r"self\.version_number\s*=\s*['\"]([^'\"]+)['\"]", content)
        if not m:
            log("❌ Could not find version number in main.py (self.version_number = '...').")
            return None
        raw = m.group(1)
        clean = raw.lstrip('v')  # drop leading 'v' for filenames
        return clean
    except Exception as e:
        log(f"❌ Error reading main.py: {e}")
        return None

# ---------------------------
# Icon handling (temp only)
# ---------------------------

def pil_to_png_bytes(img) -> bytes:
    from io import BytesIO
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def convert_png_to_ico_temp(png_path: Path, version: str) -> Path | None:
    """Convert PNG to ICO for PyInstaller, saved in temp folder."""
    if not png_path.exists() or Image is None:
        return None
    try:
        tmpdir = Path(tempfile.gettempdir())
        ico_path = tmpdir / f"PlayGreedyGardens-v{version}.ico"
        log("🎨 Creating ICO (temp for build)...")
        img = Image.open(png_path)
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        sizes = [(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)]
        img.save(ico_path, format="ICO", sizes=sizes)
        return ico_path
    except Exception as e:
        log(f"⚠️  ICO creation failed: {e}")
        return None

def convert_png_to_icns_temp(png_path: Path, version: str) -> Path | None:
    """Convert PNG to ICNS for PyInstaller, saved in temp folder."""
    if not png_path.exists() or not is_macos() or not which("iconutil") or Image is None:
        return None
    try:
        tmpdir = Path(tempfile.gettempdir())
        icns_path = tmpdir / f"PlayGreedyGardens-v{version}.icns"
        log("🎨 Creating ICNS (temp for build)...")
        with tempfile.TemporaryDirectory() as tmpbuild:
            iconset = Path(tmpbuild) / "icon.iconset"
            iconset.mkdir(parents=True, exist_ok=True)
            base = Image.open(png_path).convert("RGBA")
            sizes = [16, 32, 64, 128, 256, 512, 1024]
            for s in sizes:
                img = base.resize((s, s), Image.LANCZOS)
                (iconset / f"icon_{s}x{s}.png").write_bytes(pil_to_png_bytes(img))
                if s != 1024:
                    img2x = base.resize((s*2, s*2), Image.LANCZOS)
                    (iconset / f"icon_{s}x{s}@2x.png").write_bytes(pil_to_png_bytes(img2x))
            run_ok(["iconutil", "-c", "icns", "-o", str(icns_path), str(iconset)], check=True)
        return icns_path
    except Exception as e:
        log(f"⚠️  ICNS creation failed: {e}")
        return None

def choose_icon_for_platform(version: str) -> Path | None:
    """Return a temp icon path for PyInstaller (never in assets/graphics)."""
    png_icon = ROOT / "assets/graphics/icon.png"
    if is_windows():
        return convert_png_to_ico_temp(png_icon, version)
    if is_macos():
        return convert_png_to_icns_temp(png_icon, version)
    return png_icon if png_icon.exists() else None

# ---------------------------
# Building with PyInstaller
# ---------------------------

def ensure_pyinstaller():
    if not which("pyinstaller"):
        log("❌ PyInstaller not found. Install with: pip install pyinstaller")
        sys.exit(1)

def build_windows_linux(version: str) -> tuple[str, Path] | tuple[None, None]:
    exe_name = f"PlayGreedyGardens-v{version}"
    icon = choose_icon_for_platform(version)
    cmd = ["pyinstaller", "--onefile", "--noconsole", "--name", exe_name, "main.py"]
    if icon:
        cmd.extend(["--icon", str(icon)])

    try:
        run_ok(cmd, check=True)
        out = ROOT / "dist" / (exe_name + (".exe" if is_windows() else ""))
        if out.exists() and is_linux():
            ensure_executable_permissions(out)
        log(f"✅ Build complete: {out}")
        return exe_name, out
    except subprocess.CalledProcessError as e:
        log(f"❌ Build failed (exit {e.returncode}).")
        return None, None

def build_macos_app(version: str) -> tuple[str, Path] | tuple[None, None]:
    exe_name = f"PlayGreedyGardens-v{version}"
    icon = choose_icon_for_platform(version)
    cmd = ["pyinstaller", "--name", exe_name, "--noconsole", "--onedir", "--add-data", "assets:assets", "main.py"]
    if icon:
        cmd.extend(["--icon", str(icon)])

    try:
        run_ok(cmd, check=True)
        app_path = ROOT / "dist" / f"{exe_name}.app"
        if not app_path.exists():
            log("⚠️  PyInstaller completed but .app not found.")
            return None, None
        codesign_mac_app(app_path)
        remove_quarantine(app_path)
        log(f"✅ Build complete: {app_path}")
        return exe_name, app_path
    except subprocess.CalledProcessError as e:
        log(f"❌ Build failed (exit {e.returncode}).")
        return None, None

def codesign_mac_app(app_path: Path):
    if not is_macos() or not which("codesign"):
        return
    try:
        log(f"🔏 Ad-hoc signing {app_path}")
        run_ok(["codesign", "--deep", "--force", "--sign", "-", str(app_path)], check=True)
        log("✅ Signed (ad-hoc)")
    except subprocess.CalledProcessError as e:
        log(f"⚠️  Code signing failed (exit {e.returncode}). Continuing unsigned.")

def remove_quarantine(path: Path):
    if not is_macos() or not which("xattr"):
        return
    try:
        run_ok(["xattr", "-dr", "com.apple.quarantine", str(path)], check=False)
        log("🧼 Removed quarantine attribute (best effort).")
    except Exception:
        pass

def ensure_executable_permissions(file_path: Path):
    if is_linux():
        try:
            file_path.chmod(0o755)
            log(f"✅ chmod +x {file_path}")
        except Exception as e:
            log(f"⚠️ chmod failed: {e}")

# ---------------------------
# Release packaging
# ---------------------------

def get_platform_name() -> str:
    s = platform.system()
    return {"Windows":"Windows", "Linux":"Linux", "Darwin":"macOS"}.get(s, s)

def create_release_folder(version: str, built_name: str, built_path: Path) -> Path | None:
    release_folder = ROOT / "release" / f"GreedyGardens-v{version}-{get_platform_name()}"
    log(f"📁 Creating release folder: {release_folder}")
    release_folder.mkdir(parents=True, exist_ok=True)

    # Copy binary/app
    if is_macos() and built_path.suffix == ".app":
        dst_app = release_folder / f"PlayGreedyGardens-v{version}.app"
        if dst_app.exists(): shutil.rmtree(dst_app)
        shutil.copytree(built_path, dst_app)
        log("✅ Copied .app bundle")
    else:
        dst_bin = release_folder / f"PlayGreedyGardens-v{version}{built_path.suffix}"
        shutil.copy2(built_path, dst_bin)
        log("✅ Copied executable")

    # Copy assets
    src_assets = ROOT / "assets"
    if src_assets.exists():
        dst_assets = release_folder / "assets"
        if dst_assets.exists(): shutil.rmtree(dst_assets)
        shutil.copytree(src_assets, dst_assets)
        log("✅ Copied assets folder")

        # Generate platform-specific icon inside release/assets/graphics
        png_icon = dst_assets / "graphics" / "icon.png"
        if png_icon.exists():
            if is_windows():
                ico_path = dst_assets / "graphics" / "icon.ico"
                convert_png_to_ico_temp(png_icon, version) and shutil.copy2(
                    Path(tempfile.gettempdir()) / f"PlayGreedyGardens-v{version}.ico", ico_path)
                log(f"✅ Wrote release icon: {ico_path}")
            elif is_macos():
                icns_path = dst_assets / "graphics" / "icon.icns"
                convert_png_to_icns_temp(png_icon, version) and shutil.copy2(
                    Path(tempfile.gettempdir()) / f"PlayGreedyGardens-v{version}.icns", icns_path)
                log(f"✅ Wrote release icon: {icns_path}")
    else:
        log("⚠️ assets/ not found")

    # # CREDITS + LICENSE
    # for name in ("CREDITS.txt", "LICENSE"):
    #     src = ROOT / name
    #     if src.exists():
    #         shutil.copy2(src, release_folder / name)
    #         log(f"✅ Copied {name}")
    #     else:
    #         log(f"⚠️ {name} not found")

    return release_folder

# ---------------------------
# Main
# ---------------------------

def main():
    log("🎮 Greedy Gardens Build Script")
    log("=" * 40)

    if not (ROOT / "main.py").exists():
        log("❌ main.py not found in project root.")
        sys.exit(1)

    ensure_pyinstaller()

    version = extract_version_from_main()
    if not version:
        sys.exit(1)

    if is_macos():
        built_name, built_path = build_macos_app(version)
    else:
        built_name, built_path = build_windows_linux(version)

    if not built_name or not built_path:
        log("\n💥 Build failed!")
        sys.exit(1)

    log("\n📦 Creating release package...")
    release = create_release_folder(version, built_name, built_path)
    if not release:
        log("\n💥 Release package creation failed!")
        sys.exit(1)

    log(f"\n🎉 Release package ready: {release}")

if __name__ == "__main__":
    main()
