"""
Definition of asset loader, which takes care of reading and parsing all files
within the assets/ directory.
"""
import os.path

class AssetLoader:
    def __init__(self):
        pass

    def loadAssets(self, path_to_folder):
        # This dictionary will hold the contents of asset files in the format:
        #   key = the files path, e.g. "assets/readme.txt"
        #   value = the conents of the file
        assets = {}

        # Go through each file in the specified dir and add contents to the dictionary
        for root, subdirs, files in os.walk(path_to_folder):
            for file_name in files:
                file_path = os.path.join(root,file_name)
                with open(file_path) as f:
                    assets[file_path] = f.read()
        return assets

if __name__ == '__main__':
    loader = AssetLoader()
    print(loader.loadAssets("../assets/scripts"))
