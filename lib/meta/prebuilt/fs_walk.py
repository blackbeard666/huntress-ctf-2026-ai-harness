"""Filesystem DIRECTORY WALK inside a volume or a partitioned raw image (prebuilt, SPECULATIVE -- never GM-asked yet):
the layer under vbr.py (boot sector) and disk_layout.py (partition table): file names, sizes, first cluster/block,
image-absolute byte offset, timestamps.

Input: a bare volume (FAT/exFAT/NTFS VBR at 0, or an ext superblock at +1024) or a raw disk image (MBR / GPT; entries in
TABLE order, numbered 1..). Default = the FIRST partition that carries a recognised filesystem; `partition_N_<field>` /
`pN_<field>` (disk / filesystem fmts) pick partition N (1-based table order). Per-file fields take the file from
`<field>_for_<name>` (name compared lowercase with non-alnum -> `_`, full name or stem), else the longest file name
quoted in the question text, else the volume's only regular file.
FAT12/16/32: root = fixed region after the FATs (FAT32: cluster chain from BPB @0x2C); 32-B dirents, LFN (attr 0x0F)
reassembled (UTF-16LE @1/@14/@28), short-name case bits @0x0C (bit3 base, bit4 ext lower -- as mtools/Windows store
`a.txt`), 0xE5 = deleted (first char lost; LFN kept when present), 0x08 volume label skipped, `.`/`..` skipped, subdirs
walked (depth <= 16, loop-guarded). start cluster = hi u16 @0x14 << 16 | lo u16 @0x1A; size u32 @0x1C.
offset_bytes = partition_offset + data_region*bps + (cluster-2)*cluster_size (image-absolute; empty file -> "none").
Times: DOS LOCAL time as stored (no TZ applied) -> `YYYY-MM-DD HH:MM:SS`; created = @0x10/@0x0E + tenths @0x0D (10 ms
units, MS spec) floored to the second; modified = @0x18/@0x16.
exFAT: 0x85 File (attrs @4, create ts @8, modify ts @12: date<<16|time DOS packed, local as stored) + 0xC0 Stream (name
len @3, first cluster u32 @20, data length u64 @24, NoFatChain flag bit1 @1) + 0xC1 Name (15 UTF-16 chars @2); type
bit7 clear = deleted (0x05/0x40/0x41). ext2/3/4: superblock @+1024 (`53 ef` @0x38), block size 1024<<u32@0x18,
inodes/group @0x28, inode size u16 @0x58, 64-bit descs (incompat 0x80, size @0xFE); inode 2 = root; extents (0xF30A
header, depth-walked) or block map (12 direct + single/double indirect); dirents {inode u32, rec_len u16, name_len u8,
type u8}; inode 0 / csum tail skipped. start_block = first physical block; offset_bytes = part + block*bs; times =
mtime u32 @0x10 / crtime u32 @0x90 (unix, UTC). volume_name @0x78, uuid @0x68 (canonical lowercase), last_mounted @0x88.
NTFS: $MFT from the VBR (LCN @0x30, record size @0x40), FILE records with update-sequence fixups, in-use flag, $FILE_NAME
(0x30; Win32/POSIX name preferred over DOS 8.3) parent ref, $DATA (0x80, unnamed) resident (no cluster) / non-resident
first run LCN -> offset; times = $STANDARD_INFORMATION FILETIME -> UTC. System files (records < 16, `$`-named records < 64 such as the $Extend children) skipped.
Lists: file_names / root_file_names / deleted_file_names / directory_names = SORTED basenames (as fls lists them
alphabetically); file_paths = sorted `/`-joined paths. Wrong magic / truncated / not that filesystem -> "none"."""
import re
import struct
import uuid
from datetime import datetime, timedelta, timezone

from .vbr import _fs_kind, _gpt, _mbr_entries

