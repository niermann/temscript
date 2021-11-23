from temscript import Microscope, NullMicroscope


if __name__ == '__main__':
    # for testing on the Titan microscope PC
    print("Starting Test...")

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
    print("Microscope.get_stem_acquisition_param():", microscope.get_stem_acquisition_param())

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

    print("Microscope.get_state():", microscope.get_state())
