# Schema Review

### Works well

**Works well:** There is no queue table and no stored position, wait time or total. A customer joining or leaving never forces other rows to be rewritten, and the end-of-day metrics (MQ-11) always match the tickets.


**Works well:** Deleting a user or a service is blocked while tickets point to them, so the history behind MQ-11 cannot be lost by accident. 


**Works well:** MQ-08 says a clerk marks a called ticket as served, completed or skipped, and MQ-11 reports "total skipped". The `skipped` status uses the same word in both, so the total is a simple count of `tickets.status = 'skipped'`.


### Problems and Changes

**Problem:** `Skipped` and `no_show` is redundant.
**Changes:** Instead of `no_show`, I used the word `skipped`.


**Problem:** No requirement in the table uses `avg_minutes` (nothing asks for an estimated wait).
**Change:** Removed `avg_minutes` and its CHECK from `services` in `schema.md` and `schema.dbml`. `services` is now `id, name`. If a requirement for estimated wait time is added later, the column can come back then.


**Problem:** Tapping the join button twice could create two waiting tickets for the same user and service. Nothing stopped it. 
**Change:** Added a partial unique index, `UNIQUE (user_id, service_id) WHERE status = 'waiting'`, to `schema.md` and as a comment in `schema.dbml` (DBML cannot write the WHERE part). A user can still join the same service again after the earlier ticket is no longer waiting. This only works if each customer has one `users` row. If customers stay anonymous, the rule needs a different key.


**Problem:** A ticket could be `called`, `served`, `completed` or `skipped` with an empty `called_at`, which would break the wait-time calculation. 
**Change:** Added `CHECK (status NOT IN ('called', 'served', 'completed', 'skipped') OR called_at IS NOT NULL)` to `tickets` in both files. A `left` ticket can still have no `called_at`, because a customer can leave before being called (MQ-06).


**Problem:** A ticket could have a verifier but no time, or a time but no verifier. 
**Change:** Added `CHECK ((verified_by IS NULL) = (verified_at IS NULL))` to `tickets` in both files.