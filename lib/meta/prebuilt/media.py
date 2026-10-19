"""`media` fmt namespace (aliases `audio`, `av`) -- prebuilt, SPECULATIVE except where noted.

D17 asked `media.primary_audio_codec_name` (answer id `d17-audio-001-media-...`): the GM files audio/video members under
the generic `media` token, NOT the container's own (`wav`, `mp3`). D16 lesson repeated: an extractor registered only as
`wav.*` / `mp3.*` is invisible when the question says `media.*`. So this module
  1. routes every field the wav / mp3 / gif prebuilt modules already extract (`media.fmt_sample_rate`,
     `media.id3_title`, `media.info_icmt`, `media.logical_screen_dimensions_pixels`, ...) to the module the MAGIC
     names (RIFF/RIFX/RF64 WAVE -> wav, ID3 / ID3v1 TAG / MPEG sync -> mp3, GIF8[79]a -> gif), never the extension
     ("transcoded, renamed" members);
  2. adds ffprobe-style first-audio-stream fields under the D17 naming (`primary_audio_<ffprobe stream key>`):
     sample_rate (Hz int), channels, bits_per_sample (PCM only), sample_fmt (libavcodec decoder output: s16, u8,
     s32, flt, dbl, fltp), channel_layout (mono/stereo), plus format_name (ffprobe format.format_name);
  3. shares the GM-verified D17 codec reader (lib/meta/media.py; 16-bit PCM WAV -> `pcm_s16le`, unchanged) under the
     `audio` / `av` fmt tokens. (`media`, `primary_audio_codec_name`) itself stays the verified builtin.
Recognisably non-media bytes (PNG/JPEG/PDF/ZIP/PE/ELF/OLE/plain text renamed .wav) -> "none" (no audio stream);
unknown / unreadable bytes -> None (cannot answer)."""
import struct

from ..spell import Hex

