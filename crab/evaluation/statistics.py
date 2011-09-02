#-*- coding:utf-8 -*-


#========================================================================
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#========================================================================
"""
:mod:`statistics` -- the statistics module
================================================================

    This module contains basic implementations that encapsulate
    retrieval-related statistics about the quality of the recommender's
    recommendations.
"""
from random import random
from math import sqrt, log
from interfaces import RecommenderEvaluator
from models.datamodel import DictDataModel
from recommender.recommender import SlopeOneRecommender
from numpy import std, array, mean


class AverageAbsoluteDifferenceRecommenderEvaluator(RecommenderEvaluator):
    '''
    A Recommender Evaluator which computes the average absolute difference
    between predicted and actual ratings for users.
    '''

    def evaluate(self, recommender, dataModel, trainingPercentage,
            evaluationPercentage):
        if trainingPercentage > 1.0 or trainingPercentage < 0.0:
            raise Exception('Training Percentage is above/under the limit.')

        if evaluationPercentage > 1.0 or evaluationPercentage < 0.0:
            raise Exception('Evaluation Percentage is above/under the limit.')
        # numUsers = dataModel.NumUsers()
        trainingUsers = {}
        testUserPrefs = {}
        self.total = 0
        self.diffs = 0.0

        for userID in dataModel.UserIDs():
            if random() < evaluationPercentage:
                self.processOneUser(trainingPercentage, trainingUsers,
                        testUserPrefs, userID, dataModel)

        trainingModel = DictDataModel(trainingUsers)

        recommender.model = trainingModel

        if isinstance(recommender, SlopeOneRecommender):
            recommender.reset()

        result = self.getEvaluation(testUserPrefs, recommender)

        return result

    def processOneUser(self, trainingPercentage, trainingUsers, testUserPrefs,
            userID, dataModel):
        trainingPrefs = []
        testPrefs = []
        prefs = dataModel.PreferencesFromUser(userID)
        for pref in prefs:
            if random() < trainingPercentage:
                trainingPrefs.append(pref)
            else:
                testPrefs.append(pref)

        if trainingPrefs:
            trainingUsers[userID] = dict(trainingPrefs)
        if testPrefs:
            testUserPrefs[userID] = dict(testPrefs)

    def getEvaluation(self, testUserPrefs, recommender):
        for userID, prefs in testUserPrefs.iteritems():
            estimatedPreference = None
            for pref in prefs:
                try:
                    estimatedPreference = recommender.estimatePreference(
                            userID=userID, itemID=pref,
                            similarity=recommender.similarity)
                except:
                    # It is possible that an item exists in the test data but
                    # not training data in which case an exception will be
                    # throw. Just ignore it and move on.
                    pass
                if estimatedPreference is not None:
                    estimatedPreference = \
                            self.capEstimatePreference(estimatedPreference)
                    self.processOneEstimate(estimatedPreference, prefs[pref])

        return self.diffs / float(self.total)

    def processOneEstimate(self, estimatedPref, realPref):
        self.diffs += abs(realPref - estimatedPref)
        self.total += 1

    def capEstimatePreference(self, estimate):
        if estimate > self.maxPreference:
            return self.maxPreference
        elif estimate < self.minPreference:
            return self.minPreference
        else:
            return estimate


class RMSRecommenderEvaluator(AverageAbsoluteDifferenceRecommenderEvaluator):
    '''
    A Recommender Evaluator which computes the root mean squared difference
    between predicted and actual ratings for users. This is the square root of
    the average of this difference, squared.
    '''

    def processOneEstimate(self, estimatedPref, realPref):
        diff = realPref - estimatedPref
        self.diffs += (diff * diff)
        self.total += 1

    def getEvaluation(self, testUserPrefs, recommender):
        for userID, prefs in testUserPrefs.iteritems():
            estimatedPreference = None
            for pref in prefs:
                try:
                    estimatedPreference = \
                            recommender.estimatePreference(userID=userID,
                                    itemID=pref,
                                    similarity=recommender.similarity)
                except:
                    # It is possible that an item exists in the test data but
                    # not training data in which case an exception will be
                    # throw. Just ignore it and move on.
                    pass
                if estimatedPreference is not None:
                    estimatedPreference = \
                            self.capEstimatePreference(estimatedPreference)
                    self.processOneEstimate(estimatedPreference, prefs[pref])

        return sqrt(self.diffs / float(self.total))


