#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #########################################################################
# Copyright (c) 2016, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2016. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# #########################################################################

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import logging

logger = logging.getLogger(__name__)


__author__ = "Doga Gursoy"
__copyright__ = "Copyright (c) 2016, UChicago Argonne, LLC."
__docformat__ = 'restructuredtext en'
__all__ = ['reconstruct', 'art', 'sirt', 'mlem', 'stream']


def reconstruct(probe, shape, data, rec):
    """ Reconstruct single x-ray beam data.

    Parameters
    ----------
    probe : Probe
    shape : list
        shape of the reconstruction grid.
    data : scalar
        Probe measurement dtaa.
    rec : ndarray
        Initialization matrix.
    """
    x0 = probe.p1.x
    y0 = probe.p1.y
    x1 = probe.p2.x
    y1 = probe.p2.y
    sx, sy = shape

    # grid frame (gx, gy)
    gx = np.linspace(0, 1, sy + 1)
    gy = np.linspace(0, 1, sy + 1)

    # avoid upper-right boundary errors
    if (x1 - x0) == 0:
        x0 += 1e-6
    if (y1 - y0) == 0:
        y0 += 1e-6

    # vector lengths (ax, ay)
    ax = (gx - x0) / (x1 - x0)
    ay = (gy - y0) / (y1 - y0)

    # edges of alpha (a0, a1)
    ax0 = min(ax[0], ax[-1])
    ax1 = max(ax[0], ax[-1])
    ay0 = min(ay[0], ay[-1])
    ay1 = max(ay[0], ay[-1])
    a0 = max(max(ax0, ay0), 0)
    a1 = min(min(ax1, ay1), 1)

    # sorted alpha vector
    cx = (ax >= a0) & (ax <= a1)
    cy = (ay >= a0) & (ay <= a1)
    alpha = np.sort(np.r_[ax[cx], ay[cy]])

    # lengths
    xv = x0 + alpha * (x1 - x0)
    yv = y0 + alpha * (y1 - y0)
    lx = np.ediff1d(xv)
    ly = np.ediff1d(yv)
    dist = np.sqrt(lx**2 + ly**2)
    dist2 = np.dot(dist, dist)
    ind = dist != 0

    # indexing
    mid = alpha[:-1] + np.ediff1d(alpha) / 2.
    xm = x0 + mid * (x1 - x0)
    ym = y0 + mid * (y1 - y0)
    ix = np.floor(sy * xm).astype('int')
    iy = np.floor(sy * ym).astype('int')

    # reconstruct
    sim = np.dot(dist[ind], rec[ix[ind], iy[ind]])
    if not dist2 == 0:
        upd = np.true_divide((data - sim), dist2)
        rec[ix[ind], iy[ind]] += dist[ind] * upd
    return rec


def art(probe, data, init, niter=10):
    """ Reconstruct data.
    """
    sx, sy = init.shape

    # grid frame (gx, gy)
    gx = np.linspace(0, 1, sy + 1)
    gy = np.linspace(0, 1, sy + 1)

    _init = np.zeros(init.shape)

    for n in range(niter):
        print (n)
        for m in range(len(probe.history)):
        # for m in range(3000):
            x0 = probe.history[m][0]
            y0 = probe.history[m][1]
            x1 = probe.history[m][2]
            y1 = probe.history[m][3]
            # print (m, x0, y0, x1, y1)

            # avoid upper-right boundary errors
            if (x1 - x0) == 0:
                x0 += 1e-6
            if (y1 - y0) == 0:
                y0 += 1e-6

            # vector lengths (ax, ay)
            ax = (gx - x0) / (x1 - x0)
            ay = (gy - y0) / (y1 - y0)

            # edges of alpha (a0, a1)
            ax0 = min(ax[0], ax[-1])
            ax1 = max(ax[0], ax[-1])
            ay0 = min(ay[0], ay[-1])
            ay1 = max(ay[0], ay[-1])
            a0 = max(max(ax0, ay0), 0)
            a1 = min(min(ax1, ay1), 1)

            # sorted alpha vector
            cx = (ax >= a0) & (ax <= a1)
            cy = (ay >= a0) & (ay <= a1)
            alpha = np.sort(np.r_[ax[cx], ay[cy]])

            # lengths
            xv = x0 + alpha * (x1 - x0)
            yv = y0 + alpha * (y1 - y0)
            lx = np.ediff1d(xv)
            ly = np.ediff1d(yv)
            dist = np.sqrt(lx**2 + ly**2)
            dist2 = np.dot(dist, dist)
            ind = dist != 0

            # indexing
            mid = alpha[:-1] + np.ediff1d(alpha) / 2.
            xm = x0 + mid * (x1 - x0)
            ym = y0 + mid * (y1 - y0)
            ix = np.floor(sy * xm).astype('int')
            iy = np.floor(sy * ym).astype('int')

            sim = np.dot(dist[ind], init[ix[ind], iy[ind]])
            if not dist2 == 0:
                upd = np.true_divide((data[m] - sim), dist2)
                init[ix[ind], iy[ind]] += dist[ind] * upd
    return init




