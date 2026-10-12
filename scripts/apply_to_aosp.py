#!/usr/bin/env python3
"""Reference helper for Android 17 Launcher3 source-level icon overrides.

Not independently verified across AOSP branches. Review diff and build after use.
Usage: python3 scripts/apply_to_aosp.py /path/to/aosp
Requires licensed PNGs in assets/icons/ alongside this repository.
"""
import argparse
from pathlib import Path
import re
import shutil
import sys

THIS = Path(__file__).resolve().parent.parent
RESOURCE = THIS / "assets" / "icons"
EXAMPLE = THIS / "examples"
ICON_NAMES = (
    "par1ah_aether_phone.png",
    "par1ah_aether_messages.png",
    "par1ah_aether_camera.png",
    "par1ah_aether_settings.png",
    "par1ah_aether_files.png",
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("aosp_root", type=Path)
    args = ap.parse_args()
    launcher = args.aosp_root.expanduser().resolve() / "packages/apps/Launcher3"
    provider = launcher / "src/com/android/launcher3/icons/LauncherIconProvider.java"
    resolver = launcher / "src/com/android/launcher3/icons/Par1ahIconResolver.java"
    xml = launcher / "res/xml/par1ah_icon_map.xml"
    drawable = launcher / "res/drawable-nodpi"

    # Preflight: refuse to overwrite existing files or unfamiliar Launcher3 code.
    for path in (provider, launcher / "Android.bp"):
        if not path.is_file():
            sys.exit(f"Expected Android 17 Launcher3 source missing: {path}")
    for filename in ICON_NAMES:
        path = RESOURCE / filename
        if not path.is_file() or path.open("rb").read(8) != b"\x89PNG\r\n\x1a\n":
            sys.exit(f"Provide a valid PNG first: {path}")
    targets = [resolver, xml] + [drawable / filename for filename in ICON_NAMES]
    for t in targets:
        if t.exists():
            sys.exit(f"Refusing to replace existing file: {t}")

    source = provider.read_text(encoding="utf-8")
    edits = (
        ("import android.content.Context;",
         "import android.content.Context;\nimport android.content.pm.ApplicationInfo;\nimport android.content.pm.ComponentInfo;\nimport android.graphics.drawable.Drawable;"),
        ("    protected final ThemeManager mThemeManager;",
         "    protected final ThemeManager mThemeManager;\n"
         "    private final Par1ahIconResolver mPar1ahIconResolver;"),
        ("        mThemeManager = themeManager;",
         "        mThemeManager = themeManager;\n"
         "        mPar1ahIconResolver = new Par1ahIconResolver(context);"),
        ("    @Override\n    protected ThemeData getThemeDataForPackage",
         "    @Override\n"
         "    public Drawable getIcon(ComponentInfo info, int iconDpi) {\n"
         "        Drawable icon = mPar1ahIconResolver.resolve(info.packageName, iconDpi);\n"
         "        return icon != null ? icon : super.getIcon(info, iconDpi);\n"
         "    }\n\n"
         "    @Override\n"
         "    public Drawable getIcon(ApplicationInfo info, int iconDpi) {\n"
         "        Drawable icon = mPar1ahIconResolver.resolve(info.packageName, iconDpi);\n"
         "        return icon != null ? icon : super.getIcon(info, iconDpi);\n"
         "    }\n\n"
         "    @Override\n    protected ThemeData getThemeDataForPackage"),
        ("mThemeManager.getIconState().getThemeCode(),",
         'mThemeManager.getIconState().getThemeCode() + ":par1ah-community-icons-v0.1",'),
    )
    for old, new in edits:
        if source.count(old) != 1:
            sys.exit(f"Unexpected LauncherIconProvider structure, no changes made: {old[:55]!r}")
        source = source.replace(old, new, 1)

    # Only after successful validation and transformation do we write.
    drawable.mkdir(parents=True, exist_ok=True)
    for name in ICON_NAMES:
        shutil.copyfile(RESOURCE / name, drawable / name)
    shutil.copyfile(EXAMPLE / "par1ah_icon_map.xml", xml)
    shutil.copyfile(EXAMPLE / "Par1ahIconResolver.java", resolver)
    provider.write_text(source, encoding="utf-8")
    print("Source patch applied. Review git diff, build Launcher3QuickStep and test in Cuttlefish.")

if __name__ == "__main__":
    main()
