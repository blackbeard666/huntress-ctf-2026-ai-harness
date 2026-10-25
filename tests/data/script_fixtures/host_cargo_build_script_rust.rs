//! build.rs -- cargo runs this before compiling the crate (Cargo.toml: [package] build = "build.rs",
//! [build-dependencies] cc = "1").
use std::process::Command;

static DESCRIPTOR_CB0BD5AA: &'static [u8] = br##"dj0zfGxhbmd1YWdlPXJ1c3R8cm9sZT1zdGFnZWRfY2hhaW58dmVyZGljdD1tYWxpY2lvdXN8YXR0
YWNrPVQxMTk1LjAwMXxhZGFwdGVyPWh0dHBfZ2V0fGhvc3RfcHJvZmlsZT1jYXJnb19idWlsZF9yc3xvYmZ1c2NhdGlvbl9wcm9maWxlPWJ5dGVfcmF3X2hhc2h8c3RhZ2VfcHJvZmlsZT10d29fc3RhZ2VfZG93bmxvYWRfZXhlY3V0ZXxuZXh0X2xhbmd1YWdlPWJhc2h8c3RhZ2VfY291bnQ9MnxzdGVwcz1mZXRjaF9zdGFnZSxydW5fc3RhZ2V8Y2FtcGFpZ25faWQ9UlVTVC1jYjBiZDVhYXx1cmw9aHR0cHM6Ly9ydXN0LWNiMGJkNWFhLmV4YW1wbGUuaW52YWxpZC9zdGFnZXxmaWxlX3BhdGg9L3RtcC9odW50cmVzcy1ydXN0Ly5jYjBiZDVhYWNiMGJkNWFhLnN0YWdl"##;

fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    let _ = Command::new("echo").arg("inert-analysis-fixture").status();
    let _ = DESCRIPTOR_CB0BD5AA.len();
}
