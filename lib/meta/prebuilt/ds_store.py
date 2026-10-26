"""macOS Finder .DS_Store (prebuilt, SPECULATIVE -- never GM-asked yet). fmt `ds_store`, alias `dsstore`.

Layout (all big-endian): `00 00 00 01` + `Bud1` @4; buddy-allocator root block offset u32 @8, size u32 @12, offset
copy u32 @16 -- every file offset is +4 (the leading alignment word). Root block: block count u32, unknown u32, block
address table (count u32s, padded to a multiple of 256; addr = offset | log2(size) in the low 5 bits), then the TOC
{count u32, [name_len u8, name, block id u32]} -- `DSDB` -> superblock {root node u32, levels u32, records u32,
nodes u32, page size u32}. B-tree node: P u32 (0 = leaf, else the rightmost child), count u32; leaf = count records,
internal = count x (child u32, record). Record: filename = u32 length (UTF-16 units) + UTF-16BE, structure id 4 ASCII
(`Iloc`, `bwsp`, `lsvp`, `icvp`, `modD`, `ptbL`, `vSrn`, ...), type 4 ASCII: bool 1 B | long/shor 4 B | type 4 B |
comp/dutc 8 B | blob u32 len + bytes | ustr u32 len + 2*len B.

file_names = sorted (Python codepoint order) UNIQUE record filenames WITHOUT "." (the folder's own view-settings
records -- the answer is the folder's contents, which is what reveals deleted/renamed children); file_names_all keeps
"."; record_count = records walked in the tree (== the superblock's record count on an intact file); structure_ids /
data_types = sorted unique 4ccs. Wrong magic / no DSDB / truncated -> "none"."""
import struct

