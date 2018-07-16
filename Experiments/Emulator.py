import graphviz
from config import *
from graphviz import Digraph
import queue

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
    The devices' running are based a unified cycle signal
    '''
    def __init__(self,time_slot):
        self.time = 0
        self.time_slot = time_slot #ms
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

        device.Query(self.time,self.global_jobs)
        device.Receive(self.time,self.global_jobs)

        while (len(device.inferior_devices)!=0):
            for sub_device in device.inferior_devices:
                self.recursive_run(sub_device)

    def run(self,max_time):
        while (self.time<max_time):
            self.recursive_run(self.Main_server)
            self.tick()


class Job:
    def __init__(self,job_type,content_size,created_time,computing_resources = 0):
        '''
        Job types:
        0x0:    transfer images or some other medias collected by sensors
        0x1:    Model parameters
        0x2:    Gradents computed by back propgation
        '''
        self.job_type = job_type
        self.content_size = content_size
        '''
        The computing resources needed to compute this job, *Gflops
        '''
        self.computing_resources = computing_resources
        self.done = False

        #the time stamp that this job is created
        self.created_time = created_time
        self.receive_time = 0

        def set_receive_time(time):
            self.receive_time = time




class Server(object):
    def __init__(self,Name,Max_flops,Port_ratio,RAM):
        #the max computing ability
        self.Name = Name

        # Server type:
        # 0x0 : Main Server
        # 0x1 : Middle Server

        self.Type = None
        #
        # 0x0 : Await, ready for task
        # 0x1 :
        #
        self.State = 0x0


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
        # TODO: The effect of RAM parameter is waiting for explore
        # '''
        self.RAM = RAM


        # inferior devices are devices connected to the server and are inferior to this server
        # in the topology

        self.inferior_devices = []


        # in this system each device only has one superior device

        self.superior_device  = None


        # The jobs queue only contains the jobs waiting to be computed
        # The communication tasks are queued in trans_in queue and trans_out queue

        self.jobs_queue      = queue.Queue()
        self.trans_in_queue  = queue.Queue()
        self.trans_out_queue = queue.Queue()

    def Connect(self,Device):
        '''
        Form the topology
        '''
        Device.superior_device = self
        self.inferior_devices.append(Device)

    def Query(self,current_time,global_jobs):
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
        #job = Job(job_type,content_size)
        while(True):
            self.superior_device.Receive(job)

    def Receive(self,job):
        self.job_queue.put(job)
>>>>>>> 01856c75b062b0b813041a1c18e74d8575ae7a96
    def Check_queue(self):
        #check the job queue, if not empty, fech jobs to process
        if(not self.jobs_queue.empty()):
            if()

class Main_Server(Server):
    def __init__(self,Name,Max_flops,Port_ratio,RAM):
        super(Main_Server, self).__init__(Name,Max_flops,Port_ratio)
        self.Type = 0x0

class Middle_Server(Server):
    def __init__(self,Name,Max_flops,Port_ratio,RAM):
        super(Middle_Server, self).__init__(Name,Max_flops,Port_ratio)
        self.Type = 0x1

class IoT:
    def __init__(self,Name,Max_flops,Port_ratio,Battery,RAM):
        self.Name = Name
        self.Max_flops = Max_flops
        self.Port_ratio = Port_ratio
        self.Battery = Battery
        self.RAM = RAM
        self.superior_device = None
        self.inferior_devices = []

    def Querry(self,current_time,global_jobs):
        job = Job(0x0,cfg_Input_size,cfg_Model_flops)
        self.superior_device.Receive(job)

    def Receive(self,current_time,global_jobs):
        pass





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
    profiler_edge.Draw_hierarchy(Main_Server)
    profiler_edge.view()


        