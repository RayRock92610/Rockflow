## 2026-10-09 - Key Sorting Fast-Path in Canonicalizer
**Learning:** Calling Array.prototype.sort on single-key or empty objects introduces avoidable sorting overhead in hot hashing paths.
**Action:** Fast-path `keys.length <= 1` before invoking `.sort()` in canonicalization helpers.
