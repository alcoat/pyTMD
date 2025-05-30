#!/usr/bin/env python
u"""
math.py
Written by Tyler Sutterley (04/2025)
Special functions of mathematical physics

PYTHON DEPENDENCIES:
    numpy: Scientific Computing Tools For Python
        https://numpy.org
        https://numpy.org/doc/stable/user/numpy-for-matlab-users.html
    scipy: Scientific Tools for Python
        https://docs.scipy.org/doc/

UPDATE HISTORY:
    Updated 04/2025: use numpy power function over using pow for consistency
    Updated 01/2025: added function for fully-normalized Legendre polynomials
    Updated 12/2024: added function to calculate an aliasing frequency
    Written 11/2024
"""
from __future__ import annotations

import numpy as np
from scipy.special import factorial

__all__ = [
    "polynomial_sum",
    "normalize_angle",
    "rotate",
    "aliasing",
    "legendre",
    "assoc_legendre",
    "sph_harm"
]

# PURPOSE: calculate the sum of a polynomial function of time
def polynomial_sum(
        coefficients: list | np.ndarray,
        t: np.ndarray
    ):
    """
    Calculates the sum of a polynomial function using Horner's method
    :cite:p:`Horner:1819br`

    Parameters
    ----------
    coefficients: list or np.ndarray
        leading coefficient of polynomials of increasing order
    t: np.ndarray
        delta time in units for a given astronomical longitudes calculation
    """
    # convert time to array if importing a single value
    t = np.atleast_1d(t)
    return np.sum([c * (t ** i) for i, c in enumerate(coefficients)], axis=0)

def normalize_angle(
        theta: float | np.ndarray,
        circle: float = 360.0
    ):
    """
    Normalize an angle to a single rotation

    Parameters
    ----------
    theta: float or np.ndarray
        Angle to normalize
    circle: float, default 360.0
        Circle of the angle
    """
    return np.mod(theta, circle)

def rotate(
        theta: float | np.ndarray,
        axis: str = 'x'
    ):
    """
    Rotate a 3-dimensional matrix about a given axis

    Parameters
    ----------
    theta: float or np.ndarray
        Angle of rotation in radians
    axis: str, default 'x'
        Axis of rotation (``'x'``, ``'y'``, or ``'z'``)
    """
    # allocate for output rotation matrix
    R = np.zeros((3, 3, len(np.atleast_1d(theta))))
    if (axis.lower() == 'x'):
        # rotate about x-axis
        R[0,0,:] = 1.0
        R[1,1,:] = np.cos(theta)
        R[1,2,:] = np.sin(theta)
        R[2,1,:] = -np.sin(theta)
        R[2,2,:] = np.cos(theta)
    elif (axis.lower() == 'y'):
        # rotate about y-axis
        R[0,0,:] = np.cos(theta)
        R[0,2,:] = -np.sin(theta)
        R[1,1,:] = 1.0
        R[2,0,:] = np.sin(theta)
        R[2,2,:] = np.cos(theta)
    elif (axis.lower() == 'z'):
        # rotate about z-axis
        R[0,0,:] = np.cos(theta)
        R[0,1,:] = np.sin(theta)
        R[1,0,:] = -np.sin(theta)
        R[1,1,:] = np.cos(theta)
        R[2,2,:] = 1.0
    else:
        raise ValueError(f'Invalid axis {axis}')
    # return the rotation matrix
    return R

def aliasing(
        f: float,
        fs: float
    ) -> float:
    """
    Calculate the aliasing frequency of a signal

    Parameters
    ----------
    f: float
        Frequency of the signal
    fs: float
        Sampling frequency of the signal

    Returns
    -------
    fa: float
        Aliasing frequency of the signal
    """
    fa = np.abs(f - fs*np.round(f/fs))
    return fa

