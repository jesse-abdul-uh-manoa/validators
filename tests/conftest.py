def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "stricter_expected: Tests that describe desired future behavior for validators.uri",
    )
