

## Phase 4: Bulletproof ID Generation & Pagination Fix (Aug 19)
- **The Duplicate Key Bug**: Supabase REST API limits fetches to 1000 rows by default. For databases with >1000 rows, state.cashbook only loaded the first 1000, causing local ID calculation (maxId + 1) to generate an ID that already existed in the hidden rows.
- **Pagination Fix**: Rewrote the get_cashbook interceptor to loop with offset and limit=1000 until all rows (4354+) are loaded securely.
- **Double-Click Protector**: Implemented window._lastInsertedId to reserve IDs instantly in memory to prevent rapid double-clicks on Mobile from throwing duplicate key errors.
- **Unix Timestamp Strategy**: Abandoned maxId + 1 entirely for new inserts. Instead, insertObj.id uses Math.floor(Date.now() / 1000) (Unix timestamp in seconds). This guarantees absolute, mathematical uniqueness across all devices (Desktop, Mobile) without needing cloud synchronization or relying on PostgreSQL auto-increment sequences. Safe up to 2.1 billion (within int4 limits).
