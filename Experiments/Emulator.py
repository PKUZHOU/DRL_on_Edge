import graphviz
from config import *
from devices import *
from graphviz import Digraph

class Profiler:
    def __init__(self,name):
        self.dot = Digraph(comment=name)
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
            self.LOG()


    def LOG(self):
        for device in self.global_jobs.keys():
            #print('time :',self.time)
            for job in self.global_jobs[device]:
                print 'Type :',job.job_type,str(job.creater)+'---->'+device



def create_edge_hierarchy():
    Main_server = Main_Server('Main_server',cfg_Main_server_Max_flops,cfg_Main_server_port_ratio)
    for i in range(cfg_Middle_server_num):
        middle_server = Middle_Server('Middle_server_'+str(i),cfg_Middle_server_Max_flops,cfg_Middle_server_port_ratio)
        for j in range(cfg_IOTdeviceNums_per_Servier):
            middle_server.Connect(IoT("Iot_"+str(i*cfg_IOTdeviceNums_per_Servier+j),cfg_IOT_Max_flops,cfg_IOT_Port_ratio,cfg_IOT_Barrery))
        Main_server.Connect(middle_server)
    return Main_server

def creat_normal_hierarchy():
    Main_server = Main_Server('Main_server', cfg_Main_server_Max_flops, cfg_Main_server_port_ratio)
    for i in range(cfg_IOTdeviceNums_per_Servier):
        Main_server.Connect(
            IoT("Iot_" + str(i), cfg_IOT_Max_flops, cfg_IOT_Port_ratio,
                cfg_IOT_Barrery))
    return Main_server

if __name__ == '__main__':
    profiler_edge   = Profiler("Edge compution hierarchy")
    profiler_normal = Profiler("Normal compution hierarchy")
    # Main_Server = creat_normal_hierarchy()
    # profiler_normal.Draw_hierarchy(Main_Server)
    # profiler_normal.view()
    Main_Server = create_edge_hierarchy()
    # profiler_edge.Draw_hierarchy(Main_Server)
    # profiler_edge.view()
    manager = Manager(cfg_TimeSlot)
    manager.set_Main_server(Main_Server)
    manager.run(cfg_MaxTime)


        