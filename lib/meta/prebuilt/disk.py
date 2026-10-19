"""`disk` alias over the virtual-disk families (prebuilt, SPECULATIVE): detect the container by its bytes, then answer
the field with that family's extractor (vhd.py / vhdx.py / vmdk.py / qcow2.py -- see their docstrings for layouts
and spellings). Detection: "vhdxfile" @0 -> vhdx; "QFI\\xfb" @0 -> qcow2; "KDMV" @0 or a text "# Disk
DescriptorFile" -> vmdk; "conectix" in the last 512/511 or first 512 bytes -> vhd. disk.format = that token
("vhd" for VPC/VHD, qemu-img calls it "vpc"). magic_hex = the first 8 bytes as lowercase hex. Not a virtual disk ->
"none"."""
from . import qcow2 as _qcow2
from . import vhd as _vhd
from . import vhdx as _vhdx
from . import vmdk as _vmdk

FIELDS = {
    ("disk", "format"): "disk_value",
    ("disk", "image_format"): "disk_value",
    ("disk", "disk_format"): "disk_value",
    ("disk", "disk_image_format"): "disk_value",
    ("disk", "container_format"): "disk_value",
    ("disk", "detected_format"): "disk_value",
    ("disk", "magic_hex"): "disk_value",
    ("disk", "cookie"): "disk_value",
    ("disk", "footer_cookie"): "disk_value",
    ("disk", "features_u32_hex"): "disk_value",
    ("disk", "file_format_version"): "disk_value",
    ("disk", "file_format_version_u32_hex"): "disk_value",
    ("disk", "data_offset"): "disk_value",
    ("disk", "data_offset_u64_hex"): "disk_value",
    ("disk", "timestamp"): "disk_value",
    ("disk", "timestamp_utc"): "disk_value",
    ("disk", "timestamp_u32_hex"): "disk_value",
    ("disk", "timestamp_raw"): "disk_value",
    ("disk", "creation_time"): "disk_value",
    ("disk", "creation_time_utc"): "disk_value",
    ("disk", "created_utc"): "disk_value",
    ("disk", "creator_application"): "disk_value",
    ("disk", "creator_app"): "disk_value",
    ("disk", "creator_version"): "disk_value",
    ("disk", "creator_version_u32_hex"): "disk_value",
    ("disk", "creator_host_os"): "disk_value",
    ("disk", "creator_host_os_u32_hex"): "disk_value",
    ("disk", "host_os"): "disk_value",
    ("disk", "original_size"): "disk_value",
    ("disk", "original_size_bytes"): "disk_value",
    ("disk", "current_size"): "disk_value",
    ("disk", "current_size_bytes"): "disk_value",
    ("disk", "virtual_size"): "disk_value",
    ("disk", "virtual_size_bytes"): "disk_value",
    ("disk", "disk_size_bytes"): "disk_value",
    ("disk", "disk_geometry"): "disk_value",
    ("disk", "geometry_chs"): "disk_value",
    ("disk", "geometry_cylinders"): "disk_value",
    ("disk", "geometry_heads"): "disk_value",
    ("disk", "geometry_sectors"): "disk_value",
    ("disk", "disk_type"): "disk_value",
    ("disk", "disk_type_u32_hex"): "disk_value",
    ("disk", "disk_type_name"): "disk_value",
    ("disk", "checksum"): "disk_value",
    ("disk", "checksum_u32_hex"): "disk_value",
    ("disk", "footer_checksum_u32_hex"): "disk_value",
    ("disk", "checksum_valid"): "disk_value",
    ("disk", "unique_id"): "disk_value",
    ("disk", "unique_id_guid"): "disk_value",
    ("disk", "unique_id_hex"): "disk_value",
    ("disk", "saved_state"): "disk_value",
    ("disk", "dynamic_header_cookie"): "disk_value",
    ("disk", "table_offset"): "disk_value",
    ("disk", "max_table_entries"): "disk_value",
    ("disk", "block_size"): "disk_value",
    ("disk", "block_size_bytes"): "disk_value",
    ("disk", "parent_unique_id_guid"): "disk_value",
    ("disk", "parent_timestamp_utc"): "disk_value",
    ("disk", "parent_name"): "disk_value",
    ("disk", "parent_unicode_name"): "disk_value",
    ("disk", "signature"): "disk_value",
    ("disk", "file_type_identifier"): "disk_value",
    ("disk", "creator"): "disk_value",
    ("disk", "file_identifier_creator"): "disk_value",
    ("disk", "sequence_number"): "disk_value",
    ("disk", "header_sequence_number"): "disk_value",
    ("disk", "file_write_guid"): "disk_value",
    ("disk", "data_write_guid"): "disk_value",
    ("disk", "log_guid"): "disk_value",
    ("disk", "log_version"): "disk_value",
    ("disk", "version"): "disk_value",
    ("disk", "header_version"): "disk_value",
    ("disk", "log_length"): "disk_value",
    ("disk", "log_length_bytes"): "disk_value",
    ("disk", "log_offset"): "disk_value",
    ("disk", "region_count"): "disk_value",
    ("disk", "region_table_entry_count"): "disk_value",
    ("disk", "bat_offset"): "disk_value",
    ("disk", "metadata_offset"): "disk_value",
    ("disk", "leave_blocks_allocated"): "disk_value",
    ("disk", "is_fixed"): "disk_value",
    ("disk", "has_parent"): "disk_value",
    ("disk", "virtual_disk_size"): "disk_value",
    ("disk", "virtual_disk_size_bytes"): "disk_value",
    ("disk", "virtual_disk_id"): "disk_value",
    ("disk", "virtual_disk_id_guid"): "disk_value",
    ("disk", "virtual_disk_id_hex"): "disk_value",
    ("disk", "logical_sector_size"): "disk_value",
    ("disk", "logical_sector_size_bytes"): "disk_value",
    ("disk", "physical_sector_size"): "disk_value",
    ("disk", "physical_sector_size_bytes"): "disk_value",
    ("disk", "magic"): "disk_value",
    ("disk", "sparse_header_version"): "disk_value",
    ("disk", "flags_u32_hex"): "disk_value",
    ("disk", "capacity"): "disk_value",
    ("disk", "capacity_sectors"): "disk_value",
    ("disk", "capacity_bytes"): "disk_value",
    ("disk", "size_bytes"): "disk_value",
    ("disk", "grain_size"): "disk_value",
    ("disk", "grain_size_sectors"): "disk_value",
    ("disk", "grain_size_bytes"): "disk_value",
    ("disk", "descriptor_offset"): "disk_value",
    ("disk", "descriptor_size"): "disk_value",
    ("disk", "num_gtes_per_gt"): "disk_value",
    ("disk", "overhead"): "disk_value",
    ("disk", "unclean_shutdown"): "disk_value",
    ("disk", "compress_algorithm"): "disk_value",
    ("disk", "descriptor_version"): "disk_value",
    ("disk", "cid"): "disk_value",
    ("disk", "content_id"): "disk_value",
    ("disk", "cid_u32_hex"): "disk_value",
    ("disk", "parent_cid"): "disk_value",
    ("disk", "parent_content_id"): "disk_value",
    ("disk", "parent_cid_u32_hex"): "disk_value",
    ("disk", "create_type"): "disk_value",
    ("disk", "createtype"): "disk_value",
    ("disk", "parent_file_name_hint"): "disk_value",
    ("disk", "parent_filename_hint"): "disk_value",
    ("disk", "encoding"): "disk_value",
    ("disk", "extent_files"): "disk_value",
    ("disk", "extent_file_names"): "disk_value",
    ("disk", "extent_filenames"): "disk_value",
    ("disk", "extent_count"): "disk_value",
    ("disk", "extent_types"): "disk_value",
    ("disk", "extent_access"): "disk_value",
    ("disk", "extent_sizes_sectors"): "disk_value",
    ("disk", "extents"): "disk_value",
    ("disk", "ddb_uuid"): "disk_value",
    ("disk", "uuid"): "disk_value",
    ("disk", "ddb_virtual_hw_version"): "disk_value",
    ("disk", "virtual_hw_version"): "disk_value",
    ("disk", "hw_version"): "disk_value",
    ("disk", "ddb_adapter_type"): "disk_value",
    ("disk", "adapter_type"): "disk_value",
    ("disk", "ddb_tools_version"): "disk_value",
    ("disk", "tools_version"): "disk_value",
    ("disk", "ddb_long_content_id"): "disk_value",
    ("disk", "long_content_id"): "disk_value",
    ("disk", "ddb_geometry_cylinders"): "disk_value",
    ("disk", "ddb_geometry_heads"): "disk_value",
    ("disk", "ddb_geometry_sectors"): "disk_value",
    ("disk", "ddb_*"): "disk_value",
    ("disk", "ddb_keys"): "disk_value",
    ("disk", "magic_u32_hex"): "disk_value",
    ("disk", "compat"): "disk_value",
    ("disk", "size"): "disk_value",
    ("disk", "backing_file"): "disk_value",
    ("disk", "backing_file_name"): "disk_value",
    ("disk", "backing_filename"): "disk_value",
    ("disk", "backing_file_offset"): "disk_value",
    ("disk", "backing_file_size"): "disk_value",
    ("disk", "backing_file_format"): "disk_value",
    ("disk", "backing_format"): "disk_value",
    ("disk", "has_backing_file"): "disk_value",
    ("disk", "cluster_bits"): "disk_value",
    ("disk", "cluster_size"): "disk_value",
    ("disk", "cluster_size_bytes"): "disk_value",
    ("disk", "crypt_method"): "disk_value",
    ("disk", "crypt_method_name"): "disk_value",
    ("disk", "encryption_method"): "disk_value",
    ("disk", "is_encrypted"): "disk_value",
    ("disk", "encrypted"): "disk_value",
    ("disk", "l1_size"): "disk_value",
    ("disk", "l1_table_offset"): "disk_value",
    ("disk", "refcount_table_offset"): "disk_value",
    ("disk", "refcount_table_clusters"): "disk_value",
    ("disk", "nb_snapshots"): "disk_value",
    ("disk", "snapshot_count"): "disk_value",
    ("disk", "number_of_snapshots"): "disk_value",
    ("disk", "snapshots_offset"): "disk_value",
    ("disk", "incompatible_features_u64_hex"): "disk_value",
    ("disk", "compatible_features_u64_hex"): "disk_value",
    ("disk", "autoclear_features_u64_hex"): "disk_value",
    ("disk", "refcount_order"): "disk_value",
    ("disk", "refcount_bits"): "disk_value",
    ("disk", "header_length"): "disk_value",
    ("disk", "compression_type"): "disk_value",
    ("disk", "header_extension_types"): "disk_value",
}


def detect(data):
    """"vhd" | "vhdx" | "vmdk" | "qcow2" | None."""
    if not data:
        return None
    if data[:8] == b"vhdxfile":
        return "vhdx"
    if data[:4] == b"QFI\xfb":
        return "qcow2"
    if data[:4] == b"KDMV" or data[:4096].lstrip().startswith(b"# Disk DescriptorFile"):
        return "vmdk"
    if _vhd.footer(data) is not None:
        return "vhd"
    return None


_MODS = {"vhd": _vhd, "vhdx": _vhdx, "vmdk": _vmdk, "qcow2": _qcow2}


def disk_value(data, ctx):
    if data is None:
        return None
    field = ctx.get("field") or ""
    kind = detect(data)
    if kind is None:
        return "none"
    if field in ("format", "image_format", "disk_format", "disk_image_format", "container_format", "detected_format"):
        return kind
    if field == "magic_hex":
        return data[:8].hex()
    try:
        return _MODS[kind].field_value(data, field)
    except Exception:  # noqa: BLE001 -- never raise past the extractor
        return None
