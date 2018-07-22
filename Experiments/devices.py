import Queue
import random
from job import *
from DEFINES import *
from config import *

"""
All the devices are running under the similar mode:
when every time slot steps, it first observes the global jobs pool to check 
if any jobs can be received at that time, then it creates the local jobs based 
on the states. After that it checks the local jobs pool to process jobs, 
Finally it decides what message can be sent to other devices and put it to the
global jobs pool
"""
class Device(object):
    def __init__(self,Name):
        self.Name = Name
        self.Events = []


class Server(Device):
    def __init__(self, Name, Max_flops, Port_ratio):
        super(Server, self).__init__(Name)
        # the max computing ability
        self.Name = Name
        # Server type:
        # 0x0 : Main Server
        # 0x1 : Middle Server
        self.Type = None
        # The Computation capacity is the max computation resource a device has
        # *Gflops
        self.Computation_capacity = Max_flops
        self.idle_compution_resource = Max_flops
        # The Network Port ratio,for server the default is 10Gbps.
        # if several devices connected to the same server they share the bandwidth
        # *Mbps
        self.Port_ratio = Port_ratio
        self.idle_bandwidth = Port_ratio
        # inferior devices are devices connected to the server and are inferior to this server
        # in the topology
        self.inferior_devices = []
        # in this system each device only has one superior device
        self.superior_device = None
        # The jobs queue only contains the jobs waiting to be computed
        self.jobs_pool = []
        
        # The experiance pool size represents the total data pairs received
        self.experiance_pool_size = 0

    def Connect(self, Device):
        '''
        Form the topology
        '''
        Device.superior_device = self
        self.inferior_devices.append(Device)

    def Process(self,current_time,global_jobs):
        self.Receive(current_time, global_jobs)
        self.ProcLocalJobs(current_time)
        self.Query(current_time, global_jobs)

    def Query(self, current_time, global_jobs):
        for job in self.jobs_pool:
            if job.done:

                #if the jobs are done, decide where to send out the results

                if job.job_type == TYPE_JOB_SERVER_INFERENCE:

                    #send the output of inference (action) to inferer devices

                    new_job = Job(TYPE_COM_SERVER2IOT_ACTIONS,current_time,0)
                    new_job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
                    new_job.set_creater(self.Name)

                    #send the action to the creator of inference querying job

                    if(not job.creater in global_jobs.keys()):
                        global_jobs[job.creater] = []
                    global_jobs[job.creater].append(new_job)

                    self.jobs_pool.remove(job)
                elif job.job_type == TYPE_JOB_SERVER_BACKWARD:

                    #update the local parameters

                    self.jobs_pool.remove(job)
                    print "SERVER_BACKWARD "+self.Name

                elif job.job_type == TYPE_JOB_SERVER_SYNC_GRADIENTS:

                    #sync the

                    print "SERVER_SYNC_GRADIENTS "+self.Name
                    self.jobs_pool.remove(job)
                
                elif job.job_type == TYPE_JOB_SERVER_UPDATE_MODEL:
                    print "SERVER_UPDATE_MODEL "+self.Name
                    self.jobs_pool.remove(job)

                # if DEBUG:
                #    // print "time :", current_time,self.Name+"\t"+" receive Type",job.job_type,"From "+job.creater

    def Receive(self, current_time, global_jobs):
        if(self.Name in global_jobs.keys()):
            for my_job in global_jobs[self.Name]:
                if my_job.receive_time <= current_time:
                    if(my_job.job_type==TYPE_COM_IOT2SERVER_MEDIAS):

                        # receive the oberved environments data sent by IOT

                        self.experiance_pool_size+=1

                        # creat a inference job to get the action

                        new_job = Job(TYPE_JOB_SERVER_INFERENCE,cfg_Input_size,current_time,cfg_Resource_Model_forward)
                        new_job.set_creater(my_job.creater)
                        self.jobs_pool.append(new_job)

                    elif(my_job.job_type==TYPE_COM_IOT2SERVER_MODEL_GRADIENTS):
                        # receive Model gradients from IOT, sync it
                        #TODO
                        new_job = Job(TYPE_JOB_SERVER_SYNC_GRADIENTS,cfg_Model_Gradients_size,current_time,cfg_SyncModel_flops)
                        new_job.set_creater(my_job.creator)
                        self.jobs_pool.append(new_job)

                    elif(my_job.job_type==TYPE_COM_SERVER2SERVER_MODEL_GRADIENTS):

                        # receive Model gradients from server, sync it
                        '''
                        Current poliy: accumudate the gradients and step for every T time slots
                        '''

                        new_job = Job(TYPE_JOB_SERVER_ACCUMULATE_GRADIENTS, cfg_Model_Gradients_size, current_time,
                                      cfg_SyncModel_flops)
                        new_job.set_creater(my_job.creator)
                        if(current_time%cfg_Main_server_update_interval == 0):
                            new_job = Job(TYPE_JOB_SERVER_STEP)
                        self.jobs_pool.append(new_job)
                    elif (my_job.job_type == TYPE_COM_IOT2SERVER_REWARDS):

                    elif(my_job.job_type==TYPE_COM_SERVER2SERVER_MODEL_PARAMETER):

                        # receive updated Model Parameters from server, and update the local model

                        new_job = Job(TYPE_JOB_SERVER_UPDATE_MODEL)
                        new_job.set_creater(my_job.creator)
                        self.jobs_pool.append(new_job)
                    global_jobs[self.Name].remove(my_job)

                    if DEBUG:
                        print( "time :", current_time,self.Name + " receive Type",my_job.job_type,"From "+my_job.creater)

    def ProcLocalJobs(self,current_time):
        for job in self.jobs_pool:
            if(job.job_type == TYPE_JOB_SERVER_INFERENCE):
                if job.computing_resources>0:
                    job.computing_resources -= self.idle_compution_resource*cfg_TimeSlot
                else:
                    job.done = True

            elif(job.job_type == TYPE_JOB_SERVER_BACKWARD):
                if job.computing_resources>0:
                    job.computing_resources -= self.idle_compution_resource*cfg_TimeSlot
                else:
                    job.done = True
            elif(job.job_type == TYPE_JOB_SERVER_SYNC_GRADIENTS):
                job.done = True
            elif(job.job_type == TYPE_JOB_SERVER_UPDATE_MODEL):
                job.done = True

