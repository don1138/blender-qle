# QLE 2.0 — Foundation Checkpoint

Date: 2026-10-18. Repository: `blender-qle`. Branch: `qle-2.0`.

Historical evidence only: this checkpoint covers the chunk 2 candidate and predates the current packaged revision.

## Implemented in chunk 2

- Persistent scene-local identity and original-World storage; saved metadata identifies managed objects, roles, original light slots, and protected dependencies independently of display names.
- Adoption of recognizable legacy QLE graphs without resetting existing appearance or unrelated constraints. Unique legacy Light-data names can recover roles after Object renaming.
- Add restores missing default parts while preserving existing adjustments, added lights, and protected originals. An intentional None backdrop is retained.
- Reset rebuilds unprotected defaults using QLE's exact original light definitions, packaged C backdrop, and 5454 K / 0.25 World. Protected lights and private aiming targets remain.
- Clear removes only identified QLE content, restores the saved original World (including an originally absent World), and leaves unrelated objects and orphan data untouched. No broad orphan purge.
- Protect/Unprotect services and operators. Protected lights remain managed; collection moves preserve unrelated collection memberships. Protection detaches a light from a deletable QLE parent without changing its evaluated pose.
- Reset/Clear operators require confirmation when invoked interactively and declare Undo support. The existing Scene Properties panel remains until chunk 3; the new N-panel and full adjustment controls are not implemented yet.
- Source and manifest now identify version 2.0.0 with Blender 4.5 minimum. This is not a built or released package.

## Verification

`tests/test_foundation.py` runs 27 scenarios with EEVEE selected and again with Cycles selected in each installed Blender version:

| Blender | EEVEE | Cycles | Total |
| --- | --- | --- | --- |
| 4.5.14 | 27 passed | 27 passed | 54 passed |
| 5.2.2 | 27 passed | 27 passed | 54 passed |

Both processes exited zero and emitted `QLE_FOUNDATION_TESTS_OK count=54`. This verifies lifecycle/data behavior under both engine selections; it does not claim rendered appearance, visual UI, interactive confirmation, or Undo testing.

Coverage includes exact original light positions/colors/powers, idempotent Add, missing-part repair, renamed/protected originals without duplication, added protected lights, Reset/Clear, unrelated name collisions, unowned objects inside QLE, missing/wrong-type assets failing before destructive changes, independent scenes, rejection of shared scene content, exact protected pose, original World missing/None, save/reopen persistence, and unregister/re-register persistence.

Reproduce from the repository root, substituting the approved Blender executable:

```sh
PYTHONDONTWRITEBYTECODE=1 /Applications/Blender-4.5.14.app/Contents/MacOS/Blender --background --factory-startup --disable-autoexec --python-exit-code 1 --python tests/test_foundation.py
```

The suite uses disposable factory scenes and temporary `.blend` files. Its legacy fixture is read from baseline commit `d9b8cad`. Tests require both zero process exit and the success marker; neither alone is sufficient.

Additional checks: Python syntax, matching version/minimum manifest values, exact extracted legacy light defaults, and `git diff --check`. QLS remained unchanged.

## Known limits and next checkpoint

- Legacy QLE stored the previous World only in process memory. When that history is absent, the new code reports it and creates a fallback World on Clear; it does not guess an original World from a name.
- If both a legacy light's Object name and Light-data name were changed, its original role may be unknowable. A recognizably tracked light is preserved as an extra; Add restores the missing identifiable default slot rather than guessing which user light to replace.
- Objects/collections shared between scenes and linked library objects are rejected for editing rather than silently changing another scene. Independent scene setups are supported and tested.
- Only the legacy C backdrop is wired in this foundation. Other backdrop assets, target-follow/position controls, RGB/Kelvin switching, Add/Delete/Reset Light UI, and viewport/orbit synchronization belong to chunk 3.
- Packaged installation, render comparisons, visual UI, confirmations, and interactive Undo verification remain for the later validation checkpoint.
- The sandboxed Blender processes crashed in Metal initialization before Python ran. The separately approved background test mission succeeded outside the sandbox. Existing Blender windows and user project files were not controlled.
- No implementation commit, build, package, push, or release was made as part of chunk 2.
