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
			
