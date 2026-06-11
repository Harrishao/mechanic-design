# -*- coding: utf-8 -*-
"""重建参考图绘制：上冲头/粉筛 机构布局、凸轮工作图、运动与压力角曲线、整机布局"""
import os, sys, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Circle, Rectangle, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
# 中文字体
for cand in ["/sessions/modest-dazzling-cori/.local/lib/python3.10/site-packages/mplfonts/fonts/NotoSansCJKsc-Regular.otf"]:
    if os.path.exists(cand):
        fm.fontManager.addfont(cand)
        plt.rcParams["font.family"] = fm.FontProperties(fname=cand).get_name()
plt.rcParams["axes.unicode_minus"] = False

# 运行计算脚本取得全部对象
exec(open(os.path.join(HERE, "计算脚本.py"), encoding="utf-8").read())

CJ = dict(color="#b22222", zorder=8)          # 铰点
def joint(ax, p, label=None, dx=4, dy=4, fs=8.5, r=2.2):
    ax.add_patch(Circle(p, r, fc="#b22222", ec="k", lw=.5, zorder=9))
    if label:
        ax.annotate(label, p, xytext=(p[0]+dx, p[1]+dy), fontsize=fs, zorder=10,
                    bbox=dict(fc="white", ec="none", alpha=.75, pad=1))
def bar(ax, p1, p2, w=2.8, c="#5a7d9a", ls="-", alpha=1, z=4):
    ax.plot([p1[0],p2[0]],[p1[1],p2[1]], lw=w, color=c, ls=ls,
            solid_capstyle="round", alpha=alpha, zorder=z)
def seglabel(ax, p1, p2, txt, off=(0,0), fs=8.5, c="#1a6b1a"):
    m = ((p1[0]+p2[0])/2+off[0], (p1[1]+p2[1])/2+off[1])
    ax.annotate(txt, m, fontsize=fs, color=c, ha="center",
                bbox=dict(fc="white", ec="none", alpha=.8, pad=1), zorder=10)

TIP45 = 45.0   # 冲头 φ34 段长
# ================= 图1：上冲头机构布局 =================
fig, ax = plt.subplots(figsize=(8.2, 13))
# 凸轮（装填位姿态=导出姿态）
pf = camU["prof"]
ax.fill(pf[:,0], pf[:,1], color="#c9d4dd", alpha=.9, zorder=2)
ax.plot(pf[:,0], pf[:,1], color="#48606f", lw=1.4, zorder=3)
th = np.linspace(0,2*np.pi,200)
ax.plot(R0U*np.cos(th), R0U*np.sin(th), ls=":", color="#777", lw=1, zorder=3)
ax.annotate(f"理论基圆 r0={R0U:.0f}", (-148, -62), fontsize=8.5, color="#555")
ax.annotate("上冲头凸轮(装填位姿态)\n实际廓线 r=42.0~68.9", (-160, 55), fontsize=9, color="#33424e")
# 主轴
ax.add_patch(Circle((0,0), 10, fc="white", ec="k", lw=1.2, zorder=6))
joint(ax, (0,0), "O1 主轴 (0,0)", dx=-105, dy=-16, fs=10)
# 两位姿
for pose, ls, al in [(pose_fill, "-", 1.0), (pose_press, "--", .55)]:
    B,Cc,Dd,E,P = [np.array(pose[k]) for k in ["B","C","D","E","P"]]
    bar(ax, O2, P, 4, "#5a7d9a", ls, al)            # 滚子臂
    bar(ax, O2, B, 4, "#5a7d9a", ls, al)            # 连杆臂
    ax.add_patch(Circle(P, RR, fc="none", ec="#8a4a4a", lw=1.4, ls=ls, alpha=al, zorder=5))
    bar(ax, B, Dd, 3, "#7a6a55", ls, al)            # 长连杆
    bar(ax, O3, Dd, 4, "#4a7a5a", ls, al)           # 上摆杆 D臂
    bar(ax, O3, Cc, 4, "#4a7a5a", ls, al)           # 上摆杆 C臂
    bar(ax, Cc, E, 3, "#7a6a55", ls, al)            # 小连杆
    # 冲头
    w34, w40 = 17, 20
    tipY = E[1] - Lp
    ax.add_patch(Rectangle((-w34, tipY), 2*w34, TIP45, fc="#d8dee4", ec="#48606f",
                 lw=1.1, ls=ls, alpha=al, zorder=4))
    ax.add_patch(Rectangle((-w40, tipY+TIP45), 2*w40, Lp-TIP45, fc="#d8dee4",
                 ec="#48606f", lw=1.1, ls=ls, alpha=al, zorder=4))
