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
0.13 2010-10-17 Added tests for sim_sorensen
0.14 2010-10-20 Added testes for sim_manhattan

'''

"""
:mod:`similarities_test` -- the similarity evaluation tests
================================================================
		

"""

__author__ = 'marcel@orygens.com'

import unittest

from similarity.similarity_distance import *

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
		
		wordlist = []
		
		for user in self.movies:
			for item in user:
				if item not in wordlist:
					wordlist.append(item)
		self.n = len(wordlist)
	
	#EUCLIDIAN Tests
	
	def test_dict_basic_rate_euclidian_similarity(self):
		self.assertAlmostEquals(0.29429805508554946, sim_euclidian(self.movies['Marcel Caraciolo'], self.movies['Luciana Nunes']))

	def test_identity_euclidian_similarity(self):
		self.assertAlmostEquals(1.0, sim_euclidian(self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))
		
	def test_value_basic_rate_euclidian_similarity(self):
		vector =   [(self.movies['Marcel Caraciolo'][item],self.movies['Luciana Nunes'][item]) for item in self.movies['Marcel Caraciolo'] if item in self.movies['Luciana Nunes']]
		vector1 = [ v1 for v1,v2 in vector]
		vector2 = [ v2 for v1,v2 in vector]
		self.assertAlmostEquals(0.29429805508554946, sim_euclidian(vector1, vector2))
			
	def test_dict_empty_rate_euclidian_similarity(self):
		self.assertAlmostEquals(0.0, sim_euclidian(self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela']))
		
	def test_values_empty_rate_euclidian_similarity(self):
		self.assertAlmostEquals(0.0, sim_euclidian([], []))
		
	def test_different_sizes_values_rate_euclidian_similarity(self):
		self.assertRaises(ValueError, sim_euclidian,[3.5,3.2], [2.0])  
		
	#PEARSON Tests      
				
	def test_dict_basic_rate_pearson_similarity(self):
		self.assertAlmostEquals(0.396059017, sim_pearson(self.movies['Marcel Caraciolo'], self.movies['Luciana Nunes']))
		
	def test_identity_pearson_similarity(self):
		self.assertAlmostEquals(1.0, sim_pearson(self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))
		
	def test_value_basic_rate_pearson_similarity(self):
		vector =   [(self.movies['Marcel Caraciolo'][item],self.movies['Luciana Nunes'][item]) for item in self.movies['Marcel Caraciolo'] if item in self.movies['Luciana Nunes']]
		vector1 = [ v1 for v1,v2 in vector]
		vector2 = [ v2 for v1,v2 in vector]
		self.assertAlmostEquals(0.396059017, sim_pearson(vector1, vector2))
		
	
	def test_dict_empty_rate_pearson_similarity(self):
		self.assertAlmostEquals(0.0, sim_pearson(self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela']))

	def test_values_empty_rate_pearson_similarity(self):
		self.assertAlmostEquals(0.0, sim_pearson([], []))

	def test_different_sizes_values_rate_pearson_similarity(self):
		self.assertRaises(ValueError, sim_pearson,[3.5,3.2], [2.0])		


	#SPEARMAN Tests      

	def test_identity_spearman_similarity(self):
		self.assertAlmostEquals(1.0, sim_spearman(self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))

	def test_basic_rate_spearman_similarity(self):
		self.assertAlmostEquals(0.5428571428, sim_spearman(self.movies['Marcel Caraciolo'], self.movies['Luciana Nunes']))
		
	def test_empty_rate_spearman_similarity(self):
		self.assertAlmostEquals(0.0, sim_spearman(self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela']))
	
	def test_different_sizes_values_rate_pearson_similarity(self):
		self.assertRaises(TypeError, sim_spearman,[3.5,3.2], [2.0])
	

	#TANIMOTO Tests
	
	def test_identity_tanimoto_similarity(self):
		self.assertAlmostEquals(1.0, sim_tanimoto(self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))
	
	def test_dict_basic_rate_tanimoto_similarity(self):
		self.assertAlmostEquals(1.0, sim_tanimoto(self.movies['Marcel Caraciolo'], self.movies['Luciana Nunes']))
		
	def test_value_basic_rate_tanimoto_similarity(self):
		vector1 = [ item for item in self.movies['Marcel Caraciolo']]
		vector2 = [ item for item in self.movies['Luciana Nunes']]
		self.assertAlmostEquals(1.0, sim_tanimoto(vector1, vector2))
			
	def test_dict_empty_rate_tanimoto_similarity(self):
		self.assertAlmostEquals(0.0, sim_tanimoto(self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela']))
		
	def test_values_empty_rate_tanimoto_similarity(self):
		self.assertAlmostEquals(0.0, sim_tanimoto([],[]))
	
	
	#COSINE Tests
	
	def test_identity_cosine_similarity(self):
		self.assertAlmostEquals(1.0, sim_tanimoto(self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))
	
	def test_dict_basic_rate_cosine_similarity(self):
		self.assertAlmostEquals(0.960646301, sim_cosine(self.movies['Marcel Caraciolo'],self.movies['Luciana Nunes']))
	
	def test_values_basic_rate_cosine_similarity(self):
		vector =   [(self.movies['Marcel Caraciolo'][item],self.movies['Luciana Nunes'][item]) for item in self.movies['Marcel Caraciolo'] if item in self.movies['Luciana Nunes']]
		vector1 = [ v1 for v1,v2 in vector]
		vector2 = [ v2 for v1,v2 in vector]
		self.assertAlmostEquals(0.960646301, sim_cosine(vector1,vector2))
		
	def test_dict_empty_rate_cosine_similarity(self):
		self.assertRaises(ValueError, sim_cosine, self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela'])        
	
	def test_values_empty_rate_cosine_similarity(self):
		self.assertAlmostEquals(0.0, sim_cosine([],[]))
		
		
	#LOGLIKEHOOD Tests
	
	def test_identity_sim_loglikehood_similarity(self):			
		self.assertAlmostEquals(0.96728745329331456, sim_loglikehood(self.n, self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))
	
	def test_dict_basic_rate_sim_loglikehood_similarity(self):
		self.assertAlmostEquals(0.96728745329331456, sim_loglikehood(self.n, self.movies['Marcel Caraciolo'],self.movies['Luciana Nunes']))
	
	def test_values_basic_rate_sim_loglikehood_similarity(self):
		vector1 = [ item for item in self.movies['Marcel Caraciolo']]
		vector2 = [ item for item in self.movies['Luciana Nunes']]
		self.assertAlmostEquals(0.96728745329331456, sim_loglikehood(self.n, vector1,vector2))
		
	def test_dict_empty_rate_sim_loglikehood_similarity(self):
		self.assertAlmostEquals(0.0, sim_loglikehood(self.n, self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela']))       
	
	def test_values_empty_rate_sim_loglikehood_similarity(self):
		self.assertAlmostEquals(0.0, sim_loglikehood(self.n,[],[]))
	
	
	#SORENSEN Tests
	
	def test_identity_rate_sorensen_similarity(self):			
		self.assertAlmostEquals(1.0, sim_sorensen(self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))
	
	def test_dict_basic_rate_sorensen_similarity(self):
		self.assertAlmostEquals(1.0, sim_sorensen(self.movies['Marcel Caraciolo'],self.movies['Luciana Nunes']))
		
	def test_values_basic_rate_sorensen_similarity(self):
		vector1 = [ item for item in self.movies['Marcel Caraciolo']]
		vector2 = [ item for item in self.movies['Luciana Nunes']]
		self.assertAlmostEquals(1.0, sim_sorensen(vector1,vector2))
		
	def test_dict_empty_rate_sorensen_similarity(self):
		self.assertAlmostEquals(0.0, sim_sorensen(self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela']))
		
	def test_values_empty_rate_sorensen_similarity(self):
		self.assertAlmostEquals(0.0, sim_sorensen([],[]))
		
	#Manhanttan Tests
	
	def test_identity_rate_manhattan_similarity(self):			
		self.assertAlmostEquals(1.0, sim_manhattan(self.movies['Marcel Caraciolo'], self.movies['Marcel Caraciolo']))
		
	def test_dict_basic_rate_manhattan_similarity(self):
		self.assertAlmostEquals(0.25, sim_manhattan(self.movies['Marcel Caraciolo'], self.movies['Luciana Nunes']))
		
		
	def test_values_basic_rate_manhattan_similarity(self):
		vector =   [(self.movies['Marcel Caraciolo'][item],self.movies['Luciana Nunes'][item]) for item in self.movies['Marcel Caraciolo'] if item in self.movies['Luciana Nunes']]
		vector1 = [ v1 for v1,v2 in vector]
		vector2 = [ v2 for v1,v2 in vector]
		self.assertAlmostEquals(0.25, sim_manhattan(vector1,vector2))

	def test_dict_empty_rate_manhattan_similarity(self):
		self.assertAlmostEquals(0.0, sim_manhattan(self.movies['Marcel Caraciolo'], self.movies['Maria Gabriela']))

	def test_values_empty_rate_manhattan_similarity(self):
		self.assertAlmostEquals(0.0, sim_manhattan([],[]))


def suite():
	suite = unittest.TestSuite()
	suite.addTests(unittest.makeSuite(SimilarityTest))
	
	return suite

if __name__ == '__main__':
	unittest.main()



