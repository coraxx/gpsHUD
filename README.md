# README #

"GPS HUD" is a tool to create speedometer animations from gpx data. I build this to create gauges that can be overlaid over e.g. GoPro footage of car/bike/whatever tour where you also recorded your GPS data. I use [GPSSpeed HD](https://itunes.apple.com/en/app/gpsspeed-hd-das-gps-tool-mit/id432156279?mt=8) on my iPhone to record the trip and export it as gpx. This data and a gauge template (e.g. a 500x500 px PNG file) can be imported and a pointer is animated based on the speed calculated from the GPS file.

![gpsHUD screenshot](http://semper.space/gpsHUD/Screenshot_01.png "GPS HUD")

The Toolbox is written in Python 3 and comes with a PyQt6 GUI. Further dependencies as of now are:

* PyQt6 [^1]
+ numpy [^2]
+ scipy [^2]
+ gizeh [^2] which needs cairo [^1]
 - on windows also needs gtk2 [(I'm using a x64 gtk2 version for my x64 Python)](http://lvserver.ugent.be/gtk-win64/gtk2-runtime/)
 - on MacOs X you can use 'brew install cairo'
+ moviepy [^2]
+ gpxpy [^2]
+ pykalman [^2]

[^1]: usually available via your favorite package manager
[^2]: available via pip

Documentation and introduction will come soon.

### License ###

Copyright (C) 2016  Jan Arnold

	This program is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 3 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program.  If not, see <http://www.gnu.org/licenses/>.

### Version ###

v2.0.0b - initial beta release

### Binaries ###

There will be [Pyinstaller](http://www.pyinstaller.org) binaries available for Mac OS X and Windows soon.


### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact


![gpsHUD gif example](http://semper.space/gpsHUD/gauge_example.gif "GPS HUD gif")