# 支点
joint(ax, O2, f"O2 下摆杆支点\n({O2[0]:.0f},{O2[1]:.0f})", dx=-12, dy=16, fs=9.5)
joint(ax, O3, f"O3 上摆杆支点\n({O3[0]:.0f},{O3[1]:.1f})", dx=14, dy=-6, fs=9.5)
ax.add_patch(Polygon([O2+(-9,-12),O2+(9,-12),O2], closed=True, fc="#999", ec="k", lw=.6, zorder=3))
ax.add_patch(Polygon([O3+(-9,-12),O3+(9,-12),O3], closed=True, fc="#999", ec="k", lw=.6, zorder=3))
# 装填位关键点标注
pf_ = {k: np.array(pose_fill[k]) for k in ["B","C","D","E","P"]}
pp_ = {k: np.array(pose_press[k]) for k in ["B","C","D","E","P"]}
joint(ax, pf_["P"], "滚子P ({:.1f},{:.1f})".format(pf_["P"][0], pf_["P"][1]), dx=18, dy=-30, fs=8.5)
joint(ax, pf_["B"], f"B ({pf_['B'][0]:.1f},{pf_['B'][1]:.1f})", dx=8, dy=-4)
joint(ax, pf_["D"], f"D ({pf_['D'][0]:.1f},{pf_['D'][1]:.1f})", dx=10, dy=-12)
joint(ax, pf_["C"], f"C ({pf_['C'][0]:.1f},{pf_['C'][1]:.1f})", dx=-78, dy=10)
joint(ax, pf_["E"], f"E 冲头销 (0,{pf_['E'][1]:.0f})", dx=-110, dy=-2)
joint(ax, pp_["E"], f"E' 保压位 (0,{pp_['E'][1]:.0f})", dx=24, dy=-6)
# 长度标注
seglabel(ax, O2, pf_["P"], f"Lr={Lr:.0f}", off=(-16,-8))
seglabel(ax, O2, pf_["B"], f"LB={LB:.0f}", off=(0,-12))
seglabel(ax, pf_["B"], pf_["D"], f"连杆 L1={L1:.1f}", off=(16,0))
seglabel(ax, O3, pf_["D"], f"R3={R3:.0f}", off=(8,14))
seglabel(ax, O3, pf_["C"], f"R3p={R3p:.0f}", off=(10,12))
seglabel(ax, pf_["C"], pf_["E"], f"小连杆 L2={L2:.0f}", off=(40,6))
ax.annotate(f"冲头销E→尖端 Lp={Lp:.0f}\n尖端: 装填Y=300 / 保压Y=205\n行程=95", (30, 255),
            fontsize=9, color="#1a6b1a", bbox=dict(fc="white", ec="#1a6b1a", lw=.6, pad=2))
# 型腔与台面
ax.add_patch(Rectangle((-17,186), 34, 30, fc="none", ec="#333", lw=1.4, hatch="//", zorder=3))
ax.plot([-120,-17],[216,216], color="#8a6d3b", lw=2.5, zorder=2)
ax.plot([17,150],[216,216], color="#8a6d3b", lw=2.5, zorder=2)
ax.annotate("型腔 φ34×30  顶面Y=216", (-150,168), fontsize=9, color="#333")
ax.annotate("台面 Y=216", (60,202), fontsize=8.5, color="#8a6d3b")
# 导向套建议
ax.add_patch(Rectangle((-26,308), 52, 50, fc="none", ec="#666", lw=1, ls="-."))
ax.annotate("导向套(φ40)建议\nY=308~358", (-128,320), fontsize=8.5, color="#666")
ax.plot([0,0],[150,560], color="#aaa", lw=.7, ls="-.", zorder=1)
ax.set_title("上冲头机构 重建参考图（XY平面）\n实线=装填位(φ=0~120°)  虚线=保压位(φ=200~240°)  主轴逆时针",
             fontsize=11.5)
