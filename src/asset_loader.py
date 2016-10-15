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

    def readFormat(self, text):
        #index_of_at will track the last instance of the "@" character in the text
        index_of_at = 0
        index_close_bracket = -1
        previous_close_bracket = -1
        index_open_bracket = -1
        formatting = {} # dictionary of formation {string : tuple} of formatters and where they apply
        text_without_formatters = ""

        #While there are remaining "@"s in the string, format into a langNode
        while (text.find("@", index_of_at) != -1):
            index_of_at = text.find("@", index_of_at)
            index_open_bracket = text.find("{", index_of_at)
            index_close_bracket = text.find("}", index_of_at)

            #if no close or open bracket exists, exit the method and return error message
            if (index_open_bracket == -1):
                print("The formatter is missing an openning bracket: {")
                return {}
            if (index_close_bracket == -1):
                print("The formatter is missing an openning bracket: }")
                return {}
            formatter = text[index_of_at + 1 :index_open_bracket]               # @formatter{formatted_test}
            formatted_text = text[index_open_bracket + 1 : index_close_bracket]
            # text_without_formatters will hold the text with the @formatter{formattted_text} replaced with just formatted_text

            text_without_formatters += text[previous_close_bracket + 1 : index_of_at]
            text_without_formatters += formatted_text

            print("index_of_at: " + str(index_of_at))
            print("index_open_bracket: " + str(index_open_bracket))
            print("index_close_bracket: " + str(index_close_bracket))
            print("formatter: " + formatter)
            print("formatted_text: " + formatted_text + "\n")

            #LangNode(text, {formatter1 : [(index1,index2), (index3, index4)], formatter2 : ...})
            #Seen above is the format we ultimately want to return
            #A LangNode, text as the key, a dictionary linking formatters to a list of tuples of all indexes of that formattter as the avlue

            # Remember where in the text_without_formatters string each formatter applies
            if formatter not in formatting:
                formatting[formatter] = [(len(text_without_formatters)-len(formatted_text), len(text_without_formatters) -1)]
            else:
                formatting[formatter].append((len(text_without_formatters)-len(formatted_text), len(text_without_formatters) -1))

            previous_close_bracket = index_close_bracket # remember where the previous } was
            index_of_at = index_of_at + 1   # start searching for the next @ after the previous @

        LangNode = (text_without_formatters, formatting)
        return LangNode


if __name__ == '__main__':
    loader = AssetLoader()
    print(loader.loadAssets("assets/scripts"))
    print(loader.readFormat("Hello @red{there}, friend. How are @bold{you} doing?"))
    print(loader.readFormat("@blue{This} is blue. But @italics{this} is italicized. And @blue{this one} is also blue."))
