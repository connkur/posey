# Posey
## DCC agnostic pose library

### Posey is a work in progress

#### Overview
The purpose of this tool is to provide animators with a single, searchable pose libaray that is compatible across common DCCs such ans Blender, Maya and MotionBuilder. The goal is to use as little API (maya.cmds, pyfbsdk, ...etc) specific code as possible and utilize matrices as the basis of copying and pasting poses since the applications I mentioned above all use matrices in some format.

#### Expectations:
1. This is a work in progress and core functionality is not done

#### Instructions:
1. Add posey to your application's PYTHONPATH
2. Run the following code:
```
import posey
posey._build()
```
