"""
In search.py, you will implement generic search algorithms which are called by
Pacman agents (in searchAgents.py).

Please only change the parts of the file you are asked to.  Look for the lines
that say

"*** YOUR CODE HERE ***"

Follow the project description for details.

Good luck and happy searching!
"""

import util

class SearchProblem:
    """
    This class outlines the structure of a search problem, but doesn't implement
    any of the methods (in object-oriented terminology: an abstract class).

    You do not need to change anything in this class, ever.
    """

    def getStartState(self):
        """
        Returns the start state for the search problem.
        """
        util.raiseNotDefined()

    def isGoalState(self, state):
        """
          state: Search state

        Returns True if and only if the state is a valid goal state.
        """
        util.raiseNotDefined()

    def getSuccessors(self, state):
        """
          state: Search state

        For a given state, this should return a list of triples, (successor,
        action, stepCost), where 'successor' is a successor to the current
        state, 'action' is the action required to get there, and 'stepCost' is
        the incremental cost of expanding to that successor.
        """
        util.raiseNotDefined()

    def getCostOfActions(self, actions):
        """
         actions: A list of actions to take

        This method returns the total cost of a particular sequence of actions.
        The sequence must be composed of legal moves.
        """
        util.raiseNotDefined()

def tinyMazeSearch(problem):
    """
    Returns a sequence of moves that solves tinyMaze.  For any other maze, the
    sequence of moves will be incorrect, so only use this for tinyMaze.
    """
    from game import Directions
    s = Directions.SOUTH
    w = Directions.WEST
    print("Solution:", [s, s, w, s, w, w, s, w])
    return  [s, s, w, s, w, w, s, w]

def depthFirstSearch(problem: SearchProblem):
    """
    Search the deepest nodes in the search tree first.

    Your search algorithm needs to return a list of actions that reaches the
    goal. Make sure to implement a graph search algorithm.

    To get started, you might want to try some of these simple commands to
    understand the search problem that is being passed in:

    print("Start:", problem.getStartState())
    print("Is the start a goal?", problem.isGoalState(problem.getStartState()))
    print("Start's successors:", problem.getSuccessors(problem.getStartState()))
    """
    "*** YOUR CODE HERE ***"
    #initial
    start = problem.getStartState()

    problem.frontier = util.Stack()
    problem.explored_set = set()
    action_list = []

    successors = problem.getSuccessors(start)

    for s in successors:
        s = list(s)
        s.append(action_list.copy())
        problem.frontier.push(s)

    problem.explored_set.add(start)

    while(problem.frontier.isEmpty() == False):

        node = problem.frontier.pop()
        now_pos = node[0]
        action = node[1]
        action_list = node[3]
        action_list.append(action)

        if problem.isGoalState(now_pos) == True:
            return action_list
        
        successors = problem.getSuccessors(now_pos)
        problem.explored_set.add(now_pos)

        for s in successors:
            s = list(s)
            s_pos = s[0]
            s.append(action_list.copy())
            if s_pos not in problem.explored_set:
                problem.frontier.push(s)

    return "no sol"

def breadthFirstSearch(problem: SearchProblem):
    """Search the shallowest nodes in the search tree first."""
    "*** YOUR CODE HERE ***"

    start = problem.getStartState()
    problem.frontier = util.Queue()
    problem.explored_set = set()
    action_list = []
    successors = problem.getSuccessors(start)

    for s in successors:
        s = list(s)
        s.append(action_list.copy())
        problem.frontier.push(s)

    problem.explored_set.add(start)

    while(problem.frontier.isEmpty() == False):

        node = problem.frontier.pop()
        now_pos = node[0]
        action = node[1]
        action_list = node[3].copy()
        action_list.append(action)
        
        if now_pos not in problem.explored_set:
            
            problem.action_list = action_list.copy()
            if problem.isGoalState(now_pos) == True:
                return action_list

            successors = problem.getSuccessors(now_pos)
            problem.explored_set.add(now_pos)

            for s in successors:
                s = list(s)
                s_pos = s[0]
                s.append(action_list.copy())

                if s_pos not in problem.explored_set:
                    problem.frontier.push(s)

    return "no sol"

def uniformCostSearch(problem: SearchProblem):
    """Search the node of least total cost first."""
    "*** YOUR CODE HERE ***"
    start = problem.getStartState()

    problem.frontier = util.PriorityQueue()
    problem.explored_set = set()
    action_list = []

    successors = problem.getSuccessors(start)

    for s in successors:
        s = list(s)
        s_cost = s[2]
        priority = s_cost
        s.append(action_list.copy())
        s.append(s_cost)
        problem.frontier.update(s,priority)

    problem.explored_set.add(start)

    while(problem.frontier.isEmpty() == False):

        node = problem.frontier.pop()
        now_pos = node[0]
        action = node[1]
        action_list = node[3]
        action_list.append(action)
        now_cost = node[4]

        if problem.isGoalState(now_pos) == True:
            return action_list 
        
        if now_pos not in problem.explored_set:
            successors = problem.getSuccessors(now_pos)
            problem.explored_set.add(now_pos)

            for s in successors:
                s = list(s)
                s_pos = s[0]
                s_cost = now_cost + s[2]
                priority = s_cost
                s.append(action_list.copy())
                s.append(s_cost)

                if s_pos not in problem.explored_set:
                    problem.frontier.update(s,priority)

    return "no sol"

def nullHeuristic(state, problem=None):
    """
    A heuristic function estimates the cost from the current state to the nearest
    goal in the provided SearchProblem.  This heuristic is trivial.
    """
    return 0

def aStarSearch(problem: SearchProblem, heuristic=nullHeuristic):
    """Search the node that has the lowest combined cost and heuristic first."""
    "*** YOUR CODE HERE ***"
    start = problem.getStartState()

    problem.frontier = util.PriorityQueue()
    problem.explored_set = set()
    action_list = []

    successors = problem.getSuccessors(start)

    for s in successors:
        s = list(s)
        s_pos = s[0]
        s_cost = s[2]
        priority = s_cost+heuristic(s_pos,problem)
        s.append(action_list.copy())
        s.append(s_cost)
        problem.frontier.update(s,priority)

    problem.explored_set.add(start)

    while(problem.frontier.isEmpty() == False):

        node = problem.frontier.pop()
        now_pos = node[0]
        action = node[1]
        action_list = node[3]
        action_list.append(action)
        now_cost = node[4]

        if problem.isGoalState(now_pos) == True:
            return action_list 
               
        if now_pos not in problem.explored_set:
            successors = problem.getSuccessors(now_pos)
            problem.explored_set.add(now_pos)

            for s in successors:

                s = list(s)
                s_pos = s[0]
                s_cost = now_cost + s[2]
                # print(now_pos)
                priority = s_cost+heuristic(s_pos,problem)
                s.append(action_list.copy())
                s.append(s_cost)

                if s_pos not in problem.explored_set:
                    problem.frontier.update(s,priority)

    return "no sol"


# Abbreviations
bfs = breadthFirstSearch
dfs = depthFirstSearch
astar = aStarSearch
ucs = uniformCostSearch
