"""Linear NOTEARS (Zheng, Aragam, Ravikumar, Xing, NeurIPS 2018), augmented-Lagrangian solver with L-BFGS-B.

Re-implementation of the reference algorithm (github.com/xunzheng/notears, notears/linear.py, Apache-2.0) for BND-06, so the
CausalArena NOTEARS row can be run without torch. Same objective (least squares 'l2' loss + lambda1 * L1, acyclicity
h(W) = tr(exp(W o W)) - d), same split of W into positive and negative parts with bounds, same schedule (rho x10 until
h shrinks by 4x, alpha += rho * h, stop at h <= h_tol or rho >= rho_max). The authors' runner (TabCausal run_notears.py)
calls it with lambda1 = 0.1, loss 'l2', w_threshold = 0 (continuous weights), h_tol = 1e-8, max_iter = 100, and binarises
|W| >= 0.5 afterwards.
"""
import numpy as np
import scipy.linalg as sla
import scipy.optimize as sopt


def notears_linear(X, lambda1=0.1, max_iter=100, h_tol=1e-8, rho_max=1e16, w_threshold=0.0):
    n, d = X.shape
    X = X - X.mean(axis=0, keepdims=True)

    def _adj(w):
        return (w[:d * d] - w[d * d:]).reshape([d, d])

    def _loss(W):
        R = X - X @ W
        loss = 0.5 / n * (R ** 2).sum()
        G = -1.0 / n * X.T @ R
        return loss, G

    def _h(W):
        E = sla.expm(W * W)
        h = np.trace(E) - d
        G = E.T * W * 2
        return h, G

    def _func(w):
        W = _adj(w)
        loss, G_loss = _loss(W)
        h, G_h = _h(W)
        obj = loss + 0.5 * rho * h * h + alpha * h + lambda1 * w.sum()
        G_smooth = G_loss + (rho * h + alpha) * G_h
        g_obj = np.concatenate((G_smooth + lambda1, -G_smooth + lambda1), axis=None)
        return obj, g_obj

    w_est, rho, alpha, h = np.zeros(2 * d * d), 1.0, 0.0, np.inf
    bnds = [(0, 0) if i == j else (0, None) for _ in range(2) for i in range(d) for j in range(d)]
    for _ in range(max_iter):
        w_new, h_new = None, None
        while rho < rho_max:
            sol = sopt.minimize(_func, w_est, method="L-BFGS-B", jac=True, bounds=bnds)
            w_new = sol.x
            h_new, _ = _h(_adj(w_new))
            if h_new > 0.25 * h:
                rho *= 10
            else:
                break
        w_est, h = w_new, h_new
        alpha += rho * h
        if h <= h_tol or rho >= rho_max:
            break
    W_est = _adj(w_est)
    W_est[np.abs(W_est) < w_threshold] = 0
    return W_est
