"""Raw disk-image GPT/MBR INTEGRITY fields (prebuilt, SPECULATIVE; no spelling GM-verified). Coverage-atlas row
"disk-rebuilt-integrity" ('Prove which image was rebuilt from an incomplete source'). fmt `disk`, aliases gpt / image /
disk_image / dd / raw_disk (keys other modules already own -- e.g. gpt.header_crc32_u32_hex in vbr.py -- are skipped).
The bytes are unwrapped like disk_layout.py (gzip/xz/bz2, fixed/dynamic VHD, sparse VMDK, qcow2) -> the raw image;
sector count N = len(image) // sector size. Sector size: the first of 512/4096/1024/2048 with `EFI PART` at LBA1, else
the first whose LAST LBA holds a header (primary gone), else 512 (MBR-only questions).
Primary header (LBA1): header CRC32 @+16 over hdr_size (@+12) bytes with @+16 zeroed; entry array = count (@+80) x
size (@+84) bytes at entry LBA (@+72), CRC32 stored @+88 (an array running past EOF is CRC'd over what is present).
Fields (bools -> true/false; no GPT header anywhere -> "none"):
  primary_header_crc_valid / partition_array_crc_valid (primary's; primary gone -> false / the backup's array);
  header_crc32_u32_hex / partition_array_crc32_u32_hex = the STORED value `0x%08x` (`*_computed_*` / `computed_*`
    keys = recomputed); header_crc_matches = stored == computed (same as *_valid);
  backup_header_present = `EFI PART` at the primary's AlternateLBA AND at the image's last LBA (as the atlas spec says:
    a backup that is not at the end of the image does not count); backup_matches_primary = a backup header (at
    AlternateLBA, else last LBA) with valid CRC, MyLBA == primary.AlternateLBA, its AlternateLBA == 1, same disk GUID,
    first/last usable, entry count/size, entry-array CRC, and identical entry bytes;
  alternate_lba_matches_image_end = primary AlternateLBA == N-1;
  image_truncated = AlternateLBA >= N or any used partition's last LBA >= N; partitions_beyond_image_count = how
    many used partitions end at/after N (int);
  protective_mbr_size_matches = the 0xEE entry's sector count == min(N-1, 0xFFFFFFFF) (no 0x55AA / no 0xEE -> "none");
  overlapping_partitions = any two used entries share an LBA;
  zero_filled_partition_sequence = per used partition (table order) whether every byte present in the image is 0x00
    (a partition with no bytes inside the image counts as zero-filled); zero_filled/empty_partition_count = how many;
    unused_partition_entry_count = all-zero type-GUID slots in the entry array;
  integrity_status / rebuilt_indicator = enum, first that applies: `truncated` (image_truncated) > `crc_mismatch`
    (primary header or array CRC bad) > `rebuilt` (backup missing / not matching / AlternateLBA != N-1 / protective
    MBR size mismatch / overlap) > `intact`; booleans is_truncated / is_rebuilt / is_intact / has_crc_mismatch."""
import struct
import zlib

from ..spell import Hex

