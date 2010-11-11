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


0.1 2010-11-08 Initial version.
'''

__author__ = 'marcel@orygens.com'

import unittest

from models.datamodel import *
from neighborhood.neighborhood import NearestNUserNeighborhood
from similarities.similarity import UserSimilarity
from similarities.similarity_distance import *
from scoring.scorer import TanHScorer, NaiveScorer

class TestNearestNUserNeighborhood(unittest.TestCase):
	
	def setUp(self):
		#SIMILARITY BY RATES.
		movies={'Marcel Caraciolo': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
		 'Just My Luck': 3.0, 'Superman Returns': 3.5, 'You, Me and Dupree': 2.5, 
		 'The Night Listener': 3.0},
		'Luciana Nunes': {'Lady in the Water': 3.0, 'Snakes on a Plane': 3.5, 
		 'Just My Luck': 1.5, 'Superman Returns': 5.0, 'The Night Listener': 3.0, 
		 'You, Me and Dupree': 3.5}, 
		'Leopoldo Pires': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.0,
		 'Superman Returns': 3.5, 'The Night Listener': 4.0},
		'Lorena Abreu': {'Snakes on a Plane': 3.5, 'Just My Luck': 3.0,
		 'The Night Listener': 4.5, 'Superman Returns': 4.0, 
		 'You, Me and Dupree': 2.5},
		'Steve Gates': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0, 
		 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
		 'You, Me and Dupree': 2.0}, 
		'Sheldom': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
		 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
		'Penny Frewman': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0},
		'Maria Gabriela': {}}

		self.model = DictDataModel(movies)
		self.similarity = UserSimilarity(self.model,sim_euclidian)
	
	
	def test_create_nearestNUserNeighborhood(self):
		numUsers = 4
		minSimilarity = 0.5
		samplingRate = 0.4
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity,samplingRate)				
		self.assertEquals(n.similarity,self.similarity)
		self.assertEquals(n.samplingRate,samplingRate)
		self.assertEquals(n.numUsers,numUsers)
		self.assertEquals(self.model,n.model)
		
	def test_maximum_limit_getSampleUserIDs(self):
		numUsers = 9
		minSimilarity = 0.0
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)				
		self.assertEquals(8,n.numUsers)

	def test_min_numUsers_getSampleUserIDs(self):
		numUsers = 4
		minSimilarity = 0.0
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)				
		self.assertEquals(8,len(n.getSampleUserIDs()))

	def test_sampling_rate_getSampleUserIDs(self):
		numUsers = 4
		minSimilarity = 0.0
		samplingRate = 0.4
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity,samplingRate)				
		self.assertEquals(3,len(n.getSampleUserIDs()))
		
	def test_empty_sampling_rate_getSampleUserIDs(self):
		numUsers = 4
		minSimilarity = 0.0
		samplingRate = 0.0
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity,samplingRate)				
		self.assertEquals(0,len(n.getSampleUserIDs()))
	
	def test_estimatePreference(self):
		numUsers = 4
		userID = 'Marcel Caraciolo'
		otherUserID = 'Luciana Nunes'
		minSimilarity = 0.0
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)
		self.assertAlmostEquals(0.294298055,n.estimatePreference(thingID=userID,similarity=self.similarity,otherUserID=otherUserID))

	def test_identity_estimatePreference(self):
		numUsers = 4
		userID = 'Marcel Caraciolo'
		otherUserID = 'Marcel Caraciolo'
		minSimilarity = 0.0
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)
		self.assertEquals(None,n.estimatePreference(thingID=userID,similarity=self.similarity,otherUserID=otherUserID))

	def test_user_dissimilar_estimatePreference(self):
		numUsers = 4
		userID = 'Marcel Caraciolo'
		otherUserID = 'Maria Gabriela'
		minSimilarity = 0.0
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)
		self.assertAlmostEquals(0.0,n.estimatePreference(thingID=userID,similarity=self.similarity,otherUserID=otherUserID))

	def test_otherUserNeighborhood(self):
		numUsers = 4
		userID = 'Luciana Nunes'
		minSimilarity = 0.0
		scorer = TanHScorer()
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)
		self.assertEquals(['Maria Gabriela', 'Penny Frewman', 'Steve Gates', 'Lorena Abreu'],n.userNeighborhood(userID,scorer))
		
	def test_userNeighborhood(self):
		numUsers = 4
		userID = 'Marcel Caraciolo'
		minSimilarity = 0.0
		scorer =  NaiveScorer()
		self.similarity = UserSimilarity(self.model,sim_tanimoto)
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)
		self.assertEquals(['Luciana Nunes', 'Steve Gates', 'Lorena Abreu', 'Sheldom'],n.userNeighborhood(userID,scorer))

	def test_invalid_UserID_userNeighborhood(self):
		numUsers = 4
		userID = 'Marcel'
		minSimilarity = 0.0
		scorer =  NaiveScorer()
		self.similarity = UserSimilarity(self.model,sim_tanimoto)
		n = NearestNUserNeighborhood(self.similarity,self.model,numUsers,minSimilarity)
		self.assertRaises(ValueError,n.userNeighborhood,userID,scorer)

	
	def suite():
		suite = unittest.TestSuite()
		suite.addTests(unittest.makeSuite(TestNearestNUserNeighborhood))

		return suite

if __name__ == '__main__':
	unittest.main()