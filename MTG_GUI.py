from tkinter import *
from tkinter import ttk        
from PIL import ImageTk,Image
import base64
from urllib.request import urlopen
    
root = Tk()
root.title("MTG Deck tool")
root.geometry('1000x600+200+20')

def selected():
	pass
	
def add_selected():
	deck_list.insert(END,inv_list.get(ANCHOR))
		
def remove_selected():
	deck_list.delete(ANCHOR)
	deck_list.config(text='')


# Labels
ttk.Label(root, text = 'Deck Details:').place(x = 300, y = 50, width = 100, height = 30)
ttk.Label(root, text = 'Ramp').place(x = 300, y = 80, width = 100, height = 30)
ttk.Label(root, text = 'Board Wipes').place(x = 300, y = 110)
ttk.Label(root, text = 'Target Cards').place(x = 300, y = 140)
ttk.Label(root, text = 'Enter the Battlefield effects').place(x = 300, y = 170)
ttk.Label(root, text = 'Card Draw').place(x = 300, y = 200)

# ttk.Label(root, text = 'Card Draw').place(relx = .5, x = 300, rely = .4, y = 170)
# ttk.Label(root, text = 'Blue').place(relx = 0.5, rely = 0.5, anchor = 'center', relwidth = 0.5, relheight = 0.5)
# ttk.Label(root, text = 'Green').place(relx = 0.5, x = 100, rely = 0.5, y = 50)
# ttk.Label(root, text = 'Orange').place(relx = 1.0, x = -5, y = 5, anchor = 'ne')

# Listboxes
deck_list = Listbox(root)
deck_list.insert(END,'this')
deck_list.insert(END,'that')
deck_list.insert(END,'there')
deck_list.place(x = 100, y = 80, width = 100, height = 500)

inv_list = Listbox(root)
inv_list.insert(END,'this')
inv_list.place(x = 800, y = 80, width = 100, height = 500)

# Buttons
deck_remove = ttk.Button(root, text = "Remove Selected", command = remove_selected)
deck_remove.place(x = 100, y = 20, width = 100, height = 40)

deck_add = ttk.Button(root, text = "Add Selected", command = add_selected)
deck_add.place(x = 800, y = 20, width = 100, height = 40)

# Images
# card_img = ImageTk.PhotoImage(Image.open("filename"))

# this GIF picture previously downloaded to tinypic.com
# image_url = "https://deckbox.org/system/images/mtg/cards/107093.gif"
# 
# image_byt = urlopen(image_url).read()
# image_b64 = base64.encodestring(image_byt)
# photo = tk.PhotoImage(data=image_b64)

# create a white canvas
# cv = tk.Canvas(bg='white')
# cv.pack(side='top', fill='both', expand='yes')

# put the image on the canvas with
# create_image(xpos, ypos, image, anchor)
# cv.create_image(10, 10, image=photo, anchor='nw')

root.mainloop()