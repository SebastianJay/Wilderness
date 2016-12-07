"""
Contains variables that should be accessible from any scope
"""

class Globals:
    XRes = 1280
    YRes = 720
    NumCols = 120
    NumRows = 35
    Timestep = 0.033
    FontName = 'Consolas'
    FontSize = 14
    IsDev = True
    AssetsRootPath = 'assets'
    SavePaths = [
        'savefiles/sav0.txt',
        'savefiles/sav1.txt',
        'savefiles/sav2.txt',
        'savefiles/sav3.txt',
    ]
    MapsPaths = [
        ('kipp_map.txt', 'kipp_map_color_mask.txt', 'kipp_map_travel_mask.txt'),
        ('kipp_map.txt', 'kipp_map_color_mask.txt', 'kipp_map_travel_mask.txt'),
    ]
    InAreaPaths = [
        ('inarea_aspire_map.txt', 'aspire.yml'),
    ]
    AreasConfigPath = 'areas.yml'
    ItemsConfigPath = 'items.yml'
    KeybindingsConfigPath = 'keybindings.yml'
    FragmentsConfigPath = 'fragments.yml'
    IconFilePathWin = 'assets/art/icon.ico'
    IconFilePathUnix = 'assets/art/icon.xbm'
    CmdMaxLength = 48
    NameMaxLength = 8
    AlphaMax = 8        # should be power of two
