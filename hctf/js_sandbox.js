// Generic static-analysis sandbox for WSH JScript fixtures (triage only, never a solver): run the file in an empty node
// `vm` context (no require/process/fs; WScript/ActiveXObject are inert stubs; eval is captured), then call every
// zero-parameter top-level function and print what came back. Prints JSON: {captures: [{via, name, value}], error}.
//   node hctf/js_sandbox.js <file.js> [timeout_ms]
"use strict";
const fs = require("fs");
const vm = require("vm");
const file = process.argv[2];
const budget = parseInt(process.argv[3] || "800", 10);
const caps = [];
const keep = (via, name, v) => {
  let s;
  try { s = typeof v === "string" ? v : JSON.stringify(v); } catch (e) { return; }
  if (s && s.length > 2 && s.length < 20000) caps.push({ via, name, value: s });
};
const inert = new Proxy(function () {}, { get: () => inert, apply: () => inert, construct: () => inert });
const ctx = {
  WScript: { Echo: (...a) => keep("echo", "WScript.Echo", a.join(" ")), Arguments: { length: 0, Item: () => "" },
             Quit: () => {}, Sleep: () => {}, ScriptFullName: "C:\\fixture.js", CreateObject: () => inert },
  ActiveXObject: function () { return inert; }, GetObject: () => inert,
  console: { log: (...a) => keep("console", "console.log", a.join(" ")) },
};
ctx.eval = (code) => { keep("eval", "eval", String(code)); return vm.runInContext(String(code), ctx, { timeout: budget }); };
vm.createContext(ctx);
let error = null;
try {
  vm.runInContext(fs.readFileSync(file, "utf8"), ctx, { timeout: budget, filename: file });
} catch (e) { error = String(e && e.message || e).slice(0, 200); }
for (const name of Object.keys(ctx)) {
  const f = ctx[name];
  if (typeof f !== "function" || f.length !== 0 || ["eval", "ActiveXObject", "GetObject"].includes(name)) continue;
  try {
    const r = vm.runInContext(`(${name})()`, ctx, { timeout: budget });
    if (r !== undefined && r !== null) keep("call", name, r);
  } catch (e) { /* a function that needs arguments or real host objects */ }
}
process.stdout.write(JSON.stringify({ captures: caps, error }));
