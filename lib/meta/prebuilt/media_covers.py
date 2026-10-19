"""Cover art, subtitle and chapter stream accounting the way ffprobe sees it -- prebuilt, SPECULATIVE (fmt media +
av/video/audio and the container tokens mp4/mov/m4a/mp3/flac/mkv).

Attached pictures: ffprobe turns an embedded cover into an extra VIDEO stream (codec_name mjpeg/png/..., disposition
attached_pic=1): ID3v2 APIC/PIC frame (mime via ffmpeg ff_id3v2_mime_tags; unknown mime = skipped), FLAC
METADATA_BLOCK_PICTURE (type 6), MP4 moov/udta/meta/ilst/covr `data` atoms (type 13 jpeg / 14 png / 27 bmp; one stream
per data atom; PNG signature overrides), Matroska Attachments/AttachedFile whose FileMimeType is an image mime (a
non-image attachment is an `attachment` stream instead; an attachment missing name/mime/data gets no stream).
PNG magic always wins over the declared type (ffmpeg). Dimensions come from the picture bytes (what ffprobe decodes),
FLAC falls back to the PICTURE block width/height. mime_type: the stored mime (ID3/FLAC/MKV); MP4 covr has no mime,
so it is derived from the codec (image/jpeg|png|bmp).
nb_streams_including_cover = ffprobe format.nb_streams = container tracks + cover streams (+ MKV non-image
attachments). audio_stream_count / audio_* fields count ONLY codec_type=audio, so an MP3/FLAC/M4A with a cover has
audio_stream_count 1 but nb_streams_including_cover 2. An MP4 QuickTime chapter text track (tref `chap` target) is
counted too, as a `data` stream (codec bin_data), NOT as a subtitle.
Subtitles (stream order): MP4 tx3g/text -> mov_text (hdlr sbtl/subt/text, not a chapter track), wvtt -> webvtt;
MKV TrackType 0x11 with S_TEXT/UTF8 -> subrip, S_TEXT/ASS|SSA -> ass, S_TEXT/WEBVTT -> webvtt (media_streams table).
Language: MP4 mdhd packed ISO-639-2 ("und" unset); MKV Language (absent -> "eng", Matroska default; stored "und" kept).
Chapters: MP4 Nero moov/udta/chpl (start in 100 ns units) overlaid BY INDEX with the QuickTime chapter track samples
(ffmpeg avpriv_new_chapter: same id -> the track's later entry wins); MKV Chapters/EditionEntry/ChapterAtom
(ChapterTimeStart ns, first ChapterDisplay/ChapString; ffmpeg keeps only atoms with a ChapterUID and strictly
increasing start; nested atoms ignored). chapter_start_times_seconds = ffprobe "%f" strings (6 decimals).
Not media (or a container this module does not parse: Ogg/WAV/AIFF covers) -> "none" / None."""
import struct

from ..spell import Dims
from .media_streams import _boxes, _child, _path, _mp4_streams, _mkv_streams, _ebml, _uint, _str

