# -*- coding: utf-8 -*-
"""
Created on Monday Oct 23rd 2023
fMO.openFile(self)
fMO.openSeg(self)
fMO.openFolder(self)
fMO.LoadWorkspace(self)
fMO.LoadWorkspaceFolder(self)
fMO.ChangeChannelSetup(self)
fMO.cropFile(self)
fMO.ResetCurrent(self)
fMO.RemoveCurrent(self)
fMO.Reset(self)
"""

import tkinter
import os
from tkinter import ttk as ttkinter

# import tkinter.messagebox
import tkinter.filedialog
import skimage.io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.backends.backend_tkagg as Tk_Agg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NT2Tk
import skimage.measure
from math import log
import pickle

if __package__ == "tmeanalyzer":
    from .imageMenu import DestroyTK, popupmsg
else:
    from imageMenu import DestroyTK, popupmsg


def openFile(self):
    ftypes = [("Tiff images", ".tif .tiff")]
    filenames = tkinter.filedialog.askopenfilenames(
        parent=self.master, filetypes=ftypes
    )
    [popup_int, label_int] = popupmsg("...", False)
    for n_im, filename in enumerate(filenames):
        label_int["text"] = (
            "Loading image "
            + str(n_im + 1)
            + " of "
            + str(len(filenames))
            + " images.\n Please hold."
        )
        popup_int.update()
        im_raw = np.squeeze(np.float32(np.array(skimage.io.imread(filename))))
        channel_variable = []
        color_variable = []
        self.activeImage = len(self.FileDictionary)
        self.FileDictionary[len(self.FileDictionary)] = filename
        n_channels = min(im_raw.shape)
        Color_pointers = self.Color_info.copy()[0:n_channels]
        Channel_pointers = self.Markers.copy()[0:n_channels]
        if n_channels == im_raw.shape[0]:
            im_raw = im_raw.transpose(1, 2, 0)
        elif n_channels == im_raw.shape[1]:
            im_raw = im_raw.transpose(0, 2, 1)
        for i in range(np.size(Channel_pointers), n_channels):
            Channel_pointers.append("garbage")
        for i in range(np.size(Color_pointers), n_channels):
            Color_pointers.append("black")
        for i in range(n_channels):
            channel_variable.append([])
            color_variable.append([])
        self.activeImagePointer = []
        self.Channel_pointers.append(Channel_pointers)
        self.Color_pointers.append(Color_pointers)
        self.channel_variable.append(channel_variable)
        self.color_variable.append(color_variable)
        self.im_raw.append(im_raw)
        self.n_channels.append(n_channels)
        self.im_analyzed.append([])
        self.analyze_index.append([])
        self.foreground_threshold.append([])
        self.analysis_params.append(self.default_analysis_params)
        self.Cell_props.append([])
        self.Tissue_props.append({})
        self.small_images.append([])
    DestroyTK(popup_int)
    self.remake_side_window()


def openSeg(self):
    ftypes = [("Tiff images", ".tif .tiff")]
    filename = tkinter.filedialog.askopenfilename(parent=self.master, filetypes=ftypes)
    if True:
        analysis_params = self.analysis_params[self.active_image].copy()
        analysis_params.pop("Foreground")
        analysis_params["Foreground"] = {"thres": []}
        im_raw = np.squeeze(np.float32(np.array(skimage.io.imread(filename))))
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        if np.size(im_raw.shape) > 2:
            n_channels = min(im_raw.shape)
            if n_channels == im_raw.shape[0]:
                im_raw = im_raw.transpose(1, 2, 0)
            elif n_channels == im_raw.shape[1]:
                im_raw = im_raw.transpose(0, 2, 1)
            Fore_mask = im_raw[:, :, 0] < 2
            Tumor_mask = im_raw[:, :, 0] == 0
            Stroma_mask = im_raw[:, :, 0] == 1
        else:
            Fore_mask = im_raw < 2
            Tumor_mask = im_raw == 0
            Stroma_mask = im_raw == 1
        if "Foreground" in analyze_index:
            im_analyzed[analyze_index.index("Foreground")] = Fore_mask
        else:
            im_analyzed.append(Fore_mask)
            analyze_index.append("Foreground")
        if "Tumor" in analyze_index:
            im_analyzed[analyze_index.index("Tumor")] = Tumor_mask
        else:
            im_analyzed.append(Tumor_mask)
            analyze_index.append("Tumor")
        if "Stroma" in analyze_index:
            im_analyzed[analyze_index.index("Stroma")] = Stroma_mask
        else:
            im_analyzed.append(Stroma_mask)
            analyze_index.append("Stroma")
        if np.size(im_raw.shape) > 2:
            if "DAPI" in analysis_params["Segments"]:
                analysis_params["Segments"].pop("DAPI")
            analysis_params["Segments"]["DAPI"] = {"thres": []}
            self.single_cells = skimage.measure.label(im_raw[:, :, 1].astype("int32"))
            self.voronoi_image = skimage.measure.label(
                im_raw[:, :, 1].astype("int32") + im_raw[:, :, 2].astype("int32")
            )
            im_analyzed.append(im_raw[:, :, 1] > 0)
            analyze_index.append("DAPI")
            im_analyzed.append(self.single_cells)
            analyze_index.append("Nuclei")
            im_analyzed.append(self.voronoi_image)
            analyze_index.append("Cells")
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            self.Get_cell_props()
        else:
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
        self.analysis_params[self.active_image] = analysis_params
        self.remake_side_window()


