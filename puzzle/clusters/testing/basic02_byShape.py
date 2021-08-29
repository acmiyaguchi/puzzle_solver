#!/usr/bin/python3
#============================ basic02_byShape ===========================
#
# @brief    Test script for basic functionality of byShape
#
#============================ basic02_byShape ===========================

#
# @file     basic02_byShape.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/29  [created]
#
#============================ basic02_byShape ===========================


#==[0] Prep environment
import matplotlib.pyplot as plt
import numpy as np
import os
import cv2
import imageio
import glob

import improcessor.basic as improcessor
from puzzle.parser.fromSketch import fromSketch
from puzzle.parser.fromLayer import fromLayer, paramPuzzle
from puzzle.builder.gridded import gridded, paramGrid

from puzzle.piece.regular import regular

from puzzle.clusters.byShape import byShape

fpath = os.path.realpath(__file__)
cpath = fpath.rsplit('/', 1)[0]

#==[1] Read the source image and template.
#
theImageSol = cv2.imread(cpath + '/../../testing/data/balloon.png')
theImageSol = cv2.cvtColor(theImageSol, cv2.COLOR_BGR2RGB)

theMaskSol_src = cv2.imread(cpath + '/../../testing/data/puzzle_15p_123rf.png')


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
theLayer = fromLayer(paramPuzzle(areaThreshold=5000,pieceConstructor=regular))

theLayer.process(theImageSol,theMaskSol)
theBoardSol = theLayer.getState()

# plt.show()

#==[2] Create a cluster instance and process the puzzle board.
#

theShapeCluster = byShape(theBoardSol)
theShapeCluster.process()

#==[3] Display the extracted features.
#

print('Should see 15 pieces, each of them will have 4 features.')
print('The number of pieces:', len(theShapeCluster.feature))
print('The number of features for each piece:', len(theShapeCluster.feature[0]))

#
#============================ basic02_byShape ===========================
