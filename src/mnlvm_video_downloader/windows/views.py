import tkinter as tk
from datetime import datetime
from multiprocessing.pool import ThreadPool
from windows.helper import open_many_file
from tkinter import Menu, messagebox
from typing import List, Tuple
from PIL import Image
import customtkinter
from utils.constants import GLIPH_ICON_SIZE, DEFAULT_WINDOW_SIZE, DATE_FORMAT, BASE_DIR

# Modes: "System" (standard), "Dark", "Light"
customtkinter.set_appearance_mode("System")
# Themes: "blue" (standard), "green", "dark-blue"
customtkinter.set_default_color_theme("green")


class Window(customtkinter.CTk):
    """Main application interface for Ekila Downloader."""

    def __init__(self, user_login: str) -> None:
        super().__init__()
        self.user_login = user_login
        self.list_file: List[str] = []
        self.is_song_loading: bool = False

        # Initialize images
        self._load_images()

        # Setup the application
        self._setup_window()
        self._create_widgets()

        # Start the date updater
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
        # self._create_button_list()
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

        # Help menu
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

        # Logo container
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

    def _create_extract_csv_panel(self) -> None:
        self.dashboard_frame = customtkinter.CTkFrame(self, corner_radius=0, width=879)
        self.dashboard_frame.grid(
            row=2, column=1, rowspan=4, columnspan=2, sticky="nsew"
        )

        self._create_dashboard_title(self.dashboard_frame, "TABLEAU DE BORD")

        # File path entry
        self.file_path = tk.StringVar()
        customtkinter.CTkLabel(
            self.dashboard_frame,
            text="Fichier csv:",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        ).grid(column=1, row=1, sticky="w", pady=15, padx=5)

        self.csv_entry = customtkinter.CTkEntry(
            self.dashboard_frame, width=500, textvariable=self.file_path
        )
        self.csv_entry.grid(column=1, row=1, sticky="w", pady=15, padx=100)

        # Text box
        self.textbox_csv = customtkinter.CTkTextbox(
            self.dashboard_frame, width=800, height=250
        )
        self.textbox_csv.grid(row=2, column=1, pady=5, sticky="nw")

        # Generate button
        self.generate_button = customtkinter.CTkButton(
            self.dashboard_frame,
            corner_radius=2,
            fg_color=("white", "#81f542"),
            border_width=0,
            text_color=("white", "#ffffff"),
            text="Generer",
            command=None,
        )
        self.generate_button.grid(row=3, column=1, pady=5, padx=5, sticky="nw")

        # Progress bar
        self.progressbar = customtkinter.CTkProgressBar(
            self.dashboard_frame,
            height=20,
            width=350,
            progress_color=("orange", "#FFA500"),
        )
        self.progressbar.grid(row=3, column=1, padx=150, sticky="nw", pady=5)
        self.progressbar.set(0)

    def _create_transfert_son_panel(self) -> None:
        self.transfert_frame = customtkinter.CTkFrame(self, corner_radius=0, width=850)
        self.transfert_frame.grid(
            row=2, column=1, rowspan=4, columnspan=3, sticky="nsew"
        )
        self.transfert_frame.columnconfigure(0, weight=1)
        self.transfert_frame.columnconfigure(1, weight=1)

        self._create_dashboard_title(self.transfert_frame, "TABLEAU DE BORD")

        self.scrollable_sons_frame = customtkinter.CTkScrollableFrame(
            self.transfert_frame,
            label_text="Liste des sons",
            height=250,
        )
        self.scrollable_sons_frame.grid(row=1, column=1, sticky=tk.W + tk.E, pady=15)
        self.scrollable_sons_frame.grid_columnconfigure(0, weight=1)

        self.scrollable_sons_list = customtkinter.CTkScrollableFrame(
            self.transfert_frame,
            label_text="Liste des playlists",
            height=250,
        )
        self.scrollable_sons_list.grid(row=1, column=2, pady=15, sticky=tk.W + tk.E)
        self.scrollable_sons_list.grid_columnconfigure(0, weight=1)

        self.button_frame = customtkinter.CTkFrame(
            self.transfert_frame, corner_radius=0
        )
        self.button_frame.grid(row=2, column=1, sticky="w")
        self.button_frame.columnconfigure(0, weight=1)
        self.button_frame.columnconfigure(1, weight=1)
        self.button_frame.columnconfigure(2, weight=1)

        self.transfert_button = customtkinter.CTkButton(
            self.button_frame,
            text="Transférer",
            command=None,
        )
        self.supprimer_button = customtkinter.CTkButton(
            self.button_frame, text="Supprimer", command=None
        )
        self.progressbar = customtkinter.CTkProgressBar(
            self.button_frame,
            height=30,
            width=350,
            progress_color=("orange", "#FFA500"),
        )

        self.transfert_button.grid(row=0, column=0, sticky=tk.W + tk.E)
        self.supprimer_button.grid(row=0, column=1, sticky=tk.W + tk.E, padx=3)
        self.progressbar.grid(row=0, column=2, sticky=tk.W + tk.E, padx=3)
        self.progressbar.set(0)

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

        # Text box
        self.textbox = customtkinter.CTkTextbox(
            self.download_frame, width=800, height=250
        )
        self.textbox.grid(row=2, column=1, pady=5, sticky="nw")

        # Download button
        self.download_sons_button = customtkinter.CTkButton(
            self.download_frame,
            corner_radius=15,
            fg_color=("white", "#81f542"),
            border_width=2,
            text_color=("white", "#ffffff"),
            text="Télécharger",
            command=None,
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

    def _create_conversion_son_panel(self) -> None:
        self.conversion_frame = customtkinter.CTkFrame(self, corner_radius=0, width=850)
        self.conversion_frame.grid(
            row=2, column=1, rowspan=4, columnspan=3, sticky="nsew"
        )

        self._create_dashboard_title(self.conversion_frame, "TABLEAU DE BORD")

        customtkinter.CTkLabel(
            self.conversion_frame,
            text="sons mp3:",
            font=customtkinter.CTkFont(size=15, weight="bold"),
        ).grid(column=1, row=1, sticky="w", pady=15, padx=5)

        self.convert_entry = tk.StringVar()
        self.son_path_entry = customtkinter.CTkEntry(
            self.conversion_frame, width=500, textvariable=self.convert_entry
        )
        self.son_path_entry.grid(column=1, row=1, sticky="nsew", pady=15, padx=100)

        # Text box
        self.textbox = customtkinter.CTkTextbox(
            self.conversion_frame, width=800, height=250
        )
        self.textbox.grid(row=2, column=1, pady=5, sticky="nw")

        # Menu button frame
        self.menu_button = customtkinter.CTkFrame(
            self.conversion_frame, corner_radius=0
        )
        self.menu_button.grid(row=3, column=1, pady=5, sticky="nw")
        self.menu_button.columnconfigure(0, weight=1)
        self.menu_button.columnconfigure(1, weight=1)
        self.menu_button.columnconfigure(2, weight=1)

        # Buttons
        self.metadata_button = customtkinter.CTkButton(
            self.menu_button,
            corner_radius=15,
            fg_color=("white", "#81f542"),
            border_width=2,
            text_color=("white", "#ffffff"),
            text="Metadata",
            command=None,
        )

        self.convert_sons_button = customtkinter.CTkButton(
            self.menu_button,
            corner_radius=15,
            fg_color=("white", "#81f542"),
            border_width=2,
            text_color=("white", "#ffffff"),
            text="Convertir en wav",
            command=None,
        )

        self.progressbar = customtkinter.CTkProgressBar(
            self.menu_button, height=30, width=350, progress_color=("orange", "#FFA500")
        )

        self.metadata_button.grid(row=0, column=0, sticky=tk.W + tk.E, padx=10)
        self.convert_sons_button.grid(row=0, column=1, sticky=tk.W + tk.E, padx=10)
        self.progressbar.grid(row=0, column=2, sticky=tk.W + tk.E)
        self.progressbar.set(0)

    # def _create_button_list(self) -> None:
    #     self.button_frame = customtkinter.CTkFrame(self, corner_radius=0)
    #     self.button_frame.grid(row=6, column=1, sticky="w")

    #     for i in range(5):
    #         self.button_frame.columnconfigure(i, weight=1)

    #     buttons = [
    #         # ("Télécharger", self.download_image, "Télécharger"),
    #         ("Quitter", self.quit_image, self.quit),
    #     ]

    #     for i, (text, image, command) in enumerate(buttons):
    #         btn = customtkinter.CTkButton(
    #             self.button_frame,
    #             corner_radius=10,
    #             text_color=("black", "#000000"),
    #             text=text,
    #             image=image,
    #             fg_color=("white", "white"),
    #             height=60,
    #             font=customtkinter.CTkFont(size=12, weight="bold"),
    #             command=command
    #             if callable(command)
    #             else lambda cmd=command: self._paginate(cmd),
    #         )
    #         btn.grid(row=0, column=i, sticky=tk.W + tk.E, padx=3)

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

    def _paginate(self, page: str) -> None:
        for child in self.button_frame.winfo_children():
            if isinstance(child, customtkinter.CTkButton):
                child.configure(fg_color=("white", "white"))

        # if page == "Transfert":
        #     self._create_transfert_son_panel()
        #     self.button_frame.winfo_children()[1].configure(fg_color=("green", "green"))
        if page == "Télécharger":
            self._create_download_son_panel()
            self.button_frame.winfo_children()[2].configure(fg_color=("green", "green"))
        # elif page == "Recherche":
        #     self._create_extract_csv_panel()
        #     self.button_frame.winfo_children()[0].configure(fg_color=("green", "green"))

    def _download_songs(self, link: str) -> None:
        with ThreadPool() as pool:
            pool.apply_async(lambda: None)

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


if __name__ == "__main__":
    print(BASE_DIR)
    app = Window("Anonymous user")
    app.mainloop()
