# inference.py
# ------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import random
import itertools
from typing import List, Dict, Tuple
import busters
import game
import bayesNet as bn
from bayesNet import normalize
import hunters
from util import manhattanDistance, raiseNotDefined
from factorOperations import joinFactorsByVariableWithCallTracking, joinFactors
from factorOperations import eliminateWithCallTracking

########### ########### ###########
########### QUESTION 1  ###########
########### ########### ###########

def constructBayesNet(gameState: hunters.GameState):
    """
    Construct an empty Bayes net according to the structure given in Figure 1
    of the project description.

    You *must* name all variables using the constants in this function.

    In this method, you should:
    - populate `variables` with the Bayes Net nodes
    - populate `edges` with every edge in the Bayes Net. we will represent each
      edge as a tuple `(from, to)`.
    - set each `variableDomainsDict[var] = values`, where `values` is a list
      of the possible assignments to `var`.
        - each agent position is a tuple (x, y) where x and y are 0-indexed
        - each observed distance is a noisy Manhattan distance:
          it's non-negative and |obs - true| <= MAX_NOISE
    - this uses slightly simplified mechanics vs the ones used later for simplicity
    """
    # constants to use
    PAC = "Pacman"
    GHOST0 = "Ghost0"
    GHOST1 = "Ghost1"
    OBS0 = "Observation0"
    OBS1 = "Observation1"
    X_RANGE = gameState.getWalls().width
    Y_RANGE = gameState.getWalls().height
    MAX_NOISE = 7

    variables = []
    edges = []
    variableDomainsDict = {}

    "*** YOUR CODE HERE ***"
    maxDistance = manhattanDistance((1,1),(X_RANGE,Y_RANGE))+MAX_NOISE+1
    variables = [PAC,GHOST0,GHOST1,OBS0,OBS1]
    edges = [(PAC,OBS0),(PAC,OBS1),(GHOST0,OBS0),(GHOST1,OBS1)]
    variableDomainsDict[PAC]  = [(x,y) for x in range(X_RANGE) for y in range(Y_RANGE)]
    variableDomainsDict[GHOST0] = [(x,y) for x in range(X_RANGE) for y in range(Y_RANGE)]
    variableDomainsDict[GHOST1]  = [(x,y) for x in range(X_RANGE) for y in range(Y_RANGE)]
    variableDomainsDict[OBS0] = [i for i in range(maxDistance)]
    variableDomainsDict[OBS1] = [i for i in range(maxDistance)]
    "*** END YOUR CODE HERE ***"

    net = bn.constructEmptyBayesNet(variables, edges, variableDomainsDict)
    return net


def inferenceByEnumeration(bayesNet: bn, queryVariables: List[str], evidenceDict: Dict):
    """
    An inference by enumeration implementation provided as reference.
    This function performs a probabilistic inference query that
    returns the factor:

    P(queryVariables | evidenceDict)

    bayesNet:       The Bayes Net on which we are making a query.
    queryVariables: A list of the variables which are unconditioned in
                    the inference query.
    evidenceDict:   An assignment dict {variable : value} for the
                    variables which are presented as evidence
                    (conditioned) in the inference query. 
    """
    callTrackingList = []
    joinFactorsByVariable = joinFactorsByVariableWithCallTracking(callTrackingList)
    eliminate = eliminateWithCallTracking(callTrackingList)

    # initialize return variables and the variables to eliminate
    evidenceVariablesSet = set(evidenceDict.keys())
    queryVariablesSet = set(queryVariables)
    eliminationVariables = (bayesNet.variablesSet() - evidenceVariablesSet) - queryVariablesSet

    # grab all factors where we know the evidence variables (to reduce the size of the tables)
    currentFactorsList = bayesNet.getAllCPTsWithEvidence(evidenceDict)

    # join all factors by variable
    for joinVariable in bayesNet.variablesSet():
        currentFactorsList, joinedFactor = joinFactorsByVariable(currentFactorsList, joinVariable)
        currentFactorsList.append(joinedFactor)

    # currentFactorsList should contain the connected components of the graph now as factors, must join the connected components
    fullJoint = joinFactors(currentFactorsList)

    # marginalize all variables that aren't query or evidence
    incrementallyMarginalizedJoint = fullJoint
    for eliminationVariable in eliminationVariables:
        incrementallyMarginalizedJoint = eliminate(incrementallyMarginalizedJoint, eliminationVariable)

    fullJointOverQueryAndEvidence = incrementallyMarginalizedJoint

    # normalize so that the probability sums to one
    # the input factor contains only the query variables and the evidence variables, 
    # both as unconditioned variables
    queryConditionedOnEvidence = normalize(fullJointOverQueryAndEvidence)
    # now the factor is conditioned on the evidence variables

    # the order is join on all variables, then eliminate on all elimination variables
    return queryConditionedOnEvidence

