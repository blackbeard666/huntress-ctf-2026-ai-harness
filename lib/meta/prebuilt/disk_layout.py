"""Raw disk-image PARTITION LAYOUT fields (prebuilt, SPECULATIVE): siblings of the GM-verified D28
`disk.partition_start_lba_sequence` (lib/meta/disk.py) on a RAW image (.img/.dd/.raw). The `disk` fmt word collides
with the virtual-disk containers in prebuilt/disk.py (VHD/VHDX/VMDK/QCOW2 header fields); these keys are only the
partition-table ones, so they parse the bytes as a raw sector image whatever container magic is (or is not) there.
Also registered under image / raw_disk / disk_image / dd / gpt / mbr / partition_table (keys vbr.py lacks).

GPT first: `EFI PART` at LBA1, probing 512 then 4096 (1024/2048) byte sectors -- same probe order as the verified
extractor. Header: current/alternate/first-usable/last-usable LBA u64 @+24/+32/+40/+48, disk GUID @+56, entry-array LBA
u64 @+72, entry count u32 @+80, entry size u32 @+84. Entries: type GUID @0, unique GUID @16, first/last LBA u64 @32/@40
(last INCLUSIVE), attributes u64 @48, name UTF-16LE @56 (72 B, cut at NUL); a zero type GUID = unused slot, skipped.
GUIDs mixed-endian -> lowercase canonical (uuid bytes_le, as sfdisk/sgdisk print them, lowercased).
Else MBR: 0x55AA @510, signature u32 @0x1B8, 4 x 16 B @0x1BE {flag @0, type @4, LBA u32 @8, count u32 @12}; zero type
skipped; an extended container (05/0f/85) stays in the list (as in the verified start-LBA sequence and as sfdisk lists
it) followed by its EBR chain: logical start = EBR LBA + rel, next EBR = extended start + rel.
Sequences (`partition_<x>_sequence` / `_list` / plural) are TABLE order, compact JSON, never sorted. end = last LBA
(MBR start+count-1); sector_count = end-start+1; size_bytes / start_offset_bytes = x sector size; type = MBR `0x%02x`
(GPT: the type GUIDs); attributes = `0x%016x` (GPT only). partition_table_type = `gpt` / `dos` as sfdisk prints
`label:`. largest_partition_index = 0-based TABLE SLOT (GPT entry-array index; MBR slot 0-3, logicals 4.. as Linux
numbers them minus one; extended containers excluded; ties -> first). GPT-only fields on an MBR disk, or no
partition table at all -> "none".
CARRIED-FAMILY HARDENING (D29+ TT/Mastery mutations of disk-001.img): the bytes are UNWRAPPED first -- gzip / xz / bzip2
(capped at 512 MiB), fixed VHD (512 B `conectix` footer stripped so the last LBA is the backup GPT's), dynamic VHD
(BAT), hosted sparse + streamOptimized VMDK (`KDMV`, grain directory/tables, deflated grains), qcow2 (L1/L2, compressed
clusters) -- read lazily through _Virt. A VMDK monolithicFlat DESCRIPTOR has no sectors -> "none"; its -flat extent is
raw. GPT: a primary whose header CRC32 / MyLBA / entry-array CRC32 fails (or a zeroed LBA1) yields to a CRC-valid BACKUP
header (primary's AlternateLBA, else the image's last LBA; its entry array sits before it); an image cut before the
backup keeps a valid primary. Entry size from the header (256 ok), entry count any, empty slots skipped, table order.
NOTE: the GM-verified `disk.partition_start_lba_sequence` key still runs lib/meta/disk.py (no unwrap, no backup
fallback); these shapes reach the same walk only via the aliases here (dd/gpt/image/... and disk.partition_start_lbas)."""
import bz2
import lzma
import struct
import uuid
import zlib

from ..spell import Hex

