*BUGS*
- [x] 1 When removing item from custom arguments, the value in the main arguments list is not reset to default.
- [x] 2 Error when adding a simple argument to custom arguments.
- [x] 3 Issue with verifying types of complex arguments (any data is considered invalid, likely some error within the code being caught by the try/except isntead of going through)
- [x] 4 Selecting a pneumatic in the dropdown does not persist
- [x] 5 If we remove or add arguments to the point where there are no arguments in the list, the add button does not update (disappear/appear)
- [x] 6 When selecting a motor object then a pneumatic object the pneumatic dropdown is not properly hidden
  - [x] ![alt text](image.png)
- [ ] driveFor is probably completely broekn
- [ ] removing item from sequence does not update displayed list
- [x] renaming sequence items causes big lag
- [x] grabbing an event to drag sometimes jumps the wrong event to cursor
  - [x] <video controls src="20250422-0119-19.8835308.mp4" title="Title"></video>
- [x] dragging event pos doesn't mark file as unsaved
- [ ] keep an eye out -- sequence not updating and hiding things, possibly after save/load?
- [ ] modifying sequence list (order of elements, names) causes huge lag spike
- [ ] flip button does not flip:
  - [ ] initialPose x coordinate
  - [ ] path event positions
*TODO*
- [x] finish saving and loading
- [x] when opening program try to open last edited file
- [x] file --> new resets sequence and filepath
- [x] when we have a sequence object selected, add new items immediately after the selected one instead of at the end and select the new object
- [ ] when moving objects up and down, make sure they get re-selected in the pygame_gui list so that the item is highlighted properly
*WANT TO DO*
- [ ] Robot simulation with timing
- [ ] Robot simulation path results
- [ ] more undo functionality
- [ ] fix paths to be done correctly such that we can run as .exe
