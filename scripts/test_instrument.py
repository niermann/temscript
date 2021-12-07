#!/usr/bin/env python3
from temscript import GetInstrument


def test_projection(instrument):
    print("Testing projection...")
    projection = instrument.Projection
    print("Projection.Mode:", projection.Mode)
    print("Projection.Focus:", projection.Focus)
    print("Projection.Magnification:", projection.Magnification)
    print("Projection.MagnificationIndex:", projection.MagnificationIndex)
    print("Projection.CameraLengthIndex:", projection.CameraLengthIndex)
    print("Projection.ImageShift:", projection.ImageShift)
    print("Projection.ImageBeamShift:", projection.ImageBeamShift)
    print("Projection.DiffractionShift:", projection.DiffractionShift)
    print("Projection.DiffractionStigmator:", projection.DiffractionStigmator)
    print("Projection.ObjectiveStigmator:", projection.ObjectiveStigmator)
    print("Projection.SubModeString:", projection.SubModeString)
    print("Projection.SubMode:", projection.SubMode)
    print("Projection.SubModeMinIndex:", projection.SubModeMinIndex)
    print("Projection.SubModeMaxIndex:", projection.SubModeMaxIndex)
    print("Projection.ObjectiveExcitation:", projection.ObjectiveExcitation)
    print("Projection.ProjectionIndex:", projection.ProjectionIndex)
    print("Projection.LensProgram:", projection.LensProgram)
    print("Projection.ImageRotation:", projection.ImageRotation)
    print("Projection.DetectorShift:", projection.DetectorShift)
    print("Projection.DetectorShiftMode:", projection.DetectorShiftMode)
    print("Projection.ImageBeamTilt:", projection.ImageBeamTilt)
    print()


def test_acquisition(instrument, do_acquisition=False):
    camera_name = None

    print("Testing acquisition...")
    acquisition = instrument.Acquisition
    cameras = acquisition.Cameras
    for n, camera in enumerate(cameras):
        print("Acquisition.Camera[%d]:" % n)
        info = camera.Info
        if not camera_name:
            camera_name = info.Name
        print("\tInfo.Name:", info.Name)
        print("\tInfo.Width:", info.Width)
        print("\tInfo.Height:", info.Height)
        print("\tInfo.PixelSize:", info.PixelSize)
        print("\tInfo.ShutterMode:", info.ShutterMode)
        print("\tInfo.ShutterModes:", info.ShutterModes)
        print("\tInfo.Binnings:", info.Binnings)
        params = camera.AcqParams
        print("\tAcqParams.ImageSize:", params.ImageSize)
        print("\tAcqParams.ExposureTime:", params.ExposureTime)
        print("\tAcqParams.Binning:", params.Binning)
        print("\tAcqParams.ImageCorrection:", params.ImageCorrection)
        print("\tAcqParams.ExposureMode:", params.ExposureMode)
        print("\tAcqParams.MinPreExposureTime:", params.MinPreExposureTime)
        print("\tAcqParams.MaxPreExposureTime:", params.MaxPreExposureTime)
        print("\tAcqParams.PreExposureTime:", params.PreExposureTime)
        print("\tAcqParams.MinPreExposurePauseTime:", params.MinPreExposurePauseTime)
        print("\tAcqParams.MaxPreExposurePauseTime:", params.MaxPreExposurePauseTime)
        print("\tAcqParams.PreExposurePauseTime:", params.PreExposurePauseTime)

    detectors = acquisition.Detectors
    for n, det in enumerate(detectors):
        print("Acquisition.Detector[%d]:" % n)
        info = det.Info
        print("\tInfo.Name:", info.Name)
        print("\tInfo.Brightness:", info.Brightness)
        print("\tInfo.Contrast:", info.Contrast)
        print("\tInfo.Binnings:", info.Binnings)

    params = acquisition.StemAcqParams
    print("Acquisition.StemAcqParams.ImageSize:", params.ImageSize)
    #Raises exception?
    #print("Acquisition.StemAcqParams.DwellTime:", params.DwellTime)
    print("Acquisition.StemAcqParams.Binning:", params.Binning)
    print()

    if not do_acquisition or not camera_name:
        return

    print("Testing image acquisition (%s)" % camera_name)
    acquisition.RemoveAllAcqDevices()
    acquisition.AddAcqDeviceByName(camera_name)
    images = acquisition.AcquireImages()
    for n, image in enumerate(images):
        print("Acquisition.AcquireImages()[%d]:" % n)
        print("\tAcqImage.Name:", image.Name)
        print("\tAcqImage.Width:", image.Width)
        print("\tAcqImage.Height:", image.Height)
        print("\tAcqImage.Depth:", image.Depth)
        array = image.Array
        print("\tAcqImage.Array.dtype:", array.dtype)
        print("\tAcqImage.Array.shape:", array.shape)
    print()


def test_vacuum(instrument):
    print("Testing vacuum...")
    vacuum = instrument.Vacuum
    print("Vacuum.Status:", vacuum.Status)
    print("Vacuum.PVPRunning:", vacuum.PVPRunning)
    print("Vacuum.ColumnValvesOpen:", vacuum.ColumnValvesOpen)
    for n, gauge in enumerate(vacuum.Gauges):
        print("Vacuum.Gauges[%d]:" % n)
        gauge.Read()
        print("\tGauge.Name:", gauge.Name)
        print("\tGauge.Pressure:", gauge.Pressure)
        print("\tGauge.Status:", gauge.Status)
        print("\tGauge.PressureLevel:", gauge.PressureLevel)
    print()