def sirt(probe, data, init, niter=10):
    """ Reconstruct data.
    """
    sx, sy = init.shape

    # grid frame (gx, gy)
    gx = np.linspace(0, 1, sy + 1)
    gy = np.linspace(0, 1, sy + 1)

    for n in range(niter):

        update = np.zeros(init.shape)
        sumdist = np.zeros(init.shape)

        print (n)
        for m in range(len(probe.history)):
        # for m in range(100):
            x0 = probe.history[m][0]
            y0 = probe.history[m][1]
            x1 = probe.history[m][2]
            y1 = probe.history[m][3]

            # avoid upper-right boundary errors
            if (x1 - x0) == 0:
                x0 += 1e-6
            if (y1 - y0) == 0:
                y0 += 1e-6

            # vector lengths (ax, ay)
            ax = (gx - x0) / (x1 - x0)
            ay = (gy - y0) / (y1 - y0)

            # edges of alpha (a0, a1)
            ax0 = min(ax[0], ax[-1])
            ax1 = max(ax[0], ax[-1])
            ay0 = min(ay[0], ay[-1])
            ay1 = max(ay[0], ay[-1])
            a0 = max(max(ax0, ay0), 0)
            a1 = min(min(ax1, ay1), 1)

            # sorted alpha vector
            cx = (ax >= a0) & (ax <= a1)
            cy = (ay >= a0) & (ay <= a1)
            alpha = np.sort(np.r_[ax[cx], ay[cy]])

            # lengths
            xv = x0 + alpha * (x1 - x0)
            yv = y0 + alpha * (y1 - y0)
            lx = np.ediff1d(xv)
            ly = np.ediff1d(yv)
            dist = np.sqrt(lx**2 + ly**2)
            dist2 = np.dot(dist, dist)
            ind = dist != 0

            # indexing
            mid = alpha[:-1] + np.ediff1d(alpha) / 2.
            xm = x0 + mid * (x1 - x0)
            ym = y0 + mid * (y1 - y0)
            ix = np.floor(sy * xm).astype('int')
            iy = np.floor(sy * ym).astype('int')

            sumdist[ix[ind], iy[ind]] += dist
            sim = np.dot(dist[ind], init[ix[ind], iy[ind]])
            if not dist2 == 0:
                upd = np.true_divide((data[m] - sim), dist2)
                update[ix[ind], iy[ind]] += dist[ind] * upd

        init += np.true_divide(update, sumdist * sy) 
    return init




