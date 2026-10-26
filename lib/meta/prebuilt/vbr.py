"""Disk / filesystem boot structures (prebuilt, SPECULATIVE -- never GM-asked yet): NTFS $Boot VBR, FAT12/16/32 and
exFAT VBRs, the MBR partition table and the GPT header + entry array.

Input = a carved boot sector ($Boot / a 512 B VBR) OR a raw disk image (.img/.dd/.raw/.001) starting with an MBR: the
filesystem fmts (ntfs / fat / exfat / vbr / boot_sector / filesystem) follow the table to the FIRST partition's VBR
(MBR: first non-zero-type entry, lba_start*512; protective 0xEE -> GPT entry array, first used entry's first LBA).
NTFS (all little-endian): `NTFS    ` @3 + 0x55AA @0x1FE; bytes/sector u16 @0x0B, sectors/cluster u8 @0x0D (>=0x80 ->
2^(256-v)), media u8 @0x15, hidden sectors u32 @0x1C, total sectors u64 @0x28, $MFT LCN u64 @0x30, $MFTMirr LCN u64
@0x38, clusters/MFT record i8 @0x40 and /index record i8 @0x44 (negative -> 2^-v bytes, else v*cluster), serial u64
@0x48 (`0x%016x`; *_u32_hex = low 32 bits; *_dir_style = `XXXX-XXXX` upper as `dir`/`vol` print the low 32 bits).
FAT12/16: ext-boot-sig 0x29 @0x26, serial u32 @0x27, label 11 B @0x2B, type label @0x36; FAT32 (`FAT32   ` @0x52):
sig @0x42, serial @0x43, label @0x47. filesystem_type = FAT12/FAT16/FAT32 by CLUSTER COUNT (MS spec, like fsstat);
fs_type_label = the stored @0x36/@0x52 string. exFAT (`EXFAT   ` @3): partition offset u64 @0x40, volume length u64
@0x48, FAT offset/length u32 @0x50/@0x54, heap offset u32 @0x58, cluster count u32 @0x5C, root cluster u32 @0x60,
serial u32 @0x64, revision u16 @0x68 -> `major.minor02` ("1.00"), flags u16 @0x6A, shifts u8 @0x6C/@0x6D, FATs @0x6E,
%use @0x70; volume_label from the root directory's 0x83 entry when the image carries it.
MBR: 0x55AA @0x1FE, disk signature u32 @0x1B8, 4 entries @0x1BE x16 {status @0, type @4, lba u32 @8, count u32 @12};
partition_types = JSON list of `0x%02x` (non-zero types, table order); active_partition_index is 0-BASED (table slot);
partition_table_type "dos"/"gpt" as sfdisk names the label. GPT: `EFI PART` @LBA1 (512 B sectors, 4096 tried too):
revision u32 @+8 ("1.0" = 0x00010000), header size @+12, CRC @+16, LBAs @+24/+32/+40/+48, disk GUID @+56 (mixed-endian
-> lowercase canonical, *_upper as sgdisk prints it), entry LBA u64 @+72, count u32 @+80, size u32 @+84, array CRC
@+88; entries {type GUID, unique GUID, first/last LBA u64, attrs u64, name UTF-16LE 72 B}, unused = zero type GUID.
Wrong magic / truncated / field not in this filesystem -> "none"."""
import struct
import uuid

from ..spell import Guid, Hex