class Main_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio):
        super(Main_Server, self).__init__(Name, Max_flops, Port_ratio)
        self.Type = 0x0

class Middle_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio):
        super(Middle_Server, self).__init__(Name, Max_flops, Port_ratio)
        self.Type = 0x1

class IoT(Device):
    def __init__(self, Name, Max_flops, Port_ratio, Battery):
        super(IoT, self).__init__(Name)
        self.Name = Name
        self.Max_flops = Max_flops
        self.Port_ratio = Port_ratio
        self.Battery = Battery
        self.superior_device = None
        self.inferior_devices = []
        self.local_jobs = []
        self.Wating_for_action = False

    def Process(self, current_time, global_jobs):
        # watch the global jobs pool, put the received jobs into local jobs pool
        self.Receive(current_time, global_jobs)
        self.ProcLocalJobs(current_time)
        self.Query(current_time, global_jobs)

    def Query(self, current_time, global_jobs):
        jobs = self.Decide_jobs(current_time)
        for job in jobs:
            if(self.superior_device.Name in global_jobs.keys()):
                global_jobs[self.superior_device.Name].append(job)
            else:
                global_jobs[self.superior_device.Name] = [job]
            jobs.remove(job)

    def Receive(self, current_time, global_jobs):
        #receive the (a) or updated model parameters from server
        if(self.Name in global_jobs.keys()):
            for job_to_receive in global_jobs[self.Name]:
                if job_to_receive.receive_time <= current_time:
                    if job_to_receive.job_type == TYPE_COM_SERVER2IOT_ACTIONS:
                        #creat an action job
                        new_job = Job(TYPE_JOB_IOT_ACT,0,current_time,0)
                        self.local_jobs.append(new_job)
                    elif job_to_receive.job_type == TYPE_COM_SERVER2IOT_MODEL_GRADIENTS:
                        #not impleted
                        pass
                    elif job_to_receive.job_type == TYPE_COM_SERVER2IOT_MODEL_PARAMETERS:
                        #not impleted
                        pass
                    global_jobs[self.Name].remove(job_to_receive)

                    if DEBUG:
                        print( "time :", current_time,self.Name+" receive Type",job_to_receive.job_type,"From "+job_to_receive.creater)

    def ProcLocalJobs(self, current_time):
        for local_job in self.local_jobs:
            if local_job.job_type == TYPE_JOB_IOT_ACT:
                #the iot device acts and return the rewards
                #print self.Name+ " act "
                self.Wating_for_action = False
                new_job = Job(TYPE_COM_IOT2SERVER_REWARDS,0,current_time)
                new_job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
                self.local_jobs.append(new_job)
                self.local_jobs.remove(local_job)

            elif local_job.job_type == TYPE_JOB_IOT_BACKWARD:
                #back ward locally
                #TODO decide BACKWARD logic


                pass
            elif local_job.job_type == TYPE_JOB_IOT_INFERENCE:
                #inference locally
                #TODO decide INFERENCE logic
                pass
            # elif local_job.job_type == TYPE_JOB_:
            #     pass

    def Decide_jobs(self, current_time):
        jobs = []
        random.seed(current_time)
        if(random.random()<0.01 and not self.Wating_for_action):
            #send (s) to uper_server
            job = Job(TYPE_COM_IOT2SERVER_MEDIAS, cfg_Input_size, current_time, cfg_Resource_Model_forward)
            job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
            job.creater = self.Name
            jobs.append(job)
            self.Wating_for_action = True

        for job in self.local_jobs:
            if job.job_type == TYPE_COM_IOT2SERVER_REWARDS:
                new_job = Job(TYPE_COM_IOT2SERVER_REWARDS,0,current_time)
                new_job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
                new_job.set_creater(self.Name)
                jobs.append(new_job)
                self.local_jobs.remove(job)
        return jobs