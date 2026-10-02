# SKILL-ADMIN — admin components + RBAC-gated routes

> Scope: `admin-app` — shell (320px sidebar + 64px topbar), editors with live preview, RBAC.
> Status: Active | Date: 2026-09-30 | Parent: `6.Admin-Panel.md §2–3`

## Rules

1. Every route in `§2.2` map requires its permission (`{resource}.{action}`); guard redirects to 403; admin primary buttons stay ink + white (never storefront ocean).
2. Editors use editor-with-live-preview (`?preview=1` renders real storefront component against unsaved state); ThreeState (Inherit/Override) per overridable setting; Reset deletes keys.
3. Shared primitives: Table (offset pagination), SortableList (drag → `sort_order`), MediaPickerModal (usage filter + S3 upload), TreeView (categories), Chart/Timeline (analytics).
4. Destructive actions confirm; 409s (dup SKU/slug) are blocking banners; autosave debounced 2s with saved indicator.

Use next: SKILL-DUMB, SKILL-CSS, SKILL-INTERFACES.