FIELDS = {
    ("disk", "primary_header_crc_valid"): "integrity_value",
    ("disk", "header_crc_valid"): "integrity_value",
    ("disk", "primary_header_crc32_valid"): "integrity_value",
    ("disk", "header_crc32_valid"): "integrity_value",
    ("disk", "partition_array_crc_valid"): "integrity_value",
    ("disk", "partition_entry_array_crc_valid"): "integrity_value",
    ("disk", "partition_array_crc32_valid"): "integrity_value",
    ("disk", "partition_entries_crc_valid"): "integrity_value",
    ("disk", "header_crc32_u32_hex"): "integrity_value",
    ("disk", "primary_header_crc32_u32_hex"): "integrity_value",
    ("disk", "header_crc32_stored_u32_hex"): "integrity_value",
    ("disk", "header_crc32_computed_u32_hex"): "integrity_value",
    ("disk", "computed_header_crc32_u32_hex"): "integrity_value",
    ("disk", "partition_array_crc32_u32_hex"): "integrity_value",
    ("disk", "partition_entry_array_crc32_u32_hex"): "integrity_value",
    ("disk", "partition_array_crc32_stored_u32_hex"): "integrity_value",
    ("disk", "partition_array_crc32_computed_u32_hex"): "integrity_value",
    ("disk", "computed_partition_array_crc32_u32_hex"): "integrity_value",
    ("disk", "partition_entry_array_crc32_computed_u32_hex"): "integrity_value",
    ("disk", "header_crc_matches"): "integrity_value",
    ("disk", "partition_array_crc_matches"): "integrity_value",
    ("disk", "backup_header_present"): "integrity_value",
    ("disk", "backup_gpt_present"): "integrity_value",
    ("disk", "has_backup_header"): "integrity_value",
    ("disk", "backup_header_valid"): "integrity_value",
    ("disk", "backup_matches_primary"): "integrity_value",
    ("disk", "backup_header_matches_primary"): "integrity_value",
    ("disk", "primary_backup_match"): "integrity_value",
    ("disk", "backup_consistent"): "integrity_value",
    ("disk", "alternate_lba_matches_image_end"): "integrity_value",
    ("disk", "backup_lba_matches_image_end"): "integrity_value",
    ("disk", "alternate_lba_at_image_end"): "integrity_value",
    ("disk", "image_truncated"): "integrity_value",
    ("disk", "is_truncated"): "integrity_value",
    ("disk", "truncated"): "integrity_value",
    ("disk", "partitions_beyond_image_count"): "integrity_value",
    ("disk", "partitions_beyond_image_end_count"): "integrity_value",
    ("disk", "partition_beyond_image_count"): "integrity_value",
    ("disk", "protective_mbr_size_matches"): "integrity_value",
    ("disk", "protective_mbr_size_valid"): "integrity_value",
    ("disk", "pmbr_size_matches"): "integrity_value",
    ("disk", "overlapping_partitions"): "integrity_value",
    ("disk", "has_overlapping_partitions"): "integrity_value",
    ("disk", "partitions_overlap"): "integrity_value",
    ("disk", "zero_filled_partition_sequence"): "integrity_value",
    ("disk", "zero_filled_partition_list"): "integrity_value",
    ("disk", "zero_filled_partitions"): "integrity_value",
    ("disk", "zero_filled_partition_count"): "integrity_value",
    ("disk", "empty_partition_count"): "integrity_value",
    ("disk", "unused_partition_entry_count"): "integrity_value",
    ("disk", "integrity_status"): "integrity_value",
    ("disk", "rebuilt_indicator"): "integrity_value",
    ("disk", "image_integrity_status"): "integrity_value",
    ("disk", "gpt_integrity_status"): "integrity_value",
    ("disk", "is_rebuilt"): "integrity_value",
    ("disk", "rebuilt"): "integrity_value",
    ("disk", "is_intact"): "integrity_value",
    ("disk", "intact"): "integrity_value",
    ("disk", "has_crc_mismatch"): "integrity_value",
    ("disk", "crc_mismatch"): "integrity_value",
    ("gpt", "primary_header_crc_valid"): "integrity_value",
    ("gpt", "header_crc_valid"): "integrity_value",
    ("gpt", "primary_header_crc32_valid"): "integrity_value",
    ("gpt", "header_crc32_valid"): "integrity_value",
    ("gpt", "partition_array_crc_valid"): "integrity_value",
    ("gpt", "partition_entry_array_crc_valid"): "integrity_value",
    ("gpt", "partition_array_crc32_valid"): "integrity_value",
    ("gpt", "partition_entries_crc_valid"): "integrity_value",
    ("gpt", "primary_header_crc32_u32_hex"): "integrity_value",
    ("gpt", "header_crc32_stored_u32_hex"): "integrity_value",
    ("gpt", "header_crc32_computed_u32_hex"): "integrity_value",
    ("gpt", "computed_header_crc32_u32_hex"): "integrity_value",
    ("gpt", "partition_array_crc32_u32_hex"): "integrity_value",
    ("gpt", "partition_array_crc32_stored_u32_hex"): "integrity_value",
    ("gpt", "partition_array_crc32_computed_u32_hex"): "integrity_value",
    ("gpt", "computed_partition_array_crc32_u32_hex"): "integrity_value",
    ("gpt", "partition_entry_array_crc32_computed_u32_hex"): "integrity_value",
    ("gpt", "header_crc_matches"): "integrity_value",
    ("gpt", "partition_array_crc_matches"): "integrity_value",
    ("gpt", "backup_header_present"): "integrity_value",
    ("gpt", "backup_gpt_present"): "integrity_value",
    ("gpt", "has_backup_header"): "integrity_value",
    ("gpt", "backup_header_valid"): "integrity_value",
    ("gpt", "backup_matches_primary"): "integrity_value",
    ("gpt", "backup_header_matches_primary"): "integrity_value",
    ("gpt", "primary_backup_match"): "integrity_value",
    ("gpt", "backup_consistent"): "integrity_value",
    ("gpt", "alternate_lba_matches_image_end"): "integrity_value",
    ("gpt", "backup_lba_matches_image_end"): "integrity_value",
    ("gpt", "alternate_lba_at_image_end"): "integrity_value",
    ("gpt", "image_truncated"): "integrity_value",
    ("gpt", "is_truncated"): "integrity_value",
    ("gpt", "truncated"): "integrity_value",
    ("gpt", "partitions_beyond_image_count"): "integrity_value",
    ("gpt", "partitions_beyond_image_end_count"): "integrity_value",
    ("gpt", "partition_beyond_image_count"): "integrity_value",
    ("gpt", "protective_mbr_size_matches"): "integrity_value",
    ("gpt", "protective_mbr_size_valid"): "integrity_value",
    ("gpt", "pmbr_size_matches"): "integrity_value",
    ("gpt", "overlapping_partitions"): "integrity_value",
    ("gpt", "has_overlapping_partitions"): "integrity_value",
    ("gpt", "partitions_overlap"): "integrity_value",
    ("gpt", "zero_filled_partition_sequence"): "integrity_value",
    ("gpt", "zero_filled_partition_list"): "integrity_value",
    ("gpt", "zero_filled_partitions"): "integrity_value",
    ("gpt", "zero_filled_partition_count"): "integrity_value",
    ("gpt", "empty_partition_count"): "integrity_value",
    ("gpt", "unused_partition_entry_count"): "integrity_value",
    ("gpt", "integrity_status"): "integrity_value",
    ("gpt", "rebuilt_indicator"): "integrity_value",
    ("gpt", "image_integrity_status"): "integrity_value",
    ("gpt", "gpt_integrity_status"): "integrity_value",
    ("gpt", "is_rebuilt"): "integrity_value",
    ("gpt", "rebuilt"): "integrity_value",
    ("gpt", "is_intact"): "integrity_value",
    ("gpt", "intact"): "integrity_value",
    ("gpt", "has_crc_mismatch"): "integrity_value",
    ("gpt", "crc_mismatch"): "integrity_value",
    ("image", "primary_header_crc_valid"): "integrity_value",
    ("image", "header_crc_valid"): "integrity_value",
    ("image", "primary_header_crc32_valid"): "integrity_value",
    ("image", "header_crc32_valid"): "integrity_value",
    ("image", "partition_array_crc_valid"): "integrity_value",
    ("image", "partition_entry_array_crc_valid"): "integrity_value",
    ("image", "partition_array_crc32_valid"): "integrity_value",
    ("image", "partition_entries_crc_valid"): "integrity_value",
    ("image", "header_crc32_u32_hex"): "integrity_value",
    ("image", "primary_header_crc32_u32_hex"): "integrity_value",
    ("image", "header_crc32_stored_u32_hex"): "integrity_value",
    ("image", "header_crc32_computed_u32_hex"): "integrity_value",
    ("image", "computed_header_crc32_u32_hex"): "integrity_value",
    ("image", "partition_array_crc32_u32_hex"): "integrity_value",
    ("image", "partition_entry_array_crc32_u32_hex"): "integrity_value",
    ("image", "partition_array_crc32_stored_u32_hex"): "integrity_value",
    ("image", "partition_array_crc32_computed_u32_hex"): "integrity_value",
    ("image", "computed_partition_array_crc32_u32_hex"): "integrity_value",
    ("image", "partition_entry_array_crc32_computed_u32_hex"): "integrity_value",
    ("image", "header_crc_matches"): "integrity_value",
    ("image", "partition_array_crc_matches"): "integrity_value",
    ("image", "backup_header_present"): "integrity_value",
    ("image", "backup_gpt_present"): "integrity_value",
    ("image", "has_backup_header"): "integrity_value",
    ("image", "backup_header_valid"): "integrity_value",
    ("image", "backup_matches_primary"): "integrity_value",
    ("image", "backup_header_matches_primary"): "integrity_value",
    ("image", "primary_backup_match"): "integrity_value",
    ("image", "backup_consistent"): "integrity_value",
    ("image", "alternate_lba_matches_image_end"): "integrity_value",
    ("image", "backup_lba_matches_image_end"): "integrity_value",
    ("image", "alternate_lba_at_image_end"): "integrity_value",
    ("image", "image_truncated"): "integrity_value",
    ("image", "is_truncated"): "integrity_value",
    ("image", "truncated"): "integrity_value",
    ("image", "partitions_beyond_image_count"): "integrity_value",
    ("image", "partitions_beyond_image_end_count"): "integrity_value",
    ("image", "partition_beyond_image_count"): "integrity_value",
    ("image", "protective_mbr_size_matches"): "integrity_value",
    ("image", "protective_mbr_size_valid"): "integrity_value",
    ("image", "pmbr_size_matches"): "integrity_value",
    ("image", "overlapping_partitions"): "integrity_value",
    ("image", "has_overlapping_partitions"): "integrity_value",
    ("image", "partitions_overlap"): "integrity_value",
    ("image", "zero_filled_partition_sequence"): "integrity_value",
    ("image", "zero_filled_partition_list"): "integrity_value",
    ("image", "zero_filled_partitions"): "integrity_value",
    ("image", "zero_filled_partition_count"): "integrity_value",
    ("image", "empty_partition_count"): "integrity_value",
    ("image", "unused_partition_entry_count"): "integrity_value",
    ("image", "integrity_status"): "integrity_value",
    ("image", "rebuilt_indicator"): "integrity_value",
    ("image", "image_integrity_status"): "integrity_value",
    ("image", "gpt_integrity_status"): "integrity_value",
    ("image", "is_rebuilt"): "integrity_value",
    ("image", "rebuilt"): "integrity_value",
    ("image", "is_intact"): "integrity_value",
    ("image", "intact"): "integrity_value",
    ("image", "has_crc_mismatch"): "integrity_value",
    ("image", "crc_mismatch"): "integrity_value",
    ("disk_image", "primary_header_crc_valid"): "integrity_value",
    ("disk_image", "header_crc_valid"): "integrity_value",
    ("disk_image", "primary_header_crc32_valid"): "integrity_value",
    ("disk_image", "header_crc32_valid"): "integrity_value",
    ("disk_image", "partition_array_crc_valid"): "integrity_value",
    ("disk_image", "partition_entry_array_crc_valid"): "integrity_value",
    ("disk_image", "partition_array_crc32_valid"): "integrity_value",
    ("disk_image", "partition_entries_crc_valid"): "integrity_value",
    ("disk_image", "header_crc32_u32_hex"): "integrity_value",
    ("disk_image", "primary_header_crc32_u32_hex"): "integrity_value",
    ("disk_image", "header_crc32_stored_u32_hex"): "integrity_value",
    ("disk_image", "header_crc32_computed_u32_hex"): "integrity_value",
    ("disk_image", "computed_header_crc32_u32_hex"): "integrity_value",
    ("disk_image", "partition_array_crc32_u32_hex"): "integrity_value",
    ("disk_image", "partition_entry_array_crc32_u32_hex"): "integrity_value",
    ("disk_image", "partition_array_crc32_stored_u32_hex"): "integrity_value",
    ("disk_image", "partition_array_crc32_computed_u32_hex"): "integrity_value",
    ("disk_image", "computed_partition_array_crc32_u32_hex"): "integrity_value",
    ("disk_image", "partition_entry_array_crc32_computed_u32_hex"): "integrity_value",
    ("disk_image", "header_crc_matches"): "integrity_value",
    ("disk_image", "partition_array_crc_matches"): "integrity_value",
    ("disk_image", "backup_header_present"): "integrity_value",
    ("disk_image", "backup_gpt_present"): "integrity_value",
    ("disk_image", "has_backup_header"): "integrity_value",
    ("disk_image", "backup_header_valid"): "integrity_value",
    ("disk_image", "backup_matches_primary"): "integrity_value",
    ("disk_image", "backup_header_matches_primary"): "integrity_value",
    ("disk_image", "primary_backup_match"): "integrity_value",
    ("disk_image", "backup_consistent"): "integrity_value",
    ("disk_image", "alternate_lba_matches_image_end"): "integrity_value",
    ("disk_image", "backup_lba_matches_image_end"): "integrity_value",
    ("disk_image", "alternate_lba_at_image_end"): "integrity_value",
    ("disk_image", "image_truncated"): "integrity_value",
    ("disk_image", "is_truncated"): "integrity_value",
    ("disk_image", "truncated"): "integrity_value",
    ("disk_image", "partitions_beyond_image_count"): "integrity_value",
    ("disk_image", "partitions_beyond_image_end_count"): "integrity_value",
    ("disk_image", "partition_beyond_image_count"): "integrity_value",
    ("disk_image", "protective_mbr_size_matches"): "integrity_value",
    ("disk_image", "protective_mbr_size_valid"): "integrity_value",
    ("disk_image", "pmbr_size_matches"): "integrity_value",
    ("disk_image", "overlapping_partitions"): "integrity_value",
    ("disk_image", "has_overlapping_partitions"): "integrity_value",
    ("disk_image", "partitions_overlap"): "integrity_value",
    ("disk_image", "zero_filled_partition_sequence"): "integrity_value",
    ("disk_image", "zero_filled_partition_list"): "integrity_value",
    ("disk_image", "zero_filled_partitions"): "integrity_value",
    ("disk_image", "zero_filled_partition_count"): "integrity_value",
    ("disk_image", "empty_partition_count"): "integrity_value",
    ("disk_image", "unused_partition_entry_count"): "integrity_value",
    ("disk_image", "integrity_status"): "integrity_value",
    ("disk_image", "rebuilt_indicator"): "integrity_value",
    ("disk_image", "image_integrity_status"): "integrity_value",
    ("disk_image", "gpt_integrity_status"): "integrity_value",
    ("disk_image", "is_rebuilt"): "integrity_value",
    ("disk_image", "rebuilt"): "integrity_value",
    ("disk_image", "is_intact"): "integrity_value",
    ("disk_image", "intact"): "integrity_value",
    ("disk_image", "has_crc_mismatch"): "integrity_value",
    ("disk_image", "crc_mismatch"): "integrity_value",
    ("dd", "primary_header_crc_valid"): "integrity_value",
    ("dd", "header_crc_valid"): "integrity_value",
    ("dd", "primary_header_crc32_valid"): "integrity_value",
    ("dd", "header_crc32_valid"): "integrity_value",
    ("dd", "partition_array_crc_valid"): "integrity_value",
    ("dd", "partition_entry_array_crc_valid"): "integrity_value",
    ("dd", "partition_array_crc32_valid"): "integrity_value",
    ("dd", "partition_entries_crc_valid"): "integrity_value",
    ("dd", "header_crc32_u32_hex"): "integrity_value",
    ("dd", "primary_header_crc32_u32_hex"): "integrity_value",
    ("dd", "header_crc32_stored_u32_hex"): "integrity_value",
    ("dd", "header_crc32_computed_u32_hex"): "integrity_value",
    ("dd", "computed_header_crc32_u32_hex"): "integrity_value",
    ("dd", "partition_array_crc32_u32_hex"): "integrity_value",
    ("dd", "partition_entry_array_crc32_u32_hex"): "integrity_value",
    ("dd", "partition_array_crc32_stored_u32_hex"): "integrity_value",
    ("dd", "partition_array_crc32_computed_u32_hex"): "integrity_value",
    ("dd", "computed_partition_array_crc32_u32_hex"): "integrity_value",
    ("dd", "partition_entry_array_crc32_computed_u32_hex"): "integrity_value",
    ("dd", "header_crc_matches"): "integrity_value",
    ("dd", "partition_array_crc_matches"): "integrity_value",
    ("dd", "backup_header_present"): "integrity_value",
    ("dd", "backup_gpt_present"): "integrity_value",
    ("dd", "has_backup_header"): "integrity_value",
    ("dd", "backup_header_valid"): "integrity_value",
    ("dd", "backup_matches_primary"): "integrity_value",
    ("dd", "backup_header_matches_primary"): "integrity_value",
    ("dd", "primary_backup_match"): "integrity_value",
    ("dd", "backup_consistent"): "integrity_value",
    ("dd", "alternate_lba_matches_image_end"): "integrity_value",
    ("dd", "backup_lba_matches_image_end"): "integrity_value",
    ("dd", "alternate_lba_at_image_end"): "integrity_value",
    ("dd", "image_truncated"): "integrity_value",
    ("dd", "is_truncated"): "integrity_value",
    ("dd", "truncated"): "integrity_value",
    ("dd", "partitions_beyond_image_count"): "integrity_value",
    ("dd", "partitions_beyond_image_end_count"): "integrity_value",
    ("dd", "partition_beyond_image_count"): "integrity_value",
    ("dd", "protective_mbr_size_matches"): "integrity_value",
    ("dd", "protective_mbr_size_valid"): "integrity_value",
    ("dd", "pmbr_size_matches"): "integrity_value",
    ("dd", "overlapping_partitions"): "integrity_value",
    ("dd", "has_overlapping_partitions"): "integrity_value",
    ("dd", "partitions_overlap"): "integrity_value",
    ("dd", "zero_filled_partition_sequence"): "integrity_value",
    ("dd", "zero_filled_partition_list"): "integrity_value",
    ("dd", "zero_filled_partitions"): "integrity_value",
    ("dd", "zero_filled_partition_count"): "integrity_value",
    ("dd", "empty_partition_count"): "integrity_value",
    ("dd", "unused_partition_entry_count"): "integrity_value",
    ("dd", "integrity_status"): "integrity_value",
    ("dd", "rebuilt_indicator"): "integrity_value",
    ("dd", "image_integrity_status"): "integrity_value",
    ("dd", "gpt_integrity_status"): "integrity_value",
    ("dd", "is_rebuilt"): "integrity_value",
    ("dd", "rebuilt"): "integrity_value",
    ("dd", "is_intact"): "integrity_value",
    ("dd", "intact"): "integrity_value",
    ("dd", "has_crc_mismatch"): "integrity_value",
    ("dd", "crc_mismatch"): "integrity_value",
    ("raw_disk", "primary_header_crc_valid"): "integrity_value",
    ("raw_disk", "header_crc_valid"): "integrity_value",
    ("raw_disk", "primary_header_crc32_valid"): "integrity_value",
    ("raw_disk", "header_crc32_valid"): "integrity_value",
    ("raw_disk", "partition_array_crc_valid"): "integrity_value",
    ("raw_disk", "partition_entry_array_crc_valid"): "integrity_value",
    ("raw_disk", "partition_array_crc32_valid"): "integrity_value",
    ("raw_disk", "partition_entries_crc_valid"): "integrity_value",
    ("raw_disk", "header_crc32_u32_hex"): "integrity_value",
    ("raw_disk", "primary_header_crc32_u32_hex"): "integrity_value",
    ("raw_disk", "header_crc32_stored_u32_hex"): "integrity_value",
    ("raw_disk", "header_crc32_computed_u32_hex"): "integrity_value",
    ("raw_disk", "computed_header_crc32_u32_hex"): "integrity_value",
    ("raw_disk", "partition_array_crc32_u32_hex"): "integrity_value",
    ("raw_disk", "partition_entry_array_crc32_u32_hex"): "integrity_value",
    ("raw_disk", "partition_array_crc32_stored_u32_hex"): "integrity_value",
    ("raw_disk", "partition_array_crc32_computed_u32_hex"): "integrity_value",
    ("raw_disk", "computed_partition_array_crc32_u32_hex"): "integrity_value",
    ("raw_disk", "partition_entry_array_crc32_computed_u32_hex"): "integrity_value",
    ("raw_disk", "header_crc_matches"): "integrity_value",
    ("raw_disk", "partition_array_crc_matches"): "integrity_value",
    ("raw_disk", "backup_header_present"): "integrity_value",
    ("raw_disk", "backup_gpt_present"): "integrity_value",
    ("raw_disk", "has_backup_header"): "integrity_value",
    ("raw_disk", "backup_header_valid"): "integrity_value",
    ("raw_disk", "backup_matches_primary"): "integrity_value",
    ("raw_disk", "backup_header_matches_primary"): "integrity_value",
    ("raw_disk", "primary_backup_match"): "integrity_value",
    ("raw_disk", "backup_consistent"): "integrity_value",
    ("raw_disk", "alternate_lba_matches_image_end"): "integrity_value",
    ("raw_disk", "backup_lba_matches_image_end"): "integrity_value",
    ("raw_disk", "alternate_lba_at_image_end"): "integrity_value",
    ("raw_disk", "image_truncated"): "integrity_value",
    ("raw_disk", "is_truncated"): "integrity_value",
    ("raw_disk", "truncated"): "integrity_value",
    ("raw_disk", "partitions_beyond_image_count"): "integrity_value",
    ("raw_disk", "partitions_beyond_image_end_count"): "integrity_value",
    ("raw_disk", "partition_beyond_image_count"): "integrity_value",
    ("raw_disk", "protective_mbr_size_matches"): "integrity_value",
    ("raw_disk", "protective_mbr_size_valid"): "integrity_value",
    ("raw_disk", "pmbr_size_matches"): "integrity_value",
    ("raw_disk", "overlapping_partitions"): "integrity_value",
    ("raw_disk", "has_overlapping_partitions"): "integrity_value",
    ("raw_disk", "partitions_overlap"): "integrity_value",
    ("raw_disk", "zero_filled_partition_sequence"): "integrity_value",
    ("raw_disk", "zero_filled_partition_list"): "integrity_value",
    ("raw_disk", "zero_filled_partitions"): "integrity_value",
    ("raw_disk", "zero_filled_partition_count"): "integrity_value",
    ("raw_disk", "empty_partition_count"): "integrity_value",
    ("raw_disk", "unused_partition_entry_count"): "integrity_value",
    ("raw_disk", "integrity_status"): "integrity_value",
    ("raw_disk", "rebuilt_indicator"): "integrity_value",
    ("raw_disk", "image_integrity_status"): "integrity_value",
    ("raw_disk", "gpt_integrity_status"): "integrity_value",
    ("raw_disk", "is_rebuilt"): "integrity_value",
    ("raw_disk", "rebuilt"): "integrity_value",
    ("raw_disk", "is_intact"): "integrity_value",
    ("raw_disk", "intact"): "integrity_value",
    ("raw_disk", "has_crc_mismatch"): "integrity_value",
    ("raw_disk", "crc_mismatch"): "integrity_value",
}

