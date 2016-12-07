from window import Window
from asset_loader import AssetLoader
from global_vars import Globals
from game_state import GameState, GameMode

class InventoryWindow(Window):
    def __init__(self, w, h):
        super().__init__(w, h)
        GameState().onInventoryChange += self.inventoryChangeHandler()

    def reset(self):
        self.inventoryList = []
        self.currentInventoryList = []
        #self.formatting.append(("bold_yellow", ((self.selectedItemPos*2+2)*self.width+1, (self.selectedItemPos*2+2)*self.width+int(self.width/3)-1)))
        self.startIndex = 0
        self.index = lambda x: (x + self.startIndex) % len(self.currentInventoryList)

    def inventoryChangeHandler(self):
        def _inventoryChangeHandler(*args, **kwargs):
            # refresh currentInventoryList by scanning for all items in Game State inventory
            currentInventoryList = []
            for itemdata in self.inventoryList:
                # TODO refactor for efficiency
                if itemdata[0] in GameState().inventory:
                    currentInventoryList.append(itemdata)
            self.currentInventoryList = currentInventoryList
        return _inventoryChangeHandler

    def load(self):
        itemsdata = AssetLoader().getConfig(Globals.ItemsConfigPath)
        for el in itemsdata.keys():
            self.inventoryList.append([el, itemsdata[el]["name"], itemsdata[el]["description"]])
        self.inventoryList.sort(key=lambda row: row[1].lower())

    def update(self, timestep, keypress):
        for key in keypress:
            if len(self.currentInventoryList) > 0:
                if key == "Up":
                    self.startIndex = (self.startIndex - 1) % len(self.currentInventoryList)
                elif key == "Down":
                    self.startIndex = (self.startIndex + 1) % len(self.currentInventoryList)
            if key == "Return":
                GameState().gameMode = GameMode.inAreaCommand

    def draw(self):
        self.clear()
        if len(self.currentInventoryList) == 0:
            message = "No items in inventory"
            for j in range(len(message)):
                self.pixels[self.height//2][self.width//2 - len(message)//2 + j] = message[j]
            return self.pixels

        selectedItemPos = 0
        numRows = (self.height - 3) // 2
        for i in range(numRows):
            if i >= len(self.currentInventoryList):
                break
            if i == selectedItemPos:
                self.pixels[((i+2) % numRows) * 2 + 2][2] = ">"
            for j in range(len(self.currentInventoryList[self.index(i)][1])):
                self.pixels[((i+2) % numRows) * 2 + 2][6+j] = self.currentInventoryList[self.index(i)][1][j]

        counter = 0
        descriptionHeight = 2
        description = self.currentInventoryList[self.index(selectedItemPos)][2]
        descriptionList = description.split(" ")

        for el in descriptionList:
            if counter + len(el) >= int(2 * self.width / 3 - 3):
                counter = 0
                descriptionHeight += 1
            for letter in el:
                self.pixels[descriptionHeight][int(self.width / 3) + 3 + counter] = letter
                counter += 1
            self.pixels[descriptionHeight][int(self.width / 3) + 3 + counter] = " "
            counter += 1

        return self.pixels

if __name__ == '__main__':
    a = InventoryWindow(100, 17)
    a.load()
    a.update()
    a.draw()
    a.debugDraw()
