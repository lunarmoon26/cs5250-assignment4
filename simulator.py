'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt
'''
import sys
from operator import attrgetter
from copy import deepcopy

input_file = 'input.txt'

def pop_new_process(process_list, current_time):
    new_proc = [process for process in process_list if process.arrive_time == current_time]
    if len(new_proc):
        process_list.remove(new_proc[0])
        return new_proc[0]
    return None

class Process:
    last_scheduled_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrival_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    schedule = []
    ready = []
    current_time = 0
    waiting_time = 0
    avail_process = deepcopy(process_list)
    current_process = None
    remain_time = 0

    while len(avail_process) or len(ready):

        if current_process:
            if current_process.burst_time == 0:
                current_process = None
            elif remain_time == 0:
                current_process.last_scheduled_time = current_time
                ready.append(current_process) # append to last of ready queue
                current_process = None 

        process = pop_new_process(avail_process, current_time)
        if process:
            ready.append(process)

        if ready and not current_process:
            current_process = ready.pop(0)
            waiting_time += (current_time - current_process.last_scheduled_time) if current_process.last_scheduled_time > 0 else (current_time - current_process.arrive_time)
            schedule.append((current_time,current_process.id))
            remain_time = time_quantum

        if current_process and remain_time:
            current_process.burst_time -= 1
            remain_time -= 1

        current_time += 1

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SRTF_scheduling(process_list):
    schedule = []
    ready = []
    current_time = 0
    waiting_time = 0
    avail_process = deepcopy(process_list)
    current_process = None

    while len(avail_process) or len(ready):
        # Mark the process as complete
        if current_process and current_process.burst_time == 0:
            current_process = None

        process = pop_new_process(avail_process, current_time)
        if process:
            ready.append(process)

        if len(ready) and not current_process:
            least_process = min(ready,key=attrgetter('burst_time', 'arrive_time'))
            # If least remaining time process in ready available
            if least_process:
                ready.remove(least_process)
                schedule.append((current_time,least_process.id))
                current_process = least_process
                waiting_time += (current_time - current_process.last_scheduled_time) if current_process.last_scheduled_time > 0 else (current_time - current_process.arrive_time)
        elif process and current_process:
            if process.burst_time < current_process.burst_time:
                # Switch to arrival process
                current_process.last_scheduled_time = current_time
                ready.append(current_process)
                ready.remove(process)
                schedule.append((current_time,process.id))
                current_process = process
        
        if current_process:
            current_process.burst_time -= 1
        
        current_time += 1

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

def SJF_scheduling(process_list, alpha):
    schedule = []
    ready = []
    current_time = 0
    waiting_time = 0
    avail_process = deepcopy(process_list)
    current_process = None
    estimate_burst = {}

    while len(avail_process) or len(ready):

        if current_process and current_process.burst_time == 0:
            actual = current_time - current_process.last_scheduled_time
            estimate_burst[current_process.id] = alpha * actual + (1 - alpha) * estimate_burst[current_process.id]
            current_process = None

        process = pop_new_process(avail_process, current_time)
        if process:
            if process.id not in estimate_burst:
                estimate_burst[process.id] = 5
            ready.append(process)

        if len(ready) and not current_process:
            ready.sort(key=lambda p: (estimate_burst[p.id], p.arrive_time))
            current_process = ready.pop(0)
            waiting_time += current_time - current_process.arrive_time
            schedule.append((current_time,current_process.id))
            current_process.last_scheduled_time = current_time

        if current_process:
            current_process.burst_time -= 1

        current_time += 1

    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time
    # return (["to be completed, scheduling SJF without using information from process.burst_time"],0.0)


def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])

