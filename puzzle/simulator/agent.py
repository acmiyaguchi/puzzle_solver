#========================= puzzle.simulator.agent ========================
#
# @class    puzzle.simulator.agent
#
# @brief    The agent simulates a subject to solve the puzzle task.
#           It takes the perceived board and the solution board,
#           and plan the next step
#
#========================= puzzle.simulator.agent ========================

#
# @file     agent.py
#
# @author   Yiye Chen,              yychen2019@gatech.edu
#
# @date     2021/08/29
#
#
#========================= puzzle.simulator.agent ========================

from puzzle.piece.template import template
from puzzle.simulator.action import Actions
from puzzle.simulator.planner import Planner_Base

class Apperance(template):
    """
    @brief  The Appearance agent class contains the basic appearance information about the agent
            It inherit the puzzle.piece.template class so that it can be treated as a special piece
    
    TODO: so far haven't thought of features need to be added to the template. Add if needed
    """
    def __init__(self, y= None, r = (0, 0), id = None):
        super().__init__(y=y, r=r, id=id)


class Agent(Actions):
    """
    The Agent class equip the Base with the actions and the planning ability
    """

    def __init__(self, app:Apperance, planner:Planner_Base=None):
        self.app = app
        super().__init__(loc=self.app.rLoc)
        self.app.rLoc = self.loc

        # planner
        self.planner = planner

        # the short-term memory of the actions to be executed to accomplish a plan
        self.cache_actions = None
    
    def setSolBoard(self, solBoard):
        """
        Set the solution board for the Agent to refer to during the puzzle solving process
        """
        self.planner.setSolBoard(solBoard)

    def setPlanner(self, planner:Planner_Base):
        self.planner = planner
    
    def process(self, meaBoard):
        """
        Process the current perceived board to produce the next action
        """
        assert self.planner is not None,\
            "The planner can not be None, or the agent has no brain! \
                Please use the setPlanner function to get a planner"
        actions = None

        # if there are no cached actions, plan new actions
        if self.cache_actions is None:
            actions = self.planner.process(meaBoard=meaBoard)
            self.cache_actions = actions

        # execute the next action
        actions = self.planner.process(meaBoard=meaBoard)
        self.cache_actions = actions

    def execute(self, action_label, action_param=None):
        """
        Exectute an action given the action label and parameter

        Overwrite the execute function since we need to keep the self.app.rLoc updated
        NOTE:This is necessary only when we are using the puzzle.template as the appearance model
        """
        if action_param is None:
            self.ACTION_LABELS[action_label]()
        else:
            self.ACTION_LABELS[action_label](action_param)
        self.app.rLoc = self.loc

    def placeInImage(self, img, offset=[0, 0], CONTOUR_DISPLAY=True):
        self.app.placeInImage(img, offset, CONTOUR_DISPLAY=CONTOUR_DISPLAY)
    
    @staticmethod
    def buildSphereAgent(radius, color, rLoc=None, planner:Planner_Base=None):
        app_sphere = template.buildSphere(radius, color, rLoc)
        return Agent(app_sphere, planner)

    @staticmethod
    def buildSquareAgent(size, color, rLoc=None, planner:Planner_Base=None):
        app_Square = template.buildSquare(size, color, rLoc)
        return Agent(app_Square, planner)