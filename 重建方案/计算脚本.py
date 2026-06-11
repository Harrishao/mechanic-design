# -*- coding: utf-8 -*-
"""
15吨压片机 上冲头/粉筛机构重建 —— 尺寸综合、凸轮设计与校核
约定（与下冲头一致）：
  O1=(0,0) 主轴；主轴逆时针(CCW)；φ=0 为装填位；
  廓线文件为【实际廓线】，第一点对应装填位滚子方向，极角随 φ 递减排点。
运动循环（主轴转角 φ）：
  上冲头：0-120 高位停；120-200 下压(摆线)；200-240 保压；240-290 回程(摆线)；290-360 停
  粉筛  ：0-90 装料位(右,筛口对型腔)；90-135 左退(摆线)[由90-120放宽]；135-290 左停；
          290-335 推卸右移(摆线)；335-360 右停
"""
import numpy as np
from scipy.optimize import brentq

D = np.pi / 180.0

# ---------------- 摆线运动规律 ----------------
def cyc(t):
    t = np.clip(t, 0, 1)
    return t - np.sin(2 * np.pi * t) / (2 * np.pi)

def law(phi, segs):
    """segs: [(p0,p1,s0,s1)], 区间内摆线过渡, 其余取最近端值"""
    phi = np.asarray(phi, float) % 360.0
    s = np.zeros_like(phi)
    for p0, p1, s0, s1 in segs:
        m = (phi >= p0) & (phi <= p1)
        s[m] = s0 + (s1 - s0) * cyc((phi[m] - p0) / (p1 - p0))
    return s

PUNCH_SEGS = lambda A: [(0,120,0,0),(120,200,0,A),(200,240,A,A),(240,290,A,0),(290,360,0,0)]
SIEVE_SEGS = lambda A: [(0,90,A,A),(90,135,A,0),(135,290,0,0),(290,335,0,A),(335,360,A,A)]

def dirv(a):  # 角度(°)→单位向量
    return np.array([np.cos(a * D), np.sin(a * D)])

# ============================================================
# 1. 上冲头机构（XY平面：凸轮→下摆杆→长连杆→上摆杆→小连杆→冲头）
# ============================================================
STROKE, TIP_HI, TIP_LO = 95.0, 300.0, 205.0
O3x, R3p, R3, L2, Lp = 140.0, 140.0, 70.0, 75.0, 130.0
O2 = np.array([100.0, 35.0]); LB, Lr, RR = 150.0, 85.0, 12.0  # 滚子d24

# 上摆杆：u=0 时 C 在 O3 正左、D 在 O3 正右；u 为CCW转角(CCW时C下移)
def C_of(u, O3y): return np.array([O3x - R3p*np.cos(u*D), O3y - R3p*np.sin(u*D)])
def D_of(u, O3y): return np.array([O3x + R3*np.cos(u*D),  O3y + R3*np.sin(u*D)])
def Ey_of(u, O3y):
    C = C_of(u, O3y)
    return C[1] - np.sqrt(L2**2 - C[0]**2)

# 求半转角 eps：冲头行程 = STROKE（行程与O3y无关）
eps = brentq(lambda e: (Ey_of(-e, 0) - Ey_of(e, 0)) - STROKE, 3, 35)
# 定 O3y：装填位(u=-eps) E_y = TIP_HI + Lp
O3y = (TIP_HI + Lp) - Ey_of(-eps, 0.0)
O3 = np.array([O3x, O3y])

# 长连杆：取中位姿态定长
B_mid = O2 + LB * dirv(0.0)
L1 = np.linalg.norm(D_of(0, O3y) - B_mid)

# 下摆杆装填位角 lam0：使 |D(-eps)-B(lam0)| = L1
f = lambda lam: np.linalg.norm(D_of(-eps, O3y) - (O2 + LB*dirv(lam))) - L1
lam0 = brentq(f, -45, -1)

def solve_u(B, u_guess):
    g = lambda u: np.linalg.norm(D_of(u, O3y) - B) - L1
    lo, hi = u_guess - 12, u_guess + 12
    for _ in range(20):
        if g(lo) * g(hi) <= 0: break
        lo -= 5; hi += 5
    else:
        raise RuntimeError("solve_u: no root")
    return brentq(g, lo, hi)

# 摆角幅值 psi_max：使 u(psi_max) = +eps
def u_of_psi(psi):
    ug = -eps
    for p in np.linspace(0, psi, max(2, int(abs(psi)) + 2)):
        ug = solve_u(O2 + LB*dirv(lam0 + p), ug)
    return ug
