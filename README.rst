Json Schema Model
=================

Build python objects using JSON schemas::

    >>> import jsonschema_model
    >>> Model = jsonschema_model.model_factory({
    ...    "name": "Model",
    ...    "properties": {
    ...        "foo": {"type": "string"},
    ...        "bar": {"type": "array", "items": {
    ...            "type": "object",
    ...            "name": "Bar",
    ...            "properties": {
    ...                "zaz": {"type": "string"},
    ...            },
    ...        }},
    ...    }})
    >>> obj = Model(foo="bar")
    >>> obj
    {'foo': 'bar'}
    >>> obj.bar.add(zaz="qux")
    {'zaz': 'qux'}
    >>> obj
    {'foo': 'bar', 'bar': [{'zaz': 'qux'}]}

    # You can access via attribute or via dict like interface
    >>> obj["bar"][0].zaz
    'qux'
