# BOM Voyage solver
Concept: `text.<field>` encoding facts about an archive member, read from the raw bytes (not decoded text, not the file name).
- `utf8_bom_present`: whether the member starts with EF BB BF -> "true"/"false" (lib.knowledge.BOOL).
- Also handles utf16le/utf16be/utf32le/utf32be `_bom_present` and a generic `bom_present`; other text.* fields get skipped and logged.
Variant axes covered: member/zip names, Mastery sets (one zip per set), misleading names like `*-with-bom.txt` (bytes win, not the name).
Field comes from `text.<field>` in the question, or from the answer-id suffix after `-text-` if the question doesn't name it.
Cases: single_solve (GM-confirmed), synthetic-mastery (one BOM member, one non-BOM member).
