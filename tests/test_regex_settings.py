from orcaparse.regex_settings import RegexSettings, DEFAULT_REGEX_FILE
import pytest


@pytest.fixture
def regex_settings():
    return RegexSettings(settings_file=DEFAULT_REGEX_FILE)


def test_regex_settings_initialization(regex_settings):
    # Verify that the instance is initialized
    assert regex_settings is not None


def test_regex_settings_items_not_empty(regex_settings):
    # Verify that `items` is not None or empty
    assert regex_settings.items is not None
    assert len(regex_settings.items) > 0


def test_regex_settings_order_not_empty(regex_settings):
    # Verify that `order` is not None or empty
    assert regex_settings.order is not None
    assert len(regex_settings.order) > 0


def test_regex_settings_order_matches_items(regex_settings):
    # Verify that each item in `order` has a corresponding entry in `items`
    for name in regex_settings.order:
        assert name in regex_settings.items


def test_regex_settings_validate_configuration(regex_settings):
    # Verify that the configuration validation passes without raising an error or warning
    try:
        regex_settings.validate_configuration()
    except Exception as e:
        pytest.fail(f"Configuration validation failed: {e}")


def test_regex_settings_to_list_not_empty(regex_settings):
    # Verify that the list conversion is not empty and contains expected objects
    items_list = regex_settings.to_list()
    assert items_list is not None
    assert len(items_list) > 0
    from orcaparse.regex_settings import RegexRequest
    assert all(isinstance(item, (RegexRequest, RegexSettings))
               for item in items_list)


def test_regex_settings_to_dict_structure(regex_settings):
    # Verify the structure of the dictionary representation
    settings_dict = regex_settings.to_dict()
    assert isinstance(settings_dict, dict)
    assert "order" in settings_dict
    assert isinstance(settings_dict["order"], list)
    for name in settings_dict["order"]:
        assert name in settings_dict
        item = settings_dict[name]
        assert isinstance(item, dict)


def test_regex_settings_save_as_json(tmp_path, regex_settings):
    # Verify that settings can be saved as a JSON file
    file_path = tmp_path / "test_regex_settings.json"
    regex_settings.save_as_json(str(file_path))
    assert file_path.exists()
    assert file_path.stat().st_size > 0
