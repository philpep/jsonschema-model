# -*- coding: utf8 -*-

from __future__ import unicode_literals

import copy
import pytest
from jsonschema_model import model_factory


@pytest.fixture
def Model():
    # evil nested schema
    schema = {
        "name": "Model",
        "type": "object",
        "properties": {
            "foo": {"type": "string"},
            "bar": {"type": "array", "items": {"type": "string"}},
        }
    }
    orig = copy.deepcopy(schema)
    schema["properties"]["zaz"] = orig
    schema["properties"]["qux"] = {"type": "array", "items": orig}
    return model_factory(schema)


def test_init(Model):
    obj = Model(foo="bar")
    assert obj == {"foo": "bar"}


def test_error(Model):
    obj = Model()
    with pytest.raises(AttributeError):
        obj.attr
    with pytest.raises(KeyError):
        obj["attr"]


def test_basic(Model):
    obj = Model()
    assert obj.foo is None
    assert obj == {}

    obj.foo = None
    assert obj == {"foo": None}

    obj.foo = "bar"
    assert obj == {"foo": "bar"}

    obj["foo"] = "zaz"
    assert obj == {"foo": "zaz"}


def test_simple_array(Model):
    obj = Model()
    obj.bar.add("foo")
    obj.bar.add("bar")
    assert obj == {"bar": ["foo", "bar"]}


def test_nested(Model):
    obj = Model()
    assert obj.zaz == {}
    assert obj == {"zaz": {}}
    obj["zaz"].foo = "bar"
    assert obj == {"zaz": {"foo": "bar"}}


def test_nested_array(Model):
    obj = Model()
    obj.qux.add(foo="bar")
    assert obj == {"qux": [{"foo": "bar"}]}
