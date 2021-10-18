# ToF ON

Blender Time-of-Flight Add-on

Much inspired by [How to calculate for every ray the total distance it has traveled from camera to emitter](https://blender.stackexchange.com/questions/81485/how-to-calculate-for-every-ray-the-total-distance-it-has-traveled-from-camera-to/91760#91760?newreg=12022d5bb157428a8a9de5e06a63412d).

# Usage

Install python 3.9.2 (version as the python in blender 2.93).

Then install the modules,

```
python -m pip install numba opencv-python
```

Open the Blender default scene.

Modify `Module Path` to where `cv2` and `numba` are installed.

Click the buttons from the top to bottom.

Find the video in temperate file directory.

## Development

Install a portable version of [Blender](https://www.blender.org/download/) in user directory, and install the [VS Code plugin](https://marketplace.visualstudio.com/items?itemName=JacquesLucke.blender-development) and the [fake bpy](https://github.com/nutti/fake-bpy-module) for developent.

On Linux, to keep cache in RAM, create RAM file system,

```
mkdir ~/ramfs
sudo mount -t tmpfs -o size=2048M tmpfs ~/ramfs
```

## Warning

Only accept simple blend file and physical shader nodes.

Shorter path overwrites the longer ones.

Not fully tested.
