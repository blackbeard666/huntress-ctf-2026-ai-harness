
## Proposed lib additions
- lib/meta: `relation.identical_sha256_groups` (D30, GM-CONFIRMED) = cluster zip members (minus delivery-manifest.json) grouped by sha256 of REAL bytes, groups len>=2, each = sorted manifest artifact `id` (e.g. "alpha-01", no ext/path), groups sorted -> compact JSON. Paths `artifacts/x.txt` and basenames `x.txt` REJECTED.
