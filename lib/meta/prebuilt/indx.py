"""NTFS $I30 directory index records (INDX blocks of $INDEX_ALLOCATION), incl. slack (prebuilt, SPECULATIVE).

Input = one INDX block or a run of them (a carved $I30 allocation). Block (little-endian, libfsntfs): `INDX` @0,
update-sequence array offset u16 @4 / count u16 @6 (block size = (count-1)*512), LSN u64 @8, VCN u64 @16, index
header @24 {entries offset u32, index length u32 (first free byte), allocated size u32, flags u8 (1 = has children)},
all relative to @24. FIXUPS FIRST (names straddling a 512-B sector end are corrupt otherwise).
Entry: file reference u64 @0 (record = low 48 bits, sequence = high 16), entry length u16 @8, key length u16 @10,
flags u16 @12 (1 = subnode VCN at the end, 2 = last/end entry), $FILE_NAME key @16: parent ref u64 @0, created /
modified / MFT-modified / accessed FILETIMEs @8/16/24/32, allocated size u64 @40, real size u64 @48, flags u32 @56,
name length u8 @64 (chars), namespace u8 @65 (0 POSIX, 1 Win32, 2 DOS, 3 Win32&DOS), UTF-16LE name @66.
entry_names = the live entries (walked up to the index length), Python-sorted, unique; DOS 8.3 duplicates (namespace
2) dropped unless the question asks for short/8.3/DOS names. "." (a directory's self-entry, e.g. the root's) counts:
it is stored. slack_entry_names = $FILE_NAME keys carved from the bytes past the index length (deleted-file
evidence: NTFS moves the end entry left on delete and leaves the old bytes): 8-aligned candidates whose four
FILETIMEs fall in 1980..2100 and whose name decodes cleanly (same plausibility rules as INDXParse / dfir_ntfs carve);
deleted_entry_names = slack names not also live.
Per-name fields (`<what>_for_<name>` or the name quoted in the question): FILETIME -> 'YYYY-MM-DDTHH:MM:SSZ'
(7-digit fraction when answer_format shows one, as mft.*_utc). Not INDX (FILE record, renamed impostor) -> "none"."""
import re
import struct

from ..spell import Hex
from .logfile import fixup
from .mft import _filetime, _frac

_LIST = ("entry_names", "file_names", "names", "index_entry_names", "entry_count", "file_count", "index_entry_count",
         "number_of_entries", "slack_entry_names", "slack_file_names", "slack_names", "carved_entry_names",
         "slack_entry_count", "deleted_entry_names", "deleted_file_names", "deleted_names", "deleted_entry_count",
         "vcn", "index_vcn", "lsn", "logfile_lsn", "entries_offset", "index_entries_offset", "first_entry_offset",
         "index_length", "index_length_bytes", "index_size", "index_size_bytes", "first_free_byte",
         "allocated_size", "allocated_size_bytes", "index_allocated_size", "index_flags_u8_hex", "has_children",
         "is_leaf", "block_size_bytes", "index_block_size", "index_record_count", "block_count", "slack_size_bytes",
         "parent_record_number")
_PER = ("created_utc", "modified_utc", "mft_modified_utc", "accessed_utc", "changed_utc", "created", "modified",
        "accessed", "file_size", "real_size", "allocated_size", "record_number", "mft_record_number",
        "sequence_number", "parent_record_number", "namespace", "file_reference_u64_hex")
