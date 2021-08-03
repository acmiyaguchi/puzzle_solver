#========================= puzzle.piece.template =========================
#
# @brief    The base class for puzzle piece specification or description
#           encapsulation. This simply stores the template image and
#           related data for a puzzle piece in its canonical
#           orientation.
#
#========================= puzzle.piece.template =========================

#
# @file     template.py
#
# @author   Patricio A. Vela,       pvela@gatech.edu
#           Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/07/24 [created]
#           2021/07/28 [modified]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#========================= puzzle.piece.template =========================

#============================= Dependencies ==============================

import numpy as np
from dataclasses import dataclass

import matplotlib.pyplot as plt

#=========================== Helper Components ===========================

@dataclass
class puzzleTemplate:
  size:    np.ndarray = np.array([])   # @< tight bbox size of puzzle piece image.
  rcoords: np.ndarray = np.array([])  # @< Puzzle piece linear image coordinates.
  appear:  np.ndarray = np.array([])  # @< Puzzle piece linear color/appearance.
  image:   np.ndarray = np.array([],dtype='uint8')  # @< Template image with BG default fill.
  mask:     np.ndarray = np.array([],dtype='uint8') # @< Template mask.
#
#========================= puzzle.piece.template =========================
#

class template:

  #================================ base ===============================
  #
  # @brief  Constructor for the puzzle.piece.base class.
  #
  def __init__(self, y = None, r = (0, 0)):
    self.y = y          # @< The puzzle piece template source data, if given. It is a class instance, see puzzleTemplate
    self.rLoc = np.array(r)       # @< The puzzle piece location in the whole image.

    # self.pLoc = p       # @< The puzzle piece discrete grid piece coordinates.
    # @note     Opting not to use discrete grid puzzle piece description.
    # @note     Excluding orientation for now. Can add later. Or sub-class it.

  #================================ size ===============================
  #
  # @brief  Returns the dimensions of the puzzle piece image.
  #
  def size(self):
    return self.y.size

  #================================ setMeasurement ===============================
  #
  # @brief  Pass along to the instance a measurement of the puzzle
  #         piece.
  #
  # @param[in]  thePiece    A measurement of the puzzle piece.
  #
  def setMeasurement(self, thePiece):

    self.y = thePiece.y
    self.rLoc = thePiece.rLoc


  #============================== setSource ============================
  #
  # @brief  Pass along the source data describing the puzzle piece.
  #
  def setSource(self, y, r = None):
    self.y = y

    if r:
      self.r = r

  #============================ setPlacement ===========================
  #
  # @brief  Provide pixel placement location information.
  #
  # @param[in]  r           Location of its frame origin. 
  # @param[in]  isCenter    Boolean indicating r is center instead.
  #
  def setPlacement(self, r, isCenter = False):
    if isCenter:
      self.rLoc = r - np.ceil(self.y.size/2)
    else:
      self.rLoc = r

  #============================ placeInImage ===========================
  #
  # @brief  Insert the puzzle piece into the image at the given location.
  #
  # @param[in]  theImage    The source image to put puzzle piece into.
  #
  def placeInImage(self, theImage, offset=[0,0]):

    # Remap coordinates from own image sprite coordinates to bigger
    # image coordinates.
    rcoords = np.array(offset).reshape(-1,1) +  self.rLoc.reshape(-1,1) + self.y.rcoords

    # Dump color/appearance information into the image (It will override the original image).
    theImage[rcoords[1], rcoords[0], :] = self.y.appear

    # @todo
    # FOR NOW JUST PROGRAM WITHOUT ORIENTATION CHANGE. LATER, INCLUDE THAT
    # OPTION.  IT WILL BE A LITTLE MORE INVOLVED. WOULD REQUIRE HAVING A
    # ROTATED IMAGE TEMPLATE AS A MEMBER VARIABLE.

  #============================ placeInImageAt ===========================
  #
  # @brief  Insert the puzzle piece into the image at the given location.
  #         
  # @param[in]  theImage    The source image to put puzzle piece into.
  # @param[in]  rc          The coordinate location.
  # @param[in]  theta       The orientation of the puzzle piece (default = 0).
  #
  def placeInImageAt(self, theImage, rc, theta = 0, isCenter = False):

    if not theta:
      theta = 0

    # If specification is at center, then compute offset to top-left corner.
    if isCenter:
      rc = rc - np.ceil(self.y.size / 2)

    # Remap coordinates from own image sprite coordinates to bigger image coordinates.
    rcoords = rc.reshape(-1,1) + self.y.rcoords

    # Dump color/appearance information into the image.
    theImage[rcoords[1], rcoords[0], :] = self.y.appear

    # @todo
    # FOR NOW JUST PROGRAM WITHOUT ORIENTATION CHANGE. LATER, INCLUDE THAT
    # OPTION.  IT WILL BE A LITTLE MORE INVOLVED.

  #============================== display ==============================
  #
  # @brief  Display the puzzle piece contents in an image window.
  #
  # @param[in]  fh  The figure label/handle if available. (optional)
  #
  # @param[out] fh  The handle of the image.
  #
  def display(self, fh = None):
    if fh:
      # See https://stackoverflow.com/a/7987462/5269146
      fh = plt.figure(fh.number)
      # See https://stackoverflow.com/questions/13384653/imshow-extent-and-aspect
    else:
      fh = plt.figure()

    # plt.imshow(self.y.image, extent = [0, 1, 0, 1])
    plt.imshow(self.y.image)
    plt.show()

    return fh

  #======================= buildFromMaskAndImage =======================
  #
  # @brief  Given a mask (individual) and an image of same base dimensions, use to
  #         instantiate a puzzle piece template.
  #
  # @param[in]  theMask    The individual mask.
  # @param[in]  theImage   The source image.
  # @param[in]  rLoc       The puzzle piece location in the whole image.
  #
  # @param[out] thePiece   The puzzle piece instance.
  #
  @staticmethod
  def buildFromMaskAndImage(theMask, theImage, rLoc = None):

    y = puzzleTemplate()

    # Populate dimensions.
    # Updated to OpenCV style
    y.size = [theMask.shape[1], theMask.shape[0]]

    y.mask = theMask.astype('uint8')

    y.rcoords = list(np.nonzero(theMask)) # 2 (row,col) x N
    # Updated to OpenCV style -> (x,y)
    y.rcoords[0], y.rcoords[1] = y.rcoords[1], y.rcoords[0]
    y.appear = theImage[y.rcoords[1],y.rcoords[0], :]
    # Store template image.
    # @note
    # For now, not concerned about bad image data outside of mask.
    y.image = theImage

    if not rLoc:
      thePiece = template(y)
    else:
      thePiece = template(y, rLoc)

    return thePiece

#
#========================= puzzle.piece.template =========================
