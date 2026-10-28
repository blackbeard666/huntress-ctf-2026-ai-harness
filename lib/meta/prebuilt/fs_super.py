"""Non-Windows filesystem SUPERBLOCK fields (prebuilt, SPECULATIVE -- never GM-asked yet): ext2/3/4, XFS, Btrfs,
HFS+/HFSX, APFS container. fmts: ext/ext2/ext3/ext4 (only keys fs_walk.py lacks), xfs, btrfs, hfs/hfsplus/hfsx, apfs,
plus `filesystem` (auto-detect; keys vbr.py / fs_walk.py lack). Input is a bare volume or a raw disk image: when no
superblock sits at offset 0 the MBR/GPT is walked and the first partition carrying one is used (a question naming
"partition N" picks the Nth used entry in table order, 1-based).

ext: superblock @1024, magic 0xEF53 @0x38 (LE). inodes/blocks count @0/@4 (+ hi u32 @0x150 when incompat 64bit 0x80),
free blocks/inodes @0x0C/@0x10, first data block @0x14, block size 1024<<u32@0x18, blocks/inodes per group @0x20/@0x28,
mtime/wtime @0x2C/@0x30, mount count u16 @0x34, max mount count s16 @0x36, state u16 @0x3A (bit0 clean, bit1 errors ->
"clean" / "not clean" / "clean with errors" as dumpe2fs prints), lastcheck @0x40, creator os @0x48, rev @0x4C, feature
compat/incompat/ro_compat @0x5C/@0x60/@0x64, last_mounted @0x88 (64 B), mkfs_time @0x108. Times are u32 unix epoch
(UTC; ext4 stores the high byte in *_hi but only beyond 2038 -- ignored), 0 -> "none". filesystem_type follows libblkid:
ext4 if incompat has anything beyond filetype|recover|meta_bg|journal_dev or ro_compat beyond sparse_super|large_file|
btree_dir; else ext3 if compat has_journal (0x4); else ext2. filesystem_features = dumpe2fs order (compat, incompat,
ro_compat bit order, e2p names), compact JSON list.
XFS: `XFSB` @0 BIG-endian; blocksize u32 @4, dblocks u64 @8, rblocks @16, uuid @32, sectsize u16 @102, inodesize u16
@104, fname @108 (12 B, NUL-trimmed), icount u64 @128, ifree @136, fdblocks @144; versionnum u16 @100 (low nibble).
Btrfs: superblock @0x10000, magic `_BHRfS_M` @+0x40; fsid @+0x20, generation u64 @+0x48, total_bytes @+0x70,
bytes_used @+0x78, num_devices @+0x88, sectorsize u32 @+0x90, nodesize @+0x94, label @+0x12B (256 B). block_count =
total_bytes // sectorsize (= blkid FSLASTBLOCK).
HFS+: volume header @0x400 BE, signature `H+` (v4) / `HX` (v5); createDate @+0x10 (seconds since 1904, LOCAL time per
TN1150 -- rendered as stored, `Z`), modifyDate @+0x14 / backupDate @+0x18 / checkedDate @+0x1C (UTC), fileCount @+0x20,
folderCount @+0x24, blockSize @+0x28, totalBlocks @+0x2C, freeBlocks @+0x30, finderInfo @+0x50 (volume id = words
6..7 @+0x68). uuid = libblkid's UUIDv3 (MD5 of its fixed namespace + the 8-byte volume id) so it matches blkid/diskutil.
filesystem_type: hfsplus (blkid TYPE for both H+ and HX); hfs_signature gives `H+`/`HX`. Classic HFS (`BD` without an
embedded H+) -> "none".
APFS: container superblock NXSB @32 of block 0 (LE): block_size u32 @36, block_count u64 @40, uuid @72, next xid @96,
max file systems @180. Volume name/UUID live in the APSB behind the object map -- not read here.
Keys fs_walk.py already owns (ext*.uuid / volume_label / block_size / block_count / created_time ...) and vbr.py's
`filesystem.filesystem_type` / `volume_label` are NOT re-registered (their extractors answer those).
Timestamps ISO-8601 `YYYY-MM-DDTHH:MM:SSZ`. UUIDs canonical lowercase. Wrong magic / truncated -> "none"."""
import hashlib
import re
import struct
import uuid
from datetime import datetime, timedelta, timezone

from ..spell import Hex

