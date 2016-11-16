from window import Window
from asset_loader import AssetLoader
from global_vars import Globals

class InventoryWindow(Window):
    def __init__(self, w, h):
        print("INIT Executing")
        super().__init__(w, h)
        self.leftSection = (0, int(w / 3))
        self.rightSection = (int(w / 3), w-1)
        self.inventoryList = []
        self.numberOfLines = int((self.height - 3) / 2)
        self.selectedItemPos = 3
        self.selectedItem = None
        self.itemsdata = None
        self.coordsToFormat = []

    def load(self):
        self.itemsdata = AssetLoader().getConfig(Globals.ItemsConfigPath)
        for el in self.itemsdata.keys():
            self.inventoryList.append([el, self.itemsdata[el]["name"], self.itemsdata[el]["description"]])
        self.inventoryList.sort(key=lambda row: row[1].lower())
        self.selectedItem = self.inventoryList[self.selectedItemPos]

    def clear(self):
        for i in range(self.width):
            for j in range(self.height):
                self.pixels[j][i] = " "

    def border(self):
        for i in range(self.width):
            for j in range(self.height):

                if i in self.leftSection or i in self.rightSection:
                    self.pixels[j][i] = "|"

                if j == 0 or j == self.height-1:
                    self.pixels[j][i] = "-"

                if (i in self.leftSection or i in self.rightSection) and (j == 0 or j == self.height-1):
                    self.pixels[j][i] = "o"

    def update(self, timestep, keypress):
        if self.selectedItem is None:
            return
        if "Up" in keypress and self.selectedItem != self.inventoryList[0]:
            self.inventoryList = self.inventoryList[-1:] + self.inventoryList[:-1]
        if "Down" in keypress and self.selectedItem != self.inventoryList[len(self.inventoryList)-1]:
            self.inventoryList = self.inventoryList[1:] + self.inventoryList[0]

    def draw(self):
        if self.selectedItem is None:
            return self.pixels
        self.clear()
        self.border()
        for i in range(0, self.numberOfLines):
            try:
                if not i == self.selectedItemPos:
                    for j in range(len(self.inventoryList[i][1])):
                        self.pixels[i*2+2][6+j] = self.inventoryList[i][1][j]
                else:
                    for j in range(len(self.inventoryList[i][1]) + 4):
                        #self.formatting.append(("bold", (i * 2 + 2, 2 + j)))
                        #self.formatting.append(("yellow", (i * 2 + 2, 2 + j)))
                        if j < 3:
                            self.pixels[i * 2 + 2][2 + j] = ">"
                        elif j == 3:
                            self.pixels[i * 2 + 2][2 + j] = " "
                        else:
                            self.pixels[i*2+2][2 + j] = self.inventoryList[i][1][j-4]
            except IndexError:
                continue
        counter = 0
        descriptionHeight = 2
        description = self.selectedItem[2]
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
