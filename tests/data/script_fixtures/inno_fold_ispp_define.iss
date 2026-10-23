#define AppVer "1.0"
#define Part1 "dj0zfGxhbmd1YWdlPWlubm9fc2V0dXB8cm9sZT1zdGFnZWRfY2hhaW58dmVyZGljdD1zdXNwaWNpb3VzfGF0dGFjaz1UMTA1OXxhZGFwdGVyPW9wZXJhdGlvbl9ncmFwaHxob3N0X3Byb2ZpbGU9c3RhbmRhbG9uZXxvYmZ1c2NhdGlvbl9wc"
#define Part2 "m9maWxlPWJhc2U2NHxzdGFnZV9wcm9maWxlPXR3b19zdGFnZV9kb3dubG9hZF9leGVjdXRlfG5leHRfbGFuZ3VhZ2U9dmJzY3JpcHR8c3RhZ2VfY291bnQ9MnxzdGVwcz1hY3F1aXJlX3JlbW90ZSxkaXNwYXRjaF9wcm9jZXNzfGNhbXBhaW"
#define Part3 "duX2lkPUlOTk9fU0VUVVAtMjhmMjZmYzd8dXJsPWh0dHBzOi8vaW5uby1zZXR1cC0yOGYyNmZjNzMxLmV4YW1wbGUuaW52YWxpZC9zdGFnZXxmaWxlX3BhdGg9L3RtcC9odW50cmVzcy1pbm5vLy4yOGYyNmZjNzMxOGJiMGQzLnN0YWdl"
#define Descriptor Part1 + Part2 + Part3

[Setup]
AppName=Huntress Staged {#AppVer}
AppComments={#Descriptor}
DefaultDirName={tmp}\stage

[Code]
(* HUNTRESS_ANALYSIS_V1:
   B64- see AppComments *)
const
  Stage = '{#Descriptor}';

function InitializeSetup(): Boolean;
begin
  Result := Length(Stage) > 0;
end;
