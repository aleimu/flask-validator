# -*- coding:utf-8 -*-
__author__ = "aleimu"
__date__ = "2018-12-6"
__doc__ = "入参校验装饰器"

from flask import Flask, jsonify
from validator import *

app = Flask(__name__)

rules_example = {
    # ---------------------in url-------------------#
    "a": [Required, Equals("123")],  # foo must be exactly equal to 123
    "b": [Required, Truthy()],  # bar must be equivalent to True
    "c": [In(["spam", "eggs", "bacon"])],  # baz must be one of these options
    "d": [Not(Range(1, 100))],  # qux must not be a number between 1 and 100 inclusive
    "e": [Length(0, maximum=5)],
    # --------------------in json------------------#
    "f": [Required, InstanceOf(int)],
    "g": [Required, Not(In(["spam", "eggs", "bacon"]))],
    "h": [Required, Pattern("\d\d\%")],
    "i": [Required, GreaterThan(1, reverse=True, auto=False)],  # auto 自动转换成float类型来做比较
    "j": [lambda x: x == "bar"],
    "k": [Required, Isalnum()],  # 判断字符串中只能由字母和数字的组合，不能有特殊符号
    "l": [Required, Isalpha()],  # 字符串里面都是字母，并且至少是一个字母，结果就为真，（汉字也可以）其他情况为假
    "m": [Required, Isdigit()],  # 判断字符串是否全为数字
}


@app.route("/wrap", methods=["GET", "POST", "PUT"])
@validator_wrap(rules=rules_example, strip=True)  # 姿势 1:只能检测是否符合规则,不能修改参数,不符合就会直接返回json给调用者
def wrap_example():
    a = request.values.get("a")
    b = request.values.get("b")
    c = request.values.get("c")
    d = request.values.get("d")
    e = request.values.get("e")
    f = request.json.get("f")
    g = request.json.get("g")
    h = request.json.get("h")
    i = request.json.get("i")
    j = request.json.get("j")
    k = request.json.get("k")
    l = request.json.get("l")
    m = request.json.get("m")
    status, data = todo(a=a, b=b, c=c, d=d, e=e, f=f, g=g, h=h, i=i, j=j, k=k, l=l, m=m)
    if status:
        return jsonify({"code": 200, "data": data, "err": None})
    else:
        return jsonify({"code": 500, "data": None, "err": data})


@app.route("/func", methods=["GET", "POST", "PUT"])
def func_example():
    result, request_args = validator_func(rules=rules_example, strip=True)  # 姿势 2
    if not result:
        return jsonify({"code": 500, "data": None, "err": request_args})
    a = request_args.get("a")
    b = request_args.get("b")
    c = request_args.get("c")
    d = request_args.get("d")
    e = request_args.get("e")
    f = request_args.get("f")
    g = request_args.get("g")
    h = request_args.get("h")
    i = request_args.get("i")
    j = request_args.get("j")
    k = request_args.get("k")
    l = request_args.get("l")
    m = request_args.get("m")
    status, data = todo(a=a, b=b, c=c, d=d, e=e, f=f, g=g, h=h, i=i, j=j, k=k, l=l, m=m)
    if status:
        return jsonify({"code": 200, "data": data, "err": None})
    else:
        return jsonify({"code": 500, "data": None, "err": data})


@app.route("/args", methods=["GET", "POST", "PUT"])
def args_example():
    a = request.values.get("a")
    b = request.values.get("b")
    c = request.values.get("c")
    d = request.values.get("d")
    e = request.values.get("e")
    f = request.values.get("f")
    g = request.values.get("g")
    h = request.values.get("h")
    i = request.values.get("i")
    j = request.values.get("j")
    k = request.values.get("k")
    l = request.values.get("l")
    m = request.values.get("m")
    status, data = todo(a, b, c, d, e, f, g, h, i, j, k, l, m=m)
    if status:
        return jsonify({"code": 200, "data": data, "err": None})
    else:
        return jsonify({"code": 500, "data": None, "err": data})


@validator_args(rules=rules_example, strip=True)  # 姿势 3
def todo(a, b, c, d, e, f, g, h, i, j, k, l, m):
    return True, {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g, "h": h, "i": i, "j": j, "k": k, "l": l,
                  "m": m}


