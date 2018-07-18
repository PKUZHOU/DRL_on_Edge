import Queue
import random
from job import *
from DEFINES import *
from config import *
class Server(object):
    def __init__(self, Name, Max_flops, Port_ratio, RAM):
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
        # '''
        # TODO: The effect of RAM parameter is waiting to explore
        # '''
        self.RAM = RAM
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
                if job.job_type == TYPE_JOB_SERVER_INFERENCE:
                    new_job = Job(TYPE_COM_SERVER2IOT_ACTIONS,current_time,0)
                    new_job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
                    if(not job.creater in global_jobs.keys()):
                        global_jobs[job.creater] = []
                    global_jobs[job.creater].append(new_job)
                    self.jobs_pool.remove(job)
                elif job.job_type == TYPE_JOB_SERVER_BACKWARD:
                    pass
                elif job.job_type == TYPE_JOB_SERVER_SYNC_GRADIENTS:
                    pass
    def Receive(self, current_time, global_jobs):
        if(self.Name in global_jobs.keys()):
            for my_job in global_jobs[self.Name]:
                if my_job.receive_time <= current_time:
                    if(my_job.job_type==TYPE_COM_IOT2SERVER_MEDIAS):
                        # receive the environments sent by IOT
                        self.experiance_pool_size+=1
                        # creat a inference job to get the action
                        new_job = Job(TYPE_JOB_SERVER_INFERENCE,cfg_Input_size,current_time,cfg_Resource_Model_forward)
                        new_job.set_creater(my_job.creater)
                        self.jobs_pool.append(new_job)

                    elif(my_job.job_type==TYPE_COM_IOT2SERVER_MODEL_GRADIENTS):
                        # receive Model gradients from IOT, sync it
                        new_job = Job(TYPE_JOB_SERVER_SYNC_GRADIENTS,cfg_Model_Gradients_size,current_time,cfg_SyncModel_flops)
                        new_job.set_creater(my_job.creator)
                        self.jobs_pool.append(new_job)

                    elif(my_job.job_type==TYPE_COM_SERVER2SERVER_MODEL_GRADIENTS):
                        # receive Model gradients from server, sync it
                        new_job = Job(TYPE_JOB_SERVER_SYNC_GRADIENTS, cfg_Model_Gradients_size, current_time,
                                      cfg_SyncModel_flops)
                        new_job.set_creater(my_job.creator)
                        self.jobs_pool.append(new_job)

                    elif(my_job.job_type==TYPE_COM_SERVER2SERVER_MODEL_PARAMETER):
                        # receive updated Model Parameters from server, and update the local model
                        pass

                    global_jobs[self.Name].remove(my_job)

    def ProcLocalJobs(self,current_time):
        for job in self.jobs_pool:
            if(job.job_type == TYPE_JOB_SERVER_INFERENCE):
                if job.computing_resources>0:
                    job.computing_resources -= self.idle_compution_resource*cfg_TimeSlot
                else:
                    job.done = True

            elif(job.job_type == TYPE_JOB_SERVER_BACKWARD):
                job.done = True
            elif(job.job_type == TYPE_JOB_SERVER_SYNC_GRADIENTS):
                job.done = True

class Main_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio, RAM):
        super(Main_Server, self).__init__(Name, Max_flops, Port_ratio,RAM)
        self.Type = 0x0

class Middle_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio, RAM):
        super(Middle_Server, self).__init__(Name, Max_flops, Port_ratio,RAM)
        self.Type = 0x1

class IoT:
    def __init__(self, Name, Max_flops, Port_ratio, Battery, RAM):
        self.Name = Name
        self.Max_flops = Max_flops
        self.Port_ratio = Port_ratio
        self.Battery = Battery
        self.RAM = RAM
        self.superior_device = None
        self.inferior_devices = []
        self.local_jobs = []

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
                    self.local_jobs.append(job_to_receive)
                    global_jobs[self.Name].remove(job_to_receive)

    def ProcLocalJobs(self, current_time):
        for local_job in self.local_jobs:
            if local_job.job_type == TYPE_JOB_IOT_ACT:
                #the iot device acts and return the rewards
                print(self.Name, " act ")
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
    def get_cpu_processing_time(self, job):
        return job.computing_resources / self.Max_flops

    def Decide_jobs(self, current_time):
        jobs = []
        random.seed(current_time)
        if(random.random()<0.01):
            #send (s) to uper_server
            job = Job(TYPE_COM_IOT2SERVER_MEDIAS, cfg_Input_size, current_time, cfg_Resource_Model_forward)
            job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
            job.creater = self.Name
            jobs.append(job)

        for job in self.local_jobs:
            if job.job_type == TYPE_COM_IOT2SERVER_REWARDS:
                new_job = Job(TYPE_COM_IOT2SERVER_REWARDS,0,current_time)
                new_job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
                new_job.set_creater(self.Name)
                jobs.append(new_job)
                self.local_jobs.remove(job)
        return jobs