########### ########### ###########
########### QUESTION 4  ###########
########### ########### ###########

def inferenceByVariableEliminationWithCallTracking(callTrackingList=None):

    def inferenceByVariableElimination(bayesNet: bn, queryVariables: List[str], evidenceDict: Dict, eliminationOrder: List[str]):
        """
        This function should perform a probabilistic inference query that
        returns the factor:

        P(queryVariables | evidenceDict)

        It should perform inference by interleaving joining on a variable
        and eliminating that variable, in the order of variables according
        to eliminationOrder.  See inferenceByEnumeration for an example on
        how to use these functions.

        You need to use joinFactorsByVariable to join all of the factors 
        that contain a variable in order for the autograder to 
        recognize that you performed the correct interleaving of 
        joins and eliminates.

        If a factor that you are about to eliminate a variable from has 
        only one unconditioned variable, you should not eliminate it 
        and instead just discard the factor.  This is since the 
        result of the eliminate would be 1 (you marginalize 
        all of the unconditioned variables), but it is not a 
        valid factor.  So this simplifies using the result of eliminate.

        The sum of the probabilities should sum to one (so that it is a true 
        conditional probability, conditioned on the evidence).

        bayesNet:         The Bayes Net on which we are making a query.
        queryVariables:   A list of the variables which are unconditioned
                          in the inference query.
        evidenceDict:     An assignment dict {variable : value} for the
                          variables which are presented as evidence
                          (conditioned) in the inference query. 
        eliminationOrder: The order to eliminate the variables in.

        Hint: BayesNet.getAllCPTsWithEvidence will return all the Conditional 
        Probability Tables even if an empty dict (or None) is passed in for 
        evidenceDict. In this case it will not specialize any variable domains 
        in the CPTs.

        Useful functions:
        BayesNet.getAllCPTsWithEvidence
        normalize
        eliminate
        joinFactorsByVariable
        joinFactors
        """

        # this is for autograding -- don't modify
        joinFactorsByVariable = joinFactorsByVariableWithCallTracking(callTrackingList)
        eliminate             = eliminateWithCallTracking(callTrackingList)
        if eliminationOrder is None: # set an arbitrary elimination order if None given
            eliminationVariables = bayesNet.variablesSet() - set(queryVariables) -\
                                   set(evidenceDict.keys())
            eliminationOrder = sorted(list(eliminationVariables))

        "*** YOUR CODE HERE ***"
        # grab all factors where we know the evidence variables (to reduce the size of the tables)
        currentFactorsList = bayesNet.getAllCPTsWithEvidence(evidenceDict)

        for eliminationVariable in eliminationOrder:
            currentFactorsList, joinedFactor = joinFactorsByVariable(currentFactorsList, eliminationVariable)

            if len(joinedFactor.unconditionedVariables()) >1:
                joinedFactor = eliminate(joinedFactor, eliminationVariable)
                currentFactorsList.append(joinedFactor)

        joinedFactor = joinFactors(currentFactorsList)

        fullJointOverQueryAndEvidence = joinedFactor

        # normalize so that the probability sums to one
        # the input factor contains only the query variables and the evidence variables, 
        # both as unconditioned variables
        queryConditionedOnEvidence = normalize(fullJointOverQueryAndEvidence)
        # now the factor is conditioned on the evidence variables

        # the order is join on all variables, then eliminate on all elimination variables
        return queryConditionedOnEvidence
        raiseNotDefined()
        "*** END YOUR CODE HERE ***"


    return inferenceByVariableElimination

inferenceByVariableElimination = inferenceByVariableEliminationWithCallTracking()