@app.route("/args_less", methods=["GET", "POST", "PUT"])
def args_less_example():
    a = request.values.get("a")
    b = request.values.get("b")
    c = request.values.get("c")
    d = request.values.get("d")
    e = request.values.get("e")
    f = request.values.get("f")
    g = request.values.get("g")
    h = request.values.get("h")
    i = request.values.get("i")
    j = request.values.get("j")
    k = request.values.get("k")
    l = request.values.get("l")
    m = request.values.get("m")
    status, data = arbitrary_args_func(a, b, c, d, e, f, g, h, i, j, k, l, m=m)
    if status:
        return jsonify({"code": 200, "data": data, "err": None})
    else:
        return jsonify({"code": 500, "data": None, "err": data})


rules_arbitrary_args_example = {
    "a": [Required, Equals("123")],  # foo must be exactly equal to 123
    "b": [Required, Isdigit()],  # bar must be equivalent to True
    "c": [Required, Truthy()],  # bar must be equivalent to True,c对应的是可变长参数,不太好做具体的校验......
    "m": [Required, Isalpha()],  # 判断字符串是否全为数字
}


@validator_arbitrary_args(rules=rules_arbitrary_args_example, strip=True, release=False)  # 姿势 4
def arbitrary_args_func(a, b="OK", *c, **m):
    return True, {"a": a, "b": b, "c": c, "m": m}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000, debug=True)

"""
curl -H "Content-Type: application/json" -X POST "http://172.16.2.192:6000/wrap?&a=123&b=123&c=spam&d=123&e=1236" -d '{"f":123,"g":"spa1","h":"11%","i":12,"j":"bar","k":"a32","l":"abc","m":"123"}'
{
  "code": 200, 
  "data": {
    "a": "123", 
    "b": "123", 
    "c": "spam", 
    "d": "123", 
    "e": "1236", 
    "f": 123, 
    "g": "spa1", 
    "h": "11%", 
    "i": 12, 
    "j": "bar", 
    "k": "a32", 
    "l": "abc", 
    "m": "123"
  }, 
  "err": null
}

curl -H "Content-Type: application/json" -X POST "http://172.16.2.192:6000/wrap?&a=123&b=123&c=spam&d=123&e=1236" -d '{"f":123,"g":"spa1","h":11,"i":12,"j":"bar","k":32,"l":"abc","m":123}'
{
  "code": 500, 
  "data": null, 
  "err": {
    "h": [
      "must match regex pattern \\d\\d\\%"
    ], 
    "k": [
      "must be numbers and letters"
    ], 
    "m": [
      "must be all numbers"
    ]
  }
}

curl -H "Content-Type: application/json" -X POST "http://172.16.2.192:6000/wrap?&a=123&b=123&c=spam&d=123&e=1236" -d '{"f":123,"g":"spa1","h":"11%","i":12,"j":"bar1","k":"a32","l":"abc","m":"123"}'
{
  "code": 500, 
  "data": null, 
  "err": {
    "j": [
      "failed validation"
    ]
  }
}

curl -H "Content-Type: application/json" -X POST "http://172.16.2.192:6000/func?&a=123&b=123&c=spam&d=123&e=1236" -d '{"f":123,"g":"spa1","h":"11%","i":0,"j":"nobar","k":"3*2","l":"ab1c","m":123}'
{
  "code": 500, 
  "data": null, 
  "err": {
    "i": [
      "must be greater than 1"
    ], 
    "j": [
      "failed validation"
    ], 
    "k": [
      "must be numbers and letters"
    ], 
    "l": [
      "must be all letters"
    ], 
    "m": [
      "must be all numbers"
    ]
  }
}

curl "http://172.16.2.192:6000/args_less" -d "a=123&b=123&c=spam&d=123&e=1236&f=123&g=spa1&h=11%&i=12&j=bar&k=32&l=abc&m=aaa"  
{
  "code": 200, 
  "data": {
    "a": "123", 
    "b": "123", 
    "c": [
      [
        "spam", 
        "123", 
        "1236", 
        "123", 
        "spa1", 
        "11%", 
        "12", 
        "bar", 
        "32", 
        "abc"
      ]
    ], 
    "m": {
      "m": "aaa"
    }
  }, 
  "err": null
}

curl "http://172.16.2.192:6000/args_less" -d "a=12&b=12&c=&d=123&e=1236&f=123&g=spa1&h=11%&i=12&j=bar&k=32&l=abc&m=123"  
{
  "code": 500, 
  "data": null, 
  "err": {
    "a": [
      "must be equal to '123'"
    ], 
    "m": [
      "must be all letters"
    ]
  }
}
"""
