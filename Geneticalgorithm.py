import copy
import lgsvl
import json
import os
import pprint
import random
import pickle
from Individual import individual
from Restart import generateRestart
class Genetic:
    def __init__(self, scenario,pop_num,sim_length,termination,mutation,crossover):
        self.scenario=scenario
        self.pop_num=pop_num
        self.sim_length=sim_length
        self.termination=termination
        self.mutation=mutation
        self.crossover=crossover
        with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/data/'+self.scenario) as scenario_file:
            scenario_=json.load(scenario_file)
        self.hdmap=scenario_["hdmap"]
        self.npc_num=scenario_["npc_num"]
        self.weather_num=scenario_["weather_num"]
        self.ego_spawn=scenario_["ego_spawn"]
        self.destination=scenario_["destination"]
        self.time_size=scenario_["time_size"]
        self.time_slice=scenario_["time_slice"]
        self.chromsome=scenario_["chromsome"]
        self.touched_ind=[]
        self.best_list=[]#记录每代中最好的一个个体
        self.gen_best=None#记录所有代中最好的个体
        self.lastRestartGen=0
        self.lis_num=2#局部迭代代数
        self.population=[]#种群
        self.lis=False#判断是否进入局部迭代
        self.pop_history=[]#记录之前所有代的个体
    


    def ga_run(self): 
        self.population=self.init_pop(self.chromsome, self.npc_num, self.weather_num,self.ego_spawn, self.sim_length, self.time_slice, self.destination, self.pop_num)
        self.evalute(self.population, self.pop_num)
        self.gen_best, index =self.find_best(self.population,self.pop_num)
        #根据终止条件选择
        if self.termination["type"]=='time':
            pass
        elif self.termination["type"]=='generation':
            self.ga_gen(self.termination["value"], self.pop_num, self.population,self.crossover,self.mutation)

    def ga_gen(self,max_gen, pop_num, population, crossover, mutation):
        for i in range(max_gen):
            #将每一代的种群保存
            self.pop_history.append(population)
            best, index=self.find_best(population, pop_num)
            self.best_list.append(best)
            #如果五代后最优秀个体的适应度函数下降则重启
            gen_noprogress=False
            ave=0
            if i>=self.lastRestartGen+5:
                for j in range(i-5,i):
                    ave+=self.best_list[j].fitness
                ave/=5
                if ave > best.fitness:
                    gen_noprogress=True
            #重启且不在局部搜索中
            if gen_noprogress==True and self.lis==False:
                newPop=generateRestart.generateRestart(self.pop_history,1000,self.chromsome,self.time_slice,self.ego_spawn,self.sim_length,self.destination)
                for i in range(pop_num):
                    self.evalute(newPop[i])
                population=copy.deepcopy(newPop)
                self.lastRestartGen=i
            #当最好适应度大于等于历史最好适应度时，则进入局部迭代
            if best.fitness >= self.gen_best.fitness:
                self.gen_best=copy.deepcopy(best)
                if self.lis==False and i > (self.lastRestartGen+self.lis_num):
                    self.lis=True
                    lis_pop=Genetic(self.scenario, pop_num, self.sim_length, self.destination)
                    lis_pop.init_lispop(best,pop_num)
                    lisbest=lis_pop.ga_gen(self.lis_num, lis_pop.pop_num, lis_pop.population, lis_pop.crossover, lis_pop.mutation)
                    if lisbest.fitness > self.gen_best.fitness:
                        population[index]=copy.deepcopy(lisbest)
                        print(" --- Find better scenario in LIS: LIS->" + str(lisbest.fitness) + ", original->" + str(self.gen_best.fitess))
                    else:
                        print("--- LIS does not find any better scenarios")
                print("\n\n === End of Local Iterative Search === \n\n")
            #挑选下一代种群并交叉和变异

            next_pop=[]
            while(len(next_pop)<pop_num):
                #轮盘赌每次选择两个个体进行交叉和变异    
                condidate_pop=self.roulette(population, 2)
                ind1=condidate_pop.pop()
                ind2=condidate_pop.pop()
                self.crossover_pop(crossover,ind1,ind2)
                self.mutation_pop(mutation,ind1)
                self.mutation_pop(mutation,ind2)
                next_pop.append(ind1)
                next_pop.append(ind2)
            
            population=copy.deepcopy(next_pop)
            self.evalute(population, pop_num)
        return self.gen_best

    #初始化种群
    def init_pop(self, chromsome, npc_num, weather_num,ego_spawn,simlength, time_slice, destination, pop_num): 
        population=[]
        individual_=individual(chromsome, npc_num,weather_num, ego_spawn,simlength, time_slice, destination)
        for i in range(pop_num):
            individual_.rand_init()
            population.append(individual_)
        return population


    #评估种群
    def evalute(self, population, pop_num):
        for i in range(pop_num):
            population[i].get_fitness(self.hdmap,self.time_size)

            

    #寻找最优的个体
    def find_best(self, population, pop_num):

        best=copy.deepcopy(population[0])
        index=0
        for i in range(pop_num):
            if best.fitness<population[i].fitness:
                best=copy.deepcopy(population[i])
                index=i
        return best,index

    #初始化局部迭代种群,所有个体都是最好的
    def init_lispop(self,individual, pop_num):
        population=[]
        for i in range(pop_num):
            population.append(individual)
        return population

    #轮盘赌选择个体
    def roulette(self, population,pop_num):
        sum_f=0
        #确保被除数不为0
        for i in range(pop_num):
            if population[i].fitness == 0:
                population[i].fitness=0.001
        #将场景适应度得分转换为正数，确保适应度得分高的概率大
        min=population[0].fitness
        for i in range(pop_num):
            if population[i].fitness< min:
                min=population[i].fitness
        if min<0:
            for i in range(pop_num):
                population[i].fitness=population[i].fitness+(-1)*min
        
        for i in range(pop_num):
            sum_f+=population[i].fitness

        # probility=[]
        # for i in range(0, pop_num):
        #     probility[i] = population[i].fitness / sum_f
        
        new_pop=[]
        for i in range(pop_num):
            u=random.random()*sum_f
            sum_=0
            for ind in range(pop_num):
                sum_ += population[ind].fitness
                if sum_ > u:
                    new_pop.append(population[ind])
                    break
        return new_pop
        

    #二元锦标赛选择个体
    def tournament(self,population):
        pass
    #交叉
    def crossover_pop(self, crossover, ind1, ind2):

        if crossover > random.random():
                # 每次交换一个场景中的一个npc和一个天气
            vehicle_index = random.randint(0, ind1.npc_num - 1)
            weather_index = random.randint(0, ind1.weather_num-1)
            vehicle_temp = copy.deepcopy(ind1.vehicle_scenario[vehicle_index])
            weather_temp= copy.deepcopy(ind1.vehicle_scenario[weather_index])

            ind1.vehicle_scenario[vehicle_temp] = copy.deepcopy(ind2.vehicle_scenario[vehicle_temp])
            ind1.weather_scenario[weather_temp] = copy.deepcopy(ind2.weather_scenario[weather_temp])
            ind2.vehicle_scenario[vehicle_temp] = vehicle_temp
            ind2.weather_scenario[weather_temp] = weather_temp


    #变异
    def mutation_pop(self, mutation, ind):
        if mutation >= random.random():

            npc_index = random.randint(0, ind.npc_num-1)
            time_index = random.randint(0, ind.time_slice-1)
            weather_index=random.randint(0, ind.weather_num-1)
            actionIndex = random.randint(0, 2)
                
            if actionIndex == 0:
                    # 改变速度
                ind.vehicle_scenario[npc_index][time_index][0] = random.uniform(ind.npc_space["speed_range"][0],ind.npc_space["speed_range"][1])
            elif actionIndex == 1:
                    # 改变动作
                ind.vehicle_scenario[npc_index][time_index][1] = random.randrange(ind.npc_space["action_range"][0],ind.npc_space["action_range"][1])

            ind.weather_scenario[weather_index]=random.uniform(ind.weathers[weather_index]["range"][0],ind.weathers[weather_index]["range"][1])

    #保存数据
    def take_checkpoint(self, obj, ck_name):
        if os.path.exists('GaCheckpoints') == False:
            os.mkdir('GaCheckpoints')
        ck_f = open('GaCheckpoints/' + ck_name, 'wb')
        pickle.dump(obj, ck_f)
        ck_f.truncate() 
        ck_f.close()

if __name__ == "__main__":
    with open('/home/zjx/svlsimulator-linux64-2021.3/PythonAPI-master/AVFUZZER/data/config.json') as conf_file:
        conf_ = json.load(conf_file)

    scenario = conf_["scenario"]
    search_method = conf_["searchMethod"]
    pop_num = conf_["pop_num"]
    sim_length = conf_["simLength"]
    termination = conf_["termination"]
    mutation=search_method["mutation"]
    crossover=search_method["crossover"]
    ga=Genetic(scenario,pop_num,sim_length,termination,mutation,crossover)
    pop_history=[]
    for i in range(2):
        pop=ga.init_pop(ga.chromsome,ga.npc_num, ga.weather_num, ga.time_slice, ga.destination, 2)
        pop_history.append(pop)
    new=generateRestart(pop_history, 3, ga.chromsome, ga.time_slice, ga.destination)
    print(new)