FIELDS = {
    ("ntfs", "oem_id"): "ntfs_value",
    ("ntfs", "oem_name"): "ntfs_value",
    ("ntfs", "filesystem_type"): "ntfs_value",
    ("ntfs", "fs_type"): "ntfs_value",
    ("ntfs", "file_system_type"): "ntfs_value",
    ("ntfs", "bytes_per_sector"): "ntfs_value",
    ("ntfs", "sectors_per_cluster"): "ntfs_value",
    ("ntfs", "cluster_size_bytes"): "ntfs_value",
    ("ntfs", "cluster_size"): "ntfs_value",
    ("ntfs", "bytes_per_cluster"): "ntfs_value",
    ("ntfs", "media_descriptor_u8_hex"): "ntfs_value",
    ("ntfs", "media_descriptor"): "ntfs_value",
    ("ntfs", "hidden_sectors"): "ntfs_value",
    ("ntfs", "sectors_per_track"): "ntfs_value",
    ("ntfs", "number_of_heads"): "ntfs_value",
    ("ntfs", "total_sectors"): "ntfs_value",
    ("ntfs", "number_of_sectors"): "ntfs_value",
    ("ntfs", "volume_size_bytes"): "ntfs_value",
    ("ntfs", "mft_cluster_number"): "ntfs_value",
    ("ntfs", "mft_lcn"): "ntfs_value",
    ("ntfs", "mft_start_cluster"): "ntfs_value",
    ("ntfs", "mft_cluster"): "ntfs_value",
    ("ntfs", "mft_start_lcn"): "ntfs_value",
    ("ntfs", "mft_offset_bytes"): "ntfs_value",
    ("ntfs", "mft_byte_offset"): "ntfs_value",
    ("ntfs", "mftmirr_cluster_number"): "ntfs_value",
    ("ntfs", "mft_mirror_cluster_number"): "ntfs_value",
    ("ntfs", "mftmirr_lcn"): "ntfs_value",
    ("ntfs", "mft_mirror_lcn"): "ntfs_value",
    ("ntfs", "clusters_per_mft_record"): "ntfs_value",
    ("ntfs", "mft_record_size_bytes"): "ntfs_value",
    ("ntfs", "mft_record_size"): "ntfs_value",
    ("ntfs", "mft_entry_size_bytes"): "ntfs_value",
    ("ntfs", "file_record_size_bytes"): "ntfs_value",
    ("ntfs", "clusters_per_index_record"): "ntfs_value",
    ("ntfs", "index_record_size_bytes"): "ntfs_value",
    ("ntfs", "index_record_size"): "ntfs_value",
    ("ntfs", "index_buffer_size_bytes"): "ntfs_value",
    ("ntfs", "volume_serial_number_u64_hex"): "ntfs_value",
    ("ntfs", "volume_serial_u64_hex"): "ntfs_value",
    ("ntfs", "volume_serial_number"): "ntfs_value",
    ("ntfs", "volume_serial"): "ntfs_value",
    ("ntfs", "volume_serial_number_hex"): "ntfs_value",
    ("ntfs", "volume_serial_u32_hex"): "ntfs_value",
    ("ntfs", "volume_serial_number_u32_hex"): "ntfs_value",
    ("ntfs", "volume_serial_dir_style"): "ntfs_value",
    ("ntfs", "volume_serial_number_dir_style"): "ntfs_value",
    ("ntfs", "volume_serial_dir"): "ntfs_value",
    ("ntfs", "checksum_u32_hex"): "ntfs_value",
    ("ntfs", "boot_signature_u16_hex"): "ntfs_value",
    ("ntfs", "end_of_sector_marker_u16_hex"): "ntfs_value",
    ("ntfs", "signature_u16_hex"): "ntfs_value",
    ("ntfs_boot", "oem_id"): "ntfs_value",
    ("ntfs_boot", "oem_name"): "ntfs_value",
    ("ntfs_boot", "filesystem_type"): "ntfs_value",
    ("ntfs_boot", "fs_type"): "ntfs_value",
    ("ntfs_boot", "file_system_type"): "ntfs_value",
    ("ntfs_boot", "bytes_per_sector"): "ntfs_value",
    ("ntfs_boot", "sectors_per_cluster"): "ntfs_value",
    ("ntfs_boot", "cluster_size_bytes"): "ntfs_value",
    ("ntfs_boot", "cluster_size"): "ntfs_value",
    ("ntfs_boot", "bytes_per_cluster"): "ntfs_value",
    ("ntfs_boot", "media_descriptor_u8_hex"): "ntfs_value",
    ("ntfs_boot", "media_descriptor"): "ntfs_value",
    ("ntfs_boot", "hidden_sectors"): "ntfs_value",
    ("ntfs_boot", "sectors_per_track"): "ntfs_value",
    ("ntfs_boot", "number_of_heads"): "ntfs_value",
    ("ntfs_boot", "total_sectors"): "ntfs_value",
    ("ntfs_boot", "number_of_sectors"): "ntfs_value",
    ("ntfs_boot", "volume_size_bytes"): "ntfs_value",
    ("ntfs_boot", "mft_cluster_number"): "ntfs_value",
    ("ntfs_boot", "mft_lcn"): "ntfs_value",
    ("ntfs_boot", "mft_start_cluster"): "ntfs_value",
    ("ntfs_boot", "mft_cluster"): "ntfs_value",
    ("ntfs_boot", "mft_start_lcn"): "ntfs_value",
    ("ntfs_boot", "mft_offset_bytes"): "ntfs_value",
    ("ntfs_boot", "mft_byte_offset"): "ntfs_value",
    ("ntfs_boot", "mftmirr_cluster_number"): "ntfs_value",
    ("ntfs_boot", "mft_mirror_cluster_number"): "ntfs_value",
    ("ntfs_boot", "mftmirr_lcn"): "ntfs_value",
    ("ntfs_boot", "mft_mirror_lcn"): "ntfs_value",
    ("ntfs_boot", "clusters_per_mft_record"): "ntfs_value",
    ("ntfs_boot", "mft_record_size_bytes"): "ntfs_value",
    ("ntfs_boot", "mft_record_size"): "ntfs_value",
    ("ntfs_boot", "mft_entry_size_bytes"): "ntfs_value",
    ("ntfs_boot", "file_record_size_bytes"): "ntfs_value",
    ("ntfs_boot", "clusters_per_index_record"): "ntfs_value",
    ("ntfs_boot", "index_record_size_bytes"): "ntfs_value",
    ("ntfs_boot", "index_record_size"): "ntfs_value",
    ("ntfs_boot", "index_buffer_size_bytes"): "ntfs_value",
    ("ntfs_boot", "volume_serial_number_u64_hex"): "ntfs_value",
    ("ntfs_boot", "volume_serial_u64_hex"): "ntfs_value",
    ("ntfs_boot", "volume_serial_number"): "ntfs_value",
    ("ntfs_boot", "volume_serial"): "ntfs_value",
    ("ntfs_boot", "volume_serial_number_hex"): "ntfs_value",
    ("ntfs_boot", "volume_serial_u32_hex"): "ntfs_value",
    ("ntfs_boot", "volume_serial_number_u32_hex"): "ntfs_value",
    ("ntfs_boot", "volume_serial_dir_style"): "ntfs_value",
    ("ntfs_boot", "volume_serial_number_dir_style"): "ntfs_value",
    ("ntfs_boot", "volume_serial_dir"): "ntfs_value",
    ("ntfs_boot", "checksum_u32_hex"): "ntfs_value",
    ("ntfs_boot", "boot_signature_u16_hex"): "ntfs_value",
    ("ntfs_boot", "end_of_sector_marker_u16_hex"): "ntfs_value",
    ("ntfs_boot", "signature_u16_hex"): "ntfs_value",
    ("fat", "oem_id"): "fat_value",
    ("fat", "oem_name"): "fat_value",
    ("fat", "filesystem_type"): "fat_value",
    ("fat", "fs_type"): "fat_value",
    ("fat", "file_system_type"): "fat_value",
    ("fat", "fs_type_label"): "fat_value",
    ("fat", "file_system_type_label"): "fat_value",
    ("fat", "filesystem_type_label"): "fat_value",
    ("fat", "bs_fil_sys_type"): "fat_value",
    ("fat", "bytes_per_sector"): "fat_value",
    ("fat", "sectors_per_cluster"): "fat_value",
    ("fat", "cluster_size_bytes"): "fat_value",
    ("fat", "cluster_size"): "fat_value",
    ("fat", "bytes_per_cluster"): "fat_value",
    ("fat", "reserved_sectors"): "fat_value",
    ("fat", "reserved_sector_count"): "fat_value",
    ("fat", "number_of_fats"): "fat_value",
    ("fat", "num_fats"): "fat_value",
    ("fat", "fat_count"): "fat_value",
    ("fat", "root_entry_count"): "fat_value",
    ("fat", "root_dir_entries"): "fat_value",
    ("fat", "max_root_entries"): "fat_value",
    ("fat", "total_sectors"): "fat_value",
    ("fat", "number_of_sectors"): "fat_value",
    ("fat", "volume_size_bytes"): "fat_value",
    ("fat", "media_descriptor_u8_hex"): "fat_value",
    ("fat", "media_descriptor"): "fat_value",
    ("fat", "sectors_per_fat"): "fat_value",
    ("fat", "fat_size_sectors"): "fat_value",
    ("fat", "hidden_sectors"): "fat_value",
    ("fat", "sectors_per_track"): "fat_value",
    ("fat", "number_of_heads"): "fat_value",
    ("fat", "volume_serial_number_u32_hex"): "fat_value",
    ("fat", "volume_serial_u32_hex"): "fat_value",
    ("fat", "volume_id_u32_hex"): "fat_value",
    ("fat", "volume_serial_number"): "fat_value",
    ("fat", "volume_serial"): "fat_value",
    ("fat", "volume_id"): "fat_value",
    ("fat", "volume_serial_number_hex"): "fat_value",
    ("fat", "volume_serial_dir_style"): "fat_value",
    ("fat", "volume_serial_number_dir_style"): "fat_value",
    ("fat", "volume_serial_dir"): "fat_value",
    ("fat", "volume_label"): "fat_value",
    ("fat", "label"): "fat_value",
    ("fat", "bs_vol_lab"): "fat_value",
    ("fat", "boot_sector_volume_label"): "fat_value",
    ("fat", "root_cluster"): "fat_value",
    ("fat", "root_directory_cluster"): "fat_value",
    ("fat", "root_dir_first_cluster"): "fat_value",
    ("fat", "fsinfo_sector"): "fat_value",
    ("fat", "backup_boot_sector"): "fat_value",
    ("fat", "drive_number_u8_hex"): "fat_value",
    ("fat", "cluster_count"): "fat_value",
    ("fat", "boot_signature_u16_hex"): "fat_value",
    ("fat", "end_of_sector_marker_u16_hex"): "fat_value",
    ("fat", "signature_u16_hex"): "fat_value",
    ("fat12", "oem_id"): "fat_value",
    ("fat12", "oem_name"): "fat_value",
    ("fat12", "filesystem_type"): "fat_value",
    ("fat12", "fs_type"): "fat_value",
    ("fat12", "file_system_type"): "fat_value",
    ("fat12", "fs_type_label"): "fat_value",
    ("fat12", "file_system_type_label"): "fat_value",
    ("fat12", "filesystem_type_label"): "fat_value",
    ("fat12", "bs_fil_sys_type"): "fat_value",
    ("fat12", "bytes_per_sector"): "fat_value",
    ("fat12", "sectors_per_cluster"): "fat_value",
    ("fat12", "cluster_size_bytes"): "fat_value",
    ("fat12", "cluster_size"): "fat_value",
    ("fat12", "bytes_per_cluster"): "fat_value",
    ("fat12", "reserved_sectors"): "fat_value",
    ("fat12", "reserved_sector_count"): "fat_value",
    ("fat12", "number_of_fats"): "fat_value",
    ("fat12", "num_fats"): "fat_value",
    ("fat12", "fat_count"): "fat_value",
    ("fat12", "root_entry_count"): "fat_value",
    ("fat12", "root_dir_entries"): "fat_value",
    ("fat12", "max_root_entries"): "fat_value",
    ("fat12", "total_sectors"): "fat_value",
    ("fat12", "number_of_sectors"): "fat_value",
    ("fat12", "volume_size_bytes"): "fat_value",
    ("fat12", "media_descriptor_u8_hex"): "fat_value",
    ("fat12", "media_descriptor"): "fat_value",
    ("fat12", "sectors_per_fat"): "fat_value",
    ("fat12", "fat_size_sectors"): "fat_value",
    ("fat12", "hidden_sectors"): "fat_value",
    ("fat12", "sectors_per_track"): "fat_value",
    ("fat12", "number_of_heads"): "fat_value",
    ("fat12", "volume_serial_number_u32_hex"): "fat_value",
    ("fat12", "volume_serial_u32_hex"): "fat_value",
    ("fat12", "volume_id_u32_hex"): "fat_value",
    ("fat12", "volume_serial_number"): "fat_value",
    ("fat12", "volume_serial"): "fat_value",
    ("fat12", "volume_id"): "fat_value",
    ("fat12", "volume_serial_number_hex"): "fat_value",
    ("fat12", "volume_serial_dir_style"): "fat_value",
    ("fat12", "volume_serial_number_dir_style"): "fat_value",
    ("fat12", "volume_serial_dir"): "fat_value",
    ("fat12", "volume_label"): "fat_value",
    ("fat12", "label"): "fat_value",
    ("fat12", "bs_vol_lab"): "fat_value",
    ("fat12", "boot_sector_volume_label"): "fat_value",
    ("fat12", "root_cluster"): "fat_value",
    ("fat12", "root_directory_cluster"): "fat_value",
    ("fat12", "root_dir_first_cluster"): "fat_value",
    ("fat12", "fsinfo_sector"): "fat_value",
    ("fat12", "backup_boot_sector"): "fat_value",
    ("fat12", "drive_number_u8_hex"): "fat_value",
    ("fat12", "cluster_count"): "fat_value",
    ("fat12", "boot_signature_u16_hex"): "fat_value",
    ("fat12", "end_of_sector_marker_u16_hex"): "fat_value",
    ("fat12", "signature_u16_hex"): "fat_value",
    ("fat16", "oem_id"): "fat_value",
    ("fat16", "oem_name"): "fat_value",
    ("fat16", "filesystem_type"): "fat_value",
    ("fat16", "fs_type"): "fat_value",
    ("fat16", "file_system_type"): "fat_value",
    ("fat16", "fs_type_label"): "fat_value",
    ("fat16", "file_system_type_label"): "fat_value",
    ("fat16", "filesystem_type_label"): "fat_value",
    ("fat16", "bs_fil_sys_type"): "fat_value",
    ("fat16", "bytes_per_sector"): "fat_value",
    ("fat16", "sectors_per_cluster"): "fat_value",
    ("fat16", "cluster_size_bytes"): "fat_value",
    ("fat16", "cluster_size"): "fat_value",
    ("fat16", "bytes_per_cluster"): "fat_value",
    ("fat16", "reserved_sectors"): "fat_value",
    ("fat16", "reserved_sector_count"): "fat_value",
    ("fat16", "number_of_fats"): "fat_value",
    ("fat16", "num_fats"): "fat_value",
    ("fat16", "fat_count"): "fat_value",
    ("fat16", "root_entry_count"): "fat_value",
    ("fat16", "root_dir_entries"): "fat_value",
    ("fat16", "max_root_entries"): "fat_value",
    ("fat16", "total_sectors"): "fat_value",
    ("fat16", "number_of_sectors"): "fat_value",
    ("fat16", "volume_size_bytes"): "fat_value",
    ("fat16", "media_descriptor_u8_hex"): "fat_value",
    ("fat16", "media_descriptor"): "fat_value",
    ("fat16", "sectors_per_fat"): "fat_value",
    ("fat16", "fat_size_sectors"): "fat_value",
    ("fat16", "hidden_sectors"): "fat_value",
    ("fat16", "sectors_per_track"): "fat_value",
    ("fat16", "number_of_heads"): "fat_value",
    ("fat16", "volume_serial_number_u32_hex"): "fat_value",
    ("fat16", "volume_serial_u32_hex"): "fat_value",
    ("fat16", "volume_id_u32_hex"): "fat_value",
    ("fat16", "volume_serial_number"): "fat_value",
    ("fat16", "volume_serial"): "fat_value",
    ("fat16", "volume_id"): "fat_value",
    ("fat16", "volume_serial_number_hex"): "fat_value",
    ("fat16", "volume_serial_dir_style"): "fat_value",
    ("fat16", "volume_serial_number_dir_style"): "fat_value",
    ("fat16", "volume_serial_dir"): "fat_value",
    ("fat16", "volume_label"): "fat_value",
    ("fat16", "label"): "fat_value",
    ("fat16", "bs_vol_lab"): "fat_value",
    ("fat16", "boot_sector_volume_label"): "fat_value",
    ("fat16", "root_cluster"): "fat_value",
    ("fat16", "root_directory_cluster"): "fat_value",
    ("fat16", "root_dir_first_cluster"): "fat_value",
    ("fat16", "fsinfo_sector"): "fat_value",
    ("fat16", "backup_boot_sector"): "fat_value",
    ("fat16", "drive_number_u8_hex"): "fat_value",
    ("fat16", "cluster_count"): "fat_value",
    ("fat16", "boot_signature_u16_hex"): "fat_value",
    ("fat16", "end_of_sector_marker_u16_hex"): "fat_value",
    ("fat16", "signature_u16_hex"): "fat_value",
    ("fat32", "oem_id"): "fat_value",
    ("fat32", "oem_name"): "fat_value",
    ("fat32", "filesystem_type"): "fat_value",
    ("fat32", "fs_type"): "fat_value",
    ("fat32", "file_system_type"): "fat_value",
    ("fat32", "fs_type_label"): "fat_value",
    ("fat32", "file_system_type_label"): "fat_value",
    ("fat32", "filesystem_type_label"): "fat_value",
    ("fat32", "bs_fil_sys_type"): "fat_value",
    ("fat32", "bytes_per_sector"): "fat_value",
    ("fat32", "sectors_per_cluster"): "fat_value",
    ("fat32", "cluster_size_bytes"): "fat_value",
    ("fat32", "cluster_size"): "fat_value",
    ("fat32", "bytes_per_cluster"): "fat_value",
    ("fat32", "reserved_sectors"): "fat_value",
    ("fat32", "reserved_sector_count"): "fat_value",
    ("fat32", "number_of_fats"): "fat_value",
    ("fat32", "num_fats"): "fat_value",
    ("fat32", "fat_count"): "fat_value",
    ("fat32", "root_entry_count"): "fat_value",
    ("fat32", "root_dir_entries"): "fat_value",
    ("fat32", "max_root_entries"): "fat_value",
    ("fat32", "total_sectors"): "fat_value",
    ("fat32", "number_of_sectors"): "fat_value",
    ("fat32", "volume_size_bytes"): "fat_value",
    ("fat32", "media_descriptor_u8_hex"): "fat_value",
    ("fat32", "media_descriptor"): "fat_value",
    ("fat32", "sectors_per_fat"): "fat_value",
    ("fat32", "fat_size_sectors"): "fat_value",
    ("fat32", "hidden_sectors"): "fat_value",
    ("fat32", "sectors_per_track"): "fat_value",
    ("fat32", "number_of_heads"): "fat_value",
    ("fat32", "volume_serial_number_u32_hex"): "fat_value",
    ("fat32", "volume_serial_u32_hex"): "fat_value",
    ("fat32", "volume_id_u32_hex"): "fat_value",
    ("fat32", "volume_serial_number"): "fat_value",
    ("fat32", "volume_serial"): "fat_value",
    ("fat32", "volume_id"): "fat_value",
    ("fat32", "volume_serial_number_hex"): "fat_value",
    ("fat32", "volume_serial_dir_style"): "fat_value",
    ("fat32", "volume_serial_number_dir_style"): "fat_value",
    ("fat32", "volume_serial_dir"): "fat_value",
    ("fat32", "volume_label"): "fat_value",
    ("fat32", "label"): "fat_value",
    ("fat32", "bs_vol_lab"): "fat_value",
    ("fat32", "boot_sector_volume_label"): "fat_value",
    ("fat32", "root_cluster"): "fat_value",
    ("fat32", "root_directory_cluster"): "fat_value",
    ("fat32", "root_dir_first_cluster"): "fat_value",
    ("fat32", "fsinfo_sector"): "fat_value",
    ("fat32", "backup_boot_sector"): "fat_value",
    ("fat32", "drive_number_u8_hex"): "fat_value",
    ("fat32", "cluster_count"): "fat_value",
    ("fat32", "boot_signature_u16_hex"): "fat_value",
    ("fat32", "end_of_sector_marker_u16_hex"): "fat_value",
    ("fat32", "signature_u16_hex"): "fat_value",
    ("vfat", "oem_id"): "fat_value",
    ("vfat", "oem_name"): "fat_value",
    ("vfat", "filesystem_type"): "fat_value",
    ("vfat", "fs_type"): "fat_value",
    ("vfat", "file_system_type"): "fat_value",
    ("vfat", "fs_type_label"): "fat_value",
    ("vfat", "file_system_type_label"): "fat_value",
    ("vfat", "filesystem_type_label"): "fat_value",
    ("vfat", "bs_fil_sys_type"): "fat_value",
    ("vfat", "bytes_per_sector"): "fat_value",
    ("vfat", "sectors_per_cluster"): "fat_value",
    ("vfat", "cluster_size_bytes"): "fat_value",
    ("vfat", "cluster_size"): "fat_value",
    ("vfat", "bytes_per_cluster"): "fat_value",
    ("vfat", "reserved_sectors"): "fat_value",
    ("vfat", "reserved_sector_count"): "fat_value",
    ("vfat", "number_of_fats"): "fat_value",
    ("vfat", "num_fats"): "fat_value",
    ("vfat", "fat_count"): "fat_value",
    ("vfat", "root_entry_count"): "fat_value",
    ("vfat", "root_dir_entries"): "fat_value",
    ("vfat", "max_root_entries"): "fat_value",
    ("vfat", "total_sectors"): "fat_value",
    ("vfat", "number_of_sectors"): "fat_value",
    ("vfat", "volume_size_bytes"): "fat_value",
    ("vfat", "media_descriptor_u8_hex"): "fat_value",
    ("vfat", "media_descriptor"): "fat_value",
    ("vfat", "sectors_per_fat"): "fat_value",
    ("vfat", "fat_size_sectors"): "fat_value",
    ("vfat", "hidden_sectors"): "fat_value",
    ("vfat", "sectors_per_track"): "fat_value",
    ("vfat", "number_of_heads"): "fat_value",
    ("vfat", "volume_serial_number_u32_hex"): "fat_value",
    ("vfat", "volume_serial_u32_hex"): "fat_value",
    ("vfat", "volume_id_u32_hex"): "fat_value",
    ("vfat", "volume_serial_number"): "fat_value",
    ("vfat", "volume_serial"): "fat_value",
    ("vfat", "volume_id"): "fat_value",
    ("vfat", "volume_serial_number_hex"): "fat_value",
    ("vfat", "volume_serial_dir_style"): "fat_value",
    ("vfat", "volume_serial_number_dir_style"): "fat_value",
    ("vfat", "volume_serial_dir"): "fat_value",
    ("vfat", "volume_label"): "fat_value",
    ("vfat", "label"): "fat_value",
    ("vfat", "bs_vol_lab"): "fat_value",
    ("vfat", "boot_sector_volume_label"): "fat_value",
    ("vfat", "root_cluster"): "fat_value",
    ("vfat", "root_directory_cluster"): "fat_value",
    ("vfat", "root_dir_first_cluster"): "fat_value",
    ("vfat", "fsinfo_sector"): "fat_value",
    ("vfat", "backup_boot_sector"): "fat_value",
    ("vfat", "drive_number_u8_hex"): "fat_value",
    ("vfat", "cluster_count"): "fat_value",
    ("vfat", "boot_signature_u16_hex"): "fat_value",
    ("vfat", "end_of_sector_marker_u16_hex"): "fat_value",
    ("vfat", "signature_u16_hex"): "fat_value",
    ("exfat", "oem_id"): "exfat_value",
    ("exfat", "oem_name"): "exfat_value",
    ("exfat", "filesystem_type"): "exfat_value",
    ("exfat", "fs_type"): "exfat_value",
    ("exfat", "file_system_type"): "exfat_value",
    ("exfat", "partition_offset"): "exfat_value",
    ("exfat", "partition_offset_sectors"): "exfat_value",
    ("exfat", "volume_length"): "exfat_value",
    ("exfat", "volume_length_sectors"): "exfat_value",
    ("exfat", "total_sectors"): "exfat_value",
    ("exfat", "number_of_sectors"): "exfat_value",
    ("exfat", "volume_size_bytes"): "exfat_value",
    ("exfat", "fat_offset"): "exfat_value",
    ("exfat", "fat_length"): "exfat_value",
    ("exfat", "cluster_heap_offset"): "exfat_value",
    ("exfat", "cluster_count"): "exfat_value",
    ("exfat", "first_cluster_of_root_directory"): "exfat_value",
    ("exfat", "root_directory_cluster"): "exfat_value",
    ("exfat", "root_cluster"): "exfat_value",
    ("exfat", "volume_serial_number_u32_hex"): "exfat_value",
    ("exfat", "volume_serial_u32_hex"): "exfat_value",
    ("exfat", "volume_serial_number"): "exfat_value",
    ("exfat", "volume_serial"): "exfat_value",
    ("exfat", "volume_serial_number_hex"): "exfat_value",
    ("exfat", "volume_serial_dir_style"): "exfat_value",
    ("exfat", "volume_serial_number_dir_style"): "exfat_value",
    ("exfat", "volume_serial_dir"): "exfat_value",
    ("exfat", "file_system_revision"): "exfat_value",
    ("exfat", "fs_revision"): "exfat_value",
    ("exfat", "filesystem_revision"): "exfat_value",
    ("exfat", "revision"): "exfat_value",
    ("exfat", "volume_flags_u16_hex"): "exfat_value",
    ("exfat", "bytes_per_sector_shift"): "exfat_value",
    ("exfat", "sectors_per_cluster_shift"): "exfat_value",
    ("exfat", "bytes_per_sector"): "exfat_value",
    ("exfat", "sectors_per_cluster"): "exfat_value",
    ("exfat", "cluster_size_bytes"): "exfat_value",
    ("exfat", "cluster_size"): "exfat_value",
    ("exfat", "bytes_per_cluster"): "exfat_value",
    ("exfat", "number_of_fats"): "exfat_value",
    ("exfat", "percent_in_use"): "exfat_value",
    ("exfat", "drive_select_u8_hex"): "exfat_value",
    ("exfat", "volume_label"): "exfat_value",
    ("exfat", "label"): "exfat_value",
    ("exfat", "boot_signature_u16_hex"): "exfat_value",
    ("exfat", "end_of_sector_marker_u16_hex"): "exfat_value",
    ("exfat", "signature_u16_hex"): "exfat_value",
    ("vbr", "oem_id"): "vbr_value",
    ("vbr", "oem_name"): "vbr_value",
    ("vbr", "filesystem_type"): "vbr_value",
    ("vbr", "fs_type"): "vbr_value",
    ("vbr", "file_system_type"): "vbr_value",
    ("vbr", "bytes_per_sector"): "vbr_value",
    ("vbr", "sectors_per_cluster"): "vbr_value",
    ("vbr", "cluster_size_bytes"): "vbr_value",
    ("vbr", "cluster_size"): "vbr_value",
    ("vbr", "bytes_per_cluster"): "vbr_value",
    ("vbr", "media_descriptor_u8_hex"): "vbr_value",
    ("vbr", "media_descriptor"): "vbr_value",
    ("vbr", "hidden_sectors"): "vbr_value",
    ("vbr", "sectors_per_track"): "vbr_value",
    ("vbr", "number_of_heads"): "vbr_value",
    ("vbr", "total_sectors"): "vbr_value",
    ("vbr", "number_of_sectors"): "vbr_value",
    ("vbr", "volume_size_bytes"): "vbr_value",
    ("vbr", "mft_cluster_number"): "vbr_value",
    ("vbr", "mft_lcn"): "vbr_value",
    ("vbr", "mft_start_cluster"): "vbr_value",
    ("vbr", "mft_cluster"): "vbr_value",
    ("vbr", "mft_start_lcn"): "vbr_value",
    ("vbr", "mft_offset_bytes"): "vbr_value",
    ("vbr", "mft_byte_offset"): "vbr_value",
    ("vbr", "mftmirr_cluster_number"): "vbr_value",
    ("vbr", "mft_mirror_cluster_number"): "vbr_value",
    ("vbr", "mftmirr_lcn"): "vbr_value",
    ("vbr", "mft_mirror_lcn"): "vbr_value",
    ("vbr", "clusters_per_mft_record"): "vbr_value",
    ("vbr", "mft_record_size_bytes"): "vbr_value",
    ("vbr", "mft_record_size"): "vbr_value",
    ("vbr", "mft_entry_size_bytes"): "vbr_value",
    ("vbr", "file_record_size_bytes"): "vbr_value",
    ("vbr", "clusters_per_index_record"): "vbr_value",
    ("vbr", "index_record_size_bytes"): "vbr_value",
    ("vbr", "index_record_size"): "vbr_value",
    ("vbr", "index_buffer_size_bytes"): "vbr_value",
    ("vbr", "volume_serial_number_u64_hex"): "vbr_value",
    ("vbr", "volume_serial_u64_hex"): "vbr_value",
    ("vbr", "volume_serial_number"): "vbr_value",
    ("vbr", "volume_serial"): "vbr_value",
    ("vbr", "volume_serial_number_hex"): "vbr_value",
    ("vbr", "volume_serial_u32_hex"): "vbr_value",
    ("vbr", "volume_serial_number_u32_hex"): "vbr_value",
    ("vbr", "volume_serial_dir_style"): "vbr_value",
    ("vbr", "volume_serial_number_dir_style"): "vbr_value",
    ("vbr", "volume_serial_dir"): "vbr_value",
    ("vbr", "checksum_u32_hex"): "vbr_value",
    ("vbr", "boot_signature_u16_hex"): "vbr_value",
    ("vbr", "end_of_sector_marker_u16_hex"): "vbr_value",
    ("vbr", "signature_u16_hex"): "vbr_value",
    ("vbr", "fs_type_label"): "vbr_value",
    ("vbr", "file_system_type_label"): "vbr_value",
    ("vbr", "filesystem_type_label"): "vbr_value",
    ("vbr", "bs_fil_sys_type"): "vbr_value",
    ("vbr", "reserved_sectors"): "vbr_value",
    ("vbr", "reserved_sector_count"): "vbr_value",
    ("vbr", "number_of_fats"): "vbr_value",
    ("vbr", "num_fats"): "vbr_value",
    ("vbr", "fat_count"): "vbr_value",
    ("vbr", "root_entry_count"): "vbr_value",
    ("vbr", "root_dir_entries"): "vbr_value",
    ("vbr", "max_root_entries"): "vbr_value",
    ("vbr", "sectors_per_fat"): "vbr_value",
    ("vbr", "fat_size_sectors"): "vbr_value",
    ("vbr", "volume_id_u32_hex"): "vbr_value",
    ("vbr", "volume_id"): "vbr_value",
    ("vbr", "volume_label"): "vbr_value",
    ("vbr", "label"): "vbr_value",
    ("vbr", "bs_vol_lab"): "vbr_value",
    ("vbr", "boot_sector_volume_label"): "vbr_value",
    ("vbr", "root_cluster"): "vbr_value",
    ("vbr", "root_directory_cluster"): "vbr_value",
    ("vbr", "root_dir_first_cluster"): "vbr_value",
    ("vbr", "fsinfo_sector"): "vbr_value",
    ("vbr", "backup_boot_sector"): "vbr_value",
    ("vbr", "drive_number_u8_hex"): "vbr_value",
    ("vbr", "cluster_count"): "vbr_value",
    ("vbr", "partition_offset"): "vbr_value",
    ("vbr", "partition_offset_sectors"): "vbr_value",
    ("vbr", "volume_length"): "vbr_value",
    ("vbr", "volume_length_sectors"): "vbr_value",
    ("vbr", "fat_offset"): "vbr_value",
    ("vbr", "fat_length"): "vbr_value",
    ("vbr", "cluster_heap_offset"): "vbr_value",
    ("vbr", "first_cluster_of_root_directory"): "vbr_value",
    ("vbr", "file_system_revision"): "vbr_value",
    ("vbr", "fs_revision"): "vbr_value",
    ("vbr", "filesystem_revision"): "vbr_value",
    ("vbr", "revision"): "vbr_value",
    ("vbr", "volume_flags_u16_hex"): "vbr_value",
    ("vbr", "bytes_per_sector_shift"): "vbr_value",
    ("vbr", "sectors_per_cluster_shift"): "vbr_value",
    ("vbr", "percent_in_use"): "vbr_value",
    ("vbr", "drive_select_u8_hex"): "vbr_value",
    ("boot_sector", "oem_id"): "vbr_value",
    ("boot_sector", "oem_name"): "vbr_value",
    ("boot_sector", "filesystem_type"): "vbr_value",
    ("boot_sector", "fs_type"): "vbr_value",
    ("boot_sector", "file_system_type"): "vbr_value",
    ("boot_sector", "bytes_per_sector"): "vbr_value",
    ("boot_sector", "sectors_per_cluster"): "vbr_value",
    ("boot_sector", "cluster_size_bytes"): "vbr_value",
    ("boot_sector", "cluster_size"): "vbr_value",
    ("boot_sector", "bytes_per_cluster"): "vbr_value",
    ("boot_sector", "media_descriptor_u8_hex"): "vbr_value",
    ("boot_sector", "media_descriptor"): "vbr_value",
    ("boot_sector", "hidden_sectors"): "vbr_value",
    ("boot_sector", "sectors_per_track"): "vbr_value",
    ("boot_sector", "number_of_heads"): "vbr_value",
    ("boot_sector", "total_sectors"): "vbr_value",
    ("boot_sector", "number_of_sectors"): "vbr_value",
    ("boot_sector", "volume_size_bytes"): "vbr_value",
    ("boot_sector", "mft_cluster_number"): "vbr_value",
    ("boot_sector", "mft_lcn"): "vbr_value",
    ("boot_sector", "mft_start_cluster"): "vbr_value",
    ("boot_sector", "mft_cluster"): "vbr_value",
    ("boot_sector", "mft_start_lcn"): "vbr_value",
    ("boot_sector", "mft_offset_bytes"): "vbr_value",
    ("boot_sector", "mft_byte_offset"): "vbr_value",
    ("boot_sector", "mftmirr_cluster_number"): "vbr_value",
    ("boot_sector", "mft_mirror_cluster_number"): "vbr_value",
    ("boot_sector", "mftmirr_lcn"): "vbr_value",
    ("boot_sector", "mft_mirror_lcn"): "vbr_value",
    ("boot_sector", "clusters_per_mft_record"): "vbr_value",
    ("boot_sector", "mft_record_size_bytes"): "vbr_value",
    ("boot_sector", "mft_record_size"): "vbr_value",
    ("boot_sector", "mft_entry_size_bytes"): "vbr_value",
    ("boot_sector", "file_record_size_bytes"): "vbr_value",
    ("boot_sector", "clusters_per_index_record"): "vbr_value",
    ("boot_sector", "index_record_size_bytes"): "vbr_value",
    ("boot_sector", "index_record_size"): "vbr_value",
    ("boot_sector", "index_buffer_size_bytes"): "vbr_value",
    ("boot_sector", "volume_serial_number_u64_hex"): "vbr_value",
    ("boot_sector", "volume_serial_u64_hex"): "vbr_value",
    ("boot_sector", "volume_serial_number"): "vbr_value",
    ("boot_sector", "volume_serial"): "vbr_value",
    ("boot_sector", "volume_serial_number_hex"): "vbr_value",
    ("boot_sector", "volume_serial_u32_hex"): "vbr_value",
    ("boot_sector", "volume_serial_number_u32_hex"): "vbr_value",
    ("boot_sector", "volume_serial_dir_style"): "vbr_value",
    ("boot_sector", "volume_serial_number_dir_style"): "vbr_value",
    ("boot_sector", "volume_serial_dir"): "vbr_value",
    ("boot_sector", "checksum_u32_hex"): "vbr_value",
    ("boot_sector", "boot_signature_u16_hex"): "vbr_value",
    ("boot_sector", "end_of_sector_marker_u16_hex"): "vbr_value",
    ("boot_sector", "signature_u16_hex"): "vbr_value",
    ("boot_sector", "fs_type_label"): "vbr_value",
    ("boot_sector", "file_system_type_label"): "vbr_value",
    ("boot_sector", "filesystem_type_label"): "vbr_value",
    ("boot_sector", "bs_fil_sys_type"): "vbr_value",
    ("boot_sector", "reserved_sectors"): "vbr_value",
    ("boot_sector", "reserved_sector_count"): "vbr_value",
    ("boot_sector", "number_of_fats"): "vbr_value",
    ("boot_sector", "num_fats"): "vbr_value",
    ("boot_sector", "fat_count"): "vbr_value",
    ("boot_sector", "root_entry_count"): "vbr_value",
    ("boot_sector", "root_dir_entries"): "vbr_value",
    ("boot_sector", "max_root_entries"): "vbr_value",
    ("boot_sector", "sectors_per_fat"): "vbr_value",
    ("boot_sector", "fat_size_sectors"): "vbr_value",
    ("boot_sector", "volume_id_u32_hex"): "vbr_value",
    ("boot_sector", "volume_id"): "vbr_value",
    ("boot_sector", "volume_label"): "vbr_value",
    ("boot_sector", "label"): "vbr_value",
    ("boot_sector", "bs_vol_lab"): "vbr_value",
    ("boot_sector", "boot_sector_volume_label"): "vbr_value",
    ("boot_sector", "root_cluster"): "vbr_value",
    ("boot_sector", "root_directory_cluster"): "vbr_value",
    ("boot_sector", "root_dir_first_cluster"): "vbr_value",
    ("boot_sector", "fsinfo_sector"): "vbr_value",
    ("boot_sector", "backup_boot_sector"): "vbr_value",
    ("boot_sector", "drive_number_u8_hex"): "vbr_value",
    ("boot_sector", "cluster_count"): "vbr_value",
    ("boot_sector", "partition_offset"): "vbr_value",
    ("boot_sector", "partition_offset_sectors"): "vbr_value",
    ("boot_sector", "volume_length"): "vbr_value",
    ("boot_sector", "volume_length_sectors"): "vbr_value",
    ("boot_sector", "fat_offset"): "vbr_value",
    ("boot_sector", "fat_length"): "vbr_value",
    ("boot_sector", "cluster_heap_offset"): "vbr_value",
    ("boot_sector", "first_cluster_of_root_directory"): "vbr_value",
    ("boot_sector", "file_system_revision"): "vbr_value",
    ("boot_sector", "fs_revision"): "vbr_value",
    ("boot_sector", "filesystem_revision"): "vbr_value",
    ("boot_sector", "revision"): "vbr_value",
    ("boot_sector", "volume_flags_u16_hex"): "vbr_value",
    ("boot_sector", "bytes_per_sector_shift"): "vbr_value",
    ("boot_sector", "sectors_per_cluster_shift"): "vbr_value",
    ("boot_sector", "percent_in_use"): "vbr_value",
    ("boot_sector", "drive_select_u8_hex"): "vbr_value",
    ("filesystem", "oem_id"): "vbr_value",
    ("filesystem", "oem_name"): "vbr_value",
    ("filesystem", "filesystem_type"): "vbr_value",
    ("filesystem", "fs_type"): "vbr_value",
    ("filesystem", "file_system_type"): "vbr_value",
    ("filesystem", "bytes_per_sector"): "vbr_value",
    ("filesystem", "sectors_per_cluster"): "vbr_value",
    ("filesystem", "cluster_size_bytes"): "vbr_value",
    ("filesystem", "cluster_size"): "vbr_value",
    ("filesystem", "bytes_per_cluster"): "vbr_value",
    ("filesystem", "media_descriptor_u8_hex"): "vbr_value",
    ("filesystem", "media_descriptor"): "vbr_value",
    ("filesystem", "hidden_sectors"): "vbr_value",
    ("filesystem", "sectors_per_track"): "vbr_value",
    ("filesystem", "number_of_heads"): "vbr_value",
    ("filesystem", "total_sectors"): "vbr_value",
    ("filesystem", "number_of_sectors"): "vbr_value",
    ("filesystem", "volume_size_bytes"): "vbr_value",
    ("filesystem", "mft_cluster_number"): "vbr_value",
    ("filesystem", "mft_lcn"): "vbr_value",
    ("filesystem", "mft_start_cluster"): "vbr_value",
    ("filesystem", "mft_cluster"): "vbr_value",
    ("filesystem", "mft_start_lcn"): "vbr_value",
    ("filesystem", "mft_offset_bytes"): "vbr_value",
    ("filesystem", "mft_byte_offset"): "vbr_value",
    ("filesystem", "mftmirr_cluster_number"): "vbr_value",
    ("filesystem", "mft_mirror_cluster_number"): "vbr_value",
    ("filesystem", "mftmirr_lcn"): "vbr_value",
    ("filesystem", "mft_mirror_lcn"): "vbr_value",
    ("filesystem", "clusters_per_mft_record"): "vbr_value",
    ("filesystem", "mft_record_size_bytes"): "vbr_value",
    ("filesystem", "mft_record_size"): "vbr_value",
    ("filesystem", "mft_entry_size_bytes"): "vbr_value",
    ("filesystem", "file_record_size_bytes"): "vbr_value",
    ("filesystem", "clusters_per_index_record"): "vbr_value",
    ("filesystem", "index_record_size_bytes"): "vbr_value",
    ("filesystem", "index_record_size"): "vbr_value",
    ("filesystem", "index_buffer_size_bytes"): "vbr_value",
    ("filesystem", "volume_serial_number_u64_hex"): "vbr_value",
    ("filesystem", "volume_serial_u64_hex"): "vbr_value",
    ("filesystem", "volume_serial_number"): "vbr_value",
    ("filesystem", "volume_serial"): "vbr_value",
    ("filesystem", "volume_serial_number_hex"): "vbr_value",
    ("filesystem", "volume_serial_u32_hex"): "vbr_value",
    ("filesystem", "volume_serial_number_u32_hex"): "vbr_value",
    ("filesystem", "volume_serial_dir_style"): "vbr_value",
    ("filesystem", "volume_serial_number_dir_style"): "vbr_value",
    ("filesystem", "volume_serial_dir"): "vbr_value",
    ("filesystem", "checksum_u32_hex"): "vbr_value",
    ("filesystem", "boot_signature_u16_hex"): "vbr_value",
    ("filesystem", "end_of_sector_marker_u16_hex"): "vbr_value",
    ("filesystem", "signature_u16_hex"): "vbr_value",
    ("filesystem", "fs_type_label"): "vbr_value",
    ("filesystem", "file_system_type_label"): "vbr_value",
    ("filesystem", "filesystem_type_label"): "vbr_value",
    ("filesystem", "bs_fil_sys_type"): "vbr_value",
    ("filesystem", "reserved_sectors"): "vbr_value",
    ("filesystem", "reserved_sector_count"): "vbr_value",
    ("filesystem", "number_of_fats"): "vbr_value",
    ("filesystem", "num_fats"): "vbr_value",
    ("filesystem", "fat_count"): "vbr_value",
    ("filesystem", "root_entry_count"): "vbr_value",
    ("filesystem", "root_dir_entries"): "vbr_value",
    ("filesystem", "max_root_entries"): "vbr_value",
    ("filesystem", "sectors_per_fat"): "vbr_value",
    ("filesystem", "fat_size_sectors"): "vbr_value",
    ("filesystem", "volume_id_u32_hex"): "vbr_value",
    ("filesystem", "volume_id"): "vbr_value",
    ("filesystem", "volume_label"): "vbr_value",
    ("filesystem", "label"): "vbr_value",
    ("filesystem", "bs_vol_lab"): "vbr_value",
    ("filesystem", "boot_sector_volume_label"): "vbr_value",
    ("filesystem", "root_cluster"): "vbr_value",
    ("filesystem", "root_directory_cluster"): "vbr_value",
    ("filesystem", "root_dir_first_cluster"): "vbr_value",
    ("filesystem", "fsinfo_sector"): "vbr_value",
    ("filesystem", "backup_boot_sector"): "vbr_value",
    ("filesystem", "drive_number_u8_hex"): "vbr_value",
    ("filesystem", "cluster_count"): "vbr_value",
    ("filesystem", "partition_offset"): "vbr_value",
    ("filesystem", "partition_offset_sectors"): "vbr_value",
    ("filesystem", "volume_length"): "vbr_value",
    ("filesystem", "volume_length_sectors"): "vbr_value",
    ("filesystem", "fat_offset"): "vbr_value",
    ("filesystem", "fat_length"): "vbr_value",
    ("filesystem", "cluster_heap_offset"): "vbr_value",
    ("filesystem", "first_cluster_of_root_directory"): "vbr_value",
    ("filesystem", "file_system_revision"): "vbr_value",
    ("filesystem", "fs_revision"): "vbr_value",
    ("filesystem", "filesystem_revision"): "vbr_value",
    ("filesystem", "revision"): "vbr_value",
    ("filesystem", "volume_flags_u16_hex"): "vbr_value",
    ("filesystem", "bytes_per_sector_shift"): "vbr_value",
    ("filesystem", "sectors_per_cluster_shift"): "vbr_value",
    ("filesystem", "percent_in_use"): "vbr_value",
    ("filesystem", "drive_select_u8_hex"): "vbr_value",
    ("mbr", "disk_signature_u32_hex"): "mbr_value",
    ("mbr", "disk_signature"): "mbr_value",
    ("mbr", "disk_identifier_u32_hex"): "mbr_value",
    ("mbr", "disk_identifier"): "mbr_value",
    ("mbr", "disk_id_u32_hex"): "mbr_value",
    ("mbr", "partition_count"): "mbr_value",
    ("mbr", "number_of_partitions"): "mbr_value",
    ("mbr", "partition_types"): "mbr_value",
    ("mbr", "partition_type_list"): "mbr_value",
    ("mbr", "active_partition_index"): "mbr_value",
    ("mbr", "bootable_partition_index"): "mbr_value",
    ("mbr", "first_partition_lba"): "mbr_value",
    ("mbr", "first_partition_start_lba"): "mbr_value",
    ("mbr", "first_partition_type_u8_hex"): "mbr_value",
    ("mbr", "partition_start_lbas"): "mbr_value",
    ("mbr", "partition_sector_counts"): "mbr_value",
    ("mbr", "boot_signature_u16_hex"): "mbr_value",
    ("mbr", "signature_u16_hex"): "mbr_value",
    ("mbr", "is_protective_mbr"): "mbr_value",
    ("mbr", "protective_mbr"): "mbr_value",
    ("mbr", "has_gpt"): "mbr_value",
    ("mbr", "partition_table_type"): "mbr_value",
    ("mbr", "label_type"): "mbr_value",
    ("partition_table", "disk_signature_u32_hex"): "mbr_value",
    ("partition_table", "disk_signature"): "mbr_value",
    ("partition_table", "disk_identifier_u32_hex"): "mbr_value",
    ("partition_table", "disk_identifier"): "mbr_value",
    ("partition_table", "disk_id_u32_hex"): "mbr_value",
    ("partition_table", "partition_count"): "mbr_value",
    ("partition_table", "number_of_partitions"): "mbr_value",
    ("partition_table", "partition_types"): "mbr_value",
    ("partition_table", "partition_type_list"): "mbr_value",
    ("partition_table", "active_partition_index"): "mbr_value",
    ("partition_table", "bootable_partition_index"): "mbr_value",
    ("partition_table", "first_partition_lba"): "mbr_value",
    ("partition_table", "first_partition_start_lba"): "mbr_value",
    ("partition_table", "first_partition_type_u8_hex"): "mbr_value",
    ("partition_table", "partition_start_lbas"): "mbr_value",
    ("partition_table", "partition_sector_counts"): "mbr_value",
    ("partition_table", "boot_signature_u16_hex"): "mbr_value",
    ("partition_table", "signature_u16_hex"): "mbr_value",
    ("partition_table", "is_protective_mbr"): "mbr_value",
    ("partition_table", "protective_mbr"): "mbr_value",
    ("partition_table", "has_gpt"): "mbr_value",
    ("partition_table", "partition_table_type"): "mbr_value",
    ("partition_table", "label_type"): "mbr_value",
    ("gpt", "signature"): "gpt_value",
    ("gpt", "revision"): "gpt_value",
    ("gpt", "revision_u32_hex"): "gpt_value",
    ("gpt", "header_size"): "gpt_value",
    ("gpt", "header_crc32_u32_hex"): "gpt_value",
    ("gpt", "current_lba"): "gpt_value",
    ("gpt", "my_lba"): "gpt_value",
    ("gpt", "backup_lba"): "gpt_value",
    ("gpt", "alternate_lba"): "gpt_value",
    ("gpt", "first_usable_lba"): "gpt_value",
    ("gpt", "last_usable_lba"): "gpt_value",
    ("gpt", "disk_guid"): "gpt_value",
    ("gpt", "disk_guid_upper"): "gpt_value",
    ("gpt", "partition_entry_lba"): "gpt_value",
    ("gpt", "partition_entries_lba"): "gpt_value",
    ("gpt", "number_of_partition_entries"): "gpt_value",
    ("gpt", "partition_entry_count"): "gpt_value",
    ("gpt", "num_partition_entries"): "gpt_value",
    ("gpt", "partition_entry_size"): "gpt_value",
    ("gpt", "size_of_partition_entry"): "gpt_value",
    ("gpt", "partition_entry_array_crc32_u32_hex"): "gpt_value",
    ("gpt", "partition_count"): "gpt_value",
    ("gpt", "number_of_partitions"): "gpt_value",
    ("gpt", "partition_names"): "gpt_value",
    ("gpt", "partition_type_guids"): "gpt_value",
    ("gpt", "partition_unique_guids"): "gpt_value",
    ("gpt", "partition_guids"): "gpt_value",
    ("gpt", "partition_first_lbas"): "gpt_value",
    ("gpt", "partition_last_lbas"): "gpt_value",
    ("gpt", "first_partition_lba"): "gpt_value",
}


