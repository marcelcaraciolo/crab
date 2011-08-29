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

#0.1 2010-11-09  Initial version.
"""
:mod:`topmatches` -- the topmatches  module
================================================================

This module contains functions that implements the find top N things logic.

"""

NO_IDS = []


def topUsers(thingID, allUserIDs, howMany, preferenceEstimator, similarity,
        rescorer=None, **extra):
    ''' Find Top N Users

    `thingID` ID of the user/item for which to find most similar users to find.

    `allUserIDs` the set of userIDs from the data model.

    `howMany` the number of most similar users to find.

    `preferenceEstimator` : a function for estimate the preference given a
    userID and otherUserID.

    `similarity` the similarity between users.

    `rescorer` a Scorer Class for rescore the preference for a thing (user or
    item).
    '''
    topNRecs = []

    extra.update({'rescorer': rescorer})

    for otherUserID in allUserIDs:
        preference = preferenceEstimator(thingID=thingID,
                similarity=similarity, otherUserID=otherUserID, **extra)

        if preference is None:
            continue

        rescoredPref = rescorer.rescore(thingID, preference) \
                        if rescorer else preference

        if rescoredPref is not None:
            topNRecs.append((otherUserID, rescoredPref))

    topNRecs = sorted(topNRecs, key=lambda item: -item[1])

    topNRecs = [item[0] for item in topNRecs]

    return topNRecs[0:howMany] if topNRecs and len(topNRecs) > howMany \
            else topNRecs if topNRecs else NO_IDS


def topItems(thingID, possibleItemIDs, howMany, preferenceEstimator,
        similarity, rescorer=None, **extra):
    '''
    Find Top N items

    `thingID` ID of the item or user  for which to find most similar items to
    find.

    `possibleItemIDs` the set of possible itemIDs from data model.

    `howMany` the number of most similar items to find.

    `preferenceEstimator` : a function for estimate the preference given an
    itemID and otherItemID.

    `similarity` the similarity between items.

    `rescorer` a Scorer Class for rescore the preference for a thing (user or
    item).
    '''
    topNRecs = []

    extra.update({'rescorer': rescorer})

    for otherItemID in possibleItemIDs:
        preference = preferenceEstimator(thingID=thingID,
                similarity=similarity, itemID=otherItemID, **extra)

        if preference is None:
            continue

        rescoredPref = rescorer.rescore(thingID, preference) \
                        if rescorer else preference

        if rescoredPref is not None:
            topNRecs.append((otherItemID, rescoredPref))

    topNRecs = sorted(topNRecs, key=lambda item: -item[1])

    topNRecs = [item[0] for item in topNRecs]

    return topNRecs[0:howMany] if topNRecs and len(topNRecs) > howMany \
            else topNRecs if topNRecs else []