ax.set_xlim(-175, 300); ax.set_ylim(-110, 575)
ax.set_aspect("equal"); ax.grid(alpha=.25, lw=.5)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.tight_layout(); fig.savefig(os.path.join(HERE,"参考图_上冲头机构.png"), dpi=170)
plt.close(fig)
print("图1 OK")

# ================= 图2：粉筛机构布局 =================
fig, ax = plt.subplots(figsize=(11, 8.5))
pf2 = camS["prof"]
ax.fill(pf2[:,0], pf2[:,1], color="#d3dbc9", alpha=.9, zorder=2)
ax.plot(pf2[:,0], pf2[:,1], color="#5a6f48", lw=1.4, zorder=3)
ax.plot(R0S*np.cos(th), R0S*np.sin(th), ls=":", color="#777", lw=1, zorder=3)
ax.annotate(f"理论基圆 r0={R0S:.0f}", (20, -R0S-12), fontsize=8.5, color="#555")
ax.annotate("粉筛凸轮(装料位姿态=全升程)\n实际廓线 r=71.0~89.1", (8, 55), fontsize=9, color="#4a5a3a")
ax.add_patch(Circle((0,0), 10, fc="white", ec="k", lw=1.2, zorder=6))
joint(ax, (0,0), "O1 主轴 (0,0)", dx=12, dy=-20, fs=10)
TRAY_L, TRAY_T, HOLE = 55.0, 14.0, 36.0   # 托架长/厚, 筛口宽(运动向)
FRONT_GAP = 10.0                           # 筛口近边距推卸前缘
for pose, ls, al, tag in [(sp_fill, "-", 1.0, "装料位"), (sp_left, "--", .55, "左停位")]:
    B, Cc, P = np.array(pose["B"]), np.array(pose["C"]), np.array(pose["P"])
    bar(ax, O2s, P, 4, "#5a7d9a", ls, al)
    bar(ax, O2s, B, 4, "#5a7d9a", ls, al)
    ax.add_patch(Circle(P, RRs, fc="none", ec="#8a4a4a", lw=1.4, ls=ls, alpha=al, zorder=5))
    bar(ax, B, Cc, 3, "#7a6a55", ls, al)
    # 托架: 销在前耳板, 前缘 = 销X-14;  筛口近边 = 前缘-10, 筛口 36 宽
    front = Cc[0] - 14
    ax.add_patch(Rectangle((front-TRAY_L, 216), TRAY_L, TRAY_T, fc="#e2d9c8",
                 ec="#7a6a55", lw=1.2, ls=ls, alpha=al, zorder=4))
    hx = front - FRONT_GAP - HOLE
    ax.add_patch(Rectangle((hx, 216), HOLE, TRAY_T, fc="white", ec="#7a6a55",
                 lw=1, ls=ls, alpha=al, zorder=5))
joint(ax, O2s, f"O2 摆杆支点 ({O2s[0]:.0f},{O2s[1]:.0f})", dx=-66, dy=-26, fs=9.5)
ax.add_patch(Polygon([O2s+(-9,-12),O2s+(9,-12),O2s], closed=True, fc="#999", ec="k", lw=.6, zorder=3))
Bf, Cf, Pf = [np.array(sp_fill[k]) for k in ["B","C","P"]]
Bl, Cl, Pl = [np.array(sp_left[k]) for k in ["B","C","P"]]
joint(ax, Bf, "B ({:.1f},{:.1f})".format(*Bf), dx=6, dy=10)
joint(ax, Bl, "B' ({:.1f},{:.1f})".format(*Bl), dx=-66, dy=10)
joint(ax, Cf, "C 托架销 (42,223)", dx=10, dy=-22)
joint(ax, Cl, "C' (-6,223)", dx=-20, dy=24)
joint(ax, Pf, "滚子P ({:.1f},{:.1f})".format(*Pf), dx=8, dy=-20, fs=8.5)
seglabel(ax, O2s, Pf, f"Lr={Lrs:.0f}", off=(-26,-6))
seglabel(ax, O2s, Bf, f"Rb={Rbs:.0f}", off=(-26,0))
seglabel(ax, Bf, Cf, f"连杆 Ls={Ls:.1f}", off=(20,-16))
# 台面/型腔
ax.plot([-160,-17],[216,216], color="#8a6d3b", lw=2.5, zorder=2)
ax.plot([17,160],[216,216], color="#8a6d3b", lw=2.5, zorder=2)
ax.add_patch(Rectangle((-17,186), 34, 30, fc="none", ec="#333", lw=1.4, hatch="//", zorder=3))
ax.annotate("型腔 φ34 顶面Y=216", (-95,170), fontsize=9, color="#333")
ax.annotate("装料位: 筛口中心X=0 正对型腔\n托架行程=48 (销X: -6→42)\n台面Y=216, 销Y=223",
            (52,250), fontsize=9, color="#1a6b1a",
            bbox=dict(fc="white", ec="#1a6b1a", lw=.6, pad=2))