def sampleFromFactorRandomSource(randomSource=None):
    if randomSource is None:
        randomSource = random.Random()

    def sampleFromFactor(factor, conditionedAssignments=None):
        """
        Sample an assignment for unconditioned variables in factor with
        probability equal to the probability in the row of factor
        corresponding to that assignment.

        factor:                 The factor to sample from.
        conditionedAssignments: A dict of assignments for all conditioned
                                variables in the factor.  Can only be None
                                if there are no conditioned variables in
                                factor, otherwise must be nonzero.

        Useful for inferenceByLikelihoodWeightingSampling

        Returns an assignmentDict that contains the conditionedAssignments but 
        also a random assignment of the unconditioned variables given their 
        probability.
        """
        if conditionedAssignments is None and len(factor.conditionedVariables()) > 0:
            raise ValueError("Conditioned assignments must be provided since \n" +
                            "this factor has conditionedVariables: " + "\n" +
                            str(factor.conditionedVariables()))

        elif conditionedAssignments is not None:
            conditionedVariables = set([var for var in conditionedAssignments.keys()])

            if not conditionedVariables.issuperset(set(factor.conditionedVariables())):
                raise ValueError("Factor's conditioned variables need to be a subset of the \n"
                                    + "conditioned assignments passed in. \n" + \
                                "conditionedVariables: " + str(conditionedVariables) + "\n" +
                                "factor.conditionedVariables: " + str(set(factor.conditionedVariables())))

            # Reduce the domains of the variables that have been
            # conditioned upon for this factor 
            newVariableDomainsDict = factor.variableDomainsDict()
            for (var, assignment) in conditionedAssignments.items():
                newVariableDomainsDict[var] = [assignment]

            # Get the (hopefully) smaller conditional probability table
            # for this variable 
            CPT = factor.specializeVariableDomains(newVariableDomainsDict)
        else:
            CPT = factor
        
        # Get the probability of each row of the table (along with the
        # assignmentDict that it corresponds to)
        assignmentDicts = sorted([assignmentDict for assignmentDict in CPT.getAllPossibleAssignmentDicts()])
        assignmentDictProbabilities = [CPT.getProbability(assignmentDict) for assignmentDict in assignmentDicts]

        # calculate total probability in the factor and index each row by the 
        # cumulative sum of probability up to and including that row
        currentProbability = 0.0
        probabilityRange = []
        for i in range(len(assignmentDicts)):
            currentProbability += assignmentDictProbabilities[i]
            probabilityRange.append(currentProbability)

        totalProbability = probabilityRange[-1]

        # sample an assignment with probability equal to the probability in the row 
        # for that assignment in the factor
        pick = randomSource.uniform(0.0, totalProbability)
        for i in range(len(assignmentDicts)):
            if pick <= probabilityRange[i]:
                return assignmentDicts[i]

    return sampleFromFactor

sampleFromFactor = sampleFromFactorRandomSource()

class DiscreteDistribution(dict):
    """
    A DiscreteDistribution models belief distributions and weight distributions
    over a finite set of discrete keys.
    """
    def __getitem__(self, key):
        self.setdefault(key, 0)
        return dict.__getitem__(self, key)

    def copy(self):
        """
        Return a copy of the distribution.
        """
        return DiscreteDistribution(dict.copy(self))

    def argMax(self):
        """
        Return the key with the highest value.
        """
        if len(self.keys()) == 0:
            return None
        all = list(self.items())
        values = [x[1] for x in all]
        maxIndex = values.index(max(values))
        return all[maxIndex][0]

    def total(self):
        """
        Return the sum of values for all keys.
        """
        return float(sum(self.values()))
    
    ########### ########### ###########
    ########### QUESTION 5a ###########
    ########### ########### ###########

    def normalize(self):
        """
        Normalize the distribution such that the total value of all keys sums
        to 1. The ratio of values for all keys will remain the same. In the case
        where the total value of the distribution is 0, do nothing.

        >>> dist = DiscreteDistribution()
        >>> dist['a'] = 1
        >>> dist['b'] = 2
        >>> dist['c'] = 2
        >>> dist['d'] = 0
        >>> dist.normalize()
        >>> list(sorted(dist.items()))
        [('a', 0.2), ('b', 0.4), ('c', 0.4), ('d', 0.0)]
        >>> dist['e'] = 4
        >>> list(sorted(dist.items()))
        [('a', 0.2), ('b', 0.4), ('c', 0.4), ('d', 0.0), ('e', 4)]
        >>> empty = DiscreteDistribution()
        >>> empty.normalize()
        >>> empty
        {}
        """
        "*** YOUR CODE HERE ***"
        total = sum(self.values())
        if total ==0:
            return
        for k in self:
            self[k] /= total
        "*** END YOUR CODE HERE ***"

    def sample(self):
        """
        Draw a random sample from the distribution and return the key, weighted
        by the values associated with each key.

        >>> dist = DiscreteDistribution()
        >>> dist['a'] = 1
        >>> dist['b'] = 2
        >>> dist['c'] = 2
        >>> dist['d'] = 0
        >>> N = 100000.0
        >>> samples = [dist.sample() for _ in range(int(N))]
        >>> round(samples.count('a') * 1.0/N, 1)  # proportion of 'a'
        0.2
        >>> round(samples.count('b') * 1.0/N, 1)
        0.4
        >>> round(samples.count('c') * 1.0/N, 1)
        0.4
        >>> round(samples.count('d') * 1.0/N, 1)
        0.0
        """
        "*** YOUR CODE HERE ***"
        total = sum(self.values())
        if total == 0:
            return None
        rand_rat = random.random()
        cal_rat = 0
        for k,v in self.items():
            cal_rat += v/total
            if cal_rat>=rand_rat:
                return k
        "*** END YOUR CODE HERE ***"


