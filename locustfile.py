from locust import HttpUser, task
import time
from distribute_challenge import object_to_string

#adapted class as wrapper to use for Locust.io , run method returns encoded object for use with locust package's post
def compute_this():
    class Compute_this():
        def __init__(self, func):
            self.func = func
            
        def __call__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            return self

        #method run to return function + args class representation
        def run(self):
            # class to represent function + args for POST
            class Compute_submit():
                def __init__(self, func, args, kwargs):
                    self.func = func
                    self.args = args
                    self.kwargs = kwargs
                
            compute_obj = Compute_submit(self.func,self.args,self.kwargs)
            
            # object to utf-8
            compute_utf8 = object_to_string(compute_obj)

            return {'func': compute_utf8}

    return Compute_this

# Class represents simulated user
class QuickstartUser(HttpUser):

    # wait_time = between(1, 2) # Could set wait_time between simulated user attempted POSTs

    host = "http://localhost:6000"

    #Task which each simulated user runs, like main.py but using locust's post method
    @task
    def hello_world(self):
        @compute_this()
        def func(x):
            time.sleep(x)
            return x*x

        data_obj =  func(2).run()

        self.client.post("/", data = data_obj)


#standalone command for locust:
#locust -f locustfile.py --csv=example --headless -u 100 -r 40 --run-time 50s
