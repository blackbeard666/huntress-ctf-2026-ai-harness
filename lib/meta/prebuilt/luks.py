"""LUKS1 / LUKS2 encrypted-volume header fields (prebuilt, SPECULATIVE -- never GM-asked yet).

The header is located at the first 512-aligned `LUKS\\xba\\xbe` magic (offset 0 for a bare header dump / volume; a
partition start inside a whole-disk image), else at a LUKS2 secondary header (`SKUL\\xba\\xbe`). All integers big-endian.
LUKS1 phdr (592 B): version u16 @6, cipher_name[32] @8, cipher_mode[32] @40, hash_spec[32] @72, payload_offset u32
@104 (512-byte SECTORS), key_bytes u32 @108, mk_digest[20] @112, mk_digest_salt[32] @132, mk_digest_iter u32 @164,
uuid[40] @168, 8 key slots x 48 B from @208 (active u32 = 0x00AC71F3 enabled / 0x0000DEAD disabled, iterations u32,
salt[32], key_material_offset u32 (sectors), stripes u32).
LUKS2 binary header (4096 B): version u16 @6, hdr_size u64 @8 (binary + JSON area), seqid u64 @16 (cryptsetup "Epoch"),
label[48] @24, checksum_alg[32] @72, salt[64] @104, uuid[40] @168, subsystem[48] @208, hdr_offset u64 @256, csum[64]
@448; JSON area @4096..hdr_size: keyslots / segments / digests / tokens / config. LUKS2 cipher = segments["0"].encryption
("aes-xts-plain64"); cipher_name / cipher_mode split it at the first "-" (the LUKS1 field pair). payload_offset is in
512-byte sectors on both versions (LUKS2 segment offset bytes / 512 -- cryptsetup luksDump LUKS1 "Payload offset");
payload_offset_bytes is the byte offset. key_bytes = LUKS1 key_bytes / LUKS2 first keyslot key_size; key_bits = x8
("MK bits"). sector_size: LUKS2 segment sector_size, 512 for LUKS1. hash_spec: LUKS1 hash_spec / LUKS2 first digest
hash. active_key_slots = indices of enabled LUKS1 slots / LUKS2 keyslot ids, ascending. Strings are NUL-trimmed verbatim.
Fields absent in the version (label/subsystem/checksum on LUKS1, mk_digest on LUKS2) -> "none"; no LUKS magic -> "none"
(VeraCrypt/TrueCrypt volumes are headerless random bytes: no magic, so every field is "none").
Oracles used for the fixtures: cryptsetup 2.8.4 luksDump (full image), blkid -p, file(1) 5.46 (header-only bytes)."""
import hashlib
import json
import re
import struct