class InferenceModule:
    """
    An inference module tracks a belief distribution over a ghost's location.
    """
    ############################################
    # Useful methods for all inference modules #
    ############################################

    def __init__(self, ghostAgent):
        """
        Set the ghost agent for later access.
        """
        self.ghostAgent = ghostAgent
        self.index = ghostAgent.index
        self.obs = []  # most recent observation position

    def getJailPosition(self):
        return (2 * self.ghostAgent.index - 1, 1)

    def getPositionDistributionHelper(self, gameState, pos, index, agent):
        try:
            jail = self.getJailPosition()
            gameState = self.setGhostPosition(gameState, pos, index + 1)
        except TypeError:
            jail = self.getJailPosition(index)
            gameState = self.setGhostPositions(gameState, pos)
        pacmanPosition = gameState.getPacmanPosition()
        ghostPosition = gameState.getGhostPosition(index + 1)  # The position you set
        dist = DiscreteDistribution()
        if pacmanPosition == ghostPosition:  # The ghost has been caught!
            dist[jail] = 1.0
            return dist
        pacmanSuccessorStates = game.Actions.getLegalNeighbors(pacmanPosition, \
                gameState.getWalls())  # Positions Pacman can move to
        if ghostPosition in pacmanSuccessorStates:  # Ghost could get caught
            mult = 1.0 / float(len(pacmanSuccessorStates))
            dist[jail] = mult
        else:
            mult = 0.0
        actionDist = agent.getDistribution(gameState)
        for action, prob in actionDist.items():
            successorPosition = game.Actions.getSuccessor(ghostPosition, action)
            if successorPosition in pacmanSuccessorStates:  # Ghost could get caught
                denom = float(len(actionDist))
                dist[jail] += prob * (1.0 / denom) * (1.0 - mult)
                dist[successorPosition] = prob * ((denom - 1.0) / denom) * (1.0 - mult)
            else:
                dist[successorPosition] = prob * (1.0 - mult)
        return dist

    def getPositionDistribution(self, gameState, pos, index=None, agent=None):
        """
        Return a distribution over successor positions of the ghost from the
        given gameState. You must first place the ghost in the gameState, using
        setGhostPosition below.
        """
        if index == None:
            index = self.index - 1
        if agent == None:
            agent = self.ghostAgent
        return self.getPositionDistributionHelper(gameState, pos, index, agent)
    
    ########### ########### ###########
    ########### QUESTION 5b ###########
    ########### ########### ###########

    def getObservationProb(self, noisyDistance: int, pacmanPosition: Tuple, ghostPosition: Tuple, jailPosition: Tuple):
        """
        Return the probability P(noisyDistance | pacmanPosition, ghostPosition).
        """
        "*** YOUR CODE HERE ***"
        #get ghost -> send None
        #其餘條件全部為0
        if noisyDistance is None:
            if ghostPosition == jailPosition:
                return 1
            else:
                return 0
        else:
            if ghostPosition == jailPosition:
                return 0
            #Normal case
            else:
                realdistance = manhattanDistance(pacmanPosition,ghostPosition)
                return busters.getObservationProbability(noisyDistance,realdistance)
        raiseNotDefined()
        "*** END YOUR CODE HERE ***"

    def setGhostPosition(self, gameState, ghostPosition, index):
        """
        Set the position of the ghost for this inference module to the specified
        position in the supplied gameState.

        Note that calling setGhostPosition does not change the position of the
        ghost in the GameState object used for tracking the true progression of
        the game.  The code in inference.py only ever receives a deep copy of
        the GameState object which is responsible for maintaining game state,
        not a reference to the original object.  Note also that the ghost
        distance observations are stored at the time the GameState object is
        created, so changing the position of the ghost will not affect the
        functioning of observe.
        """
        conf = game.Configuration(ghostPosition, game.Directions.STOP)
        gameState.data.agentStates[index] = game.AgentState(conf, False)
        return gameState

    def setGhostPositions(self, gameState, ghostPositions):
        """
        Sets the position of all ghosts to the values in ghostPositions.
        """
        for index, pos in enumerate(ghostPositions):
            conf = game.Configuration(pos, game.Directions.STOP)
            gameState.data.agentStates[index + 1] = game.AgentState(conf, False)
        return gameState

    def observe(self, gameState):
        """
        Collect the relevant noisy distance observation and pass it along.
        """
        distances = gameState.getNoisyGhostDistances()
        if len(distances) >= self.index:  # Check for missing observations
            obs = distances[self.index - 1]
            self.obs = obs
            self.observeUpdate(obs, gameState)

    def initialize(self, gameState):
        """
        Initialize beliefs to a uniform distribution over all legal positions.
        """
        self.legalPositions = [p for p in gameState.getWalls().asList(False) if p[1] > 1]
        self.allPositions = self.legalPositions + [self.getJailPosition()]
        self.initializeUniformly(gameState)

    ######################################
    # Methods that need to be overridden #
    ######################################

    def initializeUniformly(self, gameState):
        """
        Set the belief state to a uniform prior belief over all positions.
        """
        raise NotImplementedError

    def observeUpdate(self, observation, gameState):
        """
        Update beliefs based on the given distance observation and gameState.
        """
        raise NotImplementedError

    def elapseTime(self, gameState):
        """
        Predict beliefs for the next time step from a gameState.
        """
        raise NotImplementedError

    def getBeliefDistribution(self):
        """
        Return the agent's current belief state, a distribution over ghost
        locations conditioned on all evidence so far.
        """
        raise NotImplementedError


