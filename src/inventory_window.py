"""
Window for displaying information about the player's inventory. The window
is a readonly view; no actions can be taken here that affect game state.
"""
from window import Window
from asset_loader import AssetLoader
from global_vars import Globals
from game_state import GameState, GameMode

class InventoryWindow(Window):

    def __init__(self, width, height):
        super().__init__(width, height)
        GameState().onInventoryChange += self.inventoryChangeHandler()
        GameState().onCharacterSwitch += self.inventoryChangeHandler()  # refresh inventory when character changes

    def inventoryChangeHandler(self):
        # TODO correct selectedIndex to point at same item
        def _inventoryChangeHandler(*args, **kwargs):
            # refresh currentInventoryList by scanning for all items in Game State inventory
            self.currentInventoryList = [
                itemdata for itemdata in self.inventoryList
                if itemdata[0] in GameState().inventory and int(GameState().inventory[itemdata[0]]) > 0
            ]
        return _inventoryChangeHandler

    def reset(self):
        self.inventoryList = []
        self.currentInventoryList = []
        self.selectedIndex = 0

    def load(self):
        itemsdata = AssetLoader().getConfig(Globals.ItemsConfigPath)
        self.inventoryList = [
            (el, itemsdata[el]["name"], itemsdata[el]["description"]) for el in itemsdata.keys()
        ]
        self.inventoryList.sort(key=lambda row: row[1].lower())

    def update(self, timestep, keypress):
        for key in keypress:
            if len(self.currentInventoryList) > 0:
                if key == "Up":
                    self.selectedIndex = (self.selectedIndex - 1) % len(self.currentInventoryList)
                elif key == "Down":
                    self.selectedIndex = (self.selectedIndex + 1) % len(self.currentInventoryList)
            if key == "Return":
                GameState().gameMode = GameMode.InAreaCommand

    def draw(self):
        self.clear()
        # empty message when nothing is in inventory
        if len(self.currentInventoryList) == 0:
            message = "No items in inventory"
            self.writeText(message, self.height // 2, self.width // 2 - len(message) // 2)
            return

        # draw subset of item names
        selectedItemPos = 0
        numRows = (self.height - 2) // 2
        for i in range(numRows):
            if i >= len(self.currentInventoryList):
                break
            itemIndex = (self.selectedIndex + i) % len(self.currentInventoryList)
            itemName = self.currentInventoryList[itemIndex][1]
            self.writeText(itemName, i * 2 + 1, 4, False, 'bold' if i == 0 else None)

        # draw cursor (constant position)
        self.setPixel('>', 1, 2)

        # draw description of selected item
        description = self.currentInventoryList[self.selectedIndex][2]
        descriptionCol = self.width // 3 + 3
        self.writeText(description, 1, descriptionCol, self.width - 2)

        # draw divider
        dividerCol = self.width // 3
        self.fillRect('|', dividerCol, 0, dividerCol + 1, self.height)
