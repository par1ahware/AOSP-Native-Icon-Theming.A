# Supply your own artwork

This repo intentionally does **not** redistribute the original PAR1AH AetherDrift illustrations.

For the reference five-icon example, supply individually cropped, licensed PNGs using these names:

- `par1ah_aether_phone.png`
- `par1ah_aether_messages.png`
- `par1ah_aether_camera.png`
- `par1ah_aether_settings.png`
- `par1ah_aether_files.png`

Put files in this directory before running the optional helper. PNGs can be 1254×1254 RGBA, as in the tested Cuttlefish example; do not assume all asset packs need that exact resolution. Android's resources/build tools handle scaling and icon normalization. Check alpha and background corners, and visually verify the actual home screen.
