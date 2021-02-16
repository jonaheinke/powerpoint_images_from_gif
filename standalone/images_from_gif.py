# -------------------------------------------------------------------------------------------------------------------- #
#                                                        IMPORT                                                        #
# -------------------------------------------------------------------------------------------------------------------- #
import json, webbrowser, win32clipboard, PySimpleGUI as sg #https://pysimplegui.readthedocs.io/
from io import BytesIO
from PIL import Image #https://pillow.readthedocs.io/



# -------------------------------------------------------------------------------------------------------------------- #
#                                                      MISC SETUP                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
sg.theme("GreenTan") #set theme for both windows
with open("schema.json", encoding = "utf-8-sig") as f:
	try:
		schema = json.load(f)
	except json.decoder.JSONDecodeError:
		print("JSON-Datei konnte nicht dekodiert werden.")
		exit()



# -------------------------------------------------------------------------------------------------------------------- #
#                                                       CHILD GUI                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
def export_image(pre_image, sch):
	with BytesIO() as output:
		if sch:
			with Image.new("RGB", pre_image.size + (sch["expand"][0] + sch["expand"][2], sch["expand"][1] + sch["expand"][3])) as image:
				image.paste(pre_image, (sch["expand"][0], sch["expand"][3]))
				with Image.open(sch["path"]) as label, label.rotate(int(sch["rotation"]) & 3 * 90) as rotated_label:
					image.paste(rotated_label, tuple(sch["position"]))
				image.save(output, "BMP")
		else:
			pre_image.save(output, "BMP")
		win32clipboard.OpenClipboard()
		win32clipboard.EmptyClipboard()
		win32clipboard.SetClipboardData(win32clipboard.CF_DIB, output.getvalue()[14:])
		win32clipboard.CloseClipboard()

child_window = None
def open_image(path):
	global child_window
	with Image.open(path) as image:
		child_layout = [[sg.Text("Click on an image to copy it")],
						[sg.HorizontalSeparator()]]
		for i in range(image.n_frames): #try getattr(image, "n_frames", 1) if it doesn't work
			image.seek(i)
			size = ()
			with BytesIO() as dat, image.resize(size) as scaled_image:
				scaled_image.save(dat, "GIF")
				child_layout.append([sg.Image(data = dat.getvalue(), key = f"image_{i}", enable_events = True)])
		child_layout.append([sg.Text("Bottom")])
		
		child_window = sg.Window("child window", child_layout, force_toplevel = True)
		while True:
			event = child_window.read()[0]
			if event and event.startswith("image_"):
				image.seek(int(event[6:]))
				export_image(image, dict())
			if event == sg.WIN_CLOSED:
				break



# -------------------------------------------------------------------------------------------------------------------- #
#                                                       MAIN GUI                                                       #
# -------------------------------------------------------------------------------------------------------------------- #
layout = [[sg.FileBrowse(tooltip = "open a gif file", size = (15, 2), enable_events = True, key = "open")],
		  [sg.HorizontalSeparator()],
		  [sg.Text("(c) Jona Heinke, 2021", enable_events = True, key = "copyright"), sg.VerticalSeparator(), sg.Text("released under MIT license", enable_events = True, key = "license")]]
window = sg.Window("Extract frames from GIF", layout, margins = (0, 3))
while True:
	event, values = window.read()
	if event == "open" and values["open"]:
		open_image(values["open"])
	elif event and event.startswith("copyright"):
		webbrowser.open("https://github.com/jonaheinke/powerpoint_images_from_gif")
	elif event and event.startswith("license"):
		webbrowser.open("https://github.com/jonaheinke/powerpoint_images_from_gif/blob/main/LICENSE")
	if event == sg.WIN_CLOSED:
		break