def test_stage(instrument, do_move=False):
    print("Testing stage...")
    stage = instrument.Stage
    pos = stage.Position
    print("Stage.Status:", stage.Status)
    print("Stage.Position:", pos)
    print("Stage.Holder:", stage.Holder)
    for axis in 'xyzab':
        print("Stage.AxisData(%s):" % axis, stage.AxisData(axis))
    print()

    if not do_move:
        return

    print("Testing movement")
    print("\tStage.Goto(x=1e-6, y=-1e-6)")
    stage.GoTo(x=1e-6, y=-1e-6)
    print("\tStage.Position:", stage.Position)
    print("\tStage.Goto(x=-1e-6, speed=0.5)")
    stage.GoTo(x=-1e-6, speed=0.5)
    print("\tStage.Position:", stage.Position)
    print("\tStage.MoveTo() to original position")
    stage.MoveTo(**pos)
    print("\tStage.Position:", stage.Position)
    print()


def test_camera(instrument):
    print("Testing camera...")
    camera = instrument.Camera
    print("Camera.Stock:", camera.Stock)
    print("Camera.MainScreen:", camera.MainScreen)
    print("Camera.IsSmallScreenDown:", camera.IsSmallScreenDown)
    print("Camera.MeasuredExposureTime:", camera.MeasuredExposureTime)
    print("Camera.FilmText:", repr(camera.FilmText))
    print("Camera.ManualExposureTime:", camera.ManualExposureTime)
    print("Camera.PlateuMarker:", camera.PlateuMarker)
    print("Camera.ExposureNumber:", camera.ExposureNumber)
    print("Camera.Usercode:", repr(camera.Usercode))
    print("Camera.ManualExposure:", camera.ManualExposure)
    print("Camera.PlateLabelDataType:", camera.PlateLabelDataType)
    print("Camera.ScreenDim:", camera.ScreenDim)
    print("Camera.ScreenDimText:", repr(camera.ScreenDimText))
    print("Camera.ScreenCurrent:", camera.ScreenCurrent)
    print()


def test_illumination(instrument):
    print("Testing illumination...")
    illum = instrument.Illumination
    print("Illumination.Mode:", illum.Mode)
    print("Illumination.SpotsizeIndex:", illum.SpotsizeIndex)
    print("Illumination.Intensity:", illum.Intensity)
    print("Illumination.IntensityZoomEnabled:", illum.IntensityZoomEnabled)
    #Critical error?
    #print("Illumination.IntensityLimitEnabled:", illum.IntensityLimitEnabled)
    print("Illumination.Shift:", illum.Shift)
    print("Illumination.Tilt:", illum.Tilt)
    print("Illumination.RotationCenter:", illum.RotationCenter)
    print("Illumination.CondenserStigmator:", illum.CondenserStigmator)
    print("Illumination.DFMode:", illum.DFMode)
    print("Illumination.CondenserMode:", illum.CondenserMode)
    print("Illumination.IlluminatedArea:", illum.IlluminatedArea)
    print("Illumination.ProbeDefocus:", illum.ProbeDefocus)
    print("Illumination.ConvergenceAngle:", illum.ConvergenceAngle)
    # Only in STEM mode?
    #print("Illumination.StemMagnification:", illum.StemMagnification)
    #print("Illumination.StemRotation:", illum.StemRotation)
    print()


def test_gun(instrument):
    print("Testing gun...")
    gun = instrument.Gun
    print("Gun.HTState:", gun.HTState)
    print("Gun.HTValue:", gun.HTValue)
    print("Gun.HTMaxValue:", gun.HTMaxValue)
    print("Gun.Shift:", gun.Shift)
    print("Gun.Tilt:", gun.Tilt)
    print()


def test_blankershutter(instrument):
    print("Testing blanker/shutter...")
    bs = instrument.BlankerShutter
    print("BlankerShutter.ShutterOverrideOn:", bs.ShutterOverrideOn)
    print()


def test_instrument_mode_control(instrument):
    print("Testing instrument mode control...")
    ctrl = instrument.InstrumentModeControl
    print("InstrumentModeControl.StemAvailable:", ctrl.StemAvailable)
    print("InstrumentModeControl.InstrumentMode:", ctrl.InstrumentMode)
    print()


def test_configuration(instrument):
    print("Testing configuration...")
    config = instrument.Configuration
    print("Configuration.ProductFamily:", config.ProductFamily)
    print()


if __name__ == '__main__':
    # for testing on the Titan microscope PC
    print("Starting Test...")

    full_test = False
    instrument = GetInstrument()
    test_projection(instrument)
    test_acquisition(instrument, do_acquisition=full_test)
    test_vacuum(instrument)
    test_stage(instrument, do_move=full_test)
    test_camera(instrument)
    test_illumination(instrument)
    test_gun(instrument)
    test_blankershutter(instrument)
    test_instrument_mode_control(instrument)
    test_configuration(instrument)