FIELDS = {
    ("indx", "entry_names"): "indx_value",
    ("indx", "file_names"): "indx_value",
    ("indx", "names"): "indx_value",
    ("indx", "index_entry_names"): "indx_value",
    ("indx", "entry_count"): "indx_value",
    ("indx", "file_count"): "indx_value",
    ("indx", "index_entry_count"): "indx_value",
    ("indx", "number_of_entries"): "indx_value",
    ("indx", "slack_entry_names"): "indx_value",
    ("indx", "slack_file_names"): "indx_value",
    ("indx", "slack_names"): "indx_value",
    ("indx", "carved_entry_names"): "indx_value",
    ("indx", "slack_entry_count"): "indx_value",
    ("indx", "deleted_entry_names"): "indx_value",
    ("indx", "deleted_file_names"): "indx_value",
    ("indx", "deleted_names"): "indx_value",
    ("indx", "deleted_entry_count"): "indx_value",
    ("indx", "vcn"): "indx_value",
    ("indx", "index_vcn"): "indx_value",
    ("indx", "lsn"): "indx_value",
    ("indx", "logfile_lsn"): "indx_value",
    ("indx", "entries_offset"): "indx_value",
    ("indx", "index_entries_offset"): "indx_value",
    ("indx", "first_entry_offset"): "indx_value",
    ("indx", "index_length"): "indx_value",
    ("indx", "index_length_bytes"): "indx_value",
    ("indx", "index_size"): "indx_value",
    ("indx", "index_size_bytes"): "indx_value",
    ("indx", "first_free_byte"): "indx_value",
    ("indx", "allocated_size"): "indx_value",
    ("indx", "allocated_size_bytes"): "indx_value",
    ("indx", "index_allocated_size"): "indx_value",
    ("indx", "index_flags_u8_hex"): "indx_value",
    ("indx", "has_children"): "indx_value",
    ("indx", "is_leaf"): "indx_value",
    ("indx", "block_size_bytes"): "indx_value",
    ("indx", "index_block_size"): "indx_value",
    ("indx", "index_record_count"): "indx_value",
    ("indx", "block_count"): "indx_value",
    ("indx", "slack_size_bytes"): "indx_value",
    ("indx", "parent_record_number"): "indx_value",
    ("indx", "entry_created_utc"): "indx_value",
    ("indx", "created_utc_for_*"): "indx_value",
    ("indx", "entry_created_utc_for_*"): "indx_value",
    ("indx", "entry_modified_utc"): "indx_value",
    ("indx", "modified_utc_for_*"): "indx_value",
    ("indx", "entry_modified_utc_for_*"): "indx_value",
    ("indx", "entry_mft_modified_utc"): "indx_value",
    ("indx", "mft_modified_utc_for_*"): "indx_value",
    ("indx", "entry_mft_modified_utc_for_*"): "indx_value",
    ("indx", "entry_accessed_utc"): "indx_value",
    ("indx", "accessed_utc_for_*"): "indx_value",
    ("indx", "entry_accessed_utc_for_*"): "indx_value",
    ("indx", "entry_changed_utc"): "indx_value",
    ("indx", "changed_utc_for_*"): "indx_value",
    ("indx", "entry_changed_utc_for_*"): "indx_value",
    ("indx", "entry_created"): "indx_value",
    ("indx", "created_for_*"): "indx_value",
    ("indx", "entry_created_for_*"): "indx_value",
    ("indx", "entry_modified"): "indx_value",
    ("indx", "modified_for_*"): "indx_value",
    ("indx", "entry_modified_for_*"): "indx_value",
    ("indx", "entry_accessed"): "indx_value",
    ("indx", "accessed_for_*"): "indx_value",
    ("indx", "entry_accessed_for_*"): "indx_value",
    ("indx", "entry_file_size"): "indx_value",
    ("indx", "file_size_for_*"): "indx_value",
    ("indx", "entry_file_size_for_*"): "indx_value",
    ("indx", "entry_real_size"): "indx_value",
    ("indx", "real_size_for_*"): "indx_value",
    ("indx", "entry_real_size_for_*"): "indx_value",
    ("indx", "entry_allocated_size"): "indx_value",
    ("indx", "allocated_size_for_*"): "indx_value",
    ("indx", "entry_allocated_size_for_*"): "indx_value",
    ("indx", "entry_record_number"): "indx_value",
    ("indx", "record_number_for_*"): "indx_value",
    ("indx", "entry_record_number_for_*"): "indx_value",
    ("indx", "entry_mft_record_number"): "indx_value",
    ("indx", "mft_record_number_for_*"): "indx_value",
    ("indx", "entry_mft_record_number_for_*"): "indx_value",
    ("indx", "entry_sequence_number"): "indx_value",
    ("indx", "sequence_number_for_*"): "indx_value",
    ("indx", "entry_sequence_number_for_*"): "indx_value",
    ("indx", "entry_parent_record_number"): "indx_value",
    ("indx", "parent_record_number_for_*"): "indx_value",
    ("indx", "entry_parent_record_number_for_*"): "indx_value",
    ("indx", "entry_namespace"): "indx_value",
    ("indx", "namespace_for_*"): "indx_value",
    ("indx", "entry_namespace_for_*"): "indx_value",
    ("indx", "entry_file_reference_u64_hex"): "indx_value",
    ("indx", "file_reference_u64_hex_for_*"): "indx_value",
    ("indx", "entry_file_reference_u64_hex_for_*"): "indx_value",
    ("i30", "entry_names"): "indx_value",
    ("i30", "file_names"): "indx_value",
    ("i30", "names"): "indx_value",
    ("i30", "index_entry_names"): "indx_value",
    ("i30", "entry_count"): "indx_value",
    ("i30", "file_count"): "indx_value",
    ("i30", "index_entry_count"): "indx_value",
    ("i30", "number_of_entries"): "indx_value",
    ("i30", "slack_entry_names"): "indx_value",
    ("i30", "slack_file_names"): "indx_value",
    ("i30", "slack_names"): "indx_value",
    ("i30", "carved_entry_names"): "indx_value",
    ("i30", "slack_entry_count"): "indx_value",
    ("i30", "deleted_entry_names"): "indx_value",
    ("i30", "deleted_file_names"): "indx_value",
    ("i30", "deleted_names"): "indx_value",
    ("i30", "deleted_entry_count"): "indx_value",
    ("i30", "vcn"): "indx_value",
    ("i30", "index_vcn"): "indx_value",
    ("i30", "lsn"): "indx_value",
    ("i30", "logfile_lsn"): "indx_value",
    ("i30", "entries_offset"): "indx_value",
    ("i30", "index_entries_offset"): "indx_value",
    ("i30", "first_entry_offset"): "indx_value",
    ("i30", "index_length"): "indx_value",
    ("i30", "index_length_bytes"): "indx_value",
    ("i30", "index_size"): "indx_value",
    ("i30", "index_size_bytes"): "indx_value",
    ("i30", "first_free_byte"): "indx_value",
    ("i30", "allocated_size"): "indx_value",
    ("i30", "allocated_size_bytes"): "indx_value",
    ("i30", "index_allocated_size"): "indx_value",
    ("i30", "index_flags_u8_hex"): "indx_value",
    ("i30", "has_children"): "indx_value",
    ("i30", "is_leaf"): "indx_value",
    ("i30", "block_size_bytes"): "indx_value",
    ("i30", "index_block_size"): "indx_value",
    ("i30", "index_record_count"): "indx_value",
    ("i30", "block_count"): "indx_value",
    ("i30", "slack_size_bytes"): "indx_value",
    ("i30", "parent_record_number"): "indx_value",
    ("i30", "entry_created_utc"): "indx_value",
    ("i30", "created_utc_for_*"): "indx_value",
    ("i30", "entry_created_utc_for_*"): "indx_value",
    ("i30", "entry_modified_utc"): "indx_value",
    ("i30", "modified_utc_for_*"): "indx_value",
    ("i30", "entry_modified_utc_for_*"): "indx_value",
    ("i30", "entry_mft_modified_utc"): "indx_value",
    ("i30", "mft_modified_utc_for_*"): "indx_value",
    ("i30", "entry_mft_modified_utc_for_*"): "indx_value",
    ("i30", "entry_accessed_utc"): "indx_value",
    ("i30", "accessed_utc_for_*"): "indx_value",
    ("i30", "entry_accessed_utc_for_*"): "indx_value",
    ("i30", "entry_changed_utc"): "indx_value",
    ("i30", "changed_utc_for_*"): "indx_value",
    ("i30", "entry_changed_utc_for_*"): "indx_value",
    ("i30", "entry_created"): "indx_value",
    ("i30", "created_for_*"): "indx_value",
    ("i30", "entry_created_for_*"): "indx_value",
    ("i30", "entry_modified"): "indx_value",
    ("i30", "modified_for_*"): "indx_value",
    ("i30", "entry_modified_for_*"): "indx_value",
    ("i30", "entry_accessed"): "indx_value",
    ("i30", "accessed_for_*"): "indx_value",
    ("i30", "entry_accessed_for_*"): "indx_value",
    ("i30", "entry_file_size"): "indx_value",
    ("i30", "file_size_for_*"): "indx_value",
    ("i30", "entry_file_size_for_*"): "indx_value",
    ("i30", "entry_real_size"): "indx_value",
    ("i30", "real_size_for_*"): "indx_value",
    ("i30", "entry_real_size_for_*"): "indx_value",
    ("i30", "entry_allocated_size"): "indx_value",
    ("i30", "allocated_size_for_*"): "indx_value",
    ("i30", "entry_allocated_size_for_*"): "indx_value",
    ("i30", "entry_record_number"): "indx_value",
    ("i30", "record_number_for_*"): "indx_value",
    ("i30", "entry_record_number_for_*"): "indx_value",
    ("i30", "entry_mft_record_number"): "indx_value",
    ("i30", "mft_record_number_for_*"): "indx_value",
    ("i30", "entry_mft_record_number_for_*"): "indx_value",
    ("i30", "entry_sequence_number"): "indx_value",
    ("i30", "sequence_number_for_*"): "indx_value",
    ("i30", "entry_sequence_number_for_*"): "indx_value",
    ("i30", "entry_parent_record_number"): "indx_value",
    ("i30", "parent_record_number_for_*"): "indx_value",
    ("i30", "entry_parent_record_number_for_*"): "indx_value",
    ("i30", "entry_namespace"): "indx_value",
    ("i30", "namespace_for_*"): "indx_value",
    ("i30", "entry_namespace_for_*"): "indx_value",
    ("i30", "entry_file_reference_u64_hex"): "indx_value",
    ("i30", "file_reference_u64_hex_for_*"): "indx_value",
    ("i30", "entry_file_reference_u64_hex_for_*"): "indx_value",
    ("index_record", "entry_names"): "indx_value",
    ("index_record", "file_names"): "indx_value",
    ("index_record", "names"): "indx_value",
    ("index_record", "index_entry_names"): "indx_value",
    ("index_record", "entry_count"): "indx_value",
    ("index_record", "file_count"): "indx_value",
    ("index_record", "index_entry_count"): "indx_value",
    ("index_record", "number_of_entries"): "indx_value",
    ("index_record", "slack_entry_names"): "indx_value",
    ("index_record", "slack_file_names"): "indx_value",
    ("index_record", "slack_names"): "indx_value",
    ("index_record", "carved_entry_names"): "indx_value",
    ("index_record", "slack_entry_count"): "indx_value",
    ("index_record", "deleted_entry_names"): "indx_value",
    ("index_record", "deleted_file_names"): "indx_value",
    ("index_record", "deleted_names"): "indx_value",
    ("index_record", "deleted_entry_count"): "indx_value",
    ("index_record", "vcn"): "indx_value",
    ("index_record", "index_vcn"): "indx_value",
    ("index_record", "lsn"): "indx_value",
    ("index_record", "logfile_lsn"): "indx_value",
    ("index_record", "entries_offset"): "indx_value",
    ("index_record", "index_entries_offset"): "indx_value",
    ("index_record", "first_entry_offset"): "indx_value",
    ("index_record", "index_length"): "indx_value",
    ("index_record", "index_length_bytes"): "indx_value",
    ("index_record", "index_size"): "indx_value",
    ("index_record", "index_size_bytes"): "indx_value",
    ("index_record", "first_free_byte"): "indx_value",
    ("index_record", "allocated_size"): "indx_value",
    ("index_record", "allocated_size_bytes"): "indx_value",
    ("index_record", "index_allocated_size"): "indx_value",
    ("index_record", "index_flags_u8_hex"): "indx_value",
    ("index_record", "has_children"): "indx_value",
    ("index_record", "is_leaf"): "indx_value",
    ("index_record", "block_size_bytes"): "indx_value",
    ("index_record", "index_block_size"): "indx_value",
    ("index_record", "index_record_count"): "indx_value",
    ("index_record", "block_count"): "indx_value",
    ("index_record", "slack_size_bytes"): "indx_value",
    ("index_record", "parent_record_number"): "indx_value",
    ("index_record", "entry_created_utc"): "indx_value",
    ("index_record", "created_utc_for_*"): "indx_value",
    ("index_record", "entry_created_utc_for_*"): "indx_value",
    ("index_record", "entry_modified_utc"): "indx_value",
    ("index_record", "modified_utc_for_*"): "indx_value",
    ("index_record", "entry_modified_utc_for_*"): "indx_value",
    ("index_record", "entry_mft_modified_utc"): "indx_value",
    ("index_record", "mft_modified_utc_for_*"): "indx_value",
    ("index_record", "entry_mft_modified_utc_for_*"): "indx_value",
    ("index_record", "entry_accessed_utc"): "indx_value",
    ("index_record", "accessed_utc_for_*"): "indx_value",
    ("index_record", "entry_accessed_utc_for_*"): "indx_value",
    ("index_record", "entry_changed_utc"): "indx_value",
    ("index_record", "changed_utc_for_*"): "indx_value",
    ("index_record", "entry_changed_utc_for_*"): "indx_value",
    ("index_record", "entry_created"): "indx_value",
    ("index_record", "created_for_*"): "indx_value",
    ("index_record", "entry_created_for_*"): "indx_value",
    ("index_record", "entry_modified"): "indx_value",
    ("index_record", "modified_for_*"): "indx_value",
    ("index_record", "entry_modified_for_*"): "indx_value",
    ("index_record", "entry_accessed"): "indx_value",
    ("index_record", "accessed_for_*"): "indx_value",
    ("index_record", "entry_accessed_for_*"): "indx_value",
    ("index_record", "entry_file_size"): "indx_value",
    ("index_record", "file_size_for_*"): "indx_value",
    ("index_record", "entry_file_size_for_*"): "indx_value",
    ("index_record", "entry_real_size"): "indx_value",
    ("index_record", "real_size_for_*"): "indx_value",
    ("index_record", "entry_real_size_for_*"): "indx_value",
    ("index_record", "entry_allocated_size"): "indx_value",
    ("index_record", "allocated_size_for_*"): "indx_value",
    ("index_record", "entry_allocated_size_for_*"): "indx_value",
    ("index_record", "entry_record_number"): "indx_value",
    ("index_record", "record_number_for_*"): "indx_value",
    ("index_record", "entry_record_number_for_*"): "indx_value",
    ("index_record", "entry_mft_record_number"): "indx_value",
    ("index_record", "mft_record_number_for_*"): "indx_value",
    ("index_record", "entry_mft_record_number_for_*"): "indx_value",
    ("index_record", "entry_sequence_number"): "indx_value",
    ("index_record", "sequence_number_for_*"): "indx_value",
    ("index_record", "entry_sequence_number_for_*"): "indx_value",
    ("index_record", "entry_parent_record_number"): "indx_value",
    ("index_record", "parent_record_number_for_*"): "indx_value",
    ("index_record", "entry_parent_record_number_for_*"): "indx_value",
    ("index_record", "entry_namespace"): "indx_value",
    ("index_record", "namespace_for_*"): "indx_value",
    ("index_record", "entry_namespace_for_*"): "indx_value",
    ("index_record", "entry_file_reference_u64_hex"): "indx_value",
    ("index_record", "file_reference_u64_hex_for_*"): "indx_value",
    ("index_record", "entry_file_reference_u64_hex_for_*"): "indx_value",
    ("ntfs_index", "entry_names"): "indx_value",
    ("ntfs_index", "file_names"): "indx_value",
    ("ntfs_index", "names"): "indx_value",
    ("ntfs_index", "index_entry_names"): "indx_value",
    ("ntfs_index", "entry_count"): "indx_value",
    ("ntfs_index", "file_count"): "indx_value",
    ("ntfs_index", "index_entry_count"): "indx_value",
    ("ntfs_index", "number_of_entries"): "indx_value",
    ("ntfs_index", "slack_entry_names"): "indx_value",
    ("ntfs_index", "slack_file_names"): "indx_value",
    ("ntfs_index", "slack_names"): "indx_value",
    ("ntfs_index", "carved_entry_names"): "indx_value",
    ("ntfs_index", "slack_entry_count"): "indx_value",
    ("ntfs_index", "deleted_entry_names"): "indx_value",
    ("ntfs_index", "deleted_file_names"): "indx_value",
    ("ntfs_index", "deleted_names"): "indx_value",
    ("ntfs_index", "deleted_entry_count"): "indx_value",
    ("ntfs_index", "vcn"): "indx_value",
    ("ntfs_index", "index_vcn"): "indx_value",
    ("ntfs_index", "lsn"): "indx_value",
    ("ntfs_index", "logfile_lsn"): "indx_value",
    ("ntfs_index", "entries_offset"): "indx_value",
    ("ntfs_index", "index_entries_offset"): "indx_value",
    ("ntfs_index", "first_entry_offset"): "indx_value",
    ("ntfs_index", "index_length"): "indx_value",
    ("ntfs_index", "index_length_bytes"): "indx_value",
    ("ntfs_index", "index_size"): "indx_value",
    ("ntfs_index", "index_size_bytes"): "indx_value",
    ("ntfs_index", "first_free_byte"): "indx_value",
    ("ntfs_index", "allocated_size"): "indx_value",
    ("ntfs_index", "allocated_size_bytes"): "indx_value",
    ("ntfs_index", "index_allocated_size"): "indx_value",
    ("ntfs_index", "index_flags_u8_hex"): "indx_value",
    ("ntfs_index", "has_children"): "indx_value",
    ("ntfs_index", "is_leaf"): "indx_value",
    ("ntfs_index", "block_size_bytes"): "indx_value",
    ("ntfs_index", "index_block_size"): "indx_value",
    ("ntfs_index", "index_record_count"): "indx_value",
    ("ntfs_index", "block_count"): "indx_value",
    ("ntfs_index", "slack_size_bytes"): "indx_value",
    ("ntfs_index", "parent_record_number"): "indx_value",
    ("ntfs_index", "entry_created_utc"): "indx_value",
    ("ntfs_index", "created_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_created_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_modified_utc"): "indx_value",
    ("ntfs_index", "modified_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_modified_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_mft_modified_utc"): "indx_value",
    ("ntfs_index", "mft_modified_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_mft_modified_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_accessed_utc"): "indx_value",
    ("ntfs_index", "accessed_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_accessed_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_changed_utc"): "indx_value",
    ("ntfs_index", "changed_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_changed_utc_for_*"): "indx_value",
    ("ntfs_index", "entry_created"): "indx_value",
    ("ntfs_index", "created_for_*"): "indx_value",
    ("ntfs_index", "entry_created_for_*"): "indx_value",
    ("ntfs_index", "entry_modified"): "indx_value",
    ("ntfs_index", "modified_for_*"): "indx_value",
    ("ntfs_index", "entry_modified_for_*"): "indx_value",
    ("ntfs_index", "entry_accessed"): "indx_value",
    ("ntfs_index", "accessed_for_*"): "indx_value",
    ("ntfs_index", "entry_accessed_for_*"): "indx_value",
    ("ntfs_index", "entry_file_size"): "indx_value",
    ("ntfs_index", "file_size_for_*"): "indx_value",
    ("ntfs_index", "entry_file_size_for_*"): "indx_value",
    ("ntfs_index", "entry_real_size"): "indx_value",
    ("ntfs_index", "real_size_for_*"): "indx_value",
    ("ntfs_index", "entry_real_size_for_*"): "indx_value",
    ("ntfs_index", "entry_allocated_size"): "indx_value",
    ("ntfs_index", "allocated_size_for_*"): "indx_value",
    ("ntfs_index", "entry_allocated_size_for_*"): "indx_value",
    ("ntfs_index", "entry_record_number"): "indx_value",
    ("ntfs_index", "record_number_for_*"): "indx_value",
    ("ntfs_index", "entry_record_number_for_*"): "indx_value",
    ("ntfs_index", "entry_mft_record_number"): "indx_value",
    ("ntfs_index", "mft_record_number_for_*"): "indx_value",
    ("ntfs_index", "entry_mft_record_number_for_*"): "indx_value",
    ("ntfs_index", "entry_sequence_number"): "indx_value",
    ("ntfs_index", "sequence_number_for_*"): "indx_value",
    ("ntfs_index", "entry_sequence_number_for_*"): "indx_value",
    ("ntfs_index", "entry_parent_record_number"): "indx_value",
    ("ntfs_index", "parent_record_number_for_*"): "indx_value",
    ("ntfs_index", "entry_parent_record_number_for_*"): "indx_value",
    ("ntfs_index", "entry_namespace"): "indx_value",
    ("ntfs_index", "namespace_for_*"): "indx_value",
    ("ntfs_index", "entry_namespace_for_*"): "indx_value",
    ("ntfs_index", "entry_file_reference_u64_hex"): "indx_value",
    ("ntfs_index", "file_reference_u64_hex_for_*"): "indx_value",
    ("ntfs_index", "entry_file_reference_u64_hex_for_*"): "indx_value",
}

