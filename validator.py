# -*- coding:utf-8 -*-
# The MIT License (MIT)
# Copyright (c) 2014 Samuel Lucidi
"""
validator.py
A library for validating that dictionary
values fit inside of certain sets of parameters.
Author: Samuel Lucidi <sam@samlucidi.com>
url: https://github.com/mansam/validator.py

"""
__doc__ = "入参校验装饰器"
__version__ = "1.2.6"

import re
import copy
import traceback
from functools import wraps
from collections import namedtuple, defaultdict, OrderedDict
from abc import ABCMeta, abstractmethod
from flask import jsonify, request

try:
    # python 3
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

ValidationResult = namedtuple('ValidationResult', ['valid', 'errors'])


def isstr(s):
    """
    Python 2/3 compatible check to see
    if an object is a string type.
    """

    try:
        return isinstance(s, basestring)
    except NameError:
        return isinstance(s, str)


def ChangeType(instance, new_type):
    try:
        instance = new_type(instance)
        return instance
    except Exception as e:
        return False


class Validator(object):
    """
    Abstract class that advanced
    validators can inherit from in order
    to set custom error messages and such.

    """

    __metaclass__ = ABCMeta

    err_message = "failed validation"
    not_message = "failed validation"

    @abstractmethod
    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class Isalnum(Validator):
    """判断字符串中只能由字母和数字的组合，不能有特殊符号"""

    def __init__(self):
        self.err_message = "must be numbers and letters"
        self.not_message = "must not be numbers and letters"

    def __call__(self, value):
        if isstr(value):
            return value.isalnum()
        else:
            return False


class Isalpha(Validator):
    """字符串里面都是字母，并且至少是一个字母，结果就为真，（汉字也可以）其他情况为假"""

    def __init__(self):
        self.err_message = "must be all letters"
        self.not_message = "must not be all letters"

    def __call__(self, value):
        if isstr(value):
            # if isinstance(value, str) or isinstance(value, unicode):
            return value.isalpha()
        else:
            return False


class Isdigit(Validator):
    """函数判断是否全为数字"""

    def __init__(self):
        self.err_message = "must be all numbers"
        self.not_message = "must not be all numbers"

    def __call__(self, value):
        if isstr(value):
            return value.isdigit()
        else:
            return False


class In(Validator):
    """
    Use to specify that the
    value of the key being
    validated must exist
    within the collection
    passed to this validator.

    # Example:
        validations = {
            "field": [In([1, 2, 3])]
        }
        passes = {"field":1}
        fails  = {"field":4}

    """

    def __init__(self, collection):
        self.collection = collection
        self.err_message = "must be one of %r" % collection
        self.not_message = "must not be one of %r" % collection

    def __call__(self, value):
        return (value in self.collection)


class Not(Validator):
    """
    Use to negate the requirement
    of another validator. Does not
    work with Required.

    """

    def __init__(self, validator):
        self.validator = validator
        self.err_message = getattr(validator, "not_message", "failed validation")
        self.not_message = getattr(validator, "err_message", "failed validation")

    def __call__(self, value):
        return not self.validator(value)


class Range(Validator):
    """
    Use to specify that the value of the
    key being validated must fall between
    the start and end values. By default
    the range is inclusive, though the
    range can be made excusive by setting
    inclusive to false.

    # Example:
        validations = {
            "field": [Range(0, 10)]
        }
        passes = {"field": 10}
        fails = {"field" : 11}

    """

    def __init__(self, start, end, reverse=True):
        self.start = start
        self.end = end
        self.reverse = reverse
        self.err_message = "must fall between %s and %s" % (start, end)
        self.not_message = "must not fall between %s and %s" % (start, end)

    def __call__(self, value):
        if self.reverse:
            return self.start <= value <= self.end
        else:
            return self.start < value < self.end


class GreaterThan(Validator):
    """
    Use to specify that the value of the
    key being validated must be greater
    than a given value. By default the
    bound is exclusive, though the bound
    can be made inclusive by setting
    inclusive to true.

    # Example:
        validations = {
            "field": [GreaterThan(10)]
        }
        passes = {"field": 11}
        fails = {"field" : 10}

    """

    def __init__(self, lower_bound, reverse=False):
        self.lower_bound = lower_bound
        self.reverse = reverse
        self.err_message = "must be greater than %s" % lower_bound
        self.not_message = "must not be greater than %s" % lower_bound

    def __call__(self, value):
        if self.reverse:
            return self.lower_bound <= value
        else:
            return self.lower_bound < value


