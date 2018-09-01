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

exceed_delay = 0


class Device(object):
    def __init__(self, Name):
        self.Name = Name
        self.Events = []

class Server(Device):
    def __init__(self, Name, Max_flops, Port_ratio):
        super(Server, self).__init__(Name)
        # Server type:
        # 0x0 : Main Server
        # 0x1 : Middle Server
        self.Type = None
        # The Computation capacity is the max computation resource a device has *Gflops
        self.Computation_capacity = Max_flops
        # The Network Port ratio,for server the default is 10Gbps.
        # *Mbps
        self.Port_ratio = Port_ratio
        # inferior devices are devices connected to the server and are inferior to this server in the topology
        self.inferior_devices = []
        # in this system each device only has one superior device
        self.superior_device = None
        # The jobs queue only contains the jobs waiting to be computed
        self.jobs_pool = []
        # The experiance pool size represents the total data pairs received
        self.allocated_band_width = {}
        self.num_inferior_device = 0
        self.experiance_pool_size = 0
        self.train_DRL_stamp = 0
        self.training_queue = 0
        self.training_interval = 5
        self.num_delay = 0
        self.old_num_delay = 0
        self.num_DRL_backwards = 0
        self.DRL_back_ward_persecond = 0
        self.num_update = 0
        self.latencies = []
    def allocate_band_width(self):
        for device in self.inferior_devices:
            self.allocated_band_width[device.Name] = float(cfg_Middle_server_port_ratio)/self.num_inferior_device

    def takePri(self,elem):
        return elem.priority

    def takeDeadline(selfs,elem):
        return elem.deadline

    def Connect(self, Device):
        '''
        Connect a inferior device to this device
        '''
        Device.superior_device = self
        self.inferior_devices.append(Device)
        self.num_inferior_device+=1
    def Process(self, current_time, global_jobs):
        """
        :param current_time: current time step
        :param global_jobs:  the global jobs pool (represents the transmitting jobs)
        :return: None

        for every timeslot, first check if any jobs can be received
                            then process local job
                            finally send out some informations
        """
        self.Receive(current_time, global_jobs)
        self.ProcLocalJobs(current_time)
        self.Query(current_time, global_jobs)

    def get_jobs_to_receive(self, global_jobs, current_time):
        jobs_to_receive = []
        if (self.Name in global_jobs.keys()):
            for job_to_receive in global_jobs[self.Name]:
                if job_to_receive.receive_time <= current_time:
                    jobs_to_receive.append(job_to_receive)
        return jobs_to_receive

    def Receive(self, current_time, global_jobs):
        # get the jobs can be received in this timeslot
        jobs_to_receive = self.get_jobs_to_receive(global_jobs, current_time)

        for job_to_receive in jobs_to_receive:
            if (job_to_receive.job_type == TYPE_COM_IOT2SERVER_MEDIAS):
                # receive the oberved environments data sent by IOT
                # creat a inference job to get the action
                new_job = Job(TYPE_JOB_SERVER_DRL_INFERENCE, cfg_Input_size, current_time,\
                              cfg_Resource_Model_forward,priority=cfg_Inference_priority)
                new_job.set_creater(job_to_receive.creater)
                new_job.deadline = job_to_receive.deadline
                self.jobs_pool.append(new_job)
            #########################
            ###   Model gradients  ##
            #########################
            elif (job_to_receive.job_type == TYPE_COM_SERVER2SERVER_DRL_MODEL_GRADIENTS):
                # receive Model gradients from server, sync it
                '''
                Current poliy: accumudate the gradients and step for every T time slots
                '''
                new_job = Job(TYPE_JOB_SERVER_ACCUMULATE_GRADIENTS, cfg_Model_Gradients_size, current_time,
                              cfg_SyncModel_flops)
                new_job.set_creater(job_to_receive.creator)
                new_job.deadline = job_to_receive.deadline
                if (current_time % cfg_Main_server_update_interval == 0):
                    new_job = Job(TYPE_JOB_SERVER_STEP)
                self.jobs_pool.append(new_job)
            elif (job_to_receive.job_type == TYPE_COM_SERVER2SERVER_RAN_MODEL_GRADIENTS):
                # receive Model gradients from server, sync it
                '''
                Current poliy: accumudate the gradients and step for every T time slots
                '''
                new_job = Job(TYPE_JOB_SERVER_ACCUMULATE_GRADIENTS, cfg_Model_Gradients_size, current_time,
                              cfg_SyncModel_flops)
                new_job.set_creater(job_to_receive.creator)
                new_job.deadline = job_to_receive.deadline
                if (current_time % cfg_Main_server_update_interval == 0):
                    new_job = Job(TYPE_JOB_SERVER_STEP)
                self.jobs_pool.append(new_job)
            ########################
            ###  sync prameters ####
            ########################
            elif (job_to_receive.job_type == TYPE_COM_SERVER2SERVER_DRL_MODEL_PARAMETER):
                # receive updated Model Parameters from server, and update the local model
                new_job = Job(TYPE_JOB_SERVER_UPDATE_MODEL)
                new_job.set_creater(job_to_receive.creator)
                new_job.deadline = job_to_receive.deadline
                self.jobs_pool.append(new_job)

            elif (job_to_receive.job_type == TYPE_COM_SERVER2SERVER_RAN_MODEL_PARAMETER):
                # receive updated Model Parameters from server, and update the local model
                new_job = Job(TYPE_JOB_SERVER_UPDATE_MODEL)
                new_job.set_creater(job_to_receive.creator)
                new_job.deadline = job_to_receive.deadline
                self.jobs_pool.append(new_job)
            #########################
            ###       Tuples       ##
            #########################

            # elif (job_to_receive.job_type == TYPE_COM_IOT2SERVER_TUPLES):
            #     new_job = Job(TYPE_JOB_SERVER_RAN_INFERENCE,cfg_Input_size,current_time,\
            #                   cfg_Resource_Model_forward,priority=cfg_Tuple_priority)
            #     new_job.set_creater(self.Name)
            #     new_job.deadline = job_to_receive.deadline
            #
            #     if not self.old_num_delay+10<self.num_delay:
            #         self.jobs_pool.append(new_job)
            #         self.num_update += 1
            #         print("Update rate : ", self.num_update*1000/current_time)
            # elif (job_to_receive.job_type == TYPE_COM_IOT2SERVER_HALFTUPLES):
            #     new_job = Job(TYPE_JOB_SERVER_RAN_INFERENCE, cfg_Input_size, current_time, \
            #                   cfg_Resource_Model_forward,priority=cfg_Tuple_priority)
            #     new_job.set_creater(self.Name)
            #     new_job.deadline = job_to_receive.deadline
            #     if not self.old_num_delay+10<self.num_delay:
            #         self.jobs_pool.append(new_job)
            #         self.num_update+=1
            #         print("UPdate rate : ",self.num_update*1000/current_time)

            # jobs are received, now delete them from global pool
            global_jobs[self.Name].remove(job_to_receive)
            if DEBUG:
                print("time :", current_time, self.Name + " receive Type", job_to_receive.job_type,
                      "From " + job_to_receive.creater)

    def ProcLocalJobs(self, current_time):
        #TODO: Dynamic-priority based algorithm
        total_computation = self.Computation_capacity/1000.*cfg_TimeSlot

        self.jobs_pool.sort(key=self.takeDeadline,reverse=False)
        # self.jobs_pool.sort(key=self.takePri,reverse=False)
        print "len pool " + str(self.Name) + " "+str(len(self.jobs_pool))
        for job in self.jobs_pool:
            if(not job.done):
                if(job.need_compute and total_computation>0):
                    if(total_computation>=job.computing_resources):
                        job.done = True
                        total_computation-=job.computing_resources
                    else:
                        job.computing_resources-=total_computation
                        total_computation = 0

    def Query(self, current_time, global_jobs):
        for job in self.jobs_pool[:]:
            if job.done:
                # if the jobs are done, decide where to send out the results
                if job.job_type == TYPE_JOB_SERVER_DRL_INFERENCE:
                    # send the output of inference (action) to inferer devices
                    new_job = Job(TYPE_COM_SERVER2IOT_ACTIONS, current_time, 0)
                    new_job.set_receive_time(current_time + cfg_IOT_SERVER_DELAY + cfg_Input_size*8*\
                                             cfg_rho/self.allocated_band_width[job.creater]*1000)
                    new_job.set_creater(self.Name)
                    # send the action to the creator of inference querying job
                    if (not job.creater in global_jobs.keys()):
                        global_jobs[job.creater] = []
                    global_jobs[job.creater].append(new_job)
                elif job.job_type == TYPE_JOB_SERVER_RAN_BACKWARD:
                    # update the local parameters
                    print "SERVER_RAN_BACKWARD " + self.Name

                elif job.job_type == TYPE_JOB_SERVER_DRL_BACKWARD:
                    # update the local parameters
                    self.is_training = False
                    if current_time>=30000:
                        self.num_DRL_backwards+=1
                    self.DRL_back_ward_persecond = self.num_DRL_backwards*1000/current_time

                    print "SERVER_DRL_BACKWARD -----" + self.Name + "DRL_BACK_ward_persecond"+str(self.DRL_back_ward_persecond)

                elif job.job_type == TYPE_JOB_SERVER_SYNC_GRADIENTS:
                    print "SERVER_SYNC_GRADIENTS " + self.Name

                elif job.job_type == TYPE_JOB_SERVER_UPDATE_MODEL:
                    print "SERVER_UPDATE_MODEL " + self.Name
                elif job.job_type == TYPE_JOB_SERVER_RAN_INFERENCE:
                    self.experiance_pool_size+=1
                    print("experiance:", self.experiance_pool_size)
                self.jobs_pool.remove(job)

        if  current_time%self.training_interval==0:
            new_job = Job(TYPE_JOB_SERVER_DRL_BACKWARD,cfg_Input_size,current_time,\
                                      cfg_Resource_Model_backward,priority=5)
            new_job.set_creater(self.Name)
            new_job.need_compute = True
            new_job.deadline = current_time+100*cfg_Max_Delay
            self.jobs_pool.append(new_job)

        if  self.old_num_delay+10<self.num_delay:
            if current_time%1000==0:
                self.training_interval+=1
            print("interval",str(self.training_interval))
            self.old_num_delay = self.num_delay
            # if DEBUG:
            #    // print "time :", current_time,self.Name+"\t"+" receive Type",job.job_type,"From "+job.creater