class IRStatsRecommenderEvaluator(RecommenderEvaluator):
    """
    For each user, this evaluator determine the top n preferences, then
    evaluate the IR statistics based on a DataModel that does not have these
    values. This number n is the 'at' value, as in 'precision at 5'.  For
    example this would mean precision evaluated by removing the top 5
    preferences for a user and then finding the percentage of those 5 items
    included in the top 5 recommendations for that user.
    """

    def evaluate(self, recommender, dataModel, at, evaluationPercentage,
            relevanceThreshold=None):
        if evaluationPercentage > 1.0 or evaluationPercentage < 0.0:
            raise Exception('Evaluation Percentage is above/under the limit.')
        if at < 1:
            raise Exception('at must be at leaste 1.')

        irStats = {'precision': None, 'recall': None, 'fallOut': None,
                   'nDCG': None}
        irFreqs = {'precision': 0, 'recall': 0, 'fallOut': 0, 'nDCG': 0}

        nItems = dataModel.NumItems()

        for userID in dataModel.UserIDs():
            if random() < evaluationPercentage:
                prefs = dataModel.PreferencesFromUser(userID)
                if len(prefs) < 2 * at:
                    # Really not enough prefs to meaningfully evaluate the user
                    continue

                relevantItemIDs = []

                # List some most-preferred items that would count as most
                # relevant results
                relevanceThreshold = relevanceThreshold if relevanceThreshold \
                                        else self.computeThreshold(prefs)

                prefs = sorted(prefs, key=lambda x: x[1], reverse=True)

                for index, pref in enumerate(prefs):
                    if index < at:
                        if pref[1] >= relevanceThreshold:
                            relevantItemIDs.append(pref[0])

                if len(relevantItemIDs) == 0:
                    continue

                trainingUsers = {}
                for otherUserID in dataModel.UserIDs():
                    self.processOtherUser(userID, relevantItemIDs,
                            trainingUsers, otherUserID, dataModel)

                trainingModel = DictDataModel(trainingUsers)

                recommender.model = trainingModel

                if isinstance(recommender, SlopeOneRecommender):
                    recommender.reset()

                try:
                    prefs = trainingModel.PreferencesFromUser(userID)
                    if not prefs:
                        continue
                except:
                    #Excluded all prefs for the user. move on.
                    continue

                recommendedItems = recommender.recommend(userID, at)
                intersectionSize = len([recommendedItem
                                        for recommendedItem in recommendedItems
                                        if recommendedItem in relevantItemIDs])

                print intersectionSize
                for key in irStats.keys():
                    irStats[key] = 0.0

                # Precision
                if len(recommendedItems) > 0:
                    irStats['precision'] += \
                            (intersectionSize / float(len(recommendedItems)))
                    irFreqs['precision'] += 1

                # Recall
                irStats['recall'] += \
                        (intersectionSize / float(len(relevantItemIDs)))
                irFreqs['recall'] += 1

                # Fall-Out
                if len(relevantItemIDs) < len(prefs):
                    irStats['fallOut'] += \
                            (len(recommendedItems) - intersectionSize) / \
                            float(nItems - len(relevantItemIDs))
                    irFreqs['fallOut'] += 1

                # nDCG. In computing, assume relevant IDs have relevance 1 and
                # others 0.
                cumulativeGain = 0.0
                idealizedGain = 0.0
                for index, recommendedItem in enumerate(recommendedItems):
                    discount = 1.0 if index == 0 \
                                else 1.0 / self.log2(index + 1)
                    if recommendedItem in relevantItemIDs:
                        cumulativeGain += discount
                    # Otherwise we are multiplying discount by relevance 0 so
                    # it does nothing.  Ideally results would be ordered with
                    # all relevant ones first, so this theoretical ideal list
                    # starts with number of relevant items equal to the total
                    # number of relevant items
                    if index < len(relevantItemIDs):
                        idealizedGain += discount
                irStats['nDCG'] += float(cumulativeGain) / idealizedGain \
                                    if idealizedGain else 0.0
                irFreqs['nDCG'] += 1

        for key in irFreqs:
            irStats[key] = irStats[key] / float(irFreqs[key]) \
                                if irFreqs[key] > 0 else None
        sum_score = irStats['precision'] + irStats['recall'] \
                if irStats['precision'] is not None and \
                        irStats['recall'] is not None \
                else None
        irStats['f1Score'] = None if not sum_score else \
                (2.0) * irStats['precision'] * irStats['recall'] / sum_score

        return irStats

    def processOtherUser(self, userID, relevantItemIDs, trainingUsers,
            otherUserID, dataModel):
        prefs = dataModel.PreferencesFromUser(otherUserID)

        if userID == otherUserID:
            prefsOtherUser = [pref for pref in prefs
                                if pref[0] not in relevantItemIDs]
            if prefsOtherUser:
                trainingUsers[otherUserID] = dict(prefsOtherUser)

        else:
            trainingUsers[otherUserID] = dict(prefs)

    def computeThreshold(self, prefs):
        if len(prefs) < 2:
            #Not enough data points: return a threshold that allows everything
            return - 10000000
        data = [pref[1] for pref in prefs]
        return mean(array(data)) + std(array(data))

    def log2(self, value):
        return log(value) / log(2.0)