_NONE = "none"
_FS_TYPES = ("ntfs", "fat", "exfat")


def _u(b, o, n):
    return int.from_bytes(b[o:o + n], "little") if len(b) >= o + n else None


def _sig_ok(b, o=0):
    return len(b) >= o + 512 and b[o + 0x1FE:o + 0x200] == b"\x55\xaa"


def _fs_kind(b, o=0):
    """'ntfs' / 'exfat' / 'fat' for a VBR at offset o, else None."""
    if len(b) < o + 512:
        return None
    oem = b[o + 3:o + 11]
    if oem == b"NTFS    " and _sig_ok(b, o):
        return "ntfs"
    if oem == b"EXFAT   " and _sig_ok(b, o):
        return "exfat"
    if b[o] not in (0xEB, 0xE9):
        return None
    bps, spc, nfats = _u(b, o + 0x0B, 2), b[o + 0x0D], b[o + 0x10]
    if bps not in (512, 1024, 2048, 4096) or spc == 0 or spc & (spc - 1) or nfats == 0:
        return None
    if b[o + 0x52:o + 0x57] == b"FAT32" or b[o + 0x36:o + 0x39] == b"FAT" or b[o + 0x26] == 0x29 or b[o + 0x42] == 0x29:
        return "fat"
    return None


