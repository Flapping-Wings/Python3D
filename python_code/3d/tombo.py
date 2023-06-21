import numpy as np
from globals import g
from nd_data import nd_data
from wing_total import wing_total
from lr_set_matrix import lr_set_matrix
from wing_m import wing_m

def tombo():
    # SETUP
    # -----

    # g.xb_f, g.nxb_f, g.nb_f, g.xc_f, g.nxc_f, g.nc_f, g.l_f, g.c_f, g.h_f,
    # g.xb_r, g.nxb_r, g.nb_r, g.xc_r, g.nxc_r, g.nc_r, g.l_r, g.c_r, g.h_r = \
    #     Wing()

    l, c, h, phiT, phiB, a, beta, delta, gMax, U, \
    xb_f, xc_f, xb_r, xc_r, b_f, b_r, e, d =      \
        nd_data(g.l_f, g.c_f, g.h_f, g.l_r, g.c_r, g.h_r, 
                g.phiT_, g.phiB_, g.a_, g.beta_, g.delta_, g.gMax_, g.U_, 
                g.xb_f, g.xc_f, g.xb_r, g.xc_r, g.b_f, g.b_r)
    
    g.LCUT = 0.1 * h[0]  
    
    log_input(c, a, d, gMax)

    # Front right wing
    xc_f, xb_f, xt_f, nxt_f, xC_f, nC_f = \
        wing_total(xb_f, g.nxb_f, g.nb_f, xc_f, g.nxc_f, g.nc_f)
    # Rear right wing
    xc_r, xb_r, xt_r, nxt_r, xC_r, nC_r = \
        wing_total(xb_r, g.nxb_r, g.nb_r, xc_r, g.nxc_r, g.nc_r)
    
    # Wake vortex magnitude array
    GAMw_f = np.zeros((g.nwing, g.nxb_f))
    GAMw_r = np.zeros((g.nwing, g.nxb_r))
    # Total wake vortex number
    nxw_f = 0; nxw_r = 0
    # Wake vortex location array (after convection)
    Xw_f = np.zeros((3, 4, g.nxb_f, g.nwing))
    Xw_r = np.zeros((3, 4, g.nxb_r, g.nwing))
    # Shed vortex location array 
    Xs_f = np.zeros((3, 4, g.nxb_f, g.nwing))
    Xs_r = np.zeros((3, 4, g.nxb_r, g.nwing))

    if g.nstep > 3:
        # Initialize the linear and angular impulse arrays
        limpa_f = np.zeros((3, g.nstep, g.nwing))
        limpa_r = np.zeros((3, g.nstep, g.nwing))
        aimpa_f = np.zeros((3, g.nstep, g.nwing))
        aimpa_r = np.zeros((3, g.nstep, g.nwing))
        limpw_f = np.zeros((3, g.nstep, g.nwing))
        limpw_r = np.zeros((3, g.nstep, g.nwing))
        aimpw_f = np.zeros((3, g.nstep, g.nwing))
        aimpw_r = np.zeros((3, g.nstep, g.nwing))

    # Normal velocity on the wing due to the wing motion & wake vortices
    Vnc_f  = np.zeros((g.nwing, nxt_f))
    Vnc_r  = np.zeros((g.nwing, nxt_r))
    Vncw_f = np.zeros((g.nwing, nxt_r))
    Vncw_r = np.zeros((g.nwing, nxt_f))

    # Sub-matrix for the non-penetration condition (self-terms)
    MVNs_f = np.zeros((nxt_f, nxt_f, g.nwing))
    MVNs_r = np.zeros((nxt_r, nxt_r, g.nwing))

    # Velocity value matrices
    VBW_f = np.zeros((3, 4, g.nxb_f, g.nwing))
    VBW_r = np.zeros((3, 4, g.nxb_r, g.nwing))

    # TODO: Document Xc_f/r
    Xc_f = np.zeros((3, 4, g.nxc_f, 2))
    Xc_r = np.zeros((3, 4, g.nxc_r, 2))
    # Space-fixed system coords of border elements on the wing
    Xb_f = np.zeros((3, 4, g.nxb_f, 2))
    Xb_r = np.zeros((3, 4, g.nxb_r, 2))
    # Global coords of total elements on the wing
    Xt_f = np.zeros((3, 4, nxt_f, 2))
    Xt_r = np.zeros((3, 4, nxt_r, 2))
    # Global coords of the collocation points on the wing
    XC_f = np.zeros((3, nxt_f, 2))
    XC_r = np.zeros((3, nxt_r, 2))
    # Unit normals at the collocation points on the wing
    NC_f = np.zeros((3, nxt_f, 2))
    NC_r = np.zeros((3, nxt_r, 2))


    # TIME MARCH
    # ----------
    for w in range(g.nwing):
        MVNs_f[:, :, w] = lr_set_matrix(w, xt_f, nxt_f, xC_f, nC_f)
        MVNs_r[:, :, w] = lr_set_matrix(w, xt_f, nxt_f, xC_f, nC_f)

    for g.istep in range(g.nstep):
        t = g.istep * g.dt

        # Get wing motion parameters
        phi = np.zeros(g.twing)
        theta = np.zeros(g.twing)
        dph = np.zeros(g.twing)
        dth = np.zeros(g.twing)

        for i in range(g.twing):
            phi[i], theta[i], dph[i], dth[i] = \
                wing_m(g.mpath[i], t, g.rt[i], g.tau[i], e[i], 
                       gMax[i], g.p[i], g.rtOff[i], phiT[i], phiB[i])
            
    # Get global coordinates of the points on the wing
    # for i in range(g.nwing):
    #     Xc_f[:,:,:,i], Xb_f[:,:,:,i], Xt_f[:,:,:,i], XC_f[:,:,i], NC_f[:,:,i] = \
    #         lr_mass_L2GT(i, beta[i], delta, phi[i], theta[i], a[i], U, t, b_f,
    #                      xc_f, xb_f, xt_f, xC_f, nC_f)


