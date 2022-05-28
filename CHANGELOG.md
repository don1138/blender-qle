**1.6.4** <!-- 22/05/27 -->
   + Bugfix: If you launch Blender and open a file with an existing **QLE** collection, deleting the collection sets the `World` to null, and causes an error when adding the collection again

**1.6.3** <!-- 22/05/24 -->
   + Change `Area_Fill` light shape to `DISK` and location Z to `8`
   + Change `Area_Left` and `Area_Right` light dimensions to `2` x `6`
   + Change `Backdrop` roughness to `1`

**1.6.2** <!-- 22/05/22 -->
   + Added new Light
   + Change `QLE World`, `Area_Fill`, and `Area_Back` blackbody from `5800` to `5454` (equal energy)
   + Change `QLE World` strength from `0` to `0.25`
   + Change `Backdrop` color to `#808080` (neutral gray)
   + Adjust light positions

**1.6.1** <!-- 21/12/29 -->
   + Bugfix Clear Collection

**1.6.0** <!-- 21/12/24 -->
   + Added new Light `Area_Back`
   + Set `Area_Left` blackbody to `3800` (orange tint)
   + Set `Area_Right` blackbody to `8800` (blue tint)
   + Adjust light positions
   + Added `Backdrop` object to scene
   + Bugfix error messages

**1.5.6** <!-- 21/07/23 -->
   + Assign custom `data.name` to Lights

**1.5.5** <!-- 21/07/18 -->
   + Fixed error if `scene.world.name` is not named "World"
   + Creates new World named "QLE World" and swaps it with existing World on Add/Delete

**1.5.4** <!-- 20/09/20 -->
   + Bugfix: When a QLE object is manually deleted and then re-added, it doesn't link back into QLE Collection
   + Bugfix: Reconnect Light to Target if disconnected
   + Add INFO Message for when Button click returns no result
   + Code cleanup: Replace all TRY/EXCEPT with IF/ELSE

**1.5.3** <!-- 20/09/12 -->
   + Clear Environment: Deselect All before deleting QLE, and Purge Scene after
   + Move Add Tracking and Add Blackbody Node into functions
   + Code cleanup

**1.5.2** <!-- 20/08/30 -->
   + Change category to ``Lighting``
   + Add Wiki URL
   + Rename script to ``quick_lighting_environment.py``.

**1.5.1** <!-- 20/08/22 -->
   + Set light Blackbody to ``5800``, more accurate Sun temperature.

**1.5** <!-- 20/07/19 -->
   + Set Lights Blackbody to ``6000``
   + Arrange Lights Nodes
   + Code cleanup.

**1.4** <!-- 20/06/29 -->
   + Error handling for clicking Add Environment multple times, or Clear Environment when there is no QLE in Scene
   + Removed **Clear All** button.

**1.3** <!-- 20/06/17 -->
   + Move Lights and Empty into new Collection
   + Refactor Clear Environment
   + Add "Clear All Lights & Empties" as temp fix for Error Handling

**1.2** <!-- 20/06/17 -->
   + Add Icons to Buttons
   + Refactor Register/Unregister

**1.1** <!-- 20/03/21 -->
   + Enable Nodes on all Lights
   + Add Blackbody Converter set to ``5000`` (daylight-ish) to Emission Shaders

**1.0** <!-- 20/02/24 -->
   + Create Add-on
