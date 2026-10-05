# Chunk Norris (Day 5, metadata-forensics) — PNG chunk structure
Concept: walk PNG chunks (length/type/data/CRC) from the signature; the declared geometry is IHDR width/height.
Confirmed: png.ihdr_dimensions_pixels -> '<width>x<height>' (lib.knowledge.PNG_DIMENSIONS_FMT), e.g. 269x153.
Variant axes handled: member/zip names (find_artifact_hinted), set prefixes, question order, extra/non-standard chunks,
trailing bytes after IEND. Unconfirmed best-effort fields: width/height/bit_depth/color_type, chunk_count,
unexpected chunk name / has_passenger / trailing bytes, geometry_valid (inflated IDAT == expected raw size), crc_valid.
