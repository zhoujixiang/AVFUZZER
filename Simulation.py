
import datetime
import json
from environs import Env
import lgsvl
import os
import time
import math
from lgsvl.agent import EgoVehicle
from util import print_debug
from lgsvl.dreamview.dreamview import Connection
from lgsvl.evaluator.utils import separation

class simulation:
    def __init__(self,time_size, simLength, destination, ego_spawn, hdmap, vehicle_scenario, weather_scenario, npc_spawn, npc_action):
        self.time_size=time_size
        self.simLength=simLength
        self.destination=destination
        self.ego_spawn=ego_spawn
        self.hdmap=hdmap
        self.vehicle_scenario=vehicle_scenario
        self.weather_scenario=weather_scenario
        self.npc_spawn=npc_spawn
        self.npc_action=npc_action
        self.path = "/home/zjx/.config/unity3d/LGElectronics/SVLSimulator-2021.3/Videos"
        self.hit=False
        self.ego=None
        self.sim=None
        self.maxint=300
        self.npclist=[]
        self.hit_list=[]
        self.initSimulator()
        self.loadmap()
        self.init_npc()
        self.init_ego()
        self.connectEvToApollo()
        self.connection()
        self.init_weather()


    def initSimulator(self):
        env = Env()
        sim = lgsvl.Simulator(env.str("LGSVL__SIMULATOR_HOST", lgsvl.wise.SimulatorSettings.simulator_host), env.int("LGSVL__SIMULATOR_PORT", lgsvl.wise.SimulatorSettings.simulator_port))
        self.sim = sim

    def loadmap(self):
        sim=self.sim
        # if sim.curent_scene == self.hdmapmap:
        #     sim.reset()
        # else:
        #     sim.load(self.hdmap)
        if sim.current_scene == lgsvl.wise.DefaultAssets.map_sanfrancisco:
            sim.reset()
        else:
            sim.load(lgsvl.wise.DefaultAssets.map_sanfrancisco)
    #在指定位置生成ego
    def init_ego(self):
        sim=self.sim
        egostate=lgsvl.AgentState()
        ego_position=lgsvl.Vector(self.ego_spawn["x"],self.ego_spawn["y"],self.ego_spawn["z"])
        egostate.transform=sim.map_point_on_lane(ego_position)
        ego = sim.add_agent(lgsvl.wise.DefaultAssets.ego_lincoln2017mkz_apollo5, lgsvl.AgentType.EGO, egostate)
        sensors=ego.get_sensors()
        for s in sensors:
            if s.name in ["IMU","Radar","Lidar","Main Camera","Telephoto Camera"]:
                s.enabled=True
        self.ego=ego

    #连接apollo
    def connectEvToApollo(self):
        ego = self.ego
        print("Connecting to bridge")
        ego.connect_bridge(os.environ.get("BRIDGE_HOST", "127.0.0.1"), 9090)
        while not ego.bridge_connected:
            time.sleep(1)
        print("Bridge connected")

    #连接dreamview并设置目的地和传感器参数
    def connection(self):
        print(1)
        connect=Connection(self.sim,self.ego)
        connect.set_setup_mode("Mkz Lgsvl")
        connect.set_vehicle("Lincoln2017MKZ_LGSVL")
        connect.set_hd_map(self.hdmap)
        modules = ['Localization','Perception','Transform','Routing','Prediction','Planning','Storytelling','Control']
        connect.setup_apollo(self.destination["x"], self.destination["z"], modules)
        print(2)

    #在ego的附近生成npc，位置随机
    def init_npc(self):
        sim=self.sim
        npcstate=lgsvl.AgentState()
        for i in range(len(self.vehicle_scenario)):
            npc_position=lgsvl.Vector(self.ego_spawn["x"]+self.npc_spawn[i][1],self.ego_spawn["y"],self.ego_spawn["z"]+self.npc_spawn[i][0])
            npcstate.transform=sim.map_point_on_lane(npc_position)
            npc=sim.add_agent("Sedan", lgsvl.AgentType.NPC, npcstate)
            self.npclist.append(npc)

    #设置npc速度
    def setnpcspeed(self, npc, speed):
        npc.follow_closest_lane(True,speed)

    #设置npc行为
    def setnpcaction(self, npc, action):
        if action=="leftChange":
            npc.change_lane(True)
        elif action=="rightChange":
            npc.change_lane(False)
        elif action=="multiple_lane_right":
            npc.change_lane(False)
            npc.change_lane(False)
        elif action=="multiple_lane_left":
            npc.change_lane(True)
            npc.change_lane(True)
        elif action=="e_stop":
            control = lgsvl.NPCControl()
            control.e_stop = True
            npc.apply_control(control)
        else:
            pass

    #设置天气和太阳
    def init_weather(self):
        self.sim.weather = lgsvl.WeatherState(rain=self.weather_scenario[0], fog=self.weather_scenario[1], wetness=self.weather_scenario[2],\
             cloudiness=self.weather_scenario[3], damage=self.weather_scenario[4])
        self.sim.set_time_of_day(self.weather_scenario[5])
        
    #刹车距离
    def brake_dist(speed):
        d_brake = 0.0467 * math.pow(speed, 2.0) + 0.4116 * speed - 1.9913 + 0.5
        if d_brake < 0:
            d_brake = 0
        return d_brake
    #删除记录
    def move_record(self):
        datanames = os.listdir(self.path)
        listnew=[]
        for i in datanames:
            listnew.append(i)
        pa=list(set(listnew)-set(self.hit_list))[0]
        os.remove(self.path+'/'+pa)

    def findFitness(self, dList, ishit):
        minD = self.maxint
        for npc in dList: # ith NPC
            for d in npc:
                if ishit == True:
                    break
                if d < minD:
                    minD = d
        fitness=minD
        return fitness

    def runsim(self):
        time_slice=len(self.vehicle_scenario[0])
        npc_num=len(self.vehicle_scenario)
        dList=[[self.maxint for i in range(time_slice)] for j in range(npc_num)]
        self.ishit=False

        def on_collision(agent1 ,agent2,contact):
            self.ishit=True

        self.ego.on_collision(on_collision)  

        for t in range(time_slice):
            i=0
            for npc in self.npclist:
                self.setnpcspeed(npc,self.vehicle_scenario[i][t][0])
                self.setnpcaction(npc,self.npc_action[self.vehicle_scenario[i][t][1]])
                i+=1

            if self.ishit==True:
                break
            
            minDeltaD = self.maxint
            npcDeltaAtTList = [0 for i in range(npc_num)]
            minD = self.maxint
            npcDAtTList = [0 for i in range(npc_num)]
            for j in range(0, int((self.time_size/time_slice) * (1/self.simLength))):
                k = 0 # k th npc
                for npc in self.npclist:
                    # Update d
                    curD = separation(self.ego.state.position, npc.state.position)
                    if minD > curD:
                        minD = curD
                    npcDAtTList[k] = minD
                    k += 1
                    self.sim.run(self.simLength)
            k = 0 # kth npc
            for npc in self.npclist:
                dList[k][t] = npcDAtTList[k]
                k += 1
        fitness_score=self.findFitness(dList, self.ishit)
        # self.sim.reset()
        self.sim.close()
        # if self.ishit==False:
        #     self.move_record()
        return fitness_score