class Main_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio):
        super(Main_Server, self).__init__(Name, Max_flops, Port_ratio)
        self.Type = 0x0


class Middle_Server(Server):
    def __init__(self, Name, Max_flops, Port_ratio):
        super(Middle_Server, self).__init__(Name, Max_flops, Port_ratio)
        self.Type = 0x1


class IoT(Device):
    def __init__(self, Name, Max_flops, Port_ratio):
        super(IoT, self).__init__(Name)
        self.Name = Name
        self.Max_flops = Max_flops
        self.Port_ratio = Port_ratio
        self.superior_device = None
        self.inferior_devices = []
        self.local_jobs = []
        self.Wating_for_action = False
        self.start_waiting = 0
        self.stamp = 0

    def Process(self, current_time, global_jobs):
        # watch the global jobs pool, put the received jobs into local jobs pool
        self.Receive(current_time, global_jobs)
        self.ProcLocalJobs(current_time)
        self.Query(current_time, global_jobs)

    def Query(self, current_time, global_jobs):
        jobs = self.Decide_jobs(current_time)
        for job in jobs[:]:
            if (self.superior_device.Name in global_jobs.keys()):
                global_jobs[self.superior_device.Name].append(job)
            else:
                global_jobs[self.superior_device.Name] = []
                global_jobs[self.superior_device.Name].append(job)
            if job.job_type == TYPE_JOB_IOT_DRL_INFERENCE:
                self.local_jobs.append(job)

            jobs.remove(job)

        for job in self.local_jobs[:]:
            if job.done:
                if job.job_type == TYPE_JOB_IOT_DRL_INFERENCE:
                    self.local_jobs.append(Job(TYPE_JOB_IOT_ACT, 0, current_time, 0))
                self.local_jobs.remove(job)


    def Receive(self, current_time, global_jobs):
        # receive the (a) or updated model parameters from server
        if (self.Name in global_jobs.keys()):
            for job_to_receive in global_jobs[self.Name][:]:
                if job_to_receive.receive_time <= current_time:
                    if job_to_receive.job_type == TYPE_COM_SERVER2IOT_ACTIONS:
                        # creat an action job
                        new_job = Job(TYPE_JOB_IOT_ACT, 0, current_time, 0)
                        self.local_jobs.append(new_job)
                        # if DRL inference job is processed on edge server, send half-tuple
                        new_job = Job(TYPE_COM_IOT2SERVER_HALFTUPLES, 0, current_time)
                        self.local_jobs.append(new_job)

                    global_jobs[self.Name].remove(job_to_receive)
                    if DEBUG:
                        print("time :", current_time, self.Name + " receive Type", job_to_receive.job_type,
                              "From " + job_to_receive.creater)

    def ProcLocalJobs(self, current_time):
            total_computation = self.Max_flops / 1000. * cfg_TimeSlot
            for job in self.local_jobs[:]:
                if (not job.done):
                    if (job.need_compute and total_computation > 0):
                        if (total_computation > job.computing_resources):
                            job.done = True
                            total_computation -= job.computing_resources
                            # if the DRL inference job is processed locally, must send tuples
                            if(job.job_type == TYPE_JOB_IOT_DRL_INFERENCE):
                                new_job = Job(TYPE_COM_IOT2SERVER_TUPLES,2*cfg_Input_size,current_time)
                                new_job.set_creater(self.Name)
                                self.local_jobs.append(new_job)
                        else:
                            job.computing_resources -= total_computation
                            total_computation = 0

                if job.job_type == TYPE_JOB_IOT_ACT:
                    # the iot device acts and return the rewards
                    # print self.Name+ " act "
                    self.Wating_for_action = False
                    delay = current_time-self.start_waiting
                    if current_time>=30000:
                        self.superior_device.latencies.append(delay)

                    if(delay>cfg_Max_Delay+3):
                        self.superior_device.num_delay+=1
                    print(delay)

                    self.local_jobs.remove(job)

    def if_local_inference(self,job_type):
        if job_type == "DRL_INFERENCE":
            time  = cfg_Resource_Model_forward/self.Max_flops*1000.
            if(time<= cfg_Max_Delay):
                return True
            else:
                return False

    def Decide_jobs(self, current_time):
        jobs = []
        if ((current_time-self.stamp)>=cfg_Max_Delay and not self.Wating_for_action):
            if self.if_local_inference("DRL_INFERENCE"):
                job = Job(TYPE_JOB_IOT_DRL_INFERENCE, cfg_Input_size, current_time, cfg_Resource_Model_forward)
                job.creater = self.Name
                job.deadline = current_time+cfg_Max_Delay
                jobs.append(job)
            else:
                # send (s) to uper_server
                job = Job(TYPE_COM_IOT2SERVER_MEDIAS, cfg_Input_size, current_time, cfg_Resource_Model_forward)
                job.set_receive_time(current_time + cfg_IOT_SERVER_DELAY + cfg_Input_size*8*\
                                     cfg_rho/self.superior_device.allocated_band_width[self.Name]*1000)
                job.creater = self.Name
                job.deadline = current_time + cfg_Max_Delay
                jobs.append(job)

            self.Wating_for_action = True
            self.start_waiting = current_time
            self.stamp = current_time


        for job in self.local_jobs[:]:
            # send half tuples
            if job.job_type == TYPE_COM_IOT2SERVER_HALFTUPLES:

                new_job = Job(TYPE_COM_IOT2SERVER_HALFTUPLES, cfg_Input_size, current_time)
                new_job.set_receive_time(current_time + cfg_IOT_SERVER_DELAY+ cfg_Input_size*8*\
                                     cfg_rho/self.superior_device.allocated_band_width[self.Name]*1000)
                new_job.set_creater(self.Name)
                new_job.deadline = current_time+10*cfg_Max_Delay
                jobs.append(new_job)
                self.local_jobs.remove(job)
            # send tuples
            if job.job_type == TYPE_COM_IOT2SERVER_TUPLES:
                new_job = Job(TYPE_COM_IOT2SERVER_TUPLES,2*cfg_Input_size,current_time)
                new_job.set_receive_time(current_time + cfg_IOT_SERVER_DELAY+ 2*cfg_Input_size*8*\
                                     cfg_rho/self.superior_device.allocated_band_width[self.Name]*1000)
                new_job.set_creater(self.Name)
                new_job.deadline = current_time + 10 * cfg_Max_Delay
                jobs.append(new_job)
                self.local_jobs.remove(job)

        return jobs