FIELDS = {
    ('apfs', 'block_count'): "super_value",
    ('apfs', 'block_size'): "super_value",
    ('apfs', 'block_size_bytes'): "super_value",
    ('apfs', 'blocks_count'): "super_value",
    ('apfs', 'blocksize'): "super_value",
    ('apfs', 'container_uuid'): "super_value",
    ('apfs', 'filesystem_size_bytes'): "super_value",
    ('apfs', 'filesystem_type'): "super_value",
    ('apfs', 'filesystem_uuid'): "super_value",
    ('apfs', 'fs_type'): "super_value",
    ('apfs', 'fs_uuid'): "super_value",
    ('apfs', 'label'): "super_value",
    ('apfs', 'magic'): "super_value",
    ('apfs', 'max_file_systems'): "super_value",
    ('apfs', 'next_xid'): "super_value",
    ('apfs', 'nx_uuid'): "super_value",
    ('apfs', 'partition_offset_bytes'): "super_value",
    ('apfs', 'size_bytes'): "super_value",
    ('apfs', 'superblock_magic'): "super_value",
    ('apfs', 'superblock_offset'): "super_value",
    ('apfs', 'total_blocks'): "super_value",
    ('apfs', 'type'): "super_value",
    ('apfs', 'uuid'): "super_value",
    ('apfs', 'volume_label'): "super_value",
    ('apfs', 'volume_name'): "super_value",
    ('apfs', 'volume_size_bytes'): "super_value",
    ('apfs', 'volume_uuid'): "super_value",
    ('btrfs', 'block_count'): "super_value",
    ('btrfs', 'block_size'): "super_value",
    ('btrfs', 'block_size_bytes'): "super_value",
    ('btrfs', 'blocks_count'): "super_value",
    ('btrfs', 'blocksize'): "super_value",
    ('btrfs', 'bytes_used'): "super_value",
    ('btrfs', 'dev_uuid'): "super_value",
    ('btrfs', 'device_count'): "super_value",
    ('btrfs', 'device_uuid'): "super_value",
    ('btrfs', 'filesystem_size_bytes'): "super_value",
    ('btrfs', 'filesystem_type'): "super_value",
    ('btrfs', 'filesystem_uuid'): "super_value",
    ('btrfs', 'fs_type'): "super_value",
    ('btrfs', 'fs_uuid'): "super_value",
    ('btrfs', 'fsid'): "super_value",
    ('btrfs', 'generation'): "super_value",
    ('btrfs', 'label'): "super_value",
    ('btrfs', 'magic'): "super_value",
    ('btrfs', 'node_size'): "super_value",
    ('btrfs', 'nodesize'): "super_value",
    ('btrfs', 'num_devices'): "super_value",
    ('btrfs', 'partition_offset_bytes'): "super_value",
    ('btrfs', 'sector_size'): "super_value",
    ('btrfs', 'sectorsize'): "super_value",
    ('btrfs', 'size_bytes'): "super_value",
    ('btrfs', 'superblock_magic'): "super_value",
    ('btrfs', 'superblock_offset'): "super_value",
    ('btrfs', 'total_blocks'): "super_value",
    ('btrfs', 'total_bytes'): "super_value",
    ('btrfs', 'type'): "super_value",
    ('btrfs', 'uuid'): "super_value",
    ('btrfs', 'volume_label'): "super_value",
    ('btrfs', 'volume_name'): "super_value",
    ('btrfs', 'volume_size_bytes'): "super_value",
    ('btrfs', 'volume_uuid'): "super_value",
    ('ext', 'backup_time'): "super_value",
    ('ext', 'backup_time_utc'): "super_value",
    ('ext', 'blocks_count'): "super_value",
    ('ext', 'blocks_per_group'): "super_value",
    ('ext', 'blocksize'): "super_value",
    ('ext', 'checked_time'): "super_value",
    ('ext', 'checked_time_utc'): "super_value",
    ('ext', 'created_time_utc'): "super_value",
    ('ext', 'created_utc'): "super_value",
    ('ext', 'creation_time_utc'): "super_value",
    ('ext', 'creator_os'): "super_value",
    ('ext', 'feature_compat_u32_hex'): "super_value",
    ('ext', 'feature_incompat_u32_hex'): "super_value",
    ('ext', 'feature_ro_compat_u32_hex'): "super_value",
    ('ext', 'features'): "super_value",
    ('ext', 'filesystem_created'): "super_value",
    ('ext', 'filesystem_created_utc'): "super_value",
    ('ext', 'filesystem_features'): "super_value",
    ('ext', 'filesystem_revision'): "super_value",
    ('ext', 'filesystem_size_bytes'): "super_value",
    ('ext', 'filesystem_state'): "super_value",
    ('ext', 'filesystem_type'): "super_value",
    ('ext', 'first_data_block'): "super_value",
    ('ext', 'free_blocks'): "super_value",
    ('ext', 'free_blocks_count'): "super_value",
    ('ext', 'free_inodes'): "super_value",
    ('ext', 'free_inodes_count'): "super_value",
    ('ext', 'fs_type'): "super_value",
    ('ext', 'fs_uuid'): "super_value",
    ('ext', 'has_extents'): "super_value",
    ('ext', 'has_journal'): "super_value",
    ('ext', 'inodes_per_group'): "super_value",
    ('ext', 'is_64bit'): "super_value",
    ('ext', 'journal_present'): "super_value",
    ('ext', 'label'): "super_value",
    ('ext', 'last_check_time'): "super_value",
    ('ext', 'last_check_time_utc'): "super_value",
    ('ext', 'last_checked'): "super_value",
    ('ext', 'last_checked_utc'): "super_value",
    ('ext', 'last_modified_time'): "super_value",
    ('ext', 'last_modified_time_utc'): "super_value",
    ('ext', 'last_mount_path'): "super_value",
    ('ext', 'last_mount_time'): "super_value",
    ('ext', 'last_mount_time_utc'): "super_value",
    ('ext', 'last_mounted_on'): "super_value",
    ('ext', 'last_mounted_path'): "super_value",
    ('ext', 'last_mounted_time'): "super_value",
    ('ext', 'last_mounted_time_utc'): "super_value",
    ('ext', 'last_write_time'): "super_value",
    ('ext', 'last_write_time_utc'): "super_value",
    ('ext', 'last_written_time'): "super_value",
    ('ext', 'last_written_time_utc'): "super_value",
    ('ext', 'magic'): "super_value",
    ('ext', 'magic_u16_hex'): "super_value",
    ('ext', 'max_mount_count'): "super_value",
    ('ext', 'mkfs_time'): "super_value",
    ('ext', 'mkfs_time_utc'): "super_value",
    ('ext', 'modified_time_utc'): "super_value",
    ('ext', 'modify_time'): "super_value",
    ('ext', 'modify_time_utc'): "super_value",
    ('ext', 'mount_count'): "super_value",
    ('ext', 'mount_point'): "super_value",
    ('ext', 'mount_time'): "super_value",
    ('ext', 'mount_time_utc'): "super_value",
    ('ext', 'os_type'): "super_value",
    ('ext', 'partition_offset_bytes'): "super_value",
    ('ext', 'revision'): "super_value",
    ('ext', 'revision_level'): "super_value",
    ('ext', 'size_bytes'): "super_value",
    ('ext', 'state'): "super_value",
    ('ext', 'superblock_magic'): "super_value",
    ('ext', 'superblock_offset'): "super_value",
    ('ext', 'total_blocks'): "super_value",
    ('ext', 'type'): "super_value",
    ('ext', 'volume_size_bytes'): "super_value",
    ('ext', 'volume_uuid'): "super_value",
    ('ext', 'write_time'): "super_value",
    ('ext', 'write_time_utc'): "super_value",
    ('ext2', 'backup_time'): "super_value",
    ('ext2', 'backup_time_utc'): "super_value",
    ('ext2', 'blocks_count'): "super_value",
    ('ext2', 'blocks_per_group'): "super_value",
    ('ext2', 'blocksize'): "super_value",
    ('ext2', 'checked_time'): "super_value",
    ('ext2', 'checked_time_utc'): "super_value",
    ('ext2', 'created_time_utc'): "super_value",
    ('ext2', 'created_utc'): "super_value",
    ('ext2', 'creation_time_utc'): "super_value",
    ('ext2', 'creator_os'): "super_value",
    ('ext2', 'feature_compat_u32_hex'): "super_value",
    ('ext2', 'feature_incompat_u32_hex'): "super_value",
    ('ext2', 'feature_ro_compat_u32_hex'): "super_value",
    ('ext2', 'features'): "super_value",
    ('ext2', 'filesystem_created'): "super_value",
    ('ext2', 'filesystem_created_utc'): "super_value",
    ('ext2', 'filesystem_features'): "super_value",
    ('ext2', 'filesystem_revision'): "super_value",
    ('ext2', 'filesystem_size_bytes'): "super_value",
    ('ext2', 'filesystem_state'): "super_value",
    ('ext2', 'filesystem_type'): "super_value",
    ('ext2', 'first_data_block'): "super_value",
    ('ext2', 'free_blocks'): "super_value",
    ('ext2', 'free_blocks_count'): "super_value",
    ('ext2', 'free_inodes'): "super_value",
    ('ext2', 'free_inodes_count'): "super_value",
    ('ext2', 'fs_type'): "super_value",
    ('ext2', 'fs_uuid'): "super_value",
    ('ext2', 'has_extents'): "super_value",
    ('ext2', 'has_journal'): "super_value",
    ('ext2', 'inodes_per_group'): "super_value",
    ('ext2', 'is_64bit'): "super_value",
    ('ext2', 'journal_present'): "super_value",
    ('ext2', 'label'): "super_value",
    ('ext2', 'last_check_time'): "super_value",
    ('ext2', 'last_check_time_utc'): "super_value",
    ('ext2', 'last_checked'): "super_value",
    ('ext2', 'last_checked_utc'): "super_value",
    ('ext2', 'last_modified_time'): "super_value",
    ('ext2', 'last_modified_time_utc'): "super_value",
    ('ext2', 'last_mount_path'): "super_value",
    ('ext2', 'last_mount_time'): "super_value",
    ('ext2', 'last_mount_time_utc'): "super_value",
    ('ext2', 'last_mounted_on'): "super_value",
    ('ext2', 'last_mounted_path'): "super_value",
    ('ext2', 'last_mounted_time'): "super_value",
    ('ext2', 'last_mounted_time_utc'): "super_value",
    ('ext2', 'last_write_time'): "super_value",
    ('ext2', 'last_write_time_utc'): "super_value",
    ('ext2', 'last_written_time'): "super_value",
    ('ext2', 'last_written_time_utc'): "super_value",
    ('ext2', 'magic'): "super_value",
    ('ext2', 'magic_u16_hex'): "super_value",
    ('ext2', 'max_mount_count'): "super_value",
    ('ext2', 'mkfs_time'): "super_value",
    ('ext2', 'mkfs_time_utc'): "super_value",
    ('ext2', 'modified_time_utc'): "super_value",
    ('ext2', 'modify_time'): "super_value",
    ('ext2', 'modify_time_utc'): "super_value",
    ('ext2', 'mount_count'): "super_value",
    ('ext2', 'mount_point'): "super_value",
    ('ext2', 'mount_time'): "super_value",
    ('ext2', 'mount_time_utc'): "super_value",
    ('ext2', 'os_type'): "super_value",
    ('ext2', 'partition_offset_bytes'): "super_value",
    ('ext2', 'revision'): "super_value",
    ('ext2', 'revision_level'): "super_value",
    ('ext2', 'size_bytes'): "super_value",
    ('ext2', 'state'): "super_value",
    ('ext2', 'superblock_magic'): "super_value",
    ('ext2', 'superblock_offset'): "super_value",
    ('ext2', 'total_blocks'): "super_value",
    ('ext2', 'type'): "super_value",
    ('ext2', 'volume_size_bytes'): "super_value",
    ('ext2', 'volume_uuid'): "super_value",
    ('ext2', 'write_time'): "super_value",
    ('ext2', 'write_time_utc'): "super_value",
    ('ext3', 'backup_time'): "super_value",
    ('ext3', 'backup_time_utc'): "super_value",
    ('ext3', 'blocks_count'): "super_value",
    ('ext3', 'blocks_per_group'): "super_value",
    ('ext3', 'blocksize'): "super_value",
    ('ext3', 'checked_time'): "super_value",
    ('ext3', 'checked_time_utc'): "super_value",
    ('ext3', 'created_time_utc'): "super_value",
    ('ext3', 'created_utc'): "super_value",
    ('ext3', 'creation_time_utc'): "super_value",
    ('ext3', 'creator_os'): "super_value",
    ('ext3', 'feature_compat_u32_hex'): "super_value",
    ('ext3', 'feature_incompat_u32_hex'): "super_value",
    ('ext3', 'feature_ro_compat_u32_hex'): "super_value",
    ('ext3', 'features'): "super_value",
    ('ext3', 'filesystem_created'): "super_value",
    ('ext3', 'filesystem_created_utc'): "super_value",
    ('ext3', 'filesystem_features'): "super_value",
    ('ext3', 'filesystem_revision'): "super_value",
    ('ext3', 'filesystem_size_bytes'): "super_value",
    ('ext3', 'filesystem_state'): "super_value",
    ('ext3', 'filesystem_type'): "super_value",
    ('ext3', 'first_data_block'): "super_value",
    ('ext3', 'free_blocks'): "super_value",
    ('ext3', 'free_blocks_count'): "super_value",
    ('ext3', 'free_inodes'): "super_value",
    ('ext3', 'free_inodes_count'): "super_value",
    ('ext3', 'fs_type'): "super_value",
    ('ext3', 'fs_uuid'): "super_value",
    ('ext3', 'has_extents'): "super_value",
    ('ext3', 'has_journal'): "super_value",
    ('ext3', 'inodes_per_group'): "super_value",
    ('ext3', 'is_64bit'): "super_value",
    ('ext3', 'journal_present'): "super_value",
    ('ext3', 'label'): "super_value",
    ('ext3', 'last_check_time'): "super_value",
    ('ext3', 'last_check_time_utc'): "super_value",
    ('ext3', 'last_checked'): "super_value",
    ('ext3', 'last_checked_utc'): "super_value",
    ('ext3', 'last_modified_time'): "super_value",
    ('ext3', 'last_modified_time_utc'): "super_value",
    ('ext3', 'last_mount_path'): "super_value",
    ('ext3', 'last_mount_time'): "super_value",
    ('ext3', 'last_mount_time_utc'): "super_value",
    ('ext3', 'last_mounted_on'): "super_value",
    ('ext3', 'last_mounted_path'): "super_value",
    ('ext3', 'last_mounted_time'): "super_value",
    ('ext3', 'last_mounted_time_utc'): "super_value",
    ('ext3', 'last_write_time'): "super_value",
    ('ext3', 'last_write_time_utc'): "super_value",
    ('ext3', 'last_written_time'): "super_value",
    ('ext3', 'last_written_time_utc'): "super_value",
    ('ext3', 'magic'): "super_value",
    ('ext3', 'magic_u16_hex'): "super_value",
    ('ext3', 'max_mount_count'): "super_value",
    ('ext3', 'mkfs_time'): "super_value",
    ('ext3', 'mkfs_time_utc'): "super_value",
    ('ext3', 'modified_time_utc'): "super_value",
    ('ext3', 'modify_time'): "super_value",
    ('ext3', 'modify_time_utc'): "super_value",
    ('ext3', 'mount_count'): "super_value",
    ('ext3', 'mount_point'): "super_value",
    ('ext3', 'mount_time'): "super_value",
    ('ext3', 'mount_time_utc'): "super_value",
    ('ext3', 'os_type'): "super_value",
    ('ext3', 'partition_offset_bytes'): "super_value",
    ('ext3', 'revision'): "super_value",
    ('ext3', 'revision_level'): "super_value",
    ('ext3', 'size_bytes'): "super_value",
    ('ext3', 'state'): "super_value",
    ('ext3', 'superblock_magic'): "super_value",
    ('ext3', 'superblock_offset'): "super_value",
    ('ext3', 'total_blocks'): "super_value",
    ('ext3', 'type'): "super_value",
    ('ext3', 'volume_size_bytes'): "super_value",
    ('ext3', 'volume_uuid'): "super_value",
    ('ext3', 'write_time'): "super_value",
    ('ext3', 'write_time_utc'): "super_value",
    ('ext4', 'backup_time'): "super_value",
    ('ext4', 'backup_time_utc'): "super_value",
    ('ext4', 'blocks_count'): "super_value",
    ('ext4', 'blocks_per_group'): "super_value",
    ('ext4', 'blocksize'): "super_value",
    ('ext4', 'checked_time'): "super_value",
    ('ext4', 'checked_time_utc'): "super_value",
    ('ext4', 'created_time_utc'): "super_value",
    ('ext4', 'created_utc'): "super_value",
    ('ext4', 'creation_time_utc'): "super_value",
    ('ext4', 'creator_os'): "super_value",
    ('ext4', 'feature_compat_u32_hex'): "super_value",
    ('ext4', 'feature_incompat_u32_hex'): "super_value",
    ('ext4', 'feature_ro_compat_u32_hex'): "super_value",
    ('ext4', 'features'): "super_value",
    ('ext4', 'filesystem_created'): "super_value",
    ('ext4', 'filesystem_created_utc'): "super_value",
    ('ext4', 'filesystem_features'): "super_value",
    ('ext4', 'filesystem_revision'): "super_value",
    ('ext4', 'filesystem_size_bytes'): "super_value",
    ('ext4', 'filesystem_state'): "super_value",
    ('ext4', 'filesystem_type'): "super_value",
    ('ext4', 'first_data_block'): "super_value",
    ('ext4', 'free_blocks'): "super_value",
    ('ext4', 'free_blocks_count'): "super_value",
    ('ext4', 'free_inodes'): "super_value",
    ('ext4', 'free_inodes_count'): "super_value",
    ('ext4', 'fs_type'): "super_value",
    ('ext4', 'fs_uuid'): "super_value",
    ('ext4', 'has_extents'): "super_value",
    ('ext4', 'has_journal'): "super_value",
    ('ext4', 'inodes_per_group'): "super_value",
    ('ext4', 'is_64bit'): "super_value",
    ('ext4', 'journal_present'): "super_value",
    ('ext4', 'label'): "super_value",
    ('ext4', 'last_check_time'): "super_value",
    ('ext4', 'last_check_time_utc'): "super_value",
    ('ext4', 'last_checked'): "super_value",
    ('ext4', 'last_checked_utc'): "super_value",
    ('ext4', 'last_modified_time'): "super_value",
    ('ext4', 'last_modified_time_utc'): "super_value",
    ('ext4', 'last_mount_path'): "super_value",
    ('ext4', 'last_mount_time'): "super_value",
    ('ext4', 'last_mount_time_utc'): "super_value",
    ('ext4', 'last_mounted_on'): "super_value",
    ('ext4', 'last_mounted_path'): "super_value",
    ('ext4', 'last_mounted_time'): "super_value",
    ('ext4', 'last_mounted_time_utc'): "super_value",
    ('ext4', 'last_write_time'): "super_value",
    ('ext4', 'last_write_time_utc'): "super_value",
    ('ext4', 'last_written_time'): "super_value",
    ('ext4', 'last_written_time_utc'): "super_value",
    ('ext4', 'magic'): "super_value",
    ('ext4', 'magic_u16_hex'): "super_value",
    ('ext4', 'max_mount_count'): "super_value",
    ('ext4', 'mkfs_time'): "super_value",
    ('ext4', 'mkfs_time_utc'): "super_value",
    ('ext4', 'modified_time_utc'): "super_value",
    ('ext4', 'modify_time'): "super_value",
    ('ext4', 'modify_time_utc'): "super_value",
    ('ext4', 'mount_count'): "super_value",
    ('ext4', 'mount_point'): "super_value",
    ('ext4', 'mount_time'): "super_value",
    ('ext4', 'mount_time_utc'): "super_value",
    ('ext4', 'os_type'): "super_value",
    ('ext4', 'partition_offset_bytes'): "super_value",
    ('ext4', 'revision'): "super_value",
    ('ext4', 'revision_level'): "super_value",
    ('ext4', 'size_bytes'): "super_value",
    ('ext4', 'state'): "super_value",
    ('ext4', 'superblock_magic'): "super_value",
    ('ext4', 'superblock_offset'): "super_value",
    ('ext4', 'total_blocks'): "super_value",
    ('ext4', 'type'): "super_value",
    ('ext4', 'volume_size_bytes'): "super_value",
    ('ext4', 'volume_uuid'): "super_value",
    ('ext4', 'write_time'): "super_value",
    ('ext4', 'write_time_utc'): "super_value",
    ('filesystem', 'backup_date'): "super_value",
    ('filesystem', 'backup_date_utc'): "super_value",
    ('filesystem', 'backup_time'): "super_value",
    ('filesystem', 'backup_time_utc'): "super_value",
    ('filesystem', 'block_count'): "super_value",
    ('filesystem', 'block_size'): "super_value",
    ('filesystem', 'block_size_bytes'): "super_value",
    ('filesystem', 'blocks_count'): "super_value",
    ('filesystem', 'blocks_per_group'): "super_value",
    ('filesystem', 'blocksize'): "super_value",
    ('filesystem', 'bytes_used'): "super_value",
    ('filesystem', 'checked_date'): "super_value",
    ('filesystem', 'checked_date_utc'): "super_value",
    ('filesystem', 'checked_time'): "super_value",
    ('filesystem', 'checked_time_utc'): "super_value",
    ('filesystem', 'container_uuid'): "super_value",
    ('filesystem', 'create_date'): "super_value",
    ('filesystem', 'create_date_utc'): "super_value",
    ('filesystem', 'created_time_utc'): "super_value",
    ('filesystem', 'created_utc'): "super_value",
    ('filesystem', 'creation_time_utc'): "super_value",
    ('filesystem', 'creator_os'): "super_value",
    ('filesystem', 'data_blocks'): "super_value",
    ('filesystem', 'dblocks'): "super_value",
    ('filesystem', 'detected_filesystem_type'): "super_value",
    ('filesystem', 'dev_uuid'): "super_value",
    ('filesystem', 'device_count'): "super_value",
    ('filesystem', 'device_uuid'): "super_value",
    ('filesystem', 'fdblocks'): "super_value",
    ('filesystem', 'feature_compat_u32_hex'): "super_value",
    ('filesystem', 'feature_incompat_u32_hex'): "super_value",
    ('filesystem', 'feature_ro_compat_u32_hex'): "super_value",
    ('filesystem', 'features'): "super_value",
    ('filesystem', 'filesystem_created'): "super_value",
    ('filesystem', 'filesystem_created_utc'): "super_value",
    ('filesystem', 'filesystem_family'): "super_value",
    ('filesystem', 'filesystem_features'): "super_value",
    ('filesystem', 'filesystem_size_bytes'): "super_value",
    ('filesystem', 'filesystem_state'): "super_value",
    ('filesystem', 'filesystem_uuid'): "super_value",
    ('filesystem', 'finder_info_volume_id_u64_hex'): "super_value",
    ('filesystem', 'first_data_block'): "super_value",
    ('filesystem', 'fname'): "super_value",
    ('filesystem', 'folder_count'): "super_value",
    ('filesystem', 'free_blocks'): "super_value",
    ('filesystem', 'free_blocks_count'): "super_value",
    ('filesystem', 'free_inodes'): "super_value",
    ('filesystem', 'free_inodes_count'): "super_value",
    ('filesystem', 'fs_uuid'): "super_value",
    ('filesystem', 'fsid'): "super_value",
    ('filesystem', 'generation'): "super_value",
    ('filesystem', 'has_extents'): "super_value",
    ('filesystem', 'has_journal'): "super_value",
    ('filesystem', 'hfs_signature'): "super_value",
    ('filesystem', 'icount'): "super_value",
    ('filesystem', 'ifree'): "super_value",
    ('filesystem', 'inode_count'): "super_value",
    ('filesystem', 'inode_size'): "super_value",
    ('filesystem', 'inodes_per_group'): "super_value",
    ('filesystem', 'is_64bit'): "super_value",
    ('filesystem', 'journal_present'): "super_value",
    ('filesystem', 'last_check_time'): "super_value",
    ('filesystem', 'last_check_time_utc'): "super_value",
    ('filesystem', 'last_checked'): "super_value",
    ('filesystem', 'last_checked_time'): "super_value",
    ('filesystem', 'last_checked_time_utc'): "super_value",
    ('filesystem', 'last_checked_utc'): "super_value",
    ('filesystem', 'last_modified_time'): "super_value",
    ('filesystem', 'last_modified_time_utc'): "super_value",
    ('filesystem', 'last_mount_path'): "super_value",
    ('filesystem', 'last_mount_time'): "super_value",
    ('filesystem', 'last_mount_time_utc'): "super_value",
    ('filesystem', 'last_mounted_on'): "super_value",
    ('filesystem', 'last_mounted_path'): "super_value",
    ('filesystem', 'last_mounted_time'): "super_value",
    ('filesystem', 'last_mounted_time_utc'): "super_value",
    ('filesystem', 'last_write_time'): "super_value",
    ('filesystem', 'last_write_time_utc'): "super_value",
    ('filesystem', 'last_written_time'): "super_value",
    ('filesystem', 'last_written_time_utc'): "super_value",
    ('filesystem', 'magic'): "super_value",
    ('filesystem', 'magic_u16_hex'): "super_value",
    ('filesystem', 'magic_u32_hex'): "super_value",
    ('filesystem', 'max_file_systems'): "super_value",
    ('filesystem', 'max_mount_count'): "super_value",
    ('filesystem', 'mkfs_time'): "super_value",
    ('filesystem', 'mkfs_time_utc'): "super_value",
    ('filesystem', 'modified_time_utc'): "super_value",
    ('filesystem', 'modify_date'): "super_value",
    ('filesystem', 'modify_date_utc'): "super_value",
    ('filesystem', 'modify_time'): "super_value",
    ('filesystem', 'modify_time_utc'): "super_value",
    ('filesystem', 'mount_count'): "super_value",
    ('filesystem', 'mount_point'): "super_value",
    ('filesystem', 'mount_time'): "super_value",
    ('filesystem', 'mount_time_utc'): "super_value",
    ('filesystem', 'next_xid'): "super_value",
    ('filesystem', 'node_size'): "super_value",
    ('filesystem', 'nodesize'): "super_value",
    ('filesystem', 'num_devices'): "super_value",
    ('filesystem', 'nx_uuid'): "super_value",
    ('filesystem', 'os_type'): "super_value",
    ('filesystem', 'partition_offset_bytes'): "super_value",
    ('filesystem', 'rblocks'): "super_value",
    ('filesystem', 'revision_level'): "super_value",
    ('filesystem', 'sector_size'): "super_value",
    ('filesystem', 'sectorsize'): "super_value",
    ('filesystem', 'sectsize'): "super_value",
    ('filesystem', 'signature'): "super_value",
    ('filesystem', 'size_bytes'): "super_value",
    ('filesystem', 'state'): "super_value",
    ('filesystem', 'superblock_magic'): "super_value",
    ('filesystem', 'superblock_offset'): "super_value",
    ('filesystem', 'superblock_type'): "super_value",
    ('filesystem', 'total_blocks'): "super_value",
    ('filesystem', 'total_bytes'): "super_value",
    ('filesystem', 'type'): "super_value",
    ('filesystem', 'uuid'): "super_value",
    ('filesystem', 'version'): "super_value",
    ('filesystem', 'volume_id_hex'): "super_value",
    ('filesystem', 'volume_name'): "super_value",
    ('filesystem', 'volume_uuid'): "super_value",
    ('filesystem', 'write_time'): "super_value",
    ('filesystem', 'write_time_utc'): "super_value",
    ('hfs', 'backup_date'): "super_value",
    ('hfs', 'backup_date_utc'): "super_value",
    ('hfs', 'backup_time'): "super_value",
    ('hfs', 'backup_time_utc'): "super_value",
    ('hfs', 'block_count'): "super_value",
    ('hfs', 'block_size'): "super_value",
    ('hfs', 'block_size_bytes'): "super_value",
    ('hfs', 'blocks_count'): "super_value",
    ('hfs', 'blocksize'): "super_value",
    ('hfs', 'checked_date'): "super_value",
    ('hfs', 'checked_date_utc'): "super_value",
    ('hfs', 'checked_time'): "super_value",
    ('hfs', 'checked_time_utc'): "super_value",
    ('hfs', 'create_date'): "super_value",
    ('hfs', 'create_date_utc'): "super_value",
    ('hfs', 'created_time'): "super_value",
    ('hfs', 'created_time_utc'): "super_value",
    ('hfs', 'creation_time'): "super_value",
    ('hfs', 'creation_time_utc'): "super_value",
    ('hfs', 'file_count'): "super_value",
    ('hfs', 'filesystem_size_bytes'): "super_value",
    ('hfs', 'filesystem_type'): "super_value",
    ('hfs', 'filesystem_uuid'): "super_value",
    ('hfs', 'finder_info_volume_id_u64_hex'): "super_value",
    ('hfs', 'folder_count'): "super_value",
    ('hfs', 'free_blocks'): "super_value",
    ('hfs', 'fs_type'): "super_value",
    ('hfs', 'fs_uuid'): "super_value",
    ('hfs', 'hfs_signature'): "super_value",
    ('hfs', 'label'): "super_value",
    ('hfs', 'last_checked_time'): "super_value",
    ('hfs', 'last_checked_time_utc'): "super_value",
    ('hfs', 'last_modified_time'): "super_value",
    ('hfs', 'last_modified_time_utc'): "super_value",
    ('hfs', 'magic'): "super_value",
    ('hfs', 'modified_time'): "super_value",
    ('hfs', 'modified_time_utc'): "super_value",
    ('hfs', 'modify_date'): "super_value",
    ('hfs', 'modify_date_utc'): "super_value",
    ('hfs', 'partition_offset_bytes'): "super_value",
    ('hfs', 'signature'): "super_value",
    ('hfs', 'size_bytes'): "super_value",
    ('hfs', 'superblock_magic'): "super_value",
    ('hfs', 'superblock_offset'): "super_value",
    ('hfs', 'total_blocks'): "super_value",
    ('hfs', 'type'): "super_value",
    ('hfs', 'uuid'): "super_value",
    ('hfs', 'version'): "super_value",
    ('hfs', 'volume_id_hex'): "super_value",
    ('hfs', 'volume_label'): "super_value",
    ('hfs', 'volume_name'): "super_value",
    ('hfs', 'volume_size_bytes'): "super_value",
    ('hfs', 'volume_uuid'): "super_value",
    ('hfsplus', 'backup_date'): "super_value",
    ('hfsplus', 'backup_date_utc'): "super_value",
    ('hfsplus', 'backup_time'): "super_value",
    ('hfsplus', 'backup_time_utc'): "super_value",
    ('hfsplus', 'block_count'): "super_value",
    ('hfsplus', 'block_size'): "super_value",
    ('hfsplus', 'block_size_bytes'): "super_value",
    ('hfsplus', 'blocks_count'): "super_value",
    ('hfsplus', 'blocksize'): "super_value",
    ('hfsplus', 'checked_date'): "super_value",
    ('hfsplus', 'checked_date_utc'): "super_value",
    ('hfsplus', 'checked_time'): "super_value",
    ('hfsplus', 'checked_time_utc'): "super_value",
    ('hfsplus', 'create_date'): "super_value",
    ('hfsplus', 'create_date_utc'): "super_value",
    ('hfsplus', 'created_time'): "super_value",
    ('hfsplus', 'created_time_utc'): "super_value",
    ('hfsplus', 'creation_time'): "super_value",
    ('hfsplus', 'creation_time_utc'): "super_value",
    ('hfsplus', 'file_count'): "super_value",
    ('hfsplus', 'filesystem_size_bytes'): "super_value",
    ('hfsplus', 'filesystem_type'): "super_value",
    ('hfsplus', 'filesystem_uuid'): "super_value",
    ('hfsplus', 'finder_info_volume_id_u64_hex'): "super_value",
    ('hfsplus', 'folder_count'): "super_value",
    ('hfsplus', 'free_blocks'): "super_value",
    ('hfsplus', 'fs_type'): "super_value",
    ('hfsplus', 'fs_uuid'): "super_value",
    ('hfsplus', 'hfs_signature'): "super_value",
    ('hfsplus', 'label'): "super_value",
    ('hfsplus', 'last_checked_time'): "super_value",
    ('hfsplus', 'last_checked_time_utc'): "super_value",
    ('hfsplus', 'last_modified_time'): "super_value",
    ('hfsplus', 'last_modified_time_utc'): "super_value",
    ('hfsplus', 'magic'): "super_value",
    ('hfsplus', 'modified_time'): "super_value",
    ('hfsplus', 'modified_time_utc'): "super_value",
    ('hfsplus', 'modify_date'): "super_value",
    ('hfsplus', 'modify_date_utc'): "super_value",
    ('hfsplus', 'partition_offset_bytes'): "super_value",
    ('hfsplus', 'signature'): "super_value",
    ('hfsplus', 'size_bytes'): "super_value",
    ('hfsplus', 'superblock_magic'): "super_value",
    ('hfsplus', 'superblock_offset'): "super_value",
    ('hfsplus', 'total_blocks'): "super_value",
    ('hfsplus', 'type'): "super_value",
    ('hfsplus', 'uuid'): "super_value",
    ('hfsplus', 'version'): "super_value",
    ('hfsplus', 'volume_id_hex'): "super_value",
    ('hfsplus', 'volume_label'): "super_value",
    ('hfsplus', 'volume_name'): "super_value",
    ('hfsplus', 'volume_size_bytes'): "super_value",
    ('hfsplus', 'volume_uuid'): "super_value",
    ('hfsx', 'backup_date'): "super_value",
    ('hfsx', 'backup_date_utc'): "super_value",
    ('hfsx', 'backup_time'): "super_value",
    ('hfsx', 'backup_time_utc'): "super_value",
    ('hfsx', 'block_count'): "super_value",
    ('hfsx', 'block_size'): "super_value",
    ('hfsx', 'block_size_bytes'): "super_value",
    ('hfsx', 'blocks_count'): "super_value",
    ('hfsx', 'blocksize'): "super_value",
    ('hfsx', 'checked_date'): "super_value",
    ('hfsx', 'checked_date_utc'): "super_value",
    ('hfsx', 'checked_time'): "super_value",
    ('hfsx', 'checked_time_utc'): "super_value",
    ('hfsx', 'create_date'): "super_value",
    ('hfsx', 'create_date_utc'): "super_value",
    ('hfsx', 'created_time'): "super_value",
    ('hfsx', 'created_time_utc'): "super_value",
    ('hfsx', 'creation_time'): "super_value",
    ('hfsx', 'creation_time_utc'): "super_value",
    ('hfsx', 'file_count'): "super_value",
    ('hfsx', 'filesystem_size_bytes'): "super_value",
    ('hfsx', 'filesystem_type'): "super_value",
    ('hfsx', 'filesystem_uuid'): "super_value",
    ('hfsx', 'finder_info_volume_id_u64_hex'): "super_value",
    ('hfsx', 'folder_count'): "super_value",
    ('hfsx', 'free_blocks'): "super_value",
    ('hfsx', 'fs_type'): "super_value",
    ('hfsx', 'fs_uuid'): "super_value",
    ('hfsx', 'hfs_signature'): "super_value",
    ('hfsx', 'label'): "super_value",
    ('hfsx', 'last_checked_time'): "super_value",
    ('hfsx', 'last_checked_time_utc'): "super_value",
    ('hfsx', 'last_modified_time'): "super_value",
    ('hfsx', 'last_modified_time_utc'): "super_value",
    ('hfsx', 'magic'): "super_value",
    ('hfsx', 'modified_time'): "super_value",
    ('hfsx', 'modified_time_utc'): "super_value",
    ('hfsx', 'modify_date'): "super_value",
    ('hfsx', 'modify_date_utc'): "super_value",
    ('hfsx', 'partition_offset_bytes'): "super_value",
    ('hfsx', 'signature'): "super_value",
    ('hfsx', 'size_bytes'): "super_value",
    ('hfsx', 'superblock_magic'): "super_value",
    ('hfsx', 'superblock_offset'): "super_value",
    ('hfsx', 'total_blocks'): "super_value",
    ('hfsx', 'type'): "super_value",
    ('hfsx', 'uuid'): "super_value",
    ('hfsx', 'version'): "super_value",
    ('hfsx', 'volume_id_hex'): "super_value",
    ('hfsx', 'volume_label'): "super_value",
    ('hfsx', 'volume_name'): "super_value",
    ('hfsx', 'volume_size_bytes'): "super_value",
    ('hfsx', 'volume_uuid'): "super_value",
    ('xfs', 'block_count'): "super_value",
    ('xfs', 'block_size'): "super_value",
    ('xfs', 'block_size_bytes'): "super_value",
    ('xfs', 'blocks_count'): "super_value",
    ('xfs', 'blocksize'): "super_value",
    ('xfs', 'data_blocks'): "super_value",
    ('xfs', 'dblocks'): "super_value",
    ('xfs', 'fdblocks'): "super_value",
    ('xfs', 'filesystem_size_bytes'): "super_value",
    ('xfs', 'filesystem_type'): "super_value",
    ('xfs', 'filesystem_uuid'): "super_value",
    ('xfs', 'fname'): "super_value",
    ('xfs', 'free_blocks'): "super_value",
    ('xfs', 'free_inodes'): "super_value",
    ('xfs', 'fs_type'): "super_value",
    ('xfs', 'fs_uuid'): "super_value",
    ('xfs', 'icount'): "super_value",
    ('xfs', 'ifree'): "super_value",
    ('xfs', 'inode_count'): "super_value",
    ('xfs', 'inode_size'): "super_value",
    ('xfs', 'label'): "super_value",
    ('xfs', 'magic'): "super_value",
    ('xfs', 'magic_u32_hex'): "super_value",
    ('xfs', 'partition_offset_bytes'): "super_value",
    ('xfs', 'rblocks'): "super_value",
    ('xfs', 'sector_size'): "super_value",
    ('xfs', 'sectsize'): "super_value",
    ('xfs', 'size_bytes'): "super_value",
    ('xfs', 'superblock_magic'): "super_value",
    ('xfs', 'superblock_offset'): "super_value",
    ('xfs', 'total_blocks'): "super_value",
    ('xfs', 'type'): "super_value",
    ('xfs', 'uuid'): "super_value",
    ('xfs', 'version'): "super_value",
    ('xfs', 'volume_label'): "super_value",
    ('xfs', 'volume_name'): "super_value",
    ('xfs', 'volume_size_bytes'): "super_value",
    ('xfs', 'volume_uuid'): "super_value",
}

