# QLE 2.0 — QLS UI Revision

Approved 2026-10-18. Implemented in `qle-2.0`; runtime testing delegated to the owner.

- Preserve Add / Reset / Clear at 1.5× height. Use QLS's 1.25× action/menu sizing, 40% label columns, and section spacing.
- Show Lights, Target, Stage, and World directly without an Adjustments wrapper. Separate major sections visually and show a Ghost empty state when no environment or protected lights exist.
- Box each light with its editable name, Select, Protect, and Enabled controls. Remember light/Position/Aim/Shape disclosures as saved Object properties. Ordinary disclosure rows allow the complete light card to sit inside a box without nesting Blender's native layout panels inside boxes.
- Lay out Target Follow (Free / Object), Light Aim (Target / Manual), and Light/World RGB / Kelvin horizontally.
- Use Stage in user-facing controls and messages. Retain internal backdrop IDs and library object names for existing scenes/assets.
- Stage has Position and Surface groups. Surface offers 22 Studio Colors with grouped swatches and active-color indication, plus Custom. Finish buttons are stacked: Reflective, Satin, Matte; Roughness follows.
- Default Stage materials use one positioned Principled surface, and the QLE World uses one positioned QLE Temperature node. The light orbit control is named Around Target.
- Follow Target now parents the light directly to its shared/private target with Keep Transform. Turning it off unparents with Keep Transform. Track To still controls aim independently. Targets have rotation and scale locked in Blender's transform tools because their intended control is translation; this is ordinary parenting, so changing a target's rotation/scale through other means inherits those changes.
- Enabling the extension or loading a saved development scene converts old per-light Follow helpers into parenting while retaining evaluated world transforms. Protected lights still use private targets so Reset/Clear can preserve them.

No Blender process, automated suite, render, or desktop validation was run for this revision. Python syntax was inspected and the ZIP rebuilt directly from source with `python3 tools/build_extension.py --source-only`. Earlier validation reports describe the previous candidate and do not establish that this revision passes.

Artifact: `dist/quick_lighting_environment-2.0.11.zip`. The current ZIP hash and file count are recorded in the build output; earlier candidates have been superseded.
