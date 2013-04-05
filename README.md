# Welcome to Tally

Many labs around the world conduct research that relies heavily on perception experiments with video. Standards for operating procedures, such as the ITU recommendations, exist for these kinds of experiments. However, the current tools for data collection for subjective testing are outdated or insufficient, and efforts to improve collection methods are too sparse and fractured to be widely effective.

To address this need, we have developed Tally, a web- based data collection tool for subjective video experiments. Our tool has numerous advantages, most notably the decoupled voting and viewing interface, flexibility and robustness, and the ability to share and collaborate on projects. We believe our web-based design is not only superior to previous attempts at such a tool, but is also the proper way of addressing the data collection problem.

Releasing the software as open source encourages growth and a well-supported user community. It is our hope that Tally will be widely adopted. The more people who use it, the better and more effective it will become. We designed Tally on the principles of openness, transparency, and collaboration, and we hope that our tool promotes these values among the research community through its use.

## Design

We designed Tally as a web-based system. Since subject scoring is done over a network, the voting control can be decoupled from the media player. The media is displayed to a TV or monitor while voting is done through an web-enabled device such as a smart-phone, tablet, laptop, or desktop.

The web-based nature of our tool offers other new benefits as well. With this design collected data is available from anywhere, and sharing data is simple. Since each person has their own personal account on the website, many people can use the same system with their individual history and data saved.

## Authors and Contributors

Ankit K. Jain (<a href="https://github.com/ankitkj" class="user-mention">@ankitkj</a>) Can Bal (<a href="https://github.com/canbal" class="user-mention">@canbal</a>)

## Support or Contact

For any inquiries email tally.vpl@gmail.com and we'll get back to you as soon as we can.

## License

