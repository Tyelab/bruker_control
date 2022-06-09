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

Here's an example of incorrect settings:

(insert image of flawed galvo-galvo settings)

Here is an example of what a stretched image looks like:

(insert image of stretched pollen grains look like here)

An additional setting should be checked to ensure that the galvos are scanning in the correct directions. The
relevant setting is called the ``X Scan Amplitude``. The default setting parameter is correct in it's magnitude
however its direction is incorrect. If this setting isn't corrected, you will see the positions of objects in the
field of view switch sides when going between Galvo-Galvo and Resonant Galvo.

Here's an example of what that behavior looks like:

(insert gif/video of what this behavior looks like)


Resonant Galvo Mode
-------------------

(insert image of acquisition mode for Resonant Galvo here)

The Resonant Galvo mode of image acquisition has parameters that look like this:

(insert image of resonant galvo general here)

The slow axis during scanning is in the Y axis whereas the fast axis for scanning is the X axis. These speeds
are reflected in the ``X Voltage Divider Value`` and ``X Acceleration`` parameters.

There's an additional setting that needs mentioning here related to the PMT pre-amplifier offset. The particulars
of what this offset actually does are still unknown and need specific clarification from Bruker's technical team.
If these settings are not correct, your imaging session will suffer from artifacts that are generated by
electrical noise from the pre-amplifier. This, in combination with `PMT "ripple noise" <https://docs.scanimage.org/Solutions/PMT%2Bnoise.html>`_,
unequal sampling of the FOV by the DAQ due to nonlinear speads of the resonant galvo, and detector shot noise can
cumulatively add significant amounts of noise to your recordings. For a discussion of these artifacts as well as
attempts to compensate for them, see `this Image.sc forum post <https://forum.image.sc/t/efficient-artifact-subtraction-of-electrical-and-resonant-scanning-artifacts-using-python-and-zarr-matlab/62939>`_.

Thus far, it has been found that `removing the artifacts <https://forum.image.sc/t/image-subtraction-in-python-behaves-differently-than-imagej/67942/5>`_
through the subtraction of an average dark image is insufficient to help with motion correction of an average signal
to noise recording. It has yet to be tested on a low signal to noise recording.

The relevant settings for these artifacts can be found in the ``DAQs / Preamplifier`` tab. The settings shown next
are problematic ones:

(insert image of this tab here)

Preamplifier Artifacts
^^^^^^^^^^^^^^^^^^^^^^

In order to illustrate these problems best, be sure to use the ``Range Check`` color table in the Image window.

(insert gif here of the range check color values)

You'll notice that when the ``Range Check`` setting is selected in the gif above that the entirety of the image
turns blue. In this color mapping, pixel values of 0 are blue while pixel values at the max of the applied
Look Up Table (or LUT) are red. The full range of values possible in this system are 0 through 65535 (the
max value of an unsigned 16bit integer which the scope samples at). In this above example, the PMTs and lasers
were off so there was no possible signal for the DAQ to sample from. However, when the preamplifiers are on,
there is still some small amount of electrical noise present.

Here's an example of this setting while collecting a Dark Image, or an image where the PMTs are on but there is no
or minimal light in the room.

(insert gif of preamp noise here)

You can see vertical striping patterns present here. Here is what an average of a dark image looks like:

(insert average dark image here)

When you take an example recording with some pollen grains, you can see the lines present especially if the PMT
voltage is turned up high.

(take recording of pollen grain with pre-amp noise here)

When you take an average of these images, you can typically see these lines present especially in low SNR
imaging regimes.

(insert average pollen grain image here w/lines)

The way this artifact is mitigated is by changing the offset for the PMT that's being imaged. Bruker's
technical team discovered that putting the value to -0.03 creates a much more uniform noise.

Here is an example of doing this while collecting a dark image:

(insert gif of changing settings while doing dark image)

You can see that the noise is much more uniform across the entire FOV and is not suffering from the
vertical striping pattern any longer.

This is further exemplified by the average dark image collected with this offset:

(insert average image with corrected offset here)

Finally, when imaging an example pollen grain, you can see that the veritcal striping is no longer
very prominent and the background noise is far less than before. A consequence of lowering this
offset value is that the true signal we're interested in will also be somewhat dimmer.  However,
given that the structures we're imaging have quite bright fluorescence, a small decrease in the
signal of a cell is well worth the dramatic reduction in noise.

(insert average image here with corrected offset)

*********************************
Prairie View Maintenance Settings
*********************************

This tab can be found by 