def mlem(probe, data, init, niter=10):
    """ Reconstruct data.
    """
    sx, sy = init.shape

    # grid frame (gx, gy)
    gx = np.linspace(0, 1, sy + 1)
    gy = np.linspace(0, 1, sy + 1)

    for n in range(niter):

        update = np.zeros(init.shape)
        sumdist = np.zeros(init.shape)

        print (n)
        for m in range(len(probe.history)):
        # for m in range(3000):
        # for m in range(100):
            x0 = probe.history[m][0]
            y0 = probe.history[m][1]
            x1 = probe.history[m][2]
            y1 = probe.history[m][3]

            # avoid upper-right boundary errors
            if (x1 - x0) == 0:
                x0 += 1e-6
            if (y1 - y0) == 0:
                y0 += 1e-6

            # vector lengths (ax, ay)
            ax = (gx - x0) / (x1 - x0)
            ay = (gy - y0) / (y1 - y0)

            # edges of alpha (a0, a1)
            ax0 = min(ax[0], ax[-1])
            ax1 = max(ax[0], ax[-1])
            ay0 = min(ay[0], ay[-1])
            ay1 = max(ay[0], ay[-1])
            a0 = max(max(ax0, ay0), 0)
            a1 = min(min(ax1, ay1), 1)

            # sorted alpha vector
            cx = (ax >= a0) & (ax <= a1)
            cy = (ay >= a0) & (ay <= a1)
            alpha = np.sort(np.r_[ax[cx], ay[cy]])

            # lengths
            xv = x0 + alpha * (x1 - x0)
            yv = y0 + alpha * (y1 - y0)
            lx = np.ediff1d(xv)
            ly = np.ediff1d(yv)
            dist = np.sqrt(lx**2 + ly**2)
            dist2 = np.dot(dist, dist)
            ind = dist != 0

            # indexing
            mid = alpha[:-1] + np.ediff1d(alpha) / 2.
            xm = x0 + mid * (x1 - x0)
            ym = y0 + mid * (y1 - y0)
            ix = np.floor(sy * xm).astype('int')
            iy = np.floor(sy * ym).astype('int')

            sumdist[ix[ind], iy[ind]] += dist
            sim = np.dot(dist[ind], init[ix[ind], iy[ind]])
            if not sim == 0:
                upd = np.true_divide(data[m] , sim)
                update[ix[ind], iy[ind]] += dist[ind] * upd

        init[sumdist > 0] *= np.true_divide(update[sumdist > 0], sumdist[sumdist > 0] * sy) 
    return init



def stream(probe, data, init):
    """ Reconstruct data.
    """
    sx, sy = init.shape

    # grid frame (gx, gy)
    gx = np.linspace(0, 1, sy + 1)
    gy = np.linspace(0, 1, sy + 1)

    for m in range(3000):
        print (m)

        update = np.zeros(init.shape)
        sumdist = np.zeros(init.shape)

        for n in range(300):
            x0 = probe.history[m+n][0]
            y0 = probe.history[m+n][1]
            x1 = probe.history[m+n][2]
            y1 = probe.history[m+n][3]

            # avoid upper-right boundary errors
            if (x1 - x0) == 0:
                x0 += 1e-6
            if (y1 - y0) == 0:
                y0 += 1e-6

            # vector lengths (ax, ay)
            ax = (gx - x0) / (x1 - x0)
            ay = (gy - y0) / (y1 - y0)

            # edges of alpha (a0, a1)
            ax0 = min(ax[0], ax[-1])
            ax1 = max(ax[0], ax[-1])
            ay0 = min(ay[0], ay[-1])
            ay1 = max(ay[0], ay[-1])
            a0 = max(max(ax0, ay0), 0)
            a1 = min(min(ax1, ay1), 1)

            # sorted alpha vector
            cx = (ax >= a0) & (ax <= a1)
            cy = (ay >= a0) & (ay <= a1)
            alpha = np.sort(np.r_[ax[cx], ay[cy]])

            # lengths
            xv = x0 + alpha * (x1 - x0)
            yv = y0 + alpha * (y1 - y0)
            lx = np.ediff1d(xv)
            ly = np.ediff1d(yv)
            dist = np.sqrt(lx**2 + ly**2)
            dist2 = np.dot(dist, dist)
            ind = dist != 0

            # indexing
            mid = alpha[:-1] + np.ediff1d(alpha) / 2.
            xm = x0 + mid * (x1 - x0)
            ym = y0 + mid * (y1 - y0)
            ix = np.floor(sy * xm).astype('int')
            iy = np.floor(sy * ym).astype('int')

            sumdist[ix[ind], iy[ind]] += dist
            sim = np.dot(dist[ind], init[ix[ind], iy[ind]])
            if not sim == 0:
                upd = np.true_divide(data[m+n] , sim)
                update[ix[ind], iy[ind]] += dist[ind] * upd

        # init[sumdist > 0] += np.true_divide(update[sumdist > 0], sumdist[sumdist > 0] * sy) 
        init[sumdist > 0] *= np.true_divide(update[sumdist > 0], sumdist[sumdist > 0] * sy)
    return init

