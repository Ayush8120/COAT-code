import os

SAMPLES_PER_OBJECT = 5
DATA_GEN_SEED = 0
QUEST_PER_TASK_0 = 5

NUM_GPUS = 2
MAX_GPU_MEM = '11Gib'
LOAD_8BIT = True
CPU_OFFLOAD = os.getenv("CPU_OFFLOAD")

RUNS_PER_TEMP = 5
RETRY_COUNT = 10