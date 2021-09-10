#  2021  Paul Austin
# Thanks to https://scryfall.com/docs/api
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from tkinter import *
from tkinter import ttk
from tkinter import messagebox  # NEW ADDITION
from PIL import ImageTk, Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from pathlib import Path
from io import BytesIO
import matplotlib.pyplot as plt
import requests
import os
import time
import csv
import mtg_main
import mtg_sql
import json_load
import mtg_regex
from tkinter import filedialog

root = Tk()
root.title("MTG Deck tool")
root.geometry('1366x730+0+0')
style = ttk.Style()
style.configure("ImportDone", font=('wasy10', 80))
# style.theme_use("alt")
# stored_link = ""   ## Might not end up using this

Current_Folder = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
Root_Folder = Path(Current_Folder).parent
image_folder = Root_Folder / "images"
deck_folder = Root_Folder / "decks"
data_folder = Root_Folder / "db"

### Mana Symbol Images
whiteimg = ImageTk.PhotoImage(Image.open(image_folder / "whitemana.png"))
whiteimage = whiteimg._PhotoImage__photo.subsample(3)
blueimg = ImageTk.PhotoImage(Image.open(image_folder / "bluemana.png"))
blueimage = blueimg._PhotoImage__photo.subsample(3)
blackimg = ImageTk.PhotoImage(Image.open(image_folder / "blackmana.png"))
blackimage = blackimg._PhotoImage__photo.subsample(3)
redimg = ImageTk.PhotoImage(Image.open(image_folder / "redmana.png"))
redimage = redimg._PhotoImage__photo.subsample(3)
greenimg = ImageTk.PhotoImage(Image.open(image_folder / "greenmana.png"))
greenimage = greenimg._PhotoImage__photo.subsample(3)
colourlessimg = ImageTk.PhotoImage(Image.open(image_folder / "colourlessmana.png"))
colourlessimage = colourlessimg._PhotoImage__photo.subsample(3)

### Button Images
addtodeckbutton = ImageTk.PhotoImage(Image.open(image_folder / "addtodeckbutton.png"))
movetosideboardbutton = ImageTk.PhotoImage(Image.open(image_folder / "movetosideboardbutton.png"))
removeselectedbutton = ImageTk.PhotoImage(Image.open(image_folder / "removeselectedbutton.png"))
inventorybutton = ImageTk.PhotoImage(Image.open(image_folder / "inventorybutton.png"))
searchbutton = ImageTk.PhotoImage(Image.open(image_folder / "searchbutton.png"))
loaddeckbutton = ImageTk.PhotoImage(Image.open(image_folder / "loaddeckbutton.png"))
savedeckbutton = ImageTk.PhotoImage(Image.open(image_folder / "savedeckbutton.png"))
newcommanderbutton = ImageTk.PhotoImage(Image.open(image_folder / "promotebutton.png"))
newdeckbutton = ImageTk.PhotoImage(Image.open(image_folder / "newdeckbutton.png"))
partnerbutton = ImageTk.PhotoImage(Image.open(image_folder / "partnerbutton.png"))
deckdetailsbutton = ImageTk.PhotoImage(Image.open(image_folder / "deckdetailsbutton.png"))


