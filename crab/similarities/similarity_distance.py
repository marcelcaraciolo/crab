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
               Added sim_euclidian , sim_pearson, sim_spearman
0.11 2010-10-13 Added sim_cosine, sim_tanimoto
0.12 2010-10-16 Added sim_loglikehood
0.13 2010-10-17 Added  sim_sorensen
0.14 2010-10-20 Added sim_manhattan
0.15 2010-10-26 Reformulated all design of the similarities.
0.16 2010-10-28 Added sim_jaccard.



'''

"""
:mod:`similarity_distance` -- the similarity distances table
================================================================

    This module is responsible of joining all similariy distances funcions.


"""

try:
    from numpy import sqrt, log
except ImportError:
    from math import sqrt, log


def sim_euclidian(vector1, vector2, **args):
    '''
    An implementation of a "similarity" based on the Euclidean "distance"
    between two vectors X and Y. Thinking of items as dimensions and
    preferences as points along those dimensions, a distance is computed using
    all items (dimensions) where both users have expressed a preference for
    that item. This is simply the square root of the sum of the squares of
    differences in position (preference) along each dimension. The similarity
    is then computed as 1 / (1 + distance), so the resulting values are in the
    range (0,1].

    Parameters:
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].
    '''
    # Using Content Mode.
    if type(vector1) == type({}):
        sim = {}
        [sim.update({item:1}) for item in vector1 if item in vector2]

        if len(sim) == 0.0:
            return 0.0

        sum_of_squares = sum([pow(vector1[item] - vector2[item], 2.0)
                           for item in vector1 if item in vector2])
    else:
        # Using Value Mode.
        if len(vector1) != len(vector2):
            raise ValueError('Dimmensions vector1 != Dimmensions vector2')

        sum_of_squares = sum([pow(vector1[i] - vector2[i], 2.0)
                              for i in range(len(vector1))])

        if not sum_of_squares:
            return 0.0

    return 1 / (1 + sqrt(sum_of_squares))


def sim_pearson(vector1, vector2, **args):
    '''
    This correlation implementation is equivalent to the cosine similarity
    since the data it receives is assumed to be centered -- mean is 0. The
    correlation may be interpreted as the cosine of the angle between the two
    vectors defined by the users' preference values.

    Parameters:
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].

    '''
    # Using Content Mode.
    if type(vector1) == type({}):
        sim = {}
        [sim.update({item:1})  for item in vector1  if item in vector2]
        n = len(sim)

        if n == 0:
            return 0.0

        sum1 = sum([vector1[it]  for it in sim])
        sum2 = sum([vector2[it]  for it in sim])

        sum1Sq = sum([pow(vector1[it], 2.0) for it in sim])
        sum2Sq = sum([pow(vector2[it], 2.0) for it in sim])

        pSum = sum(vector1[it] * vector2[it] for it in sim)

        num = pSum - (sum1 * sum2 / float(n))

        den = sqrt((sum1Sq - pow(sum1, 2.0) / n) *
                   (sum2Sq - pow(sum2, 2.0) / n))

        if den == 0.0:
            return 0.0

        return num / den
    else:
        # Using Value Mode.
        if len(vector1) != len(vector2):
            raise ValueError('Dimmensions vector1 != Dimmensions vector2')

        if len(vector1) == 0 or len(vector2) == 0:
            return 0.0

        sum1 = sum(vector1)
        sum2 = sum(vector2)

        sum1q = sum([pow(v, 2) for v in vector1])
        sum2q = sum([pow(v, 2) for v in vector2])

        pSum = sum([vector1[i] * vector2[i] for i in range(len(vector1))])

        num = pSum - (sum1 * sum2 / len(vector1))

        den = sqrt((sum1q - pow(sum1, 2) / len(vector1)) *
                   (sum2q - pow(sum2, 2) / len(vector1)))

        if den == 0.0:
            return 0.0

        return num / den


def sim_spearman(vector1, vector2, **args):
    '''
    Like  sim_pearson , but compares relative ranking of preference values
    instead of preference values themselves. That is, each user's preferences
    are sorted and then assign a rank as their preference value, with 1 being
    assigned to the least preferred item.

    Parameters:
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].

    '''

    if type(vector1) == type([]):
        raise TypeError('It still not yet implemented.')

    simP1 = {}
    simP2 = {}
    rank = 1.0

    # First order from the lowest to greatest value.
    vector1_items = sorted(vector1.items(), lambda x, y: cmp(x[1], y[1]))
    vector2_items = sorted(vector2.items(), lambda x, y: cmp(x[1], y[1]))

    for key, value in vector1_items:
        if key in vector2:
            simP1.update({key: rank})
            rank += 1

    rank = 1.0
    for key, values in vector2_items:
        if key in vector2:
            simP2.update({key: rank})
            rank += 1

    sumDiffSq = 0.0
    for key, rank in simP1.items():
        if key in simP2:
            sumDiffSq += pow((rank - simP2[key]), 2.0)

    n = len(simP1)

    if n == 0:
        return 0.0

    return 1.0 - ((6.0 * sumDiffSq) / (n * (n * n - 1)))


def sim_tanimoto(vector1, vector2, **args):
    '''
      An implementation of a "similarity" based on the Tanimoto coefficient,
    or extended Jaccard coefficient.

    This is intended for "binary" data sets where a user either expresses a
    generic "yes" preference for an item or has no preference. The actual
    preference values do not matter here, only their presence or absence.

    Parameters:
        the prefs: The preferences in dict format.
        person1: The user profile you want to compare
        person2: The second user profile you want to compare

    The value returned is in [0,1].

    '''
    simP1P2 = [item for item in vector1 if item in vector2]
    if len(simP1P2) == 0:
        return 0.0

    return float(len(simP1P2)) / (len(vector1) + len(vector2) - len(simP1P2))


def sim_cosine(vector1, vector2, **args):
    '''
     An implementation of the cosine similarity. The result is the cosine of
     the angle formed between the two preference vectors.  Note that this
     similarity does not "center" its data, shifts the user's preference values
     so that each of their means is 0. For this behavior, use Pearson
     Coefficient, which actually is mathematically equivalent for centered
     data.

    Parameters:
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].
    '''

    if len(vector1) == 0 or len(vector2) == 0:
        return 0.0

    # Using Content Mode.
    if type(vector1) == type({}):
        try:
            from numpy import dot, norm
            v = [(vector1[item], vector2[item]) for item in vector1
                 if item in vector2]
            vector1 = [vec[0] for vec in v]
            vector2 = [vec[1] for vec in v]
        except ImportError:
            def dot(p1, p2):
                return sum([p1.get(item, 0) * p2.get(item, 0) for item in p2])

            def norm(p):
                return sqrt(sum([p.get(item, 0) * p.get(item, 0)
                                 for item in p]))
    else:
        try:
            from numpy import dot, norm
        except ImportError:
            def dot(p1, p2):
                return sum([p1[i] * p2[i] for i in xrange(len(p1))])

            def norm(p):
                return sqrt(sum([p[i] * p[i] for i in xrange(len(p))]))

    return dot(vector1, vector2) / (norm(vector1) * norm(vector2))


def sim_loglikehood(n, vector1, vector2, **args):
    '''
    See http://citeseerx.ist.psu.edu/viewdoc/summary?doi=10.1.1.14.5962 and
    http://tdunning.blogspot.com/2008/03/surprise-and-coincidence.html .

    Parameters:
        n : Total  Number of items
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].
    '''

    def safeLog(d):
        if d <= 0.0:
            return 0.0
        else:
            return log(d)

    def logL(p, k, n):
        return k * safeLog(p) + (n - k) * safeLog(1.0 - p)

    def twoLogLambda(k1, k2, n1, n2):
        p = (k1 + k2) / (n1 + n2)
        return 2.0 * (logL(k1 / n1, k1, n1) + logL(k2 / n2, k2, n2)
                      - logL(p, k1, n1) - logL(p, k2, n2))

    # Using Content Mode.
    if type(vector1) == type({}):
        simP1P2 = {}
        [simP1P2.update({item: 1}) for item in vector1 if item in vector2]

        if len(simP1P2) == 0:
            return 0.0

        nP1P2 = len(simP1P2)
        nP1 = len(vector1)
        nP2 = len(vector2)
    else:
        nP1P2 = len([item  for item in vector1 if item in vector2])

        if nP1P2 == 0:
            return 0.0

        nP1 = len(vector1)
        nP2 = len(vector2)

    if (nP1 - nP1P2 == 0)  or (n - nP2 == 0):
        return 1.0

    logLikeliHood = twoLogLambda(float(nP1P2), float(nP1 - nP1P2),
                                 float(nP2), float(n - nP2))

    return 1.0 - 1.0 / (1.0 + float(logLikeliHood))


def sim_sorensen(vector1, vector2, **args):
    '''
    The Sørensen index, also known as Sørensen’s similarity coefficient, is a
    statistic used for comparing the similarity of two samples.  It was
    developed by the botanist Thorvald Sørensen and published in 1948.[1] See
    the link: http://en.wikipedia.org/wiki/S%C3%B8rensen_similarity_index

    This is intended for "binary" data sets where a user either expresses a
    generic "yes" preference for an item or has no preference. The actual
    preference values do not matter here, only their presence or absence.

    Parameters:
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].

    '''
    nP1P2 = len([item  for item in vector1 if item in vector2])

    if len(vector1) + len(vector2) == 0:
        return 0.0

    return float(2.0 * nP1P2 / (len(vector1) + len(vector2)))


def sim_manhattan(vector1, vector2, **args):
    """The distance between two points in a grid based on a strictly horizontal
    and/or vertical path (that is, along the grid lines as opposed to the
    diagonal or "as the crow flies" distance.  The Manhattan distance is the
    simple sum of the horizontal and vertical components, whereas the diagonal
    distance might be computed by applying the Pythagorean theorem.

    Parameters:
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].

    """
    # Content Mode
    if type(vector1) == type({}):
        nP1P2 = len([item  for item in vector1 if item in vector2])
        distance = sum([abs(vector1[key] - vector2[key])
                        for key in vector1 if key in vector2])
    else:
        nP1P2 = len(vector1)
        distance = sum([abs(vector1[i] - vector2[i])
                        for i in xrange(len(vector1))])

    if nP1P2 > 0:
        return 1 - (float(distance) / nP1P2)
    else:
        return 0.0


def sim_jaccard(vector1, vector2, **args):
    """
    Jaccard similarity coefficient is a statistic used for comparing the
    similarity and diversity of sample sets.  The Jaccard coefficient measures
    similarity between sample sets, and is defined as the size of the
    intersection divided by the size of the union of the sample sets.

    Parameters:
        vector1: The vector you want to compare
        vector2: The second vector you want to compare
        args: optional arguments

    The value returned is in [0,1].
    """

    # Content Mode
    if type(vector1) == type({}):
        simP1P2 = {}

        [simP1P2.update({item:1}) for item in vector1 if item in vector2]

        nP1P2 = len(simP1P2)
    else:
        nP1P2 = len([item  for item in vector1 if item in vector2])

    if len(vector1) == 0 and len(vector2) == 0:
        return 0.0

    return float(nP1P2) / (len(vector1) + len(vector2) - nP1P2)