FIELDS = {
    ("luks", "version"): "luks_value",
    ("luks", "luks_version"): "luks_value",
    ("luks", "header_version"): "luks_value",
    ("luks", "uuid"): "luks_value",
    ("luks", "volume_uuid"): "luks_value",
    ("luks", "header_uuid"): "luks_value",
    ("luks", "label"): "luks_value",
    ("luks", "volume_label"): "luks_value",
    ("luks", "header_label"): "luks_value",
    ("luks", "subsystem"): "luks_value",
    ("luks", "subsystem_label"): "luks_value",
    ("luks", "sub_label"): "luks_value",
    ("luks", "cipher_name"): "luks_value",
    ("luks", "cipher_algorithm"): "luks_value",
    ("luks", "encryption_algorithm"): "luks_value",
    ("luks", "cipher_mode"): "luks_value",
    ("luks", "encryption_mode"): "luks_value",
    ("luks", "cipher"): "luks_value",
    ("luks", "cipher_spec"): "luks_value",
    ("luks", "encryption"): "luks_value",
    ("luks", "segment_cipher"): "luks_value",
    ("luks", "segment_encryption"): "luks_value",
    ("luks", "data_cipher"): "luks_value",
    ("luks", "hash_spec"): "luks_value",
    ("luks", "hash"): "luks_value",
    ("luks", "hash_algorithm"): "luks_value",
    ("luks", "digest_hash"): "luks_value",
    ("luks", "pbkdf_hash"): "luks_value",
    ("luks", "af_hash"): "luks_value",
    ("luks", "payload_offset"): "luks_value",
    ("luks", "payload_offset_sectors"): "luks_value",
    ("luks", "data_offset_sectors"): "luks_value",
    ("luks", "payload_offset_bytes"): "luks_value",
    ("luks", "data_offset"): "luks_value",
    ("luks", "data_offset_bytes"): "luks_value",
    ("luks", "segment_offset"): "luks_value",
    ("luks", "segment_offset_bytes"): "luks_value",
    ("luks", "key_bytes"): "luks_value",
    ("luks", "key_size_bytes"): "luks_value",
    ("luks", "master_key_bytes"): "luks_value",
    ("luks", "volume_key_bytes"): "luks_value",
    ("luks", "key_bits"): "luks_value",
    ("luks", "key_size_bits"): "luks_value",
    ("luks", "key_size"): "luks_value",
    ("luks", "mk_bits"): "luks_value",
    ("luks", "master_key_bits"): "luks_value",
    ("luks", "volume_key_bits"): "luks_value",
    ("luks", "mk_digest_hex"): "luks_value",
    ("luks", "mk_digest"): "luks_value",
    ("luks", "master_key_digest_hex"): "luks_value",
    ("luks", "mk_salt_hex"): "luks_value",
    ("luks", "mk_digest_salt_hex"): "luks_value",
    ("luks", "mk_salt"): "luks_value",
    ("luks", "mk_iterations"): "luks_value",
    ("luks", "mk_digest_iterations"): "luks_value",
    ("luks", "mk_digest_iter"): "luks_value",
    ("luks", "digest_iterations"): "luks_value",
    ("luks", "active_key_slots"): "luks_value",
    ("luks", "active_keyslots"): "luks_value",
    ("luks", "enabled_key_slots"): "luks_value",
    ("luks", "active_key_slot_indices"): "luks_value",
    ("luks", "key_slot_indices"): "luks_value",
    ("luks", "keyslot_ids"): "luks_value",
    ("luks", "active_key_slot_count"): "luks_value",
    ("luks", "active_keyslot_count"): "luks_value",
    ("luks", "enabled_key_slot_count"): "luks_value",
    ("luks", "key_slot_count"): "luks_value",
    ("luks", "keyslot_count"): "luks_value",
    ("luks", "number_of_key_slots"): "luks_value",
    ("luks", "keyslots_count"): "luks_value",
    ("luks", "key_material_offsets"): "luks_value",
    ("luks", "keyslot_material_offsets"): "luks_value",
    ("luks", "keyslot_iterations"): "luks_value",
    ("luks", "key_slot_iterations"): "luks_value",
    ("luks", "pbkdf"): "luks_value",
    ("luks", "pbkdf_type"): "luks_value",
    ("luks", "keyslot_pbkdf"): "luks_value",
    ("luks", "kdf_type"): "luks_value",
    ("luks", "hdr_size"): "luks_value",
    ("luks", "header_size"): "luks_value",
    ("luks", "header_size_bytes"): "luks_value",
    ("luks", "metadata_size"): "luks_value",
    ("luks", "metadata_area_bytes"): "luks_value",
    ("luks", "metadata_size_bytes"): "luks_value",
    ("luks", "json_size"): "luks_value",
    ("luks", "json_area_size"): "luks_value",
    ("luks", "json_area_bytes"): "luks_value",
    ("luks", "seqid"): "luks_value",
    ("luks", "sequence_id"): "luks_value",
    ("luks", "epoch"): "luks_value",
    ("luks", "header_seqid"): "luks_value",
    ("luks", "checksum_alg"): "luks_value",
    ("luks", "checksum_algorithm"): "luks_value",
    ("luks", "csum_alg"): "luks_value",
    ("luks", "header_checksum_alg"): "luks_value",
    ("luks", "checksum_hex"): "luks_value",
    ("luks", "header_checksum_hex"): "luks_value",
    ("luks", "csum_hex"): "luks_value",
    ("luks", "checksum_valid"): "luks_value",
    ("luks", "header_checksum_valid"): "luks_value",
    ("luks", "csum_valid"): "luks_value",
    ("luks", "hdr_offset"): "luks_value",
    ("luks", "header_offset"): "luks_value",
    ("luks", "sector_size"): "luks_value",
    ("luks", "sector_size_bytes"): "luks_value",
    ("luks", "segment_sector_size"): "luks_value",
    ("luks", "encryption_sector_size"): "luks_value",
    ("luks", "segment_count"): "luks_value",
    ("luks", "number_of_segments"): "luks_value",
    ("luks", "data_segment_count"): "luks_value",
    ("luks", "keyslots_size"): "luks_value",
    ("luks", "keyslots_area_bytes"): "luks_value",
    ("luks", "keyslots_size_bytes"): "luks_value",
    ("luks", "token_count"): "luks_value",
    ("luks", "number_of_tokens"): "luks_value",
    ("luks", "digest_count"): "luks_value",
    ("luks", "number_of_digests"): "luks_value",
    ("luks", "luks_offset"): "luks_value",
    ("luks", "header_offset_in_image"): "luks_value",
    ("luks", "luks_header_offset"): "luks_value",
    ("luks", "luks_start_offset"): "luks_value",
    ("luks", "present"): "luks_value",
    ("luks", "luks_present"): "luks_value",
    ("luks", "is_luks"): "luks_value",
    ("luks", "has_luks"): "luks_value",
    ("luks", "encrypted"): "luks_value",
    ("luks", "is_encrypted"): "luks_value",
    ("luks1", "version"): "luks_value",
    ("luks1", "luks_version"): "luks_value",
    ("luks1", "header_version"): "luks_value",
    ("luks1", "uuid"): "luks_value",
    ("luks1", "volume_uuid"): "luks_value",
    ("luks1", "header_uuid"): "luks_value",
    ("luks1", "label"): "luks_value",
    ("luks1", "volume_label"): "luks_value",
    ("luks1", "header_label"): "luks_value",
    ("luks1", "subsystem"): "luks_value",
    ("luks1", "subsystem_label"): "luks_value",
    ("luks1", "sub_label"): "luks_value",
    ("luks1", "cipher_name"): "luks_value",
    ("luks1", "cipher_algorithm"): "luks_value",
    ("luks1", "encryption_algorithm"): "luks_value",
    ("luks1", "cipher_mode"): "luks_value",
    ("luks1", "encryption_mode"): "luks_value",
    ("luks1", "cipher"): "luks_value",
    ("luks1", "cipher_spec"): "luks_value",
    ("luks1", "encryption"): "luks_value",
    ("luks1", "segment_cipher"): "luks_value",
    ("luks1", "segment_encryption"): "luks_value",
    ("luks1", "data_cipher"): "luks_value",
    ("luks1", "hash_spec"): "luks_value",
    ("luks1", "hash"): "luks_value",
    ("luks1", "hash_algorithm"): "luks_value",
    ("luks1", "digest_hash"): "luks_value",
    ("luks1", "pbkdf_hash"): "luks_value",
    ("luks1", "af_hash"): "luks_value",
    ("luks1", "payload_offset"): "luks_value",
    ("luks1", "payload_offset_sectors"): "luks_value",
    ("luks1", "data_offset_sectors"): "luks_value",
    ("luks1", "payload_offset_bytes"): "luks_value",
    ("luks1", "data_offset"): "luks_value",
    ("luks1", "data_offset_bytes"): "luks_value",
    ("luks1", "segment_offset"): "luks_value",
    ("luks1", "segment_offset_bytes"): "luks_value",
    ("luks1", "key_bytes"): "luks_value",
    ("luks1", "key_size_bytes"): "luks_value",
    ("luks1", "master_key_bytes"): "luks_value",
    ("luks1", "volume_key_bytes"): "luks_value",
    ("luks1", "key_bits"): "luks_value",
    ("luks1", "key_size_bits"): "luks_value",
    ("luks1", "key_size"): "luks_value",
    ("luks1", "mk_bits"): "luks_value",
    ("luks1", "master_key_bits"): "luks_value",
    ("luks1", "volume_key_bits"): "luks_value",
    ("luks1", "mk_digest_hex"): "luks_value",
    ("luks1", "mk_digest"): "luks_value",
    ("luks1", "master_key_digest_hex"): "luks_value",
    ("luks1", "mk_salt_hex"): "luks_value",
    ("luks1", "mk_digest_salt_hex"): "luks_value",
    ("luks1", "mk_salt"): "luks_value",
    ("luks1", "mk_iterations"): "luks_value",
    ("luks1", "mk_digest_iterations"): "luks_value",
    ("luks1", "mk_digest_iter"): "luks_value",
    ("luks1", "digest_iterations"): "luks_value",
    ("luks1", "active_key_slots"): "luks_value",
    ("luks1", "active_keyslots"): "luks_value",
    ("luks1", "enabled_key_slots"): "luks_value",
    ("luks1", "active_key_slot_indices"): "luks_value",
    ("luks1", "key_slot_indices"): "luks_value",
    ("luks1", "keyslot_ids"): "luks_value",
    ("luks1", "active_key_slot_count"): "luks_value",
    ("luks1", "active_keyslot_count"): "luks_value",
    ("luks1", "enabled_key_slot_count"): "luks_value",
    ("luks1", "key_slot_count"): "luks_value",
    ("luks1", "keyslot_count"): "luks_value",
    ("luks1", "number_of_key_slots"): "luks_value",
    ("luks1", "keyslots_count"): "luks_value",
    ("luks1", "key_material_offsets"): "luks_value",
    ("luks1", "keyslot_material_offsets"): "luks_value",
    ("luks1", "keyslot_iterations"): "luks_value",
    ("luks1", "key_slot_iterations"): "luks_value",
    ("luks1", "pbkdf"): "luks_value",
    ("luks1", "pbkdf_type"): "luks_value",
    ("luks1", "keyslot_pbkdf"): "luks_value",
    ("luks1", "kdf_type"): "luks_value",
    ("luks1", "hdr_size"): "luks_value",
    ("luks1", "header_size"): "luks_value",
    ("luks1", "header_size_bytes"): "luks_value",
    ("luks1", "metadata_size"): "luks_value",
    ("luks1", "metadata_area_bytes"): "luks_value",
    ("luks1", "metadata_size_bytes"): "luks_value",
    ("luks1", "json_size"): "luks_value",
    ("luks1", "json_area_size"): "luks_value",
    ("luks1", "json_area_bytes"): "luks_value",
    ("luks1", "seqid"): "luks_value",
    ("luks1", "sequence_id"): "luks_value",
    ("luks1", "epoch"): "luks_value",
    ("luks1", "header_seqid"): "luks_value",
    ("luks1", "checksum_alg"): "luks_value",
    ("luks1", "checksum_algorithm"): "luks_value",
    ("luks1", "csum_alg"): "luks_value",
    ("luks1", "header_checksum_alg"): "luks_value",
    ("luks1", "checksum_hex"): "luks_value",
    ("luks1", "header_checksum_hex"): "luks_value",
    ("luks1", "csum_hex"): "luks_value",
    ("luks1", "checksum_valid"): "luks_value",
    ("luks1", "header_checksum_valid"): "luks_value",
    ("luks1", "csum_valid"): "luks_value",
    ("luks1", "hdr_offset"): "luks_value",
    ("luks1", "header_offset"): "luks_value",
    ("luks1", "sector_size"): "luks_value",
    ("luks1", "sector_size_bytes"): "luks_value",
    ("luks1", "segment_sector_size"): "luks_value",
    ("luks1", "encryption_sector_size"): "luks_value",
    ("luks1", "segment_count"): "luks_value",
    ("luks1", "number_of_segments"): "luks_value",
    ("luks1", "data_segment_count"): "luks_value",
    ("luks1", "keyslots_size"): "luks_value",
    ("luks1", "keyslots_area_bytes"): "luks_value",
    ("luks1", "keyslots_size_bytes"): "luks_value",
    ("luks1", "token_count"): "luks_value",
    ("luks1", "number_of_tokens"): "luks_value",
    ("luks1", "digest_count"): "luks_value",
    ("luks1", "number_of_digests"): "luks_value",
    ("luks1", "luks_offset"): "luks_value",
    ("luks1", "header_offset_in_image"): "luks_value",
    ("luks1", "luks_header_offset"): "luks_value",
    ("luks1", "luks_start_offset"): "luks_value",
    ("luks1", "present"): "luks_value",
    ("luks1", "luks_present"): "luks_value",
    ("luks1", "is_luks"): "luks_value",
    ("luks1", "has_luks"): "luks_value",
    ("luks1", "encrypted"): "luks_value",
    ("luks1", "is_encrypted"): "luks_value",
    ("luks2", "version"): "luks_value",
    ("luks2", "luks_version"): "luks_value",
    ("luks2", "header_version"): "luks_value",
    ("luks2", "uuid"): "luks_value",
    ("luks2", "volume_uuid"): "luks_value",
    ("luks2", "header_uuid"): "luks_value",
    ("luks2", "label"): "luks_value",
    ("luks2", "volume_label"): "luks_value",
    ("luks2", "header_label"): "luks_value",
    ("luks2", "subsystem"): "luks_value",
    ("luks2", "subsystem_label"): "luks_value",
    ("luks2", "sub_label"): "luks_value",
    ("luks2", "cipher_name"): "luks_value",
    ("luks2", "cipher_algorithm"): "luks_value",
    ("luks2", "encryption_algorithm"): "luks_value",
    ("luks2", "cipher_mode"): "luks_value",
    ("luks2", "encryption_mode"): "luks_value",
    ("luks2", "cipher"): "luks_value",
    ("luks2", "cipher_spec"): "luks_value",
    ("luks2", "encryption"): "luks_value",
    ("luks2", "segment_cipher"): "luks_value",
    ("luks2", "segment_encryption"): "luks_value",
    ("luks2", "data_cipher"): "luks_value",
    ("luks2", "hash_spec"): "luks_value",
    ("luks2", "hash"): "luks_value",
    ("luks2", "hash_algorithm"): "luks_value",
    ("luks2", "digest_hash"): "luks_value",
    ("luks2", "pbkdf_hash"): "luks_value",
    ("luks2", "af_hash"): "luks_value",
    ("luks2", "payload_offset"): "luks_value",
    ("luks2", "payload_offset_sectors"): "luks_value",
    ("luks2", "data_offset_sectors"): "luks_value",
    ("luks2", "payload_offset_bytes"): "luks_value",
    ("luks2", "data_offset"): "luks_value",
    ("luks2", "data_offset_bytes"): "luks_value",
    ("luks2", "segment_offset"): "luks_value",
    ("luks2", "segment_offset_bytes"): "luks_value",
    ("luks2", "key_bytes"): "luks_value",
    ("luks2", "key_size_bytes"): "luks_value",
    ("luks2", "master_key_bytes"): "luks_value",
    ("luks2", "volume_key_bytes"): "luks_value",
    ("luks2", "key_bits"): "luks_value",
    ("luks2", "key_size_bits"): "luks_value",
    ("luks2", "key_size"): "luks_value",
    ("luks2", "mk_bits"): "luks_value",
    ("luks2", "master_key_bits"): "luks_value",
    ("luks2", "volume_key_bits"): "luks_value",
    ("luks2", "mk_digest_hex"): "luks_value",
    ("luks2", "mk_digest"): "luks_value",
    ("luks2", "master_key_digest_hex"): "luks_value",
    ("luks2", "mk_salt_hex"): "luks_value",
    ("luks2", "mk_digest_salt_hex"): "luks_value",
    ("luks2", "mk_salt"): "luks_value",
    ("luks2", "mk_iterations"): "luks_value",
    ("luks2", "mk_digest_iterations"): "luks_value",
    ("luks2", "mk_digest_iter"): "luks_value",
    ("luks2", "digest_iterations"): "luks_value",
    ("luks2", "active_key_slots"): "luks_value",
    ("luks2", "active_keyslots"): "luks_value",
    ("luks2", "enabled_key_slots"): "luks_value",
    ("luks2", "active_key_slot_indices"): "luks_value",
    ("luks2", "key_slot_indices"): "luks_value",
    ("luks2", "keyslot_ids"): "luks_value",
    ("luks2", "active_key_slot_count"): "luks_value",
    ("luks2", "active_keyslot_count"): "luks_value",
    ("luks2", "enabled_key_slot_count"): "luks_value",
    ("luks2", "key_slot_count"): "luks_value",
    ("luks2", "keyslot_count"): "luks_value",
    ("luks2", "number_of_key_slots"): "luks_value",
    ("luks2", "keyslots_count"): "luks_value",
    ("luks2", "key_material_offsets"): "luks_value",
    ("luks2", "keyslot_material_offsets"): "luks_value",
    ("luks2", "keyslot_iterations"): "luks_value",
    ("luks2", "key_slot_iterations"): "luks_value",
    ("luks2", "pbkdf"): "luks_value",
    ("luks2", "pbkdf_type"): "luks_value",
    ("luks2", "keyslot_pbkdf"): "luks_value",
    ("luks2", "kdf_type"): "luks_value",
    ("luks2", "hdr_size"): "luks_value",
    ("luks2", "header_size"): "luks_value",
    ("luks2", "header_size_bytes"): "luks_value",
    ("luks2", "metadata_size"): "luks_value",
    ("luks2", "metadata_area_bytes"): "luks_value",
    ("luks2", "metadata_size_bytes"): "luks_value",
    ("luks2", "json_size"): "luks_value",
    ("luks2", "json_area_size"): "luks_value",
    ("luks2", "json_area_bytes"): "luks_value",
    ("luks2", "seqid"): "luks_value",
    ("luks2", "sequence_id"): "luks_value",
    ("luks2", "epoch"): "luks_value",
    ("luks2", "header_seqid"): "luks_value",
    ("luks2", "checksum_alg"): "luks_value",
    ("luks2", "checksum_algorithm"): "luks_value",
    ("luks2", "csum_alg"): "luks_value",
    ("luks2", "header_checksum_alg"): "luks_value",
    ("luks2", "checksum_hex"): "luks_value",
    ("luks2", "header_checksum_hex"): "luks_value",
    ("luks2", "csum_hex"): "luks_value",
    ("luks2", "checksum_valid"): "luks_value",
    ("luks2", "header_checksum_valid"): "luks_value",
    ("luks2", "csum_valid"): "luks_value",
    ("luks2", "hdr_offset"): "luks_value",
    ("luks2", "header_offset"): "luks_value",
    ("luks2", "sector_size"): "luks_value",
    ("luks2", "sector_size_bytes"): "luks_value",
    ("luks2", "segment_sector_size"): "luks_value",
    ("luks2", "encryption_sector_size"): "luks_value",
    ("luks2", "segment_count"): "luks_value",
    ("luks2", "number_of_segments"): "luks_value",
    ("luks2", "data_segment_count"): "luks_value",
    ("luks2", "keyslots_size"): "luks_value",
    ("luks2", "keyslots_area_bytes"): "luks_value",
    ("luks2", "keyslots_size_bytes"): "luks_value",
    ("luks2", "token_count"): "luks_value",
    ("luks2", "number_of_tokens"): "luks_value",
    ("luks2", "digest_count"): "luks_value",
    ("luks2", "number_of_digests"): "luks_value",
    ("luks2", "luks_offset"): "luks_value",
    ("luks2", "header_offset_in_image"): "luks_value",
    ("luks2", "luks_header_offset"): "luks_value",
    ("luks2", "luks_start_offset"): "luks_value",
    ("luks2", "present"): "luks_value",
    ("luks2", "luks_present"): "luks_value",
    ("luks2", "is_luks"): "luks_value",
    ("luks2", "has_luks"): "luks_value",
    ("luks2", "encrypted"): "luks_value",
    ("luks2", "is_encrypted"): "luks_value",
}