_EXT_COMPAT = ["dir_prealloc", "imagic_inodes", "has_journal", "ext_attr", "resize_inode", "dir_index",
               "lazy_bg", "exclude_inode", "exclude_bitmap", "sparse_super2", "fast_commit", "stable_inodes",
               "orphan_file"]
_EXT_INCOMPAT = ["compression", "filetype", "needs_recovery", "journal_dev", "meta_bg", None, "extent", "64bit",
                 "mmp", "flex_bg", "ea_inode", None, "dirdata", "metadata_csum_seed", "large_dir", "inline_data",
                 "encrypt", "casefold"]
_EXT_RO = ["sparse_super", "large_file", "btree_dir", "huge_file", "uninit_bg", "dir_nlink", "extra_isize",
           "has_snapshot", "quota", "bigalloc", "metadata_csum", "replica", "read-only", "project", "shared_blocks",
           "verity", "orphan_present"]
_OS = {0: "Linux", 1: "Hurd", 2: "Masix", 3: "FreeBSD", 4: "Lites"}
_HFS_NS = bytes([0xb3, 0xe2, 0x0f, 0x39, 0xf2, 0x92, 0x11, 0xd6, 0x97, 0xa4, 0x00, 0x30, 0x65, 0x43, 0xec, 0xac])
_EPOCH1904 = datetime(1904, 1, 1, tzinfo=timezone.utc)


