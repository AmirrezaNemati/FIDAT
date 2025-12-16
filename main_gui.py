from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTabWidget, QPushButton, QLineEdit, QLabel,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QGridLayout,
    QGroupBox, QRadioButton, QFileDialog, QMessageBox, QAbstractItemView,
    QSizePolicy, QAction, QMenuBar, QTextBrowser, QSpacerItem, QApplication
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QIcon
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import scipy as sp

from calculations import Calculations
from plotting import Plotting
import os
from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QHeaderView
from PyQt5.QtCore import Qt, QTimer
import os
import threading
from PyQt5 import QtGui
from PyQt5 import QtWidgets




class SurfaceIrrigationSystemDesign(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set Window Icon
        self.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))

        self.setWindowTitle('Furrow Irrigation Design and Assessment Tool (FIDAT)')
        self.resize(850, 630)

        font = QFont("Arial", 10)
        self.setFont(font)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.tab_widget = QTabWidget()
        self.tab1 = QWidget()
        self.tab5 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()

        self.tab_widget.addTab(self.tab1, "Data")
        self.tab_widget.addTab(self.tab5, "Parameters Estimation")
        self.tab_widget.addTab(self.tab2, "Exist Condition")
        self.tab_widget.addTab(self.tab3, "Optimized Condition")
        self.tab_widget.addTab(self.tab4, "Optimization table")

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setSpacing(5)

        self.setup_tab1()
        self.setup_tab2()
        self.setup_tab3()
        self.setup_tab4()
        self.setup_tab5()

        self.calculations = Calculations(self)
        self.plotting = Plotting(self)

        self.setup_menu()

        self.about_widget = None

    def setup_menu(self):
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # About Action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about_dialog)
        menu_bar.addAction(about_action)

        # Help Action
        help_action = QAction("Help", self)
        help_action.triggered.connect(self.open_help_pdf)
        menu_bar.addAction(help_action)

    def show_about_dialog(self):
        # نمایش Splash Screen
        pixmap__ = QtGui.QPixmap("resources/icons/loading.png")
        splash = QtWidgets.QSplashScreen(pixmap__)
        splash.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
        splash.show()
        QtWidgets.QApplication.processEvents()  # به‌روزرسانی فوری رابط کاربری

        if not hasattr(self, "about_widget") or not self.about_widget:
            self.about_widget = QWidget()
            self.about_widget.setWindowTitle("About")
            self.about_widget.resize(586, 570)

            icon = QIcon("resources/icons/furrow_icon.ico")
            self.about_widget.setWindowIcon(icon)

            layout = QVBoxLayout(self.about_widget)
            horizontal_layout = QHBoxLayout()

            left_spacer = QLabel()

            logo = QLabel()
            pixmap = QPixmap("resources/images/furrow_irrigation__.jpg")
            # تنظیم اندازه QLabel
            logo.setFixedSize(900, 232)  # اندازه دلخواه (عرض، ارتفاع)
            # مقیاس‌دهی تصویر برای تطبیق با QLabel
            logo.setPixmap(pixmap.scaled(logo.size(), Qt.KeepAspectRatio))
            logo.setScaledContents(True)  # فعال کردن مقیاس‌دهی محتوای QLabel

            right_spacer = QLabel()

            horizontal_layout.addWidget(left_spacer)
            horizontal_layout.addWidget(logo)
            horizontal_layout.addWidget(right_spacer)

            layout.addLayout(horizontal_layout)

            text_browser = QTextBrowser()
            # محتوای HTML
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #f5f7fa;
                        text-align: center;
                        margin: 0;
                        padding: 0;
                    }
                    .container {
                        border-radius: 10px;
                        margin: 20px auto;
                        padding: 20px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                        max-width: 600px;
                    }
                    h1 {
                        color: #1a5f7a;
                        font-size: 24px;
                        margin-bottom: 20px;
                    }
                    h2 {
                        color: #2980b9;
                        font-size: 20px;
                        margin-top: 30px;
                    }
                    p {
                        color: #34495e;
                        font-size: 14px;
                        line-height: 1.6;
                    }
                    .soft-text {
                        color: #7f8c8d;
                        font-size: 12px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>Furrow Irrigation Design and Assessment Tool (FIDAT) - Version 1.0</h1>
                    <p>This software provides comprehensive analysis of field conditions, calculating irrigation efficiency and assisting in the design of optimized furrow irrigation systems.</p>
                    <h2>Developer</h2>
                    <p>Amirreza Nemati Mansour</p>
                    <p>amirreza.nemati@ut.ac.ir</p>
                    <h2>Supervisor</h2>
                    <p>Majid Raoof</p>
                    <p>majidraoof2000gmail.com</p>
                    <h2>Initiated and Developed at</h2>
                    <p>Mohaghegh Ardabili University</p>
                </div>
            </body>
            </html>
            """
            # تنظیم محتوای HTML در QTextBrowser
            text_browser.setHtml(html_content)
            layout.addWidget(text_browser)

        self.about_widget.show()
        splash.close()
        self.about_widget.raise_()

    def setup_tab1(self):
        self.tab1_layout = QGridLayout()
        self.tab1.setLayout(self.tab1_layout)
        self.tab1_layout.setContentsMargins(10, 10, 10, 10)
        self.tab1_layout.setSpacing(10)

        # Buttons
        self.input_data_button = QPushButton('Input data')
        self.clear_data_button = QPushButton('Clear data')
        self.calc_data_button = QPushButton('Calculate')
        self.calc_data_button.setEnabled(False)

        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.addWidget(self.input_data_button)
        self.buttons_layout.addWidget(self.clear_data_button)
        self.buttons_layout.addWidget(self.calc_data_button)
        self.buttons_layout.addStretch(1)  # Spacer

        # Input fields and labels
        self.label_n = QLabel("Manning's roughness coefficient :")
        self.inputN_data = QLineEdit('0')
        self.label_S = QLabel('Longitudinal slope of the furrow(m/m) :')
        self.inputS_data = QLineEdit('0')
        self.label_Q = QLabel('Furrow inflow rate(m3/min) :')
        self.inputQ_data = QLineEdit('0')
        self.label_W = QLabel('Furrow width(m) :')
        self.inputW_data = QLineEdit('0')
        self.label_I = QLabel('Net irrigation requirement(cm) :')
        self.inputI_data = QLineEdit('0')

        self.inputs_layout = QGridLayout()
        self.inputs_layout.addWidget(self.label_n, 0, 0)
        self.inputs_layout.addWidget(self.inputN_data, 0, 1)
        self.inputs_layout.addWidget(self.label_S, 1, 0)
        self.inputs_layout.addWidget(self.inputS_data, 1, 1)
        self.inputs_layout.addWidget(self.label_W, 0, 2)
        self.inputs_layout.addWidget(self.inputW_data, 0, 3)
        self.inputs_layout.addWidget(self.label_I, 1, 2)
        self.inputs_layout.addWidget(self.inputI_data, 1, 3)
        self.inputs_layout.addWidget(self.label_Q, 2, 0)
        self.inputs_layout.addWidget(self.inputQ_data, 2, 1)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Infiltration duration(min)', 'cumulative infiltration(cm)', 'Furrow length(m)', 'Advance time(min)', 'Recession time(min)'])
        self.table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)


        # Radio buttons
        self.radio_group = QGroupBox('Infiltration Equations')
        self.radio_layout = QHBoxLayout()
        self.radio_kostiakovlewis = QRadioButton('Kostiakov-Lewis')
        self.radio_kostiakov = QRadioButton('Kostiakov')
        self.radio_philip = QRadioButton('Philip')
        self.radio_scs = QRadioButton('SCS')
        self.radio_layout.addWidget(self.radio_kostiakovlewis)
        self.radio_layout.addWidget(self.radio_kostiakov)
        self.radio_layout.addWidget(self.radio_philip)
        self.radio_layout.addWidget(self.radio_scs)
        self.radio_kostiakovlewis.setChecked(True)
        self.radio_group.setLayout(self.radio_layout)

        self.tab1_layout.addLayout(self.buttons_layout, 0, 0, 3, 1)
        self.tab1_layout.addLayout(self.inputs_layout, 0, 1, 1, 4)
        self.tab1_layout.addWidget(self.table, 2, 0, 1, 5)
        self.tab1_layout.addWidget(self.radio_group, 1, 0,1,5)

        # Connect signals
        self.input_data_button.clicked.connect(self.input_data_clicked)
        self.clear_data_button.clicked.connect(self.clear_data_clicked)
        self.calc_data_button.clicked.connect(self.calc_data_clicked)

    def setup_tab2(self):
        self.tab2_layout = QGridLayout()
        self.tab2.setLayout(self.tab2_layout)
        self.tab2_layout.setContentsMargins(10,10,10,10)
        self.tab2_layout.setSpacing(10)

        # Edit Boxes and Labels
        self.editBox_Vn = QLineEdit('0')
        self.editBox_Vn.setReadOnly(True)
        self.editBox_Vdp = QLineEdit('0')
        self.editBox_Vdp.setReadOnly(True)
        self.editBox_Vin = QLineEdit('0')
        self.editBox_Vin.setReadOnly(True)
        self.editBox_Vr = QLineEdit('0')
        self.editBox_Vr.setReadOnly(True)
        self.editBox_Cu = QLineEdit('0')
        self.editBox_Cu.setReadOnly(True)
        self.editBox_Ae = QLineEdit('0')
        self.editBox_Ae.setReadOnly(True)
        self.editBox_Twr = QLineEdit('0')
        self.editBox_Twr.setReadOnly(True)
        self.editBox_Dpr = QLineEdit('0')
        self.editBox_Dpr.setReadOnly(True)
        self.editBox_tco = QLineEdit('0')

        self.label_Vn = QLabel('Vn :')
        self.label_Vdp = QLabel('Vdp :')
        self.label_Vin = QLabel('Vin :')
        self.label_Vr = QLabel('Vr :')
        self.label_Cu = QLabel('CU :')
        self.label_Ae = QLabel('AE :')
        self.label_Twr = QLabel('TWR :')
        self.label_Dpr = QLabel('DPR :')
        self.label_tco = QLabel('Tco :')

        # Arrange in grid
        self.tab2_layout.addWidget(self.label_Vn, 0, 0)
        self.tab2_layout.addWidget(self.editBox_Vn, 0, 1)
        self.tab2_layout.addWidget(self.label_Cu, 0, 2)
        self.tab2_layout.addWidget(self.editBox_Cu, 0, 3)
        self.tab2_layout.addWidget(self.label_Vdp, 1, 0)
        self.tab2_layout.addWidget(self.editBox_Vdp, 1, 1)
        self.tab2_layout.addWidget(self.label_Ae, 1, 2)
        self.tab2_layout.addWidget(self.editBox_Ae, 1, 3)
        self.tab2_layout.addWidget(self.label_Vin, 2, 0)
        self.tab2_layout.addWidget(self.editBox_Vin, 2, 1)
        self.tab2_layout.addWidget(self.label_Twr, 2, 2)
        self.tab2_layout.addWidget(self.editBox_Twr, 2, 3)
        self.tab2_layout.addWidget(self.label_Vr, 3, 0)
        self.tab2_layout.addWidget(self.editBox_Vr, 3, 1)
        self.tab2_layout.addWidget(self.label_Dpr, 3, 2)
        self.tab2_layout.addWidget(self.editBox_Dpr, 3, 3)
        self.tab2_layout.addWidget(self.label_tco,4,0)
        self.tab2_layout.addWidget(self.editBox_tco,4,1)

        

        # Plot area
        self.figure_tab2 = plt.figure()
        self.canvas_tab2 = FigureCanvas(self.figure_tab2)

        # دکمه ذخیره نمودار
        self.save_fig2_button = QPushButton("Save Figure")
        self.save_fig2_button.clicked.connect(lambda: self.save_figure(self.figure_tab2))

        # Layout for plot and button
        plot_layout = QVBoxLayout()
        plot_layout.addWidget(self.canvas_tab2)
        plot_layout.addWidget(self.save_fig2_button, alignment=Qt.AlignRight)

        self.tab2_layout.addLayout(plot_layout, 5, 0, 1, 4)

    def setup_tab3(self):
        self.tab3_layout = QGridLayout()
        self.tab3.setLayout(self.tab3_layout)
        self.tab3_layout.setContentsMargins(10,10,10,10)
        self.tab3_layout.setSpacing(10)

        # Edit Boxes
        self.editBox_Vn2 = QLineEdit('0')
        self.editBox_Vn2.setReadOnly(True)
        self.editBox_Vdp2 = QLineEdit('0')
        self.editBox_Vdp2.setReadOnly(True)
        self.editBox_Vin2 = QLineEdit('0')
        self.editBox_Vin2.setReadOnly(True)
        self.editBox_Vr2 = QLineEdit('0')
        self.editBox_Vr2.setReadOnly(True)
        self.editBox_Cu2 = QLineEdit('0')
        self.editBox_Cu2.setReadOnly(True)
        self.editBox_Ae2 = QLineEdit('0')
        self.editBox_Ae2.setReadOnly(True)
        self.editBox_Twr2 = QLineEdit('0')
        self.editBox_Twr2.setReadOnly(True)
        self.editBox_Dpr2 = QLineEdit('0')
        self.editBox_Dpr2.setReadOnly(True)
        self.editBox_Tco = QLineEdit('0')
        self.editBox_Tco.setReadOnly(True)

        # Labels
        self.label_Vn2 = QLabel('Vn :')
        self.label_Vdp2 = QLabel('Vdp :')
        self.label_Vin2 = QLabel('Vin :')
        self.label_Vr2 = QLabel('Vr :')
        self.label_Cu2 = QLabel('CU :')
        self.label_Ae2 = QLabel('AE :')
        self.label_Twr2 = QLabel('TWR :')
        self.label_Dpr2 = QLabel('DPR :')
        self.label_Tco = QLabel('Tco:')

        # Arrange in grid
        self.tab3_layout.addWidget(self.label_Vn2, 0, 0)
        self.tab3_layout.addWidget(self.editBox_Vn2, 0, 1)
        self.tab3_layout.addWidget(self.label_Cu2, 0, 2)
        self.tab3_layout.addWidget(self.editBox_Cu2, 0, 3)
        self.tab3_layout.addWidget(self.label_Vdp2, 1, 0)
        self.tab3_layout.addWidget(self.editBox_Vdp2, 1, 1)
        self.tab3_layout.addWidget(self.label_Ae2, 1, 2)
        self.tab3_layout.addWidget(self.editBox_Ae2, 1, 3)
        self.tab3_layout.addWidget(self.label_Vin2, 2, 0)
        self.tab3_layout.addWidget(self.editBox_Vin2, 2, 1)
        self.tab3_layout.addWidget(self.label_Twr2, 2, 2)
        self.tab3_layout.addWidget(self.editBox_Twr2, 2, 3)
        self.tab3_layout.addWidget(self.label_Vr2, 3, 0)
        self.tab3_layout.addWidget(self.editBox_Vr2, 3, 1)
        self.tab3_layout.addWidget(self.label_Dpr2, 3, 2)
        self.tab3_layout.addWidget(self.editBox_Dpr2, 3, 3)
        self.tab3_layout.addWidget(self.label_Tco,4,0)
        self.tab3_layout.addWidget(self.editBox_Tco,4,1)

        # Optimal Furrow Length
        self.length_optim_label = QLabel('')
        self.length_optim_value = QLabel('')
        self.length_optim_unit = QLabel('')
        self.tab3_layout.addWidget(self.length_optim_label, 4, 3)
        self.tab3_layout.addWidget(self.length_optim_value, 4, 3)
        self.tab3_layout.addWidget(self.length_optim_unit, 4, 3)

        # Plots
        self.figure_AE_tab3 = plt.figure()
        self.canvas_AE_tab3 = FigureCanvas(self.figure_AE_tab3)
        self.figure_CU_tab3 = plt.figure()
        self.canvas_CU_tab3 = FigureCanvas(self.figure_CU_tab3)
        self.figure_TWR_tab3 = plt.figure()
        self.canvas_TWR_tab3 = FigureCanvas(self.figure_TWR_tab3)
        

        # Save buttons for plots
        self.save_figAE_button = QPushButton("Save AE Figure")
        self.save_figAE_button.clicked.connect(lambda: self.save_figure(self.figure_AE_tab3))

        self.save_figCU_button = QPushButton("Save CU Figure")
        self.save_figCU_button.clicked.connect(lambda: self.save_figure(self.figure_CU_tab3))

        self.save_figTWR_button = QPushButton("Save TWR Figure")
        self.save_figTWR_button.clicked.connect(lambda: self.save_figure(self.figure_TWR_tab3))

        # Layouts for plots
        plots_layout_top = QHBoxLayout()
        layout_ae = QVBoxLayout()
        layout_ae.addWidget(self.canvas_AE_tab3)
        layout_ae.addWidget(self.save_figAE_button, alignment=Qt.AlignRight)

        layout_cu = QVBoxLayout()
        layout_cu.addWidget(self.canvas_CU_tab3)
        layout_cu.addWidget(self.save_figCU_button, alignment=Qt.AlignRight)

        plots_layout_top.addLayout(layout_ae)
        plots_layout_top.addLayout(layout_cu)

        plots_layout_bottom = QVBoxLayout()
        plots_layout_bottom.addWidget(self.canvas_TWR_tab3)
        plots_layout_bottom.addWidget(self.save_figTWR_button, alignment=Qt.AlignRight)

        self.tab3_layout.addLayout(plots_layout_top, 5, 0, 1, 4)
        self.tab3_layout.addLayout(plots_layout_bottom, 6, 0, 1, 4)

    def setup_tab4(self):
        self.tab4_layout = QVBoxLayout()
        self.tab4.setLayout(self.tab4_layout)
        self.tab4_layout.setContentsMargins(10,10,10,10)
        self.tab4_layout.setSpacing(10)

        # Output data button
        self.output_data_button = QPushButton('Output data')
        self.output_data_button.setEnabled(False)
        self.table1 = QTableWidget()
        self.table1.setColumnCount(9)
        self.table1.setHorizontalHeaderLabels(['X (m)', 'Vn (m3)', 'Vdp (m3)', 'Vin (m3)', 'Vr (m3)', 'CU (%)', 'AE (%)', 'TWR (%)', 'DPR (%)'])
        self.table1.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        header = self.table1.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)

        self.tab4_layout.addWidget(self.output_data_button)
        self.tab4_layout.addWidget(self.table1)
        self.output_data_button.clicked.connect(self.output_data_clicked)

    def setup_tab5(self):
        self.tab5_layout = QGridLayout()
        self.tab5.setLayout(self.tab5_layout)
        self.tab5_layout.setContentsMargins(10, 10, 10, 10)
        self.tab5_layout.setSpacing(10)

        # Main parameter P
        self.label_P = QLabel('P :')
        self.inputP_data = QLineEdit('0')
        self.inputP_data.setReadOnly(True)

        self.p_layout = QHBoxLayout()
        self.p_layout.addWidget(self.label_P)
        self.p_layout.addWidget(self.inputP_data)
        self.p_layout.setSpacing(2)

        self.tab5_layout.addLayout(self.p_layout, 0, 0, 1, 2)

        # Kostiakov-Lewis
        self.group_kostiakovlewis = QGroupBox('Kostiakov-Lewis')
        self.group_kostiakovlewis.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
        self.koslew_layout = QGridLayout()
        self.koslew_c_label = QLabel('c :')
        self.koslew_c_edit = QLineEdit('0')
        self.koslew_c_edit.setReadOnly(True)
        self.koslew_a_label = QLabel('a :')
        self.koslew_a_edit = QLineEdit('0')
        self.koslew_a_edit.setReadOnly(True)
        self.koslew_f_label = QLabel('f :')
        self.koslew_f_edit = QLineEdit('0')
        self.koslew_f_edit.setReadOnly(True)
        self.koslew_layout.addWidget(self.koslew_c_label, 0, 0)
        self.koslew_layout.addWidget(self.koslew_c_edit, 0, 1)
        self.koslew_layout.addWidget(self.koslew_a_label, 1, 0)
        self.koslew_layout.addWidget(self.koslew_a_edit, 1, 1)
        self.koslew_layout.addWidget(self.koslew_f_label, 2, 0)
        self.koslew_layout.addWidget(self.koslew_f_edit, 2, 1)
        self.group_kostiakovlewis.setLayout(self.koslew_layout)

        # Kostiakov
        self.group_kostiakov = QGroupBox('Kostiakov')
        self.group_kostiakov.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
        self.kos_layout = QGridLayout()
        self.kos_c_label = QLabel('c :')
        self.kos_c_edit = QLineEdit('0')
        self.kos_c_edit.setReadOnly(True)
        self.kos_a_label = QLabel('a :')
        self.kos_a_edit = QLineEdit('0')
        self.kos_a_edit.setReadOnly(True)
        self.kos_layout.addWidget(self.kos_c_label, 0, 0)
        self.kos_layout.addWidget(self.kos_c_edit, 0, 1)
        self.kos_layout.addWidget(self.kos_a_label, 1, 0)
        self.kos_layout.addWidget(self.kos_a_edit, 1, 1)
        self.group_kostiakov.setLayout(self.kos_layout)

        # Philip
        self.group_philip = QGroupBox('Philip')
        self.group_philip.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
        self.philip_layout = QGridLayout()
        self.philip_s_label = QLabel('S :')
        self.philip_s_edit = QLineEdit('0')
        self.philip_s_edit.setReadOnly(True)
        self.philip_A_label = QLabel('A :')
        self.philip_A_edit = QLineEdit('0')
        self.philip_A_edit.setReadOnly(True)
        self.philip_layout.addWidget(self.philip_s_label, 0, 0)
        self.philip_layout.addWidget(self.philip_s_edit, 0, 1)
        self.philip_layout.addWidget(self.philip_A_label, 1, 0)
        self.philip_layout.addWidget(self.philip_A_edit, 1, 1)
        self.group_philip.setLayout(self.philip_layout)

        # SCS
        self.group_scs = QGroupBox('SCS')
        self.group_scs.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
        self.scs_layout = QGridLayout()
        self.scs_a_label = QLabel('a :')
        self.scs_a_edit = QLineEdit('0')
        self.scs_a_edit.setReadOnly(True)
        self.scs_b_label = QLabel('b :')
        self.scs_b_edit = QLineEdit('0')
        self.scs_b_edit.setReadOnly(True)
        self.scs_c_label = QLabel('c :')
        self.scs_c_edit = QLineEdit('0')
        self.scs_c_edit.setReadOnly(True)
        self.scs_layout.addWidget(self.scs_a_label, 0, 0)
        self.scs_layout.addWidget(self.scs_a_edit, 0, 1)
        self.scs_layout.addWidget(self.scs_b_label, 1, 0)
        self.scs_layout.addWidget(self.scs_b_edit, 1, 1)
        self.scs_layout.addWidget(self.scs_c_label, 2, 0)
        self.scs_layout.addWidget(self.scs_c_edit, 2, 1)
        self.group_scs.setLayout(self.scs_layout)

        self.tab5_layout.addWidget(self.group_kostiakovlewis, 1, 0)
        self.tab5_layout.addWidget(self.group_kostiakov, 1, 1)
        self.tab5_layout.addWidget(self.group_philip, 2, 0)
        self.tab5_layout.addWidget(self.group_scs, 2, 1)

        # Error Metrics (Model Error)
        self.group_model_error = QGroupBox('Model Error')
        self.group_model_error.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
        self.error_layout = QGridLayout()
        self.label_Re = QLabel('RE :')
        self.editBox_Re = QLineEdit('0')
        self.editBox_Re.setReadOnly(True)
        self.label_Rmse = QLabel('RMSE :')
        self.editBox_Rmse = QLineEdit('0')
        self.editBox_Rmse.setReadOnly(True)
        self.error_layout.addWidget(self.label_Re, 0, 0)
        self.error_layout.addWidget(self.editBox_Re, 0, 1)
        self.error_layout.addWidget(self.label_Rmse, 1, 0)
        self.error_layout.addWidget(self.editBox_Rmse, 1, 1)
        self.group_model_error.setLayout(self.error_layout)


        self.text_Atn = QLabel('')
        self.text_Atn.setAlignment(Qt.AlignCenter)
        self.error_layout.addWidget(self.text_Atn, 2, 1, 1, 1)


        # Walker Method
        self.group_walker_method = QGroupBox('Walker Method')
        self.group_walker_method.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
        self.walker_layout = QGridLayout()
        self.label_P_walker = QLabel('P :')
        self.editBox_P_walker = QLineEdit('0')
        self.editBox_P_walker.setReadOnly(True)
        self.label_R_walker = QLabel('R :')
        self.editBox_R_walker = QLineEdit('0')
        self.editBox_R_walker.setReadOnly(True)
        self.label_p_walker = QLabel("P' :")
        self.editBox_p_walker = QLineEdit('0')
        self.editBox_p_walker.setReadOnly(True)
        self.label_r_walker = QLabel("R' :")
        self.editBox_r_walker = QLineEdit('0')
        self.editBox_r_walker.setReadOnly(True)
        self.walker_layout.addWidget(self.label_P_walker, 0, 0)
        self.walker_layout.addWidget(self.editBox_P_walker, 0, 1)
        self.walker_layout.addWidget(self.label_R_walker, 1, 0)
        self.walker_layout.addWidget(self.editBox_R_walker, 1, 1)
        self.walker_layout.addWidget(self.label_p_walker, 2, 0)
        self.walker_layout.addWidget(self.editBox_p_walker, 2, 1)
        self.walker_layout.addWidget(self.label_r_walker, 3, 0)
        self.walker_layout.addWidget(self.editBox_r_walker, 3, 1)
        self.group_walker_method.setLayout(self.walker_layout)

        # Add to layout
        self.tab5_layout.addWidget(self.group_model_error, 3, 0)
        self.tab5_layout.addWidget(self.group_walker_method, 3, 1)

    def input_data_clicked(self):
        n_data = float(self.inputN_data.text())
        s_data = float(self.inputS_data.text())
        q_data1 = float(self.inputQ_data.text())
        W = float(self.inputW_data.text())
        I_Inff = float(self.inputI_data.text())
        if n_data == 0 or s_data == 0 or q_data1 == 0 or W == 0 or I_Inff == 0:
            QMessageBox.critical(self, 'Attention', 'Please determine the variables.')
            return
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getOpenFileName(
            self, "Select file to Read", "", "Text Files (*.txt *.dat *.TXT);;Excel Files (*.xls *.xlsx *.csv)", options=options)
        if filename:
            try:
                import pandas as pd
                if filename.lower().endswith(('.xls', '.xlsx')):
                    data = pd.read_excel(filename, header=None).values
                elif filename.lower().endswith('.csv'):
                    data = pd.read_csv(filename, header=None).values
                else:
                    data = np.loadtxt(filename)
                # Set data into the table
                self.table.setRowCount(data.shape[0])
                self.table.setColumnCount(data.shape[1])
                for i in range(data.shape[0]):
                    for j in range(data.shape[1]):
                        item = QTableWidgetItem(str(data[i, j]))
                        self.table.setItem(i, j, item)
                # Enable 'Calculate' button if data is loaded and inputs are valid
                if n_data > 0 and s_data > 0 and q_data1 > 0 and W > 0 and I_Inff > 0:
                    self.calc_data_button.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load data: {str(e)}')

    def clear_data_clicked(self):
        self.table.setRowCount(0)
        self.inputN_data.setText('0')
        self.inputP_data.setText('0')
        self.inputQ_data.setText('0')
        self.inputW_data.setText('0')
        self.inputI_data.setText('0')
        self.inputS_data.setText('0')
        # Clear tab2
        self.editBox_Vn.setText('0')
        self.editBox_Vdp.setText('0')
        self.editBox_Vin.setText('0')
        self.editBox_Vr.setText('0')
        self.editBox_Cu.setText('0')
        self.editBox_Ae.setText('0')
        self.editBox_Twr.setText('0')
        self.editBox_Dpr.setText('0')
        self.text_Atn.setText('')
        self.figure_tab2.clear()
        self.canvas_tab2.draw()
        # Clear tab3
        self.editBox_Vn2.setText('0')
        self.editBox_Vdp2.setText('0')
        self.editBox_Vin2.setText('0')
        self.editBox_Vr2.setText('0')
        self.editBox_Cu2.setText('0')
        self.editBox_Ae2.setText('0')
        self.editBox_Twr2.setText('0')
        self.editBox_Dpr2.setText('0')
        self.editBox_Tco.setText('0')
        self.editBox_P_walker.setText('0')
        self.editBox_R_walker.setText('0')
        self.editBox_p_walker.setText('0')
        self.editBox_r_walker.setText('0')
        self.length_optim_label.setText('')
        self.length_optim_value.setText('')
        self.length_optim_unit.setText('')
        self.figure_AE_tab3.clear()
        self.canvas_AE_tab3.draw()
        self.figure_CU_tab3.clear()
        self.canvas_CU_tab3.draw()
        self.figure_TWR_tab3.clear()
        self.canvas_TWR_tab3.draw()
        # Clear tab4
        self.calc_data_button.setEnabled(False)
        self.output_data_button.setEnabled(False)
        self.table1.setRowCount(0)
        # Clear tab5
        self.inputP_data.setText('0')
        self.koslew_c_edit.setText('0')
        self.koslew_a_edit.setText('0')
        self.koslew_f_edit.setText('0')
        self.kos_c_edit.setText('0')
        self.kos_a_edit.setText('0')
        self.philip_s_edit.setText('0')
        self.philip_A_edit.setText('0')
        self.scs_a_edit.setText('0')
        self.scs_b_edit.setText('0')
        self.scs_c_edit.setText('0')
        self.editBox_Re.setText('0')
        self.editBox_Rmse.setText('0')
        QMessageBox.information(self, 'Message', 'Data cleared.')

    def calc_data_clicked(self):
        self.calculations.perform_calculations()
        # پس از رسم نمودار، از tight_layout استفاده می‌کنیم
        for fig in [self.figure_tab2, self.figure_AE_tab3, self.figure_CU_tab3, self.figure_TWR_tab3]:
            fig.tight_layout()
        self.canvas_tab2.draw()
        self.canvas_AE_tab3.draw()
        self.canvas_CU_tab3.draw()
        self.canvas_TWR_tab3.draw()

    def output_data_clicked(self):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Select file to Save", "", "CSV Files (*.csv)", options=options)
        if filename:
            data = self.calculations.optimization_output
            try:
                import pandas as pd
                df = pd.DataFrame(data, columns=['X', 'Vn', 'Vdp', 'Vin', 'Vr', 'CU', 'AE', 'TWR', 'DPR'])
                if filename.lower().endswith('.csv'):
                    df.to_csv(filename, index=False)
                QMessageBox.information(self, 'Success', 'Data saved successfully.')
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save data: {str(e)}')

    def save_figure(self, figure):
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(
            self, "Save Figure", "", "PNG Files (*.png);;JPEG Files (*.jpg *.jpeg);;PDF Files (*.pdf);;All Files (*)", options=options)
        if filename:
            figure.savefig(filename, dpi=400)
            QMessageBox.information(self, 'Success', 'Figure saved successfully.')

    def open_help_pdf(self):
        # مسیر فایل PDF
        pdf_path = r"resources\pdf_help\English.pdf"

        if os.path.exists(pdf_path):
            # نمایش Splash Screen
            pixmap__ = QtGui.QPixmap("resources/icons/loading.png")
            splash = QtWidgets.QSplashScreen(pixmap__)
            splash.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
            splash.show()
            QtWidgets.QApplication.processEvents()

            def open_pdf():
                try:
                    os.startfile(pdf_path)
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Unable to open the help file: {e}")
                finally:
                    splash.close()

            threading.Thread(target=open_pdf, daemon=True).start()

        else:
            QMessageBox.critical(self, "Error", "Help file not found.")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("resources/icons/furrow_icon.ico"))
    window = SurfaceIrrigationSystemDesign()
    window.show()
    sys.exit(app.exec_())
