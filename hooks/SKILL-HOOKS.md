# SKILL-HOOKS — source-injected hooks (ports and adapters)

> Scope: every stateful hook in `app/hooks/` + `components/shell/`.
> Status: Active | Date: 2026-10-02 | Parent: `SKILL-DUMB` (dumb leaves) + `SKILL-INTERFACES` (port shapes)

## Rules

1. **Hooks take sources, never URLs.** `useCartDrawer(source: CartSource)`, `useSearchOverlay(source: SearchSource)`, `useSession(source: SessionSource)` — interaction state lives in the hook, data comes from the injected port. A hook that fetches directly fails review.
2. **Demo sources beside hooks, clearly named** (`demoCartSource.ts`): in-memory, same DTO shapes as `4.API-Design`; swapped at the call site (one line) when the service lands. Throwaway-by-replacement, never by rewrite.
3. **Contract tests prove the swap early:** same behavior under demo vs stub-service sources — verified before the backend exists.
4. **Homes:** shared islands in `app/hooks/` (AGENTS.md constitution); shell-local hooks beside `components/shell/`; `lib/` stays pure (no hooks — state violates purity). Pure presentation maps (`tagTone`-style value→tone tables) live in `lib/<domain>/`, never in components — one home, every variant reads it.
5. **Kill criteria:** direct fetch in a hook · URL string in a hook · demo state that can't be replaced without touching components (means the port leaked).

```ts
// GOOD — port in, behavior out
function useCartDrawer(source: CartSource) {
  const [open, setOpen] = useState(false); // interaction state: hook's job
  const lines = source.lines();            // data: source's job
  return { open, setOpen, lines, setQty: source.setQty };
}
// BAD — service hard-wired, untestable without backend
function useCartDrawer() {
  const [lines, setLines] = useState([]);
  useEffect(() => { fetch('/api/cart').then(r => r.json()).then(setLines); }, []);
}
```

Use next: SKILL-INTERFACES, SKILL-DUMB.
