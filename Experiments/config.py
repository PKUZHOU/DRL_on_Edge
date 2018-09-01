cfg_Main_server_Max_flops       = 100000  #Gops
cfg_Main_server_port_ratio      = 10000   #Mbps
cfg_Middle_server_Max_flops     = 10000   #Gops
cfg_Middle_server_port_ratio    = 1000    #Mbps
cfg_Middle_server_num           = 1
cfg_IOTdeviceNums_per_Servier   = 40
cfg_IOT_Max_flops               = 300     #Gops
cfg_IOT_Min_flops               = 1       #Gops
cfg_IOT_Port_ratio              = 10      #Mbps
cfg_SyncModel_flops             = 2

cfg_Input_size                  = 640*480*3/1000000.   #MB
cfg_Resource_Model_forward      = 10.     #Gops
cfg_Resource_Model_backward     = 20.     #Gops
cfg_rho                         = 0.01
cfg_IOT_SERVER_DELAY            = 2       #ms
cfg_TimeSlot                    = 1       #ms
cfg_MaxTime                     = 40000

cfg_Model_Parameter_size        = 10      #MB
cfg_Model_Gradients_size        = 10      #MB

cfg_Max_Delay                   = 50      #ms

cfg_Tuple_priority              = 3
cfg_Inference_priority          = 1

cfg_Middle_server_max_queue_len = 5000
DEBUG = 0