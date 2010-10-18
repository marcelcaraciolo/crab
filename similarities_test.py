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
				Added tests for sim_euclidian, sim_pearson and sim_spearman
0.11 2010-10-13 Added tests for sim_tanimoto, sim_cosine
0.12 2010-10-17 Added tests for sim_loglikehood

'''

"""
:mod:`similarities_test` -- the similarity evaluation tests
================================================================
		

"""

__author__ = 'marcel@orygens.com'

import unittest

from similarity.similarity_distance import sim_euclidian,sim_pearson, sim_spearman, sim_tanimoto, sim_cosine, sim_loglikehood

class SimilarityTest(unittest.TestCase):
	
	def setUp(self):
		
		#SIMILARITY BY RATES.
		self.movies={'Marcel Caraciolo': {'Lady in the Water': 2.5, 'Snakes on a Plane': 3.5,
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
	
	
	def test_basic_rate_euclidian_similarity(self):
		self.assertAlmostEquals(0.148148148148148, sim_euclidian(self.movies,'Marcel Caraciolo', 'Luciana Nunes'))
		
	def test_empty_rate_euclidian_similarity(self):
		self.assertAlmostEquals(0.0, sim_euclidian(self.movies,'Marcel Caraciolo', 'Maria Gabriela'))
		
	def test_basic_rate_pearson_similarity(self):
		self.assertAlmostEquals(0.396059017, sim_pearson(self.movies,'Marcel Caraciolo', 'Luciana Nunes'))

	def test_empty_rate_pearson_similarity(self):
		self.assertAlmostEquals(0, sim_pearson(self.movies,'Marcel Caraciolo', 'Maria Gabriela'))
		
	def test_basic_rate_spearman_similarity(self):
		self.assertAlmostEquals(0.5428571428, sim_spearman(self.movies,'Marcel Caraciolo', 'Luciana Nunes'))
		
	def test_empty_rate_spearman_similarity(self):
		self.assertAlmostEquals(0, sim_pearson(self.movies,'Marcel Caraciolo', 'Maria Gabriela'))
	
	def test_basic_rate_tanimoto_similarity(self):
		self.assertAlmostEquals(0.26086956, sim_tanimoto(self.movies,'Marcel Caraciolo', 'Luciana Nunes'))
			
	def test_empty_rate_tanimoto_similarity(self):
		self.assertAlmostEquals(0.0, sim_tanimoto(self.movies,'Marcel Caraciolo', 'Maria Gabriela'))
	
	def test_basic_rate_cosine_similarity(self):
		self.assertAlmostEquals(0.960646301, sim_cosine(self.movies,'Marcel Caraciolo', 'Luciana Nunes'))

	def test_empty_rate_cosine_similarity(self):
		self.assertRaises(ValueError, sim_cosine, self.movies,'Marcel Caraciolo', 'Maria Gabriela')        
		
	
	def test_basic_rate_loglikehood_similarity(self):
		self.assertAlmostEquals(0.8999736, sim_loglikehood(self.movies,'Marcel Caraciolo', 'Luciana Nunes'))

	def test_empty_rate_loglikehood_similarity(self):
		self.assertAlmostEquals(0.0, sim_loglikehood(self.movies,'Marcel Caraciolo', 'Maria Gabriela'))

def suite():
	suite = unittest.TestSuite()
	suite.addTests(unittest.makeSuite(SimilarityTest))
	
	return suite

if __name__ == '__main__':
	unittest.main()



