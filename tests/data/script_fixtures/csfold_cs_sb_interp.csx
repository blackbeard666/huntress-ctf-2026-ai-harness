#nullable enable
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
const string p0_dbe52f93 = "dj0zfGxhbmd1YWdlPWNzaGFycF9zY3JpcHR8cm9sZT1sYXVuY2hlcnx2ZXJkaWN0PXN1c3BpY2lvdXN8YXR0YWNrPVQxMDU5fGFkYXB0ZXI9cHJvY2Vzc19idWlsZGVyfGhvc3RfcHJ";
const string p1_dbe52f93 = "vZmlsZT1zdGFuZGFsb25lfG9iZnVzY2F0aW9uX3Byb2ZpbGU9YmFzZTY0fHN0YWdlX3Byb2ZpbGU9dHdvX3N0YWdlX2Rvd25sb2FkX2V4ZWN1dGV8bmV4dF9sYW5ndWFnZT1iYXRjaH";
const string p2_dbe52f93 = "xzdGFnZV9jb3VudD0yfHN0ZXBzPWFjcXVpcmVfcmVtb3RlLGRpc3BhdGNoX3Byb2Nlc3N8Y2FtcGFpZ25faWQ9Q1NIQVJQX1NDUklQVC0yNDk5M2E3Y3x1cmw9aHR0cHM6Ly9jc2hhc";
const string p3_dbe52f93 = "nBfc2NyaXB0LTI0OTkzYTdjNjAuZXhhbXBsZS5pbnZhbGlkL3N0YWdlfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLWNzaGFycF9zY3JpcHQvLjI0OTkzYTdjNjA4ZjQ3YjUuc3RhZ2U=";
var sb_dbe52f93 = new StringBuilder();
sb_dbe52f93.Append(p0_dbe52f93).Append(p1_dbe52f93);
sb_dbe52f93.Append($"{p2_dbe52f93}{p3_dbe52f93}");
string descriptor_dbe52f93 = sb_dbe52f93.ToString();
IReadOnlyDictionary<string,string> BuildPlan_dbe52f93() => new Dictionary<string,string> { ["descriptor"] = descriptor_dbe52f93 };