def openFolder(self):
    def Folder_stitch_selected(verts, *a):
        ROI_path = matplotlib.path.Path(verts)
        points = np.transpose((self.xy_locs[:, 0].ravel(), self.xy_locs[:, 1].ravel()))
        mask = ROI_path.contains_points(points)
        mask = ~mask
        mask = np.nonzero(mask)[0]
        file_list = self.file_list
        filedir = self.filedir
        file_list_temp = self.file_list_temp
        for i in mask:
            file_list.pop(file_list.index(file_list_temp[i]))
        DestroyTK(self.popup)
        openFolder_real(filedir, file_list)
        openFolder_sub(1)

    def openFolder_sub(redo=0, *a):
        if redo == 0:
            ftypes = [("Tiff images", ".tif .tiff")]
            filename = tkinter.filedialog.askopenfilename(
                parent=self.master, filetypes=ftypes
            )
            filedir = filename[: -1 * filename[::-1].find("/")]
            file_list = os.listdir(filedir)
            self.filedir = filedir
        else:
            filedir = self.filedir
            file_list = os.listdir(filedir)
        self.file_list = file_list
        if self.combine_large == "PreDetermined stitch":
            filenames = []
            for i, filename in enumerate(file_list):
                if filename.find("_component_data.tif") >= 0:
                    filenames.append(filename)
            filenames_orig = filenames
            images_to_combine = []
            filenames = []
            master_file_list = []
            for i in range(len(filenames_orig)):
                filename = filenames_orig[i]
                filename = filename[: -1 * filename[::-1].find("[") - 1]
                filenames.append(filename)
                if filename != "":
                    if filenames[i] in master_file_list:
                        images_to_combine[master_file_list.index(filenames[i])].append(
                            filenames_orig[i]
                        )
                    else:
                        master_file_list.append(filenames[i])
                        images_to_combine.append([])
                        images_to_combine[master_file_list.index(filenames[i])].append(
                            filenames_orig[i]
                        )
            for i, file_list in enumerate(images_to_combine):
                if np.size(file_list) > 1:
                    xy_locs = []
                    for i, sub in enumerate(file_list):
                        xy_locs.append(
                            [
                                int(
                                    sub[
                                        sub.find("[") + 1 : sub.find(",", sub.find("["))
                                    ]
                                ),
                                int(
                                    sub[
                                        sub.find(",", sub.find("[")) + 1 : sub.find("]")
                                    ]
                                ),
                            ]
                        )
                    xy_locs = np.array(xy_locs)
                    xy_locs = (xy_locs - xy_locs.min(0)) * self.magnification
            self.xy_locs = xy_locs
            popup = tkinter.Tk()
            popup.wm_title("Stitchin region selection")
            label = ttkinter.Label(
                popup, text="Phenotype selection for file :\n" + master_file_list[-1]
            )
            label.pack(side="bottom", fill="x", pady=10)
            internal_windows = tkinter.Frame(popup, width=440, height=440)
            internal_windows.pack(side=tkinter.LEFT, anchor="w")
            f2 = plt.Figure(figsize=(6, 6), dpi=100)
            f2.patch.set_visible(False)
            f2.subplots_adjust(
                left=0.1, bottom=0.1, right=0.92, top=0.92, wspace=0, hspace=0
            )
            ax2 = f2.gca()
            ax2 = f2.gca()
            image_canvas2 = Tk_Agg.FigureCanvasTkAgg(f2, master=internal_windows)
            image_canvas2.draw()
            image_canvas2.get_tk_widget().pack(
                side=tkinter.TOP, expand=True, anchor="n"
            )
            image_canvas2._tkcanvas.pack(
                side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True
            )
            image_toolbar2 = NT2Tk(image_canvas2, internal_windows)
            image_toolbar2.update()
            ax2.clear()
            ax2.set_position([0.1, 0.1, 0.65, 0.65])
            ax2.scatter(xy_locs[:, 0], xy_locs[:, 1], c="C0")
            ax2.set_xlim((np.min(xy_locs[:, 0]) - 1000, np.max(xy_locs[:, 0]) + 1000))
            ax2.set_ylim((np.min(xy_locs[:, 1]) - 1000, np.max(xy_locs[:, 1]) + 1000))
            self.popup = popup
            ROIPolygon = matplotlib.widgets.PolygonSelector(
                ax2,
                Folder_stitch_selected,
                lineprops=dict(color="r", linestyle="-", linewidth=1, alpha=0.5),
                markerprops=dict(marker="o", markersize=3, mec="r", mfc="r", alpha=0.5),
            )
            ROIPolygon.active = True
            ROIPolygon.visible = True
            self.file_list_temp = file_list
            popup.mainloop()
        else:
            openFolder_real(filedir, file_list)

    def openFolder_real(filedir, file_list, *a):
        combine_large = self.combine_large in [
            "Combine images",
            "Combine and downsample",
        ]
        downsample = self.combine_large in [
            "Stitch and downsample",
            "Combine and downsample",
        ]
        stitch_large = self.combine_large in [
            "Stitch images",
            "Stitch and downsample",
            "PreDetermined stitch",
        ]
        self.loaded_images = []

        for i, filename in enumerate(file_list):
            if filename.find("_component_data.tif") >= 0:
                im_raw = np.squeeze(
                    np.float32(np.array(skimage.io.imread(filedir + filename)))
                )
                channel_variable = []
                color_variable = []
                w = []
                c = []
                self.activeImage = len(self.FileDictionary)
                self.FileDictionary[len(self.FileDictionary)] = filename
                n_channels = min(im_raw.shape)
                Color_pointers = self.Color_info.copy()[0:n_channels]
                Channel_pointers = self.Markers.copy()[0:n_channels]
                if n_channels == im_raw.shape[0]:
                    im_raw = im_raw.transpose(1, 2, 0)
                elif n_channels == im_raw.shape[1]:
                    im_raw = im_raw.transpose(0, 2, 1)
                for i in range(np.size(Channel_pointers), n_channels):
                    Channel_pointers.append("garbage")
                for i in range(np.size(Color_pointers), n_channels):
                    Color_pointers.append("black")
                for i in range(n_channels):
                    channel_variable.append([])
                    color_variable.append([])

                self.loaded_images.append(self.activeImage)
                self.activeImagePointer = []
                self.Channel_pointers.append(Channel_pointers)
                self.Color_pointers.append(Color_pointers)
                self.channel_variable.append(channel_variable)
                self.color_variable.append(color_variable)
                self.im_raw.append(im_raw)
                self.n_channels.append(n_channels)
                self.im_analyzed.append([])
                self.analyze_index.append([])
                self.foreground_threshold.append([])
                self.analysis_params.append(self.default_analysis_params)
                self.Cell_props.append([])
                self.Tissue_props.append({})
                self.small_images.append([])
                filename = (
                    filename[: filename.find("_component_data.tif")]
                    + "_binary_seg_maps.tif"
                )
                if filename in file_list:
                    analysis_params = self.analysis_params[self.activeImage].copy()
                    im_raw = np.squeeze(
                        np.float32(np.array(skimage.io.imread(filedir + filename)))
                    )
                    im_analyzed = self.im_analyzed[self.activeImage]
                    analyze_index = self.analyze_index[self.activeImage]
                    analysis_params.pop("Foreground")
                    analysis_params["Foreground"] = {"thres": []}
                    if np.size(im_raw.shape) > 2:
                        n_channels = min(im_raw.shape)
                        if n_channels == im_raw.shape[0]:
                            im_raw = im_raw.transpose(1, 2, 0)
                        elif n_channels == im_raw.shape[1]:
                            im_raw = im_raw.transpose(0, 2, 1)
                        Fore_mask = im_raw[:, :, 0] < 2
                        Tumor_mask = im_raw[:, :, 0] == 0
                        Stroma_mask = im_raw[:, :, 0] == 1
                    else:
                        Fore_mask = im_raw < 2
                        Tumor_mask = im_raw == 0
                        Stroma_mask = im_raw == 1
                    if "Foreground" in analyze_index:
                        im_analyzed[analyze_index.index("Foreground")] = Fore_mask
                    else:
                        im_analyzed.append(Fore_mask)
                        analyze_index.append("Foreground")
                    if "Tumor" in analyze_index:
                        im_analyzed[analyze_index.index("Tumor")] = Tumor_mask
                    else:
                        im_analyzed.append(Tumor_mask)
                        analyze_index.append("Tumor")
                    if "Stroma" in analyze_index:
                        im_analyzed[analyze_index.index("Stroma")] = Stroma_mask
                    else:
                        im_analyzed.append(Stroma_mask)
                        analyze_index.append("Stroma")
                    if np.size(im_raw.shape) > 2:
                        if "DAPI" in analysis_params["Segments"]:
                            analysis_params["Segments"].pop("DAPI")
                        analysis_params["Segments"]["DAPI"] = {"thres": []}
                        self.single_cells = skimage.measure.label(
                            im_raw[:, :, 1].astype("int32")
                        )
                        self.voronoi_image = skimage.measure.label(
                            im_raw[:, :, 1].astype("int32")
                            + im_raw[:, :, 2].astype("int32")
                        )
                        im_analyzed.append(im_raw[:, :, 1] > 0)
                        analyze_index.append("DAPI")
                        im_analyzed.append(self.single_cells)
                        analyze_index.append("Nuclei")
                        im_analyzed.append(self.voronoi_image)
                        analyze_index.append("Cells")
                        self.im_analyzed[self.activeImage] = im_analyzed
                        self.analyze_index[self.activeImage] = analyze_index
                        self.Get_cell_props()
                    else:
                        self.im_analyzed[self.activeImage] = im_analyzed
                        self.analyze_index[self.activeImage] = analyze_index
                    self.analysis_params[self.activeImage] = analysis_params.copy()
        if (np.size(self.loaded_images) > 1) & combine_large:
            nx_size = np.uint32(np.floor(np.sqrt(np.size(self.loaded_images))))
            ny_size = nx_size
            n_image = 0
            while np.size(self.loaded_images) > (nx_size * ny_size):
                ny_size = ny_size + 1
            im_temp = self.im_raw[self.loaded_images[n_image]]
            i = 2
            while (i < nx_size) & downsample:
                im_temp = (
                    skimage.transform.pyramid_reduce(im_temp / im_temp.max())
                    * im_temp.max()
                )
                i = i * 2
            im_raw_combined = im_temp
            for i in range(1, nx_size):
                n_image = n_image + 1
                if n_image < np.size(self.loaded_images):
                    im_temp = self.im_raw[self.loaded_images[n_image]]
                    i = 2
                    while (i < nx_size) & downsample:
                        im_temp = (
                            skimage.transform.pyramid_reduce(im_temp / im_temp.max())
                            * im_temp.max()
                        )
                        i = i * 2
                else:
                    im_temp = np.zeros_like(im_temp)
                im_raw_combined = np.concatenate((im_raw_combined, im_temp), axis=1)
            for i in range(1, ny_size):
                n_image = n_image + 1
                if n_image < np.size(self.loaded_images):
                    im_temp = self.im_raw[self.loaded_images[n_image]]
                    i = 2
                    while (i < nx_size) & downsample:
                        im_temp = (
                            skimage.transform.pyramid_reduce(im_temp / im_temp.max())
                            * im_temp.max()
                        )
                        i = i * 2
                else:
                    im_temp = np.zeros_like(im_temp)
                im_combined = im_temp
                for i in range(1, nx_size):
                    n_image = n_image + 1
                    if n_image < np.size(self.loaded_images):
                        im_temp = self.im_raw[self.loaded_images[n_image]]
                        i = 2
                        while (i < nx_size) & downsample:
                            im_temp = (
                                skimage.transform.pyramid_reduce(
                                    im_temp / im_temp.max()
                                )
                                * im_temp.max()
                            )
                            i = i * 2
                    else:
                        im_temp = np.zeros_like(im_temp)
                    im_combined = np.concatenate((im_combined, im_temp), axis=1)
                im_raw_combined = np.concatenate((im_raw_combined, im_combined), axis=0)
            pheno_list = []
            for i in self.loaded_images:
                pheno_list = np.unique(
                    np.concatenate((pheno_list, self.analyze_index[i]))
                )
            im_analyzed = []
            analyze_index = []
            for pheno in pheno_list:
                im_analyzed_temp = np.zeros_like(
                    im_raw_combined[:, :, 0], dtype="int64"
                )
                for n_image in self.loaded_images:
                    if pheno in self.analyze_index[n_image]:
                        im_temp2 = self.im_analyzed[n_image][
                            self.analyze_index[n_image].index(pheno)
                        ]
                        i = 2
                        while (i < nx_size) & downsample:
                            im_temp2 = (
                                skimage.transform.pyramid_reduce(
                                    im_temp2 / im_temp2.max()
                                )
                                * im_temp2.max()
                            )
                            i = i * 2
                        n_y = np.uint32(n_image / nx_size)
                        n_x = n_image - nx_size * n_y
                        if pheno in ["Nuclei", "Cells"]:
                            im_temp2[im_temp2 > 0] = np.max(im_analyzed_temp)
                        im_analyzed_temp[
                            n_y * im_temp2.shape[0] : (n_y + 1) * im_temp2.shape[0],
                            n_x * im_temp2.shape[1] : (n_x + 1) * im_temp2.shape[1],
                        ] = im_temp2
                im_analyzed.append(im_analyzed_temp)
                analyze_index.append(pheno)
            im_raw = im_raw_combined
            self.activeImage = len(self.FileDictionary)
            self.FileDictionary[len(self.FileDictionary)] = filedir + "combined"
            DestroyTK(self.rightWindow)
            self.rightWindow = tkinter.Frame(self.rightWindow_master, width=100)
            self.rightWindow.pack(side=tkinter.RIGHT)
            channel_variable = []
            color_variable = []
            w = []
            c = []
            n_channels = min(im_raw.shape)
            Color_pointers = self.Color_info.copy()[0:n_channels]
            Channel_pointers = self.Markers.copy()[0:n_channels]
            # if n_channels == 3:
            #     Color_pointers[0] = 'red'
            #     Color_pointers[1] = 'green'
            #     Color_pointers[2] = 'blue'
            if n_channels == im_raw.shape[0]:
                im_raw = im_raw.transpose(1, 2, 0)
            elif n_channels == im_raw.shape[1]:
                im_raw = im_raw.transpose(0, 2, 1)
            for i in range(np.size(Channel_pointers), n_channels):
                Channel_pointers.append("garbage")
            for i in range(np.size(Color_pointers), n_channels):
                Color_pointers.append("black")
            for i in range(n_channels):
                channel_variable.append([])
                color_variable.append([])
                internal_windows = tkinter.Frame(self.rightWindow, width=100, height=20)
                internal_windows.pack(side=tkinter.TOP)
                channel_variable[i] = tkinter.StringVar(internal_windows)
                channel_variable[i].set(Channel_pointers[i])
                channel_variable[i].trace("w", self.cc_changed)
                w.append(
                    tkinter.OptionMenu(
                        internal_windows, channel_variable[i], *self.Markers
                    )
                )
                w[i].config(width=10)
                w[i].pack(side=tkinter.LEFT)
                color_variable[i] = tkinter.StringVar(internal_windows)
                color_variable[i].set(Color_pointers[i])
                color_variable[i].trace("w", self.cc_changed)
                c.append(
                    tkinter.OptionMenu(
                        internal_windows, color_variable[i], *self.Color_info
                    )
                )
                c[i].config(width=10)
                c[i].pack(side=tkinter.LEFT)
            internal_windows = tkinter.Frame(self.rightWindow, width=100, height=20)
            internal_windows.pack(side=tkinter.TOP)
            im_display_button = tkinter.Button(
                master=internal_windows,
                text="Display",
                command=self.display_composite_image,
            )
            im_display_button.pack(side=tkinter.TOP)
            internal_windows = tkinter.Frame(self.rightWindow, width=100, height=20)
            internal_windows.pack(side=tkinter.TOP)
            active_image = tkinter.StringVar(internal_windows)
            active_image.set(
                "("
                + str(self.activeImage)
                + ", "
                + self.FileDictionary[self.activeImage]
                + ")"
            )
            active_image.trace("w", self.image_changed)
            w = tkinter.OptionMenu(
                internal_windows, active_image, *self.FileDictionary.items()
            )
            w.config(width=10)
            w.pack(side=tkinter.TOP)

            self.activeImagePointer = active_image
            #                self.activeImagePointer = []
            self.Channel_pointers.append(Channel_pointers)
            self.Color_pointers.append(Color_pointers)
            self.channel_variable.append(channel_variable)
            self.color_variable.append(color_variable)
            self.im_raw.append(im_raw)
            self.n_channels.append(n_channels)
            self.im_analyzed.append(im_analyzed)
            self.analyze_index.append(analyze_index)
            self.foreground_threshold.append([])
            self.analysis_params.append(self.default_analysis_params)
            self.Cell_props.append([])
            self.Tissue_props.append({})
            self.small_images.append([])

        if (np.size(self.loaded_images) > 1) & stitch_large:
            images_to_combine = []
            filenames = []
            master_file_list = []
            for i in range(np.size(self.loaded_images)):
                filename = self.FileDictionary[self.loaded_images[i]]
                filename = filename[: -1 * filename[::-1].find("[") - 1]
                filenames.append(filename)
                if filename != "":
                    if filenames[i] in master_file_list:
                        images_to_combine[master_file_list.index(filenames[i])].append(
                            self.loaded_images[i]
                        )
                    else:
                        images_to_combine.append([self.loaded_images[i]])
                        master_file_list.append(filenames[i])
            for i, file_list in enumerate(images_to_combine):
                if np.size(file_list) > 1:
                    xy_locs = []
                    nx_size = np.uint32(np.floor(np.sqrt(np.size(file_list))))
                    i = 2
                    n_downsample = 1
                    while (i < nx_size) & downsample:
                        i = i * 2
                        n_downsample = n_downsample / 2
                    for i, file_number in enumerate(file_list):
                        sub = self.FileDictionary[file_number]
                        xy_locs.append(
                            [
                                int(
                                    sub[
                                        sub.find("[") + 1 : sub.find(",", sub.find("["))
                                    ]
                                ),
                                int(
                                    sub[
                                        sub.find(",", sub.find("[")) + 1 : sub.find("]")
                                    ]
                                ),
                            ]
                        )
                    xy_locs = np.array(xy_locs)
                    xy_locs = (xy_locs - xy_locs.min(0)) * self.magnification
                    im_temp = np.float32(np.array(self.im_raw[file_number]))
                    im_temp = im_temp.transpose(
                        np.argsort(im_temp.shape)[2],
                        np.argsort(im_temp.shape)[1],
                        np.argsort(im_temp.shape)[0],
                    )
                    im_raw = np.zeros(
                        [
                            np.uint32(
                                n_downsample
                                * (100 + im_temp.shape[0] + xy_locs.max(0)[0])
                            ),
                            np.uint32(
                                n_downsample
                                * (100 + im_temp.shape[1] + xy_locs.max(0)[1])
                            ),
                            im_temp.shape[2],
                        ],
                        "float32",
                    )

                    for i, file_number in enumerate(file_list):
                        im_temp = np.float32(np.array(self.im_raw[file_number]))
                        im_temp = im_temp.transpose(
                            np.argsort(im_temp.shape)[2],
                            np.argsort(im_temp.shape)[1],
                            np.argsort(im_temp.shape)[0],
                        )
                        j = 2
                        while (j < nx_size) & downsample:
                            j = j * 2
                            im_temp = (
                                skimage.transform.pyramid_reduce(
                                    im_temp / im_temp.max()
                                )
                                * im_temp.max()
                            )
                        im_raw[
                            np.uint32(n_downsample * xy_locs[i, 0]) : np.uint32(
                                n_downsample * xy_locs[i, 0]
                            )
                            + im_temp.shape[0],
                            np.uint32(n_downsample * xy_locs[i, 1]) : np.uint32(
                                n_downsample * xy_locs[i, 1]
                            )
                            + im_temp.shape[1],
                            :,
                        ] = im_temp
                    im_raw = im_raw.transpose(
                        np.argsort(im_raw.shape)[2],
                        np.argsort(im_raw.shape)[1],
                        np.argsort(im_raw.shape)[0],
                    )

                    self.activeImage = len(self.FileDictionary)
                    self.FileDictionary[len(self.FileDictionary)] = (
                        sub[: -1 * sub[::-1].find("[") - 1] + "stitched"
                    )
                    DestroyTK(self.rightWindow)
                    self.rightWindow = tkinter.Frame(self.rightWindow_master, width=100)
                    self.rightWindow.pack(side=tkinter.RIGHT)
                    channel_variable = []
                    color_variable = []
                    w = []
                    c = []
                    n_channels = min(im_raw.shape)
                    Color_pointers = self.Color_info.copy()[0:n_channels]
                    Channel_pointers = self.Markers.copy()[0:n_channels]
                    if n_channels == im_raw.shape[0]:
                        im_raw = im_raw.transpose(1, 2, 0)
                    elif n_channels == im_raw.shape[1]:
                        im_raw = im_raw.transpose(0, 2, 1)
                    for i in range(np.size(Channel_pointers), n_channels):
                        Channel_pointers.append("garbage")
                    for i in range(np.size(Color_pointers), n_channels):
                        Color_pointers.append("black")
                    for i in range(n_channels):
                        internal_windows = tkinter.Frame(
                            self.rightWindow, width=100, height=20
                        )
                        internal_windows.pack(side=tkinter.TOP)
                        channel_variable.append(tkinter.StringVar(internal_windows))
                        channel_variable[i].set(Channel_pointers[i])
                        channel_variable[i].trace("w", self.cc_changed)
                        w.append(
                            tkinter.OptionMenu(
                                internal_windows, channel_variable[i], *self.Markers
                            )
                        )
                        w[i].config(width=10)
                        w[i].pack(side=tkinter.LEFT)
                        color_variable.append(tkinter.StringVar(internal_windows))
                        color_variable[i].set(Color_pointers[i])
                        color_variable[i].trace("w", self.cc_changed)
                        c.append(
                            tkinter.OptionMenu(
                                internal_windows, color_variable[i], *self.Color_info
                            )
                        )
                        c[i].config(width=10)
                        c[i].pack(side=tkinter.LEFT)
                    internal_windows = tkinter.Frame(
                        self.rightWindow, width=100, height=20
                    )
                    internal_windows.pack(side=tkinter.TOP)
                    im_display_button = tkinter.Button(
                        master=internal_windows,
                        text="Display",
                        command=self.display_composite_image,
                    )
                    im_display_button.pack(side=tkinter.TOP)
                    internal_windows = tkinter.Frame(
                        self.rightWindow, width=100, height=20
                    )
                    internal_windows.pack(side=tkinter.TOP)
                    active_image = tkinter.StringVar(internal_windows)
                    active_image.set(
                        "("
                        + str(self.activeImage)
                        + ", "
                        + self.FileDictionary[self.activeImage]
                        + ")"
                    )
                    active_image.trace("w", self.image_changed)
                    w = tkinter.OptionMenu(
                        internal_windows, active_image, *self.FileDictionary.items()
                    )
                    w.config(width=10)
                    w.pack(side=tkinter.TOP)

                    self.activeImagePointer = active_image
                    self.Channel_pointers.append(Channel_pointers)
                    self.Color_pointers.append(Color_pointers)
                    self.channel_variable.append(channel_variable)
                    self.color_variable.append(color_variable)
                    self.im_raw.append(im_raw)
                    self.n_channels.append(n_channels)
                    self.im_analyzed.append([])
                    self.analyze_index.append([])
                    self.foreground_threshold.append([])
                    self.analysis_params.append(self.default_analysis_params)
                    self.Cell_props.append([])
                    self.Tissue_props.append({})
                    self.small_images.append([])
        self.remake_side_window()

    def openFolder_test(*a):
        stitch_large = self.combine_large in [
            "Stitch images",
            "Stitch and downsample",
            "PreDetermined stitch",
        ]
        if stitch_large:

            def get_tick_values(*args):
                self.magnification = 1
                for i in range(dropdown_options.index(combine_option.get())):
                    self.magnification = self.magnification * 2

            popup = tkinter.Tk()
            dropdown_options = ["10x", "20x", "40x"]
            combine_option = tkinter.StringVar(popup)
            combine_option.set(dropdown_options[0])
            combine_option.trace("w", get_tick_values)
            label = tkinter.Label(popup, text="The magnification is:")
            label.pack()
            c = tkinter.OptionMenu(popup, combine_option, *dropdown_options)
            c.pack()
            folderButton = ttkinter.Button(
                popup,
                text="Load Folder",
                command=lambda: [get_tick_values(), DestroyTK(popup), openFolder_sub()],
            )
            folderButton.pack()
            popup.mainloop()

        else:
            openFolder_sub()

    def get_tick_values(*args):
        self.combine_large = combine_option.get()

    popup = tkinter.Tk()
    dropdown_options = [
        "Do not combine images",
        "Combine images",
        "Combine and downsample",
        "Stitch images",
        "Stitch and downsample",
        "PreDetermined stitch",
    ]
    combine_option = tkinter.StringVar(popup)
    combine_option.set(dropdown_options[0])
    combine_option.trace("w", get_tick_values)
    c = tkinter.OptionMenu(popup, combine_option, *dropdown_options)
    c.pack()
    folderButton = ttkinter.Button(
        popup,
        text="Load Folder",
        command=lambda: [get_tick_values(), DestroyTK(popup), openFolder_test()],
    )
    folderButton.pack()
    popup.mainloop()


