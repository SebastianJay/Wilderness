# World Map

The game will have several areas placed on two world maps (one for each protagonist). In the world map view, the player can travel across two axes using the arrow keys. Some tiles may be impassable, or some may require certain progress to be made (e.g. for Lore, having a plane).

To construct a world map we will have three different text files that act as different layers:

## Visible Mask

The actual characters that appear on screen. If there are *R* rows and *C* columns in the map, then the text file will have *R* lines that are *C* characters each. Imagine a map containing forests (`^`), plains (`-`) and water (`~`) -- then a 3 row by 6 column map might look like:

```
^^--~~
--^-~~
-^-~~~
```

The player will occupy one of the tiles at a time, with a reserved character as an indicator (e.g. `@`). That indicator char will replace the appropriate char on the visible mask to show the player's position.

## Color Mask

The colors that correspond to the characters in the visible mask. For example, forest tiles might be green, and plains could be brown, and water could be blue. We will define a scheme that maps chars to colors.

* `r` - red
* `g` - green
* `b` - blue
* `y` - yellow
* `o` - orange
* `v` - purple
* `p` - pink
* `c` - cyan
* `w` or empty space - white
* `n` - brown

For the above map, the color mask might look like:

```
ggnnbb
nngnbb
ngnbbb
```

## Travel Mask

Some tiles on the map might be impassable (that is, the player cannot travel over them), or they might serve as entrances to areas. We will define a scheme that maps chars to their functional purpose in the game.

* `0` - always passable tiles
* `1` - always impassable tiles
* `2` and onward - passable under a certain condition; to be defined
* `a` and onward - entrance to an area, to be defined

For the above map, if we say that we cannot travel on water but can travel everywhere else, the travel mask might look like:

```
000011
000011
000111
```
