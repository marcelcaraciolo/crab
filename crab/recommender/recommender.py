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
:mod:`recommender` -- the recommender modules
================================================================

This module contains functions and classes to produce recommendations.

"""

from interfaces import UserBasedRecommender, ItemBasedRecommender, Recommender
from topmatches import topUsers, topItems
from utils import DiffStorage


class UserRecommender(UserBasedRecommender):
    '''
    A simple Recommender which uses a given dataModel and NeighborHood
    to produce recommendations.

    '''
    def __init__(self, model, similarity, neighborhood, capper=True):
        ''' UserBasedRecommender Class Constructor

            `model` is the data source model

            `neighborhood` is the neighborhood strategy for computing the most
            similar users.

            `similarity` is the class used for computing the similarities over
            the users.

            `capper` a normalizer for Maximum/Minimum Preferences range.

        '''
        UserBasedRecommender.__init__(self, model)
        self.neighborhood = neighborhood
        self.similarity = similarity
        self.capper = capper

    def recommend(self, userID, howMany, rescorer=None):
        nearestN = self.neighborhood.userNeighborhood(userID, rescorer)

        if not nearestN:
            return []

        allItemIDs = self.allOtherItems(userID, nearestN)

        rec_items = topItems(userID, allItemIDs, howMany,
                self.estimatePreference, self.similarity, rescorer)

        return rec_items

    def estimatePreference(self, **args):
        userID = args.get('thingID', None) or args.get('userID', None)
        itemID = args.get('itemID', None)
        similarity = args.get('similarity', self.similarity)
        nHood = args.get('neighborhood', None)
        rescorer = args.get('rescorer', None)

        if not nHood:
            pref = self.model.PreferenceValue(userID, itemID)
            if pref is not None:
                return pref

            nHood = self.neighborhood.userNeighborhood(userID=userID,
                    rescorer=rescorer)

        if not nHood:
            return None

        preference = 0.0
        totalSimilarity = 0.0
        count = 0
        for usrID in nHood:
            if usrID != userID:
                pref = self.model.PreferenceValue(usrID, itemID)
                if pref is not None:
                    sim = similarity.getSimilarity(usrID, userID)
                    if sim is not None:
                        preference += sim * pref
                        totalSimilarity += sim
                        count += 1

        # Throw out the estimate if it was based on no data points, of course,
        # but also if based on just one. This is a bit of a band-aid on the
        # 'stock' item-based algorithm for the moment.  The reason is that in
        # this case the estimate is, simply, the user's rating for one item
        # that happened to have a defined similarity. The similarity score
        # doesn't matter, and that seems like a bad situation.
        if count <= 1 or totalSimilarity == 0.0:
            return None

        estimated = float(preference) / totalSimilarity

        if self.capper:
            # TODO: Maybe put this in a separated function.
            max = self.model.MaxPreference()
            min = self.model.MinPreference()
            estimated = max if estimated > max else \
                    min if estimated < min else estimated

        return estimated

    def mostSimilarUserIDs(self, userID, howMany, rescorer=None):
        return topUsers(userID, self.model.UserIDs(), howMany,
                self.neighborhood.estimatePreference, self.similarity,
                rescorer)

    def allOtherItems(self, userID, neighborhood):
        possibleItemIDs = []
        for usrID in neighborhood:
            possibleItemIDs.extend(self.model.ItemIDsFromUser(usrID))

        itemIds = self.model.ItemIDsFromUser(userID)
        possibleItemIDs = list(set(possibleItemIDs))

        return [itemID for itemID in possibleItemIDs if itemID not in itemIds]


class SlopeOneRecommender(Recommender):
    """
    A basic "slope one" recommender. This is a recommender specially suitable
    when user preferencces are updating frequently as it can incorporate this
    information without expensive recomputation.  It can also be used as a
    weighted slope one recommender.
    """
    def __init__(self, model, weighted=True, stdDevWeighted=True,
            toPrune=True):
        '''
        SlopeOneRecommender Class Constructor

       `model` is the data source model

       `weighted` is a flag that if it is True, it act as a weighted slope one
       recommender.

       `stdDevWeighted` is a flag that if it is True, use standard deviation
       weighting of diffs

       `toPrune` is a flag that if it is True, it will prune the irrelevant
       diffs, represented by one data point.
        '''
        Recommender.__init__(self, model)
        self.weighted = weighted
        self.stdDevWeighted = stdDevWeighted
        self.storage = DiffStorage(self.model, self.stdDevWeighted, toPrune)

    def recommend(self, userID, howMany, rescore=None):
        possibleItemIDs = self.possibleItemIDs(userID)
        rec_items = topItems(userID, possibleItemIDs, howMany,
                self.estimatePreference, None, None)
        return rec_items

    def possibleItemIDs(self, userID):
        preferences = self.model.ItemIDsFromUser(userID)
        recommendableItems = self.storage.recommendableItems()
        return [itemID for itemID in recommendableItems
                if itemID not in preferences]

    def estimatePreference(self, **args):
        userID = args.get('thingID', None) or args.get('userID', None)
        itemID = args.get('itemID', None)
        #similarity = args.get('similarity', None)
        nHood = args.get('neighborhood', None)
        #rescorer = args.get('rescorer', None)

        if not nHood:
            pref = self.model.PreferenceValue(userID, itemID)
            if pref is not None:
                return pref

        count = 0
        totalPreference = 0.0
        prefs = self.model.PreferencesFromUser(userID)
        averages = self.storage.diffsAverage(userID, itemID, prefs)
        for i in range(len(prefs)):
            averageDiffValue = averages[i]
            if averageDiffValue is not None:
                if self.weighted:
                    weight = self.storage.count(itemID, prefs[i][0])
                    if self.stdDevWeighted:
                        stdev = self.storage.standardDeviation(
                                itemID, prefs[i][0])
                        if stdev is not None:
                            weight /= 1.0 + stdev
                            # If stdev is None, it is because count is 1. Since
                            # we are weighting by count the weight is already
                            # low. So we assume stdev is 0.0.
                    totalPreference += \
                            weight * (prefs[i][1] + averageDiffValue)
                    count += weight
                else:
                    totalPreference += prefs[i][1] + averageDiffValue
                    count += 1

        if count <= 0:
            return None
            # BUGFIX
            # itemAverage = self.storage.AverageItemPref(itemID)
            # if itemAverage is not None:
            #    itemAverage = itemAverage.Average()
            #    return itemAverage
            # else:
            #    return None
        else:
            return totalPreference / float(count)


class ItemRecommender(ItemBasedRecommender):
    '''
    A simple recommender which uses a given DataModel and ItemSimilarity to
    produce recommendations. This class represents a support for item based
    recommenders.
    '''
    def __init__(self, model, similarity, itemStrategy, capper=True):
        '''
        UserBasedRecommender Class Constructor

        `model` is the data source model

        `itemStrategy` is the candidate item strategy for computing the most
        similar items.

        `similarity` is the class used for computing the similarities over
        the items.

        `capper` a normalizer for Maximum/Minimum Preferences range.
        '''
        ItemBasedRecommender.__init__(self, model)
        self.strategy = itemStrategy
        self.similarity = similarity
        self.capper = capper

    def recommend(self, userID, howMany, rescorer=None):
        if self.numPreferences(userID) == 0:
            return []

        possibleItemIDs = self.allOtherItems(userID)

        rec_items = topItems(userID, possibleItemIDs, howMany,
                self.estimatePreference, self.similarity, rescorer)

        return rec_items

    def allOtherItems(self, userID):
        return self.strategy.candidateItems(userID, self.model)

    def estimateMultiItemsPreference(self, **args):
        toItemIDs = args.get('thingID', None)
        itemID = args.get('itemID', None)
        similarity = args.get('similarity', self.similarity)
        rescorer = args.get('rescorer', None)

        sum = 0.0
        total = 0

        for toItemID in toItemIDs:
            preference = similarity.getSimilarity(itemID, toItemID)

            rescoredPref = rescorer.rescore((itemID, toItemID), preference) \
                                if rescorer else preference

            sum += rescoredPref
            total += 1

        return sum / total

    def numPreferences(self, userID):
        return len(self.model.PreferencesFromUser(userID))

    def estimatePreference(self, **args):
        userID = args.get('thingID', None) or args.get('userID', None)
        itemID = args.get('itemID', None)
        similarity = args.get('similarity', self.similarity)

        preference = self.model.PreferenceValue(userID, itemID)

        if preference is not None:
            return preference

        totalSimilarity = 0.0
        preference = 0.0
        count = 0

        prefs = self.model.PreferencesFromUser(userID)
        for toItemID, pref in prefs:
            if toItemID != itemID:
                sim = similarity.getSimilarity(itemID, toItemID)
                if sim is not None:
                    preference += sim * pref
                    totalSimilarity += sim
                    count += 1

        # Throw out the estimate if it was based on no data points, of course,
        # but also if based on just one. This is a bit of a band-aid on the
        # 'stock' item-based algorithm for the moment.  The reason is that in
        # this case the estimate is, simply, the user's rating for one item
        # that happened to have a defined similarity. The similarity score
        # doesn't matter, and that seems like a bad situation.
        if count <= 1 or totalSimilarity == 0.0:
            return None

        estimated = float(preference) / totalSimilarity

        if self.capper:
            # TODO: Maybe put this in a separated function.
            max = self.model.MaxPreference()
            min = self.model.MinPreference()
            estimated = max if estimated > max else \
                        min if estimated < min else estimated

        return estimated

    def estimateBecausePreference(self, **args):
        userID = args.get('thingID') or args.get('userID')
        itemID = args.get('itemID')
        similarity = args.get('similarity', self.similarity)
        recommendedItemID = args.get('recommendedItemID')

        pref = self.model.PreferenceValue(userID, itemID)

        if pref is None:
            return None

        simValue = similarity.getSimilarity(itemID, recommendedItemID)

        return (1.0 + simValue) * pref

    def recommendedBecause(self, userID, itemID, howMany, rescorer=None):
        prefs = self.model.PreferencesFromUser(userID)
        allUserItems = [otherItemID for otherItemID, pref in prefs
                        if otherItemID != itemID]
        allUserItems = list(set(allUserItems))

        return topItems(thingID=userID, possibleItemIDs=allUserItems,
                howMany=howMany,
                preferenceEstimator=self.estimateBecausePreference,
                similarity=self.similarity, rescorer=None,
                recommendedItemID=itemID)

    def mostSimilarItems(self, itemIDs, howMany, rescorer=None):
        possibleItemIDs = []
        for itemID in itemIDs:
            prefs = self.model.PreferencesForItem(itemID)
            for userID, pref in prefs:
                possibleItemIDs.extend(self.model.ItemIDsFromUser(userID))

        possibleItemIDs = list(set(possibleItemIDs))

        pItems = [itemID for itemID in possibleItemIDs
                  if itemID not in itemIDs]

        return topItems(itemIDs, pItems, howMany,
                self.estimateMultiItemsPreference, self.similarity, rescorer)