psi_est = np.degrees(2 * R3 * np.sin(eps * D) / LB)   # 摆角初估
psi_max = brentq(lambda p: u_of_psi(p) - eps, 0.6 * psi_est, 1.5 * psi_est)

# 滚子臂方位 mu0：装填位 |P|=r0，且压程(摆杆CCW)时 |P| 增大
def mu0_of(r0):
    aO1 = np.degrees(np.arctan2(-O2[1], -O2[0]))           # O2→O1 方位
    a, b = np.linalg.norm(O2), Lr
    g = np.degrees(np.arccos((a*a + b*b - r0*r0) / (2*a*b)))
    for mu in (aO1 - g, aO1 + g):
        P = O2 + Lr * dirv(mu)
        t = np.array([-np.sin(mu*D), np.cos(mu*D)])        # CCW 切向
        if np.dot(P, t) > 0:                                # d|P|/dpsi > 0
            return mu
    raise RuntimeError

# ---------------- 凸轮通用：节曲线/实际廓线/压力角/曲率 ----------------
PHI = np.arange(0, 360, 0.5)

def cam_design(O2_, Lr_, mu0_, psi_fun, rr, sign=+1):
    """sign=+1: mu=mu0+psi（摆杆CCW升程）; sign=-1: mu=mu0-psi"""
    psi = psi_fun(PHI)
    mu = mu0_ + sign * psi
    P = O2_[None,:] + Lr_ * np.stack([np.cos(mu*D), np.sin(mu*D)], 1)  # 固定系滚子中心
    c, s = np.cos(-PHI*D), np.sin(-PHI*D)
    Rp = np.stack([c*P[:,0] - s*P[:,1], s*P[:,0] + c*P[:,1]], 1)       # 凸轮系节曲线
    dphi = 0.5 * D
    dR  = (np.roll(Rp,-1,0) - np.roll(Rp,1,0)) / (2*dphi)
    d2R = (np.roll(Rp,-1,0) - 2*Rp + np.roll(Rp,1,0)) / dphi**2
    T = dR / np.linalg.norm(dR, axis=1, keepdims=True)
    N = np.stack([-T[:,1], T[:,0]], 1)
    inward = -Rp / np.linalg.norm(Rp, axis=1, keepdims=True)
    flip = (np.sum(N*inward, 1) < 0); N[flip] *= -1                    # 指向凸轮体内
    prof = Rp + rr * N                                                  # 实际廓线
    cph, sph = np.cos(PHI*D), np.sin(PHI*D)
    Nf = np.stack([cph*N[:,0] - sph*N[:,1], sph*N[:,0] + cph*N[:,1]], 1)
    dpsi = (psi_fun(PHI+0.25) - psi_fun(PHI-0.25)) / 0.5               # °/°
    vdir = np.stack([-np.sin(mu*D), np.cos(mu*D)], 1) * (sign*np.sign(dpsi))[:,None]
    cosa = np.abs(np.sum(Nf*vdir, 1))
    alpha = np.degrees(np.arccos(np.clip(cosa, -1, 1)))
    alpha[np.abs(dpsi) < 1e-6] = np.nan
    cross = dR[:,0]*d2R[:,1] - dR[:,1]*d2R[:,0]
    rho = (np.sum(dR**2,1))**1.5 / np.where(np.abs(cross)<1e-12, 1e-12, np.abs(cross))
    return dict(psi=psi, P=P, pitch=Rp, prof=prof, alpha=alpha, rho=rho,
                rpitch=np.linalg.norm(Rp,axis=1), rprof=np.linalg.norm(prof,axis=1))

def amax(alpha, p0, p1, margin=2.0):
    m = (PHI > p0+margin) & (PHI < p1-margin)
    return np.nanmax(alpha[m])

# ---- 上冲头凸轮：扫 r0，工作行程(120-200)≤30°，回程(240-290)≤45° ----
psiU = lambda ph: law(ph, PUNCH_SEGS(psi_max))
camU = None
for r0 in np.arange(48, 100, 1.0):
    mu0 = mu0_of(r0)
    cd = cam_design(O2, Lr, mu0, psiU, RR, +1)
    if amax(cd['alpha'],120,200) <= 30 and amax(cd['alpha'],240,290) <= 45:
        camU, R0U, MU0U = cd, r0, mu0
        break
if camU is None:
    raise SystemExit("上冲头凸轮: r0 扫描无解，需调整杆系")

