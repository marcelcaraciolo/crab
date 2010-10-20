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


0.1 2010-10-11 Initial version.
               Added sim_euclidian , sim_pearson, sim_spearman
0.11 2010-10-13 Added sim_cosine, sim_tanimoto
0.12 2010-10-16 Added sim_loglikehood
0.13 2010-10-17 Added  sim_sorensen
0.14 2010-10-20 Added sim_manhattan



'''

"""
:mod:`similarity_distance` -- the similarity distances table
================================================================

	This module is responsible of joining all similariy distances funcions.
		

"""

from math import sqrt, log

def sim_euclidian(prefs, person1 , person2):
	'''
	An implementation of a "similarity" based on the Euclidean "distance" between two users X and Y. Thinking
	of items as dimensions and preferences as points along those dimensions, a distance is computed using all
	items (dimensions) where both users have expressed a preference for that item. This is simply the square
	root of the sum of the squares of differences in position (preference) along each dimension. The similarity
	is then computed as 1 / (1 + distance), so the resulting values are in the range (0,1].
	
	Parameters:
		the prefs: The preferences in dict format.
		person1: The user profile you want to compare 
		person2: The second user profile you want to compare
	
	'''

	sim = {}
	
	[sim.update({item:1})  for item in prefs[person1]  if item in prefs[person2]]
	
	if len(sim) == 0: return 0.0
	
	sum_of_squares = sum([ pow(prefs[person1][item] - prefs[person2][item],2) 
	     					for item in prefs[person1] if item in prefs[person2]])
	
	return 1 / (1+ sum_of_squares)
	


def sim_pearson(prefs,person1,person2):
	'''
	This correlation implementation is equivalent to the cosine similarity since the data it receives
	 is assumed to be centered -- mean is 0. The correlation may be interpreted as the cosine of the angle
	 between the two vectors defined by the users' preference values.
	
	Parameters:
		the prefs: The preferences in dict format.
		person1: The user profile you want to compare 
		person2: The second user profile you want to compare
	'''
	sim = {}
	
	[  sim.update({item:1})  for item in prefs[person1]  if item in prefs[person2]  ]
	
	n = len(sim)
	
	if n == 0: return 0.0
	
	sum1 = sum([ prefs[person1][it]  for it in sim])
	sum2 = sum([ prefs[person2][it]  for it in sim])
	
	sum1Sq = sum([pow(prefs[person1][it],2) for it in sim])
	sum2Sq = sum([pow(prefs[person2][it],2) for it in sim])
	
	pSum = sum(prefs[person1][it] * prefs[person2][it] for it in sim)
	
	num  = pSum - (sum1*sum2 / float(n))
	
	den = sqrt((sum1Sq-pow(sum1,2)/n) * (sum2Sq-pow(sum2,2)/n))
	
	if den == 0: return 0
	
	r = num/den
	
	return r
	
	
	
def sim_spearman(prefs,person1,person2):
	'''
	Like  sim_pearson , but compares relative ranking of preference values instead of
	preference values themselves. That is, each user's preferences are sorted and then assign a rank as their
 	preference value, with 1 being assigned to the least preferred item.

	Parameters:
		the prefs: The preferences in dict format.
		person1: The user profile you want to compare 
		person2: The second user profile you want to compare

 	'''
	simP1 = {}
	simP2 = {}
	rank = 1.0
	
	
	#First order from the lowest to greatest value.
	person1_items = sorted(prefs[person1].items(),lambda x, y: cmp(x[1], y[1]))
	person2_items = sorted(prefs[person2].items(),lambda x, y: cmp(x[1], y[1]))
	
	
	for key,value in person1_items:
		if key in prefs[person2]:
			simP1.update({key:rank})
			rank+=1
	
	rank = 1.0
	for key,values in person2_items:
		if key in prefs[person1]:
			simP2.update({key:rank})
			rank+=1
	
	sumDiffSq = 0.0
	for key,rank in simP1.items():
		if key in simP2:
			sumDiffSq +=  pow((rank -  simP2[key]),2.0)
	
	n = len(simP1)
	
	if n == 0: return 0.0
	
	return 1.0 -  (  (6.0 * sumDiffSq) /  (n * (n*n -1)) )
	

def sim_tanimoto(prefs,person1,person2):
	'''
  	An implementation of a "similarity" based on the Tanimoto coefficient, 
    or extended Jaccard coefficient.
	
	This is intended for "binary" data sets where a user either expresses a generic "yes" preference for an
	item or has no preference. The actual preference values do not matter here, only their presence or absence.
 
	Parameters:
		the prefs: The preferences in dict format.
		person1: The user profile you want to compare 
		person2: The second user profile you want to compare
		
	The value returned is in [0,1].

 	'''
	simP1P2  =  {}
	
	[simP1P2.update({item:1}) for item in prefs[person1] if item in prefs[person2]]
	
	return float(len(simP1P2))/ (len(person1) + len(person2) - len(simP1P2))
	

def sim_cosine(prefs, person1, person2):
	'''
	 An implementation of the cosine similarity. The result is the cosine of the angle formed between the two preference vectors.
	 Note that this similarity does not "center" its data, shifts the user's preference values so that each of their
	 means is 0. For this behavior, use Pearson Coefficient, which actually is mathematically
	 equivalent for centered data.	
	
	Parameters:
		the prefs: The preferences in dict format.
		person1: The user profile you want to compare 
		person2: The second user profile you want to compare
	'''
	
	def dot(p1,p2):
		return sum([prefs[p1][item] * prefs[p2][item] for item in prefs[p2]])
		
	def norm(p):
		return sqrt(sum([prefs[p].get(item,0) * prefs[p].get(item,0)  for item in prefs[p]]))
		
	
	if len(prefs[person1]) != len(prefs[person2]):
		raise ValueError('Size vectors different.')
		
	return dot(person1,person2) / (norm(person1) * norm(person2))
	
	
def sim_loglikehood(prefs,person1,person2):
	'''
	See http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.14.5962 and http://tdunning.blogspot.com/2008/03/surprise-and-coincidence.html .

	Parameters:
		the prefs: The preferences in dict format.
		person1: The user profile you want to compare 
		person2: The second user profile you want to compare
	'''
	
	def safeLog(d):
		if d <= 0.0:
			return 0.0
		else:
			return log(d)		
	
	def logL(p,k,n):
		return k * safeLog(p) + (n - k) * safeLog(1.0 - p)
	
	def twoLogLambda(k1,k2,n1,n2):
		p = (k1 + k2) / (n1 + n2)
		return 2.0 * (logL(k1/n1,k1,n1)  + logL(k2/n2,k2,n2) 
					  - logL(p,k1,n1) - logL(p,k2,n2))
	
	simP1P2  =  {}

	[simP1P2.update({item:1}) for item in prefs[person1] if item in prefs[person2]]
	
	if len(simP1P2) == 0:
		return 0.0
	
	nP1P2 = len(simP1P2)
	nP2 = len(prefs[person2])
	nP1 = len(prefs[person1])
	n = len(prefs)
	
	logLikeliHood = twoLogLambda(float(nP1P2), float(nP1 - nP1P2),float(nP2) ,float( n - nP2))
	
	return 1.0 - 1.0 / (1.0 + logLikeliHood )

def sim_sorensen(prefs,person1,person2):
	'''
	The Sørensen index, also known as Sørensen’s similarity coefficient,
	 is a statistic used for comparing the similarity of two samples. 
	 It was developed by the botanist Thorvald Sørensen and published in 1948.[1]
	 See the link: http://en.wikipedia.org/wiki/S%C3%B8rensen_similarity_index
	
	This is intended for "binary" data sets where a user either expresses a generic "yes" preference for an
	item or has no preference. The actual preference values do not matter here, only their presence or absence.
	
	Parameters:
		the prefs: The preferences in dict format.
		person1: The user profile you want to compare 
		person2: The second user profile you want to compare
	
	'''
	nP1P2 =  len([ item  for item in prefs[person1] if item in prefs[person2] ])
	
	if len(prefs[person1]) + len(prefs[person2]) == 0:
		return 0.0
	
	return float(2.0*nP1P2 / (len(prefs[person1]) + len(prefs[person2]) ) )


def sim_manhattan(prefs,person1,person2):
	"""The distance between two points in a grid based on a strictly horizontal and/or vertical path (that is, along the grid lines
		as opposed to the diagonal or "as the crow flies" distance. 
		The Manhattan distance is the simple sum of the horizontal and vertical components,
	 	whereas the diagonal distance might be computed by applying the Pythagorean theorem.	
	
		Parameters:
			the prefs: The preferences in dict format.
			person1: The user profile you want to compare 
			person2: The second user profile you want to compare
		
	"""
	nP1P2 =  len([ item  for item in prefs[person1] if item in prefs[person2] ])
	distance = sum([ abs(prefs[person1][key] - prefs[person2][key])   for key in prefs[person1] if key in prefs[person2]])
	
	if nP1P2 > 0:
		return float(distance)/ nP1P2
	else:
		return 0.0

	