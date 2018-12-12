## 简单介绍

1. 封装了 https://github.com/mansam/validator.py, 扩展了字符串校验,部分使用方法可以参考此处,考虑到代码比较少,可以直接copy
2. validator_func 针对flask的request.json/requests.values的参数校验以及修改
3. validator_wrap 是针对flask route的装饰器,针对request.json/requests.values的参数校验,只是校验
4. validator_func_wrap 针对普通函数的参数校验以及修改,注意不要使用python传参的高级特性(一个参数对应多个值),这个方法可以脱离flask使用,所以如果需要就直接copy过去吧.

## 测试
1. 我curl测试了一些,可能不完整,哈哈,要是担心的话,参考这里  https://github.com/mansam/validator.py/blob/master/tests/test_validator.py
2. 支持python2和python3

## example

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