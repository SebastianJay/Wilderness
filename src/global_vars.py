"""
Contains variables that should be accessible from any scope
"""

class Globals:
    NumCols = 120
    NumRows = 35
    FontName = 'Consolas'
    DefaultFontSize = 12
    DefaultUseStyling = True
    DefaultScrollThreshold = 0.025
    Timestep = 0.033
    IsDev = True
    AssetsRootPath = 'assets'
    SavePaths = [
        'savefiles/sav0.txt',
        'savefiles/sav1.txt',
        'savefiles/sav2.txt',
        'savefiles/sav3.txt',
    ]
    SettingsPath = 'settings.txt'
    MapsPaths = [
        ('lore_map.txt', 'lore_map_color_mask.txt', 'lore_map_travel_mask.txt'),
        ('kipp_map.txt', 'kipp_map_color_mask.txt', 'kipp_map_travel_mask.txt'),
    ]
    AreasConfigPath = 'areas.yml'
    ItemsConfigPath = 'items.yml'
    KeybindingsConfigPath = 'keybindings.yml'
    FragmentsConfigPath = 'fragments.yml'
    IconFilePathWin = 'icon.ico'
    IconFilePathUnix = 'icon.xbm'
    CmdMaxLength = 48
    NameMaxLength = 8
    AlphaMax = 8        # should be power of two
