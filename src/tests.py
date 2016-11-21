def test_assets_load_and_parse():
    from asset_loader import AssetLoader
    retval = AssetLoader().loadAssets()
    # loadAssets() returned success
    assert retval
