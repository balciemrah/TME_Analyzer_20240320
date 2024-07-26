import tkinter
import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as Tk_Agg
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk as NT2Tk

# import sklearn.linear_model
# from scipy.stats import linregress
from tkinter import ttk as ttkinter
from skimage.feature import peak_local_max
from scipy import ndimage as ndi
import skimage
from collections import Counter
import stardist
import stardist.models
from csbdeep.utils import normalize as StarDist2D_normalize
from math import atan2, log, pi as PI
import pandas as pd


def DestroyTK(tk_param):
    try:
        tk_param.destroy()
    except tkinter.TclError:
        pass
    except ttkinter.TclError:
        pass


def popupmsg(msg, self_control=True):
    def Quit(*a):
        popupnew2 = tkinter.Tk()
        popupnew2.wm_title("!")
        label2 = tkinter.Label(
            popupnew2,
            text="This will stop the current"
            + " operation following this iteration!\n"
            + "Are you sure?",
        )
        label2.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popupnew2,
            text="Go Ahead",
            command=lambda: [DestroyTK(popupnew2), DestroyTK(popupnew)],
        )
        B1.pack()
        B2 = tkinter.Button(
            popupnew2, text="Go Back", command=lambda: [DestroyTK(popupnew2)]
        )
        B2.pack()
        popupnew2.mainloop()

    popupnew = tkinter.Tk()
    popupnew.wm_title("!")
    label = tkinter.Label(popupnew, text=msg)
    label.pack(side="top", fill="x", pady=10)
    if self_control:
        B1 = tkinter.Button(
            popupnew, text="Okay", command=lambda: [DestroyTK(popupnew)]
        )
        B1.pack()
    else:
        popupnew.protocol("WM_DELETE_WINDOW", Quit)
    popupnew.update()
    return popupnew, label


class Slider(tkinter.Frame):
    def __init__(self, parent=None, area_lim=None):
        self.text_mod = False
        tkinter.Frame.__init__(self, parent)
        scale_window = tkinter.Frame(self)
        scale_window.pack(side=tkinter.RIGHT)
        self.number = 0
        self.slide = tkinter.Scale(
            scale_window,
            orient=tkinter.HORIZONTAL,
            command=self.setValue,
            length=200,
            sliderlength=20,
            showvalue=0,
            resolution=0.01,
            fro=0,
            to=6,
            font=("Arial", 9),
        )
        if area_lim is None:
            self.txt_value = tkinter.StringVar(self)
        else:
            for i in area_lim.trace_info():
                area_lim.trace_remove(i[0], i[1])
            self.txt_value = area_lim

        self.text = tkinter.Entry(scale_window, textvariable=self.txt_value)
        txt = self.text.get()
        if txt != "inf":
            try:
                self.number = np.float(txt)
                self.text_mod = True
                self.slide.set(log(self.number, 10))
                self.number = np.float(txt)
            except ValueError:
                self.slide.set(6)
        else:
            self.slide.set(6)
        self.trace = self.txt_value.trace_add("write", self.text_changed)
        # labelButton =
        # labelButton.pack()
        # self.text.insert(0, "DAPI")
        self.slide.pack(side=tkinter.TOP, expand=1, fill=tkinter.X)
        self.text.pack(side=tkinter.TOP, fill=tkinter.BOTH)

    def text_changed(self, *a):
        txt = self.text.get()
        if txt != "inf":
            try:
                self.number = np.float(txt)
                self.text_mod = True
                self.slide.set(log(self.number, 10))
                self.number = np.float(txt)
            except ValueError:
                pass

    def setValue(self, val):
        if float(val) == 6:
            self.number = np.inf
        else:
            self.number = 10 ** (np.float(val))
        # self.text.configure(text='%s' %self.number)
        if not (self.text_mod):
            self.txt_value.trace_remove("write", self.trace)
            self.text.delete(0, tkinter.END)
            self.text.insert(0, "%s" % self.number)
            self.trace = self.txt_value.trace_add("write", self.text_changed)
        else:
            self.text_mod = False


