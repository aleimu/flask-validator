## 简单介绍

1. 封装了 https://github.com/mansam/validator.py, 扩展了字符串校验,部分使用方法可以参考此处,考虑到代码比较少,可以直接copy
2. validator_func 针对flask的request.json/requests.values的参数校验以及修改,修改的方式有限,可以自己控制
3. validator_wrap 是针对flask route的装饰器,针对request.json/requests.values的参数校验,只是校验,当然校验的方式可以自己写扩展
4. validator_args 针对普通函数的参数校验以及修改,注意不要使用python传参的高级特性(可变长参数),这个方法可以脱离flask使用,所以如果需要就直接copy过去吧.
5. validator_arbitrary_args 针对包含可变长参数的函数的校验和修改,同样,这个方法也是可以脱离flask使用的,,所以如果需要就直接copy过去吧.

## 测试
1. 我curl测试了一些,可能不完整,哈哈,要是担心的话,参考这里  https://github.com/mansam/validator.py/blob/master/tests/test_validator.py
2. 具体的使用方法都写字了flask_validator_exampleXXX中了,可以参考一下.
3. 支持python2和python3


## curl example

    # curl "http://127.0.0.1:6000/wrap" -d "a=123&b=123&c=spam&d=123&e=1236&f=123&g=spa1&h=11%&i=12&j=bar&k=32&l=abc&m=123"
    {
      "code": 200,
      "data": {
        "a": "123",
        "b": "123",
        "c": "spam",
        "d": "123",
        "e": "1236",
        "f": "123",
        "g": "spa1",
        "h": "11%",
        "i": "12",
        "j": "bar",
        "k": "32",
        "l": "abc",
        "m": "123"
      },
      "err": null
    }

    # curl "http://127.0.0.1:5000/wrap" -d "a=123&b=123&c=spam&d=123&e=1236&f=123&g=spa1&h=11%&i=12&j=bar&k=32&l=abc&m=123 "
    {"code":500,"data":null,"err":"m should not contain spaces"}

    # curl "http://127.0.0.1:5000/wrap" -d "a=123&b=123&c=spam&d=13&e=1236&f=123&g=spa1&h=11%&i=12&j=bar&k=32&l=abc&m=123"
    {"code":500,"data":null,"err":{"d":["must not fall between 1 and 100"]}}

    # curl "http://127.0.0.1:5000/wrap" -d "a=1234&b=&c=nospam&d=13&e=123456&f=123&g=spa1&h=11%&i=12&j=bar&k=3a2&l=1abc&m=123a"
    {"code":500,"data":null,"err":{"a":["must be equal to '123'"],"b":["must be True-equivalent value"],"c":["must be one of ['spam', 'eggs', 'bacon']"],"d":["must not fall between 1 and 100"],"e":["must be at most 5 elements in length"],"l":["must be all letters"],"m":["must be all numbers"]}}

## validator.py example copy

    from validator import Required, Not, Truthy, Blank, Range, Equals, In, validate

    # let's say that my dictionary needs to meet the following rules...
    rules = {
        "foo": [Required, Equals(123)], # foo must be exactly equal to 123
        "bar": [Required, Truthy()],    # bar must be equivalent to True
        "baz": [In(["spam", "eggs", "bacon"])], # baz must be one of these options
        "qux": [Not(Range(1, 100))] # qux must not be a number between 1 and 100 inclusive
    }

    # then this following dict would pass:
    passes = {
        "foo": 123,
        "bar": True, # or a non-empty string, or a non-zero int, etc...
        "baz": "spam",
        "qux": 101
    }
    >>> validate(rules, passes)
    (True, {})

    # but this one would fail
    fails = {
        "foo": 321,
        "bar": False, # or 0, or [], or an empty string, etc...
        "baz": "barf",
        "qux": 99
    }
    >>> validate(rules, fails)
    (False, {
     'foo': ["must be equal to 123"],
     'bar': ['must be True-equivalent value'],
     'baz': ["must be one of ['spam', 'eggs', 'bacon']"],
     'qux': ['must not fall between 1 and 100']
    })