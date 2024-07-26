"""
Created on Tuesday Oct 24th 2023
 sMO.SaveCurrentImage
 sMO.SaveAllImages
 sMO.ExportData
 sMO.Export_folder_data
 sMO.SaveWorkspace
 sMO.Export_folder_workspace
 sMO.SavePhenos
 sMO.SavePhenosAll
"""

import tkinter

# import os
import tkinter.filedialog
import skimage.io
import numpy as np
from scipy import ndimage as ndi
import pandas as pd

# from math import log
import pickle

if __package__ == "tmeanalyzer":
    from . import dataMenu as dMO
    from .imageMenu import DestroyTK, popupmsg
else:
    import dataMenu as dMO
    from imageMenu import DestroyTK, popupmsg


def SaveCurrentImage(self):
    ftypes = [("Tiff images", ".tif .tiff")]
    filename = tkinter.filedialog.asksaveasfilename(
        parent=self.master, filetypes=ftypes
    )
    if filename:
        im_raw = self.im_raw[self.activeImage]
        if not (filename[-4:] == ".tif") | (filename[-5:] == ".tiff"):
            filename += ".tif"
        skimage.io.imsave(filename, im_raw.transpose(2, 0, 1))


def SaveAllImages(self):
    popup = tkinter.Tk()
    popup.wm_title("Save Multiple Images")
    label = tkinter.Label(popup, text="How would you like to name your files?")
    label.pack(side="top", fill="x", pady=10)
    label_var = tkinter.StringVar()
    labelButton = tkinter.Entry(popup, textvariable=label_var)
    labelButton.pack()
    labelButton.insert(0, "")
    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")
    label = tkinter.Label(internal_window, text="Use default names?")
    label.pack(side="left", fill="x", pady=10)
    default_name_check = tkinter.IntVar(internal_window)
    default_check = tkinter.Checkbutton(internal_window, variable=default_name_check)
    default_check.pack(side="left")

    label = tkinter.Label(popup, text="Number of Digits?")
    label.pack(side="top", fill="x", pady=10)
    labelButton2 = tkinter.Entry(popup)
    labelButton2.pack()
    labelButton2.insert(0, "3")

    label = tkinter.Label(popup, text="Data to export")
    label.pack(side="top", fill="x", pady=10)
    labelButton3 = tkinter.Entry(popup)
    labelButton3.pack()
    labelButton3.insert(0, "all")
    image_available = []
    for activeImage in range(len(self.FileDictionary)):
        image_available.append(activeImage)
    label = tkinter.Label(popup, text="Data available: " + str(image_available)[1:-1])
    label.pack(side="top", fill="x", pady=10)

    internal_window3 = tkinter.Frame(popup)
    internal_window3.pack(side="top")

    def export_image(*a):
        # combine_data = combine_check.get()
        use_def = default_name_check.get()
        file_header = []
        if not use_def:
            file_header = labelButton.get()
        #            if combine_data:
        #                n_digits = 0
        if len(labelButton2.get()) < 1:
            n_digits = 0
        else:
            n_digits = int(labelButton2.get())
        if labelButton3.get() in ["all", "All"]:
            images_to_analyze = image_available
        else:
            images_to_analyze = np.uint32(labelButton3.get().split(","))
        filename = tkinter.filedialog.asksaveasfilename(parent=self.master)
        [popup_int, label_int] = popupmsg("...", False)
        activeImage = self.activeImage
        if use_def:
            filedir = filename[: -1 * filename[::-1].find("/")]
            for n_im, i in enumerate(images_to_analyze):
                label_int["text"] = (
                    "Exporting image for "
                    + str(n_im + 1)
                    + " of "
                    + str(len(images_to_analyze))
                    + " images.\n Please hold."
                )
                popup_int.update()
                filename = self.FileDictionary[i]
                im_raw = self.im_raw[i]
                if "/" in filename:
                    filename = filedir + filename[-1 * filename[::-1].find("/") : -4]
                skimage.io.imsave(filename + ".tif", im_raw.transpose(2, 0, 1))
        else:
            filedir = filename[: -1 * filename[::-1].find("/")]
            for n_im, i in enumerate(images_to_analyze):
                label_int["text"] = (
                    "Exporting image for "
                    + str(n_im + 1)
                    + " of "
                    + str(len(images_to_analyze))
                    + " images.\n Please hold."
                )
                popup_int.update()
                filename = filedir + file_header + "_" + str(n_im).zfill(n_digits)
                im_raw = self.im_raw[i]
                skimage.io.imsave(filename + ".tif", im_raw.transpose(2, 0, 1))
        self.activeImage = activeImage
        DestroyTK(popup_int)

    B1 = tkinter.Button(
        internal_window3,
        text="Export",
        command=lambda: [export_image(), DestroyTK(popup)],
    )
    B1.pack(side="left")
    B2 = tkinter.Button(
        internal_window3, text="Go Back", command=lambda: [DestroyTK(popup)]
    )
    B2.pack(side="left")


def ExportData(self):
    cell_props = self.Cell_props[self.activeImage]
    Channel_pointers = self.Channel_pointers[self.activeImage].copy()
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
    if (len(cell_props) == 0) & (len(self.Tissue_props[self.activeImage]) == 0):
        popupmsg("Please perform Nucleus segmentation first")
    else:
        filename = tkinter.filedialog.asksaveasfilename(parent=self.master)
        if filename:
            if len(cell_props) > 0:
                cell_props_new = cell_props.copy()
                cell_props_new = cell_props_new.drop(columns="Show Data")
                for column_names in cell_props_new.columns.tolist():
                    if "Fluorescent" in column_names:
                        cell_props_new = cell_props_new.drop(columns=column_names)
                for i, ch_name in enumerate(Channel_pointers):
                    for column_names in cell_props.columns.tolist():
                        if "Fluorescent" in column_names:
                            temp_data = []
                            for n in cell_props.index:
                                temp_data.append(cell_props[column_names][n][i])
                            cell_props_new[ch_name + " " + column_names] = temp_data
                if filename[-4:] in [".xls", ".txt", ".csv"]:
                    cell_props_new.to_csv(filename, sep="\t")
                elif filename[-5:] == ".xlsx":
                    cell_props_new.to_excel(filename)
                else:
                    filename = filename + ".xls"
                    cell_props_new.to_csv(filename, sep="\t")
            else:
                cell_props_new = pd.DataFrame()
            if (filename[-4:] not in [".xls", ".txt", ".csv"]) & (
                filename[-5:] != ".xlsx"
            ):
                filename = filename + ".xls"
            with pd.ExcelWriter(filename) as writer:
                cell_props_new.to_excel(writer, sheet_name="Cell Props")
                for tissue_name in self.Tissue_props[self.activeImage].keys():
                    tissue_props = self.Tissue_props[self.activeImage][tissue_name]
                    cell_props_new = tissue_props.copy()
                    cell_props_new = cell_props_new.drop(columns="Show Data")
                    for column_names in cell_props_new.columns.tolist():
                        if "Fluorescent" in column_names:
                            cell_props_new = cell_props_new.drop(columns=column_names)
                    for i, ch_name in enumerate(Channel_pointers):
                        for column_names in tissue_props.columns.tolist():
                            if "Fluorescent" in column_names:
                                temp_data = []
                                for n in tissue_props.index:
                                    temp_data.append(tissue_props[column_names][n][i])
                                cell_props_new[ch_name + " " + column_names] = temp_data
                    cell_props_new.to_excel(writer, sheet_name=tissue_name + " Props")