FIELDS = {
    ("media", "attached_pic_present"): "attached_pic_present",
    ("media", "has_attached_pic"): "attached_pic_present",
    ("media", "attached_picture_present"): "attached_pic_present",
    ("media", "cover_art_present"): "attached_pic_present",
    ("media", "has_cover_art"): "attached_pic_present",
    ("media", "embedded_cover_present"): "attached_pic_present",
    ("media", "attached_pic_count"): "attached_pic_count",
    ("media", "attached_pic_stream_count"): "attached_pic_count",
    ("media", "cover_art_count"): "attached_pic_count",
    ("media", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("media", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("media", "cover_art_codec_name"): "attached_pic_codec_name",
    ("media", "cover_codec_name"): "attached_pic_codec_name",
    ("media", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("media", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("media", "cover_art_mime_type"): "attached_pic_mime_type",
    ("media", "cover_mime_type"): "attached_pic_mime_type",
    ("media", "picture_mime_type"): "attached_pic_mime_type",
    ("media", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("media", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("media", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("media", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("media", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("media", "stream_count_including_cover"): "nb_streams_including_cover",
    ("media", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("media", "subtitle_stream_count"): "subtitle_stream_count",
    ("media", "subtitle_streams_count"): "subtitle_stream_count",
    ("media", "nb_subtitle_streams"): "subtitle_stream_count",
    ("media", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("media", "subtitle_track_count"): "subtitle_stream_count",
    ("media", "subtitle_codec_names"): "subtitle_codec_names",
    ("media", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("media", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("media", "subtitle_codec_name"): "subtitle_codec_name",
    ("media", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("media", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("media", "subtitle_languages"): "subtitle_languages",
    ("media", "subtitle_stream_languages"): "subtitle_languages",
    ("media", "subtitle_track_languages"): "subtitle_languages",
    ("media", "chapter_count"): "chapter_count",
    ("media", "chapters_count"): "chapter_count",
    ("media", "nb_chapters"): "chapter_count",
    ("media", "number_of_chapters"): "chapter_count",
    ("media", "chapter_titles"): "chapter_titles",
    ("media", "chapter_names"): "chapter_titles",
    ("media", "chapter_start_times_seconds"): "chapter_start_times",
    ("media", "chapter_start_times"): "chapter_start_times",
    ("av", "attached_pic_present"): "attached_pic_present",
    ("av", "has_attached_pic"): "attached_pic_present",
    ("av", "attached_picture_present"): "attached_pic_present",
    ("av", "cover_art_present"): "attached_pic_present",
    ("av", "has_cover_art"): "attached_pic_present",
    ("av", "embedded_cover_present"): "attached_pic_present",
    ("av", "attached_pic_count"): "attached_pic_count",
    ("av", "attached_pic_stream_count"): "attached_pic_count",
    ("av", "cover_art_count"): "attached_pic_count",
    ("av", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("av", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("av", "cover_art_codec_name"): "attached_pic_codec_name",
    ("av", "cover_codec_name"): "attached_pic_codec_name",
    ("av", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("av", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("av", "cover_art_mime_type"): "attached_pic_mime_type",
    ("av", "cover_mime_type"): "attached_pic_mime_type",
    ("av", "picture_mime_type"): "attached_pic_mime_type",
    ("av", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("av", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("av", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("av", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("av", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("av", "stream_count_including_cover"): "nb_streams_including_cover",
    ("av", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("av", "subtitle_stream_count"): "subtitle_stream_count",
    ("av", "subtitle_streams_count"): "subtitle_stream_count",
    ("av", "nb_subtitle_streams"): "subtitle_stream_count",
    ("av", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("av", "subtitle_track_count"): "subtitle_stream_count",
    ("av", "subtitle_codec_names"): "subtitle_codec_names",
    ("av", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("av", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("av", "subtitle_codec_name"): "subtitle_codec_name",
    ("av", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("av", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("av", "subtitle_languages"): "subtitle_languages",
    ("av", "subtitle_stream_languages"): "subtitle_languages",
    ("av", "subtitle_track_languages"): "subtitle_languages",
    ("av", "chapter_count"): "chapter_count",
    ("av", "chapters_count"): "chapter_count",
    ("av", "nb_chapters"): "chapter_count",
    ("av", "number_of_chapters"): "chapter_count",
    ("av", "chapter_titles"): "chapter_titles",
    ("av", "chapter_names"): "chapter_titles",
    ("av", "chapter_start_times_seconds"): "chapter_start_times",
    ("av", "chapter_start_times"): "chapter_start_times",
    ("video", "attached_pic_present"): "attached_pic_present",
    ("video", "has_attached_pic"): "attached_pic_present",
    ("video", "attached_picture_present"): "attached_pic_present",
    ("video", "cover_art_present"): "attached_pic_present",
    ("video", "has_cover_art"): "attached_pic_present",
    ("video", "embedded_cover_present"): "attached_pic_present",
    ("video", "attached_pic_count"): "attached_pic_count",
    ("video", "attached_pic_stream_count"): "attached_pic_count",
    ("video", "cover_art_count"): "attached_pic_count",
    ("video", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("video", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("video", "cover_art_codec_name"): "attached_pic_codec_name",
    ("video", "cover_codec_name"): "attached_pic_codec_name",
    ("video", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("video", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("video", "cover_art_mime_type"): "attached_pic_mime_type",
    ("video", "cover_mime_type"): "attached_pic_mime_type",
    ("video", "picture_mime_type"): "attached_pic_mime_type",
    ("video", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("video", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("video", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("video", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("video", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("video", "stream_count_including_cover"): "nb_streams_including_cover",
    ("video", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("video", "subtitle_stream_count"): "subtitle_stream_count",
    ("video", "subtitle_streams_count"): "subtitle_stream_count",
    ("video", "nb_subtitle_streams"): "subtitle_stream_count",
    ("video", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("video", "subtitle_track_count"): "subtitle_stream_count",
    ("video", "subtitle_codec_names"): "subtitle_codec_names",
    ("video", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("video", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("video", "subtitle_codec_name"): "subtitle_codec_name",
    ("video", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("video", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("video", "subtitle_languages"): "subtitle_languages",
    ("video", "subtitle_stream_languages"): "subtitle_languages",
    ("video", "subtitle_track_languages"): "subtitle_languages",
    ("video", "chapter_count"): "chapter_count",
    ("video", "chapters_count"): "chapter_count",
    ("video", "nb_chapters"): "chapter_count",
    ("video", "number_of_chapters"): "chapter_count",
    ("video", "chapter_titles"): "chapter_titles",
    ("video", "chapter_names"): "chapter_titles",
    ("video", "chapter_start_times_seconds"): "chapter_start_times",
    ("video", "chapter_start_times"): "chapter_start_times",
    ("audio", "attached_pic_present"): "attached_pic_present",
    ("audio", "has_attached_pic"): "attached_pic_present",
    ("audio", "attached_picture_present"): "attached_pic_present",
    ("audio", "cover_art_present"): "attached_pic_present",
    ("audio", "has_cover_art"): "attached_pic_present",
    ("audio", "embedded_cover_present"): "attached_pic_present",
    ("audio", "attached_pic_count"): "attached_pic_count",
    ("audio", "attached_pic_stream_count"): "attached_pic_count",
    ("audio", "cover_art_count"): "attached_pic_count",
    ("audio", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("audio", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("audio", "cover_art_codec_name"): "attached_pic_codec_name",
    ("audio", "cover_codec_name"): "attached_pic_codec_name",
    ("audio", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("audio", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("audio", "cover_art_mime_type"): "attached_pic_mime_type",
    ("audio", "cover_mime_type"): "attached_pic_mime_type",
    ("audio", "picture_mime_type"): "attached_pic_mime_type",
    ("audio", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("audio", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("audio", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("audio", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("audio", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("audio", "stream_count_including_cover"): "nb_streams_including_cover",
    ("audio", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("audio", "subtitle_stream_count"): "subtitle_stream_count",
    ("audio", "subtitle_streams_count"): "subtitle_stream_count",
    ("audio", "nb_subtitle_streams"): "subtitle_stream_count",
    ("audio", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("audio", "subtitle_track_count"): "subtitle_stream_count",
    ("audio", "subtitle_codec_names"): "subtitle_codec_names",
    ("audio", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("audio", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("audio", "subtitle_codec_name"): "subtitle_codec_name",
    ("audio", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("audio", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("audio", "subtitle_languages"): "subtitle_languages",
    ("audio", "subtitle_stream_languages"): "subtitle_languages",
    ("audio", "subtitle_track_languages"): "subtitle_languages",
    ("audio", "chapter_count"): "chapter_count",
    ("audio", "chapters_count"): "chapter_count",
    ("audio", "nb_chapters"): "chapter_count",
    ("audio", "number_of_chapters"): "chapter_count",
    ("audio", "chapter_titles"): "chapter_titles",
    ("audio", "chapter_names"): "chapter_titles",
    ("audio", "chapter_start_times_seconds"): "chapter_start_times",
    ("audio", "chapter_start_times"): "chapter_start_times",
    ("mp4", "attached_pic_present"): "attached_pic_present",
    ("mp4", "has_attached_pic"): "attached_pic_present",
    ("mp4", "attached_picture_present"): "attached_pic_present",
    ("mp4", "cover_art_present"): "attached_pic_present",
    ("mp4", "has_cover_art"): "attached_pic_present",
    ("mp4", "embedded_cover_present"): "attached_pic_present",
    ("mp4", "attached_pic_count"): "attached_pic_count",
    ("mp4", "attached_pic_stream_count"): "attached_pic_count",
    ("mp4", "cover_art_count"): "attached_pic_count",
    ("mp4", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("mp4", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("mp4", "cover_art_codec_name"): "attached_pic_codec_name",
    ("mp4", "cover_codec_name"): "attached_pic_codec_name",
    ("mp4", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("mp4", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("mp4", "cover_art_mime_type"): "attached_pic_mime_type",
    ("mp4", "cover_mime_type"): "attached_pic_mime_type",
    ("mp4", "picture_mime_type"): "attached_pic_mime_type",
    ("mp4", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("mp4", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("mp4", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("mp4", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("mp4", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("mp4", "stream_count_including_cover"): "nb_streams_including_cover",
    ("mp4", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("mp4", "subtitle_stream_count"): "subtitle_stream_count",
    ("mp4", "subtitle_streams_count"): "subtitle_stream_count",
    ("mp4", "nb_subtitle_streams"): "subtitle_stream_count",
    ("mp4", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("mp4", "subtitle_track_count"): "subtitle_stream_count",
    ("mp4", "subtitle_codec_names"): "subtitle_codec_names",
    ("mp4", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("mp4", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("mp4", "subtitle_codec_name"): "subtitle_codec_name",
    ("mp4", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("mp4", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("mp4", "subtitle_languages"): "subtitle_languages",
    ("mp4", "subtitle_stream_languages"): "subtitle_languages",
    ("mp4", "subtitle_track_languages"): "subtitle_languages",
    ("mp4", "chapter_count"): "chapter_count",
    ("mp4", "chapters_count"): "chapter_count",
    ("mp4", "nb_chapters"): "chapter_count",
    ("mp4", "number_of_chapters"): "chapter_count",
    ("mp4", "chapter_titles"): "chapter_titles",
    ("mp4", "chapter_names"): "chapter_titles",
    ("mp4", "chapter_start_times_seconds"): "chapter_start_times",
    ("mp4", "chapter_start_times"): "chapter_start_times",
    ("mov", "attached_pic_present"): "attached_pic_present",
    ("mov", "has_attached_pic"): "attached_pic_present",
    ("mov", "attached_picture_present"): "attached_pic_present",
    ("mov", "cover_art_present"): "attached_pic_present",
    ("mov", "has_cover_art"): "attached_pic_present",
    ("mov", "embedded_cover_present"): "attached_pic_present",
    ("mov", "attached_pic_count"): "attached_pic_count",
    ("mov", "attached_pic_stream_count"): "attached_pic_count",
    ("mov", "cover_art_count"): "attached_pic_count",
    ("mov", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("mov", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("mov", "cover_art_codec_name"): "attached_pic_codec_name",
    ("mov", "cover_codec_name"): "attached_pic_codec_name",
    ("mov", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("mov", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("mov", "cover_art_mime_type"): "attached_pic_mime_type",
    ("mov", "cover_mime_type"): "attached_pic_mime_type",
    ("mov", "picture_mime_type"): "attached_pic_mime_type",
    ("mov", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("mov", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("mov", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("mov", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("mov", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("mov", "stream_count_including_cover"): "nb_streams_including_cover",
    ("mov", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("mov", "subtitle_stream_count"): "subtitle_stream_count",
    ("mov", "subtitle_streams_count"): "subtitle_stream_count",
    ("mov", "nb_subtitle_streams"): "subtitle_stream_count",
    ("mov", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("mov", "subtitle_track_count"): "subtitle_stream_count",
    ("mov", "subtitle_codec_names"): "subtitle_codec_names",
    ("mov", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("mov", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("mov", "subtitle_codec_name"): "subtitle_codec_name",
    ("mov", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("mov", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("mov", "subtitle_languages"): "subtitle_languages",
    ("mov", "subtitle_stream_languages"): "subtitle_languages",
    ("mov", "subtitle_track_languages"): "subtitle_languages",
    ("mov", "chapter_count"): "chapter_count",
    ("mov", "chapters_count"): "chapter_count",
    ("mov", "nb_chapters"): "chapter_count",
    ("mov", "number_of_chapters"): "chapter_count",
    ("mov", "chapter_titles"): "chapter_titles",
    ("mov", "chapter_names"): "chapter_titles",
    ("mov", "chapter_start_times_seconds"): "chapter_start_times",
    ("mov", "chapter_start_times"): "chapter_start_times",
    ("m4a", "attached_pic_present"): "attached_pic_present",
    ("m4a", "has_attached_pic"): "attached_pic_present",
    ("m4a", "attached_picture_present"): "attached_pic_present",
    ("m4a", "cover_art_present"): "attached_pic_present",
    ("m4a", "has_cover_art"): "attached_pic_present",
    ("m4a", "embedded_cover_present"): "attached_pic_present",
    ("m4a", "attached_pic_count"): "attached_pic_count",
    ("m4a", "attached_pic_stream_count"): "attached_pic_count",
    ("m4a", "cover_art_count"): "attached_pic_count",
    ("m4a", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("m4a", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("m4a", "cover_art_codec_name"): "attached_pic_codec_name",
    ("m4a", "cover_codec_name"): "attached_pic_codec_name",
    ("m4a", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("m4a", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("m4a", "cover_art_mime_type"): "attached_pic_mime_type",
    ("m4a", "cover_mime_type"): "attached_pic_mime_type",
    ("m4a", "picture_mime_type"): "attached_pic_mime_type",
    ("m4a", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("m4a", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("m4a", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("m4a", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("m4a", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("m4a", "stream_count_including_cover"): "nb_streams_including_cover",
    ("m4a", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("m4a", "subtitle_stream_count"): "subtitle_stream_count",
    ("m4a", "subtitle_streams_count"): "subtitle_stream_count",
    ("m4a", "nb_subtitle_streams"): "subtitle_stream_count",
    ("m4a", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("m4a", "subtitle_track_count"): "subtitle_stream_count",
    ("m4a", "subtitle_codec_names"): "subtitle_codec_names",
    ("m4a", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("m4a", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("m4a", "subtitle_codec_name"): "subtitle_codec_name",
    ("m4a", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("m4a", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("m4a", "subtitle_languages"): "subtitle_languages",
    ("m4a", "subtitle_stream_languages"): "subtitle_languages",
    ("m4a", "subtitle_track_languages"): "subtitle_languages",
    ("m4a", "chapter_count"): "chapter_count",
    ("m4a", "chapters_count"): "chapter_count",
    ("m4a", "nb_chapters"): "chapter_count",
    ("m4a", "number_of_chapters"): "chapter_count",
    ("m4a", "chapter_titles"): "chapter_titles",
    ("m4a", "chapter_names"): "chapter_titles",
    ("m4a", "chapter_start_times_seconds"): "chapter_start_times",
    ("m4a", "chapter_start_times"): "chapter_start_times",
    ("mp3", "attached_pic_present"): "attached_pic_present",
    ("mp3", "has_attached_pic"): "attached_pic_present",
    ("mp3", "attached_picture_present"): "attached_pic_present",
    ("mp3", "cover_art_present"): "attached_pic_present",
    ("mp3", "has_cover_art"): "attached_pic_present",
    ("mp3", "embedded_cover_present"): "attached_pic_present",
    ("mp3", "attached_pic_count"): "attached_pic_count",
    ("mp3", "attached_pic_stream_count"): "attached_pic_count",
    ("mp3", "cover_art_count"): "attached_pic_count",
    ("mp3", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("mp3", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("mp3", "cover_art_codec_name"): "attached_pic_codec_name",
    ("mp3", "cover_codec_name"): "attached_pic_codec_name",
    ("mp3", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("mp3", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("mp3", "cover_art_mime_type"): "attached_pic_mime_type",
    ("mp3", "cover_mime_type"): "attached_pic_mime_type",
    ("mp3", "picture_mime_type"): "attached_pic_mime_type",
    ("mp3", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("mp3", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("mp3", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("mp3", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("mp3", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("mp3", "stream_count_including_cover"): "nb_streams_including_cover",
    ("mp3", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("mp3", "subtitle_stream_count"): "subtitle_stream_count",
    ("mp3", "subtitle_streams_count"): "subtitle_stream_count",
    ("mp3", "nb_subtitle_streams"): "subtitle_stream_count",
    ("mp3", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("mp3", "subtitle_track_count"): "subtitle_stream_count",
    ("mp3", "subtitle_codec_names"): "subtitle_codec_names",
    ("mp3", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("mp3", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("mp3", "subtitle_codec_name"): "subtitle_codec_name",
    ("mp3", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("mp3", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("mp3", "subtitle_languages"): "subtitle_languages",
    ("mp3", "subtitle_stream_languages"): "subtitle_languages",
    ("mp3", "subtitle_track_languages"): "subtitle_languages",
    ("mp3", "chapter_count"): "chapter_count",
    ("mp3", "chapters_count"): "chapter_count",
    ("mp3", "nb_chapters"): "chapter_count",
    ("mp3", "number_of_chapters"): "chapter_count",
    ("mp3", "chapter_titles"): "chapter_titles",
    ("mp3", "chapter_names"): "chapter_titles",
    ("mp3", "chapter_start_times_seconds"): "chapter_start_times",
    ("mp3", "chapter_start_times"): "chapter_start_times",
    ("flac", "attached_pic_present"): "attached_pic_present",
    ("flac", "has_attached_pic"): "attached_pic_present",
    ("flac", "attached_picture_present"): "attached_pic_present",
    ("flac", "cover_art_present"): "attached_pic_present",
    ("flac", "has_cover_art"): "attached_pic_present",
    ("flac", "embedded_cover_present"): "attached_pic_present",
    ("flac", "attached_pic_count"): "attached_pic_count",
    ("flac", "attached_pic_stream_count"): "attached_pic_count",
    ("flac", "cover_art_count"): "attached_pic_count",
    ("flac", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("flac", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("flac", "cover_art_codec_name"): "attached_pic_codec_name",
    ("flac", "cover_codec_name"): "attached_pic_codec_name",
    ("flac", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("flac", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("flac", "cover_art_mime_type"): "attached_pic_mime_type",
    ("flac", "cover_mime_type"): "attached_pic_mime_type",
    ("flac", "picture_mime_type"): "attached_pic_mime_type",
    ("flac", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("flac", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("flac", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("flac", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("flac", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("flac", "stream_count_including_cover"): "nb_streams_including_cover",
    ("flac", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("flac", "subtitle_stream_count"): "subtitle_stream_count",
    ("flac", "subtitle_streams_count"): "subtitle_stream_count",
    ("flac", "nb_subtitle_streams"): "subtitle_stream_count",
    ("flac", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("flac", "subtitle_track_count"): "subtitle_stream_count",
    ("flac", "subtitle_codec_names"): "subtitle_codec_names",
    ("flac", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("flac", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("flac", "subtitle_codec_name"): "subtitle_codec_name",
    ("flac", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("flac", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("flac", "subtitle_languages"): "subtitle_languages",
    ("flac", "subtitle_stream_languages"): "subtitle_languages",
    ("flac", "subtitle_track_languages"): "subtitle_languages",
    ("flac", "chapter_count"): "chapter_count",
    ("flac", "chapters_count"): "chapter_count",
    ("flac", "nb_chapters"): "chapter_count",
    ("flac", "number_of_chapters"): "chapter_count",
    ("flac", "chapter_titles"): "chapter_titles",
    ("flac", "chapter_names"): "chapter_titles",
    ("flac", "chapter_start_times_seconds"): "chapter_start_times",
    ("flac", "chapter_start_times"): "chapter_start_times",
    ("mkv", "attached_pic_present"): "attached_pic_present",
    ("mkv", "has_attached_pic"): "attached_pic_present",
    ("mkv", "attached_picture_present"): "attached_pic_present",
    ("mkv", "cover_art_present"): "attached_pic_present",
    ("mkv", "has_cover_art"): "attached_pic_present",
    ("mkv", "embedded_cover_present"): "attached_pic_present",
    ("mkv", "attached_pic_count"): "attached_pic_count",
    ("mkv", "attached_pic_stream_count"): "attached_pic_count",
    ("mkv", "cover_art_count"): "attached_pic_count",
    ("mkv", "attached_pic_codec_name"): "attached_pic_codec_name",
    ("mkv", "attached_picture_codec_name"): "attached_pic_codec_name",
    ("mkv", "cover_art_codec_name"): "attached_pic_codec_name",
    ("mkv", "cover_codec_name"): "attached_pic_codec_name",
    ("mkv", "attached_pic_mime_type"): "attached_pic_mime_type",
    ("mkv", "attached_picture_mime_type"): "attached_pic_mime_type",
    ("mkv", "cover_art_mime_type"): "attached_pic_mime_type",
    ("mkv", "cover_mime_type"): "attached_pic_mime_type",
    ("mkv", "picture_mime_type"): "attached_pic_mime_type",
    ("mkv", "attached_pic_dimensions_pixels"): "attached_pic_dimensions",
    ("mkv", "attached_pic_dimensions"): "attached_pic_dimensions",
    ("mkv", "cover_art_dimensions_pixels"): "attached_pic_dimensions",
    ("mkv", "cover_dimensions_pixels"): "attached_pic_dimensions",
    ("mkv", "nb_streams_including_cover"): "nb_streams_including_cover",
    ("mkv", "stream_count_including_cover"): "nb_streams_including_cover",
    ("mkv", "nb_streams_including_attached_pic"): "nb_streams_including_cover",
    ("mkv", "subtitle_stream_count"): "subtitle_stream_count",
    ("mkv", "subtitle_streams_count"): "subtitle_stream_count",
    ("mkv", "nb_subtitle_streams"): "subtitle_stream_count",
    ("mkv", "number_of_subtitle_streams"): "subtitle_stream_count",
    ("mkv", "subtitle_track_count"): "subtitle_stream_count",
    ("mkv", "subtitle_codec_names"): "subtitle_codec_names",
    ("mkv", "subtitle_stream_codec_names"): "subtitle_codec_names",
    ("mkv", "subtitle_track_codec_names"): "subtitle_codec_names",
    ("mkv", "subtitle_codec_name"): "subtitle_codec_name",
    ("mkv", "first_subtitle_codec_name"): "subtitle_codec_name",
    ("mkv", "subtitle_stream_codec_name"): "subtitle_codec_name",
    ("mkv", "subtitle_languages"): "subtitle_languages",
    ("mkv", "subtitle_stream_languages"): "subtitle_languages",
    ("mkv", "subtitle_track_languages"): "subtitle_languages",
    ("mkv", "chapter_count"): "chapter_count",
    ("mkv", "chapters_count"): "chapter_count",
    ("mkv", "nb_chapters"): "chapter_count",
    ("mkv", "number_of_chapters"): "chapter_count",
    ("mkv", "chapter_titles"): "chapter_titles",
    ("mkv", "chapter_names"): "chapter_titles",
    ("mkv", "chapter_start_times_seconds"): "chapter_start_times",
    ("mkv", "chapter_start_times"): "chapter_start_times",
}



def _img_dims(p):
    """(w, h) of an embedded picture from its own bytes (PNG IHDR / JPEG SOFn / GIF LSD / BMP DIB), else PIL."""
    try:
        if p[:8] == b"\x89PNG\r\n\x1a\n" and len(p) >= 24:
            return struct.unpack_from(">II", p, 16)
        if p[:6] in (b"GIF87a", b"GIF89a"):
            return struct.unpack_from("<HH", p, 6)
        if p[:2] == b"BM" and len(p) >= 26:
            w, h = struct.unpack_from("<ii", p, 18)
            return w, abs(h)
        if p[:2] == b"\xff\xd8":
            i = 2
            while i + 9 < len(p):
                if p[i] != 0xFF:
                    i += 1
                    continue
                m = p[i + 1]
                if m in (0xD8, 0x01) or 0xD0 <= m <= 0xD7 or m == 0xFF:
                    i += 1 if m == 0xFF else 2
                    continue
                ln, = struct.unpack_from(">H", p, i + 2)
                if m in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    h, w = struct.unpack_from(">HH", p, i + 5)
                    return w, h
                i += 2 + ln
        import io
        from PIL import Image
        return Image.open(io.BytesIO(p)).size
    except Exception:
        return None


# ffmpeg ff_id3v2_mime_tags (id3v2.c), shared by ID3 APIC and FLAC PICTURE; an unknown mime = picture skipped
_MIME_CODEC = {"image/gif": "gif", "image/jpeg": "mjpeg", "image/jpg": "mjpeg", "image/png": "png",
               "image/tiff": "tiff", "image/bmp": "bmp", "image/webp": "webp", "JPG": "mjpeg", "PNG": "png"}
# ffmpeg matroskadec mkv_image_mime_tags: these attachment mimes become attached_pic VIDEO streams
_MKV_IMG = {"image/gif": "gif", "image/jpeg": "mjpeg", "image/png": "png", "image/tiff": "tiff",
            "image/webp": "webp", "image/bmp": "bmp", "image/jpg": "mjpeg"}
_PNGSIG = b"\x89PNG\r\n\x1a\n"
# ffmpeg ff_mkv_codec_tags subtitle ids media_streams' table lacks (ffmpeg's own muxer writes D_WEBVTT/SUBTITLES)
_MKV_SUB_EXTRA = {"D_WEBVTT/SUBTITLES": "webvtt", "D_WEBVTT/CAPTIONS": "webvtt", "D_WEBVTT/DESCRIPTIONS": "webvtt",
                  "D_WEBVTT/METADATA": "webvtt", "S_TEXT/ASCII": "text", "S_ARIBSUB": "arib_caption",
                  "S_TEXT/TTML": "ttml"}


def _pic(codec, mime, data, fb_dims=None):
    if data[:8] == _PNGSIG:
        codec = "png"
    return {"codec_name": codec, "mime_type": mime, "dims": _img_dims(data) or fb_dims}


def _syncsafe(b):
    return (b[0] << 21) | (b[1] << 14) | (b[2] << 7) | b[3]


def _id3_pics(b):
    """APIC/PIC frames of a leading ID3v2 tag (ffmpeg id3v2.c read_apic), in tag order."""
    if b[:3] != b"ID3" or len(b) < 10:
        return []
    ver, flags, size = b[3], b[5], _syncsafe(b[6:10])
    tag = b[10:10 + size]
    if flags & 0x80 and ver < 4:
        tag = tag.replace(b"\xff\x00", b"\xff")                  # whole-tag unsynchronisation (v2.2/2.3)
    i, out = 0, []
    if flags & 0x40 and ver >= 3 and len(tag) >= 4:            # extended header
        i = (_syncsafe(tag[:4]) if ver == 4 else struct.unpack_from(">I", tag, 0)[0] + 4)
    hl = 6 if ver == 2 else 10
    while i + hl <= len(tag):
        fid = tag[i:i + (3 if ver == 2 else 4)]
        if not fid.strip(b"\0") or not fid.isalnum():
            break
        if ver == 2:
            fsz = int.from_bytes(tag[i + 3:i + 6], "big")
            ff = 0
        else:
            fsz = _syncsafe(tag[i + 4:i + 8]) if ver == 4 else struct.unpack_from(">I", tag, i + 4)[0]
            ff = struct.unpack_from(">H", tag, i + 8)[0]
        body = tag[i + hl:i + hl + fsz]
        i += hl + fsz
        if fid not in (b"APIC", b"PIC") or len(body) < 4:
            continue
        if ver == 4 and ff & 0x0001 and len(body) >= 4:        # data length indicator
            body = body[4:]
        if ver == 4 and ff & 0x0002:
            body = body.replace(b"\xff\x00", b"\xff")
        enc = body[0]
        if ver == 2:
            mime, j = body[1:4].decode("latin-1"), 4
        else:
            k = body.find(b"\0", 1)
            if k < 0:
                continue
            mime, j = body[1:k].decode("latin-1"), k + 1
        j += 1                                                  # picture type
        if enc in (1, 2):                                       # UTF-16 description: \0\0 on an even boundary
            k = j
            while k + 1 < len(body) and body[k:k + 2] != b"\0\0":
                k += 2
            j = k + 2
        else:
            k = body.find(b"\0", j)
            j = (k + 1) if k >= 0 else len(body)
        data = body[j:]
        codec = _MIME_CODEC.get(mime)
        if codec is None or not data:
            continue
        if mime in ("JPG", "PNG"):
            mime = "image/jpeg" if mime == "JPG" else "image/png"
        out.append(_pic(codec, mime, data))
    return out


def _flac_pics(b):
    """METADATA_BLOCK_PICTURE (type 6) blocks of a native FLAC stream (ffmpeg flac_picture.c)."""
    i = 4
    if b[:3] == b"ID3":
        i = 10 + _syncsafe(b[6:10]) + 4
    out = []
    while i + 4 <= len(b):
        hdr = b[i]
        ln = int.from_bytes(b[i + 1:i + 4], "big")
        blk = b[i + 4:i + 4 + ln]
        if hdr & 0x7F == 6 and len(blk) >= 32:
            ml, = struct.unpack_from(">I", blk, 4)
            mime = blk[8:8 + ml].decode("latin-1", "replace")
            p = 8 + ml
            dl, = struct.unpack_from(">I", blk, p)
            p += 4 + dl
            w, h = struct.unpack_from(">II", blk, p)
            p += 16
            sz, = struct.unpack_from(">I", blk, p)
            data = blk[p + 4:p + 4 + sz]
            codec = _MIME_CODEC.get(mime)
            if data[:8] == _PNGSIG:
                codec = "png"
            if codec and data:
                out.append(_pic(codec, mime, data, (w, h) if w and h else None))
        i += 4 + ln
        if hdr & 0x80:
            break
    return out


def _mp4_moov(b):
    if b[4:8] not in (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip", b"pnot"):
        return None
    moov = None
    for t, s, e in _boxes(b, 0, len(b)):
        if t == b"moov":
            moov = (s, e)
    return moov


def _mp4_covr(b, moov):
    """moov/udta/meta/ilst/covr data atoms (ffmpeg mov_read_covr: one attached_pic stream per data atom)."""
    out = []
    ud = _child(b, moov[0], moov[1], b"udta")
    if not ud:
        return out
    meta = _child(b, ud[0], ud[1], b"meta")
    if not meta:
        return out
    ms = meta[0] + 4 if b[meta[0] + 4:meta[0] + 8] != b"hdlr" else meta[0]   # full box (ISO) vs QuickTime meta
    il = _child(b, ms, meta[1], b"ilst")
    cv = il and _child(b, il[0], il[1], b"covr")
    if not cv:
        return out
    for t, s, e in _boxes(b, *cv):
        if t != b"data" or e - s < 8:
            continue
        typ, = struct.unpack_from(">I", b, s)
        data = b[s + 8:e]
        codec = {13: "mjpeg", 14: "png", 27: "bmp"}.get(typ)
        if codec is None or not data:
            continue
        if codec != "bmp" and len(data) >= 8:
            codec = "png" if data[:8] == _PNGSIG else "mjpeg"
        out.append({"codec_name": codec, "mime_type": {"mjpeg": "image/jpeg", "png": "image/png",
                    "bmp": "image/bmp"}[codec], "dims": _img_dims(data)})
    return out


def _mp4_trak_meta(b, moov):
    """[(track_id, [tref chap ids], stts-expanded [(start, dur)], timescale, samples)] in trak order."""
    out = []
    for t, ts, te in _boxes(b, *moov):
        if t != b"trak":
            continue
        tid, chaps = None, []
        th = _child(b, ts, te, b"tkhd")
        if th:
            tid, = struct.unpack_from(">I", b, th[0] + (20 if b[th[0]] == 1 else 12))
        tr = _child(b, ts, te, b"tref")
        if tr:
            for rt, rs, re_ in _boxes(b, *tr):
                if rt == b"chap":
                    chaps += [struct.unpack_from(">I", b, k)[0] for k in range(rs, re_ - 3, 4)]
        out.append({"id": tid, "chap": chaps, "s": ts, "e": te})
    return out


def _mp4_text_samples(b, ts, te):
    """[(start_ticks, dur_ticks, text)] of a QuickTime text/tx3g track, plus timescale."""
    md = _child(b, ts, te, b"mdia")
    if not md:
        return None
    h = _child(b, md[0], md[1], b"mdhd")
    scale = struct.unpack_from(">I", b, h[0] + (20 if b[h[0]] == 1 else 12))[0] if h else 0
    st = _path(b, md[0], md[1], b"minf", b"stbl")
    if not st or not scale:
        return None
    g = lambda typ: _child(b, st[0], st[1], typ)  # noqa: E731
    stts, stsz, stsc = g(b"stts"), g(b"stsz"), g(b"stsc")
    stco, co64 = g(b"stco"), g(b"co64")
    if not (stts and stsz and stsc and (stco or co64)):
        return None
    durs = []
    n, = struct.unpack_from(">I", b, stts[0] + 4)
    for k in range(n):
        c, d = struct.unpack_from(">II", b, stts[0] + 8 + 8 * k)
        durs += [d] * min(c, 10000)
    fixed, cnt = struct.unpack_from(">II", b, stsz[0] + 4)
    sizes = [fixed] * cnt if fixed else [struct.unpack_from(">I", b, stsz[0] + 12 + 4 * k)[0] for k in range(cnt)]
    if stco:
        nc, = struct.unpack_from(">I", b, stco[0] + 4)
        offs = [struct.unpack_from(">I", b, stco[0] + 8 + 4 * k)[0] for k in range(nc)]
    else:
        nc, = struct.unpack_from(">I", b, co64[0] + 4)
        offs = [struct.unpack_from(">Q", b, co64[0] + 8 + 8 * k)[0] for k in range(nc)]
    ns, = struct.unpack_from(">I", b, stsc[0] + 4)
    runs = [struct.unpack_from(">III", b, stsc[0] + 8 + 12 * k) for k in range(ns)]
    pos, si = [], 0
    for ci in range(len(offs)):
        spc = 0
        for k, (first, per, _d) in enumerate(runs):
            if first - 1 <= ci:
                spc = per
        o = offs[ci]
        for _ in range(spc):
            if si >= len(sizes):
                break
            pos.append((o, sizes[si]))
            o += sizes[si]
            si += 1
    out, t = [], 0
    for k, (o, sz) in enumerate(pos):
        d = durs[k] if k < len(durs) else 0
        txt = ""
        if sz >= 2:
            ln, = struct.unpack_from(">H", b, o)
            raw = b[o + 2:o + 2 + min(ln, sz - 2)]
            if raw[:2] in (b"\xfe\xff", b"\xff\xfe"):
                txt = raw.decode("utf-16", "replace")
            else:
                txt = raw.decode("utf-8", "replace")
        out.append((t, d, txt))
        t += d
    return out, scale


def _mp4_chpl(b, moov):
    """Nero moov/udta/chpl: [(start_seconds, title)] (start in 100 ns units)."""
    ud = _child(b, moov[0], moov[1], b"udta")
    c = ud and _child(b, ud[0], ud[1], b"chpl")
    if not c:
        return []
    s, e = c
    v = b[s]
    i = s + 4 + (4 if v == 1 else 0)
    n = b[i]
    i += 1
    out = []
    for _ in range(n):
        if i + 9 > e:
            break
        st, = struct.unpack_from(">Q", b, i)
        ln = b[i + 8]
        out.append((st / 1e7, b[i + 9:i + 9 + ln].decode("utf-8", "replace")))
        i += 9 + ln
    return out


def _mp4_info(b):
    moov = _mp4_moov(b)
    if moov is None:
        return None
    streams = _mp4_streams(b) or []
    traks = _mp4_trak_meta(b, moov)
    chap_ids = {c for t in traks for c in t["chap"]}
    chapters = [(s, ttl) for s, ttl in _mp4_chpl(b, moov)]
    for k, t in enumerate(traks):
        if t["id"] in chap_ids and k < len(streams):
            streams[k] = dict(streams[k], codec_type="data", codec_name="bin_data")   # ffmpeg: chapter track = data
    for t in traks:                         # QuickTime chapter track: overrides chpl entries by index (avpriv_new_chapter)
        if t["id"] in chap_ids:
            r = _mp4_text_samples(b, t["s"], t["e"])
            if r:
                smp, scale = r
                for k, (st, _d, txt) in enumerate(smp):
                    if k < len(chapters):
                        chapters[k] = (st / scale, txt)
                    else:
                        chapters.append((st / scale, txt))
            break
    return {"streams": streams, "pics": _mp4_covr(b, moov), "chapters": chapters}


def _mkv_info(b):
    streams = _mkv_streams(b)
    if streams is None:
        return None
    pics, n_att, chapters = [], 0, []
    for eid, s, e, _ in _ebml(b, 0, len(b)):
        if eid != 0x18538067:
            continue
        for cid, cs, ce, _u in _ebml(b, s, e):
            if cid == 0x1941A469:                                   # Attachments
                for aid, as_, ae, _ in _ebml(b, cs, ce):
                    if aid != 0x61A7:
                        continue
                    nm = mime = data = None
                    for k, ks, ke, _ in _ebml(b, as_, ae):
                        if k == 0x466E:
                            nm = _str(b, ks, ke)
                        elif k == 0x4660:
                            mime = _str(b, ks, ke)
                        elif k == 0x465C:
                            data = b[ks:ke]
                    if not (nm and mime and data):
                        continue                                    # ffmpeg: incomplete attachment, no stream
                    n_att += 1
                    if mime in _MKV_IMG:
                        pics.append({"codec_name": _MKV_IMG[mime], "mime_type": mime, "dims": _img_dims(data)})
            elif cid == 0x1654AE6B:                                 # Tracks: fill codec ids media_streams left None
                k = 0
                for tid, ts, te, _ in _ebml(b, cs, ce):
                    if tid != 0xAE:
                        continue
                    for c, s2, e2, _ in _ebml(b, ts, te):
                        if c == 0x86 and k < len(streams) and streams[k].get("codec_name") is None:
                            codec = _MKV_SUB_EXTRA.get(_str(b, s2, e2))
                            if codec:
                                streams[k] = dict(streams[k], codec_name=codec, codec_type="subtitle")
                    k += 1
            elif cid == 0x1043A770:                                 # Chapters
                last = None
                for ed, es, ee, _ in _ebml(b, cs, ce):
                    if ed != 0x45B9:
                        continue
                    for at, ats, ate, _ in _ebml(b, es, ee):
                        if at != 0xB6:
                            continue
                        start, uid, title = None, 0, None
                        for k, ks, ke, _ in _ebml(b, ats, ate):
                            if k == 0x91:
                                start = _uint(b, ks, ke)
                            elif k == 0x73C4:
                                uid = _uint(b, ks, ke)
                            elif k == 0x80 and title is None:
                                for d, ds, de, _ in _ebml(b, ks, ke):
                                    if d == 0x85:
                                        title = _str(b, ds, de)
                        # ffmpeg matroska_read_header: needs a UID and strictly increasing starts
                        if start is not None and uid and (last is None or start > last):
                            chapters.append((start / 1e9, title or ""))
                            last = start
        break
    return {"streams": streams, "pics": pics, "extra_streams": n_att - len(pics), "chapters": chapters}


def _info(b):
    if not b or len(b) < 12:
        return None
    try:
        if b[:4] == b"\x1a\x45\xdf\xa3":
            return _mkv_info(b)
        if b[4:8] in (b"ftyp", b"moov", b"mdat", b"free", b"wide", b"skip", b"pnot"):
            return _mp4_info(b)
        flac_at = 10 + _syncsafe(b[6:10]) if b[:3] == b"ID3" else 0
        if b[flac_at:flac_at + 4] == b"fLaC":
            return {"streams": [{"codec_type": "audio", "codec_name": "flac"}], "pics": _flac_pics(b),
                    "chapters": []}
        if b[:3] == b"ID3" or (b[0] == 0xFF and b[1] & 0xE0 == 0xE0):
            return {"streams": [{"codec_type": "audio", "codec_name": "mp3"}], "pics": _id3_pics(b),
                    "chapters": []}
    except Exception:
        return None
    return None


def _go(data, fn):
    if data is None:
        return None
    try:
        inf = _info(bytes(data))
        if inf is None:
            return "none"
        return fn(inf)
    except Exception:
        return None


def _first(inf, key):
    p = inf["pics"]
    if not p:
        return "none"
    v = p[0].get(key)
    return "none" if v is None else v


def attached_pic_present(data, ctx):
    return _go(data, lambda i: bool(i["pics"]))


def attached_pic_count(data, ctx):
    return _go(data, lambda i: len(i["pics"]))


def attached_pic_codec_name(data, ctx):
    return _go(data, lambda i: _first(i, "codec_name"))


def attached_pic_mime_type(data, ctx):
    return _go(data, lambda i: _first(i, "mime_type"))


def attached_pic_dimensions(data, ctx):
    def f(i):
        d = _first(i, "dims")
        return d if d == "none" else Dims(d[0], d[1])
    return _go(data, f)


def nb_streams_including_cover(data, ctx):
    """ffprobe format.nb_streams: container tracks (+ MP4 chapter text track as a data stream) + one attached_pic
    video stream per cover (+ non-image MKV attachments as attachment streams)."""
    return _go(data, lambda i: len(i["streams"]) + len(i["pics"]) + i.get("extra_streams", 0))


def _subs(i):
    return [s for s in i["streams"] if s.get("codec_type") == "subtitle"]


def subtitle_stream_count(data, ctx):
    return _go(data, lambda i: len(_subs(i)))


def subtitle_codec_names(data, ctx):
    return _go(data, lambda i: [s.get("codec_name") or "none" for s in _subs(i)])


def subtitle_codec_name(data, ctx):
    return _go(data, lambda i: (_subs(i)[0].get("codec_name") or "none") if _subs(i) else "none")


def subtitle_languages(data, ctx):
    return _go(data, lambda i: [s.get("language") or "und" for s in _subs(i)])


def chapter_count(data, ctx):
    return _go(data, lambda i: len(i["chapters"]))


def chapter_titles(data, ctx):
    return _go(data, lambda i: [t for _s, t in i["chapters"]])


def chapter_start_times(data, ctx):
    """ffprobe chapters[].start_time "%f" strings (seconds, 6 decimals), chapter order."""
    return _go(data, lambda i: ["%.6f" % s for s, _t in i["chapters"]])
