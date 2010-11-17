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


0.1 2010-11-16 Initial version.
'''

__author__ = 'marcel@orygens.com'

import unittest

from models.datamodel import *
from neighborhood.itemstrategies import PreferredItemsNeighborhoodStrategy


class TestPreferredItemsNeighborhoodStrategy(unittest.TestCase):
	
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

	
	
	def test_empty_candidateItems(self):
		userID = 'Maria Gabriela'
		strategy = PreferredItemsNeighborhoodStrategy()
		self.assertEquals([],strategy.candidateItems(userID,self.model))


	def test_full_candidateItems(self):
		userID = 'Marcel Caraciolo'
		strategy = PreferredItemsNeighborhoodStrategy()
		self.assertEquals([],strategy.candidateItems(userID,self.model))
		

	def test_semi_candidateItems(self):
		userID = 'Leopoldo Pires'
		strategy = PreferredItemsNeighborhoodStrategy()
		self.assertEquals(['Just My Luck', 'You, Me and Dupree'],strategy.candidateItems(userID,self.model))
		

	def suite():
		suite = unittest.TestSuite()
		suite.addTests(unittest.makeSuite(TestNearestNUserNeighborhood))

		return suite

if __name__ == '__main__':
	unittest.main()