def Export_folder_data(self):
    popup = tkinter.Tk()
    popup.wm_title("Save Multiple Data Tables")
    label = tkinter.Label(popup, text="How would you like to name your files?")
    label.pack(side="top", fill="x", pady=10)
    label_var = tkinter.StringVar()
    labelButton = tkinter.Entry(popup, textvariable=label_var)
    labelButton.pack()
    labelButton.insert(0, "")
    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")
    label = tkinter.Label(internal_window, text="Use default names?")
    label.pack(side="left", fill="x", pady=10)
    default_name_check = tkinter.IntVar(internal_window)
    default_check = tkinter.Checkbutton(internal_window, variable=default_name_check)
    default_check.pack(side="left")

    label = tkinter.Label(popup, text="Number of Digits?")
    label.pack(side="top", fill="x", pady=10)
    labelButton2 = tkinter.Entry(popup)
    labelButton2.pack()
    labelButton2.insert(0, "3")

    internal_window2 = tkinter.Frame(popup)
    internal_window2.pack(side="top")
    label = tkinter.Label(internal_window2, text="Combine data?")
    label.pack(side="left", fill="x", pady=10)
    combine_check = tkinter.IntVar(internal_window2)
    default_check = tkinter.Checkbutton(internal_window2, variable=combine_check)
    default_check.pack(side="left")

    label = tkinter.Label(popup, text="Data to combine")
    label.pack(side="top", fill="x", pady=10)
    labelButton3 = tkinter.Entry(popup)
    labelButton3.pack()
    labelButton3.insert(0, "all")
    image_available = []
    for activeImage in range(len(self.FileDictionary)):
        if (len(self.Cell_props[activeImage]) > 0) | (
            len(self.Tissue_props[activeImage]) > 0
        ):
            image_available.append(activeImage)
    label = tkinter.Label(popup, text="Data available: " + str(image_available)[1:-1])
    label.pack(side="top", fill="x", pady=10)

    internal_window3 = tkinter.Frame(popup)
    internal_window3.pack(side="top")

    def export_data(*a):
        combine_data = combine_check.get()
        use_def = default_name_check.get()
        file_header = []
        if not use_def:
            file_header = labelButton.get()
        if combine_data:
            n_digits = 0
        elif len(labelButton2.get()) < 1:
            n_digits = 0
        else:
            n_digits = int(labelButton2.get())
        if labelButton3.get() in ["all", "All"]:
            images_to_analyze = image_available
        else:
            images_to_analyze = np.uint32(labelButton3.get().split(","))
        filename = tkinter.filedialog.asksaveasfilename(parent=self.master)
        [popup_int, label_int] = popupmsg("...", False)
        if combine_data:
            cell_props_all = []
            file_keys = []
            for n_im, i in enumerate(images_to_analyze):
                label_int["text"] = (
                    "Exporting data for "
                    + str(n_im + 1)
                    + " of "
                    + str(len(images_to_analyze))
                    + " images.\n Please hold."
                )
                popup_int.update()
                self.activeImage = i
                cell_props = self.Cell_props[i]
                file_keys.append(self.FileDictionary[i])
                Channel_pointers = self.Channel_pointers[i].copy()
                analysis_params = self.analysis_params[i].copy()
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
                if len(cell_props) > 0:
                    cell_props_new = cell_props.copy()
                    cell_props_new = cell_props_new.drop(columns="Show Data")
                    for column_names in cell_props_new.columns.tolist():
                        if "Fluorescent" in column_names:
                            cell_props_new = cell_props_new.drop(columns=column_names)
                    for i, ch_name in enumerate(Channel_pointers):
                        for column_names in cell_props.columns.tolist():
                            if "Fluorescent" in column_names:
                                temp_data = []
                                for n in cell_props.index:
                                    temp_data.append(cell_props[column_names][n][i])
                                cell_props_new[ch_name + " " + column_names] = temp_data
                else:
                    cell_props_new = pd.DataFrame()
                cell_props_all.append(cell_props_new)
            cell_props_new = pd.concat(cell_props_all, keys=file_keys)
            if filename[-4:] in [".xls", ".txt", ".csv"]:
                cell_props_new.to_csv(filename, sep="\t")
            elif filename[-5:] == ".xlsx":
                cell_props_new.to_excel(filename)
            else:
                filename = filename + ".xls"
                cell_props_new.to_csv(filename, sep="\t")
            with pd.ExcelWriter(filename) as writer:
                cell_props_new.to_excel(writer, sheet_name="Cell Props")
                tissue_props_all = {}
                file_keys = {}
                for n_im, i in enumerate(images_to_analyze):
                    for tissue_name in self.Tissue_props[self.activeImage].keys():
                        if tissue_name not in tissue_props_all.keys():
                            tissue_props_all[tissue_name] = []
                            file_keys[tissue_name] = []
                        tissue_props = self.Tissue_props[self.activeImage][tissue_name]
                        cell_props_new = tissue_props.copy()
                        cell_props_new = cell_props_new.drop(columns="Show Data")
                        file_keys.append(self.FileDictionary[i])
                        for column_names in cell_props_new.columns.tolist():
                            if "Fluorescent" in column_names:
                                cell_props_new = cell_props_new.drop(
                                    columns=column_names
                                )
                        for i, ch_name in enumerate(Channel_pointers):
                            for column_names in tissue_props.columns.tolist():
                                if "Fluorescent" in column_names:
                                    temp_data = []
                                    for n in tissue_props.index:
                                        temp_data.append(
                                            tissue_props[column_names][n][i]
                                        )
                                    cell_props_new[ch_name + " " + column_names] = (
                                        temp_data
                                    )

                    cell_props_all.append(cell_props_new)
                    cell_props_new.to_excel(writer, sheet_name=tissue_name + " Props")

        elif use_def:
            filedir = filename[: -1 * filename[::-1].find("/")]
            for n_im, i in enumerate(images_to_analyze):
                label_int["text"] = (
                    "Exporting data for "
                    + str(n_im + 1)
                    + " of "
                    + str(len(images_to_analyze))
                    + " images.\n Please hold."
                )
                popup_int.update()
                cell_props = self.Cell_props[i]
                filename = self.FileDictionary[i]
                self.activeImage = i
                if "/" in filename:
                    filename = filedir + filename[-1 * filename[::-1].find("/") : -4]
                Channel_pointers = self.Channel_pointers[i].copy()
                analysis_params = self.analysis_params[i].copy()
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
                if len(cell_props) > 0:
                    cell_props_new = cell_props.copy()
                    cell_props_new = cell_props_new.drop(columns="Show Data")
                    for column_names in cell_props_new.columns.tolist():
                        if "Fluorescent" in column_names:
                            cell_props_new = cell_props_new.drop(columns=column_names)
                    for i, ch_name in enumerate(Channel_pointers):
                        for column_names in cell_props.columns.tolist():
                            if "Fluorescent" in column_names:
                                temp_data = []
                                for n in cell_props.index:
                                    temp_data.append(cell_props[column_names][n][i])
                                cell_props_new[ch_name + " " + column_names] = temp_data
                else:
                    cell_props_new = pd.DataFrame()
                if filename[-4:] in [".xls", ".txt", ".csv"]:
                    cell_props_new.to_csv(filename, sep="\t")
                elif filename[-5:] == ".xlsx":
                    cell_props_new.to_excel(filename)
                else:
                    filename = filename + ".xls"
                    cell_props_new.to_csv(filename, sep="\t")
                with pd.ExcelWriter(filename) as writer:
                    cell_props_new.to_excel(writer, sheet_name="Cell Props")
                    for tissue_name in self.Tissue_props[self.activeImage].keys():
                        tissue_props = self.Tissue_props[self.activeImage][tissue_name]
                        cell_props_new = tissue_props.copy()
                        cell_props_new = cell_props_new.drop(columns="Show Data")
                        for column_names in cell_props_new.columns.tolist():
                            if "Fluorescent" in column_names:
                                cell_props_new = cell_props_new.drop(
                                    columns=column_names
                                )
                        for i, ch_name in enumerate(Channel_pointers):
                            for column_names in tissue_props.columns.tolist():
                                if "Fluorescent" in column_names:
                                    temp_data = []
                                    for n in tissue_props.index:
                                        temp_data.append(
                                            tissue_props[column_names][n][i]
                                        )
                                    cell_props_new[ch_name + " " + column_names] = (
                                        temp_data
                                    )
                        cell_props_new.to_excel(
                            writer, sheet_name=tissue_name + " Props"
                        )

        else:
            filedir = filename[: -1 * filename[::-1].find("/")]
            for n_im, i in enumerate(images_to_analyze):
                self.activeImage = i
                label_int["text"] = (
                    "Exporting data for "
                    + str(n_im + 1)
                    + " of "
                    + str(len(images_to_analyze))
                    + " images.\n Please hold."
                )
                popup_int.update()
                cell_props = self.Cell_props[i]
                filename = filedir + file_header + "_" + str(n_im).zfill(n_digits)
                Channel_pointers = self.Channel_pointers[i].copy()
                analysis_params = self.analysis_params[i].copy()
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
                if len(cell_props) > 0:
                    cell_props_new = cell_props.copy()
                    cell_props_new = cell_props_new.drop(columns="Show Data")
                    for column_names in cell_props_new.columns.tolist():
                        if "Fluorescent" in column_names:
                            cell_props_new = cell_props_new.drop(columns=column_names)
                    for i_c, ch_name in enumerate(Channel_pointers):
                        for column_names in cell_props.columns.tolist():
                            if "Fluorescent" in column_names:
                                temp_data = []
                                for n in cell_props.index:
                                    temp_data.append(cell_props[column_names][n][i_c])
                                cell_props_new[ch_name + " " + column_names] = temp_data
                else:
                    cell_props_new = pd.DataFrame()
                if filename[-4:] in [".xls", ".txt", ".csv"]:
                    cell_props_new.to_csv(filename, sep="\t")
                elif filename[-5:] == ".xlsx":
                    cell_props_new.to_excel(filename)
                else:
                    filename = filename + ".xls"
                    cell_props_new.to_csv(filename, sep="\t")
                with pd.ExcelWriter(filename) as writer:
                    cell_props_new.to_excel(writer, sheet_name="Cell Props")
                    for tissue_name in self.Tissue_props[self.activeImage].keys():
                        tissue_props = self.Tissue_props[self.activeImage][tissue_name]
                        cell_props_new = tissue_props.copy()
                        cell_props_new = cell_props_new.drop(columns="Show Data")
                        for column_names in cell_props_new.columns.tolist():
                            if "Fluorescent" in column_names:
                                cell_props_new = cell_props_new.drop(
                                    columns=column_names
                                )
                        for i, ch_name in enumerate(Channel_pointers):
                            for column_names in tissue_props.columns.tolist():
                                if "Fluorescent" in column_names:
                                    temp_data = []
                                    for n in tissue_props.index:
                                        temp_data.append(
                                            tissue_props[column_names][n][i]
                                        )
                                    cell_props_new[ch_name + " " + column_names] = (
                                        temp_data
                                    )
                        cell_props_new.to_excel(
                            writer, sheet_name=tissue_name + " Props"
                        )

        DestroyTK(popup_int)

    B1 = tkinter.Button(
        internal_window3,
        text="Export",
        command=lambda: [export_data(), DestroyTK(popup)],
    )
    B1.pack(side="left")
    B2 = tkinter.Button(
        internal_window3, text="Go Back", command=lambda: [DestroyTK(popup)]
    )
    B2.pack(side="left")

    def def_changed(*a):
        if default_name_check.get() == 1:
            labelButton.delete(0, tkinter.END)
            labelButton2.delete(0, tkinter.END)
            combine_check.set(False)

    default_name_check.trace_add("write", def_changed)

    def label_changed(*a):
        label_name = labelButton.get()
        if len(label_name) > 0:
            default_name_check.set(False)

    label_var.trace("w", label_changed)

    def combine_changed(*a):
        if combine_check.get() == 1:
            labelButton2.delete(0, tkinter.END)
            default_name_check.set(False)

    combine_check.trace_add("write", combine_changed)
    popup.mainloop()


