# Asset kit layout

Lincoln builds one batch card into one directory. One command regenerates the kit. A hand edit that is not in the script is not in the kit.

```
<output>/
  <assets written by the script>
  make_<kit>.sh          mesh and texture kit
  make_<kit>.py          audio kit
  verify.json            re-import data: objects, parent, triangles, pivots, sizes, textures
  verify_kit.py          exits non-zero on a miss
  README.md
  previews/
    contact sheet
    320×240 layout shot
```

Read `common.md` first. Build P0 rows first. Do not rebuild a shared prop named on the card. The finished contact sheet is the bar the next card names.

A new export or render setting gets a tiny headless test before it stays.
