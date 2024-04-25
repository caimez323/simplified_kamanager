import wx,json,os,math
from read import load_config,get_data
from connect import upload_data

def getIndexFromName(dataDic,name):
    for index,value in dataDic.items():
        if name == value["name"]:
            return index



class ItemEditor(wx.Frame):
    def __init__(self, parent, gearsData, resourcesData,DB):
        super().__init__(parent, title="Éditeur d'objet", size=(500, 600))
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.gearsData = gearsData
        self.resourcesData = resourcesData
        self.sort_column = None
        self.sort_order = True 
        self.toBeSync = {"resources" : {}, "gears": {}}
        self.DB = DB
        self.ingredients = {}

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
        self.resource_list.SetColumnWidth(0, 250)
        self.resource_list.SetColumnWidth(1, 100)

        self.resource_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_resources_click)
        
        # Search control
        self.resource_search_ctrl = wx.SearchCtrl(self.resources_tab)
        self.resource_search_ctrl.Bind(wx.EVT_TEXT, self.on_search_resources)
        resource_sizer.Add(self.resource_search_ctrl, 0, wx.EXPAND | wx.ALL, 5)
        
        # Fill datas
        for id,item in self.resourcesData.items():
            index = self.resource_list.InsertItem(self.resource_list.GetItemCount(), item["name"])
            self.resource_list.SetItem(index, 0, str(item["name"]))
            self.resource_list.SetItem(index, 1, str(item["price"]))
            
            self.resource_list.SetItemData(index, index)
        
        resource_sizer.Add(self.resource_list, 1, wx.EXPAND | wx.ALL, 5)
        self.resources_tab.SetSizer(resource_sizer)
        
        # Recipe
        recipe_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.recipe_list = wx.ListCtrl(self.recipe_tab, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
        self.recipe_list.InsertColumn(0, "Nom")
        self.recipe_list.InsertColumn(1, "Need")
        self.recipe_list.SetColumnWidth(0, 250)
        self.recipe_list.SetColumnWidth(1, 75)
        self.recipe_list.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.on_craft_done)
        
        recipe_sizer.Add(self.recipe_list, 1, wx.EXPAND | wx.ALL, 5)
        self.recipe_tab.SetSizer(recipe_sizer)

        # == tab control
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)
        self.list_ctrl.Bind(wx.EVT_LIST_COL_CLICK, self.on_column_click)
        main_sizer.Add(self.notebook, 1, wx.EXPAND)

        #==== Boutons
        button_sizer = wx.GridSizer(rows=2, cols=3, hgap=5, vgap=4)
        main_sizer.Add(button_sizer,0,wx.EXPAND | wx.ALL, 5)
        
        # Afficher les éléments dans la console
        show_items_button = wx.Button(panel, label="Afficher les éléments dans la console")
        show_items_button.Bind(wx.EVT_BUTTON, self.on_show_items)
        #button_sizer.Add(show_items_button, 0, wx.ALL | wx.CENTER, 10)

        # Enlever l'état caché de tous les éléments
        display_all_button = wx.Button(panel, label="Re-afficher l.cachées")
        display_all_button.Bind(wx.EVT_BUTTON, self.on_redisplay_all)
        button_sizer.Add(display_all_button, 0, wx.ALL | wx.CENTER, 10)

        # Sync button
        sync_button = wx.Button(panel, label="SYNC")
        sync_button.Bind(wx.EVT_BUTTON, self.sync_request_data_res)
        button_sizer.Add(sync_button, 0, wx.ALL | wx.CENTER, 10)
        
        # Add to craft
        addCraftButton = wx.Button(panel, label="Craft")
        addCraftButton.Bind(wx.EVT_BUTTON, self.addToCraft)
        button_sizer.Add(addCraftButton, 0, wx.ALL | wx.CENTER, 10)
        
        # Craft done => double click columns
        
        # Change recipe/Price gears
        changeGearButton = wx.Button(panel, label="Modifier")
        changeGearButton.Bind(wx.EVT_BUTTON,self.on_change_gear)
        button_sizer.Add(changeGearButton,0,wx.ALL | wx.CENTER, 10)
        
        

        
        
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
        self.recipe_list.DeleteAllItems()
        if selection == 1: # Recipe
            #index = self.recipe_list.GetFirstSelected()
            for item,qqt in self.ingredients.items():
                index = self.recipe_list.InsertItem(self.recipe_list.GetItemCount(), item)
                self.recipe_list.SetItem(index, 0 ,str(item))
                self.recipe_list.SetItem(index, 1, str(qqt))
                self.recipe_list.SetItemData(index, index)
            #if index != -1:
            #    self.on_select(wx.ListEvent(index=index))

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
        items = sorted(items, key= lambda x: x[self.sort_column], reverse = self.sort_order)

        for i, (_, name, level, price, coeff, index) in enumerate(items):
            self.list_ctrl.SetItem(i, 0, name)
            self.list_ctrl.SetItem(i, 1, str(level))
            self.list_ctrl.SetItem(i, 2, str(price))
            self.list_ctrl.SetItem(i, 3, str(coeff))

    def on_toggle_hidden(self, event):
        index = event.GetIndex()
        # Mettre à jour la valeur "hidden" dans les données
        # Cependant, l'index des data peut ne pas être le même que l'ordre qui est affiché car la grille à pu être modifiée
        indexInDataCorrected = getIndexFromName(self.gearsData,self.list_ctrl.GetItem(index,0).GetText())
        self.gearsData[indexInDataCorrected]["hidden"] = True

        #On fait disparaitre
        self.list_ctrl.DeleteItem(index)

    def on_show_items(self, event):
        print("====")
        for key,item in self.gearsData.items():
            print("{} , {}".format(item["name"],item["hidden"]))
    
    def on_redisplay_all(self,event):
        for key,item in self.gearsData.items():
            if item["hidden"] :
                item["hidden"] = False
                index = self.list_ctrl.InsertItem(self.list_ctrl.GetItemCount(), item["name"])
                self.list_ctrl.SetItem(index, 1, str(item["level"]))
                self.list_ctrl.SetItem(index, 2, str(item["price"]))
                self.list_ctrl.SetItem(index, 3, str(self.calcul_coeff(item)))
                
    def calcul_coeff(self,item):
        cout = 0
        for component in item["recipe"]:
            compoPrice = self.resourcesData[component["id"]]["price"]
            cout+= component["quantity"] * compoPrice
            
        return int(math.floor(100*item["price"]/cout))
             
    def sync_request_data_res(self,e):
        if self.DB == None :
            self.DB = load_config()
        toBeSyncResources = self.toBeSync["resources"]
        toBeSyncGears = self.toBeSync["gears"]

        for id,value in toBeSyncResources.items():
            to_add = {id:value}
            print("Synced : {}".format(to_add))
            upload_data(self.DB,"resources","common",to_add)
        
        # do the same thing for gears
        for id,value in toBeSyncGears.items():
            to_add = {id:value}
            docID = math.floor(int(id)/1000)
            print("Synced on database{} : {}".format(to_add))
            upload_data(self.DB,"gears","common{}".format(docID),to_add)
        
        self.toBeSync = {"resources" :{},"gears" : {}}
        print("Synced DONE")
        
    def on_resources_click(self,event):
        index = event.GetIndex()
        value = self.resource_list.GetItem(index, 1).GetText()

        # Créer une boîte de dialogue pour modifier le prix
        dlg = wx.TextEntryDialog(self, f"Entrez le nouveau prix pour {self.resource_list.GetItem(index, 0).GetText()} :", "Modifier le prix", value)

        # Afficher la boîte de dialogue
        if dlg.ShowModal() == wx.ID_OK:
            new_price = dlg.GetValue()
            self.resource_list.SetItem(index, 1, new_price)
            # Changer dans la var self.resourcesData
            tIndex = getIndexFromName(self.resourcesData,self.resource_list.GetItem(index, 0).GetText())
            self.resourcesData[tIndex]["price"] = int(new_price)
            self.toBeSync["resources"][tIndex] = self.resourcesData[tIndex]
            print("Modification effectuée dans le cache => Pour la partager, utilisez SYNC")
        # Close
        dlg.Destroy()
        
    def addToCraft(self,event):
        index = self.list_ctrl.GetFirstSelected()
        itemName = self.list_ctrl.GetItem(index, 0).GetText()
        item = self.gearsData[getIndexFromName(self.gearsData,itemName)]
        
        for component in item["recipe"]:
            compoName = self.resourcesData[component["id"]]["name"]
            compoQQT = component["quantity"]
            print("Add to craft : {} X {}".format(compoName,compoQQT))
            if compoName in self.ingredients:
                self.ingredients[compoName] += compoQQT
            else:
                self.ingredients[compoName] = compoQQT
                
    def on_craft_done(self, event):
        index = event.GetIndex()
        ingredientName = event.GetText() #Jsp pourquoi
        print("'{}' done".format(ingredientName))
        del self.ingredients[ingredientName]
        #On fait disparaitre
        self.recipe_list.DeleteItem(index)
        
    def on_change_gear(self,event):
        index = self.list_ctrl.GetFirstSelected()
        value = self.list_ctrl.GetItem(index, 2).GetText()
        itemName = self.list_ctrl.GetItem(index, 0).GetText()

        # Créer une boîte de dialogue pour modifier le prix
        dlg = wx.TextEntryDialog(self, f"Entrez le nouveau prix pour {self.list_ctrl.GetItem(index, 0).GetText()} :", "Modifier le prix", value)

        # Afficher la boîte de dialogue
        if dlg.ShowModal() == wx.ID_OK:
            new_price = dlg.GetValue()
            # Change in list
            self.list_ctrl.SetItem(index, 2, new_price)
        
            # Change in gearsData
            tIndex = getIndexFromName(self.gearsData,itemName)
            self.gearsData[tIndex]["price"] = int(new_price)
            self.toBeSync[tIndex] = self.gearsData[tIndex]
            print("Modification effectuée dans le cache => Pour la partager, utilisez SYNC")

        # Close
        dlg.Destroy()
        