FIELDS = {
    ("fat", "file_names"): "walk_value",
    ("fat", "file_paths"): "walk_value",
    ("fat", "file_count"): "walk_value",
    ("fat", "root_file_names"): "walk_value",
    ("fat", "root_entry_names"): "walk_value",
    ("fat", "directory_names"): "walk_value",
    ("fat", "directory_count"): "walk_value",
    ("fat", "deleted_file_names"): "walk_value",
    ("fat", "deleted_file_count"): "walk_value",
    ("fat", "file_names_sorted"): "walk_value",
    ("fat", "number_of_files"): "walk_value",
    ("fat", "start_cluster"): "walk_value",
    ("fat", "first_cluster"): "walk_value",
    ("fat", "file_start_cluster"): "walk_value",
    ("fat", "offset_bytes"): "walk_value",
    ("fat", "file_offset_bytes"): "walk_value",
    ("fat", "data_offset_bytes"): "walk_value",
    ("fat", "start_offset_bytes"): "walk_value",
    ("fat", "file_size_bytes"): "walk_value",
    ("fat", "file_size"): "walk_value",
    ("fat", "created"): "walk_value",
    ("fat", "created_time"): "walk_value",
    ("fat", "creation_time"): "walk_value",
    ("fat", "modified"): "walk_value",
    ("fat", "modified_time"): "walk_value",
    ("fat", "modification_time"): "walk_value",
    ("fat", "start_block"): "walk_value",
    ("fat", "first_block"): "walk_value",
    ("fat", "inode"): "walk_value",
    ("fat", "inode_number"): "walk_value",
    ("fat", "mft_record_number"): "walk_value",
    ("fat", "start_cluster_for_*"): "walk_value",
    ("fat", "first_cluster_for_*"): "walk_value",
    ("fat", "file_start_cluster_for_*"): "walk_value",
    ("fat", "offset_bytes_for_*"): "walk_value",
    ("fat", "file_offset_bytes_for_*"): "walk_value",
    ("fat", "data_offset_bytes_for_*"): "walk_value",
    ("fat", "start_offset_bytes_for_*"): "walk_value",
    ("fat", "file_size_bytes_for_*"): "walk_value",
    ("fat", "file_size_for_*"): "walk_value",
    ("fat", "created_for_*"): "walk_value",
    ("fat", "created_time_for_*"): "walk_value",
    ("fat", "creation_time_for_*"): "walk_value",
    ("fat", "modified_for_*"): "walk_value",
    ("fat", "modified_time_for_*"): "walk_value",
    ("fat", "modification_time_for_*"): "walk_value",
    ("fat", "start_block_for_*"): "walk_value",
    ("fat", "first_block_for_*"): "walk_value",
    ("fat", "inode_for_*"): "walk_value",
    ("fat", "inode_number_for_*"): "walk_value",
    ("fat", "mft_record_number_for_*"): "walk_value",
    ("fat12", "file_names"): "walk_value",
    ("fat12", "file_paths"): "walk_value",
    ("fat12", "file_count"): "walk_value",
    ("fat12", "root_file_names"): "walk_value",
    ("fat12", "root_entry_names"): "walk_value",
    ("fat12", "directory_names"): "walk_value",
    ("fat12", "directory_count"): "walk_value",
    ("fat12", "deleted_file_names"): "walk_value",
    ("fat12", "deleted_file_count"): "walk_value",
    ("fat12", "file_names_sorted"): "walk_value",
    ("fat12", "number_of_files"): "walk_value",
    ("fat12", "start_cluster"): "walk_value",
    ("fat12", "first_cluster"): "walk_value",
    ("fat12", "file_start_cluster"): "walk_value",
    ("fat12", "offset_bytes"): "walk_value",
    ("fat12", "file_offset_bytes"): "walk_value",
    ("fat12", "data_offset_bytes"): "walk_value",
    ("fat12", "start_offset_bytes"): "walk_value",
    ("fat12", "file_size_bytes"): "walk_value",
    ("fat12", "file_size"): "walk_value",
    ("fat12", "created"): "walk_value",
    ("fat12", "created_time"): "walk_value",
    ("fat12", "creation_time"): "walk_value",
    ("fat12", "modified"): "walk_value",
    ("fat12", "modified_time"): "walk_value",
    ("fat12", "modification_time"): "walk_value",
    ("fat12", "start_block"): "walk_value",
    ("fat12", "first_block"): "walk_value",
    ("fat12", "inode"): "walk_value",
    ("fat12", "inode_number"): "walk_value",
    ("fat12", "mft_record_number"): "walk_value",
    ("fat12", "start_cluster_for_*"): "walk_value",
    ("fat12", "first_cluster_for_*"): "walk_value",
    ("fat12", "file_start_cluster_for_*"): "walk_value",
    ("fat12", "offset_bytes_for_*"): "walk_value",
    ("fat12", "file_offset_bytes_for_*"): "walk_value",
    ("fat12", "data_offset_bytes_for_*"): "walk_value",
    ("fat12", "start_offset_bytes_for_*"): "walk_value",
    ("fat12", "file_size_bytes_for_*"): "walk_value",
    ("fat12", "file_size_for_*"): "walk_value",
    ("fat12", "created_for_*"): "walk_value",
    ("fat12", "created_time_for_*"): "walk_value",
    ("fat12", "creation_time_for_*"): "walk_value",
    ("fat12", "modified_for_*"): "walk_value",
    ("fat12", "modified_time_for_*"): "walk_value",
    ("fat12", "modification_time_for_*"): "walk_value",
    ("fat12", "start_block_for_*"): "walk_value",
    ("fat12", "first_block_for_*"): "walk_value",
    ("fat12", "inode_for_*"): "walk_value",
    ("fat12", "inode_number_for_*"): "walk_value",
    ("fat12", "mft_record_number_for_*"): "walk_value",
    ("fat16", "file_names"): "walk_value",
    ("fat16", "file_paths"): "walk_value",
    ("fat16", "file_count"): "walk_value",
    ("fat16", "root_file_names"): "walk_value",
    ("fat16", "root_entry_names"): "walk_value",
    ("fat16", "directory_names"): "walk_value",
    ("fat16", "directory_count"): "walk_value",
    ("fat16", "deleted_file_names"): "walk_value",
    ("fat16", "deleted_file_count"): "walk_value",
    ("fat16", "file_names_sorted"): "walk_value",
    ("fat16", "number_of_files"): "walk_value",
    ("fat16", "start_cluster"): "walk_value",
    ("fat16", "first_cluster"): "walk_value",
    ("fat16", "file_start_cluster"): "walk_value",
    ("fat16", "offset_bytes"): "walk_value",
    ("fat16", "file_offset_bytes"): "walk_value",
    ("fat16", "data_offset_bytes"): "walk_value",
    ("fat16", "start_offset_bytes"): "walk_value",
    ("fat16", "file_size_bytes"): "walk_value",
    ("fat16", "file_size"): "walk_value",
    ("fat16", "created"): "walk_value",
    ("fat16", "created_time"): "walk_value",
    ("fat16", "creation_time"): "walk_value",
    ("fat16", "modified"): "walk_value",
    ("fat16", "modified_time"): "walk_value",
    ("fat16", "modification_time"): "walk_value",
    ("fat16", "start_block"): "walk_value",
    ("fat16", "first_block"): "walk_value",
    ("fat16", "inode"): "walk_value",
    ("fat16", "inode_number"): "walk_value",
    ("fat16", "mft_record_number"): "walk_value",
    ("fat16", "start_cluster_for_*"): "walk_value",
    ("fat16", "first_cluster_for_*"): "walk_value",
    ("fat16", "file_start_cluster_for_*"): "walk_value",
    ("fat16", "offset_bytes_for_*"): "walk_value",
    ("fat16", "file_offset_bytes_for_*"): "walk_value",
    ("fat16", "data_offset_bytes_for_*"): "walk_value",
    ("fat16", "start_offset_bytes_for_*"): "walk_value",
    ("fat16", "file_size_bytes_for_*"): "walk_value",
    ("fat16", "file_size_for_*"): "walk_value",
    ("fat16", "created_for_*"): "walk_value",
    ("fat16", "created_time_for_*"): "walk_value",
    ("fat16", "creation_time_for_*"): "walk_value",
    ("fat16", "modified_for_*"): "walk_value",
    ("fat16", "modified_time_for_*"): "walk_value",
    ("fat16", "modification_time_for_*"): "walk_value",
    ("fat16", "start_block_for_*"): "walk_value",
    ("fat16", "first_block_for_*"): "walk_value",
    ("fat16", "inode_for_*"): "walk_value",
    ("fat16", "inode_number_for_*"): "walk_value",
    ("fat16", "mft_record_number_for_*"): "walk_value",
    ("fat32", "file_names"): "walk_value",
    ("fat32", "file_paths"): "walk_value",
    ("fat32", "file_count"): "walk_value",
    ("fat32", "root_file_names"): "walk_value",
    ("fat32", "root_entry_names"): "walk_value",
    ("fat32", "directory_names"): "walk_value",
    ("fat32", "directory_count"): "walk_value",
    ("fat32", "deleted_file_names"): "walk_value",
    ("fat32", "deleted_file_count"): "walk_value",
    ("fat32", "file_names_sorted"): "walk_value",
    ("fat32", "number_of_files"): "walk_value",
    ("fat32", "start_cluster"): "walk_value",
    ("fat32", "first_cluster"): "walk_value",
    ("fat32", "file_start_cluster"): "walk_value",
    ("fat32", "offset_bytes"): "walk_value",
    ("fat32", "file_offset_bytes"): "walk_value",
    ("fat32", "data_offset_bytes"): "walk_value",
    ("fat32", "start_offset_bytes"): "walk_value",
    ("fat32", "file_size_bytes"): "walk_value",
    ("fat32", "file_size"): "walk_value",
    ("fat32", "created"): "walk_value",
    ("fat32", "created_time"): "walk_value",
    ("fat32", "creation_time"): "walk_value",
    ("fat32", "modified"): "walk_value",
    ("fat32", "modified_time"): "walk_value",
    ("fat32", "modification_time"): "walk_value",
    ("fat32", "start_block"): "walk_value",
    ("fat32", "first_block"): "walk_value",
    ("fat32", "inode"): "walk_value",
    ("fat32", "inode_number"): "walk_value",
    ("fat32", "mft_record_number"): "walk_value",
    ("fat32", "start_cluster_for_*"): "walk_value",
    ("fat32", "first_cluster_for_*"): "walk_value",
    ("fat32", "file_start_cluster_for_*"): "walk_value",
    ("fat32", "offset_bytes_for_*"): "walk_value",
    ("fat32", "file_offset_bytes_for_*"): "walk_value",
    ("fat32", "data_offset_bytes_for_*"): "walk_value",
    ("fat32", "start_offset_bytes_for_*"): "walk_value",
    ("fat32", "file_size_bytes_for_*"): "walk_value",
    ("fat32", "file_size_for_*"): "walk_value",
    ("fat32", "created_for_*"): "walk_value",
    ("fat32", "created_time_for_*"): "walk_value",
    ("fat32", "creation_time_for_*"): "walk_value",
    ("fat32", "modified_for_*"): "walk_value",
    ("fat32", "modified_time_for_*"): "walk_value",
    ("fat32", "modification_time_for_*"): "walk_value",
    ("fat32", "start_block_for_*"): "walk_value",
    ("fat32", "first_block_for_*"): "walk_value",
    ("fat32", "inode_for_*"): "walk_value",
    ("fat32", "inode_number_for_*"): "walk_value",
    ("fat32", "mft_record_number_for_*"): "walk_value",
    ("vfat", "file_names"): "walk_value",
    ("vfat", "file_paths"): "walk_value",
    ("vfat", "file_count"): "walk_value",
    ("vfat", "root_file_names"): "walk_value",
    ("vfat", "root_entry_names"): "walk_value",
    ("vfat", "directory_names"): "walk_value",
    ("vfat", "directory_count"): "walk_value",
    ("vfat", "deleted_file_names"): "walk_value",
    ("vfat", "deleted_file_count"): "walk_value",
    ("vfat", "file_names_sorted"): "walk_value",
    ("vfat", "number_of_files"): "walk_value",
    ("vfat", "start_cluster"): "walk_value",
    ("vfat", "first_cluster"): "walk_value",
    ("vfat", "file_start_cluster"): "walk_value",
    ("vfat", "offset_bytes"): "walk_value",
    ("vfat", "file_offset_bytes"): "walk_value",
    ("vfat", "data_offset_bytes"): "walk_value",
    ("vfat", "start_offset_bytes"): "walk_value",
    ("vfat", "file_size_bytes"): "walk_value",
    ("vfat", "file_size"): "walk_value",
    ("vfat", "created"): "walk_value",
    ("vfat", "created_time"): "walk_value",
    ("vfat", "creation_time"): "walk_value",
    ("vfat", "modified"): "walk_value",
    ("vfat", "modified_time"): "walk_value",
    ("vfat", "modification_time"): "walk_value",
    ("vfat", "start_block"): "walk_value",
    ("vfat", "first_block"): "walk_value",
    ("vfat", "inode"): "walk_value",
    ("vfat", "inode_number"): "walk_value",
    ("vfat", "mft_record_number"): "walk_value",
    ("vfat", "start_cluster_for_*"): "walk_value",
    ("vfat", "first_cluster_for_*"): "walk_value",
    ("vfat", "file_start_cluster_for_*"): "walk_value",
    ("vfat", "offset_bytes_for_*"): "walk_value",
    ("vfat", "file_offset_bytes_for_*"): "walk_value",
    ("vfat", "data_offset_bytes_for_*"): "walk_value",
    ("vfat", "start_offset_bytes_for_*"): "walk_value",
    ("vfat", "file_size_bytes_for_*"): "walk_value",
    ("vfat", "file_size_for_*"): "walk_value",
    ("vfat", "created_for_*"): "walk_value",
    ("vfat", "created_time_for_*"): "walk_value",
    ("vfat", "creation_time_for_*"): "walk_value",
    ("vfat", "modified_for_*"): "walk_value",
    ("vfat", "modified_time_for_*"): "walk_value",
    ("vfat", "modification_time_for_*"): "walk_value",
    ("vfat", "start_block_for_*"): "walk_value",
    ("vfat", "first_block_for_*"): "walk_value",
    ("vfat", "inode_for_*"): "walk_value",
    ("vfat", "inode_number_for_*"): "walk_value",
    ("vfat", "mft_record_number_for_*"): "walk_value",
    ("exfat", "file_names"): "walk_value",
    ("exfat", "file_paths"): "walk_value",
    ("exfat", "file_count"): "walk_value",
    ("exfat", "root_file_names"): "walk_value",
    ("exfat", "root_entry_names"): "walk_value",
    ("exfat", "directory_names"): "walk_value",
    ("exfat", "directory_count"): "walk_value",
    ("exfat", "deleted_file_names"): "walk_value",
    ("exfat", "deleted_file_count"): "walk_value",
    ("exfat", "file_names_sorted"): "walk_value",
    ("exfat", "number_of_files"): "walk_value",
    ("exfat", "start_cluster"): "walk_value",
    ("exfat", "first_cluster"): "walk_value",
    ("exfat", "file_start_cluster"): "walk_value",
    ("exfat", "offset_bytes"): "walk_value",
    ("exfat", "file_offset_bytes"): "walk_value",
    ("exfat", "data_offset_bytes"): "walk_value",
    ("exfat", "start_offset_bytes"): "walk_value",
    ("exfat", "file_size_bytes"): "walk_value",
    ("exfat", "file_size"): "walk_value",
    ("exfat", "created"): "walk_value",
    ("exfat", "created_time"): "walk_value",
    ("exfat", "creation_time"): "walk_value",
    ("exfat", "modified"): "walk_value",
    ("exfat", "modified_time"): "walk_value",
    ("exfat", "modification_time"): "walk_value",
    ("exfat", "start_block"): "walk_value",
    ("exfat", "first_block"): "walk_value",
    ("exfat", "inode"): "walk_value",
    ("exfat", "inode_number"): "walk_value",
    ("exfat", "mft_record_number"): "walk_value",
    ("exfat", "start_cluster_for_*"): "walk_value",
    ("exfat", "first_cluster_for_*"): "walk_value",
    ("exfat", "file_start_cluster_for_*"): "walk_value",
    ("exfat", "offset_bytes_for_*"): "walk_value",
    ("exfat", "file_offset_bytes_for_*"): "walk_value",
    ("exfat", "data_offset_bytes_for_*"): "walk_value",
    ("exfat", "start_offset_bytes_for_*"): "walk_value",
    ("exfat", "file_size_bytes_for_*"): "walk_value",
    ("exfat", "file_size_for_*"): "walk_value",
    ("exfat", "created_for_*"): "walk_value",
    ("exfat", "created_time_for_*"): "walk_value",
    ("exfat", "creation_time_for_*"): "walk_value",
    ("exfat", "modified_for_*"): "walk_value",
    ("exfat", "modified_time_for_*"): "walk_value",
    ("exfat", "modification_time_for_*"): "walk_value",
    ("exfat", "start_block_for_*"): "walk_value",
    ("exfat", "first_block_for_*"): "walk_value",
    ("exfat", "inode_for_*"): "walk_value",
    ("exfat", "inode_number_for_*"): "walk_value",
    ("exfat", "mft_record_number_for_*"): "walk_value",
    ("ntfs", "file_names"): "walk_value",
    ("ntfs", "file_paths"): "walk_value",
    ("ntfs", "file_count"): "walk_value",
    ("ntfs", "root_file_names"): "walk_value",
    ("ntfs", "root_entry_names"): "walk_value",
    ("ntfs", "directory_names"): "walk_value",
    ("ntfs", "directory_count"): "walk_value",
    ("ntfs", "deleted_file_names"): "walk_value",
    ("ntfs", "deleted_file_count"): "walk_value",
    ("ntfs", "file_names_sorted"): "walk_value",
    ("ntfs", "number_of_files"): "walk_value",
    ("ntfs", "start_cluster"): "walk_value",
    ("ntfs", "first_cluster"): "walk_value",
    ("ntfs", "file_start_cluster"): "walk_value",
    ("ntfs", "offset_bytes"): "walk_value",
    ("ntfs", "file_offset_bytes"): "walk_value",
    ("ntfs", "data_offset_bytes"): "walk_value",
    ("ntfs", "start_offset_bytes"): "walk_value",
    ("ntfs", "file_size_bytes"): "walk_value",
    ("ntfs", "file_size"): "walk_value",
    ("ntfs", "created"): "walk_value",
    ("ntfs", "created_time"): "walk_value",
    ("ntfs", "creation_time"): "walk_value",
    ("ntfs", "modified"): "walk_value",
    ("ntfs", "modified_time"): "walk_value",
    ("ntfs", "modification_time"): "walk_value",
    ("ntfs", "start_block"): "walk_value",
    ("ntfs", "first_block"): "walk_value",
    ("ntfs", "inode"): "walk_value",
    ("ntfs", "inode_number"): "walk_value",
    ("ntfs", "mft_record_number"): "walk_value",
    ("ntfs", "start_cluster_for_*"): "walk_value",
    ("ntfs", "first_cluster_for_*"): "walk_value",
    ("ntfs", "file_start_cluster_for_*"): "walk_value",
    ("ntfs", "offset_bytes_for_*"): "walk_value",
    ("ntfs", "file_offset_bytes_for_*"): "walk_value",
    ("ntfs", "data_offset_bytes_for_*"): "walk_value",
    ("ntfs", "start_offset_bytes_for_*"): "walk_value",
    ("ntfs", "file_size_bytes_for_*"): "walk_value",
    ("ntfs", "file_size_for_*"): "walk_value",
    ("ntfs", "created_for_*"): "walk_value",
    ("ntfs", "created_time_for_*"): "walk_value",
    ("ntfs", "creation_time_for_*"): "walk_value",
    ("ntfs", "modified_for_*"): "walk_value",
    ("ntfs", "modified_time_for_*"): "walk_value",
    ("ntfs", "modification_time_for_*"): "walk_value",
    ("ntfs", "start_block_for_*"): "walk_value",
    ("ntfs", "first_block_for_*"): "walk_value",
    ("ntfs", "inode_for_*"): "walk_value",
    ("ntfs", "inode_number_for_*"): "walk_value",
    ("ntfs", "mft_record_number_for_*"): "walk_value",
    ("ext", "file_names"): "walk_value",
    ("ext", "file_paths"): "walk_value",
    ("ext", "file_count"): "walk_value",
    ("ext", "root_file_names"): "walk_value",
    ("ext", "root_entry_names"): "walk_value",
    ("ext", "directory_names"): "walk_value",
    ("ext", "directory_count"): "walk_value",
    ("ext", "deleted_file_names"): "walk_value",
    ("ext", "deleted_file_count"): "walk_value",
    ("ext", "file_names_sorted"): "walk_value",
    ("ext", "number_of_files"): "walk_value",
    ("ext", "start_cluster"): "walk_value",
    ("ext", "first_cluster"): "walk_value",
    ("ext", "file_start_cluster"): "walk_value",
    ("ext", "offset_bytes"): "walk_value",
    ("ext", "file_offset_bytes"): "walk_value",
    ("ext", "data_offset_bytes"): "walk_value",
    ("ext", "start_offset_bytes"): "walk_value",
    ("ext", "file_size_bytes"): "walk_value",
    ("ext", "file_size"): "walk_value",
    ("ext", "created"): "walk_value",
    ("ext", "created_time"): "walk_value",
    ("ext", "creation_time"): "walk_value",
    ("ext", "modified"): "walk_value",
    ("ext", "modified_time"): "walk_value",
    ("ext", "modification_time"): "walk_value",
    ("ext", "start_block"): "walk_value",
    ("ext", "first_block"): "walk_value",
    ("ext", "inode"): "walk_value",
    ("ext", "inode_number"): "walk_value",
    ("ext", "mft_record_number"): "walk_value",
    ("ext", "start_cluster_for_*"): "walk_value",
    ("ext", "first_cluster_for_*"): "walk_value",
    ("ext", "file_start_cluster_for_*"): "walk_value",
    ("ext", "offset_bytes_for_*"): "walk_value",
    ("ext", "file_offset_bytes_for_*"): "walk_value",
    ("ext", "data_offset_bytes_for_*"): "walk_value",
    ("ext", "start_offset_bytes_for_*"): "walk_value",
    ("ext", "file_size_bytes_for_*"): "walk_value",
    ("ext", "file_size_for_*"): "walk_value",
    ("ext", "created_for_*"): "walk_value",
    ("ext", "created_time_for_*"): "walk_value",
    ("ext", "creation_time_for_*"): "walk_value",
    ("ext", "modified_for_*"): "walk_value",
    ("ext", "modified_time_for_*"): "walk_value",
    ("ext", "modification_time_for_*"): "walk_value",
    ("ext", "start_block_for_*"): "walk_value",
    ("ext", "first_block_for_*"): "walk_value",
    ("ext", "inode_for_*"): "walk_value",
    ("ext", "inode_number_for_*"): "walk_value",
    ("ext", "mft_record_number_for_*"): "walk_value",
    ("ext", "volume_name"): "walk_value",
    ("ext", "volume_label"): "walk_value",
    ("ext", "filesystem_uuid"): "walk_value",
    ("ext", "uuid"): "walk_value",
    ("ext", "last_mounted"): "walk_value",
    ("ext", "last_mounted_directory"): "walk_value",
    ("ext", "block_size"): "walk_value",
    ("ext", "block_size_bytes"): "walk_value",
    ("ext", "inode_count"): "walk_value",
    ("ext", "block_count"): "walk_value",
    ("ext", "inode_size"): "walk_value",
    ("ext2", "file_names"): "walk_value",
    ("ext2", "file_paths"): "walk_value",
    ("ext2", "file_count"): "walk_value",
    ("ext2", "root_file_names"): "walk_value",
    ("ext2", "root_entry_names"): "walk_value",
    ("ext2", "directory_names"): "walk_value",
    ("ext2", "directory_count"): "walk_value",
    ("ext2", "deleted_file_names"): "walk_value",
    ("ext2", "deleted_file_count"): "walk_value",
    ("ext2", "file_names_sorted"): "walk_value",
    ("ext2", "number_of_files"): "walk_value",
    ("ext2", "start_cluster"): "walk_value",
    ("ext2", "first_cluster"): "walk_value",
    ("ext2", "file_start_cluster"): "walk_value",
    ("ext2", "offset_bytes"): "walk_value",
    ("ext2", "file_offset_bytes"): "walk_value",
    ("ext2", "data_offset_bytes"): "walk_value",
    ("ext2", "start_offset_bytes"): "walk_value",
    ("ext2", "file_size_bytes"): "walk_value",
    ("ext2", "file_size"): "walk_value",
    ("ext2", "created"): "walk_value",
    ("ext2", "created_time"): "walk_value",
    ("ext2", "creation_time"): "walk_value",
    ("ext2", "modified"): "walk_value",
    ("ext2", "modified_time"): "walk_value",
    ("ext2", "modification_time"): "walk_value",
    ("ext2", "start_block"): "walk_value",
    ("ext2", "first_block"): "walk_value",
    ("ext2", "inode"): "walk_value",
    ("ext2", "inode_number"): "walk_value",
    ("ext2", "mft_record_number"): "walk_value",
    ("ext2", "start_cluster_for_*"): "walk_value",
    ("ext2", "first_cluster_for_*"): "walk_value",
    ("ext2", "file_start_cluster_for_*"): "walk_value",
    ("ext2", "offset_bytes_for_*"): "walk_value",
    ("ext2", "file_offset_bytes_for_*"): "walk_value",
    ("ext2", "data_offset_bytes_for_*"): "walk_value",
    ("ext2", "start_offset_bytes_for_*"): "walk_value",
    ("ext2", "file_size_bytes_for_*"): "walk_value",
    ("ext2", "file_size_for_*"): "walk_value",
    ("ext2", "created_for_*"): "walk_value",
    ("ext2", "created_time_for_*"): "walk_value",
    ("ext2", "creation_time_for_*"): "walk_value",
    ("ext2", "modified_for_*"): "walk_value",
    ("ext2", "modified_time_for_*"): "walk_value",
    ("ext2", "modification_time_for_*"): "walk_value",
    ("ext2", "start_block_for_*"): "walk_value",
    ("ext2", "first_block_for_*"): "walk_value",
    ("ext2", "inode_for_*"): "walk_value",
    ("ext2", "inode_number_for_*"): "walk_value",
    ("ext2", "mft_record_number_for_*"): "walk_value",
    ("ext2", "volume_name"): "walk_value",
    ("ext2", "volume_label"): "walk_value",
    ("ext2", "filesystem_uuid"): "walk_value",
    ("ext2", "uuid"): "walk_value",
    ("ext2", "last_mounted"): "walk_value",
    ("ext2", "last_mounted_directory"): "walk_value",
    ("ext2", "block_size"): "walk_value",
    ("ext2", "block_size_bytes"): "walk_value",
    ("ext2", "inode_count"): "walk_value",
    ("ext2", "block_count"): "walk_value",
    ("ext2", "inode_size"): "walk_value",
    ("ext3", "file_names"): "walk_value",
    ("ext3", "file_paths"): "walk_value",
    ("ext3", "file_count"): "walk_value",
    ("ext3", "root_file_names"): "walk_value",
    ("ext3", "root_entry_names"): "walk_value",
    ("ext3", "directory_names"): "walk_value",
    ("ext3", "directory_count"): "walk_value",
    ("ext3", "deleted_file_names"): "walk_value",
    ("ext3", "deleted_file_count"): "walk_value",
    ("ext3", "file_names_sorted"): "walk_value",
    ("ext3", "number_of_files"): "walk_value",
    ("ext3", "start_cluster"): "walk_value",
    ("ext3", "first_cluster"): "walk_value",
    ("ext3", "file_start_cluster"): "walk_value",
    ("ext3", "offset_bytes"): "walk_value",
    ("ext3", "file_offset_bytes"): "walk_value",
    ("ext3", "data_offset_bytes"): "walk_value",
    ("ext3", "start_offset_bytes"): "walk_value",
    ("ext3", "file_size_bytes"): "walk_value",
    ("ext3", "file_size"): "walk_value",
    ("ext3", "created"): "walk_value",
    ("ext3", "created_time"): "walk_value",
    ("ext3", "creation_time"): "walk_value",
    ("ext3", "modified"): "walk_value",
    ("ext3", "modified_time"): "walk_value",
    ("ext3", "modification_time"): "walk_value",
    ("ext3", "start_block"): "walk_value",
    ("ext3", "first_block"): "walk_value",
    ("ext3", "inode"): "walk_value",
    ("ext3", "inode_number"): "walk_value",
    ("ext3", "mft_record_number"): "walk_value",
    ("ext3", "start_cluster_for_*"): "walk_value",
    ("ext3", "first_cluster_for_*"): "walk_value",
    ("ext3", "file_start_cluster_for_*"): "walk_value",
    ("ext3", "offset_bytes_for_*"): "walk_value",
    ("ext3", "file_offset_bytes_for_*"): "walk_value",
    ("ext3", "data_offset_bytes_for_*"): "walk_value",
    ("ext3", "start_offset_bytes_for_*"): "walk_value",
    ("ext3", "file_size_bytes_for_*"): "walk_value",
    ("ext3", "file_size_for_*"): "walk_value",
    ("ext3", "created_for_*"): "walk_value",
    ("ext3", "created_time_for_*"): "walk_value",
    ("ext3", "creation_time_for_*"): "walk_value",
    ("ext3", "modified_for_*"): "walk_value",
    ("ext3", "modified_time_for_*"): "walk_value",
    ("ext3", "modification_time_for_*"): "walk_value",
    ("ext3", "start_block_for_*"): "walk_value",
    ("ext3", "first_block_for_*"): "walk_value",
    ("ext3", "inode_for_*"): "walk_value",
    ("ext3", "inode_number_for_*"): "walk_value",
    ("ext3", "mft_record_number_for_*"): "walk_value",
    ("ext3", "volume_name"): "walk_value",
    ("ext3", "volume_label"): "walk_value",
    ("ext3", "filesystem_uuid"): "walk_value",
    ("ext3", "uuid"): "walk_value",
    ("ext3", "last_mounted"): "walk_value",
    ("ext3", "last_mounted_directory"): "walk_value",
    ("ext3", "block_size"): "walk_value",
    ("ext3", "block_size_bytes"): "walk_value",
    ("ext3", "inode_count"): "walk_value",
    ("ext3", "block_count"): "walk_value",
    ("ext3", "inode_size"): "walk_value",
    ("ext4", "file_names"): "walk_value",
    ("ext4", "file_paths"): "walk_value",
    ("ext4", "file_count"): "walk_value",
    ("ext4", "root_file_names"): "walk_value",
    ("ext4", "root_entry_names"): "walk_value",
    ("ext4", "directory_names"): "walk_value",
    ("ext4", "directory_count"): "walk_value",
    ("ext4", "deleted_file_names"): "walk_value",
    ("ext4", "deleted_file_count"): "walk_value",
    ("ext4", "file_names_sorted"): "walk_value",
    ("ext4", "number_of_files"): "walk_value",
    ("ext4", "start_cluster"): "walk_value",
    ("ext4", "first_cluster"): "walk_value",
    ("ext4", "file_start_cluster"): "walk_value",
    ("ext4", "offset_bytes"): "walk_value",
    ("ext4", "file_offset_bytes"): "walk_value",
    ("ext4", "data_offset_bytes"): "walk_value",
    ("ext4", "start_offset_bytes"): "walk_value",
    ("ext4", "file_size_bytes"): "walk_value",
    ("ext4", "file_size"): "walk_value",
    ("ext4", "created"): "walk_value",
    ("ext4", "created_time"): "walk_value",
    ("ext4", "creation_time"): "walk_value",
    ("ext4", "modified"): "walk_value",
    ("ext4", "modified_time"): "walk_value",
    ("ext4", "modification_time"): "walk_value",
    ("ext4", "start_block"): "walk_value",
    ("ext4", "first_block"): "walk_value",
    ("ext4", "inode"): "walk_value",
    ("ext4", "inode_number"): "walk_value",
    ("ext4", "mft_record_number"): "walk_value",
    ("ext4", "start_cluster_for_*"): "walk_value",
    ("ext4", "first_cluster_for_*"): "walk_value",
    ("ext4", "file_start_cluster_for_*"): "walk_value",
    ("ext4", "offset_bytes_for_*"): "walk_value",
    ("ext4", "file_offset_bytes_for_*"): "walk_value",
    ("ext4", "data_offset_bytes_for_*"): "walk_value",
    ("ext4", "start_offset_bytes_for_*"): "walk_value",
    ("ext4", "file_size_bytes_for_*"): "walk_value",
    ("ext4", "file_size_for_*"): "walk_value",
    ("ext4", "created_for_*"): "walk_value",
    ("ext4", "created_time_for_*"): "walk_value",
    ("ext4", "creation_time_for_*"): "walk_value",
    ("ext4", "modified_for_*"): "walk_value",
    ("ext4", "modified_time_for_*"): "walk_value",
    ("ext4", "modification_time_for_*"): "walk_value",
    ("ext4", "start_block_for_*"): "walk_value",
    ("ext4", "first_block_for_*"): "walk_value",
    ("ext4", "inode_for_*"): "walk_value",
    ("ext4", "inode_number_for_*"): "walk_value",
    ("ext4", "mft_record_number_for_*"): "walk_value",
    ("ext4", "volume_name"): "walk_value",
    ("ext4", "volume_label"): "walk_value",
    ("ext4", "filesystem_uuid"): "walk_value",
    ("ext4", "uuid"): "walk_value",
    ("ext4", "last_mounted"): "walk_value",
    ("ext4", "last_mounted_directory"): "walk_value",
    ("ext4", "block_size"): "walk_value",
    ("ext4", "block_size_bytes"): "walk_value",
    ("ext4", "inode_count"): "walk_value",
    ("ext4", "block_count"): "walk_value",
    ("ext4", "inode_size"): "walk_value",
    ("filesystem", "file_names"): "walk_value",
    ("filesystem", "file_paths"): "walk_value",
    ("filesystem", "file_count"): "walk_value",
    ("filesystem", "root_file_names"): "walk_value",
    ("filesystem", "root_entry_names"): "walk_value",
    ("filesystem", "directory_names"): "walk_value",
    ("filesystem", "directory_count"): "walk_value",
    ("filesystem", "deleted_file_names"): "walk_value",
    ("filesystem", "deleted_file_count"): "walk_value",
    ("filesystem", "file_names_sorted"): "walk_value",
    ("filesystem", "number_of_files"): "walk_value",
    ("filesystem", "start_cluster"): "walk_value",
    ("filesystem", "first_cluster"): "walk_value",
    ("filesystem", "file_start_cluster"): "walk_value",
    ("filesystem", "offset_bytes"): "walk_value",
    ("filesystem", "file_offset_bytes"): "walk_value",
    ("filesystem", "data_offset_bytes"): "walk_value",
    ("filesystem", "start_offset_bytes"): "walk_value",
    ("filesystem", "file_size_bytes"): "walk_value",
    ("filesystem", "file_size"): "walk_value",
    ("filesystem", "created"): "walk_value",
    ("filesystem", "created_time"): "walk_value",
    ("filesystem", "creation_time"): "walk_value",
    ("filesystem", "modified"): "walk_value",
    ("filesystem", "modified_time"): "walk_value",
    ("filesystem", "modification_time"): "walk_value",
    ("filesystem", "start_block"): "walk_value",
    ("filesystem", "first_block"): "walk_value",
    ("filesystem", "inode"): "walk_value",
    ("filesystem", "inode_number"): "walk_value",
    ("filesystem", "mft_record_number"): "walk_value",
    ("filesystem", "start_cluster_for_*"): "walk_value",
    ("filesystem", "first_cluster_for_*"): "walk_value",
    ("filesystem", "file_start_cluster_for_*"): "walk_value",
    ("filesystem", "offset_bytes_for_*"): "walk_value",
    ("filesystem", "file_offset_bytes_for_*"): "walk_value",
    ("filesystem", "data_offset_bytes_for_*"): "walk_value",
    ("filesystem", "start_offset_bytes_for_*"): "walk_value",
    ("filesystem", "file_size_bytes_for_*"): "walk_value",
    ("filesystem", "file_size_for_*"): "walk_value",
    ("filesystem", "created_for_*"): "walk_value",
    ("filesystem", "created_time_for_*"): "walk_value",
    ("filesystem", "creation_time_for_*"): "walk_value",
    ("filesystem", "modified_for_*"): "walk_value",
    ("filesystem", "modified_time_for_*"): "walk_value",
    ("filesystem", "modification_time_for_*"): "walk_value",
    ("filesystem", "start_block_for_*"): "walk_value",
    ("filesystem", "first_block_for_*"): "walk_value",
    ("filesystem", "inode_for_*"): "walk_value",
    ("filesystem", "inode_number_for_*"): "walk_value",
    ("filesystem", "mft_record_number_for_*"): "walk_value",
    ("filesystem", "partition_1_*"): "walk_value",
    ("filesystem", "partition_2_*"): "walk_value",
    ("filesystem", "partition_3_*"): "walk_value",
    ("filesystem", "partition_4_*"): "walk_value",
    ("filesystem", "p1_*"): "walk_value",
    ("filesystem", "p2_*"): "walk_value",
    ("filesystem", "p3_*"): "walk_value",
    ("filesystem", "p4_*"): "walk_value",
    ("disk", "file_names"): "walk_value",
    ("disk", "file_paths"): "walk_value",
    ("disk", "file_count"): "walk_value",
    ("disk", "root_file_names"): "walk_value",
    ("disk", "root_entry_names"): "walk_value",
    ("disk", "directory_names"): "walk_value",
    ("disk", "directory_count"): "walk_value",
    ("disk", "deleted_file_names"): "walk_value",
    ("disk", "deleted_file_count"): "walk_value",
    ("disk", "file_names_sorted"): "walk_value",
    ("disk", "number_of_files"): "walk_value",
    ("disk", "start_cluster"): "walk_value",
    ("disk", "first_cluster"): "walk_value",
    ("disk", "file_start_cluster"): "walk_value",
    ("disk", "offset_bytes"): "walk_value",
    ("disk", "file_offset_bytes"): "walk_value",
    ("disk", "data_offset_bytes"): "walk_value",
    ("disk", "start_offset_bytes"): "walk_value",
    ("disk", "file_size_bytes"): "walk_value",
    ("disk", "file_size"): "walk_value",
    ("disk", "created"): "walk_value",
    ("disk", "created_time"): "walk_value",
    ("disk", "modified"): "walk_value",
    ("disk", "modified_time"): "walk_value",
    ("disk", "modification_time"): "walk_value",
    ("disk", "start_block"): "walk_value",
    ("disk", "first_block"): "walk_value",
    ("disk", "inode"): "walk_value",
    ("disk", "inode_number"): "walk_value",
    ("disk", "mft_record_number"): "walk_value",
    ("disk", "start_cluster_for_*"): "walk_value",
    ("disk", "first_cluster_for_*"): "walk_value",
    ("disk", "file_start_cluster_for_*"): "walk_value",
    ("disk", "offset_bytes_for_*"): "walk_value",
    ("disk", "file_offset_bytes_for_*"): "walk_value",
    ("disk", "data_offset_bytes_for_*"): "walk_value",
    ("disk", "start_offset_bytes_for_*"): "walk_value",
    ("disk", "file_size_bytes_for_*"): "walk_value",
    ("disk", "file_size_for_*"): "walk_value",
    ("disk", "created_for_*"): "walk_value",
    ("disk", "created_time_for_*"): "walk_value",
    ("disk", "creation_time_for_*"): "walk_value",
    ("disk", "modified_for_*"): "walk_value",
    ("disk", "modified_time_for_*"): "walk_value",
    ("disk", "modification_time_for_*"): "walk_value",
    ("disk", "start_block_for_*"): "walk_value",
    ("disk", "first_block_for_*"): "walk_value",
    ("disk", "inode_for_*"): "walk_value",
    ("disk", "inode_number_for_*"): "walk_value",
    ("disk", "mft_record_number_for_*"): "walk_value",
    ("disk", "partition_1_*"): "walk_value",
    ("disk", "partition_2_*"): "walk_value",
    ("disk", "partition_3_*"): "walk_value",
    ("disk", "partition_4_*"): "walk_value",
    ("disk", "p1_*"): "walk_value",
    ("disk", "p2_*"): "walk_value",
    ("disk", "p3_*"): "walk_value",
    ("disk", "p4_*"): "walk_value",
}

