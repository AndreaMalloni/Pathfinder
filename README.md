# PathFinder - file automation made easy
PathFinder is a simple automation app made with python that aims to help you organize your system and keep it always clean. 

## How does it work?
Like the title says, it's simple.

1. You set a **source** folder
2. You specify a **filetype**, or more than one, so that PathFinder can recognize which file you want to organize
3. At last, you set, for each filetype, a **destination** folder, where those file will be moved.

After this little initial configuration, everytime a file of the said types appens to be in one of the source folders, for example your **downloads** folder, it will be moved in the relative destination. 

Are you tired of your messy downloads folder? Now you can fix it.

## Details
Here are some details on the implementation 
### Interface
The GUI is made with PyQt5 framework, in particular PySide2, it's open source version. All the code can be found in the *interface.py* file.
### Service
The script, which will run in background as a windows service, uses the **watchdog** module to monitor the filesystem and keep an eye on your files. All the code can be found in the *pathfinder.py* file.
### Configuration
Your configuration is stored in .ini format, in the *data.ini* file

**WARNING - DEPRECATED CODE, USE AT YOUR OWN RISK**
