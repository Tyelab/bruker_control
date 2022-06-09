#####################################
Bruker's (Legacy) Ultima Investigator
#####################################

The microscope this repository has been developed for is theoretically capable of interacting with any multi-photon microscope from
the `Bruker Corporation <https://www.bruker.com/en/products-and-solutions/fluorescence-microscopy/multiphoton-microscopes.html>`_ 
since each scope relies upon `Prairie View software and API <https://pvupdate.blogspot.com/>`_. However, it only has been tested
while using a legacy `Ultima Investigator <https://www.bruker.com/en/products-and-solutions/fluorescence-microscopy/multiphoton-microscopes/ultima-investigator.html>`_.
It was purchased by the Tye Lab when the system was first entering its commercial phase around 2012. Given its age, there are
things unique to our scope involving both the scope's hardware and software.

This page documents these aspects and also provides notes about the microscope's use as well.

**************************
Prairie View Configuration
**************************

Prairie View has a configuration utility (get image of configuration tool above here) that lets you set many different parameters
related to the hardware running the system. These settings include, among many:
- Laser Settings (i.e. pockels, beam path, shutter path)
- PMT Settings
- Microscope Axis Controller (X/Y/Z plane motion)
- Z-Focus Devices

These settings should *not* be changed by the user of the system without the explicit confirmation of Team2P members and a representative
from Bruker's support team.

You can find this tool by going to your Windows search bar and typing ``Configuration`` into the box. The OS will find the shortcut for you.

(gif goes here)

Here is what that page looks like:

(insert image here)

Tye Lab Specific Configuration Settings
***************************************

The lab's microscope settings had to be customized some to enable the use of whole-field LED stimulation for optogenetic manipulation experiments.
In order to use this feature, Prairie View had to be tricked into thinking it has the ability to perform point stimulations via spiral galvo operations.
Point stimulations refer to the use of a stimulation laser that will stimulate one point in the field of view for your experiment. Typically, this point
is a specific cell or list of cells an experimenter wants to manipulate during imaging. Our scope doesn't have this ability as it's missing both the
spiral galvos themselves as well as the stimulation laser necessary to perform these functions. However, in order to trigger stimulations through the
Voltage Output command in Prairie View, Prarie View must think that this hardware is present. This trickery is done by changing two settings in the
Lasers/Shutters tab of the Configuration App as well as performing a calibration for the non-existent uncaging galvo ability.

Laser Settings
--------------

Originally, the laser settings for our scope looked like this:

(insert original full image here)

You'll notice that:
- The ``Device Type`` field shows ``Imaging (DAQ Buffered)``
- The ``Shared Line`` field  cannot be toggled
- The ``Mark Points/Uncaging`` input boxes can be toggled (strangely)
- The first option in ``Uncaging`` settings stating ``Uncaging Galvos Present / Simulatneous Uncaging`` is *not* checked

The trick is to change the ``Device Type`` field and the ``Uncaging Galvos Present / Simultaneous Uncaging`` setting as shown below.

(insert current full image here)

Notice that:
- The ``Device Type`` field  shows ``Imaging/Uncaging (Alt. Beam Route)``
- The ``Shared Line`` field can be toggled. *Don't* change the number there.
- The ``Mark Points/Uncagaing`` input boxes *cannot* be toggled (strangely)
- The first option in ``Uncaging`` settings stating ``Uncaging Galvos Present / Simultaneous Uncaging`` *is* checked

Uncaging Galvo Calibration
--------------------------

Within the Prairie View software, there is a trick related to calibrating uncaged galvos. Note again that this scope
does not have this ability and we do this purely to enable whole-field LED stimulation through Voltage Outputs.

These settings can be found by going to the ``Tools`` tab and selecting the ``Calibration/Alignment`` option.

(insert uncaging selection here)

(insert gif of uncaging selection here)

Given that this is all trickery, it doesn't matter which of the calibration modes we select. You can choose the
``Burn Spots`` option. Don't worry, you won't be actually burning anything.

When you click the ``Next`` button, you can simply continue clicking ``Next`` until you are met with the ``Finish``
button. Now that things are "calibrated", performing whole-field LED stimulations is possible. Documentation setting
up Voltage Output settings to use this feature is forthcoming.


Miscellaneous Settings
----------------------

There's a tab in the Configuration App called Miscellaneous that contains various different configuration values.

(insert full image here)

During a recent visit from Bruker's technical team, they changed one setting related to the microscope base field.

(insert focused image here)

It was not noted what the setting was when they checked this, but the ``Select the type of microscope base`` now
states ``Bruker Ultima Investigator (Moving)``.

**************************
Prairie View Scan Settings
**************************

There are several Scan Settings that can be configured within the Prairie View software related to how the system
acquires images.

These settings can be found by going to the ``Tools`` tab and selecting the ``Scan Settings`` option.

(insert selection here)

(insert image of tab here)

You'll notice that when this window first opens, all the selections are greyed out and inaccessible to change.
This is because these are sensitive settings for running the microscope without damaging the hardware that most
users do not need to access. However, in our case as users of a legacy system, we need to ensure the software is
using specific settings.

First, it is vital to note that this window updates according to which type of scanning is being performed. The
window itself does *NOT* tell you which settings are being observed/updated. You must use the ``Acquisition Mode``
window for knowing which settings you are observing.

To access these parameters, double *right-click* your mouse on the tab. The settings will all become accessible.

There is a Legacy default for all the parameters that must be selected: ``Ultima Investigator (Divide/5)``.

This setting relates to timing how the galvos in move while scanning your field of view. If the setting is incorrect,
the images you collect will be strangely stretched!

(insert gif here)

Galvo-Galvo Mode
----------------

(insert image of acquisition mode for Galvo-Galvo here)

The Galvo-Galvo mode of image acquisition has parameters that look like this:

(insert image of galvo-galvo general here)

Note that in this mode, the Voltage Divider Values for the X and Y axes are the
same. If these are different values, you will notice that your images are stretched apart in
odd ways!




*********************************
Prairie View Maintenance Settings
*********************************

This tab can be found by 
