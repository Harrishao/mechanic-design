# -*- coding: utf-8 -*-
"""v4 (销左端, Y=223, 水平连杆) 参考图"""
import os, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import Rectangle, Circle, Arc, Polygon

HERE = os.path.dirname(os.path.abspath(__file__))
fp = "/sessions/modest-dazzling-cori/.local/lib/python3.10/site-packages/mplfonts/fonts/NotoSansCJKsc-Regular.otf"
fm.fontManager.addfont(fp); plt.rcParams["font.family"] = fm.FontProperties(fname=fp).get_name()
plt.rcParams["axes.unicode_minus"] = False

exec(open(os.path.join(HERE, "粉筛v4_左端销223.py"), encoding="utf-8").read())

r = camS["rprof"]; th = np.degrees(np.arctan2(camS["prof"][:,1], camS["prof"][:,0]))
m = r > r.max()-0.02
ths = np.sort(((th[m]-th[np.argmax(r)]+180)%360)-180) + th[np.argmax(r)]
FAR_MID = ((ths[0]+ths[-1])/2 + 180) % 360 - 180
print(f"v4 远休弧中点方向(零件系) {FAR_MID:.1f}")

def dim_h(ax,x0,x1,y,txt,dy=3,fs=8.5,c="#1a6b1a"):
    ax.annotate("",(x0,y),(x1,y),arrowprops=dict(arrowstyle="<->",color=c,lw=.9))
    ax.text((x0+x1)/2,y+dy,txt,ha="center",fontsize=fs,color=c)
def dim_v(ax,y0,y1,x,txt,dx=3,fs=8.5,c="#1a6b1a"):
    ax.annotate("",(x,y0),(x,y1),arrowprops=dict(arrowstyle="<->",color=c,lw=.9))
    ax.text(x+dx,(y0+y1)/2,txt,va="center",fontsize=fs,color=c)
def joint(ax,p,label=None,dx=4,dy=4,fs=8.5):
    ax.add_patch(Circle(p,2.2,fc="#b22222",ec="k",lw=.5,zorder=9))
    if label:
        ax.annotate(label,p,xytext=(p[0]+dx,p[1]+dy),fontsize=fs,zorder=10,
                    bbox=dict(fc="white",ec="none",alpha=.75,pad=1))
def bar(ax,p1,p2,w=3,c="#5a7d9a",ls="-",al=1):
    ax.plot([p1[0],p2[0]],[p1[1],p2[1]],lw=w,color=c,ls=ls,solid_capstyle="round",alpha=al,zorder=4)

XL,XR,YB,YT = -27.,28.,216.,230.
ZB,ZF = -30.,30.
HX0,HX1,HZ0,HZ1 = -18.,18.,-20.,20.
PIN = np.array([-47.,223.])
LUGX0 = -54.
EARZ = [(-16.,-8.),(8.,16.)]
R7,R4 = 7.,4.

