#! /usr/bin/python3

import math
import collections
import pickle
from Individual import individual
from os import listdir
import random
import json


def getAllCheckpoints(ck_path):
	onlyfiles = [f for f in listdir(ck_path)]
	prevPopPool = []

	for i in range(len(onlyfiles)):
		with open(ck_path+'/'+onlyfiles[i], "rb") as f:
			if "generation" not in onlyfiles[i]:
				continue
			try:
				prevPop = pickle.load(f)
				prevPopPool.append(prevPop)
			except Exception:
				pass

	return prevPopPool

def generateRestart(pop_history, scenarioNum, chromosome,time_slice,ego_spawn,simlength, destination):
				 
	newPopCandiate = []
	newScenarioList = []
	popSize = len(pop_history[0])
	npcSize = len(pop_history[0][0].vehicle_scenario)
	weatherSize=len(pop_history[0][0].weather_scenario)
	scenarioSize = len(pop_history[0])
	popPoolSize = len(pop_history)
	dictScenario = {}

	for i in range(scenarioNum):
		individual_ = individual(chromosome, npcSize,weatherSize, ego_spawn,simlength,time_slice, destination)
		individual_.rand_init()
		newPopCandiate.append(individual_)

	# Go through every scenario

	for i in range(scenarioNum):
		similarity = 0;
		for j in range(popPoolSize):
			simiPop = 0;
			for k in range(scenarioSize):
				vehicle_scenario1 = newPopCandiate[i].vehicle_scenario
				vehicle_scenario2 = pop_history[j][k].vehicle_scenario
				weather_scenario1 = newPopCandiate[i].weather_scenario
				weather_scenario2 = pop_history[j][k].weather_scenario
				simi = getSimilaritybetweenScenarios(vehicle_scenario1, vehicle_scenario2, weather_scenario1, weather_scenario2 )
				simiPop += simi

			simiPop /= scenarioSize
			similarity += simiPop
		similarity /= popPoolSize
		dictScenario[i] = similarity

	sorted_x = sorted(dictScenario.items(), key=lambda kv: kv[1], reverse=True)
	sorted_dict = collections.OrderedDict(sorted_x)

	index = sorted_dict.keys()

	j = 0

	for i in index:
		if j == popSize:
			break
		newScenarioList.append(newPopCandiate[i])
		j += 1

	return newScenarioList

def getSimilaritybetweenScenarios(vehicle_scenario1, vehicle_scenario2, weather_scenario1, weather_scenario2):

	npcSize = len(vehicle_scenario1)
	weatherSize=len(weather_scenario1)

	scenarioNpc = 0.0
	scenraioWeather=0.0


	for i in range(npcSize):
		npc1 = vehicle_scenario1[i]	
		npc2 = vehicle_scenario2[i]
		npcSimi = getSimilarityBetweenNpcs(npc1, npc2)
		scenarioNpc += npcSimi
	
	scenraioWeather=getSimilarityBetweenWeathers(weather_scenario1,weather_scenario2)
	
		
	return (scenarioNpc/npcSize) + (scenraioWeather/weatherSize)

def getSimilarityBetweenNpcs(npc1, npc2):
	sumnpc = 0.0
	for i in  range(len(npc1)):
		sumnpc += math.pow(npc1[i][0]-npc2[i][0],2)
		sumnpc += math.pow(npc1[i][0]-npc2[i][0],2)
	return math.sqrt(sumnpc) 

def getSimilarityBetweenWeathers(weather1, weather2):
	sumweather=0.0
	for i in range(len(weather1)):
		sumweather += math.pow(weather1[i]-weather2[i],2)
	return math.sqrt(sumweather)

if __name__ == '__main__':
	pass
