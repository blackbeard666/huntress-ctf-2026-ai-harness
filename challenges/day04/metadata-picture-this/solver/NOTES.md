# Picture This (day 4, metadata-forensics)
Concept: `jpeg.<field>` of a named JPEG inside the evidence zip. The true pixel size is the SOFn frame header
(FFC0..FFCF minus C4/C8/CC: P, Y=height, X=width); names/EXIF can lie ("presentation vs structure").
Confirmed: `jpeg.sof_dimensions_pixels` = `<width>x<height>` (single solve: camera-001.jpg -> 257x146).

Variant axes handled: member/zip names (set1/set2 zips), question order, baseline vs progressive SOF (synthetic case),
APP1 Exif present or not, junk/fill bytes between segments. Segment walk follows lengths, no fixed offsets.
Best-effort (unconfirmed spellings) extras: sof_width/height/components/precision, exif_orientation,
exif_dimensions_pixels, display_dimensions_pixels (swapped for orientation 5-8), orientation mismatch boolean.
