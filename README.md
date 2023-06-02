# BLTS-Installer
Installer and Migration Tool for BLTS

## Dependencies
* pymysql
* psutil
* pyinstaller (optional)

## Building
If you want to build the tool for portability and without needing python to run the script,\n
I recommend building using pyinstaller **(Tested)**


First install pyinstaller via

`pip install pyinstaller`

then navigate to project directory and build from there 

`pyinstaller --onefile --add-data=assets/*;assets --icon=assets/icon.ico pysintaller --name="BLTS Installer and Migration Tool"`

then the output will be placed on the `/dist` folder

### Running
Running via python

`python installer.py`

Note: *If you build the project using pyinstaller, just run the executable file*
