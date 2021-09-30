# ================================ puzzle.piece.edge ================================
#
# @brief    Uses edge features to establish similarity.
#
# ================================ puzzle.piece.edge ================================

#
# @file     edge.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/26 [created]
#
#
# ================================ puzzle.piece.edge ================================

# ===== Environment / Dependencies
#
import cv2
import numpy as np

from puzzle.piece.matchDifferent import matchDifferent
from puzzle.piece.regular import regular


#
# ================================ puzzle.piece.edge ================================
#
class edge(matchDifferent):

    def __init__(self, tau_shape=100, tau_color=400):
        """
        @brief  Constructor for the puzzle piece edge class.
                150 for lab space/400 for RGB space
        Args:
            tau_shape: The threshold for the shape feature.
            tau_color: The threshold for the color feature.
        """

        super(edge, self).__init__()

        self.tau_shape = tau_shape
        self.tau_color = tau_color

    @staticmethod
    def shapeFeaExtract(piece, method=None):
        """
        @brief  Extract the edge shape feature from an input image of the edge.

        Args:
            edge: An EdgeDes instance.
            method: The comparison method, we have two modes: type or shape coords.

        Returns:
            Shape feature.
        """

        shapeFea = []
        for i in range(4):
            if method == 'type':
                shapeFea.append(piece.edge[i].type)
            else:
                y, x = np.nonzero(piece.edge[i].mask)
                coords = np.hstack((x.reshape(-1, 1), y.reshape(-1, 1)))
                shapeFea.append(coords)

        shapeFea = np.array(shapeFea)

        return shapeFea

    @staticmethod
    def colorFeaExtract(piece, feaLength=300):
        """
        @brief  Extract the edge color feature from an input image of the edge.

        Args:
            edge:  An EdgeDes instance.
            feaLength: The resized feature vector length setting.

        Returns:
            The resized feature vector.
        """

        feaResize = []
        for i in range(4):
            y, x = np.nonzero(piece.edge[i].mask)

            # Extract the valid pts
            pts = piece.edge[i].image[y, x]

            # Expand dim for further processing
            feaOri = np.expand_dims(pts, axis=0)

            # Resize to a unit length
            feaResize.append(cv2.resize(feaOri, (feaLength, 1)).flatten())

            # # # @todo Yunzhi: May need to double check the color space
            # feaResize = cv2.cvtColor(feaResize, cv2.COLOR_RGB2Lab)

        feaResize = np.array(feaResize, dtype='float32')

        return feaResize

    def process(self, piece, method=None):
        """
        @brief  Compute features from the data.

        Args:
            piece: A puzzle piece instance.
            method: The method option.

        Returns:
            The shape & color feature vectors.
        """

        feature_shape = edge.shapeFeaExtract(piece, method=method)
        feature_color = edge.colorFeaExtract(piece)

        return list(zip(feature_shape, feature_color))

    def score(self, piece_A, piece_B, method='type'):
        """
        @brief  Compute the score between two passed puzzle piece data.

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.
            method: We use some built-in functions in similaritymeasures
                    (pcm/frechet_dist/area_between_two_curves/curve_length_measure/dtw)
                    or just the types of the edges.

        Returns:
            The shape & color distance between the two passed data.
        """

        def dis_shape(feature_shape_A, feature_shape_B, method=method):

            if method == 'type':
                if feature_shape_A == feature_shape_B:
                    distance = 0
                else:
                    distance = float('inf')
            else:
                distance = method(feature_shape_A, feature_shape_B)
            # For dtw
            if isinstance(distance, tuple):
                distance = distance[0]
            return distance

        def dis_color(feature_color_A, feature_color_B):

            # distance = np.mean(np.sum((feature_color_A[0] - feature_color_B[0]) ** 2, axis=1) ** (1. / 2))
            feature_color_A = feature_color_A.reshape(-1, 3)
            feature_color_B = feature_color_B.reshape(-1, 3)
            distance = np.mean(np.sum((feature_color_A - feature_color_B) ** 2, axis=1) ** (1. / 2))

            return distance

        distance_shape = []
        distance_color = []

        if type(piece_A) != type(piece_B):
            raise TypeError('Input should be of the same type.')
        else:
            if isinstance(piece_A, regular):

                ret_A = self.process(piece_A, method=method)
                ret_B = self.process(piece_B, method=method)
                for i in range(4):
                    distance_shape.append(dis_shape(ret_A[i][0], ret_B[i][0], method=method))
                    distance_color.append(dis_color(ret_A[i][1], ret_B[i][1]))

            else:
                raise TypeError('The input type is wrong. Need a template instance or a puzzleTemplate instance.')

        return distance_shape, distance_color

    def compare(self, piece_A, piece_B, method='type'):
        """
        @brief  Compare between two passed puzzle piece data.

        Args:
            piece_A: A template instance saving a piece's info.
            piece_B: A template instance saving a piece's info.
            method: The method option.

        Returns:
            The comparison result.
        """

        # score is to calculate the similarity while it will call the feature extraction process inside
        distance_shape, distance_color = self.score(piece_A, piece_B, method=method)

        if (np.array(distance_shape) < self.tau_shape).all() and (np.array(distance_color) < self.tau_color).all():
            return True
        else:
            return False

#
# ================================ puzzle.piece.edge ================================