ax.plot([0,0],[150,290], color="#aaa", lw=.7, ls="-.", zorder=1)
ax.set_title("粉筛机构 重建参考图（XY平面）  实线=装料位(φ=0~90°)  虚线=左停位(φ=135~290°)\n"
             "注：粉筛连杆与托架耳板位于 Z≈+45 平面（托架前缘侧），与冲头平面错开", fontsize=11)
ax.set_xlim(-230, 200); ax.set_ylim(-130, 300)
ax.set_aspect("equal"); ax.grid(alpha=.25, lw=.5)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.tight_layout(); fig.savefig(os.path.join(HERE,"参考图_粉筛机构.png"), dpi=170)
plt.close(fig); print("图2 OK")

# ================= 图3：凸轮工作图 =================
fig, axs = plt.subplots(1, 2, figsize=(12.5, 6.6))
for axc, cam, r0, rr, Pj, ttl, rngtxt in [
    (axs[0], camU, R0U, RR, np.array(pose_fill["P"]),
     "上冲头凸轮 v2（装填位姿态）", "实际廓线 r=42.0~68.9  轮缘宽30  Z=67.5"),
    (axs[1], camS, R0S, RRs, np.array(sp_fill["P"]),
     "粉筛凸轮 v2（装料位姿态=全升程）", "实际廓线 r=71.0~89.1  轮缘宽20  Z=132.5")]:
    pr, pi = cam["prof"], cam["pitch"]
    axc.fill(pr[:,0], pr[:,1], color="#cfd8e0", alpha=.95)
    axc.plot(pr[:,0], pr[:,1], color="#2f4858", lw=1.6, label="实际廓线(导出txt)")
    axc.plot(pi[:,0], pi[:,1], color="#b8860b", lw=1, ls="--", label="理论(节)曲线")
    axc.plot(r0*np.cos(th), r0*np.sin(th), ":", color="#888", lw=1, label=f"理论基圆 r0={r0:.0f}")
    axc.add_patch(Circle(Pj, rr, fc="none", ec="#b22222", lw=1.6, label=f"滚子 r={rr:.0f}"))
    axc.add_patch(Circle((0,0), 10, fc="white", ec="k", lw=1.2))
    axc.plot([0],[0], "k+", ms=10)
    axc.annotate("", xy=(np.cos(2.0)*r0*.62, np.sin(2.0)*r0*.62),
                 xytext=(np.cos(1.45)*r0*.62, np.sin(1.45)*r0*.62),
                 arrowprops=dict(arrowstyle="->", color="#b22222", lw=1.6))
    axc.annotate("ω 逆时针", (np.cos(1.8)*r0*.62, np.sin(1.8)*r0*.62+8),
                 fontsize=9, color="#b22222", ha="center")
    a0 = np.degrees(np.arctan2(Pj[1], Pj[0]))
    axc.plot([0, Pj[0]],[0, Pj[1]], lw=.8, color="#b22222", ls="-.")
    axc.annotate(f"装填位滚子方位 {a0:.1f}°\n(廓线文件首点方向)", (Pj[0]*0.45, Pj[1]*0.45-14),
                 fontsize=8.5, color="#b22222")
    axc.set_title(f"{ttl}\n{rngtxt}", fontsize=10.5)
    axc.legend(fontsize=8, loc="upper left")
    axc.set_aspect("equal"); axc.grid(alpha=.3, lw=.5)
    axc.set_xlabel("X (mm)"); axc.set_ylabel("Y (mm)")
