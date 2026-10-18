# QLE 2.0 — Agreed Scope and Panel

Recorded: 2026-10-18. Status: implementation and packaged checks complete; focused desktop smoke tests performed. QLS-style UI and direct-parenting revision subsequently implemented; see `UI_REVISION.md`. Owner performs runtime testing for that revision. See `FOUNDATION_VALIDATION.md`, `CONTROLS_VALIDATION.md`, and `RELEASE_VALIDATION.md` for evidence and specific UI coverage limits.

## Repository and approval boundaries

- Work in `/Users/don/Developer/blender-qle`, branch `qle-2.0`.
- Starting commit: `d9b8cad` (`Rename quick_camera_overlays.py`).
- `master` remains at the existing version during development.
- Reuse suitable code and assets from `/Users/don/Developer/blender-qls`; do not modify that repository for this work.
- Approval for chunk 1 covers creating this branch and recording this plan only.
- Obtain `Approved` before each subsequent implementation chunk and its checks. Desktop application control requires separate, mission-specific permission under the user's instructions.
- No commit, tag, push, release, or publication is part of chunk 1.
- Use Conventional Commit prefixes without scopes when commits are authorized.

## Product boundary

This is Quick Lighting Environment 2.0, in the existing QLE repository. Replace the legacy Properties > Scene panel with a 3D Viewport sidebar panel under Quick Tools. Keep QLE's familiar starting result while exposing useful adjustments.

- Minimum Blender version: 4.5.
- Support EEVEE and Cycles without changing the user's render engine.
- Preserve QLE's original four-light settings, positions, RGB colors, target, C backdrop, and World defaults. QLS's QLE Classic is not an exact substitute.
- Control existing legacy QLE setups where safely identifiable, preserving their appearance and adjustments.
- Include Add/Delete Light, Protect, individual Reset Light, orbit positioning, manual positioning synchronization, Target/Manual aiming, object-following target, backdrop choices, and RGB/Kelvin modes for Lights and World.
- No Simple/Advanced switch: one remembered, initially closed Adjustments section provides the compact view.
- Exclude camera management, reflectors, environment dome, whole-rig transforms/power scaling, light-type switching, full rig/fixture preset libraries, and tabletop backdrop. Exposure and Normalize are not panel controls in this scope.
- No planned feature ladder or further scope expansion; validate this focused release before considering later additions.

## Panel wireframe

`>` denotes a section closed by default; `v` denotes open by default. Contents under closed sections are shown here for completeness.

```text
Quick Tools
└── Quick Lighting Environment
    │
    ├── [ Add ] [ Reset ] [ Clear ]
    │
    └── > Adjustments
        │
        ├── v Lights
        │   ├── [ Add Light ]
        │   │
        │   ├── > Area_Left     [Select] [Protect] [Enabled]
        │   │   ├── Power      [100 W]
        │   │   ├── Color Mode [RGB] [Kelvin]
        │   │   │   ├── RGB: Color [color picker]
        │   │   │   └── Kelvin:
        │   │   │       ├── Temperature [preset menu]
        │   │   │       └── Kelvin [value K]
        │   │   ├── > Position
        │   │   │   ├── Follow Target [checked]
        │   │   │   ├── Around Subject [angle]
        │   │   │   ├── Elevation [angle]
        │   │   │   └── Distance [value m]
        │   │   ├── > Aim
        │   │   │   ├── Mode [Target] [Manual]
        │   │   │   └── Manual: Rotation X / Y / Z
        │   │   ├── > Shape
        │   │   │   ├── Shape [Rectangle / Square / Disk / Ellipse]
        │   │   │   ├── Size X [value m]
        │   │   │   └── Size Y [value m]
        │   │   └── [Reset Light] [Delete Light]
        │   ├── > Area_Right    [same header and light controls]
        │   ├── > Area_Fill     [same header and light controls]
        │   ├── > Area_Back     [same header and light controls]
        │   └── > Added Light…  [same header and light controls]
        │
        ├── > Target                              [Select]
        │   ├── Follow [Free] [Object]
        │   ├── Object mode: [object picker]
        │   └── Position X / Y / Z
        │
        ├── > Backdrop                  [Select] [Enabled]
        │   ├── Type [C Backdrop / L Backdrop / Flat Background / Floor / None]
        │   ├── Color [color picker]
        │   ├── Finish [Reflective] [Satin] [Matte]
        │   ├── Roughness [value]
        │   └── > Position
        │       └── Position X / Y / Z
        │
        └── > World
            ├── Strength [0.25]
            ├── Color Mode [RGB] [Kelvin]
            ├── RGB: Color [color picker]
            └── Kelvin:
                ├── Temperature [preset menu]
                └── Kelvin [5454 K]
```

Only show the active color mode's fields. Square/Disk expose one Size; Rectangle/Ellipse expose two. Show protected lights in the same editable list, with a closed padlock. Preserve user-renamed light names through management actions that retain the light.

## Environment actions

| Action | Behavior |
| --- | --- |
| Add | Create QLE if absent. Otherwise restore missing default lights and the required backdrop for the current selection, preserving existing adjustments, added lights, and an intentional None backdrop. A protected original light satisfies its original role and must not be duplicated. |
| Reset | Restore the original unprotected lights, shared target, C backdrop, and QLE World defaults. Recreate missing originals and remove added unprotected lights. Protected lights retain their settings, positions, and required aiming dependencies. |
| Clear | Remove unprotected QLE content and restore the previous World. Protected lights and their required dependencies remain editable. |