class Equals(Validator):
    """
    Use to specify that the
    value of the key being
    validated must be equal to
    the value that was passed
    to this validator.

    # Example:
        validations = {
            "field": [Equals(1)]
        }
        passes = {"field":1}
        fails  = {"field":4}

    """

    def __init__(self, obj):
        self.obj = obj
        self.err_message = "must be equal to %r" % obj
        self.not_message = "must not be equal to %r" % obj

    def __call__(self, value):
        return value == self.obj


class Blank(Validator):
    """
    Use to specify that the
    value of the key being
    validated must be equal to
    the empty string.

    This is a shortcut for saying
    Equals("").

    # Example:
        validations = {
            "field": [Blank()]
        }
        passes = {"field":""}
        fails  = {"field":"four"}

    """

    def __init__(self):
        self.err_message = "must be an empty string"
        self.not_message = "must not be an empty string"

    def __call__(self, value):
        return value == ""


class Truthy(Validator):
    """
    Use to specify that the
    value of the key being
    validated must be truthy,
    i.e. would cause an if statement
    to evaluate to True.

    # Example:
        validations = {
            "field": [Truthy()]
        }
        passes = {"field": 1}
        fails  = {"field": 0}


    """

    def __init__(self):
        self.err_message = "must be True-equivalent value"
        self.not_message = "must be False-equivalent value"

    def __call__(self, value):
        if value:
            return True
        else:
            return False


def Required(field, dictionary):
    """
    When added to a list of validations
    for a dictionary key indicates that
    the key must be present. This
    should not be called, just inserted
    into the list of validations.

    # Example:
        validations = {
            "field": [Required, Equals(2)]
        }

    By default, keys are considered
    optional and their validations
    will just be ignored if the field
    is not present in the dictionary
    in question.

    """

    return (field in dictionary)


class InstanceOf(Validator):
    """
    Use to specify that the
    value of the key being
    validated must be an instance
    of the passed in base class
    or its subclasses.

    # Example:
        validations = {
            "field": [InstanceOf(basestring)]
        }
        passes = {"field": ""} # is a <'str'>, subclass of basestring
        fails  = {"field": str} # is a <'type'>

    """

    def __init__(self, base_class):
        self.base_class = base_class
        self.err_message = "must be an instance of %s or its subclasses" % base_class.__name__
        self.not_message = "must not be an instance of %s or its subclasses" % base_class.__name__

    def __call__(self, value):
        return isinstance(value, self.base_class)


class SubclassOf(Validator):
    """
    Use to specify that the
    value of the key being
    validated must be a subclass
    of the passed in base class.

    # Example:
        validations = {
            "field": [SubclassOf(basestring)]
        }
        passes = {"field": str} # is a subclass of basestring
        fails  = {"field": int}

    """

    def __init__(self, base_class):
        self.base_class = base_class
        self.err_message = "must be a subclass of %s" % base_class.__name__
        self.not_message = "must not be a subclass of %s" % base_class.__name__

    def __call__(self, class_):
        return issubclass(class_, self.base_class)


class Pattern(Validator):
    """
    Use to specify that the
    value of the key being
    validated must match the
    pattern provided to the
    validator.

    # Example:
        validations = {
            "field": [Pattern('\d\d\%')]
        }
        passes = {"field": "30%"}
        fails  = {"field": "30"}

    """

    def __init__(self, pattern):
        self.pattern = pattern
        self.err_message = "must match regex pattern %s" % pattern
        self.not_message = "must not match regex pattern %s" % pattern
        self.compiled = re.compile(pattern)

    def __call__(self, value):
        return self.compiled.match(value)


class Then(Validator):
    """
    Special validator for use as
    part of the If rule.
    If the conditional part of the validation
    passes, then this is used to apply another
    set of dependent rules.

    # Example:
        validations = {
            "foo": [If(Equals(1), Then({"bar": [Equals(2)]}))]
        }
        passes = {"foo": 1, "bar": 2}
        also_passes = {"foo": 2, "bar": 3}
        fails = {"foo": 1, "bar": 3}
    """

    def __init__(self, validation):
        self.validation = validation

    def __call__(self, dictionary):
        return validate(self.validation, dictionary)


