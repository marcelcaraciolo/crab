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

#0.1 2010-10-31  Initial version.
#0.11 2010-11-04 Added Recommender Abstract Class and Neighborhood Abstract class.


"""
:mod:`interfaces` -- the interfaces module
================================================================

	This module contains basic interfaces used throughout the crab package.
	The interfaces are realized as abstract base classes (ie., some optional functionality
	 is provided in the interface itself, so that the interfaces can be subclassed).		

"""

#Base classes


class Similarity(object):
	"""
	Similarity Class - for similarity searches over a set of items/users.
	
	In all instances, there is a data model against which we want to perform the
	similarity search.
	
	For each similarity search, the input is a item/user and the output are its
	similarities to individual items/users.
	
	Similarity queries are realized by calling ``self[query_item]``.
	There is also a convenience wrapper, where iterating over `self` yields
	similarities of each object in the model against the whole data model (ie.,
	the query is each item/user in turn).
	
		
	""" 
	
	def __init__(self,model,distance,numBest=None):
		""" The constructor of Similarity class 
		
		`model` defines the data model where data is fetched.
		
		`distance` The similarity measured (function) between two vectors.
		
		If `numBest` is left unspecified, similarity queries return a full list (one
		float for every item in the model, including the query item).
		
		If `numBest` is set, queries return `numBest` most similar items, as a
		sorted list.
		
		
		"""
		self.model = model
		self.distance = distance
		self.numBest = numBest
		
	
	def getSimilarity(self,vec1,vec2):
		"""
		Return similarity of a vector `vec1` to a specific vector `vec2` in the model.
		The vector is assumed to be either of unit length or empty.
		
		"""
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	
	def getSimilarities(self,vec):
		"""
		
		Return similarity of a vector `vec` to all vectors in the model.
		The vector is assumed to be either of unit length or empty.
		
		"""
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		

	def __getitem__(self,vec):
		"""
		Get similarities of a vector `vec` to all items in the model
		"""
		allSims = self.getSimilarities(vec)
		
		#return either all similarities as a list, or only self.numBest most similar, depending on settings from the constructor
		
		if self.numBest is None:
			return allSims
		else:
			tops = [(label, sim) for label, sim in allSims]
			tops = sorted(tops, key = lambda item: -item[1]) # sort by -sim => highest sim first
			return tops[ : self.numBest] # return at most numBest top 2-tuples (label, sim)



class Recommender(object):
	"""
	Recommender Class - Base interface for recommending items for a user.
	
	Implementations will likely take advantage of serveral classes in other packages
	to compute this.

	"""
	
	
	def __init__(self,model):
 		""" The constructor of Similarity class 

		`model` defines the data model where data is fetched.

		"""
		self.model = model
	
	
	def recommend(self,userID,howMany,rescorer=None):
		'''
		Return a list of recommended items, ordered from most strongly recommend to least.
		
		`userID`   user for which recommendations are to be computed.
		
		`howMany`  desired number of recommendations
		
		`rescorer` rescoring function to apply before final list of recommendations is determined.
		
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")


	def estimatePreference(self,userID,itemID):
		'''
		Return an estimated preference if the user has not expressed a preference for the item, or else the 
		user's actual preference for the item. If a preference cannot be estimated, returns None
		
		`userID`   user ID whose preference is to be estimated
		
		`itemID`  item ID to estimate preference for
		
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
	def allOtherItems(self,userID):
		'''
		Return all items in the `model` for which the user has not expressed the preference and
		could possibly be recommended to the user
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
			
	
	def setPreference(self,userID,itemID,value):
		'''
		Set a new preference of a user for a specific item with a certain magnitude.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")


	def removePreference(self,userID,itemID):
		'''
		Remove a preference of a user for a specific item
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")


class UserBasedRecommender(Recommender):
	
	def __init__(self,model):
 		""" The constructor of Similarity class 

		`model` defines the data model where data is fetched.

		"""
		Recommender.__init__(self,model)
	
	def mostSimilarUserIDs(self,userID,howMany,rescorer=None):
		'''
		Return users most similar to the given user.
		
		`userID` ID of the user for which to find most similar users to find.
		`howMany` the number of most similar users to find
		`rescorer`  which can adjust user-user similarity estimates used to determine most similar
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")		
	

		
class Neighborhood(object):
	''' 
	Implementations of this interface compute a "neighborhood" of users like a given user. 
	This neighborhood can be used to compute recommendations then.
	'''
	def __init__(self,similarity,dataModel,samplingRate):
		''' Base Constructor Class '''
		self.model = dataModel
		self.samplingRate = samplingRate
		self.similarity = similarity
	
	def userNeighborhood(self,userID):
		'''
		Return IDs of users in the neighborhood
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
	
	
	def estimatePreference(self,**args):
		'''
		Estimate a preference for an item/user.
		'''
		raise NotImplementedError("cannot instantiate Abstract Base Class")
		
		
		