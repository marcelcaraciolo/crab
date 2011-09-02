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

#0.1 2010-11-09 Initial version.
"""
:mod:`scorer` -- the scoring classes and functions
================================================================

This module contains functions and classes to compute the new score for a
preference given an thing (user or item).

"""

from interfaces import Scorer
from math import tanh


class NaiveScorer(Scorer):
    '''
    A simple Scorer which always returns the original score.
    '''

    def rescore(self, thing, score):
        '''
        return same originalScore as new score, always
        '''
        return  score


class TanHScorer(Scorer):
    '''
    A simple Scorer which returns the score normalized betweeen 0 and 1 where 1
    is most similar and 0 dissimilar.  '''

    def rescore(self, thing, score):
        return  1 - tanh(score)