def SelectROI(self):
    def resetROI(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to reset ROI")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2, text="Go Ahead", command=lambda: [DestroyTK(popup2), resetROIsure()]
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def resetROIsure(*a):
        self.activeROI = []
        ax = self.ax
        ax.clear()
        ax.imshow(self.im_2_display, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        self.ax_canvas.draw()
        self.ROIPolygon = matplotlib.widgets.PolygonSelector(
            self.ax,
            ROIselected,
            lineprops=dict(color="w", linestyle="-", linewidth=2, alpha=0.5),
            markerprops=dict(marker="o", markersize=7, mec="w", mfc="w", alpha=0.5),
        )

    def ROIselected(verts):
        self.ROIverts = verts

    def addROI(*a):
        ROI_path = matplotlib.path.Path(self.ROIPolygon.verts)
        im_temp = self.im_2_display
        y, x = np.mgrid[: im_temp.shape[0], : im_temp.shape[1]]
        points = np.transpose((x.ravel(), y.ravel()))
        mask = ROI_path.contains_points(points)
        mask = mask.reshape(im_temp.shape[0], im_temp.shape[1])
        if len(self.activeROI) == 0:
            self.activeROI = mask
        else:
            self.activeROI = self.activeROI | mask
        mask_copy = np.float32(self.activeROI)
        mask_copy = (1 - mask_copy) / 2
        for i in range(3):
            im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
        ax = self.ax
        ax.clear()
        ax.imshow(im_temp, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        for i in range(3):
            im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
        self.ax_canvas.draw()
        self.ROIPolygon.disconnect_events()
        self.ROIPolygon = matplotlib.widgets.PolygonSelector(
            self.ax,
            ROIselected,
            lineprops=dict(color="w", linestyle="-", linewidth=2, alpha=0.5),
            markerprops=dict(marker="o", markersize=7, mec="w", mfc="w", alpha=0.5),
        )

    def removeROI(*a):
        ROI_path = matplotlib.path.Path(self.ROIPolygon.verts)
        im_temp = self.im_2_display
        y, x = np.mgrid[: im_temp.shape[0], : im_temp.shape[1]]
        points = np.transpose((x.ravel(), y.ravel()))
        mask = ROI_path.contains_points(points) == 0
        mask = mask.reshape(im_temp.shape[0], im_temp.shape[1])
        if len(self.activeROI) == 0:
            self.activeROI = mask
        else:
            self.activeROI = self.activeROI & mask
        mask_copy = np.float32(self.activeROI)
        mask_copy = (1 - mask_copy) / 2
        for i in range(3):
            im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
        ax = self.ax
        ax.clear()
        ax.imshow(im_temp, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        for i in range(3):
            im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
        self.ax_canvas.draw()
        self.ROIPolygon.disconnect_events()
        self.ROIPolygon = matplotlib.widgets.PolygonSelector(
            self.ax,
            ROIselected,
            lineprops=dict(color="w", linestyle="-", linewidth=2, alpha=0.5),
            markerprops=dict(marker="o", markersize=7, mec="w", mfc="w", alpha=0.5),
        )

    def SaveROI(*a):
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        if len(self.activeROI) != 0:
            if "ROI" in analyze_index:
                im_analyzed[analyze_index.index("ROI")] = self.activeROI
                self.im_analyzed[self.activeImage] = im_analyzed
            else:
                im_analyzed.append(self.activeROI)
                analyze_index.append("ROI")
                self.im_analyzed[self.activeImage] = im_analyzed
                self.analyze_index[self.activeImage] = analyze_index
                self.remake_side_window()
        else:
            if "ROI" in analyze_index:
                im_analyzed.pop(analyze_index.index("ROI"))
                color_variable = self.color_variable[self.activeImage]
                Color_pointers = self.Color_pointers[self.activeImage]
                color_variable.pop(
                    analyze_index.index("ROI") + self.n_channels[self.activeImage]
                )
                Color_pointers.pop(
                    analyze_index.index("ROI") + self.n_channels[self.activeImage]
                )
                analyze_index.pop(analyze_index.index("ROI"))
                self.im_analyzed[self.activeImage] = im_analyzed
                self.analyze_index[self.activeImage] = analyze_index
                self.color_variable[self.activeImage] = color_variable
                self.Color_pointers[self.activeImage] = Color_pointers
                self.remake_side_window()
        DestroyTK(self.popup)

    def QuitROI(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to quit without saving")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Okay",
            command=lambda: [DestroyTK(self.popup), DestroyTK(popup2), resetROIsure()],
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    im_analyzed = self.im_analyzed[self.activeImage]
    analyze_index = self.analyze_index[self.activeImage]
    if len(im_analyzed) == 0:
        self.activeROI = []
    else:
        if "ROI" in analyze_index:
            self.activeROI = im_analyzed[analyze_index.index("ROI")]
        else:
            self.activeROI = []
    popup = tkinter.Tk()
    self.popup = popup
    im_2_display = self.im_2_display
    popup.wm_title("ROI Selection")
    label = tkinter.Label(
        popup, text="ROI selection for file :" + self.FileDictionary[self.activeImage]
    )
    toolbar = tkinter.Frame(popup)
    resetButton = tkinter.Button(toolbar, text="Reset ROI", command=resetROI)
    resetButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    addButton = tkinter.Button(toolbar, text="Add ROI", command=addROI)
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    removeButton = tkinter.Button(toolbar, text="Remove ROI", command=removeROI)
    removeButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    registerButton = tkinter.Button(toolbar, text="Save and Quit", command=SaveROI)
    registerButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    cancelButton = tkinter.Button(toolbar, text="Quit", command=QuitROI)
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
    ax.autoscale(False)
    ax.axis("off")
    self.ax = ax
    image_canvas.draw()
    self.ax_canvas = image_canvas
    self.popup_statusBar = tkinter.Label(
        popup, text="Working on ROI", bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
    )
    self.popup_statusBar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
    if len(self.activeROI) != 0:
        im_temp = self.im_2_display
        mask_copy = np.float32(self.activeROI)
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
            DestroyTK(self.popup_statusBar)
    t = (
        "Select points in the figure by enclosing them within a polygon. "
        + "Press the 'esc' key to start a new polygon. "
        + "\nTry holding the 'shift' key to move all of the vertices. "
        + "Try holding the 'ctrl' key to move a single vertex."
        + "\nOnce finished, either add ROI or remove ROI by pressing the "
        + "relevant button"
    )
    self.popup_statusBar = tkinter.Label(
        self.popup, text=t, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
    )
    self.popup_statusBar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
    self.ROIPolygon = matplotlib.widgets.PolygonSelector(
        self.ax,
        ROIselected,
        lineprops=dict(color="w", linestyle="-", linewidth=2, alpha=0.5),
        markerprops=dict(marker="o", markersize=7, mec="w", mfc="w", alpha=0.5),
    )
    popup.mainloop()


def UnmixChannels(self):
    def UnmixForAllImages(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Channel Unmixing All")
        label = tkinter.Label(
            popup2,
            text="This will overwrite all your images!"
            + "\nAre you sure?\n\nPS: It is advised that"
            + " you manually check\nyour analysis "
            + "following this step.",
        )
        label.pack(side="top", fill="x", pady=10)
        internal_windows_4 = tkinter.Frame(popup2, width=100, height=20)
        internal_windows_4.pack(side=tkinter.TOP)

        unmix_button = tkinter.Button(
            master=internal_windows_4,
            text="Yes",
            command=lambda: [DestroyTK(popup2), Perform_All_Unmix()],
        )
        unmix_button.pack(side=tkinter.TOP)

        back_button = tkinter.Button(
            master=internal_windows_4,
            text="Cancel",
            command=lambda: [DestroyTK(popup2)],
        )
        back_button.pack(side=tkinter.TOP)

    def Perform_All_Unmix(*a):
        inputted_params = []
        inputted_params.append(self.unmix_params[0].get())
        inputted_params.append(self.unmix_params[1].get())
        inputted_params.append(self.unmix_params[2].get())
        inputted_params.append(np.float32(self.unmix_params[3].get()))
        inputted_params.append(np.float32(self.unmix_params[4].get()))
        inputted_params.append(True)

        if (inputted_params[0] == "All") & (inputted_params[2] == "All"):
            popupmsg(
                "Did not think any sane person "
                + "would want this...\n"
                + "If you are reading this message, and "
                + "really want this implemented\n"
                + "send an email to Emrah to implement this."
            )
        else:
            DestroyTK(self.popup)
            [popup, label] = popupmsg("...", False)
            for self.activeImage in range(len(self.FileDictionary)):
                label["text"] = (
                    "Unmixing image "
                    + str(self.activeImage + 1)
                    + " of "
                    + str(len(self.FileDictionary))
                    + " images.\n Please hold."
                )
                popup.update()
                Perform_Unmix(inputted_params=inputted_params)
            DestroyTK(popup)

    def WannaPerform_Unmix(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Channel Unmixing")
        label = tkinter.Label(
            popup2, text="This will overwrite your image!\n" + "Are you sure?"
        )
        label.pack(side="top", fill="x", pady=10)
        internal_windows_4 = tkinter.Frame(popup2, width=100, height=20)
        internal_windows_4.pack(side=tkinter.TOP)

        unmix_button = tkinter.Button(
            master=internal_windows_4,
            text="Yes",
            command=lambda: [DestroyTK(popup2), Perform_Unmix()],
        )
        unmix_button.pack(side=tkinter.TOP)

        back_button = tkinter.Button(
            master=internal_windows_4,
            text="Cancel",
            command=lambda: [DestroyTK(popup2)],
        )
        back_button.pack(side=tkinter.TOP)

    def Perform_Unmix(*a, inputted_params=[]):
        Channel_pointers = self.Channel_pointers[self.activeImage]
        if len(inputted_params) == 0:
            channel_variable_1 = self.unmix_params[0].get()
            direction_variable = self.unmix_params[1].get()
            channel_variable_2 = self.unmix_params[2].get()
            unmix_threshold = np.float32(self.unmix_params[3].get())
            unmix_range = np.float32(self.unmix_params[4].get())
            if unmix_range <= 0:
                unmix_range = 100
            popup_control_out = False
        else:
            channel_variable_1 = inputted_params[0]
            direction_variable = inputted_params[1]
            channel_variable_2 = inputted_params[2]
            unmix_threshold = inputted_params[3]
            unmix_range = inputted_params[4]
            if unmix_range <= 0:
                unmix_range = 100
            popup_control_out = inputted_params[5]

        im_raw = self.im_raw[self.activeImage]
        n_channels = min(im_raw.shape)
        im_raw_temp = im_raw.copy()
        destroy_popup = True
        if channel_variable_1 != "All":
            ch_1 = Channel_pointers.index(channel_variable_1)
            if channel_variable_2 != "All":
                ch_2 = Channel_pointers.index(channel_variable_2)
                im_1 = im_raw[:, :, ch_1].ravel()
                im_2 = im_raw[:, :, ch_2].ravel()
                im_1 = im_1[(im_2 == im_2)]
                im_2 = im_2[(im_2 == im_2)]
                im_2 = im_2[(im_1 == im_1)]
                im_1 = im_1[(im_1 == im_1)]
                if direction_variable == "Bleed to":
                    if unmix_range < 100:
                        im_2 = im_2[
                            np.argsort(im_1)[
                                -1 * np.int32(len(im_1) * unmix_range / 100) :
                            ]
                        ]
                        im_1 = im_1[
                            np.argsort(im_1)[
                                -1 * np.int32(len(im_1) * unmix_range / 100) :
                            ]
                        ]
                    z = np.polyfit(im_1, im_2, 1)  # subtract 1 from 2
                    p_1 = np.poly1d(z)
                    if unmix_threshold > 0:
                        y_hat = p_1(im_1)
                        y_bar = np.sum(im_2) / len(im_2)
                        ssreg = np.sum((y_hat - y_bar) ** 2)
                        sstot = np.sum((im_2 - y_bar) ** 2)
                        r_square = ssreg / sstot
                        if r_square > unmix_threshold:
                            im_raw_temp[:, :, ch_2] = (
                                im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                            )
                    else:
                        im_raw_temp[:, :, ch_2] = (
                            im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                        )
                else:
                    if unmix_range < 100:
                        im_1 = im_1[
                            np.argsort(im_2)[
                                -1 * np.int32(len(im_2) * unmix_range / 100) :
                            ]
                        ]
                        im_2 = im_2[
                            np.argsort(im_2)[
                                -1 * np.int32(len(im_2) * unmix_range / 100) :
                            ]
                        ]
                    z = np.polyfit(im_2, im_1, 1)  # subtract 1 from 2
                    p_1 = np.poly1d(z)
                    if unmix_threshold > 0:
                        y_hat = p_1(im_2)
                        y_bar = np.sum(im_1) / len(im_1)
                        ssreg = np.sum((y_hat - y_bar) ** 2)
                        sstot = np.sum((im_1 - y_bar) ** 2)
                        r_square = ssreg / sstot
                        if r_square > unmix_threshold:
                            im_raw_temp[:, :, ch_1] = (
                                im_raw[:, :, ch_1] - p_1(im_raw[:, :, ch_2]) + p_1(0)
                            )
                    else:
                        im_raw_temp[:, :, ch_1] = (
                            im_raw[:, :, ch_1] - p_1(im_raw[:, :, ch_2]) + p_1(0)
                        )

                if direction_variable == "Bleed both":
                    im_1 = im_raw[:, :, ch_1].ravel()
                    im_2 = im_raw[:, :, ch_2].ravel()
                    im_1 = im_1[(im_2 == im_2)]
                    im_2 = im_2[(im_2 == im_2)]
                    im_2 = im_2[(im_1 == im_1)]
                    im_1 = im_1[(im_1 == im_1)]
                    if unmix_range < 100:
                        im_2 = im_2[
                            np.argsort(im_1)[
                                -1 * np.int32(len(im_1) * unmix_range / 100) :
                            ]
                        ]
                        im_1 = im_1[
                            np.argsort(im_1)[
                                -1 * np.int32(len(im_1) * unmix_range / 100) :
                            ]
                        ]
                    z = np.polyfit(im_1, im_2, 1)  # subtract 1 from 2
                    p_1 = np.poly1d(z)
                    if unmix_threshold > 0:
                        y_hat = p_1(im_1)
                        y_bar = np.sum(im_2) / len(im_2)
                        ssreg = np.sum((y_hat - y_bar) ** 2)
                        sstot = np.sum((im_2 - y_bar) ** 2)
                        r_square = ssreg / sstot
                        if r_square > unmix_threshold:
                            im_raw_temp[:, :, ch_2] = (
                                im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                            )
                    else:
                        im_raw_temp[:, :, ch_2] = (
                            im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                        )
            else:
                if direction_variable == "Bleed to":
                    for ch_2 in range(len(Channel_pointers)):
                        im_1 = im_raw[:, :, ch_1].ravel()
                        if ch_2 == ch_1:
                            continue
                        im_2 = im_raw[:, :, ch_2].ravel()
                        im_1 = im_1[(im_2 == im_2)]
                        im_2 = im_2[(im_2 == im_2)]
                        im_2 = im_2[(im_1 == im_1)]
                        im_1 = im_1[(im_1 == im_1)]
                        if unmix_range < 100:
                            im_2 = im_2[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                            im_1 = im_1[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                        z = np.polyfit(im_1, im_2, 1)  # subtract 1 from 2
                        p_1 = np.poly1d(z)
                        if unmix_threshold > 0:
                            y_hat = p_1(im_1)
                            y_bar = np.sum(im_2) / len(im_2)
                            ssreg = np.sum((y_hat - y_bar) ** 2)
                            sstot = np.sum((im_2 - y_bar) ** 2)
                            r_square = ssreg / sstot
                            if r_square > unmix_threshold:
                                im_raw_temp[:, :, ch_2] = (
                                    im_raw[:, :, ch_2]
                                    - p_1(im_raw[:, :, ch_1])
                                    + p_1(0)
                                )
                        else:
                            im_raw_temp[:, :, ch_2] = (
                                im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                            )
                else:
                    im_1 = im_raw[:, :, ch_1].ravel()
                    im_2 = np.zeros([len(im_1), len(Channel_pointers) - 1])
                    i = 0
                    for ch_2 in range(len(Channel_pointers)):
                        if ch_2 == ch_1:
                            continue
                        im_2[:, i] = im_raw[:, :, ch_2].ravel()
                        i = i + 1
                    im_2_temp = np.sum(im_2, axis=1)
                    im_1 = im_1[(im_2_temp == im_2_temp)]
                    im_2 = im_2[(im_2_temp == im_2_temp), :]
                    im_2 = im_2[(im_1 == im_1), :]
                    im_1 = im_1[(im_1 == im_1)]
                    # lm = sklearn.linear_model.LinearRegression()
                    # model = lm.fit(im_2, im_1)
                    X = np.c_[im_2, np.ones(im_2.shape[0])]  # add bias term
                    beta_hat = np.linalg.lstsq(X, im_1, rcond=None)[0]

                    if unmix_threshold > 0:
                        # y_hat = model.predict(im_2)
                        # y_bar = np.sum(im_1)/len(im_1)
                        # ssreg = np.sum((y_hat-y_bar)**2)
                        # sstot = np.sum((im_1-y_bar)**2)
                        # r_square = ssreg/sstot
                        y_hat = np.dot(X, beta_hat)
                        y_bar = np.sum(im_1) / len(im_1)
                        ssreg = np.sum((y_hat - y_bar) ** 2)
                        sstot = np.sum((im_1 - y_bar) ** 2)
                        r_square = ssreg / sstot
                        if r_square > unmix_threshold:
                            im_raw_extracted = im_raw[
                                :, :, [i != ch_1 for i in range(n_channels)]
                            ]
                            im_raw_extracted = im_raw_extracted.reshape(
                                (
                                    np.int32(im_raw_extracted.size / (n_channels - 1)),
                                    n_channels - 1,
                                )
                            )
                            X = np.c_[
                                im_raw_extracted, np.ones(im_raw_extracted.shape[0])
                            ]
                            X0 = np.c_[
                                im_raw_extracted * 0, np.ones(im_raw_extracted.shape[0])
                            ]
                            im_raw_temp[:, :, ch_1] = (
                                im_raw[:, :, ch_1]
                                - np.dot(X, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                                + np.dot(X0, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                            )
                            # im_raw_temp[:, :, ch_1] = im_raw[
                            #         :, :, ch_1] - model.predict(
                            #         im_raw_extracted).reshape(im_raw[
                            #             :, :, ch_1].shape) + model.predict(
                            #                 im_raw_extracted*0).reshape(
                            #                     im_raw[:, :, ch_1].shape)
                    else:
                        im_raw_extracted = im_raw[
                            :, :, [i != ch_1 for i in range(n_channels)]
                        ]
                        im_raw_extracted = im_raw_extracted.reshape(
                            (
                                np.int32(im_raw_extracted.size / (n_channels - 1)),
                                n_channels - 1,
                            )
                        )
                        X = np.c_[im_raw_extracted, np.ones(im_raw_extracted.shape[0])]
                        X0 = np.c_[
                            im_raw_extracted * 0, np.ones(im_raw_extracted.shape[0])
                        ]
                        im_raw_temp[:, :, ch_1] = (
                            im_raw[:, :, ch_1]
                            - np.dot(X, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                            + np.dot(X0, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                        )
                        # im_raw_temp[:, :, ch_1] = im_raw[
                        #         :, :, ch_1] - model.predict(
                        #         im_raw_extracted).reshape(im_raw[
                        #                 :, :, ch_1].shape) + model.predict(
                        #                 im_raw_extracted*0).reshape(
                        #                         im_raw[:, :, ch_1].shape)
                if direction_variable == "Bleed both":
                    for ch_2 in range(len(Channel_pointers)):
                        im_1 = im_raw[:, :, ch_1].ravel()
                        if ch_2 == ch_1:
                            continue
                        im_2 = im_raw[:, :, ch_2].ravel()
                        im_1 = im_1[(im_2 == im_2)]
                        im_2 = im_2[(im_2 == im_2)]
                        im_2 = im_2[(im_1 == im_1)]
                        im_1 = im_1[(im_1 == im_1)]
                        if unmix_range < 100:
                            im_2 = im_2[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                            im_1 = im_1[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                        z = np.polyfit(im_1, im_2, 1)  # subtract 1 from 2
                        p_1 = np.poly1d(z)
                        if unmix_threshold > 0:
                            y_hat = p_1(im_1)
                            y_bar = np.sum(im_2) / len(im_2)
                            ssreg = np.sum((y_hat - y_bar) ** 2)
                            sstot = np.sum((im_2 - y_bar) ** 2)
                            r_square = ssreg / sstot
                            if r_square > unmix_threshold:
                                im_raw_temp[:, :, ch_2] = (
                                    im_raw[:, :, ch_2]
                                    - p_1(im_raw[:, :, ch_1])
                                    + p_1(0)
                                )
                        else:
                            im_raw_temp[:, :, ch_2] = (
                                im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                            )
        else:
            if channel_variable_2 != "All":
                ch_1 = Channel_pointers.index(channel_variable_2)
                if direction_variable == "Bleed from":
                    for ch_2 in range(len(Channel_pointers)):
                        im_1 = im_raw[:, :, ch_1].ravel()
                        if ch_2 == ch_1:
                            continue
                        im_2 = im_raw[:, :, ch_2].ravel()
                        im_1 = im_1[(im_2 == im_2)]
                        im_2 = im_2[(im_2 == im_2)]
                        im_2 = im_2[(im_1 == im_1)]
                        im_1 = im_1[(im_1 == im_1)]
                        if unmix_range < 100:
                            im_2 = im_2[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                            im_1 = im_1[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                        z = np.polyfit(im_1, im_2, 1)  # subtract 1 from 2
                        p_1 = np.poly1d(z)
                        if unmix_threshold > 0:
                            y_hat = p_1(im_1)
                            y_bar = np.sum(im_2) / len(im_2)
                            ssreg = np.sum((y_hat - y_bar) ** 2)
                            sstot = np.sum((im_2 - y_bar) ** 2)
                            r_square = ssreg / sstot
                            if r_square > unmix_threshold:
                                im_raw_temp[:, :, ch_2] = (
                                    im_raw[:, :, ch_2]
                                    - p_1(im_raw[:, :, ch_1])
                                    + p_1(0)
                                )
                        else:
                            im_raw_temp[:, :, ch_2] = (
                                im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                            )
                else:
                    im_1 = im_raw[:, :, ch_1].ravel()
                    im_2 = np.zeros([len(im_1), len(Channel_pointers) - 1])
                    i = 0
                    for ch_2 in range(len(Channel_pointers)):
                        if ch_2 == ch_1:
                            continue

                        im_2[:, i] = im_raw[:, :, ch_2].ravel()
                        i = i + 1
                    im_2_temp = np.sum(im_2, axis=1)
                    im_1 = im_1[(im_2_temp == im_2_temp)]
                    im_2 = im_2[(im_2_temp == im_2_temp), :]
                    im_2 = im_2[(im_1 == im_1), :]
                    im_1 = im_1[(im_1 == im_1)]
                    # lm = sklearn.linear_model.LinearRegression()
                    # model = lm.fit(im_2, im_1)
                    X = np.c_[im_2, np.ones(im_2.shape[0])]  # add bias term
                    beta_hat = np.linalg.lstsq(X, im_1, rcond=None)[0]
                    if unmix_threshold > 0:
                        # y_hat = model.predict(im_2)
                        # y_bar = np.sum(im_1)/len(im_1)
                        # ssreg = np.sum((y_hat-y_bar)**2)
                        # sstot = np.sum((im_1-y_bar)**2)
                        # r_square = ssreg/sstot
                        y_hat = np.dot(X, beta_hat)
                        y_bar = np.sum(im_1) / len(im_1)
                        ssreg = np.sum((y_hat - y_bar) ** 2)
                        sstot = np.sum((im_1 - y_bar) ** 2)
                        r_square = ssreg / sstot
                        if r_square > unmix_threshold:
                            im_raw_extracted = im_raw[
                                :, :, [i != ch_1 for i in range(n_channels)]
                            ]
                            im_raw_extracted = im_raw_extracted.reshape(
                                (
                                    np.int32(im_raw_extracted.size / (n_channels - 1)),
                                    n_channels - 1,
                                )
                            )
                            X = np.c_[
                                im_raw_extracted, np.ones(im_raw_extracted.shape[0])
                            ]
                            X0 = np.c_[
                                im_raw_extracted * 0, np.ones(im_raw_extracted.shape[0])
                            ]
                            im_raw_temp[:, :, ch_1] = (
                                im_raw[:, :, ch_1]
                                - np.dot(X, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                                + np.dot(X0, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                            )
                            # im_raw_temp[:, :, ch_1] = im_raw[
                            #         :, :, ch_1] - model.predict(
                            #         im_raw_extracted).reshape(im_raw[
                            #             :, :, ch_1].shape) + model.predict(
                            #     im_raw_extracted*0).reshape(
                            #             im_raw[:, :, ch_1].shape)
                    else:
                        im_raw_extracted = im_raw[
                            :, :, [i != ch_1 for i in range(n_channels)]
                        ]
                        im_raw_extracted = im_raw_extracted.reshape(
                            (
                                np.int32(im_raw_extracted.size / (n_channels - 1)),
                                n_channels - 1,
                            )
                        )
                        X = np.c_[im_raw_extracted, np.ones(im_raw_extracted.shape[0])]
                        X0 = np.c_[
                            im_raw_extracted * 0, np.ones(im_raw_extracted.shape[0])
                        ]
                        im_raw_temp[:, :, ch_1] = (
                            im_raw[:, :, ch_1]
                            - np.dot(X, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                            + np.dot(X0, beta_hat).reshape(im_raw[:, :, ch_1].shape)
                        )
                        # im_raw_temp[:, :, ch_1] = im_raw[
                        #         :, :, ch_1] - model.predict(
                        #         im_raw_extracted).reshape(im_raw[
                        #                 :, :, ch_1].shape) + model.predict(
                        #                 im_raw_extracted*0).reshape(im_raw[
                        #                         :, :, ch_1].shape)
                if direction_variable == "Bleed both":
                    for ch_2 in range(len(Channel_pointers)):
                        im_1 = im_raw[:, :, ch_1].ravel()
                        if ch_2 == ch_1:
                            continue
                        im_2 = im_raw[:, :, ch_2].ravel()
                        im_1 = im_1[(im_2 == im_2)]
                        im_2 = im_2[(im_2 == im_2)]
                        im_2 = im_2[(im_1 == im_1)]
                        im_1 = im_1[(im_1 == im_1)]
                        if unmix_range < 100:
                            im_2 = im_2[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                            im_1 = im_1[
                                np.argsort(im_1)[
                                    -1 * np.int32(len(im_1) * unmix_range / 100) :
                                ]
                            ]
                        z = np.polyfit(im_1, im_2, 1)  # subtract 1 from 2
                        p_1 = np.poly1d(z)
                        if unmix_threshold > 0:
                            y_hat = p_1(im_1)
                            y_bar = np.sum(im_2) / len(im_2)
                            ssreg = np.sum((y_hat - y_bar) ** 2)
                            sstot = np.sum((im_2 - y_bar) ** 2)
                            r_square = ssreg / sstot
                            if r_square > unmix_threshold:
                                im_raw_temp[:, :, ch_2] = (
                                    im_raw[:, :, ch_2]
                                    - p_1(im_raw[:, :, ch_1])
                                    + p_1(0)
                                )
                        else:
                            im_raw_temp[:, :, ch_2] = (
                                im_raw[:, :, ch_2] - p_1(im_raw[:, :, ch_1]) + p_1(0)
                            )
            else:
                popupmsg(
                    "Did not think any sane person "
                    + "would want this...\n"
                    + "If you are reading this message, and "
                    + "really want this implemented\n"
                    + "send an email to Emrah to implement this."
                )
                destroy_popup = False
        if destroy_popup:
            self.im_raw[self.activeImage] = im_raw_temp
            if not popup_control_out:
                DestroyTK(self.popup)

    popup2 = tkinter.Tk()
    self.popup = popup2
    popup2.wm_title("Channel Unmixing")
    Channel_pointers = self.Channel_pointers[self.activeImage].copy()
    Channel_pointers.append("All")
    label = tkinter.Label(popup2, text="Which channels you want to unmix?")
    label.pack(side="top", fill="x", pady=10)
    internal_windows_1 = tkinter.Frame(popup2, width=100, height=20)
    internal_windows_1.pack(side=tkinter.TOP)
    channel_variable_1 = tkinter.StringVar(internal_windows_1)
    channel_variable_1.set(Channel_pointers[0])
    w_1 = tkinter.OptionMenu(internal_windows_1, channel_variable_1, *Channel_pointers)
    w_1.config(width=10)
    w_1.pack(side=tkinter.LEFT)
    direction_options = ["Bleed to", "Bleed from", "Bleed both"]

    internal_windows_2 = tkinter.Frame(popup2, width=100, height=20)
    internal_windows_2.pack(side=tkinter.TOP)
    direction_variable = tkinter.StringVar(internal_windows_2)
    direction_variable.set(direction_options[0])
    w_2 = tkinter.OptionMenu(internal_windows_2, direction_variable, *direction_options)
    w_2.config(width=10)
    w_2.pack(side=tkinter.LEFT)

    internal_windows_3 = tkinter.Frame(popup2, width=100, height=20)
    internal_windows_3.pack(side=tkinter.TOP)
    channel_variable_2 = tkinter.StringVar(internal_windows_3)
    channel_variable_2.set(Channel_pointers[1])
    w_3 = tkinter.OptionMenu(internal_windows_3, channel_variable_2, *Channel_pointers)
    w_3.config(width=10)
    w_3.pack(side=tkinter.LEFT)

    internal_windows_4 = tkinter.Frame(popup2, width=200, height=20)
    internal_windows_4.pack(side=tkinter.TOP)
    label = ttkinter.Label(
        internal_windows_4, text="Cross correlation threshold", anchor="e"
    )
    label.config(width=30)
    label.pack(side=tkinter.LEFT)
    labelButton = tkinter.Entry(internal_windows_4)
    unmix_threshold = labelButton
    labelButton.pack()
    labelButton.insert(0, "0")

    internal_windows_5 = tkinter.Frame(popup2, width=200, height=20)
    internal_windows_5.pack(side=tkinter.TOP)
    label = ttkinter.Label(internal_windows_5, text="Top what % of cells", anchor="e")
    label.config(width=30)
    label.pack(side=tkinter.LEFT)
    labelButton2 = tkinter.Entry(internal_windows_5)
    unmix_range = labelButton2
    labelButton2.pack()
    labelButton2.insert(0, "1")

    internal_windows_9 = tkinter.Frame(popup2, width=100, height=20)
    internal_windows_9.pack(side=tkinter.TOP)

    unmix_button = tkinter.Button(
        master=internal_windows_9, text="Unmix", command=WannaPerform_Unmix
    )
    unmix_button.pack(side=tkinter.TOP)
    internal_windows_10 = tkinter.Frame(popup2, width=100, height=20)
    internal_windows_10.pack(side=tkinter.TOP)

    unmix_all_button = tkinter.Button(
        master=internal_windows_9, text="Unmix all images", command=UnmixForAllImages
    )
    unmix_all_button.pack(side=tkinter.TOP)
    self.unmix_params = [
        channel_variable_1,
        direction_variable,
        channel_variable_2,
        unmix_threshold,
        unmix_range,
    ]


def ThresholdForeground(self):
    FilterImage(self, mode=2)

    def Fore_ch_changed(*a):
        n_channels = self.n_channels_temp
        im_raw = self.im_raw_temp
        Channel_pointers = self.Channel_pointers_temp.copy()
        Color_pointers = self.Color_pointers_temp
        ax2 = self.ax2
        for i in range(n_channels):
            Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
        self.Channel_of_choice = Channel_pointers.index(self.ForeVariable.get())
        to_plot = im_raw[:, :, self.Channel_of_choice].copy()
        if self.adaptive_temp[self.Channel_of_choice] > 0:
            self.adaptive_val.delete(0, tkinter.END)
            self.adaptive_val.insert(
                0, str(int(self.adaptive_temp[self.Channel_of_choice]))
            )
            self.adaptive_var.set(1)
        else:
            self.adaptive_var.set(0)
        if self.adaptive_var.get() > 0:
            filter_size = int(self.adaptive_val.get())
            to_plot = im_raw[:, :, self.Channel_of_choice].copy()
            to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
        ax2.clear()
        if self.adaptive_var.get() > 0:
            ax2.hist(
                to_plot.copy().reshape(-1),
                bins=np.linspace(to_plot.min(), to_plot.max(), 500),
            )
            ax2.autoscale(True)
        else:
            ax2.hist(
                to_plot.copy().reshape(-1),
                bins=np.logspace(np.log10(0.01), np.log10(to_plot.max()), 500),
                log=True,
            )
            ax2.autoscale(True)
            ax2.set_xscale("log")
        garbage = matplotlib.widgets.Cursor(ax2, useblit=True, color="r", horizOn=False)
        span_selector = matplotlib.widgets.SpanSelector(
            ax2, Fore_changed, "horizontal", useblit=True
        )
        span_selector.active = True
        ax2.axis("on")
        self.ax2_canvas.draw()
        garbage = [
            self.foreground_threshold[self.activeImage][0][self.Channel_of_choice],
            self.foreground_threshold[self.activeImage][1][self.Channel_of_choice],
        ]
        garbage = Fore_changed(*garbage)

    def Adaptive_changed(*a):
        ax2 = self.ax2
        n_channels = self.n_channels_temp
        im_raw = self.im_raw_temp
        Channel_pointers = self.Channel_pointers_temp.copy()
        Color_pointers = self.Color_pointers_temp
        for i in range(n_channels):
            Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
        self.Channel_of_choice = Channel_pointers.index(self.ForeVariable.get())
        to_plot = im_raw[:, :, self.Channel_of_choice].copy()
        if self.adaptive_var.get() > 0:
            filter_size = int(self.adaptive_val.get())
            to_plot = im_raw[:, :, self.Channel_of_choice].copy()
            to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
        ax2.clear()
        if self.adaptive_var.get() > 0:
            ax2.hist(
                to_plot.copy().reshape(-1),
                bins=np.linspace(to_plot.min(), to_plot.max(), 500),
            )
            ax2.autoscale(True)
        else:
            ax2.hist(
                to_plot.copy().reshape(-1),
                bins=np.logspace(np.log10(0.01), np.log10(to_plot.max()), 500),
                log=True,
            )
            ax2.autoscale(True)
            ax2.set_xscale("log")
        span_selector = matplotlib.widgets.SpanSelector(
            ax2, Fore_changed, "horizontal", useblit=True
        )
        span_selector.active = True
        ax2.axis("on")
        self.ax2_canvas.draw()

    def Fore_changed(*a):
        ax = self.ax
        im_temp = self.im_2_display
        i = self.Channel_of_choice
        im_raw = np.array(self.im_raw_temp)
        im_temp = np.array(self.im_2_display)
        mask_copy = np.ones((im_raw.shape[0], im_raw.shape[1]), bool)
        to_plot = im_raw[:, :, i].copy()
        if self.adaptive_var.get() > 0:
            filter_size = int(self.adaptive_val.get())
            to_plot = im_raw[:, :, i].copy()
            to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
        foreground_threshold = np.array(self.foreground_threshold[self.activeImage])
        foreground_threshold[0][i] = a[0]
        if a[1] != a[0]:
            if np.max(to_plot) < a[1]:
                foreground_threshold[1][i] = np.inf
            else:
                foreground_threshold[1][i] = a[1]
        mask_copy = (
            np.array(to_plot >= foreground_threshold[0][i])
            & (to_plot <= foreground_threshold[1][i])
            & mask_copy
        )
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
        self.fore_thres_temp = foreground_threshold

    def resetFore(*a):
        def resetForesure(*a):
            n_channels = self.n_channels_temp
            self.adaptive_temp = np.zeros(n_channels)
            self.adap_temp = np.zeros(n_channels)
            self.foreground_threshold[self.activeImage] = [
                np.zeros(n_channels),
                np.full(n_channels, np.inf),
            ]
            self.fore_thres_temp = [np.zeros(n_channels), np.full(n_channels, np.inf)]
            self.activeFore = []
            ax = self.ax
            ax.clear()
            ax.imshow(self.im_2_display, aspect="equal")
            ax.autoscale(False)
            ax.axis("off")
            self.ax_canvas.draw()
            rightWindow = self.fore_rightWindow
            n_channels = self.n_channels_temp
            Channel_pointers = self.Channel_pointers_temp.copy()
            Color_pointers = self.Color_pointers_temp
            for i in range(n_channels):
                Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
            self.foreground_threshold[self.activeImage] = np.array(self.fore_thres_temp)
            for i in range(n_channels):
                internal_windows2 = self.fore_windows[i]
                DestroyTK(internal_windows2)
                internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
                internal_windows2.pack(side=tkinter.TOP)
                label = tkinter.Label(
                    internal_windows2,
                    text=Channel_pointers[i]
                    + "   -   "
                    + str(self.fore_thres_temp[0][i])
                    + " - "
                    + str(self.fore_thres_temp[1][i]),
                )
                label.pack()
                self.fore_windows[i] = internal_windows2
            self.RedoPhenotyping()

        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to reset Foreground")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Go Ahead",
            command=lambda: [DestroyTK(popup2), resetForesure()],
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def addFore(*a):
        rightWindow = self.fore_rightWindow
        n_channels = self.n_channels_temp
        Channel_pointers = self.Channel_pointers_temp.copy()
        Color_pointers = self.Color_pointers_temp
        if self.adaptive_var.get() > 0:
            filter_size = int(self.adaptive_val.get())
        else:
            filter_size = 0
        self.adaptive_temp[self.Channel_of_choice] = filter_size
        for i in range(n_channels):
            Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
        self.foreground_threshold[self.activeImage] = np.array(self.fore_thres_temp)
        for i in range(n_channels):
            internal_windows2 = self.fore_windows[i]
            DestroyTK(internal_windows2)
            internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
            internal_windows2.pack(side=tkinter.TOP)
            label = tkinter.Label(
                internal_windows2,
                text=Channel_pointers[i]
                + "   -   "
                + str(self.fore_thres_temp[0][i])
                + " - "
                + str(self.fore_thres_temp[1][i]),
            )
            label.pack()
            self.fore_windows[i] = internal_windows2

    def rmvFore(*a):
        rightWindow = self.fore_rightWindow
        self.fore_thres_temp = np.array(self.foreground_threshold[self.activeImage])
        self.fore_thres_temp[0][self.Channel_of_choice] = 0
        self.fore_thres_temp[1][self.Channel_of_choice] = np.inf
        self.adaptive_temp[self.Channel_of_choice] = 0
        n_channels = self.n_channels_temp
        Channel_pointers = self.Channel_pointers_temp.copy()
        Color_pointers = self.Color_pointers_temp
        for i in range(n_channels):
            Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
        self.foreground_threshold[self.activeImage] = np.array(self.fore_thres_temp)
        for i in range(n_channels):
            internal_windows2 = self.fore_windows[i]
            DestroyTK(internal_windows2)
            internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
            internal_windows2.pack(side=tkinter.TOP)
            label = tkinter.Label(
                internal_windows2,
                text=Channel_pointers[i]
                + "   -   "
                + str(self.fore_thres_temp[0][i])
                + " - "
                + str(self.fore_thres_temp[1][i]),
            )
            label.pack()
            self.fore_windows[i] = internal_windows2

    def SaveFore(*a):
        n_channels = self.n_channels_temp
        im_raw = self.im_raw_temp
        Color_pointers = self.Color_pointers_temp
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        fore_thres = self.foreground_threshold[self.activeImage]
        analysis_params = self.analysis_params[self.activeImage].copy()
        analysis_params.pop("Foreground")
        analysis_params["Foreground"] = {
            "thres": fore_thres,
            "adaptive_size": self.adaptive_temp,
        }
        self.analysis_params[self.activeImage] = analysis_params.copy()
        for i in range(n_channels):
            to_plot = im_raw[:, :, i].copy()
            if self.adaptive_temp[i] > 0:
                filter_size = self.adaptive_temp[i]
                to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
            if (fore_thres[0][i] != 0) | (fore_thres[1][i] < np.inf):
                im_temp = (im_temp) | (
                    ((to_plot) >= fore_thres[0][i]) & ((to_plot) <= fore_thres[1][i])
                )
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        if im_temp.max() == 1:
            if "Foreground" in analyze_index:
                im_analyzed[analyze_index.index("Foreground")] = im_temp
                self.im_analyzed[self.activeImage] = im_analyzed
            else:
                im_analyzed.append(im_temp)
                analyze_index.append("Foreground")
                self.im_analyzed[self.activeImage] = im_analyzed
                self.analyze_index[self.activeImage] = analyze_index
                self.remake_side_window()
        else:
            if "Foreground" in analyze_index:
                analysis_params = self.analysis_params[self.activeImage].copy()
                analysis_params.pop("Foreground")
                analysis_params["Foreground"] = {}
                self.analysis_params[self.activeImage] = analysis_params.copy()
                im_analyzed.pop(analyze_index.index("Foreground"))
                color_variable = self.color_variable[self.activeImage]
                Color_pointers = self.Color_pointers[self.activeImage]
                color_variable.pop(
                    analyze_index.index("Foreground")
                    + self.n_channels[self.activeImage]
                )
                Color_pointers.pop(
                    analyze_index.index("Foreground")
                    + self.n_channels[self.activeImage]
                )
                analyze_index.pop(analyze_index.index("Foreground"))
                self.im_analyzed[self.activeImage] = im_analyzed
                self.analyze_index[self.activeImage] = analyze_index
                self.color_variable[self.activeImage] = color_variable
                self.Color_pointers[self.activeImage] = Color_pointers
                self.remake_side_window()
        DestroyTK(self.popup)
        self.RedoPhenotyping()

    def ShowFore(*a):
        n_channels = self.n_channels_temp
        im_raw = self.im_raw_temp
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        fore_thres = self.foreground_threshold[self.activeImage]
        for i in range(n_channels):
            to_plot = im_raw[:, :, i].copy()
            if self.adaptive_temp[i] > 0:
                filter_size = self.adaptive_temp[i]
                to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
            if (fore_thres[0][i] != 0) | (fore_thres[1][i] < np.inf):
                im_temp = (im_temp) | (
                    ((to_plot) >= fore_thres[0][i]) & ((to_plot) <= fore_thres[1][i])
                )
        ax = self.ax
        mask_copy = (1 - np.array(im_temp)) / 2
        im_temp = self.im_2_display
        for i in range(3):
            im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
        ax.clear()
        ax.imshow(im_temp, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        for i in range(3):
            im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
        self.ax_canvas.draw()

    im_analyzed = self.im_analyzed[self.activeImage]
    analyze_index = self.analyze_index[self.activeImage]
    foreground_threshold = self.foreground_threshold[self.activeImage]
    n_channels = self.n_channels_temp
    im_raw = self.im_raw_temp
    adaptive_thres = np.zeros(n_channels)
    self.adaptive_temp = adaptive_thres
    analysis_params = self.analysis_params[self.activeImage].copy()
    if len(im_analyzed) == 0:
        self.activeFore = []
        foreground_threshold = [np.zeros(n_channels), np.full(n_channels, np.inf)]
    else:
        if "Foreground" in analyze_index:
            self.activeFore = im_analyzed[analyze_index.index("Foreground")]
            if "adaptive_size" in analysis_params["Foreground"]:
                self.adaptive_temp = analysis_params["Foreground"]["adaptive_size"]
        else:
            foreground_threshold = [np.zeros(n_channels), np.full(n_channels, np.inf)]
            self.activeFore = []
    if len(self.activeFore) == 0:
        foreground_threshold = [np.zeros(n_channels), np.full(n_channels, np.inf)]
    popup = tkinter.Tk()
    while len(foreground_threshold[0]) < n_channels:
        foreground_threshold = [
            np.append(foreground_threshold[0], 0),
            np.append(foreground_threshold[1], np.inf),
        ]
    while len(self.adaptive_temp) < n_channels:
        self.adaptive_temp = np.append(self.adaptive_temp, 0)
    self.foreground_threshold[self.activeImage] = foreground_threshold
    self.fore_thres_temp = np.array(foreground_threshold)
    self.popup = popup
    im_2_display = self.im_2_display
    popup.wm_title("Foreground Selection")
    label = tkinter.Label(
        popup,
        text="Foregorund selection for file :" + self.FileDictionary[self.activeImage],
    )
    toolbar = tkinter.Frame(popup)
    resetButton = tkinter.Button(toolbar, text="Reset Foreground", command=resetFore)
    resetButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    addButton = tkinter.Button(toolbar, text="Add Mask", command=addFore)
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvButton = tkinter.Button(toolbar, text="Remove Mask", command=rmvFore)
    rmvButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    showButton = tkinter.Button(toolbar, text="Show Joint Mask", command=ShowFore)
    showButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    saveButton = tkinter.Button(toolbar, text="Save and Quit", command=SaveFore)
    saveButton.pack(side=tkinter.LEFT, padx=2, pady=2)

    self.adaptive_var = tkinter.IntVar(popup)
    check_adaptive = tkinter.Checkbutton(
        toolbar, text="Adaptive Threshold", variable=self.adaptive_var
    )
    self.adaptive_var.trace_variable("w", Adaptive_changed)
    check_adaptive.pack(side=tkinter.LEFT)

    labelButton = tkinter.Entry(toolbar)
    labelButton.pack(side=tkinter.LEFT)
    labelButton.insert(0, "100")
    self.adaptive_val = labelButton

    toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
    label.pack(side="bottom", fill="x", pady=10)
    t = (
        "Select a channel of choice and add a threshold through\n   "
        + "either selecting a value or a range. Once finished, press Add"
    )
    popup_statusBar = tkinter.Label(
        popup, text=t, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
    )
    popup_statusBar.pack(side=tkinter.TOP, fill=tkinter.X)
    mainWindow = tkinter.Frame(popup, width=700)
    f = plt.Figure(figsize=(10, 7), dpi=100)
    f.patch.set_visible(False)
    f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax = f.gca()
    image_canvas = Tk_Agg.FigureCanvasTkAgg(f, master=mainWindow)
    image_canvas.draw()
    image_canvas.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_toolbar = NT2Tk(image_canvas, mainWindow)
    image_toolbar.update()
    image_canvas._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    ax.clear()
    ax.imshow(im_2_display, aspect="equal")
    ax.autoscale(False)
    ax.axis("off")
    self.ax = ax
    image_canvas.draw()
    self.ax_canvas = image_canvas
    if len(self.activeFore) != 0:
        im_temp = self.im_2_display
        mask_copy = np.float32(self.activeFore)
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

    rightWindow = tkinter.Frame(popup, width=400)
    rightWindow.pack(side=tkinter.RIGHT)
    mainWindow.pack(side=tkinter.RIGHT)
    Channel_pointers = self.Channel_pointers_temp.copy()
    Color_pointers = self.Color_pointers_temp
    for i in range(n_channels):
        Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
    internal_windows1 = tkinter.Frame(rightWindow, width=200, height=20)
    self.ForeVariable = tkinter.StringVar(internal_windows1)
    self.ForeVariable.set(Channel_pointers[0])
    self.ForeVariable.trace("w", Fore_ch_changed)
    w = tkinter.OptionMenu(internal_windows1, self.ForeVariable, *Channel_pointers)
    w.config(width=20)
    w.pack(side=tkinter.LEFT)
    internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
    addButton = tkinter.Button(
        master=internal_windows2, text="Add Mask", command=addFore
    )
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvButton = tkinter.Button(
        master=internal_windows2, text="Remove Mask", command=rmvFore
    )
    rmvButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    internal_windows3 = tkinter.Frame(rightWindow, width=200, height=20)
    registerButton = tkinter.Button(
        master=internal_windows3, text="Save and Quit", command=SaveFore
    )
    registerButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    internal_windows = tkinter.Frame(rightWindow, width=400, height=400)
    internal_windows.pack(side=tkinter.TOP)
    internal_windows1.pack(side=tkinter.TOP)
    internal_windows2.pack(side=tkinter.TOP)
    internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
    showButton = tkinter.Button(
        master=internal_windows2, text="Show Joint Mask", command=ShowFore
    )
    showButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    internal_windows2.pack(side=tkinter.TOP)
    internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
    internal_windows2.pack(side=tkinter.TOP)
    internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
    internal_windows2.pack(side=tkinter.TOP)
    label = tkinter.Label(internal_windows2, text="Current Thresholds")
    label.pack()
    rightWindow2 = tkinter.Frame(rightWindow, width=400, height=400)
    rightWindow2.pack(side=tkinter.TOP)
    self.fore_rightWindow = rightWindow2
    self.fore_windows = []
    for i in range(n_channels):
        internal_windows2 = tkinter.Frame(rightWindow2, width=200, height=20)
        internal_windows2.pack(side=tkinter.TOP)
        label = tkinter.Label(
            internal_windows2,
            text=Channel_pointers[i]
            + "   -   "
            + str(foreground_threshold[0][i])
            + " - "
            + str(foreground_threshold[1][i]),
        )
        label.pack()
        self.fore_windows.append(internal_windows2)
    internal_windows3.pack(side=tkinter.TOP)
    f2 = plt.Figure(figsize=(4, 4), dpi=100)
    f2.patch.set_visible(False)
    f2.subplots_adjust(left=0.1, bottom=0.1, right=1, top=1, wspace=0, hspace=0)
    ax2 = f2.gca()
    image_canvas2 = Tk_Agg.FigureCanvasTkAgg(f2, master=internal_windows)
    image_canvas2.draw()
    image_canvas2.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_canvas2._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    image_toolbar2 = NT2Tk(image_canvas2, internal_windows)
    image_toolbar2.update()
    ax2.clear()
    self.Channel_of_choice = Channel_pointers.index(self.ForeVariable.get())
    ax2.hist(
        im_raw[:, :, self.Channel_of_choice].copy().reshape(-1),
        bins=np.logspace(
            np.log10(0.01), np.log10(im_raw[:, :, self.Channel_of_choice].max()), 500
        ),
        log=True,
    )
    ax2.autoscale(True)
    ax2.set_xscale("log")
    garbage = matplotlib.widgets.Cursor(ax2, useblit=True, color="r", horizOn=False)
    span_selector = matplotlib.widgets.SpanSelector(
        ax2, Fore_changed, "horizontal", useblit=True
    )
    garbage.active = True
    span_selector.active = True
    ax2.axis("on")
    self.ax2 = ax2
    image_canvas2.draw()
    self.ax2_canvas = image_canvas2
    popup.mainloop()


def SegmentDetection(self):
    FilterImage(self, mode=2)
    banned_seg_names = []
    for i in self.Markers:
        if i != "DAPI":
            banned_seg_names.append(i)
        banned_seg_names.append(i + "-Filter")

    def Seg_ch_changed(*a):
        ax2 = self.ax2
        n_channels = self.n_channels_temp
        im_raw = np.array(self.im_raw_temp)
        Channel_pointers = self.Channel_pointers_temp.copy()
        Color_pointers = self.Color_pointers_temp
        for i in range(n_channels):
            Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
        self.Channel_of_choice = Channel_pointers.index(self.ForeVariable.get())
        to_plot = im_raw[:, :, self.Channel_of_choice]
        if self.adaptive_var.get() > 0:
            filter_size = int(self.adaptive_val.get())
            to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
            to_plot[to_plot < 0] = 0
        ax2.clear()
        ax2.hist(
            to_plot.copy().reshape(-1),
            bins=np.logspace(
                np.log10(max(0.01, np.median(to_plot) / 50)),
                np.log10(to_plot.max()),
                500,
            )
            + np.linspace(0, np.mean(to_plot), 500),
        )
        ax2.autoscale(True)
        ax2.set_xlim(xmin=max((0.01, np.median(to_plot) / 50)))
        ax2.set_xscale("log")

        garbage = matplotlib.widgets.Cursor(ax2, useblit=True, color="r", horizOn=False)
        span_selector = matplotlib.widgets.SpanSelector(
            ax2, Seg_changed, "horizontal", useblit=True
        )
        span_selector.active = True
        garbage.active = True
        self.ax2_canvas.draw()
        ax = self.ax
        im_temp = self.im_2_display
        segment_threshold = self.thres_temp
        adaptive_thres = self.adaptive_temp
        im_temp = np.array(self.im_2_display)
        mask_copy = np.ones((im_raw.shape[0], im_raw.shape[1]), bool)
        for i in range(n_channels):
            if adaptive_thres[i] > 0:
                filter_size = int(adaptive_thres[i])
                to_plot = im_raw[:, :, i]
                to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
                to_plot[to_plot < 0] = 0
                im_raw[:, :, i] = to_plot
            mask_copy = (
                np.array(im_raw[:, :, i] >= segment_threshold[0][i])
                & (im_raw[:, :, i] <= segment_threshold[1][i])
                & mask_copy
            )
        mask_copy = (1 - np.float32(mask_copy)) / 2
        for i in range(3):
            im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
        ax.clear()
        ax.imshow(im_temp, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        for i in range(3):
            im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
        self.ax_canvas.draw()

    def Seg_changed(*a):
        ax = self.ax
        im_temp = self.im_2_display
        n_channels = self.n_channels_temp
        im_raw = np.array(self.im_raw_temp)
        segment_threshold = np.array(self.thres_temp.copy())
        adaptive_thres = np.array(self.adaptive_temp.copy())
        if self.adaptive_var.get() > 0:
            adaptive_thres[self.Channel_of_choice] = int(self.adaptive_val.get())
        segment_threshold[0][self.Channel_of_choice] = a[0]
        if a[1] != a[0]:
            segment_threshold[1][self.Channel_of_choice] = a[1]
        im_temp = np.array(self.im_2_display)
        mask_copy = np.ones((im_raw.shape[0], im_raw.shape[1]), bool)
        for i in range(n_channels):
            if adaptive_thres[i] > 0:
                filter_size = int(adaptive_thres[i])
                to_plot = im_raw[:, :, i]
                to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
                to_plot[to_plot < 0] = 0
                im_raw[:, :, i] = to_plot
            if np.max(im_raw[:, :, i]) < segment_threshold[1][i]:
                segment_threshold[1][i] = np.inf
            mask_copy = (
                np.array(im_raw[:, :, i] >= segment_threshold[0][i])
                & (im_raw[:, :, i] <= segment_threshold[1][i])
                & mask_copy
            )
        mask_copy = (1 - np.float32(mask_copy)) / 2
        for i in range(3):
            im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
        ax.clear()
        ax.imshow(im_temp, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        for i in range(3):
            im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
        self.ax_canvas.draw()
        self.ch_temp = segment_threshold
        self.adap_temp = adaptive_thres

    def resetSeg(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(
            popup2, text="You are about to reset current segmentation"
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2, text="Go Ahead", command=lambda: [DestroyTK(popup2), resetSegsure()]
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def resetSegsure(*a):
        n_channels = self.n_channels_temp
        self.thres_temp = [np.zeros(n_channels), np.full(n_channels, np.inf)]
        self.ch_temp = [np.zeros(n_channels), np.full(n_channels, np.inf)]
        self.adaptive_temp = np.zeros(n_channels)
        self.adap_temp = np.zeros(n_channels)
        self.activeSegment = []
        ax = self.ax
        ax.clear()
        ax.imshow(self.im_2_display, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        try:
            self.ax_canvas.draw()
            rightWindow = self.fore_rightWindow
            Channel_pointers = self.Channel_pointers_temp.copy()
            Color_pointers = self.Color_pointers_temp
            for i in range(n_channels):
                Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
            for i in range(n_channels):
                internal_windows2 = self.fore_windows[i]
                DestroyTK(internal_windows2)
                internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
                internal_windows2.pack(side=tkinter.TOP)
                label = tkinter.Label(
                    internal_windows2,
                    text=Channel_pointers[i]
                    + "   -   "
                    + str(self.ch_temp[0][i])
                    + " - "
                    + str(self.ch_temp[1][i]),
                )
                label.pack()
                self.fore_windows[i] = internal_windows2
        except tkinter.TclError:
            pass

    def addSegCh(*a):
        rightWindow = self.fore_rightWindow
        n_channels = self.n_channels_temp
        Channel_pointers = self.Channel_pointers_temp.copy()
        Color_pointers = self.Color_pointers_temp
        for i in range(n_channels):
            Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
        self.thres_temp = np.array(self.ch_temp)
        self.adaptive_temp = np.array(self.adap_temp)
        for i in range(n_channels):
            internal_windows2 = self.fore_windows[i]
            DestroyTK(internal_windows2)
            internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
            internal_windows2.pack(side=tkinter.TOP)
            label = tkinter.Label(
                internal_windows2,
                text=Channel_pointers[i]
                + "   -   "
                + str(self.thres_temp[0][i])
                + " - "
                + str(self.thres_temp[1][i]),
            )
            label.pack()
            self.fore_windows[i] = internal_windows2

    def rmvSegCh(*a):
        ax = self.ax
        im_temp = self.im_2_display
        segment_threshold = self.thres_temp
        adaptive_thres = self.adaptive_temp
        adaptive_thres[self.Channel_of_choice] = 0
        segment_threshold[0][self.Channel_of_choice] = 0
        segment_threshold[1][self.Channel_of_choice] = np.inf
        rightWindow = self.fore_rightWindow
        n_channels = self.n_channels_temp
        Channel_pointers = self.Channel_pointers_temp.copy()
        Color_pointers = self.Color_pointers_temp
        im_raw = np.array(self.im_raw_temp)
        for i in range(n_channels):
            Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
        for i in range(n_channels):
            internal_windows2 = self.fore_windows[i]
            DestroyTK(internal_windows2)
            internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
            internal_windows2.pack(side=tkinter.TOP)
            label = tkinter.Label(
                internal_windows2,
                text=Channel_pointers[i]
                + "   -   "
                + str(self.thres_temp[0][i])
                + " - "
                + str(self.thres_temp[1][i]),
            )
            label.pack()
            self.fore_windows[i] = internal_windows2
        im_temp = np.array(self.im_2_display)
        mask_copy = np.ones((im_raw.shape[0], im_raw.shape[1]), bool)
        for i in range(n_channels):
            if adaptive_thres[i] > 0:
                filter_size = int(adaptive_thres[i])
                to_plot = im_raw[:, :, i]
                to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
                to_plot[to_plot < 0] = 0
                im_raw[:, :, i] = to_plot
            mask_copy = (
                np.array(im_raw[:, :, i] >= segment_threshold[0][i])
                & (im_raw[:, :, i] <= segment_threshold[1][i])
                & mask_copy
            )
        mask_copy = (1 - np.float32(mask_copy)) / 2
        for i in range(3):
            im_temp[:, :, i] = mask_copy + im_temp[:, :, i]
        ax.clear()
        ax.imshow(im_temp, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        for i in range(3):
            im_temp[:, :, i] = im_temp[:, :, i] - mask_copy
        self.ax_canvas.draw()
        self.ch_temp = np.array(segment_threshold)
        self.adap_temp = np.array(adaptive_thres)

    def AddSeg(*a):
        def AddSegSure(popup2, *a):
            def AddSegSureSure(*a):
                segName = self.SegName.get()
                n_channels = self.n_channels_temp
                im_raw = np.array(self.im_raw_temp)
                analyze_index = self.analyze_index[self.activeImage]
                im_analyzed = self.im_analyzed[self.activeImage]
                segment_threshold = np.array(self.thres_temp.copy())
                adaptive_thres = np.array(self.adaptive_temp.copy())
                analysis_params = self.analysis_params[self.activeImage].copy()
                if segName in analysis_params["Segments"]:
                    analysis_params["Segments"].pop(segName)
                analysis_params["Segments"][segName] = {
                    "thres": segment_threshold,
                    "adaptive_size": adaptive_thres,
                }
                self.analysis_params[self.activeImage] = analysis_params.copy()
                mask_copy = np.ones((im_raw.shape[0], im_raw.shape[1]), bool)
                for i in range(n_channels):
                    if adaptive_thres[i] > 0:
                        filter_size = int(adaptive_thres[i])
                        to_plot = im_raw[:, :, i]
                        to_plot = to_plot - ndi.filters.uniform_filter(
                            to_plot, filter_size
                        )
                        to_plot[to_plot < 0] = 0
                        im_raw[:, :, i] = to_plot

                    mask_copy = (
                        np.array(im_raw[:, :, i] >= segment_threshold[0][i])
                        & (im_raw[:, :, i] <= segment_threshold[1][i])
                        & mask_copy
                    )
                # mask_copy = ndi.morphology.binary_opening(mask_copy)
                if "Foreground" in analyze_index:
                    mask_copy = (
                        mask_copy & im_analyzed[analyze_index.index("Foreground")]
                    )
                if mask_copy.max() == 1:
                    if segName in analyze_index:
                        im_analyzed[analyze_index.index(segName)] = mask_copy
                        self.im_analyzed[self.activeImage] = im_analyzed
                    else:
                        im_analyzed.append(mask_copy)
                        analyze_index.append(segName)
                        self.im_analyzed[self.activeImage] = im_analyzed
                        self.analyze_index[self.activeImage] = analyze_index
                        self.remake_side_window()
                else:
                    if segName in analyze_index:
                        im_analyzed.pop(analyze_index.index(segName))
                        color_variable = self.color_variable[self.activeImage]
                        Color_pointers = self.Color_pointers[self.activeImage]
                        color_variable.pop(
                            analyze_index.index(segName)
                            + self.n_channels[self.activeImage]
                        )
                        Color_pointers.pop(
                            analyze_index.index(segName)
                            + self.n_channels[self.activeImage]
                        )
                        analyze_index.pop(analyze_index.index(segName))
                        self.im_analyzed[self.activeImage] = im_analyzed
                        self.analyze_index[self.activeImage] = analyze_index
                        self.color_variable[self.activeImage] = color_variable
                        self.Color_pointers[self.activeImage] = Color_pointers
                        self.remake_side_window()
                resetSegsure()
                self.RedoPhenotyping()

            segName = self.SegName.get()
            analyze_index = self.analyze_index[self.activeImage]
            if segName in banned_seg_names:
                popup3 = tkinter.Tk()
                popup3.wm_title("Banned name")
                label = tkinter.Label(
                    popup3,
                    text=(
                        segName
                        + " is a reserved name and you"
                        + "/ncannot give that name to your segment"
                    ),
                )
                label.pack(side="top", fill="x", pady=10)
                B2 = tkinter.Button(
                    popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
                )
                B2.pack()
                popup3.mainloop()
            elif segName in analyze_index:
                popup3 = tkinter.Tk()
                popup3.wm_title("Tissue Exists")
                label = tkinter.Label(
                    popup3,
                    text="A tissue with the same name exists.\n"
                    + "would you like to overwrite?",
                )
                label.pack(side="top", fill="x", pady=10)
                B1 = tkinter.Button(
                    popup3,
                    text="Okay",
                    command=lambda: [
                        DestroyTK(popup3),
                        AddSegSureSure(),
                        DestroyTK(popup2),
                    ],
                )
                B1.pack()
                B2 = tkinter.Button(
                    popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
                )
                B2.pack()
                popup3.mainloop()
            else:
                AddSegSureSure()
                DestroyTK(popup2)

        def get_tick_values(*args):
            if combine_option.get() == "other":
                self.SegName.delete(0, tkinter.END)
            else:
                self.SegName.delete(0, tkinter.END)
                self.SegName.insert(0, combine_option.get())

        popup2 = tkinter.Tk()
        popup2.wm_title("Add Segment")
        dropdown_options = ["DAPI", "Tumor", "Stroma", "other"]
        label = tkinter.Label(popup2, text="How would you like to name your tissue?")
        label.pack(side="top", fill="x", pady=10)
        combine_option = tkinter.StringVar(popup2)
        combine_option.set(dropdown_options[0])
        c = tkinter.OptionMenu(popup2, combine_option, *dropdown_options)
        c.pack()
        labelButton = tkinter.Entry(popup2)
        labelButton.pack()
        labelButton.insert(0, "DAPI")
        self.SegName = labelButton
        combine_option.trace("w", get_tick_values)
        B1 = tkinter.Button(popup2, text="Okay", command=lambda: [AddSegSure(popup2)])
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def RmvSeg(*a):
        def RmvSegSure(popup2, *a):
            segName = self.SegName.get()
            DestroyTK(popup2)
            analysis_params = self.analysis_params[self.activeImage].copy()
            if segName in analysis_params["Segments"]:
                analysis_params["Segments"].pop(segName)
            elif segName in analysis_params["Phenotypes"]:
                analysis_params["Phenotypes"].pop(segName)
            self.analysis_params[self.activeImage] = analysis_params.copy()
            analyze_index = self.analyze_index[self.activeImage]
            im_analyzed = self.im_analyzed[self.activeImage]
            color_variable = self.color_variable[self.activeImage]
            Color_pointers = self.Color_pointers[self.activeImage]
            if segName in analyze_index:
                im_analyzed.pop(analyze_index.index(segName))
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
            resetSegsure()
            self.RedoPhenotyping()

        analysis_params = self.analysis_params[self.activeImage].copy()
        seg_names = [i for i in analysis_params["Segments"].keys()]
        for i in analysis_params["Phenotypes"].keys():
            seg_names.append(i)
        if len(seg_names) > 0:
            popup2 = tkinter.Tk()
            popup2.wm_title("Remove Segment")
            label = tkinter.Label(popup2, text="Which tissue would you like to remove?")
            label.pack(side="top", fill="x", pady=10)
            internal_windows = tkinter.Frame(popup2, width=200, height=20)
            internal_windows.pack(side=tkinter.TOP)
            self.SegName = tkinter.StringVar(internal_windows)
            self.SegName.set(seg_names[0])
            w = tkinter.OptionMenu(internal_windows, self.SegName, *seg_names)
            w.config(width=20)
            w.pack(side=tkinter.LEFT)
            B1 = tkinter.Button(
                popup2, text="Remove", command=lambda: [RmvSegSure(popup2)]
            )
            B1.pack()
            B2 = tkinter.Button(
                popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
            )
            B2.pack()
            popup2.mainloop()

    def QuitSeg(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to quit tissue segmentation")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Okay",
            command=lambda: [
                resetSegsure(popup2),
                DestroyTK(self.popup),
                DestroyTK(popup2),
            ],
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()
        self.remake_side_window()

    n_channels = self.n_channels_temp
    Channel_pointers = self.Channel_pointers_temp.copy()
    Color_pointers = self.Color_pointers_temp
    im_raw = np.array(self.im_raw_temp)
    self.activeSegment = []
    segment_threshold = [np.zeros(n_channels), np.full(n_channels, np.inf)]
    adaptive_thres = np.zeros(n_channels)
    self.adaptive_temp = adaptive_thres
    self.thres_temp = segment_threshold
    popup = tkinter.Tk()
    self.popup = popup
    im_2_display = self.im_2_display
    popup.wm_title("Tissue Segmentation")
    label = tkinter.Label(
        popup,
        text="Tissue Segmentation for file :" + self.FileDictionary[self.activeImage],
    )
    toolbar = tkinter.Frame(popup)
    addButton = tkinter.Button(toolbar, text="Add Channel", command=addSegCh)
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvButton = tkinter.Button(toolbar, text="Remove Channel", command=rmvSegCh)
    rmvButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    resetButton = tkinter.Button(toolbar, text="Reset Segmentation", command=resetSeg)
    resetButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    addButton = tkinter.Button(toolbar, text="Add Segment", command=AddSeg)
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvButton = tkinter.Button(toolbar, text="Remove Segment", command=RmvSeg)
    rmvButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    cancelButton = tkinter.Button(toolbar, text="Quit", command=QuitSeg)
    cancelButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    self.adaptive_var = tkinter.IntVar(popup)
    check_adaptive = tkinter.Checkbutton(
        toolbar, text="Adaptive Threshold", variable=self.adaptive_var
    )
    self.adaptive_var.trace_variable("w", Seg_ch_changed)
    check_adaptive.pack(side=tkinter.LEFT)

    labelButton = tkinter.Entry(toolbar)
    labelButton.pack(side=tkinter.LEFT)
    labelButton.insert(0, "100")
    self.adaptive_val = labelButton

    toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
    label.pack(side="bottom", fill="x", pady=10)
    t = (
        "Select a channel of choice and add a threshold through "
        + "either selecting a value or a range. Once finished, press Add."
        + "\n   To save your work with a segment name press add segment"
        + ", press remove segment to remove a segmentation data"
    )
    popup_statusBar = tkinter.Label(
        popup, text=t, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
    )
    popup_statusBar.pack(side=tkinter.TOP, fill=tkinter.X)
    mainWindow = tkinter.Frame(popup, width=700)
    f = plt.Figure(figsize=(10, 7), dpi=100)
    f.patch.set_visible(False)
    f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax = f.gca()
    image_canvas = Tk_Agg.FigureCanvasTkAgg(f, master=mainWindow)
    image_canvas.draw()
    image_canvas.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_toolbar = NT2Tk(image_canvas, mainWindow)
    image_toolbar.update()
    image_canvas._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    ax.clear()
    ax.imshow(im_2_display, aspect="equal")
    ax.autoscale(False)
    ax.axis("off")
    self.ax = ax
    image_canvas.draw()
    self.ax_canvas = image_canvas
    rightWindow = tkinter.Frame(popup, width=400)
    rightWindow.pack(side=tkinter.RIGHT)
    mainWindow.pack(side=tkinter.RIGHT)
    if "DAPI" in Channel_pointers:
        def_ch_point = Channel_pointers.index("DAPI")
    else:
        def_ch_point = 0
    for i in range(n_channels):
        Channel_pointers[i] = Channel_pointers[i] + " - " + Color_pointers[i]
    internal_windows1 = tkinter.Frame(rightWindow, width=200, height=20)
    self.ForeVariable = tkinter.StringVar(internal_windows1)
    self.ForeVariable.set(Channel_pointers[def_ch_point])
    self.ForeVariable.trace("w", Seg_ch_changed)
    w = tkinter.OptionMenu(internal_windows1, self.ForeVariable, *Channel_pointers)
    w.config(width=20)
    w.pack(side=tkinter.LEFT)
    internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
    addButton = tkinter.Button(
        master=internal_windows2, text="Add Channel", command=addSegCh
    )
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvButton = tkinter.Button(
        master=internal_windows2, text="Remove Channel", command=rmvSegCh
    )
    rmvButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    internal_windows3 = tkinter.Frame(rightWindow, width=200, height=20)
    registerButton = tkinter.Button(
        master=internal_windows3, text="Add Segment", command=AddSeg
    )
    registerButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    internal_windows = tkinter.Frame(rightWindow, width=400, height=400)
    internal_windows.pack(side=tkinter.TOP)
    internal_windows1.pack(side=tkinter.TOP)
    internal_windows2.pack(side=tkinter.TOP)
    internal_windows2 = tkinter.Frame(rightWindow, width=200, height=20)
    internal_windows2.pack(side=tkinter.TOP)
    label = tkinter.Label(internal_windows2, text="Current Channels")
    label.pack()
    rightWindow2 = tkinter.Frame(rightWindow, width=400, height=400)
    rightWindow2.pack(side=tkinter.TOP)
    self.fore_rightWindow = rightWindow2
    self.fore_windows = []
    for i in range(n_channels):
        internal_windows2 = tkinter.Frame(rightWindow2, width=200, height=20)
        internal_windows2.pack(side=tkinter.TOP)
        label = tkinter.Label(
            internal_windows2,
            text=Channel_pointers[i]
            + "   -   "
            + str(segment_threshold[0][i])
            + " - "
            + str(segment_threshold[1][i]),
        )
        label.pack()
        self.fore_windows.append(internal_windows2)
    internal_windows3.pack(side=tkinter.TOP)
    f2 = plt.Figure(figsize=(4, 4), dpi=100)
    f2.patch.set_visible(False)
    f2.subplots_adjust(left=0.1, bottom=0.1, right=1, top=1, wspace=0, hspace=0)
    ax2 = f2.gca()
    image_canvas2 = Tk_Agg.FigureCanvasTkAgg(f2, master=internal_windows)
    image_canvas2.draw()
    image_canvas2.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_canvas2._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    image_toolbar2 = NT2Tk(image_canvas2, internal_windows)
    image_toolbar2.update()
    self.Channel_of_choice = Channel_pointers.index(self.ForeVariable.get())
    ax2.clear()
    ax2.hist(
        im_raw[:, :, self.Channel_of_choice].copy().reshape(-1),
        bins=np.logspace(
            np.log10(max(0.01, np.median(im_raw[:, :, self.Channel_of_choice]) / 50)),
            np.log10(im_raw[:, :, self.Channel_of_choice].max()),
            500,
        )
        + np.linspace(0, np.mean(im_raw[:, :, self.Channel_of_choice]), 500),
    )
    ax2.autoscale(True)
    ax2.set_xlim(xmin=max((0.01, np.median(im_raw[:, :, self.Channel_of_choice]) / 50)))
    ax2.set_xscale("log")
    garbage = matplotlib.widgets.Cursor(ax2, useblit=True, color="r", horizOn=False)
    span_selector = matplotlib.widgets.SpanSelector(
        ax2, Seg_changed, "horizontal", useblit=True
    )
    garbage.active = True
    span_selector.active = True
    ax2.axis("on")
    self.ax2 = ax2
    image_canvas2.draw()
    self.ax2_canvas = image_canvas2
    popup.mainloop()


def FillHoles(self):
    FilterImage(self, mode=2)

    def Fill_ch_changed(*arg, **kwag):
        analyze_index = self.analyze_index[self.activeImage]
        im_analyzed = self.im_analyzed[self.activeImage]
        if self.fill_ch != analyze_index.index(self.ForeVariable.get()):
            self.fill_ch = analyze_index.index(self.ForeVariable.get())
            self.ForeLimits = [0, np.inf]
            self.HoleLimits = [0, np.inf]
            segName = analyze_index[self.fill_ch]
            n_channels = self.n_channels_temp
            im_raw = self.im_raw_temp
            analysis_params = self.analysis_params[self.activeImage].copy()
            exclude_edges = False
            if segName == "Foreground":
                fore_thres = analysis_params["Foreground"]["thres"]
                if "adaptive_size" in analysis_params["Foreground"]:
                    adaptive_temp = analysis_params["Foreground"]["adaptive_size"]
                else:
                    adaptive_temp = np.zeros(n_channels)
                self.foreground_threshold[self.activeImage] = fore_thres
                im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
                for i in range(n_channels):
                    to_plot = im_raw[:, :, i].copy()
                    if adaptive_temp[i] > 0:
                        filter_size = adaptive_temp[i]
                        to_plot = to_plot - ndi.filters.uniform_filter(
                            to_plot, filter_size
                        )
                        # to_plot[to_plot < 0] = 0
                    if (fore_thres[0][i] != 0) | (fore_thres[1][i] < np.inf):
                        im_temp = (im_temp) | (
                            ((to_plot) >= fore_thres[0][i])
                            & ((to_plot) <= fore_thres[1][i])
                        )
                # im_temp = ndi.morphology.binary_opening(im_temp)
                Fore_mask = im_temp > 0
                self.fill_im = Fore_mask > 0
                if "ForeLimits" in analysis_params["Foreground"].keys():
                    Fore_labels = skimage.measure.label(Fore_mask)
                    Fore_objects = ndi.find_objects(Fore_labels)
                    self.HoleLimits = analysis_params["Foreground"]["HoleLimits"].copy()
                    self.ForeLimits = analysis_params["Foreground"]["ForeLimits"].copy()
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
                    if "ExcludeEdges" in analysis_params["Foreground"]:
                        exclude_edges = analysis_params["Foreground"]["ExcludeEdges"]
                        if exclude_edges:
                            Fore_mask = skimage.segmentation.clear_border(Fore_mask)
            elif isinstance(analysis_params["Segments"][segName]["thres"], str):
                if analysis_params["Segments"][segName]["class"] == "Nuc":
                    self.fill_im = im_analyzed[analyze_index.index("Nuclei")].copy()
                else:
                    self.fill_im = im_analyzed[analyze_index.index("segName")].copy()
                Fore_mask = self.fill_im.copy()
                if "Foreground" in analyze_index:
                    Fore_mask[
                        np.logical_not(im_analyzed[analyze_index.index("Foreground")])
                    ] = 0
                if "ForeLimits" in analysis_params["Segments"][segName].keys():
                    Fore_labels = skimage.measure.label(Fore_mask)
                    Fore_objects = ndi.find_objects(Fore_labels)
                    self.HoleLimits = analysis_params["Segments"][segName][
                        "HoleLimits"
                    ].copy()
                    self.ForeLimits = analysis_params["Segments"][segName][
                        "ForeLimits"
                    ].copy()
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
                        Fore_mask[s1] = most_frequent

                    if "Foreground" in analyze_index:
                        Fore_mask[
                            np.logical_not(
                                im_analyzed[analyze_index.index("Foreground")]
                            )
                        ] = 0
                    del Fore_labels
                    del Fore_objects
                    del Back_mask
                    del Back_labels
                    del Back_objects
                    if "ExcludeEdges" in analysis_params["Segments"][segName]:
                        exclude_edges = analysis_params["Segments"][segName][
                            "ExcludeEdges"
                        ]
                        if exclude_edges:
                            Fore_mask = skimage.segmentation.clear_border(Fore_mask)
            else:
                im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
                seg_thres = analysis_params["Segments"][segName]["thres"]
                if "adaptive_size" in analysis_params["Segments"][segName].keys():
                    adaptive_thres = analysis_params["Segments"][segName][
                        "adaptive_size"
                    ]
                else:
                    adaptive_thres = np.zeros(n_channels)
                for i in range(n_channels):
                    to_plot = im_raw[:, :, i]
                    if adaptive_thres[i] > 0:
                        filter_size = int(adaptive_thres[i])
                        to_plot = to_plot - ndi.filters.uniform_filter(
                            to_plot, filter_size
                        )
                        to_plot[to_plot < 0] = 0
                    if (seg_thres[0][i] != 0) | (seg_thres[1][i] < np.inf):
                        im_temp = (im_temp) | (
                            ((to_plot) >= seg_thres[0][i])
                            & ((to_plot) <= seg_thres[1][i])
                        )
                del to_plot
                # im_temp = ndi.morphology.binary_opening(im_temp)
                Fore_mask = im_temp > 0
                if "Foreground" in analyze_index:
                    Fore_mask = (
                        Fore_mask & im_analyzed[analyze_index.index("Foreground")]
                    )
                self.fill_im = Fore_mask > 0
                if "ForeLimits" in analysis_params["Segments"][segName].keys():
                    Fore_labels = skimage.measure.label(Fore_mask)
                    Fore_objects = ndi.find_objects(Fore_labels)
                    self.HoleLimits = analysis_params["Segments"][segName][
                        "HoleLimits"
                    ].copy()
                    self.ForeLimits = analysis_params["Segments"][segName][
                        "ForeLimits"
                    ].copy()
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
                    del Fore_labels
                    del Fore_objects
                    del Back_mask
                    del Back_labels
                    del Back_objects
                    if "ExcludeEdges" in analysis_params["Segments"][segName]:
                        exclude_edges = analysis_params["Segments"][segName][
                            "ExcludeEdges"
                        ]
                        if exclude_edges:
                            Fore_mask = skimage.segmentation.clear_border(Fore_mask)
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
                Back_area.append(np.sum(Back_labels[s1] == label))
            Back_area = np.array(Back_area)
            ax = self.ax
            ax.clear()
            ax.imshow(Fore_mask, aspect="equal")
            ax.autoscale(False)
            ax.axis("off")
            self.ax_canvas.draw()
            self.fore_lim_label.config(
                text="Foreground Area Limits"
                + "   -   "
                + str(self.ForeLimits[0])
                + " - "
                + str(self.ForeLimits[1])
            )
            self.fore_lim_label.update()
            ax2 = self.ax2
            ax2.clear()
            ax2.hist(
                Fore_area,
                bins=np.logspace(np.log10(10), np.log10(max_fore_back_area), 50),
                log=True,
            )
            ax2.autoscale(True)
            ax2.set_xscale("log")
            garbage = matplotlib.widgets.Cursor(
                ax2, useblit=True, color="r", horizOn=False
            )
            span_selector = matplotlib.widgets.SpanSelector(
                ax2, Fore_fill_changed, "horizontal", useblit=True
            )
            garbage.active = True
            span_selector.active = True
            ax2.axis("on")
            self.ax2_canvas.draw()
            self.back_lim_label.config(
                text="Background Area Limits"
                + "   -   "
                + str(self.HoleLimits[0])
                + " - "
                + str(self.HoleLimits[1])
            )
            self.back_lim_label.update()
            ax3 = self.ax3
            ax3.clear()
            ax3.hist(
                Back_area,
                bins=np.logspace(np.log10(10), np.log10(max_fore_back_area), 50),
                log=True,
            )
            ax3.autoscale(True)
            ax3.set_xscale("log")
            garbage2 = matplotlib.widgets.Cursor(
                ax3, useblit=True, color="r", horizOn=False
            )
            span_selector2 = matplotlib.widgets.SpanSelector(
                ax3, Back_fill_changed, "horizontal", useblit=True
            )
            garbage2.active = True
            span_selector2.active = True
            ax3.axis("on")
            self.adaptive_var.set(exclude_edges)
            self.ax3_canvas.draw()

    def ResetFill(*a):
        def ResetFillSure(*a):
            analysis_params = self.analysis_params[self.activeImage].copy()
            analyze_index = self.analyze_index[self.activeImage]
            im_analyzed = self.im_analyzed[self.activeImage]
            segName = analyze_index[self.fill_ch]
            self.HoleLimits = [0, np.inf]
            self.ForeLimits = [0, np.inf]
            n_channels = self.n_channels_temp
            im_raw = self.im_raw_temp
            if segName == "Foreground":
                fore_thres = analysis_params["Foreground"]["thres"]
                self.foreground_threshold[self.activeImage] = fore_thres
                if "adaptive_size" in analysis_params["Foreground"]:
                    adaptive_temp = analysis_params["Foreground"]["adaptive_size"]
                else:
                    adaptive_temp = np.zeros(n_channels)
                im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
                for i in range(n_channels):
                    to_plot = im_raw[:, :, i].copy()
                    if adaptive_temp[i] > 0:
                        filter_size = adaptive_temp[i]
                        to_plot = to_plot - ndi.filters.uniform_filter(
                            to_plot, filter_size
                        )
                        # to_plot[to_plot < 0] = 0
                    if (fore_thres[0][i] != 0) | (fore_thres[1][i] < np.inf):
                        im_temp = (im_temp) | (
                            ((to_plot) >= fore_thres[0][i])
                            & ((to_plot) <= fore_thres[1][i])
                        )
                # im_temp = ndi.morphology.binary_opening(im_temp)
                Fore_mask = im_temp > 0
                self.fill_im = Fore_mask > 0
            elif isinstance(analysis_params["Segments"][segName]["thres"], str):
                if ("ForeLimits" in analysis_params["Segments"][segName].keys()) | (
                    "ExcludeEdges" in analysis_params["Segments"][segName]
                ):
                    seg_thres = analysis_params["Segments"][segName]["thres"]
                    im_raw = self.im_raw_temp
                    if seg_thres == "Stardist_2D_versatile_fluo":
                        model_versatile = stardist.models.StarDist2D.from_pretrained(
                            "2D_versatile_fluo"
                        )
                        ch_used = analysis_params["Segments"][segName]["ch_used"]
                        n_ch_used = analysis_params["Segments"][segName]["n_ch_used"]
                        anal_class = analysis_params["Segments"][segName]["class"]
                        probability_threshold = model_versatile.thresholds[0]
                        nonmaximum_suppression = model_versatile.thresholds[1]
                        if "d_prob_thres" in analysis_params["Segments"][segName]:
                            probability_threshold += analysis_params["Segments"][
                                segName
                            ]["d_prob_thres"]
                        if "d_nms_thres" in analysis_params["Segments"][segName]:
                            nonmaximum_suppression += analysis_params["Segments"][
                                segName
                            ]["d_nms_thres"]
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
                        im_temp = np.float32(im_temp)
                        Fore_mask = np.ones_like(im_temp == 0)
                        if "ROI" in analyze_index:
                            Fore_mask = (
                                Fore_mask & im_analyzed[analyze_index.index("ROI")]
                            )
                        if "Foreground" in analyze_index:
                            Fore_mask = (
                                Fore_mask
                                & im_analyzed[analyze_index.index("Foreground")]
                            )
                        img = StarDist2D_normalize(im_temp, 1, 99.8, axis=(0, 1))
                        single_cells = model_versatile.predict_instances(
                            img,
                            prob_thresh=probability_threshold,
                            nms_thresh=nonmaximum_suppression,
                        )[0]
                        single_cells = np.uint32(single_cells * np.float32(Fore_mask))
                        mask = single_cells > 0
                        if anal_class == "Seg":
                            im_temp = mask
                        else:
                            im_temp = single_cells
                    self.fill_im = im_temp
                else:
                    if analysis_params["Segments"][segName]["class"] == "Nuc":
                        self.fill_im = im_analyzed[analyze_index.index("Nuclei")].copy()
                    else:
                        self.fill_im = im_analyzed[
                            analyze_index.index("segName")
                        ].copy()
            else:
                im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
                seg_thres = analysis_params["Segments"][segName]["thres"]
                if "adaptive_size" in analysis_params["Segments"][segName].keys():
                    adaptive_thres = analysis_params["Segments"][segName][
                        "adaptive_size"
                    ]
                else:
                    adaptive_thres = np.zeros(n_channels)
                for i in range(n_channels):
                    to_plot = im_raw[:, :, i]
                    if adaptive_thres[i] > 0:
                        filter_size = int(adaptive_thres[i])
                        to_plot = to_plot - ndi.filters.uniform_filter(
                            to_plot, filter_size
                        )
                        to_plot[to_plot < 0] = 0

                    if (seg_thres[0][i] != 0) | (seg_thres[1][i] < np.inf):
                        im_temp = (im_temp) | (
                            ((to_plot) >= seg_thres[0][i])
                            & ((to_plot) <= seg_thres[1][i])
                        )
                del to_plot
                # im_temp = ndi.morphology.binary_opening(im_temp)
                Fore_mask = im_temp > 0
                if "Foreground" in analyze_index:
                    Fore_mask = (
                        Fore_mask & im_analyzed[analyze_index.index("Foreground")]
                    )
                self.fill_im = Fore_mask > 0
            self.im_analyzed[self.activeImage] = im_analyzed
            self.adaptive_var.set(False)
            remake_fill_after_change()

        analyze_index = self.analyze_index[self.activeImage]
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(
            popup2,
            text="You are about to reset your current "
            + analyze_index[self.fill_ch]
            + " mask",
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2, text="Okay", command=lambda: [DestroyTK(popup2), ResetFillSure()]
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def Back_fill_changed(*a):
        self.HoleLimits[0] = a[0]
        if a[1] != a[0]:
            self.HoleLimits[1] = a[1]
        if a[1] > max_fore_back_area:
            self.HoleLimits[1] = np.inf
        remake_fill_after_change()

    def Fore_fill_changed(*a):
        self.ForeLimits[0] = a[0]
        if a[1] != a[0]:
            self.ForeLimits[1] = a[1]
        if a[1] > max_fore_back_area:
            self.ForeLimits[1] = np.inf
        remake_fill_after_change()

    def remake_fill_after_change(*a):
        analyze_index = self.analyze_index[self.activeImage]
        analysis_params = self.analysis_params[self.activeImage].copy()
        im_analyzed = self.im_analyzed[self.activeImage]
        segName = analyze_index[self.fill_ch]
        NN_image = False
        if segName != "Foreground":
            if isinstance(analysis_params["Segments"][segName]["thres"], str):
                NN_image = True
            if "Foreground" in analyze_index:
                self.fill_im[
                    np.logical_not(im_analyzed[analyze_index.index("Foreground")])
                ] = 0
        if NN_image:
            Fore_mask = self.fill_im.copy()
        else:
            Fore_mask = self.fill_im > 0
        if self.adaptive_var.get() > 0:
            Fore_mask = skimage.segmentation.clear_border(Fore_mask)
        Fore_labels = skimage.measure.label(Fore_mask)
        Fore_objects = ndi.find_objects(Fore_labels)
        Fore_area = []
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
        Back_area = []
        if NN_image:
            mask_temp = Back_mask == -1
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
                Fore_mask[s1] = most_frequent
        else:
            for i, s1 in enumerate(Back_objects):
                if s1 is None:
                    continue
                label = i + 1
                region_area = np.sum(Back_labels[s1] == label)
                if region_area < self.HoleLimits[0]:
                    Fore_mask[s1][Back_labels[s1] == label] = 1
                elif region_area > self.HoleLimits[1]:
                    Fore_mask[s1][Back_labels[s1] == label] = 1
        ax = self.ax
        ax.clear()
        ax.imshow(Fore_mask, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        self.ax_canvas.draw()
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
            Back_area.append(np.sum(Back_labels[s1] == label))
        Back_area = np.array(Back_area)
        ax2 = self.ax2
        ax2.clear()
        ax2.hist(
            Fore_area,
            bins=np.logspace(np.log10(10), np.log10(max_fore_back_area), 50),
            log=True,
        )
        ax2.autoscale(True)
        ax2.set_xscale("log")
        garbage = matplotlib.widgets.Cursor(ax2, useblit=True, color="r", horizOn=False)
        span_selector = matplotlib.widgets.SpanSelector(
            ax2, Fore_fill_changed, "horizontal", useblit=True
        )
        garbage.active = True
        span_selector.active = True
        ax2.axis("on")
        self.ax2_canvas.draw()
        ax3 = self.ax3
        ax3.clear()
        ax3.hist(
            Back_area,
            bins=np.logspace(np.log10(10), np.log10(max_fore_back_area), 50),
            log=True,
        )
        ax3.autoscale(True)
        ax3.set_xscale("log")
        garbage2 = matplotlib.widgets.Cursor(
            ax3, useblit=True, color="r", horizOn=False
        )
        span_selector2 = matplotlib.widgets.SpanSelector(
            ax3, Back_fill_changed, "horizontal", useblit=True
        )
        garbage2.active = True
        span_selector2.active = True
        ax3.axis("on")
        self.ax3_canvas.draw()
        self.fore_lim_label.config(
            text="Foreground Area Limits"
            + "   -   "
            + str(self.ForeLimits[0])
            + " - "
            + str(self.ForeLimits[1])
        )
        self.fore_lim_label.update()
        self.back_lim_label.config(
            text="Background Area Limits"
            + "   -   "
            + str(self.HoleLimits[0])
            + " - "
            + str(self.HoleLimits[1])
        )
        self.back_lim_label.update()

    def SaveFill(*a):
        def SaveFillSure(*a):
            analyze_index = self.analyze_index[self.activeImage]
            analysis_params = self.analysis_params[self.activeImage].copy()
            segName = analyze_index[self.fill_ch]
            im_analyzed = self.im_analyzed[self.activeImage]
            NN_image = False
            if segName != "Foreground":
                if isinstance(analysis_params["Segments"][segName]["thres"], str):
                    NN_image = True
                if "Foreground" in analyze_index:
                    self.fill_im[
                        np.logical_not(im_analyzed[analyze_index.index("Foreground")])
                    ] = 0
            if NN_image:
                Fore_mask = self.fill_im.copy()
            else:
                Fore_mask = self.fill_im > 0
            if self.adaptive_var.get() > 0:
                Fore_mask = skimage.segmentation.clear_border(Fore_mask)
            Fore_labels = skimage.measure.label(Fore_mask)
            Fore_objects = ndi.find_objects(Fore_labels)
            segName = analyze_index[self.fill_ch]
            if segName == "Foreground":
                if "ForeLimits" in analysis_params[segName]:
                    analysis_params[segName].pop("ForeLimits")
                if "HoleLimits" in analysis_params[segName]:
                    analysis_params[segName].pop("HoleLimits")
                analysis_params[segName]["ForeLimits"] = self.ForeLimits.copy()
                analysis_params[segName]["HoleLimits"] = self.HoleLimits.copy()
                analysis_params[segName]["ExcludeEdges"] = self.adaptive_var.get() > 0
            else:
                if "ForeLimits" in analysis_params["Segments"][segName].keys():
                    analysis_params["Segments"][segName].pop("ForeLimits")
                if "HoleLimits" in analysis_params["Segments"][segName].keys():
                    analysis_params["Segments"][segName].pop("HoleLimits")
                analysis_params["Segments"][segName][
                    "ForeLimits"
                ] = self.ForeLimits.copy()
                analysis_params["Segments"][segName][
                    "HoleLimits"
                ] = self.HoleLimits.copy()
                analysis_params["Segments"][segName]["ExcludeEdges"] = (
                    self.adaptive_var.get() > 0
                )
            self.analysis_params[self.activeImage] = analysis_params.copy()
            for i, s1 in enumerate(Fore_objects):
                if s1 is None:
                    continue
                label = i + 1
                region_area = np.sum(Fore_labels[s1] == label)
                if region_area < self.ForeLimits[0]:
                    Fore_mask[s1][Fore_labels[s1] == label] = 0
                elif region_area > self.ForeLimits[1]:
                    Fore_mask[s1][Fore_labels[s1] == label] = 0
            Fore_mask = Fore_mask > 0
            Back_mask = Fore_mask == 0
            # if segName != "Foreground":
            #     if "Foreground" in analyze_index:
            #         Back_mask[im_analyzed[analyze_index.index("Foreground")] == False] = 0
            Back_labels = skimage.measure.label(Back_mask)
            Back_objects = ndi.find_objects(Back_labels)
            if NN_image:
                mask_temp = Back_mask == -1
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
                    Fore_mask[s1] = most_frequent
            else:
                for i, s1 in enumerate(Back_objects):
                    if s1 is None:
                        continue
                    label = i + 1
                    region_area = np.sum(Back_labels[s1] == label)
                    if region_area < self.HoleLimits[0]:
                        Fore_mask[s1][Back_labels[s1] == label] = 1
                    elif region_area > self.HoleLimits[1]:
                        Fore_mask[s1][Back_labels[s1] == label] = 1
            if segName != "Foreground":
                if "Foreground" in analyze_index:
                    Fore_mask[
                        np.logical_not(im_analyzed[analyze_index.index("Foreground")])
                    ] = 0
            im_analyzed[self.fill_ch] = Fore_mask
            self.im_analyzed[self.activeImage] = im_analyzed
            self.RedoPhenotyping()

        analyze_index = self.analyze_index[self.activeImage]
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(
            popup2,
            text="You are about to overwrite your current "
            + analyze_index[self.fill_ch]
            + " mask",
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2, text="Okay", command=lambda: [DestroyTK(popup2), SaveFillSure()]
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def QuitFill(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to quit hole filling")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Okay",
            command=lambda: [DestroyTK(self.popup), DestroyTK(popup2)],
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    popup = tkinter.Tk()
    self.popup = popup
    if len(self.ForeLimits) < 2:
        self.ForeLimits = [0, np.inf]
    if len(self.HoleLimits) < 2:
        self.HoleLimits = [0, np.inf]
    analyze_index = self.analyze_index[self.activeImage].copy()
    index_options = self.analyze_index[self.activeImage].copy()
    for i in analyze_index[::-1]:
        if i != "Foreground":
            if i not in [
                j for j in self.analysis_params[self.activeImage]["Segments"].keys()
            ]:
                index_options.pop(index_options.index(i))
    analysis_params = self.analysis_params[self.activeImage].copy()
    if "Foreground" in analyze_index:
        self.fill_ch = analyze_index.index("Foreground")
    else:
        self.fill_ch = 0
        while "filter_1" in analysis_params["Segments"][analyze_index[self.fill_ch]]:
            self.fill_ch += 1
    exclude_edges = False
    segName = analyze_index[self.fill_ch]
    n_channels = self.n_channels_temp
    im_raw = self.im_raw_temp
    max_fore_back_area = im_raw.shape[0] * im_raw.shape[1]
    if segName == "Foreground":
        fore_thres = analysis_params["Foreground"]["thres"]
        if "adaptive_size" in analysis_params["Foreground"]:
            adaptive_temp = analysis_params["Foreground"]["adaptive_size"]
        else:
            adaptive_temp = np.zeros(n_channels)
        while len(fore_thres[0]) < n_channels:
            fore_thres = [np.append(fore_thres[0], 0), np.append(fore_thres[1], np.inf)]
        while len(adaptive_temp) < n_channels:
            adaptive_temp = np.append(adaptive_temp, 0)
        self.foreground_threshold[self.activeImage] = fore_thres
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        for i in range(n_channels):
            to_plot = im_raw[:, :, i].copy()
            if adaptive_temp[i] > 0:
                filter_size = adaptive_temp[i]
                to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
                # to_plot[to_plot < 0] = 0
            if (fore_thres[0][i] != 0) | (fore_thres[1][i] < np.inf):
                im_temp = (im_temp) | (
                    ((to_plot) >= fore_thres[0][i]) & ((to_plot) <= fore_thres[1][i])
                )
        # im_temp = ndi.morphology.binary_opening(im_temp)
        Fore_mask = im_temp > 0
        self.fill_im = Fore_mask > 0
        if "ForeLimits" in analysis_params["Foreground"].keys():
            Fore_labels = skimage.measure.label(Fore_mask)
            Fore_objects = ndi.find_objects(Fore_labels)
            self.HoleLimits = analysis_params["Foreground"]["HoleLimits"].copy()
            self.ForeLimits = analysis_params["Foreground"]["ForeLimits"].copy()
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
            if "ExcludeEdges" in analysis_params["Foreground"]:
                exclude_edges = analysis_params["Foreground"]["ExcludeEdges"]
                if exclude_edges:
                    Fore_mask = skimage.segmentation.clear_border(Fore_mask)
    elif isinstance(analysis_params["Segments"][segName]["thres"], str):
        im_analyzed = self.im_analyzed[self.activeImage]
        if analysis_params["Segments"][segName]["class"] == "Nuc":
            self.fill_im = im_analyzed[analyze_index.index("Nuclei")].copy()
        else:
            self.fill_im = im_analyzed[analyze_index.index("segName")].copy()
        Fore_mask = self.fill_im.copy()
        if "Foreground" in analyze_index:
            Fore_mask[
                np.logical_not(im_analyzed[analyze_index.index("Foreground")])
            ] = 0
        if "ForeLimits" in analysis_params["Segments"][segName].keys():
            Fore_labels = skimage.measure.label(Fore_mask)
            Fore_objects = ndi.find_objects(Fore_labels)
            self.HoleLimits = analysis_params["Segments"][segName]["HoleLimits"].copy()
            self.ForeLimits = analysis_params["Segments"][segName]["ForeLimits"].copy()
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
            #     Back_mask[im_analyzed[analyze_index.index("Foreground")] == False] = 0
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
                Fore_mask[s1] = most_frequent
            if "Foreground" in analyze_index:
                Fore_mask[
                    np.logical_not(im_analyzed[analyze_index.index("Foreground")])
                ] = 0
            del Fore_labels
            del Fore_objects
            del Back_mask
            del Back_labels
            del Back_objects
            if "ExcludeEdges" in analysis_params["Segments"][segName]:
                exclude_edges = analysis_params["Segments"][segName]["ExcludeEdges"]
                if exclude_edges:
                    Fore_mask = skimage.segmentation.clear_border(Fore_mask)
    else:
        im_analyzed = self.im_analyzed[self.activeImage]
        im_temp = np.zeros((im_raw.shape[0], im_raw.shape[1]), dtype=bool)
        seg_thres = analysis_params["Segments"][segName]["thres"]
        if "adaptive_size" in analysis_params["Segments"][segName].keys():
            adaptive_thres = analysis_params["Segments"][segName]["adaptive_size"]
        else:
            adaptive_thres = np.zeros(n_channels)
        while len(seg_thres[0]) < n_channels:
            seg_thres = [np.append(seg_thres[0], 0), np.append(seg_thres[1], np.inf)]
        while len(adaptive_thres) < n_channels:
            adaptive_thres = np.append(adaptive_thres, 0)
        for i in range(n_channels):
            to_plot = im_raw[:, :, i]
            if adaptive_thres[i] > 0:
                filter_size = int(adaptive_thres[i])
                to_plot = to_plot - ndi.filters.uniform_filter(to_plot, filter_size)
                to_plot[to_plot < 0] = 0

            if (seg_thres[0][i] != 0) | (seg_thres[1][i] < np.inf):
                im_temp = (im_temp) | (
                    ((to_plot) >= seg_thres[0][i]) & ((to_plot) <= seg_thres[1][i])
                )
        del to_plot
        # im_temp = ndi.morphology.binary_opening(im_temp)
        Fore_mask = im_temp > 0
        if "Foreground" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("Foreground")]
        self.fill_im = Fore_mask > 0
        if "ForeLimits" in analysis_params["Segments"][segName].keys():
            Fore_labels = skimage.measure.label(Fore_mask)
            Fore_objects = ndi.find_objects(Fore_labels)
            self.HoleLimits = analysis_params["Segments"][segName]["HoleLimits"].copy()
            self.ForeLimits = analysis_params["Segments"][segName]["ForeLimits"].copy()
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
            del Fore_labels
            del Fore_objects
            del Back_mask
            del Back_labels
            del Back_objects
            if "ExcludeEdges" in analysis_params["Segments"][segName]:
                exclude_edges = analysis_params["Segments"][segName]["ExcludeEdges"]
                if exclude_edges:
                    Fore_mask = skimage.segmentation.clear_border(Fore_mask)
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
        Back_area.append(np.sum(Back_labels[s1] == label))
    Back_area = np.array(Back_area)
    popup.wm_title("Fill Images")
    t = "Select a channel of choice and add fill holes or clear  " + "isolated areas."
    label = tkinter.Label(
        popup,
        text="Mask Filling" + " for file :" + self.FileDictionary[self.activeImage],
    )
    toolbar = tkinter.Frame(popup)
    addButton = tkinter.Button(toolbar, text="Register Filled Image", command=SaveFill)
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    resetButton = tkinter.Button(toolbar, text="Reset", command=ResetFill)
    resetButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    cancelButton = tkinter.Button(toolbar, text="Quit without saving", command=QuitFill)
    cancelButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    self.adaptive_var = tkinter.IntVar(popup)
    check_adaptive = tkinter.Checkbutton(
        toolbar, text="Exclude edges", variable=self.adaptive_var
    )
    self.adaptive_var.set(exclude_edges)
    self.adaptive_var.trace_variable("w", remake_fill_after_change)
    check_adaptive.pack(side=tkinter.LEFT)
    toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
    label.pack(side="bottom", fill="x", pady=10)
    popup_statusBar = tkinter.Label(
        popup, text=t, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
    )
    popup_statusBar.pack(side=tkinter.TOP, fill=tkinter.X)
    mainWindow = tkinter.Frame(popup, width=700)
    f = plt.Figure(figsize=(10, 7), dpi=100)
    f.patch.set_visible(False)
    f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax = f.gca()
    image_canvas = Tk_Agg.FigureCanvasTkAgg(f, master=mainWindow)
    image_canvas.draw()
    image_canvas.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_toolbar = NT2Tk(image_canvas, mainWindow)
    image_toolbar.update()
    image_canvas._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    ax.clear()
    ax.imshow(Fore_mask, aspect="equal")
    ax.autoscale(False)
    ax.axis("off")
    self.ax = ax
    image_canvas.draw()
    self.ax_canvas = image_canvas
    rightWindow = tkinter.Frame(popup, width=400)
    rightWindow.pack(side=tkinter.RIGHT)
    mainWindow.pack(side=tkinter.RIGHT)
    internal_windows1 = tkinter.Frame(rightWindow, width=200, height=20)
    self.ForeVariable = tkinter.StringVar(internal_windows1)
    if self.fill_ch > 0:
        self.ForeVariable.set(analyze_index[self.fill_ch])
    else:
        self.ForeVariable.set(index_options[self.fill_ch])
    self.ForeVariable.trace("w", Fill_ch_changed)
    w = tkinter.OptionMenu(internal_windows1, self.ForeVariable, *index_options)
    w.config(width=20)
    w.pack(side=tkinter.LEFT)
    internal_windows1.pack(side=tkinter.TOP)
    fore_windows = tkinter.Frame(rightWindow, width=200, height=20)
    fore_windows.pack(side=tkinter.TOP)
    self.fore_lim_label = tkinter.Label(
        fore_windows,
        text="Foreground Area Limits"
        + "   -   "
        + str(self.ForeLimits[0])
        + " - "
        + str(self.ForeLimits[1]),
    )
    self.fore_lim_label.pack()
    internal_windows = tkinter.Frame(rightWindow, width=400, height=400)
    internal_windows.pack(side=tkinter.TOP)
    f2 = plt.Figure(figsize=(4, 3), dpi=100)
    f2.patch.set_visible(False)
    f2.subplots_adjust(left=0.1, bottom=0.1, right=1, top=1, wspace=0, hspace=0)
    ax2 = f2.gca()
    image_canvas2 = Tk_Agg.FigureCanvasTkAgg(f2, master=internal_windows)
    image_canvas2.draw()
    image_canvas2.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_canvas2._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    image_toolbar2 = NT2Tk(image_canvas2, internal_windows)
    image_toolbar2.update()
    ax2.clear()
    ax2.hist(
        Fore_area,
        bins=np.logspace(np.log10(10), np.log10(max_fore_back_area), 50),
        log=True,
    )
    ax2.autoscale(True)
    ax2.set_xscale("log")
    garbage = matplotlib.widgets.Cursor(ax2, useblit=True, color="r", horizOn=False)
    span_selector = matplotlib.widgets.SpanSelector(
        ax2, Fore_fill_changed, "horizontal", useblit=True
    )
    garbage.active = True
    span_selector.active = True
    ax2.axis("on")
    self.ax2 = ax2
    image_canvas2.draw()
    self.ax2_canvas = image_canvas2
    back_windows = tkinter.Frame(rightWindow, width=200, height=20)
    back_windows.pack(side=tkinter.TOP)
    self.back_lim_label = tkinter.Label(
        back_windows,
        text="Background Area Limits"
        + "   -   "
        + str(self.HoleLimits[0])
        + " - "
        + str(self.HoleLimits[1]),
    )
    self.back_lim_label.pack()
    internal_windows2 = tkinter.Frame(rightWindow, width=400, height=400)
    internal_windows2.pack(side=tkinter.TOP)
    f3 = plt.Figure(figsize=(4, 3), dpi=100)
    f3.patch.set_visible(False)
    f3.subplots_adjust(left=0.1, bottom=0.1, right=1, top=1, wspace=0, hspace=0)
    ax3 = f3.gca()
    image_canvas3 = Tk_Agg.FigureCanvasTkAgg(f3, master=internal_windows2)
    image_canvas3.draw()
    image_canvas3.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
    image_canvas3._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
    image_toolbar3 = NT2Tk(image_canvas3, internal_windows2)
    image_toolbar3.update()
    ax3.clear()
    ax3.hist(
        Back_area,
        bins=np.logspace(np.log10(10), np.log10(max_fore_back_area), 50),
        log=True,
    )
    ax3.autoscale(True)
    ax3.set_xscale("log")
    garbage2 = matplotlib.widgets.Cursor(ax3, useblit=True, color="r", horizOn=False)
    span_selector2 = matplotlib.widgets.SpanSelector(
        ax3, Back_fill_changed, "horizontal", useblit=True
    )
    garbage2.active = True
    span_selector2.active = True
    ax3.axis("on")
    self.ax3 = ax3
    image_canvas2.draw()
    self.ax3_canvas = image_canvas3
    popup.mainloop()


def NucleusDetection(self, external_mode=False, Fore_mask=[]):
    def Combine_small_cells(internal_mode=True, *a):
        if internal_mode:
            voronoi_extend = ExtendVar.get() == "Extend Cell Area To:"
            try:
                voronoi_limit = int(float(area_lim.get()))
            except OverflowError:
                voronoi_limit = np.inf
            except ValueError:
                voronoi_limit = np.inf
        else:
            analysis_params = self.analysis_params[self.activeImage].copy()
            if "CellLimits" in analysis_params["Segments"]["DAPI"]:
                voronoi_extend = (
                    analysis_params["Segments"]["DAPI"]["CellMeth"]
                    == "Extend Cell Area To:"
                )
                voronoi_limit = analysis_params["Segments"]["DAPI"]["CellLimits"]
            else:
                voronoi_extend = False
                voronoi_limit = np.inf
        voronoi_image = self.voronoi_image
        single_cells = self.single_cells
        nucleus_limits = self.NucLimits
        if internal_mode:
            area_limit = np.float(self.adaptive_val.get())
            self.adaptive_temp = area_limit
            [popup_int, label_int] = popupmsg("Combining Cells", False)
        else:
            area_limit = self.adaptive_temp
        if self.adaptive_temp == 0:
            return
        voronoi_image = skimage.segmentation.watershed(
            -ndi.distance_transform_edt(single_cells > 0), single_cells
        )

        voronoi_image = skimage.measure.label(voronoi_image)
        voronoi_image[Fore_mask < 1] = 0
        voronoi_objects = ndi.find_objects(voronoi_image)
        small_cell_nuclei = single_cells * 0
        cell_index = []
        cell_areas = []
        nucleus_index = []
        small_nucleus_index = []
        nucleus_area = []
        excluded_nucleus_ids = []
        num_small_cells = 0
        num_combinations_made = 0
        num_removals_made = 0
        for i, s1 in enumerate(voronoi_objects):
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < (np.sort(im_nuc_temp.ravel())[voronoi_limit])] = (
                    False
                )
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < voronoi_limit] = False
                voronoi_temp = voronoi_image[s1]
                voronoi_temp[im_temp] = 0
                voronoi_image[s1] = voronoi_temp
                im_temp = voronoi_image[s1] == label
            im_nuc_temp = single_cells[s1]
            im_nuc_temp = im_nuc_temp[im_temp]
            i = im_nuc_temp.max()
            if i == 0:
                continue
            cell_area = np.sum(im_temp)
            nucleus_index.append(i)
            cell_areas.append(cell_area)
            if cell_area < area_limit:
                num_small_cells += 1
                small_cell_nuclei[single_cells == i] = 1
                small_nucleus_index.append(i)
        if internal_mode:
            label_int["text"] = (
                "Combining Cells\n"
                + str(num_small_cells)
                + " found"
                + "\n Please hold."
            )
            popup_int.update()
        small_cell_nuclei2 = ndi.morphology.binary_dilation(
            small_cell_nuclei > 0, iterations=1
        )
        small_cell_nuclei2 = skimage.measure.label(small_cell_nuclei2)
        small_objects = ndi.find_objects(small_cell_nuclei2)
        cells_together = []
        areas_together = []
        for i, s1 in enumerate(small_objects):
            if s1 is None:
                continue
            label = i + 1
            im_temp = small_cell_nuclei2[s1] == label
            im_nuc_temp = single_cells[s1]
            im_nuc_temp = im_nuc_temp[im_temp]
            cells_temp = [i for i in np.unique(im_nuc_temp) if i != 0]
            cells_together.append(cells_temp)
            areas_together.append(
                [cell_areas[nucleus_index.index(j)] for j in cells_temp]
            )
        for i in range(len(cells_together), 0, -1):
            i = i - 1
            n_cells = cells_together[i]
            if len(n_cells) == 1:
                cells_together.pop(i)
                areas_together.pop(i)
            # elif np.sum(areas_together[i]) > area_limits[1]:
            #     cells_together.pop(i)
            #     areas_together.pop(i)
            #     n_excluded = n_excluded + 1
        i_min = 0
        while len(cells_together) > 0:
            if i_min == -1:
                break
            i_min = -1
            max_area = np.inf
            for i, j in enumerate(areas_together):
                if np.sum(j) < max_area:
                    max_area = np.sum(j)
                    i_min = i
            if i_min != -1:
                nuclei_combined = single_cells * 0
                for i in cells_together[i_min]:
                    nuclei_combined = (
                        nuclei_combined
                        + ndi.morphology.binary_dilation(
                            single_cells == i, iterations=2
                        )
                        * 1
                    )
                single_cells[nuclei_combined > 1] = cells_together[i_min][0]
            cells_together.pop(i_min)
            areas_together.pop(i_min)
        single_cells[Fore_mask < 1] = 0
        single_cells = skimage.measure.label(single_cells)
        cell_objects = ndi.find_objects(single_cells)
        voronoi_image = skimage.segmentation.watershed(
            -ndi.distance_transform_edt(single_cells > 0), single_cells
        )
        voronoi_image = skimage.measure.label(voronoi_image)
        voronoi_image[Fore_mask < 1] = 0
        voronoi_objects = ndi.find_objects(voronoi_image)
        small_cell_nuclei = single_cells * 0
        cell_index = []
        cell_areas = []
        nucleus_index = []
        small_nucleus_index = []
        nucleus_area = []
        excluded_nucleus_ids = []
        for i, s1 in enumerate(voronoi_objects):
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < (np.sort(im_nuc_temp.ravel())[voronoi_limit])] = (
                    False
                )
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < voronoi_limit] = False
                voronoi_temp = voronoi_image[s1]
                voronoi_temp[im_temp] = 0
                voronoi_image[s1] = voronoi_temp
                im_temp = voronoi_image[s1] == label
            im_nuc_temp = single_cells[s1]
            im_nuc_temp = im_nuc_temp[im_temp]
            i = im_nuc_temp.max()
            if i == 0:
                continue
            cell_area = np.sum(im_temp)
            nucleus_index.append(i)
            cell_areas.append(cell_area)
            if cell_area < area_limit:
                small_cell_nuclei[single_cells == i] = 1
                small_nucleus_index.append(i)
        small_cell_nuclei2 = ndi.morphology.binary_dilation(
            small_cell_nuclei > 0, iterations=2
        )
        small_cell_nuclei2 = skimage.measure.label(small_cell_nuclei2)
        small_objects = ndi.find_objects(small_cell_nuclei2)
        cells_together = []
        areas_together = []
        for i, s1 in enumerate(small_objects):
            if s1 is None:
                continue
            label = i + 1
            im_temp = small_cell_nuclei2[s1] == label
            im_nuc_temp = single_cells[s1]
            im_nuc_temp = im_nuc_temp[im_temp]
            cells_temp = [i for i in np.unique(im_nuc_temp) if i != 0]
            cells_together.append(cells_temp)
            areas_together.append(
                [cell_areas[nucleus_index.index(j)] for j in cells_temp]
            )
        for i in range(len(cells_together), 0, -1):
            i = i - 1
            n_cells = cells_together[i]
            if len(n_cells) == 1:
                single_cells[single_cells == n_cells] = 0
                cells_together.pop(i)
                areas_together.pop(i)
        i_min = 0
        while len(cells_together) > 0:
            if i_min == -1:
                break
            i_min = -1
            max_area = np.inf
            for i, j in enumerate(areas_together):
                if np.sum(j) < max_area:
                    max_area = np.sum(j)
                    i_min = i
            if i_min != -1:
                nuclei_combined = single_cells * 0
                for i in cells_together[i_min]:
                    nuclei_combined = (
                        nuclei_combined
                        + ndi.morphology.binary_dilation(
                            single_cells == i, iterations=2
                        )
                        * 1
                    )
                single_cells[nuclei_combined > 1] = cells_together[i_min][0]
            cells_together.pop(i_min)
            areas_together.pop(i_min)
        single_cells = skimage.measure.label(single_cells)
        single_cells[Fore_mask < 1] = 0
        cell_objects = ndi.find_objects(single_cells)
        for i, s1 in enumerate(cell_objects):
            if s1 is None:
                continue
            label = i + 1
            im_temp = single_cells[s1] == label
            if np.sum(im_temp) < nucleus_limits[0]:
                single_cells[single_cells == label] = 0
        n_try = 0
        n_cells = 0
        combined = -1
        n_cells_before = 0
        n_cells_list = []
        repeated_times = 0
        finished = False
        while not finished:
            max_area_int = np.inf
            n_try = n_try + 1

            single_cells[Fore_mask < 1] = 0
            single_cells = skimage.measure.label(single_cells)
            cell_objects = ndi.find_objects(single_cells)

            for i, s1 in enumerate(cell_objects):
                if s1 is None:
                    continue
                label = i + 1
                im_temp = single_cells[s1] == label
                if np.sum(im_temp) < nucleus_limits[0]:
                    single_cells[single_cells == label] = 0
            finished = True
            voronoi_image = skimage.segmentation.watershed(
                -ndi.distance_transform_edt(single_cells > 0), single_cells
            )

            voronoi_image = skimage.measure.label(voronoi_image)
            voronoi_image[Fore_mask < 1] = 0
            single_cells[Fore_mask < 1] = 0
            voronoi_objects = ndi.find_objects(voronoi_image)
            cell_objects = ndi.find_objects(single_cells)
            cell_index = []
            cell_areas = []
            nucleus_index = []
            nucleus_area = []
            excluded_nucleus_ids = []
            for i, s1 in enumerate(cell_objects):
                if s1 is None:
                    continue
                label = i + 1
                im_temp = single_cells[s1] == label
                nucleus_area.append(np.sum(im_temp))
            for i, s1 in enumerate(voronoi_objects):
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
                    im_temp = voronoi_image[s1] == label
                im_nuc_temp = single_cells[s1]
                im_nuc_temp = im_nuc_temp[im_temp]
                nucleus_index.append(im_nuc_temp.max())
                cell_index.append(label)
                cell_areas.append(np.sum(im_temp))
            n_cells_list.append(len(cell_areas))
            if len(n_cells_list) > 20:
                n_cells_list.pop(0)
            if n_cells_before == len(cell_areas):
                repeated_times = repeated_times + 1
            elif len(cell_areas) < n_cells_before:
                repeated_times = 0
            n_cells_before = np.min(n_cells_list)
            combined = []
            combined_nuc_index = []
            for cell_area in np.unique(cell_areas):
                if (cell_area > area_limit) | (cell_area > max_area_int):
                    continue
                n_i = -1
                tuple_ended = False
                while not tuple_ended:
                    try:
                        n_i = cell_areas.index(cell_area, n_i + 1)
                    except:
                        tuple_ended = True
                        break
                    if nucleus_index[n_i] in excluded_nucleus_ids:
                        continue
                    if nucleus_index[n_i] in combined_nuc_index:
                        continue
                    nuc = single_cells == nucleus_index[n_i]
                    nuc_expanded = ndi.binary_dilation(nuc, iterations=2)
                    neighbor_cells = np.unique(single_cells[nuc_expanded ^ nuc])
                    i_min = -1
                    min_area = np.inf
                    for i in neighbor_cells:
                        if i in combined_nuc_index:
                            continue
                        if (i == 0) | (repeated_times > 20):
                            continue
                        else:
                            if cell_areas[nucleus_index.index(i)] < min_area:
                                min_area = cell_areas[nucleus_index.index(i)]
                                i_min = i
                    if i_min > -1:
                        finished = False
                        num_combinations_made += 1
                        single_cells[
                            (
                                ndi.morphology.binary_dilation(
                                    single_cells == i_min, iterations=2
                                )
                                * 1
                                + nuc_expanded * 1
                                + nuc * 1
                            )
                            > 1
                        ] = i_min
                        combined_nuc_index.append(i_min)
                        combined_nuc_index.append(nucleus_index[n_i])
                        combined.append(1)
                        if min_area + cell_area < max_area_int:
                            max_area_int = min_area + cell_area
                        if internal_mode:
                            label_int["text"] = (
                                "Combining Cells\n"
                                + str(num_small_cells)
                                + " found.\n"
                                + str(num_combinations_made)
                                + " combinations and "
                                + str(num_removals_made)
                                + " removals made.\n Please hold."
                            )
                            popup_int.update()
                    else:
                        #                            tuple_ended = True
                        finished = False
                        num_removals_made += 1
                        single_cells[nuc] = 0
                        combined.append(0)
                        if internal_mode:
                            label_int["text"] = (
                                "Combining Cells\n"
                                + str(num_small_cells)
                                + " found.\n"
                                + str(num_combinations_made)
                                + " combinations and "
                                + str(num_removals_made)
                                + " removals made.\n Please hold."
                            )
                            popup_int.update()

        single_cells = skimage.measure.label(single_cells)
        single_cells[Fore_mask < 1] = 0
        cell_objects = ndi.find_objects(single_cells)

        for i, s1 in enumerate(cell_objects):
            if s1 is None:
                continue
            label = i + 1
            im_temp = single_cells[s1] == label
            if np.sum(im_temp) < nucleus_limits[0]:
                single_cells[single_cells == label] = 0

        self.voronoi_image = voronoi_image
        self.single_cells = single_cells

        if internal_mode:
            single_cells = skimage.measure.label(single_cells)
            single_objects = ndi.find_objects(single_cells)
            single_cells_mask = np.zeros_like(Fore_mask) < 0
            for i, s1 in enumerate(single_objects):
                if s1 is None:
                    continue
                label = i + 1
                im_temp = single_cells[s1] == label
                im_temp = np.float32(im_temp) - np.float32(
                    ndi.morphology.binary_erosion(
                        im_temp, iterations=round(single_cells.shape[0] / 500)
                    )
                )
                single_cells_mask[s1][single_cells[s1] == label] = im_temp[
                    single_cells[s1] == label
                ]
            ax = self.ax
            ax.clear()
            masked_image = self.im_2_display.copy()
            voronoi_image_mask = np.zeros_like(Fore_mask) < 0
            voronoi_image = skimage.measure.label(voronoi_image)
            voronoi_image = np.uint32(voronoi_image * np.float32(Fore_mask))
            voronoi_objects = ndi.find_objects(voronoi_image)
            try:
                voronoi_limit = int(float(area_lim.get()))
            except OverflowError:
                voronoi_limit = np.inf
            except ValueError:
                voronoi_limit = np.inf
            for i, s1 in enumerate(voronoi_objects):
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
                    im_temp = voronoi_image[s1] == label
                im_temp = np.float32(im_temp) - np.float32(
                    ndi.morphology.binary_erosion(
                        im_temp, iterations=round(single_cells.shape[0] / 1000)
                    )
                )
                voronoi_image_mask[s1][voronoi_image[s1] == label] = im_temp[
                    voronoi_image[s1] == label
                ]
            mask_image_temp = masked_image[:, :, 1]
            mask_image_temp[single_cells_mask] = mask_image_temp.max()
            masked_image[:, :, 1] = mask_image_temp
            mask_image_temp = masked_image[:, :, 2]
            mask_image_temp[voronoi_image_mask] = mask_image_temp.max()
            masked_image[:, :, 2] = mask_image_temp
            ax.imshow(masked_image, aspect="equal")
            ax.autoscale(False)
            ax.axis("off")
            DestroyTK(popup_int)
            self.ax_canvas.draw()

    def SaveNuc(*a):
        analyze_index = self.analyze_index[self.activeImage]
        im_analyzed = self.im_analyzed[self.activeImage]
        if "Nuclei" in analyze_index:
            im_analyzed[analyze_index.index("Nuclei")] = self.single_cells
            self.im_analyzed[self.activeImage] = im_analyzed
        else:
            im_analyzed.append(self.single_cells)
            analyze_index.append("Nuclei")
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            self.remake_side_window()
        if "Cells" in analyze_index:
            im_analyzed[analyze_index.index("Cells")] = self.voronoi_image
            self.im_analyzed[self.activeImage] = im_analyzed
        else:
            im_analyzed.append(self.voronoi_image)
            analyze_index.append("Cells")
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            self.remake_side_window()
        self.Get_cell_props()
        DestroyTK(self.popup)
        analysis_params = self.analysis_params[self.activeImage].copy()
        if "NucLimits" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("NucLimits")
        analysis_params["Segments"]["DAPI"]["NucLimits"] = self.NucLimits
        if "CombineNucs" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("CombineNucs")
        analysis_params["Segments"]["DAPI"]["CombineNucs"] = self.adaptive_temp
        if "CellLimits" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("CellLimits")
        try:
            voronoi_limit = int(float(area_lim.get()))
        except OverflowError:
            voronoi_limit = np.inf
        except ValueError:
            voronoi_limit = np.inf
        analysis_params["Segments"]["DAPI"]["CellLimits"] = voronoi_limit
        if "CellMeth" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("CellMeth")
        analysis_params["Segments"]["DAPI"]["CellMeth"] = ExtendVar.get()
        self.analysis_params[self.activeImage] = analysis_params.copy()
        self.RedoPhenotyping()

    def QuitNuc(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to quit cell segmentation")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Okay",
            command=lambda: [DestroyTK(self.popup), DestroyTK(popup2)],
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    def Get_changed_nuc(*a, **k):
        voronoi_extend = ExtendVar.get() == "Extend Cell Area To:"
        self.adaptive_temp = 0
        def_DAPI_image = 0
        water_nuc = 0
        analyze_index = self.analyze_index[self.activeImage]
        im_analyzed = self.im_analyzed[self.activeImage]
        DAPI_mask = im_analyzed[analyze_index.index("DAPI")]
        Fore_mask = np.ones_like(DAPI_mask)
        if "ROI" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("ROI")]
        if "Foreground" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("Foreground")]
        DAPI_mask = DAPI_mask & Fore_mask
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
        if water_nuc:
            cluster_labels = skimage.segmentation.watershed(
                def_DAPI_image * (-ws_dist), ws_markers, mask=cell_clusters > 0
            )
        else:
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
        ax3 = self.ax3
        ax3.clear()
        ax3.hist(nucleus_area, bins=100)
        ax3.autoscale(True)
        self.nucleus_lim_label.config(
            text="Nucleus Area Limits"
            + "   -   "
            + str(self.NucLimits[0])
            + " - "
            + str(self.NucLimits[1])
        )
        garbage2 = matplotlib.widgets.Cursor(
            ax3, useblit=True, color="r", horizOn=False
        )
        span_selector2 = matplotlib.widgets.SpanSelector(
            ax3, Nuc_changed, "horizontal", useblit=True
        )
        garbage2.active = True
        span_selector2.active = True
        ax3.axis("on")
        self.ax3_canvas.draw()
        ax = self.ax
        ax.clear()
        masked_image = self.im_2_display.copy()
        voronoi_image_mask = np.zeros_like(DAPI_labels) < 0
        voronoi_image = skimage.segmentation.watershed(
            -ndi.distance_transform_edt(single_cells > 0), single_cells
        )
        voronoi_image = skimage.measure.label(voronoi_image)
        voronoi_image = np.uint32(voronoi_image * np.float32(Fore_mask))
        voronoi_objects = ndi.find_objects(voronoi_image)
        try:
            voronoi_limit = int(float(area_lim.get()))
        except OverflowError:
            voronoi_limit = np.inf
        except ValueError:
            voronoi_limit = np.inf
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < (np.sort(im_nuc_temp.ravel())[voronoi_limit])] = (
                    False
                )
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < voronoi_limit] = False
                voronoi_temp = voronoi_image[s1]
                voronoi_temp[im_temp] = 0
                voronoi_image[s1] = voronoi_temp
                im_temp = voronoi_image[s1] == label
            im_temp = np.float32(im_temp) - np.float32(
                ndi.morphology.binary_erosion(
                    im_temp, iterations=round(single_cells.shape[0] / 1000)
                )
            )
            voronoi_image_mask[s1][voronoi_image[s1] == label] = im_temp[
                voronoi_image[s1] == label
            ]
        self.voronoi_image = voronoi_image
        mask_image_temp = masked_image[:, :, 1]
        mask_image_temp[single_cells_mask] = mask_image_temp.max()
        masked_image[:, :, 1] = mask_image_temp
        mask_image_temp = masked_image[:, :, 2]
        mask_image_temp[voronoi_image_mask] = mask_image_temp.max()
        masked_image[:, :, 2] = mask_image_temp
        ax.imshow(masked_image, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        self.ax_canvas.draw()

    def Nuc_changed(*a):
        self.NucLimits[0] = a[0]
        if a[1] != a[0]:
            if a[1] > max_nucleus_area:
                self.NucLimits[1] = np.inf
            else:
                self.NucLimits[1] = a[1]
        else:
            self.NucLimits[1] = np.inf
        Get_changed_nuc()

    if external_mode:
        Combine_small_cells(False)
        return
    analyze_index = self.analyze_index[self.activeImage]
    if "DAPI" in analyze_index:
        if len(self.NucLimits) < 2:
            self.NucLimits = [0, np.inf]
        analysis_params = self.analysis_params[self.activeImage].copy()
        if "DAPI" in analysis_params["Segments"]:
            if "CombineNucs" in analysis_params["Segments"]["DAPI"]:
                self.adaptive_temp = analysis_params["Segments"]["DAPI"]["CombineNucs"]
            else:
                self.adaptive_temp = 0
            if "NucLimits" in analysis_params["Segments"]["DAPI"]:
                if not isinstance(
                    analysis_params["Segments"]["DAPI"]["NucLimits"], str
                ):
                    self.NucLimits = analysis_params["Segments"]["DAPI"]["NucLimits"]
        else:
            self.adaptive_temp = 0
        popup = tkinter.Tk()
        self.popup = popup
        im_analyzed = self.im_analyzed[self.activeImage]
        DAPI_mask = im_analyzed[analyze_index.index("DAPI")]
        Fore_mask = np.ones_like(DAPI_mask)
        if "ROI" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("ROI")]
        if "Foreground" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("Foreground")]
        DAPI_mask = DAPI_mask & Fore_mask
        DAPI_labels = skimage.measure.label(DAPI_mask)
        DAPI_objects = ndi.find_objects(DAPI_labels)
        nucleus_area = []
        for i, s1 in enumerate(DAPI_objects):
            if s1 is None:
                continue
            label = i + 1
            nucleus_area.append(np.sum(DAPI_labels[s1] == label))
        nucleus_area = np.array(nucleus_area)
        max_nucleus_area = np.max(nucleus_area)
        popup.wm_title("Nucleus and Cell Segmentation")
        label = tkinter.Label(
            popup,
            text="Nucleus and Cell Segmentation"
            + " for file :"
            + self.FileDictionary[self.activeImage],
        )
        t = (
            "Note: This module uses the DAPI mask; that should be gen"
            + "erated for nucleus foreground through Tissue segmentation"
            + "\nChoose a range for nucleus area to see how the nuclei "
            + "and cell are segmented. Press accept segmentation to"
            + "register the masks."
        )
        toolbar = tkinter.Frame(popup)
        addButton = tkinter.Button(
            toolbar, text="Register Segmentation", command=SaveNuc
        )
        addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        cancelButton = tkinter.Button(
            toolbar, text="Quit without saving", command=QuitNuc
        )
        cancelButton.pack(side=tkinter.LEFT, padx=2, pady=2)
        combineButton = tkinter.Button(
            toolbar, text="Combine cells <", command=Combine_small_cells
        )
        combineButton.pack(side=tkinter.LEFT, padx=2, pady=2)

        labelButton = tkinter.Entry(toolbar)
        labelButton.pack(side=tkinter.LEFT)
        labelButton.insert(0, "100")
        self.adaptive_val = labelButton
        toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
        label.pack(side="bottom", fill="x", pady=10)
        popup_statusBar = tkinter.Label(
            popup, text=t, bd=1, relief=tkinter.SUNKEN, anchor=tkinter.W
        )
        popup_statusBar.pack(side=tkinter.TOP, fill=tkinter.X)
        im_2_display = self.im_2_display
        mainWindow = tkinter.Frame(popup, width=700)
        f = plt.Figure(figsize=(10, 7), dpi=100)
        f.patch.set_visible(False)
        f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        ax = f.gca()
        image_canvas = Tk_Agg.FigureCanvasTkAgg(f, master=mainWindow)
        image_canvas.draw()
        image_canvas.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
        image_toolbar = NT2Tk(image_canvas, mainWindow)
        image_toolbar.update()
        image_canvas._tkcanvas.pack(side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True)
        ax.clear()

        masked_image = im_2_display.copy()
        ax.imshow(masked_image, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        self.ax = ax
        image_canvas.draw()
        self.ax_canvas = image_canvas
        rightWindow = tkinter.Frame(popup, width=400)
        rightWindow.pack(side=tkinter.RIGHT)
        mainWindow.pack(side=tkinter.RIGHT)
        internal_windows = tkinter.Frame(rightWindow, width=400, height=100)
        internal_windows.pack(side=tkinter.TOP)

        area_lim = tkinter.StringVar(popup)
        if "CellLimits" in analysis_params["Segments"]["DAPI"]:
            voronoi_limit = analysis_params["Segments"]["DAPI"]["CellLimits"]
            if float(voronoi_limit) < np.inf:
                area_lim.set(float(voronoi_limit))
        print(analysis_params["Segments"]["DAPI"])
        ExtendVar = tkinter.StringVar(internal_windows)
        if "CellMeth" in analysis_params["Segments"]["DAPI"]:
            ExtendVar.set(analysis_params["Segments"]["DAPI"]["CellMeth"])
        else:
            ExtendVar.set("Extend Cell Area To:")
        label = tkinter.OptionMenu(
            internal_windows, ExtendVar, *["Extend Cell Area To:", "Extend Cells:"]
        )
        # label = tkinter.Label(internal_windows, text="Extend Cells To:")
        label.pack(side=tkinter.LEFT)
        nuc_slider = Slider(internal_windows, area_lim)
        nuc_slider.pack(side=tkinter.LEFT)
        ApplyButton = tkinter.Button(
            internal_windows, text="Apply", command=Get_changed_nuc
        )
        ApplyButton.pack(side=tkinter.LEFT, padx=2, pady=2)

        # area_lim.trace("w", Nuc_changed)
        internal_windows = tkinter.Frame(rightWindow, width=400, height=400)
        internal_windows.pack(side=tkinter.TOP)
        fore_windows = tkinter.Frame(rightWindow, width=200, height=20)
        fore_windows.pack(side=tkinter.TOP)
        self.nucleus_lim_label = tkinter.Label(
            fore_windows,
            text="Nucleus Area Limits"
            + "   -   "
            + str(self.NucLimits[0])
            + " - "
            + str(self.NucLimits[1]),
        )
        self.nucleus_lim_label.pack()
        f2 = plt.Figure(figsize=(4, 3), dpi=100)
        f2.patch.set_visible(False)
        f2.subplots_adjust(left=0.1, bottom=0.1, right=1, top=1, wspace=0, hspace=0)
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
        ax2.hist(
            nucleus_area,
            bins=np.logspace(np.log10(10), np.log10(nucleus_area.max()), 50),
            log=True,
        )
        ax2.autoscale(True)
        ax2.set_xscale("log")
        garbage = matplotlib.widgets.Cursor(ax2, useblit=True, color="r", horizOn=False)
        span_selector = matplotlib.widgets.SpanSelector(
            ax2, Nuc_changed, "horizontal", useblit=True
        )
        garbage.active = True
        span_selector.active = True
        ax2.axis("on")
        self.ax2 = ax2
        image_canvas2.draw()
        self.ax2_canvas = image_canvas2
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
        internal_windows2 = tkinter.Frame(rightWindow, width=400, height=400)
        internal_windows2.pack(side=tkinter.TOP)
        f3 = plt.Figure(figsize=(4, 3), dpi=100)
        f3.patch.set_visible(False)
        f3.subplots_adjust(left=0.1, bottom=0.1, right=1, top=1, wspace=0, hspace=0)
        ax3 = f3.gca()
        temp = Tk_Agg.FigureCanvasTkAgg(f3, master=internal_windows2)
        image_canvas3 = temp
        image_canvas3.draw()
        image_canvas3.get_tk_widget().pack(side=tkinter.TOP, expand=True, anchor="n")
        image_canvas3._tkcanvas.pack(
            side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True
        )
        image_toolbar3 = NT2Tk(image_canvas3, internal_windows2)
        image_toolbar3.update()
        ax3.clear()
        ax3.hist(nucleus_area, bins=50)
        ax3.autoscale(True)
        garbage2 = matplotlib.widgets.Cursor(
            ax3, useblit=True, color="r", horizOn=False
        )
        span_selector2 = matplotlib.widgets.SpanSelector(
            ax3, Nuc_changed, "horizontal", useblit=True
        )
        garbage2.active = True
        span_selector2.active = True
        ax3.axis("on")
        self.ax3 = ax3
        image_canvas3.draw()
        self.ax3_canvas = image_canvas3

        ax.clear()
        masked_image = im_2_display.copy()
        voronoi_image = skimage.segmentation.watershed(
            -ndi.distance_transform_edt(single_cells > 0), single_cells
        )
        voronoi_image_mask = np.zeros_like(DAPI_labels) < 0
        voronoi_image = skimage.measure.label(voronoi_image)
        voronoi_image = np.uint32(voronoi_image * np.float32(Fore_mask))
        self.voronoi_image = voronoi_image
        voronoi_objects = ndi.find_objects(voronoi_image)
        voronoi_extend = ExtendVar.get() == "Extend Cell Area To:"
        try:
            voronoi_limit = int(float(area_lim.get()))
        except OverflowError:
            voronoi_limit = np.inf
        except ValueError:
            voronoi_limit = np.inf
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < (np.sort(im_nuc_temp.ravel())[voronoi_limit])] = (
                    False
                )
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < voronoi_limit] = False
                voronoi_temp = voronoi_image[s1]
                voronoi_temp[im_temp] = 0
                voronoi_image[s1] = voronoi_temp
                im_temp = voronoi_image[s1] == label
            im_temp = np.float32(im_temp) - np.float32(
                ndi.morphology.binary_erosion(
                    im_temp, iterations=round(single_cells.shape[0] / 1000)
                )
            )
            voronoi_image_mask[s1][voronoi_image[s1] == label] = im_temp[
                voronoi_image[s1] == label
            ]
        mask_image_temp = masked_image[:, :, 1]
        mask_image_temp[single_cells_mask] = mask_image_temp.max()
        masked_image[:, :, 1] = mask_image_temp
        mask_image_temp = masked_image[:, :, 2]
        mask_image_temp[voronoi_image_mask] = mask_image_temp.max()
        masked_image[:, :, 2] = mask_image_temp
        ax.imshow(masked_image, aspect="equal")
        ax.autoscale(False)
        ax.axis("off")
        image_canvas.draw()

        popup.mainloop()

    else:
        popup = tkinter.Tk()
        popup.wm_title("DAPI NOT DEFINED!")
        label = tkinter.Label(
            popup, text="Nucleus detection requires " + "a defined DAPI segmentation"
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup,
            text="Define now",
            command=lambda: [DestroyTK(popup), SegmentDetection(self)],
        )
        B1.pack(side=tkinter.LEFT, padx=2, pady=2)
        B2 = tkinter.Button(popup, text="Go Back", command=lambda: [DestroyTK(popup)])
        B2.pack(side=tkinter.LEFT, padx=2, pady=2)
        popup.mainloop()


def FilterImage(self, mode=0, segName=[], *a):
    def Get_filtered_image(external_use=False, segName=[], *a):
        im_raw = np.array(self.im_raw[self.activeImage])
        n_channels = self.n_channels[self.activeImage]
        Channel_pointers = self.Channel_pointers[self.activeImage][:n_channels]
        if external_use:
            analysis_params = self.analysis_params[self.activeImage]["Segments"][
                segName
            ]
            n_ch = Channel_pointers.index(analysis_params["Ch_name"])
            filter_type1 = analysis_params["filter_type1"]
            filter_type2 = analysis_params["filter_type2"]
            filter_1_size = int(analysis_params["filter_1"])
            filter_2_size = int(analysis_params["filter_2"])
            filter_1_button = int(filter_1_size >= 0)
            filter_2_button = int(filter_2_size >= 0)
            filter_operator_type = analysis_params["operator"]
            if "normalize" in analysis_params:
                normalize_image = analysis_params["normalize"]
            else:
                normalize_image = 0
        else:
            n_ch = Channel_pointers.index(channel_param.get())
            filter_type1 = filter_type1_var.get()[:-7]
            filter_type2 = filter_type2_var.get()[:-7]
            filter_1_size = int(filter_1.get())
            filter_2_size = int(filter_2.get())
            filter_1_button = filter_1_but.get()
            filter_2_button = filter_2_but.get()
            filter_operator_type = filter_operator.get()
            normalize_image = image_norm.get()
        im_init = im_raw[:, :, n_ch]
        if filter_1_button == 1:
            if filter_1_size == 0:
                im_1 = im_init.copy()
            elif filter_type1 == "Gaussian":
                im_1 = ndi.filters.gaussian_filter(im_init, filter_1_size)
            elif filter_type1 == "Gradient Magnitude":
                im_1 = ndi.filters.gaussian_gradient_magnitude(im_init, filter_1_size)
            elif filter_type1 == "Laplace":
                im_1 = ndi.filters.gaussian_laplace(im_init, filter_1_size)
            elif filter_type1 == "Maximum":
                im_1 = ndi.filters.maximum_filter(im_init, filter_1_size)
            elif filter_type1 == "Median":
                im_1 = ndi.filters.median_filter(im_init, filter_1_size)
            elif filter_type1 == "Minimum":
                im_1 = ndi.filters.minimum_filter(im_init, filter_1_size)
            elif filter_type1 == "Uniform":
                im_1 = ndi.filters.uniform_filter(im_init, filter_1_size)
        else:
            im_1 = im_init * 0
        if filter_operator_type[:3] == "and":
            im_init = im_1
            filter_operator_type = filter_operator_type[-1]
        if filter_2_button == 1:
            if filter_2_size == 0:
                im_2 = im_init.copy()
            elif filter_type2 == "Gaussian":
                im_2 = ndi.filters.gaussian_filter(im_init, filter_2_size)
            elif filter_type2 == "Gradient Magnitude":
                im_2 = ndi.filters.gaussian_gradient_magnitude(im_init, filter_2_size)
            elif filter_type2 == "Laplace":
                im_2 = ndi.filters.gaussian_laplace(im_init, filter_2_size)
            elif filter_type2 == "Maximum":
                im_2 = ndi.filters.maximum_filter(im_init, filter_2_size)
            elif filter_type2 == "Median":
                im_2 = ndi.filters.median_filter(im_init, filter_2_size)
            elif filter_type2 == "Minimum":
                im_2 = ndi.filters.minimum_filter(im_init, filter_2_size)
            elif filter_type2 == "Uniform":
                im_2 = ndi.filters.uniform_filter(im_init, filter_2_size)
        else:
            im_2 = im_init * 0
        if filter_operator_type == "+":
            im_out = im_1 + im_2
        elif filter_operator_type == "-":
            im_out = im_1 - im_2
        elif filter_operator_type == "*":
            if (filter_1_button == 0) | (filter_2_button == 0):
                im_out = im_1 + im_2
            else:
                im_out = im_1 * im_2
        elif filter_operator_type == "/":
            if (filter_1_button == 0) | (filter_2_button == 0):
                im_out = im_1 + im_2
            else:
                im_out = im_1 / im_2
        if (filter_1_button == 0) & (filter_2_button == 0):
            im_out = im_init.copy()
        if normalize_image > 0:
            im_out = im_out - np.min(im_out)
            im_out = im_out / np.max(im_out)
        return im_out

    def Modify_images_for_filtered(*a):
        n_channels = self.n_channels[self.activeImage]
        n_channels_init = self.n_channels[self.activeImage]
        im_raw = self.im_raw[self.activeImage].copy()
        analysis_params = self.analysis_params[self.activeImage]
        im_analyzed = self.im_analyzed[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        Channel_pointers = self.Channel_pointers[self.activeImage].copy()
        Color_pointers = self.Color_pointers[self.activeImage].copy()
        Channel_pointers_temp = Channel_pointers[:n_channels]
        Color_pointers_temp = Color_pointers[:n_channels]
        for segName in analysis_params["Segments"].keys():
            if "filter_1" in analysis_params["Segments"][segName]:
                if analysis_params["Segments"][segName]["Visible"]:
                    im_temp = np.zeros(
                        (im_raw.shape[0], im_raw.shape[1], 1), dtype=im_raw.dtype
                    )
                    if segName in analyze_index:
                        im_temp[:, :, 0] = im_analyzed[analyze_index.index(segName)]
                    else:
                        im_temp[:, :, 0] = Get_filtered_image(True, segName)
                    im_raw = np.concatenate((im_raw, im_temp), axis=2)
                    n_channels += 1
                    try:
                        Color_pointers_temp.append(
                            Color_pointers[
                                analyze_index.index(segName) + n_channels_init
                            ]
                        )
                    except IndexError:
                        Color_pointers_temp.append("black")
                    Channel_pointers_temp.append(segName)
        self.im_raw_temp = im_raw
        self.n_channels_temp = n_channels
        self.Channel_pointers_temp = Color_pointers_temp
        self.Color_pointers_temp = Channel_pointers_temp

    if mode == 1:
        return Get_filtered_image(external_use=True, segName=segName)
    elif mode == 2:
        Modify_images_for_filtered()
        return
    filters_available = [
        "Gaussian",
        "Gradient Magnitude",
        "Laplace",
        "Maximum",
        "Median",
        "Minimum",
        "Uniform",
    ]
    filters_available = [i + " filter" for i in filters_available]
    banned_seg_names = ["DAPI", "Tumor", "Stroma"]
    for i in self.Markers:
        if i != "DAPI":
            banned_seg_names.append(i)
        banned_seg_names.append(i + "-Filter")
    im_raw = self.im_raw[self.activeImage]
    Channel_pointers = self.Channel_pointers[self.activeImage]
    popup = tkinter.Tk()
    self.popup = popup
    im_2_display = self.im_2_display.copy()

    def AddImage(*a):
        def AddImageSure(popup2, *a):
            def AddImageSureSure(popup, *a):
                im_out = Get_filtered_image()
                segName = self.SegName.get()
                analyze_index = self.analyze_index[self.activeImage]
                im_analyzed = self.im_analyzed[self.activeImage]
                analysis_params = self.analysis_params[self.activeImage].copy()
                if segName in analysis_params["Segments"]:
                    analysis_params["Segments"].pop(segName)
                if filter_1_but.get() == 1:
                    filter_1_value = int(filter_1.get())
                else:
                    filter_1_value = -1
                if filter_2_but.get() == 1:
                    filter_2_value = int(filter_2.get())
                else:
                    filter_2_value = -1
                analysis_params["Segments"][segName] = {
                    "Visible": True,
                    "filter_1": filter_1_value,
                    "filter_2": filter_2_value,
                    "filter_type1": filter_type1_var.get()[:-7],
                    "filter_type2": filter_type2_var.get()[:-7],
                    "operator": filter_operator.get(),
                    "Ch_name": channel_param.get(),
                    "normalize": image_norm.get(),
                }
                self.analysis_params[self.activeImage] = analysis_params.copy()
                DestroyTK(popup)
                if segName in analyze_index:
                    im_analyzed[analyze_index.index(segName)] = im_out
                    self.im_analyzed[self.activeImage] = im_analyzed
                    self.RedoPhenotyping()
                else:
                    im_analyzed.append(im_out)
                    analyze_index.append(segName)
                    self.im_analyzed[self.activeImage] = im_analyzed
                    self.analyze_index[self.activeImage] = analyze_index
                    self.remake_side_window()
                    self.RedoPhenotyping()

            segName = self.SegName.get()
            analyze_index = self.analyze_index[self.activeImage]
            if segName in banned_seg_names:
                popup3 = tkinter.Tk()
                popup3.wm_title("Banned name")
                label = tkinter.Label(
                    popup3,
                    text=(
                        segName
                        + " is a reserved name and you"
                        + "\cannot give that name to your filter"
                    ),
                )
                label.pack(side="top", fill="x", pady=10)
                B2 = tkinter.Button(
                    popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
                )
                B2.pack()
                popup3.mainloop()
            elif segName in analyze_index:
                popup3 = tkinter.Tk()
                popup3.wm_title("Tissue Exists")
                label = tkinter.Label(
                    popup3,
                    text="A tissue with the same name exists.\n"
                    + "would you like to overwrite?",
                )
                label.pack(side="top", fill="x", pady=10)
                B1 = tkinter.Button(
                    popup3,
                    text="Okay",
                    command=lambda: [DestroyTK(popup3), AddImageSureSure(popup2)],
                )
                B1.pack()
                B2 = tkinter.Button(
                    popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
                )
                B2.pack()
                popup3.mainloop()
            else:
                AddImageSureSure(popup2)

        popup2 = tkinter.Tk()
        popup2.wm_title("Add Channel")
        label = tkinter.Label(popup2, text="How would you like to name your channel?")
        label.pack(side="top", fill="x", pady=10)
        labelButton = tkinter.Entry(popup2)
        labelButton.pack()
        labelButton.insert(0, channel_param.get() + "_filtered")
        self.SegName = labelButton
        B1 = tkinter.Button(popup2, text="Okay", command=lambda: [AddImageSure(popup2)])
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        if (filter_1_but.get() == 0) & (filter_2_but.get() == 0):
            popupmsg(
                "You do not have a new image; \nyou can" + " still save it if you want"
            )
        popup2.mainloop()

    def OverwriteImage(*a):
        def OverwriteSure(*a):
            im_out = Get_filtered_image()
            im_raw[:, :, Channel_pointers.index(channel_param.get())] = im_out

            self.im_raw[self.activeImage] = im_raw
            self.Analysis_like = self.activeImage
            self.QuickAnalysisLikeSure()

        popup3 = tkinter.Tk()
        popup3.wm_title("Filtered Phenotyping")
        label = tkinter.Label(
            popup3,
            text=(
                "If you continue, your original image will be"
                + "\novwritten, your whole analysis will be\n"
                + "redone, and you might need to readjust your"
                + "analysis.\nUsing 'Add Image' option is more "
                + "reliable.\n\nAre you sure you want to continue?"
            ),
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup3,
            text="Yes, I want to overwrite my image",
            command=lambda: [DestroyTK(popup3), OverwriteSure()],
        )
        B1.pack()
        B2 = tkinter.Button(
            popup3, text="No, Go Back", command=lambda: [DestroyTK(popup3)]
        )
        B2.pack()
        popup3.mainloop()

    def PhenotypeImage(*a):
        def PhenoSure(*a):
            analysis_params = self.analysis_params[self.activeImage].copy()
            filter_type1 = filter_type1_var.get()[:-7]
            filter_type2 = filter_type2_var.get()[:-7]
            if filter_1_but.get() == 1:
                filter_1_value = int(filter_1.get())
            else:
                filter_1_value = -1
            if filter_2_but.get() == 1:
                filter_2_value = int(filter_2.get())
            else:
                filter_2_value = -1
            analysis_params["Segments"][channel_param.get() + "-Filter"] = {
                "Visible": False,
                "filter_1": filter_1_value,
                "filter_2": filter_2_value,
                "filter_type1": filter_type1,
                "filter_type2": filter_type2,
                "operator": filter_operator.get(),
                "Ch_name": channel_param.get(),
                "normalize": image_norm.get(),
            }
            self.analysis_params[self.activeImage] = analysis_params.copy()
            self.RedoPhenotyping()

        popup3 = tkinter.Tk()
        popup3.wm_title("Filtered Phenotyping")
        label = tkinter.Label(
            popup3,
            text=(
                "If you continue, this image will be phenotyped"
                + "\ninstead of the original image.\n"
                + "Are you sure?"
            ),
        )
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup3, text="Okay", command=lambda: [DestroyTK(popup3), PhenoSure()]
        )
        B1.pack()
        B2 = tkinter.Button(popup3, text="Go Back", command=lambda: [DestroyTK(popup3)])
        B2.pack()
        popup3.mainloop()

    def RmvSeg(*a):
        def RmvSegSure(popup2, *a):
            segName = self.SegName.get()
            DestroyTK(popup2)
            analysis_params = self.analysis_params[self.activeImage].copy()
            if segName in analysis_params["Segments"]:
                analysis_params["Segments"].pop(segName)
            elif segName in analysis_params["Phenotypes"]:
                analysis_params["Phenotypes"].pop(segName)
            self.analysis_params[self.activeImage] = analysis_params.copy()
            analyze_index = self.analyze_index[self.activeImage]
            im_analyzed = self.im_analyzed[self.activeImage]
            color_variable = self.color_variable[self.activeImage]
            Color_pointers = self.Color_pointers[self.activeImage]
            if segName in analyze_index:
                im_analyzed.pop(analyze_index.index(segName))
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
            self.RedoPhenotyping()

        analysis_params = self.analysis_params[self.activeImage].copy()
        seg_names = [i for i in analysis_params["Segments"].keys()]
        for i in analysis_params["Phenotypes"].keys():
            seg_names.append(i)
        if len(seg_names) > 0:
            popup2 = tkinter.Tk()
            popup2.wm_title("Remove Segment")
            label = tkinter.Label(popup2, text="Which tissue would you like to remove?")
            label.pack(side="top", fill="x", pady=10)
            internal_windows = tkinter.Frame(popup2, width=200, height=20)
            internal_windows.pack(side=tkinter.TOP)
            self.SegName = tkinter.StringVar(internal_windows)
            self.SegName.set(seg_names[0])
            w = tkinter.OptionMenu(internal_windows, self.SegName, *seg_names)
            w.config(width=20)
            w.pack(side=tkinter.LEFT)
            B1 = tkinter.Button(
                popup2, text="Remove", command=lambda: [RmvSegSure(popup2)]
            )
            B1.pack()
            B2 = tkinter.Button(
                popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
            )
            B2.pack()
            popup2.mainloop()

    def QuitSeg(*a):
        popup2 = tkinter.Tk()
        popup2.wm_title("Are you sure?")
        label = tkinter.Label(popup2, text="You are about to quit image filtering")
        label.pack(side="top", fill="x", pady=10)
        B1 = tkinter.Button(
            popup2,
            text="Okay",
            command=lambda: [DestroyTK(self.popup), DestroyTK(popup2)],
        )
        B1.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()
        self.remake_side_window()

    def FilterChanged(*a):
        im_out = Get_filtered_image()
        if display_param.get() == "Composite":
            im_2_display_temp = im_2_display.copy()
            n_ch = Channel_pointers.index(channel_param.get())
            ch_color = self.color_variable[self.activeImage][n_ch].get()
            im_out = (im_out - im_out.min()) / (im_out.max() - im_out.min())
            im_init = im_raw[:, :, n_ch]
            im_out_dif = im_out - (
                (im_init - im_init.min()) / (im_init.max() - im_init.min())
            )
            # im_out = im_out - im_out.mean() + im_init.mean()
            for j in range(3):
                im_temp = im_2_display_temp[:, :, j]
                im2_add = (im_out_dif) * self.LUT[ch_color][j]
                im_temp = im_temp + im2_add
                im_2_display_temp[:, :, j] = im_temp
        else:
            im_2_display_temp = im_2_display * 0
            for j in range(3):
                im_temp = im_2_display_temp[:, :, j]
                im2_add = (im_out - im_out.min()) / (im_out.max() - im_out.min())
                im2_add = im2_add * self.LUT[display_param.get()][j]
                im_temp = im_temp + im2_add
                im_2_display_temp[:, :, j] = im_temp
        ax_image.clear()
        ax_image.imshow(im_2_display_temp, aspect="equal")
        ax_image.autoscale(False)
        ax_image.axis("off")
        image_canvas.draw()

    popup.wm_title("Image Filtering")
    label = tkinter.Label(
        popup, text="Filtering for file :" + self.FileDictionary[self.activeImage]
    )
    toolbar = tkinter.Frame(popup)
    addButton = tkinter.Button(toolbar, text="Add Image", command=AddImage)
    addButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvButton = tkinter.Button(toolbar, text="Overwrite Image", command=OverwriteImage)
    rmvButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    rmvButton = tkinter.Button(
        toolbar, text="Use for Phenotyping", command=PhenotypeImage
    )
    rmvButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    resetButton = tkinter.Button(toolbar, text="Remove Image", command=RmvSeg)
    resetButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    cancelButton = tkinter.Button(toolbar, text="Quit", command=QuitSeg)
    cancelButton.pack(side=tkinter.LEFT, padx=2, pady=2)
    filter_1_but = tkinter.IntVar(popup)
    check_filter1 = tkinter.Checkbutton(toolbar, text="", variable=filter_1_but)
    filter_1_but.trace_variable("w", FilterChanged)
    check_filter1.pack(side=tkinter.LEFT)

    filter_type1_var = tkinter.StringVar(popup)
    filter_type1_var.set("Gaussian filter")
    filter_type1_var.trace("w", FilterChanged)
    filter_menu1 = tkinter.OptionMenu(toolbar, filter_type1_var, *filters_available)
    filter_menu1.config(width=10)
    filter_menu1.pack(side=tkinter.LEFT)

    filter_1 = tkinter.Entry(toolbar)
    filter_1.config(width=10)
    filter_1.pack(side=tkinter.LEFT)
    filter_1.insert(0, "3")
    filter_operator = tkinter.StringVar(popup)
    filter_operator.set("-")
    filter_operator.trace("w", FilterChanged)
    check_operator = tkinter.OptionMenu(
        toolbar, filter_operator, *["+", "-", "*", "/", "and+", "and-", "and*", "and/"]
    )
    check_operator.config(width=5)
    check_operator.pack(side=tkinter.LEFT)
    filter_2_but = tkinter.IntVar(popup)
    check_filter2 = tkinter.Checkbutton(toolbar, text="", variable=filter_2_but)
    filter_2_but.trace_variable("w", FilterChanged)
    check_filter2.pack(side=tkinter.LEFT)

    filter_type2_var = tkinter.StringVar(popup)
    filter_type2_var.set("Gaussian filter")
    filter_type2_var.trace("w", FilterChanged)
    filter_menu2 = tkinter.OptionMenu(toolbar, filter_type2_var, *filters_available)
    filter_menu2.config(width=10)
    filter_menu2.pack(side=tkinter.LEFT)

    filter_2 = tkinter.Entry(toolbar)
    filter_2.config(width=10)
    filter_2.pack(side=tkinter.LEFT)
    filter_2.insert(0, "30")

    label = tkinter.Label(toolbar, text="Normalize")
    label.pack(side=tkinter.LEFT)

    image_norm = tkinter.IntVar(popup)
    check_filter2 = tkinter.Checkbutton(toolbar, text="", variable=image_norm)
    image_norm.trace_variable("w", FilterChanged)
    check_filter2.pack(side=tkinter.LEFT)

    label = tkinter.Label(toolbar, text="Display")
    label.pack(side=tkinter.LEFT)
    channel_param = tkinter.StringVar(popup)
    channel_param.set(Channel_pointers[0])
    channel_param.trace("w", FilterChanged)
    channel_menu = tkinter.OptionMenu(toolbar, channel_param, *Channel_pointers)
    channel_menu.config(width=10)
    channel_menu.pack(side=tkinter.LEFT)

    display_param = tkinter.StringVar(popup)
    display_possibilities = ["Composite"]
    for i in self.LUT.keys():
        display_possibilities.append(i)
    display_param.set("Composite")
    display_param.trace("w", FilterChanged)
    display_menu = tkinter.OptionMenu(toolbar, display_param, *display_possibilities)
    display_menu.config(width=10)
    display_menu.pack(side=tkinter.LEFT)

    toolbar.pack(side=tkinter.TOP, fill=tkinter.X)
    f = plt.Figure(figsize=(10, 7), dpi=100)
    f.patch.set_visible(False)
    f.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
    ax_image = f.gca()
    mainWindow = tkinter.Frame(popup, width=700)
    image_canvas = Tk_Agg.FigureCanvasTkAgg(f, master=mainWindow)
    image_canvas.draw()
    image_canvas.get_tk_widget().pack(side=tkinter.LEFT, expand=True)
    image_toolbar = NT2Tk(image_canvas, mainWindow)
    image_toolbar.update()
    image_canvas._tkcanvas.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)
    mainWindow.pack(side=tkinter.RIGHT)
    ax_image.clear()
    ax_image.imshow(im_2_display, aspect="equal")
    ax_image.autoscale(False)
    ax_image.axis("off")
    image_canvas.draw()
    popup.mainloop()


def MaskEnumeration(self):
    Segment_keys = list(self.analysis_params[self.activeImage]["Segments"].keys())

    def MaskAnalysisAdd(*a, **k):
        segName = self.SegName.get()
        analysis_params = self.analysis_params[self.activeImage].copy()
        if segName in analysis_params["Segments"]:
            analysis_params["Segments"][segName]["Speck"] = 2

    def SpeckAnalysisAdd(*a, **k):
        segName = self.SegName.get()
        analysis_params = self.analysis_params[self.activeImage].copy()
        if segName in analysis_params["Segments"]:
            analysis_params["Segments"][segName]["Speck"] = 1

    def AnalysisRmv(*a, **k):
        segName = self.SegName.get()
        analysis_params = self.analysis_params[self.activeImage].copy()
        if segName in analysis_params["Segments"]:
            analysis_params["Segments"][segName]["Speck"] = 0

    if len(Segment_keys) > 0:
        popup2 = tkinter.Tk()
        popup2.wm_title("Add Segment Mask/Spot Enumeration")
        label = tkinter.Label(
            popup2, text="Which tissue would you like to be enumerated?"
        )
        label.pack(side="top", fill="x", pady=10)
        internal_windows = tkinter.Frame(popup2, width=200, height=20)
        internal_windows.pack(side=tkinter.TOP)
        self.SegName = tkinter.StringVar(internal_windows)
        self.SegName.set(Segment_keys[0])
        w = tkinter.OptionMenu(internal_windows, self.SegName, *Segment_keys)
        w.config(width=20)
        w.pack(side=tkinter.LEFT)
        B1 = tkinter.Button(
            popup2,
            text="Enumerate Mask",
            command=lambda: [MaskAnalysisAdd(), DestroyTK(popup2)],
        )
        B1.pack()
        B2 = tkinter.Button(
            popup2,
            text="Enumerate Spot",
            command=lambda: [SpeckAnalysisAdd(), DestroyTK(popup2)],
        )
        B2.pack()
        B3 = tkinter.Button(
            popup2, text="Remove", command=lambda: [AnalysisRmv(), DestroyTK(popup2)]
        )
        B3.pack()
        B4 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B4.pack()
        popup2.mainloop()


def Tissue_analysis(self, tissue_name=[], external_use=False):
    def Get_tissue_props(tissue_name, internal_call=True):
        im_raw = np.array(self.im_raw[self.activeImage])
        n_channels = self.n_channels[self.activeImage]
        analyze_index = self.analyze_index[self.activeImage]
        im_analyzed = self.im_analyzed[self.activeImage]
        tissue_masks = im_analyzed[analyze_index.index(tissue_name)]
        analysis_params = self.analysis_params[self.activeImage].copy()
        analysis_params["Segments"][tissue_name]["Tissue_props"] = True
        self.analysis_params[self.activeImage] = analysis_params.copy()
        Channel_pointers = self.Channel_pointers[self.activeImage]
        Segment_keys = list(analysis_params["Segments"].keys())
        Fore_mask = np.ones_like(tissue_masks)
        if "ROI" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("ROI")]
        if "Foreground" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("Foreground")]
        tissue_masks[Fore_mask < 1] = 0
        tissue_masks = skimage.measure.label(tissue_masks)
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
                    filter_ch = Channel_pointers.index(
                        analysis_params["Segments"][SegName]["Ch_name"]
                    )
                    im_raw[:, :, filter_ch] = FilterImage(self, mode=1, segName=SegName)

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
                            Speck_temp[
                                int(speck_centroid[0]), int(speck_centroid[1])
                            ] = 1
                    else:
                        Speck_temp = speck_im
                    Speck_images.append(Speck_temp)
        single_objects = ndi.find_objects(tissue_masks)
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
                n_cells_missing += 1
                continue
            label = i + 1
            im_temp = tissue_masks[s1] == label
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
                                np.array(
                                    [[0, 1, 0], [1, 1, 1], [0, 1, 0]], dtype=np.uint8
                                ),
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
        nucleus_index = pd.Index(nucleus_index, name="tissue number")
        tissue_props = pd.DataFrame(
            {
                "Area": nucleus_areas,
                "Perimeter": nucleus_perim,
                "Centroid": nucleus_centroids,
                "Eccentricity": nucleus_eccentricity,
                "Equivalent Diameter": nucleus_equiv_diam,
                "Major Axis Length": nucleus_mj_ax,
                "Minor Axis Length": nucleus_mn_ax,
                "Orientation": nucleus_orientation,
                "Fluorescent Maximum Intensity": max_I_n,
                "Fluorescent Mean Intensity": mean_I_n,
                "Fluorescent Minimum Intensity": min_I_n,
                "Fluorescent Total Intensity": sum_I_n,
                "Fluorescent STD Intensity": std_I_n,
                "Segments": [["All"] for _ in range(np.size(nucleus_areas))],
                "Phenotypes": [["All"] for _ in range(np.size(nucleus_areas))],
                "Show Data": np.ones_like(nucleus_areas),
            },
            index=nucleus_index,
        )
        segment_list = tissue_props["Segments"][:].tolist()
        nucleus_centroids = np.uint32(np.round(tissue_props["Centroid"][:].tolist()))
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
        for i in range(np.size(segment_list)):
            if Tumor_mask[nucleus_centroids[i][0], nucleus_centroids[i][1]] == 1:
                segment_list[i].append("Tumor+")
            elif Stroma_mask[nucleus_centroids[i][0], nucleus_centroids[i][1]] == 1:
                segment_list[i].append("Stroma+")
        tissue_props["Segments"] = segment_list
        self.Tissue_props[self.activeImage][tissue_name] = tissue_props
        if internal_call:
            TissuePhenotype_select(tissue_name)

    def TissuePhenotype_select(tissue_name=[]):
        tissue_keys = [i for i in self.Tissue_props[self.activeImage].keys()]
        if len(tissue_name) == 0:
            tissue_name = tissue_keys[0]

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
                    if segName in tissue_keys:
                        self.Tissue_props[self.activeImage].pop(segName)
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
                self.QuickAnalysisLikeSure()
                DestroyTK(pop2)
                DestroyTK(self.popup)
                PhenotypeSelectionForReal()

            Color_pointers = self.Color_pointers[self.activeImage]
            n_channels = self.n_channels[self.activeImage]
            if len(Color_pointers) > n_channels:
                analyze_index = [
                    i
                    for i in self.analysis_params[self.activeImage]["Phenotypes"].keys()
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
                    popup2,
                    text="Remove",
                    command=lambda: [DestroyTK(popup2), RmvSegSure()],
                )
                B1.pack()
                B2 = tkinter.Button(
                    popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
                )
                B2.pack()
                popup2.mainloop()

        def Define_Tissue_Phenotype_Mask(*a):
            def Make_mask_sure(*a):
                combined_name = self.SegName[1].get()
                tissue_props = self.Tissue_props[self.activeImage]
                for tissue_name in tissue_props:
                    if combined_name.find(tissue_name + " - ") == 0:
                        break
                pheno_name = combined_name[
                    combined_name.find(tissue_name + " - ") + len(tissue_name + " - ") :
                ]
                analyze_index = self.analyze_index[self.activeImage]
                im_analyzed = self.im_analyzed[self.activeImage]
                tissue_mask = im_analyzed[analyze_index.index(tissue_name)]
                tissue_mask_new = tissue_mask < 0
                tissue_phenos = self.Tissue_props[self.activeImage][tissue_name][
                    "Phenotypes"
                ].to_numpy()
                Fore_mask = np.ones_like(tissue_mask)
                if "ROI" in analyze_index:
                    Fore_mask = Fore_mask & im_analyzed[analyze_index.index("ROI")]
                if "Foreground" in analyze_index:
                    Fore_mask = (
                        Fore_mask & im_analyzed[analyze_index.index("Foreground")]
                    )
                tissue_mask[Fore_mask < 1] = 0
                tissue_mask = skimage.measure.label(tissue_mask)
                single_objects = ndi.find_objects(tissue_mask)
                for i, s1 in enumerate(single_objects):
                    if s1 is None:
                        continue
                    if pheno_name in tissue_phenos[i]:
                        label = i + 1
                        im_temp = tissue_mask[s1]
                        im_temp2 = tissue_mask_new[s1]
                        im_temp2[im_temp == label] = True
                        tissue_mask_new[s1] = im_temp2
                if self.SegName[0].get() in analyze_index:
                    im_analyzed[analyze_index.index(self.SegName[0].get())] = (
                        tissue_mask_new
                    )
                else:
                    analyze_index.append(self.SegName[0].get())
                    im_analyzed.append(tissue_mask_new)
                self.analysis_params[self.activeImage]["Segments"][
                    self.SegName[0].get()
                ] = {"thres": pheno_name, "adaptive_size": tissue_name}
                self.analyze_index[self.activeImage] = analyze_index
                self.im_analyzed[self.activeImage] = im_analyzed
                self.remake_side_window()

            def Make_mask(popup2, *a):
                banned_seg_names = ["DAPI", "Tumor", "Stroma"]
                for i in self.Markers:
                    if i != "DAPI":
                        banned_seg_names.append(i)
                    banned_seg_names.append(i + "-Filter")
                segName = self.SegName[0].get()
                analyze_index = self.analyze_index[self.activeImage]
                if segName in banned_seg_names:
                    popup3 = tkinter.Tk()
                    popup3.wm_title("Banned name")
                    label = tkinter.Label(
                        popup3,
                        text=(
                            segName
                            + " is a reserved name and you"
                            + "/ncannot give that name to your segment"
                        ),
                    )
                    label.pack(side="top", fill="x", pady=10)
                    B2 = tkinter.Button(
                        popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
                    )
                    B2.pack()
                    popup3.mainloop()
                elif segName in analyze_index:
                    popup3 = tkinter.Tk()
                    popup3.wm_title("Tissue Exists")
                    label = tkinter.Label(
                        popup3,
                        text="A tissue with the same name exists.\n"
                        + "would you like to overwrite?",
                    )
                    label.pack(side="top", fill="x", pady=10)
                    B1 = tkinter.Button(
                        popup3,
                        text="Okay",
                        command=lambda: [
                            DestroyTK(popup3),
                            Make_mask_sure(),
                            DestroyTK(popup2),
                        ],
                    )
                    B1.pack()
                    B2 = tkinter.Button(
                        popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
                    )
                    B2.pack()
                    popup3.mainloop()
                else:
                    Make_mask_sure()
                    DestroyTK(popup2)

            tissue_props = self.Tissue_props[self.activeImage]
            seg_available = []
            if len(tissue_props) > 0:
                for i in tissue_props:
                    seg_available_temp = []
                    for j in np.unique(np.hstack(tissue_props[i]["Phenotypes"][:])):
                        seg_available_temp.append(j)
                    seg_available_temp = list(np.unique(seg_available_temp))
                    seg_available_temp.pop(seg_available_temp.index("All"))
                    for j in seg_available_temp:
                        seg_available.append(i + " - " + j)
            if len(seg_available) == 0:
                popup2 = tkinter.Tk()
                popup2.wm_title("Cannot Make Tissue Phenotype Mask")
                label = ttkinter.Label(
                    popup2, text="You have no tissue phenotype defined!"
                )
                label.pack(side="top", fill="x", pady=10)
                B2 = tkinter.Button(
                    popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
                )
                B2.pack()
                popup2.mainloop()
                return
            popup2 = tkinter.Tk()
            popup2.wm_title("Make Tissue Phenotype Mask")
            label = ttkinter.Label(
                popup2, text="Which tissue phenotype do you want a mask of?"
            )
            label.pack(side="top", fill="x", pady=10)
            internal_windows = tkinter.Frame(popup2, width=200, height=20)
            internal_windows.pack(side=tkinter.TOP)
            labelButton = tkinter.Entry(popup2)
            labelButton.pack()
            labelButton.insert(0, "Maskname")
            self.SegName = [labelButton]

            self.SegName.append(tkinter.StringVar(internal_windows))
            self.SegName[1].set(seg_available[0])
            w = tkinter.OptionMenu(internal_windows, self.SegName[1], *seg_available)
            w.config(width=20)
            w.pack(side=tkinter.LEFT)
            B1 = tkinter.Button(
                popup2,
                text="Make mask",
                command=lambda: [
                    # DestroyTK(popup2),
                    Make_mask(popup2)
                ],
            )
            B1.pack()
            B2 = tkinter.Button(
                popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
            )
            B2.pack()
            popup2.mainloop()

        def PhenotypeSelectionForReal(tissue_name=[], *a):
            tissue_props = self.Tissue_props[self.activeImage]
            tissue_keys = [i for i in self.Tissue_props[self.activeImage].keys()]
            if len(tissue_name) == 0:
                tissue_name = tissue_keys[0]

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
            popup.wm_title("Tissue phenotype Selection")
            self.popup = popup
            label = ttkinter.Label(
                popup,
                text="Tissue phenotype selection for file :\n"
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
            addTissueButton = ttkinter.Button(
                toolbar, text="Add Tissue", command=addTissue
            )
            addTissueButton.pack(side=tkinter.TOP, padx=2, pady=2)
            addTissueButton.config(width=20)
            addButton = ttkinter.Button(toolbar, text="Add Phenotype", command=addPop)
            addButton.pack(side=tkinter.TOP, padx=2, pady=2)
            addButton.config(width=20)
            resetButton = ttkinter.Button(
                toolbar, text="Reset Selection", command=resetPop
            )
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
            tMaskButton = ttkinter.Button(
                toolbar, text="Make Tissue Mask", command=Define_Tissue_Phenotype_Mask
            )
            tMaskButton.pack(side=tkinter.TOP, padx=2, pady=2)
            tMaskButton.config(width=20)
            cancelButton = ttkinter.Button(toolbar, text="Quit", command=QuitPop)
            cancelButton.pack(side=tkinter.TOP, padx=2, pady=2)
            cancelButton.config(width=20)
            toolbar.pack(side=tkinter.TOP, fill=tkinter.X)

            scale_pointers = ["Linear", "Log"]
            x1_pointers = tissue_keys
            # if "Cytoplasm Area" in cell_props:
            #     x1_pointers = ['Nucleus', 'Cytoplasm', 'Cell']
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
            x_variable1.set(tissue_name)
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
            y_var_pointer1 = tkinter.OptionMenu(
                internal_windows3, x_variable1, *x1_pointers
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
            image_canvas2.get_tk_widget().pack(
                side=tkinter.TOP, expand=True, anchor="n"
            )
            image_canvas2._tkcanvas.pack(
                side=tkinter.BOTTOM, fill=tkinter.BOTH, expand=True
            )
            image_toolbar2 = NT2Tk(image_canvas2, internal_windows)
            image_toolbar2.update()
            ax2.clear()
            if x_variable2.get() == "Geometry":
                x_data = np.vstack(tissue_props[x_variable1.get()][x_variable3.get()])
            else:
                x_data = np.vstack(
                    tissue_props[x_variable1.get()]["Fluorescent " + x_variable3.get()]
                )[:, Channel_pointers.index(x_variable2.get())]
            if y_variable2.get() == "Geometry":
                y_data = np.vstack(tissue_props[x_variable1.get()][y_variable3.get()])
            else:
                y_data = np.vstack(
                    tissue_props[x_variable1.get()]["Fluorescent " + y_variable3.get()]
                )[:, Channel_pointers.index(y_variable2.get())]
            ax2.set_position([0.1, 0.1, 0.65, 0.65])
            axHistx = f2.add_axes([0.1, 0.77, 0.65, 0.15], sharex=ax2)
            axHisty = f2.add_axes([0.77, 0.1, 0.15, 0.65], sharey=ax2)
            axamp = f2.add_axes(
                [0.2, 0.95, 0.2, 0.02], facecolor="lightgoldenrodyellow"
            )
            axamp2 = f2.add_axes(
                [0.8, 0.85, 0.18, 0.15], facecolor="lightgoldenrodyellow"
            )
            axamp3 = f2.add_axes(
                [0.8, 0.75, 0.18, 0.08], facecolor="lightgoldenrodyellow"
            )
            axamp4 = f2.add_axes(
                [0.6, 0.92, 0.18, 0.08], facecolor="lightgoldenrodyellow"
            )

            axampy1 = f2.add_axes(
                [0.03, 0.1, 0.05, 0.02], facecolor="lightgoldenrodyellow"
            )
            axampy2 = f2.add_axes(
                [0.03, 0.75, 0.05, 0.02], facecolor="lightgoldenrodyellow"
            )
            axampx1 = f2.add_axes(
                [0.1, 0.03, 0.05, 0.02], facecolor="lightgoldenrodyellow"
            )
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

            cursor_on = matplotlib.widgets.RadioButtons(
                axamp3, ("cursor on", "cursor off")
            )
            show_pop_on = matplotlib.widgets.RadioButtons(
                axamp4, ("show pop", "hide pop")
            )
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
                tissue_name = self.Pheno_x_variable1.get()
                tissue_props = self.Tissue_props[self.activeImage][tissue_name]
                im_all_cells = im_analyzed[0].copy()
                im_selected_cells = np.zeros(
                    (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
                )
                im_all_cells = np.zeros(
                    (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
                )
                nucleus_centroids = np.uint32(
                    np.round(tissue_props["Centroid"][:].tolist())
                )
                for i in range(len(tissue_props["Centroid"])):
                    im_all_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
                for i in self.selected_points:
                    im_selected_cells[
                        nucleus_centroids[i][0], nucleus_centroids[i][1]
                    ] = 1
                im_selected_cells = (
                    ndi.distance_transform_edt(im_selected_cells == 0)
                    <= self.size_slider.val
                )
                im_2_display_new = self.im_2_display.copy() / 2
                im_temp = im_2_display_new[:, :, 0]
                im_temp[im_selected_cells > 0] = im_selected_cells[
                    im_selected_cells > 0
                ]
                im_all_cells[im_selected_cells > 0] = 0
                im_all_cells = (
                    ndi.distance_transform_edt(im_all_cells == 0)
                    <= self.size_slider.val
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
            self.axHisty.hist(
                y_data, bins=y_edges, orientation="horizontal", color="C0"
            )
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
                    scattered_plot = axScatter.scatter(
                        x_data[mask], y_data[mask], c="C1"
                    )
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
                tissue_props = self.Tissue_props[self.activeImage][
                    self.Pheno_x_variable1.get()
                ]
                show_data = np.array(tissue_props["Show Data"])
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
            tissue_props = self.Tissue_props[self.activeImage]
            channel_variable = self.channel_variable[self.activeImage]
            Channel_pointers = self.Channel_pointers[self.activeImage].copy()
            n_channels = self.n_channels[self.activeImage]
            x_variable0 = self.Pheno_x_variable0
            x_variable1 = self.Pheno_x_variable1
            x_variable2 = self.Pheno_x_variable2
            x_variable3 = self.Pheno_x_variable3
            y_variable0 = self.Pheno_y_variable0
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
                x_data = np.vstack(tissue_props[x_variable1.get()][x_variable3.get()])
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
                    tissue_props[x_variable1.get()]["Fluorescent " + x_variable3.get()]
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
                y_data = np.vstack(tissue_props[x_variable1.get()][y_variable3.get()])
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
                    tissue_props[x_variable1.get()]["Fluorescent " + y_variable3.get()]
                )[:, Channel_pointers.index(y_variable2.get())]
            ax2.set_xscale(x_variable0.get())
            ax2.set_yscale(y_variable0.get())
            self.x_data = x_data
            self.y_data = y_data
            update_pheno()

        def addTissue(*a):
            def AddTisSure(*a):
                tissue_keys = [i for i in self.Tissue_props[self.activeImage].keys()]
                segName = self.SegName.get()
                if segName in tissue_keys:
                    self.Pheno_x_variable1.set(segName)
                else:
                    self.popup.destroy()
                    Get_tissue_props(segName)

            def RmvTisSure(*a):
                tissue_keys = [i for i in self.Tissue_props[self.activeImage].keys()]
                segName = self.SegName.get()
                analysis_params = self.analysis_params[self.activeImage].copy()
                if segName in analysis_params["Segments"]:
                    if "Tissue_props" in analysis_params["Segments"][segName]:
                        analysis_params["Segments"][segName].pop("Tissue_props")
                        self.analysis_params[self.activeImage] = analysis_params.copy()
                if segName in tissue_keys:
                    self.Tissue_props[self.activeImage].pop(segName)
                    tissue_keys = [
                        i for i in self.Tissue_props[self.activeImage].keys()
                    ]
                    if len(tissue_keys) > 0:
                        self.popup.destroy()
                        TissuePhenotype_select()
                    else:
                        self.popup.destroy()
                        Tissue_analysis(self)
                else:
                    popupmsg("This Tissue is not in Tissue phenotyping list")

            analyze_index = [
                i for i in self.analysis_params[self.activeImage]["Segments"].keys()
            ]
            popup2 = tkinter.Tk()
            popup2.wm_title("Add Tissue")
            label = tkinter.Label(
                popup2, text="Which tissue would you like to phenotype?"
            )
            label.pack(side="top", fill="x", pady=10)
            internal_windows = tkinter.Frame(popup2, width=200, height=20)
            internal_windows.pack(side=tkinter.TOP)
            self.SegName = tkinter.StringVar(internal_windows)
            self.SegName.set(analyze_index[0])
            w = tkinter.OptionMenu(internal_windows, self.SegName, *analyze_index)
            w.config(width=20)
            w.pack(side=tkinter.LEFT)
            B0 = tkinter.Button(
                popup2,
                text="Add Tissue",
                command=lambda: [DestroyTK(popup2), AddTisSure()],
            )
            B0.pack()
            B1 = tkinter.Button(
                popup2,
                text="Remove Tissue",
                command=lambda: [DestroyTK(popup2), RmvTisSure()],
            )
            B1.pack()
            B2 = tkinter.Button(
                popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
            )
            B2.pack()
            popup2.mainloop()

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

        def axHisty_changed(*b):
            hist_limits = self.hist_spanner_limits
            a = np.array(b)
            points = np.transpose((self.x_data.ravel(), self.y_data.ravel()))
            if a[0] == a[1]:
                a[1] = np.inf
            elif a[1] > np.max(points[:, 1]):
                a[1] = np.inf
            hist_limits[:, 1] = a
            tissue_props = self.Tissue_props[self.activeImage][
                self.Pheno_x_variable1.get()
            ]
            show_data = np.array(tissue_props["Show Data"])
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
            tissue_props = self.Tissue_props[self.activeImage][
                self.Pheno_x_variable1.get()
            ]
            show_data = np.array(tissue_props["Show Data"])
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
            tissue_props = self.Tissue_props[self.activeImage][
                self.Pheno_x_variable1.get()
            ]
            show_data = np.array(tissue_props["Show Data"])
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
            tissue_props = self.Tissue_props[self.activeImage][
                self.Pheno_x_variable1.get()
            ]
            tissue_props["Show Data"] = 1
            self.Histx_spanner.active = False
            self.Histy_spanner.active = False
            self.ROIPolygon.active = False
            self.ROIPolygon._xs, self.ROIPolygon._ys = [0], [0]
            self.ROIPolygon._polygon_completed = False
            self.selected_points = []
            self.ROI_path = []
            self.ROI_verts = []
            self.hist_spanner_limits = np.array([[0, 0], [np.inf, np.inf]])
            update_pheno()
            self.Tissue_props[self.activeImage][
                self.Pheno_x_variable1.get()
            ] = tissue_props
            self.image_canvas2.draw()

        def SavePop(*a):
            popup2 = tkinter.Tk()
            popup2.wm_title("Add Phenotype")
            label = ttkinter.Label(
                popup2, text="How would you like to name the phenotype?"
            )
            label.pack(side="top", fill="x", pady=10)
            labelButton = tkinter.Entry(popup2)
            segName = self.pheno_var.get()
            if segName != "New":
                labelButton.insert(0, segName)
            self.SegName = labelButton
            labelButton.pack()
            B1 = ttkinter.Button(
                popup2, text="Okay", command=lambda: [SavePopSure(popup2)]
            )
            B1.pack()
            B2 = ttkinter.Button(
                popup2, text="Go Back", command=lambda: [DestroyTK(popup2)]
            )
            B2.pack()
            popup2.mainloop()

        def SavePopSure(popup2, *a):
            segName = self.SegName.get()
            tissue_props = self.Tissue_props[self.activeImage][
                self.Pheno_x_variable1.get()
            ]
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
                label = ttkinter.Label(
                    popup3, text="You cannot name your Phenotype All.\n"
                )
                label.pack(side="top", fill="x", pady=10)
                B2 = ttkinter.Button(
                    popup3, text="Go Back", command=lambda: [DestroyTK(popup3)]
                )
                B2.pack()
                popup3.mainloop()
            elif segName in np.unique(np.hstack(tissue_props["Phenotypes"][:])):
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
            tissue_name = self.Pheno_x_variable1.get()
            tissue_props = self.Tissue_props[self.activeImage][tissue_name]
            segName = self.SegName.get()
            im_analyzed = self.im_analyzed[self.activeImage]
            analyze_index = self.analyze_index[self.activeImage]
            im_all_cells = im_analyzed[0]
            pheno_list = tissue_props["Phenotypes"][:].tolist()
            nucleus_centroids = np.uint32(
                np.round(tissue_props["Centroid"][:].tolist())
            )
            im_selected_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            im_all_cells = np.zeros(
                (im_all_cells.shape[0], im_all_cells.shape[1]), dtype=bool
            )
            if segName in np.unique(np.hstack(pheno_list)):
                for i in pheno_list.index:
                    if segName in pheno_list[i - 1]:
                        pheno_list[i - 1].remove(segName)
            for i in self.selected_points:
                pheno_list[i].append(segName)
                im_selected_cells[nucleus_centroids[i][0], nucleus_centroids[i][1]] = 1
            tissue_props["Phenotypes"] = pheno_list
            segName = tissue_name + " - " + segName
            self.Tissue_props[self.activeImage][tissue_name] = tissue_props
            im_selected_cells = ndi.distance_transform_edt(im_selected_cells == 0) <= 5
            if (segName) in analyze_index:
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
                "y_axis1": self.Pheno_x_variable1.get(),
                "y_axis2": self.Pheno_y_variable2.get(),
                "y_axis3": self.Pheno_y_variable3.get(),
                "positive_area": self.ROI_verts.copy(),
                "hist_limits": self.hist_spanner_limits.copy(),
            }
            self.analysis_params[self.activeImage] = analysis_params.copy()

        def QuitPop(*a):
            popup2 = tkinter.Tk()
            popup2.wm_title("Are you sure?")
            label = ttkinter.Label(
                popup2, text="You are about to exit Phenotype Selection"
            )
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

        PhenotypeSelectionForReal()

    def Tissue_selection(*a):
        def AddTisSure(*a):
            segName = self.SegName.get()
            Get_tissue_props(segName)

        analyze_index = [
            i for i in self.analysis_params[self.activeImage]["Segments"].keys()
        ]
        popup2 = tkinter.Tk()
        popup2.wm_title("Add Tissue")
        label = tkinter.Label(popup2, text="Which tissue would you like to phenotype?")
        label.pack(side="top", fill="x", pady=10)
        internal_windows = tkinter.Frame(popup2, width=200, height=20)
        internal_windows.pack(side=tkinter.TOP)
        self.SegName = tkinter.StringVar(internal_windows)
        self.SegName.set(analyze_index[0])
        w = tkinter.OptionMenu(internal_windows, self.SegName, *analyze_index)
        w.config(width=20)
        w.pack(side=tkinter.LEFT)
        B0 = tkinter.Button(
            popup2, text="Add Tissue", command=lambda: [DestroyTK(popup2), AddTisSure()]
        )
        B0.pack()
        B2 = tkinter.Button(popup2, text="Go Back", command=lambda: [DestroyTK(popup2)])
        B2.pack()
        popup2.mainloop()

    if len(tissue_name) > 0:
        Get_tissue_props(tissue_name, False)
        return
    tissue_keys = [i for i in self.Tissue_props[self.activeImage].keys()]
    if len(tissue_keys) > 0:
        TissuePhenotype_select()
    elif (
        len([i for i in self.analysis_params[self.activeImage]["Segments"].keys()]) > 0
    ):
        Tissue_selection()
    else:
        popupmsg("You need a defined tissue to perform tissue phenotyping")


def NN_segmentation(self):
    def preview_changed(*a):
        model_used = model_variable.get()
        if model_used == "Stardist_2D_versatile_fluo":
            Stardist_2D_versatile_fluo(True)

    def Perform_NN(*a):
        model_used = model_variable.get()
        if model_used == "Stardist_2D_versatile_fluo":
            Stardist_2D_versatile_fluo()

    def nuc_analysis_changed(*a):
        for child in segname_window.winfo_children():
            DestroyTK(child)
        if nucleus_var.get() == 1:
            label = tkinter.Label(segname_window, text="Segment: DAPI   | ")
            label.pack(side=tkinter.LEFT)
            label = tkinter.Label(segname_window, text="Labels: Nucleus & Cells   | ")
            label.pack(side=tkinter.LEFT)
            label = tkinter.OptionMenu(
                segname_window, ExtendVar, *["Extend Cell Area To:", "Extend Cells:"]
            )
            label.pack(side=tkinter.LEFT)
            nuc_slider = Slider(segname_window, area_lim)
            nuc_slider.pack(side=tkinter.LEFT)
        else:
            label = tkinter.Label(segname_window, text="Segment:")
            label.pack(side=tkinter.LEFT)
            seg_entry = tkinter.Entry(segname_window, textvariable=segname_var)
            seg_entry.pack(side=tkinter.LEFT)
            label = tkinter.Label(segname_window, text="Label:")
            label.pack(side=tkinter.LEFT)
            label_entry = tkinter.Entry(segname_window, textvariable=labelname_var)
            label_entry.pack(side=tkinter.LEFT)

    def Stardist_2D_versatile_fluo(preview=False, *a):
        model_versatile = stardist.models.StarDist2D.from_pretrained(
            "2D_versatile_fluo"
        )
        perform_nuclei = nucleus_var.get() == 1
        if perform_nuclei:
            segName = "DAPI"
        else:
            segName = segname_var.get()
        ch_used = channel_variable.get()
        n_ch_used = channel_options.index(ch_used)
        if n_ch_used < n_channels:
            im_temp = im_raw[:, :, n_ch_used]
        else:
            im_temp = im_analyzed[n_ch_used - n_channels]
        im_temp = np.float32(im_temp)
        Fore_mask = np.ones_like(im_temp == 0)
        if "ROI" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("ROI")]
        if "Foreground" in analyze_index:
            Fore_mask = Fore_mask & im_analyzed[analyze_index.index("Foreground")]
        img = StarDist2D_normalize(im_temp, 1, 99.8, axis=(0, 1))
        probability_threshold = model_versatile.thresholds[0]
        nonmaximum_suppression = model_versatile.thresholds[1]
        try:
            probability_threshold += np.float(prob_thres_var.get())
        except ValueError:
            prob_thres_var.set(0.0)
        try:
            nonmaximum_suppression += np.float(nms_thres_var.get())
        except ValueError:
            nms_thres_var.set(0.0)
        single_cells = model_versatile.predict_instances(
            img, prob_thresh=probability_threshold, nms_thresh=nonmaximum_suppression
        )[0]
        single_cells = np.uint32(single_cells * np.float32(Fore_mask))
        single_cells = skimage.measure.label(single_cells)
        if preview:
            self.a.clear()
            self.a.imshow(img, aspect="equal", cmap="gray")
            self.a.imshow(
                single_cells,
                aspect="equal",
                cmap=stardist.random_label_cmap(),
                alpha=0.5,
            )
            self.a.autoscale(False)
            self.a.axis("off")
            self.image_canvas.draw()
            return
        mask = single_cells > 0
        if len(segName) > 0:
            if segName in analysis_params["Segments"]:
                analysis_params["Segments"].pop(segName)
            analysis_params["Segments"][segName] = {
                "thres": "Stardist_2D_versatile_fluo",
                "ch_used": ch_used,
                "n_ch_used": n_ch_used,
                "class": "Seg",
                "d_prob_thres": np.float(prob_thres_var.get()),
                "d_nms_thres": np.float(nms_thres_var.get()),
            }
            if segName in analyze_index:
                im_analyzed[analyze_index.index(segName)] = mask
            else:
                im_analyzed.append(mask)
                analyze_index.append(segName)
        if not perform_nuclei:
            label_name = labelname_var.get()
            if len(label_name) > 0:
                if label_name in analysis_params["Segments"]:
                    analysis_params["Segments"].pop(label_name)
                analysis_params["Segments"][label_name] = {
                    "thres": "Stardist_2D_versatile_fluo",
                    "ch_used": ch_used,
                    "n_ch_used": n_ch_used,
                    "class": "Label",
                    "d_prob_thres": np.float(prob_thres_var.get()),
                    "d_nms_thres": np.float(nms_thres_var.get()),
                }
                if label_name in analyze_index:
                    im_analyzed[analyze_index.index(label_name)] = single_cells
                else:
                    im_analyzed.append(single_cells)
                    analyze_index.append(label_name)
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            DestroyTK(popup)
            self.remake_side_window()
            self.RedoPhenotyping()
            return
        analysis_params["Segments"][segName]["class"] = "Nuc"
        if "Nuclei" in analyze_index:
            im_analyzed[analyze_index.index("Nuclei")] = single_cells
            self.im_analyzed[self.activeImage] = im_analyzed
        else:
            im_analyzed.append(single_cells)
            analyze_index.append("Nuclei")
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            self.remake_side_window()
        voronoi_image = skimage.segmentation.watershed(
            -ndi.distance_transform_edt(single_cells > 0), single_cells
        )
        voronoi_image = skimage.measure.label(voronoi_image)
        voronoi_image = np.uint32(voronoi_image * np.float32(Fore_mask))
        voronoi_extend = ExtendVar.get() == "Extend Cell Area To:"
        voronoi_objects = ndi.find_objects(voronoi_image)
        try:
            voronoi_limit = int(float(area_lim.get()))
        except OverflowError:
            voronoi_limit = np.inf
        except ValueError:
            voronoi_limit = np.inf
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < (np.sort(im_nuc_temp.ravel())[voronoi_limit])] = (
                    False
                )
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
                im_nuc_temp = ndi.distance_transform_edt(np.logical_not(im_nuc_temp))
                im_nuc_temp[~im_temp] = np.inf
                im_temp[im_nuc_temp < voronoi_limit] = False
                voronoi_temp = voronoi_image[s1]
                voronoi_temp[im_temp] = 0
                voronoi_image[s1] = voronoi_temp
        if "Cells" in analyze_index:
            im_analyzed[analyze_index.index("Cells")] = voronoi_image
            self.im_analyzed[self.activeImage] = im_analyzed
        else:
            im_analyzed.append(voronoi_image)
            analyze_index.append("Cells")
            self.im_analyzed[self.activeImage] = im_analyzed
            self.analyze_index[self.activeImage] = analyze_index
            self.remake_side_window()
        DestroyTK(self.popup)
        analysis_params["Segments"]["DAPI"]["NucLimits"] = "Stardist_2D_versatile_fluo"
        if "CellLimits" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("CellLimits")
        try:
            voronoi_limit = int(float(area_lim.get()))
        except OverflowError:
            voronoi_limit = np.inf
        except ValueError:
            voronoi_limit = np.inf
        analysis_params["Segments"]["DAPI"]["CellLimits"] = voronoi_limit
        if "CellMeth" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("CellMeth")
        analysis_params["Segments"]["DAPI"]["CellMeth"] = ExtendVar.get()
        if "d_prob_thres" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("d_prob_thres")
        analysis_params["Segments"]["DAPI"]["d_prob_thres"] = np.float(
            prob_thres_var.get()
        )
        if "d_nms_thres" in analysis_params["Segments"]["DAPI"]:
            analysis_params["Segments"]["DAPI"].pop("d_nms_thres")
        analysis_params["Segments"]["DAPI"]["d_nms_thres"] = np.float(
            nms_thres_var.get()
        )
        self.analysis_params[self.activeImage] = analysis_params.copy()
        self.RedoPhenotyping()

    analyze_index = self.analyze_index[self.activeImage]
    im_analyzed = self.im_analyzed[self.activeImage]
    im_raw = self.im_raw[self.activeImage]
    analysis_params = self.analysis_params[self.activeImage].copy()
    channel_options = [i for i in self.Channel_pointers[self.activeImage]]
    n_channels = self.n_channels[self.activeImage]
    for i in self.analyze_index[self.activeImage]:
        channel_options.append(i)
    model_options = ["Stardist_2D_versatile_fluo"]
    popup = tkinter.Tk()
    self.popup = popup
    popup.geometry("600x300")
    popup.wm_title("Neural Networks")
    internal_windows = tkinter.Frame(self.popup, width=200, height=20)
    internal_windows.pack(side=tkinter.TOP)

    model_variable = tkinter.StringVar(internal_windows, value=model_options[0])
    model_drop = tkinter.OptionMenu(internal_windows, model_variable, *model_options)
    segname_var = tkinter.StringVar(popup)
    labelname_var = tkinter.StringVar(popup)
    prob_thres_var = tkinter.StringVar(popup, "0.0")
    nms_thres_var = tkinter.StringVar(popup, "0.0")
    model_drop.config(width=30)
    model_drop.pack(side=tkinter.LEFT)

    channel_variable = tkinter.StringVar(internal_windows)
    if "DAPI" in channel_options:
        channel_variable.set("DAPI")
    else:
        channel_variable.set(channel_options[0])
    channel_drop = tkinter.OptionMenu(
        internal_windows, channel_variable, *channel_options
    )
    channel_drop.config(width=10)
    channel_drop.pack(side=tkinter.LEFT)

    nucleus_var = tkinter.IntVar(popup, value=1)
    check_nucleus = tkinter.Checkbutton(
        internal_windows, text="Nucleus Segmentation", variable=nucleus_var
    )
    check_nucleus.pack(side=tkinter.LEFT)
    nucleus_var.trace_variable("w", nuc_analysis_changed)

    stardist_params_window = tkinter.Frame(popup, width=100, height=20)
    stardist_params_window.pack(side=tkinter.TOP)
    label = tkinter.Label(stardist_params_window, text="Threshold:")
    label.pack(side=tkinter.LEFT)
    thres_entry = tkinter.Entry(stardist_params_window, textvariable=prob_thres_var)
    thres_entry.pack(side=tkinter.LEFT)
    label = tkinter.Label(stardist_params_window, text="non-maximum suppression:")
    label.pack(side=tkinter.LEFT)
    nms_entry = tkinter.Entry(stardist_params_window, textvariable=nms_thres_var)
    nms_entry.pack(side=tkinter.LEFT)
    segname_window = tkinter.Frame(popup, width=100, height=20)
    segname_window.pack(side=tkinter.TOP)
    label = tkinter.Label(segname_window, text="Segment: DAPI   | ")
    label.pack(side=tkinter.LEFT)
    label = tkinter.Label(segname_window, text="Labels: Nucleus & Cells   | ")
    label.pack(side=tkinter.LEFT)
    ExtendVar = tkinter.StringVar(popup)
    ExtendVar.set("Extend Cell Area To:")
    label = tkinter.OptionMenu(
        segname_window, ExtendVar, *["Extend Cell Area To:", "Extend Cells:"]
    )
    label.pack(side=tkinter.LEFT)
    area_lim = tkinter.StringVar(popup)
    nuc_slider = Slider(segname_window, area_lim)
    nuc_slider.pack(side=tkinter.LEFT)
    internal_windows = tkinter.Frame(popup, width=100, height=20)
    internal_windows.pack(side=tkinter.TOP)
    load_button = tkinter.Button(
        master=internal_windows, text="Load Model", command=self.to_be_implemented
    )
    load_button.pack(side=tkinter.LEFT)
    perform_button = tkinter.Button(
        master=internal_windows, text="Perform", command=Perform_NN
    )
    perform_button.pack(side=tkinter.LEFT)
    cancel_button = tkinter.Button(
        master=internal_windows, text="Cancel", command=lambda: [DestroyTK(popup)]
    )
    cancel_button.pack(side=tkinter.LEFT)
    preview_check = tkinter.Button(
        master=internal_windows, text="Preview", command=preview_changed
    )
    preview_check.pack(side=tkinter.LEFT)
    popup.mainloop()
