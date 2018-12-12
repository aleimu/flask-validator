## 简单介绍

1. 封装了 https://github.com/mansam/validator.py, 扩展了字符串校验,部分使用方法可以参考此处,考虑到代码比较少,可以直接就copy
2. validator_func 针对flask的request.json/requests.values的参数校验以及修改
3. validator_wrap flask route的装饰器,针对request.json/requests.values的参数校验,只是校验
4. validator_func_wrap 针对普通函数的参数校验以及修改,注意不要使用python传参的高级特性(一个参数对应多个值),这个方法可以脱离flask使用,所以如果需要就直接copy过去吧.

## 测试
1. 我curl测试了一些,可能不完整,哈哈,要是担心的话,参考这里  https://github.com/mansam/validator.py/blob/master/tests/test_validator.py
2. 支持python2和python3