# 上冲头全程冲头位移（FK 校验）
def punch_tip(phi):
    psi = psiU(np.atleast_1d(phi))
    out, ug = [], -eps
    for p in psi:
        B = O2 + LB * dirv(lam0 + p)
        ug = solve_u(B, ug)
        out.append(Ey_of(ug, O3y) - Lp)
    return np.array(out)

PH72 = np.arange(0, 360, 2.5)
tip = punch_tip(PH72)

# 关键位姿坐标
def punch_pose(psi):
    B = O2 + LB * dirv(lam0 + psi)
    u = solve_u(B, 0 if psi > psi_max/2 else -eps)
    Cp, Dp = C_of(u, O3y), D_of(u, O3y)
    E = np.array([0.0, Ey_of(u, O3y)])
    P = O2 + Lr * dirv(MU0U + psi)
    return dict(B=B, C=Cp, D=Dp, E=E, P=P, u=u, tip=E[1]-Lp)
pose_fill  = punch_pose(0.0)
pose_press = punch_pose(psi_max)

# 传动角（工作行程内）
def trans_angles():
    res = {'B':90.0, 'D':90.0, 'C':0.0}
    ug = -eps
    for ph in np.arange(120, 200.1, 1.0):
        p = psiU(np.array([ph]))[0]
        B = O2 + LB*dirv(lam0+p); ug = solve_u(B, ug)
        Dp, Cp = D_of(ug,O3y), C_of(ug,O3y)
        link = (Dp-B)/np.linalg.norm(Dp-B)
        armB = dirv(lam0+p); armD = (Dp-O3)/R3
        gB = np.degrees(np.arcsin(np.abs(np.cross(link, armB))))
        gD = np.degrees(np.arcsin(np.abs(np.cross(link, armD))))
        res['B'] = min(res['B'], gB); res['D'] = min(res['D'], gD)
        res['C'] = max(res['C'], np.degrees(np.arcsin(abs(Cp[0])/L2)))
    return res
TA = trans_angles()

arm_angle_U = (MU0U - lam0) % 360
if arm_angle_U > 180: arm_angle_U = 360 - arm_angle_U

print("="*62)
print("【上冲头】")
print(f"  上摆杆半转角 eps={eps:.3f}°  总转角={2*eps:.3f}°")
print(f"  O3=({O3x:.1f},{O3y:.2f})  R3p={R3p} R3={R3} L2={L2} Lp={Lp}")
print(f"  长连杆 L1={L1:.2f}  下摆杆 LB={LB} Lr={Lr}")
print(f"  lam0(装填位B臂方位)={lam0:.3f}°  psi_max={psi_max:.3f}°")
print(f"  滚子臂装填位方位 mu0={MU0U:.3f}°  两臂夹角={arm_angle_U:.2f}°")
print(f"  凸轮: r0={R0U}  滚子r={RR}  节曲线r: {camU['rpitch'].min():.2f}~{camU['rpitch'].max():.2f}"
      f"  实际r: {camU['rprof'].min():.2f}~{camU['rprof'].max():.2f}")
print(f"  压力角: 压程max={amax(camU['alpha'],120,200):.2f}°  回程max={amax(camU['alpha'],240,290):.2f}°")
print(f"  节曲线最小曲率半径={np.nanmin(np.abs(camU['rho'])):.1f} (>滚子{RR}即无根切)")
print(f"  冲头位移: 高位tip={tip.max():.3f}  低位tip={tip.min():.3f}  行程={tip.max()-tip.min():.4f}")
print(f"  装填位: B=({pose_fill['B'][0]:.2f},{pose_fill['B'][1]:.2f}) D=({pose_fill['D'][0]:.2f},{pose_fill['D'][1]:.2f})"
      f" C=({pose_fill['C'][0]:.2f},{pose_fill['C'][1]:.2f}) E=(0,{pose_fill['E'][1]:.2f}) P=({pose_fill['P'][0]:.2f},{pose_fill['P'][1]:.2f})")
print(f"  保压位: B=({pose_press['B'][0]:.2f},{pose_press['B'][1]:.2f}) D=({pose_press['D'][0]:.2f},{pose_press['D'][1]:.2f})"
      f" C=({pose_press['C'][0]:.2f},{pose_press['C'][1]:.2f}) E=(0,{pose_press['E'][1]:.2f}) P=({pose_press['P'][0]:.2f},{pose_press['P'][1]:.2f})")
