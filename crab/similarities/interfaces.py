#-*- coding:utf-8 -*-

'''

* Licensed to the Apache Software Foundation (ASF) under one or more
* contributor license agreements.  See the NOTICE file distributed with
* this work for additional information regarding copyright ownership.
* The ASF licenses this file to You under the Apache License, Version 2.0
* (the "License"); you may not use this file except in compliance with
* the License.  You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.

0.1 2010-10-28 Initial version.

'''

"""
:mod:`interfaces` -- the interfaces module
================================================================

	This module contains basic interfaces used throughout the similarities package.
	The interfaces are realized as abstract base classes (ie., some optional functionality
	 is provided in the interface itself, so that the interfaces can be subclassed).		

"""



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
	
	
	Example:
		>>> position = PsoDimmensions()
		>>> choices = [1,2,3,4]
		>>> lst = DimmensionList(choices)
		>>> position.add(lst)
		>>> position[0].getRandomDimmension() in lst
		True
		
	""" 
	
	def __init__(self,model):
		""" The constructor of Similarity class """
		self.model = model
	
	
	def getSimilarities(self,vec):
		"""
		
		Return similarity of a vector `vec` to all vectors in the model.
		The vector is assumed to be either of unit length or empty.
		
		"""
		return None
		

	def __getitem__(self,vec):
		#get similarities of vec to all items in the model
		
		#if self.normalize:
		#vec = matutils.unitVec(vec)
		
		allSims = self.getSimilarities(vec)
		
		#return either all similarities as a list, or only self.numBest most similar, depending on settings from the constructor
		
		if self.numBest is None:
			return allSims
		else:
			tops = [(label, sim) for label, sim in enumerate(allSims) if sim > 0]
			tops = sorted(tops, key = lambda item: -item[1]) # sort by -sim => highest sim first
			return tops[ : self.numBest] # return at most numBest top 2-tuples (label, sim)
			
		
	def __iter__(self):
		"""
		For each object in model, compute the similarity function against all other objects and yield the result. """
		for num, item in enumerate(self.model):
			yield self[item]