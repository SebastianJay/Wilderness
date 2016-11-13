def test_assets_load_and_parse():
    from asset_loader import AssetLoader
    AssetLoader().loadAssets()
    # no exceptions
    assert True
