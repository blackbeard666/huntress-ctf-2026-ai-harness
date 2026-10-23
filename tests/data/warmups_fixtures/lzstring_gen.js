const LZ = require(process.env.LZ);
const [form, plain] = process.argv.slice(2);
const f = {base64: LZ.compressToBase64, uri: LZ.compressToEncodedURIComponent, utf16: LZ.compressToUTF16,
           hex: s => Buffer.from(LZ.compressToUint8Array(s)).toString('hex')}[form];
process.stdout.write(f(plain));
