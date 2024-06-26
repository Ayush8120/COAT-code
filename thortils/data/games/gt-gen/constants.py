SAMPLES_PER_OBJECT = 5
DATA_GEN_SEED = 0
QUEST_PER_TASK_0 = 5

NUM_GPUS = 4
MAX_GPU_MEM = '11Gib'
LOAD_8BIT = False
CPU_OFFLOAD = False 

RUNS_PER_TEMP = 1
TASK_0_NUM_QUESTIONS = 10000
TASK_1_NUM_QUESTIONS = 5000
TASK_2_NUM_QUESTIONS = 5000
AGENT_HEIGHT = 150 #+ " cm"
WALL_HEIGHT = 300 #+ " cm"
SHELF_HEIGHT = 250 #+ " cm"
MAX_AGENT_WEIGHT_LIFT = 10 # + " Kg"

#Temp
Natural_Heating_Cooling_Penalty =  100 #+ " seconds"

#depends on tool use : fridge
Cooling_Penalty_High_Room = 30  #+ " seconds" # using fridge
Cooling_Penalty_Room_Low = 30 #+ " seconds"
Cooling_Penalty_High_Low = 60 #+ " seconds"

#depends on heating tool and object
Heating_Penalty_Low_High = 60 #+ " seconds" # using heating device
Heating_Penalty_Low_Room = 30 #+ " seconds"
Heating_Penalty_Room_High = 30 #+ " seconds"

#
Heating_Stove = 100 #+ " seconds"
Heating_MicroWave =  40 #+ " seconds"
Heating_Candle = 5 #+ " seconds"
Heating_Coffee_Machine = 10 #+ " seconds"

#Condition 
Cleaning_Time = 50 #+ " seconds"
Cleaning_Effort = 30 

#
Tool_Use_Penalty = 10 #+ " units"
Machine_Use_Penalty = 20 #+ " units"


#Safety Penalty
Safety_Penalty = 100
Bad_Choice = 500 

#Already_in_use
# Waiting_Time = 100 + " seconds"
# Stuff_Movement_Penalty = 15 + " units"
Rev_to_free_time = 80 #+ " seconds"