#!/usr/bin/env python
# -*- coding: utf-8 -*-

import copy
import warnings


class Storage(dict):
    """
    from web.py
    对字典进行扩展，使其支持通过 dict.a形式访问以代替dict['a']
    """

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __setattr__(self, key, value):
        self[key] = value

    def __delattr__(self, key):
        try:
            del self[key]
        except KeyError as k:
            raise AttributeError(k)

    def __repr__(self):
        return '<Storage ' + dict.__repr__(self) + '>'

class SortedDict(dict):
    """
    A dictionary that keeps its keys in the order in which they're inserted.
    """

    def __new__(cls, *args, **kwargs):
        instance = super(SortedDict, cls).__new__(cls, *args, **kwargs)
        instance.keyOrder = []
        return instance

    def __init__(self, data=None):
        if data is None or isinstance(data, dict):
            data = data or []
            super(SortedDict, self).__init__(data)
            self.keyOrder = list(data) if data else []
        else:
            super(SortedDict, self).__init__()
            super_set = super(SortedDict, self).__setitem__
            for key, value in data:
                # Take the ordering from first key
                if key not in self:
                    self.keyOrder.append(key)
                    # But override with last value in data (dict() does this)
                super_set(key, value)

    def __deepcopy__(self, memo):
        return self.__class__([(key, copy.deepcopy(value, memo))
                               for key, value in self.items()])

    def __copy__(self):
        # The Python's default copy implementation will alter the state
        # of self. The reason for this seems complex but is likely related to
        # subclassing dict.
        return self.copy()

    def __setitem__(self, key, value):
        if key not in self:
            self.keyOrder.append(key)
        super(SortedDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        super(SortedDict, self).__delitem__(key)
        self.keyOrder.remove(key)

    def __iter__(self):
        return iter(self.keyOrder)

    def __reversed__(self):
        return reversed(self.keyOrder)

    def pop(self, k, *args):
        result = super(SortedDict, self).pop(k, *args)
        try:
            self.keyOrder.remove(k)
        except ValueError:
            # Key wasn't in the dictionary in the first place. No problem.
            pass
        return result

    def popitem(self):
        result = super(SortedDict, self).popitem()
        self.keyOrder.remove(result[0])
        return result

    def _iteritems(self):
        for key in self.keyOrder:
            yield key, self[key]

    def _iterkeys(self):
        for key in self.keyOrder:
            yield key

    def _itervalues(self):
        for key in self.keyOrder:
            yield self[key]

    items = _iteritems
    keys = _iterkeys
    values = _itervalues

    def update(self, dict_):
        for k, v in dict_.iteritems():
            self[k] = v

    def setdefault(self, key, default):
        if key not in self:
            self.keyOrder.append(key)
        return super(SortedDict, self).setdefault(key, default)

    def value_for_index(self, index):
        """Returns the value of the item at the given zero-based index."""
        # This, and insert() are deprecated because they cannot be implemented
        # using collections.OrderedDict (Python 2.7 and up), which we'll
        # eventually switch to
        warnings.warn(
            "SortedDict.value_for_index is deprecated", PendingDeprecationWarning,
            stacklevel=2
        )
        return self[self.keyOrder[index]]

    def insert(self, index, key, value):
        """Inserts the key, value pair before the item with the given index."""
        warnings.warn(
            "SortedDict.insert is deprecated", PendingDeprecationWarning,
            stacklevel=2
        )
        if key in self.keyOrder:
            n = self.keyOrder.index(key)
            del self.keyOrder[n]
            if n < index:
                index -= 1
        self.keyOrder.insert(index, key)
        super(SortedDict, self).__setitem__(key, value)

    def copy(self):
        """Returns a copy of this object."""
        # This way of initializing the copy means it works for subclasses, too.
        return self.__class__(self)

    def __repr__(self):
        """
        Replaces the normal dict.__repr__ with a version that returns the keys
        in their sorted order.
        """
        return '{%s}' % ', '.join(['%r: %r' % (k, v) for k, v in self.iteritems()])

    def clear(self):
        super(SortedDict, self).clear()
        self.keyOrder = []

def _dict_to_storage_check_list(from_list):
    for i,item in enumerate(from_list):
        if type(item) == dict:
            from_list[i] = dict_to_storage(item)
        elif type(item) == list:
            from_list[i] = _dict_to_storage_check_list(item)
    return from_list

def dict_to_storage(from_dict):
    """
        >>> b = {'a': [ [ [{'a3':3}]]]}
        >>> a = {'a': [ [ [{'a3':3, 'b': b}]]]}
        dict_to_storage(a).a[0][0][0].b.a[0][0][0].a3 == 3

        Returns:
            [type] -- [description]
    """
    for k in from_dict.keys():
        if type(from_dict[k]) == dict:
            from_dict[k] = dict_to_storage(from_dict[k])
        elif type(from_dict[k]) == list:
            from_dict[k] = _dict_to_storage_check_list(from_dict[k])
    return Storage(from_dict)
