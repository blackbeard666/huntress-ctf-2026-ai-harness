"""Claimed recording DEVICE / producer of a video (fmt media; aliases video, av, mp4, mov) -- prebuilt, SPECULATIVE.

D18 flavor "the recording that could not have come from the claimed device". MP4/MOV sources, verbatim strings:
  - QuickTime metadata: moov/meta (and moov/udta/meta) `keys` (mdta namespace) + `ilst` items indexed 1-based into
    the keys: com.apple.quicktime.make/.model/.software/.creationdate/.location.ISO6709/.camera.lens_model,
    com.android.manufacturer/.model/.version/.capture.fps (float32 data type 23 -> "%f" like ffmpeg mov.c).
  - udta international text atoms (2-byte len + 2-byte lang + text): \xa9mak make, \xa9mod model, \xa9swr software,
    \xa9too encoder, \xa9xyz location, \xa9day date; GoPro udta FIRM (firmware string), GPMF presence.
  - device_make = apple make > com.android.manufacturer > \xa9mak; device_model likewise; device_software = apple
    software > \xa9swr > com.android.version > GoPro FIRM > MKV Info WritingApp > AVI ISFT.
  - handler_name = first video trak mdia/hdlr name (QuickTime Pascal or ISO C string; ffprobe stream handler_name:
    `Core Media Video` Apple, `VideoHandle` Android, `VideoHandler` Lavf).
  - video_encoder / compressor_name = stsd VisualSampleEntry compressorname (Pascal @entry+50, len <= 31) = ffprobe
    stream tag `encoder` (`Lavc61.3.100 libx264`, `H.264`, `AVC Coding`). Container encoder (\xa9too) stays in
    media_tags (media.encoder); media.tag_<mdta key with _ for .> falls back to media_device.tag_fallback.
  - mdta_keys: key names in stored order. is_screen_recording: DIAGNOSTIC heuristic only (no device keys + display
    sized / odd dims + VFR stts).
Parseable container without the key -> "none"; non-media member -> "none"; unknown bytes -> None."""
import struct