class MtgGui:
    """ CLASS VARIABLES """
    commander = ""
    partner = ""
    current_card = ""
    current_tier = ""
    current_status = ""
    total_mana_cost_string = ""  # Will be used to determine total number of Mana Symbols in a deck of specific color
    sum_white = 0
    sum_blue = 0
    sum_black = 0
    sum_red = 0
    sum_green = 0
    sql_search_params = ""
    sql_search_statement = ""
    sql_inner_join = ""
    current_deck_notes = ""
    deck_status_options = ('ACTIVE', 'INACTIVE', 'UNASSEMBLED')
    deck_tier_options = ('Primary', 'Secondary', 'Online')

    """ INITIALIZATION AND GUI BUILDING START """

    def __init__(self, window):
        # Was getting way too long so it is divided up into GUI sections
        self.build_main_window(window)
        self.build_card_finder(window)
        self.build_deck_details(window)
        self.build_deck_selector(window)

    def build_deck_selector(self, window):
        #### DECK SELECTOR START ####
        ### Deck Selection Frame on the left side and A Card Finder Frame behind which it may hide ##
        self.deck_select = LabelFrame(window, text="Deck Selection", padx=10, pady=10)
        self.deck_select.place(x=25, y=10, width=380, height=440)

        self.treev_deck_list = ttk.Treeview(self.deck_select, selectmode='browse')
        self.treev_deck_list.place(x=0, y=0, width=350, height=372)
        self.treev_deck_list["columns"] = ("1", "2")
        self.treev_deck_list['show'] = 'headings'
        self.treev_deck_list.heading("1", text="Name")
        self.treev_deck_list.heading("2", text="Colour ID")
        self.treev_deck_list.column("1", width=215, minwidth=150, anchor='c')
        self.treev_deck_list.column("2", width=100, minwidth=80, anchor='se')

        ## Mana Colour Buttons
        deck_white = IntVar()
        deck_blue = IntVar()
        deck_black = IntVar()
        deck_red = IntVar()
        deck_green = IntVar()
        deck_colourless = IntVar()

        # Check Buttons to filter which decks to display in the deck list
        self.checkwhite_d = Checkbutton(self.deck_select, image=whiteimage, variable=deck_white,
                                        command=self.show_certain_decks, borderwidth=0)
        self.checkwhite_d.place(x=0, y=380)  # , width = 40)
        self.checkblue_d = Checkbutton(self.deck_select, image=blueimage, variable=deck_blue,
                                       command=self.show_certain_decks, borderwidth=0)
        self.checkblue_d.place(x=60, y=380)
        self.checkblack_d = Checkbutton(self.deck_select, image=blackimage, variable=deck_black,
                                        command=self.show_certain_decks, borderwidth=0)
        self.checkblack_d.place(x=120, y=380)
        self.checkred_d = Checkbutton(self.deck_select, image=redimage, variable=deck_red,
                                      command=self.show_certain_decks, borderwidth=0)
        self.checkred_d.place(x=180, y=380)
        self.checkgreen_d = Checkbutton(self.deck_select, image=greenimage, variable=deck_green,
                                        command=self.show_certain_decks, borderwidth=0)
        self.checkgreen_d.place(x=240, y=380)
        self.checkcolourless_d = Checkbutton(self.deck_select, image=colourlessimage, variable=deck_colourless,
                                             command=self.show_certain_decks, borderwidth=0)
        self.checkcolourless_d.place(x=300, y=380)

    def build_deck_details(self, window):
        #### DECK DETAILS START ####
        self.deck_details = LabelFrame(window, text="Deck Details", padx=10, pady=10)
        self.deck_details.place(x=25, y=10, width=380, height=440)

        ## Deck Name
        self.deckname_label = ttk.Label(self.deck_details, text='Deck Name:')
        self.deckname_label.place(x=0, y=0)  # , width = 150, height = 30)
        self.deck_name = StringVar(self.deck_details)  ## or "" ?
        self.decknamebox = Entry(self.deck_details, textvariable=self.deck_name)
        self.decknamebox.place(x=100, y=0, width=240)

        ## Deck ID Code
        self.deckid_label = ttk.Label(self.deck_details, text='Deck ID:')
        self.deckid_label.place(x=0, y=40)  # , width = 150, height = 30)
        self.deck_id = StringVar(self.deck_details)  ## or "" ?
        self.deckidbox = Entry(self.deck_details, textvariable=self.deck_id)
        self.deckidbox.place(x=100, y=40, width=240)

        ## Deck Physical Location
        self.decklocation_label = ttk.Label(self.deck_details, text='Deck Location:')
        self.decklocation_label.place(x=0, y=80)  # , width = 150, height = 30)
        self.decklocation = StringVar(self.deck_details)  ## or "" ?
        self.decklocationbox = Entry(self.deck_details, textvariable=self.decklocation)
        self.decklocationbox.place(x=100, y=80, width=240)

        ## Deck Tier
        self.decktier_label = ttk.Label(self.deck_details, text='Deck Tier:')
        self.decktier_label.place(x=0, y=120)  # , width = 150, height = 30)
        self.deck_tier = StringVar(value="Select an option")
        self.decktierbox = OptionMenu(self.deck_details, self.deck_tier, *self.deck_tier_options,
                                      command=self.get_deck_tier)
        self.decktierbox.place(x=100, y=118, width=240)

        ## Deck Status
        self.deckstatus_label = ttk.Label(self.deck_details, text='Deck Status')
        self.deckstatus_label.place(x=0, y=160)  # , width = 150, height = 30)
        self.deckstatus = StringVar(value="Select an option")
        self.deckstatusbox = OptionMenu(self.deck_details, self.deckstatus, *self.deck_status_options,
                                        command=self.get_deck_status)  # "ACTIVE", "INACTIVE", "UNASSEMBLED")
        self.deckstatusbox.place(x=100, y=158, width=240)

        ## Deck Table Name
        self.decktable_label = ttk.Label(self.deck_details, text='Deck Table:')
        self.decktable_label.place(x=0, y=200)  # , width = 150, height = 30)
        self.deck_table = StringVar(self.deck_details)  ## or "" ?
        self.decktablebox = Entry(self.deck_details, textvariable=self.deck_table)
        self.decktablebox.place(x=100, y=200, width=240)

        ## Deck Notes
        self.notes_label = ttk.Label(self.deck_details, text='Deck Notes:')
        self.notes_label.place(x=0, y=240)
        self.deck_notes = StringVar(self.deck_details)
        # self.decknotesbox = Text(self.deck_details, textvariable=self.deck_notes)
        self.decknotesbox = Entry(self.deck_details, textvariable=self.deck_notes)
        self.decknotesbox.place(x=100, y=240, width=240, height=160)

    def build_card_finder(self, window):
        #### CARD FINDER START ####
        self.card_finder = LabelFrame(window, text="Card Search", padx=10, pady=10)
        self.card_finder.place(x=25, y=10, width=380, height=440)

        ## Card Name
        self.cardname_label = ttk.Label(self.card_finder, text='Card Name:')
        self.cardname_label.place(x=0, y=0)  # , width = 150, height = 30)
        self.cardname = StringVar(self.card_finder)  ## or "" ?
        self.searchname = Entry(self.card_finder, textvariable=self.cardname)
        self.searchname.place(x=70, y=0, width=290)

        ## Converted Mana Cost
        self.cmc_label = ttk.Label(self.card_finder, text='CMC:')
        self.cmc_label.place(x=0, y=25)  # , width = 150, height = 30)
        self.cmc_approx = StringVar(value="Select an option")
        self.cmc_which = OptionMenu(self.card_finder, self.cmc_approx, "<=", "=", ">=")
        self.cmc_which.place(x=68, y=20, width=140)  # , height = 35)
        self.cardcmc = StringVar()  ## or "" ?
        self.searchcmc = Entry(self.card_finder, textvariable=self.cardcmc)
        self.searchcmc.place(x=220, y=25, width=140)

        ## Rules Text
        self.cardrules_label = ttk.Label(self.card_finder, text='Rules Text:')
        self.cardrules_label.place(x=0, y=51)  # , width = 150, height = 30)
        self.cardrules = StringVar()  ## or "" ?
        self.searchrules = Entry(self.card_finder, textvariable=self.cardrules)
        self.searchrules.place(x=70, y=51, width=290)

        ## Keywords
        self.keywords_label = ttk.Label(self.card_finder, text='Keywords:')
        self.keywords_label.place(x=0, y=75)  # , width = 150, height = 30)
        self.card_kw = StringVar()  ## or "" ?
        self.card_kwbox = Entry(self.card_finder, textvariable=self.card_kw)
        self.card_kwbox.place(x=70, y=75, width=290)

        ## Mana Colour Buttons
        self.inc_white = IntVar()
        self.inc_blue = IntVar()
        self.inc_black = IntVar()
        self.inc_red = IntVar()
        self.inc_green = IntVar()
        self.inc_colourless = IntVar()
        self.exclusive_colour = IntVar()
        self.checkwhite = Checkbutton(self.card_finder, image=whiteimage, variable=self.inc_white, borderwidth=0)
        self.checkwhite.place(x=0, y=100)  # , width = 40)
        self.checkblue = Checkbutton(self.card_finder, image=blueimage, variable=self.inc_blue, borderwidth=0)
        self.checkblue.place(x=47, y=100)
        self.checkblack = Checkbutton(self.card_finder, image=blackimage, variable=self.inc_black, borderwidth=0)
        self.checkblack.place(x=94, y=100)
        self.checkred = Checkbutton(self.card_finder, image=redimage, variable=self.inc_red, borderwidth=0)
        self.checkred.place(x=141, y=100)
        self.checkgreen = Checkbutton(self.card_finder, image=greenimage, variable=self.inc_green, borderwidth=0)
        self.checkgreen.place(x=188, y=100)
        self.checkcolourless = Checkbutton(self.card_finder, image=colourlessimage, variable=self.inc_colourless,
                                           borderwidth=0)
        self.checkcolourless.place(x=235, y=100)
        self.checkcolourless = Checkbutton(self.card_finder, text="Exclusive?", variable=self.exclusive_colour,
                                           borderwidth=0)
        self.checkcolourless.place(x=282, y=102)

        ## Card Type and Sub Type
        self.cardtype_label = ttk.Label(self.card_finder, text='Card Type:')
        self.cardtype_label.place(x=0, y=130)
        self.cardtype = Listbox(self.card_finder, selectmode="multiple")
        self.cardtype.insert(END, "Creature")
        self.cardtype.insert(END, "Instant")
        self.cardtype.insert(END, "Sorcery")
        self.cardtype.insert(END, "Artifact")
        self.cardtype.insert(END, "Enchantment")
        self.cardtype.insert(END, "Planeswalker")
        self.cardtype.insert(END, "Land")
        self.cardtype.place(x=0, y=155, width=100, height=115)
        self.subtype_label = ttk.Label(self.card_finder, text='Sub Type:')
        self.subtype_label.place(x=110, y=130)  # , width = 150, height = 30)
        self.subtype = StringVar()  ## or "" ?
        self.searchsubtype = Entry(self.card_finder, textvariable=self.subtype)
        self.searchsubtype.place(x=110, y=130, width=250)

        ## Power
        self.power_label = ttk.Label(self.card_finder, text='Power:')
        self.power_label.place(x=110, y=155)  # , width = 150, height = 30)
        self.power_approx = StringVar(value="Select an option")
        self.power_which = OptionMenu(self.card_finder, self.power_approx, "<=", "=", ">=")
        self.power_which.place(x=180, y=152, width=120)  # , height = 35)
        # self.power_which.configure(state='disabled')        
        self.cardpower = StringVar()  ## or "" ?
        self.searchpower = Entry(self.card_finder, textvariable=self.cardpower)
        # self.searchpower.configure(state='disabled')
        self.searchpower.place(x=310, y=155, width=50)
        ## Toughness
        self.tough_label = ttk.Label(self.card_finder, text='Toughness:')
        self.tough_label.place(x=110, y=185)  # , width = 150, height = 30)
        self.tough_approx = StringVar(value="Select an option")
        self.tough_which = OptionMenu(self.card_finder, self.tough_approx, "<=", "=", ">=")
        # self.tough_which.configure(state='disabled')
        self.tough_which.place(x=180, y=182, width=120)  # , height = 35)
        self.cardtough = StringVar()  ## or "" ?
        self.searchtough = Entry(self.card_finder, textvariable=self.cardtough)
        # self.searchtough.configure(state='disabled')
        self.searchtough.place(x=310, y=185, width=50)

        ## Draw/Ramp/Target/Broad/ETB  Check buttons
        self.inc_ramp = IntVar()
        self.inc_draw = IntVar()
        self.inc_target = IntVar()
        self.inc_broad = IntVar()
        self.inc_etb = IntVar()
        self.inc_legend = IntVar()
        self.checkramp = Checkbutton(self.card_finder, text='Ramp', variable=self.inc_ramp, borderwidth=0)
        self.checkramp.place(x=110, y=220)  # , width = 40)
        self.checkdraw = Checkbutton(self.card_finder, text='Draw', variable=self.inc_draw, borderwidth=0)
        self.checkdraw.place(x=190, y=220)
        self.checktarget = Checkbutton(self.card_finder, text='Target', variable=self.inc_target, borderwidth=0)
        self.checktarget.place(x=260, y=220)
        self.checkbroad = Checkbutton(self.card_finder, text='Broad', variable=self.inc_broad, borderwidth=0)
        self.checkbroad.place(x=110, y=250)
        self.checketb = Checkbutton(self.card_finder, text='ETB', variable=self.inc_etb, borderwidth=0)
        self.checketb.place(x=190, y=250)
        self.check_legend = Checkbutton(self.card_finder, text='Legendary', variable=self.inc_legend, borderwidth=0)
        self.check_legend.place(x=260, y=250)

        ## SQL Statement
        self.sql_label = ttk.Label(self.card_finder,
                                   text='OR.. enter SQL parameters: SELECT\nName, Mana_Cost, Card_Type FROM')
        self.sql_label.place(x=0, y=295)
        self.table_select = StringVar(value="Select an option")
        self.table_which = OptionMenu(self.card_finder, self.table_select, "Cards_Condensed", "Face_Cards_Condensed")
        self.table_which.place(x=200, y=300, width=160)
        self.sql_label2 = ttk.Label(self.card_finder, text='WHERE')
        self.sql_label2.place(x=0, y=335)
        self.sql_direct = StringVar(self.card_finder)  ## or "" ?
        self.sql_direct_box = Entry(self.card_finder, textvariable=self.sql_direct)
        self.sql_direct_box.place(x=50, y=335, width=310)

        ### Card Finder Frame Buttons ###
        self.searchthese = Button(self.card_finder, image=searchbutton, command=self.search_name, borderwidth=0)
        self.searchthese.place(x=120, y=360)

        #### CARD SEARCH RESULTS START ####
        ## Search Results frame on the left side hides behind the Card Finder Frame and Deck selection frame ##
        self.search_results = LabelFrame(window, text="Search Results", padx=10, pady=10)
        self.search_results.place(x=25, y=10, width=380, height=440)

        # Using treeview widget        
        self.treev_results = ttk.Treeview(self.search_results, selectmode='extended')
        self.treev_results.place(x=0, y=0, width=340, height=320)
        self.treev_results_vscrb = ttk.Scrollbar(self.search_results, orient="vertical",
                                                 command=self.treev_results.yview)
        self.treev_results_vscrb.place(x=340, y=0, width=25, height=320)
        # Configuring treeview 
        self.treev_results.configure(xscrollcommand=self.treev_results_vscrb.set)
        # Assigning the heading names to the respective columns
        self.treev_results["columns"] = ("1", "2", "3")
        self.treev_results['show'] = 'headings'
        self.treev_results.heading("1", text="Name")
        self.treev_results.heading("2", text="Mana Cost")
        self.treev_results.heading("3", text="Type")
        self.treev_results.column("1", width=165, minwidth=150, anchor='c')
        self.treev_results.column("2", width=74, minwidth=40, anchor=CENTER)
        self.treev_results.column("3", width=100, minwidth=70, anchor='se')

        ## Filter Name within Search Results
        self.filter_name_label = ttk.Label(self.search_results, text='Filter Name')
        self.filter_name_label.place(x=15, y=325)
        self.filter_name = StringVar()  ## or "" ?
        self.filter_name_box = Entry(self.search_results, textvariable=self.filter_name)
        self.filter_name_box.place(x=110, y=325, width=230)

        ### CARD SEARCH RESULTS   Frame Buttons ###
        self.add_from_search = Button(self.search_results, image=addtodeckbutton,
                                      command=self.add_selected_from_results, borderwidth=0)
        self.add_from_search.place(x=25, y=360)
        self.sb_from_search = Button(self.search_results, image=movetosideboardbutton,
                                     command=self.sb_selected_from_results, borderwidth=0)
        self.sb_from_search.place(x=200, y=360)

    def build_main_window(self, window):
        ###  MAIN WINDOW STUFF ###
        # Using treeview widget        
        style.map('Treeview', background=[('selected', 'red')])
        self.treev_maindeck = ttk.Treeview(window, selectmode='extended')
        self.treev_maindeck.place(x=950, y=0, width=370, height=370)
        self.treev_maindeck_vscrb = ttk.Scrollbar(window, orient="vertical", command=self.treev_maindeck.yview)
        self.treev_maindeck_vscrb.place(x=1320, y=0, width=30, height=370)

        self.treev_sideboard = ttk.Treeview(window, selectmode='extended')
        self.treev_sideboard.place(x=950, y=420, width=370, height=230)
        self.treev_sideboard_vscrb = ttk.Scrollbar(window, orient="vertical", command=self.treev_sideboard.yview)
        self.treev_sideboard_vscrb.place(x=1320, y=425, width=30, height=230)

        # Configuring treeview
        self.treev_maindeck.configure(xscrollcommand=self.treev_maindeck_vscrb.set)
        self.treev_sideboard.configure(xscrollcommand=self.treev_sideboard_vscrb.set)

        self.treev_maindeck["columns"] = ("1", "2", "3")
        self.treev_maindeck['show'] = 'headings'

        self.treev_sideboard["columns"] = ("1", "2", "3")
        self.treev_sideboard['show'] = 'headings'
        # Assigning the heading names to the respective columns
        self.treev_maindeck.heading("1", text="Name")
        self.treev_maindeck.heading("2", text="Type")
        self.treev_maindeck.heading("3", text="Qty")

        self.treev_sideboard.heading("1", text="Name")
        self.treev_sideboard.heading("2", text="Type")
        self.treev_sideboard.heading("3", text="Qty")
        # Assigning the width and anchor to  the respective columns
        self.treev_maindeck.column("1", width=160, minwidth=120, anchor='c')
        self.treev_maindeck.column("2", width=100, minwidth=70, anchor=CENTER)
        self.treev_maindeck.column("3", width=40, minwidth=40, anchor='se')

        self.treev_sideboard.column("1", width=160, minwidth=120, anchor='c')
        self.treev_sideboard.column("2", width=100, minwidth=70, anchor=CENTER)
        self.treev_sideboard.column("3", width=40, minwidth=40, anchor='se')

        # Set up deck and card data labels in main window
        self.deck_label = ttk.Label(window, text='Deck Details:')
        # self.deck_label = ttk.Label(window, background="white", text = 'Deck Details:')        
        self.deck_label.place(x=20, y=500)  # , width = 150, height = 30)
        self.ramp_label = ttk.Label(window, text='Ramp Cards:')
        self.ramp_label.place(x=20, y=530)  # , width = 150, height = 30)
        self.broad_label = ttk.Label(window, text="Non-Target 'Broad' Cards:")
        self.broad_label.place(x=20, y=560)
        self.target_label = ttk.Label(window, text='Target Cards:')
        self.target_label.place(x=20, y=585)
        self.etb_label = ttk.Label(window, text='Enter the Battlefield effect Cards:')
        self.etb_label.place(x=20, y=610)
        self.draw_label = ttk.Label(window, text='Card Draw Cards:')
        self.draw_label.place(x=20, y=635)
        self.avg_cmc_label = ttk.Label(window, text='Avg CMC:')
        self.avg_cmc_label.place(x=20, y=660)

        # 2nd Column of Labels
        self.commander_label = ttk.Label(window, text='Commander: ')
        self.commander_label.place(x=410, y=420)
        self.clr_id_label = ttk.Label(window, text='Colour ID: ')
        self.clr_id_label.place(x=410, y=450)
        self.commander_cmc_label = ttk.Label(window, text='Commander Mana Cost: ')
        self.commander_cmc_label.place(x=410, y=475)
        self.deck_tier_label = ttk.Label(window, text='Deck Tier: ')
        self.deck_tier_label.place(x=410, y=500)
        self.land_label = ttk.Label(window, text='# of Lands: ')
        self.land_label.place(x=410, y=525)
        self.deck_ID_label = ttk.Label(window, text='Deck ID: ')
        self.deck_ID_label.place(x=410, y=550)
        self.deck_location_label = ttk.Label(window, text='Deck Location: ')
        self.deck_location_label.place(x=410, y=575)
        self.status_label = ttk.Label(window, text='Deck Status: ')
        self.status_label.place(x=410, y=600)
        ## Placeholder Labels for Partner Commander, if applicable
        self.partner_label = ttk.Label(window, text='')
        self.partner_label.place(x=410, y=625)
        self.prtnr_clr_label = ttk.Label(window, text='')
        self.prtnr_clr_label.place(x=410, y=650)
        self.partner_cmc_label = ttk.Label(window, text='')
        self.partner_cmc_label.place(x=410, y=675)

        ## Update Card Quantity
        self.update_Qty_label = ttk.Label(root, text='Adjust Qty:')
        self.update_Qty_label.place(x=1220, y=380)  # , width = 150, height = 30)
        self.card_qty = StringVar()  ## or "" ?
        self.card_qtybox = Entry(root, textvariable=self.card_qty)
        self.card_qtybox.place(x=1290, y=380, width=30)

        ### BUTTONS ###
        self.move_to_sideboard = Button(root, image=movetosideboardbutton, command=self.bench_selected, borderwidth=0)
        self.move_to_sideboard.place(x=945, y=370)  # , width = 120, height = 30)
        self.remove_from_deck = Button(root, image=removeselectedbutton, command=self.remove_selected_from_main,
                                       borderwidth=0)
        self.remove_from_deck.place(x=1075, y=370)  # , width = 120, height = 30)
        self.move_to_deck = Button(root, image=addtodeckbutton, command=self.add_selected, borderwidth=0)
        self.move_to_deck.place(x=945, y=650)  # , width = 120, height = 30)
        self.remove_from_sideboard = Button(root, image=removeselectedbutton, command=self.remove_selected_from_sb,
                                            borderwidth=0)
        self.remove_from_sideboard.place(x=1075, y=650)  # , width = 120, height = 30)
        self.show_deck_list = Button(root, image=loaddeckbutton, command=self.open_deck, borderwidth=0)
        self.show_deck_list.place(x=10, y=450)  # , width = 120, height = 30)
        self.show_deck_meta = Button(root, image=deckdetailsbutton, command=self.show_deck_details, borderwidth=0)
        self.show_deck_meta.place(x=140, y=450)  # , width = 120, height = 30)
        self.show_inv_search = Button(root, image=inventorybutton, command=self.hide_deck_list, borderwidth=0)
        self.show_inv_search.place(x=270, y=450)  # , width = 120, height = 30)
        self.save_deck_button = Button(root, image=savedeckbutton, command=self.save_deck, borderwidth=0)
        self.save_deck_button.place(x=810, y=360)  # , width = 120, height = 30)
        self.prom_button = Button(root, image=newcommanderbutton, command=self.new_commander, borderwidth=0)
        self.prom_button.place(x=410, y=360)  # , width = 120, height = 30)
        self.partner_button = Button(root, image=partnerbutton, command=self.new_partner, borderwidth=0)
        self.partner_button.place(x=530, y=360)
        self.new_deck_button = Button(root, image=newdeckbutton, command=self.new_deck, borderwidth=0)
        self.new_deck_button.place(x=680, y=360)  # , width = 120, height = 30)

        ### MENU ###
        my_menu = Menu(window)
        window.config(menu=my_menu)

        file_menu = Menu(my_menu)
        my_menu.add_cascade(label="Deck", menu=file_menu)
        file_menu.add_command(label="New", command=self.new_deck)
        file_menu.add_separator()
        file_menu.add_command(label="Show Details", command=self.show_deck_details)
        file_menu.add_command(label="Show Inventory", command=self.hide_deck_list)
        file_menu.add_separator()
        file_menu.add_command(label="Open", command=self.open_deck)
        file_menu.add_command(label="Save", command=self.save_deck)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.destroy)

        import_menu = Menu(my_menu)
        my_menu.add_cascade(label="Import", menu=import_menu)
        import_menu.add_command(label="Clear Inventory", command=self.clear_inventory_gui)
        import_menu.add_command(label="Inventory", command=self.import_inventory_gui)
        import_menu.add_command(label="Append CSV to inventory", command=self.append_inventory_gui)
        import_menu.add_separator()
        import_menu.add_command(label="JSON Data", command=self.import_json_gui)

    def fill_decklist(self):
        # Populate the list of decks to load at initialization , this is called in mtg_main.py        
        mtg_sql.cur.execute("SELECT Deck_Name, Colour_ID FROM All_Decks")
        deck_names = mtg_sql.cur.fetchall()
        for deck in deck_names:
            self.treev_deck_list.insert('', 'end', text=deck[0], values=(deck[0], deck[1]))

    """ INITIALIZATION AND GUI BUILDING END """

    """ SHOW / HIDE FRAMES START """

    def show_deck_details(self):
        self.deck_details.lift()
        self.deck_select.lower()
        self.search_results.lower()
        self.card_finder.lower()

    def open_deck(self):
        self.search_results.lower()
        self.deck_details.lower()
        self.card_finder.lower()
        self.deck_select.lift()

    def show_deck_list(self):
        # deck_select.configure(visible='True')
        self.search_results.lower()
        self.deck_details.lower()
        self.card_finder.lower()
        self.deck_select.lift()

    def hide_deck_list(self):
        # deck_select.configure(visible='False')
        self.card_finder.lift()
        self.deck_select.lower()
        self.search_results.lower()
        self.deck_details.lower()

    """ SHOW / HIDE FRAMES END """

    """ BINDING & EVENTS START """

    def set_event_bindings(self):
        self.treev_maindeck.bind('<ButtonRelease-1>', self.main_deck_Click)
        self.treev_sideboard.bind('<ButtonRelease-1>', self.side_board_Click)
        self.treev_deck_list.bind('<ButtonRelease-1>', self.deck_select_Click)
        self.treev_results.bind('<ButtonRelease-1>', self.search_results_Click)
        self.card_qtybox.bind('<Return>', self.update_card_qty)
        self.decknotesbox.bind('<Return>', self.update_decknotes)
        self.decktablebox.bind('<Return>', self.update_decktable)
        self.decklocationbox.bind('<Return>', self.update_decklocation)
        self.deckidbox.bind('<Return>', self.update_deckid)
        self.decknamebox.bind('<Return>', self.update_deckname)
        self.filter_name_box.bind('<Return>', self.filter_results)

    def search_results_Click(self, event):
        """Checks which table the data for the selected card is in and displays preview image of the card """
        # for item in self.treev_results.selection():
        #     item_text = self.treev_results.get(item)
        for item in self.treev_results.selection():
            item_text = self.treev_results.item(item, "values")

        if len(item_text) > 0:
            link2 = ""
            search_this = (item_text,)
            if "----" not in item_text[0]:
                if type(mtg_sql.check_cardref(item_text[0])) is tuple:
                    this_table = (mtg_sql.check_cardref(item_text[0])[0])
                else:
                    this_table = mtg_sql.check_cardref(item_text[0])

                if this_table == "Face_Cards_Condensed":
                    srch_name = (item_text[0].split("//")[0].strip(),)
                    mtg_sql.cur.execute("SELECT Flip_Name from Face_Cards_Condensed WHERE Name=?", srch_name)
                    flip_name = mtg_sql.cur.fetchone()
                    mtg_sql.cur.execute("SELECT Image_URL from Face_Cards_Condensed WHERE Name=?", flip_name)
                    link2 = mtg_sql.cur.fetchone()[0]
                else:
                    srch_name = (item_text[0],)

                # print ("SEARCHING CARD TYPE.. ", srch_name)
                mtg_sql.cur.execute(
                    "SELECT Image_URL, ETB, Draw, Target, Broad, Ramp from " + this_table + " WHERE Name=?", srch_name)
                pic_url = mtg_sql.cur.fetchone()

                try:
                    link = pic_url[0]
                except Exception as e:
                    link = ""
                    print("Exception encountered in search_results_Click on link = pic_url[0] ", e)
                response = requests.get(link)
                img_data = response.content
                img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                img = img._PhotoImage__photo.subsample(2)  ## Zoom out by 2, works okay

                ## Preview the card - I believe by default the edition will tend to be off the latest set
                panel = ttk.Label(root, image=img)
                panel.image = img
                panel.place(x=410, y=20, width=244, height=340)
                if this_table == "Face_Cards_Condensed":
                    response = requests.get(link2)
                    img_data = response.content
                    img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                    img = img._PhotoImage__photo.subsample(2)

                    panel = ttk.Label(root, image=img)
                    panel.image = img
                    panel.place(x=654, y=20, width=244, height=340)
                else:
                    panel = ttk.Label(root)
                    panel.place(x=654, y=20, width=244, height=340)
                self.current_card = item_text[0]

    def deck_select_Click(self, event):
        for item in self.treev_deck_list.selection():
            item_text = self.treev_deck_list.item(item, "values")
            # print (item_text[0]) # name of the deck I clicked on
        self.close_deck()
        search_this = (item_text[0],)
        # print (item_text[0])
        mtg_sql.cur.execute("""SELECT Deck_list FROM All_Decks WHERE Deck_Name =?""", search_this)
        to_load = mtg_sql.cur.fetchone()
        # print (to_load)
        # try:
        #     self.load_deck(to_load[0])
        # except Exception as e:
        #     print ("Encountered error on deck selection ", e)
        if to_load is None:
            print("to_load is Null")
        else:
            self.deck_table = (to_load[0])
            self.load_deck(to_load[0])

    def main_deck_Click(self, event):
        item_iid = self.treev_maindeck.selection()[0]
        parent_iid = self.treev_maindeck.parent(item_iid)

        for item in self.treev_maindeck.selection():
            item_text = self.treev_maindeck.item(item, "values")

        # Fetch the link to the card image for the selected card (main card list for opened deck) 
        if "----" not in item_text[0]:
            if type(mtg_sql.check_cardref(item_text[0])) is tuple:
                this_table = (mtg_sql.check_cardref(item_text[0])[0])
            else:
                this_table = mtg_sql.check_cardref(item_text[0])
            # print (item_text[0]," found in ", this_table)
            if this_table == "Face_Cards_Condensed":
                srch_name = (item_text[0].split("//")[0].strip(),)
                mtg_sql.cur.execute("SELECT Flip_Name from Face_Cards_Condensed WHERE Name=?", srch_name)
                flip_name = mtg_sql.cur.fetchone()
                mtg_sql.cur.execute("SELECT Image_URL from Face_Cards_Condensed WHERE Name=?", flip_name)
                link2 = mtg_sql.cur.fetchone()[0]
            else:
                srch_name = (item_text[0],)

            # print ("SEARCHING CARD TYPE.. ", srch_name)
            mtg_sql.cur.execute(
                "SELECT Image_URL, ETB, Draw, Target, Broad, Ramp  from " + this_table + " WHERE Name=?", srch_name)
            pic_url = mtg_sql.cur.fetchone()

            try:
                link = pic_url[0]
            except Exception as e:
                link = ""
                print("Exception encountered in main_deck_Click on link = pic_url[0] ", e)

            response = requests.get(link)
            img_data = response.content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
            img = img._PhotoImage__photo.subsample(2)  ## Zoom out by 2, works okay

            ## Preview the card - I believe by default the edition will tend to be off the latest set
            panel = ttk.Label(root, image=img)
            panel.image = img
            panel.place(x=410, y=20, width=244, height=340)
            if this_table == "Face_Cards_Condensed":
                response = requests.get(link2)
                img_data = response.content
                img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                img = img._PhotoImage__photo.subsample(2)

                panel = ttk.Label(root, image=img)
                panel.image = img
                panel.place(x=654, y=20, width=244, height=340)
            else:
                panel = ttk.Label(root)
                panel.place(x=654, y=20, width=244, height=340)
            self.current_card = item_text[0]
            self.card_qty = item_text[2]
            self.card_qtybox.delete(0, END)
            self.card_qtybox.insert(0, self.card_qty)

            ## Count all card types in main deck and sideboard and count all mana symbols in main deck only
            get_all_counts = ()
            get_all_counts = self.count_cards()
            self.show_pie_chart()

    def update_card_qty(self, event):
        print("update card qty to ", self.card_qtybox.get())
        selected = self.treev_maindeck.focus()
        item_text = self.treev_maindeck.item(selected, "values")
        self.treev_maindeck.item(selected, text="", values=(item_text[0], item_text[1], self.card_qtybox.get()))

    def update_decknotes(self, event):
        self.deck_notes = self.decknotesbox.get()
        print("Deck notes: ", self.deck_notes)

    def update_decktable(self, event):
        self.deck_table = self.decktablebox.get()
        print("Deck table updated: ", self.deck_table)

    def update_decklocation(self, event):
        self.decklocation = self.decklocationbox.get()
        self.deck_location_label.configure(text='Deck Location: ' + self.decklocation)
        print("Deck location updated: ", self.decklocation)

    def update_deckid(self, event):
        self.deck_id = self.deckidbox.get()
        self.deck_ID_label.configure(text='Deck ID: ' + self.deck_id)
        print("Deck ID updated: ", self.deck_id)

    def update_deckname(self, event):
        self.deck_name = self.decknamebox.get()
        self.deck_label.configure(text='Deck Name: ' + self.deck_name)
        print("Deck Name updated: ", self.deck_name)

    def get_deck_tier(self, event):
        print("Current deck tier: ", self.current_tier)
        self.current_tier = self.deck_tier.get()
        self.deck_tier_label.configure(text='Deck Tier: ' + self.current_tier)

    def get_deck_status(self, event):
        print("Current deck status: ", self.current_status)
        self.current_status = self.deckstatus.get()
        self.status_label.configure(text='Deck Status: ' + self.current_status)

    def side_board_Click(self, event):
        for item in self.treev_sideboard.selection():
            item_text = self.treev_sideboard.item(item, "values")

        if "----" not in item_text[0]:
            # Fetch the link to the card image for the selected card (main card list for opened deck) 
            # print ("Sideboard click event, no '----' detected: ",item_text[0])
            if type(mtg_sql.check_cardref(item_text[0])) is tuple:
                this_table = (mtg_sql.check_cardref(item_text[0])[0])
                # print ("SEARCHING TABLE: ",this_table)
            else:
                this_table = mtg_sql.check_cardref(item_text[0])

            if this_table == "Face_Cards_Condensed":
                srch_name = (item_text[0].split("//")[0].strip(),)
                mtg_sql.cur.execute("SELECT Flip_Name from Face_Cards_Condensed WHERE Name=?", srch_name)
                flip_name = mtg_sql.cur.fetchone()
                mtg_sql.cur.execute("SELECT Image_URL from Face_Cards_Condensed WHERE Name=?", flip_name)
                link2 = mtg_sql.cur.fetchone()[0]

            else:
                srch_name = (item_text[0],)

            mtg_sql.cur.execute(
                "SELECT Image_URL, ETB, Draw, Target, Broad, Ramp  from " + this_table + " WHERE Name=?", srch_name)
            pic_url = mtg_sql.cur.fetchone()
            try:
                link = pic_url[0]
            except Exception as e:
                # link = stored_link
                print("Exception encountered in side_board_Click on link = pic_url[0] ", e)

            response = requests.get(link)
            img_data = response.content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
            img = img._PhotoImage__photo.subsample(2)  ## Zoom out by 2, works okay

            ## Preview the card - I believe by default the edition will tend to be off the latest set
            panel = ttk.Label(root, image=img)
            panel.image = img
            panel.place(x=410, y=20, width=244, height=340)
            # stored_link = link
            if this_table == "Face_Cards_Condensed":
                response = requests.get(link2)
                img_data = response.content
                img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                img = img._PhotoImage__photo.subsample(2)

                panel = ttk.Label(root, image=img)
                panel.image = img
                panel.place(x=654, y=20, width=244, height=340)
            else:
                panel = ttk.Label(root)
                panel.place(x=654, y=20, width=244, height=340)
            self.current_card = item_text[0]

            ## Count all card types in main deck and sideboard and count all mana symbols in main deck only
            get_all_counts = ()
            get_all_counts = self.count_cards()

    def filter_results(self, event):
        ### Clear the existing search results
        self.prep_search_result_list()

        ### SEARCH SINGLE SIDED CARD TABLE FIRST ###    
        if len(self.sql_inner_join) > 0:
            self.sql_search_statement = "SELECT Cards_Condensed.Name, Cards_Condensed.Mana_Cost, Cards_Condensed.Card_Type, Creatures.Power, Creatures.Toughness FROM Cards_Condensed INNER JOIN Creatures ON Creatures.Name=Cards_Condensed.Name WHERE " + self.sql_search_params + " AND " + self.sql_inner_join
        else:
            self.sql_search_statement = "SELECT Name, Mana_Cost, Card_Type FROM Cards_Condensed WHERE " + self.sql_search_params

        mtg_sql.cur.execute(self.sql_search_statement)
        results = mtg_sql.cur.fetchall()
        search_result_counter = 0
        for items in results:
            if self.filter_name.get().lower() in items[0].lower():
                if '----' not in items[0]:
                    search_result_counter += 1

                    if 'Creature' in items[2]:
                        self.treev_results.insert("Crt", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Instant' in items[2]:
                        self.treev_results.insert("Inst", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Sorcery' in items[2]:
                        self.treev_results.insert("Sorc", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Artifact' in items[2]:
                        self.treev_results.insert("Arts", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Enchantment' in items[2]:
                        self.treev_results.insert("Ench", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Planeswalker' in items[2]:
                        self.treev_results.insert("Plane", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Land' in items[2]:
                        self.treev_results.insert("Lnd", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    else:
                        self.treev_results.insert("", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
        # print ("From Cards Table: ", results)

        ### SEARCH FACE_CARD TABLE AFTER AND ADD RESULTS ###    
        if len(self.sql_inner_join) > 0:
            self.sql_search_statement = "SELECT Face_Cards_Condensed.Name, Face_Cards_Condensed.Mana_Cost, Face_Cards_Condensed.Card_Type, Creatures.Power, Creatures.Toughness FROM Face_Cards_Condensed INNER JOIN Creatures ON Creatures.Name=Face_Cards_Condensed.Name WHERE " + self.sql_search_params + " AND " + self.sql_inner_join
        else:
            self.sql_search_statement = "SELECT Name, Mana_Cost, Card_Type FROM Face_Cards_Condensed WHERE " + self.sql_search_params

        mtg_sql.cur.execute(self.sql_search_statement)
        results = mtg_sql.cur.fetchall()

        for items in results:
            if self.filter_name.get().lower() in items[0].lower():
                if '----' not in items[0]:
                    search_result_counter += 1
                    if 'Creature' in items[2]:
                        self.treev_results.insert("Crt", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Instant' in items[2]:
                        self.treev_results.insert("Inst", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Sorcery' in items[2]:
                        self.treev_results.insert("Sorc", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Artifact' in items[2]:
                        self.treev_results.insert("Arts", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Enchantment' in items[2]:
                        self.treev_results.insert("Ench", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Planeswalker' in items[2]:
                        self.treev_results.insert("Plane", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Land' in items[2]:
                        self.treev_results.insert("Lnd", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    else:
                        self.treev_results.insert("", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))

    def import_inventory_file(self, open_file):
        print("starting inventory import..")
        begin_inv_time = time.time()
        importcount = 0
        with open(open_file, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            next(csv_reader)
            for line in csv_reader:
                importcount += 1
                """# basically using the try block for weird things like Bösium 'BÃ¶sium' Strip
                https://www.compart.com/en/unicode/U+00F6#:~:text=Unicode%20Character%20%E2%80%9C%C3%B6%E2%80%9D%20(U%2B00F6)
                U+00F6   or U+00D6   ö:  '\xf6'    û: '\xfb'     'Ã¢'
                    """
                try:
                    search_this = json_load.fix_text(line[2])
                    mtg_main.scryfall_search_exact(search_this)
                except Exception as e:
                    print("exception error occured importing inventory for ", line[2], "  ", e)
                    importcount -= 1

        # print(f'{importignorecount} records skipped')
        mtg_sql.db.commit()
        end_inv_time = time.time()
        run_time = end_inv_time - begin_inv_time
        print(f'{importcount} records added to Cards & Face_Cards Tables')
        print("Import Runtime:", round(run_time, 2), " seconds")
        # self.labelComplete = Label(window, text="IMPORT COMPLETE",font=("Arial", 25))
        # self.labelComplete.place(x = 410, y = 450)
        messagebox.showinfo("showinfo", "Import Complete")

    def append_inventory_gui(self, open_file):
        inv_filename = filedialog.askopenfilename(initialdir=data_folder, title="Import Deckbox Inventory",
                                                  filetypes=(("Comma Separated Values", "*.csv"), ("All Files", "*.*")))
        if len(inv_filename) > 0:
            self.import_inventory_file(inv_filename)

    def import_inventory_gui(self):
        inv_filename = filedialog.askopenfilename(initialdir=data_folder, title="Import Deckbox Inventory",
                                                  filetypes=(("Comma Separated Values", "*.csv"), ("All Files", "*.*")))
        if len(inv_filename) > 0:
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Face_Cards_Condensed'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Face_Cards'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Cards'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Cards_Condensed'")
            mtg_sql.check_all_tables()
            self.import_inventory_file(inv_filename)

    def import_json_gui(self):
        json_filename = filedialog.askopenfilename(initialdir=data_folder, title="Import JSON Data",
                                                   filetypes=(("JSON Data file", "*.json"), ("All Files", "*.*")))

        if len(json_filename) > 0:
            begin_time = time.time()
            print("Starting JSON import..", time.localtime(begin_time))
            counter = 0
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Cardref'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Grandtable'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableCondensed'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplit'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'GrandtableSplitCondensed'")
            mtg_sql.check_all_tables()

            with open(json_filename, encoding='utf-8') as f:
                data = json_load.json.load(f)
            for card in data:  # ['name']:
                if card['lang'] == "en":
                    try:
                        counter += 1
                        json_load.select_case_layout_JSON(card['layout'], card)
                    except Exception as e:
                        counter -= 1
                        print("Encountered exception accessing ", card['name'], card['lang'], " - import_json_gui(),",
                              "  ", e)
            print(counter, " records found")
            end_time = time.time()
            run_time = end_time - begin_time
            # print (time.localtime(end_time))
            print("Import runtime:", round(run_time, 3), " seconds")
            # self.labelComplete = Label(window, text="IMPORT COMPLETE",font=("Arial", 25))
            # self.labelComplete.place(x = 410, y = 450)
            messagebox.showinfo("showinfo", "Import Complete")

    def clear_inventory_gui(self):
        if (messagebox.askquestion("askquestion", "Clear Inventory, are you sure?")) == 1:
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Face_Cards_Condensed'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Face_Cards'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Cards'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Cards_Condensed'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'All_Decks'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Creatures'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Spells'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Planeswalkers'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Lands'")
            mtg_sql.cur.execute("DROP TABLE IF EXISTS 'Test_Matches'")
            mtg_sql.check_all_tables()

    """ BINDING & EVENTS END """

    """ GUI FUNCTIONS AND PROCESSING START """

    def show_pie_chart(self):
        ## clear the existing figure
        plt.close('all')
        plt.clf()

        fig = plt.figure(figsize=(2, 2), dpi=100)
        # fig.set_size_inches(2, 2)

        # Data to plot, only show labels for colors included in the deck
        if self.sum_white > 0:
            white_label = self.sum_white
        else:
            white_label = ""
        if self.sum_blue > 0:
            blue_label = self.sum_blue
        else:
            blue_label = ""
        if self.sum_black > 0:
            black_label = self.sum_black
        else:
            black_label = ""
        if self.sum_red > 0:
            red_label = self.sum_red
        else:
            red_label = ""
        if self.sum_green > 0:
            green_label = self.sum_green
        else:
            green_label = ""

        pie_labels = white_label, blue_label, black_label, red_label, green_label
        pie_sizes = [self.sum_white, self.sum_blue, self.sum_black, self.sum_red, self.sum_green]
        pie_colors = ['white', 'blue', 'black', 'red', 'green']
        # explode = (0, 0, 0, 0, 0)  # explode 1st slice (Ireland), makes it more prominent

        # Plot pie chart
        try:
            plt.pie(pie_sizes, colors=pie_colors, labels=pie_labels, normalize=False, shadow=True, startangle=90,
                    wedgeprops={'linewidth': 2, 'linestyle': 'solid', 'antialiased': True})
        except:
            plt.pie(pie_sizes, colors=pie_colors, labels=pie_labels, shadow=True, startangle=90,
                    wedgeprops={'linewidth': 2, 'linestyle': 'solid', 'antialiased': True})
        # plt.pie(pie_sizes, explode=explode, colors=pie_colors, autopct='%1.1f%%', shadow=True, startangle=0)
        plt.axis('equal')  # creates the pie chart like a circle
        canvasbar = FigureCanvasTkAgg(fig, master=root)
        canvasbar.draw()
        canvasbar.get_tk_widget().place(x=800, y=530, anchor=CENTER)  # show the barchart on the ouput window

    def show_certain_decks(self):
        ### COLOUR ID ###
        self.search_colours = ()
        if self.deck_white.get() == 1: self.search_colours = self.search_colours + ('W',)
        if self.deck_blue.get() == 1: self.search_colours = self.search_colours + ('U',)
        if self.deck_black.get() == 1: self.search_colours = self.search_colours + ('B',)
        if self.deck_red.get() == 1: self.search_colours = self.search_colours + ('R',)
        if self.deck_green.get() == 1: self.search_colours = self.search_colours + ('G',)
        if self.deck_colourless.get() == 1: self.search_colours = self.search_colours + ('C',)
        sql_search_params = ""
        if len(self.search_colours) > 0:
            sql_search_params = "("
            colourscounter = 0
            for colours in self.search_colours:
                colourscounter += 1
                if colourscounter > 1:
                    sql_search_params = sql_search_params + "AND Colour_ID LIKE '%" + colours + "%' "
                else:
                    sql_search_params = sql_search_params + "Colour_ID LIKE '%" + colours + "%' "
            sql_search_params = sql_search_params + ")"

            ### Clear the existing list of decks and will repopulate ###        
            self.treev_deck_list.delete(*self.treev_deck_list.get_children())
            sql_statement = "SELECT Deck_Name, Colour_ID FROM All_Decks WHERE " + sql_search_params
            print(sql_statement)
            if len(sql_statement) > 4:
                mtg_sql.cur.execute(sql_statement)
                deck_names = mtg_sql.cur.fetchall()
                for deck in deck_names:
                    self.treev_deck_list.insert('', 'end', text=deck[0], values=(deck[0], deck[1]))
        else:
            ## No colours are selected, just show all decks
            self.treev_deck_list.delete(*self.treev_deck_list.get_children())
            self.fill_decklist()

    def count_cards(self):
        creature_count = 0
        instant_count = 0
        sorcery_count = 0
        artifact_count = 0
        enchantment_count = 0
        planeswalker_count = 0
        lands_count = 0
        sb_creature_count = 0
        sb_instant_count = 0
        sb_sorcery_count = 0
        sb_artifact_count = 0
        sb_enchantment_count = 0
        sb_planeswalker_count = 0
        sb_lands_count = 0

        # Count all children in Main deck Treeview
        for allchilds in self.get_all_children(self.treev_maindeck):
            cardtype = self.treev_maindeck.item(allchilds, "values")[1].lower()
            cardname = self.treev_maindeck.item(allchilds, "values")[0]
            if 'creature' in cardtype:
                creature_count += int(self.treev_maindeck.item(allchilds, "values")[2])
            elif 'instant' in cardtype:
                instant_count += int(self.treev_maindeck.item(allchilds, "values")[2])
            elif 'sorcery' in cardtype:
                sorcery_count += int(self.treev_maindeck.item(allchilds, "values")[2])
            elif 'artifact' in cardtype:
                artifact_count += int(self.treev_maindeck.item(allchilds, "values")[2])
            elif 'enchantment' in cardtype:
                enchantment_count += int(self.treev_maindeck.item(allchilds, "values")[2])
            elif 'planeswalker' in cardtype:
                planeswalker_count += int(self.treev_maindeck.item(allchilds, "values")[2])
            elif 'land' in cardtype:
                lands_count += int(self.treev_maindeck.item(allchilds, "values")[2])

            ### Check which table the card is in, and get the mana cost for all cards in the main deck only
            if "----" not in cardname:
                if type(mtg_sql.check_cardref(cardname)) is tuple:
                    this_table = (mtg_sql.check_cardref(cardname)[0])
                    # print ("SEARCHING TABLE: ",this_table)
                else:
                    this_table = mtg_sql.check_cardref(cardname)
                search_this = (cardname,)
                mtg_sql.cur.execute("SELECT Mana_cost FROM " + this_table + " WHERE Name=?", search_this)
                fetch = mtg_sql.cur.fetchone()
                if type(fetch) is tuple:
                    c_mana_cost = fetch[0]
                    self.total_mana_cost_string = self.total_mana_cost_string + c_mana_cost

        print("Total Main deck Mana cost: ", self.total_mana_cost_string)

        # Count all children in Sideboard Treeview
        for allchilds in self.get_all_children(self.treev_sideboard):
            cardtype = self.treev_sideboard.item(allchilds, "values")[1].lower()
            if 'creature' in cardtype:
                sb_creature_count += int(self.treev_sideboard.item(allchilds, "values")[2])
            elif 'instant' in cardtype:
                sb_instant_count += int(self.treev_sideboard.item(allchilds, "values")[2])
            elif 'sorcery' in cardtype:
                sb_sorcery_count += int(self.treev_sideboard.item(allchilds, "values")[2])
            elif 'artifact' in cardtype:
                sb_artifact_count += int(self.treev_sideboard.item(allchilds, "values")[2])
            elif 'enchantment' in cardtype:
                sb_enchantment_count += int(self.treev_sideboard.item(allchilds, "values")[2])
            elif 'planeswalker' in cardtype:
                sb_planeswalker_count += int(self.treev_sideboard.item(allchilds, "values")[2])
            elif 'land' in cardtype:
                sb_lands_count += int(self.treev_sideboard.item(allchilds, "values")[2])

        # Update the card type headings in main table
        item_text = self.treev_maindeck.item("Crt", "values")
        self.treev_maindeck.item('Crt', text="", values=(item_text[0], item_text[1], creature_count))
        item_text = self.treev_maindeck.item('Inst', "values")
        self.treev_maindeck.item('Inst', text="", values=(item_text[0], item_text[1], instant_count))
        item_text = self.treev_maindeck.item('Sorc', "values")
        self.treev_maindeck.item('Sorc', text="", values=(item_text[0], item_text[1], sorcery_count))
        item_text = self.treev_maindeck.item('Arts', "values")
        self.treev_maindeck.item('Arts', text="", values=(item_text[0], item_text[1], artifact_count))
        item_text = self.treev_maindeck.item('Ench', "values")
        self.treev_maindeck.item('Ench', text="", values=(item_text[0], item_text[1], enchantment_count))
        item_text = self.treev_maindeck.item('Plane', "values")
        self.treev_maindeck.item('Plane', text="", values=(item_text[0], item_text[1], planeswalker_count))
        item_text = self.treev_maindeck.item('Lnd', "values")
        self.treev_maindeck.item('Lnd', text="", values=(item_text[0], item_text[1], lands_count))

        # Update the card type headings in sideboard table        
        item_text = self.treev_sideboard.item("Crt", "values")
        self.treev_sideboard.item('Crt', text="", values=(item_text[0], item_text[1], sb_creature_count))
        item_text = self.treev_sideboard.item('Inst', "values")
        self.treev_sideboard.item('Inst', text="", values=(item_text[0], item_text[1], sb_instant_count))
        item_text = self.treev_sideboard.item('Sorc', "values")
        self.treev_sideboard.item('Sorc', text="", values=(item_text[0], item_text[1], sb_sorcery_count))
        item_text = self.treev_sideboard.item('Arts', "values")
        self.treev_sideboard.item('Arts', text="", values=(item_text[0], item_text[1], sb_artifact_count))
        item_text = self.treev_sideboard.item('Ench', "values")
        self.treev_sideboard.item('Ench', text="", values=(item_text[0], item_text[1], sb_enchantment_count))
        item_text = self.treev_sideboard.item('Plane', "values")
        self.treev_sideboard.item('Plane', text="", values=(item_text[0], item_text[1], sb_planeswalker_count))
        item_text = self.treev_sideboard.item('Lnd', "values")
        self.treev_sideboard.item('Lnd', text="", values=(item_text[0], item_text[1], sb_lands_count))

        (
        self.sum_white, self.sum_blue, self.sum_black, self.sum_red, self.sum_green) = mtg_regex.regex_get_mana_symbols(
            self.total_mana_cost_string)
        self.show_pie_chart()
        self.total_mana_cost_string = ""

        return (creature_count, instant_count, sorcery_count, artifact_count, enchantment_count, planeswalker_count,
                lands_count,
                sb_creature_count, sb_instant_count, sb_sorcery_count, sb_artifact_count, sb_enchantment_count,
                sb_planeswalker_count, sb_lands_count)

    def search_name(self):
        """Either execute a direct SQL SELECT statement if specified or aggregate all the other search parameters together and get the appropriate SQL statement """

        self.sql_search_params = ""
        if len(self.sql_direct.get()) > 0:
            ### Clear the existing search results
            self.prep_search_result_list()
            self.sql_search_params = self.sql_direct.get()
            self.sql_search_statement = "SELECT Name, Mana_Cost, Card_Type FROM " + self.table_select.get() + " WHERE " + self.sql_direct.get()
            # print (sql_search_statement)
            mtg_sql.cur.execute(self.sql_search_statement)
            results = mtg_sql.cur.fetchall()

            search_result_counter = 0
            for items in results:
                if '----' not in items[0]:
                    search_result_counter += 1
                    if 'Creature' in items[2]:
                        self.treev_results.insert("Crt", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Instant' in items[2]:
                        self.treev_results.insert("Inst", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Sorcery' in items[2]:
                        self.treev_results.insert("Sorc", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Artifact' in items[2]:
                        self.treev_results.insert("Arts", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Enchantment' in items[2]:
                        self.treev_results.insert("Ench", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Planeswalker' in items[2]:
                        self.treev_results.insert("Plane", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Land' in items[2]:
                        self.treev_results.insert("Lnd", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    else:
                        self.treev_results.insert("", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))

            # print ("From Cards Table: ", results)            
        else:
            if len(self.subtype.get()) > 0:
                self.sql_search_params = self.sql_search_params + "Card_Type LIKE '%" + self.subtype.get() + "%' AND "
                # print ("Sub Type: ", self.subtype.get())
            if len(self.cardrules.get()) > 0:
                self.sql_search_params = self.sql_search_params + "Oracle_Text LIKE '%" + self.cardrules.get() + "%' AND "
                # print ("Card Rules: ", self.cardrules.get())
            if len(self.cardname.get()) > 0:
                self.sql_search_params = self.sql_search_params + "Name LIKE '%" + self.cardname.get() + "%' AND "
                # print ("Card Name: ", self.cardname.get())
            if len(self.cardcmc.get()) > 0:
                self.cmcadjust = self.cmc_approx.get()
                self.sql_search_params = self.sql_search_params + "CMC " + self.cmcadjust + self.cardcmc.get() + " AND "
                # print ("Card CMC: ", self.cmcadjust, self.cardcmc.get())

            values = [self.cardtype.get(idx) for idx in self.cardtype.curselection()]
            # print (len(self.cardtype.curselection()), " selected card types")   ## or len(values)
            typevaluescounter = 0
            if len(values) > 0:
                self.sql_search_params = self.sql_search_params + "("
                for ctypes in values:
                    typevaluescounter += 1
                    if typevaluescounter > 1:
                        self.sql_search_params = self.sql_search_params + "OR Card_type LIKE '%" + ctypes + "%' "
                    else:
                        self.sql_search_params = self.sql_search_params + "Card_type LIKE '%" + ctypes + "%' "
                self.sql_search_params = self.sql_search_params.strip()
                self.sql_search_params = self.sql_search_params + ")"
            # else:
            #     print (', '.join(values))

            ### COLOUR ID START ###
            self.search_colours = ()
            self.exclude_colours = ()
            """Creating a search_colours tuple to find cards within that colour identity, and an exclude tuple
            to remove stuff that isn't in that colour id  -  Colourless cards can be used with any colour so they aren't added to
            exclude tuple"""
            if self.inc_white.get() == 1:
                self.search_colours = self.search_colours + ('W',)
            else:
                self.exclude_colours = self.exclude_colours + ('W',)
            if self.inc_blue.get() == 1:
                self.search_colours = self.search_colours + ('U',)
            else:
                self.exclude_colours = self.exclude_colours + ('U',)
            if self.inc_black.get() == 1:
                self.search_colours = self.search_colours + ('B',)
            else:
                self.exclude_colours = self.exclude_colours + ('B',)
            if self.inc_red.get() == 1:
                self.search_colours = self.search_colours + ('R',)
            else:
                self.exclude_colours = self.exclude_colours + ('R',)
            if self.inc_green.get() == 1:
                self.search_colours = self.search_colours + ('G',)
            else:
                self.exclude_colours = self.exclude_colours + ('G',)
            if self.inc_colourless.get() == 1: self.search_colours = self.search_colours + ('C',)

            if len(self.search_colours) > 0:
                if self.sql_search_params[-5:] == " AND ":
                    # Removes the additional 'AND' at the end of the statement if there is one
                    size = len(self.sql_search_params)
                    mod_string = self.sql_search_params[:size - 4]
                    self.sql_search_params = mod_string
                # print ("Search Colour ID: ", self.search_colours)
                self.sql_search_params = self.sql_search_params + " AND ("

                colourscounter = 0
                if self.exclusive_colour.get() == 1:
                    ##  This ignores the exclusion list and will only search for cards that match all selected colours
                    ## Searching Black and Green will give only cards that are Golgari

                    ## Iterate through inclusion list
                    for colours in self.search_colours:
                        colourscounter += 1
                        if colourscounter > 1:
                            self.sql_search_params = self.sql_search_params + "AND Colour_ID LIKE '%" + colours + "%' "
                        else:
                            self.sql_search_params = self.sql_search_params + "Colour_ID LIKE '%" + colours + "%' "
                    self.sql_search_params = self.sql_search_params + ")"

                    ## Iterate through exclusion list
                    if len(self.exclude_colours) > 0:
                        self.sql_search_params = self.sql_search_params + " AND ("
                        colourscounter = 0
                        for ex_colours in self.exclude_colours:
                            colourscounter += 1
                            if colourscounter > 1:
                                self.sql_search_params = self.sql_search_params + "AND Colour_ID NOT LIKE '%" + ex_colours + "%' "
                            else:
                                self.sql_search_params = self.sql_search_params + "Colour_ID NOT LIKE '%" + ex_colours + "%' "
                        self.sql_search_params = self.sql_search_params + ")"

                else:
                    ##  This will do OR searches instead of AND.  Will search for all cards that are WITHIN the colour identity  (not including colourless cards unless it is 'selected')
                    ## Searching Black and Green will give cards that are Golgari, Sultai, Abzan, .. WUBRG..etc
                    for colours in self.search_colours:
                        colourscounter += 1
                        if colourscounter > 1:
                            self.sql_search_params = self.sql_search_params + "OR Colour_ID LIKE '%" + colours + "%' "
                        else:
                            self.sql_search_params = self.sql_search_params + "Colour_ID LIKE '%" + colours + "%' "
                    self.sql_search_params = self.sql_search_params + ")"

                    # print ("len exclude colours: " ,len(self.exclude_colours) )
                    if len(self.exclude_colours) > 0:
                        self.sql_search_params = self.sql_search_params + " AND ("
                        colourscounter = 0
                        for ex_colours in self.exclude_colours:
                            colourscounter += 1
                            if colourscounter > 1:
                                self.sql_search_params = self.sql_search_params + "AND Colour_ID NOT LIKE '%" + ex_colours + "%' "
                            else:
                                self.sql_search_params = self.sql_search_params + "Colour_ID NOT LIKE '%" + ex_colours + "%' "
                        self.sql_search_params = self.sql_search_params + ")"
                        ### COLOUR ID END ###

            ### MISC Checkboxes ###
            if self.sql_search_params[-5:] == " AND ":
                # Removes the additional 'AND' at the end of the statement if there is one
                size = len(self.sql_search_params)
                mod_string = self.sql_search_params[:size - 4]
                self.sql_search_params = mod_string
            misc_count = 0

            if self.inc_ramp.get() == 1:
                misc_count += 1
                if len(self.sql_search_params) < 6:
                    self.sql_search_params = self.sql_search_params + "Ramp !='-'"
                else:
                    self.sql_search_params = self.sql_search_params + " AND Ramp !='-'"
            if self.inc_draw.get() == 1:
                if len(self.sql_search_params) < 6:
                    self.sql_search_params = self.sql_search_params + " Draw !='-'"
                else:
                    self.sql_search_params = self.sql_search_params + " AND Draw !='-'"
            if self.inc_target.get() == 1:
                if len(self.sql_search_params) < 6:
                    self.sql_search_params = self.sql_search_params + " Target !='-'"
                else:
                    self.sql_search_params = self.sql_search_params + " AND Target !='-'"
            if self.inc_etb.get() == 1:
                if len(self.sql_search_params) < 6:
                    self.sql_search_params = self.sql_search_params + " ETB !='-'"
                else:
                    self.sql_search_params = self.sql_search_params + " AND ETB !='-'"
            if self.inc_broad.get() == 1:
                if len(self.sql_search_params) < 6:
                    self.sql_search_params = self.sql_search_params + " Broad !='-'"
                else:
                    self.sql_search_params = self.sql_search_params + " AND Broad !='-'"
            if self.inc_legend.get() == 1:
                if len(self.sql_search_params) < 6:
                    self.sql_search_params = self.sql_search_params + " Legendary ='Yes'"
                else:
                    self.sql_search_params = self.sql_search_params + " AND Legendary ='Yes'"
                    ###  MISC Checkboxes ###

            if len(self.card_kw.get()) > 0:
                if self.sql_search_params[-5:] == " AND ":
                    # Removes the additional 'AND' at the end of the statement if there is one
                    size = len(self.sql_search_params)
                    mod_string = self.sql_search_params[:size - 4]
                    self.sql_search_params = mod_string
                keywords_list = str(self.card_kw.get()).split(" ")
                kwcounter = 0
                self.sql_search_params = self.sql_search_params + " AND ("

                for keyword in keywords_list:
                    kwcounter += 1
                    if kwcounter > 1:
                        self.sql_search_params = self.sql_search_params + "AND Keywords LIKE '%" + keyword + "%' "
                    else:
                        self.sql_search_params = self.sql_search_params + "Keywords LIKE '%" + keyword + "%' "
                self.sql_search_params = self.sql_search_params + ")"

            if len(self.cardpower.get()) > 0:
                self.poweradjust = self.power_approx.get()
                self.sql_inner_join = "Power " + self.poweradjust + self.cardpower.get()

            if len(self.cardtough.get()) > 0:
                self.toughadjust = self.tough_approx.get()
                if len(self.sql_inner_join) > 0:
                    self.sql_inner_join = self.sql_inner_join + " AND Toughness " + self.toughadjust + self.cardtough.get()
                else:
                    self.sql_inner_join = "Toughness " + self.toughadjust + self.cardtough.get()

            ###  Remove the starting/trailing "AND" at the end of the statement if there is one
            if self.sql_search_params[-5:] == " AND ":
                size = len(self.sql_search_params)
                mod_string = self.sql_search_params[:size - 5]
                self.sql_search_params = mod_string

            if self.sql_search_params[:5] == " AND ":
                mod_string = self.sql_search_params[4:]
                self.sql_search_params = mod_string

            ### Clear the existing search results
            self.prep_search_result_list()

            ### SEARCH SINGLE SIDED CARD TABLE FIRST ###    
            if len(self.sql_inner_join) > 0:
                print(self.sql_search_params)
                self.sql_search_statement = "SELECT Cards_Condensed.Name, Cards_Condensed.Mana_Cost, Cards_Condensed.Card_Type, Creatures.Power, Creatures.Toughness FROM Cards_Condensed INNER JOIN Creatures ON Creatures.Name=Cards_Condensed.Name WHERE " + self.sql_search_params + " AND " + self.sql_inner_join
            else:
                self.sql_search_statement = "SELECT Name, Mana_Cost, Card_Type FROM Cards_Condensed WHERE " + self.sql_search_params

            print(self.sql_search_statement)
            mtg_sql.cur.execute(self.sql_search_statement)
            results = mtg_sql.cur.fetchall()
            search_result_counter = 0
            for items in results:
                search_result_counter += 1
                if '----' not in items[0]:

                    if 'Creature' in items[2]:
                        self.treev_results.insert("Crt", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Instant' in items[2]:
                        self.treev_results.insert("Inst", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Sorcery' in items[2]:
                        self.treev_results.insert("Sorc", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Artifact' in items[2]:
                        self.treev_results.insert("Arts", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Enchantment' in items[2]:
                        self.treev_results.insert("Ench", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Planeswalker' in items[2]:
                        self.treev_results.insert("Plane", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Land' in items[2]:
                        self.treev_results.insert("Lnd", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    else:
                        self.treev_results.insert("", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
            # print ("From Cards Table: ", results)

            ### SEARCH FACE_CARD TABLE AFTER AND ADD RESULTS ###    
            if len(self.sql_inner_join) > 0:
                self.sql_search_statement = "SELECT Face_Cards_Condensed.Name, Face_Cards_Condensed.Mana_Cost, Face_Cards_Condensed.Card_Type, Creatures.Power, Creatures.Toughness FROM Face_Cards_Condensed INNER JOIN Creatures ON Creatures.Name=Face_Cards_Condensed.Name WHERE " + self.sql_search_params + " AND " + self.sql_inner_join
            else:
                self.sql_search_statement = "SELECT Name, Mana_Cost, Card_Type FROM Face_Cards_Condensed WHERE " + self.sql_search_params

            # print (self.sql_search_statement)
            mtg_sql.cur.execute(self.sql_search_statement)
            results = mtg_sql.cur.fetchall()

            for items in results:
                search_result_counter += 1
                # Now to figure out where to put that entry
                if '----' not in items[0]:

                    if 'Creature' in items[2]:
                        self.treev_results.insert("Crt", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Instant' in items[2]:
                        self.treev_results.insert("Inst", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Sorcery' in items[2]:
                        self.treev_results.insert("Sorc", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Artifact' in items[2]:
                        self.treev_results.insert("Arts", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Enchantment' in items[2]:
                        self.treev_results.insert("Ench", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Planeswalker' in items[2]:
                        self.treev_results.insert("Plane", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    elif 'Land' in items[2]:
                        self.treev_results.insert("Lnd", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
                    else:
                        self.treev_results.insert("", 'end', text="L" + str(search_result_counter),
                                                  values=(items[0], items[1], items[2]))
            # print ("From Face_Cards Table: ", results)

        self.deck_select.lower()
        self.card_finder.lower()
        self.search_results.lift()

    def sb_selected_from_results(self):
        x = self.treev_results.selection()
        main_listcounter = len(self.treev_sideboard.get_children())

        children = self.get_all_children(self.treev_sideboard)
        found_flag = False

        for record in x:
            main_listcounter += 1
            item_text = self.treev_results.item(record, "values")
            # Got the name, will add to deck if it doesn't already exist there 

            for childs in children:
                childname = self.treev_sideboard.item(childs, "values")[0].strip()
                # print (childname, item_text[0])
                if item_text[0] == childname:
                    # print ( item_text[0], self.treev_maindeck.item(childs,"values"))
                    print(childname, " already exists in main deck list")
                    found_flag = True
                    break

            if found_flag == True: break
            # Now to figure out where to put that entry, then see if it is already in there
            if 'Creature' in item_text[2]:
                self.treev_sideboard.insert("Crt", 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))
            elif 'Instant' in item_text[2]:
                self.treev_sideboard.insert("Inst", 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))
            elif 'Sorcery' in item_text[2]:
                self.treev_sideboard.insert("Sorc", 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))
            elif 'Artifact' in item_text[2]:
                self.treev_sideboard.insert("Arts", 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))
            elif 'Enchantment' in item_text[2]:
                self.treev_sideboard.insert("Ench", 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))
            elif 'Planeswalker' in item_text[2]:
                self.treev_sideboard.insert("Plane", 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))
            elif 'Land' in item_text[2]:
                self.treev_sideboard.insert("Lnd", 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))
            else:
                self.treev_sideboard.insert('', 'end', text="L" + str(main_listcounter),
                                            values=(item_text[0], item_text[2], 1))

    def get_all_children(self, tree, item=""):
        children = tree.get_children(item)
        for child in children:
            children += self.get_all_children(tree, child)
        return children

    def add_selected_from_results(self):
        x = self.treev_results.selection()
        main_listcounter = len(self.treev_maindeck.get_children())

        children = self.get_all_children(self.treev_maindeck)

        for record in x:
            found_flag = False
            main_listcounter += 1
            item_text = self.treev_results.item(record, "values")
            # Got the name, will add to deck if it doesn't already exist there 

            for childs in children:
                childname = self.treev_maindeck.item(childs, "values")[0].strip()
                # print (childname, item_text[0])
                if item_text[0] == childname:
                    # print ( item_text[0], self.treev_maindeck.item(childs,"values"))
                    print(childname, " already exists in main deck list")
                    found_flag = True
                    # break

            if found_flag == False:
                if "-----" not in item_text[0]:
                    # Now to figure out where to put that entry, then see if it is already in there
                    if 'Creature' in item_text[2]:
                        self.treev_maindeck.insert("Crt", 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))
                    elif 'Instant' in item_text[2]:
                        self.treev_maindeck.insert("Inst", 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))
                    elif 'Sorcery' in item_text[2]:
                        self.treev_maindeck.insert("Sorc", 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))
                    elif 'Artifact' in item_text[2]:
                        self.treev_maindeck.insert("Arts", 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))
                    elif 'Enchantment' in item_text[2]:
                        self.treev_maindeck.insert("Ench", 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))
                    elif 'Planeswalker' in item_text[2]:
                        self.treev_maindeck.insert("Plane", 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))
                    elif 'Land' in item_text[2]:
                        self.treev_maindeck.insert("Lnd", 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))
                    else:
                        self.treev_maindeck.insert('', 'end', text="L" + str(main_listcounter),
                                                   values=(item_text[0], item_text[2], 1))

    def add_selected(self):
        x = self.treev_sideboard.selection()
        main_listcounter = len(self.treev_maindeck.get_children())
        # print ("main deck number of items: ",main_listcounter)
        # print ("x: ",x)    
        for record in x:
            main_listcounter += 1
            # print (treev_sideboard.items[record][0])
            # print ("record[0]: ", record[0])
            item_text = self.treev_sideboard.item(record, "values")

            # Now to figure out where to put that entry
            if '----' in item_text[0]:
                # Ignoring all of the heading catagories, so you don't have "------CREATURES------" in both tables for example
                continue
            else:
                if 'Creature' in item_text[1]:
                    self.treev_maindeck.insert("Crt", 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))
                elif 'Instant' in item_text[1]:
                    self.treev_maindeck.insert("Inst", 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))
                elif 'Sorcery' in item_text[1]:
                    self.treev_maindeck.insert("Sorc", 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))
                elif 'Artifact' in item_text[1]:
                    self.treev_maindeck.insert("Arts", 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))
                elif 'Enchantment' in item_text[1]:
                    self.treev_maindeck.insert("Ench", 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))
                elif 'Planeswalker' in item_text[1]:
                    self.treev_maindeck.insert("Plane", 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))
                elif 'Land' in item_text[1]:
                    self.treev_maindeck.insert("Lnd", 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))
                else:
                    self.treev_maindeck.insert('', 'end', text="L" + str(main_listcounter),
                                               values=(item_text[0], item_text[1], item_text[2]))

            self.treev_sideboard.delete(record)

    def remove_selected_from_main(self):
        # Cards are removed from the main deck
        x = self.treev_maindeck.selection()
        for record in x:
            item_text = self.treev_maindeck.item(record, "values")
            # print (item_text[0])

            if "----" in item_text[0]:
                # print ("Not this one")
                pass
            else:
                # print ("this one can be removed")
                self.treev_maindeck.delete(record)

    def remove_selected_from_sb(self):
        # Cards are removed from the main deck
        x = self.treev_sideboard.selection()
        for record in x:
            item_text = self.treev_sideboard.item(record, "values")
            # print (item_text[0])

            if "----" in item_text[0]:
                # print ("Not this one")
                pass
            else:
                # print ("This one can be removed")
                self.treev_sideboard.delete(record)

    def bench_selected(self):
        # Cards are removed from the main deck and moved to the sideboard
        x = self.treev_maindeck.selection()
        side_listcounter = len(self.treev_sideboard.get_children())
        # print ("sideboard number of items: ",side_listcounter)
        # print (x)    
        for record in x:
            side_listcounter += 1
            item_text = self.treev_maindeck.item(record, "values")

            # Now to figure out where to put that entry
            if '----' in item_text[0]:
                # Ignoring all of the heading catagories, so you don't have "------CREATURES------" in both tables for example
                continue
            else:
                if 'Creature' in item_text[1]:  # An Enchanted or Artifact Creature will be classified as a creature
                    self.treev_sideboard.insert("Crt", 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))
                elif 'Instant' in item_text[1]:
                    self.treev_sideboard.insert("Inst", 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))
                elif 'Sorcery' in item_text[1]:
                    self.treev_sideboard.insert("Sorc", 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))
                elif 'Artifact' in item_text[1]:
                    self.treev_sideboard.insert("Arts", 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))
                elif 'Enchantment' in item_text[1]:
                    self.treev_sideboard.insert("Ench", 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))
                elif 'Planeswalker' in item_text[1]:
                    self.treev_sideboard.insert("Plane", 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))
                elif 'Land' in item_text[1]:
                    self.treev_sideboard.insert("Lnd", 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))
                else:
                    self.treev_sideboard.insert('', 'end', text="L" + str(side_listcounter),
                                                values=(item_text[0], item_text[1], item_text[2]))

                self.treev_maindeck.delete(record)

    def new_commander(self):
        """The last selected card from the main deck list or sideboard list becomes the commander.
        Checks eligibility based on Legendary Creature status, or Planeswalkers that specifically can be commander
        Updates some deck data labels"""

        if type(mtg_sql.check_cardref(self.current_card)) is tuple:
            this_table = (mtg_sql.check_cardref(self.current_card)[0])
            # print ("SEARCHING TABLE: ",this_table)
        else:
            this_table = mtg_sql.check_cardref(self.current_card)

        search_commander = (self.current_card,)

        mtg_sql.cur.execute(
            "SELECT Mana_cost, Legendary, Card_Type, Oracle_Text, Keywords, Colour_ID FROM " + this_table + " WHERE Name=?",
            search_commander)
        fetch = mtg_sql.cur.fetchone()
        # print (fetch[0])
        if 'partner' not in fetch[4].lower():
            self.partner_cmc_label.configure(text='')
            self.partner_label.configure(text='')
            self.prtnr_clr_label.configure(text='')

        if fetch[1] == "Yes" and ('creature' in fetch[2].lower() or 'can be your commander' in fetch[3].lower()):
            # Confirm that the card is either a Legendary Creature or a Planeswalker that can be your commander
            self.commander_cmc_label.configure(text='Commander Mana Cost: ' + fetch[0])
            self.commander = self.current_card
            self.commander_label.configure(text='Commander: ' + self.commander)
            self.clr_id_label.configure(text='Colour ID: ' + fetch[5])

    def new_partner(self):
        """The last selected card from the main deck list or sideboard list becomes the partner.
        Checks eligibility based on Legendary Creature status, or Planeswalkers that specifically can be commander,
        that also have the partner keyword
        Updates some deck data labels"""

        ## First confirm if the current commander has the keyword 'Partner'
        if type(mtg_sql.check_cardref(self.commander)) is tuple:
            this_table = (mtg_sql.check_cardref(self.commander)[0])
            # print ("SEARCHING TABLE: ",this_table)
        else:
            this_table = mtg_sql.check_cardref(self.commander)

        search_commander = (self.commander,)
        mtg_sql.cur.execute("SELECT Keywords, Image_URL FROM " + this_table + " WHERE Name=?", search_commander)
        fetch = mtg_sql.cur.fetchone()
        if 'partner' in fetch[0].lower():
            # Current Commander can be Partner, now check the new card out
            if type(mtg_sql.check_cardref(self.current_card)) is tuple:
                this_table = (mtg_sql.check_cardref(self.current_card)[0])
                # print ("SEARCHING TABLE: ",this_table)
            else:
                this_table = mtg_sql.check_cardref(self.current_card)

            search_commander = (self.current_card,)
            commander_img = fetch[1]

            mtg_sql.cur.execute(
                "SELECT Mana_cost, Legendary, Card_Type, Oracle_Text, Keywords, Colour_ID, Image_URL FROM " + this_table + " WHERE Name=?",
                search_commander)
            fetch = mtg_sql.cur.fetchone()
            # print (fetch[0])
            if 'partner' in fetch[4].lower() and fetch[1] == "Yes" and (
                    'creature' in fetch[2].lower() or 'can be your commander' in fetch[3].lower()):
                # Confirm that the card is either a Legendary Creature or a Planeswalker that can be your commander, and has Partner
                self.partner_cmc_label.configure(text='Partner Mana Cost: ' + fetch[0])
                self.partner = self.current_card
                self.partner_label.configure(text='Partner: ' + self.partner)
                self.prtnr_clr_label.configure(text='Partner Colour ID: ' + fetch[5])
                partner_img = fetch[6]

                response = requests.get(commander_img)
                img_data = response.content
                img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                img = img._PhotoImage__photo.subsample(2)  ## Zoom out by 2, works okay
                panel = ttk.Label(root, image=img)
                panel.image = img
                panel.place(x=410, y=20, width=244, height=340)

                response = requests.get(partner_img)
                img_data = response.content
                img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
                img = img._PhotoImage__photo.subsample(2)
                panel = ttk.Label(root, image=img)
                panel.image = img
                panel.place(x=654, y=20, width=244, height=340)

    """ GUI FUNCTIONS AND PROCESSING END """

    """ DECK HANDLING START """

    def close_deck(self):
        self.treev_maindeck.delete(*self.treev_maindeck.get_children())
        self.treev_sideboard.delete(*self.treev_sideboard.get_children())

    def save_deck(self):
        # print (self.deck_ID, self.deck_name, self.commander,self.deck_tier, self.deck_table)
        if len(self.deck_table) > 0:
            # Recreate the table with the list of cards and quantities
            sqlstatement = "DROP TABLE IF EXISTS '" + str(self.deck_table) + "'"
            print(sqlstatement)
            mtg_sql.cur.execute(sqlstatement)
            mtg_sql.check_new_deck_table(self.deck_table)
            children = self.get_all_children(self.treev_maindeck)

            for child in children:
                childname = self.treev_maindeck.item(child, "values")[0].strip()
                childtype = self.treev_maindeck.item(child, "values")[1].strip()
                childqty = self.treev_maindeck.item(child, "values")[2]
                if "----" not in childname:    mtg_sql.import_into_deck(self.deck_table, childname, childtype,
                                                                        int(childqty), "-")

            children = self.get_all_children(self.treev_sideboard)
            for child in children:
                childname = self.treev_sideboard.item(child, "values")[0].strip()
                childtype = self.treev_sideboard.item(child, "values")[1].strip()
                childqty = self.treev_sideboard.item(child, "values")[2]
                if "----" not in childname: mtg_sql.import_into_deck(self.deck_table, childname, childtype,
                                                                     int(childqty), "Yes")

        ## New deck table is assembled, now rebuild the deck in the All_Decks table
        sql_statement = "DELETE FROM All_Decks WHERE id_Code='" + str(self.deck_id) + "'"
        mtg_sql.cur.execute(sql_statement)

        if type(self.deck_tier) is str:
            self.current_tier = 'undetermined'
        else:
            self.current_tier = self.deck_tier.get()

        if type(self.deck_tier) is str:
            current_deckstatus = 'undetermined'
        else:
            current_deckstatus = self.deckstatus.get()

        self.deck_id = self.deckidbox.get()
        self.deck_name = self.decknamebox.get()
        self.decklocation = self.decklocationbox.get()
        self.deck_table = self.decktablebox.get()
        self.deck_notes = self.decknotesbox.get()

        print("saving deck..ID ", self.deck_id, "name: ", self.deck_name, "commander: ", self.commander, "partner: ",
              self.partner, "tier: ", self.current_tier, "table; ", self.deck_table, "status: ", current_deckstatus,
              "location: ",
              self.decklocation, "notes: ", self.deck_notes)

        print("partner type: ", type(self.partner), "   tier type: ", type(self.deck_tier))
        mtg_sql.create_new_deck(self.deck_id, self.deck_name, self.commander, self.partner, self.deck_tier,
                                self.deck_table, current_deckstatus, self.decklocation, self.deck_notes)
        self.close_deck()
        print("Closed and reopening deck..")
        self.load_deck(self.deck_table)

        mtg_sql.db.commit()
        print("Committed to dat'nbase")

    def prep_deck_list(self):
        """Establish the card categories in the main deck list and the sideboard  """
        self.treev_maindeck.insert("", 1, text="Crt", iid="Crt", open=True,
                                   values=("------CREATURES------", "------------", "------"))
        self.treev_maindeck.insert("", 2, text="Inst", iid="Inst", open=True,
                                   values=("------INSTANTS------", "------------", "------"))
        self.treev_maindeck.insert("", 3, text="Sorc", iid="Sorc", open=True,
                                   values=("------SORCERIES------", "------------", "------"))
        self.treev_maindeck.insert("", 4, text="Arts", iid="Arts", open=True,
                                   values=("------ARTIFACTS------", "------------", "------"))
        self.treev_maindeck.insert("", 5, text="Ench", iid="Ench", open=True,
                                   values=("------ENCHANTMENTS------", "------------", "------"))
        self.treev_maindeck.insert("", 6, text="Plane", iid="Plane", open=True,
                                   values=("------PLANESWALKERS------", "------------", "------"))
        self.treev_maindeck.insert("", 7, text="Lnd", iid="Lnd", open=True,
                                   values=("------LANDS------", "------------", "------"))

        self.treev_sideboard.insert("", 1, text="Crt", iid="Crt", open=True,
                                    values=("------CREATURES------", "------------", "------"))
        self.treev_sideboard.insert("", 2, text="Inst", iid="Inst", open=True,
                                    values=("------INSTANTS------", "------------", "------"))
        self.treev_sideboard.insert("", 3, text="Sorc", iid="Sorc", open=True,
                                    values=("------SORCERIES------", "------------", "------"))
        self.treev_sideboard.insert("", 4, text="Arts", iid="Arts", open=True,
                                    values=("------ARTIFACTS------", "------------", "------"))
        self.treev_sideboard.insert("", 5, text="Ench", iid="Ench", open=True,
                                    values=("------ENCHANTMENTS------", "------------", "------"))
        self.treev_sideboard.insert("", 6, text="Plane", iid="Plane", open=True,
                                    values=("------PLANESWALKERS------", "------------", "------"))
        self.treev_sideboard.insert("", 7, text="Lnd", iid="Lnd", open=True,
                                    values=("------LANDS------", "------------", "------"))

    def prep_search_result_list(self):
        """Clear the list and Re-Establish the card categories in the Card finder search results, this is done more frequently so it is in it's own function """
        self.treev_results.delete(*self.treev_results.get_children())
        self.treev_results.insert("", 1, text="Crt", iid="Crt", open=True,
                                  values=("------CREATURES------", "------------", "-----------"))
        self.treev_results.insert("", 2, text="Inst", iid="Inst", open=True,
                                  values=("------INSTANTS------", "------------", "------------"))
        self.treev_results.insert("", 3, text="Sorc", iid="Sorc", open=True,
                                  values=("------SORCERIES------", "------------", "------------"))
        self.treev_results.insert("", 4, text="Arts", iid="Arts", open=True,
                                  values=("------ARTIFACTS------", "------------", "------------"))
        self.treev_results.insert("", 5, text="Ench", iid="Ench", open=True,
                                  values=("------ENCHANTMENTS------", "------------", "------------"))
        self.treev_results.insert("", 6, text="Plane", iid="Plane", open=True,
                                  values=("------PLANESWALKERS------", "------------", "------------"))
        self.treev_results.insert("", 7, text="Lnd", iid="Lnd", open=True,
                                  values=("------LANDS------", "------------", "------------"))

    def new_deck(self):
        # Close current deck and wipe the current treeviews
        self.close_deck()
        self.prep_deck_list()
        # Reset variables
        self.commander = ""
        self.partner = ""
        self.deck_ID = ""
        self.deck_table = ""
        self.decklocation = ""
        self.deck_name = ""
        self.current_status = "UNASSEMBLED"
        self.current_tier = "Online"
        self.total_mana_cost_string = ""

        # Clear Deck details view
        self.decktablebox.delete(0, END)
        self.decklocationbox.delete(0, END)
        self.deckidbox.delete(0, END)
        self.decknamebox.delete(0, END)
        self.decknotesbox.delete(0, END)

        self.deck_label.configure(text='Deck Name: ')
        self.etb_label.configure(text='Enter the Battlefield effect Cards: ')
        self.draw_label.configure(text='Card Draw Cards: ')
        self.target_label.configure(text='Target Cards: ')
        self.broad_label.configure(text="Non-Target 'Broad' Cards: ")
        self.ramp_label.configure(text='Ramp Cards: ')
        self.avg_cmc_label.configure(text='Avg CMC: ')
        self.commander_label.configure(text='Commander: ')
        self.clr_id_label.configure(text='Colour ID: ')
        self.commander_cmc_label.configure(text='Commander Mana Cost: ')
        self.deck_tier_label.configure(text='Deck Tier: Online')
        self.land_label.configure(text='# of Lands: ')
        self.deck_ID_label.configure(text='Deck ID: ')
        self.status_label.configure(text='Deck Status: UNASSEMBLED')
        self.deck_location_label.configure(text='Deck Location: ')
        panel = ttk.Label(root)
        panel.place(x=410, y=20, width=490, height=340)

    def load_deck(self, deck):

        mtg_sql.cur.execute("""SELECT * FROM """ + deck)
        lst = mtg_sql.cur.fetchall()
        main_listcounter = 0
        side_listcounter = 0
        self.prep_deck_list()

        for items in lst:
            if items[3] == 'Yes':
                side_listcounter += 1
                if 'Creature' in items[1]:
                    self.treev_sideboard.insert("Crt", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
                elif 'Instant' in items[1]:
                    self.treev_sideboard.insert("Inst", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
                elif 'Sorcery' in items[1]:
                    self.treev_sideboard.insert("Sorc", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
                elif 'Artifact' in items[1]:
                    self.treev_sideboard.insert("Arts", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
                elif 'Enchantment' in items[1]:
                    self.treev_sideboard.insert("Ench", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
                elif 'Planeswalker' in items[1]:
                    self.treev_sideboard.insert("Plane", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
                elif 'Land' in items[1]:
                    self.treev_sideboard.insert("Lnd", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
                else:
                    self.treev_sideboard.insert("", 'end', text="L" + str(side_listcounter),
                                                values=(items[0], items[1], items[2]))
            else:
                main_listcounter += 1
                if 'Creature' in items[1]:
                    self.treev_maindeck.insert("Crt", 'end', text="L" + str(main_listcounter),
                                               values=(items[0], items[1], items[2]))
                elif 'Instant' in items[1]:
                    self.treev_maindeck.insert("Inst", 'end', text="L" + str(side_listcounter),
                                               values=(items[0], items[1], items[2]))
                elif 'Sorcery' in items[1]:
                    self.treev_maindeck.insert("Sorc", 'end', text="L" + str(side_listcounter),
                                               values=(items[0], items[1], items[2]))
                elif 'Artifact' in items[1]:
                    self.treev_maindeck.insert("Arts", 'end', text="L" + str(side_listcounter),
                                               values=(items[0], items[1], items[2]))
                elif 'Enchantment' in items[1]:
                    self.treev_maindeck.insert("Ench", 'end', text="L" + str(side_listcounter),
                                               values=(items[0], items[1], items[2]))
                elif 'Land' in items[1]:
                    self.treev_maindeck.insert("Lnd", 'end', text="L" + str(side_listcounter),
                                               values=(items[0], items[1], items[2]))
                elif 'Planeswalker' in items[1]:
                    self.treev_maindeck.insert("Plane", 'end', text="L" + str(side_listcounter),
                                               values=(items[0], items[1], items[2]))
                else:
                    # cards that are not in my inventory will show up uncategorized as that data is currently pulled from the Cards/Face_Cards tables, not
                    # the Grandtables, might change that in the future
                    self.treev_maindeck.insert("", 'end', text="L" + str(main_listcounter),
                                               values=(items[0], items[1], items[2]))

        search_deck = (deck,)
        mtg_sql.cur.execute("""SELECT Avg_CMC, Board_Wipe, Draw, ETB_Effects, Ramp, Target_Removal, Deck_Name, Commander, Partner,
                    Colour_ID, Deck_Tier, Lands, id_Code, Status, Location, Notes FROM All_Decks WHERE Deck_list =?""",
                            search_deck)
        all_things = mtg_sql.cur.fetchone()
        # print (all_things)
        try:
            avg_cmc = all_things[0]
            broad_count = all_things[1]
            draw_count = all_things[2]
            etb_count = all_things[3]
            ramp_count = all_things[4]
            target_count = all_things[5]
            deck_name = all_things[6]
            commander = all_things[7]
            clr_id = all_things[9]
            deck_tier = all_things[10]
            lands = all_things[11]
            id_code = all_things[12]
            status = all_things[13]
            location = all_things[14]
            # monstrous line, but sometimes partner might be NoneType
            self.current_deck_notes = all_things[15]
            self.partner = all_things[8]
        except:
            avg_cmc = 0
            broad_count = 0
            draw_count = 0
            etb_count = 0
            ramp_count = 0
            target_count = 0
            deck_name = "Name"
            commander = ""
            clr_id = ""
            # deck_tier='Online'
            lands = 0
            id_code = "id-code"
            # status='UNASSEMBLED'
            location = "-"
            # monstrous line, but sometimes partner might be NoneType
            self.partner = ""
            self.current_deck_notes = ""

        # print (self.partner, " Partner: ", type(self.partner) )
        search_commander = (commander,)
        self.commander = commander
        self.deck_id = id_code
        self.deck_table = deck
        self.deck_name = deck_name
        # self.deck_tier = deck_tier
        self.current_tier = deck_tier
        self.deckstatus = status
        self.decklocation = location

        self.decktablebox.delete(0, END)
        if len(self.deck_table) > 0: self.decktablebox.insert(0, self.deck_table)
        self.decklocationbox.delete(0, END)
        if len(str(self.decklocation)) > 0: self.decklocationbox.insert(0, self.decklocation)
        self.deckidbox.delete(0, END)
        if len(str(self.deck_id)) > 0: self.deckidbox.insert(0, self.deck_id)
        self.decknamebox.delete(0, END)
        if len(str(self.deck_name)) > 0: self.decknamebox.insert(0, self.deck_name)
        self.decknotesbox.delete(0, END)
        if len(str(self.current_deck_notes)) > 0: self.decknotesbox.insert(0, self.current_deck_notes)

        if type(mtg_sql.check_cardref(commander)) is tuple:
            this_table = (mtg_sql.check_cardref(commander)[0])
            # print ("SEARCHING TABLE: ",this_table)
        else:
            this_table = mtg_sql.check_cardref(commander)

        # Display sides of cards if it is double sided, 
        if this_table == "Face_Cards_Condensed":
            if "//" in search_commander:
                search_commander = (commander.split("//")[0].strip(),)
                mtg_sql.cur.execute("SELECT Flip_Name from Face_Cards_Condensed WHERE Name=?", search_commander)
                flip_name = mtg_sql.cur.fetchone()
                mtg_sql.cur.execute("SELECT Image_URL from Face_Cards_Condensed WHERE Name=?", flip_name)
                link2 = mtg_sql.cur.fetchone()[0]
            else:
                mtg_sql.cur.execute("SELECT Flip_Name from Face_Cards_Condensed WHERE Name=?", search_commander)
                flip_name = mtg_sql.cur.fetchone()
                mtg_sql.cur.execute("SELECT Image_URL from Face_Cards_Condensed WHERE Name=?", flip_name)
                link2 = mtg_sql.cur.fetchone()[0]
        mtg_sql.cur.execute("SELECT Mana_cost, Image_URL FROM " + this_table + " WHERE Name=?", search_commander)
        fetch = mtg_sql.cur.fetchone()
        c_mana_cost = fetch[0]
        link = fetch[1]

        response = requests.get(link)
        img_data = response.content
        img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
        img = img._PhotoImage__photo.subsample(2)  ## Zoom out by 2, works okay
        panel = ttk.Label(root, image=img)
        panel.image = img
        panel.place(x=410, y=20, width=244, height=340)

        if len(self.partner) > 0:
            if type(mtg_sql.check_cardref(self.partner)) is tuple:
                this_table = (mtg_sql.check_cardref(self.partner)[0])
                # print ("SEARCHING TABLE: ",this_table)
            else:
                this_table = mtg_sql.check_cardref(self.partner)
            search_partner = (self.partner,)
            mtg_sql.cur.execute("SELECT Mana_cost, Image_URL, Colour_ID FROM " + this_table + " WHERE Name=?",
                                search_partner)
            fetch = mtg_sql.cur.fetchone()
            partner_img = fetch[1]
            self.partner_cmc_label.configure(text='Partner Mana Cost: ' + fetch[0])
            self.partner_label.configure(text='Partner: ' + self.partner)
            self.prtnr_clr_label.configure(text='Partner Colour ID: ' + fetch[2])

        self.deck_label.configure(text='Deck Name: ' + str(deck_name))
        self.etb_label.configure(text='Enter the Battlefield effect Cards: ' + str(etb_count))
        self.draw_label.configure(text='Card Draw Cards: ' + str(draw_count))
        self.target_label.configure(text='Target Cards: ' + str(target_count))
        self.broad_label.configure(text="Non-Target 'Broad' Cards: " + str(broad_count))
        self.ramp_label.configure(text='Ramp Cards: ' + str(ramp_count))
        self.avg_cmc_label.configure(text='Avg CMC: ' + str(avg_cmc))
        self.commander_label.configure(text='Commander: ' + str(commander))
        self.clr_id_label.configure(text='Colour ID: ' + str(clr_id))
        self.commander_cmc_label.configure(text='Commander Mana Cost: ' + str(c_mana_cost))
        self.deck_tier_label.configure(text='Deck Tier: ' + str(deck_tier))
        self.deck_location_label.configure(text='Deck Location: ' + str(location))
        self.land_label.configure(text='# of Lands: ' + str(lands))
        self.deck_ID_label.configure(text='Deck ID: ' + str(id_code))
        self.status_label.configure(text='Deck Status: ' + str(status))

        if this_table == "Face_Cards_Condensed":
            response = requests.get(link2)
            img_data = response.content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
            img = img._PhotoImage__photo.subsample(2)

            panel = ttk.Label(root, image=img)
            panel.image = img
            panel.place(x=654, y=20, width=244, height=340)
        elif len(self.partner) > 0:
            response = requests.get(partner_img)
            img_data = response.content
            img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)))
            img = img._PhotoImage__photo.subsample(2)
            panel = ttk.Label(root, image=img)
            panel.image = img
            panel.place(x=654, y=20, width=244, height=340)
        else:
            panel = ttk.Label(root)
            panel.place(x=654, y=20, width=244, height=340)

        get_all_counts = ()
        get_all_counts = self.count_cards()

    """ DECK HANDLING END """


""" DONE IN MAIN.PY, the following is for testing purposes """
# d = MtgGui(root)
# d.load_deck('zAlela')
# d.fill_decklist()
# d.set_event_bindings()
# 
# root.mainloop()
