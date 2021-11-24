#!/usr/bin/python3
# ============================ basic02_simple ===========================
#
# @brief    Test script for the most basic functionality of simple class.
#           Display a visual sequence of the puzzle being solved.
#
# ============================ basic02_simple ===========================

#
# @file     basic02_simple.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/15  [created]
#
# ============================ basic02_simple ===========================


# ==[0] Prep environment
import glob
import os

import cv2
import imageio
import matplotlib.pyplot as plt

from puzzle.builder.gridded import Gridded
from puzzle.manager import Manager
from puzzle.parser.fromLayer import FromLayer
from puzzle.solver.simple import Simple

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

# ==[1] Create image & mask for solution
#
theImageSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png')

theMaskSol = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image_solution.png', cv2.IMREAD_GRAYSCALE)
_, theMaskSol = cv2.threshold(theMaskSol, 10, 255, cv2.THRESH_BINARY)

# ==[1.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.process(theImageSol, theMaskSol)
theBoardSol = theLayer.getState()

# ==[2] Create image & mask for measurement
#
theImageMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_image.png')
theMaskMea = cv2.imread(cpath + '/../../testing/data/shapes_color_six_binary.png', cv2.IMREAD_GRAYSCALE)

# ==[2.1] Extract info from theImage & theMask to obtain a board instance
#
theLayer = FromLayer()
theLayer.process(theImageMea, theMaskMea)
theBoardMea = theLayer.getState()

# ==[3] Display the current & solution board
#
f, axarr = plt.subplots(1, 2)

theBoardMea_img = theBoardMea.toImage(ID_DISPLAY=True)
theBoardSol_img = theBoardSol.toImage()
axarr[0].imshow(theBoardMea_img)
axarr[0].title.set_text('Original measured board')

axarr[1].imshow(theBoardSol_img)
axarr[1].title.set_text('Solution board')

# ==[4] Create match by manager
#
theManager = Manager(theBoardSol)
theManager.process(theBoardMea)

# ==[5] Create simple instance and set up the match
#
theSolver = Simple(Gridded(theBoardSol), Gridded(theBoardMea))

theSolver.setMatch(theManager.pAssignments)

# ==[6] Start the solver to take turns, execute the plan, and display the updated board.
#

plt.ion()
fh = plt.figure()

# saveMe = True
saveMe = False

if saveMe:
    f.savefig(cpath + f'/data/theBoard.png')

FINISHED = False
i = 0

while 1:

    # Since we use the same instance in the simulator and the solver,
    # it will update automatically
    theSolver.current.display(fh=fh, ID_DISPLAY=True)
    fh.suptitle(f'Step {i}', fontsize=20)
    plt.pause(1)

    if FINISHED:
        break
    if i == 0:
        # Display the original one at the very beginning
        print(f'The original measured board')

    if saveMe:
        fh.savefig(cpath + f'/data/basic02_step{str(i).zfill(2)}.png')

    print(f'Step {i + 1}:')

    plan = theSolver.takeTurn(defaultPlan='order')

    if plan[0] is None:
        print('All the matched puzzle pieces have been in position. No move.')
        FINISHED = True
    else:

        piece_id = plan[0][0]
        piece_index = plan[0][1]
        action_type = plan[0][2]
        action = plan[0][3]

        if action_type == 'rotate':
            print(f'Rotate piece {piece_id} by {int(action)} degree')
            theSolver.current.pieces[piece_index] = theSolver.current.pieces[piece_index].rotatePiece(
                action)
        elif action_type == 'move':
            print(f'Move piece {piece_id} by {action}')
            theSolver.current.pieces[piece_index].setPlacement(action, offset=True)

    i = i + 1

plt.ioff()
# plt.draw()

if saveMe:
    # Build GIF
    with imageio.get_writer(cpath + f'/data/basic02.gif', mode='I', fps=1) as writer:
        filename_list = glob.glob(cpath + f'/data/basic02_step*.png')
        filename_list.sort()
        for filename in filename_list:
            image = imageio.imread(filename)
            writer.append_data(image)

#
# ============================ basic02_simple ===========================
