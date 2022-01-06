#!/usr/bin/env python3
from time import sleep
from argparse import ArgumentParser

from temscript import Microscope, NullMicroscope, RemoteMicroscope


parser = ArgumentParser()
parser.add_argument("--null", action='store_true', default=False, help="Use NullMicroscope")
parser.add_argument("--remote", type=str, default='', help="Use RemoteMicroscope with given hostname:port")
parser.add_argument("--stage", action='store_true', default=False, help="Test stage movement (defaults to false)")
parser.add_argument("--ccd", action='store_true', default=False, help="Test CCD acquisition (defaults to false)")
parser.add_argument("--all", action='store_true', default=False, help="Perform all optional tests (defaults to false)")
parser.add_argument("--noshow", action='store_true', default=False, help="Don't show anything on UI (only stdout)")
args = parser.parse_args()

if args.null:
    print("Starting test of NullMicroscope()")
    microscope = NullMicroscope()
elif args.remote:
    address = args.remote.split(":", 2)
    if len(address) > 1:
        address = (address[0], int(address[1]))
    else:
        address = (address[0], 8080)
    print("Starting test of RemoteMicroscope(%s:%d)" % address)
    microscope = RemoteMicroscope(address)
else:
    print("Starting test of local Microscope()")
    microscope = Microscope()

print("Microscope.get_family():", microscope.get_family())
print("Microscope.get_microscope_id():", microscope.get_microscope_id())
print("Microscope.get_version():", microscope.get_version())
print("Microscope.get_voltage():", microscope.get_voltage())
print("Microscope.get_vacuum():", microscope.get_vacuum())
print("Microscope.get_stage_holder():", microscope.get_stage_holder())
print("Microscope.get_stage_status():", microscope.get_stage_status())
print("Microscope.get_stage_limits():", microscope.get_stage_limits())
print("Microscope.get_stage_position():", microscope.get_stage_position())

cameras = microscope.get_cameras()
print("Microscope.get_cameras():", cameras)
for name in cameras.keys():
    print("Microscope.get_camera_param(%s):" % name, microscope.get_camera_param(name))
detectors = microscope.get_stem_detectors()
print("Microscope.get_stem_detectors():", detectors)
for name in detectors.keys():
    print("Microscope.get_stem_detector_param(%s):" % name, microscope.get_stem_detector_param(name))

# TODO: fails if not STEM
# print("Microscope.get_stem_acquisition_param():", microscope.get_stem_acquisition_param())

# Test invalid camera
try:
    microscope.get_camera_param('ThereIsNoCameraWithThisName')
except KeyError:
    print("Microscope.get_camera_param() fails with KeyError: YES")
else:
    print("Microscope.get_camera_param() fails with KeyError: NO")

print("Microscope.get_image_shift():", microscope.get_image_shift())
print("Microscope.get_beam_shift():", microscope.get_beam_shift())
print("Microscope.get_beam_tilt():", microscope.get_beam_tilt())
print("Microscope.get_projection_sub_mode():", microscope.get_projection_sub_mode())
print("Microscope.get_projection_mode():", microscope.get_projection_mode())
print("Microscope.get_projection_mode_string():", microscope.get_projection_mode_string())
print("Microscope.get_magnification_index():", microscope.get_magnification_index())
print("Microscope.get_indicated_camera_length():", microscope.get_indicated_camera_length())
print("Microscope.get_indicated_magnification():", microscope.get_indicated_magnification())
print("Microscope.get_defocus():", microscope.get_defocus())
print("Microscope.get_objective_excitation():", microscope.get_objective_excitation())
print("Microscope.get_intensity():", microscope.get_intensity())
print("Microscope.get_objective_stigmator():", microscope.get_objective_stigmator())
print("Microscope.get_condenser_stigmator():", microscope.get_condenser_stigmator())
print("Microscope.get_diffraction_shift():", microscope.get_diffraction_shift())
print("Microscope.get_intensity():", microscope.get_intensity())
print("Microscope.get_screen_current():", microscope.get_screen_current())
print("Microscope.get_screen_position():", microscope.get_screen_position())
print("Microscope.get_illumination_mode():", microscope.get_illumination_mode())
print("Microscope.get_spot_size_index():", microscope.get_spot_size_index())
print("Microscope.get_dark_field_mode():", microscope.get_dark_field_mode())
print("Microscope.get_beam_blanked():", microscope.get_beam_blanked())
print("Microscope.is_stem_available():", microscope.is_stem_available())
print("Microscope.get_instrument_mode():", microscope.get_instrument_mode())

print("Microscope.get_condenser_mode():", microscope.get_condenser_mode())
print("Microscope.get_convergence_angle():", microscope.get_convergence_angle())
print("Microscope.get_probe_defocus():", microscope.get_probe_defocus())
print("Microscope.get_illuminated_area():", microscope.get_illuminated_area())

# TODO: fails if not STEM
# print("Microscope.get_stem_magnification():", microscope.get_stem_magnification())
# print("Microscope.get_stem_rotation():", microscope.get_stem_rotation())

print("Microscope.get_state():", microscope.get_state())

if args.stage or args.all:
    print("Testing stage movement:")

    pos = microscope.get_stage_position()
    new_x = 10e-6 if pos['x'] < 0 else -10e-6
    microscope.set_stage_position(x=new_x)
    for n in range(5):
        print("\tstatus=%s, position=%s" % (microscope.get_stage_status(), microscope.get_stage_position()))
        sleep(0.1)

    pos = microscope.get_stage_position()
    new_y = 10e-6 if pos['y'] < 0 else -10e-6
    new_x = 10e-6 if pos['x'] < 0 else -10e-6
    microscope.set_stage_position({'y': new_y}, x=new_x)
    for n in range(5):
        print("\tstatus=%s, position=%s" % (microscope.get_stage_status(), microscope.get_stage_position()))
        sleep(0.1)

    pos = microscope.get_stage_position()
    new_y = 10e-6 if pos['y'] < 0 else -10e-6
    microscope.set_stage_position(y=new_y, speed=0.5)
    for n in range(5):
        print("\tstatus=%s, position=%s" % (microscope.get_stage_status(), microscope.get_stage_position()))
        sleep(0.1)

if cameras and (args.ccd or args.all):
    ccd = list(cameras.keys())[0]
    print("Testing camera '%s'" % ccd)

    param = microscope.get_camera_param(ccd)
    print("\tinitial camera_param(%s):" % ccd, param)
    exposure = 1.0 if param["exposure(s)"] != 1.0 else 2.0
    microscope.set_camera_param(ccd, {"exposure(s)": exposure})
    param = microscope.get_camera_param(ccd)
    print("\tupdated camera_param(%s):" % ccd, param)

    print("\tacquiring image...")
    images = microscope.acquire(ccd)

    print("\t\tshape:", images[ccd].shape)
    print("\t\tdtype:", images[ccd].dtype)

    if not args.noshow:
        import matplotlib.pyplot as plt
        plt.imshow(images[ccd], cmap="gray")
        plt.show()