_NONE = "none"
_FAT_FMTS = {"fat": "fat", "fat12": "fat", "fat16": "fat", "fat32": "fat", "vfat": "fat", "exfat": "exfat",
             "ntfs": "ntfs", "ext": "ext", "ext2": "ext", "ext3": "ext", "ext4": "ext"}
_PER = {"start_cluster": "start", "first_cluster": "start", "file_start_cluster": "start", "start_block": "start",
        "first_block": "start", "offset_bytes": "offset", "file_offset_bytes": "offset", "data_offset_bytes": "offset",
        "start_offset_bytes": "offset", "file_size_bytes": "size", "file_size": "size", "created": "created",
        "created_time": "created", "creation_time": "created", "modified": "modified", "modified_time": "modified",
        "modification_time": "modified", "inode": "inode", "inode_number": "inode", "mft_record_number": "inode"}
_PART = re.compile(r"^(?:partition_|p)(\d+)_(.+)$")
_FOR = re.compile(r"^(.+?)_for_(.+)$")
_MAXF = 20000


def _u(b, o, n):
    return int.from_bytes(b[o:o + n], "little") if 0 <= o and len(b) >= o + n else None


def _ext_at(b, o):
    return len(b) >= o + 2048 and b[o + 1024 + 0x38:o + 1024 + 0x3A] == b"\x53\xef"