_SIZES = (512, 4096, 1024, 2048)


def _hdr(b, at):
    """Parsed GPT header at byte `at` (stored + computed CRCs), or None when `EFI PART` is absent."""
    if at < 0 or at + 92 > len(b) or bytes(b[at:at + 8]) != b"EFI PART":
        return None
    hsz, crc = struct.unpack("<II", bytes(b[at + 12:at + 20]))
    raw = bytearray(b[at:at + max(92, min(hsz, 4096))])
    raw[16:20] = b"\0\0\0\0"
    my, alt, first, last = struct.unpack("<QQQQ", bytes(b[at + 24:at + 56]))
    ent, n, esz, ecrc = struct.unpack("<QIII", bytes(b[at + 72:at + 92]))
    return {"crc": crc, "crc_calc": zlib.crc32(bytes(raw)), "my": my, "alt": alt, "first": first, "last": last,
            "guid": bytes(b[at + 56:at + 72]), "ent": ent, "n": n, "esz": esz, "ecrc": ecrc}


def _array(b, h, ss):
    a = h["ent"] * ss
    z = a + h["n"] * h["esz"]
    if h["n"] * h["esz"] > (4 << 20) or a >= len(b):
        return b""
    return bytes(b[a:min(z, len(b))])


def analyse(b):
    """Integrity facts of one raw image (after unwrap), or None if no GPT header is found at all."""
    from .disk_layout import _unwrap
    b = _unwrap(b)
    if not b or len(b) < 1024:
        return None
    ss = next((s for s in _SIZES if len(b) >= 2 * s and bytes(b[s:s + 8]) == b"EFI PART"), None)
    if ss is None:
        ss = next((s for s in _SIZES if len(b) >= 2 * s and _hdr(b, (len(b) // s - 1) * s)), None)
    if ss is None:
        return None
    N = len(b) // ss
    p = _hdr(b, ss)
    last_h = _hdr(b, (N - 1) * ss)
    bk = None
    if p is not None and 1 < p["alt"] < N:
        bk = _hdr(b, p["alt"] * ss)
    bk_any = bk or last_h
    ref = p or bk_any
    arr = _array(b, ref, ss)
    esz = ref["esz"] if ref["esz"] >= 128 else 128
    parts, unused = [], 0
    for i in range(min(ref["n"], 4096)):
        e = arr[i * esz:i * esz + 128]
        if len(e) < 128:
            break
        if e[:16] == b"\0" * 16:
            unused += 1
            continue
        s, l = struct.unpack_from("<QQ", e, 32)
        parts.append((s, l))
    f = {"ss": ss, "N": N}
    f["primary_ok"] = p is not None and p["crc"] == p["crc_calc"]
    f["hdr_crc"], f["hdr_crc_calc"] = ref["crc"], ref["crc_calc"]
    f["arr_crc"], f["arr_crc_calc"] = ref["ecrc"], zlib.crc32(arr)
    f["arr_ok"] = ref["ecrc"] == f["arr_crc_calc"] and len(arr) == ref["n"] * ref["esz"]
    if p is None:
        f["arr_ok_primary"] = False
    else:
        f["arr_ok_primary"] = f["arr_ok"]
    f["backup_present"] = p is not None and bk is not None and last_h is not None and p["alt"] == N - 1 \
        if p is not None else last_h is not None
    match = False
    if p is not None and bk_any is not None:
        q = bk_any
        match = (q["crc"] == q["crc_calc"] and q["my"] == p["alt"] and q["alt"] == 1 and q["guid"] == p["guid"]
                 and (q["first"], q["last"], q["n"], q["esz"], q["ecrc"]) == (p["first"], p["last"], p["n"], p["esz"],
                                                                             p["ecrc"])
                 and _array(b, q, ss) == _array(b, p, ss))
    f["backup_match"] = match
    f["alt_end"] = ref["alt"] == N - 1 if p is not None else False
    beyond = sum(1 for _, l in parts if l >= N)
    f["beyond"] = beyond
    f["truncated"] = (p is not None and p["alt"] >= N) or beyond > 0
    srt = sorted(parts)
    f["overlap"] = any(srt[i + 1][0] <= srt[i][1] for i in range(len(srt) - 1))
    zf = []
    for s, l in parts:
        a, z = s * ss, min((l + 1) * ss, len(b))
        seg = bytes(b[a:z]) if a < z else b""
        zf.append(seg.count(0) == len(seg))
    f["zero"], f["unused"] = zf, unused
    pm = None
    if bytes(b[510:512]) == b"\x55\xaa":
        for i in range(4):
            e = 446 + 16 * i
            if b[e + 4] == 0xEE:
                pm = struct.unpack("<I", bytes(b[e + 12:e + 16]))[0] == min(N - 1, 0xFFFFFFFF)
                break
    f["pmbr"] = pm
    crc_bad = not f["primary_ok"] or not f["arr_ok_primary"]
    if f["truncated"]:
        st = "truncated"
    elif crc_bad:
        st = "crc_mismatch"
    elif not f["backup_present"] or not match or not f["alt_end"] or pm is False or f["overlap"]:
        st = "rebuilt"
    else:
        st = "intact"
    f["status"] = st
    return f


def integrity_value(data, ctx):
    """<fmt>.<integrity field> (see the module docstring)."""
    if data is None:
        return None
    try:
        f = analyse(data)
    except Exception:  # noqa: BLE001 -- decoy / damaged input
        return None
    if f is None:
        return "none"
    k = ctx.get("field") or ""
    if "computed" in k:
        return Hex(f["hdr_crc_calc"] if k.find("header") >= 0 and "array" not in k else f["arr_crc_calc"], 8)
    if k.endswith("_u32_hex"):
        return Hex(f["arr_crc"] if "array" in k else f["hdr_crc"], 8)
    if k in ("partition_array_crc_matches",) or (k.startswith("partition_") and "crc" in k):
        return f["arr_ok_primary"]
    if "crc" in k and "header" in k:
        return f["primary_ok"]
    if k.startswith(("backup_header_present", "backup_gpt_present", "has_backup", "backup_header_valid")):
        return f["backup_present"]
    if k.startswith(("backup_", "primary_backup")):
        return f["backup_match"]
    if k.startswith(("alternate_lba", "backup_lba")):
        return f["alt_end"]
    if k in ("image_truncated", "is_truncated", "truncated"):
        return f["truncated"]
    if "beyond" in k:
        return f["beyond"]
    if "protective" in k or k.startswith("pmbr"):
        return "none" if f["pmbr"] is None else f["pmbr"]
    if "overlap" in k:
        return f["overlap"]
    if k.startswith("zero_filled_partition_") and k.endswith("count") or k == "empty_partition_count":
        return sum(f["zero"])
    if k.startswith("zero_filled"):
        return f["zero"]
    if k == "unused_partition_entry_count":
        return f["unused"]
    if k.endswith(("status", "indicator")):
        return f["status"]
    if k in ("is_rebuilt", "rebuilt"):
        return f["status"] == "rebuilt"
    if k in ("is_intact", "intact"):
        return f["status"] == "intact"
    if k in ("has_crc_mismatch", "crc_mismatch"):
        return f["status"] == "crc_mismatch"
    return None
