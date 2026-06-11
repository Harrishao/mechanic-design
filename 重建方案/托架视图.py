# -*- coding: utf-8 -*-
"""粉筛托架 前视图(XY) + 上视图(XZ) 建模参考图  位置基准：装料位(托架销X=+42)"""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, Circle, Arc

HERE = os.path.dirname(os.path.abspath(__file__))
fp = "/sessions/modest-dazzling-cori/.local/lib/python3.10/site-packages/mplfonts/fonts/NotoSansCJKsc-Regular.otf"
fm.fontManager.addfont(fp); plt.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False

# ---- 几何（装料位）----
XL, XR   = -27.0, 28.0      # 托架本体 X (长55, 前缘=推卸前缘 X=+28)
YB, YT   = 216.0, 230.0     # 厚14
ZB, ZF   = -30.0, 30.0      # 宽60 (Z, +Z为前)
HX0, HX1 = -18.0, 18.0      # 筛口 X (36)
HZ0, HZ1 = -20.0, 20.0      # 筛口 Z (40)
PIN      = np.array([42.0, 223.0])  # 销孔轴心 (X,Y), 轴线沿Z, d8
EZ0, EZ1 = 41.0, 49.0       # 耳板 Z (厚8, 中面 Z=+45)
NX0, NX1 = 8.0, 28.0        # 连接颈 X
NZ0, NZ1 = 30.0, 41.0       # 连接颈 Z
EX0, EX1 = 8.0, 49.0        # 耳板 X (端部 R7 圆头, 圆心=销孔轴心)
R7, R4   = 7.0, 4.0

def dim_h(ax, x0, x1, y, txt, dy=3, fs=8.5, c="#1a6b1a"):
    ax.annotate("", (x0, y), (x1, y), arrowprops=dict(arrowstyle="<->", color=c, lw=.9))
    ax.text((x0+x1)/2, y+dy, txt, ha="center", fontsize=fs, color=c)
def dim_v(ax, y0, y1, x, txt, dx=3, fs=8.5, c="#1a6b1a", rot=90):
    ax.annotate("", (x, y0), (x, y1), arrowprops=dict(arrowstyle="<->", color=c, lw=.9))
    ax.text(x+dx, (y0+y1)/2, txt, va="center", fontsize=fs, color=c, rotation=rot)

fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 10.5), sharex=True,
                             gridspec_kw=dict(height_ratios=[1, 1.15]))

# ================= 前视图 (XY, 视向 -Z) =================
a1.plot([-130, 130],[216,216], color="#8a6d3b", lw=2, zorder=1)
a1.text(-128, 211, "台面 Y=216", fontsize=8.5, color="#8a6d3b")
# 本体
a1.add_patch(Rectangle((XL,YB), XR-XL, YT-YB, fc="#e2d9c8", ec="k", lw=1.4, zorder=3))
# 筛口（Y向通孔 → 前视为虚线轮廓）
a1.plot([HX0,HX0],[YB,YT], "k--", lw=1, zorder=4); a1.plot([HX1,HX1],[YB,YT], "k--", lw=1, zorder=4)
# 耳板（位于前侧 Z=41~49, 前视可见, 实线）+ 连接颈（被本体遮挡部分略）
a1.add_patch(Rectangle((XR,YB), EX1-XR-R7+R7, 0, fc="none"))  # 占位
a1.plot([XR, PIN[0]],[YT,YT], "k-", lw=1.4, zorder=5)
a1.plot([XR, PIN[0]],[YB,YB], "k-", lw=1.4, zorder=5)
arc = Arc(PIN, 2*R7, 2*R7, theta1=-90, theta2=90, lw=1.4, color="k", zorder=5)
a1.add_patch(arc)
a1.add_patch(Circle(PIN, R4, fc="white", ec="k", lw=1.2, zorder=6))
a1.plot([PIN[0]-7,PIN[0]+7],[PIN[1],PIN[1]], "k-.", lw=.6, zorder=6)
a1.plot([PIN[0],PIN[0]],[PIN[1]-7,PIN[1]+7], "k-.", lw=.6, zorder=6)
a1.annotate("销孔 φ8 通孔\n轴心 (42, 223)，轴线沿Z", (PIN[0]+12, PIN[1]+10), fontsize=9)
# 左停位虚影
a1.add_patch(Rectangle((XL-48,YB), XR-XL, YT-YB, fc="none", ec="#999", lw=1, ls="--", zorder=2))
a1.text(XL-46, YT+3, "左停位（整体左移48）", fontsize=8, color="#777")
# 尺寸
dim_h(a1, XL, XR, YT+12, "55")
dim_h(a1, HX0, HX1, YB-9, "筛口 36", dy=-7)
dim_h(a1, HX1, XR, YB-9, "10", dy=-7)
dim_h(a1, XL, HX0, YB-9, "9", dy=-7)
dim_h(a1, XR, PIN[0], YT+12, "14")
dim_v(a1, YB, YT, XL-10, "14")
dim_v(a1, YB, PIN[1], PIN[0]+22, "7", rot=0)
a1.text(0, 222.2, "(筛口中心X=0\n正对型腔)", ha="center", fontsize=8, color="#555")
a1.plot([0,0],[206,238], color="#aaa", lw=.7, ls="-.")
a1.set_title("前视图（XY平面，视向 −Z）  装料位：前缘X=+28, 本体X −27~+28", fontsize=11)
a1.set_ylabel("Y (mm)"); a1.set_ylim(200, 248); a1.set_aspect("equal"); a1.grid(alpha=.25, lw=.5)

