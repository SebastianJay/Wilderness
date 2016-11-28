This is a special folder within `assets/scripts` that allows for partial scripts (fragments) which get repeated in game to be specified only once; they can be "imported" with a special command.

Create the fragment file in this directory, add an entry to `config/fragments.yml` to map the camel case fragment name to the readable file path relative to this directory, and then in the script use a statement like `$fragment_fragmentName`. On runtime the game will execute the scripts from the fragment files.

Fragments may contain any functions and formatting that a normal script can have... but be careful when using `$fragment` itself, as a cycle (circular dependency) can result in game hanging/crashing.
