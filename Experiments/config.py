cfg_Main_server_Max_flops     = 100000 #Gops
cfg_Main_server_port_ratio    = 10000  #Mbps
cfg_Middle_server_Max_flops   = 10000
cfg_Middle_server_port_ratio  = 1000
cfg_Middle_server_num         = 4
cfg_IOTdeviceNums_per_Servier = 5
cfg_IOT_Max_flops             = 20
cfg_IOT_Port_ratio            = 100
cfg_IOT_Barrery               = 3000  #Mah


cfg_Input_size                = 640*360*3 #Bytes
cfg_Resource_Model_forward    = 10000 #flops
cfg_Resource_Model_backward   = 20000 #flops

cfg_IOT_SERVER_DELAY          = 10 #ms
cfg_TimeSlot                  = 10 #ms
cfg_MaxTime                   = 10000000

cfg_Model_Parameter_size      = 10 #MB
cfg_Model_Gradients_size      = 10 #MB

cfg_SyncModel_flops           = 100000
cfg_Main_server_update_interval = 10000*cfg_TimeSlot

DEBUG = 1