def SaveWorkspace(self, redo_option=False):
    def SaveWorkspaceSafe(option, redo_option):
        filename_save = tkinter.filedialog.asksaveasfilename(parent=self.master)
        if filename_save:
            if redo_option:
                dMO.RedoAnalysis(self)
            im_raw = self.im_raw[self.activeImage]
            filename = self.FileDictionary[self.activeImage]
            Channel_pointers = self.Channel_pointers[self.activeImage]
            Color_pointers = self.Color_pointers[self.activeImage]
            im_analyzed = self.im_analyzed[self.activeImage]
            analyze_index = self.analyze_index[self.activeImage]
            Cell_props = self.Cell_props[self.activeImage]
            Tissue_props = self.Tissue_props[self.activeImage]
            analysis_params = self.analysis_params[self.activeImage].copy()
            foreground_threshold = self.foreground_threshold[self.activeImage]
            pickle_savename = filename_save
            if filename_save[-7:] != ".pickle":
                if "." not in filename_save[-5:]:
                    pickle_savename += ".pickle"
            with open(pickle_savename, "wb") as f:
                if option == 0:
                    pickle.dump(
                        {
                            "im_raw": im_raw,
                            "filename": filename,
                            "Channel_pointers": Channel_pointers,
                            "Color_pointers": Color_pointers,
                            "im_analyzed": im_analyzed,
                            "analyze_index": analyze_index,
                            "Cell_props": Cell_props,
                            "Tissue_props": Tissue_props,
                            "analysis_params": analysis_params,
                            "foreground_threshold": foreground_threshold,
                        },
                        f,
                    )
                if option == 1:
                    pickle.dump(
                        {
                            "im_raw": [],
                            "filename": filename,
                            "Channel_pointers": Channel_pointers,
                            "Color_pointers": Color_pointers,
                            "im_analyzed": im_analyzed,
                            "analyze_index": analyze_index,
                            "Cell_props": Cell_props,
                            "Tissue_props": Tissue_props,
                            "analysis_params": analysis_params,
                            "foreground_threshold": foreground_threshold,
                        },
                        f,
                    )
                if option == 2:
                    pickle.dump(
                        {
                            "im_raw": filename_save + ".tif",
                            "filename": filename,
                            "Channel_pointers": Channel_pointers,
                            "Color_pointers": Color_pointers,
                            "im_analyzed": im_analyzed,
                            "analyze_index": analyze_index,
                            "Cell_props": Cell_props,
                            "Tissue_props": Tissue_props,
                            "analysis_params": analysis_params,
                            "foreground_threshold": foreground_threshold,
                        },
                        f,
                    )
                    skimage.io.imsave(filename_save + ".tif", im_raw.transpose(2, 0, 1))

    im_raw = self.im_raw[self.activeImage]
    if im_raw.nbytes > 1024 * 1024 * 1024 * 2:
        popup2 = tkinter.Tk()
        popup2.wm_title("Image too large")
        label = tkinter.Label(
            popup2,
            text="The image is too large to pickle\n"
            + "Would you like to save it as a seperate image instead?",
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Yes",
            command=lambda: [DestroyTK(popup2), SaveWorkspaceSafe(2, redo_option)],
        )
        B1.pack()
        B2 = tkinter.Button(
            popup2,
            text="No",
            command=lambda: [DestroyTK(popup2), SaveWorkspaceSafe(1, redo_option)],
        )
        B2.pack()
        popup2.mainloop()
    else:
        SaveWorkspaceSafe(0, redo_option)