fig.suptitle("凸轮工作图（孔径φ20配主轴；键槽按装填位对齐法定位）", fontsize=11.5)
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig(os.path.join(HERE,"参考图_凸轮工作图.png"), dpi=170)
plt.close(fig); print("图3 OK")

# ================= 图4：运动与压力角 =================
fig, axs = plt.subplots(2, 2, figsize=(12.5, 8))
SHADE = [(0,90,"#eef3fa","装料/筛料"),(90,135,"#fdf3e3","下沉/左退"),(135,200,"#fbe9e9","加压"),
         (200,240,"#f8dddd","保压"),(240,290,"#e7f2e7","退回/顶出"),(290,335,"#efe7f6","推卸"),(335,360,"#eef3fa","复位")]
def shade(a):
    for s0,s1,c,_ in SHADE: a.axvspan(s0,s1,color=c,zorder=0)
ax1 = axs[0,0]; shade(ax1)
ax1.plot(PH72, 300-tip, color="#b22222", lw=2)
ax1.set_title("上冲头位移（向下为正, 0=装填位 尖端Y=300）", fontsize=10)
ax1.axhline(95, ls=":", color="#666", lw=.8); ax1.text(8, 88, "95 (保压, 尖端Y=205)", fontsize=8)
ax2 = axs[0,1]; shade(ax2)
au = camU["alpha"].copy()
ax2.plot(PHI, au, color="#2f4858", lw=1.6)
ax2.axhline(30, color="#b22222", ls="--", lw=1); ax2.text(5, 31, "许用[α]=30°(工作行程)", fontsize=8, color="#b22222")
ax2.set_title(f"上冲头凸轮压力角  压程max={amax(camU['alpha'],120,200):.1f}°  回程max={amax(camU['alpha'],240,290):.1f}°(空程)", fontsize=10)
ax3 = axs[1,0]; shade(ax3)
cxs = []
for ph in PH72:
    q = sieve_pose(psiS(np.array([ph]))[0])
    cxs.append(q["C"][0])
ax3.plot(PH72, cxs, color="#1a6b1a", lw=2)
ax3.set_title("粉筛托架销 X 位移（42=装料位 筛口对型腔; -6=左停位）", fontsize=10)
ax4 = axs[1,1]; shade(ax4)
ax4.plot(PHI, camS["alpha"], color="#5a6f48", lw=1.6)
ax4.axhline(30, color="#b22222", ls="--", lw=1)
ax4.set_title(f"粉筛凸轮压力角  推卸max={amax(camS['alpha'],290,335):.1f}°  左退max={amax(camS['alpha'],90,135):.1f}°(空程)", fontsize=10)
for a in axs.flat:
    a.set_xlim(0,360); a.set_xticks(np.arange(0,361,30)); a.grid(alpha=.3, lw=.5)
    a.set_xlabel("主轴转角 φ (°)")
axs[0,0].set_ylabel("位移 (mm)"); axs[1,0].set_ylabel("位移 (mm)")
axs[0,1].set_ylabel("α (°)"); axs[1,1].set_ylabel("α (°)")
fig.suptitle("重建机构 运动规律与凸轮压力角校核（下冲头相位不变；粉筛左退窗口 90~135°）", fontsize=11.5)
fig.tight_layout(rect=[0,0,1,0.955])
fig.savefig(os.path.join(HERE,"参考图_运动与压力角.png"), dpi=170)
plt.close(fig); print("图4 OK")

