# -*- coding:utf-8 -*-
__author__ = "aleimu"
__date__ = "2018-12-24"
__doc__ = "入参校验装饰器,新增了email和时间的校验样例"

from flask import Flask, jsonify
from validator import *

app = Flask(__name__)

rules_example = {
    # ---------------------in url-------------------#
    "a": [Required, Email()],  # check Email format
    "b": [Required, Datetime()],  # check Datetime format
    "c": [Required, Datetime(format="%Y-%m-%dT%H:%M:%S")],  # check Datetime format,and diy your format
    "d": [Required, Date()],  # check Date format
    "e": [Required, Date(format="%Y-%m-%d")],  # check Date format,and diy your format
    # --------------------in json------------------#

}


@app.route("/wrap", methods=["GET", "POST", "PUT"])
@validator_wrap(rules=rules_example, strip=True)  # 姿势 1:只能检测是否符合规则,不能修改参数,不符合就会直接返回json给调用者
def wrap_example():
    a = request.values.get("a")
    b = request.values.get("b")
    c = request.values.get("c")
    d = request.values.get("d")
    e = request.values.get("e")
    # f = request.json.get("f")
    # g = request.json.get("g")
    # h = request.json.get("h")
    # i = request.json.get("i")
    # j = request.json.get("j")
    # k = request.json.get("k")
    # l = request.json.get("l")
    # m = request.json.get("m")
    status, data = todo(a=a, b=b, c=c, d=d, e=e)
    if status:
        return jsonify({"code": 200, "data": data, "err": None})
    else:
        return jsonify({"code": 500, "data": None, "err": data})


def todo(a, b, c, d, e):
    return True, {"a": a, "b": b, "c": c, "d": d, "e": e}


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=6000, debug=True)

"""
# curl "http://172.16.2.192:6000/wrap?&a=123@qq.com&b=2016-10-24T14:01:57.102152Z&c=2016-10-24T14:01:57&d=2016-10-24&e=2016-10-24"
{
  "code": 200,
  "data": {
    "a": "123@qq.com",
    "b": "2016-10-24T14:01:57.102152Z",
    "c": "2016-10-24T14:01:57",
    "d": "2016-10-24",
    "e": "2016-10-24"
  },
  "err": null
}

# curl "http://172.16.2.192:6000/wrap?&a=123@qq.com&b=2016-10-24T1401:57.102152Z&c=016-10-24T14:01:57&d=2016-13-24&e=2016-10-241"
{
  "code": 500,
  "data": null,
  "err": {
    "b": [
      "Invalid Datetime format"
    ],
    "c": [
      "Invalid Datetime format"
    ],
    "d": [
      "Invalid Date format"
    ],
    "e": [
      "Invalid Date format"
    ]
  }
}

# curl "http://172.16.2.192:6000/wrap?&a=123@qqcom&b=2016-10-24T14:01:57.102152Z&c=2016-10-24T14:01&d=201
6-10-24&e=2016-10"
{
  "code": 500,
  "data": null,
  "err": {
    "a": [
      "Invalid Email"
    ],
    "c": [
      "Invalid Datetime format"
    ],
    "e": [
      "Invalid Date format"
    ]
  }
}



"""
