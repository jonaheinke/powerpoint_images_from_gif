import os, PyInstaller.__main__

#os.chdir(os.path.dirname(os.path.realpath(__file__)))
#print(os.path.dirname(os.path.realpath(__file__)))

#include = ("img", "schema.json")
include = ["schema.json"]

print(["image_extract_label.py", "--onefile", *["--add-data \"" + file_folder + os.pathsep + file_folder + "\"" for file_folder in include]])

PyInstaller.__main__.run([
	"image_extract_label.py",
	#"--onefile",
	"-F",
	#"--distpath 'C:\\Users\\jona-\\Desktop'",
	#*["--add-data \"" + file_folder + os.pathsep + file_folder + "\"" for file_folder in include]
	#"--add-data 'res/;.'",
	"--noconsole",
	"--clean",
	"--upx-dir=C:\\Programme\\PATHABLE\\upx\\"
	#"--specpath build",
])

#TODO: see https://medium.com/swlh/easy-steps-to-create-an-executable-in-python-using-pyinstaller-cc48393bcc64, .spec editing -> datas
"""
print("Now change datas to [('res', 'res')]")
input()
PyInstaller.__main__.run(["image_extract_label.spec", "-F"])
"""