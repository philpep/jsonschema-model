# -*- coding: utf8 -*-

from __future__ import unicode_literals

import copy
import pytest
from jsonschema_model import model_factory, MultipleItemFound


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


def test_update_array(Model):
    obj = Model()
    obj.update(bar=["foo"])
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


def test_init_fill(Model):
    data = {
        "foo": "a",
        "bar": ["b", "c"],
        "zaz": {
            "bar": ["d"],
        },
        "qux": [{"foo": "e"}, {"bar": ["f"]}],
    }
    obj = Model(**data)
    assert obj.foo == "a"
    assert obj.bar == ["b", "c"]
    assert obj.zaz.bar == ["d"]
    assert obj.qux[0].foo == "e"
    assert obj.qux[1].bar == ["f"]
    assert obj == data

    g = obj.qux.add(foo="g", bar=["h"])
    assert obj.qux[2] == {"foo": "g", "bar": ["h"]}
    g.bar.add("i")
    assert obj.qux[2] == {"foo": "g", "bar": ["h", "i"]}


def test_name():
    model = model_factory({
        "type": "object",
        "name": "FooObject",
        "properties": {
            "foo": {
                "type": "object",
                "properties": {
                    "foo": {"type": "string"},
                },
            },
        },
    })
    obj = model(foo={"foo": "bar"})
    assert obj.__class__.__name__ == "FooObject"
    assert obj.foo.__class__.__name__ == "Object"


def test_get_or_create_invalid():
    model = model_factory({
        "type": "object",
        "properties": {
            "l": {"type": "array", "items": {"type": "string"}},
        },
    })
    obj = model()
    with pytest.raises(RuntimeError):
        obj.l.get_or_create("foo", "bar")
    with pytest.raises(RuntimeError):
        obj.l.get_or_create("foo", a="bar")
    with pytest.raises(MultipleItemFound):
        obj.l.add("foo")
        obj.l.add("foo")
        obj.l.get_or_create("foo")


def test_get_or_create_simple():
    model = model_factory({
        "type": "object",
        "properties": {
            "l": {"type": "array", "items": {"type": "string"}},
        },
    })
    obj = model()
    obj.l.get_or_create("foo")
    obj.l.get_or_create("foo")
    assert obj == {"l": ["foo"]}
    obj.l.get_or_create("bar")
    assert obj == {"l": ["foo", "bar"]}


def test_get_or_create_object():
    model = model_factory({
        "type": "object",
        "properties": {
            "l": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "a": {"type": "string"},
                        "b": {"type": "string"},
                    },
                },
            },
        },
    })
    obj = model()
    obj.l.get_or_create(a="foo")
    assert obj == {"l": [{"a": "foo"}]}
    obj.l.get_or_create(a="foo")
    assert obj == {"l": [{"a": "foo"}]}
    obj.l.get_or_create(a="foo", b="bar")
    assert obj == {"l": [{"a": "foo"}, {"a": "foo", "b": "bar"}]}
    obj.l.get_or_create(a="foo", b="bar")
    assert obj == {"l": [{"a": "foo"}, {"a": "foo", "b": "bar"}]}
