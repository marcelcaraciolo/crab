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

#REVISION HISTORY

#0.1 2010-11-04  Initial version.



"""
:mod:`recommender` -- the recommender modules  
================================================================

This module contains functions and classes to produce recommendations.

"""

from interfaces import UserBasedRecommender
from topmatches import topUsers, topItems

class UserRecommender(UserBasedRecommender):
	'''
	A simple Recommender which uses a given dataModel and NeighborHood 
	to produce recommendations.	
	
	'''
	def __init__(self,model,similarity,neighborhood,capper=True):
		''' UserBasedRecommender Class Constructor 
			
			`model` is the data source model
			
			`neighborhood` is the neighborhood strategy for computing the most similar users.
			
			`similarity` is the class used for computing the similarities over the users.
			
			`capper` a normalizer for Maximum/Minimum Preferences range.
			
		'''
		UserBasedRecommender.__init__(self,model)
		self.neighborhood = neighborhood
		self.similarity  = similarity
		self.capper = capper
		
	def recommend(self,userID,howMany,rescorer=None):
		nearestN = self.neighborhood.userNeighborhood(userID,rescorer)
		
		if not nearestN:
			return []
		
		allItemIDs = self.allOtherItems(userID, nearestN)
				
		rec_items = topItems(userID,allItemIDs,howMany,self.estimatePreference,self.similarity,rescorer)

		return rec_items
	

	def estimatePreference(self,**args):
		userID = args.get('thingID',None) or args.get('userID',None)
		itemID = args.get('itemID',None)
		similarity = args.get('similarity',self.similarity)
		nHood = args.get('neighborhood',None)
		rescorer = args.get('rescorer',None)
		
		if not nHood:
			pref = self.model.PreferenceValue(userID,itemID)
			if pref is not None:
				return pref
			
			nHood = self.neighborhood.userNeighborhood(userID=userID,rescorer=rescorer)
			
		if not nHood:
			return None
		
		preference = 0.0
		totalSimilarity = 0.0
		count = 0
		for usrID in nHood:
			if usrID != userID:
				pref = self.model.PreferenceValue(usrID,itemID)
				if pref is not None:
					sim = similarity.getSimilarity(usrID, userID)
					if sim is not None:
						preference+= sim*pref
						totalSimilarity += sim
						count+=1
		

		#Throw out the estimate if it was based on no data points, of course, but also if based on
		#just one. This is a bit of a band-aid on the 'stock' item-based algorithm for the moment.
		#The reason is that in this case the estimate is, simply, the user's rating for one item
		#that happened to have a defined similarity. The similarity score doesn't matter, and that
		#seems like a bad situation.
		if count <=1 or totalSimilarity == 0.0:
			return None
		
		estimated = float(preference) / totalSimilarity
		
		if self.capper:
			#TODO: Maybe put this in a separated function.
			max = self.model.MaxPreference()
			min = self.model.MinPreference()
			estimated =  max if estimated > max else min if estimated < min else estimated
					
		return estimated


	def mostSimilarUserIDs(self,userID,howMany,rescorer=None):
		return topUsers(userID,self.model.UserIDs(),howMany,self.neighborhood.estimatePreference,self.similarity,rescorer)		

				
	def allOtherItems(self,userID,neighborhood):
		possibleItemIDs = []
		for usrID in neighborhood:
			possibleItemIDs.extend(self.model.ItemIDsFromUser(usrID))
		
		itemIds = self.model.ItemIDsFromUser(userID)
		possibleItemIDs = list(set(possibleItemIDs))
		
		return [itemID for itemID in possibleItemIDs if itemID not in itemIds]		
		