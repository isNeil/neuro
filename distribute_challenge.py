from base64 import b64encode, b64decode
import pickle
import cloudpickle
import requests

url = 'http://localhost:6000'

# return utf-8 string encoding of cloudpickled object bytestring via b64
def object_to_string(obj):
    obj_bytes = cloudpickle.dumps(obj)
    obj_b64 = b64encode(obj_bytes)
    return obj_b64.decode('utf-8')

# decode b64 and unpickle to get back to obj
def b64_to_object(b64):
    bytestring = b64decode(b64)
    return pickle.loads(bytestring)

#class as wrapper to POST function to url
def compute_this():
    class Compute_this():
        def __init__(self, func):
            self.func = func
            self.url = url
            
        def __call__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            return self

        #method run to POST function + args representation to server
        def run(self):
            # class to represent function + args for POST
            class Compute_submit():
                def __init__(self, func, args, kwargs):
                    self.func = func
                    self.args = args
                    self.kwargs = kwargs
            
            compute_obj = Compute_submit(self.func,self.args,self.kwargs)
            
            # cloudpickle object to utf-8 for convenient http POST
            compute_utf8 = object_to_string(compute_obj)

            #response
            res = requests.post(url, data = {'func': compute_utf8})

            # needs error handling here if res.status_code != 200

            # response (res.content) is pickled and encoded to utf-8, so we undo encoding and pickling
            return b64_to_object(res.content)

    return Compute_this

