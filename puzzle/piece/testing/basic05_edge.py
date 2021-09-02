#!/usr/bin/python3
#============================ basic05_edge ===========================
#
# @brief    Test script for the most basic functionality of edge matcher
#           for regular puzzle pieces. (60p img)
#
#============================ basic05_edge ===========================

#
# @file     basic05_edge.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/09/01  [created]
#
#============================ basic05_edge ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
from copy import deepcopy

from puzzle.utils.imageProcessing import cropImage

import improcessor.basic as improcessor
import similaritymeasures

from puzzle.parser.fromSketch import fromSketch
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.piece.regular import regular

from puzzle.builder.gridded import gridded, paramGrid

from puzzle.piece.edge import edge

from puzzle.board import board

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_60p_AdSt408534841.png')
theImageSol = cropImage(theImageSol, theMaskSol_src)


#==[1.1] Create an improcesser to obtain the mask.
#

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(theMaskSol_src.copy())
theMaskSol = theDet.getState().x

#==[1.2] Extract info from theImage & theMask to obtain a board instance
#
theLayer = fromLayer(paramPuzzle(areaThreshold=5000))

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()


#==[2] Create an Grid instance and explode it into two new boards
#

print('Running through test cases. Will take a bit.')

theGrid = gridded.buildFrom_ImageAndMask(theImageSol, theMaskSol, theParams=paramGrid(areaThreshold=5000, pieceConstructor=regular))

epImage, epBoard = theGrid.explodedPuzzle(dx=100,dy=100)


#==[2.1] Create a new Grid instance from the images
#

# @note
# Not a fair game to directly use the epBoard
# Instead, should restart from images

improc = improcessor.basic(cv2.cvtColor, (cv2.COLOR_BGR2GRAY,),
                  improcessor.basic.thresh, ((5,255,cv2.THRESH_BINARY),),
                  cv2.GaussianBlur, ((3, 3), 0,),
                  cv2.Canny, (30, 200,),
                  improcessor.basic.thresh, ((10,255,cv2.THRESH_BINARY),))

theDet = fromSketch(improc)
theDet.process(epImage.copy())
theMaskSol_new = theDet.getState().x

theGrid_new = gridded.buildFrom_ImageAndMask(epImage, theMaskSol_new, theParams=paramGrid(areaThreshold=1000, pieceConstructor=regular))


#==[1.3] Focus on a single puzzle piece and duplicate it with a new location
#

theRegular_A = regular(theBoardSol.pieces[36])
theRegular_B = theGrid_new.solution.pieces[36]

#==[2] Create a new board
#
theBoard = board()
theBoard.addPiece(theRegular_A)
theBoard.addPiece(theRegular_B)

#==[3] Create an edge matcher
#

theMatcher = edge()

#==[4] Display the new board and the comparison result.
#
print('Should see True.')
print(theMatcher.compare(theRegular_A, theRegular_B,method=similaritymeasures.pcm))

theBoard.display()

plt.show()

#
#============================ basic05_edge ===========================
