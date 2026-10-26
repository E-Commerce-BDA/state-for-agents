# SKILL-NEST-CLI — code generation via Nest CLI

> Scope: scaffolding modules, controllers, services, guards, and filters using `nest` CLI.
> Status: Active | Date: 2026-10-26 | Parent: `Documentation/2.Tech-Stack.md §5`, `services/SKILL-NESTJS.md`

## Rules

1. **CLI-first for structure:** Use `nest g <schematic> <name> [options]` to scaffold modules, controllers, services, and guards. Never hand-roll boilerplate class definitions that the CLI can generate accurately in seconds.
2. **Module-first generation:** Always generate the module first (`nest g mo <name>`), then generate components into it (`nest g co <name>`, `nest g s <name>`). The CLI automatically registers controllers and providers into the target domain module instead of polluting `app.module.ts`.
3. **ESM / NodeNext import discipline:** Nest CLI generates bare relative imports (e.g., `'./cart.service'`). Because our services use `"moduleResolution": "nodenext"`, check and append `.js` extension to relative imports (e.g., `'./cart.service.js'`) so `tsc` and `vitest` resolve cleanly without runtime errors.
4. **Test file control:** Use `--no-spec` when writing dedicated Vitest suites, or immediately convert the generated `.spec.ts` from Jest conventions to `vitest` globals (`describe`, `it`, `expect`, `vi`).
5. **No flat clutter:** Never use `--flat` unless creating a root-level utility. Keep domain artifacts co-located in their domain directory (e.g. `src/cart/`).
6. **Dry-run validation:** When uncertain about the destination path or module registration, use `--dry-run` to preview file paths and module updates before touching the disk.

## Good vs bad

```bash
# GOOD — module-first, co-located service & controller, automatic module wiring
pnpm nest g mo cart
pnpm nest g co cart --no-spec
pnpm nest g s cart --no-spec
# Result: src/cart/cart.module.ts (registered in app.module.ts),
#         src/cart/cart.controller.ts (registered in cart.module.ts),
#         src/cart/cart.service.ts (registered in cart.module.ts)

# BAD — hand-rolling files, missing module imports, or dumping flat files in src/
pnpm nest g co cart --flat       # pollutes src/ with loose files outside domain folder
# Hand-writing cart.module.ts and forgetting to register it in app.module.ts
```

> Note: Nest CLI is available locally in each service repo (`pnpm nest`). Always run commands from the service root (e.g. `e:/E-Commerce/cart-svc`).

Use next: SKILL-NESTJS (controller/service patterns), SKILL-POSTGRES (raw SQL queries), SKILL-INTERFACES (DTO & types).
