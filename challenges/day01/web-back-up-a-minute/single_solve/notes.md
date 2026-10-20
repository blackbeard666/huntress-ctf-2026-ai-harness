robots.txt Disallow /snapshots-<hex>/ -> dir index -> environment-copy-<hex>.json.bak support_note=proof_<hex32> | CORRECT
solver: live crawl (target url from contract/status.json `targets`), robots->index->backup links, regex proof_...; --from-solver refused (no artifacts dir for a target-only mode) -> submitted value directly
