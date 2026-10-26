// Independent Befunge-93/98 and ><> reader (esolangs.org semantics), never lib/: reads $encoded, runs it, prints what
// the program outputs. argv[2] = "b93" (80x25 torus, grown to the text), "b98" (adds ; a-f ' to b93) or "fish".
// Exits 1 when the program never halts in 1e6 steps, errors (><> "something smells fishy"), or prints no text.
const mode = process.argv[2] || "b93";
const rows = (process.env.encoded || "").split(/\r?\n/);
const fish = mode === "fish";
let W = Math.max(...rows.map((r) => r.length)), H = rows.length;
if (!fish) { W = Math.max(W, 80); H = Math.max(H, 25); }
const grid = Array.from({ length: H }, (_, j) => Array.from({ length: W }, (_, i) => (rows[j] || "").charCodeAt(i) || 32));
const st = [];
const pop = () => (st.length ? st.pop() : (fish ? die("pop on empty stack") : 0));
function die(m) { console.error(m); process.exit(1); }
let x = 0, y = 0, dx = 1, dy = 0, quote = 0, out = "", halted = false;
const step = () => { x = (x + dx + W) % W; y = (y + dy + H) % H; };
for (let n = 0; n < 1e6 && !halted; n++) {
  const c = grid[y][x], ch = String.fromCharCode(c);
  if (quote) { if (c === quote) quote = 0; else st.push(c); step(); continue; }
  if (/[0-9]/.test(ch)) st.push(c - 48);
  else if ((fish || mode === "b98") && /[a-f]/.test(ch)) st.push(c - 87);
  else if (ch === '"' || (ch === "'" && fish)) quote = c;
  else if (ch === ">") { dx = 1; dy = 0; } else if (ch === "<") { dx = -1; dy = 0; }
  else if (ch === "^") { dx = 0; dy = -1; } else if (ch === "v") { dx = 0; dy = 1; }
  else if (fish) {
    if (ch === "/") [dx, dy] = [-dy, -dx];
    else if (ch === "\\") [dx, dy] = [dy, dx];
    else if (ch === "|") dx = -dx;
    else if (ch === "_") dy = -dy;
    else if (ch === "#") { dx = -dx; dy = -dy; }
    else if ("+-*,%=)(".includes(ch)) {
      const b = pop(), a = pop();
      if ((ch === "," || ch === "%") && b === 0) die("division by zero");
      st.push({ "+": a + b, "-": a - b, "*": a * b, ",": a / b, "%": ((a % b) + b) % b, "=": +(a === b), ")": +(a > b), "(": +(a < b) }[ch]);
    } else if (ch === "!") step();
    else if (ch === "?") { if (pop() === 0) step(); }
    else if (ch === ":") { const v = pop(); st.push(v, v); }
    else if (ch === "~") pop();
    else if (ch === "$") { const b = pop(), a = pop(); st.push(b, a); }
    else if (ch === "@") { const c3 = pop(), b = pop(), a = pop(); st.push(c3, a, b); }
    else if (ch === "r") st.reverse();
    else if (ch === "l") st.push(st.length);
    else if (ch === "o") out += String.fromCodePoint(pop());
    else if (ch === "n") out += String(pop());
    else if (ch === ";") halted = true;
    else if (ch !== " ") die(`fishy instruction ${JSON.stringify(ch)}`);
  } else {
    if ("+-*/%`".includes(ch)) {
      const b = pop(), a = pop();
      st.push({ "+": a + b, "-": a - b, "*": a * b, "/": b ? Math.trunc(a / b) : 0, "%": b ? a % b : 0, "`": +(a > b) }[ch]);
    } else if (ch === "!") st.push(+!pop());
    else if (ch === "?") { dx = 1; dy = 0; }
    else if (ch === "_") { dx = pop() ? -1 : 1; dy = 0; }
    else if (ch === "|") { dy = pop() ? -1 : 1; dx = 0; }
    else if (ch === ":") { const v = pop(); st.push(v, v); }
    else if (ch === "\\") { const b = pop(), a = pop(); st.push(b, a); }
    else if (ch === "$") pop();
    else if (ch === ".") out += pop() + " ";
    else if (ch === ",") out += String.fromCodePoint(pop());
    else if (ch === "#") step();
    else if (ch === "g") { const yy = pop(), xx = pop(); st.push(grid[yy]?.[xx] ?? 32); }
    else if (ch === "p") { const yy = pop(), xx = pop(), v = pop(); if (grid[yy] && xx < W) grid[yy][xx] = v; }
    else if (ch === "&") st.push(0);
    else if (ch === "~") st.push(-1);
    else if (ch === "@") halted = true;
    else if (mode === "b98" && ch === ";") { do step(); while (grid[y][x] !== 59); }
    else if (mode === "b98" && ch === "'") { step(); st.push(grid[y][x]); }
  }
  step();
}
if (!halted) die("did not halt in 1e6 steps");
if (!/[A-Za-z]/.test(out) || /[\x00-\x08\x0e-\x1f\x7f]/.test(out)) die(`no text output: ${JSON.stringify(out.slice(0, 40))}`);
process.stdout.write(out);
