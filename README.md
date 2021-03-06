# OmbroBox
A simple physics sandbox.

<div>
  <img src="https://github.com/SudoOmbro/OmbroBox/blob/main/screenshots/img1.png" style=" width:200px ; height:200px"  >
  <img src="https://github.com/SudoOmbro/OmbroBox/blob/main/screenshots/img2.png" style=" width:200px ; height:200px"  >
  <img src="https://github.com/SudoOmbro/OmbroBox/blob/main/screenshots/img3.png" style=" width:200px ; height:200px"  >
  <img src="https://github.com/SudoOmbro/OmbroBox/blob/main/screenshots/img4.png" style=" width:200px ; height:200px"  >
</div>

## Features

- ECS-like architecture achieved through multiple inheritace
- Sand, Water & Gas Physics
- Buoyancy
- Heath transfer
- Status changes (ice -> water -> vapor)
- Scriptable custom tile behaviours

## controls
- Click with the `Left mouse button` to add the selected Tile
- Click with the `Right mouse button` to delete the tile you are hovering on
- Use the `Mouse wheel` to select different tiles
- Press `Space` to Pause/Unpause the simulation
- Press `F1` to enable additional information
- Press `ESC` to reset the world
- Press `Left CTRL` while adding or deleting tiles to enable big brush mode

## Performance
For being pure python it's as good as it gets (without using multiprocessing or Cython), i would suggest using PyPy.
