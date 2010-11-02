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


0.1 2010-11-01 Initial version.

'''

__author__ = 'marcel@orygens.com'

import unittest

from models.datamodel import *


class TestDictModel(unittest.TestCase):
	
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
		
	def test_create_DictModel(self):		
		model = DictDataModel(self.movies)
		self.assertEquals(self.movies,model.dataU)
		
	def test_UserIDs_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(['Leopoldo Pires', 'Lorena Abreu', 'Luciana Nunes', 'Marcel Caraciolo',
		 	'Maria Gabriela', 'Penny Frewman', 'Sheldom', 'Steve Gates'] ,model.UserIDs())
	
	def test_ItemIDs_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(['Just My Luck', 'Lady in the Water', 'Snakes on a Plane', 
		   'Superman Returns', 'The Night Listener', 'You, Me and Dupree'],model.ItemIDs())
		
	def test_PreferencesFromUser_Existing_UserDictModel(self):
		model = DictDataModel(self.movies)
		#Ordered by ItemID
		self.assertEquals([('Just My Luck', 3.0), ('Snakes on a Plane', 3.5), ('Superman Returns', 4.0), 
		('The Night Listener', 4.5), ('You, Me and Dupree', 2.5)],model.PreferencesFromUser('Lorena Abreu'))
		#Ordered by Rate (Reverse)
		self.assertEquals([('The Night Listener', 4.5), ('Superman Returns', 4.0), ('Snakes on a Plane', 3.5), 
		('Just My Luck', 3.0), ('You, Me and Dupree', 2.5)],model.PreferencesFromUser('Lorena Abreu',orderByID=False))
		

	def test_PreferencesFromUser_Existing_User_No_PreferencesDictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals([],model.PreferencesFromUser('Maria Gabriela'))

	def test_PreferencesFromUser_Non_Existing_User_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertRaises(ValueError, model.PreferencesFromUser, 'Flavia')    
	
	def test_ItemIDsFromUser_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(['Just My Luck', 'Lady in the Water', 'Snakes on a Plane', 
			'Superman Returns', 'The Night Listener', 'You, Me and Dupree'] , model.ItemIDsFromUser('Marcel Caraciolo'))
	
	def test_PreferencesForItem_Existing_Item_DictModel(self):
		model = DictDataModel(self.movies)
		#Ordered by ItemID
		self.assertEquals([('Leopoldo Pires', 3.5), ('Lorena Abreu', 4.0), ('Luciana Nunes', 5.0), ('Marcel Caraciolo', 3.5), 
		('Penny Frewman', 4.0), ('Sheldom', 5.0), ('Steve Gates', 3.0)],model.PreferencesForItem('Superman Returns'))
		#Ordered by Rate (Reverse)
		self.assertEquals([('Luciana Nunes', 5.0), ('Sheldom', 5.0), ('Penny Frewman', 4.0), ('Lorena Abreu', 4.0), 
		('Leopoldo Pires', 3.5), ('Marcel Caraciolo', 3.5), ('Steve Gates', 3.0)], model.PreferencesForItem('Superman Returns',orderByID=False))

	def test_PreferencesForItem_Existing_Item_No_PreferencesDictModel(self):
		model = DictDataModel(self.movies)
		#BUG ? If there is an item without rating in the model, it must return [] or raise an Exception ?
		self.assertRaises(ValueError, model.PreferencesFromUser, 'Night Listener')	    

	def test_PreferencesForItem_Non_Existing_Item_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertRaises(ValueError, model.PreferencesFromUser, 'Back to the Future')	    
		
	def test_PreferenceValue_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(3.5 , model.PreferenceValue('Marcel Caraciolo','Superman Returns'))
	
	def test_NumUsers_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(8,model.NumUsers())
		
	def test_NumItems_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(6,model.NumItems())	
		
	def test_NumUsersWithPreferenceFor_Invalid_User_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertRaises(ValueError, model.NumUsersWithPreferenceFor)	
		self.assertRaises(ValueError, model.NumUsersWithPreferenceFor,'SuperMan Returns','Just My Luck', 'Lady in The Water')	
		self.assertRaises(ValueError, model.NumUsersWithPreferenceFor,'SuperMan Returns','Back to the future')	
			
	def test_NumUsersWithPreferenceFor_One_User_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(7, model.NumUsersWithPreferenceFor('Superman Returns'))    

	def test_NumUsersWithPreferenceFor_Two_Users_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(4, model.NumUsersWithPreferenceFor('Superman Returns','Just My Luck'))
		
	def test_hasPreferenceValues_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(True, model.hasPreferenceValues())
	
	def test_MaxPreference_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(5.0, model.MaxPreference())
	
	def test_MinPreference_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals(1.0, model.MinPreference())
	
	def test_get_item_DictModel(self):
		model = DictDataModel(self.movies)
		self.assertEquals([('Just My Luck', 3.0), ('Lady in the Water', 2.5), ('Snakes on a Plane', 3.5), 
		('Superman Returns', 3.5), ('The Night Listener', 3.0), ('You, Me and Dupree', 2.5)] , model['Marcel Caraciolo'])	
		
	def test_iter_DictModel(self):
		model = DictDataModel(self.movies)
		elements =  [ pref  for pref in model ]
		self.assertEquals(('Leopoldo Pires', [('Lady in the Water', 2.5), ('Snakes on a Plane', 3.0), 
		('Superman Returns', 3.5), ('The Night Listener', 4.0)]), elements[0])
			
def suite():
	suite = unittest.TestSuite()
	suite.addTests(unittest.makeSuite(TestDictModel))
	
	return suite

if __name__ == '__main__':
	unittest.main()