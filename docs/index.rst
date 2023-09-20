######################
Amazon Braket Examples
######################

.. replite::
   :kernel: xeus-python
   :toolbar: 0
   :theme: JupyterLab Light
   :width: 100%
   :height: 600px

.. replite::
   :kernel: xeus-python
   :height: 600px

   import matplotlib.pyplot as plt
   import numpy as np

   x = np.linspace(0, 2 * np.pi, 200)
   y = np.sin(x)

   fig, ax = plt.subplots()
   ax.plot(x, y)
   plt.show()

.. jupyterlite::
   :width: 100%
   :height: 600px

.. retrolite:: ./0_Getting_Started.ipynb
   :width: 100%
   :height: 600px
   