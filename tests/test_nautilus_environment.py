import nautilus_trader


def test_nautilus_trader_is_available():
    version = nautilus_trader.__version__
    assert version
    assert version.startswith("1.")