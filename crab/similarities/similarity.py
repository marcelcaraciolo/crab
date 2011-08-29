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

# REVISION HISTORY

#0.1 2010-10-31  Initial version.
"""
:mod:`similarity_distance` -- the similarity distances table
================================================================

This module contains functions and classes for computing similarities across a
collection of vectors.

"""


from interfaces import Similarity


class UserSimilarity(Similarity):
    '''
    Returns the degree of similarity, of two users, based on the their
    preferences. Implementations of this class define a notion of similarity
    between two users.  Implementations should  return values in the range 0.0
    to 1.0, with 1.0 representing perfect similarity.
    '''

    def __init__(self, model, distance, numBest=None):
        Similarity.__init__(self, model, distance, numBest)

    def getSimilarity(self, vec1, vec2):
        usr1Prefs = dict(self.model.PreferencesFromUser(vec1))
        usr2Prefs = dict(self.model.PreferencesFromUser(vec2))

        # Evaluate the similarity between the two users vectors.
        return self.distance(usr1Prefs, usr2Prefs)

    def getSimilarities(self, vec):
        return [(other, self.getSimilarity(vec, other))
                for other, v in self.model]

    def __iter__(self):
        """
        For each object in model, compute the similarity function against all
        other objects and yield the result.  """
        for num, user, vec in enumerate(self.model):
            yield self[user]


class ItemSimilarity(Similarity):
    '''
    Returns the degree of similarity, of two items, based on its preferences by
    the users.  Implementations of this class define a notion of similarity
    between two items.  Implementations should  return values in the range 0.0
    to 1.0, with 1.0 representing perfect similarity.
    '''
    def __init__(self, model, distance, numBest=None):
        Similarity.__init__(self, model, distance, numBest)

    def getSimilarity(self, vec1, vec2):
        item1Prefs = dict(self.model.PreferencesForItem(vec1))
        item2Prefs = dict(self.model.PreferencesForItem(vec2))

        # Evaluate the similarity between the two users vectors.
        return self.distance(item1Prefs, item2Prefs)

    def getSimilarities(self, vec):
        return [(other, self.getSimilarity(vec, other))
                for other in self.model.ItemIDs()]

    def __iter__(self):
        """
        For each object in model, compute the similarity function against all
        other objects and yield the result.
        """
        for num, item in enumerate(self.model.ItemIDs()):
            yield item, self.PreferencesForItem(userID)