def LoadWorkspace(self):
    filenames = tkinter.filedialog.askopenfilenames(parent=self.master)
    [popup_int, label_int] = popupmsg("...", False)
    for n_im, filename in enumerate(filenames):
        label_int["text"] = (
            "Loading workspace for "
            + str(n_im + 1)
            + " of "
            + str(len(filenames))
            + " images.\n Please hold."
        )
        popup_int.update()
        try:
            pickle_data = pickle.load(open(filename, "rb"))
            self.activeImage = len(self.FileDictionary)
            if isinstance(pickle_data["im_raw"], str):
                im_raw = np.squeeze(
                    np.float32(np.array(skimage.io.imread(pickle_data["im_raw"])))
                )
                self.im_raw.append(im_raw)
            else:
                self.im_raw.append(pickle_data["im_raw"])

            self.FileDictionary[len(self.FileDictionary)] = pickle_data["filename"]
            self.Channel_pointers.append(pickle_data["Channel_pointers"])
            self.Color_pointers.append(pickle_data["Color_pointers"])
            self.im_analyzed.append(pickle_data["im_analyzed"])
            self.analyze_index.append(pickle_data["analyze_index"])
            self.Cell_props.append(pickle_data["Cell_props"])
            self.analysis_params.append(pickle_data["analysis_params"])
            self.n_channels.append(min(self.im_raw[self.activeImage].shape))
            if "Tissue_props" in pickle_data:
                self.Tissue_props.append(pickle_data["Tissue_props"])
            else:
                self.Tissue_props.append({})
            self.foreground_threshold.append(pickle_data["foreground_threshold"])
            self.small_images.append([])
            Color_pointers = self.Color_pointers[self.activeImage]
            channel_variable = []
            color_variable = []
            n_channels = self.n_channels[self.activeImage]
            for i in range(n_channels):
                channel_variable.append([])
                color_variable.append([])
            for i in range(n_channels, len(Color_pointers)):
                color_variable.append([])
            self.channel_variable.append(channel_variable)
            self.color_variable.append(color_variable)
            self.activeImagePointer = []
            self.remake_side_window()
        except NameError:
            pass
        except AttributeError:
            pass
    DestroyTK(popup_int)
    self.remake_side_window()


