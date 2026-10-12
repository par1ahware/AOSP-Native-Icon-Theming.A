# Architecture notes

The verified Android 17 Launcher3QuickStep checkout had these components:

- `src/com/android/launcher3/BubbleTextView.java`: applies icon and label information to home-screen and app-drawer views.
- `src/com/android/launcher3/model/data/ItemInfoWithIcon.java`: creates `FastBitmapDrawable` from cached `BitmapInfo` and theme state.
- `src/com/android/launcher3/graphics/ThemeManager.kt`: manages icon themes, preferences, shape data, state, listeners, and factory registrations.
- `src/com/android/launcher3/graphics/theme/MonoIconThemeFactory.kt`: maps a monochrome theme ID to the stock `MonoIconThemeController`.
- `frameworks/libs/systemui/iconloaderlib/src/com/android/launcher3/icons/mono/MonoIconThemeController.kt`: monochrome bitmap/color transformations, not full-color PNG substitution.
- `src/com/android/launcher3/icons/LauncherIconProvider.java`: Launcher3's `IconProvider` subclass and the chosen source-level integration point.
- `src/com/android/launcher3/icons/IconCache.kt`: caches app titles/bitmap icons; source state revisions affect refresh behavior.

## Decision

Keep `ThemeManager` and Android's stock themed-icon architecture intact. Resolve user-supplied full-color icons by package in `LauncherIconProvider` and return the original icon if no replacement is available. This does not require changing underlying app APKs or Android's common framework iconloaderlib.

## Limitations to address in a production theme engine

- **Runtime theme selection:** example has one compiled-in map, not a pack installer.
- **Cache revisions:** manual source suffix used in the tested prototype. Production should have a reliable theme ID plus pack version and trigger cache updates on changes.
- **Per-activity targeting:** prototype maps packages, not individual activities.
- **Calendar/clock dynamism:** replacement of those packages can suppress calendar date/clock animation. Define explicit policy and preserve clock features when needed.
- **Accessibility and multi-user:** test work profiles, aliases, badge behavior, pending/archived app states, safe mode, high contrast, folders, app shortcuts, and dynamic icons.
- **Icon mask/white-square issues:** distinguish transparency within PNGs from `AdaptiveIconDrawable` backgrounds and Launcher3 icon normalization.
- **System surfaces:** launcher appearance does not automatically replace icons in Settings, recents, notifications, or third-party apps.
- **Device images:** deploying an APK update to Cuttlefish is not equivalent to generating a full production PAR1AH OS image.

Next logical design: signed theme packs with a manifest, safe validation, explicit owner selection, package/activity-level icon mappings, unpacking into managed application storage, deterministic cache invalidation, and rollback to original icons. Treat installed themes as untrusted data, never execute theme-provided code.
