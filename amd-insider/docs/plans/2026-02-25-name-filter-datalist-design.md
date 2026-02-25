# Name Filter Datalist Design

## Goal
Add dropdown suggestions for the name filter while keeping substring (`key in`) matching behavior.

## Scope
- UI: convert existing name input to use native `datalist` suggestions.
- Data source: suggestions come from current `yearRows` (current selected year, or all when year=all).
- Matching logic: keep existing `includes` behavior in `applyFilters`.

## Non-Goals
- No custom autocomplete component.
- No API/schema changes.
- No changes to chart filtering behavior.

## UX Behavior
- User can type freely or select from dropdown suggestions.
- Filter remains case-insensitive contains match (`insider_name.toLowerCase().includes(input)`).
- Suggestions refresh whenever year data is loaded.

## Technical Notes
- Keep `id="nameFilter"` unchanged to preserve event wiring.
- Add `<datalist id="nameOptions"></datalist>` and bind via `list="nameOptions"` on the input.
- Add `updateNameFilterOptions()` helper to build unique sorted names from `yearRows`.
- Call helper inside `loadYear()` after `yearRows` assignment and before/around table render.
