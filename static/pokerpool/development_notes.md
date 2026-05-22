# Poker Pool — Development Notes

Timestamped log of key decisions, lessons learned, and bugs encountered during development.

---

## 2026-05-20 — Session 1: Milestone 1 Build

### Decision: Single-file architecture for M1
**Time:** 2026-05-20 ~start of session
**Context:** Spec recommends a multi-file TS directory structure (§23.2). For M1 prototype, we're building as a single HTML file with embedded JS to keep iteration fast and avoid build tooling overhead. The architecture will still separate concerns logically (rules engine, physics, UI) within the file.
**Rationale:** Faster to iterate, easier to test in browser, can refactor to multi-file in M2. The spec's separation-of-concerns principle is honored through code organization within the file.

### Decision: Matter.js via Phaser 3's built-in integration
**Time:** 2026-05-20
**Context:** Phaser 3 has built-in Matter.js support. Using `Phaser.Physics.Matter` rather than standalone Matter.js.
**Rationale:** Less boilerplate, Phaser handles the render-physics sync automatically.

### Decision: Programmatic visuals only for M1
**Time:** 2026-05-20
**Context:** Spec mentions Kenney assets (§22). For M1, using simple circles for balls with number labels, rectangles for table, colored circles for pockets.
**Rationale:** No asset loading complexity. Focus on rules and feel. Assets come in M2.