def _mbr_entries(b):
    """[(slot, status, type, lba, count)] for the non-zero-type MBR entries, or None (not an MBR)."""
    if not _sig_ok(b) or _fs_kind(b, 0):
        return None
    ents = []
    for i in range(4):
        e = 0x1BE + 16 * i
        status, ptype = b[e], b[e + 4]
        if status not in (0, 0x80):
            return None
        if ptype:
            ents.append((i, status, ptype, _u(b, e + 8, 4), _u(b, e + 12, 4)))
    return ents


def _gpt(b):
    """Parsed GPT header + used entries, or None."""
    for ss in (512, 4096):
        h = ss
        if b[h:h + 8] != b"EFI PART" or len(b) < h + 92:
            continue
        r = {"sector": ss, "signature": "EFI PART", "revision_raw": _u(b, h + 8, 4), "header_size": _u(b, h + 12, 4),
             "header_crc32": _u(b, h + 16, 4), "current_lba": _u(b, h + 24, 8), "backup_lba": _u(b, h + 32, 8),
             "first_usable_lba": _u(b, h + 40, 8), "last_usable_lba": _u(b, h + 48, 8),
             "disk_guid": bytes(b[h + 56:h + 72]), "entry_lba": _u(b, h + 72, 8), "entry_count": _u(b, h + 80, 4),
             "entry_size": _u(b, h + 84, 4), "array_crc32": _u(b, h + 88, 4), "entries": []}
        es, base = r["entry_size"], r["entry_lba"] * ss
        if 128 <= es <= 4096 and r["entry_count"] <= 4096:
            for i in range(r["entry_count"]):
                e = base + i * es
                if len(b) < e + 128:
                    break
                tg = bytes(b[e:e + 16])
                if tg == b"\0" * 16:
                    continue
                name = b[e + 56:e + 128].decode("utf-16-le", "replace").split("\0", 1)[0]
                r["entries"].append({"type": str(uuid.UUID(bytes_le=tg)), "unique": str(uuid.UUID(bytes_le=bytes(b[e + 16:e + 32]))),
                                     "first": _u(b, e + 32, 8), "last": _u(b, e + 40, 8), "name": name})
        return r
    return None