FIELDS = {
    ("disk", "partition_start_lba_list"): "layout_value",
    ("disk", "partition_start_lbas"): "layout_value",
    ("disk", "partition_end_lba_sequence"): "layout_value",
    ("disk", "partition_end_lba_list"): "layout_value",
    ("disk", "partition_end_lbas"): "layout_value",
    ("disk", "partition_last_lba_sequence"): "layout_value",
    ("disk", "partition_last_lba_list"): "layout_value",
    ("disk", "partition_last_lbas"): "layout_value",
    ("disk", "partition_sector_count_sequence"): "layout_value",
    ("disk", "partition_sector_count_list"): "layout_value",
    ("disk", "partition_sector_counts"): "layout_value",
    ("disk", "partition_size_bytes_sequence"): "layout_value",
    ("disk", "partition_size_bytes_list"): "layout_value",
    ("disk", "partition_sizes_bytes"): "layout_value",
    ("disk", "partition_start_offset_bytes_sequence"): "layout_value",
    ("disk", "partition_start_offset_bytes_list"): "layout_value",
    ("disk", "partition_start_offsets_bytes"): "layout_value",
    ("disk", "partition_name_sequence"): "layout_value",
    ("disk", "partition_name_list"): "layout_value",
    ("disk", "partition_names"): "layout_value",
    ("disk", "partition_type_guid_sequence"): "layout_value",
    ("disk", "partition_type_guid_list"): "layout_value",
    ("disk", "partition_type_guids"): "layout_value",
    ("disk", "partition_unique_guid_sequence"): "layout_value",
    ("disk", "partition_unique_guid_list"): "layout_value",
    ("disk", "partition_unique_guids"): "layout_value",
    ("disk", "partition_type_sequence"): "layout_value",
    ("disk", "partition_type_list"): "layout_value",
    ("disk", "partition_types"): "layout_value",
    ("disk", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("disk", "partition_attributes_u64_hex_list"): "layout_value",
    ("disk", "partition_count"): "layout_value",
    ("disk", "partition_table_type"): "layout_value",
    ("disk", "disk_guid"): "layout_value",
    ("disk", "disk_signature_u32_hex"): "layout_value",
    ("disk", "sector_size_bytes"): "layout_value",
    ("disk", "first_usable_lba"): "layout_value",
    ("disk", "last_usable_lba"): "layout_value",
    ("disk", "alternate_lba"): "layout_value",
    ("disk", "backup_lba"): "layout_value",
    ("disk", "backup_header_lba"): "layout_value",
    ("disk", "partition_entry_lba"): "layout_value",
    ("disk", "partition_entry_count"): "layout_value",
    ("disk", "partition_entry_size_bytes"): "layout_value",
    ("disk", "image_size_bytes"): "layout_value",
    ("disk", "image_sector_count"): "layout_value",
    ("disk", "largest_partition_index"): "layout_value",
    ("disk", "largest_partition_name"): "layout_value",
    ("image", "partition_start_lba_sequence"): "layout_value",
    ("image", "partition_start_lba_list"): "layout_value",
    ("image", "partition_start_lbas"): "layout_value",
    ("image", "partition_end_lba_sequence"): "layout_value",
    ("image", "partition_end_lba_list"): "layout_value",
    ("image", "partition_end_lbas"): "layout_value",
    ("image", "partition_last_lba_sequence"): "layout_value",
    ("image", "partition_last_lba_list"): "layout_value",
    ("image", "partition_last_lbas"): "layout_value",
    ("image", "partition_sector_count_sequence"): "layout_value",
    ("image", "partition_sector_count_list"): "layout_value",
    ("image", "partition_sector_counts"): "layout_value",
    ("image", "partition_size_bytes_sequence"): "layout_value",
    ("image", "partition_size_bytes_list"): "layout_value",
    ("image", "partition_sizes_bytes"): "layout_value",
    ("image", "partition_start_offset_bytes_sequence"): "layout_value",
    ("image", "partition_start_offset_bytes_list"): "layout_value",
    ("image", "partition_start_offsets_bytes"): "layout_value",
    ("image", "partition_name_sequence"): "layout_value",
    ("image", "partition_name_list"): "layout_value",
    ("image", "partition_names"): "layout_value",
    ("image", "partition_type_guid_sequence"): "layout_value",
    ("image", "partition_type_guid_list"): "layout_value",
    ("image", "partition_type_guids"): "layout_value",
    ("image", "partition_unique_guid_sequence"): "layout_value",
    ("image", "partition_unique_guid_list"): "layout_value",
    ("image", "partition_unique_guids"): "layout_value",
    ("image", "partition_type_sequence"): "layout_value",
    ("image", "partition_type_list"): "layout_value",
    ("image", "partition_types"): "layout_value",
    ("image", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("image", "partition_attributes_u64_hex_list"): "layout_value",
    ("image", "partition_count"): "layout_value",
    ("image", "partition_table_type"): "layout_value",
    ("image", "disk_guid"): "layout_value",
    ("image", "disk_signature_u32_hex"): "layout_value",
    ("image", "sector_size_bytes"): "layout_value",
    ("image", "first_usable_lba"): "layout_value",
    ("image", "last_usable_lba"): "layout_value",
    ("image", "alternate_lba"): "layout_value",
    ("image", "backup_lba"): "layout_value",
    ("image", "backup_header_lba"): "layout_value",
    ("image", "partition_entry_lba"): "layout_value",
    ("image", "partition_entry_count"): "layout_value",
    ("image", "partition_entry_size_bytes"): "layout_value",
    ("image", "image_size_bytes"): "layout_value",
    ("image", "image_sector_count"): "layout_value",
    ("image", "largest_partition_index"): "layout_value",
    ("image", "largest_partition_name"): "layout_value",
    ("raw_disk", "partition_start_lba_sequence"): "layout_value",
    ("raw_disk", "partition_start_lba_list"): "layout_value",
    ("raw_disk", "partition_start_lbas"): "layout_value",
    ("raw_disk", "partition_end_lba_sequence"): "layout_value",
    ("raw_disk", "partition_end_lba_list"): "layout_value",
    ("raw_disk", "partition_end_lbas"): "layout_value",
    ("raw_disk", "partition_last_lba_sequence"): "layout_value",
    ("raw_disk", "partition_last_lba_list"): "layout_value",
    ("raw_disk", "partition_last_lbas"): "layout_value",
    ("raw_disk", "partition_sector_count_sequence"): "layout_value",
    ("raw_disk", "partition_sector_count_list"): "layout_value",
    ("raw_disk", "partition_sector_counts"): "layout_value",
    ("raw_disk", "partition_size_bytes_sequence"): "layout_value",
    ("raw_disk", "partition_size_bytes_list"): "layout_value",
    ("raw_disk", "partition_sizes_bytes"): "layout_value",
    ("raw_disk", "partition_start_offset_bytes_sequence"): "layout_value",
    ("raw_disk", "partition_start_offset_bytes_list"): "layout_value",
    ("raw_disk", "partition_start_offsets_bytes"): "layout_value",
    ("raw_disk", "partition_name_sequence"): "layout_value",
    ("raw_disk", "partition_name_list"): "layout_value",
    ("raw_disk", "partition_names"): "layout_value",
    ("raw_disk", "partition_type_guid_sequence"): "layout_value",
    ("raw_disk", "partition_type_guid_list"): "layout_value",
    ("raw_disk", "partition_type_guids"): "layout_value",
    ("raw_disk", "partition_unique_guid_sequence"): "layout_value",
    ("raw_disk", "partition_unique_guid_list"): "layout_value",
    ("raw_disk", "partition_unique_guids"): "layout_value",
    ("raw_disk", "partition_type_sequence"): "layout_value",
    ("raw_disk", "partition_type_list"): "layout_value",
    ("raw_disk", "partition_types"): "layout_value",
    ("raw_disk", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("raw_disk", "partition_attributes_u64_hex_list"): "layout_value",
    ("raw_disk", "partition_count"): "layout_value",
    ("raw_disk", "partition_table_type"): "layout_value",
    ("raw_disk", "disk_guid"): "layout_value",
    ("raw_disk", "disk_signature_u32_hex"): "layout_value",
    ("raw_disk", "sector_size_bytes"): "layout_value",
    ("raw_disk", "first_usable_lba"): "layout_value",
    ("raw_disk", "last_usable_lba"): "layout_value",
    ("raw_disk", "alternate_lba"): "layout_value",
    ("raw_disk", "backup_lba"): "layout_value",
    ("raw_disk", "backup_header_lba"): "layout_value",
    ("raw_disk", "partition_entry_lba"): "layout_value",
    ("raw_disk", "partition_entry_count"): "layout_value",
    ("raw_disk", "partition_entry_size_bytes"): "layout_value",
    ("raw_disk", "image_size_bytes"): "layout_value",
    ("raw_disk", "image_sector_count"): "layout_value",
    ("raw_disk", "largest_partition_index"): "layout_value",
    ("raw_disk", "largest_partition_name"): "layout_value",
    ("disk_image", "partition_start_lba_sequence"): "layout_value",
    ("disk_image", "partition_start_lba_list"): "layout_value",
    ("disk_image", "partition_start_lbas"): "layout_value",
    ("disk_image", "partition_end_lba_sequence"): "layout_value",
    ("disk_image", "partition_end_lba_list"): "layout_value",
    ("disk_image", "partition_end_lbas"): "layout_value",
    ("disk_image", "partition_last_lba_sequence"): "layout_value",
    ("disk_image", "partition_last_lba_list"): "layout_value",
    ("disk_image", "partition_last_lbas"): "layout_value",
    ("disk_image", "partition_sector_count_sequence"): "layout_value",
    ("disk_image", "partition_sector_count_list"): "layout_value",
    ("disk_image", "partition_sector_counts"): "layout_value",
    ("disk_image", "partition_size_bytes_sequence"): "layout_value",
    ("disk_image", "partition_size_bytes_list"): "layout_value",
    ("disk_image", "partition_sizes_bytes"): "layout_value",
    ("disk_image", "partition_start_offset_bytes_sequence"): "layout_value",
    ("disk_image", "partition_start_offset_bytes_list"): "layout_value",
    ("disk_image", "partition_start_offsets_bytes"): "layout_value",
    ("disk_image", "partition_name_sequence"): "layout_value",
    ("disk_image", "partition_name_list"): "layout_value",
    ("disk_image", "partition_names"): "layout_value",
    ("disk_image", "partition_type_guid_sequence"): "layout_value",
    ("disk_image", "partition_type_guid_list"): "layout_value",
    ("disk_image", "partition_type_guids"): "layout_value",
    ("disk_image", "partition_unique_guid_sequence"): "layout_value",
    ("disk_image", "partition_unique_guid_list"): "layout_value",
    ("disk_image", "partition_unique_guids"): "layout_value",
    ("disk_image", "partition_type_sequence"): "layout_value",
    ("disk_image", "partition_type_list"): "layout_value",
    ("disk_image", "partition_types"): "layout_value",
    ("disk_image", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("disk_image", "partition_attributes_u64_hex_list"): "layout_value",
    ("disk_image", "partition_count"): "layout_value",
    ("disk_image", "partition_table_type"): "layout_value",
    ("disk_image", "disk_guid"): "layout_value",
    ("disk_image", "disk_signature_u32_hex"): "layout_value",
    ("disk_image", "sector_size_bytes"): "layout_value",
    ("disk_image", "first_usable_lba"): "layout_value",
    ("disk_image", "last_usable_lba"): "layout_value",
    ("disk_image", "alternate_lba"): "layout_value",
    ("disk_image", "backup_lba"): "layout_value",
    ("disk_image", "backup_header_lba"): "layout_value",
    ("disk_image", "partition_entry_lba"): "layout_value",
    ("disk_image", "partition_entry_count"): "layout_value",
    ("disk_image", "partition_entry_size_bytes"): "layout_value",
    ("disk_image", "image_size_bytes"): "layout_value",
    ("disk_image", "image_sector_count"): "layout_value",
    ("disk_image", "largest_partition_index"): "layout_value",
    ("disk_image", "largest_partition_name"): "layout_value",
    ("dd", "partition_start_lba_sequence"): "layout_value",
    ("dd", "partition_start_lba_list"): "layout_value",
    ("dd", "partition_start_lbas"): "layout_value",
    ("dd", "partition_end_lba_sequence"): "layout_value",
    ("dd", "partition_end_lba_list"): "layout_value",
    ("dd", "partition_end_lbas"): "layout_value",
    ("dd", "partition_last_lba_sequence"): "layout_value",
    ("dd", "partition_last_lba_list"): "layout_value",
    ("dd", "partition_last_lbas"): "layout_value",
    ("dd", "partition_sector_count_sequence"): "layout_value",
    ("dd", "partition_sector_count_list"): "layout_value",
    ("dd", "partition_sector_counts"): "layout_value",
    ("dd", "partition_size_bytes_sequence"): "layout_value",
    ("dd", "partition_size_bytes_list"): "layout_value",
    ("dd", "partition_sizes_bytes"): "layout_value",
    ("dd", "partition_start_offset_bytes_sequence"): "layout_value",
    ("dd", "partition_start_offset_bytes_list"): "layout_value",
    ("dd", "partition_start_offsets_bytes"): "layout_value",
    ("dd", "partition_name_sequence"): "layout_value",
    ("dd", "partition_name_list"): "layout_value",
    ("dd", "partition_names"): "layout_value",
    ("dd", "partition_type_guid_sequence"): "layout_value",
    ("dd", "partition_type_guid_list"): "layout_value",
    ("dd", "partition_type_guids"): "layout_value",
    ("dd", "partition_unique_guid_sequence"): "layout_value",
    ("dd", "partition_unique_guid_list"): "layout_value",
    ("dd", "partition_unique_guids"): "layout_value",
    ("dd", "partition_type_sequence"): "layout_value",
    ("dd", "partition_type_list"): "layout_value",
    ("dd", "partition_types"): "layout_value",
    ("dd", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("dd", "partition_attributes_u64_hex_list"): "layout_value",
    ("dd", "partition_count"): "layout_value",
    ("dd", "partition_table_type"): "layout_value",
    ("dd", "disk_guid"): "layout_value",
    ("dd", "disk_signature_u32_hex"): "layout_value",
    ("dd", "sector_size_bytes"): "layout_value",
    ("dd", "first_usable_lba"): "layout_value",
    ("dd", "last_usable_lba"): "layout_value",
    ("dd", "alternate_lba"): "layout_value",
    ("dd", "backup_lba"): "layout_value",
    ("dd", "backup_header_lba"): "layout_value",
    ("dd", "partition_entry_lba"): "layout_value",
    ("dd", "partition_entry_count"): "layout_value",
    ("dd", "partition_entry_size_bytes"): "layout_value",
    ("dd", "image_size_bytes"): "layout_value",
    ("dd", "image_sector_count"): "layout_value",
    ("dd", "largest_partition_index"): "layout_value",
    ("dd", "largest_partition_name"): "layout_value",
    ("gpt", "partition_start_lba_sequence"): "layout_value",
    ("gpt", "partition_start_lba_list"): "layout_value",
    ("gpt", "partition_start_lbas"): "layout_value",
    ("gpt", "partition_end_lba_sequence"): "layout_value",
    ("gpt", "partition_end_lba_list"): "layout_value",
    ("gpt", "partition_end_lbas"): "layout_value",
    ("gpt", "partition_last_lba_sequence"): "layout_value",
    ("gpt", "partition_last_lba_list"): "layout_value",
    ("gpt", "partition_sector_count_sequence"): "layout_value",
    ("gpt", "partition_sector_count_list"): "layout_value",
    ("gpt", "partition_sector_counts"): "layout_value",
    ("gpt", "partition_size_bytes_sequence"): "layout_value",
    ("gpt", "partition_size_bytes_list"): "layout_value",
    ("gpt", "partition_sizes_bytes"): "layout_value",
    ("gpt", "partition_start_offset_bytes_sequence"): "layout_value",
    ("gpt", "partition_start_offset_bytes_list"): "layout_value",
    ("gpt", "partition_start_offsets_bytes"): "layout_value",
    ("gpt", "partition_name_sequence"): "layout_value",
    ("gpt", "partition_name_list"): "layout_value",
    ("gpt", "partition_type_guid_sequence"): "layout_value",
    ("gpt", "partition_type_guid_list"): "layout_value",
    ("gpt", "partition_unique_guid_sequence"): "layout_value",
    ("gpt", "partition_unique_guid_list"): "layout_value",
    ("gpt", "partition_type_sequence"): "layout_value",
    ("gpt", "partition_type_list"): "layout_value",
    ("gpt", "partition_types"): "layout_value",
    ("gpt", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("gpt", "partition_attributes_u64_hex_list"): "layout_value",
    ("gpt", "partition_table_type"): "layout_value",
    ("gpt", "disk_signature_u32_hex"): "layout_value",
    ("gpt", "sector_size_bytes"): "layout_value",
    ("gpt", "backup_header_lba"): "layout_value",
    ("gpt", "partition_entry_size_bytes"): "layout_value",
    ("gpt", "image_size_bytes"): "layout_value",
    ("gpt", "image_sector_count"): "layout_value",
    ("gpt", "largest_partition_index"): "layout_value",
    ("gpt", "largest_partition_name"): "layout_value",
    ("mbr", "partition_start_lba_sequence"): "layout_value",
    ("mbr", "partition_start_lba_list"): "layout_value",
    ("mbr", "partition_end_lba_sequence"): "layout_value",
    ("mbr", "partition_end_lba_list"): "layout_value",
    ("mbr", "partition_end_lbas"): "layout_value",
    ("mbr", "partition_last_lba_sequence"): "layout_value",
    ("mbr", "partition_last_lba_list"): "layout_value",
    ("mbr", "partition_last_lbas"): "layout_value",
    ("mbr", "partition_sector_count_sequence"): "layout_value",
    ("mbr", "partition_sector_count_list"): "layout_value",
    ("mbr", "partition_size_bytes_sequence"): "layout_value",
    ("mbr", "partition_size_bytes_list"): "layout_value",
    ("mbr", "partition_sizes_bytes"): "layout_value",
    ("mbr", "partition_start_offset_bytes_sequence"): "layout_value",
    ("mbr", "partition_start_offset_bytes_list"): "layout_value",
    ("mbr", "partition_start_offsets_bytes"): "layout_value",
    ("mbr", "partition_name_sequence"): "layout_value",
    ("mbr", "partition_name_list"): "layout_value",
    ("mbr", "partition_names"): "layout_value",
    ("mbr", "partition_type_guid_sequence"): "layout_value",
    ("mbr", "partition_type_guid_list"): "layout_value",
    ("mbr", "partition_type_guids"): "layout_value",
    ("mbr", "partition_unique_guid_sequence"): "layout_value",
    ("mbr", "partition_unique_guid_list"): "layout_value",
    ("mbr", "partition_unique_guids"): "layout_value",
    ("mbr", "partition_type_sequence"): "layout_value",
    ("mbr", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("mbr", "partition_attributes_u64_hex_list"): "layout_value",
    ("mbr", "disk_guid"): "layout_value",
    ("mbr", "sector_size_bytes"): "layout_value",
    ("mbr", "first_usable_lba"): "layout_value",
    ("mbr", "last_usable_lba"): "layout_value",
    ("mbr", "alternate_lba"): "layout_value",
    ("mbr", "backup_lba"): "layout_value",
    ("mbr", "backup_header_lba"): "layout_value",
    ("mbr", "partition_entry_lba"): "layout_value",
    ("mbr", "partition_entry_count"): "layout_value",
    ("mbr", "partition_entry_size_bytes"): "layout_value",
    ("mbr", "image_size_bytes"): "layout_value",
    ("mbr", "image_sector_count"): "layout_value",
    ("mbr", "largest_partition_index"): "layout_value",
    ("mbr", "largest_partition_name"): "layout_value",
    ("partition_table", "partition_start_lba_sequence"): "layout_value",
    ("partition_table", "partition_start_lba_list"): "layout_value",
    ("partition_table", "partition_end_lba_sequence"): "layout_value",
    ("partition_table", "partition_end_lba_list"): "layout_value",
    ("partition_table", "partition_end_lbas"): "layout_value",
    ("partition_table", "partition_last_lba_sequence"): "layout_value",
    ("partition_table", "partition_last_lba_list"): "layout_value",
    ("partition_table", "partition_last_lbas"): "layout_value",
    ("partition_table", "partition_sector_count_sequence"): "layout_value",
    ("partition_table", "partition_sector_count_list"): "layout_value",
    ("partition_table", "partition_size_bytes_sequence"): "layout_value",
    ("partition_table", "partition_size_bytes_list"): "layout_value",
    ("partition_table", "partition_sizes_bytes"): "layout_value",
    ("partition_table", "partition_start_offset_bytes_sequence"): "layout_value",
    ("partition_table", "partition_start_offset_bytes_list"): "layout_value",
    ("partition_table", "partition_start_offsets_bytes"): "layout_value",
    ("partition_table", "partition_name_sequence"): "layout_value",
    ("partition_table", "partition_name_list"): "layout_value",
    ("partition_table", "partition_names"): "layout_value",
    ("partition_table", "partition_type_guid_sequence"): "layout_value",
    ("partition_table", "partition_type_guid_list"): "layout_value",
    ("partition_table", "partition_type_guids"): "layout_value",
    ("partition_table", "partition_unique_guid_sequence"): "layout_value",
    ("partition_table", "partition_unique_guid_list"): "layout_value",
    ("partition_table", "partition_unique_guids"): "layout_value",
    ("partition_table", "partition_type_sequence"): "layout_value",
    ("partition_table", "partition_attributes_u64_hex_sequence"): "layout_value",
    ("partition_table", "partition_attributes_u64_hex_list"): "layout_value",
    ("partition_table", "disk_guid"): "layout_value",
    ("partition_table", "sector_size_bytes"): "layout_value",
    ("partition_table", "first_usable_lba"): "layout_value",
    ("partition_table", "last_usable_lba"): "layout_value",
    ("partition_table", "alternate_lba"): "layout_value",
    ("partition_table", "backup_lba"): "layout_value",
    ("partition_table", "backup_header_lba"): "layout_value",
    ("partition_table", "partition_entry_lba"): "layout_value",
    ("partition_table", "partition_entry_count"): "layout_value",
    ("partition_table", "partition_entry_size_bytes"): "layout_value",
    ("partition_table", "image_size_bytes"): "layout_value",
    ("partition_table", "image_sector_count"): "layout_value",
    ("partition_table", "largest_partition_index"): "layout_value",
    ("partition_table", "largest_partition_name"): "layout_value",
}


_EXT = (0x05, 0x0F, 0x85)
_CAP = 512 << 20   # unwrapped/virtual image cap (bytes): a gzip bomb or a huge sparse disk keeps only its prefix


def _u(fmt, b, off):
    """struct.unpack over b[off:...] (works on bytes and on the _Virt lazy image)."""
    return struct.unpack(fmt, b[off:off + struct.calcsize(fmt)])


class _Virt:
    """Lazy virtual disk: `read(cluster_index) -> bytes|None` per cluster (None = unallocated -> zeros). Supports
    len(), int indexing and step-1 slicing, so the partition walk reads a qcow2 / sparse VMDK / dynamic VHD in place."""

    def __init__(self, size, csize, read):
        self.size, self.cs, self._read, self._cache = size, csize, read, {}

    def __len__(self):
        return self.size

    def _cl(self, i):
        c = self._cache.get(i)
        if c is None:
            try:
                c = self._read(i)
            except Exception:  # noqa: BLE001 -- a damaged map entry reads as zeros
                c = None
            c = (bytes(c or b"")[:self.cs]).ljust(self.cs, b"\0")
            if len(self._cache) > 256:
                self._cache.clear()
            self._cache[i] = c
        return c

    def __getitem__(self, k):
        if isinstance(k, int):
            if k < 0:
                k += self.size
            if not 0 <= k < self.size:
                raise IndexError(k)
            return self._cl(k // self.cs)[k % self.cs]
        a, z, _ = k.indices(self.size)
        out = bytearray()
        while a < z:
            ci, co = divmod(a, self.cs)
            n = min(self.cs - co, z - a)
            out += self._cl(ci)[co:co + n]
            a += n
        return bytes(out)


def _inflate(blob, wbits):
    d = zlib.decompressobj(wbits)
    try:
        return d.decompress(blob, _CAP)
    except zlib.error:
        return None


def _qcow2(b):
    """qcow2 v2/v3 -> _Virt (L1 -> L2 -> cluster; compressed clusters = raw deflate; bit0 = zero cluster)."""
    _v, _bo, _bs, cbits, size, crypt, l1n, l1o = struct.unpack_from(">IQIIQIIQ", b, 4)
    if crypt or not 9 <= cbits <= 21:
        return None
    cs, l2n = 1 << cbits, (1 << cbits) // 8
    ext_l2 = len(b) >= 80 and _v >= 3 and struct.unpack_from(">Q", b, 72)[0] & 0x10
    if ext_l2:
        return None
    x = 62 - (cbits - 8)

    def read(ci):
        l1i, l2i = divmod(ci, l2n)
        if l1i >= l1n:
            return None
        l2o = struct.unpack_from(">Q", b, l1o + 8 * l1i)[0] & 0x00FFFFFFFFFFFE00
        if not l2o:
            return None
        e = struct.unpack_from(">Q", b, l2o + 8 * l2i)[0]
        if e & (1 << 62):
            off = e & ((1 << x) - 1)
            nsec = ((e >> x) & ((1 << (cbits - 8)) - 1)) + 1
            return _inflate(b[off:off + nsec * 512 + 512], -15)
        if e & 1:
            return None
        o = e & 0x00FFFFFFFFFFFE00
        return b[o:o + cs] if o else None
    return _Virt(min(size, 1 << 40), cs, read)


def _vmdk(b):
    """Hosted sparse VMDK (`KDMV`: monolithicSparse or streamOptimized) -> _Virt via grain directory/tables."""
    _ver, flags, cap, gsz, _do, _ds, ngte, _rgd, gd = struct.unpack_from("<IIQQQQIQQ", b, 4)
    if gd == 0xFFFFFFFFFFFFFFFF and len(b) >= 1536 and b[-1024:-1020] == b"KDMV":   # streamOptimized: footer copy
        gd = struct.unpack_from("<Q", b, len(b) - 1024 + 56)[0]
    if not gsz or not ngte or gsz > 1 << 16:
        return None
    gs, comp = gsz * 512, bool(flags & 0x10000)

    def read(ci):
        gdi, gti = divmod(ci, ngte)
        gto = struct.unpack_from("<I", b, gd * 512 + 4 * gdi)[0]
        if not gto:
            return None
        ge = struct.unpack_from("<I", b, gto * 512 + 4 * gti)[0]
        if ge <= 1:
            return None
        o = ge * 512
        if comp:
            n = struct.unpack_from("<I", b, o + 8)[0]
            return _inflate(b[o + 12:o + 12 + n], 15)
        return b[o:o + gs]
    return _Virt(min(cap * 512, 1 << 40), gs, read)


def _vhd_dynamic(b):
    """Dynamic/differencing VHD (`conectix` footer copy at 0 -> `cxsparse` header -> BAT) -> _Virt."""
    doff = struct.unpack_from(">Q", b, 16)[0]
    size = struct.unpack_from(">Q", b, 48)[0]
    if b[doff:doff + 8] != b"cxsparse":
        return None
    bat = _u(">Q", b, doff + 16)[0]
    nent, bsz = _u(">II", b, doff + 28)
    if not bsz or bsz % 512:
        return None
    bmp = -(-(bsz // 512 // 8) // 512) * 512

    def read(ci):
        if ci >= nent:
            return None
        s = struct.unpack_from(">I", b, bat + 4 * ci)[0]
        if s == 0xFFFFFFFF:
            return None
        o = s * 512 + bmp
        return b[o:o + bsz]
    return _Virt(min(size, 1 << 40), bsz, read)


def _unwrap(b, depth=0):
    """The raw sector image inside a container: gzip / xz / bzip2 (decompressed, capped at _CAP), fixed VHD (footer
    stripped so the LAST LBA -- the backup GPT -- is right), dynamic VHD, sparse/streamOptimized VMDK, qcow2.
    Anything else is returned unchanged (a raw .img/.dd, or a VMDK flat extent)."""
    if depth > 3 or not b or len(b) < 4:
        return b
    try:
        h = bytes(b[:8])
        if h[:2] == b"\x1f\x8b":
            d = zlib.decompressobj(31)
            return _unwrap(d.decompress(bytes(b), _CAP), depth + 1)
        if h[:6] == b"\xfd7zXZ\x00":
            return _unwrap(lzma.LZMADecompressor().decompress(bytes(b), _CAP), depth + 1)
        if h[:3] == b"BZh":
            return _unwrap(bz2.BZ2Decompressor().decompress(bytes(b), _CAP), depth + 1)
        if h[:4] == b"QFI\xfb":
            return _qcow2(b) or b
        if h[:4] == b"KDMV":
            return _vmdk(b) or b
        if h == b"conectix":
            return _vhd_dynamic(b) or b
        if len(b) >= 1024 and len(b) % 512 == 0 and b[-512:-504] == b"conectix" \
                and struct.unpack_from(">I", b, len(b) - 512 + 60)[0] == 2:      # fixed VHD: raw + 512 B footer
            return b[:-512]
    except Exception:  # noqa: BLE001
        return b
    return b


def _guid(raw):
    return str(uuid.UUID(bytes_le=bytes(raw)))


def _hdr_ok(b, at, ss, lba):
    """GPT header at byte `at`: signature, MyLBA == lba, header CRC32 (and the entry-array CRC when it is readable)."""
    if b[at:at + 8] != b"EFI PART":
        return False
    hsz, crc = _u("<II", b, at + 12)
    if not 92 <= hsz <= ss:
        return False
    h = bytearray(b[at:at + hsz])
    h[16:20] = b"\0\0\0\0"
    if zlib.crc32(h) != crc or _u("<Q", b, at + 24)[0] != lba:
        return False
    ent_lba, n, esz, ecrc = _u("<QIII", b, at + 72)
    end = ent_lba * ss + n * esz
    if end <= len(b) and n * esz <= 1 << 20:
        return zlib.crc32(b[ent_lba * ss:end]) == ecrc
    return True


def _gpt_at(b, ss, at):
    cur, alt, first, last = _u("<QQQQ", b, at + 24)
    ent_lba, n, esz = _u("<QII", b, at + 72)
    if esz < 128:
        return None
    parts, base = [], ent_lba * ss
    for i in range(min(n, 4096)):
        off = base + i * esz
        if off + 128 > len(b):
            break
        e = b[off:off + 128]
        if e[:16] == b"\0" * 16:
            continue
        s, l, attrs = struct.unpack_from("<QQQ", e, 32)
        name = e[56:128].decode("utf-16-le", "replace").split("\0", 1)[0]
        parts.append({"slot": i, "start": s, "end": l, "count": l - s + 1, "type_guid": _guid(e[:16]),
                      "unique_guid": _guid(e[16:32]), "name": name, "attrs": attrs, "type": _guid(e[:16])})
    return {"label": "gpt", "ss": ss, "parts": parts, "disk_guid": _guid(b[at + 56:at + 72]),
            "first_usable": first, "last_usable": last, "alternate": alt, "current": cur,
            "entry_lba": ent_lba, "entry_count": n, "entry_size": esz,
            "sig": _u("<I", b, 440)[0] if b[510:512] == b"\x55\xaa" else None}


def _gpt(b):
    """GPT layout dict, or None. Per sector size (512, 4096, 1024, 2048): a CRC-valid primary at LBA1 wins; a damaged
    one (bad CRC / zeroed LBA1) falls back to a CRC-valid BACKUP header (primary's AlternateLBA, else the image's last
    LBA -- its entry array sits before it); with no valid copy, a primary that still says `EFI PART` is used as is."""
    n = len(b)
    for ss in (512, 4096, 1024, 2048):
        if n < 2 * ss:
            continue
        prim = b[ss:ss + 8] == b"EFI PART" and n >= ss + 92
        if prim and _hdr_ok(b, ss, ss, 1):
            return _gpt_at(b, ss, ss)
        cands = []
        if prim:
            alt = _u("<Q", b, ss + 32)[0]
            if 1 < alt and (alt + 1) * ss <= n:
                cands.append(alt)
        cands.append(n // ss - 1)
        for lba in cands:
            if lba > 1 and _hdr_ok(b, lba * ss, ss, lba):
                return _gpt_at(b, ss, lba * ss)
        if prim:
            return _gpt_at(b, ss, ss)
    return None


def _mbr(b):
    """MBR layout (primaries in slot order, the extended container itself, then its EBR-chain logicals), or None."""
    if len(b) < 512 or b[510:512] != b"\x55\xaa":
        return None
    parts = []
    for i in range(4):
        e = 446 + 16 * i
        typ, (start, cnt) = b[e + 4], _u("<II", b, e + 8)
        if typ == 0:
            continue
        parts.append({"slot": i, "start": start, "end": start + cnt - 1, "count": cnt, "type": "0x%02x" % typ,
                      "boot": b[e] == 0x80, "ext": typ in _EXT})
        if typ in _EXT:
            ext, cur, seen, nlog = start, start, set(), 4
            while cur not in seen and cur * 512 + 512 <= len(b) and len(seen) < 4096:
                seen.add(cur)
                o = cur * 512
                if b[o + 510:o + 512] != b"\x55\xaa":
                    break
                t1, (s1, c1) = b[o + 450], _u("<II", b, o + 454)
                if t1:
                    parts.append({"slot": nlog, "start": cur + s1, "end": cur + s1 + c1 - 1, "count": c1,
                                  "type": "0x%02x" % t1, "boot": b[o + 446] == 0x80, "ext": False})
                    nlog += 1
                t2, s2 = b[o + 466], _u("<I", b, o + 470)[0]
                if not t2:
                    break
                cur = ext + s2
    if not parts:
        return None
    return {"label": "dos", "ss": 512, "parts": parts, "sig": _u("<I", b, 440)[0]}


def layout(b):
    """Unwrap the container, then GPT (primary, else backup) if any copy is found, else MBR+EBR; None if neither
    (a protective 0xEE MBR whose GPT copies are both gone is None, not the bogus [1] of the 0xEE entry)."""
    b = _unwrap(b)
    if not b or len(b) < 512:
        return None
    g = _gpt(b)
    if g is not None:
        g["size"] = len(b)
        return g
    m = _mbr(b)
    if m is not None and any(p["type"] == "0xee" for p in m["parts"]):
        return None
    if m is not None:
        m["size"] = len(b)
    return m


_SEQ = {"start_lba": "start", "first_lba": "start", "starting_lba": "start", "end_lba": "end", "last_lba": "end",
        "ending_lba": "end", "sector_count": "count", "size_sectors": "count", "length_sectors": "count",
        "size_bytes": "size", "length_bytes": "size", "start_offset_bytes": "off", "start_offset": "off",
        "offset_bytes": "off", "byte_offset": "off", "name": "name", "label": "name", "type_guid": "type_guid",
        "unique_guid": "unique_guid", "partition_guid": "unique_guid", "guid": "unique_guid", "type": "type",
        "type_code": "type", "attributes_u64_hex": "attrs", "attribute_flags_u64_hex": "attrs"}
_PLURAL = {"start_lbas": "start_lba", "first_lbas": "first_lba", "end_lbas": "end_lba", "last_lbas": "last_lba",
           "sector_counts": "sector_count", "sizes_bytes": "size_bytes", "start_offsets_bytes": "start_offset_bytes",
           "names": "name", "labels": "label", "type_guids": "type_guid", "unique_guids": "unique_guid",
           "guids": "guid", "types": "type", "attributes_u64_hex": "attributes_u64_hex"}


def _seq_key(field):
    """partition_<x>_sequence | partition_<x>_list | partition_<x>s -> the _SEQ key, else None."""
    if not field.startswith("partition_"):
        return None
    f = field[len("partition_"):]
    for suf in ("_sequence", "_list", "_array"):
        if f.endswith(suf):
            f = f[:-len(suf)]
            return f if f in _SEQ else None
    if f in _PLURAL:
        return _PLURAL[f]
    return None


def _seq(L, key):
    ss, out = L["ss"], []
    for p in L["parts"]:
        if key == "size":
            v = p["count"] * ss
        elif key == "off":
            v = p["start"] * ss
        elif key == "attrs":
            if "attrs" not in p:
                return "none"
            v = "0x%016x" % p["attrs"]
        else:
            v = p.get(key)
            if v is None:
                return "none"   # GPT-only (names/GUIDs) on an MBR disk
        out.append(v)
    return out


_GPT_SCALAR = {"disk_guid": "disk_guid", "first_usable_lba": "first_usable", "last_usable_lba": "last_usable",
               "alternate_lba": "alternate", "backup_lba": "alternate", "backup_header_lba": "alternate",
               "current_lba": "current", "my_lba": "current", "partition_entry_lba": "entry_lba",
               "partition_entries_lba": "entry_lba", "partition_entry_count": "entry_count",
               "number_of_partition_entries": "entry_count", "num_partition_entries": "entry_count",
               "partition_entry_size_bytes": "entry_size", "partition_entry_size": "entry_size",
               "size_of_partition_entry": "entry_size"}


def layout_value(data, ctx):
    """disk.<partition-layout field> of a RAW image (MBR/EBR or GPT). Sequences in TABLE order (never sorted)."""
    if data is None:
        return None
    field = (ctx or {}).get("field") or ""
    try:
        L = layout(data)
        if L is None:
            return "none"
        ss, parts = L["ss"], L["parts"]
        k = _seq_key(field)
        if k is not None:
            return _seq(L, _SEQ[k])
        if field in ("partition_count", "number_of_partitions", "num_partitions"):
            return len(parts)
        if field in ("partition_table_type", "label_type", "partition_scheme", "partition_table_label"):
            return L["label"]
        if field in ("sector_size_bytes", "sector_size", "logical_sector_size_bytes"):
            return ss
        if field == "image_size_bytes":
            return L["size"]
        if field == "image_sector_count":
            return L["size"] // ss
        if field in ("disk_signature_u32_hex", "disk_identifier_u32_hex", "disk_id_u32_hex"):
            return "none" if L.get("sig") is None else Hex(L["sig"], 8)
        if field in _GPT_SCALAR:
            v = L.get(_GPT_SCALAR[field])
            return "none" if v is None else v
        if field in ("largest_partition_index", "largest_partition_name"):
            cand = [p for p in parts if not p.get("ext")]
            if not cand:
                return "none"
            big = max(cand, key=lambda p: p["count"])   # first in table order wins a tie
            if field == "largest_partition_index":
                return big["slot"]
            return big.get("name", "none")
    except Exception:  # noqa: BLE001 -- never raise past the extractor
        return None
    return None
