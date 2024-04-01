import warnings
from typing import ItemsView, KeysView, ValuesView


class Data:
    """
        Dict with comment field, that returns False even if the comment is present, but dict is empty
    """

    def __init__(self, data: dict | None = None, comment: str = ''):
        """Initialize the OrcaData class with data and an optional comment.

        Parameters:
            data (dict or None, optional): The main data dictionary to store the parsed data.
            comment (str, optional): An optional comment about the data. Defaults to ''.
        """
        # instead of data or {} it is better to use this to raise error if someone will try to use False or 0 as data
        data = {} if data is None else data

        if not isinstance(data, dict):
            raise TypeError(f'Data should be a dict not {type(data)}')
        self.data: dict = data
        """ The main data dictionary to store the parsed data. """
        self.comment: str = comment
        """ Comment about the data. """

    def keys(self) -> KeysView[str]:
        """Return a view object that displays a list of the dictionary's keys.

        Returns:
            KeysView[str]: A view object of the dictionary's keys.
        """
        return self.data.keys()

    def items(self) -> ItemsView[str, any]:
        """Return a view object that displays a list of the dictionary's key-value tuple pairs.

        Returns:
            ItemsView[str, any]: A view object of the dictionary's key-value pairs.
        """
        return self.data.items()

    def values(self) -> ValuesView[any]:
        """Return a view object that displays a list of the dictionary's values.

        Returns:
            ValuesView[any]: A view object of the dictionary's values.
        """
        return self.data.values()

    def __getitem__(self, key: str) -> dict | None:
        """Retrieve items from the data. Supports single keys, iterables of keys, and the ellipsis for all data.

        Parameters:
            key (str): The key or keys to retrieve data for. Supports single keys, iterables of keys, and the ellipsis.

        Returns:
            The value associated with the key, a dictionary for multiple keys, or None if the key doesn't exist.
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

    def __setitem__(self, key: str, value) -> None:
        """Set an item in the data dictionary.

        Parameters:
            key (str): The key for the item to set.
            value: The value to set for the given key.
        """
        self.data[key] = value

    def __contains__(self, key: str) -> bool:
        """Check if a key exists in the data.

        Parameters:
            key (str): The key to check in the data.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self.data

    def __delitem__(self, key: str) -> None:
        """Delete an item by key from the data dictionary.

        Parameters:
            key (str): The key of the item to delete.
        """
        del self.data[key]

    def get(self, key: str, default=None) -> None:
        """Safely retrieve an item by key, returning a default value if the key does not exist.

        Parameters:
            key (str): The key of the item to retrieve.
            default (optional): The default value to return if the key does not exist.

        Returns:
            The value associated with the key, or the default value.
        """
        return self.data.get(key, default)

    def __len__(self) -> int:
        """Return the number of items in the data dictionary.

        Returns:
            int: The number of items.
        """
        return len(self.data)

    def update(self, *args, **kwargs) -> None:
        """Update the dictionary with the key/value pairs from other, overwriting existing keys.

        Parameters:
            *args: A dictionary or an iterable of key/value pairs (as tuples or other iterables of length two).
            **kwargs: Additional key/value pairs to update the dictionary with.
        """
        self.data.update(*args, **kwargs)

    def pop(self, key: str, default=None) -> any:
        """Remove the specified key and return the corresponding value.

        If key is not found, default is returned if given, otherwise KeyError is raised.

        Parameters:
            key (str): The key to remove and return its value.
            default (optional): The value to return if the key is not found.

        Returns:
            The value for the key if key is in the dictionary, else default.
        """
        return self.data.pop(key, default)

    def popitem(self) -> tuple:
        """Remove and return a (key, value) pair from the dictionary.

        Pairs are returned in LIFO order. Raises KeyError if the dict is empty.

        Returns:
            tuple: The removed (key, value) pair.
        """
        return self.data.popitem()

    def clear(self) -> None:
        """Remove all items from the dictionary."""
        self.data.clear()

    def copy(self) -> dict:
        """Return a shallow copy of the dictionary.

        Returns:
            dict: A shallow copy of the dictionary.
        """
        return self.data.copy()

    def setdefault(self, key: str, default=None) -> any:
        """Return the value of the key if it is in the dictionary, otherwise insert it with a default value.

        Parameters:
            key (str): The key to check or insert in the dictionary.
            default (optional): The value to set if the key is not already in the dictionary.

        Returns:
            The value for the key if key is in the dictionary, else default.
        """
        return self.data.setdefault(key, default)

    def __iter__(self) -> iter:
        """Return an iterator over the keys of the data dictionary.

        Returns:
            An iterator over the keys.
        """
        return iter(self.data)

    def __str__(self) -> str:
        """Return a string representation of the OrcaData instance.

        Returns:
            str: A string summarizing the OrcaData contents and comment.
        """
        data_summary = ', '.join(
            f'`{key}`' for key in self.data)
        return f'OrcaData with items: {data_summary}. Comment: {self.comment}'