- Reset and Clear require confirmation explaining their effects and protected-light preservation.
- No separate Repair, Reset Lights, or Reset Rig button.
- Reset target defaults: position `(0, 0, 1)`, Follow Free.
- Repeated Add preserves the original-World reference. Reset preserves it too; Clear restores it.
- World state is persistent and isolated per scene. Do not copy QLE's transient global name-based restoration or broad orphan purge.
- Clear resets the retained backdrop selection to C so Clear followed by Add starts fresh. Add inside an existing environment preserves its selected backdrop, including None.

## Light behavior

- Add Light creates an Area Rectangle, 1 × 1 m, 100 W, white RGB, aimed at the shared target, with Follow Target enabled.
- Starting placement: 3 m from the target, centered horizontally on the front (-Y side), 45 degrees above it.
- Original lights retain the exact source `LIGHT_SETTINGS` values, not Kelvin approximations or QLS replacements.
- Enabled controls viewport and render visibility together.
- Reset Light restores settings, position, aim, enabled state, and Follow Target to that light's defaults. Preserve name and protection. Original lights use original QLE defaults; added lights use Add Light defaults. Do not move the shared target.
- Delete Light removes only that light and its exclusively required helpers. Shared targets and other lights remain. Later Add restores a deleted original, but not a deleted added light.

### Position and aim

- Around Subject, Elevation, and Distance describe position relative to the lighting target. Orbit is movement around the target, not rotation of the lamp itself.
- Follow Target defaults On: target translation carries the light while preserving relative placement.
- Follow Target Off: target movement leaves the light's world position unchanged; the relative position fields reflect the new relationship.
- Changing Follow Target must preserve the current light position.
- Target Aim points at the target independently of Follow Target. Manual Aim permits direct rotation XYZ.
- Users can grab and move lights in the viewport and enter exact coordinates using Blender's normal transform tools. Do not expose QLS helpers as the user's positioning workflow.
- Manual movement must update the position fields; subsequent field edits continue from that position without snapping elsewhere. QLS's helper hierarchy must be adapted to meet this requirement.

### Protection and identity

- Protect moves the light and required helpers to `QLE Protected`, preserving appearance and position. It remains QLE-managed and editable, rather than being released from the add-on.
- Protected lights survive both Clear and Reset. Unprotect returns the light to ordinary QLE content, making it subject to those actions again.
- Preserve any private target/dependency required to keep protected lights valid and unaffected by resetting or removing shared content.
- Stable saved identity and original-light role must be independent of display names. A protected original continues filling its original role across Clear/Add, even after renaming. A protected added light remains an extra.
- If an unrelated object uses a desired name, allow Blender's suffixing. Do not adopt, overwrite, or delete unrelated data merely because names match.

## Target behavior

- Free stays at its chosen position. Object follows the selected object's translation without inheriting rotation or scale.
- Selecting a follow object automatically snaps the target to that object's origin. Selecting a different object snaps to the new object's origin.
- After snapping, Position remains editable for an offset, such as moving the aim point from feet to chest.
- Switching to Free preserves world position. Deleting the followed object falls back to Free at the last position.
- Target movement carries lights with Follow Target enabled. Lights with that option disabled stay in place, though Target Aim still updates their direction.

## Color behavior: Lights and World

- RGB and Kelvin are exclusive modes with separately remembered values.
- RGB uses its saved color without temperature multiplication.
- Kelvin uses the selected temperature with a white RGB multiplier. No Tint field; a saved blue RGB color must not contaminate Kelvin.
- Switching back to RGB restores the previous RGB color. Switching back to Kelvin restores the previous Kelvin setting.
- Reuse QLS's 19 temperature presets, grouping, values, labels, and descriptions. (The earlier conversational count of 20 was incorrect; verified during chunk 3.)
- Original lights default to their exact legacy RGB colors. Their preloaded Kelvin values are Area Right `20000 K`, Area Left `3800 K`, Fill `5454 K`, and Back `5454 K`; switching modes does not alter the saved RGB colors. New lights default to white RGB with `6500 K` preloaded.
- World defaults to Kelvin 5454 K at Strength 0.25, matching legacy QLE.
- Verify actual EEVEE and Cycles results; API availability alone is not evidence of correct rendering.

## Backdrop behavior

- Types: C Backdrop (legacy default), L Backdrop, Flat Background, Floor, None. Reuse suitable QLS assets; omit Tabletop.
- Selecting a type replaces geometry while preserving Color, Roughness, and Enabled state.
- None removes backdrop geometry and disables geometry-dependent controls. Selecting another type restores geometry with the retained surface settings.
- Preserve original QLE geometry, material appearance, placement, and visibility as the factory backdrop defaults. Verify the legacy material before implementing reset; do not silently replace it with QLS's gray/matte default.
- Finish shortcuts use QLS values: Reflective 0.10, Satin 0.35, Matte 0.70; Roughness remains editable.
- The verified legacy material uses Diffuse at Roughness 1.0. Preserve it until an explicit Finish/Roughness edit switches the surface to Principled; Reset restores the legacy material.
- Position and Select permit native viewport placement. Enabled affects viewport and render visibility.

## Approved work sequence

1. **Branch and plan:** create `qle-2.0` and record this agreement. Current approval is limited to this chunk.
2. **Foundation:** safe ownership, legacy adoption, Add/Reset/Clear, protection, and appropriate verification. Obtain approval first.
3. **Controls:** implement the panel, position/aim synchronization, target following, backdrop choices, and Light/World color modes. Obtain approval first.
4. **Validation and packaging:** verify the packaged extension at the Blender 4.5 baseline and supported newer target(s), in EEVEE and Cycles. Cover save/reopen, manual transforms, old scenes, protected dependencies, identity, and World restoration. Obtain approval first, including separate permission for any desktop-control mission.

Report completed work and verification at each checkpoint. Stop for the next chunk's approval. No additional product decisions are outstanding; raise only concrete conflicts uncovered during implementation.