def Export_folder_workspace(self, redo_analysis=False):
    popup = tkinter.Tk()
    popup.wm_title("Save Multiple Workspaces")
    label = tkinter.Label(popup, text="How would you like to name your files?")
    label.pack(side="top", fill="x", pady=10)
    label_var = tkinter.StringVar()
    labelButton = tkinter.Entry(popup, textvariable=label_var)
    labelButton.pack()
    labelButton.insert(0, "")
    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")
    label = tkinter.Label(internal_window, text="Use default names?")
    label.pack(side="left", fill="x", pady=10)
    default_name_check = tkinter.IntVar(internal_window)
    default_check = tkinter.Checkbutton(internal_window, variable=default_name_check)
    default_check.pack(side="left")

    label = tkinter.Label(popup, text="Number of Digits?")
    label.pack(side="top", fill="x", pady=10)
    labelButton2 = tkinter.Entry(popup)
    labelButton2.pack()
    labelButton2.insert(0, "3")

    label = tkinter.Label(popup, text="Data to export")
    label.pack(side="top", fill="x", pady=10)
    labelButton3 = tkinter.Entry(popup)
    labelButton3.pack()
    labelButton3.insert(0, "all")
    image_available = []
    for activeImage in range(len(self.FileDictionary)):
        if len(self.analyze_index[activeImage]) > 0:
            image_available.append(activeImage)
    label = tkinter.Label(popup, text="Data available: " + str(image_available)[1:-1])
    label.pack(side="top", fill="x", pady=10)

    internal_window3 = tkinter.Frame(popup)
    internal_window3.pack(side="top")

    def export_workspace(*a):
        use_def = default_name_check.get()
        file_header = []
        if not use_def:
            file_header = labelButton.get()
        if len(labelButton2.get()) < 1:
            n_digits = 0
        else:
            n_digits = int(labelButton2.get())
        if labelButton3.get() in ["all", "All"]:
            images_to_analyze = image_available
        else:
            images_to_analyze = np.uint32(labelButton3.get().split(","))
        filename = tkinter.filedialog.asksaveasfilename(parent=self.master)
        [popup_int, label_int] = popupmsg("...", False)
        activeImage = self.activeImage
        if use_def:
            filedir = filename[: -1 * filename[::-1].find("/")]
            for n_im, i in enumerate(images_to_analyze):
                if redo_analysis:
                    label_int["text"] = (
                        "Redoing analysis for "
                        + str(n_im + 1)
                        + " of "
                        + str(len(images_to_analyze))
                        + " images.\n Please hold."
                    )
                    popup_int.update()
                    self.activeImage = i
                    self.Analysis_like = self.activeImage
                    dMO.QuickAnalysisLikeSure(self)
                label_int["text"] = (
                    "Exporting workspace for "
                    + str(n_im + 1)
                    + " of "
                    + str(len(images_to_analyze))
                    + " images.\n Please hold."
                )
                popup_int.update()
                filename = self.FileDictionary[i]
                im_raw = self.im_raw[i]
                if im_raw.nbytes > 1024 * 1024 * 1024 * 2:
                    to_dump = {
                        "im_raw": [],
                        "filename": filename,
                        "Channel_pointers": self.Channel_pointers[i],
                        "Color_pointers": self.Color_pointers[i],
                        "im_analyzed": self.im_analyzed[i],
                        "analyze_index": self.analyze_index[i],
                        "Cell_props": self.Cell_props[i],
                        "Tissue_props": self.Tissue_props[i],
                        "analysis_params": self.analysis_params[i].copy(),
                        "foreground_threshold": self.foreground_threshold[i],
                    }
                else:
                    to_dump = {
                        "im_raw": im_raw,
                        "filename": filename,
                        "Channel_pointers": self.Channel_pointers[i],
                        "Color_pointers": self.Color_pointers[i],
                        "im_analyzed": self.im_analyzed[i],
                        "analyze_index": self.analyze_index[i],
                        "Cell_props": self.Cell_props[i],
                        "Tissue_props": self.Tissue_props[i],
                        "analysis_params": self.analysis_params[i].copy(),
                        "foreground_threshold": self.foreground_threshold[i],
                    }
                if "/" in filename:
                    filename = filedir + filename[-1 * filename[::-1].find("/") : -4]
                with open(filename + ".pickle", "wb") as f:
                    pickle.dump(to_dump, f)
        else:
            filedir = filename[: -1 * filename[::-1].find("/")]
            for n_im, i in enumerate(images_to_analyze):
                if redo_analysis:
                    label_int["text"] = (
                        "Redoing analysis for "
                        + str(n_im + 1)
                        + " of "
                        + str(len(images_to_analyze))
                        + " images.\n Please hold."
                    )
                    popup_int.update()
                    self.activeImage = i
                    self.Analysis_like = self.activeImage
                    dMO.QuickAnalysisLikeSure(self)
                label_int["text"] = (
                    "Exporting workspace for "
                    + str(n_im + 1)
                    + " of "
                    + str(len(images_to_analyze))
                    + " images.\n Please hold."
                )
                popup_int.update()
                filename = filedir + file_header + "_" + str(n_im).zfill(n_digits)
                im_raw = self.im_raw[i]
                if im_raw.nbytes > 1024 * 1024 * 1024 * 2:
                    to_dump = {
                        "im_raw": [],
                        "filename": self.FileDictionary[i],
                        "Channel_pointers": self.Channel_pointers[i],
                        "Color_pointers": self.Color_pointers[i],
                        "im_analyzed": self.im_analyzed[i],
                        "analyze_index": self.analyze_index[i],
                        "Cell_props": self.Cell_props[i],
                        "Tissue_props": self.Tissue_props[i],
                        "analysis_params": self.analysis_params[i].copy(),
                        "foreground_threshold": self.foreground_threshold[i],
                    }
                else:
                    to_dump = {
                        "im_raw": im_raw,
                        "filename": self.FileDictionary[i],
                        "Channel_pointers": self.Channel_pointers[i],
                        "Color_pointers": self.Color_pointers[i],
                        "im_analyzed": self.im_analyzed[i],
                        "analyze_index": self.analyze_index[i],
                        "Cell_props": self.Cell_props[i],
                        "Tissue_props": self.Tissue_props[i],
                        "analysis_params": self.analysis_params[i].copy(),
                        "foreground_threshold": self.foreground_threshold[i],
                    }
                with open(filename + ".pickle", "wb") as f:
                    pickle.dump(to_dump, f)
        self.activeImage = activeImage
        DestroyTK(popup_int)

    B1 = tkinter.Button(
        internal_window3,
        text="Export",
        command=lambda: [export_workspace(), DestroyTK(popup)],
    )
    B1.pack(side="left")
    B2 = tkinter.Button(
        internal_window3, text="Go Back", command=lambda: [DestroyTK(popup)]
    )
    B2.pack(side="left")

    def def_changed(*a):
        if default_name_check.get() == 1:
            labelButton.delete(0, tkinter.END)
            labelButton2.delete(0, tkinter.END)

    default_name_check.trace_add("write", def_changed)

    def label_changed(*a):
        label_name = labelButton.get()
        if len(label_name) > 0:
            default_name_check.set(False)

    label_var.trace("w", label_changed)
    popup.mainloop()


