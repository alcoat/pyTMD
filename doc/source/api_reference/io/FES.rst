===
FES
===

- Reads files for Finite Element Solution (FES), Empirical Ocean Tide (EOT), and Hamburg direct data Assimilation Methods for Tides (HAMTIDE) models

   * ascii
   * netCDF4
- Spatially interpolates tidal constituents to input coordinates

Calling Sequence
----------------

.. code-block:: python

    import pyTMD.io
    amp,ph = pyTMD.io.FES.extract_constants(ilon, ilat, model_files,
       type='z',
       version=version,
       method='spline',
       compressed=True,
       scale=1.0/100.0)

`Source code`__

.. __: https://github.com/pyTMD/pyTMD/blob/main/pyTMD/io/FES.py

.. autofunction:: pyTMD.io.FES.extract_constants

.. autofunction:: pyTMD.io.FES.read_constants

.. autofunction:: pyTMD.io.FES.interpolate_constants

.. autofunction:: pyTMD.io.FES.read_ascii_file

.. autofunction:: pyTMD.io.FES.read_netcdf_file

.. autofunction:: pyTMD.io.FES.output_netcdf_file

.. autofunction:: pyTMD.io.FES._extend_array

.. autofunction:: pyTMD.io.FES._extend_matrix

.. autofunction:: pyTMD.io.FES._crop

.. autofunction:: pyTMD.io.FES._shift
