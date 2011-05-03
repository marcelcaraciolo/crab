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
from math import sqrt

sys.path.append('/Users/marcelcaraciolo/Desktop/crab/crab/crab')


from models.datamodel import *
from recommender.topmatches import *
from recommender.recommender import UserRecommender, ItemRecommender, SlopeOneRecommender
from recommender.utils import DiffStorage
from similarities.similarity import UserSimilarity, ItemSimilarity
from similarities.similarity_distance import *
from scoring.scorer import TanHScorer, NaiveScorer
from neighborhood.neighborhood import NearestNUserNeighborhood
from neighborhood.itemstrategies import  PreferredItemsNeighborhoodStrategy
from evaluation.statistics import *



class TestAverageAbsoluteDistanceRecommenderEvaluator(unittest.TestCase):
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
        self.similarity_item = ItemSimilarity(self.model,sim_euclidian)
        self.strategy = PreferredItemsNeighborhoodStrategy()

    def test_Create_AvgAbsDistanceRecSys(self):
        evaluator = AverageAbsoluteDifferenceRecommenderEvaluator()
        self.assertEquals(evaluator.minPreference,0.0)
        self.assertEquals(evaluator.maxPreference,5.0)
  
    def test_evaluate_AvgAbsDistanceRecSys(self):
        evaluator = AverageAbsoluteDifferenceRecommenderEvaluator()
        
        recommender  = UserRecommender(self.model,self.similarity,self.neighbor,True)
        evaluationPercentage = 1.0
        trainingPercentage = 0.7
    
        numUsers = self.model.NumUsers()
        trainingUsers = {}
        testUserPrefs = {}
        self.total = 0
        self.diffs = 0.0

        for userID in self.model.UserIDs():
            if random() < evaluationPercentage:
                evaluator.processOneUser(trainingPercentage,trainingUsers,testUserPrefs,userID,self.model)        

        total_training =  sum([ len([pref  for pref in prefs]) for user,prefs in trainingUsers.iteritems()])
        total_testing =  sum([ len([pref  for pref in prefs]) for user,prefs in testUserPrefs.iteritems()])
        
        #self.assertAlmostEquals(total_training/float(total_training+total_testing), 0.7)
        #self.assertAlmostEquals(total_testing/float(total_training+total_testing), 0.3)
        
        
        trainingModel = DictDataModel(trainingUsers)
        
        self.assertEquals(sorted(trainingModel.UserIDs()), sorted([user for user in trainingUsers]))

        recommender.model = trainingModel

        self.assertEquals(recommender.model,trainingModel)
        
        for userID,prefs in testUserPrefs.iteritems():
            estimatedPreference = None
            for pref in prefs:
                try:
                    estimatedPreference = recommender.estimatePreference(userID=userID,similarity=self.similarity,itemID=pref)
                except:
                    pass
                if estimatedPreference is not None:
                    estimatedPreference = evaluator.capEstimatePreference(estimatedPreference)
                    self.assert_(estimatedPreference <= evaluator.maxPreference and estimatedPreference >= evaluator.minPreference)
                    self.diffs +=  abs(prefs[pref] - estimatedPreference)
                    self.total += 1
        
  
        result = self.diffs / float(self.total)


    def test_User_AvgDistanceRecSys(self):
        evaluator = AverageAbsoluteDifferenceRecommenderEvaluator()
        recommender  = UserRecommender(self.model,self.similarity,self.neighbor,True)
        result = evaluator.evaluate(recommender,self.model,0.7,1.0)
        #print result
    
    def test_Item_AvgDistanceRecSys(self):
        evaluator = AverageAbsoluteDifferenceRecommenderEvaluator()
        recommender = ItemRecommender(self.model,self.similarity_item,self.strategy,False)
        result = evaluator.evaluate(recommender,self.model,0.7,1.0)
        #print result

    def test_Slope_AvgDistanceRecSys(self):
        evaluator = AverageAbsoluteDifferenceRecommenderEvaluator()
        recommender = SlopeOneRecommender(self.model,True,False,False)
        result = evaluator.evaluate(recommender,self.model,0.7,1.0)
        #print result

    def test_limits_AvgDistanceRecSys(self):
        evaluator = AverageAbsoluteDifferenceRecommenderEvaluator()
        recommender = SlopeOneRecommender(self.model,True,False,False)
        self.assertRaises(Exception,evaluator.evaluate,recommender,self.model,1.3,-0.3)


