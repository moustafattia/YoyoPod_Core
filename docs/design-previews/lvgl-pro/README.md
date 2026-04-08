# LVGL Pro Viewer Mockups

This folder is a small LVGL Pro project you can open directly in the editor or in the online viewer.

- `project.xml` defines two targets:
  - `whisplay_portrait` for `screens/hub.xml`
  - `standard_landscape` for `screens/main_menu.xml`
- `globals.xml` carries the shared YoyoPod palette pulled from `yoyopy/ui/screens/theme.py`.
- `translations.xml` is intentionally minimal so the editor/codegen pipeline has a valid translations file to load.
- The screen XML files are currently smoke-test baselines:
  - `hub.xml` is one centered button
  - `main_menu.xml` is a small vertical list of buttons

Once those render reliably in LVGL Pro, add layout, colors, and card styling back one step at a time.

If you want to iterate fast, start by changing colors, radii, positions, and copy inside the two screen files.
