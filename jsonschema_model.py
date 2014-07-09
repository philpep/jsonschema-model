# -*- coding: utf8 -*-

from __future__ import unicode_literals


class Array(list):
    Model = None

    def __init__(self, *args, **kwargs):
        list.__init__(self)
        for e in list(*args, **kwargs):
            self.add(e)

    def add(self, *args, **kwargs):
        if self.Model is not None:
            obj = self.Model(*args, **kwargs)
        else:
            obj = args[0]
        self.append(obj)
        return obj


class Model(dict):
    schema = None

    def __init__(self, *args, **kwargs):
        dict.__init__(self)
        for k, v in dict(*args, **kwargs).items():
            self.__setitem__(k, v)

    def __setitem__(self, key, value):
        try:
            model = self._get_model(key)
        except KeyError:
            pass
        else:
            if model is not None:
                value = model(value)
        dict.__setitem__(self, key, value)

    def _get_model(self, key):
        schema = self.schema["properties"].get(key)

        if schema is None:
            raise KeyError(key)

        if schema["type"] == "object":
            return model_factory(schema)
        elif schema["type"] == "array":
            if schema["items"]["type"] == "object":
                ArrayModel = model_factory(schema["items"])
            else:
                ArrayModel = None
            return type(str("Array"), (Array,), {"Model": ArrayModel})
        else:
            return None

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            model = self._get_model(key)
            if model is not None:
                value = model()
                dict.__setitem__(self, key, value)
                return value

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)


def model_factory(schema):
    return type(str(schema["name"]), (Model,), {"schema": schema})
