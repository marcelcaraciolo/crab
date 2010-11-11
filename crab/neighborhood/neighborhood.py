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
:mod:`neighborhood` -- the neighborhood modules  
================================================================

This module contains functions and classes to compute the neighborhood given an user.

"""

from interfaces import Neighborhood
from recommender.topmatches import topUsers
import random


class NearestNUserNeighborhood(Neighborhood):
	
	def __init__(self,similarity,model,numUsers,minSimilarity,samplingRate=1):
		''' Constructor Class

		`numUsers` neighborhood size; capped at the number of users in the data model		
		`samplingRate`  percentage of users to consider when building neighborhood
		`minSimilarity`  minimal similarity required for neighbors	 
		'''
		Neighborhood.__init__(self,similarity,model,samplingRate)
		nUsers = model.NumUsers()
		self.numUsers =  nUsers if numUsers > nUsers else numUsers
		self.minSimilarity = minSimilarity
	
	
	def estimatePreference(self,**args):
		#@TODO: How to improve this architecture for estimatePreference as a method for topMatches.
		userID = args.get('thingID',None) or args.get('userID',None)
		otherUserID = args.get('otherUserID',None) 
		similarity = args.get('similarity',self.similarity)
		
		#Don't consider the user itself as possible most similar user
		if userID == otherUserID:
			return None
			
		estimated = similarity.getSimilarity(userID,otherUserID)
	
		return estimated
			
	
	def userNeighborhood(self,userID,rescorer=None):
		''' Return the most similar users to the given userID'''
		#Sampling
		userIDs = self.getSampleUserIDs()
		
		if not userIDs:
			return []
		 
		rec_users = topUsers(userID,userIDs,self.numUsers,self.estimatePreference,self.similarity,rescorer)
	
		return rec_users
	
	def getSampleUserIDs(self):
		userIDs = self.model.UserIDs()
		
		numberOfUsers = int(float(self.samplingRate) * len(userIDs))
		
		if numberOfUsers == len(userIDs):
			return userIDs
		elif numberOfUsers == 0:
			return []
		else:
			total_users = 0
			length = len(userIDs) - numberOfUsers
			while total_users < length:
				random.shuffle(userIDs)
				userIDs.pop()
				total_users+=1

			return userIDs
	