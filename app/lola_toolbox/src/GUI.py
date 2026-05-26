#!/usr/bin/env python3

import os
import tempfile
from pathlib import Path
import webbrowser

import FreeSimpleGUI as sg

from src import main
from src import archive
from src import crypto
from src import connection

LOLA_TOOLBOX_VERSION = "1.2.2"

class Window:
    """
    Window object used to create the GUI
    The constructor hold information to build the window
    use the method start() to start the GUI
    """

    def __init__(self):
        self.font = "Arial 14"
        sg.theme("DarkAmber")
        self.layout_lines = [
            [
                sg.Text("Select a Bordereau file", size=(25, 1)),
                sg.InputText(),
                sg.FileBrowse(
                    file_types=(("All files", "*"),), key="bordereau_path_file"
                ),
            ],
            [
                sg.Text("Select a Dataset", size=(25, 1)),
                sg.InputText(),
                sg.FileBrowse(
                    file_types=(("All files", "*"),), key="dataset_path_file"
                ),
            ],
            [
                sg.Text("Where to store encrypted file", size=(25, 1)),
                sg.InputText(),
                sg.FileSaveAs(
                    file_types=(("All files", "*.*"),), key="output_encrypted_path_file"
                ),
            ],
        ]
        self.layout_center_lines = [
            [
                sg.Text(
                    text="", size=(100, 1), justification="center", key="progress_step"
                )
            ],
            [sg.ProgressBar(100, orientation="h", size=(200, 20), key="progress")],
            [
                sg.Button("Encrypt", key="Button-encrypt"),
                sg.Button(
                    "Transfer to Lola-platform",
                    key="Button-transfer",
                    disabled=True,
                    tooltip="Encrypt before to enable the option",
                ),
            ],
        ]

        self.layout_transfert_files = [
            [
                sg.Text("Select a file(s)"),
                sg.Button(
                    "Select multiples files", key="Button-select_files_transfert"
                ),
            ],
            [
                sg.Text("Where to store encrypted file", size=(25, 1)),
                sg.InputText(),
                sg.FileSaveAs(
                    file_types=(("All files", "*.*"),),
                    key="output_encrypted_path_file_transfert",
                ),
            ],
            [
                sg.Text("Selected file. Total: 0 file", key="Total-files"),
                sg.Listbox(values=[], size=(80, 5), key="-FILELIST-"),
            ],
        ]
        self.layout_transfert_buttons = [
            [
                sg.Text(
                    text="",
                    size=(100, 1),
                    justification="center",
                    key="progress_step_transfert",
                )
            ],
            [
                sg.ProgressBar(
                    100, orientation="h", size=(200, 20), key="progress_bar_transfert"
                )
            ],
            [
                sg.Button("Encrypt", key="Button-encrypt_transfert"),
                sg.Button(
                    "Transfer to Lola-platform",
                    key="Button-transfer_transfert",
                    tooltip="Encrypt before to enable the option",
                    disabled=True,
                ),
            ],
        ]

        self.tab_about_layout = [
            [
                sg.Text(text=f"Lola Toolbox version {LOLA_TOOLBOX_VERSION}"),
                sg.Image(filename=str(Path(main.GetPath.get(Path("img/lola_toolbox-icon_64px.png"))))),
            ],
            [
                sg.Text(text="Contact:"),
                sg.Text(
                    text="mailto:philippe.noel@loria.fr",
                    text_color="lightblue",
                    enable_events=True,
                    key="-OPENLINK-mail",
                ),
            ],
            [
                sg.Text(text="Gitlab:"),
                sg.Text(
                    text=" https://gitlab.inria.fr/lola/lola_toolbox",
                    text_color="lightblue",
                    enable_events=True,
                    key="-OPENLINK-gitlab",
                ),
            ],
            [
                sg.Text(text="Releases:"),
                sg.Text(
                    text=" https://gitlab.inria.fr/lola/lola_toolbox/-/releases",
                    text_color="lightblue",
                    enable_events=True,
                    key="-OPENLINK-gitlab-releases",
                ),
            ],
        ]

        self.tab_xapi_layout = [
            [sg.Column(self.layout_lines, element_justification="left")],
            [sg.Column(self.layout_center_lines, element_justification="center")],
        ]
        self.tab_transfert_layout = [
            [sg.Column(self.layout_transfert_files, element_justification="left")],
            [sg.Column(self.layout_transfert_buttons, element_justification="center")],
        ]
        self.layout = [
            [
                sg.TabGroup(
                    [
                        [
                            sg.Tab("Xapi File", self.tab_xapi_layout),
                            sg.Tab("Regular Files", self.tab_transfert_layout),
                            sg.Tab("About", self.tab_about_layout),
                        ]
                    ]
                )
            ],
            [
                sg.Text(
                    f"Lola Toolbox version {LOLA_TOOLBOX_VERSION}", 
                    size=(80, 1), 
                    key="LOLA-TOOLBOX-VERSION-MESSAGE",
                    justification="right",
                    expand_x=True
                )
            ],
        ]

    def start(self):
        # Create the Window
        self.window = sg.Window(
            "Prepare Data",
            self.layout,
            size=(800, 450),
            font=self.font,
            resizable=True,
            finalize=True,
        )
        # Set cursors
        self.set_cursors()

        checked_version = False
        # Event Loop to process "events" and get the "values" of the inputs
        while True:
            self.event, self.values = self.window.read(timeout=100)
            if self.event == "Button-encrypt":
                self.encrypt_event(
                    progress_bar_tag="progress",
                    output="output_encrypted_path_file",
                    progress_step_tag="progress_step",
                    transfer_to_sftp_button_tag="Button-transfer",
                    bordereau="bordereau_path_file",
                    dataset="dataset_path_file",
                    filetype="xapi",
                )

            if self.event == "Button-transfer":
                self.transfert_event("progress_step")

            if self.event == sg.WIN_CLOSED or self.event is None:
                break

            ## Transfert tab
            if self.event == "Button-select_files_transfert":
                lst_files = self.select_multiple_files()
                self.window["-FILELIST-"].update(lst_files)
                if len(lst_files) > 1:
                    string = f"Selected files. Total: {len(lst_files)} files"
                else:
                    string = f"Selected file. Total: {len(lst_files)} file"
                self.window["Total-files"].update(string)

            if self.event == "Button-encrypt_transfert":
                lst_files = self.window["-FILELIST-"].get_list_values()
                if self.values["output_encrypted_path_file_transfert"] == "":
                    sg.popup_error("Please select an output path for the encrypted file", font=self.font)
                    continue
                self.encrypt_event(
                    progress_bar_tag="progress_bar_transfert",
                    progress_step_tag="progress_step_transfert",
                    transfer_to_sftp_button_tag="Button-transfer_transfert",
                    output="output_encrypted_path_file_transfert",
                    multiples_files=lst_files,
                    filetype="file",
                )

            if self.event and self.event.startswith("-OPENLINK-"):
                webbrowser.open(self.window[self.event].get())

            if checked_version is False:
                try:
                    latest_version = connection.Releases.get_latest_version()
                    checked_version = True
                    if latest_version:
                        if latest_version > LOLA_TOOLBOX_VERSION:
                            self.window["LOLA-TOOLBOX-VERSION-MESSAGE"].update(
                                f"New version {latest_version} available. Go to the Release page in the 'About' tab."
                            )
                except Exception as e:
                    # If version check fails, just mark it as checked and continue
                    checked_version = True
                    print(f"Could not check for updates: {e}")

        self.window.close()

    def select_multiple_files(self):
        """
        Open a popup to select multiple files.

        Return the list of files selected
        """
        files_as_str = sg.popup_get_file(
            "You can select multiple files with shift + click",
            multiple_files=True,
            font=self.font,
        )
        # Handle case where user cancels file selection
        if not files_as_str:
            return []
        lst_files = [Path(f) for f in files_as_str.split(";")]
        return lst_files

    def compress(self, lst_files):
        """
        Event to compress files. Return the path of the
        compressed file.

        :param lst_files: List of files to compress
        :type lst_files: list
        :return: the path of the compressed file
        :rtype: str
        """
        _, tmp_zippath = tempfile.mkstemp()
        tmp_zippath = Path(tmp_zippath)
        archive.compress(output_archive=tmp_zippath, lst_files=lst_files)
        return tmp_zippath

    def transfert_event(self, tag_status_bar):
        progress_status = self.window[tag_status_bar]
        progress_status.update(
            f"Uploading {self.output_file} file to sftp Lola server"
        )
        try:
            my_sftp = connection.sftp()
            my_sftp.init_connection()
            my_sftp.put(self.output_file, callback=self.update_progress_bar)
            progress_status.update("Upload complete!")
            sg.popup("Upload successful!", font=self.font)
        except Exception as e:
            progress_status.update("Upload failed!")
            sg.popup_error(f"Upload failed: {e}", font=self.font)

    def encrypt_event(
        self,
        progress_bar_tag: str,
        progress_step_tag: str,
        output: str,
        filetype: str,
        transfer_to_sftp_button_tag: str,
        multiples_files: list = None,
        dataset: str = None,
        bordereau: str = None,
    ):
        # get sg object
        progression_step = self.window[progress_step_tag]
        progress_bar = self.window[progress_bar_tag]

        try:
            if not multiples_files:
                dataset = Path(self.values[dataset])
                bordereau = Path(self.values[bordereau])
                
                # Validate files exist
                if not dataset.exists():
                    sg.popup_error(f"Dataset file not found: {dataset}", font=self.font)
                    return
                if not bordereau.exists():
                    sg.popup_error(f"Bordereau file not found: {bordereau}", font=self.font)
                    return
                    
                multiples_files = [dataset, bordereau]

            self.output_file = Path(self.values[output])

            # First step: compression
            progression_step.update("Compressing")
            progress_bar.update(current_count=0)
            zipfile = self.compress(multiples_files)
            progress_bar.update(current_count=50)

            # Second step: Crypting
            progression_step.update("Crypting")
            crypto.encrypt_file(zipfile, self.output_file, filetype)
            progress_bar.update(current_count=100)
            progression_step.update("")
            
            if self.output_file.is_file():
                progression_step.update(f"DONE. {self.output_file} file generated")
                self.window[transfer_to_sftp_button_tag].update(disabled=False)
                sg.popup(f"Encryption successful!\nFile saved to: {self.output_file}", font=self.font)
            else:
                sg.popup_error("Encryption failed - output file not created", font=self.font)
                
            # Clean up temporary file
            if zipfile.exists():
                os.remove(zipfile)
                
        except Exception as e:
            progression_step.update(f"Error: {str(e)}")
            sg.popup_error(f"Encryption failed: {e}", font=self.font)
            progress_bar.update(current_count=0)

    def update_progress_bar(self, current, end):
        progress_bar = self.window["progress"]
        if end > 0:
            percent = (current * 100) / end
            progress_bar.update(current_count=percent)

    def set_cursors(self):
        """
        Set cursors for links
        """
        # Get list of event
        lst_links = [
            self.window.element_list()[ii].Key
            for ii in range(len(self.window.element_list()))
            if str(self.window.element_list()[ii].Key).startswith("-OPENLINK-")
        ]
        for ii in lst_links:
            self.window[ii].set_cursor(cursor="hand2")