class ExactInference(InferenceModule):
    """
    The exact dynamic inference module should use forward algorithm updates to
    compute the exact belief function at each time step.
    """
    def initializeUniformly(self, gameState):
        """
        Begin with a uniform distribution over legal ghost positions (i.e., not
        including the jail position).
        """
        self.beliefs = DiscreteDistribution()
        for p in self.legalPositions:
            self.beliefs[p] = 1.0
        self.beliefs.normalize()
    
    ########### ########### ###########
    ########### QUESTION 6  ###########
    ########### ########### ###########

    def observeUpdate(self, observation: int, gameState: busters.GameState):
        """
        Update beliefs based on the distance observation and Pacman's position.

        The observation is the noisy Manhattan distance to the ghost you are
        tracking.

        self.allPositions is a list of the possible ghost positions, including
        the jail position. You should only consider positions that are in
        self.allPositions.

        The update model is not entirely stationary: it may depend on Pacman's
        current position. However, this is not a problem, as Pacman's current
        position is known.
        """
        "*** YOUR CODE HERE ***"
        #goal: You should iterate your updates over the variable `self.allPositions` which includes all legal positions plus the special jail position.
        #Beliefs represent the probability that the ghost is at a particular location, and are stored as a `DiscreteDistribution` object in a field called `self.beliefs`, 
        #which you should update.
        for pos in self.allPositions:
            pacmanpos = gameState.getPacmanPosition()
            ObsProb = self.getObservationProb(observation,pacmanpos,pos,self.getJailPosition())
            self.beliefs[pos] = ObsProb*self.beliefs[pos]

        "*** END YOUR CODE HERE ***"
        self.beliefs.normalize()
    
    ########### ########### ###########
    ########### QUESTION 7  ###########
    ########### ########### ###########

    def elapseTime(self, gameState: busters.GameState):
        """
        Predict beliefs in response to a time step passing from the current
        state.

        The transition model is not entirely stationary: it may depend on
        Pacman's current position. However, this is not a problem, as Pacman's
        current position is known.
        """
        "*** YOUR CODE HERE ***"
        newBeliefs = DiscreteDistribution()
        for oldPos in self.allPositions:
            newPostDist = self.getPositionDistribution(gameState,oldPos)
            for newPosition, prob in newPostDist.items():
                newBeliefs[newPosition] += self.beliefs[oldPos]*prob
        self.beliefs = newBeliefs
        "*** END YOUR CODE HERE ***"

    def getBeliefDistribution(self):
        return self.beliefs


