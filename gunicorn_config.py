from time import time

"""
Gunicorn Server Hooks functions, used to log hook events in gunicorn_log.csv 
under header: time,pid,hook
"""
gunicorn_log = 'gunicorn_log.csv'

def on_starting(server):
    """
    on server start
    """
    with open(gunicorn_log, "a") as myfile:
        myfile.write("{},,reload\n".format(str(time())))

def on_reload(server):
    """
    on server reload
    """
    with open(gunicorn_log, "a") as myfile:
        myfile.write("{},,reload\n".format(str(time())))

def post_worker_init(worker):
    """
    on worker initialization
    """
    with open(gunicorn_log, "a") as myfile:
        myfile.write("{},{},init\n".format(str(time()), str(worker.pid)))

def pre_request(worker, req):
    """
    before a worker processes the request
    """
    with open(gunicorn_log, "a") as myfile:
        myfile.write("{},{},pre\n".format(str(time()), str(worker.pid)))

def post_request(worker, req): #(req.method, req.path),
    """
    after a worker processes the request
    """
    with open(gunicorn_log, "a") as myfile:
        myfile.write("{},{},post\n".format(str(time()), str(worker.pid)))

def worker_abort(worker):
    """
    on worker SIGABRT signal (typically timeout)
    """
    with open(gunicorn_log, "a") as myfile:
        myfile.write("{},{},SIGABRT\n".format(str(time()), str(worker.pid)))


def worker_exit(server, worker):
    """
    on worker exit worker process
    """
    with open(gunicorn_log, "a") as myfile:
        myfile.write("{},{},exit\n".format(str(time()), str(worker.pid)))
