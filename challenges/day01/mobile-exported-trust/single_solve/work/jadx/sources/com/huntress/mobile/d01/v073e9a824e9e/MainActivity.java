package com.huntress.mobile.d01.v073e9a824e9e;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

/* JADX INFO: loaded from: classes.dex */
public class MainActivity extends Activity {
    @Override // android.app.Activity
    protected void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        TextView textView = new TextView(this);
        textView.setText("Huntress Mobile Arena — Day 01\\nExported Trust\\n\\nCase reference: MOB-01-073E9A824E\\n\\nAnalyze the public APK and cross the exported Activity and caller trust boundary.");
        textView.setTextSize(18.0f);
        textView.setPadding(40, 40, 40, 40);
        setContentView(textView);
    }
}