FIELDS = {
    ("media", "primary_audio_codec"): "codec_name",
    ("media", "audio_codec_name"): "codec_name",
    ("media", "audio_codec"): "codec_name",
    ("media", "first_audio_codec_name"): "codec_name",
    ("media", "first_audio_stream_codec_name"): "codec_name",
    ("media", "audio_stream_codec_name"): "codec_name",
    ("media", "primary_audio_sample_rate"): "stream_value",
    ("media", "primary_audio_sample_rate_hz"): "stream_value",
    ("media", "audio_sample_rate"): "stream_value",
    ("media", "audio_sample_rate_hz"): "stream_value",
    ("media", "sample_rate"): "stream_value",
    ("media", "sample_rate_hz"): "stream_value",
    ("media", "primary_audio_channels"): "stream_value",
    ("media", "primary_audio_channel_count"): "stream_value",
    ("media", "audio_channels"): "stream_value",
    ("media", "audio_channel_count"): "stream_value",
    ("media", "channels"): "stream_value",
    ("media", "channel_count"): "stream_value",
    ("media", "num_channels"): "stream_value",
    ("media", "primary_audio_bits_per_sample"): "stream_value",
    ("media", "audio_bits_per_sample"): "stream_value",
    ("media", "bits_per_sample"): "stream_value",
    ("media", "primary_audio_bit_depth"): "stream_value",
    ("media", "audio_bit_depth"): "stream_value",
    ("media", "bit_depth"): "stream_value",
    ("media", "primary_audio_sample_fmt"): "stream_value",
    ("media", "audio_sample_fmt"): "stream_value",
    ("media", "primary_audio_sample_format"): "stream_value",
    ("media", "sample_fmt"): "stream_value",
    ("media", "primary_audio_channel_layout"): "stream_value",
    ("media", "audio_channel_layout"): "stream_value",
    ("media", "channel_layout"): "stream_value",
    ("media", "format_name"): "format_name",
    ("media", "container_format_name"): "format_name",
    ("media", "container_format"): "format_name",
    ("media", "container_name"): "format_name",
    ("media", "container"): "format_name",
    ("media", "fmt_sample_rate"): "media_route",
    ("media", "fmt_samples_per_sec"): "media_route",
    ("media", "samples_per_sec"): "media_route",
    ("media", "fmt_sample_rate_hz"): "media_route",
    ("media", "fmt_channels"): "media_route",
    ("media", "fmt_num_channels"): "media_route",
    ("media", "fmt_bits_per_sample"): "media_route",
    ("media", "fmt_block_align"): "media_route",
    ("media", "block_align"): "media_route",
    ("media", "fmt_byte_rate"): "media_route",
    ("media", "byte_rate"): "media_route",
    ("media", "fmt_avg_bytes_per_sec"): "media_route",
    ("media", "avg_bytes_per_sec"): "media_route",
    ("media", "fmt_audio_format"): "media_route",
    ("media", "audio_format"): "media_route",
    ("media", "fmt_format_tag"): "media_route",
    ("media", "format_tag"): "media_route",
    ("media", "fmt_audio_format_u16_hex"): "media_route",
    ("media", "fmt_format_tag_u16_hex"): "media_route",
    ("media", "audio_format_u16_hex"): "media_route",
    ("media", "format_tag_u16_hex"): "media_route",
    ("media", "data_size_bytes"): "media_route",
    ("media", "data_chunk_size"): "media_route",
    ("media", "data_chunk_size_bytes"): "media_route",
    ("media", "info_*"): "media_route",
    ("media", "list_info_*"): "media_route",
    ("media", "riff_info_*"): "media_route",
    ("media", "info_tag_ids"): "media_route",
    ("media", "info_chunk_ids"): "media_route",
    ("media", "title"): "media_route",
    ("media", "artist"): "media_route",
    ("media", "comment"): "media_route",
    ("media", "software"): "media_route",
    ("media", "copyright"): "media_route",
    ("media", "id3_title"): "media_route",
    ("media", "id3_artist"): "media_route",
    ("media", "id3_album"): "media_route",
    ("media", "id3_album_artist"): "media_route",
    ("media", "id3_year"): "media_route",
    ("media", "id3_date"): "media_route",
    ("media", "id3_recording_time"): "media_route",
    ("media", "id3_genre"): "media_route",
    ("media", "id3_track"): "media_route",
    ("media", "id3_track_number"): "media_route",
    ("media", "id3_composer"): "media_route",
    ("media", "id3_encoder"): "media_route",
    ("media", "id3_encoded_by"): "media_route",
    ("media", "id3_encoder_settings"): "media_route",
    ("media", "id3_publisher"): "media_route",
    ("media", "id3_copyright"): "media_route",
    ("media", "id3_comment"): "media_route",
    ("media", "id3_comments"): "media_route",
    ("media", "id3_comm"): "media_route",
    ("media", "id3_comment_text"): "media_route",
    ("media", "id3_version"): "media_route",
    ("media", "id3v2_version"): "media_route",
    ("media", "id3_tag_version"): "media_route",
    ("media", "tag_version"): "media_route",
    ("media", "id3v2_major_version"): "media_route",
    ("media", "id3_major_version"): "media_route",
    ("media", "id3_tag_size"): "media_route",
    ("media", "id3v2_tag_size"): "media_route",
    ("media", "id3_size"): "media_route",
    ("media", "id3_frame_ids"): "media_route",
    ("media", "id3_frame_names"): "media_route",
    ("media", "id3v2_frame_ids"): "media_route",
    ("media", "frame_ids"): "media_route",
    ("media", "title"): "media_route",
    ("media", "artist"): "media_route",
    ("media", "album"): "media_route",
    ("media", "comment"): "media_route",
    ("media", "id3v2_title"): "media_route",
    ("media", "id3v2_artist"): "media_route",
    ("media", "id3v2_album"): "media_route",
    ("media", "id3v2_comment"): "media_route",
    ("media", "id3v1_title"): "media_route",
    ("media", "id3v1_artist"): "media_route",
    ("media", "id3v1_album"): "media_route",
    ("media", "id3v1_year"): "media_route",
    ("media", "id3v1_comment"): "media_route",
    ("media", "id3v1_genre"): "media_route",
    ("media", "id3_*"): "media_route",
    ("media", "logical_screen_dimensions_pixels"): "media_route",
    ("media", "logical_screen_descriptor_dimensions_pixels"): "media_route",
    ("media", "lsd_dimensions_pixels"): "media_route",
    ("media", "screen_dimensions_pixels"): "media_route",
    ("media", "dimensions_pixels"): "media_route",
    ("media", "image_dimensions_pixels"): "media_route",
    ("media", "logical_screen_width"): "media_route",
    ("media", "logical_screen_height"): "media_route",
    ("media", "version"): "media_route",
    ("media", "header_version"): "media_route",
    ("media", "gif_version"): "media_route",
    ("media", "signature_version"): "media_route",
    ("media", "frame_count"): "media_route",
    ("media", "image_count"): "media_route",
    ("media", "image_descriptor_count"): "media_route",
    ("media", "number_of_frames"): "media_route",
    ("media", "frames_count"): "media_route",
    ("media", "global_color_table_present"): "media_route",
    ("media", "has_global_color_table"): "media_route",
    ("media", "global_color_table_flag"): "media_route",
    ("media", "global_color_table_size"): "media_route",
    ("media", "global_color_table_entries"): "media_route",
    ("media", "background_color_index"): "media_route",
    ("media", "loop_count"): "media_route",
    ("media", "netscape_loop_count"): "media_route",
    ("media", "comment"): "media_route",
    ("media", "comment_text"): "media_route",
    ("audio", "primary_audio_codec_name"): "codec_name",
    ("audio", "primary_audio_codec"): "codec_name",
    ("audio", "audio_codec_name"): "codec_name",
    ("audio", "audio_codec"): "codec_name",
    ("audio", "first_audio_codec_name"): "codec_name",
    ("audio", "first_audio_stream_codec_name"): "codec_name",
    ("audio", "audio_stream_codec_name"): "codec_name",
    ("audio", "primary_audio_sample_rate"): "stream_value",
    ("audio", "primary_audio_sample_rate_hz"): "stream_value",
    ("audio", "audio_sample_rate"): "stream_value",
    ("audio", "audio_sample_rate_hz"): "stream_value",
    ("audio", "sample_rate"): "stream_value",
    ("audio", "sample_rate_hz"): "stream_value",
    ("audio", "primary_audio_channels"): "stream_value",
    ("audio", "primary_audio_channel_count"): "stream_value",
    ("audio", "audio_channels"): "stream_value",
    ("audio", "audio_channel_count"): "stream_value",
    ("audio", "channels"): "stream_value",
    ("audio", "channel_count"): "stream_value",
    ("audio", "num_channels"): "stream_value",
    ("audio", "primary_audio_bits_per_sample"): "stream_value",
    ("audio", "audio_bits_per_sample"): "stream_value",
    ("audio", "bits_per_sample"): "stream_value",
    ("audio", "primary_audio_bit_depth"): "stream_value",
    ("audio", "audio_bit_depth"): "stream_value",
    ("audio", "bit_depth"): "stream_value",
    ("audio", "primary_audio_sample_fmt"): "stream_value",
    ("audio", "audio_sample_fmt"): "stream_value",
    ("audio", "primary_audio_sample_format"): "stream_value",
    ("audio", "sample_fmt"): "stream_value",
    ("audio", "primary_audio_channel_layout"): "stream_value",
    ("audio", "audio_channel_layout"): "stream_value",
    ("audio", "channel_layout"): "stream_value",
    ("audio", "format_name"): "format_name",
    ("audio", "container_format_name"): "format_name",
    ("audio", "container_format"): "format_name",
    ("audio", "container_name"): "format_name",
    ("audio", "container"): "format_name",
    ("audio", "fmt_sample_rate"): "media_route",
    ("audio", "fmt_samples_per_sec"): "media_route",
    ("audio", "samples_per_sec"): "media_route",
    ("audio", "fmt_sample_rate_hz"): "media_route",
    ("audio", "fmt_channels"): "media_route",
    ("audio", "fmt_num_channels"): "media_route",
    ("audio", "fmt_bits_per_sample"): "media_route",
    ("audio", "fmt_block_align"): "media_route",
    ("audio", "block_align"): "media_route",
    ("audio", "fmt_byte_rate"): "media_route",
    ("audio", "byte_rate"): "media_route",
    ("audio", "fmt_avg_bytes_per_sec"): "media_route",
    ("audio", "avg_bytes_per_sec"): "media_route",
    ("audio", "fmt_audio_format"): "media_route",
    ("audio", "audio_format"): "media_route",
    ("audio", "fmt_format_tag"): "media_route",
    ("audio", "format_tag"): "media_route",
    ("audio", "fmt_audio_format_u16_hex"): "media_route",
    ("audio", "fmt_format_tag_u16_hex"): "media_route",
    ("audio", "audio_format_u16_hex"): "media_route",
    ("audio", "format_tag_u16_hex"): "media_route",
    ("audio", "data_size_bytes"): "media_route",
    ("audio", "data_chunk_size"): "media_route",
    ("audio", "data_chunk_size_bytes"): "media_route",
    ("audio", "info_*"): "media_route",
    ("audio", "list_info_*"): "media_route",
    ("audio", "riff_info_*"): "media_route",
    ("audio", "info_tag_ids"): "media_route",
    ("audio", "info_chunk_ids"): "media_route",
    ("audio", "title"): "media_route",
    ("audio", "artist"): "media_route",
    ("audio", "comment"): "media_route",
    ("audio", "software"): "media_route",
    ("audio", "copyright"): "media_route",
    ("audio", "id3_title"): "media_route",
    ("audio", "id3_artist"): "media_route",
    ("audio", "id3_album"): "media_route",
    ("audio", "id3_album_artist"): "media_route",
    ("audio", "id3_year"): "media_route",
    ("audio", "id3_date"): "media_route",
    ("audio", "id3_recording_time"): "media_route",
    ("audio", "id3_genre"): "media_route",
    ("audio", "id3_track"): "media_route",
    ("audio", "id3_track_number"): "media_route",
    ("audio", "id3_composer"): "media_route",
    ("audio", "id3_encoder"): "media_route",
    ("audio", "id3_encoded_by"): "media_route",
    ("audio", "id3_encoder_settings"): "media_route",
    ("audio", "id3_publisher"): "media_route",
    ("audio", "id3_copyright"): "media_route",
    ("audio", "id3_comment"): "media_route",
    ("audio", "id3_comments"): "media_route",
    ("audio", "id3_comm"): "media_route",
    ("audio", "id3_comment_text"): "media_route",
    ("audio", "id3_version"): "media_route",
    ("audio", "id3v2_version"): "media_route",
    ("audio", "id3_tag_version"): "media_route",
    ("audio", "tag_version"): "media_route",
    ("audio", "id3v2_major_version"): "media_route",
    ("audio", "id3_major_version"): "media_route",
    ("audio", "id3_tag_size"): "media_route",
    ("audio", "id3v2_tag_size"): "media_route",
    ("audio", "id3_size"): "media_route",
    ("audio", "id3_frame_ids"): "media_route",
    ("audio", "id3_frame_names"): "media_route",
    ("audio", "id3v2_frame_ids"): "media_route",
    ("audio", "frame_ids"): "media_route",
    ("audio", "title"): "media_route",
    ("audio", "artist"): "media_route",
    ("audio", "album"): "media_route",
    ("audio", "comment"): "media_route",
    ("audio", "id3v2_title"): "media_route",
    ("audio", "id3v2_artist"): "media_route",
    ("audio", "id3v2_album"): "media_route",
    ("audio", "id3v2_comment"): "media_route",
    ("audio", "id3v1_title"): "media_route",
    ("audio", "id3v1_artist"): "media_route",
    ("audio", "id3v1_album"): "media_route",
    ("audio", "id3v1_year"): "media_route",
    ("audio", "id3v1_comment"): "media_route",
    ("audio", "id3v1_genre"): "media_route",
    ("audio", "id3_*"): "media_route",
    ("av", "primary_audio_codec_name"): "codec_name",
    ("av", "primary_audio_codec"): "codec_name",
    ("av", "audio_codec_name"): "codec_name",
    ("av", "audio_codec"): "codec_name",
    ("av", "first_audio_codec_name"): "codec_name",
    ("av", "first_audio_stream_codec_name"): "codec_name",
    ("av", "audio_stream_codec_name"): "codec_name",
    ("av", "primary_audio_sample_rate"): "stream_value",
    ("av", "primary_audio_sample_rate_hz"): "stream_value",
    ("av", "audio_sample_rate"): "stream_value",
    ("av", "audio_sample_rate_hz"): "stream_value",
    ("av", "sample_rate"): "stream_value",
    ("av", "sample_rate_hz"): "stream_value",
    ("av", "primary_audio_channels"): "stream_value",
    ("av", "primary_audio_channel_count"): "stream_value",
    ("av", "audio_channels"): "stream_value",
    ("av", "audio_channel_count"): "stream_value",
    ("av", "channels"): "stream_value",
    ("av", "channel_count"): "stream_value",
    ("av", "num_channels"): "stream_value",
    ("av", "primary_audio_bits_per_sample"): "stream_value",
    ("av", "audio_bits_per_sample"): "stream_value",
    ("av", "bits_per_sample"): "stream_value",
    ("av", "primary_audio_bit_depth"): "stream_value",
    ("av", "audio_bit_depth"): "stream_value",
    ("av", "bit_depth"): "stream_value",
    ("av", "primary_audio_sample_fmt"): "stream_value",
    ("av", "audio_sample_fmt"): "stream_value",
    ("av", "primary_audio_sample_format"): "stream_value",
    ("av", "sample_fmt"): "stream_value",
    ("av", "primary_audio_channel_layout"): "stream_value",
    ("av", "audio_channel_layout"): "stream_value",
    ("av", "channel_layout"): "stream_value",
    ("av", "format_name"): "format_name",
    ("av", "container_format_name"): "format_name",
    ("av", "container_format"): "format_name",
    ("av", "container_name"): "format_name",
    ("av", "container"): "format_name",
    ("av", "fmt_sample_rate"): "media_route",
    ("av", "fmt_samples_per_sec"): "media_route",
    ("av", "samples_per_sec"): "media_route",
    ("av", "fmt_sample_rate_hz"): "media_route",
    ("av", "fmt_channels"): "media_route",
    ("av", "fmt_num_channels"): "media_route",
    ("av", "fmt_bits_per_sample"): "media_route",
    ("av", "fmt_block_align"): "media_route",
    ("av", "block_align"): "media_route",
    ("av", "fmt_byte_rate"): "media_route",
    ("av", "byte_rate"): "media_route",
    ("av", "fmt_avg_bytes_per_sec"): "media_route",
    ("av", "avg_bytes_per_sec"): "media_route",
    ("av", "fmt_audio_format"): "media_route",
    ("av", "audio_format"): "media_route",
    ("av", "fmt_format_tag"): "media_route",
    ("av", "format_tag"): "media_route",
    ("av", "fmt_audio_format_u16_hex"): "media_route",
    ("av", "fmt_format_tag_u16_hex"): "media_route",
    ("av", "audio_format_u16_hex"): "media_route",
    ("av", "format_tag_u16_hex"): "media_route",
    ("av", "data_size_bytes"): "media_route",
    ("av", "data_chunk_size"): "media_route",
    ("av", "data_chunk_size_bytes"): "media_route",
    ("av", "info_*"): "media_route",
    ("av", "list_info_*"): "media_route",
    ("av", "riff_info_*"): "media_route",
    ("av", "info_tag_ids"): "media_route",
    ("av", "info_chunk_ids"): "media_route",
    ("av", "title"): "media_route",
    ("av", "artist"): "media_route",
    ("av", "comment"): "media_route",
    ("av", "software"): "media_route",
    ("av", "copyright"): "media_route",
    ("av", "id3_title"): "media_route",
    ("av", "id3_artist"): "media_route",
    ("av", "id3_album"): "media_route",
    ("av", "id3_album_artist"): "media_route",
    ("av", "id3_year"): "media_route",
    ("av", "id3_date"): "media_route",
    ("av", "id3_recording_time"): "media_route",
    ("av", "id3_genre"): "media_route",
    ("av", "id3_track"): "media_route",
    ("av", "id3_track_number"): "media_route",
    ("av", "id3_composer"): "media_route",
    ("av", "id3_encoder"): "media_route",
    ("av", "id3_encoded_by"): "media_route",
    ("av", "id3_encoder_settings"): "media_route",
    ("av", "id3_publisher"): "media_route",
    ("av", "id3_copyright"): "media_route",
    ("av", "id3_comment"): "media_route",
    ("av", "id3_comments"): "media_route",
    ("av", "id3_comm"): "media_route",
    ("av", "id3_comment_text"): "media_route",
    ("av", "id3_version"): "media_route",
    ("av", "id3v2_version"): "media_route",
    ("av", "id3_tag_version"): "media_route",
    ("av", "tag_version"): "media_route",
    ("av", "id3v2_major_version"): "media_route",
    ("av", "id3_major_version"): "media_route",
    ("av", "id3_tag_size"): "media_route",
    ("av", "id3v2_tag_size"): "media_route",
    ("av", "id3_size"): "media_route",
    ("av", "id3_frame_ids"): "media_route",
    ("av", "id3_frame_names"): "media_route",
    ("av", "id3v2_frame_ids"): "media_route",
    ("av", "frame_ids"): "media_route",
    ("av", "title"): "media_route",
    ("av", "artist"): "media_route",
    ("av", "album"): "media_route",
    ("av", "comment"): "media_route",
    ("av", "id3v2_title"): "media_route",
    ("av", "id3v2_artist"): "media_route",
    ("av", "id3v2_album"): "media_route",
    ("av", "id3v2_comment"): "media_route",
    ("av", "id3v1_title"): "media_route",
    ("av", "id3v1_artist"): "media_route",
    ("av", "id3v1_album"): "media_route",
    ("av", "id3v1_year"): "media_route",
    ("av", "id3v1_comment"): "media_route",
    ("av", "id3v1_genre"): "media_route",
    ("av", "id3_*"): "media_route",
    ("media", "primary_audio_bit_rate"): "stream_info",
    ("media", "primary_audio_bitrate"): "stream_info",
    ("media", "audio_bit_rate"): "stream_info",
    ("media", "audio_bitrate"): "stream_info",
    ("media", "stream_bit_rate"): "stream_info",
    ("media", "primary_audio_codec_long_name"): "stream_info",
    ("media", "audio_codec_long_name"): "stream_info",
    ("media", "codec_long_name"): "stream_info",
    ("media", "primary_audio_codec_tag_hex"): "stream_info",
    ("media", "primary_audio_codec_tag"): "stream_info",
    ("media", "primary_audio_codec_tag_u32_hex"): "stream_info",
    ("media", "audio_codec_tag_hex"): "stream_info",
    ("media", "codec_tag_hex"): "stream_info",
    ("media", "codec_tag"): "stream_info",
    ("media", "primary_audio_codec_tag_string"): "stream_info",
    ("media", "audio_codec_tag_string"): "stream_info",
    ("media", "codec_tag_string"): "stream_info",
    ("media", "primary_audio_duration_seconds"): "stream_info",
    ("media", "primary_audio_duration"): "stream_info",
    ("media", "audio_duration_seconds"): "stream_info",
    ("media", "audio_duration"): "stream_info",
    ("media", "stream_duration_seconds"): "stream_info",
    ("media", "primary_audio_nb_samples"): "stream_info",
    ("media", "primary_audio_duration_ts"): "stream_info",
    ("media", "primary_audio_sample_count"): "stream_info",
    ("media", "nb_samples"): "stream_info",
    ("media", "duration_ts"): "stream_info",
    ("media", "sample_count"): "stream_info",
    ("media", "audio_nb_samples"): "stream_info",
    ("media", "audio_duration_ts"): "stream_info",
    ("media", "format_long_name"): "stream_info",
    ("media", "container_long_name"): "stream_info",
    ("media", "container_format_long_name"): "stream_info",
    ("media", "nb_streams"): "stream_info",
    ("media", "format_nb_streams"): "stream_info",
    ("media", "stream_count"): "stream_info",
    ("media", "number_of_streams"): "stream_info",
    ("media", "audio_stream_count"): "stream_info",
    ("media", "nb_audio_streams"): "stream_info",
    ("media", "audio_streams_count"): "stream_info",
    ("media", "number_of_audio_streams"): "stream_info",
    ("media", "format_duration_seconds"): "stream_info",
    ("media", "format_duration"): "stream_info",
    ("media", "duration_seconds"): "stream_info",
    ("media", "duration"): "stream_info",
    ("media", "format_size_bytes"): "stream_info",
    ("media", "format_size"): "stream_info",
    ("media", "format_bit_rate"): "stream_info",
    ("media", "format_bitrate"): "stream_info",
    ("media", "overall_bit_rate"): "stream_info",
    ("media", "overall_bitrate"): "stream_info",
    ("media", "container_bit_rate"): "stream_info",
    ("audio", "primary_audio_bit_rate"): "stream_info",
    ("audio", "primary_audio_bitrate"): "stream_info",
    ("audio", "audio_bit_rate"): "stream_info",
    ("audio", "audio_bitrate"): "stream_info",
    ("audio", "stream_bit_rate"): "stream_info",
    ("audio", "primary_audio_codec_long_name"): "stream_info",
    ("audio", "audio_codec_long_name"): "stream_info",
    ("audio", "codec_long_name"): "stream_info",
    ("audio", "primary_audio_codec_tag_hex"): "stream_info",
    ("audio", "primary_audio_codec_tag"): "stream_info",
    ("audio", "primary_audio_codec_tag_u32_hex"): "stream_info",
    ("audio", "audio_codec_tag_hex"): "stream_info",
    ("audio", "codec_tag_hex"): "stream_info",
    ("audio", "codec_tag"): "stream_info",
    ("audio", "primary_audio_codec_tag_string"): "stream_info",
    ("audio", "audio_codec_tag_string"): "stream_info",
    ("audio", "codec_tag_string"): "stream_info",
    ("audio", "primary_audio_duration_seconds"): "stream_info",
    ("audio", "primary_audio_duration"): "stream_info",
    ("audio", "audio_duration_seconds"): "stream_info",
    ("audio", "audio_duration"): "stream_info",
    ("audio", "stream_duration_seconds"): "stream_info",
    ("audio", "primary_audio_nb_samples"): "stream_info",
    ("audio", "primary_audio_duration_ts"): "stream_info",
    ("audio", "primary_audio_sample_count"): "stream_info",
    ("audio", "nb_samples"): "stream_info",
    ("audio", "duration_ts"): "stream_info",
    ("audio", "sample_count"): "stream_info",
    ("audio", "audio_nb_samples"): "stream_info",
    ("audio", "audio_duration_ts"): "stream_info",
    ("audio", "format_long_name"): "stream_info",
    ("audio", "container_long_name"): "stream_info",
    ("audio", "container_format_long_name"): "stream_info",
    ("audio", "nb_streams"): "stream_info",
    ("audio", "format_nb_streams"): "stream_info",
    ("audio", "stream_count"): "stream_info",
    ("audio", "number_of_streams"): "stream_info",
    ("audio", "audio_stream_count"): "stream_info",
    ("audio", "nb_audio_streams"): "stream_info",
    ("audio", "audio_streams_count"): "stream_info",
    ("audio", "number_of_audio_streams"): "stream_info",
    ("audio", "format_duration_seconds"): "stream_info",
    ("audio", "format_duration"): "stream_info",
    ("audio", "duration_seconds"): "stream_info",
    ("audio", "duration"): "stream_info",
    ("audio", "format_size_bytes"): "stream_info",
    ("audio", "format_size"): "stream_info",
    ("audio", "format_bit_rate"): "stream_info",
    ("audio", "format_bitrate"): "stream_info",
    ("audio", "overall_bit_rate"): "stream_info",
    ("audio", "overall_bitrate"): "stream_info",
    ("audio", "container_bit_rate"): "stream_info",
    ("av", "primary_audio_bit_rate"): "stream_info",
    ("av", "primary_audio_bitrate"): "stream_info",
    ("av", "audio_bit_rate"): "stream_info",
    ("av", "audio_bitrate"): "stream_info",
    ("av", "stream_bit_rate"): "stream_info",
    ("av", "primary_audio_codec_long_name"): "stream_info",
    ("av", "audio_codec_long_name"): "stream_info",
    ("av", "codec_long_name"): "stream_info",
    ("av", "primary_audio_codec_tag_hex"): "stream_info",
    ("av", "primary_audio_codec_tag"): "stream_info",
    ("av", "primary_audio_codec_tag_u32_hex"): "stream_info",
    ("av", "audio_codec_tag_hex"): "stream_info",
    ("av", "codec_tag_hex"): "stream_info",
    ("av", "codec_tag"): "stream_info",
    ("av", "primary_audio_codec_tag_string"): "stream_info",
    ("av", "audio_codec_tag_string"): "stream_info",
    ("av", "codec_tag_string"): "stream_info",
    ("av", "primary_audio_duration_seconds"): "stream_info",
    ("av", "primary_audio_duration"): "stream_info",
    ("av", "audio_duration_seconds"): "stream_info",
    ("av", "audio_duration"): "stream_info",
    ("av", "stream_duration_seconds"): "stream_info",
    ("av", "primary_audio_nb_samples"): "stream_info",
    ("av", "primary_audio_duration_ts"): "stream_info",
    ("av", "primary_audio_sample_count"): "stream_info",
    ("av", "nb_samples"): "stream_info",
    ("av", "duration_ts"): "stream_info",
    ("av", "sample_count"): "stream_info",
    ("av", "audio_nb_samples"): "stream_info",
    ("av", "audio_duration_ts"): "stream_info",
    ("av", "format_long_name"): "stream_info",
    ("av", "container_long_name"): "stream_info",
    ("av", "container_format_long_name"): "stream_info",
    ("av", "nb_streams"): "stream_info",
    ("av", "format_nb_streams"): "stream_info",
    ("av", "stream_count"): "stream_info",
    ("av", "number_of_streams"): "stream_info",
    ("av", "audio_stream_count"): "stream_info",
    ("av", "nb_audio_streams"): "stream_info",
    ("av", "audio_streams_count"): "stream_info",
    ("av", "number_of_audio_streams"): "stream_info",
    ("av", "format_duration_seconds"): "stream_info",
    ("av", "format_duration"): "stream_info",
    ("av", "duration_seconds"): "stream_info",
    ("av", "duration"): "stream_info",
    ("av", "format_size_bytes"): "stream_info",
    ("av", "format_size"): "stream_info",
    ("av", "format_bit_rate"): "stream_info",
    ("av", "format_bitrate"): "stream_info",
    ("av", "overall_bit_rate"): "stream_info",
    ("av", "overall_bitrate"): "stream_info",
    ("av", "container_bit_rate"): "stream_info",
}


