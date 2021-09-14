***************
Prerequisites
***************

- Python3
- pip

********
Install
********

pip
====
Preferred method

Install
--------

.. tabbed:: pip

   .. code-block:: sh
      :caption: install

      pip install xdgpspconf


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip install xdgpspconf


Update
-------

.. tabbed:: pip

   .. code-block:: sh
      :caption: install

      pip install -U xdgpspconf


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip install -U xdgpspconf


Uninstall
----------

.. tabbed:: pip

   .. code-block:: sh
      :caption: uninstall

      pip uninstall xdgpspconf


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip uninstall xdgpspconf




`pspman <https://gitlab.com/pradyparanjpe/pspman>`__
=====================================================

(Linux only)

For automated management: updates, etc


Install
--------

.. code-block:: sh

   pspman -s -i https://gitlab.com/pradyparanjpe/xdgpspconf.git



Update
-------

.. code-block:: sh

    pspman


*That's all.*


Uninstall
----------

Remove installation:

.. code-block:: sh

    pspman -s -d xdgpspconf