class If(Validator):
    """
    Special conditional validator.
    If the validator passed as the first
    parameter to this function passes,
    then a second set of rules will be
    applied to the dictionary.

    # Example:
        validations = {
            "foo": [If(Equals(1), Then({"bar": [Equals(2)]}))]
        }
        passes = {"foo": 1, "bar": 2}
        also_passes = {"foo": 2, "bar": 3}
        fails = {"foo": 1, "bar": 3}
    """

    def __init__(self, validator, then_clause):
        self.validator = validator
        self.then_clause = then_clause

    def __call__(self, value, dictionary):
        conditional = False
        dependent = None
        if self.validator(value):
            conditional = True
            dependent = self.then_clause(dictionary)
        return conditional, dependent


class Length(Validator):
    """
    Use to specify that the
    value of the key being
    validated must have at least
    `minimum` elements and optionally
    at most `maximum` elements.

    At least one of the parameters
    to this validator must be non-zero,
    and neither may be negative.

    # Example:
        validations = {
            "field": [Length(0, maximum=5)]
        }
        passes = {"field": "hello"}
        fails  = {"field": "hello world"}

    """

    err_messages = {
        "maximum": "must be at most {0} elements in length",
        "minimum": "must be at least {0} elements in length",
        "range": "must{0}be between {1} and {2} elements in length"
    }

    def __init__(self, minimum, maximum=0):
        if not minimum and not maximum:
            raise ValueError("Length must have a non-zero minimum or maximum parameter.")
        if minimum < 0 or maximum < 0:
            raise ValueError("Length cannot have negative parameters.")

        self.minimum = minimum
        self.maximum = maximum
        if minimum and maximum:
            self.err_message = self.err_messages["range"].format(' ', minimum, maximum)
            self.not_message = self.err_messages["range"].format(' not ', minimum, maximum)
        elif minimum:
            self.err_message = self.err_messages["minimum"].format(minimum)
            self.not_message = self.err_messages["maximum"].format(minimum - 1)
        elif maximum:
            self.err_message = self.err_messages["maximum"].format(maximum)
            self.not_message = self.err_messages["minimum"].format(maximum + 1)

    def __call__(self, value):
        if self.maximum:
            return self.minimum <= len(value) <= self.maximum
        else:
            return self.minimum <= len(value)


class Contains(Validator):
    """
    Use to ensure that the value of the key
    being validated contains the value passed
    into the Contains validator. Works with
    any type that supports the 'in' syntax.

    # Example:
        validations = {
            "field": [Contains(3)]
        }
        passes = {"field": [1, 2, 3]}
        fails  = {"field": [4, 5, 6]}

    """

    def __init__(self, contained):
        self.contained = contained
        self.err_message = "must contain {0}".format(contained)
        self.not_message = "must not contain {0}".format(contained)

    def __call__(self, container):
        return self.contained in container


class Each(Validator):
    """
    Use to ensure that

    If Each is passed a list of validators, it
    just applies each of them to each element in
    the list.

    If it's instead passed a *dictionary*, it treats
    it as a validation to be applied to each element in
    the dictionary.

    """

    def __init__(self, validations):
        assert isinstance(validations, (list, tuple, set, dict))
        self.validations = validations

    def __call__(self, container):
        assert isinstance(container, (list, tuple, set))

        # handle the "apply simple validation to each in list"
        # use case
        if isinstance(self.validations, (list, tuple, set)):
            errors = []
            for item in container:
                for v in self.validations:
                    valid = v(item)
                    if not valid:
                        errors.append("all values " + v.err_message)

        # handle the somewhat messier list of dicts case
        if isinstance(self.validations, dict):
            errors = defaultdict(list)
            for index, item in enumerate(container):
                valid, err = validate(self.validations, item)
                if not valid:
                    errors[index] = err
            errors = dict(errors)

        return (len(errors) == 0, errors)