print(f"  传动角: 连杆-下摆杆min={TA['B']:.1f}°  连杆-上摆杆min={TA['D']:.1f}°  小连杆偏摆max={TA['C']:.2f}°")

# ============================================================
# 2. 粉筛机构（凸轮→摆杆→连杆→托架销C, C_y=223, X: -6→+42）
# ============================================================
CY, CX_FILL, S_STROKE = 223.0, 42.0, 48.0
O2s = np.array([-100.0, -45.0]); Rbs, Lrs, RRs = 110.0, 50.0, 10.0  # 滚子d20
LAM_MID = 100.0

def sieve_Cx(lam, Ls):
    B = O2s + Rbs * dirv(lam)
    return B[0] + np.sqrt(Ls**2 - (CY - B[1])**2)

def sieve_solve(Ls):
    g = lambda h: (sieve_Cx(LAM_MID - h, Ls) - sieve_Cx(LAM_MID + h, Ls)) - S_STROKE
    return brentq(g, 5, 30)   # 半摆角; lam小→C右

Ls = brentq(lambda L: sieve_Cx(LAM_MID - sieve_solve(L), L) - CX_FILL, 195, 340)
hs = sieve_solve(Ls); psi_s = 2*hs
lam_left = LAM_MID + hs          # 左停位(基圆)
lam_fill = LAM_MID - hs          # 装料位(全升程)

def mu0s_of(r0):
    aO1 = np.degrees(np.arctan2(-O2s[1], -O2s[0]))
    a, b = np.linalg.norm(O2s), Lrs
    g = np.degrees(np.arccos((a*a + b*b - r0*r0) / (2*a*b)))
    for mu in (aO1 - g, aO1 + g):
        P = O2s + Lrs * dirv(mu)
        t = np.array([-np.sin(mu*D), np.cos(mu*D)])
        if np.dot(P, -t) > 0:    # 推卸=lam减小=CW, mu=mu0-psi, 升程半径增大
            return mu
    raise RuntimeError

psiS = lambda ph: law(ph, SIEVE_SEGS(psi_s))
camS = None
for r0 in np.arange(np.floor(abs(np.linalg.norm(O2s)-Lrs))+3, 130, 1.0):
    mu0 = mu0s_of(r0)
    cd = cam_design(O2s, Lrs, mu0, psiS, RRs, -1)
    if amax(cd['alpha'],290,335) <= 28 and amax(cd['alpha'],90,135) <= 38:
        camS, R0S, MU0S = cd, r0, mu0
        break
if camS is None:
    raise SystemExit("粉筛凸轮: r0 扫描无解，需调整杆系")

def sieve_pose(psi):   # psi: 0=左停 → psi_s=装料
    lam = lam_left - psi
    B = O2s + Rbs * dirv(lam)
    Cx = B[0] + np.sqrt(Ls**2 - (CY - B[1])**2)
    P = O2s + Lrs * dirv(MU0S - psi)
    return dict(B=B, C=np.array([Cx, CY]), P=P, lam=lam)
sp_fill = sieve_pose(psi_s); sp_left = sieve_pose(0.0)

# 粉筛传动角
gmin_B, gmax_horiz = 90.0, 0.0
for ps in np.linspace(0, psi_s, 40):
    q = sieve_pose(ps)
    link = (q['C'] - q['B']) / Ls
    armB = dirv(q['lam'])
    gmin_B = min(gmin_B, np.degrees(np.arcsin(abs(np.cross(link, armB)))))
    gmax_horiz = max(gmax_horiz, np.degrees(np.arctan2(abs(link[1]), abs(link[0]))))

arm_angle_S = (MU0S - lam_left) % 360
if arm_angle_S > 180: arm_angle_S = 360 - arm_angle_S

print("="*62)
print("【粉筛】")
print(f"  O2s=({O2s[0]:.0f},{O2s[1]:.0f})  a={np.linalg.norm(O2s):.2f}  Rb={Rbs} Lr={Lrs} 连杆Ls={Ls:.2f}")
print(f"  摆角 psi={psi_s:.3f}°  左停位臂方位={lam_left:.3f}°  装料位臂方位={lam_fill:.3f}°")
print(f"  滚子臂左停位方位 mu0={MU0S:.3f}°  两臂夹角={arm_angle_S:.2f}°")
print(f"  凸轮: r0={R0S}  滚子r={RRs}  节曲线r: {camS['rpitch'].min():.2f}~{camS['rpitch'].max():.2f}"
      f"  实际r: {camS['rprof'].min():.2f}~{camS['rprof'].max():.2f}")