class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Menu Principal", size=(300, 150))
        
        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        launchButton = wx.Button(panel, label="Ouvrir main")
        launchButton.Bind(wx.EVT_BUTTON, self.on_open_editor)
        main_sizer.Add(launchButton, 0, wx.ALL | wx.CENTER, 10)

        updateButton = wx.Button(panel, label="Load database")
        updateButton.Bind(wx.EVT_BUTTON, self.load_database)
        main_sizer.Add(updateButton, 0, wx.ALL | wx.CENTER, 10)

        self.db = None
        panel.SetSizer(main_sizer)
        self.Center()
        
    def on_open_editor(self, event):
        
        # look for empty database
        if not os.path.exists("resources.database") or not os.path.exists("gears.database"):
            print("Error : Load database First then relaunch main frame")
            return -1
        
        # Load local database
        
        gears = json.load(open("gears.database"))
        resources = json.load(open("resources.database"))
        
        editor_frame = ItemEditor(None, gears,resources,self.db)  # Crée une instance de l'éditeur d'objets
        editor_frame.Show()  # Affiche la fenêtre de l'éditeur d'objets
        
    def load_database(self,event):
        if self.db == None:
            self.db = load_config()
        #Load ressources
        resources = get_data(self.db,"resources","common")
        gears = {}
        
        #Load gears
        for i in range(0,5):
            tmp = get_data(self.db,"gears","common{}".format(i))
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