_FT_LO, _FT_HI = 119_600_064_000_000_000, 157_288_000_000_000_000   # 1980-01-01 .. 2099-06 (FILETIME)


def _key(b, o, end):
    """A $FILE_NAME key at b[o:], or None."""
    if o + 66 > end:
        return None
    nl, ns = b[o + 64], b[o + 65]
    if nl == 0 or ns > 3 or o + 66 + 2 * nl > end:
        return None
    try:
        name = bytes(b[o + 66:o + 66 + 2 * nl]).decode("utf-16-le")
    except UnicodeDecodeError:
        return None
    parent, cr, mo, mc, ac, alloc, real, flags = struct.unpack_from("<QQQQQQQI", b, o)
    return {"name": name, "ns": ns, "parent": parent, "created": cr, "modified": mo, "mft_modified": mc,
            "accessed": ac, "alloc": alloc, "real": real, "flags": flags}


def _plausible(k):
    if any(c in k["name"] for c in "\x00/") or not k["name"].isprintable():
        return False
    return all(_FT_LO <= k[t] <= _FT_HI for t in ("created", "modified", "mft_modified", "accessed"))


def _block(raw):
    b = fixup(raw)
    if b is None:
        return None
    eo, ilen, alen, hflags = struct.unpack_from("<IIIB", b, 24)
    start, stop = 24 + eo, min(24 + ilen, len(b))
    live, pos = [], start
    while pos + 16 <= stop:
        ref, ln, kl, fl = struct.unpack_from("<QHHH", b, pos)
        if ln < 16 or pos + ln > len(b):
            break
        if not fl & 2 and kl >= 66:
            k = _key(b, pos + 16, pos + 16 + kl)
            if k:
                k["ref"] = ref
                live.append(k)
        if fl & 2:
            break
        pos += ln
    slack = []
    for o in range((stop + 7) & ~7, len(b) - 66, 8):
        k = _key(b, o, len(b))
        if k and _plausible(k):
            k["ref"] = struct.unpack_from("<Q", b, o - 16)[0] if o >= 16 else 0
            slack.append(k)
    return {"lsn": struct.unpack_from("<Q", b, 8)[0], "vcn": struct.unpack_from("<Q", b, 16)[0], "eo": eo,
            "ilen": ilen, "alen": alen, "hflags": hflags, "size": len(b), "live": live, "slack": slack,
            "slack_bytes": len(b) - stop}


