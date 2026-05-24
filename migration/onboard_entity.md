# Onboard a new entity package under `src/Entity/`

When IT adds `src/Entity/{EntityPackage}/` with `objects/` and `layouts/`:

1. **Constitution gate** — Decide `targetTable` (standard vs custom) and document in registry `constitutionNotes`.
2. **Registry** — Add row to `migration/entity-registry.json` (`status`: `pilot` or `active`).
3. **Field maps** — Add `STANDARD_FIELD_MAP` / `CUSTOM_FIELD_MAP` (or new config module) in `migration/lib/`; extend `parse_entity.py`.
4. **Parse** — `python migration/migrate_entity.py --entity {EntityPackage} --steps parse`
5. **Data model** — Add section to `specs/001-migrate-salesforce-customizations/data-model.md`.
6. **Apply** — Confirm environment (`pac org who`), then:
   ```powershell
   python migration/migrate_entity.py --entity {EntityPackage} --steps metadata,form
   ```
7. **Validate** — `python migration/migrate_entity.py --entity {EntityPackage} --steps validate`
8. **ALM** — `pac solution export` / `unpack` → commit `solutions/AccountMigration/`

Do not copy `apply_account_*.py`; use shared `migration/lib/` only.
