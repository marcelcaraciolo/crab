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
from neighborhood.neighborhood import NearestNUserNeighborhood
from similarities.similarity import UserSimilarity
from similarities.similarity_distance import *
from scoring.scorer import TanHScorer, NaiveScorer


def estimateUserUser(**args):
	userID = args['thingID'] or args.get('userID',None)
	otherUserID = args['otherUserID']
	similarity = args['similarity']
	
	if userID == otherUserID:
		return None
			
	estimated = similarity.getSimilarity(userID,otherUserID)
		
	return estimated


def estimateUserItem(**args):
	userID = args.get('thingID',None) or args.get('userID',None)
	itemID = args.get('itemID',None)
	similarity = args.get('similarity',None)
	nHood = args.get('neighborhood',None)
	model =args.get('model',None)
	rescorer = args.get('rescorer',None)
	capper = args.get('capper',False)
	
	pref = model.PreferenceValue(userID,itemID)
	if pref is not None:
		return pref

	nHood = nHood.userNeighborhood(userID=userID,rescorer=rescorer)
	
	if not nHood:
		return None
	
	preference = 0.0
	totalSimilarity = 0.0
	count = 0
	for usrID in nHood:
		if usrID != userID:
			pref = model.PreferenceValue(usrID,itemID)
			if pref is not None:
				sim = similarity.getSimilarity(usrID, userID)
				if sim is not None:
					preference+= sim*pref
					totalSimilarity += sim
					count+=1
	
	#Throw out the estimate if it was based on no data points, of course, but also if based on
	#just one. This is a bit of a band-aid on the 'stock' item-based algorithm for the moment.
	#The reason is that in this case the estimate is, simply, the user's rating for one item
	#that happened to have a defined similarity. The similarity score doesn't matter, and that
	#seems like a bad situation.
	if count <=1:
		return None
	
	estimated = float(preference) / totalSimilarity
	
		
	if capper:
		#TODO: Maybe put this in a separated function.
		max = self.model.MaxPreference()
		min = self.model.MinPreference()
		estimated =  max if estimated > max else min if estimated < min else estimated
				
	return estimated



class TestTopMatches(unittest.TestCase):
	
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
		'Steve Gates': {'Lady in  the Water': 3.0, 'Snakes on a Plane': 4.0, 
		 'Just My Luck': 2.0, 'Superman Returns': 3.0, 'The Night Listener': 3.0,
		 'You, Me and Dupree': 2.0}, 
		'Sheldom': {'Lady in the Water': 3.0, 'Snakes on a Plane': 4.0,
		 'The Night Listener': 3.0, 'Superman Returns': 5.0, 'You, Me and Dupree': 3.5},
		'Penny Frewman': {'Snakes on a Plane':4.5,'You, Me and Dupree':1.0,'Superman Returns':4.0},
		'Maria Gabriela': {}}

		self.model = DictDataModel(movies)
		self.similarity = UserSimilarity(self.model,sim_euclidian)
			
	def test_topUsers(self):
		userID = 'Luciana Nunes'
		numUsers = 4
		allUserIDs = self.model.UserIDs()
		preferenceEstimator = estimateUserUser
		rescorer = NaiveScorer()		
		self.assertEquals(['Sheldom', 'Leopoldo Pires', 'Marcel Caraciolo', 'Lorena Abreu'] ,topUsers(userID,allUserIDs,numUsers,preferenceEstimator,self.similarity))


	def test_rescorer_topUsers(self):
		userID = 'Luciana Nunes'
		numUsers = 4
		allUserIDs = self.model.UserIDs()
		preferenceEstimator = estimateUserUser
		rescorer  = TanHScorer()	
		self.assertEquals(['Maria Gabriela', 'Penny Frewman', 'Steve Gates', 'Lorena Abreu'] ,topUsers(userID,allUserIDs,numUsers,preferenceEstimator,self.similarity,rescorer))

	def test_maxUsers_topUsers(self):
		userID = 'Luciana Nunes'
		numUsers = 9
		allUserIDs = self.model.UserIDs()
		preferenceEstimator = estimateUserUser
		rescorer  = TanHScorer()	
		self.assertEquals(['Maria Gabriela', 'Penny Frewman', 'Steve Gates', 'Lorena Abreu', 'Marcel Caraciolo', 'Leopoldo Pires', 'Sheldom'],topUsers(userID,allUserIDs,numUsers,preferenceEstimator,self.similarity,rescorer))

	def test_minUsers_topUsers(self):
		userID = 'Luciana Nunes'
		numUsers = 0
		allUserIDs = self.model.UserIDs()
		preferenceEstimator = estimateUserUser
		rescorer  = TanHScorer()	
		self.assertEquals([],topUsers(userID,allUserIDs,numUsers,preferenceEstimator,self.similarity,rescorer))
	
	def test_UserItem_topItems(self):
		userID = 'Leopoldo Pires'
		numItems = 4
		allItemIDs = self.model.ItemIDs()
		preferenceEstimator = estimateUserItem
		rescorer = NaiveScorer()	
		n = NearestNUserNeighborhood(self.similarity,self.model,4,0.0)								
		self.assertEquals(['The Night Listener', 'Superman Returns', 'Snakes on a Plane', 'Just My Luck'],
			topItems(userID,allItemIDs,numItems, preferenceEstimator,self.similarity,None,model=self.model,neighborhood=n))
			
	def test_rescorer_UserItem_topItems(self):
		userID = 'Leopoldo Pires'
		numItems = 4
		allItemIDs = self.model.ItemIDs()
		preferenceEstimator = estimateUserItem
		rescorer = TanHScorer()	
		n = NearestNUserNeighborhood(self.similarity,self.model,4,0.0)								
		self.assertEquals(['Lady in the Water', 'You, Me and Dupree', 'Snakes on a Plane', 'Superman Returns'],
			topItems(userID,allItemIDs,numItems, preferenceEstimator,self.similarity,rescorer,model=self.model,neighborhood=n))

	def test_maxItems_UserItem_topItems(self):
		userID = 'Leopoldo Pires'
		numItems = 9
		allItemIDs = self.model.ItemIDs()
		preferenceEstimator = estimateUserItem
		n = NearestNUserNeighborhood(self.similarity,self.model,4,0.0)								
		self.assertEquals(['The Night Listener', 'Superman Returns', 'Snakes on a Plane', 'Just My Luck', 
				'Lady in the Water', 'You, Me and Dupree'], topItems(userID,allItemIDs,numItems, preferenceEstimator,self.similarity,None,model=self.model,neighborhood=n,))


	def test_minItems_UserItem_topItems(self):
		userID = 'Leopoldo Pires'
		numItems = 0
		allItemIDs = self.model.ItemIDs()
		preferenceEstimator = estimateUserItem
		n = NearestNUserNeighborhood(self.similarity,self.model,4,0.0)								
		self.assertEquals([], topItems(userID,allItemIDs,numItems, preferenceEstimator,self.similarity,None,model=self.model,neighborhood=n,))


	def suite():
		suite = unittest.TestSuite()
		suite.addTests(unittest.makeSuite(TestNearestNUserNeighborhood))

		return suite

if __name__ == '__main__':
	unittest.main()