def LoadWorkspaceFolder(self):
    filename = tkinter.filedialog.askopenfilename(parent=self.master)
    filedir = filename[: -1 * filename[::-1].find("/")]
    file_list = os.listdir(filedir)
    [popup_int, label_int] = popupmsg("...", False)
    for n_im, filename in enumerate(file_list):
        print(filename)
        label_int["text"] = (
            "Loading workspace for "
            + str(n_im + 1)
            + " of "
            + str(len(file_list))
            + " images.\n Please hold."
        )
        popup_int.update()
        try:
            filename = filedir + filename
            pickle_data = pickle.load(open(filename, "rb"))
            self.activeImage = len(self.FileDictionary)
            self.im_raw.append(pickle_data["im_raw"])
            self.FileDictionary[len(self.FileDictionary)] = pickle_data["filename"]
            self.Channel_pointers.append(pickle_data["Channel_pointers"])
            self.Color_pointers.append(pickle_data["Color_pointers"])
            self.im_analyzed.append(pickle_data["im_analyzed"])
            self.analyze_index.append(pickle_data["analyze_index"])
            self.Cell_props.append(pickle_data["Cell_props"])
            self.analysis_params.append(pickle_data["analysis_params"])
            if "Tissue_props" in pickle_data:
                self.Tissue_props.append(pickle_data["Tissue_props"])
            else:
                self.Tissue_props.append({})
            self.n_channels.append(min(self.im_raw[self.activeImage].shape))
            self.foreground_threshold.append(pickle_data["foreground_threshold"])
            self.small_images.append([])
            print(pickle_data["analysis_params"])
            Color_pointers = self.Color_pointers[self.activeImage]
            channel_variable = []
            color_variable = []
            n_channels = self.n_channels[self.activeImage]
            for i in range(n_channels):
                channel_variable.append([])
                color_variable.append([])
            for i in range(n_channels, len(Color_pointers)):
                color_variable.append([])
            self.channel_variable.append(channel_variable)
            self.color_variable.append(color_variable)
            self.activeImagePointer = []
        except NameError:
            pass
        except AttributeError:
            pass
    DestroyTK(popup_int)
    self.remake_side_window()