_CANON = {
    "version": "version",
    "luks_version": "version",
    "header_version": "version",
    "uuid": "uuid",
    "volume_uuid": "uuid",
    "header_uuid": "uuid",
    "label": "label",
    "volume_label": "label",
    "header_label": "label",
    "subsystem": "subsystem",
    "subsystem_label": "subsystem",
    "sub_label": "subsystem",
    "cipher_name": "cipher_name",
    "cipher_algorithm": "cipher_name",
    "encryption_algorithm": "cipher_name",
    "cipher_mode": "cipher_mode",
    "encryption_mode": "cipher_mode",
    "cipher": "cipher",
    "cipher_spec": "cipher",
    "encryption": "cipher",
    "segment_cipher": "cipher",
    "segment_encryption": "cipher",
    "data_cipher": "cipher",
    "hash_spec": "hash_spec",
    "hash": "hash_spec",
    "hash_algorithm": "hash_spec",
    "digest_hash": "hash_spec",
    "pbkdf_hash": "hash_spec",
    "af_hash": "hash_spec",
    "payload_offset": "payload_offset",
    "payload_offset_sectors": "payload_offset",
    "data_offset_sectors": "payload_offset",
    "payload_offset_bytes": "payload_offset_bytes",
    "data_offset": "payload_offset_bytes",
    "data_offset_bytes": "payload_offset_bytes",
    "segment_offset": "payload_offset_bytes",
    "segment_offset_bytes": "payload_offset_bytes",
    "key_bytes": "key_bytes",
    "key_size_bytes": "key_bytes",
    "master_key_bytes": "key_bytes",
    "volume_key_bytes": "key_bytes",
    "key_bits": "key_bits",
    "key_size_bits": "key_bits",
    "key_size": "key_bits",
    "mk_bits": "key_bits",
    "master_key_bits": "key_bits",
    "volume_key_bits": "key_bits",
    "mk_digest_hex": "mk_digest_hex",
    "mk_digest": "mk_digest_hex",
    "master_key_digest_hex": "mk_digest_hex",
    "mk_salt_hex": "mk_salt_hex",
    "mk_digest_salt_hex": "mk_salt_hex",
    "mk_salt": "mk_salt_hex",
    "mk_iterations": "mk_iterations",
    "mk_digest_iterations": "mk_iterations",
    "mk_digest_iter": "mk_iterations",
    "digest_iterations": "mk_iterations",
    "active_key_slots": "active_key_slots",
    "active_keyslots": "active_key_slots",
    "enabled_key_slots": "active_key_slots",
    "active_key_slot_indices": "active_key_slots",
    "key_slot_indices": "active_key_slots",
    "keyslot_ids": "active_key_slots",
    "active_key_slot_count": "active_key_slot_count",
    "active_keyslot_count": "active_key_slot_count",
    "enabled_key_slot_count": "active_key_slot_count",
    "key_slot_count": "active_key_slot_count",
    "keyslot_count": "active_key_slot_count",
    "number_of_key_slots": "active_key_slot_count",
    "keyslots_count": "active_key_slot_count",
    "key_material_offsets": "key_material_offsets",
    "keyslot_material_offsets": "key_material_offsets",
    "keyslot_iterations": "keyslot_iterations",
    "key_slot_iterations": "keyslot_iterations",
    "pbkdf": "pbkdf",
    "pbkdf_type": "pbkdf",
    "keyslot_pbkdf": "pbkdf",
    "kdf_type": "pbkdf",
    "hdr_size": "hdr_size",
    "header_size": "hdr_size",
    "header_size_bytes": "hdr_size",
    "metadata_size": "hdr_size",
    "metadata_area_bytes": "hdr_size",
    "metadata_size_bytes": "hdr_size",
    "json_size": "json_size",
    "json_area_size": "json_size",
    "json_area_bytes": "json_size",
    "seqid": "seqid",
    "sequence_id": "seqid",
    "epoch": "seqid",
    "header_seqid": "seqid",
    "checksum_alg": "checksum_alg",
    "checksum_algorithm": "checksum_alg",
    "csum_alg": "checksum_alg",
    "header_checksum_alg": "checksum_alg",
    "checksum_hex": "checksum_hex",
    "header_checksum_hex": "checksum_hex",
    "csum_hex": "checksum_hex",
    "checksum_valid": "checksum_valid",
    "header_checksum_valid": "checksum_valid",
    "csum_valid": "checksum_valid",
    "hdr_offset": "hdr_offset",
    "header_offset": "hdr_offset",
    "sector_size": "sector_size",
    "sector_size_bytes": "sector_size",
    "segment_sector_size": "sector_size",
    "encryption_sector_size": "sector_size",
    "segment_count": "segment_count",
    "number_of_segments": "segment_count",
    "data_segment_count": "segment_count",
    "keyslots_size": "keyslots_size",
    "keyslots_area_bytes": "keyslots_size",
    "keyslots_size_bytes": "keyslots_size",
    "token_count": "token_count",
    "number_of_tokens": "token_count",
    "digest_count": "digest_count",
    "number_of_digests": "digest_count",
    "luks_offset": "luks_offset",
    "header_offset_in_image": "luks_offset",
    "luks_header_offset": "luks_offset",
    "luks_start_offset": "luks_offset",
    "present": "present",
    "luks_present": "present",
    "is_luks": "present",
    "has_luks": "present",
    "encrypted": "present",
    "is_encrypted": "present",
}

