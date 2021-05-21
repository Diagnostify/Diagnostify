# Diagnostify: Your personal Health Consultant

### About Diagnostify
Diagnostify is a smart health monitoring system, which is made with the aim of reducing the number of severe Covid-19 cases by the <b>early and regular monitoring</b> of critical parameters of the user. This will in turn help to track down the number of cases and will also <b>ease the burden on the medical staff</b> of our country.
### Features

- It is free of cost and Open Source.
- It is user-friendly and provides full statistics with quite accurate results
- It has a legitimate diagnostic test along with a designated X-ray and CT scan page, which can be used to tell whether the person is infected by Covid-19 or not
- Our app takes the input in the form of speech from the user making our app usable by all
- Almost everything in our app is automated, and the results come in less than a minute
### Downloads And Installation
- First, open and download the installer from the following link:
```bash
https://www.dropbox.com/s/mt8or97b2jl1n9b/Diagnostify-Setup.exe?dl=0
```
- Then, run the File: `Diagnostify-Setup.exe` from the Downlods folder
- Choose the app installation location and click Next
- The Installer will download the App, and the required dependencies to run the App
- After the installation finishes, click close and Search for `Diagnostify` in the Search Bar and Run the `Diagnostify.exe`
- Enter the User Information and then app will run
## Note
Before running the code, 
- Install the dependencies: 
```python
pip install pyttsx3 speech_recognition PySimpleGUI matplotlib wxpython keras opencv-python kivy
python >= 3.6
```
- Please open the files in the directory `models/xception_chest.h5` and  `models/xception_ct.h5` and download the files and save them with the same names
