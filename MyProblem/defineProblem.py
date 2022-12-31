
import json
import numpy as np
import time
import os
from pymoo.core.problem import Problem
#from Coverage.err_length import err_length
#from Coverage.severity import severity



with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/data/straight_road.json') as scenario_file:
    scenario_=json.load(scenario_file)

    hdmap=scenario_["hdmap"]
    npc_num=scenario_["npc_num"]
    destination=scenario_["destination"]
    time_size=scenario_["time_size"]
    time_slice=scenario_["time_slice"]
    chromsome=scenario_["chromsome"]
    weathers=chromsome["weather"]
    print(weathers)

#     def _evaluate(self, X, out, *args, **kwargs):
#         print(X)
#         X_list = X.tolist()
#         X_rec = X.flatten().tolist()

#         safe, hit = self.sim(X_list)
#         print(safe)

#         self.x_history.append(X_rec)
#         self.safe_history.append(safe)
#         self.hit_history.append(hit)
#         self.time_history.append(time.time() - self.start_time)

#         safe_np = np.array(safe)

#         out["F"] = safe_np


#     def sim(self, X):
#         # parse json scenario
#         with open(self.home + '/scenario/' + self.scenario + '.json') as scenf:
#             scen = json.load(scenf)
#         hdmap = scen["hdmap"]
#         daytime = scen["daytime"]
#         destination = scen["destination"]
#         timeout = scen["timeout"]
#         weather = scen["weather"]
#         npc = scen["npc"]
#         pedestrian = scen["pedestrian"]

#         cov = []
#         safe = []
#         hit = []
#         print(X)
#         for x in X:
#             print(x)
#             #assign X and call simulation
#             for i in range(len(self.var)):
#                 vl = self.var[i].split('_')
#                 vm = vl[0]
#                 for vl_ in vl[1:]:
#                     if vl_.isnumeric():
#                         vm = vm + '[' + vl_ + ']'
#                     else:
#                         vm = vm + '[\"' + vl_ + '\"]'
#                 exec(vm + "= " + str(x[i]))
            
# #            if self.cov_metric == "code":
# #                os.system("find /apollo -name *.gcda -type f -delete")

#             log_file ='/log/' + str(time.time())
#             safe_, hit_ =  simulation(hdmap, destination, timeout, daytime, weather, npc, pedestrian, self.sim_length, log_file)



# #           elif cov_metric == "neuron":
# #               cov_ = neuron_coverage()

#             safe.append(safe_)
#             hit.append(hit_)

#         return safe, hit
