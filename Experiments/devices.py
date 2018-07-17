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
        self.Query(current_time, global_jobs)
        self.ProcLocalJobs(current_time)

    def Query(self, current_time, global_jobs):
        '''
        pull a request to the superior device, the type is based on current sate

        Type 0x0:
            Middle server pushes gradients to Main server
        Type 0x1:
            Main server pushes new model to Middle server
        Type 0x2:
            Middle server pushes new model to Edge devices
        Type 0x3:
            Middle server pushes prediction to Edge devices
        Type 0x4:
        '''
        pass

    def Receive(self, current_time, global_jobs):
        pass

    def Check_queue(self):
        # check the job queue, if not empty, fech jobs to process
        pass

    def ProcLocalJobs(self,current_time):
        pass



class Main_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio, RAM):
        super(Main_Server, self).__init__(Name, Max_flops, Port_ratio,RAM)
        self.Type = 0x0
    def Query(self, current_time, global_jobs):
        pass
    def Receive(self, current_time, global_jobs):
        pass
    def ProcLocalJobs(self,current_time):
        pass

class Middle_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio, RAM):
        super(Middle_Server, self).__init__(Name, Max_flops, Port_ratio,RAM)
        self.Type = 0x1
    def Query(self, current_time, global_jobs):
        pass
    def Receive(self, current_time, global_jobs):
        if(self.Name in global_jobs.keys()):
            for my_job in global_jobs[self.Name]:
                if my_job.receive_time <= current_time:
                    #print(self.Name," ",self.experiance_pool_size)
                    if(my_job.job_type==TYPE_JOB_SEND_MEDIAS):
                        self.experiance_pool_size+=1
                        self.jobs_pool.append(my_job)
                    elif(my_job.job_type==TYPE_JOB_SEND_MODEL_GRADIENTS):
                        pass
                        #global_jobs[self.Name].remove(my_job)
                    global_jobs[self.Name].remove(my_job)
    def ProcLocalJobs(self,current_time):
        if(not len(self.jobs_pool) == 0):
            for job in self.jobs_pool:
                


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
        self.Query(current_time, global_jobs)
        self.ProcLocalJobs(current_time)

    def Query(self, current_time, global_jobs):
        jobs = self.Decide_jobs(current_time)
        for job in jobs:
            if(self.superior_device.Name in global_jobs.keys()):
                global_jobs[self.superior_device.Name].append(job)
            else:
                global_jobs[self.superior_device.Name] = [job]

    def Receive(self, current_time, global_jobs):
        if(self.Name in global_jobs.keys()):
            for job_to_receive in global_jobs[self.Name]:
                if job_to_receive.receive_time <= current_time:
                    self.local_jobs.append(job_to_receive)
                    global_jobs[self.Name].remove(job_to_receive)

    def ProcLocalJobs(self, current_time):
        for local_job in self.local_jobs:
            if local_job.job_type == TYPE_JOB_IOT_ACT:
                pass
            elif local_job.job_type == TYPE_JOB_IOT_BACKWARD:
                #TODO decide BACKWARD logic
                pass
            elif local_job.job_type == TYPE_JOB_IOT_INFERENCE:
                #TODO decide INFERENCE logic
                pass

    def get_cpu_processing_time(self, job):
        return job.computing_resources / self.Max_flops

    def Decide_jobs(self, current_time):
        jobs = []

        random.seed(current_time)
        if(random.random()<0.01):
            job = Job(TYPE_JOB_SEND_MEDIAS, cfg_Input_size, current_time, cfg_Resource_Model_forward)
            job.set_receive_time(current_time+cfg_IOT_SERVER_DELAY)
            job.creater = self.Name
            jobs.append(job)

        return jobs