#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt

from temscript import Microscope, NullMicroscope


if __name__ == '__main__':
    # for testing on the Titan microscope PC
    print("Starting Test...")

    microscope = Microscope()
    cameras = microscope.get_cameras()

    for name in cameras.keys():
        print("Testing %s:" % name)
        init_param = microscope.get_camera_param(name)
        print("\tInitial param:", init_param)

        param = dict(init_param)
        param["image_size"] = "FULL"
        param["exposure(s)"] = 1.0
        param["binning"] = 1
        microscope.set_camera_param(name, param)
        print()
        print("\tFull param:", microscope.get_camera_param(name))

        acq = microscope.acquire(name)
        image = acq[name]
        print("\tSize: ", image.shape[1], "x", image.shape[0])
        print("\tMean: ", np.mean(image))
        print("\tStdDev: ", np.std(image))
        vmin = np.percentile(image, 3)
        vmax = np.percentile(image, 97)
        plt.subplot(141)
        plt.imshow(image, interpolation="nearest", cmap="gray", vmin=vmin, vmax=vmax)
        plt.title("Full")
        plt.colorbar()

        param = dict(init_param)
        param["image_size"] = "HALF"
        param["exposure(s)"] = 1.0
        param["binning"] = 1
        microscope.set_camera_param(name, param)
        print()
        print("\tHalf param:", microscope.get_camera_param(name))

        acq = microscope.acquire(name)
        image = acq[name]
        print("\tSize: ", image.shape[1], "x", image.shape[0])
        print("\tMean: ", np.mean(image))
        print("\tStdDev: ", np.std(image))
        vmin = np.percentile(image, 3)
        vmax = np.percentile(image, 97)
        plt.subplot(142)
        plt.imshow(image, interpolation="nearest", cmap="gray", vmin=vmin, vmax=vmax)
        plt.title("Half")
        plt.colorbar()

        param = dict(init_param)
        param["image_size"] = "FULL"
        param["exposure(s)"] = 1.0
        param["binning"] = 2
        microscope.set_camera_param(name, param)
        print()
        print("\tBinned param:", microscope.get_camera_param(name))

        acq = microscope.acquire(name)
        image = acq[name]
        print("\tSize: ", image.shape[1], "x", image.shape[0])
        print("\tMean: ", np.mean(image))
        print("\tStdDev: ", np.std(image))
        vmin = np.percentile(image, 3)
        vmax = np.percentile(image, 97)
        plt.subplot(143)
        plt.imshow(image, interpolation="nearest", cmap="gray", vmin=vmin, vmax=vmax)
        plt.title("Binned")
        plt.colorbar()

        param = dict(init_param)
        param["image_size"] = "FULL"
        param["exposure(s)"] = 2.0
        param["binning"] = 1
        microscope.set_camera_param(name, param)
        print()
        print("\tLong exposure param:", microscope.get_camera_param(name))

        acq = microscope.acquire(name)
        image = acq[name]
        print("\tSize: ", image.shape[1], "x", image.shape[0])
        print("\tMean: ", np.mean(image))
        vmin = np.percentile(image, 3)
        vmax = np.percentile(image, 97)
        print("\tStdDev: ", np.std(image))
        plt.subplot(144)
        plt.imshow(image, interpolation="nearest", cmap="gray", vmin=vmin, vmax=vmax)
        print("\tStdDev: ", np.std(image))
        plt.title("Long Exp.")
        plt.colorbar()

        print()
        plt.suptitle(name)
        plt.show()
