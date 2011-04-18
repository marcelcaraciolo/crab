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
import sys

#sys.path.append('/Users/marcelcaraciolo/Desktop/crab/crab/crab')


from models.datamodel import *
from recommender.topmatches import *
from recommender.recommender import UserRecommender, ItemRecommender
from recommender.utils import DiffStorage
from similarities.similarity import UserSimilarity, ItemSimilarity
from similarities.similarity_distance import *
from scoring.scorer import TanHScorer, NaiveScorer
from neighborhood.neighborhood import NearestNUserNeighborhood
from neighborhood.itemstrategies import  PreferredItemsNeighborhoodStrategy


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
		
		
		
class TestSlopeOneRecommender(unittest.TestCase):
	
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
		
	def test_create_diffStorage(self):
		storage = DiffStorage(self.model,False)
		self.assertEquals(storage.stdDevWeighted,False)
		self.assertEquals(storage.model,self.model)
	
	def test_buildAveragesDiff(self):
		storage = DiffStorage(self.model,False)
		self.assertEquals(storage._diffStorage,{'Lady in the Water': {'Snakes on a Plane': -4.0, 'You, Me and Dupree': 0.0, 'Superman Returns': -6.0, 'The Night Listener': -2.0}, 
		                      'Snakes on a Plane': {'You, Me and Dupree': 8.0, 'Superman Returns': -2.0, 'The Night Listener': 1.0}, 
		                      'Just My Luck': {'Snakes on a Plane': -5.0, 'Lady in the Water': -2.0, 'You, Me and Dupree': -1.0, 'Superman Returns': -6.0, 'The Night Listener': -4.0}, 
		                      'Superman Returns': {'You, Me and Dupree': 9.5, 'The Night Listener': 3.5}, 
		                      'You, Me and Dupree': {}, 
		                      'The Night Listener': {'You, Me and Dupree': 2.5}})
		
		self.assertEquals(storage._freqs,{'Lady in the Water': {'Snakes on a Plane': 5, 'You, Me and Dupree': 4, 'Superman Returns': 5, 'The Night Listener': 5},
		             'Snakes on a Plane': {'You, Me and Dupree': 6, 'Superman Returns': 7, 'The Night Listener': 6}, 
		             'Just My Luck': {'Snakes on a Plane': 4, 'Lady in the Water': 3, 'You, Me and Dupree': 4, 'Superman Returns': 4, 'The Night Listener': 4},
		             'Superman Returns': {'You, Me and Dupree': 6, 'The Night Listener': 6}, 
		             'You, Me and Dupree': {}, 'The Night Listener': {'You, Me and Dupree': 5}} )
		
		self.assertEquals(storage._recommendableItems,['Just My Luck', 'Lady in the Water', 'Snakes on a Plane', 'Superman Returns', 'The Night Listener', 'You, Me and Dupree'])
		
		
		storage = DiffStorage(DictDataModel({}),False)
		self.assertEquals(storage._diffStorage,{})
		self.assertEquals(storage._freqs,{})
		self.assertEquals(storage._recommendableItems,[])
				
		storage = DiffStorage(DictDataModel({}),False)
		self.assertEquals(storage._diffStorage,{})
		self.assertEquals(storage._freqs,{})
		self.assertEquals(storage._recommendableItems,[])
		
		storage = DiffStorage(DictDataModel({'Maria':{'A':4.0}}),False)
		self.assertEquals(storage._diffStorage,{'A': {}})
		self.assertEquals(storage._freqs,{'A': {} })
		self.assertEquals(storage._recommendableItems,['A'])

		storage = DiffStorage(DictDataModel({'Maria':{'A':4.0}, 'Joao':{'B': 5.0} }),False)
		self.assertEquals(storage._diffStorage,{'A': {}, 'B':{}})
		self.assertEquals(storage._freqs,{'A': {}, 'B': {} })
		self.assertEquals(storage._recommendableItems,['A','B'])
			
		storage = DiffStorage(DictDataModel({'Maria':{'A':4.0, 'B': 2.0}, 'Joao':{'B': 5.0} }),False)
		self.assertEquals(storage._diffStorage,{'A': {}, 'B':{}})
		self.assertEquals(storage._freqs,{'A': {}, 'B': {} })
		self.assertEquals(storage._recommendableItems,['A','B'])
		
		storage = DiffStorage(DictDataModel({'Maria':{'A':4.0, 'B': 2.0}, 'Joao':{'B': 5.0, 'A':5.0}, 'Flavia':{'A': 2.0, 'C': 3.0} }),False)
		self.assertEquals(storage._diffStorage,{'A': {'B': 2.0}, 'B':{}, 'C':{}})
		self.assertEquals(storage._freqs,{'A': {'B':2}, 'B': {}, 'C': {} })
		self.assertEquals(storage._recommendableItems,['A','B', 'C'])
	

	
	
		
		
				

