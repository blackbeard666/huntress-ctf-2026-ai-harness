// Huntress Script Triage -- inert static-analysis fixture (wsh_jscript_windows)
var decode_a78fb44a = function decode_a78fb44a_body(v_a19c) {
  var v_b27e = [];
  for (var i = 0; i < v_a19c.length; i++) { v_b27e.push((v_a19c[i] + 31) % 256); }
  return v_b27e;
};
var recover_2c6c0e9c = function recover_2c6c0e9c_body() {
  // configuration reconstruction
  var packedText = "5c:03:54:55:46:51:54:03:1b:3c:03:42:44:52:56:4a:53:46:40:53:46:4e:50:55:46:03:0d:03:58:53:4a:55:46:40:47:4a:4d:46:03:0d:03:45:4a:54:51:42:55:44:49:40:51:53:50:44:46:54:54:03:0d:03:49:42:4f:45:50:47:47:40:54:44:53:4a:51:55:03:3e:0d:03:42:45:42:51:55:46:53:03:1b:03:2e:4a:44:53:50:54:50:47:55:0f:39:2e:2d:29:35:35:31:03:0d:03:57:42:4d:56:46:54:03:1b:5c:03:44:42:4e:51:42:4a:48:4f:40:4a:45:03:1b:03:44:42:4e:51:42:4a:48:4f:0e:19:16:13:14:14:14:14:19:16:13:03:0d:03:56:53:4d:03:1b:03:49:55:55:51:54:1b:10:10:19:16:13:14:14:14:14:19:16:13:0f:46:59:42:4e:51:4d:46:0f:4a:4f:57:42:4d:4a:45:10:19:16:18:15:16:43:19:18:0f:45:42:55:03:0d:03:56:54:46:53:40:42:48:46:4f:55:03:1b:03:29:56:4f:55:53:46:54:54:2d:42:43:10:19:16:13:14:14:14:14:19:16:13:03:0d:03:47:4a:4d:46:40:51:42:55:49:03:1b:03:24:1b:3d:3d:36:54:46:53:54:3d:3d:31:56:43:4d:4a:44:3d:3d:29:56:4f:55:53:46:54:54:2d:42:43:3d:3d:54:55:42:48:46:0e:19:16:13:14:14:14:14:19:16:13:0f:45:42:55:03:0d:03:53:46:48:4a:54:55:53:5a:40:51:42:55:49:03:1b:03:29:2c:24:36:3d:3d:34:50:47:55:58:42:53:46:3d:3d:29:56:4f:55:53:46:54:54:2d:42:43:3d:3d:25:4a:54:51:50:54:42:43:4d:46:3d:3d:19:16:13:14:14:14:14:19:16:13:03:0d:03:4f:46:59:55:40:54:55:42:48:46:03:1b:03:53:46:54:50:56:53:44:46:0e:54:42:4e:51:4d:46:0f:51:54:12:03:5e:0d:03:54:55:42:48:46:24:50:56:4f:55:03:1b:15:5e";
  var packedParts = packedText.split(":");
  var v_a19c = [];
  for (var hi = 0; hi < packedParts.length; hi++) { v_a19c.push(parseInt(packedParts[hi], 16)); }
  var v_f602 = "PROCESSOR_ARCHITECTURE";
  var v_b27e = [];
  try { v_b27e = decode_a78fb44a(v_a19c); } catch (ignored) { v_b27e = []; }
  var v_c304;
  v_c304 = "";
  for (var bi = 0; bi < v_b27e.length; bi++) { v_c304 += String.fromCharCode(v_b27e[bi]); }
  return v_c304;
  // end reconstruction
};
var inspect_15693a0d = function inspect_15693a0d_body() {
  var v_d41a = eval("(" + recover_2c6c0e9c() + ")");
  var v_e598 = new Object();
  v_e598.steps = v_d41a.steps;
  v_e598.adapter = v_d41a.adapter;
  v_e598.values = v_d41a.values;
  v_e598.stageCount = v_d41a.stageCount;
  return v_e598;
};
