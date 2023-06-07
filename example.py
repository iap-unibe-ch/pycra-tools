import graspy as gr
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TKAgg')
import os

os.chdir('/storage/basin/work/AWS/aws_grasp/AWS_12_22/reduced_struct_2/ps_1/scan_angle_1')
# test = gr.GridFile(["farfield_54.grd", "farfield_89.grd", "farfield_183.grd"])
# print(test.data)
# test.power()
test = gr.GridFile(["far_uv_89.grd", "far_uv_183.grd"])
test.co_cross()
fig, ax, con = test.plotcont(test.data.co_dB[:, :, 0])
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)
plt.show()
# test2 = gr.CutFile(["cut_54.cut"])