_AUDIO_FMTS = ("media", "audio", "av")
_MOD = {"wav": None, "mp3": None, "gif": None}
_NON_MEDIA = (b"\x89PNG", b"\xff\xd8\xff", b"%PDF", b"PK\x03\x04", b"MZ", b"\x7fELF", b"\xd0\xcf\x11\xe0", b"BM",
              b"{\\rtf", b"SQLite format 3")
_MPEG_RATES = {3: (44100, 48000, 32000), 2: (22050, 24000, 16000), 0: (11025, 12000, 8000)}
_ADTS_RATES = (96000, 88200, 64000, 48000, 44100, 32000, 24000, 22050, 16000, 12000, 11025, 8000, 7350)
_SAMPLE_FMT = {"pcm_u8": "u8", "pcm_s8": "u8", "pcm_s16le": "s16", "pcm_s16be": "s16", "pcm_s24le": "s32",
               "pcm_s24be": "s32", "pcm_s32le": "s32", "pcm_s32be": "s32", "pcm_f32le": "flt", "pcm_f32be": "flt",
               "pcm_f64le": "dbl", "pcm_f64be": "dbl", "pcm_alaw": "s16", "pcm_mulaw": "s16", "adpcm_ms": "s16",
               "adpcm_ima_wav": "s16p", "mp3": "fltp", "mp2": "fltp", "aac": "fltp", "vorbis": "fltp",
               "opus": "fltp", "amr_nb": "flt", "amr_wb": "flt", "alac": "s16p",
               "wmav1": "fltp", "wmav2": "fltp", "wmapro": "fltp", "wmavoice": "flt", "adpcm_ima_qt": "s16p"}


