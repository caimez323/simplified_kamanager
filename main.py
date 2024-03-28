import firebase_admin
from firebase_admin import firestore
from dotenv import load_dotenv
import os,sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QLabel





def load_database():
    cred = firebase_admin.credentials.Certificate("creditentials.json")
    firebase_admin.initialize_app(cred,{'databaseURL': os.getenv("DATABASE_URL")})
    database = firebase_admin.firestore.client()
    return database

import wx

class ItemEditor(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Éditeur d'objet", size=(600, 300))
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.data = data
        self.sort_column = None
        self.sort_order = True  # True pour trier par ordre croissant, False pour trier par ordre décroissant

        self.notebook = wx.Notebook(panel)
        self.list_tab = wx.Panel(self.notebook)
        self.recipe_tab = wx.Panel(self.notebook)

        self.notebook.AddPage(self.list_tab, "Liste")
        self.notebook.AddPage(self.recipe_tab, "Recette")

        # List Tab
        list_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.list_ctrl = wx.ListCtrl(self.list_tab, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Nom")
        self.list_ctrl.InsertColumn(1, "Niveau")
        self.list_ctrl.InsertColumn(2, "Prix")
        self.list_ctrl.InsertColumn(3, "Coefficient")
        self.list_ctrl.SetColumnWidth(0, 200)
        for item in data:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item["name"])
            self.list_ctrl.SetItem(index, 1, str(item["level"]))
            self.list_ctrl.SetItem(index, 2, str(item["price"]))
            self.list_ctrl.SetItem(index, 3, "-1")

        list_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.list_tab.SetSizer(list_sizer)

        # Recipe Tab
        recipe_sizer = wx.BoxSizer(wx.VERTICAL)
        self.recipe_panel = wx.Panel(self.recipe_tab)
        recipe_sizer.Add(self.recipe_panel, 1, wx.EXPAND | wx.ALL, 5)
        self.recipe_tab.SetSizer(recipe_sizer)

        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)
        self.list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
        main_sizer.Add(self.notebook, 1, wx.EXPAND)
        panel.SetSizer(main_sizer)

    def on_tab_change(self, event):
        selection = event.GetSelection()
        if selection == 1:  # Recipe Tab
            # Populate recipe tab
            index = self.list_ctrl.GetFirstSelected()
            if index != -1:
                self.on_select(wx.ListEvent(index=index))

    def on_select(self, event):
        index = event.GetIndex()
        item = self.data[index]
        ingredients = item.get("recipe", [])

        self.recipe_panel.DestroyChildren()

        recipe_label = wx.StaticText(self.recipe_panel, label="Liste des Ingrédients:")
        self.recipe_panel.GetSizer().Add(recipe_label, 0, wx.ALL, 5)

        for ingredient in ingredients:
            label = wx.StaticText(self.recipe_panel, label=f"{ingredient['name']} ({ingredient['quantity']})")
            self.recipe_panel.GetSizer().Add(label, 0, wx.ALL, 5)

        self.recipe_panel.Layout()
        self.recipe_panel.Refresh()

    def on_column_click(self, event):
        column = event.GetColumn()
        if column == self.sort_column:
            self.sort_order = not self.sort_order
        else:
            self.sort_column = column
            self.sort_order = True

        self.sort_items()

    def sort_items(self):
        items = [(self.list_ctrl.GetItemText(i), int(self.list_ctrl.GetItem(i, 1).GetText()), int(self.list_ctrl.GetItem(i, 2).GetText()), int(self.list_ctrl.GetItem(i, 3).GetText()), i) for i in range(self.list_ctrl.GetItemCount())]
        items.sort(key=lambda x: x[self.sort_column], reverse=not self.sort_order)

        for i, (name, level, price, coeff, index) in enumerate(items):
            self.list_ctrl.SetItem(i, 0, name)
            self.list_ctrl.SetItem(i, 1, str(level))
            self.list_ctrl.SetItem(i, 2, str(price))
            self.list_ctrl.SetItem(i, 3, str(coeff))

if __name__ == "__main__":
    data = [
        {
            "id": 1,
            "name": "Amulette du Hibou",
            "level": 8,
            "price": 90,
            "recipe": [
                {"name": "Bave de Bouftou", "quantity": 3, "id": "48"},
                {"name": "Relique d'Incarnam", "quantity": 3, "id": "2192"}
            ],
            "hidden": False,
            "trueHidden": False,
            "toCraft": 0
        },
        {
            "id": 2,
            "name": "Bottes d'Alchimiste",
            "level": 12,
            "price": 150,
            "recipe": [
                {"name": "Bave de Bouftou", "quantity": 4, "id": "48"},
                {"name": "Cuir de Boufton Noir", "quantity": 3, "id": "2202"}
            ],
            "hidden": False,
            "trueHidden": False,
            "toCraft": 0
        }
    ]
    app = wx.App()
    frame = ItemEditor(None, data)
    frame.Show()
    app.MainLoop()
