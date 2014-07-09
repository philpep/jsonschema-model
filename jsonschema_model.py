# -*- coding: utf8 -*-

from __future__ import unicode_literals


class Array(list):
    Model = None

    def add(self, *args, **kwargs):
        if self.Model is not None:
            obj = self.Model(*args, **kwargs)
        else:
            obj = args[0]
        self.append(obj)
        return obj


class Model(dict):
    schema = None

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            schema = self.schema["properties"].get(key)
            if schema is None:
                raise KeyError(key)

            if schema["type"] == "object":
                value = model_factory(schema)()
                dict.__setitem__(self, key, value)
                return value
            elif schema["type"] == "array":
                if schema["items"]["type"] == "object":
                    ArrayModel = model_factory(schema["items"])
                else:
                    ArrayModel = None
                value = type(str("Array"), (Array,), {"Model": ArrayModel})()
                dict.__setitem__(self, key, value)
                return value
            else:
                return None

    def __getattr__(self, key):
        try:
            return self.__getitem__(key)
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        return self.__setitem__(key, value)


def model_factory(schema):
    return type(str(schema["name"]), (Model,), {"schema": schema})