def _container(b):
    """The prebuilt module a member belongs to by MAGIC (never the extension): 'wav' | 'mp3' | 'gif' | None."""
    if b[:4] in (b"RIFF", b"RIFX", b"RF64") and b[8:12] == b"WAVE":
        return "wav"
    if b[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if b[:3] == b"ID3" or (len(b) >= 128 and b[-128:-125] == b"TAG"):
        return "mp3"
    if len(b) > 4 and b[0] == 0xFF and (b[1] & 0xE0) == 0xE0 and (b[1] & 0x06):
        return "mp3"
    return None


def _non_media(b):
    """True when the bytes are recognisably NOT audio/video (image, document, archive, executable, plain text)."""
    if b.startswith(_NON_MEDIA) or b[:6] in (b"GIF87a", b"GIF89a"):
        return True
    head = b[:512]
    return bool(head) and all(c in b"\t\n\r" or 32 <= c < 127 for c in head)


def media_route(data, ctx):
    """media.<field> for a field the wav / mp3 / gif prebuilt modules extract: delegated to the module the MAGIC
    names, with ctx rewritten to that module's fmt. A field that module does not know -> None (cannot answer)."""
    if data is None:
        return None
    try:
        b = bytes(data)
        ctx = dict(ctx or {})
        field = ctx.get("field") or ""
        mod = _container(b)
        if mod is None:
            return "none" if _non_media(b) else None
        if _MOD[mod] is None:
            from . import gif, mp3, wav
            _MOD.update(wav=wav, mp3=mp3, gif=gif)
        m = _MOD[mod]
        fn = m.FIELDS.get((mod, field))
        param = ctx.get("param")
        if fn is None:
            fam = [k for (f, k) in m.FIELDS if f == mod and k.endswith("_*") and field.startswith(k[:-1])]
            if not fam:
                return None
            k = max(fam, key=len)
            fn, field, param = m.FIELDS[(mod, k)], k, field[len(k) - 1:]
        ctx.update(fmt=mod, field=field, param=param)
        return getattr(m, fn)(b, ctx)
    except Exception:  # noqa: BLE001 -- a malformed member never raises past the extractor
        return None


def codec_name(data, ctx):
    """ffprobe codec_name of the first audio stream: the GM-verified D17 reader (lib/meta/media.py), shared under the
    `audio` / `av` fmt aliases. A recognisably non-media member (PNG/PDF/text renamed .wav) has no audio -> none."""
    if not data:
        return None
    from ..media import primary_audio_codec_name
    alt = _alt(bytes(data))   # ASF / CAF first: the D17 reader's MPEG-sync fallback misreads CAF payload bytes
    v = alt["codec"] if alt.get("codec") else primary_audio_codec_name(bytes(data), ctx)
    if v is None and _non_media(bytes(data)):
        return "none"
    return v


def _alt(b):
    """{codec, sample_rate, channels, format_name} of an ASF/WMA or CAF member (containers lib/meta/media.py does not
    walk) via the prebuilt asf / caf parsers, else {}."""
    try:
        if b[:4] == b"caff":
            from .caf import codec_of, parse
            p = parse(b)
            d = p and p["desc"]
            if not d:
                return {"format_name": "caf"}
            return {"codec": codec_of(d), "sample_rate": int(d["rate"]), "channels": d["channels"],
                    "format_name": "caf"}
        if b[:16] == b"\x30\x26\xb2\x75\x8e\x66\xcf\x11\xa6\xd9\x00\xaa\x00\x62\xce\x6c":
            from .asf import codec_of, parse
            p = parse(b)
            a = next((x for x in (p or {}).get("streams", ()) if "tag" in x), None)
            if a is None:
                return {"format_name": "asf"}
            return {"codec": codec_of(a), "sample_rate": a["rate"], "channels": a["channels"], "format_name": "asf"}
    except (struct.error, IndexError, ValueError, TypeError):
        return {}
    return {}


def _f80(x):
    """IEEE 754 80-bit extended (AIFF COMM sampleRate) -> int Hz."""
    exp = ((x[0] & 0x7F) << 8 | x[1]) - 16383 - 63
    mant = int.from_bytes(x[2:10], "big")
    return int(mant * 2.0 ** exp) if mant else 0


def _stream(b, codec):
    """{sample_rate, channels, bits_per_sample} of the first audio stream from the container header (keys present only
    when the header stores them). Same container walk as media._audio_codec."""
    if b[:4] in (b"RIFF", b"RIFX", b"RF64") and b[8:12] == b"WAVE":
        en = ">" if b[:4] == b"RIFX" else "<"
        i = 12
        while i + 8 <= len(b):
            cid, ln = b[i:i + 4], struct.unpack(en + "I", b[i + 4:i + 8])[0]
            if cid == b"fmt ":
                tag, ch, rate, _br, _al, bits = struct.unpack_from(en + "HHIIHH", b, i + 8)
                return {"sample_rate": rate, "channels": ch, "bits_per_sample": bits}
            i += 8 + ln + (ln & 1)
        return {}
    if b[:4] == b"FORM" and b[8:12] in (b"AIFF", b"AIFC"):
        i = 12
        while i + 8 <= len(b):
            cid, ln = b[i:i + 4], struct.unpack(">I", b[i + 4:i + 8])[0]
            if cid == b"COMM":
                ch, _n, bits = struct.unpack_from(">HIH", b, i + 8)
                return {"sample_rate": _f80(b[i + 16:i + 26]), "channels": ch, "bits_per_sample": bits}
            i += 8 + ln + (ln & 1)
        return {}
    if b[:4] == b"fLaC" and len(b) >= 26:   # STREAMINFO: 20-bit rate, 3-bit channels-1, 5-bit bps-1
        v = int.from_bytes(b[18:21], "big")
        return {"sample_rate": v >> 4, "channels": ((v >> 1) & 7) + 1}
    if b[:4] == b"OggS" and len(b) > 27:
        p = 27 + b[26]
        if b[p:p + 8] == b"OpusHead":
            return {"sample_rate": 48000, "channels": b[p + 9]}   # libavcodec decodes Opus at 48 kHz always
        if b[p:p + 7] == b"\x01vorbis":
            return {"sample_rate": struct.unpack_from("<I", b, p + 12)[0], "channels": b[p + 11]}
        if b[p:p + 5] == b"\x7fFLAC" and b[p + 9:p + 13] == b"fLaC":
            v = int.from_bytes(b[p + 27:p + 30], "big")
            return {"sample_rate": v >> 4, "channels": ((v >> 1) & 7) + 1}
        return {}
    if b[:6] == b"#!AMR\n":
        return {"sample_rate": 8000, "channels": 1}
    if b[:9] == b"#!AMR-WB\n":
        return {"sample_rate": 16000, "channels": 1}
    if b[:4] == b".snd" and len(b) >= 24:
        _o, _s, enc, rate, ch = struct.unpack_from(">IIIII", b, 4)
        bits = {1: 8, 2: 8, 3: 16, 4: 24, 5: 32, 6: 32, 7: 64, 27: 8}.get(enc)
        return dict({"sample_rate": rate, "channels": ch}, **({"bits_per_sample": bits} if bits else {}))
    if b[4:8] == b"ftyp":
        k = b.find(b"stsd")
        if k >= 0 and k + 48 <= len(b):
            e = k + 12   # stsd: size(4 before) 'stsd' ver/flags(4) entry_count(4); entry: size type[4] reserved...
            ch, bits = struct.unpack_from(">HH", b, e + 24)
            rate = struct.unpack_from(">I", b, e + 32)[0] >> 16
            return {"sample_rate": rate, "channels": ch}
        return {}
    if codec in ("mp3", "mp2", "mp1", "aac"):
        i = 0
        if b[:3] == b"ID3" and len(b) > 10:
            sz = b[6:10]
            i = 10 + ((sz[0] << 21) | (sz[1] << 14) | (sz[2] << 7) | sz[3])
        for j in range(i, min(len(b) - 3, i + 65536)):
            if b[j] == 0xFF and (b[j + 1] & 0xE0) == 0xE0:
                h = b[j + 1:j + 4]
                if codec == "aac":
                    if (h[0] & 0xF6) != 0xF0:
                        continue
                    fi, cc = (h[1] >> 2) & 0xF, ((h[1] & 1) << 2) | (h[2] >> 6)
                    out = {"sample_rate": _ADTS_RATES[fi]} if fi < 13 else {}
                    return dict(out, **({"channels": cc} if cc else {}))
                ver, ri = (h[0] >> 3) & 3, (h[1] >> 2) & 3
                if ver == 1 or ri == 3 or not (h[0] & 0x06):
                    continue
                return {"sample_rate": _MPEG_RATES[ver][ri], "channels": 1 if (h[2] >> 6) == 3 else 2}
    return {}


def stream_value(data, ctx):
    """media.primary_audio_<sample_rate|channels|bits_per_sample|sample_fmt|channel_layout> (+ aliases): ffprobe's
    first-audio-stream values from the container header. sample_rate in Hz (int); channels int; bits_per_sample = ffprobe's
    av_get_bits_per_sample(codec_id) (pcm_s24le 24, pcm_u8/alaw/mulaw 8, adpcm 4, lossy/flac 0);
    sample_fmt = libavcodec's decoder output format for the codec (s16 / u8 / s32 / flt / dbl / fltp);
    channel_layout = mono/stereo for 1/2 channels (ffmpeg's default layout; others -> None).
    Recognisably non-media bytes (image/document/text renamed .wav) -> none; unreadable audio -> None."""
    if not data:
        return None
    try:
        b = bytes(data)
        from ..media import _audio_codec
        s = _alt(b) or None   # ASF / CAF first (see codec_name)
        codec = s.get("codec") if s else _audio_codec(b)
        if codec is None:
            return "none" if _non_media(b) else None
        s = s or _stream(b, codec)
        f = (ctx or {}).get("field") or ""
        if "sample_fmt" in f or "sample_format" in f:
            return _SAMPLE_FMT.get(codec)
        if "layout" in f:
            return {1: "mono", 2: "stereo"}.get(s.get("channels"))
        if "sample_rate" in f:
            return s.get("sample_rate") or None
        if "channel" in f:
            return s.get("channels") or None
        if "bit" in f:
            return _bits_per_sample(codec)
        return None
    except Exception:  # noqa: BLE001
        return None


_FORMAT_NAMES = (((b"RIFF", 0), (b"WAVE", 8), "wav"), ((b"RIFX", 0), (b"WAVE", 8), "wav"),
                 ((b"RF64", 0), (b"WAVE", 8), "wav"), ((b"FORM", 0), (b"AIFF", 8), "aiff"),
                 ((b"FORM", 0), (b"AIFC", 8), "aiff"), ((b"fLaC", 0), (b"", 0), "flac"),
                 ((b"OggS", 0), (b"", 0), "ogg"), ((b"#!AMR", 0), (b"", 0), "amr"), ((b".snd", 0), (b"", 0), "au"),
                 ((b"ftyp", 4), (b"", 0), "mov,mp4,m4a,3gp,3g2,mj2"),
                 ((b"\x1a\x45\xdf\xa3", 0), (b"", 0), "matroska,webm"))


def format_name(data, ctx):
    """ffprobe format.format_name of the container, by MAGIC: wav, aiff, flac, ogg, amr, au, mp3 (ID3 / MPEG sync),
    aac (ADTS), mov,mp4,m4a,3gp,3g2,mj2 (ftyp), matroska,webm (EBML). Non-media -> none; unknown -> None."""
    if not data:
        return None
    try:
        b = bytes(data)
        for (m1, o1), (m2, o2), name in _FORMAT_NAMES:
            if b[o1:o1 + len(m1)] == m1 and b[o2:o2 + len(m2)] == m2:
                return name
        if _alt(b):
            return _alt(b).get("format_name")
        if _non_media(b):
            return "none"
        from ..media import _audio_codec
        c = _audio_codec(b)
        return {"mp3": "mp3", "mp2": "mp3", "mp1": "mp3", "aac": "aac"}.get(c)
    except Exception:  # noqa: BLE001
        return None


_LONG_NAMES = {"aac": "AAC (Advanced Audio Coding)", "ac3": "ATSC A/52A (AC-3)", "adpcm_ima_qt": "ADPCM IMA QuickTime",
               "adpcm_ima_wav": "ADPCM IMA WAV", "adpcm_ms": "ADPCM Microsoft",
               "alac": "ALAC (Apple Lossless Audio Codec)", "amr_nb": "AMR-NB (Adaptive Multi-Rate NarrowBand)",
               "amr_wb": "AMR-WB (Adaptive Multi-Rate WideBand)", "dts": "DCA (DTS Coherent Acoustics)",
               "eac3": "ATSC A/52B (AC-3, E-AC-3)", "flac": "FLAC (Free Lossless Audio Codec)",
               "gsm_ms": "GSM Microsoft variant", "mp1": "MP1 (MPEG audio layer 1)", "mp2": "MP2 (MPEG audio layer 2)",
               "mp3": "MP3 (MPEG audio layer 3)", "opus": "Opus (Opus Interactive Audio Codec)",
               "pcm_alaw": "PCM A-law / G.711 A-law", "pcm_mulaw": "PCM mu-law / G.711 mu-law", "speex": "Speex",
               "vorbis": "Vorbis", "wmapro": "Windows Media Audio 9 Professional", "wmav1": "Windows Media Audio 1",
               "wmav2": "Windows Media Audio 2", "pcm_u8": "PCM unsigned 8-bit", "pcm_s8": "PCM signed 8-bit"}
_FORMAT_LONG = {"wav": "WAV / WAVE (Waveform Audio)", "aiff": "Audio IFF", "flac": "raw FLAC", "ogg": "Ogg",
                "amr": "3GPP AMR", "au": "Sun AU", "mov,mp4,m4a,3gp,3g2,mj2": "QuickTime / MOV",
                "matroska,webm": "Matroska / WebM", "mp3": "MP2/3 (MPEG audio layer 2/3)",
                "aac": "raw ADTS AAC (Advanced Audio Coding)"}   # ffmpeg 7.0.2 `-h demuxer=<name>` long names


def _bits_per_sample(codec):
    """ffprobe stream bits_per_sample = av_get_bits_per_sample(codec_id): PCM width, 8 for G.711, 4 for IMA/MS ADPCM,
    0 for everything else (mp3/aac/vorbis/opus/flac/alac...)."""
    if codec in ("pcm_alaw", "pcm_mulaw", "pcm_u8", "pcm_s8"):
        return 8
    if codec.startswith("pcm_"):
        d = "".join(c for c in codec[5:] if c.isdigit())
        return int(d) if d else 0
    return 4 if codec in ("adpcm_ms", "adpcm_ima_wav", "adpcm_ima_qt") else 0


def _long_name(codec):
    if codec in _LONG_NAMES:
        return _LONG_NAMES[codec]
    if codec.startswith("pcm_"):   # pcm_s16le -> "PCM signed 16-bit little-endian" (libavcodec descriptor text)
        k, rest = codec[4], codec[5:]
        bits, end = rest[:-2], {"le": "little-endian", "be": "big-endian"}.get(rest[-2:])
        kind = {"s": "signed", "u": "unsigned"}.get(k)
        if kind and end and bits.isdigit():
            return "PCM %s %s-bit %s" % (kind, bits, end)
        if k == "f" and end and bits.isdigit():
            return "PCM %s-bit floating point %s" % (bits, end)
    return None


def _chunks(b, start, en):
    """[(id, body_offset, body_len)] of a RIFF/IFF chunk list (pad byte honoured; a short last body is clipped)."""
    out, i = [], start
    while i + 8 <= len(b):
        ln = struct.unpack(en + "I", b[i + 4:i + 8])[0]
        out.append((b[i:i + 4], i + 8, ln))
        i += 8 + ln + (ln & 1)
    return out


def _ogg_pages(b):
    """[(header_type, granule, serial, body)] of every Ogg page (stops at the first broken capture pattern)."""
    out, i = [], 0
    while i + 27 <= len(b) and b[i:i + 4] == b"OggS":
        ht, gr, ser = b[i + 5], struct.unpack_from("<q", b, i + 6)[0], struct.unpack_from("<I", b, i + 14)[0]
        n = b[i + 26]
        body = sum(b[i + 27:i + 27 + n])
        out.append((ht, gr, ser, b[i + 27 + n:i + 27 + n + body]))
        i += 27 + n + body
    return out


def _probe(b):
    """ffprobe-like {codec, codec_tag, rate, channels, nb_samples, bit_rate, nb_streams, audio_streams} for the first
    audio stream (keys only when derivable from the header bytes). duration_ts == nb_samples (time_base 1/rate) for
    WAV / AIFF / FLAC / Ogg (Opus: 1/48000, last granule as ffmpeg reports it)."""
    from ..media import _audio_codec
    codec = _audio_codec(b)
    if codec is None:
        return None
    s = _stream(b, codec)
    out = {"codec": codec, "codec_tag": 0, "nb_streams": 1, "audio_streams": 1}
    rate, ch = s.get("sample_rate"), s.get("channels")
    if b[:4] in (b"RIFF", b"RIFX", b"RF64") and b[8:12] == b"WAVE":
        en = ">" if b[:4] == b"RIFX" else "<"
        ck = _chunks(b, 12, en)
        fmt = next((c for c in ck if c[0] == b"fmt "), None)
        data = next((c for c in ck if c[0] == b"data"), None)
        if fmt is None:
            return out
        tag, _c, _r, byte_rate, align, bits = struct.unpack_from(en + "HHIIHH", b, fmt[1])
        if tag == 0xFFFE and fmt[2] >= 40:   # riff.c parse_waveformatex: codec_tag = SubFormat's first u32
            tag = struct.unpack_from(en + "I", b, fmt[1] + 24)[0]
        out["codec_tag"] = tag
        out["bit_rate"] = byte_rate * 8      # riff.c ff_get_wav_header: bit_rate = nAvgBytesPerSec * 8
        fact = next((c for c in ck if c[0] == b"fact"), None)
        if fact is not None and fact[2] >= 4 and not codec.startswith("pcm_"):
            out["nb_samples"] = struct.unpack_from(en + "I", b, fact[1])[0]
        elif data is not None and codec.startswith("pcm_") and align and b[:4] != b"RF64":
            # wavdec.c: sample_count = (data_size << 3) / (channels * bits_per_coded_sample)
            out["nb_samples"] = (data[2] * 8) // (ch * bits) if ch and bits else data[2] // align
    elif b[:4] == b"FORM":
        comm = next((c for c in _chunks(b, 12, ">") if c[0] == b"COMM"), None)
        if comm is not None:
            _c, frames, bits = struct.unpack_from(">HIH", b, comm[1])
            out["nb_samples"] = frames
            if codec.startswith("pcm_") and rate and ch:
                out["bit_rate"] = rate * ch * bits   # aiffdec.c: sample_rate * (block_align << 3)
    elif b[:4] == b"fLaC":
        v = int.from_bytes(b[18:26], "big")    # STREAMINFO: 20 rate | 3 ch-1 | 5 bps-1 | 36 total samples
        if v & 0xFFFFFFFFF:
            out["nb_samples"] = v & 0xFFFFFFFFF
        i, pic = 4, 0
        while i + 4 <= len(b):
            t, ln = b[i] & 0x7F, int.from_bytes(b[i + 1:i + 4], "big")
            pic += t == 6                      # PICTURE block = an attached_pic video stream in ffprobe
            if b[i] & 0x80:
                break
            i += 4 + ln
        out["nb_streams"] = 1 + pic
    elif b[:4] == b"OggS":
        pages = _ogg_pages(b)
        if not pages:
            return out
        first, ser = pages[0][3], pages[0][2]
        bos = [p for p in pages if p[0] & 2]
        out["nb_streams"] = len(bos) or 1
        out["audio_streams"] = sum(1 for p in bos if p[3][:8] == b"OpusHead" or p[3][:7] == b"\x01vorbis"
                                   or p[3][:5] == b"\x7fFLAC" or p[3][:5] == b"Speex") or 1
        last = max((p[1] for p in pages if p[2] == ser and p[1] >= 0), default=None)
        if codec == "vorbis":
            nom = struct.unpack_from("<i", first, 20)[0]
            if nom > 0:
                out["bit_rate"] = nom             # oggparsevorbis: bit_rate = bitrate_nominal
            if last is not None:
                out["nb_samples"] = last
        elif codec == "opus" and last is not None:
            # ffmpeg 7.0.2 -i on an Opus .ogg: Duration = last granule / 48000 (pre_skip NOT subtracted, start 0)
            out["nb_samples"] = last
            rate = 48000
        elif codec == "flac" and last is not None:
            out["nb_samples"] = last
    elif b[4:8] == b"ftyp":
        k = b.find(b"stsd")
        if k >= 0 and k + 20 <= len(b):        # first sample entry fourcc = codec_tag (mov.c: AV_RL32 of the type)
            out["codec_tag"] = struct.unpack_from("<I", b, k + 16)[0]
        out["nb_streams"] = b.count(b"trak") or 1
        out["audio_streams"] = b.count(b"hdlr\x00\x00\x00\x00\x00\x00\x00\x00soun") or 1
    elif codec in ("mp3", "mp2", "mp1") and b[:3] == b"ID3" and len(b) > 10:
        sz = b[6:10]
        tag = b[10:10 + ((sz[0] << 21) | (sz[1] << 14) | (sz[2] << 7) | sz[3])]
        out["nb_streams"] = 1 + (b"APIC" in tag or b"PIC\x00" in tag)   # cover art = attached_pic video stream
    elif b[:4] == b".snd" and len(b) >= 24:
        off, size, enc = struct.unpack_from(">III", b, 4)
        bits = _bits_per_sample(codec)
        if bits and rate and ch:
            out["bit_rate"] = rate * ch * bits
            if size != 0xFFFFFFFF:
                out["nb_samples"] = size * 8 // (bits * ch)
    if rate:
        out["rate"] = rate
    return out


def _fmt6(x):
    return "%.6f" % x   # ffprobe prints durations with "%f"


def stream_info(data, ctx):
    """media.<ffprobe stream/format key> beyond the basic five: primary_audio_bit_rate (WAV: fmt nAvgBytesPerSec*8;
    AIFF/AU PCM: rate*ch*bits; Vorbis: nominal), codec_long_name (libavcodec descriptor), codec_tag_hex/_string
    (WAV fmt tag / SubFormat; 0 = "[0][0][0][0]" for flac/ogg/mp3/aiff), duration_seconds / nb_samples /
    duration_ts (time_base 1/rate), format_long_name (demuxer long name), nb_streams, audio_stream_count,
    format_size_bytes, format_duration_seconds and format_bit_rate (libavformat update_stream_timings:
    trunc(size*8 / duration rounded to microseconds)). Values a header cannot give (MP3/MP4/MKV durations) -> None."""
    if not data:
        return None
    try:
        b = bytes(data)
        f = (ctx or {}).get("field") or ""
        if f in ("format_size_bytes", "format_size"):
            pr = _probe(b)
            return len(b) if pr else ("none" if _non_media(b) else None)
        if "long_name" in f and ("format" in f or "container" in f):
            n = format_name(b, ctx)
            return _FORMAT_LONG.get(n, n if n == "none" else None)
        pr = _probe(b)
        if pr is None:
            if "streams" in f or f.endswith("stream_count"):   # ffprobe opens a still image as one video stream
                from .media_video import _still
                try:
                    st = _still(b)
                except (ValueError, IndexError, struct.error, OverflowError):
                    st = None
                if st:
                    return 0 if ("audio" in f) else len(st)
            return "none" if _non_media(b) else None
        codec, tag = pr["codec"], pr["codec_tag"]
        if "long_name" in f:
            return _long_name(codec)
        if "codec_tag" in f:
            if f.endswith("_string"):
                return "".join(chr(c) if (c in b"._- /" or chr(c).isalnum()) and c < 128 else "[%d]" % c
                               for c in tag.to_bytes(4, "little"))
            return Hex(tag, 8 if f.endswith("_u32_hex") else 4)
        if f.startswith("audio_stream") or "audio_streams" in f or f == "number_of_audio_streams":
            return pr["audio_streams"]
        if "streams" in f or f == "stream_count":
            return pr["nb_streams"]
        n, rate = pr.get("nb_samples"), pr.get("rate")
        if "nb_samples" in f or "duration_ts" in f or "sample_count" in f:
            return n
        if "duration" in f:
            if n is None or not rate:
                return None
            if f.startswith(("format", "duration")):   # AVFormatContext.duration is in microseconds
                return _fmt6((n * 1000000 + rate // 2) // rate / 1e6)
            return _fmt6(n / rate)
        if f.startswith(("format", "overall", "container")):
            if n is None or not rate:
                return None
            us = (n * 1000000 + rate // 2) // rate
            return int(len(b) * 8.0 * 1000000 / us) if us > 0 else None
        if "bit" in f:
            return pr.get("bit_rate")
        return None
    except Exception:  # noqa: BLE001
        return None