class ParticleFilter(InferenceModule):
    """
    A particle filter for approximately tracking a single ghost.
    """
    def __init__(self, ghostAgent, numParticles=300):
        InferenceModule.__init__(self, ghostAgent)
        self.setNumParticles(numParticles)

    def setNumParticles(self, numParticles):
        self.numParticles = numParticles
    
    ########### ########### ###########
    ########### QUESTION 9  ###########
    ########### ########### ###########

    def initializeUniformly(self, gameState: busters.GameState):
        """
        Initialize a list of particles. Use self.numParticles for the number of
        particles. Use self.legalPositions for the legal board positions where
        a particle could be located. Particles should be evenly (not randomly)
        distributed across positions in order to ensure a uniform prior. Use
        self.particles for the list of particles.
        """
        self.particles = []
        "*** YOUR CODE HERE ***"

        #平均分配particle到每個 direction
        particlenum = self.numParticles
        particlecount = particlenum//len(self.legalPositions)
        remain = particlenum % len(self.legalPositions)

        #分配除不進的 particle
        for p in self.legalPositions:

            h = particlecount
            if remain >0:
                h+=1
                remain-=1

            # A list is simply a collection of unweighted variables
            self.particles.extend([p]*h)

        "*** END YOUR CODE HERE ***"

    def getBeliefDistribution(self):
        """
        Return the agent's current belief state, a distribution over ghost
        locations conditioned on all evidence and time passage. This method
        essentially converts a list of particles into a belief distribution.

        This function should return a normalized distribution.
        """
        "*** YOUR CODE HERE ***"
        beliefdist = DiscreteDistribution()

        #透過particles表示該前往的分數
        #放入beliefdist然後轉成normalized distribution

        for p in self.particles:
            beliefdist[p] += 1
        beliefdist.normalize()
        return beliefdist
        "*** END YOUR CODE HERE ***"
    
    ########### ########### ###########
    ########### QUESTION 10 ###########
    ########### ########### ###########

    def observeUpdate(self, observation: int, gameState: busters.GameState):
        """
        Update beliefs based on the distance observation and Pacman's position.

        The observation is the noisy Manhattan distance to the ghost you are
        tracking.

        There is one special case that a correct implementation must handle.
        When all particles receive zero weight, the list of particles should
        be reinitialized by calling initializeUniformly. The total method of
        the DiscreteDistribution may be useful.
        """
        "*** YOUR CODE HERE ***"
        newParticles = []
        dist = DiscreteDistribution()
        for p in self.particles:
            prob = 1
            if p not in dist:
                dist[p] = 0
            prob *= self.getObservationProb(observation, gameState.getPacmanPosition(), p, self.getJailPosition())
            dist[p] += prob
        if dist.total() == 0:
            self.initializeUniformly(gameState)
            return
        for i in range(self.numParticles):
            newParticles.append(dist.sample())
        
        self.particles = newParticles

        "*** END YOUR CODE HERE ***"
    
    ########### ########### ###########
    ########### QUESTION 11 ###########
    ########### ########### ###########

    def elapseTime(self, gameState):
        """
        Sample each particle's next state based on its current state and the
        gameState.
        """
        "*** YOUR CODE HERE ***"
        newparticles = []
        #基於 particle current state 及 pacman gamestate 決定 particle 下個 state
        for oldP in self.particles:
            newP = oldP
            newPosDist = self.getPositionDistribution(gameState, newP)
            newP = newPosDist.sample()
            newparticles.append(newP)
        self.particles = newparticles

        "*** END YOUR CODE HERE ***"