class TestRMSRecommenderEvaluator(unittest.TestCase):
    
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
        self.similarity_item = ItemSimilarity(self.model,sim_euclidian)
        self.strategy = PreferredItemsNeighborhoodStrategy()

    def test_Create_RMSRecommenderEvaluator(self):
        evaluator = RMSRecommenderEvaluator()
        self.assertEquals(evaluator.minPreference,0.0)
        self.assertEquals(evaluator.maxPreference,5.0)
  
    def test_evaluate_RMSRecommenderEvaluator(self):
        evaluator = RMSRecommenderEvaluator()
        
        recommender  = UserRecommender(self.model,self.similarity,self.neighbor,True)
        evaluationPercentage = 1.0
        trainingPercentage = 0.7
    
        numUsers = self.model.NumUsers()
        trainingUsers = {}
        testUserPrefs = {}
        self.total = 0
        self.diffs = 0.0

        for userID in self.model.UserIDs():
            if random() < evaluationPercentage:
                evaluator.processOneUser(trainingPercentage,trainingUsers,testUserPrefs,userID,self.model)        

        total_training =  sum([ len([pref  for pref in prefs]) for user,prefs in trainingUsers.iteritems()])
        total_testing =  sum([ len([pref  for pref in prefs]) for user,prefs in testUserPrefs.iteritems()])
        
        #self.assertAlmostEquals(total_training/float(total_training+total_testing), 0.7)
        #self.assertAlmostEquals(total_testing/float(total_training+total_testing), 0.3)
        
        
        trainingModel = DictDataModel(trainingUsers)
        
        self.assertEquals(sorted(trainingModel.UserIDs()), sorted([user for user in trainingUsers]))

        recommender.model = trainingModel

        self.assertEquals(recommender.model,trainingModel)
        
        for userID,prefs in testUserPrefs.iteritems():
            estimatedPreference = None
            for pref in prefs:
                try:
                    estimatedPreference = recommender.estimatePreference(userID=userID,similarity=self.similarity,itemID=pref)
                except:
                    pass
                if estimatedPreference is not None:
                    estimatedPreference = evaluator.capEstimatePreference(estimatedPreference)
                    self.assert_(estimatedPreference <= evaluator.maxPreference and estimatedPreference >= evaluator.minPreference)
                    diff =  prefs[pref] - estimatedPreference
                    self.diffs+= (diff * diff)
                    self.total += 1
        
  
        result = sqrt(self.diffs / float(self.total))


    def test_User_RMSRecommenderEvaluator(self):
        evaluator = RMSRecommenderEvaluator()
        recommender  = UserRecommender(self.model,self.similarity,self.neighbor,True)
        result = evaluator.evaluate(recommender,self.model,0.7,1.0)
        #print result
    
    def test_Item_RMSRecommenderEvaluator(self):
        evaluator = RMSRecommenderEvaluator()
        recommender = ItemRecommender(self.model,self.similarity_item,self.strategy,False)
        result = evaluator.evaluate(recommender,self.model,0.7,1.0)
        #print result

    def test_Slope_RMSRecommenderEvaluator(self):
        evaluator = RMSRecommenderEvaluator()
        recommender = SlopeOneRecommender(self.model,True,False,False)
        result = evaluator.evaluate(recommender,self.model,0.7,1.0)
        #print result

    def test_limits_RMSRecommenderEvaluator(self):
        evaluator = RMSRecommenderEvaluator()
        recommender = SlopeOneRecommender(self.model,True,False,False)
        self.assertRaises(Exception,evaluator.evaluate,recommender,self.model,1.3,-0.3)



