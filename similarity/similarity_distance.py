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



'''

"""
:mod:`similarity_distance` -- the similarity distances table
================================================================

	This module is responsible of joining all similariy distances funcions.
		

"""

from math import sqrt

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
		
	
	
	
	
	
	