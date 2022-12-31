import json
import random
import numpy as np
from Simulation import simulation
class individual:
    def __init__(self, chromsome, npc_num,weather_num, ego_spawn,simlength,time_slice,destination):
        self.weathers=chromsome["weather"]
        npc=chromsome["npc"]
        spawn_dis=npc["spawn_dis"]
        self.lateral=spawn_dis["lateral"]
        self.longitudinal=spawn_dis["longitudinal"]
        self.npc_space=npc["npc_space"]
        self.npc_num=npc_num
        self.weather_num=weather_num
        self.ego_spawn=ego_spawn
        self.sim_length=simlength
        self.time_slice=time_slice
        self.npc_action=npc["action"]
        self.destination=destination
        self.fitness=0
        self.vehicle_scenario=[[[] for i in range(time_slice)] for j in range(npc_num)]
        self.weather_scenario=[0 for i in range(len(self.weathers))]
        self.npc_spawn=[[]for i in range(npc_num)]


    def rand_init(self):
        #初始化车辆的参数
        for i in range(self.npc_num):
            for j in range(self.time_slice):
                v=random.uniform(self.npc_space["speed_range"][0],self.npc_space["speed_range"][1])
                a=random.randint(self.npc_space["action_range"][0],self.npc_space["action_range"][1])
                self.vehicle_scenario[i][j].append(v)
                self.vehicle_scenario[i][j].append(a)
        #初始化天气参数
        weather_num=0
        for weather in self.weathers:
            self.weather_scenario[weather_num]=random.uniform(weather["range"][0],weather["range"][1])
            weather_num=weather_num+1
        #初始化npc位置
        for i in range(self.npc_num):
            self.npc_spawn[i].append(random.uniform(self.lateral[0],self.lateral[1]))
            self.npc_spawn[i].append(random.uniform(self.longitudinal[0],self.longitudinal[1]))

        
    def get_fitness(self, hdmap, time_size):

        simulation_=simulation(time_size,self.sim_length,self.destination,self.ego_spawn,hdmap,self.vehicle_scenario,self.weather_scenario,self.npc_spawn, self.npc_action)
        self.fitness=simulation_.runsim()


if __name__ == "__main__":
    with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/data/straight_road.json') as scenario_file:
            scenario_=json.load(scenario_file)
            hdmap=scenario_["hdmap"]
            npc_num=scenario_["npc_num"]
            weather_num=scenario_["weather_num"]
            ego_spawn=scenario_["ego_spawn"]
            simlength=0.5
            destination=scenario_["destination"]
            time_size=scenario_["time_size"]
            time_slice=scenario_["time_slice"]
            chromsome=scenario_["chromsome"]

    individual_=individual(chromsome,npc_num,weather_num,ego_spawn,simlength,time_slice,destination)
    for i in range(10):
        print(i)
        individual_.rand_init()
        individual_.get_fitness(hdmap,time_size)