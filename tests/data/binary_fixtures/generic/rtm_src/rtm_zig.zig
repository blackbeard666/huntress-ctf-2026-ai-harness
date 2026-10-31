var seed: u32 = 300;
fn pick(v: ?u32) !u8 {
    const x = v orelse return error.Missing;
    return @intCast(x);
}
pub fn main() void {
    const p: *volatile u32 = &seed;
    const s = pick(p.*) catch unreachable;
    if (s == 3) @panic("rtm zig marker");
}