def SavePhenos(self):
    def SavePhenosSafe(*a):
        self.popList = ["Image"]
        analysis_params = self.analysis_params[self.activeImage].copy()
        analyze_index = self.analyze_index[self.activeImage]
        im_analyzed = self.im_analyzed[self.activeImage]
        Channel_pointers = self.Channel_pointers[self.activeImage]
        n_channels = self.n_channels[self.activeImage]
        Color_pointers = self.Color_pointers[self.activeImage]
        color_variable = self.color_variable[self.activeImage]
        im_raw = self.im_raw[self.activeImage]
        for i in Channel_pointers:
            self.popList.append(i)
        for i in range(n_channels, len(Color_pointers)):
            self.popList.append(analyze_index[i - n_channels])
        for n_s, pheno in enumerate(self.popList):
            n_i = n_s - 1
            if n_s > 0:
                if Color_pointers[n_i] == "black":
                    continue
            if int(digits_num.get()) > 0:
                output_digits = str(n_s).zfill(int(digits_num.get()))
            else:
                output_digits = ""
            temp = labelButton.get()
            if temp.find("*image") >= 0:
                temp_loc = temp.find("*image")
                temp = temp[:temp_loc] + filename + temp[temp_loc + 6 :]
            if temp.find("*pheno") >= 0:
                temp_loc = temp.find("*pheno")
                temp = temp[:temp_loc] + pheno + temp[temp_loc + 6 :]
            temp = temp.replace("/", " ")
            output_filename = (
                self.output_dir + temp + output_digits + file_extension.get()
            )
            if pheno == "Image":
                skimage.io.imsave(output_filename, np.array(self.im_2_display))
            elif n_i < n_channels:
                im_2_write = np.zeros(
                    (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                )
                Color_pointers_temp = color_variable[n_i].get()
                for j in range(3):
                    im_temp = im_2_write[:, :, j]
                    im2_add = im_raw[:, :, n_i] / im_raw[:, :, n_i].max()
                    im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                    im_temp = im_temp + im2_add
                    im_2_write[:, :, j] = im_temp
                skimage.io.imsave(output_filename, im_2_write)
                continue
            else:
                Color_pointers_temp = color_variable[n_i].get()
                im_temp_2 = im_analyzed[n_i - n_channels]
                if analyze_index[n_i - n_channels] == "Cells":
                    im_2_write = self.im_2_display.copy()
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
                    im2_add = im_temp_2 / im_temp_2.max()
                    dummy = im2_add > 0
                    for j in range(3):
                        im_temp = im_2_write[:, :, j]
                        im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                        im_temp[dummy] = im2_add2[dummy]
                        im_2_write[:, :, j] = im_temp
                elif analyze_index[n_i - n_channels] == "Nuclei":
                    im_2_write = self.im_2_display.copy()
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
                    im2_add = im_temp_2 / im_temp_2.max()
                    dummy = im2_add > 0
                    for j in range(3):
                        im_temp = im_2_write[:, :, j]
                        im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                        im_temp[dummy] = im2_add2[dummy]
                        im_2_write[:, :, j] = im_temp
                else:
                    if pheno in analysis_params["Phenotypes"].keys():
                        im_2_write = np.zeros(
                            (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                        )
                        ch_temp = analysis_params["Phenotypes"][pheno]["x_axis2"]
                        ch_used = False
                        if ch_temp in Channel_pointers[:n_channels]:
                            ch_used = True
                            n_ch = Channel_pointers[:n_channels].index(ch_temp)
                            Color_pointers_temp = color_variable[n_ch].get()
                            for j in range(3):
                                im_temp = im_2_write[:, :, j]
                                im2_add = im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                im_temp = im_temp + im2_add
                                im_2_write[:, :, j] = im_temp
                        ch_temp = analysis_params["Phenotypes"][pheno]["y_axis2"]
                        if ch_temp in Channel_pointers[:n_channels]:
                            ch_used = True
                            n_ch = Channel_pointers[:n_channels].index(ch_temp)
                            Color_pointers_temp = color_variable[n_ch].get()
                            for j in range(3):
                                im_temp = im_2_write[:, :, j]
                                im2_add = im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                im_temp = im_temp + im2_add
                                im_2_write[:, :, j] = im_temp
                        if not ch_used:
                            im_2_write = self.im_2_display.copy()
                        Color_pointers_temp = color_variable[n_i].get()

                        im_temp_2 = np.float32(im_temp_2) - np.float32(
                            ndi.morphology.binary_erosion(
                                im_temp_2, iterations=round(im_temp_2.shape[0] / 500)
                            )
                        )
                        im2_add = im_temp_2 / im_temp_2.max()
                        dummy = im2_add > 0
                        for j in range(3):
                            im_temp = im_2_write[:, :, j]
                            if im_temp.max() > 0:
                                im_temp = im_temp / im_temp.max()
                            im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                            im_temp[dummy] = im2_add2[dummy]
                            im_2_write[:, :, j] = im_temp
                    elif pheno in analysis_params["Segments"].keys():
                        im_temp_2 = im_analyzed[n_i - n_channels]
                        im_2_write = np.zeros(
                            (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                        )
                        ch_thres = analysis_params["Segments"][pheno]["thres"]
                        if isinstance(ch_thres, str):
                            n_ch = analysis_params["Segments"][pheno]["ch_used"]
                            n_ch = Channel_pointers[:n_channels].index(n_ch)
                            ch_used = True
                            Color_pointers_temp = color_variable[n_ch].get()
                            for j in range(3):
                                im_temp = im_2_write[:, :, j]
                                im2_add = im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                im_temp = im_temp + im2_add
                                im_2_write[:, :, j] = im_temp
                        else:
                            ch_used = False
                            for n_ch in range(n_channels):
                                if ch_thres[0][n_ch] > 0:
                                    ch_used = True
                                    Color_pointers_temp = color_variable[n_ch].get()
                                    for j in range(3):
                                        im_temp = im_2_write[:, :, j]
                                        im2_add = (
                                            im_raw[:, :, n_ch]
                                            / im_raw[:, :, n_ch].max()
                                        )
                                        im2_add = (
                                            im2_add * self.LUT[Color_pointers_temp][j]
                                        )
                                        im_temp = im_temp + im2_add
                                        im_2_write[:, :, j] = im_temp
                                elif ch_thres[1][n_ch] < np.inf:
                                    ch_used = True
                                    Color_pointers_temp = color_variable[n_ch].get()
                                    for j in range(3):
                                        im_temp = im_2_write[:, :, j]
                                        im2_add = (
                                            im_raw[:, :, n_ch]
                                            / im_raw[:, :, n_ch].max()
                                        )
                                        im2_add = (
                                            im2_add * self.LUT[Color_pointers_temp][j]
                                        )
                                        im_temp = im_temp + im2_add
                                        im_2_write[:, :, j] = im_temp
                        if not ch_used:
                            im_2_write = self.im_2_display.copy()

                        Color_pointers_temp = color_variable[n_i].get()
                        im_temp_2 = np.float32(im_temp_2) - np.float32(
                            ndi.morphology.binary_erosion(
                                im_temp_2, iterations=round(im_temp_2.shape[0] / 500)
                            )
                        )
                        im2_add = im_temp_2 / im_temp_2.max()
                        dummy = im2_add > 0
                        for j in range(3):
                            im_temp = im_2_write[:, :, j]
                            if im_temp.max() > 0:
                                im_temp = im_temp / im_temp.max()
                            im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                            im_temp[dummy] = im2_add2[dummy]
                            im_2_write[:, :, j] = im_temp
                    elif pheno == "Foreground":
                        im_2_write = np.zeros(
                            (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                        )
                        ch_thres = analysis_params[pheno]["thres"]
                        ch_used = False
                        for n_ch in range(n_channels):
                            if ch_thres[0][n_ch] > 0:
                                ch_used = True
                                Color_pointers_temp = color_variable[n_ch].get()
                                for j in range(3):
                                    im_temp = im_2_write[:, :, j]
                                    im2_add = (
                                        im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                    )
                                    im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                    im_temp = im_temp + im2_add
                                    im_2_write[:, :, j] = im_temp
                            elif ch_thres[1][n_ch] < np.inf:
                                ch_used = True
                                Color_pointers_temp = color_variable[n_ch].get()
                                for j in range(3):
                                    im_temp = im_2_write[:, :, j]
                                    im2_add = (
                                        im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                    )
                                    im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                    im_temp = im_temp + im2_add
                                    im_2_write[:, :, j] = im_temp
                        if not ch_used:
                            im_2_write = self.im_2_display.copy()
                        Color_pointers_temp = color_variable[n_i].get()
                        im_temp_2 = np.float32(im_temp_2) - np.float32(
                            ndi.morphology.binary_erosion(
                                im_temp_2, iterations=round(im_temp_2.shape[0] / 500)
                            )
                        )
                        im2_add = im_temp_2 / im_temp_2.max()
                        dummy = im2_add > 0
                        for j in range(3):
                            im_temp = im_2_write[:, :, j]
                            if im_temp.max() > 0:
                                im_temp = im_temp / im_temp.max()
                            im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                            im_temp[dummy] = im2_add2[dummy]
                            im_2_write[:, :, j] = im_temp
                    else:
                        im_2_write = np.zeros(
                            (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                        )
                        im_2_write = self.im_2_display.copy()
                        im_temp_2 = np.float32(im_temp_2) - np.float32(
                            ndi.morphology.binary_erosion(
                                im_temp_2, iterations=round(im_temp_2.shape[0] / 500)
                            )
                        )
                        im2_add = im_temp_2 / im_temp_2.max()
                        dummy = im2_add > 0
                        Color_pointers_temp = color_variable[n_i].get()
                        for j in range(3):
                            im_temp = im_2_write[:, :, j]
                            if im_temp.max() > 0:
                                im_temp = im_temp / im_temp.max()
                            im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                            im_temp[dummy] = im2_add2[dummy]
                            im_2_write[:, :, j] = im_temp
                for j in range(3):
                    im_temp = im_2_write[:, :, j]
                    if im_temp.max() > 0:
                        im_temp = im_temp / im_temp.max()
                    im_2_write[:, :, j] = im_temp
                skimage.io.imsave(output_filename, im_2_write)

    possible_extensions = [
        ".emf",
        ".eps",
        ".jpg",
        ".pdf",
        ".png",
        ".ps",
        ".raw",
        ".rgba",
        ".svg",
        ".svgz",
        ".tif",
    ]
    window_width = 100
    filename = self.FileDictionary[self.activeImage]
    self.output_dir = filename[: filename[::-1].find("/") * -1]
    filename = filename[filename[::-1].find("/") * -1 :]

    def filename_changed(*a):
        output_digits = ""
        for i in range(int(digits_num.get())):
            output_digits = output_digits + "0"
        if default_name_check.get() == 1:
            labelButton.delete(0, tkinter.END)
            labelButton.insert(0, "*image*pheno")
            labelButtonPath.delete(0, tkinter.END)
            labelButtonPath.insert(
                0,
                self.output_dir
                + labelButton.get()
                + output_digits
                + file_extension.get(),
            )
        else:
            labelButtonPath.delete(0, tkinter.END)
            labelButtonPath.insert(
                0,
                self.output_dir
                + labelButton.get()
                + output_digits
                + file_extension.get(),
            )

    def path_changed(*a):
        filename_dir = tkinter.filedialog.askdirectory(
            parent=self.master, initialdir=self.output_dir
        )
        if filename_dir[-1] == "/":
            self.output_dir = filename_dir
        else:
            self.output_dir = filename_dir + "/"
        filename_changed()

    popup = tkinter.Tk()
    popup.wm_title("Export Phenos")
    label = tkinter.Label(
        popup, text="How would you like to name your files?", width=window_width
    )
    label.pack(side="top", fill="x", pady=10)
    labelButton = tkinter.Entry(popup, width=window_width)
    labelButton.insert(0, "*image*pheno")
    labelButton.pack()
    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")
    default_name_check = tkinter.IntVar(internal_window)
    default_name_check.set(1)
    default_check = tkinter.Checkbutton(
        internal_window, variable=default_name_check, text="Use figure titles?"
    )
    default_check.pack(side="left")
    default_name_check.trace("w", filename_changed)

    Update_filename = tkinter.Button(
        internal_window, text="Update", command=filename_changed
    )
    Update_filename.pack(side="left")

    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")

    label = tkinter.Label(internal_window, text="Number of Digits:")
    label.pack(side=tkinter.LEFT, fill="x", pady=10)

    digits_num = tkinter.StringVar(internal_window)
    digits_num.set(0)
    digits_num.trace("w", filename_changed)
    digits_numDropdown = tkinter.OptionMenu(
        internal_window, digits_num, *[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    )
    digits_numDropdown.config(width=10)
    digits_numDropdown.pack(side=tkinter.LEFT, padx=2, pady=2)

    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")

    label = tkinter.Label(internal_window, text="Extension:")
    label.pack(side=tkinter.LEFT, fill="x", pady=10)

    file_extension = tkinter.StringVar(internal_window)
    file_extension.set(".png")
    file_extension.trace("w", filename_changed)
    file_extensionDropdown = tkinter.OptionMenu(
        internal_window, file_extension, *possible_extensions
    )
    file_extensionDropdown.config(width=10)
    file_extensionDropdown.pack(side=tkinter.LEFT, padx=2, pady=2)

    label = tkinter.Label(popup, text="Current path:")
    label.pack(side="top", fill="x", pady=10)

    labelButtonPath = tkinter.Entry(popup, width=window_width)
    try:
        labelButtonPath.insert(
            0, self.output_dir + labelButton.get() + file_extension.get()
        )
    except TypeError:
        pass
    labelButtonPath.pack()

    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")

    label = tkinter.Label(internal_window, text="")
    label.pack(side=tkinter.LEFT, fill="x", pady=10)

    internal_window3 = tkinter.Frame(popup)
    internal_window3.pack(side="top")

    Change_path = tkinter.Button(
        internal_window3, text="Change Path", command=path_changed
    )
    Change_path.pack(side="left")
    B1 = tkinter.Button(
        internal_window3,
        text="Export",
        command=lambda: [SavePhenosSafe(), popup.destroy()],
    )
    B1.pack(side="left")
    B2 = tkinter.Button(internal_window3, text="Go Back", command=popup.destroy)
    B2.pack(side="left")

    popup.mainloop()


def SavePhenosAll(self):
    def SavePhenosSafe(*a):
        popList_out = ["Image"]
        analyze_index_out = self.analyze_index[self.activeImage]
        Channel_pointers_out = self.Channel_pointers[self.activeImage]
        n_channels_out = self.n_channels[self.activeImage]
        Color_pointers_out = self.Color_pointers[self.activeImage]
        color_variable_out = self.color_variable[self.activeImage]
        for i in Channel_pointers_out:
            popList_out.append(i)
        for i in range(n_channels_out, len(Color_pointers_out)):
            popList_out.append(analyze_index_out[i - n_channels_out])
        for activeImage in range(len(self.FileDictionary)):
            popList = ["Image"]
            analysis_params = self.analysis_params[activeImage].copy()
            analyze_index = self.analyze_index[activeImage]
            im_analyzed = self.im_analyzed[activeImage]
            Channel_pointers = self.Channel_pointers[activeImage]
            n_channels = self.n_channels[activeImage]
            Color_pointers = self.Color_pointers[activeImage]
            color_variable = self.color_variable[activeImage]
            filename = self.FileDictionary[activeImage]
            filename = filename[filename[::-1].find("/") * -1 :]
            im_raw = self.im_raw[activeImage]
            for i in Channel_pointers:
                popList.append(i)
            for i in range(n_channels, len(Color_pointers)):
                popList.append(analyze_index[i - n_channels])
            if default_color_check.get() < 1:
                analyze_index_out = analyze_index
                Channel_pointers_out = Channel_pointers
                n_channels_out = n_channels
                Color_pointers_out = Color_pointers
                color_variable_out = color_variable
                popList_out = popList
            make_im_2_display = True
            if make_im_2_display:
                im_2_display = np.zeros(
                    (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                )
                for i in range(n_channels):
                    Color_pointers_temp = color_variable[i].get()
                    for j in range(3):
                        im_temp = im_2_display[:, :, j]
                        im2_add = im_raw[:, :, i] / im_raw[:, :, i].max()
                        im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                        im_temp = im_temp + im2_add
                        im_2_display[:, :, j] = im_temp
                for i in range(n_channels, len(Color_pointers)):
                    Color_pointers_temp = color_variable[i].get()
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
                    im2_add = im_temp_2 / im_temp_2.max()
                    dummy = im2_add > 0
                    for j in range(3):
                        im_temp = im_2_display[:, :, j]
                        im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                        im_temp[dummy] = im2_add2[dummy]
                        im_2_display[:, :, j] = im_temp

            for n_s, pheno in enumerate(popList):
                n_i = n_s - 1
                if pheno in popList_out:
                    if popList_out.count(pheno) == 1:
                        n_o = popList_out.index(pheno)
                        if popList.count(pheno) > 1:
                            print(filename, "has unmatching channels", pheno)
                    elif popList_out.count(pheno) == popList.count(pheno):
                        if pheno != "DAPI":
                            print(filename, "has misnamed channel", pheno)
                        out_indexes = list(
                            np.unique(
                                [
                                    popList_out.index(pheno, i)
                                    for i in range(len(popList_out))
                                    if pheno in popList_out[i:]
                                ]
                            )
                        )
                        in_indexes = list(
                            np.unique(
                                [
                                    popList.index(pheno, i)
                                    for i in range(len(popList))
                                    if pheno in popList[i:]
                                ]
                            )
                        )
                        n_o = out_indexes[in_indexes.index(n_s)]
                    else:
                        print(filename, "has unmatching channels", pheno)
                        n_o = popList_out.index(pheno)
                    n_o -= 1
                else:
                    continue
                if n_s > 0:
                    if Color_pointers_out[n_o] == "black":
                        continue
                if int(digits_num.get()) > 0:
                    output_digits = str(n_o + 1).zfill(int(digits_num.get()))
                else:
                    output_digits = ""
                temp = labelButton.get()
                if temp.find("*image") >= 0:
                    temp_loc = temp.find("*image")
                    temp = temp[:temp_loc] + filename + temp[temp_loc + 6 :]
                if temp.find("*pheno") >= 0:
                    temp_loc = temp.find("*pheno")
                    temp = temp[:temp_loc] + pheno + temp[temp_loc + 6 :]
                temp = temp.replace("/", " ")
                output_filename = (
                    self.output_dir + temp + output_digits + file_extension.get()
                )
                if pheno == "Image":
                    skimage.io.imsave(output_filename, im_2_display)
                elif n_i < n_channels:
                    im_2_write = np.zeros(
                        (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                    )
                    Color_pointers_temp = color_variable_out[n_o].get()
                    for j in range(3):
                        im_temp = im_2_write[:, :, j]
                        im2_add = im_raw[:, :, n_i] / im_raw[:, :, n_i].max()
                        im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                        im_temp = im_temp + im2_add
                        im_2_write[:, :, j] = im_temp
                    skimage.io.imsave(output_filename, im_2_write)
                    continue
                else:
                    Color_pointers_temp = color_variable_out[n_o].get()
                    im_temp_2 = im_analyzed[n_i - n_channels]
                    if analyze_index[n_i - n_channels] == "Cells":
                        im_2_write = im_2_display.copy()
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
                        im2_add = im_temp_2 / im_temp_2.max()
                        dummy = im2_add > 0
                        for j in range(3):
                            im_temp = im_2_write[:, :, j]
                            im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                            im_temp[dummy] = im2_add2[dummy]
                            im_2_write[:, :, j] = im_temp
                    elif analyze_index[n_i - n_channels] == "Nuclei":
                        im_2_write = im_2_display.copy()
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
                        im2_add = im_temp_2 / im_temp_2.max()
                        dummy = im2_add > 0
                        for j in range(3):
                            im_temp = im_2_write[:, :, j]
                            im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                            im_temp[dummy] = im2_add2[dummy]
                            im_2_write[:, :, j] = im_temp
                    else:
                        if pheno in analysis_params["Phenotypes"].keys():
                            im_2_write = np.zeros(
                                (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                            )
                            ch_temp = analysis_params["Phenotypes"][pheno]["x_axis2"]
                            ch_used = False
                            if ch_temp in Channel_pointers[:n_channels]:
                                ch_used = True
                                n_ch = Channel_pointers[:n_channels].index(ch_temp)
                                Color_pointers_temp = color_variable_out[n_ch].get()
                                for j in range(3):
                                    im_temp = im_2_write[:, :, j]
                                    im2_add = (
                                        im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                    )
                                    im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                    im_temp = im_temp + im2_add
                                    im_2_write[:, :, j] = im_temp
                            ch_temp = analysis_params["Phenotypes"][pheno]["y_axis2"]
                            if ch_temp in Channel_pointers[:n_channels]:
                                ch_used = True
                                n_ch = Channel_pointers[:n_channels].index(ch_temp)
                                Color_pointers_temp = color_variable_out[n_ch].get()
                                for j in range(3):
                                    im_temp = im_2_write[:, :, j]
                                    im2_add = (
                                        im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                    )
                                    im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                    im_temp = im_temp + im2_add
                                    im_2_write[:, :, j] = im_temp
                            if not ch_used:
                                im_2_write = im_2_display.copy()
                            Color_pointers_temp = color_variable_out[n_o].get()

                            im_temp_2 = np.float32(im_temp_2) - np.float32(
                                ndi.morphology.binary_erosion(
                                    im_temp_2,
                                    iterations=round(im_temp_2.shape[0] / 500),
                                )
                            )
                            im2_add = im_temp_2 / im_temp_2.max()
                            dummy = im2_add > 0
                            for j in range(3):
                                im_temp = im_2_write[:, :, j]
                                if im_temp.max() > 0:
                                    im_temp = im_temp / im_temp.max()
                                im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                                im_temp[dummy] = im2_add2[dummy]
                                im_2_write[:, :, j] = im_temp
                        elif pheno in analysis_params["Segments"].keys():
                            im_temp_2 = im_analyzed[n_i - n_channels]
                            im_2_write = np.zeros(
                                (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                            )
                            ch_thres = analysis_params["Segments"][pheno]["thres"]
                            if isinstance(ch_thres, str):
                                n_ch = analysis_params["Segments"][pheno]["ch_used"]
                                n_ch = Channel_pointers[:n_channels].index(n_ch)
                                ch_used = True
                                Color_pointers_temp = color_variable_out[n_ch].get()
                                for j in range(3):
                                    im_temp = im_2_write[:, :, j]
                                    im2_add = (
                                        im_raw[:, :, n_ch] / im_raw[:, :, n_ch].max()
                                    )
                                    im2_add = im2_add * self.LUT[Color_pointers_temp][j]
                                    im_temp = im_temp + im2_add
                                    im_2_write[:, :, j] = im_temp
                            else:
                                ch_used = False
                                for n_ch in range(n_channels):
                                    if ch_thres[0][n_ch] > 0:
                                        ch_used = True
                                        Color_pointers_temp = color_variable_out[
                                            n_ch
                                        ].get()
                                        for j in range(3):
                                            im_temp = im_2_write[:, :, j]
                                            im2_add = (
                                                im_raw[:, :, n_ch]
                                                / im_raw[:, :, n_ch].max()
                                            )
                                            im2_add = (
                                                im2_add
                                                * self.LUT[Color_pointers_temp][j]
                                            )
                                            im_temp = im_temp + im2_add
                                            im_2_write[:, :, j] = im_temp
                                    elif ch_thres[1][n_ch] < np.inf:
                                        ch_used = True
                                        Color_pointers_temp = color_variable_out[
                                            n_ch
                                        ].get()
                                        for j in range(3):
                                            im_temp = im_2_write[:, :, j]
                                            im2_add = (
                                                im_raw[:, :, n_ch]
                                                / im_raw[:, :, n_ch].max()
                                            )
                                            im2_add = (
                                                im2_add
                                                * self.LUT[Color_pointers_temp][j]
                                            )
                                            im_temp = im_temp + im2_add
                                            im_2_write[:, :, j] = im_temp
                            if not ch_used:
                                im_2_write = im_2_display.copy()

                            Color_pointers_temp = color_variable_out[n_o].get()
                            im_temp_2 = np.float32(im_temp_2) - np.float32(
                                ndi.morphology.binary_erosion(
                                    im_temp_2,
                                    iterations=round(im_temp_2.shape[0] / 500),
                                )
                            )
                            im2_add = im_temp_2 / im_temp_2.max()
                            dummy = im2_add > 0
                            for j in range(3):
                                im_temp = im_2_write[:, :, j]
                                if im_temp.max() > 0:
                                    im_temp = im_temp / im_temp.max()
                                im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                                im_temp[dummy] = im2_add2[dummy]
                                im_2_write[:, :, j] = im_temp
                        elif pheno == "Foreground":
                            im_2_write = np.zeros(
                                (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                            )
                            ch_thres = analysis_params[pheno]["thres"]
                            ch_used = False
                            for n_ch in range(n_channels):
                                if ch_thres[0][n_ch] > 0:
                                    ch_used = True
                                    Color_pointers_temp = color_variable_out[n_ch].get()
                                    for j in range(3):
                                        im_temp = im_2_write[:, :, j]
                                        im2_add = (
                                            im_raw[:, :, n_ch]
                                            / im_raw[:, :, n_ch].max()
                                        )
                                        im2_add = (
                                            im2_add * self.LUT[Color_pointers_temp][j]
                                        )
                                        im_temp = im_temp + im2_add
                                        im_2_write[:, :, j] = im_temp
                                elif ch_thres[1][n_ch] < np.inf:
                                    ch_used = True
                                    Color_pointers_temp = color_variable_out[n_ch].get()
                                    for j in range(3):
                                        im_temp = im_2_write[:, :, j]
                                        im2_add = (
                                            im_raw[:, :, n_ch]
                                            / im_raw[:, :, n_ch].max()
                                        )
                                        im2_add = (
                                            im2_add * self.LUT[Color_pointers_temp][j]
                                        )
                                        im_temp = im_temp + im2_add
                                        im_2_write[:, :, j] = im_temp
                            if not ch_used:
                                im_2_write = im_2_display.copy()
                            im_temp_2 = np.float32(im_temp_2) - np.float32(
                                ndi.morphology.binary_erosion(
                                    im_temp_2,
                                    iterations=round(im_temp_2.shape[0] / 500),
                                )
                            )
                            Color_pointers_temp = color_variable_out[n_o].get()
                            im2_add = im_temp_2 / im_temp_2.max()
                            dummy = im2_add > 0
                            for j in range(3):
                                im_temp = im_2_write[:, :, j]
                                if im_temp.max() > 0:
                                    im_temp = im_temp / im_temp.max()
                                im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                                im_temp[dummy] = im2_add2[dummy]
                                im_2_write[:, :, j] = im_temp
                        else:
                            im_2_write = np.zeros(
                                (im_raw.shape[0], im_raw.shape[1], 3), dtype=np.float32
                            )
                            im_2_write = im_2_display.copy()
                            im_temp_2 = np.float32(im_temp_2) - np.float32(
                                ndi.morphology.binary_erosion(
                                    im_temp_2,
                                    iterations=round(im_temp_2.shape[0] / 500),
                                )
                            )
                            im2_add = im_temp_2 / im_temp_2.max()
                            dummy = im2_add > 0
                            Color_pointers_temp = color_variable_out[n_o].get()
                            for j in range(3):
                                im_temp = im_2_write[:, :, j]
                                if im_temp.max() > 0:
                                    im_temp = im_temp / im_temp.max()
                                im2_add2 = im2_add * self.LUT[Color_pointers_temp][j]
                                im_temp[dummy] = im2_add2[dummy]
                                im_2_write[:, :, j] = im_temp
                    for j in range(3):
                        im_temp = im_2_write[:, :, j]
                        if im_temp.max() > 0:
                            im_temp = im_temp / im_temp.max()
                        im_2_write[:, :, j] = im_temp
                    skimage.io.imsave(output_filename, im_2_write)

    possible_extensions = [
        ".emf",
        ".eps",
        ".jpg",
        ".pdf",
        ".png",
        ".ps",
        ".raw",
        ".rgba",
        ".svg",
        ".svgz",
        ".tif",
    ]
    window_width = 100
    filename = self.FileDictionary[self.activeImage]
    self.output_dir = filename[: filename[::-1].find("/") * -1]
    filename = filename[filename[::-1].find("/") * -1 :]

    def filename_changed(*a):
        output_digits = ""
        for i in range(int(digits_num.get())):
            output_digits = output_digits + "0"
        if default_name_check.get() == 1:
            labelButton.delete(0, tkinter.END)
            labelButton.insert(0, "*image*pheno")
            labelButtonPath.delete(0, tkinter.END)
            labelButtonPath.insert(
                0,
                self.output_dir
                + labelButton.get()
                + output_digits
                + file_extension.get(),
            )
        else:
            labelButtonPath.delete(0, tkinter.END)
            labelButtonPath.insert(
                0,
                self.output_dir
                + labelButton.get()
                + output_digits
                + file_extension.get(),
            )

    def path_changed(*a):
        filename_dir = tkinter.filedialog.askdirectory(
            parent=self.master, initialdir=self.output_dir
        )
        if filename_dir[-1] == "/":
            self.output_dir = filename_dir
        else:
            self.output_dir = filename_dir + "/"
        filename_changed()

    popup = tkinter.Tk()
    popup.wm_title("Export Phenos")
    label = tkinter.Label(
        popup, text="How would you like to name your files?", width=window_width
    )
    label.pack(side="top", fill="x", pady=10)
    labelButton = tkinter.Entry(popup, width=window_width)
    labelButton.insert(0, "*image*pheno")
    labelButton.pack()
    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")
    default_name_check = tkinter.IntVar(internal_window)
    default_name_check.set(1)
    default_check = tkinter.Checkbutton(
        internal_window, variable=default_name_check, text="Use figure titles?"
    )
    default_check.pack(side="left")
    default_name_check.trace("w", filename_changed)

    Update_filename = tkinter.Button(
        internal_window, text="Update", command=filename_changed
    )
    Update_filename.pack(side="left")

    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")

    label = tkinter.Label(internal_window, text="Number of Digits:")
    label.pack(side=tkinter.LEFT, fill="x", pady=10)

    digits_num = tkinter.StringVar(internal_window)
    digits_num.set(0)
    digits_num.trace("w", filename_changed)
    digits_numDropdown = tkinter.OptionMenu(
        internal_window, digits_num, *[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    )
    digits_numDropdown.config(width=10)
    digits_numDropdown.pack(side=tkinter.LEFT, padx=2, pady=2)

    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")

    label = tkinter.Label(internal_window, text="Extension:")
    label.pack(side=tkinter.LEFT, fill="x", pady=10)

    file_extension = tkinter.StringVar(internal_window)
    file_extension.set(".png")
    file_extension.trace("w", filename_changed)
    file_extensionDropdown = tkinter.OptionMenu(
        internal_window, file_extension, *possible_extensions
    )
    file_extensionDropdown.config(width=10)
    file_extensionDropdown.pack(side=tkinter.LEFT, padx=2, pady=2)

    label = tkinter.Label(popup, text="Current path:")
    label.pack(side="top", fill="x", pady=10)

    labelButtonPath = tkinter.Entry(popup, width=window_width)
    try:
        labelButtonPath.insert(
            0, self.output_dir + labelButton.get() + file_extension.get()
        )
    except TypeError:
        pass
    labelButtonPath.pack()

    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")

    label = tkinter.Label(internal_window, text="")
    label.pack(side=tkinter.LEFT, fill="x", pady=10)

    internal_window = tkinter.Frame(popup)
    internal_window.pack(side="top")

    default_color_check = tkinter.IntVar(internal_window)
    default_color_check.set(1)
    default_check = tkinter.Checkbutton(
        internal_window,
        variable=default_color_check,
        text="Use current colors/phenos on all?",
    )
    default_check.pack(side="left")

    internal_window3 = tkinter.Frame(popup)
    internal_window3.pack(side="top")

    Change_path = tkinter.Button(
        internal_window3, text="Change Path", command=path_changed
    )
    Change_path.pack(side="left")
    B1 = tkinter.Button(
        internal_window3,
        text="Export",
        command=lambda: [SavePhenosSafe(), popup.destroy()],
    )
    B1.pack(side="left")
    B2 = tkinter.Button(internal_window3, text="Go Back", command=popup.destroy)
    B2.pack(side="left")

    popup.mainloop()
