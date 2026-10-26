// JSFuck oracle: run the program in a node vm context (V8), capture its value / alert / console.log argument.
// usage: node jsfuck_oracle.js < encoded.txt
const vm = require('vm');
let code = require('fs').readFileSync(0, 'utf8'), seen = null;
const ctx = vm.createContext({alert: x => { seen = String(x); }, console: {log: x => { seen = String(x); }}});
const v = vm.runInContext(code, ctx, {timeout: 5000});
process.stdout.write(seen !== null ? seen : String(v));
