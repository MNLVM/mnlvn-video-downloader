import tkinter as tk
import asyncio
from datetime import datetime
from windows.helper import open_many_file
from tkinter import Menu, messagebox
from typing import List, Tuple
from PIL import Image
import customtkinter
from utils.constants import GLIPH_ICON_SIZE, DEFAULT_WINDOW_SIZE, DATE_FORMAT, BASE_DIR
from controllers.video import YouTubeDownloaderController

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("green")


class Window(customtkinter.CTk):
    def __init__(
        self, yt_controler: YouTubeDownloaderController, user_login: str = "Anonymous"
    ) -> None:
        super().__init__()
        self.user_login = user_login
        self.list_file: List[str] = []
        self.is_song_loading: bool = False
        self.yt_controler = yt_controler

        self._load_images()

        self._setup_window()
        self._create_widgets()

        self._update_date()

    def _load_images(self) -> None:
        self.logo = self._create_image(
            str(BASE_DIR) + "\windows\images\logos.png", (270, 145)
        )
        self.logo_welcome = self._create_image(
            str(BASE_DIR) + "\windows\images\ekila-downaudio.jpg", (859, 145)
        )

        self.search_image = self._create_image(
            str(BASE_DIR) + "\windows\images\search.png", GLIPH_ICON_SIZE
        )
        self.download_image = self._create_image(
            str(BASE_DIR) + "\windows\images\download.png", GLIPH_ICON_SIZE
        )
        self.quit_image = self._create_image(
            str(BASE_DIR) + "\windows\images\quitter.png", GLIPH_ICON_SIZE
        )

    def set_path_file(self) -> None:
        path, _ = open_many_file()
        if self.link_entry:
            if self.link_entry.get() != "":
                self.link_entry.delete(0, tk.END)
            self.link_entry.insert(0, str(path))

    def _create_image(self, path: str, size: Tuple[int, int]) -> customtkinter.CTkImage:
        return customtkinter.CTkImage(Image.open(path), size=size)

    def _setup_window(self) -> None:
        self.title("MNLVM Video Downloader")
        self.geometry(DEFAULT_WINDOW_SIZE)
        self.resizable(False, False)
        self.grid_rowconfigure(6, weight=2)
        self.columnconfigure(0, weight=0)

    def _create_widgets(self) -> None:
        self._create_menu_bar()
        self._create_header()
        self._create_sidebar()
        self._create_download_son_panel()
        self._create_footer()

    def change_appearance_mode_event(self, new_appearance_mode: str) -> None:
        mode_mapping = {
            "Mode clair": "Light",
            "Mode sombre": "Dark",
            "Mode système": "System",
        }
        customtkinter.set_appearance_mode(
            mode_mapping.get(new_appearance_mode, new_appearance_mode)
        )

    def change_scaling_event(self, new_scaling: str) -> None:
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def _update_date(self) -> None:
        self.date_label.configure(text=datetime.today().strftime(DATE_FORMAT))
        self.after(200, self._update_date)

    def _create_menu_bar(self) -> None:
        menu_bar = Menu(self)
        self.config(menu=menu_bar)

        menu_file = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Fichier", menu=menu_file)
        menu_file.add_command(label="Ouvrir un fichier csv", command=self.set_path_file)
        menu_file.add_command(label="Vider", command=None)
        menu_file.add_command(label="Quitter", command=self.quit)

        menu_help = Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Aide", menu=menu_help)
        menu_help.add_command(label="A propos", command=self._show_about)

    def _create_header(self) -> None:
        self.user_label = customtkinter.CTkLabel(master=self, text=f"{self.user_login}")
        self.user_label.grid(row=0, column=0, sticky="nw", padx=2)
        self.date_label = customtkinter.CTkLabel(
            master=self, text=datetime.today().strftime(DATE_FORMAT)
        )
        self.date_label.grid(row=0, column=1, padx=90, sticky="e")

        self.logo_container = customtkinter.CTkFrame(self, corner_radius=0, width=1129)
        self.logo_container.grid(row=1, column=0, columnspan=2, sticky="nsew")

        self.logo_label = customtkinter.CTkLabel(
            self.logo_container, text="", height=145, image=self.logo, width=270
        )
        self.logo_label.grid(row=1, column=0)

        self.panel_logo_label = customtkinter.CTkLabel(
            self.logo_container, text="", width=859, height=145, image=self.logo_welcome
        )
        self.panel_logo_label.grid(row=1, column=2)

    def _create_sidebar(self) -> None:
        self.sidebar_frame = customtkinter.CTkFrame(
            self, corner_radius=0, width=250, height=420
        )
        self.sidebar_frame.grid(row=2, column=0, sticky="w")

        self.tabview = customtkinter.CTkTabview(self.sidebar_frame, width=250)
        self.tabview.grid(row=2, column=0, padx=10)
        self.tabview.add("Actualités")
        self.tabview.add("Communiqués")

        self.appearance_mode_label = customtkinter.CTkLabel(
            self.sidebar_frame, text="Appearance Mode:", anchor="w"
        )
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))

        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(
            self.sidebar_frame,
            values=["Mode clair", "Mode sombre", "Mode système"],
            command=self.change_appearance_mode_event,
        )
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))

    def _create_download_son_panel(self) -> None:
        self.down_path = tk.StringVar()
        self.download_frame = customtkinter.CTkFrame(self, corner_radius=0, width=850)
        self.download_frame.grid(
            row=2, column=1, rowspan=4, columnspan=3, sticky="nsew"
        )
        self._create_dashboard_title(self.download_frame, "TABLEAU DE BORD")

        customtkinter.CTkLabel(
            self.download_frame,
            font=customtkinter.CTkFont(size=15, weight="bold"),
            text="Fichier csv:",
        ).grid(column=1, row=1, sticky="w", pady=15, padx=5)

        self.link_entry = customtkinter.CTkEntry(
            self.download_frame, width=500, textvariable=self.down_path
        )
        self.link_entry.grid(column=1, row=1, sticky="nsew", pady=15, padx=100)

        self.textbox = customtkinter.CTkTextbox(
            self.download_frame, width=800, height=250
        )
        self.textbox.grid(row=2, column=1, pady=5, sticky="nw")

        self.download_sons_button = customtkinter.CTkButton(
            self.download_frame,
            corner_radius=15,
            fg_color=("white", "#81f542"),
            border_width=2,
            text_color=("white", "#ffffff"),
            text="Télécharger",
            command=lambda: asyncio.run(
                (self.yt_controler._download(self.down_path.get()))
            ),
        )
        self.download_sons_button.grid(row=3, column=1, pady=5, sticky="nw")

        self.download_progressbar = customtkinter.CTkProgressBar(
            self.download_frame,
            height=30,
            width=350,
            progress_color=("orange", "#FFA500"),
        )
        self.download_progressbar.grid(row=3, column=1, padx=150, pady=5, sticky="nw")
        self.download_progressbar.set(0)

    def _create_dashboard_title(
        self, frame: customtkinter.CTkFrame, title: str
    ) -> None:
        title_label = customtkinter.CTkLabel(
            frame,
            text=title,
            font=customtkinter.CTkFont(size=20, weight="bold"),
        )
        title_label.grid(row=0, column=1, pady=10, sticky="news")

    def _create_footer(self) -> None:
        self.footer_frame = customtkinter.CTkFrame(self)
        self.footer_frame.grid(row=9, column=1, sticky="nsew")

        self.footer_label = customtkinter.CTkLabel(
            self.footer_frame,
            text="Copyright © MNLV Africa Sarl Tous droits réservés",
            font=customtkinter.CTkFont(size=8, weight="bold"),
        )
        self.footer_label.grid(row=0, column=1, columnspan=2, sticky="e", padx=300)

    def _show_about(self) -> None:
        messagebox.showinfo(
            title="A propos",
            message="Ekila Downloader v0.1, copyright MNLV Africa \n Droits réservés",
        )

    def quit(self) -> None:
        if messagebox.askyesno(
            title="Exit", message="Etes vous sur de vouloir quitter?"
        ):
            self.destroy()
