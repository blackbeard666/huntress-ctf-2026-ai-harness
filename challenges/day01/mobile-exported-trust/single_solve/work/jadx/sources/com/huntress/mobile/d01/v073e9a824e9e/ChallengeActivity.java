package com.huntress.mobile.d01.v073e9a824e9e;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.WebView;
import android.widget.TextView;

/* JADX INFO: loaded from: classes.dex */
public class ChallengeActivity extends Activity {
    @Override // android.app.Activity
    protected void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        Intent intent = getIntent();
        String stringExtra = intent.getStringExtra("answer");
        String stringExtra2 = intent.getStringExtra("case_id");
        Uri data = intent.getData();
        if (data != null) {
            stringExtra = data.getQueryParameter("answer");
            stringExtra2 = data.getQueryParameter("case_id");
        }
        if (stringExtra == null || stringExtra2 == null) {
            TextView textView = new TextView(this);
            textView.setText("Missing challenge answer or case_id");
            setContentView(textView);
            return;
        }
        String str = "http://127.0.0.1:19090/mobile/attempt/d01-ec1629b73a8465b3/evidence?case_id=" + Uri.encode(stringExtra2) + "&client_secret=SECRET-A8614359B0F872F166A024&proof=" + Uri.encode(stringExtra);
        WebView webView = new WebView(this);
        setContentView(webView);
        webView.loadUrl(str);
    }
}
