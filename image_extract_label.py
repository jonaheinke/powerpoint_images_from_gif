version = "1.2"

# -------------------------------------------------------------------------------------------------------------------- #
#                                                        IMPORT                                                        #
# -------------------------------------------------------------------------------------------------------------------- #
import os, platform, operator, json, webbrowser, win32clipboard, PySimpleGUI as sg #https://pysimplegui.readthedocs.io/
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError #https://pillow.readthedocs.io/



# -------------------------------------------------------------------------------------------------------------------- #
#                                                      MISC SETUP                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
def replace_name(value):
	value["name"].replace("_", " ")
	return value

sg.theme("GreenTan") #set theme for both windows
schema = {}
try: #https://cloudconvert.com/woff2-to-ttf
	with open(os.path.join("res", "schema.json"), encoding = "utf-8-sig") as f:
		try:
			temp = json.load(f)
		except json.decoder.JSONDecodeError:
			sg.Popup("JSON file couldn't be decoded.", any_key_closes = True)
	#schema = {key.replace("_", " "):replace_name(value) for key, value in temp.items()}
except:
	sg.Popup("schema.json not found.", any_key_closes = True)
schema = dict(temp)
#TODO: name correction
'''
for group, sch_list in temp.items():
	#for el in value:
		#el["name"].replace("_", " ")
	for sch_name, sch_def in sch_list.items():
		
	schema[group.replace("_", " ")] = value
'''


# -------------------------------------------------------------------------------------------------------------------- #
#                                                       CHILD GUI                                                      #
# -------------------------------------------------------------------------------------------------------------------- #
#a ≡ b mod m
#  | a ∈ list(ℤ) ∪ tuple(ℤ)
#  | b ∈ tuple(ℕ\[m, ∞))
#  | m ∈ ℕ*
def modulo(a, m):
	return tuple(map(operator.mod, a, m))

def gettextsize(font, content):
	return ([], 0, "") #font.getsize(content)

delimiter = "_"
def encode_descriptor(items):
	return delimiter.join(map(lambda x: str(x).replace(delimiter, " "), items))

def decode_descriptor(string):
	return string.split(delimiter)

def export_image(pre_image, sch, content = ""):
	pre_image = pre_image.convert("RGBA")
	with BytesIO() as output:
		if sch:
			image_size = (pre_image.width + sch["expand"][1] + sch["expand"][3], pre_image.height + sch["expand"][0] + sch["expand"][2])
			with Image.new("RGBA", image_size, (0xFF,) * 3) as image:
				image.alpha_composite(pre_image, modulo((sch["expand"][3], sch["expand"][0]), image_size)) #TODO: allow expand to be negative for cropping
				with Image.open(os.path.join("res", sch["file"])).convert("RGBA") as label:#, label.rotate(int(sch["rotation"]) & 3 * 90) as rotated_label:
					image.alpha_composite(label, modulo(sch["position"], image_size))
				#print text
				if content and "text" in sch:
					text = sch["text"]
					font = ImageFont.truetype(text["font"], text["size"])
					widths, height, newcontent = gettextsize(font, content)
					draw = ImageDraw.Draw(image)
					for width in widths:
						draw.rectangle([(x0, y0), (x1, y1)] or [x0, y0, x1, y1], text["background"])
					draw.multiline_text(xy, newcontent, text["color"], font, anchor, text["spacing"])
				image.save(output, "BMP")
		else:
			pre_image.save(output, "BMP")
		win32clipboard.OpenClipboard()
		win32clipboard.EmptyClipboard()
		win32clipboard.SetClipboardData(win32clipboard.CF_DIB, output.getvalue()[14:])
		win32clipboard.CloseClipboard()
		sg.PopupNoButtons("copied to clipboard", auto_close = True, auto_close_duration = 2, non_blocking = True, no_titlebar = True, keep_on_top = True)

