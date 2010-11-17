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
:mod:`itemstrategies` -- the item strategies modules  
================================================================

This module contains functions and classes to retrieve all items that could possibly be recommended to the user


"""

from interfaces import CandidateItemsStrategy

class PreferredItemsNeighborhoodStrategy(CandidateItemsStrategy):
	'''
	Returns all items that have not been rated by the user and that were preferred by another user that
	has preferred at least one item that the current user has preferred too
	'''
	
	def candidateItems(self,userID,model):
		possibleItemIDs = []
		itemIDs = model.ItemIDsFromUser(userID)
		for itemID in itemIDs:
			prefs2 = model.PreferencesForItem(itemID)
			for otherUserID,pref in prefs2:
				possibleItemIDs.extend(model.ItemIDsFromUser(otherUserID))
				
		possibleItemIDs = list(set(possibleItemIDs))
		
		return [itemID for itemID in possibleItemIDs if itemID not in itemIDs]
	