# ================= 上视图 (XZ, 视向 -Y, +Z 画向下方便对照前视) =================
# 注: 绘图纵轴取 Z, 上为 +Z(前)
a2.add_patch(Rectangle((XL,ZB), XR-XL, ZF-ZB, fc="#e2d9c8", ec="k", lw=1.4, zorder=3))
a2.add_patch(Rectangle((HX0,HZ0), HX1-HX0, HZ1-HZ0, fc="white", ec="k", lw=1.2, zorder=4))
a2.text(0, 0, "筛口 36×40\n(上下通)", ha="center", va="center", fontsize=9)
# 连接颈
a2.add_patch(Rectangle((NX0,NZ0), NX1-NX0, NZ1-NZ0, fc="#d5cdbc", ec="k", lw=1.2, zorder=3))
# 耳板（圆头）
a2.add_patch(Rectangle((EX0,EZ0), PIN[0]-EX0, EZ1-EZ0, fc="#cfc7b6", ec="k", lw=1.2, zorder=3))
a2.plot([PIN[0],PIN[0]+R7],[EZ0,EZ0],"k-",lw=1.2); a2.plot([PIN[0],PIN[0]+R7],[EZ1,EZ1],"k-",lw=1.2)
a2.plot([PIN[0]+R7,PIN[0]+R7],[EZ0,EZ1],"k-",lw=1.2)
# 销孔(轴线沿Z, 上视为虚线)
a2.plot([PIN[0]-R4,PIN[0]-R4],[EZ0,EZ1],"k--",lw=1); a2.plot([PIN[0]+R4,PIN[0]+R4],[EZ0,EZ1],"k--",lw=1)
a2.plot([PIN[0],PIN[0]],[EZ0-6,EZ1+6],"k-.",lw=.6)
a2.annotate("耳板 厚8\nZ=+41~+49 (中面+45)", (PIN[0]+14, 44), fontsize=9)
a2.annotate("连接颈 20×11\n(X 8~28, Z 30~41)", (NX0-66, 33), fontsize=8.5)
# 尺寸
dim_h(a2, XL, XR, ZB-8, "55", dy=-7)
dim_h(a2, HX0, HX1, HZ0+6, "36", dy=2)
dim_v(a2, ZB, ZF, XL-10, "60")
dim_v(a2, HZ0, HZ1, HX0+6, "40", dx=-9)
dim_v(a2, ZF, EZ1, XR+34, "19", rot=0)
dim_v(a2, ZB, HZ0, XL+5, "10", dx=-1, rot=0)
dim_v(a2, HZ1, ZF, XL+5, "10", dx=-1, rot=0)
a2.plot([0,0],[ZB-14, EZ1+10], color="#aaa", lw=.7, ls="-.")
a2.text(-126, 36, "+Z = 前侧(耳板/连杆侧)\n连杆运动平面 Z≈+45\n冲头/型腔位于 Z=0±20 → 错开", fontsize=8.5,
        bbox=dict(fc="white", ec="#888", lw=.6, pad=2))
a2.set_title("上视图（XZ平面，视向 −Y）", fontsize=11)
a2.set_xlabel("X (mm)"); a2.set_ylabel("Z (mm)")
a2.set_xlim(-135, 135); a2.set_ylim(-50, 62); a2.set_aspect("equal"); a2.grid(alpha=.25, lw=.5)

fig.suptitle("粉筛托架 建模参考图（装料位，托架销 X=+42；行程48 → 左停位销 X=−6）", fontsize=12)
fig.tight_layout(rect=[0,0,1,0.965])
fig.savefig(os.path.join(HERE, "参考图_托架视图.png"), dpi=170)
print("托架视图 OK")
