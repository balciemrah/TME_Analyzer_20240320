# -*- coding: utf-8 -*-
"""
Created on Monday Oct 23rd 2023
dMO.PhenotypeSelection
dMO.DataAnalysis
dMO.Get_cell_props
dMO.Tissue_analysis
dMO.QuickAnalysis
dMO.RedoAnalysis
dMO.RedoAnalysisAll
"""


import tkinter
import os
from tkinter import ttk as ttkinter
import tkinter.messagebox
import tkinter.filedialog
import skimage.io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.backends.backend_tkagg as Tk_Agg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NT2Tk
from scipy import ndimage as ndi
import skimage.measure
from skimage.feature import peak_local_max
import pandas as pd
from math import atan2, pi as PI
import pickle
import stardist
import stardist.models
from csbdeep.utils import normalize as StarDist2D_normalize
from collections import Counter

if __package__ == "tmeanalyzer":
    from . import imageMenu as iMO
    from .imageMenu import DestroyTK, popupmsg
else:
    import imageMenu as iMO
    from imageMenu import DestroyTK, popupmsg
# import FlowCytometryTools
# import openTSNE
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


def Apply_default_analysis(self):
    def Apply_default_analysis_sure(*a):
        self.analysis_params[self.activeImage] = {
            "Segments": {
                "CK_filtered": {
                    "Visible": True,
                    "filter_1": 10,
                    "filter_2": 1000,
                    "filter_type1": "Gaussian",
                    "filter_type2": "Minimum",
                    "operator": "and-",
                    "Ch_name": "CK",
                    "normalize": 0,
                    "normalize": 0,
                },
                "CD8-Filter": {
                    "Visible": False,
                    "filter_1": 0,
                    "filter_2": 1000,
                    "filter_type1": "Gaussian",
                    "filter_type2": "Uniform",
                    "operator": "-",
                    "Ch_name": "CD8",
                    "normalize": 0,
                },
                "CD20-Filter": {
                    "Visible": False,
                    "filter_1": 0,
                    "filter_2": 1000,
                    "filter_type1": "Gaussian",
                    "filter_type2": "Uniform",
                    "operator": "-",
                    "Ch_name": "CD20",
                    "normalize": 0,
                },
                "CD3-Filter": {
                    "Visible": False,
                    "filter_1": 0,
                    "filter_2": 1000,
                    "filter_type1": "Gaussian",
                    "filter_type2": "Uniform",
                    "operator": "-",
                    "Ch_name": "CD3",
                    "normalize": 0,
                },
                "CD68-Filter": {
                    "Visible": False,
                    "filter_1": 0,
                    "filter_2": 1000,
                    "filter_type1": "Gaussian",
                    "filter_type2": "Uniform",
                    "operator": "-",
                    "Ch_name": "CD68",
                    "normalize": 0,
                },
                "CD56-Filter": {
                    "Visible": False,
                    "filter_1": 0,
                    "filter_2": 1000,
                    "filter_type1": "Gaussian",
                    "filter_type2": "Uniform",
                    "operator": "-",
                    "Ch_name": "CD56",
                    "normalize": 0,
                },
                "CK-Filter": {
                    "Visible": False,
                    "filter_1": 0,
                    "filter_2": 1000,
                    "filter_type1": "Gaussian",
                    "filter_type2": "Uniform",
                    "operator": "-",
                    "Ch_name": "CK",
                    "normalize": 0,
                },
                "Tumor": {
                    "thres": np.array(
                        [
                            [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
                            [
                                np.inf,
                                np.inf,
                                np.inf,
                                np.inf,
                                np.inf,
                                np.inf,
                                np.inf,
                                np.inf,
                                np.inf,
                            ],
                        ]
                    ),
                    "adaptive_size": np.array(
                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
                    ),
                    "ForeLimits": [5000, np.inf],
                    "HoleLimits": [5000, np.inf],
                    "ExcludeEdges": False,
                },
                "DAPI": {
                    "thres": "Stardist_2D_versatile_fluo",
                    "ch_used": "DAPI",
                    "n_ch_used": 0,
                    "class": "Nuc",
                    "NucLimits": "Stardist_2D_versatile_fluo",
                    "CellLimits": np.inf,
                    "CellMeth": "Extend Cell Area To:",
                    "d_prob_thres": 0.0,
                    "d_nms_thres": 0.0,
                },
            },
            "Phenotypes": {
                "CD8+": {
                    "x_axis0": "Linear",
                    "x_axis1": "Nucleus",
                    "x_axis2": "Geometry",
                    "x_axis3": "Area",
                    "y_axis0": "Log",
                    "y_axis1": "Cell",
                    "y_axis2": "CD8",
                    "y_axis3": "Mean Intensity",
                    "positive_area": [],
                    "hist_limits": np.array([[0.0, 0.4], [np.inf, np.inf]]),
                },
                "CD20+": {
                    "x_axis0": "Linear",
                    "x_axis1": "Nucleus",
                    "x_axis2": "Geometry",
                    "x_axis3": "Area",
                    "y_axis0": "Log",
                    "y_axis1": "Cell",
                    "y_axis2": "CD20",
                    "y_axis3": "Mean Intensity",
                    "positive_area": [],
                    "hist_limits": np.array([[0.0, 0.7], [np.inf, np.inf]]),
                },
                "CD3+": {
                    "x_axis0": "Linear",
                    "x_axis1": "Nucleus",
                    "x_axis2": "Geometry",
                    "x_axis3": "Area",
                    "y_axis0": "Log",
                    "y_axis1": "Cell",
                    "y_axis2": "CD3",
                    "y_axis3": "Mean Intensity",
                    "positive_area": [],
                    "hist_limits": np.array([[0.0, 0.3], [np.inf, np.inf]]),
                },
                "CD68+": {
                    "x_axis0": "Linear",
                    "x_axis1": "Nucleus",
                    "x_axis2": "Geometry",
                    "x_axis3": "Area",
                    "y_axis0": "Log",
                    "y_axis1": "Cell",
                    "y_axis2": "CD68",
                    "y_axis3": "Mean Intensity",
                    "positive_area": [],
                    "hist_limits": np.array([[0.0, 1.0], [np.inf, np.inf]]),
                },
                "CD56+": {
                    "x_axis0": "Linear",
                    "x_axis1": "Nucleus",
                    "x_axis2": "Geometry",
                    "x_axis3": "Area",
                    "y_axis0": "Log",
                    "y_axis1": "Cell",
                    "y_axis2": "CD56",
                    "y_axis3": "Mean Intensity",
                    "positive_area": [],
                    "hist_limits": np.array([[0.0, 0.7], [np.inf, np.inf]]),
                },
                "CK+": {
                    "x_axis0": "Linear",
                    "x_axis1": "Nucleus",
                    "x_axis2": "Geometry",
                    "x_axis3": "Area",
                    "y_axis0": "Log",
                    "y_axis1": "Cell",
                    "y_axis2": "CK",
                    "y_axis3": "Mean Intensity",
                    "positive_area": [],
                    "hist_limits": np.array([[0.0, 0.1], [np.inf, np.inf]]),
                },
            },
            "Foreground": {
                "thres": [
                    np.array([0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.0]),
                    np.array(
                        [
                            np.inf,
                            np.inf,
                            np.inf,
                            np.inf,
                            np.inf,
                            np.inf,
                            np.inf,
                            np.inf,
                            np.inf,
                        ]
                    ),
                ],
                "adaptive_size": np.array(
                    [1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 0]
                ),
                "ForeLimits": [5000, np.inf],
                "HoleLimits": [5000, np.inf],
                "ExcludeEdges": False,
            },
        }
        self.Analysis_like = self.activeImage
        QuickAnalysisLikeSure(self)

    if len(self.FileDictionary) == 0:
        popupmsg("Please first open an image file")
    else:
        Channel_pointers = self.Channel_pointers[self.activeImage][
            : self.n_channels[self.activeImage]
        ]
        if len(Channel_pointers) == 8:
            if False not in [
                i in Channel_pointers
                for i in ["CD3", "CD8", "CD20", "CD56", "CD68", "CK", "DAPI"]
            ]:
                popup2 = tkinter.Tk()
                popup2.wm_title("Are you sure?")
                label = tkinter.Label(
                    popup2, text="You are about to overwrite your current analysis"
                )
                label.pack(side="top", fill="x", pady=10)
                B1 = tkinter.Button(
                    popup2,
                    text="Go Ahead",
                    command=lambda: [DestroyTK(popup2), Apply_default_analysis_sure()],
                )
                B1.pack()
                B2 = tkinter.Button(
                    popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
                )
                B2.pack()
                popup2.mainloop()
            else:
                popup2 = tkinter.Tk()
                popup2.wm_title("Incorrect Channels!")
                label = tkinter.Label(
                    popup2,
                    text="The channels provided do not match the default analysis setting "
                    + "CD3, CD8, CD20, CD56, CD68, CK, DAPI, background. ",
                )
                label.pack(side="top", fill="x", pady=10)
                B2 = tkinter.Button(
                    popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
                )
                B2.pack()
                popup2.mainloop()
        else:
            popup2 = tkinter.Tk()
            popup2.wm_title("Incorrect Channels!")
            label = tkinter.Label(
                popup2,
                text="The channels provided do not match the default analysis setting "
                + "CD3, CD8, CD20, CD56, CD68, CK, DAPI, background. ",
            )
            label.pack(side="top", fill="x", pady=10)
            B2 = tkinter.Button(
                popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
            )
            B2.pack()
            popup2.mainloop()


def PhenotypeSelection(self):
    if "Tumor" in self.analyze_index[self.activeImage]:
        banned_seg_names = ["DAPI", "Tumor", "Stroma", "Tumor+", "Stroma+"]
    else:
        banned_seg_names = ["DAPI"]
    for i in self.Markers:
        if i != "DAPI":
            banned_seg_names.append(i)
        banned_seg_names.append(i + "-Filter")

    def RmvPheno(*a):
        def RmvSegSure(*a):
            [pop2, x] = popupmsg(
                "Your adjustment is expected to change"
                + " phenotyping. \nThe data is currently"
                + " being reanalyzed. Please hold.",
                False,
            )
            segName = self.SegName.get()
            analysis_params = self.analysis_params[self.activeImage].copy()
            if segName in analysis_params["Phenotypes"]:
                analysis_params["Phenotypes"].pop(segName)
            elif segName in analysis_params["Segments"]:
                analysis_params["Segments"].pop(segName)
            self.analysis_params[self.activeImage] = analysis_params.copy()
            analyze_index = self.analyze_index[self.activeImage]
            im_analyzed = self.im_analyzed[self.activeImage]
            im_analyzed.pop(analyze_index.index(segName))
            color_variable = self.color_variable[self.activeImage]
            Color_pointers = self.Color_pointers[self.activeImage]
            color_variable.pop(
                analyze_index.index(segName) + self.n_channels[self.activeImage]
            )
            Color_pointers.pop(
                analyze_index.index(segName) + self.n_channels[self.activeImage]
            )
            analyze_index.pop(analyze_index.index(segName))
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            self.color_variable[self.activeImage] = color_variable
            self.Color_pointers[self.activeImage] = Color_pointers
            self.remake_side_window()
            self.Analysis_like = self.activeImage
            QuickAnalysisLikeSure(self)
            DestroyTK(pop2)
            DestroyTK(self.popup)
            PhenotypeSelectionForReal()

        Color_pointers = self.Color_pointers[self.activeImage]
        n_channels = self.n_channels[self.activeImage]
        if len(Color_pointers) > n_channels:
            analyze_index = [
                i for i in self.analysis_params[self.activeImage]["Phenotypes"].keys()
            ]
            popup2 = tkinter.Tk()
            popup2.wm_title("Remove Segment")
            label = tkinter.Label(
                popup2, text="Which phenotype would you like to remove?"
            )
            label.pack(side="top", fill="x", pady=10)
            internal_windows = tkinter.Frame(popup2, width=200, height=20)
            internal_windows.pack(side=tkinter.TOP)
            self.SegName = tkinter.StringVar(internal_windows)
            self.SegName.set(analyze_index[0])
            w = tkinter.OptionMenu(internal_windows, self.SegName, *analyze_index)
            w.config(width=20)
            w.pack(side=tkinter.LEFT)
            B1 = tkinter.Button(
                popup2, text="Remove", command=lambda: [DestroyTK(popup2), RmvSegSure()]
            )
            B1.pack()
            B2 = tkinter.Button(
                popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
            )
            B2.pack()
            popup2.mainloop()

    def PhenotypeSelectionForReal(*a):
        def change_widget(cursor_on_off):
            if cursor_on_off == "cursor on":
                multiwidget.visible = True
                multiwidget.connect()
            elif cursor_on_off == "cursor off":
                multiwidget.visible = False
                multiwidget.disconnect()
            update_pheno()

        def change_population(show_pop_on):
            if show_pop_on == "show pop":
                self.show_selected_pop = True
            elif show_pop_on == "hide pop":
                self.show_selected_pop = False
            update_population_image()

        self.tracing_on = True
        self.show_selected_pop = False
        self.selected_points = []
        if len(self.Cell_props[self.activeImage]) == 0:
            Get_cell_props(self)
        cell_props = self.Cell_props[self.activeImage]
        channel_variable = self.channel_variable[self.activeImage]
        Channel_pointers = self.Channel_pointers[self.activeImage].copy()
        n_channels = self.n_channels[self.activeImage]
        for i in range(n_channels):
            Channel_pointers[i] = channel_variable[i].get()
        analysis_params = self.analysis_params[self.activeImage].copy()
        Segment_keys = list(analysis_params["Segments"].keys())
        for SegName in Segment_keys:
            if "filter_1" in analysis_params["Segments"][SegName]:
                if analysis_params["Segments"][SegName]["Visible"]:
                    Channel_pointers.append(SegName)
            if "Speck" in analysis_params["Segments"][SegName]:
                if analysis_params["Segments"][SegName]["Speck"] == 1:
                    Channel_pointers.append(SegName + "-Speck")
                elif analysis_params["Segments"][SegName]["Speck"] == 2:
                    Channel_pointers.append(SegName + "-Mask")
        popup = tkinter.Tk()
        popup.wm_title("Phenotype Selection")
        self.popup = popup
        label = ttkinter.Label(
            popup,
            text="Phenotype selection for file :\n"
            + self.FileDictionary[self.activeImage],
        )
        label.pack(side="bottom", fill="x", pady=10)
        self.popup_statusBar = label
        left_windows = tkinter.Frame(popup, width=440, height=440)
        left_windows.pack(side=tkinter.LEFT, anchor="w")
        upper_windows = tkinter.Frame(left_windows, width=440, height=400)
        upper_windows.pack(side=tkinter.TOP, anchor="w")
        internal_windows3 = tkinter.Frame(upper_windows, width=40, height=400)
        internal_windows3.pack(side=tkinter.LEFT, anchor="w")
        internal_windows = tkinter.Frame(upper_windows, width=400, height=400)
        internal_windows.pack(side=tkinter.LEFT, anchor="ne")
        internal_windows2 = tkinter.Frame(left_windows, width=400, height=40)
        internal_windows2.pack(side=tkinter.BOTTOM, anchor="s")
        internal_windows4 = tkinter.Frame(popup, width=40, height=400)
        internal_windows4.pack(side=tkinter.LEFT)

        toolbar = tkinter.Frame(internal_windows4)
        self.popList = ["New"]
        analysis_params = self.analysis_params[self.activeImage].copy()
        for i in analysis_params["Phenotypes"].keys():
            self.popList.append(i)
        pheno_var = tkinter.StringVar(internal_windows4)
        pheno_var.set(self.popList[0])
        pheno_var.trace("w", DefPhenoChanged)
        popSelectionDropdown = tkinter.OptionMenu(toolbar, pheno_var, *self.popList)
        popSelectionDropdown.config(width=20)
        popSelectionDropdown.pack(side=tkinter.TOP, padx=2, pady=2)
        addButton = ttkinter.Button(toolbar, text="Add Phenotype", command=addPop)
        addButton.pack(side=tkinter.TOP, padx=2, pady=2)
        addButton.config(width=20)
        resetButton = ttkinter.Button(toolbar, text="Reset Selection", command=resetPop)
        resetButton.pack(side=tkinter.TOP, padx=2, pady=2)
        resetButton.config(width=20)
        registerButton = ttkinter.Button(
            toolbar, text="Save Selection", command=SavePop
        )
        registerButton.pack(side=tkinter.TOP, padx=2, pady=2)
        registerButton.config(width=20)
        removeButton = ttkinter.Button(
            toolbar, text="Remove Phenotype", command=RmvPheno
        )
        removeButton.pack(side=tkinter.TOP, padx=2, pady=2)
        removeButton.config(width=20)
        cancelButton = ttkinter.Button(toolbar, text="Quit", command=QuitPop)
        cancelButton.pack(side=tkinter.TOP, padx=2, pady=2)
        cancelButton.config(width=20)
        toolbar.pack(side=tkinter.TOP, fill=tkinter.X)

        scale_pointers = ["Linear", "Log"]
        x1_pointers = ["Nucleus", "Cell"]
        if "Cytoplasm Area" in cell_props:
            x1_pointers = ["Nucleus", "Cytoplasm", "Cell"]
        x2_pointers = np.hstack(["Geometry", Channel_pointers])
        x3_pointers = [
            "Area",
            "Perimeter",
            "Eccentricity",
            "Equivalent Diameter",
            "Major Axis Length",
            "Minor Axis Length",
            "Orientation",
        ]
        x_variable0 = tkinter.StringVar(internal_windows2)
        x_variable0.set(scale_pointers[0])
        x_variable0.trace("w", PhenoChanged)
        x_var_pointer0 = tkinter.OptionMenu(
            internal_windows2, x_variable0, *scale_pointers
        )
        x_var_pointer0.config(width=10)
        x_var_pointer0.pack(side=tkinter.LEFT)
        x_variable1 = tkinter.StringVar(internal_windows2)
        x_variable1.set(x1_pointers[0])
        x_variable1.trace("w", PhenoChanged)
        x_var_pointer1 = tkinter.OptionMenu(
            internal_windows2, x_variable1, *x1_pointers
        )
        x_var_pointer1.config(width=20)
        x_var_pointer1.pack(side=tkinter.LEFT)
        x_variable2 = tkinter.StringVar(internal_windows2)
        x_variable2.set(x2_pointers[0])
        x_variable2.trace("w", PhenoChanged)
        x_var_pointer2 = tkinter.OptionMenu(
            internal_windows2, x_variable2, *x2_pointers
        )
        x_var_pointer2.config(width=20)
        x_var_pointer2.pack(side=tkinter.LEFT)
        x_variable3 = tkinter.StringVar(internal_windows2)
        x_variable3.set(x3_pointers[0])
        x_variable3.trace("w", PhenoChanged)
        x_var_pointer3 = tkinter.OptionMenu(
            internal_windows2, x_variable3, *x3_pointers
        )
        x_var_pointer3.config(width=20)
        x_var_pointer3.pack(side=tkinter.LEFT)
        y_variable0 = tkinter.StringVar(internal_windows3)
        y_variable0.set(scale_pointers[0])
        y_variable0.trace("w", PhenoChanged)
        y_var_pointer0 = tkinter.OptionMenu(
            internal_windows3, y_variable0, *scale_pointers
        )
        y_var_pointer0.config(width=10)
        y_var_pointer0.pack(side=tkinter.TOP)
        y_variable1 = tkinter.StringVar(internal_windows3)
        y_variable1.set(x1_pointers[0])
        y_variable1.trace("w", PhenoChanged)
        y_var_pointer1 = tkinter.OptionMenu(
            internal_windows3, y_variable1, *x1_pointers
        )
        y_var_pointer1.config(width=10)
        y_var_pointer1.pack(side=tkinter.TOP)
        y_variable2 = tkinter.StringVar(internal_windows3)
        y_variable2.set(x2_pointers[0])
        y_variable2.trace("w", PhenoChanged)
        y_var_pointer2 = tkinter.OptionMenu(
            internal_windows3, y_variable2, *x2_pointers
        )
        y_var_pointer2.config(width=10)
        y_var_pointer2.pack(side=tkinter.TOP)
        y_variable3 = tkinter.StringVar(internal_windows3)
        y_variable3.set(x3_pointers[1])
        y_variable3.trace("w", PhenoChanged)
        y_var_pointer3 = tkinter.OptionMenu(
            internal_windows3, y_variable3, *x3_pointers
        )
        y_var_pointer3.config(width=10)
        y_var_pointer3.pack(side=tkinter.TOP)
        f2 = plt.Figure(figsize=(6, 6), dpi=100)
        f2.patch.set_visible(False)
        f2.subplots_adjust(
            left=0.1, bottom=0.1, right=0.92, top=0.92, wspace=0, hspace=0
        )
        ax2 = f2.gca()
        temp = Tk_Agg.FigureCanvasTkAgg(f2, master=internal_windows)
        image_canvas2 = temp
        image_canvas2.draw()
        image_canvas2.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
        image_canvas2._tkcanvas.pack(
            side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True
        )
        image_toolbar2 = NT2Tk(image_canvas2, internal_windows)
        image_toolbar2.update()
        ax2.clear()
        if x_variable2.get() == "Geometry":
            x_data = np.vstack(cell_props[x_variable1.get() + " " + x_variable3.get()])
        else:
            x_data = np.vstack(
                cell_props[x_variable1.get() + " Fluorescent " + x_variable3.get()]
            )[:, Channel_pointers.index(x_variable2.get())]
        if y_variable2.get() == "Geometry":
            y_data = np.vstack(cell_props[y_variable1.get() + " " + y_variable3.get()])
        else:
            y_data = np.vstack(
                cell_props[y_variable1.get() + " Fluorescent " + y_variable3.get()]
            )[:, Channel_pointers.index(y_variable2.get())]
        ax2.set_position([0.1, 0.1, 0.65, 0.65])
        axHistx = f2.add_axes([0.1, 0.77, 0.65, 0.15], sharex=ax2)
        axHisty = f2.add_axes([0.77, 0.1, 0.15, 0.65], sharey=ax2)
        axamp = f2.add_axes([0.2, 0.95, 0.2, 0.02], facecolor="lightgoldenrodyellow")
        axamp2 = f2.add_axes([0.8, 0.85, 0.18, 0.15], facecolor="lightgoldenrodyellow")
        axamp3 = f2.add_axes([0.8, 0.75, 0.18, 0.08], facecolor="lightgoldenrodyellow")
        axamp4 = f2.add_axes([0.6, 0.92, 0.18, 0.08], facecolor="lightgoldenrodyellow")

        axampy1 = f2.add_axes([0.03, 0.1, 0.05, 0.02], facecolor="lightgoldenrodyellow")
        axampy2 = f2.add_axes(
            [0.03, 0.75, 0.05, 0.02], facecolor="lightgoldenrodyellow"
        )
        axampx1 = f2.add_axes([0.1, 0.03, 0.05, 0.02], facecolor="lightgoldenrodyellow")
        axampx2 = f2.add_axes(
            [0.75, 0.03, 0.05, 0.02], facecolor="lightgoldenrodyellow"
        )
        self.xlim_1_slider = matplotlib.widgets.Slider(
            axampx1, "Xmin", -1.0, 1.0, valinit=0
        )
        self.xlim_2_slider = matplotlib.widgets.Slider(
            axampx2, "Xmax", -1.0, 1.0, valinit=0
        )
        self.ylim_1_slider = matplotlib.widgets.Slider(
            axampy1, "", -1.0, 1.0, valinit=0
        )
        self.ylim_2_slider = matplotlib.widgets.Slider(
            axampy2, "", -1.0, 1.0, valinit=0
        )
        self.xlim_1_slider.on_changed(update_pheno)
        self.xlim_2_slider.on_changed(update_pheno)
        self.ylim_1_slider.on_changed(update_pheno)
        self.ylim_2_slider.on_changed(update_pheno)

        self.size_slider = matplotlib.widgets.Slider(
            axamp, "Point Size", 0.1, 20.0, valinit=5
        )
        self.radio = matplotlib.widgets.RadioButtons(
            axamp2, ("scatter", "2D hist", "contour", "contourf", "pcolor")
        )
        self.radio.on_clicked(update_pheno)
        self.size_slider.on_changed(update_pheno)
        multiwidget = matplotlib.widgets.MultiCursor(
            f2.canvas,
            (ax2, axHistx, axHisty),
            color="r",
            lw=1,
            horizOn=True,
            vertOn=True,
        )

        cursor_on = matplotlib.widgets.RadioButtons(axamp3, ("cursor on", "cursor off"))
        show_pop_on = matplotlib.widgets.RadioButtons(axamp4, ("show pop", "hide pop"))
        self.Histx_spanner = matplotlib.widgets.SpanSelector(
            axHistx, axHistx_changed, "horizontal", useblit=True
        )
        self.Histy_spanner = matplotlib.widgets.SpanSelector(
            axHisty, axHisty_changed, "vertical", useblit=True
        )
        self.Histx_spanner.active = False
        self.Histy_spanner.active = False

        cursor_on.set_active(1)
        cursor_on.on_clicked(change_widget)
        show_pop_on.set_active(1)
        show_pop_on.on_clicked(change_population)
        self.axHistx = axHistx
        self.axHisty = axHisty
        self.x_data = x_data
        self.y_data = y_data
        ax2.autoscale(True)
        self.ax2 = ax2
        self.Pheno_x_variable0 = x_variable0
        self.Pheno_x_variable1 = x_variable1
        self.Pheno_x_variable2 = x_variable2
        self.Pheno_x_variable3 = x_variable3
        self.Pheno_y_variable0 = y_variable0
        self.Pheno_y_variable1 = y_variable1
        self.Pheno_y_variable2 = y_variable2
        self.Pheno_y_variable3 = y_variable3
        self.pheno_var = pheno_var
        self.popSelectionDropdown = popSelectionDropdown
        self.Pheno_x_var_pointer3 = x_var_pointer3
        self.Pheno_y_var_pointer3 = y_var_pointer3
        self.image_canvas2 = image_canvas2
        update_pheno()
        self.ROIPolygon = matplotlib.widgets.PolygonSelector(
            self.ax2,
            onPopSelect,
            lineprops=dict(color="r", linestyle="-", linewidth=1, alpha=0.5),
            markerprops=dict(marker="o", markersize=3, mec="r", mfc="r", alpha=0.5),
        )
        change_widget("cursor off")
        self.ROIPolygon.active = False
        self.ROI_path = []
        self.ROI_verts = []
        self.hist_spanner_limits = np.array([[0, 0], [np.inf, np.inf]])
        popup.mainloop()

    def update_population_image(*a):

        if self.show_selected_pop:
            self.a.clear()
            im_analyzed = self.im_analyzed[self.activeImage]
            analyze_index = self.analyze_index[self.activeImage]
            cell_props = self.Cell_props[self.activeImage]
            im_all_cells = im_analyzed[analyze_index.index("All Cells")].copy()
            im_selected_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            im_all_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            nucleus_centroids = np.uint32(
                np.round(cell_props["Nucleus Centroid"][:].tolist())
            )
            for i in range(len(cell_props["Nucleus Centroid"])):
                im_all_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
            for i in self.selected_points:
                im_selected_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
            im_selected_cells = (
                ndi.distance_transform_edt(im_selected_cells == 0)
                <= self.size_slider.val
            )
            im_2_display_new = self.im_2_display.copy() / 2
            im_temp = im_2_display_new[:, :, 0]
            im_temp[im_selected_cells > 0] = im_selected_cells[im_selected_cells > 0]
            im_all_cells[im_selected_cells > 0] = 0
            im_all_cells = (
                ndi.distance_transform_edt(im_all_cells == 0) <= self.size_slider.val
            )
            im_2_display_new[:, :, 0] = im_temp
            im_temp = im_2_display_new[:, :, 2]
            im_temp[im_all_cells > 0] = im_all_cells[im_all_cells > 0]
            im_2_display_new[:, :, 2] = im_temp
            self.a.imshow(im_2_display_new, aspect="equal")
            self.a.autoscale(False)
            self.a.axis("off")
            self.image_canvas.draw()
        else:
            self.a.clear()
            self.a.imshow(self.im_2_display, aspect="equal")
            self.a.autoscale(False)
            self.a.axis("off")
            self.image_canvas.draw()

    def update_pheno(*a, **k):
        Xmin_mod = self.xlim_1_slider.val
        Xmax_mod = self.xlim_2_slider.val
        Ymin_mod = self.ylim_1_slider.val
        Ymax_mod = self.ylim_2_slider.val
        amp = self.size_slider.val
        mask = self.selected_points
        plot_type = self.radio.value_selected
        axScatter = self.ax2
        x_data = np.squeeze(self.x_data)
        y_data = np.squeeze(self.y_data)
        n_bins = np.int32(500 / amp)
        if self.Pheno_x_variable0.get() == "Log":
            x_min = np.log10(max(0.0001, min(x_data)))
            x_max = np.log10(max(x_data))
            x_range = x_max - x_min
            x_min = x_min + x_range * Xmin_mod
            x_max = x_max + x_range * Xmax_mod
            x_edges = np.logspace(x_min, x_max, n_bins)
        else:
            x_min = 0
            x_max = max(x_data)
            x_range = x_max - x_min
            x_min = x_min + x_range * Xmin_mod
            x_max = x_max + x_range * Xmax_mod
            x_edges = np.linspace(x_min, x_max, n_bins)
        axScatter.set_xlim((min(x_edges), max(x_edges) * 1.2))
        if self.Pheno_y_variable0.get() == "Log":
            y_min = np.log10(max(0.0001, min(y_data)))
            y_max = np.log10(max(y_data))
            y_range = y_max - y_min
            y_min = y_min + y_range * Ymin_mod
            y_max = y_max + y_range * Ymax_mod
            y_edges = np.logspace(y_min, y_max, n_bins)
        else:
            y_min = 0
            y_max = max(y_data)
            y_range = y_max - y_min
            y_min = y_min + y_range * Ymin_mod
            y_max = y_max + y_range * Ymax_mod
            y_edges = np.linspace(y_min, y_max, n_bins)
        axScatter.set_ylim((min(y_edges), max(y_edges) * 1.2))
        axScatter.collections.clear()
        axScatter.images.clear()

        self.axHistx.patches.clear()
        self.axHisty.patches.clear()
        self.axHistx.hist(x_data, bins=x_edges, color="C0")
        self.axHisty.hist(y_data, bins=y_edges, orientation="horizontal", color="C0")
        mask_defined = np.size(mask) > 0
        if mask_defined:
            self.axHistx.hist(x_data[mask], bins=x_edges, color="C1")
            self.axHisty.hist(
                y_data[mask], bins=y_edges, orientation="horizontal", color="C1"
            )
        if plot_type == "scatter":
            scattered_plot = axScatter.scatter(x_data, y_data, c="C0")
            scattered_plot.set_sizes([amp])
            if mask_defined:
                scattered_plot = axScatter.scatter(x_data[mask], y_data[mask], c="C1")
                scattered_plot.set_sizes([amp])
        if plot_type == "2D hist":
            if mask_defined:
                axScatter.hist2d(x_data[mask], y_data[mask], bins=n_bins)
                axScatter.hist2d(x_data, y_data, bins=n_bins, alpha=0.5)
            else:
                axScatter.hist2d(x_data, y_data, bins=n_bins)
            #            axScatter.hist2d(x_data, y_data, bins=n_bins)
            axScatter.set_xlim((min(x_edges), max(x_edges) * 1.2))
            axScatter.set_ylim((min(y_edges), max(y_edges) * 1.2))
        #            im2.set_data(xcenters2, ycenters2, H2)
        #            im2.set_visible(True)
        #            im2.autoscale()
        if plot_type == "contour":
            H2, xedges2, yedges2 = np.histogram2d(
                x_data, y_data, bins=[x_edges, y_edges]
            )
            H2 = H2.T
            xcenters2 = (xedges2[:-1] + xedges2[1:]) / 2
            ycenters2 = (yedges2[:-1] + yedges2[1:]) / 2
            X, Y = np.meshgrid(xcenters2, ycenters2)
            if mask_defined:
                H, xedges2, yedges2 = np.histogram2d(
                    x_data[mask], y_data[mask], bins=[x_edges, y_edges]
                )
                H = H.T
                axScatter.contour(X, Y, H, cmap="RdBu_r")
                axScatter.contour(X, Y, H2, cmap="RdBu_r", alpha=0.2)
            else:
                axScatter.contour(X, Y, H2, cmap="RdBu_r")
            axScatter.set_xlim((min(x_edges), max(x_edges) * 1.2))
            axScatter.set_ylim((min(y_edges), max(y_edges) * 1.2))
        if plot_type == "contourf":
            H2, xedges2, yedges2 = np.histogram2d(
                x_data, y_data, bins=[x_edges, y_edges]
            )
            H2 = H2.T
            xcenters2 = (xedges2[:-1] + xedges2[1:]) / 2
            ycenters2 = (yedges2[:-1] + yedges2[1:]) / 2
            X, Y = np.meshgrid(xcenters2, ycenters2)
            if mask_defined:
                H, xedges2, yedges2 = np.histogram2d(
                    x_data[mask], y_data[mask], bins=[x_edges, y_edges]
                )
                H = H.T
                axScatter.contourf(X, Y, H, cmap="RdBu_r")
                axScatter.contourf(X, Y, H2, cmap="RdBu_r", alpha=0.2)
            else:
                axScatter.contourf(X, Y, H2, cmap="RdBu_r")
            axScatter.set_xlim((min(x_edges), max(x_edges) * 1.2))
            axScatter.set_ylim((min(y_edges), max(y_edges) * 1.2))
        if plot_type == "pcolor":
            H2, xedges2, yedges2 = np.histogram2d(
                x_data, y_data, bins=[x_edges, y_edges]
            )
            H2 = H2.T
            xcenters2 = (xedges2[:-1] + xedges2[1:]) / 2
            ycenters2 = (yedges2[:-1] + yedges2[1:]) / 2
            X, Y = np.meshgrid(xcenters2, ycenters2)
            if mask_defined:
                H, xedges2, yedges2 = np.histogram2d(
                    x_data[mask], y_data[mask], bins=[x_edges, y_edges]
                )
                H = H.T
                axScatter.pcolormesh(X, Y, H, cmap="RdBu_r")
                axScatter.pcolormesh(X, Y, H2, cmap="RdBu_r", alpha=0.2)
            else:
                axScatter.pcolormesh(X, Y, H2, cmap="RdBu_r")
            axScatter.set_xlim((min(x_edges), max(x_edges) * 1.2))
            axScatter.set_ylim((min(y_edges), max(y_edges) * 1.2))
        axScatter.figure.canvas.draw_idle()
        self.axHistx.set_xlim(axScatter.get_xlim())
        self.axHisty.set_ylim(axScatter.get_ylim())
        self.axHistx.xaxis.set_tick_params(labelbottom=False)
        self.axHisty.yaxis.set_tick_params(labelleft=False)
        self.axHistx.xaxis.set_tick_params(which="minor", labelbottom=False)
        self.axHisty.yaxis.set_tick_params(which="minor", labelleft=False)
        max_y = 0
        for i in self.axHistx.patches:
            max_y = max(max_y, i.get_height())
        self.axHistx.set_ylim((0, max_y * 1.1))
        max_x = 0
        for i in self.axHisty.patches:
            max_x = max(max_x, i.get_width())
        self.axHisty.set_xlim((0, max_x * 1.1))
        self.image_canvas2.draw()
        if self.show_selected_pop:
            update_population_image()

    def DefPhenoChanged(*a, **k):
        analysis_params = self.analysis_params[self.activeImage].copy()
        segName = self.pheno_var.get()
        if segName == "New":
            resetPop()
        else:
            resetPop()
            self.tracing_on = False
            self.Pheno_x_variable0.set(
                analysis_params["Phenotypes"][segName]["x_axis0"]
            )
            self.Pheno_x_variable1.set(
                analysis_params["Phenotypes"][segName]["x_axis1"]
            )
            self.Pheno_x_variable2.set(
                analysis_params["Phenotypes"][segName]["x_axis2"]
            )
            self.Pheno_x_variable3.set(
                analysis_params["Phenotypes"][segName]["x_axis3"]
            )
            self.Pheno_y_variable0.set(
                analysis_params["Phenotypes"][segName]["y_axis0"]
            )
            self.Pheno_y_variable1.set(
                analysis_params["Phenotypes"][segName]["y_axis1"]
            )
            self.Pheno_y_variable2.set(
                analysis_params["Phenotypes"][segName]["y_axis2"]
            )
            self.Pheno_y_variable3.set(
                analysis_params["Phenotypes"][segName]["y_axis3"]
            )
            self.tracing_on = True
            PhenoChanged()
            self.ROI_verts = analysis_params["Phenotypes"][segName]["positive_area"]
            self.hist_spanner_limits = analysis_params["Phenotypes"][segName][
                "hist_limits"
            ].copy()
            cell_props = self.Cell_props[self.activeImage]
            show_data = np.array(cell_props["Show Data"])
            points = np.transpose((self.x_data.ravel(), self.y_data.ravel()))
            self.Histx_spanner.active = True
            self.Histy_spanner.active = True
            self.ROIPolygon.active = True
            self.ROIPolygon.visible = True
            self.image_canvas2.get_tk_widget().focus_force()
            if np.size(self.ROI_verts) > 0:
                self.ROI_path = matplotlib.path.Path(self.ROI_verts)
                self.ROIPolygon._xs = np.append(
                    self.ROI_path.vertices[:, 0], self.ROI_path.vertices[0, 0]
                )
                self.ROIPolygon._ys = np.append(
                    self.ROI_path.vertices[:, 1], self.ROI_path.vertices[0, 1]
                )
                self.ROIPolygon._polygon_completed = True
                self.ROIPolygon._draw_polygon()
                mask = self.ROI_path.contains_points(points)
                mask = mask & (show_data > 0)
                mask = np.nonzero(mask)[0]
            else:
                self.ROI_path = []
                mask = (points[:, 0] * 0) == 0
                if self.hist_spanner_limits[0, 0] > 0:
                    mask = (mask) & (points[:, 0] > self.hist_spanner_limits[0, 0])
                if self.hist_spanner_limits[1, 0] < np.inf:
                    mask = (mask) & (points[:, 0] < self.hist_spanner_limits[1, 0])
                if self.hist_spanner_limits[0, 1] > 0:
                    mask = (mask) & (points[:, 1] > self.hist_spanner_limits[0, 1])
                if self.hist_spanner_limits[1, 1] < np.inf:
                    mask = (mask) & (points[:, 1] < self.hist_spanner_limits[1, 1])
                mask = mask & (show_data > 0)
                mask = np.nonzero(mask)[0]
            self.selected_points = mask
        update_pheno()
        addPop()

    def PhenoChanged(*a, **k):
        if self.tracing_on:
            PhenoChanged_do()
        else:
            pass

    def PhenoChanged_do(*a):
        self.selected_points = []
        ax2 = self.ax2
        cell_props = self.Cell_props[self.activeImage]
        channel_variable = self.channel_variable[self.activeImage]
        Channel_pointers = self.Channel_pointers[self.activeImage].copy()
        n_channels = self.n_channels[self.activeImage]
        x_variable0 = self.Pheno_x_variable0
        x_variable1 = self.Pheno_x_variable1
        x_variable2 = self.Pheno_x_variable2
        x_variable3 = self.Pheno_x_variable3
        y_variable0 = self.Pheno_y_variable0
        y_variable1 = self.Pheno_y_variable1
        y_variable2 = self.Pheno_y_variable2
        y_variable3 = self.Pheno_y_variable3
        x_var_pointer3 = self.Pheno_x_var_pointer3
        y_var_pointer3 = self.Pheno_y_var_pointer3
        x3_pointers = [
            "Area",
            "Perimeter",
            "Eccentricity",
            "Equivalent Diameter",
            "Major Axis Length",
            "Minor Axis Length",
            "Orientation",
        ]
        x4_pointers = [
            "Mean Intensity",
            "Maximum Intensity",
            "Minimum Intensity",
            "Total Intensity",
            "STD Intensity",
        ]
        for i in range(n_channels):
            Channel_pointers[i] = channel_variable[i].get()
        analysis_params = self.analysis_params[self.activeImage].copy()
        Segment_keys = list(analysis_params["Segments"].keys())
        for SegName in Segment_keys:
            if "filter_1" in analysis_params["Segments"][SegName]:
                if analysis_params["Segments"][SegName]["Visible"]:
                    Channel_pointers.append(SegName)
            if "Speck" in analysis_params["Segments"][SegName]:
                if analysis_params["Segments"][SegName]["Speck"] == 1:
                    Channel_pointers.append(SegName + "-Speck")
                if analysis_params["Segments"][SegName]["Speck"] == 2:
                    Channel_pointers.append(SegName + "-Mask")
        #        ax2.clear()
        if x_variable2.get() == "Geometry":
            if x_variable3.get() in x4_pointers:
                x_variable3.set(x3_pointers[0])
                x_var_pointer3["menu"].delete(0, "end")
                for label_option in x3_pointers:
                    x_var_pointer3["menu"].add_command(
                        label=label_option,
                        command=lambda label_option2=label_option: x_variable3.set(
                            label_option2
                        ),
                    )
            x_data = np.vstack(cell_props[x_variable1.get() + " " + x_variable3.get()])
        else:
            if x_variable3.get() in x3_pointers:
                x_variable3.set(x4_pointers[0])
                x_var_pointer3["menu"].delete(0, "end")
                for label_option in x4_pointers:
                    x_var_pointer3["menu"].add_command(
                        label=label_option,
                        command=lambda label_option2=label_option: x_variable3.set(
                            label_option2
                        ),
                    )
            x_data = np.vstack(
                cell_props[x_variable1.get() + " Fluorescent " + x_variable3.get()]
            )[:, Channel_pointers.index(x_variable2.get())]
        if y_variable2.get() == "Geometry":
            if y_variable3.get() in x4_pointers:
                y_variable3.set(x3_pointers[0])
                y_var_pointer3["menu"].delete(0, "end")
                for label_option in x3_pointers:
                    y_var_pointer3["menu"].add_command(
                        label=label_option,
                        command=lambda label_option2=label_option: y_variable3.set(
                            label_option2
                        ),
                    )
            y_data = np.vstack(cell_props[y_variable1.get() + " " + y_variable3.get()])
        else:
            if y_variable3.get() in x3_pointers:
                y_variable3.set(x4_pointers[0])
                y_var_pointer3["menu"].delete(0, "end")
                for label_option in x4_pointers:
                    y_var_pointer3["menu"].add_command(
                        label=label_option,
                        command=lambda label_option2=label_option: y_variable3.set(
                            label_option2
                        ),
                    )
            y_data = np.vstack(
                cell_props[y_variable1.get() + " Fluorescent " + y_variable3.get()]
            )[:, Channel_pointers.index(y_variable2.get())]
        ax2.set_xscale(x_variable0.get())
        ax2.set_yscale(y_variable0.get())
        self.x_data = x_data
        self.y_data = y_data
        update_pheno()

    #        ax2.autoscale(True)
    #        self.image_canvas2.draw()

    def addPop(*a):
        t = (
            "Select points in the figure by enclosing them within a "
            + "polygon. Press the 'esc' key to start a new polygon. \n"
            + "Try holding the 'shift' key to move all of the vertices. "
            + "Try holding the 'ctrl' key to move a single vertex."
        )
        self.popup_statusBar.config(text=t)
        self.Histx_spanner.active = True
        self.Histy_spanner.active = True
        self.ROIPolygon.active = True
        self.ROIPolygon.visible = True
        self.image_canvas2.get_tk_widget().focus_force()
        if self.showPopmessage == 1:
            self.showPopmessage = 0
            popupmsg(t)

    def axHisty_changed(*b):
        hist_limits = self.hist_spanner_limits
        a = np.array(b)
        points = np.transpose((self.x_data.ravel(), self.y_data.ravel()))
        if a[0] == a[1]:
            a[1] = np.inf
        elif a[1] > np.max(points[:, 1]):
            a[1] = np.inf
        hist_limits[:, 1] = a
        cell_props = self.Cell_props[self.activeImage]
        show_data = np.array(cell_props["Show Data"])
        mask = (
            (points[:, 1] > hist_limits[0, 1])
            & (points[:, 1] < hist_limits[1, 1])
            & (points[:, 0] > hist_limits[0, 0])
            & (points[:, 0] < hist_limits[1, 0])
        )
        mask = mask & (show_data > 0)
        mask = np.nonzero(mask)[0]
        self.selected_points = mask
        update_pheno()
        self.ROI_path = []
        self.ROI_verts = []
        self.hist_spanner_limits = hist_limits

    def axHistx_changed(*b):
        hist_limits = self.hist_spanner_limits
        a = np.array(b)
        points = np.transpose((self.x_data.ravel(), self.y_data.ravel()))
        if a[0] == a[1]:
            a[1] = np.inf
        elif a[1] > np.max(points[:, 0]):
            a[1] = np.inf
        hist_limits[:, 0] = a
        cell_props = self.Cell_props[self.activeImage]
        show_data = np.array(cell_props["Show Data"])
        mask = (
            (points[:, 1] > hist_limits[0, 1])
            & (points[:, 1] < hist_limits[1, 1])
            & (points[:, 0] > hist_limits[0, 0])
            & (points[:, 0] < hist_limits[1, 0])
        )
        mask = mask & (show_data > 0)
        mask = np.nonzero(mask)[0]
        self.selected_points = mask
        update_pheno()
        self.ROI_path = []
        self.ROI_verts = []
        self.hist_spanner_limits = hist_limits

    def onPopSelect(verts, *a):
        cell_props = self.Cell_props[self.activeImage]
        show_data = np.array(cell_props["Show Data"])
        ROI_path = matplotlib.path.Path(verts)
        points = np.transpose((self.x_data.ravel(), self.y_data.ravel()))
        mask = ROI_path.contains_points(points)
        mask = mask & (show_data > 0)
        mask = np.nonzero(mask)[0]
        self.ROI_path = ROI_path
        self.ROI_verts = verts
        self.hist_spanner_limits = np.array([[0, 0], [np.inf, np.inf]])
        self.selected_points = mask
        update_pheno()

    def resetPop(*a):
        cell_props = self.Cell_props[self.activeImage]
        cell_props["Show Data"] = 1
        self.Histx_spanner.active = False
        self.Histy_spanner.active = False
        self.ROIPolygon.active = False
        #        self.ROIPolygon.visible = False
        self.ROIPolygon._xs, self.ROIPolygon._ys = [0], [0]
        self.ROIPolygon._polygon_completed = False
        #        ax2 = self.ax2
        #        ax2.clear()
        #        ax2.plot(self.x_data, self.y_data, '.')
        #        ax2.set_xscale(self.Pheno_x_variable0.get())
        #        ax2.set_yscale(self.Pheno_y_variable0.get())
        #        ax2.autoscale(True)
        #        self.image_canvas2.draw()
        self.selected_points = []
        self.ROI_path = []
        self.ROI_verts = []
        self.hist_spanner_limits = np.array([[0, 0], [np.inf, np.inf]])
        update_pheno()
        self.Cell_props[self.activeImage] = cell_props
        self.image_canvas2.draw()

    def SavePop(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Add Phenotype")
        label = ttkinter.Label(popup2, text="How would you like to name the phenotype?")
        label.pack(side="top", fill="x", pady=10)
        labelButton = tkinter.Entry(popup2)
        segName = self.pheno_var.get()
        if segName != "New":
            labelButton.insert(0, segName)
        self.SegName = labelButton
        labelButton.pack()
        B1 = ttkinter.Button(popup2, text="Okay", command=lambda: [SavePopSure(popup2)])
        B1.pack()
        B2 = ttkinter.Button(
            popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
        )
        B2.pack()
        popup2.mainloop()

    def SavePopSure(popup2, *a):
        segName = self.SegName.get()
        cell_props = self.Cell_props[self.activeImage]
        if segName in banned_seg_names:
            popup3 = tkinter.Tk()
            popup3.wm_title("Banned name")
            label = tkinter.Label(
                popup3,
                text=(
                    segName
                    + " is a reserved name and you"
                    + "\cannot give that name to your phenotype"
                ),
            )
            label.pack(side="top", fill="x", pady=10)
            B2 = tkinter.Button(
                popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
            )
            B2.pack()
            popup3.mainloop()
        elif segName in ["All", "all"]:
            popup3 = tkinter.Tk()
            popup3.wm_title("Invalid Entry")
            label = ttkinter.Label(popup3, text="You cannot name your Phenotype All.\n")
            label.pack(side="top", fill="x", pady=10)
            B2 = ttkinter.Button(
                popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
            )
            B2.pack()
            popup3.mainloop()
        elif segName in np.unique(np.hstack(cell_props["Phenotypes"][:])):
            popup3 = tkinter.Tk()
            popup3.wm_title("Phenotype Exists")
            label = ttkinter.Label(
                popup3,
                text="A phenotype with the same name exists."
                + "\nwould you like to overwrite?",
            )
            label.pack(side="top", fill="x", pady=10)
            B1 = ttkinter.Button(
                popup3,
                text="Okay",
                command=lambda: [
                    DestroyTK(popup3),
                    SavePopSureSure(),
                    DestroyTK(popup2),
                ],
            )
            B1.pack()
            B2 = ttkinter.Button(
                popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
            )
            B2.pack()
            popup3.mainloop()
        else:
            SavePopSureSure()
            DestroyTK(popup2)

    def SavePopSureSure(*a):
        cell_props = self.Cell_props[self.activeImage]
        segName = self.SegName.get()
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        im_all_cells = im_analyzed[analyze_index.index("All Cells")]
        pheno_list = cell_props["Phenotypes"][:].tolist()
        nucleus_centroids = np.uint32(
            np.round(cell_props["Nucleus Centroid"][:].tolist())
        )
        im_selected_cells = np.zeros(
            (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
        )
        if segName in np.unique(np.hstack(pheno_list)):
            for i in cell_props.index:
                if segName in pheno_list[i - 1]:
                    pheno_list[i - 1].remove(segName)
        for i in self.selected_points:
            pheno_list[i].append(segName)
            im_selected_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
        cell_props["Phenotypes"] = pheno_list
        self.Cell_props[self.activeImage] = cell_props
        im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
        if segName in analyze_index:
            im_analyzed[analyze_index.index(segName)] = im_selected_cells
            self.im_analyzed[self.activeImage] = im_analyzed
        else:
            im_analyzed.append(im_selected_cells)
            analyze_index.append(segName)
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            self.remake_side_window()
        analysis_params = self.analysis_params[self.activeImage].copy()
        if segName in analysis_params["Phenotypes"]:
            analysis_params["Phenotypes"].pop(segName)
        else:
            self.popList.append(segName)
            self.popSelectionDropdown["menu"].add_command(
                label=segName, command=tkinter._setit(self.pheno_var, segName)
            )
        analysis_params["Phenotypes"][segName] = {
            "x_axis0": self.Pheno_x_variable0.get(),
            "x_axis1": self.Pheno_x_variable1.get(),
            "x_axis2": self.Pheno_x_variable2.get(),
            "x_axis3": self.Pheno_x_variable3.get(),
            "y_axis0": self.Pheno_y_variable0.get(),
            "y_axis1": self.Pheno_y_variable1.get(),
            "y_axis2": self.Pheno_y_variable2.get(),
            "y_axis3": self.Pheno_y_variable3.get(),
            "positive_area": self.ROI_verts.copy(),
            "hist_limits": self.hist_spanner_limits.copy(),
        }
        self.analysis_params[self.activeImage] = analysis_params.copy()

    def QuitPop(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = ttkinter.Label(popup2, text="You are about to exit Phenotype Selection")
        label.pack(side="top", fill="x", pady=10)
        B1 = ttkinter.Button(
            popup2,
            text="Go Ahead",
            command=lambda: [DestroyTK(self.popup), DestroyTK(popup2)],
        )
        B1.pack()
        B2 = ttkinter.Button(
            popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
        )
        B2.pack()
        popup2.mainloop()

    analyze_index = self.analyze_index[self.activeImage]
    if "DAPI" not in analyze_index:
        popup = tkinter.Tk()
        popup.wm_title("DAPI NOT DEFINED!")
        label = ttkinter.Label(
            popup,
            text="Phenotype Selection requires "
            + "a defined DAPI, Cell and Nucleus"
            + "segmentation",
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = ttkinter.Button(
            popup,
            text="Define now",
            command=lambda: [DestroyTK(popup), self.SegmentDetection()],
        )
        B1.pack(side=tkinter.LEFT, padx=2, pady=2)
        B2 = ttkinter.Button(popup, text="Go Back", command=lambda: [DestroyTK(popup)])
        B2.pack(side=tkinter.LEFT, padx=2, pady=2)
        popup.mainloop()
    elif "Cells" not in analyze_index:
        popup = tkinter.Tk()
        popup.wm_title("Cells NOT DEFINED!")
        label = ttkinter.Label(
            popup,
            text="Nucleus detection requires "
            + "a defined Cell and Nucleus segmentation",
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = ttkinter.Button(
            popup,
            text="Define now",
            command=lambda: [DestroyTK(popup), self.NucleusDetection()],
        )
        B1.pack(side=tkinter.LEFT, padx=2, pady=2)
        B2 = ttkinter.Button(popup, text="Go Back", command=lambda: [DestroyTK(popup)])
        B2.pack(side=tkinter.LEFT, padx=2, pady=2)
        popup.mainloop()
    elif "Nuclei" not in analyze_index:
        popup = tkinter.Tk()
        popup.wm_title("Nuclei NOT DEFINED!")
        label = ttkinter.Label(
            popup,
            text="Nucleus detection requires "
            + "a defined Cell and Nucleus segmentation",
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = ttkinter.Button(
            popup,
            text="Define now",
            command=lambda: [DestroyTK(popup), self.NucleusDetection()],
        )
        B1.pack(side=tkinter.LEFT, padx=2, pady=2)
        B2 = ttkinter.Button(popup, text="Go Back", command=lambda: [DestroyTK(popup)])
        B2.pack(side=tkinter.LEFT, padx=2, pady=2)
        popup.mainloop()
    else:
        PhenotypeSelectionForReal()


def DataAnalysis(self):
    def get_dists(locs1, locs2):
        dist_array = np.zeros((locs1.shape[0], locs2.shape[0]))
        for i in range(locs1.shape[0]):
            dist_array[i, :] = (
                (locs1[i, 0] - locs2[:, 0]) ** 2 + (locs1[i, 1] - locs2[:, 1]) ** 2
            ) ** 0.5
        return dist_array

    def do_monte_carlo(
        cell_dists, n_1, n_2, anal_type=False, n_trial=1000, n_cells=1, is_dist=True
    ):
        if is_dist:
            cell_dists[cell_dists < 0.001] = np.nan
            dist_all = []
            for i in range(n_trial):
                x_y = np.random.choice(range(cell_dists.shape[0]), n_1, replace=False)
                if anal_type:
                    x_y2 = x_y
                else:
                    x_y2 = np.random.choice(
                        range(cell_dists.shape[1]), n_2, replace=False
                    )
                dists_temp_orig = cell_dists[x_y, :][:, x_y2]
                if dists_temp_orig.shape[1] > n_cells:
                    min_dist = np.mean(
                        np.nanmean(
                            np.sort(dists_temp_orig, axis=1)[:, :n_cells], axis=1
                        )
                    )
                else:
                    min_dist = np.mean(np.nanmean(dists_temp_orig, axis=1))
                dist_all.append(min_dist)
            return np.mean(dist_all), np.std(dist_all)
        else:
            cell_dists[cell_dists == 0] = np.inf
            dist_all = []
            for i in range(n_trial):
                x_y = np.random.choice(range(cell_dists.shape[0]), n_1, replace=False)
                if anal_type:
                    x_y2 = x_y
                else:
                    x_y2 = np.random.choice(
                        range(cell_dists.shape[1]), n_2, replace=False
                    )
                dists_temp_orig = cell_dists[x_y, :][:, x_y2]
                n_cells = np.sum(dists_temp_orig <= n_cells)
                min_dist = n_cells / n_2
                dist_all.append(min_dist)
            return np.mean(dist_all), np.std(dist_all)

    def PerformNNA_Analysis(
        segment_var,
        pheno_cells,
        pheno_cells2,
        phenotypes,
        pheno_temp,
        NNA_relation,
        NNA_dist,
        pheno_temp2,
        locations,
        numbers,
        density,
        number_density,
        average_area,
        cell_props,
        cell_props2,
        all_dists,
    ):

        seg_available = np.unique(np.hstack(cell_props["Segments"][:]))
        if segment_var == "Anywhere":
            for segment_var_temp in seg_available:
                average_area.append(np.nan)
                all_cells = np.array(
                    [segment_var_temp in x for x in cell_props["Segments"]]
                )
                all_cells2 = np.array(
                    [segment_var_temp in x for x in cell_props2["Segments"]]
                )
                cells_selected1 = all_cells & pheno_cells
                cells_selected2 = all_cells2 & pheno_cells2
                cell1xy = np.array(cell_props["Cell Centroid"][cells_selected1])
                cell1xy = np.array([np.float32([b[1], b[0]]) for b in cell1xy])
                cell1Areas = np.array(cell_props["Cell Area"][cells_selected1])
                cell2xy = np.array(cell_props2["Cell Centroid"][cells_selected2])
                cell2xy = np.array([np.float32([b[1], b[0]]) for b in cell2xy])
                cell2Areas = np.array(cell_props2["Cell Area"][cells_selected2])
                min_dist = []
                num_den_temp = []
                area_den_temp = []
                if (len(cell1xy) == 0) | (len(cell2xy) == 0):
                    phenotypes.append(
                        pheno_temp
                        + " "
                        + NNA_relation
                        + " "
                        + NNA_dist
                        + " "
                        + pheno_temp2
                    )
                    locations.append(segment_var_temp)
                    numbers.append(np.nan)
                    number_density.append(np.nan)
                    density.append(np.nan)
                    continue
                if NNA_relation == "distance to":
                    n_cells = np.int32(NNA_dist)
                    if n_cells < 1:
                        continue
                    for i in range(len(cell1xy)):
                        dists_temp_orig = (
                            (cell1xy[i, 0] - cell2xy[:, 0]) ** 2
                            + (cell1xy[i, 1] - cell2xy[:, 1]) ** 2
                        ) ** 0.5
                        dists_temp = dists_temp_orig[dists_temp_orig != 0]
                        if len(dists_temp) > 0:
                            if len(dists_temp) > n_cells:
                                max_dist = np.sort(dists_temp)[n_cells - 1]
                                min_dist.append(np.mean(np.sort(dists_temp)[:n_cells]))
                                num_den_temp.append(n_cells / (PI * max_dist**2))
                                area_den_temp.append(
                                    np.sum(cell2Areas[dists_temp_orig <= max_dist])
                                    / (PI * max_dist**2)
                                )
                            else:
                                min_dist.append(np.mean(dists_temp))
                                max_dist = np.max(dists_temp)
                                num_den_temp.append(
                                    len(dists_temp) / (PI * max_dist**2)
                                )
                                area_den_temp.append(
                                    np.sum(cell2Areas[dists_temp_orig <= max_dist])
                                    / (PI * max_dist**2)
                                )
                    phenotypes.append(
                        pheno_temp
                        + " "
                        + NNA_relation
                        + " "
                        + NNA_dist
                        + " "
                        + pheno_temp2
                    )
                    locations.append(segment_var_temp)
                    if len(min_dist) > 0:
                        numbers.append(np.mean(min_dist))
                        number_density.append(np.mean(num_den_temp))
                        density.append(np.mean(area_den_temp))
                    else:
                        numbers.append(np.nan)
                        number_density.append(np.nan)
                        density.append(np.nan)

                elif NNA_relation == "within":
                    n_dist = np.float(NNA_dist)
                    if n_dist <= 0:
                        continue
                    for i in range(len(cell2xy)):
                        dists_temp_orig = (
                            (cell2xy[i, 0] - cell1xy[:, 0]) ** 2
                            + (cell2xy[i, 1] - cell1xy[:, 1]) ** 2
                        ) ** 0.5
                        dists_temp = dists_temp_orig[dists_temp_orig != 0]
                        if len(dists_temp) > 0:
                            max_dist = n_dist
                            n_cells = np.sum(dists_temp <= max_dist)
                            min_dist.append(n_cells)
                            num_den_temp.append(n_cells / (PI * max_dist**2))
                            area_den_temp.append(
                                np.sum(cell1Areas[dists_temp_orig <= max_dist])
                                / (PI * max_dist**2)
                            )
                        else:
                            min_dist.append(0)
                            num_den_temp.append(0)
                            area_den_temp.append(0)
                    phenotypes.append(
                        pheno_temp
                        + " "
                        + NNA_relation
                        + " "
                        + NNA_dist
                        + " "
                        + pheno_temp2
                    )
                    locations.append(segment_var_temp)
                    if len(min_dist) > 0:
                        numbers.append(np.mean(min_dist))
                        number_density.append(np.mean(num_den_temp))
                        density.append(np.mean(area_den_temp))
                    else:
                        numbers.append(np.nan)
                        number_density.append(np.nan)
                        density.append(np.nan)

                elif NNA_relation == "distance to score":
                    n_cells = np.int32(NNA_dist)
                    if n_cells < 1:
                        continue
                    dists_temp_orig = get_dists(cell1xy, cell2xy)
                    dists_temp_orig[dists_temp_orig == 0] = np.nan
                    if dists_temp_orig.shape[1] > n_cells:
                        min_dist = np.mean(
                            np.nanmean(
                                np.sort(dists_temp_orig, axis=1)[:, :n_cells], axis=1
                            )
                        )
                    else:
                        min_dist = np.mean(
                            np.nanmean(np.sort(dists_temp_orig, axis=1), axis=1)
                        )
                    phenotypes.append(
                        pheno_temp
                        + " "
                        + NNA_relation
                        + " "
                        + NNA_dist
                        + " "
                        + pheno_temp2
                    )
                    locations.append(segment_var_temp)
                    number_density.append(np.nan)
                    density.append(np.nan)
                    if isinstance(min_dist, float):
                        mu, sigma = do_monte_carlo(
                            np.array(all_dists.iloc[all_cells, all_cells2]),
                            cell1xy.shape[0],
                            cell2xy.shape[0],
                            pheno_temp == pheno_temp2,
                            n_trial=1000,
                            n_cells=n_cells,
                            is_dist=True,
                        )
                        numbers.append((min_dist - mu) / sigma)
                    else:
                        numbers.append(np.nan)

                elif NNA_relation == "within score":
                    n_dist = np.float(NNA_dist)
                    if n_dist <= 0:
                        continue
                    dists_temp_orig = get_dists(cell1xy, cell2xy)
                    dists_temp_orig[dists_temp_orig == 0] = np.inf
                    n_cells = np.sum(dists_temp_orig <= n_dist)
                    min_dist = n_cells / cell2xy.shape[0]
                    phenotypes.append(
                        pheno_temp
                        + " "
                        + NNA_relation
                        + " "
                        + NNA_dist
                        + " "
                        + pheno_temp2
                    )
                    locations.append(segment_var_temp)
                    number_density.append(np.nan)
                    density.append(np.nan)
                    if isinstance(min_dist, float):
                        mu, sigma = do_monte_carlo(
                            np.array(all_dists.iloc[all_cells, all_cells2]),
                            cell1xy.shape[0],
                            cell2xy.shape[0],
                            pheno_temp == pheno_temp2,
                            n_trial=1000,
                            n_cells=n_dist,
                            is_dist=False,
                        )
                        numbers.append((min_dist - mu) / sigma)
                    else:
                        numbers.append(np.nan)

        else:
            average_area.append(np.nan)
            segment_var_temp = segment_var
            all_cells = np.array(
                [segment_var_temp in x for x in cell_props["Segments"]]
            )
            all_cells2 = np.array(
                [segment_var_temp in x for x in cell_props2["Segments"]]
            )
            cells_selected1 = all_cells & pheno_cells
            cells_selected2 = all_cells2 & pheno_cells2
            cell1xy = np.array(cell_props["Cell Centroid"][cells_selected1])
            cell1xy = np.array([np.float32([b[1], b[0]]) for b in cell1xy])
            cell1Areas = np.array(cell_props["Cell Area"][cells_selected1])
            cell2xy = np.array(cell_props2["Cell Centroid"][cells_selected2])
            cell2xy = np.array([np.float32([b[1], b[0]]) for b in cell2xy])
            cell2Areas = np.array(cell_props2["Cell Area"][cells_selected2])
            min_dist = []
            num_den_temp = []
            area_den_temp = []
            if (len(cell1xy) == 0) | (len(cell2xy) == 0):
                phenotypes.append(
                    pheno_temp + " " + NNA_relation + " " + NNA_dist + " " + pheno_temp2
                )
                locations.append(segment_var_temp)
                numbers.append(np.nan)
                number_density.append(np.nan)
                density.append(np.nan)
                return (phenotypes, locations, numbers, number_density, density)
            if NNA_relation == "distance to":
                n_cells = np.int32(NNA_dist)
                if n_cells < 1:
                    return (phenotypes, locations, numbers, number_density, density)
                for i in range(len(cell1xy)):
                    dists_temp_orig = (
                        (cell1xy[i, 0] - cell2xy[:, 0]) ** 2
                        + (cell1xy[i, 1] - cell2xy[:, 1]) ** 2
                    ) ** 0.5
                    dists_temp = dists_temp_orig[dists_temp_orig != 0]
                    if len(dists_temp) > 0:
                        if len(dists_temp) > n_cells:
                            max_dist = np.sort(dists_temp)[n_cells - 1]
                            min_dist.append(np.mean(np.sort(dists_temp)[:n_cells]))
                            num_den_temp.append(n_cells / (PI * max_dist**2))
                            area_den_temp.append(
                                np.sum(cell2Areas[dists_temp_orig <= max_dist])
                                / (PI * max_dist**2)
                            )
                        else:
                            min_dist.append(np.mean(dists_temp))
                            max_dist = np.max(dists_temp)
                            num_den_temp.append(len(dists_temp) / (PI * max_dist**2))
                            area_den_temp.append(
                                np.sum(cell2Areas[dists_temp_orig <= max_dist])
                                / (PI * max_dist**2)
                            )
                phenotypes.append(
                    pheno_temp + " " + NNA_relation + " " + NNA_dist + " " + pheno_temp2
                )
                locations.append(segment_var_temp)
                if len(min_dist) > 0:
                    numbers.append(np.mean(min_dist))
                    number_density.append(np.mean(num_den_temp))
                    density.append(np.mean(area_den_temp))
                else:
                    numbers.append(np.nan)
                    number_density.append(np.nan)
                    density.append(np.nan)

            elif NNA_relation == "within":
                n_dist = np.float(NNA_dist)
                if n_dist <= 0:
                    return (phenotypes, locations, numbers, number_density, density)
                for i in range(len(cell2xy)):
                    dists_temp_orig = (
                        (cell2xy[i, 0] - cell1xy[:, 0]) ** 2
                        + (cell2xy[i, 1] - cell1xy[:, 1]) ** 2
                    ) ** 0.5
                    dists_temp = dists_temp_orig[dists_temp_orig != 0]
                    if len(dists_temp) > 0:
                        max_dist = n_dist
                        n_cells = np.sum(dists_temp <= max_dist)
                        min_dist.append(n_cells)
                        num_den_temp.append(n_cells / (PI * max_dist**2))
                        area_den_temp.append(
                            np.sum(cell1Areas[dists_temp_orig <= max_dist])
                            / (PI * max_dist**2)
                        )
                    else:
                        min_dist.append(0)
                        num_den_temp.append(0)
                        area_den_temp.append(0)
                phenotypes.append(
                    pheno_temp + " " + NNA_relation + " " + NNA_dist + " " + pheno_temp2
                )
                locations.append(segment_var_temp)
                if len(min_dist) > 0:
                    numbers.append(np.mean(min_dist))
                    number_density.append(np.mean(num_den_temp))
                    density.append(np.mean(area_den_temp))
                else:
                    numbers.append(np.nan)
                    number_density.append(np.nan)
                    density.append(np.nan)

            elif NNA_relation == "distance to score":
                n_cells = np.int32(NNA_dist)
                if n_cells < 1:
                    return (phenotypes, locations, numbers, number_density, density)
                dists_temp_orig = get_dists(cell1xy, cell2xy)
                dists_temp_orig[dists_temp_orig == 0] = np.nan
                if dists_temp_orig.shape[1] > n_cells:
                    min_dist = np.mean(
                        np.nanmean(
                            np.sort(dists_temp_orig, axis=1)[:, :n_cells], axis=1
                        )
                    )
                else:
                    min_dist = np.mean(
                        np.nanmean(np.sort(dists_temp_orig, axis=1), axis=1)
                    )
                phenotypes.append(
                    pheno_temp + " " + NNA_relation + " " + NNA_dist + " " + pheno_temp2
                )
                locations.append(segment_var_temp)
                number_density.append(np.nan)
                density.append(np.nan)
                if isinstance(min_dist, float):
                    mu, sigma = do_monte_carlo(
                        np.array(all_dists.iloc[all_cells, all_cells2]),
                        cell1xy.shape[0],
                        cell2xy.shape[0],
                        pheno_temp == pheno_temp2,
                        n_trial=1000,
                        n_cells=n_cells,
                        is_dist=True,
                    )
                    numbers.append((min_dist - mu) / sigma)
                else:
                    numbers.append(np.nan)

            elif NNA_relation == "within score":
                n_dist = np.float(NNA_dist)
                if n_dist <= 0:
                    return (phenotypes, locations, numbers, number_density, density)
                dists_temp_orig = get_dists(cell1xy, cell2xy)
                dists_temp_orig[dists_temp_orig == 0] = np.inf
                n_cells = np.sum(dists_temp_orig <= n_dist)
                min_dist = n_cells / cell2xy.shape[0]
                phenotypes.append(
                    pheno_temp + " " + NNA_relation + " " + NNA_dist + " " + pheno_temp2
                )
                locations.append(segment_var_temp)
                number_density.append(np.nan)
                density.append(np.nan)
                if isinstance(min_dist, float):
                    mu, sigma = do_monte_carlo(
                        np.array(all_dists.iloc[all_cells, all_cells2]),
                        cell1xy.shape[0],
                        cell2xy.shape[0],
                        pheno_temp == pheno_temp2,
                        n_trial=1000,
                        n_cells=n_dist,
                        is_dist=False,
                    )
                    numbers.append((min_dist - mu) / sigma)
                else:
                    numbers.append(np.nan)

        return (phenotypes, locations, numbers, number_density, density, average_area)

    def GetPhenoCells(cell_phenos, pheno_var, logicle_int, pheno_cells):
        all_pheno_var = np.array([pheno_var in x for x in cell_phenos])
        if logicle_int == "and":
            pheno_cells = pheno_cells & all_pheno_var
        elif logicle_int == "or":
            pheno_cells = pheno_cells | all_pheno_var
        elif logicle_int == "and not":
            pheno_cells = pheno_cells & ~all_pheno_var
        elif logicle_int == "or not":
            pheno_cells = pheno_cells | ~all_pheno_var
        return pheno_cells

    def addPhenoButton_int(internal_windows, i, j=-1, *a):
        if j < 0:
            addPhenoButton = ttkinter.Button(
                internal_windows, text="Add Phenotype", command=lambda: [addPheno(i, j)]
            )
            addPhenoButton.pack(side=tkinter.LEFT, padx=2, pady=2)
            self.dataParams[i][8] = addPhenoButton
        else:
            addPhenoButton = ttkinter.Button(
                internal_windows,
                text="Add Phenotype " + str(j + 1),
                command=lambda: [addPheno(i, j)],
            )
            addPhenoButton.pack(side=tkinter.LEFT, padx=2, pady=2)
            if j == 0:
                self.dataParams[i][15] = addPhenoButton
            elif j == 1:
                self.dataParams[i][16] = addPhenoButton

    def addDPop(*a):
        cell_props = self.Cell_props[self.activeImage]
        # pheno_available = np.unique(np.hstack(cell_props['Phenotypes'][:]))
        # pheno_available = np.append(pheno_available, 'Everything')
        pheno_available = [i for i in analysis_params["Phenotypes"].keys()]
        pheno_available = np.append(pheno_available, "All")
        pheno_available = np.append(pheno_available, "Everything")
        seg_available = np.unique(np.hstack(cell_props["Segments"][:]))
        seg_available = np.append(seg_available, "Anywhere")
        internal_windows = tkinter.Frame(self.popup, width=200, height=10)
        internal_windows.pack(side=tkinter.TOP)
        data_int = []
        data_int.append(0)
        data_int.append(internal_windows)
        internal_windows1 = tkinter.Frame(internal_windows)
        internal_windows1.pack(side=tkinter.LEFT)
        data_int.append(internal_windows1)
        pheno_variable1 = tkinter.StringVar(internal_windows1)
        pheno_variable1.set(pheno_available[-1])
        data_int.append(pheno_variable1)
        x_var_pointer1 = tkinter.OptionMenu(
            internal_windows1, pheno_variable1, *pheno_available
        )
        x_var_pointer1.config(width=10)
        x_var_pointer1.pack(side=tkinter.LEFT)
        label = ttkinter.Label(internal_windows, text="in")
        data_int.append(pheno_variable1.get())
        label.pack(side=tkinter.LEFT)
        x_variable2 = tkinter.StringVar(internal_windows)
        x_variable2.set(seg_available[-1])
        data_int.append(x_variable2)
        x_var_pointer2 = tkinter.OptionMenu(
            internal_windows, x_variable2, *seg_available
        )
        x_var_pointer2.config(width=10)
        x_var_pointer2.pack(side=tkinter.LEFT)
        data_int.append(x_var_pointer2)
        data_int.append(x_variable2.get())
        n = len(self.dataParams)
        addPhenoButton = ttkinter.Button(
            internal_windows,
            text="Add Phenotype",
            command=lambda: [addPheno(data_int[9])],
        )
        addPhenoButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        data_int.append(addPhenoButton)
        data_int.append(n)
        self.dataParams.append(data_int)

    def addNNA(*a):
        cell_props = self.Cell_props[self.activeImage]
        # pheno_available = np.unique(np.hstack(cell_props['Phenotypes'][:]))
        # pheno_available = np.append(pheno_available, 'Everything')
        pheno_available = [i for i in analysis_params["Phenotypes"].keys()]
        pheno_available = np.append(pheno_available, "All")
        pheno_available = np.append(pheno_available, "Everything")
        # seg_available = np.unique(np.hstack(cell_props['Segments'][:]))
        # seg_available = np.append(seg_available, 'Anywhere')
        seg_available = []
        if len(cell_props) > 0:
            seg_available1 = np.unique(np.hstack(cell_props["Segments"][:]))
            for i in seg_available1:
                seg_available.append(i)
        for tissue_props in self.Tissue_props[self.activeImage].keys():
            tissue_props = self.Tissue_props[self.activeImage][tissue_props]
            seg_available1 = np.unique(np.hstack(tissue_props["Segments"][:]))
            for i in seg_available1:
                seg_available.append(i)
        seg_available = np.unique(seg_available)
        seg_available = np.append(seg_available, "Anywhere")
        NNA_vars = ["distance to", "within", "distance to score", "within score"]
        internal_windows = tkinter.Frame(self.popup, width=200, height=10)
        internal_windows.pack(side=tkinter.TOP)
        data_int = []
        data_int.append(1)
        data_int.append(internal_windows)
        internal_windows1 = tkinter.Frame(internal_windows)
        internal_windows1.pack(side=tkinter.LEFT)
        data_int.append(internal_windows1)
        internal_windows2 = tkinter.Frame(internal_windows)
        internal_windows2.pack(side=tkinter.LEFT)
        data_int.append(internal_windows2)

        pheno_variable1 = tkinter.StringVar(internal_windows1)
        pheno_variable1.set(pheno_available[-1])
        data_int.append(pheno_variable1)
        x_var_pointer1 = tkinter.OptionMenu(
            internal_windows1, pheno_variable1, *pheno_available
        )
        x_var_pointer1.config(width=5)
        x_var_pointer1.pack(side=tkinter.LEFT)
        data_int.append(pheno_variable1.get())

        NNA_variable = tkinter.StringVar(internal_windows2)
        NNA_variable.set(NNA_vars[0])
        data_int.append(NNA_variable)
        NNA_pointer = tkinter.OptionMenu(internal_windows2, NNA_variable, *NNA_vars)
        NNA_pointer.config(width=5)
        NNA_pointer.pack(side=tkinter.LEFT)
        data_int.append(NNA_pointer)
        data_int.append(NNA_variable.get())

        NNA_dist_variable = tkinter.StringVar(internal_windows2)
        NNA_dist_variable.set("1")
        NNA_dist = tkinter.Entry(internal_windows2, textvariable=NNA_dist_variable)
        NNA_dist.config(width=5)
        NNA_dist.pack(side=tkinter.LEFT)
        data_int.append(NNA_dist_variable)

        pheno_variable2 = tkinter.StringVar(internal_windows2)
        pheno_variable2.set(pheno_available[-2])
        data_int.append(pheno_variable2)
        x_var_pointer2 = tkinter.OptionMenu(
            internal_windows2, pheno_variable2, *pheno_available
        )
        x_var_pointer2.config(width=5)
        x_var_pointer2.pack(side=tkinter.LEFT)
        data_int.append(pheno_variable2.get())

        label = ttkinter.Label(internal_windows, text="in")
        label.pack(side=tkinter.LEFT)
        x_variable2 = tkinter.StringVar(internal_windows)
        x_variable2.set(seg_available[-1])
        data_int.append(x_variable2)
        x_var_pointer3 = tkinter.OptionMenu(
            internal_windows, x_variable2, *seg_available
        )
        x_var_pointer3.config(width=5)
        x_var_pointer3.pack(side=tkinter.LEFT)
        data_int.append(x_var_pointer3)
        data_int.append(x_variable2.get())
        n = len(self.dataParams)
        addPhenoButton = ttkinter.Button(
            internal_windows,
            text="Add Phenotype 1",
            command=lambda: [addPheno(data_int[17], 0)],
        )
        addPhenoButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        addPhenoButton2 = ttkinter.Button(
            internal_windows,
            text="Add Phenotype 2",
            command=lambda: [addPheno(data_int[17], 1)],
        )
        addPhenoButton2.pack(side=tkinter.LEFT, padx=2, pady=2)
        data_int.append(addPhenoButton)
        data_int.append(addPhenoButton2)
        data_int.append(n)
        self.dataParams.append(data_int)

    def rmvPop(*a):
        DOI = np.int32(self.data_label_point.get())
        if (DOI <= len(self.dataParams)) & (DOI > 0):
            DestroyTK(self.dataParams[DOI - 1][1])
            self.dataParams.pop(DOI - 1)
        for i in range(0, len(self.dataParams)):
            if self.dataParams[i][0] == 0:
                self.dataParams[i][9] = i
            else:
                self.dataParams[i][17] = i

    def ShowData(*a):
        try:
            DestroyTK(self.ax2)
        except NameError:
            pass
        except AttributeError:
            pass
        self.ax2 = tkinter.Frame(self.popup2, width=200, height=500)
        self.ax2.pack(side=tkinter.TOP)
        self.tree = ttkinter.Treeview(self.ax2)
        self.tree["columns"] = ("1", "2", "3", "4", "5", "6")
        #            self.tree.grid(row=4, column=0, columnspan=2)
        self.tree.heading("#0", text="Filename")
        self.tree.heading("1", text="Phenotype")
        self.tree.heading("2", text="Location")
        self.tree.heading("3", text="Number")
        self.tree.heading("4", text="Number Density")
        self.tree.heading("5", text="Area Density")
        self.tree.heading("6", text="Average Area")
        for filename, data_frame in self.overall_data_to_export.items():
            self.tree.insert("", "end", filename, text=filename)
            phenotypes = data_frame["Phenotypes"][:]
            locations = data_frame["Locations"][:]
            numbers = data_frame["Number"][:]
            number_density = data_frame["Number Density"][:]
            density = data_frame["Area Density"][:]
            average_area = data_frame["Average Area"][:]
            for i, pheno in enumerate(phenotypes):
                self.tree.insert(
                    filename,
                    "end",
                    values=(
                        phenotypes[i],
                        locations[i],
                        numbers[i],
                        number_density[i],
                        density[i],
                        average_area[i],
                    ),
                )
        self.tree.pack()

    def AppendData(activeImage=[], *a):
        def get_all_dists(Props1, Props2):
            locs1 = np.array(Props1["Cell Centroid"])
            locs1 = np.array([np.float32(b) for b in locs1])
            locs2 = np.array(Props2["Cell Centroid"])
            locs2 = np.array([np.float32(b) for b in locs2])
            return pd.DataFrame(
                index=Props1.index, columns=Props2.index, data=get_dists(locs1, locs2)
            )

        def define_cell_dists(cell_props, all_cell_dists):
            if len(all_cell_dists) > 0:
                return all_cell_dists
            else:
                locs = np.array(cell_props["Cell Centroid"])
                locs = np.array([np.float32(b) for b in locs])
                return pd.DataFrame(
                    index=cell_props.index,
                    columns=cell_props.index,
                    data=get_dists(locs, locs),
                )

        show_data = False
        if activeImage == []:
            activeImage = self.activeImage
            show_data = True
        filename = self.FileDictionary[activeImage]
        cell_props = self.Cell_props[activeImage]
        tissue_props = self.Tissue_props[activeImage]
        analysis_params = self.analysis_params[activeImage].copy()
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        im_raw = np.array(self.im_raw[self.activeImage])
        if len(cell_props) > 0:
            seg_available = np.unique(np.hstack(cell_props["Segments"][:]))
        else:
            seg_available = []
        phenotypes = []
        locations = []
        numbers = []
        number_density = []
        density = []
        average_area = []
        all_cell_dists = []

        if len(tissue_props) > 0:
            seg_available_temp = list(seg_available)
            for i in tissue_props:
                for j in np.unique(np.hstack(tissue_props[i]["Segments"][:])):
                    seg_available_temp.append(j)
            seg_available_temp = np.unique(seg_available_temp)
        else:
            seg_available_temp = np.unique(seg_available)
        tissue_seg_areas = {}
        if "Tumor" in analyze_index:
            Tumor_mask = im_analyzed[analyze_index.index("Tumor")]
            if "Stroma" in analyze_index:
                Stroma_mask = im_analyzed[analyze_index.index("Stroma")]
            else:
                Stroma_mask = Tumor_mask == 0
        elif "Stroma" in analyze_index:
            Stroma_mask = im_analyzed[analyze_index.index("Stroma")]
            Tumor_mask = Stroma_mask == 0
        else:
            Stroma_mask = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
            Tumor_mask = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        for i in seg_available_temp:
            Fore_mask = np.ones((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
            if "ROI" in analyze_index:
                Fore_mask = Fore_mask & im_analyzed[analyze_index.index("ROI")]
            if "Foreground" in analyze_index:
                Fore_mask = Fore_mask & im_analyzed[analyze_index.index("Foreground")]
            if i == "All":
                tissue_seg_areas[i] = np.sum(Fore_mask > 0)
            elif i == "Tumor+":
                tissue_seg_areas[i] = np.sum((Tumor_mask & Fore_mask) > 0)
            elif i == "Stroma+":
                tissue_seg_areas[i] = np.sum((Stroma_mask & Fore_mask) > 0)

        for data_int in self.dataParams:
            if data_int[0] == 0:
                pheno_var = data_int[3].get()
                segment_var = data_int[5].get()
                if pheno_var == "Everything":
                    pheno_available = []
                    for segName in analysis_params["Phenotypes"].keys():
                        tissue_temp = []
                        for i in analysis_params["Segments"].keys():
                            if segName.find(i + " - ") == 0:
                                tissue_temp = i
                        if len(tissue_temp) == 0:
                            pheno_available.append(segName)
                    if len(pheno_available) > 0:
                        pheno_available.append("All")
                    for pheno_temp in pheno_available:
                        pheno_cells = np.array(
                            [pheno_temp in x for x in cell_props["Phenotypes"]]
                        )
                        for i in range(10, len(data_int), 4):
                            logicle_int = data_int[i].get()
                            pheno_var = data_int[i + 2].get()
                            pheno_temp = (
                                pheno_temp + " " + logicle_int + " " + pheno_var
                            )
                            pheno_cells = GetPhenoCells(
                                cell_props["Phenotypes"],
                                pheno_var,
                                logicle_int,
                                pheno_cells,
                            )
                        if segment_var == "Anywhere":
                            for segment_var_temp in seg_available:
                                phenotypes.append(pheno_temp)
                                locations.append(segment_var_temp)
                                all_cells = np.array(
                                    [
                                        segment_var_temp in x
                                        for x in cell_props["Segments"]
                                    ]
                                )
                                cells_selected = all_cells & pheno_cells
                                numbers.append(sum(cells_selected))
                                number_density.append(
                                    sum(cells_selected)
                                    / sum(cell_props["Cell Area"][all_cells])
                                )
                                density.append(
                                    sum(cell_props["Cell Area"][cells_selected])
                                    / sum(cell_props["Cell Area"][all_cells])
                                )
                                average_area.append(
                                    np.mean(cell_props["Cell Area"][cells_selected])
                                )
                        else:
                            phenotypes.append(pheno_temp)
                            locations.append(segment_var)
                            all_cells = np.array(
                                [segment_var in x for x in cell_props["Segments"]]
                            )
                            cells_selected = all_cells & pheno_cells
                            numbers.append(sum(cells_selected))
                            number_density.append(
                                sum(cells_selected)
                                / sum(cell_props["Cell Area"][all_cells])
                            )
                            density.append(
                                sum(cell_props["Cell Area"][cells_selected])
                                / sum(cell_props["Cell Area"][all_cells])
                            )
                            average_area.append(
                                np.mean(cell_props["Cell Area"][cells_selected])
                            )
                    tissue_pheno_available = []
                    for segName in analysis_params["Phenotypes"].keys():
                        for i in analysis_params["Segments"].keys():
                            if segName.find(i + " - ") == 0:
                                tissue_pheno_available.append([segName, i])
                    if len(tissue_pheno_available) > 0:
                        tissue_pheno_available.append("All")
                    for pheno_init in tissue_pheno_available:
                        tissue_temp = pheno_init[1]
                        tissue_seg_available = np.unique(
                            np.hstack(tissue_props[tissue_temp]["Segments"][:])
                        )
                        pheno_temp = pheno_init[0][len(tissue_temp) + 3 :]
                        pheno_cells = np.array(
                            [
                                pheno_temp in x
                                for x in tissue_props[tissue_temp]["Phenotypes"]
                            ]
                        )
                        pheno_temp = pheno_init[0]
                        for i in range(10, len(data_int), 4):
                            logicle_int = data_int[i].get()
                            pheno_var = data_int[i + 2].get()
                            if tissue_temp in pheno_var:
                                pheno_temp = (
                                    pheno_temp + " " + logicle_int + " " + pheno_var
                                )
                                pheno_var = pheno_var[len(tissue_temp) + 3 :]
                                pheno_cells = GetPhenoCells(
                                    tissue_props[tissue_temp]["Phenotypes"],
                                    pheno_var,
                                    logicle_int,
                                    pheno_cells,
                                )
                        if segment_var == "Anywhere":
                            for segment_var_temp in tissue_seg_available:
                                phenotypes.append(pheno_init[0])
                                locations.append(segment_var_temp)
                                all_cells = np.array(
                                    [
                                        segment_var_temp in x
                                        for x in tissue_props[tissue_temp]["Segments"]
                                    ]
                                )
                                cells_selected = all_cells & pheno_cells
                                numbers.append(sum(cells_selected))
                                number_density.append(
                                    sum(cells_selected)
                                    / sum(tissue_props[tissue_temp]["Area"][all_cells])
                                )
                                density.append(
                                    sum(
                                        tissue_props[tissue_temp]["Area"][
                                            cells_selected
                                        ]
                                    )
                                    / tissue_seg_areas[segment_var_temp]
                                )
                                average_area.append(
                                    np.mean(
                                        tissue_props[tissue_temp]["Area"][
                                            cells_selected
                                        ]
                                    )
                                )
                        else:
                            phenotypes.append(pheno_init[0])
                            locations.append(segment_var)
                            all_cells = np.array(
                                [
                                    segment_var in x
                                    for x in tissue_props[tissue_temp]["Segments"]
                                ]
                            )
                            cells_selected = all_cells & pheno_cells
                            numbers.append(sum(cells_selected))
                            number_density.append(
                                sum(cells_selected)
                                / sum(tissue_props[tissue_temp]["Area"][all_cells])
                            )
                            density.append(
                                sum(tissue_props[tissue_temp]["Area"][cells_selected])
                                / tissue_seg_areas[segment_var]
                            )
                            average_area.append(
                                np.mean(
                                    tissue_props[tissue_temp]["Area"][cells_selected]
                                )
                            )
                else:
                    pheno_temp = pheno_var
                    tissue_temp = []
                    for i in analysis_params["Segments"].keys():
                        if pheno_temp.find(i + " - ") == 0:
                            tissue_temp = i
                    if len(tissue_temp) == 0:
                        pheno_cells = np.array(
                            [pheno_temp in x for x in cell_props["Phenotypes"]]
                        )
                        for i in range(10, len(data_int), 4):
                            logicle_int = data_int[i].get()
                            pheno_var = data_int[i + 2].get()
                            pheno_temp = (
                                pheno_temp + " " + logicle_int + " " + pheno_var
                            )
                            pheno_cells = GetPhenoCells(
                                cell_props["Phenotypes"],
                                pheno_var,
                                logicle_int,
                                pheno_cells,
                            )
                        if segment_var == "Anywhere":
                            for segment_var_temp in seg_available:
                                phenotypes.append(pheno_temp)
                                locations.append(segment_var_temp)
                                all_cells = np.array(
                                    [
                                        segment_var_temp in x
                                        for x in cell_props["Segments"]
                                    ]
                                )
                                cells_selected = all_cells & pheno_cells
                                numbers.append(sum(cells_selected))
                                number_density.append(
                                    sum(cells_selected)
                                    / sum(cell_props["Cell Area"][all_cells])
                                )
                                density.append(
                                    sum(cell_props["Cell Area"][cells_selected])
                                    / sum(cell_props["Cell Area"][all_cells])
                                )
                                average_area.append(
                                    np.mean(cell_props["Cell Area"][cells_selected])
                                )
                        else:
                            phenotypes.append(pheno_temp)
                            locations.append(segment_var)
                            all_cells = np.array(
                                [segment_var in x for x in cell_props["Segments"]]
                            )
                            cells_selected = all_cells & pheno_cells
                            numbers.append(sum(cells_selected))
                            number_density.append(
                                sum(cells_selected)
                                / sum(cell_props["Cell Area"][all_cells])
                            )
                            density.append(
                                sum(cell_props["Cell Area"][cells_selected])
                                / sum(cell_props["Cell Area"][all_cells])
                            )
                            average_area.append(
                                np.mean(cell_props["Cell Area"][cells_selected])
                            )

                    else:
                        pheno_init = [pheno_temp, tissue_temp]
                        pheno_temp = pheno_init[0][len(tissue_temp) + 3 :]
                        tissue_seg_available = np.unique(
                            np.hstack(tissue_props[tissue_temp]["Segments"][:])
                        )
                        pheno_cells = np.array(
                            [
                                pheno_temp in x
                                for x in tissue_props[tissue_temp]["Phenotypes"]
                            ]
                        )
                        pheno_temp = pheno_init[0]
                        for i in range(10, len(data_int), 4):
                            logicle_int = data_int[i].get()
                            pheno_var = data_int[i + 2].get()
                            if tissue_temp in pheno_var:
                                pheno_temp = (
                                    pheno_temp + " " + logicle_int + " " + pheno_var
                                )
                                pheno_var = pheno_var[len(tissue_temp) + 3 :]
                                pheno_cells = GetPhenoCells(
                                    tissue_props[tissue_temp]["Phenotypes"],
                                    pheno_var,
                                    logicle_int,
                                    pheno_cells,
                                )
                        if segment_var == "Anywhere":
                            for segment_var_temp in tissue_seg_available:
                                phenotypes.append(pheno_init[0])
                                locations.append(segment_var_temp)
                                all_cells = np.array(
                                    [
                                        segment_var_temp in x
                                        for x in tissue_props[tissue_temp]["Segments"]
                                    ]
                                )
                                cells_selected = all_cells & pheno_cells
                                numbers.append(sum(cells_selected))
                                number_density.append(
                                    sum(cells_selected)
                                    / sum(tissue_props[tissue_temp]["Area"][all_cells])
                                )
                                density.append(
                                    sum(
                                        tissue_props[tissue_temp]["Area"][
                                            cells_selected
                                        ]
                                    )
                                    / tissue_seg_areas[segment_var_temp]
                                )
                                average_area.append(
                                    np.mean(
                                        tissue_props[tissue_temp]["Area"][
                                            cells_selected
                                        ]
                                    )
                                )
                        else:
                            phenotypes.append(pheno_init[0])
                            locations.append(segment_var)
                            all_cells = np.array(
                                [
                                    segment_var_temp in x
                                    for x in tissue_props[tissue_temp]["Segments"]
                                ]
                            )
                            cells_selected = all_cells & pheno_cells
                            numbers.append(sum(cells_selected))
                            number_density.append(
                                sum(cells_selected)
                                / sum(tissue_props[tissue_temp]["Area"][all_cells])
                            )
                            density.append(
                                sum(tissue_props[tissue_temp]["Area"][cells_selected])
                                / tissue_seg_areas[segment_var]
                            )
                            average_area.append(
                                np.mean(
                                    tissue_props[tissue_temp]["Area"][cells_selected]
                                )
                            )

            elif data_int[0] == 1:
                pheno_var1 = data_int[4].get()
                NNA_relation = data_int[6].get()
                NNA_dist = data_int[9].get()
                pheno_var2 = data_int[10].get()
                segment_var = data_int[12].get()

                if pheno_var1 == "Everything":
                    pheno_available = []
                    for segName in analysis_params["Phenotypes"].keys():
                        tissue_temp = []
                        for i in analysis_params["Segments"].keys():
                            if segName.find(i + " - ") == 0:
                                tissue_temp = i
                        if len(tissue_temp) == 0:
                            pheno_available.append(segName)
                    if len(pheno_available) > 0:
                        pheno_available.append("All")
                    for pheno_temp in pheno_available:
                        pheno_cells = np.array(
                            [pheno_temp in x for x in cell_props["Phenotypes"]]
                        )
                        for i in range(18, len(data_int), 5):
                            if data_int[i] == 0:
                                logicle_int = data_int[i + 1].get()
                                pheno_var = data_int[i + 3].get()
                                pheno_temp = (
                                    pheno_temp + " " + logicle_int + " " + pheno_var
                                )
                                pheno_cells = GetPhenoCells(
                                    cell_props["Phenotypes"],
                                    pheno_var,
                                    logicle_int,
                                    pheno_cells,
                                )

                        if pheno_var2 == "Everything":
                            pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                tissue_temp = []
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_temp = i
                                if len(tissue_temp) == 0:
                                    pheno_available.append(segName)
                            if len(pheno_available) > 0:
                                pheno_available.append("All")
                            for pheno_temp2 in pheno_available:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                if "score" in NNA_relation:
                                    all_cell_dists = define_cell_dists(
                                        cell_props, all_cell_dists
                                    )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    cell_props,
                                    all_cell_dists,
                                )
                            tissue_pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_pheno_available.append([segName, i])
                            if len(tissue_pheno_available) > 0:
                                tissue_pheno_available.append("All")
                            for pheno_init in tissue_pheno_available:
                                tissue_temp = pheno_init[1]
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists = get_all_dists(
                                        cell_props, tissue_props_temp
                                    )
                                else:
                                    ref_dists = []
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    tissue_props_temp,
                                    ref_dists,
                                )
                        else:
                            pheno_temp2 = pheno_var2
                            tissue_temp = []
                            for i in analysis_params["Segments"].keys():
                                if pheno_temp2.find(i + " - ") == 0:
                                    tissue_temp = i
                            if len(tissue_temp) == 0:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                if "score" in NNA_relation:
                                    all_cell_dists = define_cell_dists(
                                        cell_props, all_cell_dists
                                    )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    cell_props,
                                    all_cell_dists,
                                )
                            else:
                                pheno_init = [pheno_temp2, tissue_temp]
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists = get_all_dists(
                                        cell_props, tissue_props_temp
                                    )
                                else:
                                    ref_dists = []
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    tissue_props_temp,
                                    ref_dists,
                                )
                    tissue_pheno_available = []
                    for segName in analysis_params["Phenotypes"].keys():
                        for i in analysis_params["Segments"].keys():
                            if segName.find(i + " - ") == 0:
                                tissue_pheno_available.append([segName, i])
                    if len(tissue_pheno_available) > 0:
                        tissue_pheno_available.append("All")
                    for pheno_init in tissue_pheno_available:
                        tissue_temp = pheno_init[1]
                        tissue_seg_available = np.unique(
                            np.hstack(tissue_props[tissue_temp]["Segments"][:])
                        )
                        pheno_temp = pheno_init[0][len(tissue_temp) + 3 :]
                        pheno_cells = np.array(
                            [
                                pheno_temp in x
                                for x in tissue_props[tissue_temp]["Phenotypes"]
                            ]
                        )
                        pheno_temp = pheno_init[0]
                        for i in range(18, len(data_int), 5):
                            if data_int[i] == 0:
                                logicle_int = data_int[i + 1].get()
                                pheno_var = data_int[i + 3].get()
                                if tissue_temp in pheno_var:
                                    pheno_temp = (
                                        pheno_temp + " " + logicle_int + " " + pheno_var
                                    )
                                    pheno_var = pheno_var[len(tissue_temp) + 3 :]
                                    pheno_cells = GetPhenoCells(
                                        tissue_props[tissue_temp]["Phenotypes"],
                                        pheno_var,
                                        logicle_int,
                                        pheno_cells,
                                    )
                        tissue_props_temp1 = tissue_props[tissue_temp].copy()
                        tissue_props_temp1["Cell Area"] = tissue_props_temp1["Area"]
                        tissue_props_temp1["Cell Centroid"] = tissue_props_temp1[
                            "Centroid"
                        ]
                        if "score" in NNA_relation:
                            ref_dists = get_all_dists(tissue_props_temp1, cell_props)
                        else:
                            ref_dists = []
                        if pheno_var2 == "Everything":
                            pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                tissue_temp = []
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_temp = i
                                if len(tissue_temp) == 0:
                                    pheno_available.append(segName)
                            if len(pheno_available) > 0:
                                pheno_available.append("All")
                            for pheno_temp2 in pheno_available:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    cell_props,
                                    ref_dists,
                                )
                            tissue_pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_pheno_available.append([segName, i])
                            if len(tissue_pheno_available) > 0:
                                tissue_pheno_available.append("All")
                            for pheno_init in tissue_pheno_available:
                                tissue_temp = pheno_init[1]
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists2 = get_all_dists(
                                        tissue_props_temp1, tissue_props_temp
                                    )
                                else:
                                    ref_dists2 = []

                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    tissue_props_temp,
                                    ref_dists2,
                                )
                        else:
                            pheno_temp2 = pheno_var2
                            tissue_temp = []
                            for i in analysis_params["Segments"].keys():
                                if pheno_temp2.find(i + " - ") == 0:
                                    tissue_temp = i
                            if len(tissue_temp) == 0:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    cell_props,
                                    ref_dists,
                                )
                            else:
                                pheno_init = [pheno_temp2, tissue_temp]
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists2 = get_all_dists(
                                        tissue_props_temp1, tissue_props_temp
                                    )
                                else:
                                    ref_dists2 = []

                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    tissue_props_temp,
                                    ref_dists2,
                                )

                else:
                    pheno_temp = pheno_var1
                    tissue_temp = []
                    for i in analysis_params["Segments"].keys():
                        if pheno_temp.find(i + " - ") == 0:
                            tissue_temp = i
                    if len(tissue_temp) == 0:
                        pheno_cells = np.array(
                            [pheno_temp in x for x in cell_props["Phenotypes"]]
                        )
                        for i in range(18, len(data_int), 5):
                            if data_int[i] == 0:
                                logicle_int = data_int[i + 1].get()
                                pheno_var = data_int[i + 3].get()
                                pheno_temp = (
                                    pheno_temp + " " + logicle_int + " " + pheno_var
                                )
                                pheno_cells = GetPhenoCells(
                                    cell_props["Phenotypes"],
                                    pheno_var,
                                    logicle_int,
                                    pheno_cells,
                                )

                        if pheno_var2 == "Everything":
                            pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                tissue_temp = []
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_temp = i
                                if len(tissue_temp) == 0:
                                    pheno_available.append(segName)
                            if len(pheno_available) > 0:
                                pheno_available.append("All")
                            for pheno_temp2 in pheno_available:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                if "score" in NNA_relation:
                                    all_cell_dists = define_cell_dists(
                                        cell_props, all_cell_dists
                                    )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    cell_props,
                                    all_cell_dists,
                                )
                            tissue_pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_pheno_available.append([segName, i])
                            if len(tissue_pheno_available) > 0:
                                tissue_pheno_available.append("All")
                            for pheno_init in tissue_pheno_available:
                                tissue_temp = pheno_init[1]
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists = get_all_dists(
                                        cell_props, tissue_props_temp
                                    )
                                else:
                                    ref_dists = []
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    tissue_props_temp,
                                    ref_dists,
                                )
                        else:
                            pheno_temp2 = pheno_var2
                            tissue_temp = []
                            for i in analysis_params["Segments"].keys():
                                if pheno_temp2.find(i + " - ") == 0:
                                    tissue_temp = i
                            if len(tissue_temp) == 0:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                if "score" in NNA_relation:
                                    all_cell_dists = define_cell_dists(
                                        cell_props, all_cell_dists
                                    )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    cell_props,
                                    all_cell_dists,
                                )
                            else:
                                pheno_init = [pheno_temp2, tissue_temp]
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists = get_all_dists(
                                        cell_props, tissue_props_temp
                                    )
                                else:
                                    ref_dists = []
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    cell_props,
                                    tissue_props_temp,
                                    ref_dists,
                                )
                    else:
                        pheno_init = [pheno_temp, tissue_temp]
                        pheno_temp = pheno_init[0][len(tissue_temp) + 3 :]
                        tissue_seg_available = np.unique(
                            np.hstack(tissue_props[tissue_temp]["Segments"][:])
                        )
                        pheno_cells = np.array(
                            [
                                pheno_temp in x
                                for x in tissue_props[tissue_temp]["Phenotypes"]
                            ]
                        )
                        pheno_temp = pheno_init[0]
                        for i in range(18, len(data_int), 5):
                            if data_int[i] == 0:
                                logicle_int = data_int[i + 1].get()
                                pheno_var = data_int[i + 3].get()
                                if tissue_temp in pheno_var:
                                    pheno_temp = (
                                        pheno_temp + " " + logicle_int + " " + pheno_var
                                    )
                                    pheno_var = pheno_var[len(tissue_temp) + 3 :]
                                    pheno_cells = GetPhenoCells(
                                        tissue_props[tissue_temp]["Phenotypes"],
                                        pheno_var,
                                        logicle_int,
                                        pheno_cells,
                                    )
                        tissue_props_temp1 = tissue_props[tissue_temp].copy()
                        tissue_props_temp1["Cell Area"] = tissue_props_temp1["Area"]
                        tissue_props_temp1["Cell Centroid"] = tissue_props_temp1[
                            "Centroid"
                        ]
                        if "score" in NNA_relation:
                            ref_dists = get_all_dists(tissue_props_temp1, cell_props)
                        else:
                            ref_dists = []

                        if pheno_var2 == "Everything":
                            # pheno_available = np.unique(np.hstack(
                            #         cell_props['Phenotypes'][:]))
                            # pheno_available = np.unique(
                            #     np.hstack(cell_props['Phenotypes'][:]))
                            pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                tissue_temp = []
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_temp = i
                                if len(tissue_temp) == 0:
                                    pheno_available.append(segName)
                            if len(pheno_available) > 0:
                                pheno_available.append("All")
                            for pheno_temp2 in pheno_available:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    cell_props,
                                    ref_dists,
                                )
                            tissue_pheno_available = []
                            for segName in analysis_params["Phenotypes"].keys():
                                for i in analysis_params["Segments"].keys():
                                    if segName.find(i + " - ") == 0:
                                        tissue_pheno_available.append([segName, i])
                            if len(tissue_pheno_available) > 0:
                                tissue_pheno_available.append("All")
                            for pheno_init in tissue_pheno_available:
                                tissue_temp = pheno_init[1]
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists2 = get_all_dists(
                                        tissue_props_temp1, tissue_props_temp
                                    )
                                else:
                                    ref_dists2 = []
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    tissue_props_temp,
                                    ref_dists2,
                                )
                        else:
                            pheno_temp2 = pheno_var2
                            tissue_temp = []
                            for i in analysis_params["Segments"].keys():
                                if pheno_temp2.find(i + " - ") == 0:
                                    tissue_temp = i
                            if len(tissue_temp) == 0:
                                pheno_cells2 = np.array(
                                    [pheno_temp2 in x for x in cell_props["Phenotypes"]]
                                )
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        pheno_temp2 = (
                                            pheno_temp2
                                            + " "
                                            + logicle_int
                                            + " "
                                            + pheno_var
                                        )
                                        pheno_cells2 = GetPhenoCells(
                                            cell_props["Phenotypes"],
                                            pheno_var,
                                            logicle_int,
                                            pheno_cells2,
                                        )
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    cell_props,
                                    ref_dists,
                                )
                            else:
                                pheno_init = [pheno_temp2, tissue_temp]
                                pheno_temp2 = pheno_init[0][len(tissue_temp) + 3 :]
                                pheno_available.append(segName)
                                tissue_seg_available = np.unique(
                                    np.hstack(tissue_props[tissue_temp]["Segments"][:])
                                )
                                pheno_cells2 = np.array(
                                    [
                                        pheno_temp2 in x
                                        for x in tissue_props[tissue_temp]["Phenotypes"]
                                    ]
                                )
                                pheno_temp2 = pheno_init[0]
                                for i in range(18, len(data_int), 5):
                                    if data_int[i] == 1:
                                        logicle_int = data_int[i + 1].get()
                                        pheno_var = data_int[i + 3].get()
                                        if tissue_temp in pheno_var:
                                            pheno_temp2 = (
                                                pheno_temp2
                                                + " "
                                                + logicle_int
                                                + " "
                                                + pheno_var
                                            )
                                            pheno_var = pheno_var[
                                                len(tissue_temp) + 3 :
                                            ]
                                            pheno_cells2 = GetPhenoCells(
                                                tissue_props[tissue_temp]["Phenotypes"],
                                                pheno_var,
                                                logicle_int,
                                                pheno_cells2,
                                            )
                                tissue_props_temp = tissue_props[tissue_temp].copy()
                                tissue_props_temp["Cell Area"] = tissue_props_temp[
                                    "Area"
                                ]
                                tissue_props_temp["Cell Centroid"] = tissue_props_temp[
                                    "Centroid"
                                ]
                                if "score" in NNA_relation:
                                    ref_dists2 = get_all_dists(
                                        tissue_props_temp1, tissue_props_temp
                                    )
                                else:
                                    ref_dists2 = []
                                [
                                    phenotypes,
                                    locations,
                                    numbers,
                                    number_density,
                                    density,
                                    average_area,
                                ] = PerformNNA_Analysis(
                                    segment_var,
                                    pheno_cells,
                                    pheno_cells2,
                                    phenotypes,
                                    pheno_temp,
                                    NNA_relation,
                                    NNA_dist,
                                    pheno_temp2,
                                    locations,
                                    numbers,
                                    density,
                                    number_density,
                                    average_area,
                                    tissue_props_temp1,
                                    tissue_props_temp,
                                    ref_dists2,
                                )

        self.overall_data_to_export[filename] = pd.DataFrame(
            {
                "Phenotypes": phenotypes,
                "Locations": locations,
                "Number": numbers,
                "Number Density": number_density,
                "Area Density": density,
                "Average Area": average_area,
            }
        )
        if show_data:
            ShowData()

    def RemoveData(*a):
        filename = self.FileDictionary[self.activeImage]
        self.overall_data_to_export.pop(filename)
        ShowData()

    def SaveData(*a):
        filename = tkinter.filedialog.asksaveasfilename(parent=self.master)
        if filename:
            data_to_export = pd.concat(
                [
                    pd.concat(
                        [
                            pd.concat(
                                [
                                    pd.DataFrame([filename], columns=["filename"])
                                    for i in range(len(data_frame))
                                ],
                                ignore_index=True,
                            ),
                            data_frame,
                        ],
                        axis=1,
                    )
                    for filename, data_frame in self.overall_data_to_export.items()
                ],
                ignore_index=True,
            )
            if filename[-4:] in [".xls", ".txt", ".csv"]:
                data_to_export.to_csv(filename, sep="\t")
            elif filename[-5:] == ".xlsx":
                data_to_export.to_excel(filename)
            else:
                data_to_export.to_csv(filename + ".xls", sep="\t")

    def resetData(*a):
        def resetDataSure(*a):
            self.overall_data_to_export = {}
            ShowData()

        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = ttkinter.Label(
            popup2, text="You are about to" + " reset all data tabled for all files"
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = ttkinter.Button(
            popup2,
            text="Go Ahead",
            command=lambda: [DestroyTK(popup2), resetDataSure()],
        )
        B1.pack()
        B2 = ttkinter.Button(
            popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
        )
        B2.pack()
        popup2.mainloop()

    def addPheno(n, j=-1, *a):
        logicle_vars = ["and", "or", "and not", "or  not"]
        cell_props = self.Cell_props[self.activeImage]
        pheno_available = np.unique(np.hstack(cell_props["Phenotypes"][:]))
        pheno_available = [i for i in analysis_params["Phenotypes"].keys()]
        # pheno_available = np.append(pheno_available, 'All')
        # pheno_available = np.append(pheno_available, 'Everything')
        #        seg_available = np.unique(np.hstack(cell_props['Segments'][:]))
        #        seg_available = np.append(seg_available, 'Anywhere')
        if j < 0:
            data_int = self.dataParams[n]
            internal_windows = data_int[2]
            logicle_variable1 = tkinter.StringVar(internal_windows)
            logicle_variable1.set(logicle_vars[0])
            data_int.append(logicle_variable1)
            x_log_pointer1 = tkinter.OptionMenu(
                internal_windows, logicle_variable1, *logicle_vars
            )
            x_log_pointer1.config(width=10)
            x_log_pointer1.pack(side=tkinter.LEFT)
            data_int.append(logicle_variable1.get())
            pheno_variable1 = tkinter.StringVar(internal_windows)
            pheno_variable1.set(pheno_available[0])
            data_int.append(pheno_variable1)
            x_var_pointer1 = tkinter.OptionMenu(
                internal_windows, pheno_variable1, *pheno_available
            )
            x_var_pointer1.config(width=10)
            x_var_pointer1.pack(side=tkinter.LEFT)
            data_int.append(pheno_variable1.get())
            self.dataParams[n] = data_int
        else:
            data_int = self.dataParams[n]
            data_int.append(j)
            internal_windows = data_int[j + 2]
            logicle_variable1 = tkinter.StringVar(internal_windows)
            logicle_variable1.set(logicle_vars[0])
            data_int.append(logicle_variable1)
            x_log_pointer1 = tkinter.OptionMenu(
                internal_windows, logicle_variable1, *logicle_vars
            )
            x_log_pointer1.config(width=5)
            x_log_pointer1.pack(side=tkinter.LEFT)
            data_int.append(logicle_variable1.get())
            pheno_variable1 = tkinter.StringVar(internal_windows)
            pheno_variable1.set(pheno_available[0])
            data_int.append(pheno_variable1)
            x_var_pointer1 = tkinter.OptionMenu(
                internal_windows, pheno_variable1, *pheno_available
            )
            x_var_pointer1.config(width=5)
            x_var_pointer1.pack(side=tkinter.LEFT)
            data_int.append(pheno_variable1.get())
            self.dataParams[n] = data_int

    def SaveDataStructure(*a):
        if len(self.dataParams) == 0:
            return
        filename_save = tkinter.filedialog.asksaveasfilename(parent=popup_main)
        dataParams = []
        for i in range(len(self.dataParams)):
            data_int = self.dataParams[i]
            if data_int[0] == 0:
                data_temp = [data_int[j] for j in [0]]
                data_temp.append(data_int[3].get())
                data_temp.append(data_int[5].get())
                for j in range(10, len(data_int), 4):
                    data_temp.append(data_int[j].get())
                    data_temp.append(data_int[j + 2].get())
                dataParams.append(data_temp)
            else:
                data_temp = [data_int[j] for j in [0]]
                data_temp.append(data_int[4].get())
                data_temp.append(data_int[6].get())
                data_temp.append(data_int[9].get())
                data_temp.append(data_int[10].get())
                data_temp.append(data_int[12].get())
                for j in range(18, len(data_int), 5):
                    data_temp.append(data_int[j])
                    data_temp.append(data_int[j + 1].get())
                    data_temp.append(data_int[j + 3].get())
                dataParams.append(data_temp)
        if filename_save:
            pickle_savename = filename_save
            if filename_save[-7:] != ".pickle":
                if "." not in filename_save[-5:]:
                    pickle_savename += ".pickle"
            with open(pickle_savename, "wb") as f:
                pickle.dump({"Data Analysis Params": dataParams}, f)

    def LoadDataStructure(*a):
        filename = tkinter.filedialog.askopenfilename(parent=self.master)
        pickle_data = pickle.load(open(filename, "rb"))
        dataParams = pickle_data["Data Analysis Params"]
        if len(dataParams) == 0:
            return
        self.dataParams = []
        # addPhenoButton = []
        for i in range(len(dataParams)):
            data_int_temp = dataParams[i]
            data_int = [data_int_temp[0]]
            if data_int[0] == 0:
                internal_windows = tkinter.Frame(self.popup, width=200, height=10)
                internal_windows.pack(side=tkinter.TOP)
                data_int.append(internal_windows)
                internal_windows1 = tkinter.Frame(internal_windows)
                internal_windows1.pack(side=tkinter.LEFT)
                data_int.append(internal_windows1)
                pheno_variable1 = tkinter.StringVar(internal_windows1)
                pheno_variable1.set(data_int_temp[1])
                data_int.append(pheno_variable1)
                x_var_pointer1 = tkinter.OptionMenu(
                    internal_windows1, pheno_variable1, *pheno_available
                )
                x_var_pointer1.config(width=10)
                x_var_pointer1.pack(side=tkinter.LEFT)
                label = ttkinter.Label(internal_windows, text="in")
                data_int.append(pheno_variable1.get())
                label.pack(side=tkinter.LEFT)
                x_variable2 = tkinter.StringVar(internal_windows)
                x_variable2.set(data_int_temp[2])
                data_int.append(x_variable2)
                x_var_pointer2 = tkinter.OptionMenu(
                    internal_windows, x_variable2, *seg_available
                )
                x_var_pointer2.config(width=10)
                x_var_pointer2.pack(side=tkinter.LEFT)
                data_int.append(x_var_pointer2)
                data_int.append(x_variable2.get())
                n = len(self.dataParams)
                addPhenoButton = ttkinter.Button(
                    internal_windows,
                    text="Add Phenotype",
                    command=lambda: [addPheno(data_int[9])],
                )
                addPhenoButton.pack(side=tkinter.LEFT, padx=2, pady=2)
                data_int.append(addPhenoButton)
                data_int.append(n)
                for j in range(3, len(data_int_temp), 2):
                    logicle_int = data_int_temp[j]
                    pheno_var = data_int_temp[j + 1]
                    internal_windows = data_int[2]
                    logicle_variable1 = tkinter.StringVar(internal_windows)
                    logicle_variable1.set(logicle_int)
                    data_int.append(logicle_variable1)
                    x_log_pointer1 = tkinter.OptionMenu(
                        internal_windows, logicle_variable1, *logicle_vars
                    )
                    x_log_pointer1.config(width=10)
                    x_log_pointer1.pack(side=tkinter.LEFT)
                    data_int.append(logicle_variable1.get())
                    pheno_variable1 = tkinter.StringVar(internal_windows)
                    pheno_variable1.set(pheno_var)
                    data_int.append(pheno_variable1)
                    x_var_pointer1 = tkinter.OptionMenu(
                        internal_windows, pheno_variable1, *pheno_available
                    )
                    x_var_pointer1.config(width=10)
                    x_var_pointer1.pack(side=tkinter.LEFT)
                    data_int.append(pheno_variable1.get())
                self.dataParams.append(data_int)
            else:
                internal_windows = tkinter.Frame(self.popup, width=200, height=10)
                internal_windows.pack(side=tkinter.TOP)
                data_int.append(internal_windows)
                internal_windows1 = tkinter.Frame(internal_windows)
                internal_windows1.pack(side=tkinter.LEFT)
                data_int.append(internal_windows1)
                internal_windows2 = tkinter.Frame(internal_windows)
                internal_windows2.pack(side=tkinter.LEFT)
                data_int.append(internal_windows2)
                pheno_variable1 = tkinter.StringVar(internal_windows1)
                pheno_variable1.set(data_int_temp[1])
                data_int.append(pheno_variable1)
                x_var_pointer1 = tkinter.OptionMenu(
                    internal_windows1, pheno_variable1, *pheno_available
                )
                x_var_pointer1.config(width=5)
                x_var_pointer1.pack(side=tkinter.LEFT)
                data_int.append(pheno_variable1.get())

                NNA_variable = tkinter.StringVar(internal_windows2)
                NNA_variable.set(data_int_temp[2])
                data_int.append(NNA_variable)
                NNA_pointer = tkinter.OptionMenu(
                    internal_windows2, NNA_variable, *NNA_vars
                )
                NNA_pointer.config(width=5)
                NNA_pointer.pack(side=tkinter.LEFT)
                data_int.append(NNA_pointer)
                data_int.append(NNA_variable.get())

                NNA_dist_variable = tkinter.StringVar(internal_windows2)
                NNA_dist_variable.set(data_int_temp[3])
                NNA_dist = tkinter.Entry(
                    internal_windows2, textvariable=NNA_dist_variable
                )
                NNA_dist.config(width=5)
                NNA_dist.pack(side=tkinter.LEFT)
                data_int.append(NNA_dist_variable)

                pheno_variable2 = tkinter.StringVar(internal_windows2)
                pheno_variable2.set(data_int_temp[4])
                data_int.append(pheno_variable2)
                x_var_pointer2 = tkinter.OptionMenu(
                    internal_windows2, pheno_variable2, *pheno_available
                )
                x_var_pointer2.config(width=5)
                x_var_pointer2.pack(side=tkinter.LEFT)
                data_int.append(pheno_variable2.get())

                label = ttkinter.Label(internal_windows, text="in")
                label.pack(side=tkinter.LEFT)
                x_variable2 = tkinter.StringVar(internal_windows)
                x_variable2.set(data_int_temp[5])
                data_int.append(x_variable2)
                x_var_pointer3 = tkinter.OptionMenu(
                    internal_windows, x_variable2, *seg_available
                )
                x_var_pointer3.config(width=5)
                x_var_pointer3.pack(side=tkinter.LEFT)
                data_int.append(x_var_pointer3)
                data_int.append(x_variable2.get())
                n = len(self.dataParams)
                addPhenoButton = ttkinter.Button(
                    internal_windows,
                    text="Add Phenotype 1",
                    command=lambda: [addPheno(data_int[17], 0)],
                )
                addPhenoButton.pack(side=tkinter.LEFT, padx=2, pady=2)
                addPhenoButton2 = ttkinter.Button(
                    internal_windows,
                    text="Add Phenotype 2",
                    command=lambda: [addPheno(data_int[17], 1)],
                )
                addPhenoButton2.pack(side=tkinter.LEFT, padx=2, pady=2)
                data_int.append(addPhenoButton)
                data_int.append(addPhenoButton2)
                data_int.append(n)
                for j in range(6, len(data_int_temp), 3):
                    window_n = data_int_temp[j]
                    data_int.append(window_n)
                    logicle_int = data_int_temp[j + 1]
                    pheno_var = data_int_temp[j + 2]
                    internal_windows = data_int[window_n + 2]
                    logicle_variable1 = tkinter.StringVar(internal_windows)
                    logicle_variable1.set(logicle_int)
                    data_int.append(logicle_variable1)
                    x_log_pointer1 = tkinter.OptionMenu(
                        internal_windows, logicle_variable1, *logicle_vars
                    )
                    x_log_pointer1.config(width=5)
                    x_log_pointer1.pack(side=tkinter.LEFT)
                    data_int.append(logicle_variable1.get())
                    pheno_variable1 = tkinter.StringVar(internal_windows)
                    pheno_variable1.set(pheno_var)
                    data_int.append(pheno_variable1)
                    x_var_pointer1 = tkinter.OptionMenu(
                        internal_windows, pheno_variable1, *pheno_available
                    )
                    x_var_pointer1.config(width=5)
                    x_var_pointer1.pack(side=tkinter.LEFT)
                    data_int.append(pheno_variable1.get())
                self.dataParams.append(data_int)
        popup_main.destroy()
        DataAnalysis(self)

    def Append_all_data(*a):
        [popup, label] = popupmsg("...", False)
        for activeImage in range(len(self.FileDictionary)):
            label["text"] = (
                "Appending data for "
                + str(activeImage + 1)
                + " of "
                + str(len(self.FileDictionary))
                + " images.\n Please hold."
            )
            popup.update()
            if (len(self.Cell_props[activeImage]) > 0) | (
                len(self.Tissue_props[activeImage]) > 0
            ):
                try:
                    AppendData(activeImage)
                except:
                    print(self.FileDictionary[activeImage], "failed")
        DestroyTK(popup)
        ShowData()

    popup_main = tkinter.Tk()
    self.popup2 = popup_main
    popup_main.geometry("1200x800")
    popup_main.wm_title("Data Analysis")
    popup = tkinter.Frame(popup_main, width=400, height=1000)
    self.popup = popup
    toolbar = tkinter.Frame(popup_main)
    addPopButton = ttkinter.Button(toolbar, text="Add Population", command=addDPop)
    addPopButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    addNNAButton = ttkinter.Button(toolbar, text="Add NNA", command=addNNA)
    addNNAButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvPopButton = ttkinter.Button(toolbar, text="Remove Population", command=rmvPop)
    rmvPopButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    labelButton = tkinter.Entry(toolbar)
    labelButton.pack(side=tkinter.LEFT)
    labelButton.insert(0, "1")
    self.data_label_point = labelButton

    showDataButton = ttkinter.Button(toolbar, text="Show Data", command=ShowData)
    showDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    appDataButton = ttkinter.Button(toolbar, text="Append Data", command=AppendData)
    appDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvDataButton = ttkinter.Button(toolbar, text="Remove Data", command=RemoveData)
    rmvDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    saveDataButton = ttkinter.Button(toolbar, text="Save Data", command=SaveData)
    saveDataButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    saveDatastrucButton = ttkinter.Button(
        toolbar, text="Save Data Structure", command=SaveDataStructure
    )
    saveDatastrucButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    loadDatastrucButton = ttkinter.Button(
        toolbar, text="Load Data Structure", command=LoadDataStructure
    )
    loadDatastrucButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    resetButton = ttkinter.Button(toolbar, text="Reset Data", command=resetData)
    resetButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    appendAllButton = ttkinter.Button(
        toolbar, text="Append All Data", command=Append_all_data
    )
    appendAllButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
    popup.pack(side=tkinter.TOP)
    cell_props = self.Cell_props[self.activeImage]
    analysis_params = self.analysis_params[self.activeImage].copy()
    # pheno_available = np.unique(np.hstack(cell_props['Phenotypes'][:]))
    pheno_available = [i for i in analysis_params["Phenotypes"].keys()]
    pheno_available = np.append(pheno_available, "All")
    pheno_available = np.append(pheno_available, "Everything")
    seg_available = []
    if len(cell_props) > 0:
        seg_available1 = np.unique(np.hstack(cell_props["Segments"][:]))
        for i in seg_available1:
            seg_available.append(i)
    for tissue_props in self.Tissue_props[self.activeImage].keys():
        tissue_props = self.Tissue_props[self.activeImage][tissue_props]
        seg_available1 = np.unique(np.hstack(tissue_props["Segments"][:]))
        for i in seg_available1:
            seg_available.append(i)
    seg_available = np.unique(seg_available)
    seg_available = np.append(seg_available, "Anywhere")
    logicle_vars = ["and", "or", "and not", "or  not"]
    NNA_vars = ["distance to", "within", "distance to score", "within score"]
    if len(self.dataParams) != 0:
        # addPhenoButton = []
        for i in range(len(self.dataParams)):
            data_int = self.dataParams[i]
            if data_int[0] == 0:
                internal_windows = tkinter.Frame(self.popup, width=200, height=10)
                internal_windows.pack(side=tkinter.TOP)
                data_int[1] = internal_windows
                internal_windows1 = tkinter.Frame(internal_windows)
                internal_windows1.pack(side=tkinter.LEFT)
                data_int[2] = internal_windows1
                pheno_variable1 = tkinter.StringVar(internal_windows1)
                pheno_variable1.set(data_int[3].get())
                data_int[3] = pheno_variable1
                x_var_pointer1 = tkinter.OptionMenu(
                    internal_windows1, pheno_variable1, *pheno_available
                )
                x_var_pointer1.config(width=10)
                x_var_pointer1.pack(side=tkinter.LEFT)
                label = ttkinter.Label(internal_windows, text="in")
                data_int[4] = pheno_variable1.get()
                label.pack(side=tkinter.LEFT)
                x_variable2 = tkinter.StringVar(internal_windows)
                x_variable2.set(data_int[5].get())
                data_int[5] = x_variable2
                x_var_pointer2 = tkinter.OptionMenu(
                    internal_windows, x_variable2, *seg_available
                )
                x_var_pointer2.config(width=10)
                x_var_pointer2.pack(side=tkinter.LEFT)
                data_int[6] = x_var_pointer2
                data_int[7] = x_variable2.get()
                addPhenoButton_int(internal_windows, i)
                for j in range(10, len(data_int), 4):
                    logicle_int = data_int[j].get()
                    pheno_var = data_int[j + 2].get()
                    internal_windows = data_int[2]
                    logicle_variable1 = tkinter.StringVar(internal_windows)
                    logicle_variable1.set(logicle_int)
                    data_int[j] = logicle_variable1
                    x_log_pointer1 = tkinter.OptionMenu(
                        internal_windows, logicle_variable1, *logicle_vars
                    )
                    x_log_pointer1.config(width=10)
                    x_log_pointer1.pack(side=tkinter.LEFT)
                    data_int[j + 1] = logicle_variable1.get()
                    pheno_variable1 = tkinter.StringVar(internal_windows)
                    pheno_variable1.set(pheno_var)
                    data_int[j + 2] = pheno_variable1
                    x_var_pointer1 = tkinter.OptionMenu(
                        internal_windows, pheno_variable1, *pheno_available
                    )
                    x_var_pointer1.config(width=10)
                    x_var_pointer1.pack(side=tkinter.LEFT)
                    data_int[j + 3] = pheno_variable1.get()
                self.dataParams[i] = data_int
            else:
                internal_windows = tkinter.Frame(self.popup, width=200, height=10)
                internal_windows.pack(side=tkinter.TOP)
                data_int[1] = internal_windows
                internal_windows1 = tkinter.Frame(internal_windows)
                internal_windows1.pack(side=tkinter.LEFT)
                data_int[2] = internal_windows1
                internal_windows2 = tkinter.Frame(internal_windows)
                internal_windows2.pack(side=tkinter.LEFT)
                data_int[3] = internal_windows2
                pheno_variable1 = tkinter.StringVar(internal_windows1)
                pheno_variable1.set(data_int[4].get())
                data_int[4] = pheno_variable1
                x_var_pointer1 = tkinter.OptionMenu(
                    internal_windows1, pheno_variable1, *pheno_available
                )
                x_var_pointer1.config(width=5)
                x_var_pointer1.pack(side=tkinter.LEFT)
                data_int[5] = pheno_variable1.get()

                NNA_variable = tkinter.StringVar(internal_windows2)
                NNA_variable.set(data_int[6].get())
                data_int[6] = NNA_variable
                NNA_pointer = tkinter.OptionMenu(
                    internal_windows2, NNA_variable, *NNA_vars
                )
                NNA_pointer.config(width=5)
                NNA_pointer.pack(side=tkinter.LEFT)
                data_int[7] = NNA_pointer
                data_int[8] = NNA_variable.get()

                NNA_dist_variable = tkinter.StringVar(internal_windows2)
                NNA_dist_variable.set(data_int[9].get())
                NNA_dist = tkinter.Entry(
                    internal_windows2, textvariable=NNA_dist_variable
                )
                NNA_dist.config(width=5)
                NNA_dist.pack(side=tkinter.LEFT)
                data_int[9] = NNA_dist_variable

                pheno_variable2 = tkinter.StringVar(internal_windows2)
                pheno_variable2.set(data_int[10].get())
                data_int[10] = pheno_variable2
                x_var_pointer2 = tkinter.OptionMenu(
                    internal_windows2, pheno_variable2, *pheno_available
                )
                x_var_pointer2.config(width=5)
                x_var_pointer2.pack(side=tkinter.LEFT)
                data_int[11] = pheno_variable2.get()

                label = ttkinter.Label(internal_windows, text="in")
                label.pack(side=tkinter.LEFT)
                x_variable2 = tkinter.StringVar(internal_windows)
                x_variable2.set(data_int[12].get())
                data_int[12] = x_variable2
                x_var_pointer3 = tkinter.OptionMenu(
                    internal_windows, x_variable2, *seg_available
                )
                x_var_pointer3.config(width=5)
                x_var_pointer3.pack(side=tkinter.LEFT)
                data_int[13] = x_var_pointer3
                data_int[14] = x_variable2.get()
                addPhenoButton_int(internal_windows, i, 0)
                addPhenoButton_int(internal_windows, i, 1)
                for j in range(18, len(data_int), 5):
                    window_n = data_int[j]
                    logicle_int = data_int[j + 1].get()
                    pheno_var = data_int[j + 3].get()
                    internal_windows = data_int[window_n + 2]
                    logicle_variable1 = tkinter.StringVar(internal_windows)
                    logicle_variable1.set(logicle_int)
                    data_int[j + 1] = logicle_variable1
                    x_log_pointer1 = tkinter.OptionMenu(
                        internal_windows, logicle_variable1, *logicle_vars
                    )
                    x_log_pointer1.config(width=5)
                    x_log_pointer1.pack(side=tkinter.LEFT)
                    data_int[j + 2] = logicle_variable1.get()
                    pheno_variable1 = tkinter.StringVar(internal_windows)
                    pheno_variable1.set(pheno_var)
                    data_int[j + 3] = pheno_variable1
                    x_var_pointer1 = tkinter.OptionMenu(
                        internal_windows, pheno_variable1, *pheno_available
                    )
                    x_var_pointer1.config(width=5)
                    x_var_pointer1.pack(side=tkinter.LEFT)
                    data_int[j + 4] = pheno_variable1.get()
                self.dataParams[i] = data_int
    else:
        internal_windows = tkinter.Frame(self.popup, width=200, height=10)
        internal_windows.pack(side=tkinter.TOP)
        data_int = []
        data_int.append(0)
        data_int.append(internal_windows)
        internal_windows1 = tkinter.Frame(internal_windows)
        internal_windows1.pack(side=tkinter.LEFT)
        data_int.append(internal_windows1)
        pheno_variable1 = tkinter.StringVar(internal_windows1)
        pheno_variable1.set(pheno_available[-1])
        data_int.append(pheno_variable1)
        x_var_pointer1 = tkinter.OptionMenu(
            internal_windows1, pheno_variable1, *pheno_available
        )
        x_var_pointer1.config(width=10)
        x_var_pointer1.pack(side=tkinter.LEFT)
        label = ttkinter.Label(internal_windows, text="in")
        data_int.append(pheno_variable1.get())
        label.pack(side=tkinter.LEFT)
        x_variable2 = tkinter.StringVar(internal_windows)
        x_variable2.set(seg_available[-1])
        data_int.append(x_variable2)
        x_var_pointer2 = tkinter.OptionMenu(
            internal_windows, x_variable2, *seg_available
        )
        x_var_pointer2.config(width=10)
        x_var_pointer2.pack(side=tkinter.LEFT)
        data_int.append(x_var_pointer2)
        data_int.append(x_variable2.get())
        addPhenoButton = ttkinter.Button(
            internal_windows,
            text="Add Phenotype",
            command=lambda: [addPheno(data_int[9])],
        )
        addPhenoButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        data_int.append(addPhenoButton)
        data_int.append(0)
        self.dataParams.append(data_int)


def Get_cell_props(self, external_use=False):
    im_raw = np.array(self.im_raw[self.activeImage])
    n_channels = self.n_channels[self.activeImage]
    analyze_index = self.analyze_index[self.activeImage]
    im_analyzed = self.im_analyzed[self.activeImage]
    single_cells = im_analyzed[analyze_index.index("Nuclei")]
    voronoi_image = im_analyzed[analyze_index.index("Cells")]
    analysis_params = self.analysis_params[self.activeImage].copy()
    Channel_pointers = self.Channel_pointers[self.activeImage]
    Segment_keys = list(analysis_params["Segments"].keys())
    Speck_analysis = 0
    Speck_segs = []
    Speck_images = []
    for SegName in Segment_keys:
        if "filter_1" in analysis_params["Segments"][SegName]:
            if analysis_params["Segments"][SegName]["Visible"]:
                Speck_analysis = Speck_analysis + 1
                Speck_segs.append(SegName)
                filter_im = im_analyzed[analyze_index.index(SegName)]
                Speck_images.append(filter_im)
            else:
                ch_name = analysis_params["Segments"][SegName]["Ch_name"]
                filter_ch = Channel_pointers.index(ch_name)
                im_raw[:, :, filter_ch] = iMO.FilterImage(self, mode=1, segName=SegName)

        elif "Speck" in analysis_params["Segments"][SegName]:
            if analysis_params["Segments"][SegName]["Speck"] > 0:
                Speck_analysis = Speck_analysis + 1
                Speck_segs.append(SegName)
                speck_im = im_analyzed[analyze_index.index(SegName)]
                if analysis_params["Segments"][SegName]["Speck"] == 1:
                    Speck_temp = speck_im * 0
                    speck_im = skimage.measure.label(speck_im)
                    speck_objects = ndi.find_objects(speck_im)
                    for i, s1 in enumerate(speck_objects):
                        if s1 is None:
                            continue
                        label = i + 1
                        im_temp = speck_im[s1] == label
                        indices = np.nonzero(im_temp)
                        coords = np.vstack(
                            [indices[i] + s1[i].start for i in range(2)]
                        ).T
                        speck_centroid = tuple(coords.mean(axis=0))
                        Speck_temp[int(speck_centroid[0]), int(speck_centroid[1])] = 1
                else:
                    Speck_temp = speck_im
                Speck_images.append(Speck_temp)

    single_objects = ndi.find_objects(single_cells)
    nucleus_areas = []
    nucleus_perim = []
    nucleus_centroids = []
    nucleus_eccentricity = []
    nucleus_equiv_diam = []
    nucleus_mj_ax = []
    nucleus_mn_ax = []
    nucleus_orientation = []
    perimeter_weights = np.zeros(50, dtype=np.double)
    perimeter_weights[[5, 7, 15, 17, 25, 27]] = 1
    perimeter_weights[[21, 33]] = (2) ** (0.5)
    perimeter_weights[[13, 23]] = (1 + ((2) ** (0.5))) / 2
    max_I_n = []
    mean_I_n = []
    min_I_n = []
    sum_I_n = []
    std_I_n = []
    nucleus_index = []
    n_cells_missing = 0
    for i, s1 in enumerate(single_objects):
        if s1 is None:
            nucleus_areas.append([])
            nucleus_perim.append([])
            nucleus_centroids.append([])
            nucleus_eccentricity.append([])
            nucleus_equiv_diam.append([])
            nucleus_mj_ax.append([])
            nucleus_mn_ax.append([])
            nucleus_orientation.append([])
            max_I_n.append([])
            mean_I_n.append([])
            min_I_n.append([])
            sum_I_n.append([])
            std_I_n.append([])
            # n_cells_missing += 1
            continue
        label = i + 1
        im_temp = single_cells[s1] == label
        nucleus_index.append(label - n_cells_missing)
        i -= n_cells_missing
        indices = np.nonzero(im_temp)
        coords = np.vstack([indices[j] + s1[j].start for j in range(2)]).T
        nucleus_centroids.append(tuple(coords.mean(axis=0)))
        nucleus_areas.append(np.sum(im_temp))
        mu = skimage.measure.moments_central(im_temp.astype(np.uint8))
        a = mu[2, 0] / mu[0, 0]
        b = mu[1, 1] / mu[0, 0]
        c = mu[0, 2] / mu[0, 0]
        # eigen values of inertia tensor
        l1 = (a + c) / 2 + ((4 * b**2 + (a - c) ** 2) ** (0.5)) / 2
        l2 = (a + c) / 2 - ((4 * b**2 + (a - c) ** 2) ** (0.5)) / 2
        if l1 == 0:
            nucleus_eccentricity.append(0)
        else:
            nucleus_eccentricity.append((1 - l2 / l1) ** (0.5))
        nucleus_mj_ax.append(4 * ((l1) ** (0.5)))
        nucleus_mn_ax.append(4 * ((l2) ** (0.5)))
        b = -b
        if a - c == 0:
            if b > 0:
                nucleus_orientation.append(-PI / 4.0)
            else:
                nucleus_orientation.append(PI / 4.0)
        else:
            nucleus_orientation.append(-0.5 * atan2(2 * b, (a - c)))
        nucleus_equiv_diam.append((4 * nucleus_areas[-1] / PI) ** (0.5))
        max_I_n.append(np.zeros(n_channels + Speck_analysis))
        mean_I_n.append(np.zeros(n_channels + Speck_analysis))
        min_I_n.append(np.zeros(n_channels + Speck_analysis))
        sum_I_n.append(np.zeros(n_channels + Speck_analysis))
        std_I_n.append(np.zeros(n_channels + Speck_analysis))
        for n_ch in range(n_channels):
            im_I = im_raw[:, :, n_ch]
            im_I_temp = im_I[s1] * im_temp
            max_I_n[-1][n_ch] = np.max(im_I_temp[im_temp])
            mean_I_n[-1][n_ch] = np.mean(im_I_temp[im_temp])
            min_I_n[-1][n_ch] = np.min(im_I_temp[im_temp])
            sum_I_n[-1][n_ch] = np.sum(im_I_temp[im_temp])
            std_I_n[-1][n_ch] = np.std(im_I_temp[im_temp])
        for n_sp in range(Speck_analysis):
            im_I = Speck_images[n_sp]
            im_I_temp = im_I[s1] * im_temp
            max_I_n[-1][n_channels + n_sp] = np.max(im_I_temp[im_temp])
            mean_I_n[-1][n_channels + n_sp] = np.mean(im_I_temp[im_temp])
            min_I_n[-1][n_channels + n_sp] = np.min(im_I_temp[im_temp])
            sum_I_n[-1][n_channels + n_sp] = np.sum(im_I_temp[im_temp])
            std_I_n[-1][n_channels + n_sp] = np.std(im_I_temp[im_temp])
        nucleus_perim.append(
            np.dot(
                np.bincount(
                    ndi.convolve(
                        im_temp.astype(np.uint8)
                        - ndi.binary_erosion(
                            im_temp.astype(np.uint8),
                            np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8),
                            border_value=0,
                        ),
                        np.array([[10, 2, 10], [2, 1, 2], [10, 2, 10]]),
                        mode="constant",
                        cval=0,
                    ).ravel(),
                    minlength=50,
                ),
                perimeter_weights,
            )
        )
    voronoi_objects = ndi.find_objects(voronoi_image)
    im_all_cells = np.zeros((single_cells.shape[0], single_cells.shape[1]), dtype=bool)
    for n_i in nucleus_index:
        i = np.uint32(np.round(nucleus_centroids[n_i - 1]))
        im_all_cells[i[0], i[1]] = 1
    im_all_cells = ndi.distance_transform_edt(im_all_cells == 0) <= 5
    if "All Cells" in analyze_index:
        im_analyzed[analyze_index.index("All Cells")] = im_all_cells
        self.im_analyzed[self.activeImage] = im_analyzed
    else:
        im_analyzed.append(im_all_cells)
        analyze_index.append("All Cells")
        self.im_analyzed[self.activeImage] = im_analyzed
        self.analyze_index[self.activeImage] = analyze_index
        self.remake_side_window()
    cell_areas = []
    cell_perim = []
    cell_centroids = []
    cell_eccentricity = []
    cell_equiv_diam = []
    cell_mj_ax = []
    cell_mn_ax = []
    cell_orientation = []
    max_I = []
    mean_I = []
    min_I = []
    sum_I = []
    std_I = []
    cell_index = []
    nucleus_index = []
    n_cells_missing = 0
    for i, s1 in enumerate(voronoi_objects):
        if s1 is None:
            n_cells_missing += 1
            continue
        label = i + 1
        im_temp = voronoi_image[s1] == label
        cell_index.append(label - n_cells_missing)
        im_nuc_temp = single_cells[s1]
        im_nuc_temp = im_nuc_temp[im_temp]
        nucleus_index.append(im_nuc_temp.max() - 1)
        indices = np.nonzero(im_temp)
        coords = np.vstack([indices[i] + s1[i].start for i in range(2)]).T
        cell_centroids.append(tuple(coords.mean(axis=0)))
        cell_areas.append(np.sum(im_temp))
        mu = skimage.measure.moments_central(im_temp.astype(np.uint8))
        a = mu[2, 0] / mu[0, 0]
        b = mu[1, 1] / mu[0, 0]
        c = mu[0, 2] / mu[0, 0]
        # eigen values of inertia tensor
        l1 = (a + c) / 2 + ((4 * b**2 + (a - c) ** 2) ** (0.5)) / 2
        l2 = (a + c) / 2 - ((4 * b**2 + (a - c) ** 2) ** (0.5)) / 2
        if l1 == 0:
            cell_eccentricity.append(0)
        else:
            cell_eccentricity.append((1 - l2 / l1) ** (0.5))
        cell_mj_ax.append(4 * ((l1) ** (0.5)))
        cell_mn_ax.append(4 * ((l2) ** (0.5)))
        b = -b
        if a - c == 0:
            if b > 0:
                cell_orientation.append(-PI / 4.0)
            else:
                cell_orientation.append(PI / 4.0)
        else:
            cell_orientation.append(-0.5 * atan2(2 * b, (a - c)))
        cell_equiv_diam.append((4 * cell_areas[-1] / PI) ** (0.5))
        max_I.append(np.zeros(n_channels + Speck_analysis))
        mean_I.append(np.zeros(n_channels + Speck_analysis))
        min_I.append(np.zeros(n_channels + Speck_analysis))
        sum_I.append(np.zeros(n_channels + Speck_analysis))
        std_I.append(np.zeros(n_channels + Speck_analysis))
        for n_ch in range(n_channels):
            im_I = im_raw[:, :, n_ch]
            im_I_temp = im_I[s1] * im_temp
            max_I[-1][n_ch] = np.max(im_I_temp[im_temp])
            mean_I[-1][n_ch] = np.mean(im_I_temp[im_temp])
            min_I[-1][n_ch] = np.min(im_I_temp[im_temp])
            sum_I[-1][n_ch] = np.sum(im_I_temp[im_temp])
            std_I[-1][n_ch] = np.std(im_I_temp[im_temp])
        for n_sp in range(Speck_analysis):
            im_I = Speck_images[n_sp]
            im_I_temp = im_I[s1] * im_temp
            max_I[-1][n_channels + n_sp] = np.max(im_I_temp[im_temp])
            mean_I[-1][n_channels + n_sp] = np.mean(im_I_temp[im_temp])
            min_I[-1][n_channels + n_sp] = np.min(im_I_temp[im_temp])
            sum_I[-1][n_channels + n_sp] = np.sum(im_I_temp[im_temp])
            std_I[-1][n_channels + n_sp] = np.std(im_I_temp[im_temp])

        cell_perim.append(
            np.dot(
                np.bincount(
                    ndi.convolve(
                        im_temp.astype(np.uint8)
                        - ndi.binary_erosion(
                            im_temp.astype(np.uint8),
                            np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8),
                            border_value=0,
                        ),
                        np.array([[10, 2, 10], [2, 1, 2], [10, 2, 10]]),
                        mode="constant",
                        cval=0,
                    ).ravel(),
                    minlength=50,
                ),
                perimeter_weights,
            )
        )
    cell_index = pd.Index(cell_index, name="cell number")
    nucleus_areas = [nucleus_areas[i] for i in nucleus_index]
    nucleus_perim = [nucleus_perim[i] for i in nucleus_index]
    nucleus_centroids = [nucleus_centroids[i] for i in nucleus_index]
    nucleus_eccentricity = [nucleus_eccentricity[i] for i in nucleus_index]
    nucleus_equiv_diam = [nucleus_equiv_diam[i] for i in nucleus_index]
    nucleus_mj_ax = [nucleus_mj_ax[i] for i in nucleus_index]
    nucleus_mn_ax = [nucleus_mn_ax[i] for i in nucleus_index]
    nucleus_orientation = [nucleus_orientation[i] for i in nucleus_index]
    max_I_n = [max_I_n[i] for i in nucleus_index]
    mean_I_n = [mean_I_n[i] for i in nucleus_index]
    min_I_n = [min_I_n[i] for i in nucleus_index]
    sum_I_n = [sum_I_n[i] for i in nucleus_index]
    std_I_n = [std_I_n[i] for i in nucleus_index]

    cytoplasm_areas = []
    cytoplasm_perim = []
    cytoplasm_centroids = []
    cytoplasm_eccentricity = []
    cytoplasm_equiv_diam = []
    cytoplasm_mj_ax = []
    cytoplasm_mn_ax = []
    cytoplasm_orientation = []
    max_I_c = []
    mean_I_c = []
    min_I_c = []
    sum_I_c = []
    std_I_c = []
    n_cells_missing = 0
    for i, s1 in enumerate(voronoi_objects):
        if s1 is None:
            n_cells_missing += 1
            continue
        label = i + 1
        im_temp = voronoi_image[s1] == label
        im_nuc_temp = single_cells[s1]
        im_nuc_temp = im_nuc_temp == im_nuc_temp[im_temp].max()
        im_temp[im_nuc_temp] = False
        indices = np.nonzero(im_temp)
        if np.sum(im_temp) < 1:
            indices = np.nonzero(im_nuc_temp)
            coords = np.vstack([indices[i] + s1[i].start for i in range(2)]).T
            cytoplasm_centroids.append(tuple(coords.mean(axis=0)))
            cytoplasm_areas.append(0)
            cytoplasm_eccentricity.append(0)
            cytoplasm_mj_ax.append(0)
            cytoplasm_mn_ax.append(0)
            cytoplasm_orientation.append(0)
            cytoplasm_equiv_diam.append(0)
            max_I_c.append(np.zeros(n_channels + Speck_analysis))
            mean_I_c.append(np.zeros(n_channels + Speck_analysis))
            min_I_c.append(np.zeros(n_channels + Speck_analysis))
            sum_I_c.append(np.zeros(n_channels + Speck_analysis))
            std_I_c.append(np.zeros(n_channels + Speck_analysis))
            cytoplasm_perim.append(0)
            continue
        coords = np.vstack([indices[i] + s1[i].start for i in range(2)]).T
        cytoplasm_centroids.append(tuple(coords.mean(axis=0)))
        cytoplasm_areas.append(np.sum(im_temp))
        mu = skimage.measure.moments_central(im_temp.astype(np.uint8))
        a = mu[2, 0] / mu[0, 0]
        b = mu[1, 1] / mu[0, 0]
        c = mu[0, 2] / mu[0, 0]
        # eigen values of inertia tensor
        l1 = (a + c) / 2 + ((4 * b**2 + (a - c) ** 2) ** (0.5)) / 2
        l2 = (a + c) / 2 - ((4 * b**2 + (a - c) ** 2) ** (0.5)) / 2
        if l1 == 0:
            cytoplasm_eccentricity.append(0)
        else:
            cytoplasm_eccentricity.append((1 - l2 / l1) ** (0.5))
        cytoplasm_mj_ax.append(4 * ((l1) ** (0.5)))
        cytoplasm_mn_ax.append(4 * ((l2) ** (0.5)))
        b = -b
        if a - c == 0:
            if b > 0:
                cytoplasm_orientation.append(-PI / 4.0)
            else:
                cytoplasm_orientation.append(PI / 4.0)
        else:
            cytoplasm_orientation.append(-0.5 * atan2(2 * b, (a - c)))
        cytoplasm_equiv_diam.append((4 * cytoplasm_areas[-1] / PI) ** (0.5))
        max_I_c.append(np.zeros(n_channels + Speck_analysis))
        mean_I_c.append(np.zeros(n_channels + Speck_analysis))
        min_I_c.append(np.zeros(n_channels + Speck_analysis))
        sum_I_c.append(np.zeros(n_channels + Speck_analysis))
        std_I_c.append(np.zeros(n_channels + Speck_analysis))
        for n_ch in range(n_channels):
            im_I = im_raw[:, :, n_ch]
            im_I_temp = im_I[s1] * im_temp
            max_I_c[-1][n_ch] = np.max(im_I_temp[im_temp])
            mean_I_c[-1][n_ch] = np.mean(im_I_temp[im_temp])
            min_I_c[-1][n_ch] = np.min(im_I_temp[im_temp])
            sum_I_c[-1][n_ch] = np.sum(im_I_temp[im_temp])
            std_I_c[-1][n_ch] = np.std(im_I_temp[im_temp])
        for n_sp in range(Speck_analysis):
            im_I = Speck_images[n_sp]
            im_I_temp = im_I[s1] * im_temp
            max_I_c[-1][n_channels + n_sp] = np.max(im_I_temp[im_temp])
            mean_I_c[-1][n_channels + n_sp] = np.mean(im_I_temp[im_temp])
            min_I_c[-1][n_channels + n_sp] = np.min(im_I_temp[im_temp])
            sum_I_c[-1][n_channels + n_sp] = np.sum(im_I_temp[im_temp])
            std_I_c[-1][n_channels + n_sp] = np.std(im_I_temp[im_temp])

        cytoplasm_perim.append(
            np.dot(
                np.bincount(
                    ndi.convolve(
                        im_temp.astype(np.uint8)
                        - ndi.binary_erosion(
                            im_temp.astype(np.uint8),
                            np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8),
                            border_value=0,
                        ),
                        np.array([[10, 2, 10], [2, 1, 2], [10, 2, 10]]),
                        mode="constant",
                        cval=0,
                    ).ravel(),
                    minlength=50,
                ),
                perimeter_weights,
            )
        )

    cell_props = pd.DataFrame(
        {
            "Cell Area": cell_areas,
            "Cell Perimeter": cell_perim,
            "Cell Centroid": cell_centroids,
            "Cell Eccentricity": cell_eccentricity,
            "Cell Equivalent Diameter": cell_equiv_diam,
            "Cell Major Axis Length": cell_mj_ax,
            "Cell Minor Axis Length": cell_mn_ax,
            "Cell Orientation": cell_orientation,
            "Cell Fluorescent Maximum Intensity": max_I,
            "Cell Fluorescent Mean Intensity": mean_I,
            "Cell Fluorescent Minimum Intensity": min_I,
            "Cell Fluorescent Total Intensity": sum_I,
            "Cell Fluorescent STD Intensity": std_I,
            "Cytoplasm Area": cytoplasm_areas,
            "Cytoplasm Perimeter": cytoplasm_perim,
            "Cytoplasm Centroid": cytoplasm_centroids,
            "Cytoplasm Eccentricity": cytoplasm_eccentricity,
            "Cytoplasm Equivalent Diameter": cytoplasm_equiv_diam,
            "Cytoplasm Major Axis Length": cytoplasm_mj_ax,
            "Cytoplasm Minor Axis Length": cytoplasm_mn_ax,
            "Cytoplasm Orientation": cytoplasm_orientation,
            "Cytoplasm Fluorescent Maximum Intensity": max_I_c,
            "Cytoplasm Fluorescent Mean Intensity": mean_I_c,
            "Cytoplasm Fluorescent Minimum Intensity": min_I_c,
            "Cytoplasm Fluorescent Total Intensity": sum_I_c,
            "Cytoplasm Fluorescent STD Intensity": std_I_c,
            "Nucleus Area": nucleus_areas,
            "Nucleus Perimeter": nucleus_perim,
            "Nucleus Centroid": nucleus_centroids,
            "Nucleus Eccentricity": nucleus_eccentricity,
            "Nucleus Equivalent Diameter": nucleus_equiv_diam,
            "Nucleus Major Axis Length": nucleus_mj_ax,
            "Nucleus Minor Axis Length": nucleus_mn_ax,
            "Nucleus Orientation": nucleus_orientation,
            "Nucleus Fluorescent Maximum Intensity": max_I_n,
            "Nucleus Fluorescent Mean Intensity": mean_I_n,
            "Nucleus Fluorescent Minimum Intensity": min_I_n,
            "Nucleus Fluorescent Total Intensity": sum_I_n,
            "Nucleus Fluorescent STD Intensity": std_I_n,
            "Segments": [["All"] for _ in range(np.size(cell_areas))],
            "Phenotypes": [["All"] for _ in range(np.size(cell_areas))],
            "Show Data": np.ones_like(cell_areas),
        },
        index=cell_index,
    )
    segment_list = cell_props["Segments"][:].tolist()
    im_all_cells = im_analyzed[analyze_index.index("All Cells")]
    nucleus_centroids = np.uint32(np.round(cell_props["Nucleus Centroid"][:].tolist()))
    segment_thres_name = ["Tumor+", "Stroma+"]
    if "Tumor" in analyze_index:
        Tumor_mask = im_analyzed[analyze_index.index("Tumor")]
        if "Stroma" in analyze_index:
            Stroma_mask = im_analyzed[analyze_index.index("Stroma")]
        else:
            Stroma_mask = Tumor_mask == 0
    elif "Stroma" in analyze_index:
        Stroma_mask = im_analyzed[analyze_index.index("Stroma")]
        Tumor_mask = Stroma_mask == 0
    else:
        Stroma_mask = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        Tumor_mask = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        segment_thres_name = []
    for i in range(np.size(segment_list)):
        if Tumor_mask[nucleus_centroids[i][0], nucleus_centroids[i][1]] == 1:
            segment_list[i].append("Tumor+")
        elif Stroma_mask[nucleus_centroids[i][0], nucleus_centroids[i][1]] == 1:
            segment_list[i].append("Stroma+")
    for pointer_temp in segment_thres_name:
        im_selected_cells = np.zeros(
            (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
        )
        for i in range(np.shape(segment_list)[0]):
            if pointer_temp in segment_list[i]:
                im_selected_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
        im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
        if pointer_temp in analyze_index:
            im_analyzed[analyze_index.index(pointer_temp)] = im_selected_cells
        else:
            im_analyzed.append(im_selected_cells)
            analyze_index.append(pointer_temp)
    self.Cell_props[self.activeImage] = cell_props
    self.analyze_index[self.activeImage] = analyze_index
    self.im_analyzed[self.activeImage] = im_analyzed


def QuickAnalysisLike(self):
    def QuickIntAnalysisLike2(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = ttkinter.Label(
            popup2, text="You are about to overwrite all your" + " current analysis"
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = ttkinter.Button(
            popup2,
            text="Okay",
            command=lambda: [DestroyTK(popup2), QuickAnalysisLikeSure(self)],
        )
        B1.pack()
        B2 = ttkinter.Button(
            popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
        )
        B2.pack()
        popup2.mainloop()

    def get_tick_values(*args):
        ImagePointer = active_image.get()
        n_start = 1
        n_end = 1
        while True:
            if any(
                x in ImagePointer[n_end]
                for x in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
            ):
                n_end = n_end + 1
            else:
                break
        self.Analysis_like = np.int32(ImagePointer[n_start:n_end])

    popup = tkinter.Tk()
    active_image = tkinter.StringVar(popup)
    active_image.set(
        "(" + str(self.activeImage) + ", " + self.FileDictionary[self.activeImage] + ")"
    )
    active_image.trace("w", get_tick_values)
    w = tkinter.OptionMenu(popup, active_image, *self.FileDictionary.items())
    w.pack(side=tkinter.TOP)
    folderButton = ttkinter.Button(
        popup,
        text="Confirm",
        command=lambda: [get_tick_values(), DestroyTK(popup), QuickIntAnalysisLike2()],
    )
    folderButton.pack()
    popup.mainloop()

    def QuickAnalysisSure(*a):
        self.im_analyzed[self.activeImage] = []
        im_analyzed = self.im_analyzed[self.activeImage]
        im_raw = self.im_raw[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        n_channels = self.n_channels[self.activeImage]
        Color_pointers = self.Color_pointers[self.activeImage].copy()[0:n_channels]
        Channel_pointers = self.Channel_pointers[self.activeImage].copy()[0:n_channels]
        channel_variable = self.channel_variable[self.activeImage].copy()[0:n_channels]
        color_variable = self.color_variable[self.activeImage].copy()[0:n_channels]
        if "ROI" in analyze_index:
            im_analyzed.append(self.activeROI)
            color_variable.append(
                self.color_variable[self.activeImage][
                    analyze_index.index("ROI") + n_channels
                ]
            )
            Color_pointers.append(
                self.Color_pointers[self.activeImage][
                    analyze_index.index("ROI") + n_channels
                ]
            )
            self.analyze_index[self.activeImage] = []
            self.analyze_index[self.activeImage].append("ROI")
        else:
            self.analyze_index[self.activeImage] = []
        self.Color_pointers[self.activeImage] = Color_pointers
        self.Channel_pointers[self.activeImage] = Channel_pointers
        self.channel_variable[self.activeImage] = channel_variable
        self.color_variable[self.activeImage] = color_variable
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        fore_thres = [np.zeros(n_channels), np.full(n_channels, np.inf)]
        fore_thres[0][Channel_pointers.index("DAPI")] = np.float(
            self.QuickParams_Fore.get()
        )
        self.foreground_threshold[self.activeImage] = fore_thres
        for i in range(n_channels):
            if (fore_thres[0][i] != 0) | (fore_thres[1][i] < np.inf):
                im_temp = (im_temp) | (
                    ((im_raw[:, :, i]) >= fore_thres[0][i])
                    & ((im_raw[:, :, i]) <= fore_thres[1][i])
                )
        # im_temp = ndi.morphology.binary_opening(im_temp)
        analyze_index = self.analyze_index[self.activeImage]
        analyze_index.append("Foreground")
        Fore_mask = im_temp > 0
        Fore_labels = skimage.measure.label(Fore_mask)
        Fore_objects = ndi.find_objects(Fore_labels)
        Fore_area = []
        for i, s1 in enumerate(Fore_objects):
            if s1 is None:
                continue
            label = i + 1
            Fore_area.append(np.sum(Fore_labels[s1] == label))
        Fore_area = np.array(Fore_area)
        Back_mask = Fore_mask == 0
        Back_labels = skimage.measure.label(Back_mask)
        Back_objects = ndi.find_objects(Back_labels)
        Back_area = []
        for i, s1 in enumerate(Back_objects):
            if s1 is None:
                continue
            label = i + 1
            Back_area.append(np.sum(Fore_labels[s1] == label))
        Back_area = np.array(Back_area)
        hole_lower_limit = np.float(self.QuickParams_Hole.get())
        if hole_lower_limit <= 1:
            hole_lower_limit = hole_lower_limit * Back_area.max()
        fore_lower_limit = np.float(self.QuickParams_Feat.get())
        if fore_lower_limit <= 1:
            fore_lower_limit = fore_lower_limit * Fore_area.max()
        self.HoleLimits = [hole_lower_limit, np.inf]
        self.ForeLimits = [fore_lower_limit, np.inf]
        for i, s1 in enumerate(Fore_objects):
            if s1 is None:
                continue
            label = i + 1
            region_area = np.sum(Fore_labels[s1] == label)
            if region_area < self.ForeLimits[0]:
                Fore_mask[s1][Fore_labels[s1] == label] = 0
            elif region_area > self.ForeLimits[1]:
                Fore_mask[s1][Fore_labels[s1] == label] = 0
        Back_mask = Fore_mask == 0
        Back_labels = skimage.measure.label(Back_mask)
        Back_objects = ndi.find_objects(Back_labels)
        for i, s1 in enumerate(Back_objects):
            if s1 is None:
                continue
            label = i + 1
            region_area = np.sum(Back_labels[s1] == label)
            if region_area < self.HoleLimits[0]:
                Fore_mask[s1][Back_labels[s1] == label] = 1
            elif region_area > self.HoleLimits[1]:
                Fore_mask[s1][Back_labels[s1] == label] = 1
        im_analyzed.append(Fore_mask)

        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        tumor_thres = [np.zeros(n_channels), np.full(n_channels, np.inf)]
        tumor_thres[0][Channel_pointers.index("CK")] = np.float(
            self.QuickParams_CKthres.get()
        )
        #        fore_thres[0][4] = 0.29
        for i in range(n_channels):
            if (tumor_thres[0][i] > 0) | (tumor_thres[1][i] < np.inf):
                im_temp = (im_temp) | (
                    ((im_raw[:, :, i]) >= tumor_thres[0][i])
                    & ((im_raw[:, :, i]) <= tumor_thres[1][i])
                )
        # im_temp = ndi.morphology.binary_opening(im_temp)
        analyze_index.append("Tumor")
        Tumor_mask = im_temp.copy() > 0
        Tumor_labels = skimage.measure.label(Tumor_mask)
        Tumor_objects = ndi.find_objects(Tumor_labels)
        Tumor_area = []
        for i, s1 in enumerate(Tumor_objects):
            if s1 is None:
                continue
            label = i + 1
            Tumor_area.append(np.sum(Tumor_labels[s1] == label))
        Tumor_area = np.array(Tumor_area)
        for i, s1 in enumerate(Tumor_objects):
            if s1 is None:
                continue
            label = i + 1
            region_area = np.sum(Tumor_labels[s1] == label)
            if region_area < self.HoleLimits[0]:
                Tumor_mask[s1][Tumor_labels[s1] == label] = 0
            elif region_area > self.HoleLimits[1]:
                Tumor_mask[s1][Tumor_labels[s1] == label] = 0
        Stroma_mask = Tumor_mask == 0
        Stroma_labels = skimage.measure.label(Stroma_mask)
        Stroma_objects = ndi.find_objects(Stroma_labels)
        for i, s1 in enumerate(Stroma_objects):
            if s1 is None:
                continue
            label = i + 1
            region_area = np.sum(Stroma_labels[s1] == label)
            if region_area < self.HoleLimits[0]:
                Tumor_mask[s1][Stroma_labels[s1] == label] = 1
            elif region_area > self.HoleLimits[1]:
                Tumor_mask[s1][Stroma_labels[s1] == label] = 1
        Tumor_mask = (Tumor_mask == 1) & (Fore_mask == 1)
        im_analyzed.append(Tumor_mask)
        Stroma_mask = (Tumor_mask == 0) & (Fore_mask == 1)
        analyze_index.append("Stroma")
        im_analyzed.append(Stroma_mask)

        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        DAPI_thres = [np.zeros(n_channels), np.full(n_channels, np.inf)]
        DAPI_thres[0][Channel_pointers.index("DAPI")] = np.float(
            self.QuickParams_DAPIthres.get()
        )
        for i in range(n_channels):
            if (DAPI_thres[0][i] > 0) | (DAPI_thres[1][i] < np.inf):
                im_temp = (im_temp) | (
                    ((im_raw[:, :, i]) >= DAPI_thres[0][i])
                    & ((im_raw[:, :, i]) <= DAPI_thres[1][i])
                )
        analyze_index.append("DAPI")
        DAPI_mask = im_temp.copy() > 0
        im_analyzed.append(DAPI_mask)
        self.NucLimits = [
            np.float(self.QuickParams_NucLow.get()),
            np.float(self.QuickParams_NucHigh.get()),
        ]
        fore_mask_DAPI = Fore_mask.copy()
        if "ROI" in analyze_index:
            fore_mask_DAPI = fore_mask_DAPI & im_analyzed[analyze_index.index("ROI")]
        DAPI_mask = DAPI_mask & fore_mask_DAPI
        DAPI_labels = skimage.measure.label(DAPI_mask)
        DAPI_objects = ndi.find_objects(DAPI_labels)
        single_cells = np.zeros_like(DAPI_labels)
        cell_counter = 0
        cell_clusters = np.zeros_like(DAPI_labels)
        cluster_counter = 0
        for i, s1 in enumerate(DAPI_objects):
            if s1 is None:
                continue
            label = i + 1
            nucleus_area = np.sum(DAPI_labels[s1] == label)
            if nucleus_area > self.NucLimits[0]:
                if nucleus_area > self.NucLimits[1]:
                    cluster_counter = cluster_counter + 1
                    cell_clusters[s1][DAPI_labels[s1] == label] = cluster_counter
                else:
                    cell_counter = cell_counter + 1
                    single_cells[s1][DAPI_labels[s1] == label] = cell_counter
        nearest_neighbor_radius = np.int32(np.ceil(np.sqrt(self.NucLimits[0])))
        ws_dist = ndi.distance_transform_edt(cell_clusters > 0)
        ws_local_maxi = peak_local_max(
            ws_dist,
            indices=False,
            footprint=np.ones((nearest_neighbor_radius, nearest_neighbor_radius)),
            labels=cell_clusters > 0,
        )
        ws_markers = ndi.label(ws_local_maxi)[0]
        cluster_labels = skimage.segmentation.watershed(
            -ws_dist, ws_markers, mask=cell_clusters > 0
        )
        cluster_labels = skimage.measure.label(cluster_labels)
        cluster_objects = ndi.find_objects(cluster_labels)
        for i, s1 in enumerate(cluster_objects):
            if s1 is None:
                continue
            label = i + 1
            nucleus_area = np.sum(cluster_labels[s1] == label)
            if nucleus_area > self.NucLimits[0]:
                if nucleus_area > self.NucLimits[1]:
                    cluster_labels[s1][cluster_labels[s1] == label] = 0
            else:
                cluster_labels[s1][cluster_labels[s1] == label] = 0
        cluster_labels = cluster_labels + single_cells.max()
        cluster_labels[cluster_labels == single_cells.max()] = 0
        single_cells = single_cells + cluster_labels
        single_cells = skimage.measure.label(single_cells)
        single_objects = ndi.find_objects(single_cells)
        nucleus_area = []
        single_cells_mask = np.zeros_like(DAPI_labels) < 0
        for i, s1 in enumerate(single_objects):
            if s1 is None:
                continue
            label = i + 1
            nucleus_area.append(np.sum(single_cells[s1] == label))
            im_temp = single_cells[s1] == label
            im_temp = np.float32(im_temp) - np.float32(
                ndi.morphology.binary_erosion(
                    im_temp, iterations=round(single_cells.shape[0] / 500)
                )
            )
            single_cells_mask[s1][single_cells[s1] == label] = im_temp[
                single_cells[s1] == label
            ]
        nucleus_area = np.array(nucleus_area)
        self.single_cells = single_cells
        voronoi_image = skimage.segmentation.watershed(
            -ndi.distance_transform_edt(single_cells > 0), single_cells
        )
        voronoi_image = skimage.measure.label(voronoi_image)
        voronoi_image = np.uint32(voronoi_image * np.float32(fore_mask_DAPI))
        self.voronoi_image = voronoi_image
        im_analyzed.append(self.single_cells)
        analyze_index.append("Nuclei")
        im_analyzed.append(self.voronoi_image)
        analyze_index.append("Cells")
        self.im_analyzed[self.activeImage] = im_analyzed
        self.analyze_index[self.activeImage] = analyze_index
        Get_cell_props(self)
        cell_props = self.Cell_props[self.activeImage]
        pheno_list = cell_props["Phenotypes"][:].tolist()
        segment_list = cell_props["Segments"][:].tolist()
        im_all_cells = im_analyzed[analyze_index.index("All Cells")]
        nucleus_centroids = np.uint32(
            np.round(cell_props["Nucleus Centroid"][:].tolist())
        )
        pheno_channel_list = []
        pheno_name_list = []
        pheno_thres = []
        pheno_thres_name = []
        for i in range(np.int32(np.size(self.QuickPheno) / 6)):
            pheno_channel_list.append(self.QuickPheno[i * 6 + 2].get())
            pheno_name_list.append(
                self.QuickPheno[i * 6 + 1].get()
                + " Fluorescent "
                + self.QuickPheno[i * 6 + 3].get()
            )
            pheno_thres.append(np.float((self.QuickPheno[i * 6 + 4].get())))
            pheno_thres_name.append(self.QuickPheno[i * 6 + 5].get())
            for j, s1 in enumerate(cell_props[pheno_name_list[i]]):
                if s1[Channel_pointers.index(pheno_channel_list[i])] > pheno_thres[i]:
                    pheno_list[j].append(pheno_thres_name[i])
        for i in range(len(segment_list)):
            segment_list[i] = ["All"]
            if Tumor_mask[nucleus_centroids[i][0], nucleus_centroids[i][1]] == 1:
                segment_list[i].append("Tumor+")
            elif Stroma_mask[nucleus_centroids[i][0], nucleus_centroids[i][1]] == 1:
                segment_list[i].append("Stroma+")
        segment_thres_name = ["Tumor+", "Stroma+"]
        for pointer_temp in pheno_thres_name:
            im_selected_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            for i in range(np.shape(pheno_list)[0]):
                if pointer_temp in pheno_list[i]:
                    im_selected_cells[
                        nucleus_centroids[i][0], nucleus_centroids[i][1]
                    ] = 1
            im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
            im_analyzed.append(im_selected_cells)
            analyze_index.append(pointer_temp)
        for pointer_temp in segment_thres_name:
            im_selected_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            for i in range(np.shape(segment_list)[0]):
                if pointer_temp in segment_list[i]:
                    im_selected_cells[
                        nucleus_centroids[i][0], nucleus_centroids[i][1]
                    ] = 1
            im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
            if pointer_temp in analyze_index:
                im_analyzed[analyze_index.index(pointer_temp)] = im_selected_cells
            else:
                im_analyzed.append(im_selected_cells)
                analyze_index.append(pointer_temp)
        cell_props["Phenotypes"] = pheno_list
        cell_props["Segments"] = segment_list
        self.Cell_props[self.activeImage] = cell_props
        self.remake_side_window()
        DestroyTK(self.popup)


def QuickAnalysisAll(self):
    def QuickAnalysisAllSure(*a):
        self.Analysis_like = self.activeImage
        [popup, label] = popupmsg("...", False)
        for self.activeImage in range(len(self.FileDictionary)):
            label["text"] = (
                "Analyzing image "
                + str(self.activeImage + 1)
                + " of "
                + str(len(self.FileDictionary))
                + " images.\n Please hold."
            )
            popup.update()
            QuickAnalysisLikeSure(self)
        DestroyTK(popup)

    popup2 = tkinter.Tk()
    popup2.wm_title("Are you sure?")
    label = ttkinter.Label(popup2, text="You are about to overwrite all your analysis")
    label.pack(side="top", fill="x", pady=10)
    B1 = ttkinter.Button(
        popup2, text="Okay", command=lambda: [DestroyTK(popup2), QuickAnalysisAllSure()]
    )
    B1.pack()
    B2 = ttkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
    B2.pack()
    popup2.mainloop()


def QuickAnalysisLikeSure(self):
    def Perform_tissue_analysis(tissue_keys):
        for tissue_name in tissue_keys:
            self.Tissue_analysis(tissue_name)

    def Get_tissue_phenotypes(*a):
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        im_all_cells = im_analyzed[0]
        Channel_pointers = self.Channel_pointers[self.activeImage].copy()
        Segment_keys = list(analysis_params["Segments"].keys())
        for SegName in Segment_keys:
            if "filter_1" in analysis_params["Segments"][SegName]:
                if analysis_params["Segments"][SegName]["Visible"]:
                    Channel_pointers.append(SegName)
            if "Speck" in analysis_params["Segments"][SegName]:
                if analysis_params["Segments"][SegName]["Speck"] == 1:
                    Channel_pointers.append(SegName + "-Speck")
                if analysis_params["Segments"][SegName]["Speck"] == 2:
                    Channel_pointers.append(SegName + "-Mask")
        for segName in analysis_params["Phenotypes"].keys():
            tissue_name = []
            for i in analysis_params["Segments"].keys():
                if segName.find(i + " - ") == 0:
                    tissue_name = i
            if len(tissue_name) == 0:
                continue
            segName_short = segName[len(tissue_name) + 3 :]
            tissue_props = self.Tissue_props[self.activeImage][tissue_name]
            pheno_list = tissue_props["Phenotypes"][:].tolist()
            nucleus_centroids = np.uint32(
                np.round(tissue_props["Centroid"][:].tolist())
            )
            if len(nucleus_centroids) == 0:
                continue
            im_selected_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            im_all_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            if analysis_params["Phenotypes"][segName]["x_axis2"] == "Geometry":
                x_data = np.vstack(
                    tissue_props[analysis_params["Phenotypes"][segName]["x_axis3"]]
                )
            else:
                x_data = np.vstack(
                    tissue_props[
                        "Fluorescent "
                        + analysis_params["Phenotypes"][segName]["x_axis3"]
                    ]
                )[
                    :,
                    Channel_pointers.index(
                        analysis_params["Phenotypes"][segName]["x_axis2"]
                    ),
                ]
            if analysis_params["Phenotypes"][segName]["y_axis2"] == "Geometry":
                y_data = np.vstack(
                    tissue_props[analysis_params["Phenotypes"][segName]["y_axis3"]]
                )
            else:
                y_data = np.vstack(
                    tissue_props[
                        "Fluorescent "
                        + analysis_params["Phenotypes"][segName]["y_axis3"]
                    ]
                )[
                    :,
                    Channel_pointers.index(
                        analysis_params["Phenotypes"][segName]["y_axis2"]
                    ),
                ]
            if np.size(analysis_params["Phenotypes"][segName]["positive_area"]) > 0:
                ROI_path = matplotlib.path.Path(
                    analysis_params["Phenotypes"][segName]["positive_area"]
                )
            else:
                ROI_path = []
            hist_spanner_limits = analysis_params["Phenotypes"][segName]["hist_limits"]
            points = np.transpose((x_data.ravel(), y_data.ravel()))
            if np.size(ROI_path) > 0:
                mask = ROI_path.contains_points(points)
                mask = np.nonzero(mask)[0]
            else:
                mask = (points[:, 0] * 0) == 0
                if hist_spanner_limits[0, 0] > 0:
                    mask = (mask) & (points[:, 0] > hist_spanner_limits[0, 0])
                if hist_spanner_limits[1, 0] < np.inf:
                    mask = (mask) & (points[:, 0] < hist_spanner_limits[1, 0])
                if hist_spanner_limits[0, 1] > 0:
                    mask = (mask) & (points[:, 1] > hist_spanner_limits[0, 1])
                if hist_spanner_limits[1, 1] < np.inf:
                    mask = (mask) & (points[:, 1] < hist_spanner_limits[1, 1])
                mask = np.nonzero(mask)[0]
            im_selected_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            for i in mask:
                pheno_list[i].append(segName_short)
                im_selected_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
            im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
            if segName in analyze_index:
                im_analyzed[analyze_index.index(segName)] = im_selected_cells
            else:
                im_analyzed.append(im_selected_cells)
                analyze_index.append(segName)
            tissue_props["Phenotypes"] = pheno_list
            # for segName in analysis_params["Segments"].keys():
            #     if segName not in ["DAPI", "Tumor", "Stroma"]:
            #         if "filter_1" in analysis_params["Segments"][segName]:
            #             continue
            #         if "Speck" in analysis_params["Segments"][segName]:
            #             if analysis_params["Segments"][segName]["Speck"] > 0:
            #                 continue
            #         mask = im_analyzed[analyze_index.index(segName)]
            #         if mask[nucleus_centroids[i][0],
            #                 nucleus_centroids[i][1]] == 1:
            #             segment_list[i].append(segName + "+")
            # tissue_props['Segments'] = segment_list
            self.Tissue_props[self.activeImage][tissue_name] = tissue_props
        self.im_analyzed[self.activeImage] = im_analyzed
        self.analyze_index[self.activeImage] = analyze_index

    analysis_mode = 0
    analysis_params = self.analysis_params[self.Analysis_like].copy()
    if "thres" in analysis_params["Foreground"]:
        if len(analysis_params["Foreground"]["thres"]) == 0:
            analysis_mode = 1
            if "DAPI" in analysis_params["Segments"]:
                if len(analysis_params["Segments"]["DAPI"]["thres"]) == 0:
                    analysis_mode = 2
    if analysis_mode == 0:
        analyze_index = self.analyze_index[self.activeImage]
        self.analysis_params[self.activeImage] = analysis_params.copy()
        im_analyzed = self.im_analyzed[self.activeImage]
        if "ROI" in analyze_index:
            self.activeROI = im_analyzed[analyze_index.index("ROI")]
        self.im_analyzed[self.activeImage] = []
        im_analyzed = self.im_analyzed[self.activeImage]
        im_raw = self.im_raw[self.activeImage]
        n_channels = self.n_channels[self.activeImage]
        Color_pointers = self.Color_pointers[self.activeImage].copy()[0:n_channels]
        Channel_pointers = self.Channel_pointers[self.activeImage].copy()[0:n_channels]
        channel_variable = self.channel_variable[self.activeImage].copy()[0:n_channels]
        color_variable = self.color_variable[self.activeImage].copy()[0:n_channels]
        if "ROI" in analyze_index:
            im_analyzed.append(self.activeROI)
            color_variable.append(
                self.color_variable[self.activeImage][
                    analyze_index.index("ROI") + n_channels
                ]
            )
            Color_pointers.append(
                self.Color_pointers[self.activeImage][
                    analyze_index.index("ROI") + n_channels
                ]
            )
            self.analyze_index[self.activeImage] = []
            self.analyze_index[self.activeImage].append("ROI")
        else:
            self.analyze_index[self.activeImage] = []
        for SegName in analysis_params["Segments"].keys():
            for SegName2 in analysis_params["Segments"].keys():
                if SegName == [SegName2 + "+"]:
                    analysis_params["Segments"].pop(SegName)
        for SegName in analysis_params["Segments"].keys():
            if "filter_1" in analysis_params["Segments"][SegName]:
                if not analysis_params["Segments"][SegName]["Visible"]:
                    continue
                im_analyzed.append(iMO.FilterImage(self, mode=1, segName=SegName))
                self.analyze_index[self.activeImage].append(SegName)
                # Channel_pointers.append(SegName)
                continue
        self.im_analyzed[self.activeImage] = im_analyzed
        analyze_index = self.analyze_index[self.activeImage]
        self.Color_pointers[self.activeImage] = Color_pointers
        self.Channel_pointers[self.activeImage] = Channel_pointers
        self.channel_variable[self.activeImage] = channel_variable
        self.color_variable[self.activeImage] = color_variable
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        if "thres" in analysis_params["Foreground"]:
            iMO.FilterImage(self, mode=2)
            n_channels_fore = self.n_channels_temp
            im_raw_fore = self.im_raw_temp
            fore_thres = analysis_params["Foreground"]["thres"]
            if "adaptive_size" in analysis_params["Foreground"]:
                adaptive_temp = analysis_params["Foreground"]["adaptive_size"]
            else:
                adaptive_temp = np.zeros(n_channels_fore)
            modify_fore = False
            while len(adaptive_temp) < n_channels_fore:
                adaptive_temp = np.append(adaptive_temp, 0)
                modify_fore = True
            while len(adaptive_temp) > n_channels_fore:
                adaptive_temp = adaptive_temp[:-1]
                modify_fore = True
            while len(fore_thres[0]) < n_channels_fore:
                fore_thres = [
                    np.append(fore_thres[0], 0),
                    np.append(fore_thres[1], np.inf),
                ]
                modify_fore = True
            while len(fore_thres[0]) > n_channels_fore:
                fore_thres = [fore_thres[0][:-1], fore_thres[1][:-1]]
                modify_fore = True
            if modify_fore:
                analysis_params["Foreground"]["thres"] = fore_thres
                analysis_params["Foreground"]["adaptive_size"] = adaptive_temp
                self.analysis_params[self.activeImage] = analysis_params.copy()
            self.foreground_threshold[self.activeImage] = fore_thres
            for i in range(n_channels_fore):
                to_plot = im_raw_fore[:, :, i].copy()
                if adaptive_temp[i] > 0:
                    filter_size = adaptive_temp[i]
                    to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
                    # to_plot[to_plot < 0] = 0
                if (fore_thres[0][i] != 0) | (fore_thres[1][i] < np.inf):
                    im_temp = (im_temp) | (
                        ((to_plot) >= fore_thres[0][i])
                        & ((to_plot) <= fore_thres[1][i])
                    )
            # im_temp = ndi.morphology.binary_opening(im_temp)
            analyze_index.append("Foreground")
            Fore_mask = im_temp > 0
        else:
            Fore_mask = im_temp == 0
        if "ForeLimits" in analysis_params["Foreground"].keys():
            Fore_labels = skimage.measure.label(Fore_mask)
            Fore_objects = ndi.find_objects(Fore_labels)
            self.HoleLimits = analysis_params["Foreground"]["HoleLimits"]
            self.ForeLimits = analysis_params["Foreground"]["ForeLimits"]
            for i, s1 in enumerate(Fore_objects):
                if s1 is None:
                    continue
                label = i + 1
                region_area = np.sum(Fore_labels[s1] == label)
                if region_area < self.ForeLimits[0]:
                    Fore_mask[s1][Fore_labels[s1] == label] = 0
                elif region_area > self.ForeLimits[1]:
                    Fore_mask[s1][Fore_labels[s1] == label] = 0
            Back_mask = Fore_mask == 0
            Back_labels = skimage.measure.label(Back_mask)
            Back_objects = ndi.find_objects(Back_labels)
            for i, s1 in enumerate(Back_objects):
                if s1 is None:
                    continue
                label = i + 1
                region_area = np.sum(Back_labels[s1] == label)
                if region_area < self.HoleLimits[0]:
                    Fore_mask[s1][Back_labels[s1] == label] = 1
                elif region_area > self.HoleLimits[1]:
                    Fore_mask[s1][Back_labels[s1] == label] = 1
        if "ExcludeEdges" in analysis_params["Foreground"].keys():
            if analysis_params["Foreground"]["ExcludeEdges"] > 0:
                Fore_mask = skimage.segmentation.clear_border(Fore_mask)
        Foreground_mask = Fore_mask
        if "ROI" in analyze_index:
            Foreground_mask = Foreground_mask & im_analyzed[analyze_index.index("ROI")]
        if "thres" in analysis_params["Foreground"]:
            im_analyzed.append(Fore_mask)
    else:
        analyze_index = self.analyze_index[self.activeImage]
        self.analysis_params[self.activeImage] = analysis_params.copy()
        im_analyzed = self.im_analyzed[self.activeImage]
        im_analyzed_init = im_analyzed
        self.im_analyzed[self.activeImage] = []
        im_analyzed = self.im_analyzed[self.activeImage]
        im_raw = self.im_raw[self.activeImage]
        n_channels = self.n_channels[self.activeImage]
        Color_pointers = self.Color_pointers[self.activeImage].copy()[0:n_channels]
        Channel_pointers = self.Channel_pointers[self.activeImage].copy()[0:n_channels]
        channel_variable = self.channel_variable[self.activeImage].copy()[0:n_channels]
        color_variable = self.color_variable[self.activeImage].copy()[0:n_channels]
        Color_pointers_init = self.Color_pointers[self.activeImage].copy()
        color_variable_init = self.color_variable[self.activeImage].copy()
        self.analyze_index[self.activeImage] = []
        analyze_index_init = analyze_index
        if "ROI" in analyze_index:
            self.activeROI = im_analyzed_init[analyze_index.index("ROI")]
            im_analyzed.append(self.activeROI)
            color_variable.append(
                self.color_variable[self.activeImage][
                    analyze_index.index("ROI") + n_channels
                ]
            )
            Color_pointers.append(
                self.Color_pointers[self.activeImage][
                    analyze_index.index("ROI") + n_channels
                ]
            )
            self.analyze_index[self.activeImage].append("ROI")
        for SegName in analysis_params["Segments"].keys():
            if "filter_1" in analysis_params["Segments"][SegName]:
                if not analysis_params["Segments"][SegName]["Visible"]:
                    continue
                im_analyzed.append(iMO.FilterImage(self, mode=1, segName=SegName))
                self.analyze_index[self.activeImage].append(SegName)
                continue
        if "Foreground" in analyze_index:
            Fore_mask = im_analyzed_init[analyze_index.index("Foreground")]
            im_analyzed.append(Fore_mask)
            color_variable.append(
                self.color_variable[self.activeImage][
                    analyze_index.index("Foreground") + n_channels
                ]
            )
            Color_pointers.append(
                self.Color_pointers[self.activeImage][
                    analyze_index.index("Foreground") + n_channels
                ]
            )
            self.analyze_index[self.activeImage].append("Foreground")
        if "Tumor" in analyze_index:
            Tumor_mask = im_analyzed_init[analyze_index.index("Tumor")]
            im_analyzed.append(Tumor_mask)
            color_variable.append(
                self.color_variable[self.activeImage][
                    analyze_index.index("Tumor") + n_channels
                ]
            )
            Color_pointers.append(
                self.Color_pointers[self.activeImage][
                    analyze_index.index("Tumor") + n_channels
                ]
            )
            self.analyze_index[self.activeImage].append("Tumor")
        if "Stroma" in analyze_index:
            Stroma_mask = im_analyzed_init[analyze_index.index("Stroma")]
            im_analyzed.append(Stroma_mask)
            color_variable.append(
                self.color_variable[self.activeImage][
                    analyze_index.index("Stroma") + n_channels
                ]
            )
            Color_pointers.append(
                self.Color_pointers[self.activeImage][
                    analyze_index.index("Stroma") + n_channels
                ]
            )
            self.analyze_index[self.activeImage].append("Stroma")
        analyze_index = self.analyze_index[self.activeImage]
        for SegName in analysis_params["Segments"].keys():
            for SegName2 in analysis_params["Segments"].keys():
                if SegName == [SegName2 + "+"]:
                    analysis_params["Segments"].pop(SegName)
        self.Color_pointers[self.activeImage] = Color_pointers
        self.Channel_pointers[self.activeImage] = Channel_pointers
        self.channel_variable[self.activeImage] = channel_variable
        self.color_variable[self.activeImage] = color_variable
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        if "thres" not in analysis_params["Foreground"]:
            Fore_mask = im_temp == 0
        Foreground_mask = Fore_mask
        if "ROI" in analyze_index:
            Foreground_mask = Foreground_mask & im_analyzed[analyze_index.index("ROI")]
    tissue_keys = []
    for SegName in analysis_params["Segments"].keys():
        if "Tissue_props" in analysis_params["Segments"][SegName]:
            if analysis_params["Segments"][SegName]["Tissue_props"]:
                tissue_keys.append(SegName)
        if (SegName == "DAPI") & (analysis_mode == 2):
            continue
        elif "filter_1" in analysis_params["Segments"][SegName]:
            # if analysis_params["Segments"][SegName]["Visible"] != True:
            #     continue
            # im_analyzed.append(iMO.FilterImage(self, mode = 1, segName = SegName))
            # analyze_index.append(SegName)
            continue
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        seg_thres = analysis_params["Segments"][SegName]["thres"]
        if isinstance(seg_thres, str):
            if seg_thres == "Stardist_2D_versatile_fluo":
                # model_versatile = self.model_versatile
                model_versatile = stardist.models.StarDist2D.from_pretrained(
                    "2D_versatile_fluo"
                )
                # if perform_nuclei:
                #     segName = "DAPI"
                # else:
                #     segName = segname_var.get()
                ch_used = analysis_params["Segments"][SegName]["ch_used"]
                n_ch_used = analysis_params["Segments"][SegName]["n_ch_used"]
                anal_class = analysis_params["Segments"][SegName]["class"]
                probability_threshold = model_versatile.thresholds[0]
                nonmaximum_suppression = model_versatile.thresholds[1]
                if "d_prob_thres" in analysis_params["Segments"][SegName]:
                    probability_threshold += analysis_params["Segments"][SegName][
                        "d_prob_thres"
                    ]
                if "d_nms_thres" in analysis_params["Segments"][SegName]:
                    nonmaximum_suppression += analysis_params["Segments"][SegName][
                        "d_nms_thres"
                    ]
                if ch_used in self.Channel_pointers[self.activeImage]:
                    channel_options = [
                        i for i in self.Channel_pointers[self.activeImage]
                    ]
                    n_ch_used = channel_options.index(ch_used)
                    im_temp = im_raw[:, :, n_ch_used]
                elif ch_used in analyze_index:
                    channel_options = [i for i in analyze_index]
                    n_ch_used = channel_options.index(ch_used)
                    im_temp = im_raw[:, :, n_ch_used]
                elif n_ch_used < n_channels:
                    channel_options = [
                        i for i in self.Channel_pointers[self.activeImage]
                    ]
                    im_temp = im_raw[:, :, n_ch_used]
                    popupmsg(
                        "No channel with name "
                        + ch_used
                        + "found,\nperforming "
                        + "Stardist_2D_versatile_fluo analysis on "
                        + channel_options[n_ch_used]
                        + " insted!"
                    )
                elif (n_ch_used - n_channels) < len(im_analyzed):
                    channel_options = [i for i in analyze_index]
                    im_temp = im_analyzed[n_ch_used - n_channels]
                    popupmsg(
                        "No channel with name "
                        + ch_used
                        + "found,\nperforming "
                        + "Stardist_2D_versatile_fluo analysis on "
                        + channel_options[n_ch_used - n_channels]
                        + " insted!"
                    )
                else:
                    popupmsg(
                        "Analysis cannot be carried on!\n"
                        + "No channel with name "
                        + ch_used
                        + " found to perform "
                        + "Stardist_2D_versatile_fluo analysis on!"
                    )
                im_temp = np.float32(im_temp)
                Fore_mask = np.ones_like(im_temp == 0)
                if "ROI" in analyze_index:
                    Fore_mask = Fore_mask & im_analyzed[analyze_index.index("ROI")]
                if "Foreground" in analyze_index:
                    Fore_mask = (
                        Fore_mask & im_analyzed[analyze_index.index("Foreground")]
                    )
                img = StarDist2D_normalize(im_temp, 1, 99.8, axis=(0, 1))
                single_cells = model_versatile.predict_instances(
                    img,
                    prob_thresh=probability_threshold,
                    nms_thresh=nonmaximum_suppression,
                )[0]
                single_cells = np.uint32(single_cells * np.float32(Fore_mask))
            if anal_class == "Seg":
                single_cells = single_cells > 0
            if "ForeLimits" in analysis_params["Segments"][SegName].keys():
                Fore_labels = skimage.measure.label(single_cells)
                Fore_objects = ndi.find_objects(Fore_labels)
                self.HoleLimits = analysis_params["Segments"][SegName]["HoleLimits"]
                self.ForeLimits = analysis_params["Segments"][SegName]["ForeLimits"]
                for i, s1 in enumerate(Fore_objects):
                    if s1 is None:
                        continue
                    label = i + 1
                    region_area = np.sum(Fore_labels[s1] == label)
                    if region_area < self.ForeLimits[0]:
                        single_cells[s1][Fore_labels[s1] == label] = 0
                    elif region_area > self.ForeLimits[1]:
                        single_cells[s1][Fore_labels[s1] == label] = 0
                Back_mask = single_cells == 0
                # Back_mask = Back_mask & Fore_mask
                mask_temp = Back_mask == -1
                Back_labels = skimage.measure.label(Back_mask)
                Back_objects = ndi.find_objects(Back_labels)
                for i, s1 in enumerate(Back_objects):
                    if s1 is None:
                        continue
                    label = i + 1
                    region_area = np.sum(Back_labels[s1] == label)
                    if region_area < self.HoleLimits[0]:
                        mask_temp[s1][Back_labels[s1] == label] = 1
                    elif region_area > self.HoleLimits[1]:
                        mask_temp[s1][Back_labels[s1] == label] = 1
                Back_labels, Back_objects = ndi.label(mask_temp)
                for i in range(1, Back_objects + 1):
                    s1 = Back_labels == i
                    surrounding_values = Fore_mask[ndi.binary_dilation(s1) & ~s1]
                    most_frequent = Counter(surrounding_values).most_common(1)[0][0]
                    single_cells[s1] = most_frequent
                single_cells[np.logical_not(Fore_mask)] = 0
                del Fore_labels
                del Fore_objects
                del Back_mask
                del Back_labels
                del Back_objects
            if "ExcludeEdges" in analysis_params["Segments"][SegName].keys():
                if analysis_params["Segments"][SegName]["ExcludeEdges"] > 0:
                    single_cells = skimage.segmentation.clear_border(single_cells)
            mask = single_cells > 0
            if anal_class == "Label":
                im_analyzed.append(single_cells)
                analyze_index.append(SegName)
            else:
                im_analyzed.append(mask)
                analyze_index.append(SegName)
            if anal_class == "Nuc":
                if (
                    analysis_params["Segments"]["DAPI"]["NucLimits"]
                    != "Stardist_2D_versatile_fluo"
                ):
                    continue
                single_cells = skimage.measure.label(single_cells)
                im_analyzed.append(single_cells)
                analyze_index.append("Nuclei")
                voronoi_image = skimage.segmentation.watershed(
                    -ndi.distance_transform_edt(single_cells > 0), single_cells
                )
                voronoi_image = skimage.measure.label(voronoi_image)
                voronoi_image = np.uint32(voronoi_image * np.float32(Fore_mask))
                if "CellLimits" in analysis_params["Segments"]["DAPI"]:
                    voronoi_limit = analysis_params["Segments"]["DAPI"]["CellLimits"]
                    voronoi_extend = (
                        analysis_params["Segments"]["DAPI"]["CellMeth"]
                        == "Extend Cell Area To:"
                    )
                    voronoi_objects = ndi.find_objects(voronoi_image)
                    for i, s1 in enumerate(
                        voronoi_objects
                    ):  # here if voronoi object size is larger than max size, get bw dist; sort bw dist, and see the value at the desired size; and then use that as the value fow BW dist <=.
                        if s1 is None:
                            continue
                        label = i + 1
                        im_temp = voronoi_image[s1] == label
                        cell_area = np.sum(im_temp)
                        if (cell_area > voronoi_limit) & (voronoi_extend):
                            im_nuc_temp = single_cells[s1]
                            im_nuc_temp = im_nuc_temp[im_temp]
                            i = im_nuc_temp.max()
                            if i == 0:
                                continue
                            im_nuc_temp = single_cells[s1] == i
                            im_nuc_temp = ndi.distance_transform_edt(
                                np.logical_not(im_nuc_temp)
                            )
                            im_nuc_temp[~im_temp] = np.inf
                            im_temp[
                                im_nuc_temp
                                < (np.sort(im_nuc_temp.ravel())[voronoi_limit])
                            ] = False
                            voronoi_temp = voronoi_image[s1]
                            voronoi_temp[im_temp] = 0
                            voronoi_image[s1] = voronoi_temp
                            im_temp = voronoi_image[s1] == label
                        elif (not voronoi_extend) & (voronoi_limit < np.inf):
                            im_nuc_temp = single_cells[s1]
                            im_nuc_temp = im_nuc_temp[im_temp]
                            i = im_nuc_temp.max()
                            if i == 0:
                                continue
                            im_nuc_temp = single_cells[s1] == i
                            im_nuc_temp = ndi.distance_transform_edt(
                                np.logical_not(im_nuc_temp)
                            )
                            im_nuc_temp[~im_temp] = np.inf
                            im_temp[im_nuc_temp < voronoi_limit] = False
                            voronoi_temp = voronoi_image[s1]
                            voronoi_temp[im_temp] = 0
                            voronoi_image[s1] = voronoi_temp
                im_analyzed.append(voronoi_image)
                analyze_index.append("Cells")
                analysis_mode = 3
                self.single_cells = single_cells
                self.voronoi_image = voronoi_image
        else:
            iMO.FilterImage(self, mode=2)
            n_channels_fore = self.n_channels_temp
            im_raw_fore = self.im_raw_temp
            if "adaptive_size" in analysis_params["Segments"][SegName].keys():
                adaptive_thres = analysis_params["Segments"][SegName]["adaptive_size"]
            else:
                adaptive_thres = np.zeros(n_channels_fore)
            modify_fore = False
            while len(adaptive_thres) < n_channels_fore:
                adaptive_thres = np.append(adaptive_thres, 0)
                modify_fore = True
            while len(adaptive_thres) > n_channels_fore:
                adaptive_thres = adaptive_thres[:-1]
                modify_fore = True
            while len(seg_thres[0]) < n_channels_fore:
                seg_thres = [
                    np.append(seg_thres[0], 0),
                    np.append(seg_thres[1], np.inf),
                ]
                modify_fore = True
            while len(seg_thres[0]) > n_channels_fore:
                seg_thres = [seg_thres[0][:-1], seg_thres[1][:-1]]
                modify_fore = True
            if modify_fore:
                analysis_params["Segments"][SegName]["thres"] = seg_thres
                analysis_params["Segments"][SegName]["adaptive_size"] = adaptive_thres
                self.analysis_params[self.activeImage] = analysis_params.copy()
            for i in range(n_channels_fore):
                to_plot = im_raw_fore[:, :, i]
                if adaptive_thres[i] > 0:
                    filter_size = int(adaptive_thres[i])
                    to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
                    # to_plot[to_plot < 0] = 0

                if (seg_thres[0][i] != 0) | (seg_thres[1][i] < np.inf):
                    im_temp = (im_temp) | (
                        ((to_plot) >= seg_thres[0][i]) & ((to_plot) <= seg_thres[1][i])
                    )
            del to_plot
            # im_temp = ndi.morphology.binary_opening(im_temp)
            analyze_index.append(SegName)
            Fore_mask = im_temp > 0
            if "Foreground" in analyze_index:
                Fore_mask = Fore_mask & im_analyzed[analyze_index.index("Foreground")]
            if "ForeLimits" in analysis_params["Segments"][SegName].keys():
                Fore_labels = skimage.measure.label(Fore_mask)
                Fore_objects = ndi.find_objects(Fore_labels)
                self.HoleLimits = analysis_params["Segments"][SegName]["HoleLimits"]
                self.ForeLimits = analysis_params["Segments"][SegName]["ForeLimits"]
                for i, s1 in enumerate(Fore_objects):
                    if s1 is None:
                        continue
                    label = i + 1
                    region_area = np.sum(Fore_labels[s1] == label)
                    if region_area < self.ForeLimits[0]:
                        Fore_mask[s1][Fore_labels[s1] == label] = 0
                    elif region_area > self.ForeLimits[1]:
                        Fore_mask[s1][Fore_labels[s1] == label] = 0
                Back_mask = Fore_mask == 0
                # if "Foreground" in analyze_index:
                #     Back_mask = Back_mask & im_analyzed[analyze_index.index("Foreground")]
                Back_labels = skimage.measure.label(Back_mask)
                Back_objects = ndi.find_objects(Back_labels)
                for i, s1 in enumerate(Back_objects):
                    if s1 is None:
                        continue
                    label = i + 1
                    region_area = np.sum(Back_labels[s1] == label)
                    if region_area < self.HoleLimits[0]:
                        Fore_mask[s1][Back_labels[s1] == label] = 1
                    elif region_area > self.HoleLimits[1]:
                        Fore_mask[s1][Back_labels[s1] == label] = 1
                if "Foreground" in analyze_index:
                    Fore_mask = (
                        Fore_mask & im_analyzed[analyze_index.index("Foreground")]
                    )
                del Fore_labels
                del Fore_objects
                del Back_mask
                del Back_labels
                del Back_objects
            if "ExcludeEdges" in analysis_params["Segments"][SegName].keys():
                if analysis_params["Segments"][SegName]["ExcludeEdges"] > 0:
                    Fore_mask = skimage.segmentation.clear_border(Fore_mask)
            Fore_mask = Foreground_mask & Fore_mask
            im_analyzed.append(Fore_mask)
    if analysis_mode < 2:
        del Fore_mask
        if "DAPI" not in analyze_index:
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            Perform_tissue_analysis(tissue_keys)
            Get_tissue_phenotypes()
            self.Cell_props[self.activeImage] = []
            self.remake_side_window()
            return
        DAPI_mask = im_analyzed[analyze_index.index("DAPI")]
        if "NucLimits" in analysis_params["Segments"]["DAPI"]:
            self.NucLimits = analysis_params["Segments"]["DAPI"]["NucLimits"]
        else:
            self.NucLimits = [0, np.inf]
        fore_mask_DAPI = Foreground_mask
        del Foreground_mask
        DAPI_mask = DAPI_mask & fore_mask_DAPI
        DAPI_labels = skimage.measure.label(DAPI_mask)
        del DAPI_mask
        DAPI_objects = ndi.find_objects(DAPI_labels)
        single_cells = np.zeros_like(DAPI_labels)
        cell_counter = 0
        cell_clusters = np.zeros_like(DAPI_labels)
        cluster_counter = 0
        for i, s1 in enumerate(DAPI_objects):
            if s1 is None:
                continue
            label = i + 1
            nucleus_area = np.sum(DAPI_labels[s1] == label)
            if nucleus_area > self.NucLimits[0]:
                if nucleus_area > self.NucLimits[1]:
                    cluster_counter = cluster_counter + 1
                    cell_clusters[s1][DAPI_labels[s1] == label] = cluster_counter
                else:
                    cell_counter = cell_counter + 1
                    single_cells[s1][DAPI_labels[s1] == label] = cell_counter
        del DAPI_objects
        nearest_neighbor_radius = np.int32(np.ceil(np.sqrt(self.NucLimits[0])))
        ws_dist = ndi.distance_transform_edt(cell_clusters > 0)
        ws_local_maxi = peak_local_max(
            ws_dist,
            indices=False,
            footprint=np.ones((nearest_neighbor_radius, nearest_neighbor_radius)),
            labels=cell_clusters > 0,
        )
        ws_markers = ndi.label(ws_local_maxi)[0]
        del ws_local_maxi
        cluster_labels = skimage.segmentation.watershed(
            -ws_dist, ws_markers, mask=cell_clusters > 0
        )
        del cell_clusters
        del ws_markers
        del ws_dist
        cluster_labels = skimage.measure.label(cluster_labels)
        cluster_objects = ndi.find_objects(cluster_labels)
        for i, s1 in enumerate(cluster_objects):
            if s1 is None:
                continue
            label = i + 1
            nucleus_area = np.sum(cluster_labels[s1] == label)
            if nucleus_area > self.NucLimits[0]:
                if nucleus_area > self.NucLimits[1]:
                    cluster_labels[s1][cluster_labels[s1] == label] = 0
            else:
                cluster_labels[s1][cluster_labels[s1] == label] = 0
        del cluster_objects
        cluster_labels = cluster_labels + single_cells.max()
        cluster_labels[cluster_labels == single_cells.max()] = 0
        single_cells = single_cells + cluster_labels
        del cluster_labels
        single_cells = skimage.measure.label(single_cells)
        single_objects = ndi.find_objects(single_cells)
        voronoi_image = skimage.segmentation.watershed(
            -ndi.distance_transform_edt(single_cells > 0), single_cells
        )
        nucleus_area = []
        single_cells_mask = np.zeros_like(DAPI_labels) < 0
        del DAPI_labels
        for i, s1 in enumerate(single_objects):
            if s1 is None:
                continue
            label = i + 1
            nucleus_area.append(np.sum(single_cells[s1] == label))
            im_temp = single_cells[s1] == label
            im_temp = np.float32(im_temp) - np.float32(
                ndi.morphology.binary_erosion(
                    im_temp, iterations=round(single_cells.shape[0] / 500)
                )
            )
            single_cells_mask[s1][single_cells[s1] == label] = im_temp[
                single_cells[s1] == label
            ]
        del single_objects
        nucleus_area = np.array(nucleus_area)
        single_cells = skimage.measure.label(single_cells)
        single_cells = np.uint32(single_cells * np.float32(fore_mask_DAPI))
        self.single_cells = single_cells
        voronoi_image = skimage.measure.label(voronoi_image)
        voronoi_image = np.uint32(voronoi_image * np.float32(fore_mask_DAPI))
        self.voronoi_image = voronoi_image
        if "CombineNucs" in analysis_params["Segments"]["DAPI"]:
            self.adaptive_temp = analysis_params["Segments"]["DAPI"]["CombineNucs"]
            self.NucleusDetection(True, fore_mask_DAPI)
        if "CellLimits" in analysis_params["Segments"]["DAPI"]:
            voronoi_limit = analysis_params["Segments"]["DAPI"]["CellLimits"]
            voronoi_extend = (
                analysis_params["Segments"]["DAPI"]["CellMeth"]
                == "Extend Cell Area To:"
            )
            voronoi_objects = ndi.find_objects(voronoi_image)
            for i, s1 in enumerate(
                voronoi_objects
            ):  # here if voronoi object size is larger than max size, get bw dist; sort bw dist, and see the value at the desired size; and then use that as the value fow BW dist <=.
                if s1 is None:
                    continue
                label = i + 1
                im_temp = voronoi_image[s1] == label
                cell_area = np.sum(im_temp)
                if (cell_area > voronoi_limit) & (voronoi_extend):
                    im_nuc_temp = single_cells[s1]
                    im_nuc_temp = im_nuc_temp[im_temp]
                    i = im_nuc_temp.max()
                    if i == 0:
                        continue
                    im_nuc_temp = single_cells[s1] == i
                    im_nuc_temp = ndi.distance_transform_edt(
                        np.logical_not(im_nuc_temp)
                    )
                    im_nuc_temp[~im_temp] = np.inf
                    im_temp[
                        im_nuc_temp < (np.sort(im_nuc_temp.ravel())[voronoi_limit])
                    ] = False
                    voronoi_temp = voronoi_image[s1]
                    voronoi_temp[im_temp] = 0
                    voronoi_image[s1] = voronoi_temp
                    im_temp = voronoi_image[s1] == label
                elif (not voronoi_extend) & (voronoi_limit < np.inf):
                    im_nuc_temp = single_cells[s1]
                    im_nuc_temp = im_nuc_temp[im_temp]
                    i = im_nuc_temp.max()
                    if i == 0:
                        continue
                    im_nuc_temp = single_cells[s1] == i
                    im_nuc_temp = ndi.distance_transform_edt(
                        np.logical_not(im_nuc_temp)
                    )
                    im_nuc_temp[~im_temp] = np.inf
                    im_temp[im_nuc_temp < voronoi_limit] = False
                    voronoi_temp = voronoi_image[s1]
                    voronoi_temp[im_temp] = 0
                    voronoi_image[s1] = voronoi_temp
            self.voronoi_image = voronoi_image
        del fore_mask_DAPI
        im_analyzed.append(self.single_cells)
        analyze_index.append("Nuclei")
        im_analyzed.append(self.voronoi_image)
        analyze_index.append("Cells")
    elif analysis_mode == 2:
        im_analyzed.append(im_analyzed_init[analyze_index_init.index("DAPI")])
        analyze_index.append("DAPI")
        color_variable.append(
            color_variable_init[analyze_index_init.index("DAPI") + n_channels]
        )
        Color_pointers.append(
            Color_pointers_init[analyze_index_init.index("DAPI") + n_channels]
        )
        im_analyzed.append(im_analyzed_init[analyze_index_init.index("Nuclei")])
        analyze_index.append("Nuclei")
        color_variable.append(
            color_variable_init[analyze_index_init.index("Nuclei") + n_channels]
        )
        Color_pointers.append(
            Color_pointers_init[analyze_index_init.index("Nuclei") + n_channels]
        )
        im_analyzed.append(im_analyzed_init[analyze_index_init.index("Cells")])
        analyze_index.append("Cells")
        color_variable.append(
            color_variable_init[analyze_index_init.index("Cells") + n_channels]
        )
        Color_pointers.append(
            Color_pointers_init[analyze_index_init.index("Cells") + n_channels]
        )
    if "Cells" not in analyze_index:
        self.im_analyzed[self.activeImage] = im_analyzed
        self.analyze_index[self.activeImage] = analyze_index
        Perform_tissue_analysis(tissue_keys)
        Get_tissue_phenotypes()
        self.Cell_props[self.activeImage] = []
        self.remake_side_window()
        return
    self.im_analyzed[self.activeImage] = im_analyzed
    self.analyze_index[self.activeImage] = analyze_index
    Get_cell_props(self)
    Perform_tissue_analysis(tissue_keys)
    Get_tissue_phenotypes()
    im_analyzed = self.im_analyzed[self.activeImage]
    analyze_index = self.analyze_index[self.activeImage]
    cell_props = self.Cell_props[self.activeImage]
    pheno_list = cell_props["Phenotypes"][:].tolist()
    segment_list = cell_props["Segments"][:].tolist()
    im_all_cells = im_analyzed[analyze_index.index("All Cells")]
    nucleus_centroids = np.uint32(np.round(cell_props["Nucleus Centroid"][:].tolist()))
    Channel_pointers = self.Channel_pointers[self.activeImage].copy()
    Segment_keys = list(analysis_params["Segments"].keys())
    for SegName in Segment_keys:
        if "filter_1" in analysis_params["Segments"][SegName]:
            if analysis_params["Segments"][SegName]["Visible"]:
                Channel_pointers.append(SegName)
        if "Speck" in analysis_params["Segments"][SegName]:
            if analysis_params["Segments"][SegName]["Speck"] == 1:
                Channel_pointers.append(SegName + "-Speck")
            if analysis_params["Segments"][SegName]["Speck"] == 2:
                Channel_pointers.append(SegName + "-Mask")
    for segName in analysis_params["Phenotypes"].keys():
        tissue_name = []
        for i in analysis_params["Segments"].keys():
            if segName.find(i + " - ") == 0:
                tissue_name = i
        if len(tissue_name) > 0:
            continue
        if analysis_params["Phenotypes"][segName]["x_axis2"] == "Geometry":
            x_data = np.vstack(
                cell_props[
                    analysis_params["Phenotypes"][segName]["x_axis1"]
                    + " "
                    + analysis_params["Phenotypes"][segName]["x_axis3"]
                ]
            )
        else:
            x_data = np.vstack(
                cell_props[
                    analysis_params["Phenotypes"][segName]["x_axis1"]
                    + " Fluorescent "
                    + analysis_params["Phenotypes"][segName]["x_axis3"]
                ]
            )[
                :,
                Channel_pointers.index(
                    analysis_params["Phenotypes"][segName]["x_axis2"]
                ),
            ]
        if analysis_params["Phenotypes"][segName]["y_axis2"] == "Geometry":
            y_data = np.vstack(
                cell_props[
                    analysis_params["Phenotypes"][segName]["y_axis1"]
                    + " "
                    + analysis_params["Phenotypes"][segName]["y_axis3"]
                ]
            )
        else:
            y_data = np.vstack(
                cell_props[
                    analysis_params["Phenotypes"][segName]["y_axis1"]
                    + " Fluorescent "
                    + analysis_params["Phenotypes"][segName]["y_axis3"]
                ]
            )[
                :,
                Channel_pointers.index(
                    analysis_params["Phenotypes"][segName]["y_axis2"]
                ),
            ]
        if np.size(analysis_params["Phenotypes"][segName]["positive_area"]) > 0:
            ROI_path = matplotlib.path.Path(
                analysis_params["Phenotypes"][segName]["positive_area"]
            )
        else:
            ROI_path = []
        hist_spanner_limits = analysis_params["Phenotypes"][segName]["hist_limits"]
        points = np.transpose((x_data.ravel(), y_data.ravel()))
        if np.size(ROI_path) > 0:
            mask = ROI_path.contains_points(points)
            mask = np.nonzero(mask)[0]
        else:
            mask = (points[:, 0] * 0) == 0
            if hist_spanner_limits[0, 0] > 0:
                mask = (mask) & (points[:, 0] > hist_spanner_limits[0, 0])
            if hist_spanner_limits[1, 0] < np.inf:
                mask = (mask) & (points[:, 0] < hist_spanner_limits[1, 0])
            if hist_spanner_limits[0, 1] > 0:
                mask = (mask) & (points[:, 1] > hist_spanner_limits[0, 1])
            if hist_spanner_limits[1, 1] < np.inf:
                mask = (mask) & (points[:, 1] < hist_spanner_limits[1, 1])
            mask = np.nonzero(mask)[0]
        im_selected_cells = np.zeros(
            (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
        )
        for i in mask:
            pheno_list[i].append(segName)
            im_selected_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
        im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
        if segName in analyze_index:
            im_analyzed[analyze_index.index(segName)] = im_selected_cells
        else:
            im_analyzed.append(im_selected_cells)
            analyze_index.append(segName)
    #        pheno_thres_name.append('Stroma+')
    for i in range(len(segment_list)):
        for segName in analysis_params["Segments"].keys():
            if segName not in ["DAPI", "Tumor", "Stroma"]:
                if "filter_1" in analysis_params["Segments"][segName]:
                    continue
                if "Speck" in analysis_params["Segments"][segName]:
                    if analysis_params["Segments"][segName]["Speck"] > 0:
                        continue
                mask = im_analyzed[analyze_index.index(segName)]
                if mask[nucleus_centroids[i][0], nucleus_centroids[i][1]] == 1:
                    segment_list[i].append(segName + "+")
    segment_thres_name = []
    for segName in analysis_params["Segments"].keys():
        if "filter_1" in analysis_params["Segments"][segName]:
            continue
        if segName not in ["DAPI", "Tumor", "Stroma"]:
            if "Speck" in analysis_params["Segments"][segName]:
                if analysis_params["Segments"][segName]["Speck"] > 0:
                    continue
            segment_thres_name.append([segName + "+"])
    for pointer_temp in segment_thres_name:
        im_selected_cells = np.zeros(
            (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
        )
        for i in range(np.shape(segment_list)[0]):
            if pointer_temp in segment_list[i]:
                im_selected_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
        im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
        if pointer_temp in analyze_index:
            im_analyzed[analyze_index.index(pointer_temp)] = im_selected_cells
        else:
            im_analyzed.append(im_selected_cells)
            analyze_index.append(pointer_temp)
    cell_props["Phenotypes"] = pheno_list
    cell_props["Segments"] = segment_list
    self.im_analyzed[self.activeImage] = im_analyzed
    self.analyze_index[self.activeImage] = analyze_index
    self.Cell_props[self.activeImage] = cell_props
    self.remake_side_window()


def RedoAnalysis(self):
    def RedoAnalysisSure(*a):
        self.Analysis_like = self.activeImage
        QuickAnalysisLikeSure(self)

    popup2 = tkinter.Tk()
    popup2.wm_title("Redo Analysis?")
    label = tkinter.Label(
        popup2,
        text="You are about to reanalyze your image\n"
        + "Are you sure you want to continue?",
    )
    label.pack(side="top", fill="x", pady=10)
    B1 = tkinter.Button(
        popup2, text="Yes", command=lambda: [DestroyTK(popup2), RedoAnalysisSure()]
    )
    B1.pack()
    B2 = tkinter.Button(popup2, text="No", command=lambda: [DestroyTK(popup2)])
    B2.pack()
    popup2.mainloop()


def RedoAnalysisAll(self):
    def RedoAnalysisSure(*a):
        self.Analysis_like = self.activeImage
        [popup, label] = popupmsg("...", False)
        for self.activeImage in range(len(self.FileDictionary)):
            self.Analysis_like = self.activeImage
            label["text"] = (
                "Analyzing image "
                + str(self.activeImage + 1)
                + " of "
                + str(len(self.FileDictionary))
                + " images.\n Please hold."
            )
            popup.update()
            QuickAnalysisLikeSure(self)
        DestroyTK(popup)

    popup2 = tkinter.Tk()
    popup2.wm_title("Redo Analysis?")
    label = tkinter.Label(
        popup2,
        text="You are about to reanalyze all your images\n"
        + "Are you sure you want to continue?",
    )
    label.pack(side="top", fill="x", pady=10)
    B1 = tkinter.Button(
        popup2, text="Yes", command=lambda: [DestroyTK(popup2), RedoAnalysisSure()]
    )
    B1.pack()
    B2 = tkinter.Button(popup2, text="No", command=lambda: [DestroyTK(popup2)])
    B2.pack()
    popup2.mainloop()
