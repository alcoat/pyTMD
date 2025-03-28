#!/usr/bin/env python
u"""
test_spatial.py (11/2020)
Verify spatial operations
"""
import pytest
import numpy as np
import pyTMD.spatial

# PURPOSE: test the data type function
def test_data_type():
    # test drift type
    exp = 'drift'
    # number of data points
    npts = 30; ntime = 30
    x = np.random.rand(npts)
    y = np.random.rand(npts)
    t = np.random.rand(ntime)
    obs = pyTMD.spatial.data_type(x,y,t)
    assert (obs == exp)
    # test grid type
    exp = 'grid'
    xgrid,ygrid = np.meshgrid(x,y)
    obs = pyTMD.spatial.data_type(xgrid,ygrid,t)
    assert (obs == exp)
    # test grid type with spatial dimensions
    exp = 'grid'
    nx = 30; ny = 20; ntime = 10
    x = np.random.rand(nx)
    y = np.random.rand(ny)
    t = np.random.rand(ntime)
    xgrid,ygrid = np.meshgrid(x,y)
    obs = pyTMD.spatial.data_type(xgrid,ygrid,t)
    assert (obs == exp)
    # test time series type
    exp = 'time series'
    # number of data points
    npts = 1; ntime = 1
    x = np.random.rand(npts)
    y = np.random.rand(npts)
    t = np.random.rand(ntime)
    obs = pyTMD.spatial.data_type(x,y,t)
    assert (obs == exp)
    # test catch for unknown data type
    msg = 'Unknown data type'
    # number of data points
    npts = 30; ntime = 10
    x = np.random.rand(npts)
    y = np.random.rand(npts)
    t = np.random.rand(ntime)
    with pytest.raises(ValueError, match=msg):
        pyTMD.spatial.data_type(x,y,t)

# PURPOSE: test ellipsoidal parameters within spatial module
def test_ellipsoid_parameters():
    assert pyTMD.spatial._wgs84.a_axis == 6378137.0
    assert pyTMD.spatial._wgs84.flat == (1.0/298.257223563)

# PURPOSE: test ellipsoid conversion
def test_convert_ellipsoid():
    # semimajor axis (a) and flattening (f) for TP and WGS84 ellipsoids
    atop,ftop = (6378136.3,1.0/298.257)
    awgs,fwgs = (6378137.0,1.0/298.257223563)
    # create latitude and height array in WGS84
    lat_WGS84 = 90.0 - np.arange(181,dtype=np.float64)
    elev_WGS84 = 3000.0 + np.zeros((181),dtype=np.float64)
    # convert from WGS84 to Topex/Poseidon Ellipsoids
    lat_TPX,elev_TPX = pyTMD.spatial.convert_ellipsoid(lat_WGS84, elev_WGS84,
        awgs, fwgs, atop, ftop, eps=1e-12, itmax=10)
    # check minimum and maximum are expected from NSIDC IDL program
    # ftp://ftp.nsidc.org/DATASETS/icesat/tools/idl/ellipsoid/test_ce.pro
    minlat = np.min(lat_TPX-lat_WGS84)
    maxlat = np.max(lat_TPX-lat_WGS84)
    explat = [-1.2305653e-7,1.2305653e-7]
    minelev = 100.0*np.min(elev_TPX-elev_WGS84)
    maxelev = 100.0*np.max(elev_TPX-elev_WGS84)
    expelev = [70.000000,71.368200]
    assert np.isclose([minlat,maxlat],explat).all()
    assert np.isclose([minelev,maxelev],expelev).all()
    # convert back from Topex/Poseidon to WGS84 Ellipsoids
    phi_WGS84,h_WGS84 = pyTMD.spatial.convert_ellipsoid(lat_TPX, elev_TPX,
        atop, ftop, awgs, fwgs, eps=1e-12, itmax=10)
    # check minimum and maximum are expected from NSIDC IDL program
    # ftp://ftp.nsidc.org/DATASETS/icesat/tools/idl/ellipsoid/test_ce.pro
    minlatdel = np.min(phi_WGS84-lat_WGS84)
    maxlatdel = np.max(phi_WGS84-lat_WGS84)
    explatdel = [-2.1316282e-14,2.1316282e-14]
    minelevdel = 100.0*np.min(h_WGS84-elev_WGS84)
    maxelevdel = 100.0*np.max(h_WGS84-elev_WGS84)
    expelevdel = [-1.3287718e-7,1.6830199e-7]
    assert np.isclose([minlatdel,maxlatdel],explatdel).all()
    assert np.isclose([minelevdel,maxelevdel],expelevdel,atol=1e-5).all()