def open_image(path):
	#choose cursor for images on different platforms
	platform_str = platform.system()
	if platform_str == "Darwin":
		image_cursor = "copy"
	else:
		image_cursor = "hand2"

	#window
	try:
		with Image.open(path) as image:
			#build layout
			child_layout = [[sg.Radio("no schema", "SCHEMA", True, key = "radio", enable_events = True)],
							[sg.Frame(group, [[sg.Radio(sch_name, "SCHEMA", key = encode_descriptor(["radio", group, sch_name]), enable_events = True)] for sch_name in sch_list.keys()], vertical_alignment = "top") for group, sch_list in schema.items()],
							[sg.Input(size = (32, 1), disabled = True, key = "content")],
							[sg.HorizontalSeparator()]]
			scalar = 0.7
			size = (int(image.width * scalar), int(image.height * scalar))
			rows = (sg.Window.get_screen_size()[1] - 185) // (size[1] + 8)
			"""
			cols = 1
			while ceil(image.n_frames / float(cols)) * (size[1] + 10) + 100 > sg.Window.get_screen_size()[1]:
				cols += 1
			"""
			for i in range(rows): #image.n_frames, try getattr(image, "n_frames", 1) if it doesn't work
				row = []
				j = 0
				while (index := i + j * rows) < image.n_frames:
					image.seek(index)
					with BytesIO() as dat, image.resize(size) as scaled_image:
						scaled_image.save(dat, "PNG")
						row.append(sg.Image(data = dat.getvalue(), background_color = "white", key = f"image_{index}", tooltip = "click: copy to clipboard", enable_events = True))
					j += 1
				child_layout.append(row)

			#create window and handle its events
			selected_schema = None
			child_window = sg.Window("click on image to copy", child_layout, margins = (0, 3), force_toplevel = True).Finalize()
			for i in range(image.n_frames):
				child_window[f"image_{i}"].Widget.config(cursor = image_cursor)
			while True:
				event, values = child_window.read()
				if event == sg.WIN_CLOSED:
					break
				elif isinstance(event, str):
					dec = decode_descriptor(event)
					if dec[0] == "image":
						image.seek(int(dec[1]))
						export_image(image, selected_schema)
					elif dec[0] == "radio":
						if len(dec) > 2:
							selected_schema = schema[dec[1]][dec[2]]
							child_window["content"].Update(disabled = "text" not in selected_schema)
						else:
							selected_schema = None
							child_window["content"].Update(disabled = True)
				else:
					print(event, values)
	except FileNotFoundError:
		sg.Popup("File not found.", any_key_closes = True)
	except UnidentifiedImageError:
		sg.Popup("Image file cannot be identified.", any_key_closes = True)
	except TypeError:
		sg.Popup("Image file type not supported.", any_key_closes = True)
	except:
		sg.Popup("Unknown error while opening picture.", any_key_closes = True)



# -------------------------------------------------------------------------------------------------------------------- #
#                                                       MAIN GUI                                                       #
# -------------------------------------------------------------------------------------------------------------------- #
layout = [[sg.Column([[sg.FileBrowse(tooltip = "open an image file", size = (15, 2), enable_events = True, key = "open")]]), sg.Column([[sg.Text("Version: " + version)]], element_justification = "right", expand_x = True)],
		  [sg.HorizontalSeparator()],
		  [sg.Text("(c) Jona Heinke, 2021", enable_events = True, key = "copyright"), sg.VerticalSeparator(), sg.Text("released under MIT license", enable_events = True, key = "license")]]
window = sg.Window("label & copy image frames", layout, margins = (0, 3)).Finalize()
window["copyright"].Widget.config(cursor = "hand2")
window["license"].Widget.config(cursor = "hand2")
while True:
	event, values = window.read()
	if event == "open" and values["open"]:
		open_image(values["open"])
	elif event and event.startswith("copyright"):
		webbrowser.open("https://github.com/jonaheinke/powerpoint_images_from_gif")
	elif event and event.startswith("license"):
		webbrowser.open("https://github.com/jonaheinke/powerpoint_images_from_gif/blob/main/LICENSE")
	elif event == sg.WIN_CLOSED:
		break
	else:
		print(event, values)