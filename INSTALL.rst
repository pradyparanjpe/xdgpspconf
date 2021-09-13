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

      pip install xdgpsp


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip install xdgpsp


Update
-------

.. tabbed:: pip

   .. code-block:: sh
      :caption: install

      pip install -U xdgpsp


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip install -U xdgpsp


Uninstall
----------

.. tabbed:: pip

   .. code-block:: sh
      :caption: uninstall

      pip uninstall xdgpsp


.. tabbed:: module import

   .. code-block:: sh
      :caption: if ``command not found: pip``

      python3 -m pip uninstall xdgpsp




`pspman <https://gitlab.com/pradyparanjpe/pspman>`__
=====================================================

(Linux only)

For automated management: updates, etc


Install
--------

.. code-block:: sh

   pspman -s -i https://gitlab.com/pradyparanjpe/xdgpsp.git



Update
-------

.. code-block:: sh

    pspman


*That's all.*


Uninstall
----------

Remove installation:

.. code-block:: sh

    pspman -s -d xdgpsp