class TestIRStatsRecommenderEvaluator(unittest.TestCase):

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
        self.similarity_item = ItemSimilarity(self.model,sim_euclidian)
        self.strategy = PreferredItemsNeighborhoodStrategy()

    def test_Create_IRStatsRecommenderEvaluator(self):
        evaluator = IRStatsRecommenderEvaluator()
        self.assertEquals(evaluator.minPreference,0.0)
        self.assertEquals(evaluator.maxPreference,5.0)

    def test_evaluate_at_not_enough_IRStatsRecommenderEvaluator(self):
        evaluator = IRStatsRecommenderEvaluator()
        recommender  = UserRecommender(self.model,self.similarity,self.neighbor,True)
        result = evaluator.evaluate(recommender,self.model,4,1.0)
        self.assertEquals(result,{'nDCG': 0.0, 'recall': 0.0, 'precision': 0.0, 'fallOut': 0.0})

    def test_User_IRStatsRecommenderEvaluator(self):
        evaluator = IRStatsRecommenderEvaluator()
        recommender  = UserRecommender(self.model,self.similarity,self.neighbor,True)
        result = evaluator.evaluate(recommender,self.model,2,1.0)
        #print result

    def test_Item_IRStatsRecommenderEvaluator(self):
        evaluator = IRStatsRecommenderEvaluator()
        recommender = ItemRecommender(self.model,self.similarity_item,self.strategy,False)
        result = evaluator.evaluate(recommender,self.model,2,1.0)
        #print result

    def test_Slope_IRStatsRecommenderEvaluator(self):
        evaluator = IRStatsRecommenderEvaluator()
        recommender = SlopeOneRecommender(self.model,True,False,False)
        result = evaluator.evaluate(recommender,self.model,2,1.0)
        #print result


    def test_evaluate_IRStatsRecommenderEvaluator(self):
        evaluator = IRStatsRecommenderEvaluator()

        recommender  = UserRecommender(self.model,self.similarity,self.neighbor,True)
        evaluationPercentage = 1.0
        relevanceThreshold = None
        at = 2
              
        irStats = {'precision': 0.0, 'recall': 0.0, 'fallOut': 0.0, 'nDCG': 0.0}
        irFreqs = {'precision': 0, 'recall': 0, 'fallOut': 0, 'nDCG': 0}
        
        nItems = self.model.NumItems()
        self.assertEquals(nItems,6)


        for userID in self.model.UserIDs():
            if random() < evaluationPercentage:
                prefs = self.model.PreferencesFromUser(userID)
                if len(prefs)  < 2 * at:
                    #Really not enough prefs to meaningfully evaluate the user
                    self.assert_(userID in ['Leopoldo Pires', 'Penny Frewman', 'Maria Gabriela'])
                    continue 
                
                relevantItemIDs = []
                
                #List some most-preferred items that would count as most relevant results
                relevanceThreshold =  relevanceThreshold if relevanceThreshold else  evaluator.computeThreshold(prefs)
                
                prefs = sorted(prefs,key=lambda x: x[1], reverse=True)
                
                self.assertEquals(max([pref[1] for pref in prefs]), prefs[0][1])
                
                for index,pref in enumerate(prefs):
                    if index < at:
                        if pref[1] >= relevanceThreshold:
                            relevantItemIDs.append(pref[0])
                
                self.assertEquals(relevantItemIDs, [ p[0] for p in sorted([ pref for pref in prefs if pref[1] >= relevanceThreshold],key=lambda x: x[1], reverse=True)[:at] ] )    
                

                if len(relevantItemIDs) == 0:
                    continue
                
                trainingUsers = {}
                for otherUserID in self.model.UserIDs():
                    evaluator.processOtherUser(userID,relevantItemIDs,trainingUsers,otherUserID,self.model)
                
                

                trainingModel = DictDataModel(trainingUsers)
                
                recommender.model = trainingModel
                
                try:
                    prefs = trainingModel.PreferencesFromUser(userID)
                    if not prefs:
                        continue
                except:
                    #Excluded all prefs for the user. move on.
                    continue
                
                recommendedItems = recommender.recommend(userID,at)


                self.assert_(len(recommendedItems)<= 2)

                intersectionSize = len([ recommendedItem  for recommendedItem in recommendedItems if recommendedItem in relevantItemIDs])
                
                
                #Precision
                if len(recommendedItems) > 0:
                    irStats['precision']+= (intersectionSize / float(len(recommendedItems)))
                    irFreqs['precision']+=1
                    
                #Recall
                irStats['recall'] += (intersectionSize/ float(len(relevantItemIDs)))
                irFreqs['recall']+=1
                
                #Fall-Out
                if len(relevantItemIDs) < len(prefs):
                    irStats['fallOut'] +=   (len(recommendedItems)  - intersectionSize) / float( nItems - len(relevantItemIDs))
                    irFreqs['fallOut'] +=1

                    
                #nDCG
                #In computing , assume relevant IDs have relevance 1 and others 0.
                cumulativeGain = 0.0
                idealizedGain = 0.0
                for index,recommendedItem in enumerate(recommendedItems):
                    discount =  1.0 if index == 0 else 1.0/ evaluator.log2(index+1)
                    if recommendedItem in relevantItemIDs:
                        cumulativeGain+=discount
                    #Otherwise we are multiplying discount by relevance 0 so it does nothing.
                    #Ideally results would be ordered with all relevant ones first, so this theoretical
                    #ideal list starts with number of relevant items equal to the total number of relevant items
                    if index < len(relevantItemIDs):
                        idealizedGain+= discount
                irStats['nDCG'] +=  float(cumulativeGain) / idealizedGain
                irFreqs['nDCG'] +=1
        
        for key in irFreqs:
            irStats[key] = irStats[key] / float(irFreqs[key])

        #print irStats



    def test_limits_RMSRecommenderEvaluator(self):
        evaluator = RMSRecommenderEvaluator()
        recommender = SlopeOneRecommender(self.model,True,False,False)
        self.assertRaises(Exception,evaluator.evaluate,recommender,self.model,0,-0.3)


def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(TestAverageAbsoluteDistanceRecommenderEvaluator))
    suite.addTests(unittest.makeSuite(TestRMSRecommenderEvaluator))
    suite.addTests(unittest.makeSuite(TestIRStatsRecommenderEvaluator))
    return suite

if __name__ == '__main__':
    unittest.main()