def _locate(b):
    """(offset, kind) of the filesystem VBR: at 0, else via the MBR / GPT to the first partition."""
    k = _fs_kind(b, 0)
    if k:
        return 0, k
    ents = _mbr_entries(b)
    if not ents:
        return None, None
    if any(e[2] == 0xEE for e in ents):
        g = _gpt(b)
        if not g or not g["entries"]:
            return None, None
        off = g["entries"][0]["first"] * g["sector"]
    else:
        off = ents[0][3] * 512
    k = _fs_kind(b, off)
    return (off, k) if k else (None, None)


def _serial_dir(v):
    v &= 0xFFFFFFFF
    return "%04X-%04X" % (v >> 16, v & 0xFFFF)


def _txt(raw):
    return raw.decode("latin-1").rstrip(" \0")


def _ntfs(b, o):
    v = b[o:o + 512]
    bps, spc_raw = _u(v, 0x0B, 2), v[0x0D]
    spc = 1 << (256 - spc_raw) if spc_raw >= 0x80 else spc_raw
    cl = bps * spc
    def recsz(x):   # noqa: E306
        x = x - 256 if x >= 0x80 else x
        return 1 << -x if x < 0 else x * cl
    ser, tot, mft = _u(v, 0x48, 8), _u(v, 0x28, 8), _u(v, 0x30, 8)
    mirr = _u(v, 0x38, 8)
    out = {"oem_id": "NTFS", "filesystem_type": "NTFS", "bytes_per_sector": bps, "sectors_per_cluster": spc,
           "cluster_size_bytes": cl, "media_descriptor_u8_hex": Hex(v[0x15], 2), "hidden_sectors": _u(v, 0x1C, 4),
           "sectors_per_track": _u(v, 0x18, 2), "number_of_heads": _u(v, 0x1A, 2), "total_sectors": tot,
           "volume_size_bytes": tot * bps, "mft_cluster_number": mft, "mft_offset_bytes": mft * cl,
           "mftmirr_cluster_number": mirr, "clusters_per_mft_record": v[0x40] - 256 if v[0x40] >= 0x80 else v[0x40],
           "mft_record_size_bytes": recsz(v[0x40]),
           "clusters_per_index_record": v[0x44] - 256 if v[0x44] >= 0x80 else v[0x44],
           "index_record_size_bytes": recsz(v[0x44]), "volume_serial_number_u64_hex": Hex(ser, 16),
           "volume_serial_u32_hex": Hex(ser & 0xFFFFFFFF, 8), "volume_serial_dir_style": _serial_dir(ser),
           "checksum_u32_hex": Hex(_u(v, 0x50, 4), 8), "boot_signature_u16_hex": Hex(_u(v, 0x1FE, 2), 4)}
    for a, t in (("oem_name", "oem_id"), ("fs_type", "filesystem_type"), ("file_system_type", "filesystem_type"),
                 ("cluster_size", "cluster_size_bytes"), ("bytes_per_cluster", "cluster_size_bytes"),
                 ("media_descriptor", "media_descriptor_u8_hex"), ("number_of_sectors", "total_sectors"),
                 ("mft_lcn", "mft_cluster_number"), ("mft_start_cluster", "mft_cluster_number"),
                 ("mft_cluster", "mft_cluster_number"), ("mft_start_lcn", "mft_cluster_number"),
                 ("mft_byte_offset", "mft_offset_bytes"), ("mft_mirror_cluster_number", "mftmirr_cluster_number"),
                 ("mftmirr_lcn", "mftmirr_cluster_number"), ("mft_mirror_lcn", "mftmirr_cluster_number"),
                 ("mft_record_size", "mft_record_size_bytes"), ("mft_entry_size_bytes", "mft_record_size_bytes"),
                 ("file_record_size_bytes", "mft_record_size_bytes"), ("index_record_size", "index_record_size_bytes"),
                 ("index_buffer_size_bytes", "index_record_size_bytes"),
                 ("volume_serial_u64_hex", "volume_serial_number_u64_hex"),
                 ("volume_serial_number", "volume_serial_number_u64_hex"),
                 ("volume_serial", "volume_serial_number_u64_hex"),
                 ("volume_serial_number_hex", "volume_serial_number_u64_hex"),
                 ("volume_serial_number_u32_hex", "volume_serial_u32_hex"),
                 ("volume_serial_number_dir_style", "volume_serial_dir_style"),
                 ("volume_serial_dir", "volume_serial_dir_style"),
                 ("end_of_sector_marker_u16_hex", "boot_signature_u16_hex"),
                 ("signature_u16_hex", "boot_signature_u16_hex")):
        out[a] = out[t]
    return out


