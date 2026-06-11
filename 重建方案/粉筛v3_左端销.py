# -*- coding: utf-8 -*-
"""粉筛 v3：托架销移至左端(双耳叉, Z=0 对中, 销高 Y=250, 左端面外伸20)
   重新综合 摆杆/连杆/支点/凸轮。装料位销 X=-47, 左停 -95, 行程48。"""
import numpy as np
from scipy.optimize import brentq

D = np.pi/180

def cyc(t):
    t = np.clip(t, 0, 1)
    return t - np.sin(2*np.pi*t)/(2*np.pi)

def law(phi, segs):
    phi = np.asarray(phi, float) % 360.0
    s = np.zeros_like(phi)
    for p0, p1, s0, s1 in segs:
        m = (phi >= p0) & (phi <= p1)
        s[m] = s0 + (s1-s0)*cyc((phi[m]-p0)/(p1-p0))
    return s

def dirv(a):
    return np.array([np.cos(a*D), np.sin(a*D)])

SIEVE_SEGS = lambda A: [(0,90,A,A),(90,135,A,0),(135,290,0,0),(290,335,0,A),(335,360,A,A)]
PHI = np.arange(0, 360, 0.5)

def cam_design(O2_, Lr_, mu0_, psi_fun, rr, sign=+1):
    psi = psi_fun(PHI)
    mu = mu0_ + sign*psi
    P = O2_[None,:] + Lr_*np.stack([np.cos(mu*D), np.sin(mu*D)], 1)
    c, s = np.cos(-PHI*D), np.sin(-PHI*D)
    Rp = np.stack([c*P[:,0]-s*P[:,1], s*P[:,0]+c*P[:,1]], 1)
    dphi = 0.5*D
    dR = (np.roll(Rp,-1,0)-np.roll(Rp,1,0))/(2*dphi)
    d2R = (np.roll(Rp,-1,0)-2*Rp+np.roll(Rp,1,0))/dphi**2
    T = dR/np.linalg.norm(dR, axis=1, keepdims=True)
    N = np.stack([-T[:,1], T[:,0]], 1)
    inward = -Rp/np.linalg.norm(Rp, axis=1, keepdims=True)
    flip = (np.sum(N*inward,1) < 0); N[flip] *= -1
    prof = Rp + rr*N
    cph, sph = np.cos(PHI*D), np.sin(PHI*D)
    Nf = np.stack([cph*N[:,0]-sph*N[:,1], sph*N[:,0]+cph*N[:,1]], 1)
    dpsi = (psi_fun(PHI+0.25)-psi_fun(PHI-0.25))/0.5
    vdir = np.stack([-np.sin(mu*D), np.cos(mu*D)], 1)*(sign*np.sign(dpsi))[:,None]
    cosa = np.abs(np.sum(Nf*vdir,1))
    alpha = np.degrees(np.arccos(np.clip(cosa,-1,1)))
    alpha[np.abs(dpsi) < 1e-6] = np.nan
    cross = dR[:,0]*d2R[:,1]-dR[:,1]*d2R[:,0]
    rho = (np.sum(dR**2,1))**1.5/np.where(np.abs(cross)<1e-12,1e-12,np.abs(cross))
    return dict(psi=psi, P=P, pitch=Rp, prof=prof, alpha=alpha, rho=rho,
                rpitch=np.linalg.norm(Rp,axis=1), rprof=np.linalg.norm(prof,axis=1))

def amax(alpha, p0, p1, margin=2.0):
    m = (PHI > p0+margin) & (PHI < p1-margin)
    return np.nanmax(alpha[m])

CY, CX_FILL, S = 250.0, -47.0, 48.0
TABLE_EDGE = -80.0
O2s = np.array([-113.0, 52.0]); Rbs, Lrs, RRs = 110.0, 50.0, 10.0
LAM_MID = 135.0

def Cx_of(lam, Ls):
    B = O2s + Rbs*dirv(lam)
    v = Ls**2 - (CY-B[1])**2
    return B[0] + np.sqrt(v) if v > 0 else np.nan

def half(Ls):
    g = lambda h: (Cx_of(LAM_MID-h, Ls) - Cx_of(LAM_MID+h, Ls)) - S
    return brentq(g, 4, 16)

Ls = brentq(lambda L: Cx_of(LAM_MID-half(L), L) - CX_FILL, 150, 215)
hs = half(Ls); psi_s = 2*hs
lam_left, lam_fill = LAM_MID+hs, LAM_MID-hs

def mu0s_of(r0):
    aO1 = np.degrees(np.arctan2(-O2s[1], -O2s[0]))
    a, b = np.linalg.norm(O2s), Lrs
    cg = (a*a + b*b - r0*r0)/(2*a*b)
    if abs(cg) > 1: raise ValueError
    g = np.degrees(np.arccos(cg))
    for mu in (aO1-g, aO1+g):
        P = O2s + Lrs*dirv(mu)
        t = np.array([-np.sin(mu*D), np.cos(mu*D)])
        if np.dot(P, -t) > 0:
            return mu
    raise ValueError

