/*
 * Copyright 2026 PAR1AHWARE contributors
 * SPDX-License-Identifier: Apache-2.0
 */
package com.android.launcher3.icons;

import android.content.Context;
import android.content.res.Resources;
import android.content.res.XmlResourceParser;
import android.graphics.drawable.Drawable;
import android.text.TextUtils;
import android.util.ArrayMap;
import android.util.Log;

import com.android.launcher3.R;

import org.xmlpull.v1.XmlPullParser;

import java.util.Map;

/**
 * Full-color launcher icon lookup by application package name.
 * Returns null for unmapped packages to preserve the original app icon.
 */
public final class Par1ahIconResolver {
    private static final String TAG = "Par1ahIconResolver";
    private final Context mContext;
    private final Map<String, Integer> mIcons = new ArrayMap<>();

    public Par1ahIconResolver(Context context) {
        mContext = context;
        loadIconMap();
    }

    private void loadIconMap() {
        try (XmlResourceParser parser =
                     mContext.getResources().getXml(R.xml.par1ah_icon_map)) {
            int event;
            while ((event = parser.next()) != XmlPullParser.END_DOCUMENT) {
                if (event != XmlPullParser.START_TAG || !"icon".equals(parser.getName())) {
                    continue;
                }
                String packageName = parser.getAttributeValue(null, "package");
                int drawableId = parser.getAttributeResourceValue(null, "drawable", 0);
                if (!TextUtils.isEmpty(packageName) && drawableId != 0) {
                    mIcons.put(packageName, drawableId);
                }
            }
        } catch (Exception e) {
            Log.e(TAG, "Unable to load icon map", e);
        }
    }

    public Drawable resolve(String packageName, int density) {
        Integer drawableId = mIcons.get(packageName);
        if (drawableId == null) return null;
        try {
            return mContext.getResources().getDrawableForDensity(
                    drawableId, density, mContext.getTheme());
        } catch (Resources.NotFoundException e) {
            Log.e(TAG, "Missing icon for " + packageName, e);
            return null;
        }
    }
}