def _fat(b, o):
    v = b[o:o + 512]
    bps, spc, rsvd, nfats = _u(v, 0x0B, 2), v[0x0D], _u(v, 0x0E, 2), v[0x10]
    roots, tot16, fat16sz, tot32 = _u(v, 0x11, 2), _u(v, 0x13, 2), _u(v, 0x16, 2), _u(v, 0x20, 4)
    is32 = fat16sz == 0
    fatsz = _u(v, 0x24, 4) if is32 else fat16sz
    tot = tot16 or tot32
    rds = (roots * 32 + bps - 1) // bps
    ncl = max(tot - (rsvd + nfats * fatsz + rds), 0) // spc
    kind = "FAT12" if ncl < 4085 else "FAT16" if ncl < 65525 else "FAT32"
    eb = 0x40 if is32 else 0x24          # BS_DrvNum; ext boot sig +2, serial +3, label +7, type +0x12
    out = {"oem_id": _txt(v[3:11]), "filesystem_type": kind, "bytes_per_sector": bps, "sectors_per_cluster": spc,
           "cluster_size_bytes": bps * spc, "reserved_sectors": rsvd, "number_of_fats": nfats,
           "root_entry_count": roots, "total_sectors": tot, "volume_size_bytes": tot * bps,
           "media_descriptor_u8_hex": Hex(v[0x15], 2), "sectors_per_fat": fatsz, "hidden_sectors": _u(v, 0x1C, 4),
           "sectors_per_track": _u(v, 0x18, 2), "number_of_heads": _u(v, 0x1A, 2), "cluster_count": ncl,
           "drive_number_u8_hex": Hex(v[eb], 2), "boot_signature_u16_hex": Hex(_u(v, 0x1FE, 2), 4)}
    if is32:
        out.update(root_cluster=_u(v, 0x2C, 4), fsinfo_sector=_u(v, 0x30, 2), backup_boot_sector=_u(v, 0x32, 2))
    if v[eb + 2] in (0x29, 0x28):
        ser = _u(v, eb + 3, 4)
        out.update(volume_serial_number_u32_hex=Hex(ser, 8), volume_serial_dir_style=_serial_dir(ser))
        if v[eb + 2] == 0x29:
            out.update(volume_label=_txt(v[eb + 7:eb + 18]) or _NONE, fs_type_label=_txt(v[eb + 18:eb + 26]) or _NONE)
    for a, t in (("oem_name", "oem_id"), ("fs_type", "filesystem_type"), ("file_system_type", "filesystem_type"),
                 ("file_system_type_label", "fs_type_label"), ("filesystem_type_label", "fs_type_label"),
                 ("bs_fil_sys_type", "fs_type_label"), ("cluster_size", "cluster_size_bytes"),
                 ("bytes_per_cluster", "cluster_size_bytes"), ("reserved_sector_count", "reserved_sectors"),
                 ("num_fats", "number_of_fats"), ("fat_count", "number_of_fats"),
                 ("root_dir_entries", "root_entry_count"), ("max_root_entries", "root_entry_count"),
                 ("number_of_sectors", "total_sectors"), ("media_descriptor", "media_descriptor_u8_hex"),
                 ("fat_size_sectors", "sectors_per_fat"), ("volume_serial_u32_hex", "volume_serial_number_u32_hex"),
                 ("volume_id_u32_hex", "volume_serial_number_u32_hex"),
                 ("volume_serial_number", "volume_serial_number_u32_hex"),
                 ("volume_serial", "volume_serial_number_u32_hex"), ("volume_id", "volume_serial_number_u32_hex"),
                 ("volume_serial_number_hex", "volume_serial_number_u32_hex"),
                 ("volume_serial_number_dir_style", "volume_serial_dir_style"),
                 ("volume_serial_dir", "volume_serial_dir_style"), ("label", "volume_label"),
                 ("bs_vol_lab", "volume_label"), ("boot_sector_volume_label", "volume_label"),
                 ("root_directory_cluster", "root_cluster"), ("root_dir_first_cluster", "root_cluster"),
                 ("end_of_sector_marker_u16_hex", "boot_signature_u16_hex"),
                 ("signature_u16_hex", "boot_signature_u16_hex")):
        if t in out:
            out[a] = out[t]
    return out


