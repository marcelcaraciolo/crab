#-*- coding:utf-8 -*-


#========================================================================
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#========================================================================



"""
:mod:`utils` -- the utils recommendation modules  
================================================================

This module contains functions and classes to help the recommendation process.

"""

class DiffStorage(object):
	'''
	An implementation of DiffStorage that merely stores item-item diffs in memory. 
	Caution: It may consume a great deal of memory due to larger datasets.
	'''
	def __init__(self,model,stdDevWeighted,toPrune=True):
		''' DiffStorage Class Constructor
		     `model` is the data source model
			 `stdDevWeighted` is a flag that if it is True, use standard deviation weighting of diffs
			 `toPrune` is a flag that if it is True, it will prune the irrelevant diffs, represented by one data point.
		'''
		self.model = model
		self.stdDevWeighted = stdDevWeighted
		self.toPrune = toPrune
		self._diffStorage = {}
		self._diffStorageStdDev = {}
		self._freqs = {}
		self._recommendableItems = []
		self._buildAverageDiffs()
	
	def _buildAverageDiffs(self):
		self._diffStorage = {}
		for userID in self.model.UserIDs():
			self.processOneUser(userID)
		if self.toPrune:
			self.pruneDiffs()
		self.updateAllRecommendableItems()
		if self.stdDevWeighted:
			self.evaluateStandardDeviation()
		self.evaluateAverage()
		
	def recommendableItems(self):
		return self._recommendableItems
	
	def updateAllRecommendableItems(self):
		self._recommendableItems = []
		for itemID in self._diffStorage:
			self._recommendableItems.append(itemID)
		self._recommendableItems.sort()
	
	def evaluateAverage(self):
		for itemIDA,ratings in self._diffStorage.iteritems():
			for itemIDB in ratings:
				ratings[itemIDB]/= self._freqs[itemIDA][itemIDB]
						
	def diffsAverage(self,userID,itemID,prefs):
		return [ self.diff(itemID,itemID2)  if itemID2 in self._freqs[itemID] else - self.diff(itemID,itemID2) if self.diff(itemID,itemID2) is not None else None  for  itemID2,rating in prefs]
	
	def diff(self,itemIDA,itemIDB):
		if itemIDA in self._diffStorage:
			if itemIDB in self._diffStorage[itemIDA]:
				return self._diffStorage[itemIDA][itemIDB]
			elif itemIDB in self._diffStorage:
				if itemIDA in self._diffStorage[itemIDB]:
					return self._diffStorage[itemIDB][itemIDA]
				else:
					return None
			else:
				return None
	
	def evaluateStandardDeviation(self):
		for itemIDA,ratings in self._diffStorage.iteritems():
			for itemIDB in ratings:
				pass

				
	
	def standardDeviation(self,itemID,itemID2):
		return 0.0
							
	def count(self,itemID,itemID2):
		try:
			return self._freqs[itemID][itemID2]
		except KeyError:
			return self._freqs[itemID2][itemID]			
	
	def pruneDiffs(self):
		'''
		Go back and prune irrelevant diffs. Irrelevant means here, represented by one data point, so possibly unreliable
		'''
		for item1 in self._freqs.keys():
			for item2 in self._freqs[item1].keys():
				if self._freqs[item1][item2] <=1:
					del self._freqs[item1][item2]
					del self._diffStorage[item1][item2]
					if len(self._diffStorage[item1])==0:
						break
						
											
	def processOneUser(self,userID):
		userPreferences = self.model.PreferencesFromUser(userID)
		for indexA,preferenceA in enumerate(userPreferences):
			itemID1,rating1 = preferenceA
			self._diffStorage.setdefault(itemID1,{})
			self._freqs.setdefault(itemID1,{})
			for indexB,preferenceB in enumerate(userPreferences[indexA+1:]):
				itemID2,rating2 = preferenceB
				self._diffStorage[itemID1].setdefault(itemID2,0.0)
				self._freqs[itemID1].setdefault(itemID2,0)
				self._diffStorage[itemID1][itemID2]+= (rating1 - rating2)
				self._freqs[itemID1][itemID2]+=1