fig,(a1,a2) = plt.subplots(2,1,figsize=(11,9.5),sharex=True)
# ===== 前视图 =====
a1.plot([-80,-17],[216,216],color="#8a6d3b",lw=2.5)
a1.plot([17,130],[216,216],color="#8a6d3b",lw=2.5)
a1.text(-79,209.5,"台面 Y=216 (左缘 X=-80)",fontsize=8.5,color="#8a6d3b")
a1.add_patch(Rectangle((XL,YB),XR-XL,YT-YB,fc="#e2d9c8",ec="k",lw=1.4,zorder=3))
a1.plot([HX0,HX0],[YB,YT],"k--",lw=1); a1.plot([HX1,HX1],[YB,YT],"k--",lw=1)
# 双耳叉(前视: 与本体同高的两片重合)
a1.add_patch(Rectangle((PIN[0],YB),XL-PIN[0],YT-YB,fc="#cfc7b6",ec="k",lw=1.3,zorder=4))
arc = Arc(PIN,2*R7,2*R7,theta1=90,theta2=270,lw=1.3,color="k",zorder=5)
a1.add_patch(arc)
a1.plot([PIN[0],XL],[YB,YB],"k-",lw=1.3,zorder=5); a1.plot([PIN[0],XL],[YT,YT],"k-",lw=1.3,zorder=5)
a1.add_patch(Circle(PIN,R4,fc="white",ec="k",lw=1.2,zorder=6))
a1.plot([PIN[0]-7,PIN[0]+7],[PIN[1],PIN[1]],"k-.",lw=.6,zorder=6)
a1.plot([PIN[0],PIN[0]],[PIN[1]-7,PIN[1]+7],"k-.",lw=.6,zorder=6)
a1.annotate("销孔 φ8, 轴心 (-47, 223)\n= 主体中心高, 双耳夹叉",(PIN[0]-10,PIN[1]+13),fontsize=9)
a1.add_patch(Rectangle((XL-48,YB),XR-XL,YT-YB,fc="none",ec="#999",lw=1,ls="--",zorder=2))
a1.text(XL-46,YT+3,"左停位(销X=-95)",fontsize=8,color="#777")
dim_h(a1,XL,XR,YT+8,"55")
dim_h(a1,PIN[0],XL,YB-8,"20",dy=-7)
dim_h(a1,HX0,HX1,YB-8,"筛口36",dy=-7)
dim_v(a1,YB,YT,XR+8,"14")
a1.plot([0,0],[206,242],color="#aaa",lw=.7,ls="-.")
a1.text(0,221.5,"筛口中心X=0",ha="center",fontsize=8,color="#555")
a1.set_title("托架 v4 前视图（XY，视向 -Z）  装料位",fontsize=11)
a1.set_ylabel("Y (mm)"); a1.set_ylim(202,248); a1.set_aspect("equal"); a1.grid(alpha=.25,lw=.5)
# ===== 上视图 =====
a2.add_patch(Rectangle((XL,ZB),XR-XL,ZF-ZB,fc="#e2d9c8",ec="k",lw=1.4,zorder=3))
a2.add_patch(Rectangle((HX0,HZ0),HX1-HX0,HZ1-HZ0,fc="white",ec="k",lw=1.2,zorder=4))
a2.text(0,0,"筛口 36×40",ha="center",va="center",fontsize=9)
for z0,z1 in EARZ:
    a2.add_patch(Rectangle((LUGX0,z0),XL-LUGX0,z1-z0,fc="#cfc7b6",ec="k",lw=1.2,zorder=4))
a2.plot([PIN[0],PIN[0]],[-22,22],"k-.",lw=.6,zorder=6)
a2.plot([PIN[0]-R4,PIN[0]-R4],[-16,16],"k--",lw=.9,zorder=5)
a2.plot([PIN[0]+R4,PIN[0]+R4],[-16,16],"k--",lw=.9,zorder=5)
a2.annotate("双耳板 厚8, Z=±8~±16, 内档16\n与本体同高(Y216~230), 端部R7",(LUGX0-6,24),fontsize=9)
a2.annotate("销 φ8×约40, 沿Z, 双剪",(PIN[0]+6,-28),fontsize=8.5)
dim_h(a2,XL,XR,ZB-8,"55",dy=-7)
dim_v(a2,ZB,ZF,XR+8,"60")
dim_v(a2,HZ0,HZ1,HX0+6,"40",dx=-11)
dim_v(a2,EARZ[0][0],EARZ[1][1],LUGX0-8,"32",dx=-11)
a2.plot([0,0],[ZB-14,ZF+14],color="#aaa",lw=.7,ls="-.")
a2.text(62,38,"连杆运动平面 Z=0, 销高=主体中心高\n力线过质心, 完全对中",fontsize=8.5,
        bbox=dict(fc="white",ec="#888",lw=.6,pad=2))
a2.set_title("托架 v4 上视图（XZ，视向 -Y）",fontsize=11)
a2.set_xlabel("X (mm)"); a2.set_ylabel("Z (mm)")
a2.set_xlim(-135,135); a2.set_ylim(-52,52); a2.set_aspect("equal"); a2.grid(alpha=.25,lw=.5)
fig.suptitle("粉筛托架 v4（销在左端、Y=223 主体中心高、双耳对中）  装料位销 X=-47, 行程48",fontsize=12)
fig.tight_layout(rect=[0,0,1,0.96])
fig.savefig(os.path.join(HERE,"参考图_托架视图_v4.png"),dpi=170)
plt.close(fig); print("托架v4 OK")

