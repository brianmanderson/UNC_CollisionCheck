# UNC_CollisionCheck

RayStation (IronPython) scripts that flag potential gantry/patient collisions in a
radiotherapy plan by modeling the treatment machine geometry as ROIs and testing them
against the patient's external contour. Written for UNC (RayStation 8.0.1.10).

## How it works

The machine head is approximated as cylinders placed at the beam isocenter and rotated
by the couch angle via a 3D transformation matrix:

- `GantryHead` cylinder, radius 42 cm
- `kVPanel` cylinder, radius 51 cm

`DosCheckRun.py` iterates over the current beam set, and for each unique
(couch angle, isocenter) pair intersects the machine ROI with the (margin-expanded)
external contour. A non-empty intersection is contoured as
`Potential_Collision_<beam>` and printed as a warning; empty results are cleaned up.
Only the gantry head is tested per position, on the assumption that if the gantry
clears, the wider kV panel geometry is handled by the same logic.

- `DosCheckRun.py` — batch check over all beams in the current beam set; run `main()`.
- `CollisionChecker.py` — earlier WPF/XAML GUI variant that prompts the user to pick a
  POI and couch angle, then builds the cylinders. Loads its GUI (`poi_gui.xaml`) from a
  hardcoded UNC network path (`\\vscifs1\PhysicsQAdata\BMA\CollisionChecker`).

## Requirements

- RayStation with the `connect` scripting API (IronPython); `CollisionChecker.py` also
  uses `wpf`/.NET (`System.Windows`).
- Runs inside RayStation against the current Case, Examination, and BeamSet.

Note: paths and machine dimensions are site-specific to UNC and hardcoded; adapt before
use elsewhere. Not actively maintained.
