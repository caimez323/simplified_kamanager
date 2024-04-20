import wx

def getIndexFromName(data,name):
    for index,value in enumerate(data):
        if name == value["name"]:
            return index



class ItemEditor(wx.Frame):
    def __init__(self, parent, data):
        super().__init__(parent, title="Éditeur d'objet", size=(800, 600))
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
        self.list_ctrl.InsertColumn(4, "Caché")
        self.list_ctrl.SetColumnWidth(0, 200)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_toggle_hidden)
        for item in data:
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item["name"])
            self.list_ctrl.SetItem(index, 1, str(item["level"]))
            self.list_ctrl.SetItem(index, 2, str(item["price"]))
            self.list_ctrl.SetItem(index, 3, "-1")
            self.list_ctrl.SetItem(index, 4, "Non" if not item.get("hidden") else "Oui")  # Mettre "Oui" si hidden est True, sinon "Non"
            self.list_ctrl.SetItemData(index, index)

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

        #==== Boutons

        # Afficher les éléments dans la console
        show_items_button = wx.Button(panel, label="Afficher les éléments dans la console")
        show_items_button.Bind(wx.EVT_BUTTON, self.on_show_items)
        main_sizer.Add(show_items_button, 0, wx.ALL | wx.CENTER, 10)

        # Enlever l'état caché de tous les éléments
        display_all_button = wx.Button(panel, label="Afficher toutes les lignes cachées")
        display_all_button.Bind(wx.EVT_BUTTON, self.on_redisplay_all)
        main_sizer.Add(display_all_button, 0, wx.ALL | wx.CENTER, 10)

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
        items = [(self.list_ctrl.GetItemData(i), self.list_ctrl.GetItemText(i), int(self.list_ctrl.GetItem(i, 1).GetText()), int(self.list_ctrl.GetItem(i, 2).GetText()), int(self.list_ctrl.GetItem(i, 3).GetText()), i) for i in range(self.list_ctrl.GetItemCount())]
        items.sort(key=lambda x: x[self.sort_column], reverse=not self.sort_order)

        for i, (_, name, level, price, coeff, index) in enumerate(items):
            self.list_ctrl.SetItem(i, 0, name)
            self.list_ctrl.SetItem(i, 1, str(level))
            self.list_ctrl.SetItem(i, 2, str(price))
            self.list_ctrl.SetItem(i, 3, str(coeff))
            self.list_ctrl.SetItem(i, 4, self.list_ctrl.GetItem(index, 4).GetText())

    def on_toggle_hidden(self, event):
        index = event.GetIndex()
        current_state = self.list_ctrl.GetItem(index, 4).GetText()
        new_state = "Oui" if current_state == "Non" else "Non"
        self.list_ctrl.SetItem(index, 4, new_state)
        # Mettre à jour la valeur "hidden" dans les données
        # Cependant, l'index des data peut ne pas être le même que l'ordre qui est affiché car la grille à pu être modifiée
        indexInDataCorrected = getIndexFromName(self.data,self.list_ctrl.GetItem(index,0).GetText())
        self.data[indexInDataCorrected]["hidden"] = (new_state == "Oui")

        #On fait disparaitre
        self.list_ctrl.DeleteItem(index)

    def on_show_items(self, event):
        print("====")
        for item in self.data:
            print("{} , {}".format(item["name"],item["hidden"]))
    
    def on_redisplay_all(self,event):
        for item in self.data:
            if item["hidden"] :
                item["hidden"] = False
                index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item["name"])
                self.list_ctrl.SetItem(index, 1, str(item["level"]))
                self.list_ctrl.SetItem(index, 2, str(item["price"]))
                self.list_ctrl.SetItem(index, 3, "-1")
                self.list_ctrl.SetItem(index, 4, "Non" if not item.get("hidden") else "Oui")  # Mettre "Oui" si hidden est True, sinon "Non"
                print(item["name"])
                print(index)
    
             

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
        ,
        {
            "id": 3,
            "name": "BAAA",
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
        ,
        {
            "id": 4,
            "name": "ZZZZZZZ",
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
