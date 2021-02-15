import sys, os, webbrowser, win32clipboard, PySimpleGUI as sg #https://pysimplegui.readthedocs.io/
from PIL import Image

#GUI INIT
sg.theme("GreenTan")
layout = [[sg.InputText("file name", size = (60, 1))],
		  [sg.FileBrowse()],
		  [sg.HorizontalSeparator()],
		  [sg.Text("(c) Jona Heinke, 2021", enable_events = True, key = "copyright"), sg.VerticalSeparator(), sg.Text("released under MIT license", enable_events = True, key = "license")]]
window = sg.Window("Extract frames from GIF", layout, margins = (0, 3))

#GUI LOOP
while True:
	event, values = window.read()
	if event and event.startswith("copyright"):
		webbrowser.open("https://github.com/jonaheinke/powerpoint_images_from_gif")
	elif event and event.startswith("license"):
		webbrowser.open("https://github.com/jonaheinke/powerpoint_images_from_gif/blob/main/LICENSE")
	if event == sg.WIN_CLOSED:
		break
