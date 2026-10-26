// JSFuck fixture generator: the upstream jsfuck.com encoder (npm jsfuck 0.4.0 / github aemkei/jsfuck 0.5.0 under tools/).
// usage: JSF_DIR=<dir with jsfuck.js> node jsfuck_gen.js <str|alert|parent> <plain>
const [mode, s] = process.argv.slice(2);
const J = require(process.env.JSF_DIR + '/jsfuck.js').JSFuck;
const src = mode === 'alert' ? 'alert(' + JSON.stringify(s) + ')' : mode === 'parent' ? 'console.log(' + JSON.stringify(s) + ')' : s;
process.stdout.write(J.encode(src, mode !== 'str', mode === 'parent'));
