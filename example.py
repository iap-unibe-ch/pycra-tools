import graspy as gr
import matplotlib.pyplot as plt
import matplotlib as mpl
mpl.use('TKAgg')
import os

# os.chdir('/storage/basin/work/AWS/aws_grasp/AWS_12_22/complete_rot_far/ps_1/scan_angle_1')
# test = gr.GridFile(["farfield_54.grd", "farfield_89.grd", "farfield_183.grd"])
# print(test.data)
# test.power()
test = gr.GridFile(["farfield_183.grd"])
test.co_cross()
fig, ax, con = test.plotcont(test.data.co_dB[:, :, 0])
ax.set_xlim(-5, 5)
ax.set_ylim(-5, 5)
plt.show()
# test2 = gr.CutFile(["cut_54.cut"])