FIELDS = {
    ("media", "device_make"): "device_value",
    ("media", "device_model"): "device_value",
    ("media", "device_software"): "device_value",
    ("media", "device_manufacturer"): "device_value",
    ("media", "make"): "device_value",
    ("media", "model"): "device_value",
    ("media", "manufacturer"): "device_value",
    ("media", "camera_make"): "device_value",
    ("media", "camera_model"): "device_value",
    ("media", "camera_software"): "device_value",
    ("media", "recording_device_make"): "device_value",
    ("media", "recording_device_model"): "device_value",
    ("media", "recording_device_software"): "device_value",
    ("media", "recording_device"): "device_value",
    ("media", "device"): "device_value",
    ("media", "capture_device"): "device_value",
    ("media", "claimed_device_make"): "device_value",
    ("media", "claimed_device_model"): "device_value",
    ("media", "claimed_device_software"): "device_value",
    ("media", "quicktime_make"): "device_value",
    ("media", "quicktime_model"): "device_value",
    ("media", "quicktime_software"): "device_value",
    ("media", "apple_make"): "device_value",
    ("media", "apple_model"): "device_value",
    ("media", "apple_software"): "device_value",
    ("media", "udta_make"): "device_value",
    ("media", "udta_model"): "device_value",
    ("media", "creation_date"): "device_value",
    ("media", "creationdate"): "device_value",
    ("media", "quicktime_creation_date"): "device_value",
    ("media", "quicktime_creationdate"): "device_value",
    ("media", "device_creation_date"): "device_value",
    ("media", "location"): "device_value",
    ("media", "location_iso6709"): "device_value",
    ("media", "quicktime_location_iso6709"): "device_value",
    ("media", "iso6709_location"): "device_value",
    ("media", "gps_location"): "device_value",
    ("media", "gps_coordinates"): "device_value",
    ("media", "gps_coordinates_iso6709"): "device_value",
    ("media", "lens_model"): "device_value",
    ("media", "camera_lens_model"): "device_value",
    ("media", "quicktime_lens_model"): "device_value",
    ("media", "android_version"): "device_value",
    ("media", "android_manufacturer"): "device_value",
    ("media", "android_model"): "device_value",
    ("media", "android_capture_fps"): "device_value",
    ("media", "capture_fps"): "device_value",
    ("media", "firmware"): "device_value",
    ("media", "firmware_version"): "device_value",
    ("media", "gopro_firmware"): "device_value",
    ("media", "handler_name"): "handler_name",
    ("media", "primary_video_handler_name"): "handler_name",
    ("media", "video_handler_name"): "handler_name",
    ("media", "video_stream_handler_name"): "handler_name",
    ("media", "first_video_handler_name"): "handler_name",
    ("media", "video_encoder"): "stream_encoder",
    ("media", "primary_video_encoder"): "stream_encoder",
    ("media", "stream_encoder"): "stream_encoder",
    ("media", "video_stream_encoder"): "stream_encoder",
    ("media", "primary_video_stream_encoder"): "stream_encoder",
    ("media", "compressor_name"): "stream_encoder",
    ("media", "compressorname"): "stream_encoder",
    ("media", "stsd_compressor_name"): "stream_encoder",
    ("media", "primary_video_compressor_name"): "stream_encoder",
    ("media", "video_compressor_name"): "stream_encoder",
    ("media", "codec_encoder"): "stream_encoder",
    ("media", "mdta_keys"): "mdta_keys",
    ("media", "quicktime_keys"): "mdta_keys",
    ("media", "metadata_keys"): "mdta_keys",
    ("media", "quicktime_metadata_keys"): "mdta_keys",
    ("media", "mdta_key_names"): "mdta_keys",
    ("media", "is_screen_recording"): "is_screen_recording",
    ("media", "screen_recording"): "is_screen_recording",
    ("media", "likely_screen_recording"): "is_screen_recording",
    ("media", "screen_recording_suspected"): "is_screen_recording",
    ("video", "device_make"): "device_value",
    ("video", "device_model"): "device_value",
    ("video", "device_software"): "device_value",
    ("video", "device_manufacturer"): "device_value",
    ("video", "make"): "device_value",
    ("video", "model"): "device_value",
    ("video", "manufacturer"): "device_value",
    ("video", "camera_make"): "device_value",
    ("video", "camera_model"): "device_value",
    ("video", "camera_software"): "device_value",
    ("video", "recording_device_make"): "device_value",
    ("video", "recording_device_model"): "device_value",
    ("video", "recording_device_software"): "device_value",
    ("video", "recording_device"): "device_value",
    ("video", "device"): "device_value",
    ("video", "capture_device"): "device_value",
    ("video", "claimed_device_make"): "device_value",
    ("video", "claimed_device_model"): "device_value",
    ("video", "claimed_device_software"): "device_value",
    ("video", "quicktime_make"): "device_value",
    ("video", "quicktime_model"): "device_value",
    ("video", "quicktime_software"): "device_value",
    ("video", "apple_make"): "device_value",
    ("video", "apple_model"): "device_value",
    ("video", "apple_software"): "device_value",
    ("video", "udta_make"): "device_value",
    ("video", "udta_model"): "device_value",
    ("video", "creation_date"): "device_value",
    ("video", "creationdate"): "device_value",
    ("video", "quicktime_creation_date"): "device_value",
    ("video", "quicktime_creationdate"): "device_value",
    ("video", "device_creation_date"): "device_value",
    ("video", "location"): "device_value",
    ("video", "location_iso6709"): "device_value",
    ("video", "quicktime_location_iso6709"): "device_value",
    ("video", "iso6709_location"): "device_value",
    ("video", "gps_location"): "device_value",
    ("video", "gps_coordinates"): "device_value",
    ("video", "gps_coordinates_iso6709"): "device_value",
    ("video", "lens_model"): "device_value",
    ("video", "camera_lens_model"): "device_value",
    ("video", "quicktime_lens_model"): "device_value",
    ("video", "android_version"): "device_value",
    ("video", "android_manufacturer"): "device_value",
    ("video", "android_model"): "device_value",
    ("video", "android_capture_fps"): "device_value",
    ("video", "capture_fps"): "device_value",
    ("video", "firmware"): "device_value",
    ("video", "firmware_version"): "device_value",
    ("video", "gopro_firmware"): "device_value",
    ("video", "handler_name"): "handler_name",
    ("video", "primary_video_handler_name"): "handler_name",
    ("video", "video_handler_name"): "handler_name",
    ("video", "video_stream_handler_name"): "handler_name",
    ("video", "first_video_handler_name"): "handler_name",
    ("video", "video_encoder"): "stream_encoder",
    ("video", "primary_video_encoder"): "stream_encoder",
    ("video", "stream_encoder"): "stream_encoder",
    ("video", "video_stream_encoder"): "stream_encoder",
    ("video", "primary_video_stream_encoder"): "stream_encoder",
    ("video", "compressor_name"): "stream_encoder",
    ("video", "compressorname"): "stream_encoder",
    ("video", "stsd_compressor_name"): "stream_encoder",
    ("video", "primary_video_compressor_name"): "stream_encoder",
    ("video", "video_compressor_name"): "stream_encoder",
    ("video", "codec_encoder"): "stream_encoder",
    ("video", "mdta_keys"): "mdta_keys",
    ("video", "quicktime_keys"): "mdta_keys",
    ("video", "metadata_keys"): "mdta_keys",
    ("video", "quicktime_metadata_keys"): "mdta_keys",
    ("video", "mdta_key_names"): "mdta_keys",
    ("video", "is_screen_recording"): "is_screen_recording",
    ("video", "screen_recording"): "is_screen_recording",
    ("video", "likely_screen_recording"): "is_screen_recording",
    ("video", "screen_recording_suspected"): "is_screen_recording",
    ("av", "device_make"): "device_value",
    ("av", "device_model"): "device_value",
    ("av", "device_software"): "device_value",
    ("av", "device_manufacturer"): "device_value",
    ("av", "make"): "device_value",
    ("av", "model"): "device_value",
    ("av", "manufacturer"): "device_value",
    ("av", "camera_make"): "device_value",
    ("av", "camera_model"): "device_value",
    ("av", "camera_software"): "device_value",
    ("av", "recording_device_make"): "device_value",
    ("av", "recording_device_model"): "device_value",
    ("av", "recording_device_software"): "device_value",
    ("av", "recording_device"): "device_value",
    ("av", "device"): "device_value",
    ("av", "capture_device"): "device_value",
    ("av", "claimed_device_make"): "device_value",
    ("av", "claimed_device_model"): "device_value",
    ("av", "claimed_device_software"): "device_value",
    ("av", "quicktime_make"): "device_value",
    ("av", "quicktime_model"): "device_value",
    ("av", "quicktime_software"): "device_value",
    ("av", "apple_make"): "device_value",
    ("av", "apple_model"): "device_value",
    ("av", "apple_software"): "device_value",
    ("av", "udta_make"): "device_value",
    ("av", "udta_model"): "device_value",
    ("av", "creation_date"): "device_value",
    ("av", "creationdate"): "device_value",
    ("av", "quicktime_creation_date"): "device_value",
    ("av", "quicktime_creationdate"): "device_value",
    ("av", "device_creation_date"): "device_value",
    ("av", "location"): "device_value",
    ("av", "location_iso6709"): "device_value",
    ("av", "quicktime_location_iso6709"): "device_value",
    ("av", "iso6709_location"): "device_value",
    ("av", "gps_location"): "device_value",
    ("av", "gps_coordinates"): "device_value",
    ("av", "gps_coordinates_iso6709"): "device_value",
    ("av", "lens_model"): "device_value",
    ("av", "camera_lens_model"): "device_value",
    ("av", "quicktime_lens_model"): "device_value",
    ("av", "android_version"): "device_value",
    ("av", "android_manufacturer"): "device_value",
    ("av", "android_model"): "device_value",
    ("av", "android_capture_fps"): "device_value",
    ("av", "capture_fps"): "device_value",
    ("av", "firmware"): "device_value",
    ("av", "firmware_version"): "device_value",
    ("av", "gopro_firmware"): "device_value",
    ("av", "handler_name"): "handler_name",
    ("av", "primary_video_handler_name"): "handler_name",
    ("av", "video_handler_name"): "handler_name",
    ("av", "video_stream_handler_name"): "handler_name",
    ("av", "first_video_handler_name"): "handler_name",
    ("av", "video_encoder"): "stream_encoder",
    ("av", "primary_video_encoder"): "stream_encoder",
    ("av", "stream_encoder"): "stream_encoder",
    ("av", "video_stream_encoder"): "stream_encoder",
    ("av", "primary_video_stream_encoder"): "stream_encoder",
    ("av", "compressor_name"): "stream_encoder",
    ("av", "compressorname"): "stream_encoder",
    ("av", "stsd_compressor_name"): "stream_encoder",
    ("av", "primary_video_compressor_name"): "stream_encoder",
    ("av", "video_compressor_name"): "stream_encoder",
    ("av", "codec_encoder"): "stream_encoder",
    ("av", "mdta_keys"): "mdta_keys",
    ("av", "quicktime_keys"): "mdta_keys",
    ("av", "metadata_keys"): "mdta_keys",
    ("av", "quicktime_metadata_keys"): "mdta_keys",
    ("av", "mdta_key_names"): "mdta_keys",
    ("av", "is_screen_recording"): "is_screen_recording",
    ("av", "screen_recording"): "is_screen_recording",
    ("av", "likely_screen_recording"): "is_screen_recording",
    ("av", "screen_recording_suspected"): "is_screen_recording",
    ("mp4", "device_make"): "device_value",
    ("mp4", "device_model"): "device_value",
    ("mp4", "device_software"): "device_value",
    ("mp4", "device_manufacturer"): "device_value",
    ("mp4", "make"): "device_value",
    ("mp4", "model"): "device_value",
    ("mp4", "manufacturer"): "device_value",
    ("mp4", "camera_make"): "device_value",
    ("mp4", "camera_model"): "device_value",
    ("mp4", "camera_software"): "device_value",
    ("mp4", "recording_device_make"): "device_value",
    ("mp4", "recording_device_model"): "device_value",
    ("mp4", "recording_device_software"): "device_value",
    ("mp4", "recording_device"): "device_value",
    ("mp4", "device"): "device_value",
    ("mp4", "capture_device"): "device_value",
    ("mp4", "claimed_device_make"): "device_value",
    ("mp4", "claimed_device_model"): "device_value",
    ("mp4", "claimed_device_software"): "device_value",
    ("mp4", "quicktime_make"): "device_value",
    ("mp4", "quicktime_model"): "device_value",
    ("mp4", "quicktime_software"): "device_value",
    ("mp4", "apple_make"): "device_value",
    ("mp4", "apple_model"): "device_value",
    ("mp4", "apple_software"): "device_value",
    ("mp4", "udta_make"): "device_value",
    ("mp4", "udta_model"): "device_value",
    ("mp4", "creation_date"): "device_value",
    ("mp4", "creationdate"): "device_value",
    ("mp4", "quicktime_creation_date"): "device_value",
    ("mp4", "quicktime_creationdate"): "device_value",
    ("mp4", "device_creation_date"): "device_value",
    ("mp4", "location"): "device_value",
    ("mp4", "location_iso6709"): "device_value",
    ("mp4", "quicktime_location_iso6709"): "device_value",
    ("mp4", "iso6709_location"): "device_value",
    ("mp4", "gps_location"): "device_value",
    ("mp4", "gps_coordinates"): "device_value",
    ("mp4", "gps_coordinates_iso6709"): "device_value",
    ("mp4", "lens_model"): "device_value",
    ("mp4", "camera_lens_model"): "device_value",
    ("mp4", "quicktime_lens_model"): "device_value",
    ("mp4", "android_version"): "device_value",
    ("mp4", "android_manufacturer"): "device_value",
    ("mp4", "android_model"): "device_value",
    ("mp4", "android_capture_fps"): "device_value",
    ("mp4", "capture_fps"): "device_value",
    ("mp4", "firmware"): "device_value",
    ("mp4", "firmware_version"): "device_value",
    ("mp4", "gopro_firmware"): "device_value",
    ("mp4", "handler_name"): "handler_name",
    ("mp4", "primary_video_handler_name"): "handler_name",
    ("mp4", "video_handler_name"): "handler_name",
    ("mp4", "video_stream_handler_name"): "handler_name",
    ("mp4", "first_video_handler_name"): "handler_name",
    ("mp4", "video_encoder"): "stream_encoder",
    ("mp4", "primary_video_encoder"): "stream_encoder",
    ("mp4", "stream_encoder"): "stream_encoder",
    ("mp4", "video_stream_encoder"): "stream_encoder",
    ("mp4", "primary_video_stream_encoder"): "stream_encoder",
    ("mp4", "compressor_name"): "stream_encoder",
    ("mp4", "compressorname"): "stream_encoder",
    ("mp4", "stsd_compressor_name"): "stream_encoder",
    ("mp4", "primary_video_compressor_name"): "stream_encoder",
    ("mp4", "video_compressor_name"): "stream_encoder",
    ("mp4", "codec_encoder"): "stream_encoder",
    ("mp4", "mdta_keys"): "mdta_keys",
    ("mp4", "quicktime_keys"): "mdta_keys",
    ("mp4", "metadata_keys"): "mdta_keys",
    ("mp4", "quicktime_metadata_keys"): "mdta_keys",
    ("mp4", "mdta_key_names"): "mdta_keys",
    ("mp4", "is_screen_recording"): "is_screen_recording",
    ("mp4", "screen_recording"): "is_screen_recording",
    ("mp4", "likely_screen_recording"): "is_screen_recording",
    ("mp4", "screen_recording_suspected"): "is_screen_recording",
    ("mov", "device_make"): "device_value",
    ("mov", "device_model"): "device_value",
    ("mov", "device_software"): "device_value",
    ("mov", "device_manufacturer"): "device_value",
    ("mov", "make"): "device_value",
    ("mov", "model"): "device_value",
    ("mov", "manufacturer"): "device_value",
    ("mov", "camera_make"): "device_value",
    ("mov", "camera_model"): "device_value",
    ("mov", "camera_software"): "device_value",
    ("mov", "recording_device_make"): "device_value",
    ("mov", "recording_device_model"): "device_value",
    ("mov", "recording_device_software"): "device_value",
    ("mov", "recording_device"): "device_value",
    ("mov", "device"): "device_value",
    ("mov", "capture_device"): "device_value",
    ("mov", "claimed_device_make"): "device_value",
    ("mov", "claimed_device_model"): "device_value",
    ("mov", "claimed_device_software"): "device_value",
    ("mov", "quicktime_make"): "device_value",
    ("mov", "quicktime_model"): "device_value",
    ("mov", "quicktime_software"): "device_value",
    ("mov", "apple_make"): "device_value",
    ("mov", "apple_model"): "device_value",
    ("mov", "apple_software"): "device_value",
    ("mov", "udta_make"): "device_value",
    ("mov", "udta_model"): "device_value",
    ("mov", "creation_date"): "device_value",
    ("mov", "creationdate"): "device_value",
    ("mov", "quicktime_creation_date"): "device_value",
    ("mov", "quicktime_creationdate"): "device_value",
    ("mov", "device_creation_date"): "device_value",
    ("mov", "location"): "device_value",
    ("mov", "location_iso6709"): "device_value",
    ("mov", "quicktime_location_iso6709"): "device_value",
    ("mov", "iso6709_location"): "device_value",
    ("mov", "gps_location"): "device_value",
    ("mov", "gps_coordinates"): "device_value",
    ("mov", "gps_coordinates_iso6709"): "device_value",
    ("mov", "lens_model"): "device_value",
    ("mov", "camera_lens_model"): "device_value",
    ("mov", "quicktime_lens_model"): "device_value",
    ("mov", "android_version"): "device_value",
    ("mov", "android_manufacturer"): "device_value",
    ("mov", "android_model"): "device_value",
    ("mov", "android_capture_fps"): "device_value",
    ("mov", "capture_fps"): "device_value",
    ("mov", "firmware"): "device_value",
    ("mov", "firmware_version"): "device_value",
    ("mov", "gopro_firmware"): "device_value",
    ("mov", "handler_name"): "handler_name",
    ("mov", "primary_video_handler_name"): "handler_name",
    ("mov", "video_handler_name"): "handler_name",
    ("mov", "video_stream_handler_name"): "handler_name",
    ("mov", "first_video_handler_name"): "handler_name",
    ("mov", "video_encoder"): "stream_encoder",
    ("mov", "primary_video_encoder"): "stream_encoder",
    ("mov", "stream_encoder"): "stream_encoder",
    ("mov", "video_stream_encoder"): "stream_encoder",
    ("mov", "primary_video_stream_encoder"): "stream_encoder",
    ("mov", "compressor_name"): "stream_encoder",
    ("mov", "compressorname"): "stream_encoder",
    ("mov", "stsd_compressor_name"): "stream_encoder",
    ("mov", "primary_video_compressor_name"): "stream_encoder",
    ("mov", "video_compressor_name"): "stream_encoder",
    ("mov", "codec_encoder"): "stream_encoder",
    ("mov", "mdta_keys"): "mdta_keys",
    ("mov", "quicktime_keys"): "mdta_keys",
    ("mov", "metadata_keys"): "mdta_keys",
    ("mov", "quicktime_metadata_keys"): "mdta_keys",
    ("mov", "mdta_key_names"): "mdta_keys",
    ("mov", "is_screen_recording"): "is_screen_recording",
    ("mov", "screen_recording"): "is_screen_recording",
    ("mov", "likely_screen_recording"): "is_screen_recording",
    ("mov", "screen_recording_suspected"): "is_screen_recording",
}