def ChangeChannelSetup(self, n_Ch=0):
    def LoadDefaultChannels(*args):
        self.all_lookup_markers = {
            0: ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
            1: ["DAPI", "CD8", "VISTA", "CD138", "CD11b", "background", "garbage"],
            2: [
                "CD3",
                "CD20",
                "CD8",
                "CK",
                "DAPI",
                "CD56",
                "CD68",
                "background",
                "garbage",
            ],
            3: [
                "DAPI",
                "CD8",
                "CD20",
                "CD3",
                "CD68",
                "CD56",
                "CK",
                "background",
                "garbage",
            ],
            4: [
                "DAPI",
                "CK",
                "CD8",
                "CD3",
                "FOXP3",
                "CD45RO",
                "GZMB",
                "background",
                "garbage",
            ],
            5: [
                "DAPI",
                "PD-L1",
                "CD11C",
                "HLA-DR",
                "CD163",
                "CK",
                "CD68",
                "background",
                "garbage",
            ],
            6: ["CK", "Ki67", "APOBEC", "DAPI", "background"],
            7: [
                "PD-1",
                "Gal-9",
                "TIM-3",
                "CD-8",
                "Ki-67",
                "PD-L1",
                "CK",
                "DAPI",
                "background",
            ],
            8: [
                "DAPI",
                "CD8",
                "Coumarin",
                "S100A7",
                "Col10",
                "CD11b",
                "Clec9A",
                "CD163",
                "background",
            ],
            9: [
                "CD4",
                "CD8",
                "CD11b",
                "CXCR3",
                "T-bet",
                "PD1",
                "DAPI",
                "CK",
                "background",
            ],
            10: [
                "FOXP3",
                "CD20",
                "BCL6",
                "T-bet",
                "CD21",
                "CD4",
                "DAPI",
                "CK",
                "background",
            ],
            11: ["DAPI", "GR1", "F4/80", "CD8", "background"],
            12: ["CD8", "IDH", "DAPI", "CD56", "CD3", "CD68", "CD20", "background"],
            13: [
                "CD56",
                "CD20",
                "CD8",
                "CK",
                "DAPI",
                "CD68",
                "CD3",
                "background",
                "garbage",
            ],
            14: [
                "PD-L1",
                "CD57",
                "CK",
                "CD4",
                "DAPI",
                "CD8",
                "CD68",
                "background",
                "garbage",
            ],
            15: [
                "CD4",
                "CD20",
                "CD21",
                "CK",
                "DAPI",
                "FoxP3",
                "T-bet",
                "GZM-B",
                "background",
            ],
            16: ["DAPI", "TDO2", "SMA", "CD8", "CD11b", "ERG", "CK-B", "background"],
            17: [
                "Cycline B",
                "APOBEC3B",
                "Cycline E",
                "DAPI",
                "Ki67",
                "p-CK",
                "background",
            ],
            18: ["CD4", "CD8", "CD20", "CK", "DAPI", "background"],
            19: ["DAPI", "CD3", "CD68", "CD8", "CD56", "CD20", "CK", "background"],
            20: [
                "CK",
                "A3B",
                "Ki67",
                "CyclinB",
                "CyclinE",
                "DAPI",
                "CD8",
                "background",
            ],
            21: ["CD8", "DAPI", "CD4", "CD66b", "CK", "background"],
            22: [
                "CD8",
                "CD20",
                "CD66b",
                "CD68",
                "CK",
                "DAPI",
                "CD3",
                "CD56",
                "background",
            ],
            23: ["DAPI", "FAP", "D2-40(podoplanin)"],
            24: ["CD8", "CD3", "CD20", "CD68", "CD138", "DAPI", "MelanA", "background"],
            25: [
                "CD3",
                "CD8",
                "CD68",
                "TMEM119",
                "CD163",
                "DAPI",
                "CD20",
                "CD31",
                "background",
            ],
        }

        self.all_lookup_colors = {
            0: [
                "red",
                "green",
                "blue",
                "cyan",
                "magenta",
                "yellow",
                "orange",
                "pink",
                "white",
                "black",
            ],
            1: [
                "blue",
                "green",
                "red",
                "cyan",
                "yellow",
                "black",
                "magenta",
                "orange",
                "pink",
                "white",
            ],
            2: [
                "green",
                "yellow",
                "red",
                "cyan",
                "blue",
                "magenta",
                "orange",
                "black",
                "pink",
                "white",
            ],
            3: [
                "blue",
                "red",
                "yellow",
                "green",
                "orange",
                "magenta",
                "cyan",
                "black",
                "pink",
                "white",
            ],
            4: [
                "blue",
                "cyan",
                "red",
                "green",
                "magenta",
                "orange",
                "yellow",
                "black",
                "pink",
                "white",
            ],
            5: [
                "blue",
                "green",
                "yellow",
                "red",
                "magenta",
                "cyan",
                "orange",
                "black",
                "pink",
                "white",
            ],
            6: [
                "cyan",
                "red",
                "yellow",
                "blue",
                "black",
                "magenta",
                "green",
                "orange",
                "pink",
                "white",
            ],
            7: [
                "green",
                "pink",
                "yellow",
                "magenta",
                "white",
                "red",
                "cyan",
                "blue",
                "black",
                "orange",
            ],
            8: [
                "blue",
                "red",
                "cyan",
                "magenta",
                "pink",
                "orange",
                "yellow",
                "green",
                "black",
                "white",
            ],
            9: [
                "green",
                "red",
                "magenta",
                "yellow",
                "white",
                "pink",
                "blue",
                "cyan",
                "black",
                "orange",
            ],
            10: [
                "red",
                "yellow",
                "orange",
                "cyan",
                "magenta",
                "green",
                "blue",
                "pink",
                "black",
                "white",
            ],
            11: [
                "blue",
                "green",
                "red",
                "yellow",
                "black",
                "magenta",
                "cyan",
                "orange",
                "pink",
                "white",
            ],
            12: [
                "red",
                "white",
                "blue",
                "magenta",
                "green",
                "orange",
                "yellow",
                "black",
                "pink",
                "cyan",
            ],
            13: [
                "magenta",
                "yellow",
                "red",
                "cyan",
                "blue",
                "orange",
                "green",
                "black",
                "pink",
                "white",
            ],
            14: [
                "magenta",
                "yellow",
                "cyan",
                "green",
                "blue",
                "red",
                "orange",
                "black",
                "pink",
                "white",
            ],
            15: [
                "green",
                "red",
                "magenta",
                "white",
                "blue",
                "yellow",
                "cyan",
                "orange",
                "black",
                "pink",
            ],
            16: [
                "blue",
                "green",
                "pink",
                "red",
                "yellow",
                "magenta",
                "cyan",
                "black",
                "white",
                "orange",
            ],
            17: [
                "cyan",
                "yellow",
                "orange",
                "blue",
                "magenta",
                "green",
                "black",
                "red",
                "pink",
                "white",
            ],
            18: [
                "green",
                "red",
                "yellow",
                "cyan",
                "blue",
                "black",
                "orange",
                "magenta",
                "pink",
                "white",
            ],
            19: [
                "blue",
                "green",
                "orange",
                "red",
                "magenta",
                "yellow",
                "cyan",
                "black",
                "pink",
                "white",
            ],
            20: [
                "cyan",
                "yellow",
                "red",
                "orange",
                "magenta",
                "blue",
                "green",
                "black",
                "pink",
                "white",
            ],
            21: [
                "red",
                "blue",
                "green",
                "yellow",
                "cyan",
                "black",
                "orange",
                "magenta",
                "pink",
                "white",
            ],
            22: [
                "red",
                "yellow",
                "white",
                "orange",
                "cyan",
                "blue",
                "green",
                "magenta",
                "black",
                "pink",
            ],
            23: [
                "blue",
                "red",
                "green",
                "black",
                "yellow",
                "white",
                "orange",
                "cyan",
                "magenta",
                "pink",
            ],
            24: [
                "red",
                "green",
                "yellow",
                "orange",
                "magenta",
                "blue",
                "cyan",
                "black",
                "white",
                "pink",
            ],
            25: [
                "green",
                "red",
                "orange",
                "white",
                "cyan",
                "blue",
                "yellow",
                "magenta",
                "black",
                "pink",
            ],
        }
        self.all_marker_dropdown = [
            "Default",
            "Myeloma: DAPI:blue, CD8:green, VISTA:red, CD138:cyan," + " CD11b:yellow",
            "Bladder Cancer: CD3:green, CD20:yellow, CD8:red, CK:cyan,"
            + " DAPI:blue, CD56:magenta, CD68:orange",
            "TNBC: DAPI:blue, CD8:red, CD20:yellow, CD3:green,"
            + " CD68:orange, CD56:magenta, CK:cyan",
            "LUMC-T-cell: DAPI:blue, CK:cyan, CD8:red, CD3:green,"
            + " FOXP3:magenta, CD45RO:orange, GZMB:yellow",
            "LUMC-myeloid: DAPI:blue, PD-L1:green, CD11C:yellow,"
            + " HLA-DR:red,  CD163:magenta, CK:cyan, CD68:orange",
            "APOBEC-ISH: CK:cyan, Ki67:red, APOBEC:yellow, DAPI:blue",
            "Checkpoint: PD-1:green, Gal-9:pink, TIM-3:yellow,"
            + " CD-8:magenta, Ki-67:white, PD-L1: red, CK:cyan, DAPI:blue",
            "Exclusion: DAPI:blue, Opal540:red, Coumarin:cyan,"
            + " Opal650:magenta, Opal620:pink, Opan690:orange,"
            + " Opal570:yellow, Opal520:green, background:black",
            "Bladder-specific: CD4:green, CD8:red, CD11b:magenta,"
            + " CXCR3:yellow, T-bet:white, PD1:pink, DAPI:blue,"
            + " CK:cyan, background:black",
            "Oral-specific: FOXP3:red, CD20:yellow, BCL6:orange,"
            + " T-bet:cyan, CD21:magenta, CD4:green, DAPI:blue, CK:pink,"
            + " background:black",
            "FM1: DAPI:blue, GR1:green, F4/80:red, CD8:yellow," + " background:black",
            "Low-Grade Glioma: CD8:red, IDH: white, DAPI:blue,"
            + " CD56:magenta, CD3:green, CD68:orange, CD20:yellow,"
            + " background:black",
            "Bladder Cancer2: CD56:magenta, CD20:yellow, CD8:red,"
            + " CK:cyan, DAPI:blue, CD68:orange, CD3:green",
            "Hong Kong NPC: PD-L1:magenta, CD57:yellow, CK:cyan, CD4:"
            + "green, DAPI:blue, CD8:red, CD68:orange, background:black",
            "Bladder CD4 subsets: CD4:green, CD20:yellow, CD21:magenta,"
            + "CK:white, DAPI:blue, FoxP3:yellow, T-bet:cyan, "
            + "GZM-B:oragne, background:black",
            "ERG immune profiling in PRCA: DAPI: blue, TDO2:green, "
            + "SMA:pink, CD8:red, CD11b:yellow, ERG:magenta, CK:cyan, "
            + "background:black",
            "APOBEC panel: Cycline B: cyan, APOBEC3B: yellow, Cycline E:"
            + " orange, DAPI: blue, Ki67: magenta, CK: green",
            "Oral-Lymphocyte: CD4: green, CD8: red, CD20: yellow, CK:"
            + " cyan, DAPI: blue",
            "Ovarian: DAPI:blue, CD3:green, CD68:orange, CD8:red,"
            + " CD56:magenta, CD20:yellow, CK:cyan",
            "APOBEC-Cycline: CK:cyan, A3B:yellow, Ki67:red, CyclinB:orange,"
            + " CyclinE:magenta, DAPI:blue, CD8:green",
            "Neutrophil-Tcell panel: CD8:red, DAPI:blue, CD4:green, "
            + "CD66b:yellow, CK:cyan",
            "NPC-effector: CD8:red, CD20:yellow, CD66b:white, CD68:orange, "
            + "CK:cyan, DAPI:blue, CD3:green, CD56:magenta",
            "mUC TSE score: DAPI:blue, FAP:red, S2-40(podoplanin):green",
            "THREAT: CD8: red, CD3: green, CD20: yellow, CD68: orange, "
            + "CD138: magenta, DAPI: blue, MelanA: cyan",
            "HGG-myeloid: CD3: green, CD8: red, CD68: orange, TMEM119: "
            + "white, CD163: cyan, DAPI: blue, CD20: yellow, CD31: magenta",
        ]

        self.all_lookup_markers = {
            0: ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"],
            # 1: ["DAPI", "CD8", "VISTA", "CD138", "CD11b",
            #     "background", "garbage"],
            # 2: ["CD3", "CD20", "CD8", "CK", "DAPI", "CD56", "CD68",
            #     "background", "garbage"],
            1: [
                "DAPI",
                "CD8",
                "CD20",
                "CD3",
                "CD68",
                "CD56",
                "CK",
                "background",
                "garbage",
            ],
        }
        # 4: ["DAPI", "CK", "CD8", "CD3", "FOXP3", "CD45RO", "GZMB",
        #     "background", "garbage"],
        # 5: ["DAPI", "PD-L1", "CD11C", "HLA-DR", "CD163", "CK", "CD68",
        #     "background", "garbage"],
        # 6: ["CK", "Ki67", "APOBEC", "DAPI", "background"],
        # 7: ["PD-1", "Gal-9", "TIM-3", "CD-8", "Ki-67", "PD-L1", "CK",
        #     "DAPI", "background"],
        # 8: ["DAPI", "CD8", "Coumarin", "S100A7", "Col10", "CD11b",
        #     "Clec9A", "CD163", "background"],
        # 9: ["CD4", "CD8", "CD11b", "CXCR3", "T-bet", "PD1", "DAPI",
        #     "CK", "background"],
        # 10: ["FOXP3", "CD20", "BCL6", "T-bet", "CD21", "CD4", "DAPI",
        #     "CK", "background"],
        # 11: ["DAPI", "GR1", "F4/80", "CD8", "background"],
        # 12: ["CD8", "IDH", "DAPI", "CD56", "CD3", "CD68", "CD20",
        #     "background"],
        # 13: ["CD56", "CD20", "CD8", "CK", "DAPI", "CD68", "CD3",
        #     "background", "garbage"],
        # 14: ["PD-L1", "CD57", "CK", "CD4", "DAPI", "CD8", "CD68",
        #     "background", "garbage"],
        # 15: ["CD4", "CD20", "CD21", "CK", "DAPI", "FoxP3", "T-bet",
        #     "GZM-B", "background"],
        # 16: ["DAPI", "TDO2", "SMA", "CD8", "CD11b", "ERG",
        #     "CK-B", "background"],
        # 17: ["Cycline B", "APOBEC3B", "Cycline E", "DAPI", "Ki67",
        #     "p-CK", "background"],
        # 18: ['CD4', 'CD8', 'CD20', 'CK', 'DAPI', 'background'],
        # 19: ['DAPI','CD3', 'CD68', 'CD8', 'CD56', 'CD20', 'CK', 'background'],
        # 20: ['CK', 'A3B', 'Ki67', 'CyclinB', 'CyclinE', 'DAPI', 'CD8', 'background'],
        # 21: ['CD8', 'DAPI', 'CD4', 'CD66b', 'CK', 'background'],
        # 22: ['CD8', 'CD20', 'CD66b', 'CD68', 'CK', 'DAPI', 'CD3', 'CD56', 'background'],
        # 23: ['DAPI', 'FAP', 'D2-40(podoplanin)'],
        # 24: ['CD8','CD3','CD20','CD68','CD138','DAPI','MelanA','background'],
        # 25: ['CD3','CD8','CD68','TMEM119','CD163','DAPI','CD20','CD31','background']}

        self.all_lookup_colors = {
            0: [
                "red",
                "green",
                "blue",
                "cyan",
                "magenta",
                "yellow",
                "orange",
                "pink",
                "white",
                "black",
            ],
            # 1: ["blue", "green", "red", "cyan", "yellow", "black",
            #     "magenta", "orange", "pink", "white"],
            # 2: ["green", "yellow", "red", "cyan", "blue", "magenta",
            #     "orange", "black", "pink", "white"],
            1: [
                "blue",
                "red",
                "yellow",
                "green",
                "orange",
                "magenta",
                "cyan",
                "black",
                "pink",
                "white",
            ],
        }
        # 4: ["blue", "cyan", "red", "green", "magenta", "orange",
        #     "yellow", "black", "pink", "white"],
        # 5: ["blue", "green", "yellow", "red", "magenta", "cyan",
        #     "orange", "black", "pink", "white"],
        # 6: ["cyan", "red", "yellow", "blue", "black", "magenta",
        #     "green", "orange", "pink", "white"],
        # 7: ["green", "pink", "yellow", "magenta", "white", "red",
        #     "cyan", "blue", "black", "orange"],
        # 8: ["blue", "red", "cyan", "magenta", "pink", "orange",
        #     "yellow", "green", "black", "white"],
        # 9: ["green", "red", "magenta", "yellow", "white", "pink",
        #     "blue", "cyan", "black", "orange"],
        # 10: ["red", "yellow", "orange", "cyan", "magenta", "green",
        #     "blue", "pink", "black", "white"],
        # 11: ["blue", "green", "red", "yellow", "black", "magenta",
        #     "cyan", "orange", "pink", "white"],
        # 12: ["red", "white", "blue", "magenta", "green", "orange",
        #     "yellow", "black", "pink", "cyan"],
        # 13: ["magenta", "yellow", "red", "cyan", "blue", "orange",
        #     "green", "black", "pink", "white"],
        # 14: ["magenta", "yellow", "cyan", "green", "blue", "red",
        #     "orange", "black", "pink", "white"],
        # 15: ["green", "red", "magenta", "white", "blue", "yellow",
        #     "cyan", "orange", "black", "pink"],
        # 16: ["blue", "green", "pink", "red", "yellow", "magenta",
        #     "cyan", "black", "white", "orange"],
        # 17: ["cyan", "yellow", "orange", "blue", "magenta",
        #     "green", "black", "red", "pink", "white"],
        # 18: ["green", "red", "yellow", "cyan", "blue", "black",
        #     "orange", "magenta", "pink", "white"],
        # 19: ["blue", "green", "orange", "red",
        # "magenta", "yellow", "cyan", "black", "pink", "white"],
        # 20: ["cyan", "yellow", "red", "orange", "magenta",
        #     "blue", "green", "black", "pink", "white"],
        # 21: ["red", "blue", "green", "yellow", "cyan", "black",
        #     "orange", "magenta", "pink", "white"],
        # 22: ["red", "yellow", "white", "orange", "cyan", "blue",
        #     "green", "magenta", "black", "pink"],
        # 23: ["blue", "red", "green", "black",
        #     "yellow", "white", "orange", "cyan", "magenta", "pink"],
        # 24: ["red", "green", "yellow", "orange",
        #     "magenta", "blue", "cyan", "black",
        #     "white", "pink"],
        # 25: ["green", "red", "orange", "white", "cyan",
        #     "blue", "yellow", "magenta", "black",
        #     "pink"]}
        self.all_marker_dropdown = [
            "Default",
            # "Myeloma: DAPI:blue, CD8:green, VISTA:red, CD138:cyan," +
            # " CD11b:yellow",
            # "Bladder Cancer: CD3:green, CD20:yellow, CD8:red, CK:cyan," +
            # " DAPI:blue, CD56:magenta, CD68:orange",
            "TNBC: DAPI:blue, CD8:red, CD20:yellow, CD3:green,"
            + " CD68:orange, CD56:magenta, CK:cyan",
        ]
        # "LUMC-T-cell: DAPI:blue, CK:cyan, CD8:red, CD3:green," +
        # " FOXP3:magenta, CD45RO:orange, GZMB:yellow",
        # "LUMC-myeloid: DAPI:blue, PD-L1:green, CD11C:yellow," +
        # " HLA-DR:red,  CD163:magenta, CK:cyan, CD68:orange",
        # "APOBEC-ISH: CK:cyan, Ki67:red, APOBEC:yellow, DAPI:blue",
        # "Checkpoint: PD-1:green, Gal-9:pink, TIM-3:yellow," +
        # " CD-8:magenta, Ki-67:white, PD-L1: red, CK:cyan, DAPI:blue",
        # "Exclusion: DAPI:blue, Opal540:red, Coumarin:cyan," +
        # " Opal650:magenta, Opal620:pink, Opan690:orange," +
        # " Opal570:yellow, Opal520:green, background:black",
        # "Bladder-specific: CD4:green, CD8:red, CD11b:magenta," +
        # " CXCR3:yellow, T-bet:white, PD1:pink, DAPI:blue," +
        # " CK:cyan, background:black",
        # "Oral-specific: FOXP3:red, CD20:yellow, BCL6:orange," +
        # " T-bet:cyan, CD21:magenta, CD4:green, DAPI:blue, CK:pink," +
        # " background:black",
        # "FM1: DAPI:blue, GR1:green, F4/80:red, CD8:yellow," +
        # " background:black",
        # "Low-Grade Glioma: CD8:red, IDH: white, DAPI:blue," +
        # " CD56:magenta, CD3:green, CD68:orange, CD20:yellow," +
        # " background:black",
        # "Bladder Cancer2: CD56:magenta, CD20:yellow, CD8:red," +
        # " CK:cyan, DAPI:blue, CD68:orange, CD3:green",
        # "Hong Kong NPC: PD-L1:magenta, CD57:yellow, CK:cyan, CD4:" +
        # "green, DAPI:blue, CD8:red, CD68:orange, background:black",
        # "Bladder CD4 subsets: CD4:green, CD20:yellow, CD21:magenta," +
        # "CK:white, DAPI:blue, FoxP3:yellow, T-bet:cyan, " +
        # "GZM-B:oragne, background:black",
        # "ERG immune profiling in PRCA: DAPI: blue, TDO2:green, " +
        # "SMA:pink, CD8:red, CD11b:yellow, ERG:magenta, CK:cyan, " +
        # "background:black",
        # "APOBEC panel: Cycline B: cyan, APOBEC3B: yellow, Cycline E:"+
        # " orange, DAPI: blue, Ki67: magenta, CK: green",
        # "Oral-Lymphocyte: CD4: green, CD8: red, CD20: yellow, CK:"+
        # " cyan, DAPI: blue",
        # "Ovarian: DAPI:blue, CD3:green, CD68:orange, CD8:red," +
        # " CD56:magenta, CD20:yellow, CK:cyan",
        # "APOBEC-Cycline: CK:cyan, A3B:yellow, Ki67:red, CyclinB:orange," +
        # " CyclinE:magenta, DAPI:blue, CD8:green",
        # "Neutrophil-Tcell panel: CD8:red, DAPI:blue, CD4:green, "+
        # "CD66b:yellow, CK:cyan",
        # "NPC-effector: CD8:red, CD20:yellow, CD66b:white, CD68:orange, "+
        # "CK:cyan, DAPI:blue, CD3:green, CD56:magenta",
        # "mUC TSE score: DAPI:blue, FAP:red, S2-40(podoplanin):green",
        # "THREAT: CD8: red, CD3: green, CD20: yellow, CD68: orange, "+
        # "CD138: magenta, DAPI: blue, MelanA: cyan",
        # "HGG-myeloid: CD3: green, CD8: red, CD68: orange, TMEM119: "+
        # "white, CD163: cyan, DAPI: blue, CD20: yellow, CD31: magenta"]

    def define_new_channel(*args):
        def addCh(*a):
            internal_windows = tkinter.Frame(popup_int, width=100, height=10)
            internal_windows.pack(side=tkinter.TOP)
            data_int = []
            data_int.append(internal_windows)
            internal_windows1 = tkinter.Frame(internal_windows)
            internal_windows1.pack(side=tkinter.LEFT)
            data_int.append(internal_windows1)
            marker_name1 = tkinter.StringVar(internal_windows1)
            marker_name1.set("DAPI")
            data_int.append(marker_name1)
            data_int.append(marker_name1.get())
            marker_1 = tkinter.Entry(internal_windows1, textvariable=marker_name1)
            marker_1.config(width=10)
            marker_1.pack(side=tkinter.LEFT)
            ch_name1 = tkinter.StringVar(internal_windows1)
            ch_name1.set("blue")
            data_int.append(ch_name1)
            data_int.append(ch_name1.get())
            ch_var_pointer1 = tkinter.OptionMenu(
                internal_windows1, ch_name1, *self.LUT.keys()
            )
            ch_var_pointer1.config(width=10)
            ch_var_pointer1.pack(side=tkinter.LEFT)
            n = len(self.newChSetup)
            data_int.append(n)
            self.newChSetup.append(data_int)

        def rmvCh(*a):
            DOI = np.int32(ChlabelButton.get())
            if (DOI <= len(self.newChSetup)) & (DOI > 0):
                DestroyTK(self.newChSetup[DOI - 1][0])
                self.newChSetup.pop(DOI - 1)
            for i in range(0, len(self.newChSetup)):
                self.newChSetup[i][6] = i

        def save_channel(*a):
            if len(self.newChSetup) == 0:
                return
            filename_save = tkinter.filedialog.asksaveasfilename(parent=popup_main)
            ChannelParams = [[i[2].get(), i[4].get()] for i in self.newChSetup]
            if filename_save:
                pickle_savename = filename_save
                if filename_save[-7:] != ".pickle":
                    if "." not in filename_save[-5:]:
                        pickle_savename += ".pickle"
                with open(pickle_savename, "wb") as f:
                    pickle.dump({"Channel Params": ChannelParams}, f)

        def load_channel(*a):
            filename = tkinter.filedialog.askopenfilename(parent=popup_main)
            pickle_data = pickle.load(open(filename, "rb"))
            ChannelParams = pickle_data["Channel Params"]
            if len(ChannelParams) == 0:
                return
            self.newChSetup = []
            for i in range(len(ChannelParams)):
                data_int_temp = ChannelParams[i]
                internal_windows = tkinter.Frame(popup_int, width=100, height=10)
                internal_windows.pack(side=tkinter.TOP)
                data_int = []
                data_int.append(internal_windows)
                internal_windows1 = tkinter.Frame(internal_windows)
                internal_windows1.pack(side=tkinter.LEFT)
                data_int.append(internal_windows1)
                marker_name1 = tkinter.StringVar(internal_windows1)
                marker_name1.set(data_int_temp[0])
                data_int.append(marker_name1)
                data_int.append(marker_name1.get())
                marker_1 = tkinter.Entry(internal_windows1, textvariable=marker_name1)
                marker_1.config(width=10)
                marker_1.pack(side=tkinter.LEFT)
                ch_name1 = tkinter.StringVar(internal_windows1)
                ch_name1.set(data_int_temp[1])
                data_int.append(ch_name1)
                data_int.append(ch_name1.get())
                ch_var_pointer1 = tkinter.OptionMenu(
                    internal_windows1, ch_name1, *self.LUT.keys()
                )
                ch_var_pointer1.config(width=10)
                ch_var_pointer1.pack(side=tkinter.LEFT)
                n = len(self.newChSetup)
                data_int.append(n)
                self.newChSetup.append(data_int)
            popup_main.destroy()
            define_new_channel(self)

        def ResetSetup(*a):
            self.newChSetup = []
            internal_windows = tkinter.Frame(popup_int, width=100, height=10)
            internal_windows.pack(side=tkinter.TOP)
            data_int = []
            data_int.append(internal_windows)
            internal_windows1 = tkinter.Frame(internal_windows)
            internal_windows1.pack(side=tkinter.LEFT)
            data_int.append(internal_windows1)
            marker_name1 = tkinter.StringVar(internal_windows1)
            marker_name1.set("DAPI")
            data_int.append(marker_name1)
            data_int.append(marker_name1.get())
            marker_1 = tkinter.Entry(internal_windows1, textvariable=marker_name1)
            marker_1.config(width=10)
            marker_1.pack(side=tkinter.LEFT)
            ch_name1 = tkinter.StringVar(internal_windows1)
            ch_name1.set("blue")
            data_int.append(ch_name1)
            data_int.append(ch_name1.get())
            ch_var_pointer1 = tkinter.OptionMenu(
                internal_windows1, ch_name1, *self.LUT.keys()
            )
            ch_var_pointer1.config(width=10)
            ch_var_pointer1.pack(side=tkinter.LEFT)
            data_int.append(0)
            self.newChSetup.append(data_int)
            popup_main.destroy()
            define_new_channel(self)

        def SaveandClose(*a):
            n_Ch = len(self.all_lookup_markers)
            self.all_lookup_markers[n_Ch] = [i[2].get() for i in self.newChSetup]
            self.all_lookup_colors[n_Ch] = [i[4].get() for i in self.newChSetup]
            marker_string = ""
            for i in self.newChSetup:
                marker_string += i[2].get() + ": " + i[4].get() + ", "
            self.all_marker_dropdown.append(marker_string[:-2])
            popup_main.destroy()
            ChangeChannelSetup(self, n_Ch)

        popup_main = tkinter.Tk()
        # popup_main.geometry("1200x800")
        popup_main.wm_title("Add New Channel")
        popup_int = tkinter.Frame(popup_main)  # , width=400, height=1000)
        toolbar = tkinter.Frame(popup_main)
        addPopButton = ttkinter.Button(toolbar, text="Add Channel", command=addCh)
        addPopButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        rmvPopButton = ttkinter.Button(toolbar, text="Remove Channel", command=rmvCh)
        rmvPopButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        ChlabelButton = tkinter.Entry(toolbar)
        ChlabelButton.pack(side=tkinter.LEFT)
        ChlabelButton.insert(0, "1")

        showDataButton = ttkinter.Button(
            toolbar, text="Save Setup to File", command=save_channel
        )
        showDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        appDataButton = ttkinter.Button(
            toolbar, text="Load Setup", command=load_channel
        )
        appDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        rmvDataButton = ttkinter.Button(toolbar, text="Reset Setup", command=ResetSetup)
        rmvDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        saveDataButton = ttkinter.Button(
            toolbar, text="Save and Close", command=SaveandClose
        )
        saveDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
        popup_int.pack(side=tkinter.TOP)
        if len(self.newChSetup) != 0:
            # addPhenoButton = []
            for i in range(len(self.newChSetup)):
                data_int = self.newChSetup[i]
                internal_windows = tkinter.Frame(popup_int, width=100, height=10)
                internal_windows.pack(side=tkinter.TOP)
                data_int[0] = internal_windows
                internal_windows1 = tkinter.Frame(internal_windows)
                internal_windows1.pack(side=tkinter.LEFT)
                data_int[1] = internal_windows1
                marker_name1 = tkinter.StringVar(internal_windows)
                marker_name1.set(data_int[2].get())
                data_int[2] = marker_name1
                data_int[3] = marker_name1.get()
                marker_1 = tkinter.Entry(internal_windows1, textvariable=marker_name1)
                marker_1.config(width=10)
                marker_1.pack(side=tkinter.LEFT)
                ch_name1 = tkinter.StringVar(internal_windows1)
                ch_name1.set(data_int[4].get())
                data_int[4] = ch_name1
                data_int[5] = ch_name1.get()
                ch_var_pointer1 = tkinter.OptionMenu(
                    internal_windows1, ch_name1, *self.LUT.keys()
                )
                ch_var_pointer1.config(width=10)
                ch_var_pointer1.pack(side=tkinter.LEFT)
                data_int[6] = i
                self.newChSetup[i] = data_int
        else:
            internal_windows = tkinter.Frame(popup_int, width=100, height=10)
            internal_windows.pack(side=tkinter.TOP)
            data_int = []
            data_int.append(internal_windows)
            internal_windows1 = tkinter.Frame(internal_windows)
            internal_windows1.pack(side=tkinter.LEFT)
            data_int.append(internal_windows1)
            marker_name1 = tkinter.StringVar(internal_windows1)
            marker_name1.set("DAPI")
            data_int.append(marker_name1)
            data_int.append(marker_name1.get())
            marker_1 = tkinter.Entry(internal_windows1, textvariable=marker_name1)
            marker_1.config(width=10)
            marker_1.pack(side=tkinter.LEFT)
            ch_name1 = tkinter.StringVar(internal_windows1)
            ch_name1.set("blue")
            data_int.append(ch_name1)
            data_int.append(ch_name1.get())
            ch_var_pointer1 = tkinter.OptionMenu(
                internal_windows1, ch_name1, *self.LUT.keys()
            )
            ch_var_pointer1.config(width=10)
            ch_var_pointer1.pack(side=tkinter.LEFT)
            data_int.append(0)
            self.newChSetup.append(data_int)

    def get_tick_values(*args):
        self.Markers = lookup_markers[dropdown_options.index(combine_option.get())]
        self.Color_info = lookup_colors[dropdown_options.index(combine_option.get())]

    lookup_markers = self.all_lookup_markers
    lookup_colors = self.all_lookup_colors
    popup = tkinter.Tk()
    dropdown_options = self.all_marker_dropdown
    combine_option = tkinter.StringVar(popup)
    combine_option.set(dropdown_options[n_Ch])
    combine_option.trace("w", get_tick_values)
    c = tkinter.OptionMenu(popup, combine_option, *dropdown_options)
    c.pack()

    confirmButton = ttkinter.Button(
        popup, text="Confirm", command=lambda: [get_tick_values(), DestroyTK(popup)]
    )
    confirmButton.pack()
    addButton = ttkinter.Button(
        popup,
        text="Add channel setup",
        command=lambda: [define_new_channel(), DestroyTK(popup)],
    )
    addButton.pack()
    LoadDButton = ttkinter.Button(
        popup,
        text="Load default channels",
        command=lambda: [
            LoadDefaultChannels(),
            DestroyTK(popup),
            ChangeChannelSetup(self),
        ],
    )
    LoadDButton.pack()
    popup.mainloop()


