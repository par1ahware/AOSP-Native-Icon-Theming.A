# Step-by-step tutorial: VS Code → AOSP source → Cuttlefish

This is a **source-level launcher modification**, not a VS Code extension, icon-pack APK, or change to the Google Play apps themselves. VS Code is just the editor; Android's Soong build system compiles the source.

## 1. Establish the target and protect the baseline

Use an already buildable Android 17 AOSP checkout. For the Cuttlefish virtual phone tested in this project:

```bash
cd "$HOME/aosp"
source build/envsetup.sh
lunch aosp_cf_x86_64_only_phone-aosp_current-userdebug
```

Confirm that the running launcher is Quickstep-based:

```bash
"$HOME/aosp/out/host/linux-x86/bin/adb" -s 0.0.0.0:6520 shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.HOME
```

The tested device returned `com.android.launcher3/.uioverrides.QuickstepLauncher`. Its system APK was at `/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk`.

Create a local development branch before changing the launcher:

```bash
git -C "$HOME/aosp/packages/apps/Launcher3" switch -c native-icon-theming
```

If already on a branch, choose an appropriate different name. Keep the stock build images and a known-good checkout independently backed up. Do not edit or distribute signing keys.

## 2. Identify *launchable application packages*

In Cuttlefish, these were the five tested package names:

| App | Package |
|---|---|
| Phone | `com.android.dialer` |
| Messages | `com.android.messaging` |
| Camera | `com.android.camera2` |
| Settings | `com.android.settings` |
| Files | `com.android.documentsui` |

Verify packages on your target rather than assuming they match. For example, `com.android.phone` is the platform's telephony service and is **not** the dialer app.

```bash
"$HOME/aosp/out/host/linux-x86/bin/adb" -s 0.0.0.0:6520 shell pm list packages | grep -Ei 'dialer|messag|camera|settings|documentsui'
```

## 3. Prepare your own full-color PNG assets

Use individually cropped PNG images, preferably with an alpha channel; the tested assets were 1254×1254 RGBA. `RGBA` means an alpha channel **exists**, but doesn't mean the entire background is transparent. Inspect corner alpha and the visible result in Launcher3. White squares are *not* necessarily caused by Cuttlefish itself.

Put your images in the AOSP launcher resource directory using Android-safe resource names (`a-z`, `0-9`, underscores):

```text
packages/apps/Launcher3/res/drawable-nodpi/
  par1ah_aether_phone.png
  par1ah_aether_messages.png
  par1ah_aether_camera.png
  par1ah_aether_settings.png
  par1ah_aether_files.png
```

You supply your **own** assets. This public tutorial intentionally does not contain PAR1AH's original artwork.

## 4. Add the icon map

Save [`examples/par1ah_icon_map.xml`](../examples/par1ah_icon_map.xml) to:

```text
packages/apps/Launcher3/res/xml/par1ah_icon_map.xml
```

Each entry maps an installed application package to an Android drawable resource, e.g.:

```xml
<icon package="com.android.dialer" drawable="@drawable/par1ah_aether_phone" />
```

The map is a **new** resource. It is not the existing `grayscale_icon_map.xml`, which feeds a monochrome-icon path.

## 5. Add the resolver class

Save [`examples/Par1ahIconResolver.java`](../examples/Par1ahIconResolver.java) to:

```text
packages/apps/Launcher3/src/com/android/launcher3/icons/Par1ahIconResolver.java
```

The resolver reads the map with `Resources.getXml`, matches package names, and returns a `Drawable` at the requested density. If no mapping exists, it returns `null` so Android's original icon logic remains available.

## 6. Integrate with LauncherIconProvider.java

Open the existing file in VS Code:

```text
packages/apps/Launcher3/src/com/android/launcher3/icons/LauncherIconProvider.java
```

The tested approach added:

```java
import android.content.pm.ApplicationInfo;
import android.content.pm.ComponentInfo;
import android.graphics.drawable.Drawable;
```

Add a field alongside the existing `ThemeManager` field:

```java
private final Par1ahIconResolver mPar1ahIconResolver;
```

Initialize it in the `@Inject` constructor after assigning `mThemeManager`:

```java
mPar1ahIconResolver = new Par1ahIconResolver(context);
```