_NON_MEDIA = (b"\x89PNG", b"\xff\xd8\xff", b"%PDF", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\xd0\xcf\x11\xe0",
              b"GIF8", b"BM", b"7z\xbc\xaf", b"Rar!", b"\x1f\x8b")
_MP4_TOP = (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip", b"pnot")
# QuickTime udta 'international text' atoms -> our device keys (ffmpeg mov.c: \xa9mak make, \xa9mod model,
# \xa9swr encoder... we keep \xa9swr as the device SOFTWARE string, \xa9too as the container encoder).
_UDTA = {b"\xa9mak": "make", b"\xa9mod": "model", b"\xa9swr": "software", b"\xa9too": "encoder", b"\xa9xyz": "location",
         b"\xa9day": "date", b"\xa9cmt": "comment", b"\xa9nam": "title", b"\xa9inf": "information"}
_FIELD_KEYS = {
    "make": (("mdta", "com.apple.quicktime.make"), ("mdta", "com.android.manufacturer"), ("udta", "make")),
    "model": (("mdta", "com.apple.quicktime.model"), ("mdta", "com.android.model"), ("udta", "model")),
    "software": (("mdta", "com.apple.quicktime.software"), ("udta", "software"), ("mdta", "com.android.version"),
                 ("raw", "FIRM"), ("mkv", "WritingApp"), ("avi", "ISFT")),
    "creationdate": (("mdta", "com.apple.quicktime.creationdate"), ("udta", "date")),
    "location": (("mdta", "com.apple.quicktime.location.ISO6709"), ("udta", "location")),
    "lens_model": (("mdta", "com.apple.quicktime.camera.lens_model"),),
    "android_version": (("mdta", "com.android.version"),),
    "android_manufacturer": (("mdta", "com.android.manufacturer"),),
    "android_model": (("mdta", "com.android.model"),),
    "android_capture_fps": (("mdta", "com.android.capture.fps"),),
    "firmware": (("raw", "FIRM"),),
}
# Display-panel sized frames (portrait or landscape) typical of iOS/Android/desktop screen captures.
_SCREEN = {(886, 1920), (1170, 2532), (1179, 2556), (1284, 2778), (1290, 2796), (1125, 2436), (828, 1792),
           (1242, 2688), (750, 1334), (1080, 2340), (1080, 2400), (1440, 3200), (1440, 3088), (1080, 2220),
           (2560, 1600), (2880, 1800), (1440, 900), (1366, 768), (3024, 1964), (3456, 2234), (2532, 1170)}


def _boxes(b, s, e):
    while s + 8 <= e:
        sz, = struct.unpack_from(">I", b, s)
        typ, hl = b[s + 4:s + 8], 8
        if sz == 1 and s + 16 <= e:
            sz, hl = struct.unpack_from(">Q", b, s + 8)[0], 16
        elif sz == 0:
            sz = e - s
        if sz < hl or s + sz > e:
            return
        yield typ, s + hl, s + sz
        s += sz


def _child(b, s, e, typ):
    for t, cs, ce in _boxes(b, s, e):
        if t == typ:
            return cs, ce
    return None


def _path(b, s, e, *typs):
    r = (s, e)
    for t in typs:
        r = _child(b, r[0], r[1], t) if r else None
    return r


def _data_value(b, s, e):
    """First `data` atom of an ilst item: (well-known type 1 utf-8, 2 utf-16, 21/22 int, 23 float32 -> '%f' like
    ffmpeg mov_read_udta_string, 24 float64)."""
    for t, cs, ce in _boxes(b, s, e):
        if t != b"data" or ce - cs < 8:
            continue
        typ = int.from_bytes(b[cs + 1:cs + 4], "big")
        p = b[cs + 8:ce]
        if typ == 23 and len(p) == 4:
            return "%f" % struct.unpack(">f", p)[0]
        if typ == 24 and len(p) == 8:
            return "%f" % struct.unpack(">d", p)[0]
        if typ in (21, 22) and len(p) in (1, 2, 4, 8):
            return str(int.from_bytes(p, "big", signed=typ == 21))
        return p.decode("utf-16-be" if typ == 2 else "utf-8", "replace").rstrip("\0")
    return None


def _meta(b, s, e, mdta, ilst4):
    """A meta box (QuickTime: no full-box header; ISO: 4-byte version/flags): `keys` (mdta namespace) + `ilst`
    whose item types are 1-based key indexes. Non-mdta ilst items (\\xa9mak ...) go to ilst4."""
    ms = s if b[s + 4:s + 8] in (b"hdlr", b"keys", b"ilst") else s + 4
    names = []
    ks = _child(b, ms, e, b"keys")
    if ks and ks[1] - ks[0] >= 8:
        n, = struct.unpack_from(">I", b, ks[0] + 4)
        p = ks[0] + 8
        for _ in range(min(n, 4096)):
            if p + 8 > ks[1]:
                break
            sz, = struct.unpack_from(">I", b, p)
            if sz < 8 or p + sz > ks[1]:
                break
            names.append(b[p + 8:p + sz].decode("utf-8", "replace"))
            p += sz
    il = _child(b, ms, e, b"ilst")
    if il is None:
        return
    for it, ics, ice in _boxes(b, il[0], il[1]):
        idx = int.from_bytes(it, "big")
        v = _data_value(b, ics, ice)
        if v is None:
            continue
        if names and 1 <= idx <= len(names):
            mdta.setdefault(names[idx - 1], v)
        else:
            ilst4.setdefault(it, v)


def _udta(b, s, e, out, ilst4, mdta, raw):
    for t, cs, ce in _boxes(b, s, e):
        if t == b"meta":
            _meta(b, cs, ce, mdta, ilst4)
        elif t[:1] == b"\xa9" and ce - cs >= 4:
            ln, = struct.unpack_from(">H", b, cs)
            if cs + 4 + ln <= ce and ln:                       # 2-byte length + 2-byte language + text
                out.setdefault(t, b[cs + 4:cs + 4 + ln].decode("utf-8", "replace").rstrip("\0"))
            else:                                              # iTunes-style data child inside udta
                v = _data_value(b, cs, ce)
                if v is not None:
                    out.setdefault(t, v)
        elif t in (b"FIRM", b"LENS", b"CAME", b"MUID"):     # GoPro udta raw strings
            raw.setdefault(t.decode(), b[cs:ce].split(b"\0")[0].decode("latin-1").strip())
        elif t == b"GPMF":
            raw.setdefault("GPMF", "present")


def _mp4(b):
    if b[4:8] not in _MP4_TOP:
        return None
    moov = None
    for t, s, e in _boxes(b, 0, len(b)):
        if t == b"moov":
            moov = (s, e)
    if moov is None:
        return None
    mdta, udta, ilst4, raw, streams = {}, {}, {}, {}, []
    for t, cs, ce in _boxes(b, *moov):
        if t == b"meta":
            _meta(b, cs, ce, mdta, ilst4)
        elif t == b"udta":
            _udta(b, cs, ce, udta, ilst4, mdta, raw)
        elif t == b"trak":
            st = {"type": None, "handler_name": None, "encoder": None, "w": 0, "h": 0, "deltas": set()}
            md = _child(b, cs, ce, b"mdia")
            if md:
                hd = _child(b, md[0], md[1], b"hdlr")
                if hd and hd[1] - hd[0] >= 24:
                    st["type"] = b[hd[0] + 8:hd[0] + 12]
                    nm = b[hd[0] + 24:hd[1]]
                    if nm[:1] and nm[0] and nm[0] == len(nm.rstrip(b"\0")) - 1:
                        nm = nm[1:]                             # QuickTime Pascal component name
                    st["handler_name"] = nm.split(b"\0")[0].decode("utf-8", "replace").strip() or None
                stbl = _path(b, md[0], md[1], b"minf", b"stbl")
                sd = _child(b, stbl[0], stbl[1], b"stsd") if stbl else None
                if sd and st["type"] == b"vide" and sd[0] + 8 + 86 <= sd[1]:
                    es = sd[0] + 8                              # VisualSampleEntry: compressorname @ entry+50
                    st["w"], st["h"] = struct.unpack_from(">HH", b, es + 32)
                    n = b[es + 50]
                    if 0 < n <= 31:
                        st["encoder"] = b[es + 51:es + 51 + n].decode("utf-8", "replace").rstrip("\0") or None
                ts = _child(b, stbl[0], stbl[1], b"stts") if stbl else None
                if ts and ts[1] - ts[0] >= 8:
                    n, = struct.unpack_from(">I", b, ts[0] + 4)
                    for i in range(min(n, 4096)):
                        o = ts[0] + 8 + 8 * i
                        if o + 8 > ts[1]:
                            break
                        st["deltas"].add(struct.unpack_from(">I", b, o + 4)[0])
            streams.append(st)
    for k, v in list(udta.items()):
        if k in _UDTA:
            udta.setdefault(_UDTA[k], v)
    for k, v in list(ilst4.items()):
        if k in _UDTA:
            udta.setdefault(_UDTA[k], v)
    return {"kind": "mp4", "mdta": mdta, "udta": udta, "raw": raw, "streams": streams}


def _ebml_scan(b, ids):
    """Shallow Matroska scan for Info string elements (MuxingApp 0x4D80, WritingApp 0x5741)."""
    out = {}
    for name, eid in ids.items():
        i = b.find(eid)
        if i < 0 or i + len(eid) >= len(b):
            continue
        c = b[i + len(eid)]
        ln = 0
        for w in range(1, 9):
            if c & (0x80 >> w - 1):
                ln = int.from_bytes(b[i + len(eid):i + len(eid) + w], "big") & ((1 << (7 * w)) - 1)
                p = i + len(eid) + w
                break
        else:
            continue
        if 0 < ln < 512:
            out[name] = b[p:p + ln].decode("utf-8", "replace").rstrip("\0")
    return out


def _parse(b):
    r = _mp4(b)
    if r is not None:
        return r
    if b[:4] == b"\x1a\x45\xdf\xa3":
        return {"kind": "mkv", "mkv": _ebml_scan(b[:1 << 20], {"MuxingApp": b"\x4d\x80", "WritingApp": b"\x57\x41"})}
    if b[:4] == b"RIFF" and b[8:12] == b"AVI ":
        out, i = {}, b.find(b"ISFT")
        if i >= 0 and i + 8 <= len(b):
            ln, = struct.unpack_from("<I", b, i + 4)
            out["ISFT"] = b[i + 8:i + 8 + ln].split(b"\0")[0].decode("latin-1").strip()
        return {"kind": "avi", "avi": out}
    if b[:4] in (b"OggS", b"fLaC", b"RIFF") or b[:3] == b"ID3":
        return {"kind": "other"}
    return None


def _load(data):
    if data is None:
        return None
    b = bytes(data)
    try:
        r = _parse(b)
    except (ValueError, IndexError, struct.error, OverflowError, TypeError):
        r = None
    if r is None:
        if b.startswith(_NON_MEDIA) or (b[:512] and all(c in b"\t\n\r" or 32 <= c < 127 for c in b[:512])):
            return "none"
        return None
    return r


def _lookup(r, src, key):
    if src == "mdta":
        d = r.get("mdta") or {}
        if key in d:
            return d[key]
        lk = key.lower()
        return next((v for k, v in d.items() if k.lower() == lk), None)
    if src == "udta":
        return (r.get("udta") or {}).get(key)
    if src == "raw":
        return (r.get("raw") or {}).get(key)
    return (r.get(src) or {}).get(key)


def _first(r, which):
    for src, key in _FIELD_KEYS[which]:
        v = _lookup(r, src, key)
        if v is not None and v.strip():
            return v.strip()
    return "none"


def _video(r):
    return next((s for s in r.get("streams") or () if s["type"] == b"vide"), None)


_KIND = (("lens", "lens_model"), ("android_capture_fps", "android_capture_fps"), ("capture_fps", "android_capture_fps"),
         ("android_version", "android_version"), ("android_manufacturer", "android_manufacturer"),
         ("android_model", "android_model"), ("firmware", "firmware"), ("creation", "creationdate"),
         ("location", "location"), ("iso6709", "location"), ("gps", "location"), ("software", "software"),
         ("manufacturer", "make"), ("make", "make"), ("model", "model"))


def device_value(data, ctx):
    """Claimed recording device strings, verbatim; absent -> "none"."""
    try:
        r = _load(data)
        if not isinstance(r, dict):
            return r
        field = (ctx or {}).get("field") or ""
        which = next((w for k, w in _KIND if k in field), None)
        if which is None and field in ("recording_device", "device", "camera", "capture_device"):
            mk, md = _first(r, "make"), _first(r, "model")
            parts = [p for p in (mk, md) if p != "none"]
            return " ".join(parts) if parts else "none"
        if which is None:
            return None
        return _first(r, which)
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None


def handler_name(data, ctx):
    """First video track's mdia/hdlr component name (ffprobe stream handler_name), verbatim."""
    try:
        r = _load(data)
        if not isinstance(r, dict):
            return r
        if r["kind"] != "mp4":
            return "none"
        v = _video(r)
        return (v or {}).get("handler_name") or "none"
    except Exception:  # noqa: BLE001
        return None


def stream_encoder(data, ctx):
    """First video track's stsd VisualSampleEntry compressorname (Pascal string @entry+50, len <= 31) = ffprobe
    stream tag `encoder` (`Lavc61.3.100 libx264`, `H.264`, `AVC Coding`); empty -> "none"."""
    try:
        r = _load(data)
        if not isinstance(r, dict):
            return r
        if r["kind"] != "mp4":
            return "none"
        v = _video(r)
        return (v or {}).get("encoder") or "none"
    except Exception:  # noqa: BLE001
        return None


def mdta_keys(data, ctx):
    """QuickTime metadata `keys` names in stored order (ffprobe prints them verbatim as format tags)."""
    try:
        r = _load(data)
        if not isinstance(r, dict):
            return r
        return list((r.get("mdta") or {}).keys()) if r["kind"] == "mp4" else []
    except Exception:  # noqa: BLE001
        return None


def mdta_tag(r, key):
    """ffprobe format tag lookup for a dotted mdta key spelled with `_`/`-`/`.` (media_tags.tag_* fallback)."""
    norm = lambda s: "".join(c if c.isalnum() else "_" for c in s.lower())  # noqa: E731
    want = norm(key)
    for k, v in (r.get("mdta") or {}).items():
        if norm(k) == want:
            return v.strip()
    return None


def tag_fallback(data, key):
    """mdta value for media_tags.tag_value when its own tag table has no such key; None when absent/unparseable."""
    try:
        r = _load(data)
        return mdta_tag(r, key) if isinstance(r, dict) and r["kind"] == "mp4" else None
    except Exception:  # noqa: BLE001
        return None


def is_screen_recording(data, ctx):
    """DIAGNOSTIC heuristic: no device keys (make/model/android/udta) AND a display-panel sized or odd-dimension
    video track AND a variable frame rate (stts with > 1 distinct sample delta)."""
    try:
        r = _load(data)
        if not isinstance(r, dict):
            return r
        if r["kind"] != "mp4":
            return False
        if any(_first(r, w) != "none" for w in ("make", "model", "android_version")):
            return False
        v = _video(r)
        if not v or not v["w"]:
            return False
        dims = (v["w"], v["h"])
        sized = dims in _SCREEN or (v["h"], v["w"]) in _SCREEN or v["w"] % 2 or v["h"] % 2 or v["w"] % 16 and v["h"] % 16
        return bool(sized and len(v["deltas"]) > 1)
    except Exception:  # noqa: BLE001
        return None
