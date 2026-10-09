# binary-swift-justice solver notes

VARIANT AXIS: Mastery set count (2 on auto-mastery-d1a6613c, up to 5 x 31 MB on D8) -- main() now groups (answer_id, question) pairs with lib.common.group_by_set and solves each set in a fork ProcessPoolExecutor (sequential fallback on pool error, HCTF_SOLVER_PARALLEL=0 disables); each set's delivery is still paired by contract sha256 via container_by_sha. Output identical to the sequential loop on all 9 cases.

## Proposed lib additions
- (none)
