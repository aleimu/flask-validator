## basic introduction

    1. Encapsulated https://github.com/mansam/validator.py, extended string verification, some methods can be referred to here, considering that the code is relatively small, you can directly copy
    2. validator_func : for the request.json / requests.values ​​parameter calibration and modification of the flask, the modification is limited, you can control
    3. validator_wrap : is a decorator for flask route, for the parameter check of request.json / requests.values, just check, of course, the way to verify can write extensions
    4. validator_args : for the normal function parameter validation and modification, be careful not to use the advanced features of python pass parameters (one parameter corresponds to multiple values), this method can be used away from the flask, so if you need to copy directly.

## test
    1. I curl some tests and may not be complete, haha, if you are worried, refer to https://github.com/mansam/validator.py/blob/master/tests/test_validator.py
    2. Support python2 and python3

    ## curl example

    #curl"http://127.0.0.1:6000/wrap"-d"a = 123&b = 123&c = spam&d = 123&e = 1236&f = 123&g = spa1&h = 11%&i = 12&j = bar&k = 32&l = abc&m = 123"
    {
    "Code": 200,
    "Data": {
    "a": "123",
    "b": "123",
    "c": "spam",
    "d": "123",
    "e": "1236",
    "f": "123",
    "g": "spa1",
    "h": "11%",
    "I": "12",
    "j": "bar",
    "k": "32",
    "l": "abc",
    "m": "123"
    },
    "err": null
    }

    #curl"http://127.0.0.1:5000/wrap"-d"a = 123&b = 123&c = spam&d = 123&e = 1236&f = 123&g = spa1&h = 11%&i = 12&j = bar&k = 32&l = abc&m = 123"
    {"code": 500, "data": null, "err": "m should not contain spaces"}

    #curl“http://127.0.0.1:5000/wrap”-d “a = 123&b = 123&c = spam&d = 13&e = 1236&f = 123&g = spa1&h = 11%&i = 12&j = bar&k = 32&l = abc&m = 123”
    {"code":500, "data":null,"err":{"d":["not between 1 and 100"]}}

    #curl“http://127.0.0.1:5000/wrap”-d “a = 1234&b =&c = nospam&d = 13&e = 123456&f = 123&g = spa1&h = 11%&i = 12&j = bar&k = 3a2&l = 1abc&m = 123a”
    {"code":500, "data":null,"err":{"a":["must be equal to '123'"], "b":["must be true equivalent"], "c" :[" must be ['spam', 'egg', 'bacon'] "], "d" one: [" must not be between 1 and 100"], "e": [" must be large The length of most 5 elements "], "l": [" must be all letters "], "m": [" must be all numbers "]}}

## validator.py Sample copy

    From the validator import required, no, Truthy, blank, range, equal, in, verify

    # Let us say that my dictionary needs to meet the following rules...
    Rules = {
    "foo": [required, equals (123)], #foo must be exactly equal to 123
    "bar": [required, Truthy()], #bar must equal True
    "baz": [in (["spam", "egg", "bacon"])], #baz must be one of these options
    "qux": [Not (range (1,100))] #qux cannot be a number between 1 and 100
    }

    # Then this dict will pass:
    Pass = {
    "foo": 123,
    "bar": True, # or non-empty string, or non-zero int, etc...
    "baz": "spam",
    "qux": 101
    }
    >>>Verification (rules, passes)
        (Yes,{})

    #But this will fail
    Failure = {
    "foo": 321,
    "bar": False, # or 0, or [], or an empty string, etc...
    "baz": "barf",
    "qux": 99
    }
    >>>Verification (rules, failures)
    (wrong, {
    'foo':["must equal 123"],
    'bar':['must be true value'],
    'baz':["Must be ['spam', 'egg', 'Bacon'],",
    'qux': ['not between 1 and 100']
    })