class Url(Validator):
    """
    Use to specify that the
    value of the key being
    validated must be a Url.

    This is a shortcut for saying
    Url().

    # Example:
        validations = {
            "field": [Url()]
        }
        passes = {"field":"http://vk.com"}
        fails  = {"field":"/1https://vk.com"}

    """

    def __init__(self):
        self.err_message = "must be a valid URL"
        self.not_message = "must not be a valid URL"

    def __call__(self, value):
        try:
            result = urlparse(value)
            return all([result.scheme, result.netloc])
        except:
            return False


def validate(validation, dictionary):
    """
    Validate that a dictionary passes a set of
    key-based validators. If all of the keys
    in the dictionary are within the parameters
    specified by the validation mapping, then
    the validation passes.

    :param validation: a mapping of keys to validators
    :type validation: dict

    :param dictionary: dictionary to be validated
    :type dictionary: dict

    :return: a tuple containing a bool indicating
    success or failure and a mapping of fields
    to error messages.

    """

    errors = defaultdict(list)
    for key in validation:
        if isinstance(validation[key], (list, tuple)):
            if Required in validation[key]:
                if not Required(key, dictionary):
                    errors[key] = "must be present"
                    continue
            _validate_list_helper(validation, dictionary, key, errors)
        else:
            v = validation[key]
            if v == Required:
                if not Required(key, dictionary):
                    errors[key] = "must be present"
            else:
                _validate_and_store_errs(v, dictionary, key, errors)
    if len(errors) > 0:
        # `errors` gets downgraded from defaultdict to dict
        # because it makes for prettier output
        return ValidationResult(valid=False, errors=dict(errors))
    else:
        return ValidationResult(valid=True, errors={})


def _validate_and_store_errs(validator, dictionary, key, errors):
    # Validations shouldn't throw exceptions because of
    # type mismatches and the like. If the rule is 'Length(5)' and
    # the value in the field is 5, that should be a validation failure,
    # not a TypeError because you can't call len() on an int.
    # It's not ideal to have to hide exceptions like this because
    # there could be actual problems with a validator, but we're just going
    # to have to rely on tests preventing broken things.
    try:
        valid = validator(dictionary[key])
    except Exception:
        # Since we caught an exception while trying to validate,
        # treat it as a failure and return the normal error message
        # for that validator.
        valid = (False, validator.err_message)
    if isinstance(valid, tuple):
        valid, errs = valid
        if errs and isinstance(errs, list):
            errors[key] += errs
        elif errs:
            errors[key].append(errs)
    elif not valid:
        # set a default error message for things like lambdas
        # and other callables that won't have an err_message set.
        msg = getattr(validator, "err_message", "failed validation")
        errors[key].append(msg)


def _validate_list_helper(validation, dictionary, key, errors):
    for v in validation[key]:
        # don't break on optional keys
        if key in dictionary:
            # Ok, need to deal with nested
            # validations.
            if isinstance(v, dict):
                _, nested_errors = validate(v, dictionary[key])
                if nested_errors:
                    errors[key].append(nested_errors)
                continue
            # Done with that, on to the actual
            # validating bit.
            # Skip Required, since it was already
            # handled before this point.
            if not v == Required:
                # special handling for the
                # If(Then()) form
                if isinstance(v, If):
                    conditional, dependent = v(dictionary[key], dictionary)
                    # if the If() condition passed and there were errors
                    # in the second set of rules, then add them to the
                    # list of errors for the key with the condtional
                    # as a nested dictionary of errors.
                    if conditional and dependent[1]:
                        errors[key].append(dependent[1])
                # handling for normal validators
                else:
                    _validate_and_store_errs(v, dictionary, key, errors)


