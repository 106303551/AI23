# multiAgents.py
# --------------
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


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent
from pacman import GameState

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState: GameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState: GameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        "*** YOUR CODE HERE ***"
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        oldPos = currentGameState.getPacmanPosition()
        newPos = successorGameState.getPacmanPosition()
        oldFood = currentGameState.getFood()
        foodPos = []
        for i,pos_list in enumerate(oldFood):
            for j,val in enumerate(pos_list):
                if val:
                    foodPos.append((i,j))
        newGhostStates = successorGameState.getGhostStates()
        newGhostpos = [ghoststate.getPosition() for ghoststate in newGhostStates]
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]
        oldPacmanGhostDis =  [util.manhattanDistance(oldPos,ghostPos) for ghostPos in newGhostpos]
        newPacmanGhostDis = [util.manhattanDistance(newPos,ghostPos) for ghostPos in newGhostpos]
        oldFoodPacmanDis = [util.manhattanDistance(oldPos,foodpos) for foodpos in foodPos]
        newFoodPacmanDis = [util.manhattanDistance(newPos,foodpos) for foodpos in foodPos]
        score = 0
        if action == 'Stop':
            score = -1000000
            return score
        for scaredtime,old_dis,new_dis in zip(newScaredTimes,oldPacmanGhostDis,newPacmanGhostDis):
            if scaredtime == 0:
                if old_dis<3:
                    if new_dis<old_dis:
                        score = -1000000
                        return score
                    else:
                        score = 100000
                        return score
        if newPos in foodPos:
            score = 100000000
            return score
        if newPos == oldPos:
            score = -10000000
            return score
        new_score = 1/min(newFoodPacmanDis)
        old_score = 1/min(oldFoodPacmanDis)
        if new_score <= old_score:
            score_list =[new_score,new_score,new_score,old_score,old_score,1]
            score = random.choice(score_list)
        else:
            score_list =[new_score,new_score,old_score,old_score,old_score,1]
            score = random.choice(score_list)
        return score

def scoreEvaluationFunction(currentGameState: GameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def minimax(curstate:GameState,agentindex,depth,maximizingPlayer):
            best_action = None
            agentNum = curstate.getNumAgents()
            if depth == self.depth or curstate.isWin() or curstate.isLose():
                return self.evaluationFunction(curstate),None
            if maximizingPlayer:
                max_score = -1000000000
                legalActions = curstate.getLegalActions(agentindex)
                for action in legalActions:
                    successor = curstate.generateSuccessor(agentindex,action)
                    if agentindex == agentNum-1:
                        now_score,_ = minimax(successor,0,depth+1,True)
                    else:
                        now_score,_ = minimax(successor,agentindex+1,depth,False)
                    if max_score<now_score:
                        max_score = now_score
                        best_action = action
                return max_score,best_action
            else:
                min_score = 100000000000000
                legalActions = curstate.getLegalActions(agentindex)
                for action in legalActions:
                    successor = curstate.generateSuccessor(agentindex,action)
                    if agentindex == agentNum-1:
                        now_score,_ = minimax(successor,0,depth+1,True)
                    else:
                        now_score,_ = minimax(successor,agentindex+1,depth,False)
                    min_score = min(min_score,now_score)
                    if now_score<min_score:
                        min_score = now_score
                        best_action = action
                return min_score,best_action
            
        score,action = minimax(gameState,0,0,True)
        return action

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
          Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def alpha_beta(curstate:GameState,agentindex,depth,maximizingPlayer,alpha,beta):
            agentNum = curstate.getNumAgents()
            bestaction = None
            if depth == self.depth or curstate.isWin() or curstate.isLose():
                return self.evaluationFunction(curstate),None
            if maximizingPlayer:
                max_score = -1000000000
                legalActions = curstate.getLegalActions(agentindex)
                for action in legalActions:
                    successor = curstate.generateSuccessor(agentindex,action)
                    if agentindex == agentNum-1:
                        now_score,_ = alpha_beta(successor,0,depth+1,True,alpha,beta)
                    else:
                        now_score,_ = alpha_beta(successor,agentindex+1,depth,False,alpha,beta)
                    if max_score<now_score:
                        max_score = now_score
                        bestaction = action
                    if max_score>beta:
                        return max_score,action
                    alpha = max(alpha,max_score)
                return max_score,bestaction
            else:
                min_score = 100000000000000
                legalActions = curstate.getLegalActions(agentindex)
                for action in legalActions:
                    successor = curstate.generateSuccessor(agentindex,action)
                    if agentindex == agentNum-1:
                        now_score,_ = alpha_beta(successor,0,depth+1,True,alpha,beta)
                    else:
                        now_score,_ = alpha_beta(successor,agentindex+1,depth,False,alpha,beta)
                    if now_score<min_score:
                        min_score = now_score
                        bestaction = action
                    if min_score<alpha:
                        return min_score,action
                    beta = min(beta,min_score)
                return min_score,bestaction
            
        alpha = -1000000000
        beta = 1000000000000000

        score,action = alpha_beta(gameState,0,0,True,alpha,beta)

        return action

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState: GameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        util.raiseNotDefined()

def betterEvaluationFunction(currentGameState: GameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    util.raiseNotDefined()

# Abbreviation
better = betterEvaluationFunction