psiS = lambda ph: law(ph, SIEVE_SEGS(psi_s))
camS = None
for r0 in np.arange(np.floor(abs(np.linalg.norm(O2s)-Lrs))+3, 130, 1.0):
    try:
        mu0 = mu0s_of(r0)
    except ValueError:
        continue
    cd = cam_design(O2s, Lrs, mu0, psiS, RRs, -1)
    if amax(cd['alpha'],290,335) <= 30 and amax(cd['alpha'],90,135) <= 40:
        camS, R0S, MU0S = cd, r0, mu0
        break
assert camS is not None, "r0 无解"

def pose(psi):
    lam = lam_left - psi
    B = O2s + Rbs*dirv(lam)
    Cx = B[0] + np.sqrt(Ls**2 - (CY-B[1])**2)
    P = O2s + Lrs*dirv(MU0S - psi)
    return B, np.array([Cx, CY]), P, lam

Bf,Cf,Pf,lf = pose(psi_s); Bl,Cl,Pl,ll = pose(0.0)
worst = -1e9
for ps in np.linspace(0, psi_s, 60):
    B,C,_,_ = pose(ps)
    t = (216.0-B[1])/(C[1]-B[1])
    worst = max(worst, B[0]+t*(C[0]-B[0]))
gB, gH = 90.0, 0.0
for ps in np.linspace(0, psi_s, 60):
    B,C,_,lam = pose(ps)
    link = (C-B)/Ls
    gB = min(gB, np.degrees(np.arcsin(abs(float(np.cross(link, dirv(lam)))))))
    gH = max(gH, np.degrees(np.arctan2(link[1], link[0])))
aS = (MU0S-lam_left)%360
aS = 360-aS if aS > 180 else aS
print(f"O2s=({O2s[0]:.0f},{O2s[1]:.0f}) a={np.linalg.norm(O2s):.2f}  Rb={Rbs} Lr={Lrs} Ls={Ls:.2f}")
print(f"摆角={psi_s:.3f}  连杆臂方位: 左停{lam_left:.2f} 装料{lam_fill:.2f}  滚子臂左停mu0={MU0S:.2f}  夹角={aS:.2f}")
print(f"凸轮v3: r0={R0S} 节曲线 {camS['rpitch'].min():.2f}~{camS['rpitch'].max():.2f} 实际 {camS['rprof'].min():.2f}~{camS['rprof'].max():.2f}")
print(f"压力角: 推卸 {amax(camS['alpha'],290,335):.2f}  左退 {amax(camS['alpha'],90,135):.2f}  最小曲率半径 {np.nanmin(np.abs(camS['rho'])):.1f}")
print(f"销行程: {Cl[0]:.3f} -> {Cf[0]:.3f} (={Cf[0]-Cl[0]:.4f})")
print(f"装料位: B=({Bf[0]:.2f},{Bf[1]:.2f}) C=({Cf[0]:.2f},{CY}) P=({Pf[0]:.2f},{Pf[1]:.2f}) |P|={np.hypot(*Pf):.2f}")
print(f"左停位: B=({Bl[0]:.2f},{Bl[1]:.2f}) C=({Cl[0]:.2f},{CY}) P=({Pl[0]:.2f},{Pl[1]:.2f}) |P|={np.hypot(*Pl):.2f}")
ok = "通过" if worst < TABLE_EDGE else "不通过"
print(f"连杆穿台面平面最右点 X={worst:.2f} (需< {TABLE_EDGE})  {ok}")
print(f"传动角: 连杆-摆杆 min {gB:.1f}  连杆仰角 max {gH:.1f}")

def seg_min_r(A, Bp):
    ts = np.linspace(0, 1, 50)
    pts = A[None,:] + ts[:,None]*(Bp-A)[None,:]
    return np.min(np.hypot(pts[:,0], pts[:,1]))
print(f"滚子臂段到主轴最小距离: {min(seg_min_r(O2s,Pf), seg_min_r(O2s,Pl)):.1f} (下冲头凸轮最大半径64)")

import os
OUT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(OUT, "粉筛凸轮v3_SW.txt"), "w") as f:
    for x, y in camS['prof']:
        f.write(f"{x:.4f}\t{y:.4f}\t0\n")
    f.write(f"{camS['prof'][0,0]:.4f}\t{camS['prof'][0,1]:.4f}\t0\n")
np.savetxt(os.path.join(OUT, "粉筛凸轮v3.csv"),
           np.column_stack([PHI, camS['psi'], camS['rpitch'], camS['rprof'], np.nan_to_num(camS['alpha'])]),
           delimiter=",", header="phi_deg,psi_deg,r_pitch,r_profile,alpha_deg", comments="", fmt="%.4f")
print("已导出 粉筛凸轮v3_SW.txt / 粉筛凸轮v3.csv")
