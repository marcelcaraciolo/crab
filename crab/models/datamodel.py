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

#0.1 2010-11-01  Initial version.
#0.2 2010-11-11 Changed the method preferenceValue implementation to use get(userID) and get(itemID)


"""
:mod:`datamodel` -- the data model module
================================================================

	This module contains models that represent a repository of information a
	 bout users and their associated preferences for items.

"""

class DataModel(object):
	''' 
	Base Data Model Class that represents the basic repository of 
	information about users and their associated preferences 
	for items.
	'''
		
	def UserIDs(self):
		'''
		Return all user IDs in the model, in order
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	def PreferencesFromUser(self,userID,orderByID=True):
		'''
		Return user's preferences, ordered by user ID (if orderByID is True) 
		or by the preference values (if orderById is False), as an array.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	def ItemIDsFromUser(self,userID):
		'''
		Return IDs of items user expresses a preference for	
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")

	def ItemIDs(self):
		'''
		Return a iterator of all item IDs in the model, in order
 		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	def PreferencesForItem(self,itemID,orderByID=True):
		'''
		Return all existing Preferences expressed for that item, 
		ordered by user ID (if orderByID is True) or by the preference values 
		(if orderById is False), as an array.
 		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
	def PreferenceValue(self,userID,itemID):
		'''
		Retrieves the preference value for a single user and item.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	def PreferenceTime(self,userID,itemID):
		'''
		Retrieves the time at which a preference value from a user and item was set, if known.
		Time is expressed in the usual way, as a number of milliseconds since the epoch.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	def NumUsers(self):
		'''
		Return total number of users known to the model.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
	def NumItems(self):
		'''
		Return total number of items known to the model.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	def NumUsersWithPreferenceFor(self,*itemIDs):
		'''
		Return the number of users who have expressed a preference for all of the items
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
	def setPreference(self,userID,itemID,value):
		'''
		Sets a particular preference (item plus rating) for a user.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
	def removePreference(self,userID, itemID):
		'''
		Removes a particular preference for a user.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
	def convertItemID2name(self, itemID):
		"""Given item id number return item name"""
		raise NotImplementedError("cannot instantiate Abstract Base Class")

	def convertUserID2name(self, userID):
		"""Given user id number return user name"""
		raise NotImplementedError("cannot instantiate Abstract Base Class")	
	
		
	def hasPreferenceValues(self):
		'''
		Return True if this implementation actually it is not a 'boolean' DataModel.
		Otherwise returns False.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
		
	def MaxPreference(self):
		'''
		Return the maximum preference value that is possible in the current problem domain being evaluated.
		For example, if the domain is movie ratings on a scale of 1 to 5, this should be 5. While  a recommender
		may estimate a preference value above 5.0, it isn't "fair" to consider that the system is actually
		suggesting an impossible rating of, say, 5.4 stars.
		In practice the application would cap this estimate to 5.0. Since evaluators evaluate
		the difference between estimated and actual value, this at least prevents this effect from unfairly
		penalizing a Recommender.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
		
	def MinPreference(self):
		'''
		Returns the minimum preference value that is possible in the current problem domain being evaluated
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		


class DictDataModel(DataModel):
	'''
	A DataModel backed by a python dict structured data. This class expects a simple dictionary where each
	element contains a userID, followed by itemID, followed by preference value and optional timestamp.
	
	{userID:{itemID:preference, itemID2:preference2}, userID2:{itemID:preference3,itemID4:preference5}}
	
	Preference value is the parameter that the user simply expresses the degree of preference for an item.
	
	'''
	def __init__(self,dataS):
		''' DictDataModel Constructor '''
		DataModel.__init__(self)
		self.dataU = dataS
		self.buildModel()
		
		
	def __getitem__(self,userID):
		return self.PreferencesFromUser(userID)		

	def __iter__(self):
		for num, user in enumerate(self.userIDs):
			yield user,self[user]
				
	def buildModel(self):
		''' Build the model '''
		self.userIDs = self.dataU.keys()
		self.userIDs.sort()
		
		self.itemIDs = []
		for userID in self.userIDs:
			items = self.dataU[userID]
			self.itemIDs.extend(items.keys())
			
		self.itemIDs = list(set(self.itemIDs))
		self.itemIDs.sort()	
		
		self.maxPref = -100000000
		self.minPref = 100000000	
		
		self.dataI = {}
		for user in self.dataU:
			for item in self.dataU[user]:
				self.dataI.setdefault(item,{})
				self.dataI[item][user] = self.dataU[user][item]
				if self.dataU[user][item] > self.maxPref:
					self.maxPref = self.dataU[user][item]
				if  self.dataU[user][item] < self.minPref:
					self.minPref = self.dataU[user][item]
					
					
	def UserIDs(self):
		return self.userIDs
		
	def ItemIDs(self):
		return self.itemIDs
	
	def PreferencesFromUser(self,userID,orderByID=True):
		userPrefs = self.dataU.get(userID,None)
		
		if userPrefs is None:
			raise ValueError('User not found. Change for a suitable exception here!')
		
		userPrefs = userPrefs.items()
		
		if not orderByID:
			userPrefs.sort(key = lambda userPref: userPref[1], reverse =True)
		else:
			userPrefs.sort(key = lambda userPref: userPref[0])
		
		return userPrefs
	
	def ItemIDsFromUser(self,userID):
		prefs = self.PreferencesFromUser(userID)
		return [key for key,value in prefs]
	
	def PreferencesForItem(self,itemID,orderByID=True):
		itemPrefs = self.dataI.get(itemID,None)
		
		if not itemPrefs:
			raise ValueError('User not found. Change for a suitable exception here!')
		
		itemPrefs = itemPrefs.items()
		
		if not orderByID:
			itemPrefs.sort(key = lambda itemPref: itemPref[1], reverse =True)
		else:
			itemPrefs.sort(key = lambda itemPref: itemPref[0])
		
		return itemPrefs	

	def PreferenceValue(self,userID,itemID):
		return self.dataU.get(userID).get(itemID,None)
	
	def NumUsers(self):
		return len(self.dataU)
	
	def NumItems(self):
		return len(self.dataI)
	
	def NumUsersWithPreferenceFor(self,*itemIDs):
		if len(itemIDs) > 2 or len(itemIDs) == 0:
			raise ValueError('Illegal number of IDs')
		
		prefs1 = dict(self.PreferencesForItem(itemIDs[0]))
		
		if not prefs1:
			return 0
		
		if len(itemIDs) == 1:
			return len(prefs1)
		
		prefs2 = dict(self.PreferencesForItem(itemIDs[1]))
		

		if not prefs2:
			return 0
					
		nUsers = len([ user for user in prefs1  if user in prefs2])
	
		return nUsers
		
	def hasPreferenceValues(self):
		return True
	
	def MaxPreference(self):
		return self.maxPref
	
	def MinPreference(self):
		return self.minPref