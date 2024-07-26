# -*- coding: utf-8 -*-
"""
Created on Thu Aug  2 17:17:39 2018

@author: github.com/balciemrah
"""
import logging
import tkinter
import os
from tkinter import ttk as ttkinter
import tkinter.messagebox
import tkinter.filedialog

# import skimage.io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as Tk_Agg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NT2Tk
from scipy import ndimage as ndi

# import skimage.measure
# import pandas as pd
# from math import log
# import pickle
import sys

if __package__ == "tmeanalyzer":
    from . import __version__
    from .imageMenu import DestroyTK, popupmsg
    from . import imageMenu as iMO
    from . import fileMenu as fMO
    from . import dataMenu as dMO
    from . import saveMenu as sMO
else:
    from imageMenu import DestroyTK, popupmsg
    import imageMenu as iMO
    import fileMenu as fMO
    import dataMenu as dMO
    import saveMenu as sMO
    from version import __version__
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"


class TextOut(tkinter.Text):

    def write(self, s):
        try:
            self.insert(tkinter.CURRENT, s)
        except tkinter.TclError:
            pass

    def flush(self):
        pass


def check_consent(loglvl=logging.ERROR):
    logger = logging.getLogger("check_consent")
    logformatter = logging.Formatter(fmt=" %(name)s :: %(levelname)-8s :: %(message)s")
    consolehandler = logging.StreamHandler(sys.stdout)
    consolehandler.setFormatter(logformatter)
    logger.addHandler(consolehandler)
    logger.setLevel(loglvl)
    logger.info(f"TkVersion: {tkinter.TkVersion}")
    logger.info(f"TME Analyzer version: {__version__}")

    def popup_license():
        popuplicense = tkinter.Tk()
        popuplicense.wm_title("License")
        label = tkinter.Label(
            popuplicense,
            text="MIT License\n"
            + "\nCopyright (c) 2023 github.com/ErasmusMC-Bioinformatics & github.com/balciemrah\n"
            + "\nPermission is hereby granted, free of charge, to any person obtaining a copy "
            + '\nof this software and associated documentation files (the "Software"), to deal '
            + "\nin the Software without restriction, including without limitation the rights "
            + "\nto use, copy, modify, merge, publish, distribute, sublicense, and/or sell "
            + "\ncopies of the Software, and to permit persons to whom the Software is "
            + "\nfurnished to do so, subject to the following conditions:\n"
            + "\nThe above copyright notice and this permission notice shall be included in all "
            + "\ncopies or substantial portions of the Software. \n"
            + '\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR '
            + "\nIMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, "
            + "\nFITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE "
            + "\nAUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER "
            + "\nLIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, "
            + "\nOUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE "
            + "SOFTWARE.",
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popuplicense,
            text="Agree",
            command=lambda: [
                popupnew.destroy(),
                popuplicense.destroy(),
                consent_given(),
            ],
        )
        B1.pack()
        B2 = tkinter.Button(
            popuplicense,
            text="Disagree",
            command=lambda: [popupnew.destroy(), popuplicense.destroy()],
        )
        B2.pack()
        popupnew.mainloop()

    popupnew = tkinter.Tk()
    popupnew.wm_title("User Agreement")
    label = tkinter.Label(
        popupnew,
        text="This software is a tool created "
        + "by Dr. H. Emrah Balcioglu (github.com/balciemrah)\n"
        + "in the Tumor Immunology group, (PI. Reno Debets, "
        + "j.debets@erasmusmc.nl)\nDepartment "
        + "of Medical Oncology in Erasmus MC, The Netherlands\n"
        + "for interrogating the tumor microenvironment "
        + 'and is provided "as is".\n\nBy '
        + "pressing agree and using this software you "
        + "confirm that you have read\nthis "
        + "statement and agree with the attached (MIT) License Agreement.",
    )
    label.pack(side="top", fill="x", pady=10)
    B1 = tkinter.Button(
        popupnew, text="Agree", command=lambda: [popupnew.destroy(), consent_given()]
    )
    B1.pack()
    B1 = tkinter.Button(
        popupnew, text="View License", command=lambda: [popup_license()]
    )
    B1.pack()
    B2 = tkinter.Button(popupnew, text="Disagree", command=popupnew.destroy)
    B2.pack()
    popupnew.mainloop()


def consent_given():
    root = tkinter.Tk()
    root.title("TME Analyzer v" + str(__version__))
    root.geometry("1200x800")
    ImageAnalysis(root)
    root.mainloop()


