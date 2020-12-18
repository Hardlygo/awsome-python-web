'''
Author: your name
Date: 2020-12-14 20:52:38
LastEditTime: 2020-12-14 21:27:04
LastEditors: Please set LastEditors
Description: In User Settings Edit
FilePath: \leetcodei:\python-workspace\awsome-python-web\www\error.py

自定义错误类
'''

class APIError(Exception):
    '''
    the base APIError which contains error(required), data(optional) and message(optional).
    '''

    def __init__(self, error, data='', message=''):
        super(APIError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class APIValueError(APIError):
    '''
    Indicate the input value has error or invalid. The data specifies the error field of input form.
    '''

    def __init__(self, field, message=""):
        super(APIValueError, self).__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''

    def __init__(self,  field, message=""):
        super(APIValueError, self).__init__("value:not found", field, message)


class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''

    def __init__(self, message=""):
        super(APIValueError, self).__init__(
            "value:forbidden", "permission", message)
