# QLE 2.0 — Package and UI Validation

**Historical evidence:** These results cover the candidate before the approved QLS UI / parenting revision. See `UI_REVISION.md`; the current ZIP has not been runtime-tested.

Date: 2026-10-18. Branch: `qle-2.0`. Candidate for user testing; not published.

## Package

- File: `dist/quick_lighting_environment-2.0.0.zip` (198,119 bytes).
- SHA-256: `168128dd8dbb5e5f8a22439ab89ad1f46c81fd123b59d4215385c095a403d4c0`.
- Built and validated with Blender 4.5.14's official extension CLI; ZIP also validated with 5.2.2's CLI. All commands exited zero.
- Exactly 16 files: 12 Python modules, two backdrop libraries, manifest, and GPL license. CRC and runtime-source byte comparisons pass. No tests, docs, caches, or QLS checkout dependency in the ZIP.
- `tools/build_extension.py` stages an explicit runtime allowlist and license in a temporary directory, then validates source, builds, validates ZIP, and checks inventory/source bytes. Blender runs offline with temporary preferences.

## Installation and persistence

`tests/test_installed.py` installed the actual ZIP into a temporary local extension repository under separate temporary profiles in Blender 4.5.14 and 5.2.2. Both processes exited zero with `QLE_INSTALLED_TESTS_OK`.

Checks include loading from the installed directory, registered panel/RNA, Add, all five backdrop options from packaged assets, Protect, save/reopen, disable/re-enable, protected Clear, previous World restoration, Add without duplicate originals, Unprotect, and Reset.

The test requires `QLE_QA_ROOT` under `/private/tmp/qle-*` and all three `BLENDER_USER_CONFIG`, `BLENDER_USER_SCRIPTS`, and `BLENDER_USER_EXTENSIONS` redirected beneath it before launching Blender. It must never use a normal user profile. In a foreground test launch it additionally prepares the disposable scene and opens the Sidebar.

## Default appearance comparison

`tests/test_default_render.py` renders identical scenes containing a diffuse brown sphere and a metallic brown sphere using the original `d9b8cad` QLE implementation and the new implementation. It compares scene-linear 128 × 96 EXR pixels within each version/engine, then removes the temporary renders.

| Blender | Engine | Mean absolute RGB difference | Peak difference |
| --- | --- | --- | --- |
| 4.5.14 | EEVEE | 0 | 0 |
| 4.5.14 | Cycles | 4.69e-9 | 1.07e-6 |
| 5.2.2 | EEVEE | 0 | 0 |
| 5.2.2 | Cycles | 3.93e-9 | 3.58e-7 |

Four comparisons / eight renders passed; both processes exited zero with `QLE_DEFAULT_RENDER_TESTS_OK count=2`. This verifies the representative default scene, not every possible subject or cross-engine equivalence. The earlier eight RGB/Kelvin comparisons and 220 functional checks are recorded in `CONTROLS_VALIDATION.md`.

## Actual desktop inspection

Temporary Blender windows with temporary profiles and disposable scenes were used. Both versions visibly draw the panel without Python drawing errors.

- **4.5.14:** light RGB/Kelvin controls and grouped temperature menu inspected. Selecting Daylight changed Left to 5600 K while Right remained 5454 K. Reset confirmation text and Cancel were checked; executing Reset restored defaults, and native Undo restored the previous Kelvin edits. Clear confirmation text was inspected.
- **5.2.2:** compact panel and Reset/Clear confirmation text inspected. Confirmed Clear removed QLE while retaining the factory subject/camera/light; native Undo restored QLE. Adjustments remained collapsed after hiding/reopening the Sidebar, saving, and reloading the disposable file.
- At narrow Sidebar widths Blender stacks enum buttons vertically; labels and values remain usable.
- Duplicate test launches occurred during window targeting, were cleaned up, and the user closed the remaining 4.5 windows. Later UI work used one uniquely identified 5.2 test process, which was closed after inspection.

This was a focused smoke test, not every visible control in both versions. **Not individually established:** Clear execution/Undo in the 4.5 desktop UI; Reset execution/Undo and temperature-menu selection in the 5.2 desktop UI; collapse persistence in 4.5. Their underlying actions have automated coverage, but those specific UI combinations should not be reported as manually passed.

## State

No runtime defects were uncovered by these checks; chunk 4 adds build/validation tools and evidence only. The ZIP is ready for the owner's hands-on review. No commit, tag, push, marketplace upload, or release was performed in this chunk.
