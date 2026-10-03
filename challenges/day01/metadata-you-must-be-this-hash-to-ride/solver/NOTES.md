Concept: identity inventory of a member inside a zip (filename, size, MD5, SHA-1, SHA-256).
Variant axes handled: zip name (falls back to the only zip present), member name/subject (roster, renamed copy, ...),
member in subdirectories (basename used), nested zips, question order/subsets, Mastery setN.* prefixes.
Member resolution: exact label from "zip -> member" artifact field, else fuzzy token match of subject vs basenames.
Cases: single_solve (GM-confirmed), synthetic-mastery (hand-made multi-member zips for set1/set2).