FIELDS = {
    ("ds_store", "file_names"): "ds_file_names",
    ("ds_store", "filenames"): "ds_file_names",
    ("ds_store", "file_list"): "ds_file_names",
    ("ds_store", "entry_names"): "ds_file_names",
    ("ds_store", "record_filenames"): "ds_file_names",
    ("ds_store", "record_names"): "ds_file_names",
    ("ds_store", "unique_file_names"): "ds_file_names",
    ("ds_store", "child_names"): "ds_file_names",
    ("ds_store", "item_names"): "ds_file_names",
    ("ds_store", "file_names_all"): "ds_file_names_all",
    ("ds_store", "all_record_filenames"): "ds_file_names_all",
    ("ds_store", "record_filenames_all"): "ds_file_names_all",
    ("ds_store", "file_count"): "ds_file_count",
    ("ds_store", "filename_count"): "ds_file_count",
    ("ds_store", "unique_file_count"): "ds_file_count",
    ("ds_store", "number_of_files"): "ds_file_count",
    ("ds_store", "entry_count"): "ds_file_count",
    ("ds_store", "record_count"): "ds_record_count",
    ("ds_store", "records_count"): "ds_record_count",
    ("ds_store", "number_of_records"): "ds_record_count",
    ("ds_store", "num_records"): "ds_record_count",
    ("ds_store", "total_records"): "ds_record_count",
    ("ds_store", "header_record_count"): "ds_header_records",
    ("ds_store", "dsdb_record_count"): "ds_header_records",
    ("ds_store", "superblock_record_count"): "ds_header_records",
    ("ds_store", "structure_ids"): "ds_structure_ids",
    ("ds_store", "structure_types"): "ds_structure_ids",
    ("ds_store", "structure_codes"): "ds_structure_ids",
    ("ds_store", "record_codes"): "ds_structure_ids",
    ("ds_store", "record_types"): "ds_structure_ids",
    ("ds_store", "codes"): "ds_structure_ids",
    ("ds_store", "property_ids"): "ds_structure_ids",
    ("ds_store", "attribute_ids"): "ds_structure_ids",
    ("ds_store", "data_types"): "ds_data_types",
    ("ds_store", "type_codes"): "ds_data_types",
    ("ds_store", "value_types"): "ds_data_types",
    ("ds_store", "record_data_types"): "ds_data_types",
    ("ds_store", "root_block_offset"): "ds_root_offset",
    ("ds_store", "root_offset"): "ds_root_offset",
    ("ds_store", "allocator_offset"): "ds_root_offset",
    ("ds_store", "buddy_root_offset"): "ds_root_offset",
    ("ds_store", "root_block_size"): "ds_root_size",
    ("ds_store", "allocator_size"): "ds_root_size",
    ("ds_store", "tree_levels"): "ds_levels",
    ("ds_store", "btree_levels"): "ds_levels",
    ("ds_store", "dsdb_levels"): "ds_levels",
    ("ds_store", "levels"): "ds_levels",
    ("ds_store", "node_count"): "ds_nodes",
    ("ds_store", "btree_nodes"): "ds_nodes",
    ("ds_store", "dsdb_nodes"): "ds_nodes",
    ("ds_store", "nodes"): "ds_nodes",
    ("ds_store", "page_size"): "ds_page_size",
    ("ds_store", "btree_page_size"): "ds_page_size",
    ("ds_store", "dsdb_page_size"): "ds_page_size",
    ("ds_store", "block_count"): "ds_block_count",
    ("ds_store", "allocator_block_count"): "ds_block_count",
    ("ds_store", "toc_names"): "ds_toc_names",
    ("ds_store", "directory_names"): "ds_toc_names",
    ("ds_store", "toc_entries"): "ds_toc_names",
    ("ds_store", "magic"): "ds_magic",
    ("dsstore", "file_names"): "ds_file_names",
    ("dsstore", "filenames"): "ds_file_names",
    ("dsstore", "file_list"): "ds_file_names",
    ("dsstore", "entry_names"): "ds_file_names",
    ("dsstore", "record_filenames"): "ds_file_names",
    ("dsstore", "record_names"): "ds_file_names",
    ("dsstore", "unique_file_names"): "ds_file_names",
    ("dsstore", "child_names"): "ds_file_names",
    ("dsstore", "item_names"): "ds_file_names",
    ("dsstore", "file_names_all"): "ds_file_names_all",
    ("dsstore", "all_record_filenames"): "ds_file_names_all",
    ("dsstore", "record_filenames_all"): "ds_file_names_all",
    ("dsstore", "file_count"): "ds_file_count",
    ("dsstore", "filename_count"): "ds_file_count",
    ("dsstore", "unique_file_count"): "ds_file_count",
    ("dsstore", "number_of_files"): "ds_file_count",
    ("dsstore", "entry_count"): "ds_file_count",
    ("dsstore", "record_count"): "ds_record_count",
    ("dsstore", "records_count"): "ds_record_count",
    ("dsstore", "number_of_records"): "ds_record_count",
    ("dsstore", "num_records"): "ds_record_count",
    ("dsstore", "total_records"): "ds_record_count",
    ("dsstore", "header_record_count"): "ds_header_records",
    ("dsstore", "dsdb_record_count"): "ds_header_records",
    ("dsstore", "superblock_record_count"): "ds_header_records",
    ("dsstore", "structure_ids"): "ds_structure_ids",
    ("dsstore", "structure_types"): "ds_structure_ids",
    ("dsstore", "structure_codes"): "ds_structure_ids",
    ("dsstore", "record_codes"): "ds_structure_ids",
    ("dsstore", "record_types"): "ds_structure_ids",
    ("dsstore", "codes"): "ds_structure_ids",
    ("dsstore", "property_ids"): "ds_structure_ids",
    ("dsstore", "attribute_ids"): "ds_structure_ids",
    ("dsstore", "data_types"): "ds_data_types",
    ("dsstore", "type_codes"): "ds_data_types",
    ("dsstore", "value_types"): "ds_data_types",
    ("dsstore", "record_data_types"): "ds_data_types",
    ("dsstore", "root_block_offset"): "ds_root_offset",
    ("dsstore", "root_offset"): "ds_root_offset",
    ("dsstore", "allocator_offset"): "ds_root_offset",
    ("dsstore", "buddy_root_offset"): "ds_root_offset",
    ("dsstore", "root_block_size"): "ds_root_size",
    ("dsstore", "allocator_size"): "ds_root_size",
    ("dsstore", "tree_levels"): "ds_levels",
    ("dsstore", "btree_levels"): "ds_levels",
    ("dsstore", "dsdb_levels"): "ds_levels",
    ("dsstore", "levels"): "ds_levels",
    ("dsstore", "node_count"): "ds_nodes",
    ("dsstore", "btree_nodes"): "ds_nodes",
    ("dsstore", "dsdb_nodes"): "ds_nodes",
    ("dsstore", "nodes"): "ds_nodes",
    ("dsstore", "page_size"): "ds_page_size",
    ("dsstore", "btree_page_size"): "ds_page_size",
    ("dsstore", "dsdb_page_size"): "ds_page_size",
    ("dsstore", "block_count"): "ds_block_count",
    ("dsstore", "allocator_block_count"): "ds_block_count",
    ("dsstore", "toc_names"): "ds_toc_names",
    ("dsstore", "directory_names"): "ds_toc_names",
    ("dsstore", "toc_entries"): "ds_toc_names",
    ("dsstore", "magic"): "ds_magic",
}

_FIXED = {b"bool": 1, b"long": 4, b"shor": 4, b"type": 4, b"comp": 8, b"dutc": 8}