def _exfat_label(b, o, bps, cl, heap, root):
    """The 0x83 Volume Label entry of the root directory's first cluster (when the image carries it)."""
    d = o + heap * bps + (root - 2) * cl
    for e in range(d, min(d + cl, len(b) - 31), 32):
        t = b[e]
        if t == 0:
            break
        if t == 0x83:
            n = min(b[e + 1], 11)
            return b[e + 2:e + 2 + 2 * n].decode("utf-16-le", "replace")
    return None


def _exfat(b, o):
    v = b[o:o + 512]
    bsh, csh = v[0x6C], v[0x6D]
    if not 9 <= bsh <= 12 or bsh + csh > 25:
        return {}
    bps, spc = 1 << bsh, 1 << csh
    vlen, ser, rev = _u(v, 0x48, 8), _u(v, 0x64, 4), _u(v, 0x68, 2)
    heap, root = _u(v, 0x58, 4), _u(v, 0x60, 4)
    out = {"oem_id": "EXFAT", "filesystem_type": "exFAT", "partition_offset": _u(v, 0x40, 8), "volume_length": vlen,
           "volume_size_bytes": vlen * bps, "fat_offset": _u(v, 0x50, 4), "fat_length": _u(v, 0x54, 4),
           "cluster_heap_offset": heap, "cluster_count": _u(v, 0x5C, 4), "first_cluster_of_root_directory": root,
           "volume_serial_number_u32_hex": Hex(ser, 8), "volume_serial_dir_style": _serial_dir(ser),
           "file_system_revision": "%d.%02d" % (rev >> 8, rev & 0xFF), "volume_flags_u16_hex": Hex(_u(v, 0x6A, 2), 4),
           "bytes_per_sector_shift": bsh, "sectors_per_cluster_shift": csh, "bytes_per_sector": bps,
           "sectors_per_cluster": spc, "cluster_size_bytes": bps * spc, "number_of_fats": v[0x6E],
           "drive_select_u8_hex": Hex(v[0x6F], 2), "percent_in_use": v[0x70],
           "boot_signature_u16_hex": Hex(_u(v, 0x1FE, 2), 4)}
    lab = _exfat_label(b, o, bps, bps * spc, heap, root) if root >= 2 else None
    if lab is not None:
        out["volume_label"] = lab or _NONE
    for a, t in (("oem_name", "oem_id"), ("fs_type", "filesystem_type"), ("file_system_type", "filesystem_type"),
                 ("partition_offset_sectors", "partition_offset"), ("volume_length_sectors", "volume_length"),
                 ("total_sectors", "volume_length"), ("number_of_sectors", "volume_length"),
                 ("root_directory_cluster", "first_cluster_of_root_directory"),
                 ("root_cluster", "first_cluster_of_root_directory"),
                 ("volume_serial_u32_hex", "volume_serial_number_u32_hex"),
                 ("volume_serial_number", "volume_serial_number_u32_hex"),
                 ("volume_serial", "volume_serial_number_u32_hex"),
                 ("volume_serial_number_hex", "volume_serial_number_u32_hex"),
                 ("volume_serial_number_dir_style", "volume_serial_dir_style"),
                 ("volume_serial_dir", "volume_serial_dir_style"), ("fs_revision", "file_system_revision"),
                 ("filesystem_revision", "file_system_revision"), ("revision", "file_system_revision"),
                 ("cluster_size", "cluster_size_bytes"), ("bytes_per_cluster", "cluster_size_bytes"),
                 ("label", "volume_label"), ("end_of_sector_marker_u16_hex", "boot_signature_u16_hex"),
                 ("signature_u16_hex", "boot_signature_u16_hex")):
        if t in out:
            out[a] = out[t]
    return out


