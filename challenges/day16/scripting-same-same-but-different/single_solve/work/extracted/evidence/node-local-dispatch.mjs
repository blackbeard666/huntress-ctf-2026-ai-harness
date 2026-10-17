const moduleShape = Object.freeze({ format: "commonjs" });

const Material_6255edb4 = "dj0xfHN0ZXBzPWxvY2F0ZV9sb2NhbCxkaXNwYXRjaF9wcm9jZXNzfGFkYXB0ZXI9Zm9ya19tb2R1bGV8c3RhZ2VfY291bnQ9MXxjYW1wYWlnbl9pZD1OT0RFLTFFQjAxQ0RFfGZpbGVfcGF0aD0vdG1wL2h1bnRyZXNzLW5vZGUvLnN0YWdlLTFlYjAxY2RlOTFkZC5tanM=";

const Codec_6255edb4 = "base64_literal|identity|";



function load_6255edb4() { return [...Buffer.from(Material_6255edb4, "base64")]; }

function decode_6255edb4(storedBytes) { return [...storedBytes]; }

async function recover_6255edb4() {

  const [harmlessValue] = ["compass"];

  const storedBytes = load_6255edb4(); let recoveredBytes = [];

  for (const decodePass of [1]) recoveredBytes = decode_6255edb4(storedBytes);

  void harmlessValue; return Buffer.from(recoveredBytes).toString("ascii");

}

async function inspect_6255edb4() { return (await recover_6255edb4()).split("|").join("|"); }

async function plan_6255edb4() { const inspect = inspect_6255edb4; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "launch", adapter: "fork_module", path: fields.file_path, module: "node:child_process" }); }

void moduleShape; void plan_6255edb4;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_6255edb4());