class TestItemBasedRecommender(unittest.TestCase):
		
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
		self.similarity = ItemSimilarity(self.model,sim_euclidian)
		self.strategy = PreferredItemsNeighborhoodStrategy()
		
	
	def test_create_ItemBasedRecommender(self):
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,True)
		self.assertEquals(recSys.similarity,self.similarity)
		self.assertEquals(recSys.capper,True)
		self.assertEquals(recSys.strategy,self.strategy)
		self.assertEquals(recSys.model,self.model)
	
	
	def test_oneItem_mostSimilarItems(self):
		itemIDs = ['Superman Returns']
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,True)
		self.assertEquals(['Snakes on a Plane', 'The Night Listener', 'Lady in the Water', 'Just My Luck'],recSys.mostSimilarItems(itemIDs,4))
	
	def test_multipeItems_mostSimilarItems(self):
		itemIDs = ['Superman Returns','Just My Luck']
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,True)
		self.assertEquals(['Lady in the Water', 'Snakes on a Plane', 'The Night Listener', 'You, Me and Dupree'],recSys.mostSimilarItems(itemIDs,4))
	
	def test_semiItem_mostSimilarItems(self):
		itemIDs = ['Superman Returns','Just My Luck','Snakes on a Plane',  'The Night Listener',  'You, Me and Dupree']
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,True)
		self.assertEquals(['Lady in the Water'],recSys.mostSimilarItems(itemIDs,4))
	
	def test_allItem_mostSimilarItems(self):
		itemIDs = ['Superman Returns','Just My Luck','Snakes on a Plane',  'The Night Listener',  'You, Me and Dupree','Lady in the Water']
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,True)
		self.assertEquals([],recSys.mostSimilarItems(itemIDs,4))
		
		
	def test_local_estimatePreference(self):
		userID = 'Marcel Caraciolo'
		itemID = 'Superman Returns'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,True)
		self.assertAlmostEquals(3.5,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID))


	def test_local_not_existing_estimatePreference(self):
		userID = 'Leopoldo Pires'
		itemID = 'You, Me and Dupree'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,True)
		self.assertAlmostEquals(3.14717875510,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID))


	def test_local_not_existing_capper_False_estimatePreference(self):
		userID = 'Leopoldo Pires'
		itemID = 'You, Me and Dupree'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,False)
		self.assertAlmostEquals(3.14717875510,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID))


	def test_local_not_existing_rescorer_estimatePreference(self):
		userID = 'Leopoldo Pires'
		itemID = 'You, Me and Dupree'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,False)
		scorer = TanHScorer()
		self.assertAlmostEquals(3.1471787551,recSys.estimatePreference(userID=userID,similarity=self.similarity,itemID=itemID,rescorer=scorer))


	def test_empty_recommend(self):
		userID = 'Marcel Caraciolo'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,False)
		self.assertEquals([],recSys.recommend(userID,4))

		
	def test_recommend(self):
		userID = 'Leopoldo Pires'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,False)
		self.assertEquals(['Just My Luck', 'You, Me and Dupree'],recSys.recommend(userID,4))

		
	def test_full_recommend(self):
		userID = 'Maria Gabriela'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,False)
		self.assertEquals([],recSys.recommend(userID,4))


	def test_semi_recommend(self):
		userID = 'Leopoldo Pires'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,False)
		self.assertEquals(['Just My Luck'],recSys.recommend(userID,1))


	def test_recommendedBecause(self):
		userID = 'Leopoldo Pires'
		itemID = 'Just My Luck'
		recSys = ItemRecommender(self.model,self.similarity,self.strategy,False)
		self.assertEquals(['The Night Listener', 'Superman Returns'],recSys.recommendedBecause(userID,itemID,2))
		
	
def suite():
	suite = unittest.TestSuite()
	suite.addTests(unittest.makeSuite(TestUserBasedRecommender))
	suite.addTests(unittest.makeSuite(TestItemBasedRecommender))
	suite.addTests(unittest.makeSuite(TestSlopeOneRecommender))
	

	return suite

if __name__ == '__main__':
	unittest.main()