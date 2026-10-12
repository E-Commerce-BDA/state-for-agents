# sf-035 — Select data pattern (done 2026-10-11)

OptionsSource port + demo + useSelectOptions hook + §9 async/themed
demos. Third instance of the useSearch pattern (new lib/select domain).

## Order (one commit per file)
1. Tracking. 2. Port. 3. Demo. 4. Hook. 5. Hook test. 6. Showcase.
7. Matrix. 8. Gate + close.

## Verification

`tsc` clean; suite 254/254 (hook trio green); `next build` green.
§9 shows async (port status visible) + themed instant customs beside
untouched native demos. 5 code commits + 1 doc commit, local.

## Follow_ups

- CMS/service swaps demoOptions (one line).
- Per-option disabled states (still open from sf-033).
