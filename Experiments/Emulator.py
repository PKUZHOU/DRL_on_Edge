import graphviz
from config import *
from devices import *
from graphviz import Digraph
import random
#from GUI import *
class Profiler:
    def __init__(self,name):
        self.dot = Digraph(comment=name)
        self.graph = []
    def Draw_hierarchy(self,current_device):
        '''
            Draw the hierarchy of the system, at first call input the root server instance
        '''
        for inferior_device in current_device.inferior_devices:
            self.dot.node(inferior_device.Name,inferior_device.Name)
            self.dot.edge(current_device.Name,inferior_device.Name)
            self.Draw_hierarchy(inferior_device)

    def view(self):
        #show the hierarchy by picture
        self.dot.render('./table.gv',view=True)

class Manager:
    '''
    The Manager of this emulator, it controls all the behavior of emulated environment.
    The devices' running are based on a unified cycle signal
    '''
    def __init__(self,time_slot):
        self.time = 0
        self.time_slot   = time_slot #ms
        self.Main_server = None
        self.global_jobs = {}
        self.old_global_jobs = {}

    def tick(self):
        '''
        the global time steps a time slot
        '''
        self.time+=self.time_slot

    def set_Main_server(self,Main_server):
        '''
        after building the hierarchy, pass the Main_server (the root of the graph) to the manager to run emulating
        '''
        self.Main_server = Main_server

    def recursive_run(self,device):
        '''
        run every devices in one time step
        '''
        # device.Query(self.time,self.global_jobs)
        # device.Receive(self.time,self.global_jobs)
        device.Process(self.time,self.global_jobs)
        if (len(device.inferior_devices)!=0):
            for sub_device in device.inferior_devices:
                self.recursive_run(sub_device)

    def run(self,max_time):
        #run the whole system until reaching the max time
        while (self.time<max_time):
            self.recursive_run(self.Main_server)
            #print (self.time)
            self.tick()
            #self.LOG()
        delays = []
        drl_bkwds =0
        for mid in self.Main_server.inferior_devices:
            delays+=mid.latencies
            drl_bkwds+=mid.num_DRL_backwards
        print "back ward persecond: "+ str(drl_bkwds*1000/10000)
        print "average_delay:"+ str(sum(delays)/len(delays))
    def LOG(self):
        for device in self.global_jobs.keys():
            if device not in self.old_global_jobs.keys():
                self.old_global_jobs[device] = []
            #print('time :',self.time)
            for job in self.global_jobs[device]:
                if job not in self.old_global_jobs[device]:
                    print( 'Type :',job.job_type,str(job.creater)+'---->'+device, "creat time:" ,job.created_time)

        #self.old_global_jobs = self.global_jobs
def create_edge_hierarchy():
    Main_server = Main_Server('Main_server',cfg_Main_server_Max_flops,cfg_Main_server_port_ratio)
    for i in range(cfg_Middle_server_num):
        middle_server = Middle_Server('Middle_server_'+str(i),cfg_Middle_server_Max_flops,cfg_Middle_server_port_ratio)
        for j in range(cfg_IOTdeviceNums_per_Servier):
            random.seed(1)
            IoT_flops = random.randint(cfg_IOT_Min_flops,cfg_IOT_Max_flops)
            middle_server.Connect(IoT("Iot_"+str(i*cfg_IOTdeviceNums_per_Servier+j),\
                                      IoT_flops,cfg_IOT_Port_ratio))
        middle_server.allocate_band_width()
        Main_server.Connect(middle_server)
    return Main_server

def creat_normal_hierarchy():
    Main_server = Main_Server('Main_server', cfg_Main_server_Max_flops, cfg_Main_server_port_ratio)
    for i in range(cfg_IOTdeviceNums_per_Servier):
        Main_server.Connect(
            IoT("Iot_" + str(i), cfg_IOT_Max_flops, cfg_IOT_Port_ratio))
    return Main_server

if __name__ == '__main__':
    Main_Server = create_edge_hierarchy()
    manager = Manager(cfg_TimeSlot)
    manager.set_Main_server(Main_Server)
    manager.run(cfg_MaxTime)


        