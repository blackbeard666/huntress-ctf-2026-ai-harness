# Two of a Kind (warmups day 04) solver notes

Concept: blob decodes (possibly via numbered per-line mixed encodings) to a message whose final line names a slug.

Variant axes handled:
- Single Solve / Time Trial: whole blob as space-separated binary.
- Mastery (18 sets, `blob-NN.txt`): numbered lines `NN<TAB>payload`, each fragment a different encoding
  (base64 / rot13 / hex / **space-separated 8-bit binary**), concatenated verbatim (split mid-word).
  `strict_line` decodes binary first (8-bit groups are also valid hex). 
- Pitfall fixed (auto-mastery-6c13182c set2/set16): the decoded slug line "er: jaunty-rainbow-clover-29" was
  rot-shifted to "an: fwqjpu-..." because "an" is a common word. rot-N now must beat the unshifted text by
  >= 2.0 English score (real words), in both `strict_line` and `best_line`.
