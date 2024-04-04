import pytest

import chemparse as chp


def test_initialization():
    data = {'a': 1, 'b': 2}
    od = chp.Data(data, "Test comment")
    assert od.data == data
    assert od.comment == "Test comment"


def test_getitem():
    od = chp.Data({'a': 1, 'b': 2})
    assert od['a'] == 1
    assert od['b'] == 2
    # returns None for missing keys
    assert od['c'] is None


def test_setitem():
    od = chp.Data({})
    od['a'] = 1
    assert od['a'] == 1


def test_len():
    od = chp.Data({'a': 1, 'b': 2, 'c': 3})
    assert len(od) == 3


def test_update():
    od = chp.Data({'a': 1})
    od.update({'b': 2})
    assert od['b'] == 2


def test_pop():
    od = chp.Data({'a': 1, 'b': 2})
    value = od.pop('a')
    assert value == 1
    assert 'a' not in od


def test_popitem():
    od = chp.Data({'a': 1, 'b': 2})
    key, value = od.popitem()
    assert key in ['a', 'b']
    assert value in [1, 2]
    assert len(od) == 1


def test_clear():
    od = chp.Data({'a': 1, 'b': 2})
    od.clear()
    assert len(od) == 0


def test_keys():
    od = chp.Data({'a': 1, 'b': 2})
    keys = od.keys()
    assert set(keys) == {'a', 'b'}


def test_values():
    od = chp.Data({'a': 1, 'b': 2})
    values = od.values()
    assert set(values) == {1, 2}


def test_items():
    od = chp.Data({'a': 1, 'b': 2})
    items = od.items()
    assert set(items) == {('a', 1), ('b', 2)}


def test_init_with_no_data():
    # Test initializing with no chp.Data provided
    od = chp.Data()
    assert od.data == {}
    assert od.comment == ''


def test_init_with_none_data():
    # Test initializing with None explicitly passed as chp.Data
    od = chp.Data(None)
    assert od.data == {}
    assert od.comment == ''


def test_init_with_non_dict_data():
    # Test initializing with a non-dict type for chp.Data, expecting a TypeError
    with pytest.raises(TypeError) as excinfo:
        od = chp.Data(data="not a dict")
    assert "Data should be a dict" in str(excinfo.value)


def test_boolean_evaluation():
    # Test that an empty .Data instance evaluates to False
    empty_od = chp.Data()
    assert not empty_od, "Empty Data instance should evaluate to False"

    # Test that a non-empty Data instance evaluates to True
    non_empty_od = chp.Data({'key': 'value'})
    assert non_empty_od, "Non-empty Data instance should evaluate to True"
