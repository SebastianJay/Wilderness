"""
Definition of asset loader, which takes care of reading and parsing all files
within the assets/ directory.
"""
from interpreter import Interpreter
import os.path
import yaml

class AssetLoader:
    def __init__(self):
        self.assets = {}

    def loadAssets(self, path_to_folder):
        # This dictionary will hold the contents of asset files in the format:
        #   key = the files path, e.g. "assets/readme.txt"
        #   value = the conents of the file
        assets = {}

        # Go through each file in the specified dir and add contents to the dictionary
        for root, subdirs, files in os.walk(path_to_folder):
            for file_name in files:
                file_path = os.path.join(root,file_name)
                # Normalize the given path
                norm_path = os.path.normcase(os.path.normpath(file_path))
                with open(norm_path) as f:
                    assets[norm_path] = f.read()

        # Do parsing of any custom scripts and yaml
        parser = Interpreter()
        for path in assets:
            if path[-len('.ignore'):] == '.ignore':
                continue
            if os.path.normcase(os.path.normpath('assets/scripts')) in path:
                # replace string with parsed (string, BodyNode)[]
                assets[path] = parser.parseScript(assets[path])
            elif os.path.normcase(os.path.normpath('assets/config')) in path:
                # replace string with parsed Python dict
                assets[path] = yaml.load(assets[path])

        self.assets = assets

    def getAsset(self, dirname, name):
        norm_name = os.path.normcase(os.path.normpath(name))
        norm_dir = os.path.normcase(os.path.normpath(dirname))
        return self.assets[os.path.join(norm_dir, norm_name)]

    def getMap(self, name):
        return self.getAsset('assets/maps', name)

    def getArt(self, name):
        return self.getAsset('assets/art', name)

    def getScript(self, name):
        return self.getAsset('assets/scripts', name)

    def getConfig(self, name):
        return self.getAsset('assets/config', name)

if __name__ == '__main__':
    loader = AssetLoader()
    loader.loadAssets("assets/scripts")
