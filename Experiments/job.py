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
        self.creater = None

    def set_receive_time(self,time):
        self.receive_time = time
    def set_creater(self,Name):
        self.creater = Name