_ACTIVE, _MAGIC1, _MAGIC2 = 0x00AC71F3, b"LUKS\xba\xbe", b"SKUL\xba\xbe"


def _s(b):
    return b.split(b"\0", 1)[0].decode("latin-1").strip()


def _find(data):
    """Offset of the LUKS header in data (first 512-aligned primary magic, else a secondary), or None."""
    for magic in (_MAGIC1, _MAGIC2):
        for m in re.finditer(re.escape(magic), data):
            o = m.start()
            if o % 512 == 0 and len(data) >= o + 8 and struct.unpack_from(">H", data, o + 6)[0] in (1, 2):
                return o
    return None


def _luks1(h, o):
    if len(h) < o + 592:
        return None
    r = {"version": 1, "luks_offset": o}
    r["cipher_name"], r["cipher_mode"], r["hash_spec"] = (_s(h[o + a:o + a + 32]) for a in (8, 40, 72))
    r["cipher"] = r["cipher_name"] + ("-" + r["cipher_mode"] if r["cipher_mode"] else "")
    r["payload_offset"], r["key_bytes"] = struct.unpack_from(">II", h, o + 104)
    r["payload_offset_bytes"] = r["payload_offset"] * 512
    r["key_bits"] = r["key_bytes"] * 8
    r["mk_digest_hex"] = h[o + 112:o + 132].hex()
    r["mk_salt_hex"] = h[o + 132:o + 164].hex()
    r["mk_iterations"], = struct.unpack_from(">I", h, o + 164)
    r["uuid"] = _s(h[o + 168:o + 208])
    act, its, kmo = [], [], []
    for i in range(8):
        a, it = struct.unpack_from(">II", h, o + 208 + 48 * i)
        if a == _ACTIVE:
            act.append(i)
            its.append(it)
            kmo.append(struct.unpack_from(">I", h, o + 208 + 48 * i + 40)[0])
    r.update(active_key_slots=act, active_key_slot_count=len(act), keyslot_iterations=its, key_material_offsets=kmo,
             sector_size=512, pbkdf="pbkdf2")
    return r