def _iso_unix(t):
    if not t:
        return "none"
    try:
        return datetime.fromtimestamp(t, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except (OverflowError, OSError, ValueError):
        return None


def _iso_1904(t):
    if not t:
        return "none"
    return (_EPOCH1904 + timedelta(seconds=t)).strftime("%Y-%m-%dT%H:%M:%SZ")


def _cstr(b):
    return bytes(b).split(b"\0", 1)[0].decode("utf-8", "replace").strip()


def _uuid(b):
    b = bytes(b)
    return "none" if not any(b) else str(uuid.UUID(bytes=b))


def _parse_ext(b, o):
    s = o + 1024
    if len(b) < s + 0x110 or b[s + 0x38:s + 0x3A] != b"\x53\xef":
        return None
    u32 = lambda x: struct.unpack_from("<I", b, s + x)[0]  # noqa: E731
    u16 = lambda x: struct.unpack_from("<H", b, s + x)[0]  # noqa: E731
    lbs = u32(0x18)
    if lbs > 16:
        return None
    compat, incompat, ro = u32(0x5C), u32(0x60), u32(0x64)
    bcount = u32(4)
    if incompat & 0x80 and len(b) >= s + 0x154:
        bcount |= u32(0x150) << 32
    if incompat & ~(0x2 | 0x4 | 0x8 | 0x10) or ro & ~(0x1 | 0x2 | 0x4):
        typ = "ext4"
    elif compat & 0x4:
        typ = "ext3"
    else:
        typ = "ext2"
    feats = [n for bits, names in ((compat, _EXT_COMPAT), (incompat, _EXT_INCOMPAT), (ro, _EXT_RO))
             for i, n in enumerate(names) if n and bits >> i & 1]
    st = u16(0x3A)
    state = ("clean" if st & 1 else "not clean") + (" with errors" if st & 2 else "")
    bsz = 1024 << lbs
    mx = struct.unpack_from("<h", b, s + 0x36)[0]
    t = {"created": _iso_unix(u32(0x108)), "mount": _iso_unix(u32(0x2C)), "write": _iso_unix(u32(0x30)),
         "check": _iso_unix(u32(0x40))}
    r = {"filesystem_type": typ, "volume_label": _cstr(b[s + 0x78:s + 0x88]) or "none", "uuid": _uuid(b[s + 0x68:s + 0x78]),
         "block_size": bsz, "block_count": bcount, "magic": Hex(0xEF53, 4), "superblock_offset": o + 1024,
         "filesystem_size_bytes": bcount * bsz, "last_mounted_path": _cstr(b[s + 0x88:s + 0xC8]) or "none",
         "free_blocks_count": u32(0x0C), "free_inodes_count": u32(0x10), "first_data_block": u32(0x14),
         "blocks_per_group": u32(0x20), "inodes_per_group": u32(0x28), "mount_count": u16(0x34),
         "max_mount_count": mx, "state": state, "revision": u32(0x4C), "creator_os": _OS.get(u32(0x48), "none"),
         "feature_compat_u32_hex": Hex(compat, 8), "feature_incompat_u32_hex": Hex(incompat, 8),
         "feature_ro_compat_u32_hex": Hex(ro, 8), "filesystem_features": feats, "has_journal": bool(compat & 4),
         "is_64bit": bool(incompat & 0x80), "has_extents": bool(incompat & 0x40), "inode_count": u32(0),
         "created_time": t["created"], "last_mount_time": t["mount"], "last_write_time": t["write"],
         "last_check_time": t["check"]}
    return r


def _parse_xfs(b, o):
    if len(b) < o + 152 or b[o:o + 4] != b"XFSB":
        return None
    be = lambda f, x: struct.unpack_from(">" + f, b, o + x)[0]  # noqa: E731
    bs, db = be("I", 4), be("Q", 8)
    return {"filesystem_type": "xfs", "volume_label": _cstr(b[o + 108:o + 120]) or "none",
            "uuid": _uuid(b[o + 32:o + 48]), "block_size": bs, "block_count": db, "dblocks": db,
            "rblocks": be("Q", 16), "sector_size": be("H", 102), "inode_size": be("H", 104), "icount": be("Q", 128),
            "ifree": be("Q", 136), "fdblocks": be("Q", 144), "version": be("H", 100) & 0xF,
            "magic": "XFSB", "magic_u32_hex": Hex(0x58465342, 8), "superblock_offset": o,
            "filesystem_size_bytes": bs * db}


def _parse_btrfs(b, o):
    s = o + 0x10000
    if len(b) < s + 0x22B or b[s + 0x40:s + 0x48] != b"_BHRfS_M":
        return None
    le = lambda f, x: struct.unpack_from("<" + f, b, s + x)[0]  # noqa: E731
    ss, tot = le("I", 0x90), le("Q", 0x70)
    return {"filesystem_type": "btrfs", "volume_label": _cstr(b[s + 0x12B:s + 0x22B]) or "none",
            "uuid": _uuid(b[s + 0x20:s + 0x30]), "block_size": ss, "block_count": tot // ss if ss else None,
            "generation": le("Q", 0x48), "total_bytes": tot, "bytes_used": le("Q", 0x78),
            "num_devices": le("Q", 0x88), "sectorsize": ss, "nodesize": le("I", 0x94),
            "dev_uuid": _uuid(b[s + 0xC9 + 0x42:s + 0xC9 + 0x52]) if len(b) >= s + 0x11B else None,
            "magic": "_BHRfS_M", "superblock_offset": o + 0x10000, "filesystem_size_bytes": tot}


def _parse_hfs(b, o):
    s = o + 0x400
    if len(b) < s + 0x70 or b[s:s + 2] not in (b"H+", b"HX"):
        return None
    be = lambda x: struct.unpack_from(">I", b, s + x)[0]  # noqa: E731
    bs, tb = be(0x28), be(0x2C)
    vid = bytes(b[s + 0x68:s + 0x70])
    if any(vid):
        d = bytearray(hashlib.md5(_HFS_NS + vid).digest())
        d[6] = 0x30 | (d[6] & 0x0F)
        d[8] = 0x80 | (d[8] & 0x3F)
        hu = str(uuid.UUID(bytes=bytes(d)))
    else:
        hu = "none"
    return {"filesystem_type": "hfsplus", "hfs_signature": b[s:s + 2].decode(), "version": struct.unpack_from(
                ">H", b, s + 2)[0], "uuid": hu, "volume_id_hex": Hex(int.from_bytes(vid, "big"), 16),
            "block_size": bs, "block_count": tb, "free_blocks": be(0x30), "file_count": be(0x20),
            "folder_count": be(0x24), "created_time": _iso_1904(be(0x10)), "modify_date": _iso_1904(be(0x14)),
            "backup_date": _iso_1904(be(0x18)), "checked_date": _iso_1904(be(0x1C)),
            "magic": b[s:s + 2].decode(), "superblock_offset": o + 0x400, "filesystem_size_bytes": bs * tb,
            "volume_label": None}


def _parse_apfs(b, o):
    if len(b) < o + 184 or b[o + 32:o + 36] != b"NXSB":
        return None
    le = lambda f, x: struct.unpack_from("<" + f, b, o + x)[0]  # noqa: E731
    bs, bc = le("I", 36), le("Q", 40)
    return {"filesystem_type": "apfs", "uuid": _uuid(b[o + 72:o + 88]), "block_size": bs, "block_count": bc,
            "next_xid": le("Q", 96), "max_file_systems": le("I", 180), "magic": "NXSB", "superblock_offset": o + 32,
            "filesystem_size_bytes": bs * bc, "volume_label": None}


_PARSERS = {"ext": _parse_ext, "xfs": _parse_xfs, "btrfs": _parse_btrfs, "hfs": _parse_hfs, "apfs": _parse_apfs}
_FAMILY = {"ext": "ext", "ext2": "ext", "ext3": "ext", "ext4": "ext", "xfs": "xfs", "btrfs": "btrfs", "hfs": "hfs",
           "hfsplus": "hfs", "hfsx": "hfs", "apfs": "apfs"}


def _sane_bs(v):
    return isinstance(v, int) and 512 <= v <= 65536 and not v & (v - 1)


def _probe(b, o, fams):
    for f in fams:
        r = _PARSERS[f](b, o)
        if r is not None and _sane_bs(r.get("block_size")):
            r["partition_offset_bytes"] = o
            return r
    return None


def _partitions(b):
    """Byte offsets of the used partitions (table order) of an MBR or GPT image."""
    out = []
    for ss in (512, 4096):
        if b[ss:ss + 8] == b"EFI PART" and len(b) >= ss + 92:
            el, n, es = struct.unpack_from("<QII", b, ss + 72)
            if not 128 <= es <= 4096:
                continue
            for i in range(min(n, 256)):
                e = el * ss + i * es
                if e + 48 > len(b):
                    break
                if any(b[e:e + 16]):
                    out.append(struct.unpack_from("<Q", b, e + 32)[0] * ss)
            return out
    if len(b) >= 512 and b[510:512] == b"\x55\xaa":
        for i in range(4):
            e = 0x1BE + 16 * i
            if b[e] not in (0, 0x80):
                return []
            if b[e + 4] and b[e + 4] not in (0x05, 0x0F, 0x85, 0xEE):
                out.append(struct.unpack_from("<I", b, e + 8)[0] * 512)
    return out


def _superblock(data, fmt, question):
    fams = [_FAMILY[fmt]] if fmt in _FAMILY else list(_PARSERS)
    r = _probe(data, 0, fams)
    if r is not None:
        return r
    parts = _partitions(data)
    m = re.search(r"partition\s*(?:#|number|index)?\s*(\d+)", question or "", re.I)
    if m and parts:
        n = int(m.group(1))
        return _probe(data, parts[n - 1], fams) if 1 <= n <= len(parts) else None
    for off in parts:
        r = _probe(data, off, fams)
        if r is not None:
            return r
    return None


_ALIAS = {"fs_type": "filesystem_type", "type": "filesystem_type", "detected_filesystem_type": "filesystem_type",
          "superblock_type": "filesystem_type", "volume_name": "volume_label", "label": "volume_label",
          "fname": "volume_label", "filesystem_uuid": "uuid", "fs_uuid": "uuid", "volume_uuid": "uuid",
          "fsid": "uuid", "container_uuid": "uuid", "nx_uuid": "uuid", "block_size_bytes": "block_size",
          "blocksize": "block_size", "total_blocks": "block_count", "blocks_count": "block_count",
          "superblock_magic": "magic", "size_bytes": "filesystem_size_bytes",
          "volume_size_bytes": "filesystem_size_bytes", "last_mounted_on": "last_mounted_path",
          "last_mount_path": "last_mounted_path", "mount_point": "last_mounted_path",
          "free_blocks": "free_blocks_count", "free_inodes": "free_inodes_count", "filesystem_state": "state",
          "revision_level": "revision", "filesystem_revision": "revision", "os_type": "creator_os",
          "features": "filesystem_features", "journal_present": "has_journal", "magic_u16_hex": "magic",
          "data_blocks": "dblocks", "sectsize": "sector_size", "inode_count": "inode_count",
          "device_count": "num_devices", "sector_size": "sector_size", "node_size": "nodesize",
          "device_uuid": "dev_uuid", "signature": "hfs_signature", "volume_id_hex": "volume_id_hex",
          "finder_info_volume_id_u64_hex": "volume_id_hex", "filesystem_family": "family",
          "creation_time": "created_time", "mkfs_time": "created_time", "filesystem_created": "created_time",
          "created": "created_time", "create_date": "created_time", "mount_time": "last_mount_time",
          "last_mounted_time": "last_mount_time", "write_time": "last_write_time",
          "last_written_time": "last_write_time", "last_checked": "last_check_time", "checked_time": "checked_date",
          "last_checked_time": "checked_date", "modify_time": "modify_date", "modified_time": "modify_date",
          "last_modified_time": "modify_date", "backup_time": "backup_date"}


def super_value(data, ctx):
    """<fs>.<field>: one superblock value (see module doc), "none" when absent / not that filesystem."""
    if data is None:
        return None
    try:
        fmt = (ctx.get("fmt") or "").lower()
        field = ctx.get("field") or ""
        if field.endswith("_utc"):
            field = field[:-4]
        q = ctx.get("question")
        q = str((q.get("question") if isinstance(q, dict) else q) or "")
        r = _superblock(bytes(data), fmt, q)
        if r is None:
            return "none"
        if field == "magic_u32_hex" and r["filesystem_type"] != "xfs":
            return "none"
        if field == "magic_u16_hex" and not r["filesystem_type"].startswith("ext"):
            return "none"
        key = _ALIAS.get(field, field)
        if key == "family":
            return _FAMILY.get(r["filesystem_type"], r["filesystem_type"])
        if r["filesystem_type"] == "hfsplus" and key == "last_check_time":
            key = "checked_date"
        if key == "sector_size" and "sector_size" not in r:
            key = "sectorsize"
        v = r.get(key)
        return "none" if v is None and key not in ("volume_label",) else ("none" if v is None else v)
    except Exception:  # noqa: BLE001 -- defensive: never raise past the extractor
        return None
