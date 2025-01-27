import pytest

from pychemparse.regex_settings import (DEFAULT_ORCA_REGEX_FILE, RegexBlueprint,
                                        RegexRequest, RegexSettings)


@pytest.fixture
def regex_settings():
    return RegexSettings(settings_file=DEFAULT_ORCA_REGEX_FILE)


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
    assert all(isinstance(item, RegexRequest)
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


@pytest.fixture
def sample_blueprint():
    order = ['TestBlock1', 'TestBlock2']
    pattern_structure = {
        'beginning': '^Test ',
        'ending': ' end$',
        'flags': ['MULTILINE']
    }
    pattern_texts = {
        'TestBlock1': 'Content for Block1',
        'TestBlock2': 'Content for Block2'
    }
    comment = 'Sample blueprint for testing'
    return RegexBlueprint(order, pattern_structure, pattern_texts, comment)


def test_regex_blueprint_to_list(sample_blueprint):
    # Verify that the to_list method generates the expected list of RegexRequest objects
    request_list = sample_blueprint.to_list()
    assert len(request_list) == len(sample_blueprint.order)
    for request, name in zip(request_list, sample_blueprint.order):
        assert isinstance(request, RegexRequest)
        assert request.p_subtype == name
        assert request.comment == sample_blueprint.comment


def test_regex_blueprint_validate_configuration(sample_blueprint):
    # Verify that the configuration validation of blueprint passes without errors
    try:
        sample_blueprint.validate_configuration()
    except ValueError as e:
        pytest.fail(f"Blueprint configuration validation failed: {e}")


def test_regex_blueprint_to_dict_structure(sample_blueprint):
    # Verify the structure of the dictionary representation of a blueprint
    blueprint_dict = sample_blueprint.to_dict()
    assert 'order' in blueprint_dict
    assert 'pattern_structure' in blueprint_dict
    assert 'pattern_texts' in blueprint_dict
    assert 'comment' in blueprint_dict
    assert blueprint_dict['comment'] == sample_blueprint.comment
    for name in blueprint_dict['order']:
        assert name in blueprint_dict['pattern_texts']


def test_regex_blueprint_length(sample_blueprint):
    # Verify that the length of the blueprint corresponds to the number of items in 'order'
    assert len(sample_blueprint) == len(sample_blueprint.order)


def test_regex_blueprint_tree_structure(sample_blueprint):
    # Verify the tree structure representation of a blueprint
    tree_str = sample_blueprint.tree()
    assert isinstance(tree_str, str)
    assert "RegexBlueprint:" in tree_str
    for name in sample_blueprint.order:
        assert name in tree_str
