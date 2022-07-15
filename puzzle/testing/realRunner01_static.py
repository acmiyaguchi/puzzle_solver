#!/usr/bin/python
"""

    @brief:             Test and update the puzzle solver planner function on the real world data.
                        The motivation for this test is the limit of the performance stability in the real system testing scenerio.
                        Hence, this can be treated as an augmentation of the previous real-world unit test for the robustness.

                        The test focus on the puzzle solving planner, rather than the activity-related functions.
    
    @author:            Yiye Chen,          yychen2019@gatech.edu
    @date:              07/14/2022[created]

"""

# ===[0] prepare Dependencies
from argparse import ArgumentParser
import os, sys
from copy import deepcopy

import rosbag
from cv_bridge import CvBridge
import matplotlib.pyplot as plt
import cv2

# display
from camera.utils.display import display_images_cv

# surveillance
from utils.survRunner import SurvRunner

# puzzle solver
from puzzle.piece.template import Template
from puzzle.runner import ParamRunner, RealSolver
from puzzle.simulator.basic import Basic

# ===[1] Get arguments
def get_args():
    parse = ArgumentParser("The arguments for the puzzle solving planner real world unit test")
    parse.add_argument("--root_data_folder", type=str, default="./data_rosbag/Testing/Yiye/robot_puzzle",
                        help="The root of the rosbag test data.")
    parse.add_argument("--piece_num", default=9, type=int, 
                        help="The number of pieces. For determining the test cases")
    parse.add_argument("--shuffleRot", action="store_true",
                        help="Add shuffle and rotation or not. For determining the test cases")

    args = parse.parse_args()
    return args

def parse_args(args):
    args.data_folder = os.path.join(args.root_data_folder, "pieces_{}".format(args.piece_num))
    args.sol_path = os.path.join(args.data_folder, "sol{}.obj".format(args.piece_num))
    post_fix = "noShuffleRot" if not args.shuffleRot else "yesShuffleRot"
    args.test_data_path = os.path.join(args.data_folder, "static_{}.bag".format(post_fix))

    return args

args = get_args()
args = parse_args(args)

# ===[2] Prepare data
bridge = CvBridge()
test_rosbag = rosbag.Bag(args.test_data_path)
test_data_path = args.test_data_path
sol_path = args.sol_path

# get the depth scale
depth_scale = None
for topic, msg, t in test_rosbag.read_messages(["/depth_scale"]):
    depth_scale = msg.data
assert depth_scale is not None, "Depth scale is not read."

# get an example data
rgb_example = None
dep_example = None
for topic, msg, t in test_rosbag.read_messages(["/test_rgb", "/test_dep"]):
    if topic == "/test_rgb":
        rgb_example = bridge.imgmsg_to_cv2(msg)[:,:,::-1]
    elif topic == "/test_dep":
        dep_example = bridge.imgmsg_to_cv2(msg) * depth_scale
    
    if rgb_example is not None and dep_example is not None:
        break


# ===[3] Prepare the models 

# surveillance for obtaining the puzzle layer
surv_args = {
    "rgb_topic": "/test_rgb",
    "dep_topic": "/test_dep",
    "reCalibrate": False,
    "calib_data_path": test_data_path 
}
surv_runner = SurvRunner(surv_args=surv_args)

# puzzle solver
configs_puzzleSolver = ParamRunner(
    areaThresholdLower=1000, # @< The area threshold (lower) for the individual puzzle piece.
    areaThresholdUpper=8000, # @< The area threshold (upper) for the individual puzzle piece.
    pieceConstructor=Template,
    lengthThresholdLower=1000,
    BoudingboxThresh=(20, 100), # @< The bounding box threshold for the size of the individual puzzle piece.
    tauDist=100, # @< The radius distance determining if one piece is at the right position.
    hand_radius=200, # @< The radius distance to the hand center determining the near-by pieces.
    tracking_life_thresh=15, # @< Tracking life for the pieces, it should be set according to the processing speed.
    # solution_area=[600,800,400,650], # @< The solution area, [xmin, xmax, ymin, ymax]. We will perform frame difference in this area to locate the touching pieces.
    # It is set by the calibration result of the solution board.
)
puzzle_solver = RealSolver(configs_puzzleSolver)

# puzzle solver - set solution board
puzzle_solver.setSolBoard(rgb_example, sol_path)
solImg = puzzle_solver.bSolImage
plt.figure()
plt.title("The solution board")
plt.imshow(solImg)
plt.show()


# ===[4] Run
rgb = None
dep = None
for topic, msg, t in test_rosbag.read_messages(["/test_rgb", "/test_depth"]):

    # ----- Read data
    if topic == "/test_rgb":
        rgb = bridge.imgmsg_to_cv2(msg)
    elif topic == "/test_depth":
        dep = bridge.imgmsg_to_cv2(msg) * depth_scale

    # if either is None, then continue to read data 
    if rgb is None or dep is None: 
        continue
    
    # ----- If obtained both modalities, process the data

    # surveillance
    surv_runner.process(rgb, dep)

    # get the puzzle layer info
    puzzle_mask = surv_runner.surv.scene_interpreter.get_layer("puzzle", mask_only=True, BEV_rectify=False)
    puzzle_layer = surv_runner.surv.scene_interpreter.get_layer("puzzle", mask_only=False, BEV_rectify=False)
    puzzle_layer_BEV = surv_runner.surv.scene_interpreter.get_layer("puzzle", mask_only=False, BEV_rectify=True)
    puzzle_trackers = surv_runner.surv.scene_interpreter.get_trackers("puzzle", BEV_rectify=False)
    human_layer = surv_runner.surv.scene_interpreter.get_layer("human", mask_only=False, BEV_rectify=False)

    # plan
    postImg = surv_runner.surv.meaBoardImg
    visibleMask = surv_runner.surv.visibleMask
    hTracker_BEV = surv_runner.surv.scene_interpreter.get_trackers("human", BEV_rectify=True)  # (2, 1)
        
    plans = puzzle_solver.process(postImg, visibleMask, hTracker_BEV, verbose=False)

    # simulate the plan
    meaBoard = puzzle_solver.getMeaBoard()
    theSim = Basic(deepcopy(meaBoard))
    for plan in plans:
        theSim.takeAction([plan])
    img_assemble = theSim.toImage()

    # visualize
    #display_images_cv([rgb[:,:,::-1]], ratio=0.6, window_name="The test rgb frame")
    #display_images_cv([img_assemble])
    #opKey = cv2.waitKey(1)

    fh, (ax1, ax2) = plt.subplots(1, 2)
    ax1.imshow(rgb)
    ax1.set_title("THe test rgb frame")

    ax2.imshow(img_assemble)
    ax2.set_title("THe simulated assembly result")

    plt.show()

    # reset
    rgb = None
    dep = None
    