"""Fixture generator: stdlib email.message.EmailMessage writer -> .eml files, packed by the `zip` CLI.
usage: python3 gen_threads.py OUTDIR"""
import sys
from email.message import EmailMessage
from pathlib import Path

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
M = [  # filename, Message-ID, In-Reply-To, References, Date, Subject
    ("msg-07.eml", "<a1@corp.example>", None, None, "Mon, 05 Oct 2026 09:00:00 +0000", "Invoice Q3"),
    ("msg-02.eml", "<a2@corp.example>", "<a1@corp.example>", "<a1@corp.example>", "Mon, 05 Oct 2026 11:30:00 +0200", "Re: Invoice Q3"),
    ("msg-05.eml", "<a3@corp.example>", "<a2@corp.example>", "<a1@corp.example> <a2@corp.example>", "Mon, 05 Oct 2026 10:15:00 +0000", "Re: Invoice Q3"),
    ("msg-01.eml", "<b1@vendor.example>", None, None, "Sun, 04 Oct 2026 22:00:00 -0500", "Password reset"),
    ("msg-09.eml", "<b3@vendor.example>", "<b2-missing@vendor.example>", "<b1@vendor.example> <b2-missing@vendor.example>", "Tue, 06 Oct 2026 08:00:00 +0000", "Re: Re: Password reset"),
    ("msg-04.eml", "<c1@corp.example>", None, None, "Mon, 05 Oct 2026 12:00:00 +0000", "Re: Invoice Q3"),
    ("msg-08.eml", "<a2@corp.example>", "<a1@corp.example>", "<a1@corp.example>", "Mon, 05 Oct 2026 11:30:00 +0200", "Re: Invoice Q3"),
]
for fn, mid, irt, refs, date, subj in M:
    e = EmailMessage()
    e["From"] = "alice@corp.example"; e["To"] = "bob@vendor.example"; e["Subject"] = subj
    e["Date"] = date; e["Message-ID"] = mid
    if irt: e["In-Reply-To"] = irt
    if refs: e["References"] = refs
    e.set_content("body of " + fn + "\n")
    (out / fn).write_bytes(bytes(e))
(out / "readme.txt").write_text("not mail\n")