# ===== 机构布局 v4 =====
fig,ax = plt.subplots(figsize=(10.5,10))
pf = camS["prof"]
ax.fill(pf[:,0],pf[:,1],color="#d3dbc9",alpha=.9,zorder=2)
ax.plot(pf[:,0],pf[:,1],color="#5a6f48",lw=1.4,zorder=3)
th2 = np.linspace(0,2*np.pi,200)
ax.plot(R0S*np.cos(th2),R0S*np.sin(th2),ls=":",color="#777",lw=1,zorder=3)
ax.annotate(f"粉筛凸轮 v4 (装料位姿态)\nr0={R0S:.0f}, 实际 70.0~82.0",(10,40),fontsize=9,color="#4a5a3a")
ax.add_patch(Circle((0,0),10,fc="white",ec="k",lw=1.2,zorder=6))
joint(ax,(0,0),"O1 (0,0)",dx=12,dy=-18,fs=10)
for (B,C,P,lam),ls,al in [((Bf,Cf,Pf,lf),"-",1.),((Bl,Cl,Pl,ll),"--",.55)]:
    bar(ax,O2s,P,4,"#5a7d9a",ls,al)
    bar(ax,O2s,B,4,"#5a7d9a",ls,al)
    ax.add_patch(Circle(P,RRs,fc="none",ec="#8a4a4a",lw=1.4,ls=ls,alpha=al,zorder=5))
    bar(ax,B,C,3,"#7a6a55",ls,al)
    face = C[0]+20
    ax.add_patch(Rectangle((face,216),55,14,fc="#e2d9c8",ec="#7a6a55",lw=1.2,ls=ls,alpha=al,zorder=4))
    ax.add_patch(Rectangle((face+9,216),36,14,fc="white",ec="#7a6a55",lw=1,ls=ls,alpha=al,zorder=5))
    ax.plot([C[0]-7,face],[223,223],color="#7a6a55",lw=1,ls=ls,alpha=al,zorder=4)
    ax.add_patch(Circle(C,4,fc="white",ec="#7a6a55",lw=1.2,alpha=al,zorder=6))
joint(ax,O2s,f"O2s 新支点 ({O2s[0]:.0f},{O2s[1]:.0f})",dx=10,dy=-6,fs=9.5)
ax.add_patch(Polygon([O2s+(-9,-12),O2s+(9,-12),O2s],closed=True,fc="#999",ec="k",lw=.6,zorder=3))
joint(ax,Bf,"B (-83.0,221.5)",dx=6,dy=10)
joint(ax,Bl,"B' (-131.0,221.5)",dx=-58,dy=10)
joint(ax,Cf,"C 销 (-47,223)",dx=8,dy=-18)
joint(ax,Cl,"C' (-95,223)",dx=-26,dy=-20)
joint(ax,Pf,"滚子 ({:.1f},{:.1f})".format(*Pf),dx=6,dy=-20,fs=8.5)
ax.annotate(f"Lr={LRS:.0f}",((O2s[0]+Pf[0])/2+8,(O2s[1]+Pf[1])/2),fontsize=8.5,color="#1a6b1a")
ax.annotate(f"竖臂 Rb={Rbs:.0f}",(O2s[0]-46,(O2s[1]+Bf[1])/2),fontsize=8.5,color="#1a6b1a")
ax.annotate(f"水平连杆 Ls={Ls:.1f}",((Bf[0]+Cf[0])/2-26,232),fontsize=8.5,color="#1a6b1a")
ax.plot([-80,-17],[216,216],color="#8a6d3b",lw=2.5,zorder=2)
ax.plot([17,140],[216,216],color="#8a6d3b",lw=2.5,zorder=2)
ax.add_patch(Rectangle((-17,186),34,30,fc="none",ec="#333",lw=1.3,hatch="//",zorder=3))
ax.annotate("台面左缘 X=-80\n(竖臂过台面平面处 X=-83.7)",(-225,196),fontsize=8.5,color="#8a6d3b")
ax.annotate("型腔",(22,190),fontsize=9,color="#333")
ax.annotate(f"行程48 (销 -95→-47)\n摆角 {psi_s:.2f}°  夹角 {aS:.2f}°\n推卸α {PU:.1f}°  传动角min {gB:.0f}°\n连杆离台面最小 {minBy-216:.1f}",
            (40,255),fontsize=9,color="#1a6b1a",bbox=dict(fc="white",ec="#1a6b1a",lw=.6,pad=2))
ax.plot([0,0],[150,290],color="#aaa",lw=.7,ls="-.",zorder=1)
ax.set_title("粉筛机构 v4（销左端 Y=223，水平连杆，全部 Z=0 平面）\n实线=装料位(φ=0~90°)  虚线=左停位(φ=135~290°)",fontsize=11)
ax.set_xlim(-240,170); ax.set_ylim(-120,300)
ax.set_aspect("equal"); ax.grid(alpha=.25,lw=.5)
ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
fig.tight_layout()
fig.savefig(os.path.join(HERE,"参考图_粉筛机构_v4.png"),dpi=170)
plt.close(fig); print("布局v4 OK")