This content is released under the [MIT License](https://github.com/canbal/Tally/blob/master/LICENSE.txt).

---

# Installation

These are the suggested installation steps and work on our tested systems. Depending on your system configurations you may need to alter some of the steps.

For example Tally can potentially run on any python server, but we only tested for Apache+mod\_wsgi. We provide the installation steps for this server as a suggested configuration.

Also for Linux and MacOSX, you do not need to use any package manager to install dependencies. You can also download their source code and proceed with their installation guides.

## Windows
### Back-end
1. Install Python 2.7.x
	- download Python 2.7.3 Windows Installer from <http://www.python.org/download/> and run it
2. Install Django, Numpy, and Scipy
	- Django
		- download the tarball of latest version of Django (Django 1.5) from <https://www.djangoproject.com/download/> and extract
		- open command window, change into extracted Django directory, and execute command "{path to Python}\python.exe setup.py install". For example, if you extracted Django and installed Python to the C drive, the command would be
			`>> cd c:\Django-1.5`  
			`>> c:\Python27\python.exe setup.py install`  
	- numpy
		- download the binary installer "numpy-1.7.0-win32-superpack-python2.7.exe" from <https://www.djangoproject.com/download/> and run the installer.
	- scipy
		- download scipy-0.12.0b1-win32-superpack-python2.7.exe from <http://sourceforge.net/projects/scipy/files/> and run the installer.
3. Download Tally
	- download the zip file from <http://canbal.github.com/Tally/>
4. Setup Tally
	- change into back-end directory  
		`>> cd Tally/django_source`  
	- initialize the Tally system  
		`>> ./manage.py init_tally`  
	- open a browser and point it to the location printed in the command window, something like http://127.0.0.1:8000, and login with the superuser credentials you just created
	- create a tester account, then logout of the website, and login as the Tester to make sure everything is working
	- stop the development server by pressing `Ctrl-C` in the command window
5. Setup a web server
	- download and install XAMPP from <http://sourceforge.net/projects/xampp/>
	- dowload the win32 binary mod_wsgi for Python 2.7 from <https://code.google.com/p/modwsgi/wiki/DownloadTheSoftware>
	- rename the downloaded file to mod_wsgi.so
	- move mod_wsgi.so to C:\xampp\apache\modules
	- open C:\xampp\apache\conf\httpd.conf in a text editor
	- near the top of the file, there will be many lines beginning with "LoadModule …"
	- at the end of this list, add the line: `LoadModule wsgi_module modules/mod_wsgi.so`
	- toward the middle of the file, there will be this block of text:

		```
		<Directory />
			Options FollowSymLinks
			AllowOverride None
			Order deny,allow
			Deny from all
		</Directory>
		```
	- just below this text, add the lines:
		
		```
		WSGIScriptAlias / {path to Tally}/django_source/Tally/wsgi.py
		WSGIPythonPath {path to Tally}/django_source
		<Directory {path to Tally}/django_source/Tally>
			<Files wsgi.py>
				Order deny,allow
				Allow from all
			</Files>
		</Directory>

		Alias /static/ {path to Tally}/django_source/static/
		<Directory {path to Tally}/django_source/static>
			Order deny,allow
			Allow from all
		</Directory>
		```
	- run the xampp server: double-click the xampp icon and click the start button next to Apache
	- open a browser and navigate to the IP address of the computer you installed everything on. You can find your IP address by opening a command window, typing in ipconfig and hitting enter.  Your IP address is the number next to the text "IPv4 Address".  The Tally login page should appear at your IP address.  The web portion of the Tally system is now fully functional and accessible from anywhere as long as your server is running.

### Desktop app
1. Download the Qt libraries and creator from <http://qt-project.org/downloads>
	- download and install Qt libraries 4.8.4 for Windows (select the appropriate file for the compiler you have installed).  Note that Tally is only compatible with Qt libraries 4.8.4
	- download and install Qt Creator 2.6.2 for Windows
2. Open {path to Tally}\qt_source\tally_desktop.pro
3. Qt will prompt you to configure the project, asking for a build kit.  In the options menu > Build and Run > Qt Versions, click "Add..." and select c:\Qt\4.8.4\bin\qmake.exe.  Go to options > Build and Run > Kits (the next tab over), click on Desktop (the default build) and select the appropriate version (4.8.4) from the Qt version dropdown menu.  Click OK.
4. Build the project in Release mode.  Create a new directory to deploy the desktop app.  Copy tally_desktop.exe from the release build directory, and phonon4.dll, QtCore4.dll, QtGui4.dll, QtNetwork4.dll, and QtWebKit4.dll from C:\Qt\4.8.4\bin, into the deployment directory.  If you compiled with mingw, you may additionally need libgcc_s_dw201.dll and mingwm10.dll or something similar.  Copy the entire directory C:\Qt\4.8.4\plugins\phonon_backend into the deployment directory.  The deployment directory now contains everything you need to run Tally Desktop on any computer.  


## Ubuntu
### Back-end
1. Install required packages  
	`$ sudo apt-get install python python-dev build-essential libatlas-base-dev gfortran git`  
2. Download and install dependencies (easiest and recommended way is installing through pip)  
	- install setuptools (required to install pip) -- download appropriate version for your python from <https://pypi.python.org/pypi/setuptools> -- if not sure about the python version installed on your system check using:  
		`$ python -V`  
	- install pip (using get-pip.py) -- this will be used to install all the other components <http://www.pip-installer.org/en/latest/installing.html#using-the-installer>  
	- install Django through pip  
		`$ sudo pip install Django`  
	- install numpy through pip  
		`$ sudo pip install numpy`  
	- install scipy through pip  
		`$ sudo pip install scipy`  
3. Download Tally
	- [recommended] through git for later updates to code
		`$ git clone git://github.com/canbal/Tally.git`
	- [alternative] download the zip file from <http://canbal.github.com/Tally/>
4. Setup Tally    
	- change into back-end directory  
		`$ cd Tally/django_source`  
	- initialize the Tally system  
		`$ ./manage.py init_tally`  
	- open a browser and point it to the location printed in the command window, something like http://127.0.0.1:8000, and login with the superuser credentials you just created
	- create a tester account, then logout of the website, and login as the Tester to make sure everything is working
	- stop the development server by pressing `Ctrl-C` in the command window
5. Setup Apache
	- install apache and mod_wsgi  
		`$ sudo apt-get install apache2 libapache2-mod-wsgi`  
	- edit /etc/apache2/httpd.conf to contain following lines (requires elevated permissions):  

		```
		WSGIScriptAlias / {path to Tally}/django_source/Tally/wsgi.py
		WSGIPythonPath {path to Tally}/django_source
		<Directory {path to Tally}/django_source/Tally>
			<Files wsgi.py>
				Order deny,allow
				Allow from all
			</Files>
		</Directory>

		Alias /static/ {path to Tally}/django_source/static/
		<Directory {path to Tally}/django_source/static>
			Order deny,allow
			Allow from all
		</Directory>
		```
	- in order to allow access to the files in Tally, you need to change the owner of the file to apache. Execute following command to give ownership to the apache user (www-data):  
		`$ sudo chown -R www-data {path to Tally}/django_source`  
		`$ sudo chgrp -R www-data {path to Tally}/django_source`  
	- restart apache with mod_wsgi support  
		`$  sudo service apache2 restart`  

### Desktop App
1. Install Qt  
	`$ sudo apt-get install qt-sdk`
2. Run Qt Creator
3. Load Tally Qt project: {path to Tally}/qt_source/tally_desktop.pro
4. Compile and run


## MacOSX
### Back-end
1. Install or update to latest Xcode (Apple's developer IDE that contains gcc etc.)
2. Install Homebrew (Homebrew is a package manager for MacOSX and makes installing some of the tools required for Tally easier -- and makes the installation guide MacOSX version independent) <http://mxcl.github.com/homebrew/>  
	`$ ruby -e "$(curl -fsSL https://raw.github.com/mxcl/homebrew/go)"`  
3. Check Homebrew is updated and working  
	`$ brew update`  
	`$ brew doctor`  
	Note: The `brew doctor` command may give you warnings. Follow the instructions so all warnings are gone.
4. Set your path to point to Homebrew packages instead of already installed ones (such as python). They exist together without problem, this step just gives Homebrew packages priority.  
	`$ echo export PATH=/usr/local/bin:\$PATH >> ~/.bash_profile`
5. Restart your Terminal so it picks up the path
6. Download and install dependencies (easiest way is through Homebrew and pip)
	- install python (Install it from Homebrew as well even if you already have it from Apple, it also installs pip, which will be required to install some other dependencies)  
		`$ brew install python`
	- check for python (output should be /usr/local/bin/python)  
		`$ which python`
	- add the latest python to your path just like we added Homebrew on step 4:  
		`$ echo export PATH=/usr/local/share/python:\$PATH >> ~/.bash_profile`
	- restart your Terminal so it picks up the path
	- install Django through pip  
		`$ pip install Django`
	- install numpy
		- [option 1] through pip (this is known to make next step fail on some systems)  
			`$ pip install numpy`  
			`$ brew install gfortran (required for scipy)`  
			`$ pip install scipy`
		- [option 2] through Homebrew  
			`$ brew tap samueljohn/python`  
			`$ brew tap homebrew/science`  
			`$ pip install nose` (required for Homebrew numpy)  
			`$ brew install numpy`  
	- install scipy
		- [option 1] through pip
			`$ brew install gfortran (required for scipy)`  
			`$ pip install scipy`
		- [option 2] through Homebrew (this works only if you installed numpy using Homebrew as well)  
			`$ brew install scipy`  
		Note: Some older Macs are not compatible with the Homebrew version of gfortran. If you encounter an installation problem due to a gfortran error, follow the "FORTRAN" section at http://www.scipy.org/Installing_SciPy/Mac_OS_X and install it from universal binaries. Then unlink the existing Homebrew gfortran and link the newly installed compiler instead.  
			`$ brew unlink gfortran`  
			`$ ln -s /usr/bin/gfortran4.2 /usr/local/bin/gfortran`  
7. Download Tally
	- [recommended] through git for later updates to code
		`$ git clone git://github.com/canbal/Tally.git`
	- [alternative] download the zip file from <http://canbal.github.com/Tally/>
8. Setup Tally
	- change into back-end directory  
		`$ cd Tally/django_source`  
	- initialize the Tally system  
		`$ ./manage.py init_tally`  
	- open a browser and point it to the location printed in the command window, something like http://127.0.0.1:8000, and login with the superuser credentials you just created
	- create a tester account, then logout of the website, and login as the Tester to make sure everything is working
	- stop the development server by pressing `Ctrl-C` in the command window
9. Install mod\_wsgi
	- [option 1] using official Homebrew package (it is known that this step is causing error on some systems - [bug report]([bug report](https://github.com/mxcl/homebrew/issues/18185))  
		`$ brew tap homebrew/apache`  
		`$ brew install mod_wsgi`  
		Note: If you're having installation problems relating to a missing 'cc' compiler and 'OSX10.8.xctoolchain', read the "Troubleshooting" section of https://github.com/Homebrew/homebrew-apache
	- [option 2] using [unofficial fixed package](https://github.com/ahihi/homebrew-apache/commit/600bf143272f34371cf0826d69758b56083f529d) developed by <a href="https://github.com/ahihi" class="user-mention">@ahihi</a>  
		`$ brew install https://raw.github.com/ahihi/homebrew-apache/600bf143272f34371cf0826d69758b56083f529d/mod_wsgi.rb`  
10. Setup mod\_wsgi to work with Apache
	- first find where Homebrew installed mod_wsgi.so and make sure this file exists  
		`$ brew list mod_wsgi`  
	- link this file to the apache2/modules  
		```
		$ sudo ln -s `brew list mod_wsgi` /usr/libexec/apache2/
		```
	- edit /etc/apache2/httpd.conf to contain following lines (requires elevated permissions):
		- near the top of the file, there will be many lines beginning with "LoadModule …"
		- at the end of this list, add the line: `LoadModule wsgi_module modules/mod_wsgi.so`
		- toward the middle of the file, there will be this block of text:

		```
		<Directory />
			Options FollowSymLinks
			AllowOverride None
			Order deny,allow
			Deny from all
		</Directory>
		```
		- just below this text, add the lines:
		
		```
		WSGIScriptAlias / {path to Tally}/django_source/Tally/wsgi.py
		WSGIPythonPath {path to Tally}/django_source
		<Directory {path to Tally}/django_source/Tally>
			<Files wsgi.py>
				Order deny,allow
				Allow from all
			</Files>
		</Directory>

		Alias /static/ {path to Tally}/django_source/static/
		<Directory {path to Tally}/django_source/static>
			Order deny,allow
			Allow from all
		</Directory>
		```
11. Start Apache
	- click on Apple logo > System Preferences
	- click on Sharing
	- turn on Web Sharing (click on the checkbox next to it)
	- in order to allow access to the files in Tally, you need to change the owner of the file to apache. Execute following command to give ownership to the apache user (www):  
		`$ sudo chown -R _www {path to Tally}/django_source`  
		`$ sudo chgrp -R _www {path to Tally}/django_source`  

### Desktop App
1. Installing Tally Desktop
	- download the Qt libraries and creator from <http://qt-project.org/downloads>
		- download and install Qt libraries 4.8.4 for Mac.  Note that Tally is only compatible with Qt libraries 4.8.4
		- download and install Qt Creator 2.6.2 for Mac.
2. Open Qt Creator and load the qt_source/tally_desktop.pro
	- File > Open File or Project > {path to Tally}/qt_source/tally_desktop.pro
	- Configure project
3. Compile and run

---

# Ideas for Future Release

Here is a list of items we would like to include in Tally in the future release. Feel free to contribute :)

### Subjective test functionality
1. Allow for practice tests which come at the beginning of every test instance, are not randomized, and whose scores are discarded or kept separate from the other test data
2. Display banners before videos and test cases such as “Test #1” or “Reference Video” for a configurable number of seconds
3. Allow a timed break between test cases
4. Enable Tally for images
5. Support SAMVIQ, DSCQS Type I
6. Insert instruction sheet for subjects before they begin a test, maybe allow a PDF to be uploaded (add instruction field to Test model)

### Site features
1. If forgotten, allow changing password
2. Disable action buttons and provide popup explanation instead of making them invisible when unavailable
3. Video uploading/downloading

### Advanced
1. Enable PDF report generation
2. Automatic data analysis tools
3. Standardized tests for visual acuity, stereo vision, and eye dominance online registration tool for scheduling participant
