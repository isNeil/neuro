# neuro challenge

distribute_challenge.py provides the client-side API module used in main.py.

The api allows remote submission of functions to flask app defined in flask_server.py.

Flask app is served by Gunicorn with configurable number of workers to client. One thread allocated to each worker means workers run a single user function at a time.

The application is load tested inside test_loop.py.

Locust.io is used to create request load with simulated user tasks defined in locustfile.py.

Gunicorn server hooks provide additional monitoring of individual workers configured by gunicorn_config.py.

Running test_loop fuction inside test_loop produces log files from locust.io (locust_*.csv) and gunicorn (gunicorn_log.csv) for varying number of workers and request loads.

Directory scaling_test_results contains results of test_loop with files for overall throughput (OK response's /s) for different number of workers and request rate. These are parsed from locust_stats_history.csv.

Function get_workers_dict in test_loop also provides further parsing of gunicorn_log.csv to give log files for each worker in directory gunicorn_worker_logs.
  
  