print(f"  压力角: 推卸max={amax(camS['alpha'],290,335):.2f}°  左退max={amax(camS['alpha'],90,135):.2f}°")
print(f"  节曲线最小曲率半径={np.nanmin(np.abs(camS['rho'])):.1f}")
print(f"  C行程: {sp_left['C'][0]:.3f} → {sp_fill['C'][0]:.3f}  (行程={sp_fill['C'][0]-sp_left['C'][0]:.4f})")
print(f"  装料位: B=({sp_fill['B'][0]:.2f},{sp_fill['B'][1]:.2f}) C=({sp_fill['C'][0]:.2f},{CY}) P=({sp_fill['P'][0]:.2f},{sp_fill['P'][1]:.2f})")
print(f"  左停位: B=({sp_left['B'][0]:.2f},{sp_left['B'][1]:.2f}) C=({sp_left['C'][0]:.2f},{CY}) P=({sp_left['P'][0]:.2f},{sp_left['P'][1]:.2f})")
print(f"  传动角: 连杆-摆杆min={gmin_B:.1f}°  连杆与水平最大夹角={gmax_horiz:.1f}°")

# ============================================================
# 3. 导出
# ============================================================
import os, json
OUT = os.path.dirname(os.path.abspath(__file__))
def save_sw(name, prof):
    with open(os.path.join(OUT, name), "w") as f:
        for x, y in prof:
            f.write(f"{x:.4f}\t{y:.4f}\t0\n")
        f.write(f"{prof[0,0]:.4f}\t{prof[0,1]:.4f}\t0\n")

save_sw("上冲头凸轮v2_SW.txt", camU['prof'])
np.savetxt(os.path.join(OUT, "上冲头凸轮v2.csv"),
           np.column_stack([PHI, camU['psi'], camU['rpitch'], camU['rprof'],
                            np.nan_to_num(camU['alpha'])]),
           delimiter=",", header="phi_deg,psi_deg,r_pitch,r_profile,alpha_deg", comments="", fmt="%.4f")
save_sw("粉筛凸轮v2_SW.txt", camS['prof'])
np.savetxt(os.path.join(OUT, "粉筛凸轮v2.csv"),
           np.column_stack([PHI, camS['psi'], camS['rpitch'], camS['rprof'],
                            np.nan_to_num(camS['alpha'])]),
           delimiter=",", header="phi_deg,psi_deg,r_pitch,r_profile,alpha_deg", comments="", fmt="%.4f")

res = dict(
    punch=dict(eps=eps, O3=[O3x,O3y], R3p=R3p, R3=R3, L2=L2, Lp=Lp, L1=L1,
               O2=O2.tolist(), LB=LB, Lr=Lr, rr=RR, lam0=lam0, psi_max=psi_max,
               mu0=MU0U, r0=float(R0U), arm_angle=float(arm_angle_U),
               rpitch=[float(camU['rpitch'].min()), float(camU['rpitch'].max())],
               rprof=[float(camU['rprof'].min()), float(camU['rprof'].max())],
               a_work=float(amax(camU['alpha'],120,200)), a_ret=float(amax(camU['alpha'],240,290)),
               fill={k: pose_fill[k].tolist() for k in ['B','C','D','E','P']},
               press={k: pose_press[k].tolist() for k in ['B','C','D','E','P']},
               tip_hi=float(tip.max()), tip_lo=float(tip.min()), TA=TA),
    sieve=dict(O2s=O2s.tolist(), Rb=Rbs, Lr=Lrs, rr=RRs, Ls=Ls, psi=psi_s,
               lam_left=lam_left, lam_fill=lam_fill, mu0=MU0S, r0=float(R0S),
               arm_angle=float(arm_angle_S),
               rpitch=[float(camS['rpitch'].min()), float(camS['rpitch'].max())],
               rprof=[float(camS['rprof'].min()), float(camS['rprof'].max())],
               a_push=float(amax(camS['alpha'],290,335)), a_ret=float(amax(camS['alpha'],90,135)),
               fill={k: sp_fill[k].tolist() for k in ['B','C','P']},
               left={k: sp_left[k].tolist() for k in ['B','C','P']},
               gB=gmin_B, gC=gmax_horiz))
with open(os.path.join(OUT, "结果.json"), "w") as f:
    json.dump(res, f, ensure_ascii=False, indent=1)
print("\n导出完成:", OUT)
