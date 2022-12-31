
import json
import time
import sys
from Geneticalgorithm import Genetic



with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/data/config.json') as conf_file:
    conf_ = json.load(conf_file)

scenario = conf_["scenario"]
search_method = conf_["searchMethod"]
pop_num = conf_["pop_num"]
sim_length = conf_["simLength"]
termination = conf_["termination"]

if search_method["methed"] == 'ga':
    mutation=search_method["mutation"]
    crossover=search_method["crossover"]
    GA=Genetic(scenario,pop_num,sim_length,termination,mutation,crossover)
    GA.ga_run()
    