def legendre(
        l: int,
        x: np.ndarray,
        m: int = 0
    ):
    """
    Computes associated Legendre functions for a particular degree
    and order :cite:p:`Munk:1966go,HofmannWellenhof:2006hy`

    Parameters
    ----------
    l: int
        degree of the Legendre polynomials (0 to 3)
    x: np.ndarray
        elements ranging from -1 to 1

        Typically ``cos(theta)``, where ``theta`` is the colatitude in radians
    m: int, default 0
        order of the Legendre polynomials (0 to ``l``)

    Returns
    -------
    Plm: np.ndarray
        Legendre polynomials of degree ``l`` and order ``m``
    """
    # verify values are integers
    l = np.int64(l)
    m = np.int64(m)
    # assert values
    assert (l >= 0) and (l <= 3), 'Degree must be between 0 and 3'
    assert (m >= 0) and (m <= l), 'Order must be between 0 and l'
    # verify dimensions
    singular_values = (np.ndim(x) == 0)
    x = np.atleast_1d(x).flatten()
    # if x is the cos of colatitude, u is the sine
    u = np.sqrt(1.0 - x**2)
    # size of the x array
    nx = len(x)
    # complete matrix of associated legendre functions
    # up to degree and order 3
    Plm = np.zeros((4, 4, nx), dtype=np.float64)
    # since tides only use low-degree harmonics:
    # functions are hard coded rather than using a recursion relation
    Plm[0, 0, :] = 1.0
    Plm[1, 0, :] = x
    Plm[1, 1, :] = u
    Plm[2, 0, :] = 0.5*(3.0*x**2 - 1.0)
    Plm[2, 1, :] = 3.0*x*u
    Plm[2, 2, :] = 3.0*u**2
    Plm[3, 0, :] = 0.5*(5.0*x**3 - 3.0*x)
    Plm[3, 1, :] = 1.5*(5.0*x**2 - 1.0)*u
    Plm[3, 2, :] = 15.0*x*u**2
    Plm[3, 3, :] = 15.0*u**3
    # return values
    if singular_values:
        return np.power(-1.0, m)*Plm[l, m, 0]
    else:
        return np.power(-1.0, m)*Plm[l, m, :]

def assoc_legendre(lmax, x):
    """
    Computes fully-normalized associated Legendre Polynomials using a
    standard forward-column method :cite:p:`Colombo:1981vh`
    :cite:p:`HofmannWellenhof:2006hy`

    Parameters
    ----------
    lmax: int
        maximum degree and order of Legendre polynomials
    x: np.ndarray
        elements ranging from -1 to 1

        Typically ``cos(theta)``, where ``theta`` is the colatitude in radians

    Returns
    -------
    Plm: np.ndarray
        fully-normalized Legendre polynomials
    """
    # verify values are integers
    lmax = np.int64(lmax)
    # verify dimensions
    singular_values = (np.ndim(x) == 0)
    x = np.atleast_1d(x).flatten()
    # if x is the cos of colatitude, u is the sine
    u = np.sqrt(1.0 - x**2)
    # size of the x array
    nx = len(x)
    # allocate for associated legendre functions
    Plm = np.zeros((lmax+1,lmax+1,nx))
    # initial polynomials for the recursion
    Plm[0,0,:] = 1.0
    Plm[1,0,:] = np.sqrt(3.0)*x
    Plm[1,1,:] = np.sqrt(3.0)*u
    for l in range(2, lmax+1):
        # normalization factor
        norm = np.sqrt(2.0*l+1.0)
        for m in range(0, l):
            # zonal and tesseral terms (non-sectorial)
            a = np.sqrt((2.0*l-1.0)/((l-m)*(l+m)))
            b = np.sqrt((l+m-1.0)*(l-m-1.0)/((l-m)*(l+m)*(2.0*l-3.0)))
            Plm[l,m,:] = a*norm*x*Plm[l-1,m,:] - b*norm*Plm[l-2,m,:]
        # sectorial terms: serve as seed values for the recursion
        # starting with P00 and P11 (outside the loop)
        Plm[l,l,:] = u*norm*np.sqrt(1.0/(2.0*l))*Plm[l-1,l-1,:]
    # return values
    if singular_values:
        return Plm[:, :, 0]
    else:
        return Plm

def sph_harm(
        l: int,
        theta: np.ndarray,
        phi: np.ndarray,
        m: int = 0
    ):
    """
    Computes the spherical harmonics for a particular degree
    and order :cite:p:`Munk:1966go,HofmannWellenhof:2006hy`

    Parameters
    ----------
    l: int
        degree of the spherical harmonics (0 to 3)
    theta: np.ndarray
        colatitude in radians
    phi: np.ndarray
        longitude in radians
    m: int, default 0
        order of the spherical harmonics (0 to ``l``)

    Returns
    -------
    Ylm: np.ndarray
        complex spherical harmonics of degree ``l`` and order ``m``
    """
    # verify dimensions
    singular_values = (np.ndim(theta) == 0)
    theta = np.atleast_1d(theta).flatten()
    phi = np.atleast_1d(phi).flatten()
    # assert dimensions
    assert len(theta) == len(phi), 'coordinates must have the same dimensions'
    # normalize associated Legendre functions
    # following Munk and Cartwright (1966)
    norm = np.sqrt(factorial(l - m)/factorial(l + m))
    Plm = norm*legendre(l, np.cos(theta), m=m)
    # spherical harmonics of degree l and order m
    dfactor = np.sqrt((2.0*l + 1.0)/(4.0*np.pi))
    Ylm = dfactor*Plm*np.sin(theta)*np.exp(1j*m*phi)
    # return values
    if singular_values:
        return Ylm[0]
    else:
        return Ylm
