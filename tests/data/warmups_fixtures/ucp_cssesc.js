// usage: node ucp_cssesc.js  (stdin -> stdout) via npm cssesc (Mathias Bynens) with {escapeEverything: true}
const cssesc = require(process.env.CSSESC);
const d = require("fs").readFileSync(0, "utf8").replace(/\n$/, "");
process.stdout.write(cssesc(d, {escapeEverything: true}));