# ================= 图5：整机布局总览（装填位） =================
fig, ax = plt.subplots(figsize=(10.5, 12))
# 下冲头凸轮（现有文件）
dc = np.loadtxt(os.path.join(HERE, "..", "凸轮廓线", "下冲头凸轮_SW.txt"))[:,:2]
ax.fill(dc[:,0], dc[:,1], color="#e0d2d2", alpha=.9, zorder=2)
ax.plot(dc[:,0], dc[:,1], color="#7a4848", lw=1.2, zorder=3)
ax.annotate("下冲头凸轮(不变)\nZ=0", (-58,-66), fontsize=8.5, color="#7a4848")
# 下冲头（示意: 滚子中心(0,53), 杆到型腔底）
ax.add_patch(Circle((0,53), 10, fc="none", ec="#7a4848", lw=1.4, zorder=5))
ax.plot([0,0],[53,186], color="#7a4848", lw=5, solid_capstyle="round", zorder=4, alpha=.8)
ax.annotate("下冲头(不变)\n滚子中心(0,53)", (12,90), fontsize=8.5, color="#7a4848")
# 上冲头机构
ax.fill(pf[:,0], pf[:,1], color="#c9d4dd", alpha=.75, zorder=2)
ax.plot(pf[:,0], pf[:,1], color="#48606f", lw=1.2, zorder=3)
ax.annotate("上冲头凸轮 v2\nZ=67.5", (40,-95), fontsize=8.5, color="#48606f")
B,Cc,Dd,E,P = [np.array(pose_fill[k]) for k in ["B","C","D","E","P"]]
for p1,p2,c in [(O2,P,"#5a7d9a"),(O2,B,"#5a7d9a"),(B,Dd,"#7a6a55"),(O3,Dd,"#4a7a5a"),(O3,Cc,"#4a7a5a"),(Cc,E,"#7a6a55")]:
    bar(ax,p1,p2,3,c)
ax.add_patch(Circle(P, RR, fc="none", ec="#8a4a4a", lw=1.2, zorder=5))
ax.add_patch(Rectangle((-17,300), 34, TIP45, fc="#d8dee4", ec="#48606f", lw=1, zorder=4))
ax.add_patch(Rectangle((-20,300+TIP45), 40, Lp-TIP45, fc="#d8dee4", ec="#48606f", lw=1, zorder=4))
for pt,lb in [(O2,"O2(100,35)"),(O3,"O3(140,457)"),((0,0),"O1(0,0)")]:
    joint(ax, pt, lb, dx=8, dy=8, fs=9)
# 粉筛机构
ax.fill(pf2[:,0], pf2[:,1], color="#d3dbc9", alpha=.75, zorder=2)
ax.plot(pf2[:,0], pf2[:,1], color="#5a6f48", lw=1.2, zorder=3)
ax.annotate("粉筛凸轮 v2\nZ=132.5", (-150,-60), fontsize=8.5, color="#5a6f48")
for p1,p2,c in [(O2s,Pf,"#5a7d9a"),(O2s,Bf,"#5a7d9a"),(Bf,Cf,"#7a6a55")]:
    bar(ax,p1,p2,3,c)
ax.add_patch(Circle(Pf, RRs, fc="none", ec="#8a4a4a", lw=1.2, zorder=5))
ax.add_patch(Rectangle((Cf[0]-14-TRAY_L, 216), TRAY_L, TRAY_T, fc="#e2d9c8", ec="#7a6a55", lw=1, zorder=4))
joint(ax, O2s, "O2s(-100,-45)", dx=-86, dy=-8, fs=9)
# 公共件
ax.plot([-170,-17],[216,216], color="#8a6d3b", lw=2.5, zorder=2)
ax.plot([17,170],[216,216], color="#8a6d3b", lw=2.5, zorder=2)
ax.add_patch(Rectangle((-17,186), 34, 30, fc="none", ec="#333", lw=1.3, hatch="//", zorder=3))
ax.plot([0,0],[-110,560], color="#aaa", lw=.6, ls="-.", zorder=1)
ax.annotate("型腔(不变)", (24,182), fontsize=9, color="#333")
ax.set_title("整机布局总览（装填位 φ=0，主轴逆时针）\n"
             "凸轮轴向站位不变: 下冲头Z=0 / 上冲头Z=67.5 / 粉筛Z=132.5；粉筛连杆位于Z≈+45平面",
             fontsize=11.5)
ax.set_xlim(-260, 320); ax.set_ylim(-150, 575)
ax.set_aspect("equal"); ax.grid(alpha=.25, lw=.5)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.tight_layout(); fig.savefig(os.path.join(HERE,"参考图_整机布局.png"), dpi=170)
plt.close(fig); print("图5 OK")
