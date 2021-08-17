#====================== puzzle.utils.dataProcessing ======================
#
# @brief    Some data processing functions.
#
#====================== puzzle.utils.dataProcessing ======================

#
# @file     dataProcessing.py
#
# @author   Yunzhi Lin,             yunzhi.lin@gatech.edu
# @date     2021/08/09 [created]
#
#!NOTE:
#!  Indent is set to 2 spaces.
#!  Tab is set to 4 spaces with conversion to spaces.
#
#====================== puzzle.utils.dataProcessing ======================


#===== Environment / Dependencies
#
import numpy as np
import types

#====================== puzzle.utils.dataProcessing ======================
#
# ================================ updateLabel ==============================
#
# @brief  Update the label according to the ranking of all the elements'
#         (with the same label) mean value.
#         E.g., x_list = [28,137,263,269,33,151] / x_label = [2,3,1,1,2,3] ->
#         x_label_updated = [0,1,2,2,0,1]
#
#
# @param[in]  x_list   The value list.
# @param[in]  x_label  The original label.
#
# @param[out] x_label_updated The updated label.
#
def updateLabel(x_list, x_label):
  x_mean = []
  for label in range(1 , 1 +len(set(x_label))):
    x_mean.append(np.mean(x_list[np.where(x_label == label)]))
  x_rank = np.array(x_mean).argsort().argsort()

  x_zip = dict(zip(list(range(1 , 1 +len(x_mean))), x_rank))

  x_label_updated = list(map(x_zip.get ,x_label))

  return x_label_updated

# ================================ copyAttributes ==============================
#
# @brief  Copy attributes from a source class to a target class.
#         See https://stackoverflow.com/a/12014625/5269146.
#
# @param[in]  source   The source class instance.
# @param[in]  target   The target class instance.
#
# @param[out] target   The updated target class instance.
#
class copyAttributes(object):
    def __init__(self, source):
        self.source = source

    def __call__(self, target):
        for attr, value in self.source.__dict__.items():
            if attr.startswith('__'):
                continue
            if isinstance(value, (property, types.FunctionType)):
                continue
            setattr(target, attr, value)
        return target

#
#====================== puzzle.utils.dataProcessing ======================