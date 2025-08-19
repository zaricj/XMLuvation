[app]

# title of your application
title = XMLuvation

# project root directory. default = The parent directory of input_file
project_dir = .

# source file entry point path. default = main.py
input_file = C:\Users\ZaricJ\Documents\Main\02_Entwicklung_und_Tools\GitHub\XMLuvation\src\main.py

# directory where the executable output is generated
exec_directory = C:\Users\ZaricJ\Documents\Main\02_Entwicklung_und_Tools\GitHub\XMLuvation\output

# path to the project file relative to project_dir
project_file = ../pyproject.toml

# application icon
icon = C:\Users\ZaricJ\Documents\Main\02_Entwicklung_und_Tools\GitHub\XMLuvation\src\resources\icons\xml_256px.ico

[python]

# python path
python_path = C:\Users\ZaricJ\Documents\Main\02_Entwicklung_und_Tools\GitHub\XMLuvation\.venv\Scripts\python.exe

# python packages to install
packages = Nuitka==2.6.8

# buildozer = for deploying Android application
android_packages = buildozer==1.5.0,cython==0.29.33

[qt]

# paths to required qml files. comma separated
# normally all the qml files required by the project are added automatically
qml_files = 

# excluded qml plugin binaries
excluded_qml_plugins = 

# qt modules used. comma separated
modules = Core,Gui,Widgets

# qt plugins used by the application. only relevant for desktop deployment
# for qt plugins used in android application see [android][plugins]
plugins = platforms/darwin,iconengines,platforms,imageformats,egldeviceintegrations,styles,platformthemes,generic,accessiblebridge,xcbglintegrations,platforminputcontexts

[android]

# path to pyside wheel
wheel_pyside = 

# path to shiboken wheel
wheel_shiboken = 

# plugins to be copied to libs folder of the packaged application. comma separated
plugins = 

[nuitka]

# usage description for permissions requested by the app as found in the info.plist file
# of the app bundle. comma separated
# eg = extra_args = --show-modules --follow-stdlib
macos.permissions = 

# mode of using nuitka. accepts standalone or onefile. default = onefile
mode = onefile

# specify any extra nuitka arguments
extra_args = --quiet --noinclude-qt-translations

[buildozer]

# build mode
# possible values = ["aarch64", "armv7a", "i686", "x86_64"]
# release creates a .aab, while debug creates a .apk
mode = debug

# path to pyside6 and shiboken6 recipe dir
recipe_dir = 

# path to extra qt android .jar files to be loaded by the application
jars_dir = 

# if empty, uses default ndk path downloaded by buildozer
ndk_path = 

# if empty, uses default sdk path downloaded by buildozer
sdk_path = 

# other libraries to be loaded at app startup. comma separated.
local_libs = 

# architecture of deployed platform
arch = 