def parse(data):
    blocks = []
    if data[:4] != b"INDX":
        return blocks
    o = 0
    while o + 512 <= len(data) and data[o:o + 4] == b"INDX":
        cnt = struct.unpack_from("<H", data, o + 6)[0]
        size = (cnt - 1) * 512 if cnt > 1 else 4096
        blk = _block(data[o:o + size])
        if blk is None:
            break
        blocks.append(blk)
        o += size
    return blocks


def _names(ents, dos):
    return sorted({e["name"] for e in ents if dos or e["ns"] != 2})


def _norm(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _pick(ents, param, q):
    if param:
        for e in ents:
            if _norm(e["name"]) == _norm(param):
                return e
    text = str((q or {}).get("question") or "")
    hits = [e for e in ents if e["name"] not in (".",) and re.search(r"(?<![\w.])%s(?![\w])" % re.escape(e["name"]),
                                                                      text)]
    if hits:
        return max(hits, key=lambda e: len(e["name"]))
    real = [e for e in ents if not e["name"].startswith("$") and e["name"] != "." and e["ns"] != 2]
    return real[0] if len(real) == 1 else None


def indx_value(data, ctx):
    if data is None:
        return None
    f = ctx.get("field") or ""
    blocks = parse(bytes(data[:1 << 26]))
    if not blocks:
        return "none"
    q = ctx.get("question") or {}
    qtext = str(q.get("question") or "") if isinstance(q, dict) else str(q)
    dos = bool(re.search(r"8\.3|\bDOS\b|short name", qtext, re.I))
    live = [e for blk in blocks for e in blk["live"]]
    slack = [e for blk in blocks for e in blk["slack"]]
    first = blocks[0]
    if f in ("entry_names", "file_names", "names", "index_entry_names"):
        return _names(live, dos)
    if f in ("entry_count", "file_count", "index_entry_count", "number_of_entries"):
        return len(_names(live, dos))
    if f in ("slack_entry_names", "slack_file_names", "slack_names", "carved_entry_names"):
        return _names(slack, dos)
    if f == "slack_entry_count":
        return len(_names(slack, dos))
    if f.startswith("deleted_"):
        gone = [n for n in _names(slack, dos) if n not in set(_names(live, True))]
        return len(gone) if f.endswith("count") else gone
    if f in ("vcn", "index_vcn"):
        return first["vcn"]
    if f in ("lsn", "logfile_lsn"):
        return first["lsn"]
    if f in ("entries_offset", "index_entries_offset", "first_entry_offset"):
        return first["eo"]
    if f in ("index_length", "index_length_bytes", "index_size", "index_size_bytes", "first_free_byte"):
        return first["ilen"]
    if f in ("allocated_size", "allocated_size_bytes", "index_allocated_size"):
        return first["alen"]
    if f == "index_flags_u8_hex":
        return Hex(first["hflags"], 2)
    if f == "has_children":
        return bool(first["hflags"] & 1)
    if f == "is_leaf":
        return not first["hflags"] & 1
    if f in ("block_size_bytes", "index_block_size"):
        return first["size"]
    if f in ("index_record_count", "block_count"):
        return len(blocks)
    if f == "slack_size_bytes":
        return first["slack_bytes"]
    if f == "parent_record_number":
        ps = {e["parent"] & 0xFFFFFFFFFFFF for e in live if e["name"] != "."}
        return ps.pop() if len(ps) == 1 else None
    # per-name: entry_<what>, <what>_for_<name>, entry_<what>_for_<name>
    what = re.sub(r"^entry_", "", f)
    what = re.sub(r"_for_.*$", "", what)
    e = _pick(live + slack, ctx.get("param"), q)
    if e is None:
        return None
    if what in ("created_utc", "created"):
        return _filetime(e["created"], _frac(q))
    if what in ("modified_utc", "modified"):
        return _filetime(e["modified"], _frac(q))
    if what in ("mft_modified_utc", "changed_utc"):
        return _filetime(e["mft_modified"], _frac(q))
    if what in ("accessed_utc", "accessed"):
        return _filetime(e["accessed"], _frac(q))
    if what in ("file_size", "real_size"):
        return e["real"]
    if what == "allocated_size":
        return e["alloc"]
    if what in ("record_number", "mft_record_number"):
        return e["ref"] & 0xFFFFFFFFFFFF
    if what == "sequence_number":
        return e["ref"] >> 48
    if what == "parent_record_number":
        return e["parent"] & 0xFFFFFFFFFFFF
    if what == "namespace":
        return e["ns"]
    if what == "file_reference_u64_hex":
        return Hex(e["ref"], 16)
    return None