def cropFile(self):
    def SelectCrop(*a):
        DestroyTK(self.popup_statusBar)
        t = "Select the crop region with a rectangle."
        self.popup_statusBar = tkinter.Label(
            self.popup, text=t, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
        )
        self.popup_statusBar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.CropRectangle = matplotlib.widgets.RectangleSelector(
            self.ax,
            onCropSelect,
            lineprops=dict(color="w", linestyle="-", linewidth=2, alpha=0.5),
            marker_props=dict(marker="o", markersize=7, mec="w", mfc="w", alpha=0.5),
        )
        self.CropRectrangle.set_active(True)
        if self.showCropmessage == 1:
            self.showCropmessage = 0
            popupmsg(t)

    def onCropSelect(eclick, erelease, *a):
        vertices = [eclick.xdata, erelease.xdata, eclick.ydata, erelease.ydata]
        vertices = [np.max([np.int32(np.round(x)), 0]) for x in vertices]
        self.CropRectangle.set_active(False)
        mask = np.zeros_like(self.reduced_image[:, :, 0])
        vertices[:2] = [np.min([x, mask.shape[1]]) for x in vertices[:2]]
        vertices[2:] = [np.min([x, mask.shape[0]]) for x in vertices[2:]]
        mask[vertices[2] : vertices[3], vertices[0] : vertices[1]] = 1
        self.activeCrop = mask
        ax = self.ax
        if len(self.activeCrop) != 0:
            im_temp = self.imCropImage
            mask_copy = np.float32(self.activeCrop)
            mask_copy = (1 - mask_copy) / 2
            for i in range(3):
                im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
            ax.clear()
            ax.imshow(im_temp, aspect="equal")
            ax.autoscale(False)
            ax.axis("off")
            for i in range(3):
                im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
                self.ax_canvas.draw()

    def addCrop(*a):
        mask = self.activeCrop
        im_raw = self.im_raw[self.activeImage]
        while round(log(mask.size / im_raw[:, :, 0].size, 2)) < 0:
            mask = skimage.transform.pyramid_expand(mask)
        a = im_raw[:, :, 0][np.ix_(mask.any(1), mask.any(0))]
        a = np.zeros([a.shape[0], a.shape[1], im_raw.shape[2]], dtype=im_raw.dtype)
        for i in range(im_raw.shape[2]):
            a[:, :, i] = im_raw[:, :, i][np.ix_(mask.any(1), mask.any(0))]
        im_raw = a
        self.FileDictionary[len(self.FileDictionary)] = (
            self.FileDictionary[self.activeImage] + "- cropped"
        )
        self.Channel_pointers.append(self.Channel_pointers[self.activeImage])
        self.Color_pointers.append(self.Color_pointers[self.activeImage])
        self.channel_variable.append(self.channel_variable[self.activeImage])
        self.color_variable.append(self.color_variable[self.activeImage])
        self.im_raw.append(im_raw)
        self.n_channels.append(self.n_channels[self.activeImage])
        self.im_analyzed.append([])
        self.analyze_index.append([])
        self.foreground_threshold.append([])
        self.analysis_params.append(self.default_analysis_params)
        self.Cell_props.append([])
        self.Tissue_props.append({})
        self.remake_side_window()
        self.small_images.append([])

    def SaveCrop(*a):
        ftypes = [("Tiff images", ".tif .tiff")]
        filename = tkinter.filedialog.asksaveasfilename(
            parent=self.master, filetypes=ftypes
        )
        if filename:
            mask = self.activeCrop
            im_raw = self.im_raw[self.activeImage]
            while round(log(mask.size / im_raw[:, :, 0].size, 2)) < 0:
                mask = skimage.transform.pyramid_expand(mask)
            a = im_raw[:, :, 0][np.ix_(mask.any(1), mask.any(0))]
            a = np.zeros([a.shape[0], a.shape[1], im_raw.shape[2]], dtype=im_raw.dtype)
            for i in range(im_raw.shape[2]):
                a[:, :, i] = im_raw[:, :, i][np.ix_(mask.any(1), mask.any(0))]
            im_raw = a
            if not (filename[-4:] == ".tif") | (filename[-5:] == ".tiff"):
                filename += ".tif"
            skimage.io.imsave(filename, im_raw.transpose(2, 0, 1))

    def QuitCrop(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = ttkinter.Label(popup2, text="You are about to quit image cropping")
        label.pack(side="top", fill="x", pady=10)
        B1 = ttkinter.Button(
            popup2,
            text="Okay",
            command=lambda: [DestroyTK(self.popup), DestroyTK(popup2)],
        )
        B1.pack()
        B2 = ttkinter.Button(
            popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
        )
        B2.pack()
        popup2.mainloop()

    im_raw = self.im_raw[self.activeImage]
    image_size = np.size(im_raw)
    if image_size > 100000000:
        im_raw_norm = im_raw.max()
        im_raw = im_raw / im_raw_norm

        while np.size(im_raw) > 100000000:
            im_raw = skimage.transform.pyramid_reduce(im_raw)
        im_raw = im_raw * im_raw_norm
    self.small_images[self.activeImage] = im_raw
    popup = tkinter.Tk()
    self.reduced_image = im_raw
    self.popup = popup
    Color_pointers = self.Color_pointers[self.activeImage]
    color_variable = self.color_variable[self.activeImage]
    Channel_pointers = self.Channel_pointers[self.activeImage]
    channel_variable = self.channel_variable[self.activeImage]
    n_channels = self.n_channels[self.activeImage]
    im_2_display = np.zeros((im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32)
    for i in range(n_channels):
        Color_pointers_temp = color_variable[i].get()
        Color_pointers[i] = color_variable[i].get()
        Channel_pointers[i] = channel_variable[i].get()
        for j in range(3):
            im_temp = im_2_display[:, :, j]
            im2_add = im_raw[:, :, i] / im_raw[:, :, i].max()
            im2_add = im2_add * self.LUT[Color_pointers_temp][j]
            im_temp = im_temp + im2_add
            im_2_display[:, :, j] = im_temp
    popup.wm_title("Crop Image")
    label = ttkinter.Label(
        popup, text="Image crop for file :" + self.FileDictionary[self.activeImage]
    )
    toolbar = tkinter.Frame(popup)
    selectButton = ttkinter.Button(toolbar, text="Select", command=SelectCrop)
    selectButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    addButton = ttkinter.Button(toolbar, text="Crop", command=addCrop)
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    saveButton = ttkinter.Button(toolbar, text="Save Image", command=SaveCrop)
    saveButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    cancelButton = ttkinter.Button(toolbar, text="Quit", command=QuitCrop)
    cancelButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
    label.pack(side="bottom", fill="x", pady=10)
    f = plt.Figure(figsize=(10, 7), dpi=100)
    f.patch.set_visible(False)
    f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax = f.gca()
    image_canvas = Tk_Agg.FigureCanvasTkAgg(f, master=popup)
    image_canvas.draw()
    image_canvas.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_toolbar = NT2Tk(image_canvas, popup)
    image_toolbar.update()
    image_canvas._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    ax.clear()
    ax.imshow(im_2_display, aspect="equal")
    self.imCropImage = im_2_display
    ax.autoscale(False)
    ax.axis("off")
    self.ax = ax
    image_canvas.draw()
    self.ax_canvas = image_canvas
    self.popup_statusBar = tkinter.Label(
        popup, text="Cropping Image", bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
    )
    self.popup_statusBar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
    if len(self.activeCrop) != 0:
        im_temp = im_2_display
        mask_copy = np.float32(self.activeCrop)
        mask_copy = (1 - mask_copy) / 2
        for i in range(3):
            im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
        ax.clear()
        ax.imshow(im_temp, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        for i in range(3):
            im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
            self.ax_canvas.draw()
    popup.mainloop()


def ResetCurrent(self):
    def ResetSure(*a):
        n_channels = self.n_channels[self.activeImage]
        self.channel_variable[self.activeImage] = self.channel_variable[
            self.activeImage
        ][0:n_channels]
        self.color_variable[self.activeImage] = self.color_variable[self.activeImage][
            0:n_channels
        ]
        self.Color_pointers[self.activeImage] = self.Color_pointers[self.activeImage][
            0:n_channels
        ]
        self.Channel_pointers[self.activeImage] = self.Channel_pointers[
            self.activeImage
        ][0:n_channels]
        self.im_analyzed[self.activeImage] = []
        self.analyze_index[self.activeImage] = []
        self.foreground_threshold[self.activeImage] = []
        self.analysis_params[self.activeImage] = self.default_analysis_params.copy()
        self.Cell_props[self.activeImage] = []
        self.Tissue_props[self.activeImage] = {}
        self.small_images[self.activeImage] = []
        self.remake_side_window()

    popup2 = tkinter.Tk()
    popup2.wm_title("Are you sure?")
    label = tkinter.Label(popup2, text="You are about to reset your current anaylsis")
    label.pack(side="top", fill="x", pady=10)
    B1 = tkinter.Button(
        popup2, text="Go Ahead", command=lambda: [DestroyTK(popup2), ResetSure()]
    )
    B1.pack()
    B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
    B2.pack()
    popup2.mainloop()


def RemoveCurrent(self):
    def ResetSure(*a):
        self.n_channels.pop(self.activeImage)
        self.channel_variable.pop(self.activeImage)
        self.color_variable.pop(self.activeImage)
        self.Color_pointers.pop(self.activeImage)
        self.Channel_pointers.pop(self.activeImage)
        self.im_analyzed.pop(self.activeImage)
        self.analyze_index.pop(self.activeImage)
        self.foreground_threshold.pop(self.activeImage)
        self.analysis_params.pop(self.activeImage)
        self.Cell_props.pop(self.activeImage)
        self.Tissue_props.pop(self.activeImage)
        self.small_images.pop(self.activeImage)
        self.im_raw.pop(self.activeImage)
        FileDictionary_init = self.FileDictionary.copy()
        self.FileDictionary = {}
        for i in FileDictionary_init.keys():
            if i == self.activeImage:
                continue
            self.FileDictionary[len(self.FileDictionary)] = FileDictionary_init[i]
        self.activeImage = 0
        self.remake_side_window()

    popup2 = tkinter.Tk()
    popup2.wm_title("Are you sure?")
    label = tkinter.Label(
        popup2, text="You are about to remove the image and its analysis"
    )
    label.pack(side="top", fill="x", pady=10)
    B1 = tkinter.Button(
        popup2, text="Go Ahead", command=lambda: [DestroyTK(popup2), ResetSure()]
    )
    B1.pack()
    B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
    B2.pack()
    popup2.mainloop()


def Reset(self):
    def ResetSure(*a):
        self.im_raw = []
        self.channel_variable = []
        self.color_variable = []
        self.Color_pointers = []
        self.Channel_pointers = []
        self.FileDictionary = {}
        self.ThresholdValues = []
        self.activeImage = []
        self.n_channels = []
        self.activeROI = []
        self.im_analyzed = []
        self.analyze_index = []
        self.foreground_threshold = []
        self.activeFore = []
        self.NucLimits = []
        self.HoleLimits = []
        self.ForeLimits = []
        self.Cell_props = []
        self.Tissue_props = []
        self.overall_data_to_export = {}
        self.analysis_params = []
        self.fill_ch = -1
        self.small_images = []
        self.remake_side_window()

    popup2 = tkinter.Tk()
    popup2.wm_title("Are you sure?")
    label = tkinter.Label(popup2, text="You are about to reset your whole anaylsis")
    label.pack(side="top", fill="x", pady=10)
    B1 = tkinter.Button(
        popup2, text="Go Ahead", command=lambda: [DestroyTK(popup2), ResetSure()]
    )
    B1.pack()
    B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
    B2.pack()
    popup2.mainloop()