def validator_func_wrap(rules, strip=True, default=(False, None), diy_func=None, release=False):
    """针对普通函数的参数校验的装饰器
    :param rules:参数的校验规则,map
    :param strip:对字段进行前后过滤空格
    :param default:将"" 装换成None
    :param diy_func:自定义的对某一参数的校验函数格式: {key:func},类似check, diy_func={"a": lambda x: x + "aa"})
    :param release:发生参数校验异常后是否依然让参数进入主流程函数
    """

    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            if release:
                args_bak = args[:]
                kwargs_bak = copy.deepcopy(kwargs)  # 下面流程异常时,是否直接使用 原参数传入f # fixme
            args_template = f.func_code.co_varnames
            args_dict = OrderedDict()
            try:
                for i, x in enumerate(args):
                    args_dict[args_template[i]] = x
                sorted_kwargs = sort_by_co_varnames(args_template, kwargs)
                args_dict.update(sorted_kwargs)
                # strip
                if strip:
                    for k in args_dict:
                        if isstr(args_dict[k]):
                            args_dict[k] = args_dict[k].strip()
                # default
                if default[0]:
                    for x in args_dict:
                        if args_dict[x] == "":
                            args_dict[x] = default[1]
                # diy_func
                if diy_func:
                    for k in args_dict:
                        if k in diy_func:
                            args_dict[k] = diy_func[k](args_dict[k])
                # rules
                if rules:
                    result, err = validate(rules, args_dict)
                    if not result:
                        return False, err
            except Exception as e:
                # print("verify_args catch err: ", traceback.format_exc())
                if release:
                    return f(*args_bak, **kwargs_bak)
                else:
                    return False, str(e)
            return f(*args_dict.values())

        return decorated_func

    return decorator


def sort_by_co_varnames(all_args, kwargs):
    new_ordered = OrderedDict()
    for x in all_args:
        if x in kwargs:
            new_ordered[x] = kwargs[x]
    return new_ordered


def validator_func(rules, strip=True, default=(False, None), diy_func=None, release=False):
    """函数版-返回dict,代替request.values/request.json
    :param rules:参数的校验规则,map
    :param strip:对字段进行前后过滤空格
    :param default:将"" 装换成None
    :param diy_func:自定义的对某一参数的校验函数格式: {key:func},类似check, diy_func={"a": lambda x: x + "aa"})
    :param release:发生参数校验异常后是否依然让参数进入主流程函数
    """
    args_dict = OrderedDict()
    try:
        if request.values:
            args_dict.update(request.values)
        if request.json:
            args_dict.update(request.json)
        if release:
            args_dict_copy = copy.deepcopy(args_dict)  # 下面流程异常时,是否直接使用 原参数传入f # fixme
        # strip
        if strip:
            for k in args_dict:
                if isstr(args_dict[k]):
                    args_dict[k] = args_dict[k].strip()
        # default
        if default[0]:
            for x in args_dict:
                if args_dict[x] == "":
                    args_dict[x] = default[1]
        # diy_func
        if diy_func:
            for k in args_dict:
                if k in diy_func:
                    args_dict[k] = diy_func[k](args_dict[k])
        # rules
        if rules:
            result, err = validate(rules, args_dict)
            if not result:
                return False, err
    except Exception as e:
        # print("verify_args catch err: ", traceback.format_exc())  # TODO
        if release:
            return True, args_dict_copy
        else:
            return False, str(e)
    return True, args_dict


def validator_wrap(rules, strip=True, diy_func=None):
    """装饰器版 - 只能检测是否符合规则,不能修改参数
    :param rules:参数的校验规则,map
    :param strip:对字段进行前后空格检测
    :param diy_func:自定义的对某一参数的校验函数格式: {key:func},类似check, diy_func={"a": lambda x: x=="aa"})
    """

    def decorator(f):
        @wraps(f)
        def decorated_func(*args, **kwargs):
            try:
                args_dict = OrderedDict()
                if request.values:
                    args_dict.update(request.values)
                if request.json:
                    args_dict.update(request.json)
                # strip
                if strip:
                    for k in args_dict:
                        if isstr(args_dict[k]):
                            if args_dict[k][0] == " " or args_dict[k][-1] == " ":
                                return jsonify({"code": 500, "data": None, "err": "%s should not contain spaces" % k})
                # diy_func
                if diy_func:
                    for k in args_dict:
                        if k in diy_func:
                            args_dict[k] = diy_func[k](args_dict[k])
                # rules
                if rules:
                    result, err = validate(rules, args_dict)
                    if not result:
                        return jsonify(
                            {"code": 500, "data": None, "err": err})
            except Exception as e:
                # print("verify_args catch err: ", traceback.format_exc())
                return jsonify({"code": 500, "data": None, "err": str(e)})
            return f(*args, **kwargs)

        return decorated_func

    return decorator
