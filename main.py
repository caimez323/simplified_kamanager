import wx,json,os,math
from read import load_config,get_data

def getIndexFromName(data,name):
    for index,value in enumerate(data):
        if name == value["name"]:
            return index



class ItemEditor(wx.Frame):
    def __init__(self, parent, gearsData, resourcesData):
        super().__init__(parent, title="Éditeur d'objet", size=(800, 600))
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.gearsData = gearsData
        self.resourcesData = resourcesData
        self.sort_column = None
        self.sort_order = True  # True pour trier par ordre croissant, False pour trier par ordre décroissant

        self.notebook = wx.Notebook(panel)
        self.list_tab = wx.Panel(self.notebook)
        self.recipe_tab = wx.Panel(self.notebook)
        self.resources_tab = wx.Panel(self.notebook)


        self.notebook.AddPage(self.list_tab, "Liste")
        self.notebook.AddPage(self.recipe_tab, "Recette")
        self.notebook.AddPage(self.resources_tab, "Ressources")

        # Main List
        list_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.list_ctrl = wx.ListCtrl(self.list_tab, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.list_ctrl.InsertColumn(0, "Nom")
        self.list_ctrl.InsertColumn(1, "Niveau")
        self.list_ctrl.InsertColumn(2, "Prix")
        self.list_ctrl.InsertColumn(3, "Coefficient")
        self.list_ctrl.SetColumnWidth(0, 200)
        self.list_ctrl.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_toggle_hidden)
        for id,item in self.gearsData.items():
            index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item["name"])
            self.list_ctrl.SetItem(index, 1, str(item["level"]))
            self.list_ctrl.SetItem(index, 2, str(item["price"]))
            self.list_ctrl.SetItem(index, 3, str(self.calcul_coeff(item)))
            self.list_ctrl.SetItemData(index, index)

        list_sizer.Add(self.list_ctrl, 1, wx.EXPAND | wx.ALL, 5)
        self.list_tab.SetSizer(list_sizer)

        # Ressource Tab
        resource_sizer = wx.BoxSizer(wx.VERTICAL)
    
        self.resource_list = wx.ListCtrl(self.resources_tab, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.resource_list.InsertColumn(0, "Nom")
        self.resource_list.InsertColumn(1, "Prix")
        self.resource_list.SetColumnWidth(0, 100)
        
        # Search control
        self.resource_search_ctrl = wx.SearchCtrl(self.resources_tab)
        self.resource_search_ctrl.Bind(wx.EVT_TEXT, self.on_search_resources)
        resource_sizer.Add(self.resource_search_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        
        # Fill datas
        for id,item in self.resourcesData.items():
            index = self.resource_list.InsertItem(self.resource_list.GetItemCount(), item["name"])
            self.resource_list.SetItem(index, 1, str(item["price"]))
            self.resource_list.SetItemData(index, index)
        
        resource_sizer.Add(self.resource_list, 1, wx.EXPAND | wx.ALL, 5)
        self.resources_tab.SetSizer(resource_sizer)


        # tab control
        
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

        # 

        panel.SetSizer(main_sizer)

    def on_search_resources(self, event):
        self.resource_list.DeleteAllItems()  # Efface tous les éléments de la liste

        for item in (self.resourcesData.values()):
            if self.resource_search_ctrl.GetValue().lower() in item["name"].lower():
                newIndex = self.resource_list.GetItemCount()
                self.resource_list.InsertItem(newIndex, item["name"])
                self.resource_list.SetItem(newIndex, 1, str(item["price"]))
                self.resource_list.SetItemData(newIndex, newIndex)

    def on_tab_change(self, event):
        selection = event.GetSelection()
        if selection == 1:  # Recipe Tab
            # Populate recipe tab
            index = self.list_ctrl.GetFirstSelected()
            if index != -1:
                self.on_select(wx.ListEvent(index=index))

    def on_select(self, event):
        index = event.GetIndex()
        item = self.gearsData[index]
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
        column = event.GetColumn()+1
        if column == self.sort_column:
            self.sort_order = not self.sort_order
        else:
            self.sort_column = column
            self.sort_order = True
        self.sort_items()

    def sort_items(self):
        items = [(self.list_ctrl.GetItemData(i), self.list_ctrl.GetItemText(i), int(self.list_ctrl.GetItem(i, 1).GetText()), int(self.list_ctrl.GetItem(i, 2).GetText()), int(self.list_ctrl.GetItem(i, 3).GetText()), i) for i in range(self.list_ctrl.GetItemCount())]
        items = sorted(items, key= lambda x: x[self.sort_column], reverse= not self.sort_order)

        for i, (_, name, level, price, coeff, index) in enumerate(items):
            self.list_ctrl.SetItem(i, 0, name)
            self.list_ctrl.SetItem(i, 1, str(level))
            self.list_ctrl.SetItem(i, 2, str(price))
            self.list_ctrl.SetItem(i, 3, str(coeff))

    def on_toggle_hidden(self, event):
        index = event.GetIndex()
        current_state = self.list_ctrl.GetItem(index, 4).GetText()
        new_state = "Oui" if current_state == "Non" else "Non"
        self.list_ctrl.SetItem(index, 4, new_state)
        # Mettre à jour la valeur "hidden" dans les données
        # Cependant, l'index des data peut ne pas être le même que l'ordre qui est affiché car la grille à pu être modifiée
        indexInDataCorrected = getIndexFromName(self.gearsData,self.list_ctrl.GetItem(index,0).GetText())
        self.gearsData[indexInDataCorrected]["hidden"] = (new_state == "Oui")

        #On fait disparaitre
        self.list_ctrl.DeleteItem(index)

    def on_show_items(self, event):
        print("====")
        for item in self.gearsData:
            print("{} , {}".format(item["name"],item["hidden"]))
    
    def on_redisplay_all(self,event):
        for item in self.gearsData:
            if item["hidden"] :
                item["hidden"] = False
                index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item["name"])
                self.list_ctrl.SetItem(index, 1, str(item["level"]))
                self.list_ctrl.SetItem(index, 2, str(item["price"]))
                self.list_ctrl.SetItem(index, 3, "-1")
                self.list_ctrl.SetItem(index, 4, "Non" if not item.get("hidden") else "Oui")  # Mettre "Oui" si hidden est True, sinon "Non"
                print(item["name"])
                print(index)
    
    def calcul_coeff(self,item):
        cout = 0
        for component in item["recipe"]:
            compoPrice = self.resourcesData[component["id"]]["price"]
            cout+= component["quantity"] * compoPrice
        vente = item["price"]
        tmp = int(math.floor(100*vente/cout))
        
        return tmp
             

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Menu Principal", size=(300, 150))
        
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        launchButton = wx.Button(panel, label="Ouvrir main")
        launchButton.Bind(wx.EVT_BUTTON, self.on_open_editor)
        main_sizer.Add(launchButton, 0, wx.ALL | wx.CENTER, 10)

        updateButton = wx.Button(panel, label="Update database")
        updateButton.Bind(wx.EVT_BUTTON, self.load_database)
        main_sizer.Add(updateButton, 0, wx.ALL | wx.CENTER, 10)

        panel.SetSizer(main_sizer)
        self.Center()
        
    def on_open_editor(self, event):
        data = [  # Définition des données d'exemple
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
        
        # look for empty database
        if not os.path.exists("resources.database") or not os.path.exists("gears.database"):
            print("Error : Load database First then relaunch main frame")
            return -1
        
        
        # Load local database
        
        gears = json.load(open("gears.database"))
        resources = json.load(open("resources.database"))
        
        editor_frame = ItemEditor(None, gears,resources)  # Crée une instance de l'éditeur d'objets
        editor_frame.Show()  # Affiche la fenêtre de l'éditeur d'objets
        
    def load_database(self,event):
        db = load_config()
        #Load ressources
        resources = get_data(db,"resources","common")
        gears = {}
        
        #Load gears
        for i in range(0,5):
            tmp = get_data(db,"gears","common{}".format(i))
            if tmp!=None:
                for k,v in tmp.items():
                    gears[k] = v

        # resources and gears are not loaded, need to write them down
        with open("gears.database","w") as file:
            file.write(json.dumps(gears,indent=4))
        with open("resources.database","w") as file:
            file.write(json.dumps(resources,indent=4))
            
        print("==========\nUpdate succesfull !\n==========")
        return resources,gears

if __name__ == "__main__":
    
    app = wx.App()
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
