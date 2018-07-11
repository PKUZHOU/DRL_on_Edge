import graphviz
from config import *
from graphviz import Digraph
import queue


class Job:
    def __init__(self,job_type,content_size):
        self.job_type = job_type
        self.content_size = content_size
        self.done = False
class Profiler:
    def __init__(self,name):
        self.dot = Digraph(comment=name)

    def Draw_hierarchy(self,current_device):
        #Draw the hierarchy of the system, at first call input the root server instance
        for inferior_device in current_device.inferior_devices:
            self.dot.node(inferior_device.Name,inferior_device.Name)
            self.dot.edge(current_device.Name,inferior_device.Name)
            self.Draw_hierarchy(inferior_device)
    def view(self):
        #show the hierarchy by picture
        self.dot.render('./table.gv',view=True)

class Server(object):
    def __init__(self,Name,Max_flops,Port_ratio):
        #the max computing ability
        self.Name = Name
        self.Max_flops = Max_flops
        #the max Port ratio, Mbps
        self.Port_ratio = Port_ratio
        self.inferior_devices = []
        #in this system each device only has one superior device
        self.superior_device  = None
        self.num_jobs = 0  # the num of jobs wating to be done
        self.job_queue = queue.Queue()

    def Connect(self,Device):
        Device.superior_device = self
        self.inferior_devices.append(Device)

    def Querry(self,job_type,content_size):
        job = Job(job_type,content_size)
        while(True):
            self.superior_device.Receive(job)

    def Receive(self,job):

class Main_Server(Server):
    def __init__(self,Name,Max_flops,Port_ratio):
        super(Main_Server, self).__init__(Name,Max_flops,Port_ratio)

class Middle_Server(Server):
    def __init__(self,Name,Max_flops,Port_ratio):
        super(Middle_Server, self).__init__(Name,Max_flops,Port_ratio)

class IoT:
    def __init__(self,Name,Max_flops,Port_ratio,Battery):
        self.Name = Name
        self.Max_flops = Max_flops
        self.Port_ratio = Port_ratio
        self.Battery = Battery
        self.superior_device = None
        self.inferior_devices = []

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


        