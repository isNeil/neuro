import subprocess
from time import sleep
import os
import csv
import shutil
# log of user defined server hooks and their timings
gunicorn_log = 'gunicorn_log.csv'

# folder of gunicorn log formatted for seeing throughput and allocation of each worker
worker_logs_dir = 'gunicorn_worker_logs'

# 10 second sliding window data from locust of various metrics (requests/s, failures/s)
locust_history = 'locust_stats_history.csv'

# output of scale test 
scaling_test_out = 'scaling_test.csv'

# want to know allocation and throughput of each worker -> only need to account for 'pre' and 'post' hooks. 'pre' tells us allocation (allocated request to worker) and 'post' tells us throughput (completed requests of worker)
# creates log file for each worker of when they are initiated ('init') and each request they process ('pre' and 'post')    
# requires a gunicorn_log
def get_workers_dict(gunicorn_log,worker_logs_dir):
    
    #over writes the folder with new data
    if os.path.isdir(worker_logs_dir):
        shutil.rmtree(worker_logs_dir)
        
    os.mkdir(worker_logs_dir)

    workers_dict = {} # tally to keep track of each worker's completed request 'post'
    start_time = None # start time, first 'pre' request for calculating instantaneous throughput 

    #iterate through gunicorn_log and extract information for each worker to respective file
    with open(gunicorn_log, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        #[time, pid, hook]
        for row in csvreader:

            # start time to work out instantaneous throughputs per worker
            if row[2]=='pre' and start_time is None:
                start_time=float(row[0])

            #update throughput count first so that rate added after is correct
            if row[2]=='post':
                if str(row[1]) in workers_dict:
                    workers_dict[str(row[1])]+=1 
                else:
                    workers_dict[str(row[1])]=1
            
            #for important hooks to our deliverables, [time, hook, instant throughput rate] is saved in worker_logs_dir under the worker.pid filename 
            if row[2]=='init' or row[2]=='pre' or row[2]=='post':
                if start_time is not None:

                    if str(row[1]) in workers_dict:
                        count = workers_dict[str(row[1])]
                    else:
                        count = 0
                    #calculate instaneous throughput rate avoiding /0 for worker that sets start_time
                    time_since_start = float(row[0]) - start_time
                    if time_since_start == 0:
                        instant_throughput = 'inf'
                    else:
                        instant_throughput = count/time_since_start
                else: 
                    instant_throughput = 'None'
                with open(os.path.join(worker_logs_dir, row[1]+'.csv'), "a") as file:
                    # [time, hook, instantaneous rate throughput]
                    file.write("{} {} {}\n".format(row[0], row[2], instant_throughput))
            
        return workers_dict


def get_latest(csv_file,column):
    with open(csv_file, 'r') as file:
        lines = file.readlines()
        first_line_list = lines[0].split(',')

        #each line is a 10s sliding window avg of stats, use the final line to ensure throughput is at steadystate (not affected by ramp up of locust connection)
        final_line_list = lines[-1].split(',')
        return final_line_list[first_line_list.index(column)] 


# runs subprocesses of gunicorn server and locust to stress test api service, looping over list of different numbers of workers and number of simulated user requests. Outputs result to scaling_test_out file.
def test_loop(scaling_test_out,gunicorn_log,list_num_users,list_num_workers):

    with open(scaling_test_out, "w") as myfile:
        myfile.write("num_users,num_workers,rps\n")

    for num_users in list_num_users:
        for num_workers in list_num_workers:
            
            # set csv column headers
            with open(gunicorn_log, "w") as myfile:
                myfile.write("time,pid,hook\n")

            # stale pidfile needs to be deleted for new pidfile to be saved?
            if os.path.exists('pidfile'):
                os.remove('pidfile')

            #start gunicorn flask server 
            gunicorn_cmd ="gunicorn -c gunicorn_config.py --pid pidfile --bind 0.0.0.0:6000 --workers {} --threads 1 --timeout 120 flask_server:app".format(num_workers).split(' ')

            proc = subprocess.Popen(gunicorn_cmd)

            locust_master_cmd ="locust -f locustfile.py --csv=example --headless -u {} -r 40 --run-time 50s".format(num_users).split(' ')
            
            proc2 = subprocess.Popen(locust_master_cmd)

            #polls locust to check if it has completed its test, when finished or it times out after 60s, its processes terminates along with gunicorn server 
            poll = proc2.poll()
            for i in range(60):
                sleep(1)
                if poll is not None:
                    break
                poll = proc2.poll()
            
            proc.terminate()
            proc2.terminate()
            
            # locust example_stats_history.csv, Requests/s includes failures so subtract Failures/s to get throughput
            rps = get_latest(locust_history,'Requests/s')
            fps = get_latest(locust_history,'Failures/s')
            rate_throughput = str(float(rps)-float(fps))

            #output results to scaling_test_out
            with open(scaling_test_out, "a") as file:
                file.write("{},{},{}\n".format(num_users,num_workers,rate_throughput))

if __name__ == "__main__":
    #10 concurrent request, 10 workers
    test_loop(scaling_test_out,gunicorn_log,[10],[10])
    # create worker logs for the final gunicorn_log
    get_workers_dict(gunicorn_log,worker_logs_dir)