def check_input():
    if g.b_r - g.b_f >= 0.5 * (g.c_r + g.c_f):
        print("Wing clearance checked")
    else:
        raise ValueError("rear and forward wings interfere")
    
    if np.any(g.p < 4):
        raise ValueError("p must >=4 for all wings")
    
    if np.any(np.abs(g.rtOff) > 0.5):
        raise ValueError("-0.5 <= rtOff <= 0.5 must be satisfied for all wings")
    
    if np.any((g.tau < 0) | (g.tau >= 2)):
        raise ValueError("0 <= tau < 2 must be satisfied for all wings")

def log_input(c, a, d, gMax):
    # TODO: Print delta_, b_f, b_r
    # TODO: Print nxb_f, nxc_f, nxb_r, nxc_r
    # TODO: Print mpath
    # TODO: Print phiT_, phiB_
    # TODO: Print a_, beta_, f_
    # TODO: Print gMax_, p, rtOff, tau, 
    # TODO: Print U_
    # TODO: Print nstep, dt
    
    air = np.sqrt(np.sum(g.U_**2))
    # TODO: Print air speed
    if air > 1.0E-03:
        # Flapping/Air Seed Ratio
        fk = 2 * g.f_ * g.d_ / air
        # TODO: Print fk
        # Pitch/Flapping Speed Ratio
        r = 0.5 * ((0.5*c + a) / d) * (g.p / g.t_) * (gMax / g.f_)
        # TODO: Print r
        # Pitch/Air Speed Ratio
        k = fk * r
        # TODO: Print k
    else:
        # Pitch/Flapping Speed Ratio
        r = 0.5 * ((0.5*c + a) / d) * (g.p / g.t_) * (gMax / g.f_)
        # TODO: Print r


if __name__ == "__main__":
    check_input()
    tombo()
