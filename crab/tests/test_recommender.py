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
from recommender.topmatches import *
from recommender.recommender import UserRecommender
from similarities.similarity import UserSimilarity
from similarities.similarity_distance import *
from scoring.scorer import TanHScorer, NaiveScorer
from neighborhood.neighborhood import NearestNUserNeighborhood



class TestUserBasedRecommender(unittest.TestCase):
	
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
		self.neighbor = NearestNUserNeighborhood(self.similarity,self.model,4,0.0)
		
	
	def test_create_UserBasedRecommender(self):
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		self.assertEquals(recSys.similarity,self.similarity)
		self.assertEquals(recSys.capper,True)
		self.assertEquals(recSys.neighborhood,self.neighbor)
		self.assertEquals(recSys.model,self.model)
	
	
	def test_all_watched_allOtherItems(self):
		userID = 'Luciana Nunes'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		nearestN = self.neighbor.userNeighborhood(userID)
		self.assertEquals([],recSys.allOtherItems(userID,nearestN))	
		
	def test_semi_watched_allOtherItems(self):
		userID = 'Leopoldo Pires'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		nearestN = self.neighbor.userNeighborhood(userID)
		self.assertEquals(['Just My Luck', 'You, Me and Dupree'],recSys.allOtherItems(userID,nearestN))	

	def test_non_watched_allOtherItems(self):
		userID = 'Maria Gabriela'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		nearestN = self.neighbor.userNeighborhood(userID)
		self.assertEquals(['Lady in the Water', 'Snakes on a Plane', 'Just My Luck', 'Superman Returns', 
							'You, Me and Dupree', 'The Night Listener'],recSys.allOtherItems(userID,nearestN))

	def test_mostSimilarUserIDs(self):
		userID = 'Marcel Caraciolo'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		self.assertEquals(['Leopoldo Pires', 'Steve Gates', 'Lorena Abreu', 'Penny Frewman'],recSys.mostSimilarUserIDs(userID,4))	
	
	def test_user_no_preference_mostSimilarUserIDs(self):
		userID = 'Maria Gabriela'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		self.assertEquals(['Leopoldo Pires', 'Lorena Abreu', 'Luciana Nunes', 'Marcel Caraciolo'],recSys.mostSimilarUserIDs(userID,4))
	
	
	def test_empty_mostSimilarUserIDs(self):
		userID = 'Maria Gabriela'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		self.assertEquals([],recSys.mostSimilarUserIDs(userID,0))
	
	def test_local_estimatePreference(self):
		userID = 'Marcel Caraciolo'
		itemID = 'Superman Returns'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		self.assertAlmostEquals(3.5,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID))
		
		
	def test_local_not_existing_estimatePreference(self):
		userID = 'Leopoldo Pires'
		itemID = 'You, Me and Dupree'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,True)
		self.assertAlmostEquals(2.065394689,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID))
		

	def test_local_not_existing_capper_False_estimatePreference(self):
		userID = 'Leopoldo Pires'
		itemID = 'You, Me and Dupree'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,False)
		self.assertAlmostEquals(2.065394689,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID))
	
	
	def test_local_not_existing_rescorer_estimatePreference(self):
		userID = 'Leopoldo Pires'
		itemID = 'You, Me and Dupree'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,False)
		scorer = TanHScorer()
		self.assertAlmostEquals(2.5761016605,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID,rescorer=scorer))

	def test_recommend(self):
		userID = 'Leopoldo Pires'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,False)
		self.assertEquals(['Just My Luck', 'You, Me and Dupree'],recSys.recommend(userID,4))
		
	
	def test_empty_recommend(self):
		userID = 'Marcel Caraciolo'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,False)
		self.assertEquals([],recSys.recommend(userID,4))
	
	def test_full_recommend(self):
		userID = 'Maria Gabriela'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,False)
		self.assertEquals([],recSys.recommend(userID,4))

	def test_semi_recommend(self):
		userID = 'Leopoldo Pires'
		recSys = UserRecommender(self.model,self.similarity,self.neighbor,False)
		self.assertEquals(['Just My Luck'],recSys.recommend(userID,1))

def suite():
	suite = unittest.TestSuite()
	suite.addTests(unittest.makeSuite(TestUserBasedRecommender))

	return suite

if __name__ == '__main__':
	unittest.main()