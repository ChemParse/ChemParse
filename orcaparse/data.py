import warnings
from typing import ItemsView, KeysView, ValuesView


class Data:
    """
    A dictionary-like class with an additional comment field. It is designed to return `False` if the dictionary is empty, even if a comment is present.

    :param data: The main data dictionary to store the parsed data. Defaults to an empty dictionary if `None` is provided. An error is raised if the input is not a dictionary.
    :type data: dict, optional
    :param comment: An optional comment about the data. Defaults to an empty string.
    :type comment: str, optional

    :ivar data: The main data dictionary where parsed data is stored. This attribute is initialized with the `data` parameter.
    :vartype data: dict
    :ivar comment: A comment about the data. This attribute is initialized with the `comment` parameter.
    :vartype comment: str
    """

    def __init__(self, data: dict | None = None, comment: str = ''):
        """
        Initialize the Data class with `data` and an optional `comment`.

        :param data: The initial dictionary to store in the Data object. If `None`, an empty dictionary is used. The parameter must be a dictionary, otherwise a TypeError is raised.
        :type data: dict | None, optional
        :param comment: A text comment or note associated with the Data object.
        :type comment: str, optional
        """
        data = {} if data is None else data

        if not isinstance(data, dict):
            raise TypeError(
                f'Data should be a dict, not {type(data).__name__}')
        self.data: dict = data  # Keep typing here for clarity
        self.comment: str = comment  # Keep typing here for clarity

    def keys(self) -> KeysView[str]:
        """
        Return a view object that displays a list of the dictionary's keys.

        :return: A view object displaying the dictionary's keys.
        :rtype: KeysView[str]
        """
        return self.data.keys()

    def items(self) -> ItemsView[str, any]:
        """
        Return a view object that displays a list of the dictionary's key-value tuple pairs.

        :return: A view object displaying the dictionary's key-value pairs.
        :rtype: ItemsView[str, any]
        """
        return self.data.items()

    def values(self) -> ValuesView[any]:
        """
        Return a view object that displays a list of the dictionary's values.

        :return: A view object of the dictionary's values.
        :rtype: ValuesView[any]
        """
        return self.data.values()

    def __getitem__(self, key: str) -> any:
        """
        Retrieve items from the data. Supports single keys, iterables of keys, and the ellipsis for all data.

        :param key: The key or keys to retrieve data for. Supports single keys, iterables of keys, and the ellipsis.
        :type key: str | Iterable[str] | Ellipsis
        :return: The value associated with the key, a dictionary for multiple keys, or None if the key doesn't exist.
        :rtype: any | dict[str, any] | None
        """
        if key is ...:  # Handle the ellipsis (...) for returning all data
            return self.data

        if isinstance(key, (list, tuple, set)) and not isinstance(key, str):
            # Handle iterable keys, returning a dictionary with requested elements
            result = {}
            for item in key:
                try:
                    result[item] = self.data[item]
                except KeyError:
                    warnings.warn(
                        f"Key '{item}' not found in data.", UserWarning)
                    result[item] = None
            return result

        return self.data.get(key)  # Return None if the key doesn't exist

    def __setitem__(self, key: str, value: any) -> None:
        """
        Set an item in the data dictionary.

        :param key: The key for the item to set.
        :type key: str
        :param value: The value to set for the given key.
        """
        self.data[key] = value

    def __contains__(self, key: str) -> bool:
        """
        Check if a key exists in the data.

        :param key: The key to check in the data.
        :type key: str
        :return: True if the key exists, False otherwise.
        :rtype: bool
        """
        return key in self.data

    def __delitem__(self, key: str) -> None:
        """
        Delete an item by key from the data dictionary.

        :param key: The key of the item to delete.
        :type key: str
        """
        del self.data[key]

    def get(self, key: str, default: any = None) -> any:
        """
        Safely retrieve an item by key, returning a default value if the key does not exist.

        :param key: The key of the item to retrieve.
        :type key: str
        :param default: The default value to return if the key does not exist. Defaults to None.
        :return: The value associated with the key, or the default value.
        :rtype: any
        """
        return self.data.get(key, default)

    def __len__(self) -> int:
        """
        Return the number of items in the data dictionary.

        :return: The number of items.
        :rtype: int
        """
        return len(self.data)

    def update(self, *args, **kwargs) -> None:
        """
        Update the dictionary with the key/value pairs from other, overwriting existing keys.

        :param args: A dictionary or an iterable of key/value pairs (as tuples or other iterables of length two).
        :param kwargs: Additional key/value pairs to update the dictionary with.
        """
        self.data.update(*args, **kwargs)

    def pop(self, key: str, default=None) -> any:
        """
        Remove the specified key and return the corresponding value. If the key is not found, `default` is returned if provided, otherwise KeyError is raised.

        :param key: The key to remove and return its value.
        :type key: str
        :param default: The value to return if the key is not found. Defaults to None.
        :return: The value for the key if the key is in the dictionary, else `default`.
        :rtype: any
        """
        return self.data.pop(key, default)

    def popitem(self) -> tuple[str, any]:
        """
        Remove and return a (key, value) pair from the dictionary in LIFO order. Raises KeyError if the dictionary is empty.

        :return: The removed (key, value) pair.
        :rtype: tuple[str, any]
        """
        return self.data.popitem()

    def clear(self) -> None:
        """
        Remove all items from the dictionary.
        """
        self.data.clear()

    def copy(self) -> dict:
        """
        Return a shallow copy of the dictionary.

        :return: A shallow copy of the dictionary.
        :rtype: dict
        """
        return self.data.copy()

    def setdefault(self, key: str, default=None) -> any:
        """
        Return the value of the key if it is in the dictionary, otherwise insert it with a `default` value.

        :param key: The key to check or insert in the dictionary.
        :type key: str
        :param default: The value to set if the key is not already in the dictionary. Defaults to None.
        :return: The value for the key if the key is in the dictionary, else `default`.
        :rtype: any
        """
        return self.data.setdefault(key, default)

    def __iter__(self) -> iter:
        """
        Return an iterator over the keys of the data dictionary.

        :return: An iterator over the keys.
        :rtype: iter
        """
        return iter(self.data)

    def __str__(self) -> str:
        """
        Return a string representation of the Data instance, summarizing its contents and any comment.

        :return: A string summarizing the Data contents and comment.
        :rtype: str
        """
        data_summary = ', '.join(f'`{key}`' for key in self.data)
        return f'Data with items: {data_summary}. Comment: {self.comment}'
