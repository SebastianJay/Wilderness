"""
Definition of asset loader, which takes care of reading and parsing all files
within the assets/ directory.
"""
from lang_parser import Parser
from global_vars import Globals
import os.path
import json
import yaml
import codecs
import traceback

def joinAndNorm(*args):
    return os.path.normcase(os.path.normpath(os.path.join(*args)))

class AssetLoader:
    # Python singleton implementation adapted from
    # http://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    class __AssetLoader:
        def __init__(self):
            # maps path to asset
            self.assets = {}
            # maps path to save file (as dict, not game state)
            self.savefiles = {}
            # persistent game settings objects
            self.settings = None
            # string containing root of assets folder
            self.root_path = ''
            # maps readable item name to item ID
            self.reverseItem = {}
            # maps readable room name to room ID
            self.reverseRoom = {}
            # indicates if asset loading happened
            self.isLoaded = False

        def loadAssets(self):
            # if assets already in memory do not reload
            if self.isLoaded:
                return

            # set root to assets for later reference
            self.root_path = Globals.AssetsRootPath

            # This dictionary will hold the contents of asset files in the format:
            #   key = the files path, e.g. "assets/readme.txt"
            #   value = the conents of the file
            assets = {}

            # Returns whether all files can read and parse successfully
            success_flag = True

            # recognized filename extensions
            whitelist_ext = ['.txt', '.wtxt', '.yml']
            # Go through each file in the specified dir and add contents to the dictionary
            for root, subdirs, files in os.walk(self.root_path):
                for file_name in files:
                    try:
                        # Normalize the given path
                        norm_path = joinAndNorm(root, file_name)
                        # Check that filename ends with recognized extension
                        ext_not_valid = True
                        for ext in whitelist_ext:
                            if len(norm_path) >= len(ext) and norm_path[-len(ext):] == ext:
                                ext_not_valid = False
                                break
                        if ext_not_valid:
                            continue
                        # Store file text into dictionary
                        with codecs.open(norm_path, "r", "utf-8") as f:
                            assets[norm_path] = f.read().replace('\r\n', '\n').replace('\r', '\n')
                    except:
                        success_flag = False

            # Do parsing of any custom scripts and yaml
            parser = Parser()  # instantiate parser on the fly
            for path in assets:
                try:
                    if joinAndNorm(self.root_path, 'scripts') in path:
                        if 'fragments' in path:
                            # replace string with parsed BodyNode
                            assets[path] = parser.parseScriptFragment(assets[path])
                        else:
                            # replace string with parsed BehaviorNode
                            assets[path] = parser.parseScript(assets[path])
                    elif joinAndNorm(self.root_path, 'config') in path:
                        # replace string with parsed Python dict
                        assets[path] = yaml.load(assets[path])
                    elif joinAndNorm(self.root_path, 'maps') in path:
                        # replace string with split string
                        assets[path] = assets[path].split('\n')
                except:
                    success_flag = False
                    if Globals.IsDev:
                        print(path)
                        traceback.print_exc()

            self.assets = assets

            # construct reverse item mapping
            itemsConfig = self.getConfig(Globals.ItemsConfigPath)
            for item in itemsConfig:
                self.reverseItem[itemsConfig[item]['name'].lower()] = item

            # construct reverse room mapping
            areasConfig = self.getConfig(Globals.AreasConfigPath)
            for area in areasConfig:
                self.reverseRoom[area] = {}
                roomsConfig = self.getConfig(areasConfig[area]['roomsConfig'])
                for room in roomsConfig:
                    self.reverseRoom[area][roomsConfig[room]['name'].lower()] = room

            self.isLoaded = True
            return success_flag

        def loadSaves(self):
            self.savefiles = {}
            for path in Globals.SavePaths:
                normPath = joinAndNorm(path)
                if os.path.exists(normPath):
                    with open(normPath, 'r') as f:
                        self.savefiles[normPath] = json.loads(f.read())

        def loadSettings(self):
            normPath = joinAndNorm(Globals.SettingsPath)
            if os.path.exists(normPath):
                with open(normPath, 'r') as f:
                    self.settings = json.loads(f.read())

        def writeSettings(self, obj):
            normPath = joinAndNorm(Globals.SettingsPath)
            with open(normPath, 'w') as f:
                f.write(json.dumps(obj))
            self.settings = obj # store the settings just written

        def freeSaveFileInd(self):
            # collapse all save path names into a big string
            searchString = ''.join(self.savefiles.keys())
            # pick out missing indices in that string
            for i in range(len(Globals.SavePaths)):
                if str(i) not in searchString:
                    return i
            return -1

        def deleteSave(self, index):
            # search for index in string name of save path
            for i, path in enumerate(Globals.SavePaths):
                if str(i) in path:
                    normPath = joinAndNorm(path)
                    if os.path.exists(normPath):
                        os.remove(normPath)
                        del self.savefiles[normPath]
                    break

        def lenSaveFiles(self):
            return len(self.savefiles)

        def getMap(self, name):
            return self.assets[joinAndNorm(self.root_path, 'maps', name)]

        def getArt(self, name):
            return self.assets[joinAndNorm(self.root_path, 'art', name)]

        def getScript(self, name):
            return self.assets[joinAndNorm(self.root_path, 'scripts', name)]

        def getScriptFragment(self, name):
            return self.assets[joinAndNorm(self.root_path, 'scripts', 'fragments', name)]

        def getConfig(self, name):
            return self.assets[joinAndNorm(self.root_path, 'config', name)]

        def getMusicPath(self, name):
            fname = self.getConfig(Globals.MusicConfigPath)[name]
            return joinAndNorm(self.root_path, 'music', fname)

        def getSave(self, name):
            if joinAndNorm(name) in self.savefiles:
                return self.savefiles[joinAndNorm(name)]
            return None

        def getSettings(self):
            return self.settings

        def reverseItemLookup(self, name):
            name = name.lower()
            if name in self.reverseItem:
                return self.reverseItem[name]
            return ''

        def reverseRoomLookup(self, name, area):
            name = name.lower()
            # area is an ID, name is the readable room name
            if area in self.reverseRoom:
                if name in self.reverseRoom[area]:
                    return self.reverseRoom[area][name]
            return ''

    instance = None
    def __new__(cls):
        if not AssetLoader.instance:
            AssetLoader.instance = AssetLoader.__AssetLoader()
        return AssetLoader.instance
    def __getattr__(self, name):
        return getattr(self.instance, name)
    def __setattr__(self, name):
        return setattr(self.instance, name)

if __name__ == '__main__':
    loader = AssetLoader()
    loader.loadAssets()
