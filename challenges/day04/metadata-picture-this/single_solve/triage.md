# Triage: metadata-forensics-day-04-picture-this

**Prompt:** A dozen photographs have been resized, renamed, and shuffled. Reconstruct their true dimensions and find the image whose presentation does not match its structure.

**1 answer(s) expected.** Formats:
- `d04-jpeg-001-jpeg-sof-dimensions-pixels`: Determine jpeg.sof_dimensions_pixels for camera-001.jpg.  _(fmt: exact artifact-derived value only, without quotes or explanatory text unless quo; norm: trim)_

## Artifacts

- **metadata-day-04-evidence.zip** (1698 bytes) sha256 `27bf2675d0c7e6cb…`
  - file: Zip archive data, made by v2.0 UNIX, extract using at least v2.0, last modified Jan 01 2026 00:00:00, uncompressed size 3025, method=deflate
  - signature: ZIP/APK/JAR/OOXML container
  - archive with 1 entries: ['camera-001.jpg']
  - **camera-001.jpg** (3025 bytes) sha256 `bc79a152e217a8e4…`
    - file: JPEG image data, baseline, precision 8, 257x146, components 3
    - signature: JPEG image -> $metadata-forensics
    - exiftool:
        [ExifTool]      ExifToolVersion                 : 13.59
        [File]          FileName                        : camera-001.jpg
        [File]          Directory                       : /home/testpwn/huntress-2026/.run/tmp/triage-metadata-day-04-evidence-0
        [File]          FileSize                        : 3.0 kB
        [File]          FileModifyDate                  : 2026:10:04 21:01:45+08:00
        [File]          FileAccessDate                  : 2026:10:04 21:01:45+08:00
        [File]          FileInodeChangeDate             : 2026:10:04 21:01:45+08:00
        [File]          FilePermissions                 : -rw-r--r--
        [File]          FileType                        : JPEG
        [File]          FileTypeExtension               : jpg
        [File]          MIMEType                        : image/jpeg
        [File]          ImageWidth                      : 257
        [File]          ImageHeight                     : 146
        [File]          EncodingProcess                 : Baseline DCT, Huffman coding
        [File]          BitsPerSample                   : 8
        [File]          ColorComponents                 : 3
        [File]          YCbCrSubSampling                : YCbCr4:2:0 (2 2)
        [Composite]     ImageSize                       : 257x146
        [Composite]     Megapixels                      : 0.038

_Deterministic triage (no LLM). Verify against the bytes; see the routed lane skill._