# PURPOSE: verify cartesian to geodetic conversions
def test_convert_geodetic():
    # choose a random set of locations
    latitude = -90.0 + 180.0*np.random.rand(100)
    longitude = -180.0 + 360.0*np.random.rand(100)
    height = 2000.0*np.random.rand(100)
    # ellipsoidal parameters
    a_axis = pyTMD.spatial._wgs84.a_axis
    flat = pyTMD.spatial._wgs84.flat
    # convert to cartesian coordinates
    x, y, z = pyTMD.spatial.to_cartesian(longitude, latitude, h=height,
        a_axis=a_axis, flat=flat)
    # convert back to geodetic coordinates
    ln1, lt1, h1 = pyTMD.spatial.to_geodetic(x, y, z,
        a_axis=a_axis, flat=flat, method='moritz')
    ln2, lt2, h2 = pyTMD.spatial.to_geodetic(x, y, z,
        a_axis=a_axis, flat=flat, method='bowring')
    ln3, lt3, h3 = pyTMD.spatial.to_geodetic(x, y, z,
        a_axis=a_axis, flat=flat, method='zhu')
    # validate outputs for Moritz iterative method
    assert np.isclose(longitude, ln1).all()
    assert np.isclose(latitude, lt1).all()
    assert np.isclose(height, h1).all()
    # validate outputs for Bowring iterative method
    assert np.isclose(longitude, ln2).all()
    assert np.isclose(latitude, lt2).all()
    assert np.isclose(height, h2).all()
    # validate outputs for Zhu closed-form method
    assert np.isclose(longitude, ln3).all()
    assert np.isclose(latitude, lt3).all()
    assert np.isclose(height, h3).all()

# PURPOSE: test wrap longitudes
def test_wrap_longitudes():
    # number of data points
    lon = np.arange(360)
    obs = pyTMD.spatial.wrap_longitudes(lon)
    # expected wrapped longitudes
    exp = np.zeros((360))
    exp[:181] = np.arange(181)
    exp[181:] = np.arange(-179,0)
    assert np.isclose(obs,exp).all()

# PURPOSE: test the conversion of degrees to DMS
def test_degrees_to_DMS():
    # test a range of angles
    d = np.array([180.0, -180.0, 180.75, -180.75, 180.755, -180.755])
    degs, mins, secs = pyTMD.spatial.to_dms(d)
    expdeg = np.array([180, -180, 180, -180, 180, -180])
    expmin = np.array([0, 0, 45, 45, 45, 45])
    expsec = np.array([0, 0, 0, 0, 18, 18])
    assert np.all(degs == expdeg)
    assert np.all(mins == expmin)
    assert np.all(secs == expsec)

# PURPOSE: test the conversion of DMS to degrees
def test_DMS_to_degrees():
    # test a range of angles
    degs = np.array([180, -180, 180, -180, 180, -180])
    mins = np.array([0, 0, 45, 45, 45, 45])
    secs = np.array([0, 0, 0, 0, 18, 18])
    d = pyTMD.spatial.from_dms(degs, mins, secs)
    expd = np.array([180.0, -180.0, 180.75, -180.75, 180.755, -180.755])
    assert np.all(d == expd)

# PURPOSE: test the conversion of ECEF to ENU coordinates
def test_ECEF_to_ENU():
    Xexp, Yexp, Zexp = (3771793.968, 140253.342, 5124304.349)
    Eexp, Nexp, Uexp = (8534.192304843, 90086.3793375129, -569.0841634049)
    lon0, lat0 = (2.0, 53.0)
    E, N, U = pyTMD.spatial.to_ENU(Xexp, Yexp, Zexp, lon0=lon0, lat0=lat0)
    assert np.isclose(E, Eexp)
    assert np.isclose(N, Nexp)
    assert np.isclose(U, Uexp)
    X, Y, Z = pyTMD.spatial.from_ENU(E, N, U, lon0=lon0, lat0=lat0)
    assert np.isclose(X, Xexp)
    assert np.isclose(Y, Yexp)
    assert np.isclose(Z, Zexp)

# PURPOSE: test the conversion of ECEF to celestial horizontal coordinates
def test_ECEF_to_horizontal():
    # US Naval Observatory (USNO)
    lon0 = -77.0669
    lat0 = 38.9215
    h0 = 92.0
    # solar ephemerides at J2000
    SX =  1.353631936e11
    SY =  1.938584775e9
    SZ = -5.755477511e10
    # lunar ephemerides at J2000
    LX =  2.09322658e8
    LY = -3.35161630e8
    LZ = -7.60803221e7
    # convert from ECEF to east-north-up (ENU) coordinates
    SE, SN, SU = pyTMD.spatial.to_ENU(SX, SY, SZ,
        lon0=lon0, lat0=lat0, h0=h0)
    LE, LN, LU = pyTMD.spatial.to_ENU(LX, LY, LZ,
        lon0=lon0, lat0=lat0, h0=h0)
    # convert from ENU to horizontal coordinates
    salt, saz, sdist = pyTMD.spatial.to_horizontal(SE, SN, SU)
    lalt, laz, ldist = pyTMD.spatial.to_horizontal(LE, LN, LU)
    # calculate zenith angle from ECEF coordinates
    solar_zenith = pyTMD.spatial.to_zenith(SX, SY, SZ,
        lon0=lon0, lat0=lat0, h0=h0)
    lunar_zenith = pyTMD.spatial.to_zenith(LX, LY, LZ,
        lon0=lon0, lat0=lat0, h0=h0)
    # check solar azimuth and elevation
    assert np.isclose(salt, -5.486, atol=0.001)
    assert np.isclose(saz, 115.320, atol=0.001)
    # check lunar azimuth and elevation
    assert np.isclose(lalt, 36.381, atol=0.001)
    assert np.isclose(laz, 156.297, atol=0.001)
    # check solar and lunar zenith angles
    assert np.isclose(solar_zenith, 95.486, atol=0.001)
    assert np.isclose(lunar_zenith, 53.619, atol=0.001)
    # verify relation between altitudes and zenith angles
    assert solar_zenith == (90.0 - salt)
    assert lunar_zenith == (90.0 - lalt)
