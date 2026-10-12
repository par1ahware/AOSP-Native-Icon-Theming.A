# Native full-color app icons in Android 17 AOSP Launcher3QuickStep

**PAR1AHWARE Developer Series #001** — a documented Android Open Source Project (AOSP) source-level customization.

This tutorial demonstrates how to display your own full-color PNG icons in the **built-in Launcher3QuickStep launcher**, rather than installing a third-party launcher or editing other applications' APKs. It is based on an implementation tested on an Android 17 x86_64 **Cuttlefish** virtual phone.

> **Scope:** Android 17 AOSP, `Launcher3QuickStep`, Cuttlefish target `aosp_cf_x86_64_only_phone-aosp_current-userdebug`. Other branches, devices, signing setups, and launchers can differ. The reusable helper included here is an *illustrative automation of the manually verified approach*; independently test it on your own checkout before relying on it.

## What was actually verified

The PAR1AHWARE development team modified the Launcher3 source to add `Par1ahIconResolver.java`, an XML package-to-resource map, resource PNGs, and a provider hook. The modified `Launcher3QuickStep` module compiled, installed as an updated system application in Cuttlefish, and displayed custom icons for **Phone, Messages, Camera, Settings, and Files**. All five target apps opened correctly in the virtual phone. Stock icons remained as fallbacks for apps without custom artwork.

Verified checkpoint in the original local AOSP checkout: `c8cc75ddc5` — `PAR1AH Launcher v0.2: integrate native AetherDrift icons`. This commit is a **local development commit**, not a published GitHub revision. No claims are made about physical-device testing or other Android versions.

## How it works

1. Add full-color PNGs to `packages/apps/Launcher3/res/drawable-nodpi/`.
2. Map package names to drawable resources in `res/xml/par1ah_icon_map.xml`.
3. Add a tiny resolver class that returns a drawable, or `null` if no matching icon exists.
4. Extend Launcher3's own `LauncherIconProvider` to use the resolver before the original icon provider.
5. Add an icon-cache state revision so a previously cached icon can refresh.
6. Build `Launcher3QuickStep`, deploy the test APK to Cuttlefish, and check results.

**This only changes how icons appear in Launcher3.** It does not modify the underlying Phone, Camera, Settings, etc. applications, nor does it change icons throughout every Android system surface. It does not yet provide runtime theme installation or live switching.

## Contents

- [`docs/STEP_BY_STEP.md`](docs/STEP_BY_STEP.md) — VS Code to AOSP build to Cuttlefish verification.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — launcher source-code reasoning and scope.
- [`docs/TROUBLESHOOTING.md`](docs/TROUBLESHOOTING.md) — cache, old APKs, missing artwork, and common terminal errors.
- [`examples/Par1ahIconResolver.java`](examples/Par1ahIconResolver.java) — standalone reference implementation.
- [`examples/par1ah_icon_map.xml`](examples/par1ah_icon_map.xml) — sample package mappings.
- [`scripts/apply_to_aosp.py`](scripts/apply_to_aosp.py) — optional, guarded development helper for a matching Android 17 checkout.
- [`assets/icons/README.md`](assets/icons/README.md) — supply your **own** PNGs; original PAR1AH artwork is not redistributed.

## Prerequisites

- An initialized and buildable Android 17 AOSP checkout.
- Launcher module source at `packages/apps/Launcher3/`.
- A working Cuttlefish virtual phone and matching ADB binary.
- Five **user-supplied**, appropriately licensed PNG icons (or start with one).
- Python 3 for the optional helper; VS Code or another text editor for source review.

## Quick start

Read the [step-by-step guide](docs/STEP_BY_STEP.md) before changing source files. Work on a development branch and retain your known-good Android images. The optional helper is conservative: it checks expected source anchors and refuses conflicting existing files instead of overwriting unknown changes.

## Privacy and distribution

This repository deliberately excludes full AOSP source, local user paths, ADB logs, keystores, signing keys, proprietary drivers, original PAR1AH artwork, and private OS components. The tutorial and new reference code are offered under Apache-2.0; Android upstream components retain their respective licenses and copyright notices.

**Author:** PAR1AHWARE · **Principle:** Borrow → Adapt → Build → Share.