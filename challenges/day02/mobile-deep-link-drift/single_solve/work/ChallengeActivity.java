package com.huntress.mobile.d02.v15b6e1b8356f;
public class ChallengeActivity extends android.app.Activity {

    public ChallengeActivity()
    {
        return;
    }

    protected void onCreate(android.os.Bundle p9)
    {
        super.onCreate(p9);
        android.content.Intent v0 = this.getIntent();
        String v2_0 = v0.getStringExtra("answer");
        String v3_0 = v0.getStringExtra("case_id");
        android.net.Uri v4 = v0.getData();
        if (v4 != null) {
            v2_0 = v4.getQueryParameter("answer");
            v3_0 = v4.getQueryParameter("case_id");
        }
        if ((v2_0 == null) || (v3_0 == null)) {
            android.webkit.WebView v6_1 = new android.widget.TextView(this);
            v6_1.setText("Missing challenge answer or case_id");
            this.setContentView(v6_1);
            return;
        } else {
            String v5_1 = new StringBuilder();
            v5_1.append("http://127.0.0.1:19090/mobile/attempt/d02-522ef6efdbc1d702/evidence?case_id=");
            v5_1.append(android.net.Uri.encode(v3_0));
            v5_1.append("&client_secret=SECRET-D47A8832A24206CA36B2C4&proof=");
            v5_1.append(android.net.Uri.encode(v2_0));
            String v5_2 = v5_1.toString();
            android.webkit.WebView v6_5 = new android.webkit.WebView(this);
            this.setContentView(v6_5);
            v6_5.loadUrl(v5_2);
            return;
        }
    }
}