class ImageAnalysis:
    def __init__(self, master):
        master.protocol("WM_DELETE_WINDOW", self.Quit)
        show_messages = 0
        default_setup = 0
        # ***** Definitions *****
        self.PerformDefinitions(default_setup, show_messages)
        self.master = master
        # ***** Main Menu *****
        menubar = tkinter.Menu(master)
        master.config(menu=menubar)
        fileMenu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Loading", menu=fileMenu)
        fileMenu.add_command(label="Load Image", command=lambda: [fMO.openFile(self)])
        fileMenu.add_command(
            label="Load Segmentation Map", command=lambda: [fMO.openSeg(self)]
        )
        fileMenu.add_command(
            label="Load Folder", command=lambda: [fMO.openFolder(self)]
        )
        fileMenu.add_separator()
        fileMenu.add_command(
            label="Load Workspace", command=lambda: [fMO.LoadWorkspace(self)]
        )
        fileMenu.add_command(
            label="Load Workspace Directory",
            command=lambda: [fMO.LoadWorkspaceFolder(self)],
        )
        fileMenu.add_separator()
        fileMenu.add_command(
            label="Change Channel Setup", command=lambda: [fMO.ChangeChannelSetup(self)]
        )
        fileMenu.add_command(label="Crop Image", command=lambda: [fMO.cropFile(self)])
        fileMenu.add_command(label="Select ROI", command=lambda: [iMO.SelectROI(self)])
        fileMenu.add_command(
            label="Unmix Channels", command=lambda: [iMO.UnmixChannels(self)]
        )
        fileMenu.add_separator()
        fileMenu.add_command(
            label="Reset Image", command=lambda: [fMO.ResetCurrent(self)]
        )
        fileMenu.add_command(
            label="Remove Image", command=lambda: [fMO.RemoveCurrent(self)]
        )
        fileMenu.add_command(label="Reset All", command=lambda: [fMO.Reset(self)])
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=self.Quit)

        imageMenu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Image Analysis", menu=imageMenu)
        imageMenu.add_command(
            label="Threshold Foregound", command=lambda: [iMO.ThresholdForeground(self)]
        )
        imageMenu.add_command(
            label="Tissue Segmentation", command=lambda: [iMO.SegmentDetection(self)]
        )
        imageMenu.add_command(
            label="Image Filtering", command=lambda: [iMO.FilterImage(self)]
        )
        imageMenu.add_command(label="Fill Holes", command=lambda: [iMO.FillHoles(self)])
        imageMenu.add_command(
            label="Nucleus Detection", command=lambda: [iMO.NucleusDetection(self)]
        )
        imageMenu.add_separator()
        imageMenu.add_command(
            label="Filter Image", command=lambda: [iMO.FilterImage(self)]
        )
        imageMenu.add_command(
            label="ISH/Mask Enumeration", command=lambda: [iMO.MaskEnumeration(self)]
        )
        imageMenu.add_command(
            label="Tissue Analysis", command=lambda: [iMO.Tissue_analysis(self)]
        )
        imageMenu.add_command(
            label="Neural Networks Segmentation",
            command=lambda: [iMO.NN_segmentation(self)],
        )
        dataMenu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Data Analysis", menu=dataMenu)
        dataMenu.add_command(
            label="Phenotype Selection", command=lambda: [dMO.PhenotypeSelection(self)]
        )
        dataMenu.add_command(
            label="Data Analysis", command=lambda: [dMO.DataAnalysis(self)]
        )
        dataMenu.add_command(
            label="Redo Cell Quantification",
            command=lambda: [dMO.Get_cell_props(self, True)],
        )
        dataMenu.add_command(
            label="Redo Tissue Quantification",
            command=lambda: [iMO.Tissue_analysis(self, external_use=True)],
        )
        dataMenu.add_separator()
        dataMenu.add_command(
            label="Apply Analysis to All", command=lambda: [dMO.QuickAnalysisAll(self)]
        )
        dataMenu.add_command(
            label="Reanalyze Image Like ...",
            command=lambda: [dMO.QuickAnalysisLike(self)],
        )
        dataMenu.add_command(
            label="Reanalyze Using default analysis",
            command=lambda: [dMO.Apply_default_analysis(self)],
        )
        dataMenu.add_separator()
        dataMenu.add_command(
            label="Redo Analysis", command=lambda: [dMO.RedoAnalysis(self)]
        )
        dataMenu.add_command(
            label="Redo Analysis for all", command=lambda: [dMO.RedoAnalysisAll(self)]
        )
        dataMenu.add_command(label="Display Log", command=self.DisplayLog)
        saveMenu = tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Saving", menu=saveMenu)
        saveMenu.add_command(
            label="Save Image", command=lambda: [sMO.SaveCurrentImage(self)]
        )
        saveMenu.add_separator()
        saveMenu.add_command(
            label="Export Data", command=lambda: [sMO.ExportData(self)]
        )
        saveMenu.add_command(
            label="Save Workplace", command=lambda: [sMO.SaveWorkspace(self)]
        )
        saveMenu.add_command(
            label="Redo Analysis and Save Workplace",
            command=lambda: [sMO.SaveWorkspace(self, True)],
        )
        saveMenu.add_command(
            label="Save Phenotype Image", command=lambda: [sMO.SavePhenos(self)]
        )
        saveMenu.add_separator()
        subSaveMenu = tkinter.Menu(saveMenu, tearoff=0)
        saveMenu.add_cascade(label="Save For All", menu=subSaveMenu)
        subSaveMenu.add_command(
            label="Save Images", command=lambda: [sMO.SaveAllImages(self)]
        )
        subSaveMenu.add_separator()
        subSaveMenu.add_command(
            label="Export Data", command=lambda: [sMO.Export_folder_data(self)]
        )
        subSaveMenu.add_command(
            label="Save Workplaces", command=lambda: [sMO.Export_folder_workspace(self)]
        )
        subSaveMenu.add_command(
            label="Redo Analysis and Save Workplaces",
            command=lambda: [sMO.Export_folder_workspace(self, True)],
        )
        subSaveMenu.add_command(
            label="Save Phenotype Images", command=lambda: [sMO.SavePhenosAll(self)]
        )
        subSaveMenu.add_separator()

        # ***** Toolbar *****

        toolbar = tkinter.Frame(master, bg="black")
        loadButton = ttkinter.Button(
            toolbar, text="Load Image", command=lambda: [fMO.openFile(self)]
        )
        loadButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        folderButton = ttkinter.Button(
            toolbar, text="Load Folder", command=lambda: [fMO.openFolder(self)]
        )
        folderButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        foregorundButton = ttkinter.Button(
            toolbar,
            text="Threshold Foreground",
            command=lambda: [iMO.ThresholdForeground(self)],
        )
        foregorundButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        segmentButton = ttkinter.Button(
            toolbar,
            text="Tissue Segmentation",
            command=lambda: [iMO.SegmentDetection(self)],
        )
        segmentButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        fillHolesButton = ttkinter.Button(
            toolbar, text="Fill Holes", command=lambda: [iMO.FillHoles(self)]
        )
        fillHolesButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        nucleusButton = ttkinter.Button(
            toolbar,
            text="Nucleus Detection",
            command=lambda: [iMO.NucleusDetection(self)],
        )
        nucleusButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        phenotypeButton = ttkinter.Button(
            toolbar,
            text="Phenotype Selection",
            command=lambda: [dMO.PhenotypeSelection(self)],
        )
        phenotypeButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        exportButton = ttkinter.Button(
            toolbar, text="Export Data", command=lambda: [sMO.ExportData(self)]
        )
        exportButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        dataAnalysis = ttkinter.Button(
            toolbar, text="Data Analysis", command=lambda: [dMO.DataAnalysis(self)]
        )
        dataAnalysis.pack(side=tkinter.LEFT, padx=2, pady=2)
        toolbar.pack(side=tkinter.TOP, fill=tkinter.X)

        # ***** Status Bar *****
        statusBar = tkinter.Label(
            master,
            text="Analyzing Images...",
            bd=1,
            relief=tkinter.SUNKEN,
            anchor=tkinter.W,
        )
        statusBar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        # ***** MainWindow *****
        f = plt.Figure(figsize=(10, 7), dpi=100)
        f.patch.set_visible(False)
        f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.a = f.gca()
        #        self.mainWindow = tkinter.Frame(master, width=700)
        self.mainWindow = tkinter.Frame(master, width=700)
        image_canvas = Tk_Agg.FigureCanvasTkAgg(f, master=self.mainWindow)
        image_canvas.draw()
        image_canvas.get_tk_widget().pack(side=tkinter.LEFT, expand=True)
        image_toolbar = NT2Tk(image_canvas, self.mainWindow)
        image_toolbar.update()
        image_canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
        self.image_canvas = image_canvas

        # ***** RightWindow *****
        self.rightWindow_master = tkinter.Frame(master, width=200)
        self.rightWindow_master.pack(side=tkinter.RIGHT)
        self.rightWindow = tkinter.Frame(self.rightWindow_master, width=200)
        self.rightWindow.pack(side=tkinter.RIGHT)
        self.mainWindow.pack(side=tkinter.RIGHT)

    def PerformDefinitions(self, default_setup, show_messages):
        self.LUT = {
            "red": [1, 0, 0],
            "green": [0, 1, 0],
            "blue": [0, 0, 1],
            "cyan": [0, 1, 1],
            "magenta": [1, 0, 1],
            "yellow": [1, 1, 0],
            "white": [1, 1, 1],
            "gray": [0.5, 0.5, 0.5],
            "black": [0, 0, 0],
            "aquamarine": [0.5, 1, 0.83],
            "coral": [1, 0.5, 0.3],
            "crimson": [0.85, 0.1, 0.3],
            "gold": [1, 0.83, 0],
            "lavender": [0.9, 0.9, 0.98],
            "olive": [0.5, 0.5, 0],
            "orange": [1, 0.5, 0],
            "orchid": [0.85, 0.44, 0.84],
            "pink": [1, 0.75, 0.8],
            "teal": [0, 0.5, 0.5],
        }
        self.all_lookup_markers = {
            0: ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"]
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
            ]
        }

        self.all_marker_dropdown = ["Default"]

        self.im_raw = []
        self.channel_variable = []
        self.color_variable = []
        self.Color_pointers = []
        self.Channel_pointers = []
        self.FileDictionary = {}
        self.ThresholdValues = []
        self.activeImage = 0
        self.n_channels = []
        self.activeROI = []
        self.im_analyzed = []
        self.analyze_index = []
        self.foreground_threshold = []
        self.activeFore = []
        self.showROImessage = show_messages
        self.showForemessage = show_messages
        self.showrmvForemessage = show_messages
        self.showDapimessage = show_messages
        self.showPopmessage = show_messages
        self.showFillmessage = show_messages
        self.NucLimits = []
        self.HoleLimits = []
        self.ForeLimits = []
        self.Cell_props = []
        self.Tissue_props = []
        self.activeCrop = []
        self.overall_data_to_export = {}
        self.dataParams = []
        self.analysis_params = []
        self.fill_ch = -1
        self.small_images = []
        self.Markers = self.all_lookup_markers[default_setup]
        self.Color_info = self.all_lookup_colors[default_setup]
        self.newChSetup = []
        self.default_analysis_params = {
            "Foreground": {},
            "Segments": {},
            "Phenotypes": {},
        }

        self.log_keeping = tkinter.Tk()
        text = TextOut(self.log_keeping)
        toolbar = tkinter.Frame(self.log_keeping, bg="black")
        loadButton = ttkinter.Button(
            toolbar, text="Clear", command=lambda: [text.delete("1.0", tkinter.END)]
        )
        loadButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        folderButton = ttkinter.Button(
            toolbar, text="Close", command=self.log_keeping.withdraw
        )
        folderButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        print_button = ttkinter.Button(
            toolbar,
            text="Print params",
            command=lambda: [
                print(self.analysis_params[self.activeImage]),
                self.DisplayLog(),
            ],
        )
        print_button.pack(side=tkinter.LEFT, padx=2, pady=2)
        toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
        sys.stdout = text
        text.pack(expand=True, fill=tkinter.BOTH)
        self.log_keeping.withdraw()
        self.log_keeping.protocol("WM_DELETE_WINDOW", self.log_keeping.withdraw)

    def to_be_implemented(self):
        popupmsg("to be implemented")

    def RedoPhenotyping(self, *a):
        def Procrastinate(popup2, *a):
            label = tkinter.Label(
                popup2, text="You will redo the analysis right,\n" + "You promise?"
            )
            label.pack(side="top", fill="x", pady=10)
            B1 = tkinter.Button(
                popup2, text="Yes!", command=lambda: [DestroyTK(popup2)]
            )
            B1.pack()
            B2 = tkinter.Button(
                popup2,
                text="Maybe",
                command=lambda: [
                    popupmsg("OK, I'm reanalyzing now."),
                    RedoPhenotypingSure(),
                    DestroyTK(popup2),
                    popupmsg("Done, thank you for your cooperation."),
                ],
            )
            B2.pack()
            popup2.mainloop()

        def RedoPhenotypingSure(*a):
            self.Analysis_like = self.activeImage
            dMO.QuickAnalysisLikeSure(self)

        def RedoPhenotypingCheck(*a):
            popup2 = tkinter.Tk()
            popup2.protocol(
                "WM_DELETE_WINDOW",
                lambda: [
                    popupmsg("OK, I'm reanalyzing now."),
                    RedoPhenotypingSure(),
                    DestroyTK(popup2),
                    popupmsg("Done, thank you for your cooperation."),
                ],
            )
            popup2.wm_title("Redo Analysis?")
            label = tkinter.Label(
                popup2,
                text="Your adjustment is expected to change "
                + "phenotyping and\nwhat you see will not be what you get"
                + " until you Redo analysis\nwould you like to do that now?",
            )
            label.pack(side="top", fill="x", pady=10)
            B1 = tkinter.Button(
                popup2,
                text="Redo Analysis now",
                command=lambda: [RedoPhenotypingSure(), DestroyTK(popup2)],
            )
            B1.pack()
            B2 = tkinter.Button(
                popup2,
                text="I will do it later",
                command=lambda: [Procrastinate(popup2)],
            )
            B2.pack()
            popup2.mainloop()

        cell_props = self.Cell_props[self.activeImage]
        redo_phenotyping = False
        if len(cell_props) > 0:
            pheno_list = cell_props["Phenotypes"][:].tolist()
            if len(pheno_list) > 0:
                redo_phenotyping = True
            else:
                dMO.Get_cell_props(self)
        if redo_phenotyping:
            RedoPhenotypingCheck()

    def DisplayLog(self):
        # print(self.analysis_params[self.activeImage])
        self.log_keeping.update()
        self.log_keeping.deiconify()
        self.log_keeping.mainloop()

    def display_composite_image(self):
        ImagePointer = self.activeImagePointer.get()
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
        if self.activeImage != np.int32(ImagePointer[n_start:n_end]):
            self.activeImage = np.int32(ImagePointer[n_start:n_end])
            self.remake_side_window()
        im_raw = self.im_raw[self.activeImage]
        Color_pointers = self.Color_pointers[self.activeImage]
        color_variable = self.color_variable[self.activeImage]
        Channel_pointers = self.Channel_pointers[self.activeImage]
        channel_variable = self.channel_variable[self.activeImage]
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        n_channels = self.n_channels[self.activeImage]
        im_2_display = np.zeros((im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32)
        for i in range(n_channels):
            if self.check_boxes[i].get() == 0:
                continue
            Color_pointers_temp = color_variable[i].get()
            Color_pointers[i] = color_variable[i].get()
            Channel_pointers[i] = channel_variable[i].get()
            for j in range(3):
                im_temp = im_2_display[:, :, j]
                im2_add = im_raw[:, :, i] / im_raw[:, :, i].max()
                im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                im_temp = im_temp + im2_add
                im_2_display[:, :, j] = im_temp
        for i in range(n_channels, len(Color_pointers)):
            if self.check_boxes[i].get() == 0:
                continue
            Color_pointers_temp = color_variable[i].get()
            Color_pointers[i] = color_variable[i].get()
            if np.sum(self.LUT[Color_pointers_temp]) == 0:
                continue
            im_temp_2 = im_analyzed[i - n_channels]
            if analyze_index[i - n_channels] == "Cells":
                voronoi_objects = ndi.find_objects(im_temp_2)
                voronoi_image_mask = np.zeros_like(im_temp_2) < 0
                for i, s1 in enumerate(voronoi_objects):
                    if s1 is None:
                        continue
                    label = i + 1
                    im_temp = im_temp_2[s1] == label
                    im_temp = np.float32(im_temp) - np.float32(
                        ndi.morphology.binary_erosion(
                            im_temp, iterations=round(im_temp_2.shape[0] / 1000)
                        )
                    )
                    voronoi_image_mask[s1][im_temp_2[s1] == label] = im_temp[
                        im_temp_2[s1] == label
                    ]
                im_temp_2 = voronoi_image_mask
            elif analyze_index[i - n_channels] == "Nuclei":
                voronoi_objects = ndi.find_objects(im_temp_2)
                voronoi_image_mask = np.zeros_like(im_temp_2) < 0
                for i, s1 in enumerate(voronoi_objects):
                    if s1 is None:
                        continue
                    label = i + 1
                    im_temp = im_temp_2[s1] == label
                    im_temp = np.float32(im_temp) - np.float32(
                        ndi.morphology.binary_erosion(
                            im_temp, iterations=round(im_temp_2.shape[0] / 500)
                        )
                    )
                    voronoi_image_mask[s1][im_temp_2[s1] == label] = im_temp[
                        im_temp_2[s1] == label
                    ]
                im_temp_2 = voronoi_image_mask
            elif im_temp_2.dtype == "float32":
                for j in range(3):
                    im_temp = im_2_display[:, :, j]
                    im2_add = im_temp_2
                    im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                    im_temp = im_temp + im2_add
                    im_2_display[:, :, j] = im_temp
                continue
            else:
                im_temp_2 = np.float32(im_temp_2) - np.float32(
                    ndi.morphology.binary_erosion(
                        im_temp_2, iterations=round(im_temp_2.shape[0] / 500)
                    )
                )
                # im_temp_2 = np.float32(ndi.binary_fill_holes(im_temp_2))
            im2_add = im_temp_2 / im_temp_2.max()
            dummy = im2_add > 0
            for j in range(3):
                im_temp = im_2_display[:, :, j]
                im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                im_temp[dummy] = im2_add2[dummy]
                im_2_display[:, :, j] = im_temp
        self.a.clear()
        self.a.imshow(im_2_display, aspect="equal")
        self.a.autoscale(False)
        self.a.axis("off")
        self.image_canvas.draw()
        self.Color_pointers[self.activeImage] = Color_pointers
        self.Channel_pointers[self.activeImage] = Channel_pointers
        self.im_2_display = im_2_display

    def remake_side_window(self):
        def checks_changed_master_check(*a):
            checks_changed(*a, master_check=True)

        def checks_changed(a, b, c, master_check=False, *arg):
            if master_check:
                if self.check_boxes[-1].get() == 1:
                    for n_i, i in enumerate(self.check_boxes[:-1]):
                        i.trace_remove(*i.trace_info()[0])
                        i.set(1)
                        i.trace_id = i.trace_add("write", checks_changed)
                        self.check_boxes[n_i] = i
                else:
                    for n_i, i in enumerate(self.check_boxes[:-1]):
                        i.trace_remove(*i.trace_info()[0])
                        i.set(0)
                        i.trace_id = i.trace_add("write", checks_changed)
                        self.check_boxes[n_i] = i
            else:
                master_check = True
                for n_i, i in enumerate(self.check_boxes[:-1]):
                    if i.get() == 0:
                        master_check = False
                if master_check:
                    self.check_boxes[-1].trace_remove(
                        *self.check_boxes[-1].trace_info()[0]
                    )
                    self.check_boxes[-1].set(1)
                    self.check_boxes[-1].trace_id = self.check_boxes[-1].trace_add(
                        "write", checks_changed_master_check
                    )
                elif self.check_boxes[-1].get() == 1:
                    self.check_boxes[-1].trace_remove(
                        *self.check_boxes[-1].trace_info()[0]
                    )
                    self.check_boxes[-1].set(0)
                    self.check_boxes[-1].trace_id = self.check_boxes[-1].trace_add(
                        "write", checks_changed_master_check
                    )
            self.display_composite_image()

        DestroyTK(self.rightWindow)
        self.rightWindow = tkinter.Frame(self.rightWindow_master, width=100)
        self.rightWindow.pack(side=tkinter.RIGHT)
        analyze_index = self.analyze_index[self.activeImage]
        w = []
        c = []
        n_channels = self.n_channels[self.activeImage]
        Channel_pointers = self.Channel_pointers[self.activeImage]
        Color_pointers = self.Color_pointers[self.activeImage]
        channel_variable = self.channel_variable[self.activeImage]
        color_variable = self.color_variable[self.activeImage]
        self.check_boxes = []
        for i in range(len(Color_pointers), (n_channels + len(analyze_index))):
            Color_pointers.append("black")
            color_variable.append([])

        for i in range(n_channels):
            internal_windows = tkinter.Frame(self.rightWindow, width=100, height=20)
            internal_windows.pack(side=tkinter.TOP)
            channel_variable[i] = tkinter.StringVar(internal_windows)
            channel_variable[i].set(Channel_pointers[i])
            channel_variable[i].trace("w", self.cc_changed)
            w.append(
                tkinter.OptionMenu(internal_windows, channel_variable[i], *self.Markers)
            )
            w[i].config(width=10)
            w[i].pack(side=tkinter.LEFT)
            color_variable[i] = tkinter.StringVar(internal_windows)
            color_variable[i].set(Color_pointers[i])
            color_variable[i].trace("w", self.cc_changed)
            c.append(
                tkinter.OptionMenu(
                    internal_windows, color_variable[i], *self.LUT.keys()
                )
            )
            c[i].config(width=10)
            c[i].pack(side=tkinter.LEFT)

            self.check_boxes.append(tkinter.IntVar(internal_windows))
            check_columns = tkinter.Checkbutton(
                internal_windows, variable=self.check_boxes[-1]
            )
            self.check_boxes[-1].set(1)
            self.check_boxes[-1].trace_id = self.check_boxes[-1].trace_add(
                "write", checks_changed
            )
            check_columns.pack(side=tkinter.LEFT)
        for i in range(n_channels, len(Color_pointers)):
            internal_windows = tkinter.Frame(self.rightWindow, width=100, height=20)
            internal_windows.pack(side=tkinter.TOP)
            label = tkinter.Label(internal_windows, text=analyze_index[i - n_channels])
            label.config(width=13)
            label.pack(side=tkinter.LEFT)
            color_variable[i] = tkinter.StringVar(internal_windows)
            color_variable[i].set(Color_pointers[i])
            color_variable[i].trace("w", self.cc_changed)
            c.append(
                tkinter.OptionMenu(
                    internal_windows, color_variable[i], *self.LUT.keys()
                )
            )
            c[i].config(width=10)
            c[i].pack(side=tkinter.LEFT)
            self.check_boxes.append(tkinter.IntVar(internal_windows))
            check_columns = tkinter.Checkbutton(
                internal_windows, variable=self.check_boxes[-1]
            )
            self.check_boxes[-1].set(1)
            self.check_boxes[-1].trace_id = self.check_boxes[-1].trace_add(
                "write", checks_changed
            )
            check_columns.pack(side=tkinter.LEFT)

        internal_windows = tkinter.Frame(self.rightWindow, width=100, height=20)
        internal_windows.pack(side=tkinter.TOP)
        self.check_boxes.append(tkinter.IntVar(internal_windows))
        check_columns = tkinter.Checkbutton(
            internal_windows, variable=self.check_boxes[-1]
        )
        self.check_boxes[-1].set(1)
        self.check_boxes[-1].trace_id = self.check_boxes[-1].trace_add(
            "write", checks_changed_master_check
        )
        check_columns.pack(side=tkinter.RIGHT)
        im_display_button = tkinter.Button(
            master=internal_windows,
            text="Display",
            command=self.display_composite_image,
        )
        im_display_button.pack(side=tkinter.RIGHT)
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
        self.channel_variable[self.activeImage] = channel_variable
        self.color_variable[self.activeImage] = color_variable

    def image_changed(self, *a, **kw):
        ImagePointer = self.activeImagePointer.get()
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
        if self.activeImage != np.int32(ImagePointer[n_start:n_end]):
            self.activeImage = np.int32(ImagePointer[n_start:n_end])
            self.remake_side_window()

    def cc_changed(self, *a, **kw):
        ImagePointer = self.activeImagePointer.get()
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
        if self.activeImage != np.int32(ImagePointer[n_start:n_end]):
            self.activeImage = np.int32(ImagePointer[n_start:n_end])
            self.remake_side_window()
        else:
            Color_pointers = self.Color_pointers[self.activeImage]
            color_variable = self.color_variable[self.activeImage]
            Channel_pointers = self.Channel_pointers[self.activeImage]
            channel_variable = self.channel_variable[self.activeImage]
            n_channels = self.n_channels[self.activeImage]
            for i in range(len(Color_pointers)):
                Color_pointers[i] = color_variable[i].get()
            for i in range(n_channels):
                Channel_pointers[i] = channel_variable[i].get()
            self.Color_pointers[self.activeImage] = Color_pointers
            self.Channel_pointers[self.activeImage] = Channel_pointers

    def Quit(self):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to Quit")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Go Ahead",
            command=lambda: [DestroyTK(popup2), self.QuitSure()],
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def QuitSure(self):
        DestroyTK(self.log_keeping)
        self.master.destroy()
