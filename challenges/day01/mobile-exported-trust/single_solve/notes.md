# Exported Trust — Day 01 mobile-android

## Artifact
exported_trust.apk (12704 bytes). Package com.huntress.mobile.d01.v073e9a824e9e. Case MOB-01-073E9A824E.

## Manifest
- MainActivity exported=true (LAUNCHER) — shows case reference text.
- ChallengeActivity exported=true, intent-filter VIEW+BROWSABLE, data scheme=huntress01 host=exported-trust pathPrefix=/unlock.

## ChallengeActivity logic (jadx)
Reads query params `answer` and `case_id` from the deep-link Uri, then builds:
  http://127.0.0.1:19090/mobile/attempt/d01-ec1629b73a8465b3/evidence?case_id=<case_id>&client_secret=SECRET-A8614359B0F872F166A024&proof=<answer>
Loads it in a WebView. Embedded client credential = SECRET-A8614359B0F872F166A024.

## Backend reachability
- hb exec curl 127.0.0.1:19090 -> connection refused. 10.0.0.219:19090 -> timeout. GM proxy only serves list/status/artifact/download/start/submit/retry (openapi). No mobile backend route. Backend is narrative; not live.

## Answer source
assets/huntress_puzzle.json: {"schema":"huntress.mobile.puzzle.v1","day":1,"codec":"plain","data":"ANS-DACC86F43B0B1C1A"}
codec=plain -> data is the evidence code verbatim. Matches answer_format ANS- + 16 hex.

hypothesis: answer = puzzle data decoded per codec | evidence: asset codec=plain data=ANS-DACC86F43B0B1C1A | result: submitting