def _luks2(h, o):
    if len(h) < o + 512:
        return None
    r = {"version": 2, "luks_offset": o}
    r["hdr_size"], r["seqid"] = struct.unpack_from(">QQ", h, o + 8)
    r["label"] = _s(h[o + 24:o + 72])
    r["checksum_alg"] = _s(h[o + 72:o + 104])
    r["uuid"] = _s(h[o + 168:o + 208])
    r["subsystem"] = _s(h[o + 208:o + 256])
    r["hdr_offset"], = struct.unpack_from(">Q", h, o + 256)
    csum = h[o + 448:o + 512]
    alg = r["checksum_alg"].lower()
    dlen = {"sha1": 20, "sha256": 32, "sha512": 64}.get(alg, 32)
    r["checksum_hex"] = csum[:dlen].hex()
    hs = r["hdr_size"]
    if 4096 < hs <= 4 << 20:
        r["json_size"] = hs - 4096
        if len(h) >= o + hs and alg in ("sha1", "sha256", "sha512"):
            blob = h[o:o + 448] + bytes(64) + h[o + 512:o + hs]
            r["checksum_valid"] = hashlib.new(alg, blob).digest() == csum[:dlen]
        js = h[o + 4096:o + hs].split(b"\0", 1)[0]
        try:
            j = json.loads(js.decode("utf-8"))
        except ValueError:
            j = None
        if isinstance(j, dict):
            ks, seg, dg = j.get("keyslots") or {}, j.get("segments") or {}, j.get("digests") or {}
            ids = sorted(int(k) for k in ks if str(k).isdigit())
            r["active_key_slots"], r["active_key_slot_count"] = ids, len(ids)
            r["segment_count"] = len(seg)
            r["token_count"] = len(j.get("tokens") or {})
            r["digest_count"] = len(dg)
            s0 = seg.get("0") or (seg[sorted(seg)[0]] if seg else None)
            if isinstance(s0, dict):
                enc = s0.get("encryption")
                if isinstance(enc, str):
                    r["cipher"] = enc
                    name, _, mode = enc.partition("-")
                    r["cipher_name"], r["cipher_mode"] = name, mode
                if s0.get("sector_size") is not None:
                    r["sector_size"] = int(s0["sector_size"])
                if str(s0.get("offset", "")).isdigit():
                    r["payload_offset_bytes"] = int(s0["offset"])
                    r["payload_offset"] = int(s0["offset"]) // 512
            k0 = ks.get(str(ids[0])) if ids else None
            if isinstance(k0, dict):
                if k0.get("key_size") is not None:
                    r["key_bytes"] = int(k0["key_size"])
                    r["key_bits"] = r["key_bytes"] * 8
                kdf = k0.get("kdf") or {}
                if kdf.get("type"):
                    r["pbkdf"] = kdf["type"]
                its = [(ks[str(i)].get("kdf") or {}).get("iterations") for i in ids]
                if all(isinstance(x, int) for x in its):
                    r["keyslot_iterations"] = its
            d0 = dg.get("0") or (dg[sorted(dg)[0]] if dg else None)
            if isinstance(d0, dict) and d0.get("hash"):
                r["hash_spec"] = d0["hash"]
                if isinstance(d0.get("iterations"), int):
                    r["mk_iterations"] = d0["iterations"]
            cfg = j.get("config") or {}
            if str(cfg.get("keyslots_size", "")).isdigit():
                r["keyslots_size"] = int(cfg["keyslots_size"])
    return r


def parse(data):
    """The LUKS header as a flat dict, or None (no LUKS magic)."""
    if not data:
        return None
    o = _find(data)
    if o is None:
        return None
    ver = struct.unpack_from(">H", data, o + 6)[0]
    return _luks1(data, o) if ver == 1 else _luks2(data, o)


def luks_value(data, ctx):
    if data is None:
        return None
    try:
        key = _CANON.get(ctx.get("field") or "")
        if key is None:
            return None
        r = parse(data)
        if key == "present":
            return r is not None
        if r is None:
            return "none"
        fmt = ctx.get("fmt") or "luks"
        if fmt in ("luks1", "luks2") and r["version"] != int(fmt[-1]):
            return "none"
        v = r.get(key)
        if v is None or v == "":
            return "none"
        return v
    except Exception:
        return None