_PARSE = {"ntfs": _ntfs, "fat": _fat, "exfat": _exfat}


def _fs_answer(data, ctx, want):
    if not data:
        return None
    try:
        off, kind = _locate(bytes(data))
        if kind is None or (want and kind != want):
            return _NONE
        v = _PARSE[kind](bytes(data), off).get(ctx.get("field") or "")
        return _NONE if v is None else v
    except (IndexError, ValueError, struct.error, TypeError, OverflowError):
        return None


def ntfs_value(data, ctx):
    """ntfs.<field>: the NTFS $Boot VBR (carved, or the first partition of an MBR/GPT disk image)."""
    return _fs_answer(data, ctx, "ntfs")


def fat_value(data, ctx):
    """fat.<field>: a FAT12/16/32 VBR."""
    return _fs_answer(data, ctx, "fat")


def exfat_value(data, ctx):
    """exfat.<field>: an exFAT VBR (+ the root-directory volume label when present)."""
    return _fs_answer(data, ctx, "exfat")


def vbr_value(data, ctx):
    """vbr / boot_sector / filesystem.<field>: whichever of NTFS / FAT / exFAT the boot sector is."""
    return _fs_answer(data, ctx, None)


def _mbr(b):
    ents = _mbr_entries(b)
    if ents is None:
        return {}
    prot = any(e[2] == 0xEE for e in ents)
    act = [e[0] for e in ents if e[1] == 0x80]
    out = {"disk_signature_u32_hex": Hex(_u(b, 0x1B8, 4), 8), "partition_count": len(ents),
           "partition_types": ["0x%02x" % e[2] for e in ents], "active_partition_index": act[0] if act else _NONE,
           "first_partition_lba": ents[0][3] if ents else _NONE,
           "first_partition_type_u8_hex": Hex(ents[0][2], 2) if ents else _NONE,
           "partition_start_lbas": [e[3] for e in ents], "partition_sector_counts": [e[4] for e in ents],
           "boot_signature_u16_hex": Hex(_u(b, 0x1FE, 2), 4), "is_protective_mbr": prot,
           "has_gpt": bool(prot and _gpt(b)), "partition_table_type": "gpt" if prot else "dos"}
    for a, t in (("disk_signature", "disk_signature_u32_hex"), ("disk_identifier_u32_hex", "disk_signature_u32_hex"),
                 ("disk_identifier", "disk_signature_u32_hex"), ("disk_id_u32_hex", "disk_signature_u32_hex"),
                 ("number_of_partitions", "partition_count"), ("partition_type_list", "partition_types"),
                 ("bootable_partition_index", "active_partition_index"),
                 ("first_partition_start_lba", "first_partition_lba"), ("signature_u16_hex", "boot_signature_u16_hex"),
                 ("protective_mbr", "is_protective_mbr"), ("label_type", "partition_table_type")):
        out[a] = out[t]
    return out


def _gpt_fields(b):
    g = _gpt(b)
    if not g:
        return {}
    ents, rev = g["entries"], g["revision_raw"]
    out = {"signature": g["signature"], "revision": "%d.%d" % (rev >> 16, rev & 0xFFFF),
           "revision_u32_hex": Hex(rev, 8), "header_size": g["header_size"],
           "header_crc32_u32_hex": Hex(g["header_crc32"], 8), "current_lba": g["current_lba"],
           "backup_lba": g["backup_lba"], "first_usable_lba": g["first_usable_lba"],
           "last_usable_lba": g["last_usable_lba"], "disk_guid": Guid("bytes_le", g["disk_guid"]),
           "disk_guid_upper": str(uuid.UUID(bytes_le=g["disk_guid"])).upper(), "partition_entry_lba": g["entry_lba"],
           "number_of_partition_entries": g["entry_count"], "partition_entry_size": g["entry_size"],
           "partition_entry_array_crc32_u32_hex": Hex(g["array_crc32"], 8), "partition_count": len(ents),
           "partition_names": [e["name"] for e in ents], "partition_type_guids": [e["type"] for e in ents],
           "partition_unique_guids": [e["unique"] for e in ents], "partition_first_lbas": [e["first"] for e in ents],
           "partition_last_lbas": [e["last"] for e in ents], "first_partition_lba": ents[0]["first"] if ents else _NONE}
    for a, t in (("my_lba", "current_lba"), ("alternate_lba", "backup_lba"),
                 ("partition_entries_lba", "partition_entry_lba"),
                 ("partition_entry_count", "number_of_partition_entries"),
                 ("num_partition_entries", "number_of_partition_entries"),
                 ("size_of_partition_entry", "partition_entry_size"), ("number_of_partitions", "partition_count"),
                 ("partition_guids", "partition_unique_guids")):
        out[a] = out[t]
    return out


def _table_answer(data, ctx, fn):
    if not data:
        return None
    try:
        v = fn(bytes(data)).get(ctx.get("field") or "")
        return _NONE if v is None else v
    except (IndexError, ValueError, struct.error, TypeError, OverflowError):
        return None


def mbr_value(data, ctx):
    """mbr / partition_table.<field>: the sector-0 MBR (a VBR at sector 0 is not an MBR -> "none")."""
    return _table_answer(data, ctx, _mbr)


def gpt_value(data, ctx):
    """gpt.<field>: the LBA-1 GPT header and its entry array."""
    return _table_answer(data, ctx, _gpt_fields)