Add these two overrides to `LauncherIconProvider`:

```java
@Override
public Drawable getIcon(ComponentInfo info, int iconDpi) {
    Drawable icon = mPar1ahIconResolver.resolve(info.packageName, iconDpi);
    return icon != null ? icon : super.getIcon(info, iconDpi);
}

@Override
public Drawable getIcon(ApplicationInfo info, int iconDpi) {
    Drawable icon = mPar1ahIconResolver.resolve(info.packageName, iconDpi);
    return icon != null ? icon : super.getIcon(info, iconDpi);
}
```

This hooks the **two public** `getIcon` overloads used by launcher icon retrieval. The shared Android `IconProvider` also has a **private** overload that cannot be overridden by subclasses. Do not rewrite that shared system library for this use case.

To account for launcher icon-cache refreshes, the tested implementation also changed its existing `updateSystemState()` theme-code argument from:

```java
mThemeManager.getIconState().getThemeCode(),
```

into:

```java
mThemeManager.getIconState().getThemeCode() + ":par1ah-custom-icons-v0.1",
```

Advance this suffix when the static icon artwork/mappings change. This is a practical first-stage cache revision, **not** a general-purpose live theme-switching system.

> **Optional:** [`scripts/apply_to_aosp.py`](../scripts/apply_to_aosp.py) performs the above steps on a known matching source structure, after checking inputs. The original implementation was manually integrated and functionally tested; the helper script is not a substitute for a code review and build.

## 7. Build the launcher module

From the same AOSP target configuration:

```bash
cd "$HOME/aosp" && source build/envsetup.sh && lunch aosp_cf_x86_64_only_phone-aosp_current-userdebug && m Launcher3QuickStep -j8
```

The expected output is at:

```text
out/target/product/vsoc_x86_64_only/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk
```

A `Build Succeeded: 0 steps` message means the build system found no work to do. To verify actual changes were included, inspect the DEX strings and APK resource listing:

```bash
unzip -p "$HOME/aosp/out/target/product/vsoc_x86_64_only/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk" 'classes*.dex' | strings | grep 'Par1ahIconResolver'
```

```bash
unzip -l "$HOME/aosp/out/target/product/vsoc_x86_64_only/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk" | grep -E 'par1ah_icon_map|par1ah_aether_phone'
```

## 8. Deploy to Cuttlefish

Use the APK corresponding to the currently selected target. For the tested x86_64 Cuttlefish phone:

```bash
"$HOME/aosp/out/host/linux-x86/bin/adb" -s 0.0.0.0:6520 install -r "$HOME/aosp/out/target/product/vsoc_x86_64_only/system_ext/priv-app/Launcher3QuickStep/Launcher3QuickStep.apk"
```

Android must accept the APK's signing lineage and privileges. **Do not uninstall the privileged system launcher** or clear its data to force an install. If installation fails, stop and inspect the precise error.

Restart the launcher without clearing its state:

```bash
"$HOME/aosp/out/host/linux-x86/bin/adb" -s 0.0.0.0:6520 shell am force-stop com.android.launcher3
"$HOME/aosp/out/host/linux-x86/bin/adb" -s 0.0.0.0:6520 shell input keyevent KEYCODE_HOME
```

For the tested Cuttlefish WebRTC viewer, open `https://localhost:8443` in a browser on the host.

## 9. Verify functionality

Open the app drawer and visually confirm the replacement artwork on **all mapped apps**. Then open Phone, Messages, Camera, Settings, and Files, and confirm they still launch. Verify that unknown apps keep their original icons. Also check the home screen, app drawer, and folders; compare icon backgrounds and masks at full size. These are the *functional tests* that passed in the original PAR1AHWARE implementation.

The launcher update in `/data/app/` may coexist with the original `/system_ext/priv-app/` APK. `pm path` alone is not always enough to diagnose the active update. See [troubleshooting](TROUBLESHOOTING.md).

## 10. Commit and share only the reusable lesson

Check your local changes, review each asset and source file, and commit in your own Launcher3 project. Keep private configs, keys, telemetry, image assets you cannot redistribute, and device logs out of public GitHub. For a standalone tutorial repository, share instructions, a clean example, and reference code—not an entire private AOSP checkout.