def _kind(b, o):
    k = _fs_kind(b, o)
    if k:
        return k
    return "ext" if _ext_at(b, o) else None


def _volumes(b):
    """[(offset, kind)] in table order (bare volume -> one entry); kind None when unrecognised."""
    k = _kind(b, 0)
    if k:
        return [(0, k)]
    ents = _mbr_entries(b)
    if not ents:
        return []
    if any(e[2] == 0xEE for e in ents):
        g = _gpt(b)
        offs = [e["first"] * g["sector"] for e in g["entries"]] if g else []
    else:
        offs = [e[3] * 512 for e in ents if e[2] not in (0x05, 0x0F, 0x85)]
    return [(o, _kind(b, o)) for o in offs]


def _dos(d, t, extra_s=0):
    if not d:
        return None
    try:
        return (datetime(1980 + (d >> 9), (d >> 5) & 15, d & 31, t >> 11, (t >> 5) & 63, (t & 31) * 2)
                + timedelta(seconds=extra_s)).strftime("%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def _unix(s):
    if not s:
        return None
    return datetime.fromtimestamp(s, timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _ft(v):
    if not v:
        return None
    try:
        return (datetime(1601, 1, 1) + timedelta(microseconds=v // 10)).strftime("%Y-%m-%d %H:%M:%S")
    except OverflowError:
        return None


def _rec(name, path, size, start, offset, created, modified, inode=None, deleted=False, is_dir=False):
    return {"name": name, "path": path, "size": size, "start": start, "offset": offset, "created": created,
            "modified": modified, "inode": inode, "deleted": deleted, "dir": is_dir}


# ---------------------------------------------------------------- FAT12/16/32
def _fat(b, o):
    bps, spc, rsvd, nfats = _u(b, o + 0x0B, 2), b[o + 0x0D], _u(b, o + 0x0E, 2), b[o + 0x10]
    roots, tot16, fat16sz, tot32 = _u(b, o + 0x11, 2), _u(b, o + 0x13, 2), _u(b, o + 0x16, 2), _u(b, o + 0x20, 4)
    fatsz = fat16sz or _u(b, o + 0x24, 4)
    tot = tot16 or tot32
    rds = (roots * 32 + bps - 1) // bps
    data_sec = rsvd + nfats * fatsz + rds
    ncl = max(tot - data_sec, 0) // spc
    bits = 12 if ncl < 4085 else 16 if ncl < 65525 else 32
    cl = bps * spc
    fat_off = o + rsvd * bps
    data_off = o + data_sec * bps

    def nxt(c):
        if bits == 12:
            v = _u(b, fat_off + c + c // 2, 2)
            if v is None:
                return None
            v = v >> 4 if c & 1 else v & 0xFFF
            return None if v >= 0xFF7 else v
        if bits == 16:
            v = _u(b, fat_off + 2 * c, 2)
            return None if v is None or v >= 0xFFF7 else v
        v = _u(b, fat_off + 4 * c, 4)
        v = None if v is None else v & 0x0FFFFFFF
        return None if v is None or v >= 0x0FFFFFF7 else v

    def chain_bytes(c):
        out, seen = bytearray(), set()
        while c is not None and 2 <= c < ncl + 2 and c not in seen and len(seen) < 65536:
            seen.add(c)
            s = data_off + (c - 2) * cl
            if s >= len(b):
                break
            out += b[s:s + cl]
            c = nxt(c)
        return bytes(out)

    files = []
    seen_dirs = set()

    def walk(raw, path, depth):
        lfn = {}
        for e in range(0, len(raw) - 31, 32):
            ent = raw[e:e + 32]
            first, attr = ent[0], ent[11]
            if first == 0:
                break
            if attr == 0x0F:
                seq = ent[0]
                part = (ent[1:11] + ent[14:26] + ent[28:32]).decode("utf-16-le", "replace")
                if first == 0xE5:
                    lfn.setdefault("_del", []).insert(0, part)
                else:
                    if seq & 0x40:
                        lfn = {}
                    lfn[seq & 0x1F] = part
                continue
            deleted = first == 0xE5
            if attr & 0x08:              # volume label (or a stray LFN with label bit)
                lfn = {}
                continue
            base, ext = ent[0:8], ent[8:11]
            if base[:1] == b".":
                lfn = {}
                continue
            if deleted:
                base = b"_" + base[1:]
            bs, es = base.decode("latin-1").rstrip(), ext.decode("latin-1").rstrip()
            if ent[12] & 0x08:
                bs = bs.lower()
            if ent[12] & 0x10:
                es = es.lower()
            short = bs + ("." + es if es else "")
            if deleted and lfn.get("_del"):
                long = "".join(lfn["_del"])
            elif not deleted and lfn and "_del" not in lfn:
                long = "".join(lfn[k] for k in sorted(lfn))
            else:
                long = None
            name = (long.split("\0", 1)[0].rstrip("￿") if long else "") or short
            lfn = {}
            start = (_u(ent, 0x14, 2) << 16 if bits == 32 else 0) | _u(ent, 0x1A, 2)
            size = _u(ent, 0x1C, 4)
            is_dir = bool(attr & 0x10)
            p = path + "/" + name
            files.append(_rec(name, p, size, start or None,
                              data_off + (start - 2) * cl if start >= 2 else None,
                              _dos(_u(ent, 0x10, 2), _u(ent, 0x0E, 2), ent[0x0D] // 100),
                              _dos(_u(ent, 0x18, 2), _u(ent, 0x16, 2)), None, deleted, is_dir))
            if is_dir and not deleted and start >= 2 and start not in seen_dirs and depth < 16 and len(files) < _MAXF:
                seen_dirs.add(start)
                walk(chain_bytes(start), p, depth + 1)

    if bits == 32:
        rc = _u(b, o + 0x2C, 4)
        seen_dirs.add(rc)
        root = chain_bytes(rc)
    else:
        rs = o + (rsvd + nfats * fatsz) * bps
        root = b[rs:rs + rds * bps]
    walk(root, "", 0)
    return {"files": files}


# ---------------------------------------------------------------- exFAT
def _exfat(b, o):
    bsh, csh = b[o + 0x6C], b[o + 0x6D]
    if not 9 <= bsh <= 12 or bsh + csh > 25:
        return None
    bps, cl = 1 << bsh, 1 << (bsh + csh)
    fat_off = o + _u(b, o + 0x50, 4) * bps
    heap = o + _u(b, o + 0x58, 4) * bps
    ncl, root = _u(b, o + 0x5C, 4), _u(b, o + 0x60, 4)

    def chain_bytes(c, length=None, contiguous=False):
        out, seen = bytearray(), set()
        while c is not None and 2 <= c < ncl + 2 and c not in seen and len(seen) < 65536:
            seen.add(c)
            s = heap + (c - 2) * cl
            if s >= len(b):
                break
            out += b[s:s + cl]
            if length is not None and len(out) >= length:
                return bytes(out[:length])
            if contiguous:
                c += 1
                continue
            v = _u(b, fat_off + 4 * c, 4)
            c = None if v is None or v >= 0xFFFFFFF7 else v
        return bytes(out)

    files = []
    seen_dirs = {root}

    def walk(raw, path, depth):
        e = 0
        while e + 32 <= len(raw):
            t = raw[e]
            if t == 0:
                break
            if t & 0x7F == 0x05:
                deleted = t == 0x05
                n2 = raw[e + 1]
                sets = raw[e:e + 32 * (n2 + 1)]
                e += 32 * (n2 + 1)
                if len(sets) < 64 or sets[32] & 0x7F != 0x40:
                    continue
                attr = _u(sets, 4, 2)
                st = sets[32:64]
                nlen, first, dlen, flags = st[3], _u(st, 20, 4), _u(st, 24, 8), st[1]
                name = "".join(sets[i:i + 32][2:32].decode("utf-16-le", "replace")
                               for i in range(64, len(sets), 32) if sets[i] & 0x7F == 0x41)[:nlen]
                c32, m32 = _u(sets, 8, 4), _u(sets, 12, 4)
                is_dir = bool(attr & 0x10)
                p = path + "/" + name
                files.append(_rec(name, p, dlen, first or None, heap + (first - 2) * cl if first >= 2 else None,
                                  _dos(c32 >> 16, c32 & 0xFFFF, sets[20] // 100), _dos(m32 >> 16, m32 & 0xFFFF),
                                  None, deleted, is_dir))
                if is_dir and not deleted and first >= 2 and first not in seen_dirs and depth < 16 \
                        and len(files) < _MAXF:
                    seen_dirs.add(first)
                    walk(chain_bytes(first, dlen or None, bool(flags & 2)), p, depth + 1)
                continue
            e += 32

    walk(chain_bytes(root), "", 0)
    return {"files": files}


# ---------------------------------------------------------------- ext2/3/4
def _ext(b, o):
    sb = o + 1024
    bs = 1024 << _u(b, sb + 0x18, 4)
    if bs > 65536:
        return None
    ipg, first_data = _u(b, sb + 0x28, 4), _u(b, sb + 0x14, 4)
    rev = _u(b, sb + 0x4C, 4)
    isz = _u(b, sb + 0x58, 2) if rev else 128
    incompat = _u(b, sb + 0x60, 4)
    dsz = (_u(b, sb + 0xFE, 2) or 32) if incompat & 0x80 else 32
    gdt = o + (first_data + 1) * bs

    def blk(n):
        return b[o + n * bs:o + (n + 1) * bs]

    def inode(n):
        g, i = (n - 1) // ipg, (n - 1) % ipg
        d = gdt + g * dsz
        it = _u(b, d + 8, 4)
        if it is None:
            return None
        if dsz >= 64:
            it |= _u(b, d + 0x28, 4) << 32
        s = o + it * bs + i * isz
        r = b[s:s + isz]
        return r if len(r) >= 128 else None

    def blocks(ino):
        """[(logical, physical)] data blocks in logical order (capped)."""
        flags = _u(ino, 0x20, 4)
        ib = ino[0x28:0x28 + 60]
        out = []
        if flags & 0x80000 and _u(ib, 0, 2) == 0xF30A:
            def ext_node(node, depth_guard):
                if _u(node, 0, 2) != 0xF30A or depth_guard > 6:
                    return
                n, depth = _u(node, 2, 2), _u(node, 6, 2)
                for k in range(n):
                    e = 12 + 12 * k
                    if depth == 0:
                        lb, ln = _u(node, e, 4), _u(node, e + 4, 2)
                        if ln > 32768:
                            ln -= 32768          # uninitialised extent
                        pb = _u(node, e + 6, 2) << 32 | _u(node, e + 8, 4)
                        for j in range(min(ln, 4096)):
                            out.append((lb + j, pb + j))
                    else:
                        leaf = _u(node, e + 8, 2) << 32 | _u(node, e + 4, 4)
                        ext_node(blk(leaf), depth_guard + 1)
            ext_node(ib, 0)
        elif not flags & 0x10000000:            # not inline data
            ptr = [_u(ib, 4 * k, 4) for k in range(15)]
            lst = ptr[:12]
            per = bs // 4
            if ptr[12]:
                ind = blk(ptr[12])
                lst += [_u(ind, 4 * k, 4) for k in range(per)]
            if ptr[13]:
                dind = blk(ptr[13])
                for k in range(per):
                    p = _u(dind, 4 * k, 4)
                    if p:
                        ind = blk(p)
                        lst += [_u(ind, 4 * j, 4) for j in range(per)]
                    if len(lst) > 65536:
                        break
            out = [(i, p) for i, p in enumerate(lst) if p]
        return out

    def size(ino):
        return _u(ino, 4, 4) | (_u(ino, 0x6C, 4) << 32)

    files = []
    seen = {2}

    def walk(n, path, depth):
        ino = inode(n)
        if ino is None:
            return
        raw = b"".join(blk(p) for _, p in blocks(ino)[:4096])
        e = 0
        while e + 8 <= len(raw):
            dino, rl, nl, ft = _u(raw, e, 4), _u(raw, e + 4, 2), raw[e + 6], raw[e + 7]
            if rl < 8:
                break
            nm = raw[e + 8:e + 8 + nl].decode("utf-8", "replace")
            e += rl
            if not dino or nm in (".", "..") or not nm:
                continue
            ci = inode(dino)
            if ci is None:
                continue
            mode = _u(ci, 0, 2)
            is_dir = (mode & 0xF000) == 0x4000 if mode else ft == 2
            bl = blocks(ci) if (mode & 0xF000) in (0x8000, 0x4000) else []
            st = bl[0][1] if bl else None
            cr = _u(ci, 0x90, 4) if isz >= 0x94 and 128 + _u(ci, 0x80, 2) >= 0x94 else None
            p = path + "/" + nm
            files.append(_rec(nm, p, size(ci), st, o + st * bs if st else None, _unix(cr), _unix(_u(ci, 0x10, 4)),
                              dino, False, is_dir))
            if is_dir and dino not in seen and depth < 16 and len(files) < _MAXF:
                seen.add(dino)
                walk(dino, p, depth + 1)

    walk(2, "", 0)
    s = b[sb:sb + 1024]
    vol = {"volume_name": s[0x78:0x88].split(b"\0", 1)[0].decode("utf-8", "replace") or _NONE,
           "uuid": str(uuid.UUID(bytes=bytes(s[0x68:0x78]))),
           "last_mounted": s[0x88:0xC8].split(b"\0", 1)[0].decode("utf-8", "replace") or _NONE,
           "block_size": bs, "inode_count": _u(s, 0, 4), "inode_size": isz,
           "block_count": _u(s, 4, 4) | ((_u(s, 0x150, 4) << 32) if incompat & 0x80 else 0)}
    for a, t in (("volume_label", "volume_name"), ("filesystem_uuid", "uuid"),
                 ("last_mounted_directory", "last_mounted"), ("block_size_bytes", "block_size")):
        vol[a] = vol[t]
    return {"files": files, "vol": vol}


# ---------------------------------------------------------------- NTFS
def _ntfs(b, o):
    bps, spc_raw = _u(b, o + 0x0B, 2), b[o + 0x0D]
    spc = 1 << (256 - spc_raw) if spc_raw >= 0x80 else spc_raw
    cl = bps * spc
    r = b[o + 0x40]
    rsz = 1 << (256 - r) if r >= 0x80 else r * cl
    if not 256 <= rsz <= 65536:
        return None
    mft = o + _u(b, o + 0x30, 8) * cl

    def fixup(rec):
        rec = bytearray(rec)
        uo, un = _u(rec, 4, 2), _u(rec, 6, 2)
        if uo is None or un is None or uo + 2 * un > len(rec):
            return None
        usn = rec[uo:uo + 2]
        for k in range(1, un):
            end = k * 512 - 2
            if end + 2 > len(rec) or rec[end:end + 2] != usn:
                return None
            rec[end:end + 2] = rec[uo + 2 * k:uo + 2 * k + 2]
        return bytes(rec)

    def first_lcn(attr):
        ro = _u(attr, 0x20, 2)
        hdr = attr[ro]
        ln, lo = hdr & 0xF, hdr >> 4
        if not ln or not lo:
            return None
        v = int.from_bytes(attr[ro + 1 + ln:ro + 1 + ln + lo], "little", signed=True)
        return v

    # $MFT's own extent: walk records by the $MFT data run length (contiguous first run only)
    rec0 = fixup(b[mft:mft + rsz])
    if not rec0 or rec0[:4] != b"FILE":
        return None
    nrec = 0
    a = _u(rec0, 0x14, 2)
    while a + 16 <= len(rec0):
        t, ln = _u(rec0, a, 4), _u(rec0, a + 4, 4)
        if t == 0xFFFFFFFF or not ln:
            break
        if t == 0x80 and rec0[a + 8]:
            nrec = _u(rec0, a + 0x30, 8) // rsz
            break
        a += ln
    recs = {}
    for n in range(min(nrec or 0, _MAXF)):
        raw = b[mft + n * rsz:mft + (n + 1) * rsz]
        if len(raw) < rsz or raw[:4] != b"FILE":
            continue
        rec = fixup(raw)
        if rec is None:
            continue
        flags = _u(rec, 0x16, 2)
        if _u(rec, 0x20, 8):            # extension record (base reference set)
            continue
        names, size, start, si = [], None, None, None
        a = _u(rec, 0x14, 2)
        while a + 16 <= len(rec):
            t, ln = _u(rec, a, 4), _u(rec, a + 4, 4)
            if t == 0xFFFFFFFF or not ln or a + ln > len(rec):
                break
            attr = rec[a:a + ln]
            nonres, nlen = attr[8], attr[9]
            if t == 0x10 and not nonres:
                v = _u(attr, 0x14, 2)
                si = (_u(attr, v, 8), _u(attr, v + 8, 8))
            elif t == 0x30 and not nonres:
                v = _u(attr, 0x14, 2)
                fl, ns = attr[v + 0x40], attr[v + 0x41]
                nm = attr[v + 0x42:v + 0x42 + 2 * fl].decode("utf-16-le", "replace")
                names.append((ns == 2, _u(attr, v, 6), nm))
            elif t == 0x80 and nlen == 0:
                if nonres:
                    size = _u(attr, 0x30, 8)
                    start = first_lcn(attr)
                else:
                    size = _u(attr, 0x10, 4)
            a += ln
        if not names:
            continue
        names.sort()
        recs[n] = {"name": names[0][2], "parent": names[0][1], "dir": bool(flags & 2), "inuse": bool(flags & 1),
                   "size": size, "start": start, "si": si}
    files = []

    def path_of(n, depth=0):
        rr = recs.get(n)
        if rr is None or n == 5 or depth > 32:
            return ""
        return path_of(rr["parent"], depth + 1) + "/" + rr["name"]

    for n, rr in recs.items():
        if n < 16 or (rr["name"].startswith("$") and n < 64):
            continue
        st = rr["start"]
        files.append(_rec(rr["name"], path_of(n), rr["size"] if not rr["dir"] else 0, st,
                          o + st * cl if st else None, _ft(rr["si"][0]) if rr["si"] else None,
                          _ft(rr["si"][1]) if rr["si"] else None, n, not rr["inuse"], rr["dir"]))
        files[-1]["root"] = rr["parent"] == 5
    return {"files": files}


_WALK = {"fat": _fat, "exfat": _exfat, "ext": _ext, "ntfs": _ntfs}


# ---------------------------------------------------------------- answering
def _norm(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _qtext(ctx):
    q = ctx.get("question")
    if isinstance(q, dict):
        q = q.get("question") or ""
    return str(q or "")


def _pick(files, param, ctx):
    live = [f for f in files if not f["dir"]]
    if param:
        p = _norm(param)
        for key in (lambda f: _norm(f["name"]), lambda f: _norm(f["path"]),
                    lambda f: _norm(f["name"].rsplit(".", 1)[0])):
            hit = [f for f in live if key(f) == p]
            if hit:
                hit.sort(key=lambda f: f["deleted"])
                return hit[0]
        return None
    q = _qtext(ctx).lower()
    member = str(ctx.get("member") or "").lower()
    hit = [f for f in live if len(f["name"]) > 2 and f["name"].lower() != member
           and re.search(r"(?<![\w.])" + re.escape(f["name"].lower()) + r"(?![\w])", q)]
    if hit:
        hit.sort(key=lambda f: (-len(f["name"]), f["deleted"]))
        return hit[0]
    alive = [f for f in live if not f["deleted"]]
    return alive[0] if len(alive) == 1 else None


def _value(res, field, ctx):
    files = [f for f in res["files"]]
    alive = [f for f in files if not f["deleted"]]
    reg = [f for f in alive if not f["dir"]]
    if field in ("file_names", "file_names_sorted"):
        return sorted(f["name"] for f in reg)
    if field == "file_paths":
        return sorted(f["path"] for f in reg)
    if field in ("file_count", "number_of_files"):
        return len(reg)
    if field in ("root_file_names", "root_entry_names"):
        root = [f for f in alive if f["path"].count("/") == 1 or f.get("root")]
        if field == "root_file_names":
            root = [f for f in root if not f["dir"]]
        return sorted(f["name"] for f in root)
    if field == "directory_names":
        return sorted(f["name"] for f in alive if f["dir"])
    if field == "directory_count":
        return len([f for f in alive if f["dir"]])
    if field == "deleted_file_names":
        return sorted(f["name"] for f in files if f["deleted"] and not f["dir"])
    if field == "deleted_file_count":
        return len([f for f in files if f["deleted"] and not f["dir"]])
    vol = res.get("vol") or {}
    if field in vol:
        return vol[field]
    m = _FOR.match(field)
    base, param = (m.group(1), m.group(2)) if m and m.group(1) in _PER else (field, None)
    what = _PER.get(base)
    if what is None:
        return None
    f = _pick(files, param, ctx)
    if f is None:
        return None
    v = f.get(what)
    return _NONE if v is None else v


def walk_value(data, ctx):
    """<fs>.<field>: the directory walk of the (selected) volume's filesystem; see the module docstring."""
    if not data:
        return None
    try:
        b = bytes(data)
        fmt, field = ctx.get("fmt") or "", ctx.get("field") or ""
        want = _FAT_FMTS.get(fmt)
        part = None
        m = _PART.match(field)
        if m and fmt in ("disk", "filesystem"):
            part, field = int(m.group(1)), m.group(2)
        vols = _volumes(b)
        if part is not None:
            if not 1 <= part <= len(vols):
                return _NONE
            vols = [vols[part - 1]]
        vols = [v for v in vols if v[1] and (want is None or v[1] == want)]
        if not vols:
            return _NONE
        off, kind = vols[0]
        res = _WALK[kind](b, off)
        if not res:
            return _NONE
        v = _value(res, field, ctx)
        return _NONE if v is None and field in ("volume_name",) else v
    except (IndexError, ValueError, struct.error, TypeError, OverflowError, KeyError, RecursionError):
        return None