def _parse(b):
    """{root_off, root_size, blocks, toc, super, records} or None (not a .DS_Store / damaged)."""
    if not b or len(b) < 36 or b[:8] != b"\x00\x00\x00\x01Bud1":
        return None
    root_off, root_size = struct.unpack_from(">II", b, 8)
    p = root_off + 4
    if p + 8 > len(b):
        return None
    nblocks, = struct.unpack_from(">I", b, p)
    if nblocks > 1 << 20 or p + 8 + 4 * nblocks > len(b):
        return None
    blocks = list(struct.unpack_from(">%dI" % nblocks, b, p + 8))
    q = p + 8 + 4 * (((nblocks + 255) // 256) * 256)
    if q + 4 > len(b):
        return None
    ntoc, = struct.unpack_from(">I", b, q)
    q += 4
    toc = []
    for _ in range(min(ntoc, 4096)):
        n = b[q]
        name = b[q + 1:q + 1 + n].decode("latin-1")
        bid, = struct.unpack_from(">I", b, q + 1 + n)
        toc.append((name, bid))
        q += 5 + n

    def block(bid):
        if bid >= len(blocks):
            raise ValueError("block id")
        a = blocks[bid]
        off, size = (a & ~0x1F) + 4, 1 << (a & 0x1F)
        if off + min(size, 8) > len(b):
            raise ValueError("block range")
        return off, size

    dsdb = dict(toc).get("DSDB")
    if dsdb is None:
        return None
    so, _ = block(dsdb)
    root, levels, nrec, nnodes, page = struct.unpack_from(">5I", b, so)
    recs = []

    def rec(o):
        nl, = struct.unpack_from(">I", b, o)
        name = b[o + 4:o + 4 + 2 * nl].decode("utf-16-be")
        o += 4 + 2 * nl
        code, typ = b[o:o + 4], b[o + 4:o + 8]
        o += 8
        if typ in _FIXED:
            o += _FIXED[typ]
        elif typ == b"blob":
            o += 4 + struct.unpack_from(">I", b, o)[0]
        elif typ == b"ustr":
            o += 4 + 2 * struct.unpack_from(">I", b, o)[0]
        else:
            raise ValueError("type %r" % typ)
        if o > len(b):
            raise ValueError("record range")
        recs.append((name, code.decode("latin-1"), typ.decode("latin-1")))
        return o

    seen = set()

    def node(bid, depth):
        if bid in seen or depth > 32:
            raise ValueError("tree loop")
        seen.add(bid)
        o, _ = block(bid)
        ptr, cnt = struct.unpack_from(">II", b, o)
        o += 8
        for _ in range(cnt):
            if ptr:
                child, = struct.unpack_from(">I", b, o)
                node(child, depth + 1)
                o += 4
            o = rec(o)
        if ptr:
            node(ptr, depth + 1)

    node(root, 0)
    return {"root_off": root_off, "root_size": root_size, "blocks": nblocks, "toc": [t[0] for t in toc],
            "super": (root, levels, nrec, nnodes, page), "records": recs}


def _get(data, fn):
    if data is None:
        return None
    try:
        d = _parse(bytes(data))
    except Exception:  # noqa: BLE001
        return "none"
    if d is None:
        return "none"
    try:
        return fn(d)
    except Exception:  # noqa: BLE001
        return None


def ds_file_names(data, ctx):
    return _get(data, lambda d: sorted({r[0] for r in d["records"] if r[0] != "."}))


def ds_file_names_all(data, ctx):
    return _get(data, lambda d: sorted({r[0] for r in d["records"]}))


def ds_file_count(data, ctx):
    return _get(data, lambda d: len({r[0] for r in d["records"] if r[0] != "."}))


def ds_record_count(data, ctx):
    return _get(data, lambda d: len(d["records"]))


def ds_header_records(data, ctx):
    return _get(data, lambda d: d["super"][2])


def ds_structure_ids(data, ctx):
    return _get(data, lambda d: sorted({r[1] for r in d["records"]}))


def ds_data_types(data, ctx):
    return _get(data, lambda d: sorted({r[2] for r in d["records"]}))


def ds_root_offset(data, ctx):
    return _get(data, lambda d: d["root_off"])


def ds_root_size(data, ctx):
    return _get(data, lambda d: d["root_size"])


def ds_levels(data, ctx):
    return _get(data, lambda d: d["super"][1])


def ds_nodes(data, ctx):
    return _get(data, lambda d: d["super"][3])


def ds_page_size(data, ctx):
    return _get(data, lambda d: d["super"][4])


def ds_block_count(data, ctx):
    return _get(data, lambda d: d["blocks"])


def ds_toc_names(data, ctx):
    return _get(data, lambda d: d["toc"])


def ds_magic(data, ctx):
    return _get(data, lambda d: "Bud1")
