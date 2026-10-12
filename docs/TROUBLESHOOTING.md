# Troubleshooting the native icon build

## APK contains code but icon is unchanged

1. Confirm installed package identity and current code paths:

```bash
"$HOME/aosp/out/host/linux-x86/bin/adb" -s 0.0.0.0:6520 shell dumpsys package com.android.launcher3 | grep -E 'codePath=|resourcePath=|lastUpdateTime=|versionName='
```

A system app may have an updated APK under `/data/app/` while the original remains at `/system_ext/priv-app/`. Check the update rather than assuming the system partition location proves nothing was installed.

2. Check that the APK contains `Par1ahIconResolver` (DEX) and the XML/PNG resources. 3. Verify the package mapping matches the exact app installed. 4. Recompile with a revised cache state string and reinstall. 5. If necessary, add targeted development logging to the icon resolver to confirm `resolve(packageName, density)` is called and returns a drawable. Avoid speculative source edits.

**Do not run `pm clear com.android.launcher3` as the first response.** That erases launcher app state, including layout/preferences, and was not necessary for the verified implementation.

## Cuttlefish web viewer doesn't load

First confirm whether port 8443 is listening, then test HTTPS locally:

```bash
ss -ltnp | grep ':8443'
```

```bash
curl -k -I --max-time 10 https://127.0.0.1:8443/
```

An HTTP/2 200 indicates the web server responds, but does not prove video streaming or that the Android VM is healthy. Inspect WebRTC/browser errors separately from Android/ADB state.

## ADB command not found

In the verified AOSP environment ADB wasn't on the shell's default PATH. Use the built binary:

```bash
"$HOME/aosp/out/host/linux-x86/bin/adb" devices -l
```

## White backgrounds / transparent icons

RGBA means a PNG supports alpha. The existence of some transparent pixels alone does not prove the background is clear. Inspect corners and foreground edges, then check the rendered adaptive-icon background/normalization. Don't assume Cuttlefish invented the white area.

## Build Succeeded: 0 steps

Ninja did no compilation actions *in that invocation*. Check generated APK modification times and inspect packaged bytecode/resources. If necessary, inspect the build graph and target selection. Don't claim a compilation occurred solely because the final line says 'success'.

## Different device / OEM

This reference was tested on Android 17 Cuttlefish. An OEM's signing keys, privileged-app policy, launcher implementation, and package names can differ significantly. Don't replace a signed stock launcher on a physical device without a compatible image, an unlock/recovery plan, and a known-good rollback.
