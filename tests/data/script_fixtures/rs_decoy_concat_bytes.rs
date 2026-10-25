// build helper
const DESCRIPTOR_VERSION: &str = concat!("crate-", env!("CARGO_PKG_VERSION"), "-", 3);
static DESCRIPTOR_STATUS: [u8; 6] = [115, 116, 97, 116, 117, 115];
const DESCRIPTOR_NOTE: &[u8] = b"\x6f\x6b";

fn main() {
    println!("{}", DESCRIPTOR_VERSION);
}
