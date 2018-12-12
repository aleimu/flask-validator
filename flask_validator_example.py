# -*- coding:utf-8 -*-
__author__ = "aleimu"
__date__ = "2018-12-6"
__doc__ = "入参校验装饰器"

from flask import Flask, jsonify
from validator import *

app = Flask(__name__)

rules_example = {
    "a": [Required, Equals("123")],  # foo must be exactly equal to 123
    "b": [Required, Truthy()],  # bar must be equivalent to True
    "c": [In(["spam", "eggs", "bacon"])],  # baz must be one of these options
    "d": [Not(Range(1, 100))],  # qux must not be a number between 1 and 100 inclusive
    "e": [Length(0, maximum=5)],
    "f": [Required, InstanceOf(str)],
    "g": [Required, Not(In(["spam", "eggs", "bacon"]))],
    "h": [Required, Pattern("\d\d\%")],
    "i": [Required, GreaterThan(1, reverse=True)],
    "j": [lambda x: x == "bar"],
    "k": [Required, Isalnum()],
    "l": [Required, Isalpha()],
    "m": [Required, Isdigit()],
}


@app.route("/wrap", methods=["GET", "POST", "PUT"])
@validator_wrap(rules=rules_example, strip=True)
def wrap_example():
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
    status, data = todo(a=a, b=b, c=c, d=d, e=e, f=f, g=g, h=h, i=i, j=j, k=k, l=l, m=m)
    if status:
        return jsonify({"code": 200, "data": data, "err": None})
    else:
        return jsonify({"code": 500, "data": None, "err": data})


@app.route("/func", methods=["GET", "POST", "PUT"])
def func_example():
    result, request_args = validator_func(rules=rules_example, strip=True)
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


@validator_args(rules=rules_example, strip=True)
def todo(a, b, c, d, e, f, g, h, i, j, k, l, m):
    return True, {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g, "h": h, "i": i, "j": j, "k": k, "l": l,
                  "m": m}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000, debug=True)

"""
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

# curl "http://127.0.0.1:6000/func" -d "a=123&b=123&c=spam&d=123&e=1236&f=123&g=spa1&h=11%&i=12&j=bar&k=32&l=abc&m=123"
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
                                                                                                            
                                                                                                                         
"""
