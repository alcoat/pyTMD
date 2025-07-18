=======
ellipse
=======

- Expresses the amplitudes and phases for the `u` and `v` components in terms of four ellipse parameters using Foreman's formula :cite:p:`Foreman:1989dt`

Calling Sequence
----------------

.. code-block:: python

    import pyTMD
    umajor,uminor,uincl,uphase = pyTMD.ellipse.ellipse(u,v)

`Source code`__

.. __: https://github.com/pyTMD/pyTMD/blob/main/pyTMD/ellipse.py

.. autofunction:: pyTMD.ellipse.ellipse

.. autofunction:: pyTMD.ellipse.inverse

.. autofunction:: pyTMD.ellipse._xy
