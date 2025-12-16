import numpy as np
import pandas as pd
from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from scipy.optimize import fsolve
from scipy.optimize import curve_fit



class Calculations:
    def __init__(self, gui):
        self.gui = gui
        self.optimization_output = None

    def perform_calculations(self):
        total_data = self.get_table_data()

        # دریافت ورودی‌ها
        n_date = float(self.gui.inputN_data.text())
        s_date = float(self.gui.inputS_data.text())
        q_date1 = float(self.gui.inputQ_data.text())
        q_date = q_date1 * (100 / 6)
        W = float(self.gui.inputW_data.text())
        I_Inff = float(self.gui.inputI_data.text())

        # محاسبه P_date
        P_date = (0.265 * ((q_date * n_date) / np.sqrt(s_date)) ** 0.425) + 0.227
        self.gui.inputP_data.setText(f'{round(P_date,2)} (m)')
        P_W = P_date / W

        # تبدیل داده‌ها به آرایه numpy
        total_data = np.array(total_data)
        t_data = total_data[:, 0]
        I_data = total_data[:, 1]
        X_data = total_data[:, 2]
        Ta_data = total_data[:, 3]
        Tr_data = total_data[:, 4]

        # انتخاب معادله نفوذ
        infiltration_type, params, Tn_prime, Ie = self.select_infiltration_equation(
            t_data, I_data, I_Inff, P_W
        )

        # محاسبه شاخص‌های خطا
        self.calculate_error_metrics(I_data, Ie)

        # ارزیابی دقت مدل بر اساس RE

        RE = self.re
        self.evaluate_model(RE)

        # حذف داده‌هایی که X_data = -1
        valid_indices = X_data != -1
        X_data = X_data[valid_indices]
        Ta_data = Ta_data[valid_indices]
        Tr_data = Tr_data[valid_indices]

        # محاسبات کارایی آبیاری
        Tr_prime = Tr_data - Tr_data[0]
        AI = 100  # مقدار پیش‌فرض AI از کد اصلی

        Tco, Tn, I_In = self.calculate_infiltration_depth(
            infiltration_type, params, P_W, W, I_Inff, AI, X_data, Ta_data, Tr_prime, Tn_prime, q_date1
        )

        # محاسبه حجم‌ها و شاخص‌ها
        Vn, Vdp, Vin, Vr, Cu, Ae, Twr, Dpr = self.calculate_volumes_and_indices(
            infiltration_type, params, P_W, W, I_Inff, AI, X_data, Tco, Tn, I_In, q_date1
        )

        # نمایش نتایج در فیلدهای رابط کاربری
        self.display_results(Vn, Vdp, Vin, Vr, Cu, Ae, Twr, Dpr,Tco)

        # رسم نمودار عمق نفوذ
        self.plot_infiltration_depth(X_data, I_In, I_Inff)

        # روش Walker
        p, r, p_prime, r_prime = self.walker_method(X_data, Ta_data, Tr_prime)

        # محاسبات جهت بهینه‌سازی طول جوی
        self.optimize_furrow_length(
            infiltration_type, params, P_W, W, I_Inff, AI, q_date1, Tn_prime, p, r, p_prime, r_prime, RE
        )

    def get_table_data(self):
        row_count = self.gui.table.rowCount()
        col_count = self.gui.table.columnCount()
        data = []
        for i in range(row_count):
            row = []
            for j in range(col_count):
                item = self.gui.table.item(i, j)
                val = float(item.text()) if (item and item.text() != '') else 0.0
                row.append(val)
            data.append(row)
        return data

    def calculate_error_metrics(self, I_data, Ie):
        Im_Ie = np.abs(I_data - Ie)
        Im_Ie_power = Im_Ie ** 2
        Im_Ie_power_counter = len(Im_Ie_power)
        Im_Ie_sum = np.sum(Im_Ie)
        Im_Ie_power_sum = np.sum(Im_Ie_power)
        I_sum = np.sum(I_data)

        RE = (Im_Ie_sum / I_sum) * 100 if I_sum != 0 else 0
        RMSE = np.sqrt(Im_Ie_power_sum / Im_Ie_power_counter) if Im_Ie_power_counter != 0 else 0

        self.re = RE
        self.gui.editBox_Re.setText(f'{round(RE,2)} (%)')
        self.gui.editBox_Rmse.setText(str(round(RMSE,2)))

    def evaluate_model(self, RE):
        if RE < 10:
            self.gui.text_Atn.setText('Model is very good')
            self.gui.text_Atn.setStyleSheet("""
                    background-color: lightgreen;
                    color: green;
                    border: 2px solid green;
                    padding: 5px;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 5px;                        
                """)
        elif 10 <= RE < 15:
            self.gui.text_Atn.setText('Model is good')
            self.gui.text_Atn.setStyleSheet("""
                    background-color: lightblue;
                    color: blue;
                    border: 2px solid blue;
                    padding: 5px;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 5px;                        
                """)
        elif 15 <= RE < 20:
            self.gui.text_Atn.setText('Model is acceptable')
            self.gui.text_Atn.setStyleSheet("""
                    background-color: lightyellow;
                    color: orange;
                    border: 2px solid orange;
                    padding: 5px;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 5px;                        
                """)
        else:
            self.gui.text_Atn.setText('Model is poor')
            self.gui.text_Atn.setStyleSheet("color: red; background-color: pink;")
            self.gui.text_Atn.setStyleSheet("""
                    background-color: pink;
                    color: red;
                    border: 2px solid red;
                    padding: 5px;
                    font-weight: bold;
                    font-size: 18px;
                    border-radius: 5px;                        
                """) 

    def select_infiltration_equation(self, t_data, I_data, I_Inff, P_W):
        """بر اساس انتخاب کاربر، نوع معادله نفوذ را تعیین کرده و پارامترهای آن را محاسبه می‌کند."""
        if self.gui.radio_scs.isChecked():
            infiltration_type = 'SCS'
            # SCS مدل
            a, b, c, Tn_prime, Ie = self.calc_scs_params(t_data, I_data, I_Inff, P_W)
            params = (a, b, c)
            self.gui.scs_a_edit.setText(str(round(a,2)))
            self.gui.scs_b_edit.setText(str(round(b,2)))
            self.gui.scs_c_edit.setText(str(round(c,2)))

        elif self.gui.radio_philip.isChecked():
            infiltration_type = 'PHILIP'
            S, A, Tn_prime, Ie = self.calc_philip_params(t_data, I_data, I_Inff, P_W)
            params = (S, A)
            self.gui.philip_s_edit.setText(str(round(S,2)))
            self.gui.philip_A_edit.setText(str(round(A,2)))

        elif self.gui.radio_kostiakov.isChecked():
            infiltration_type = 'KOSTIAKOV'
            C, a, Tn_prime, Ie = self.calc_kostiakov_params(t_data, I_data, I_Inff, P_W)
            params = (C, a)
            self.gui.kos_c_edit.setText(str(round(C,2)))
            self.gui.kos_a_edit.setText(str(round(a,2)))

        elif self.gui.radio_kostiakovlewis.isChecked():
            infiltration_type = 'KOSTIAKOVLEWIS'
            a, b, f0, Tn_prime, Ie = self.calc_kostiakovlewis_params(t_data, I_data, I_Inff, P_W)
            params = (a, b, f0)
            self.gui.koslew_a_edit.setText(str(round(a,2)))
            self.gui.koslew_c_edit.setText(str(round(b,2)))
            self.gui.koslew_f_edit.setText(str(round(f0,2)))

        else:
            QMessageBox.warning(self.gui, 'Error', 'Please select an infiltration equation.')
            raise ValueError("No infiltration equation selected.")

        return infiltration_type, params, Tn_prime, Ie

    def calc_scs_params(self, t_data, I_data, I_Inff, P_W):
        t_data1 = t_data[1:]
        I_data1 = I_data[1:]
        I_C = I_data1 - 0.7
        valid_indices = I_C > 0
        I_C = I_C[valid_indices]
        t_data1 = t_data1[valid_indices]

        log_I_C = np.log10(I_C)
        log_t_data = np.log10(t_data1)
        slope, intercept = np.polyfit(log_t_data, log_I_C, 1)

        b = slope
        a = 10 ** intercept
        c = 0.7

        Tn_prime = ((I_Inff / P_W - c) / a) ** (1 / b)
        Ie = (a * t_data ** b) + c
        return a, b, c, Tn_prime, Ie

    def calc_philip_params(self, t_data, I_data, I_Inff, P_W):
        t_step = np.diff(t_data)
        I_step = np.diff(I_data)
        i = I_step / t_step
        sqrt_tData = 1 / np.sqrt(t_data[1:])
        slope, intercept = np.polyfit(sqrt_tData, i, 1)

        S = 2 * slope
        A = intercept

        def func(t):
            return (S * np.sqrt(t) + A * t) * P_W - I_Inff

        Tn_prime = fsolve(func, x0=1)[0]
        Ie = S * np.sqrt(t_data) + A * t_data
        return S, A, Tn_prime, Ie

    def calc_kostiakov_params(self, t_data, I_data, I_Inff, P_W):
        t_data1 = t_data[1:]
        I_data1 = I_data[1:]
        log_t = np.log10(t_data1)
        log_I = np.log10(I_data1)

        slope, intercept = np.polyfit(log_t, log_I, 1)
        a = slope
        C = 10 ** intercept

        Tn_prime = ((I_Inff / P_W) / C) ** (1 / a)
        t_data_safe = np.where(t_data <= 0, 1e-6, t_data)
        Ie = C * t_data_safe ** a
        return C, a, Tn_prime, Ie

    def calc_kostiakovlewis_params(self, t_data, I_data, I_Inff, P_W):
        # I_step = np.diff(I_data)
        # t_step = np.diff(t_data)
        # i = I_step / t_step

        # f0 = np.min(i)
        # i_f0 = i - f0
        # valid_indices = i_f0 > 0
        # i_f0 = i_f0[valid_indices]
        # t_data1 = t_data[1:][valid_indices]

        # log_t = np.log10(t_data1)
        # log_i_f0 = np.log10(i_f0)
        # slope, intercept = np.polyfit(log_t, log_i_f0, 1)
        # b = slope + 1
        # a = (10 ** intercept) / b

        # def func(t):
        #     return (a * t ** b + f0 * t) * P_W - I_Inff

        # Tn_prime = fsolve(func, x0=1)[0]
        # t_data_safe = np.where(t_data <= 0, 1e-6, t_data)
        # Ie = a * t_data_safe ** b + f0 * t_data_safe
        # return a, b, f0, Tn_prime, Ie


       
        # تبدیل داده‌های ورودی به آرایه‌های NumPy
        t_data = np.array(t_data, dtype=float)
        I_data = np.array(I_data, dtype=float)

        # ایجاد نسخه‌های کپی از داده‌ها برای جایگزینی مقادیر صفر
        t_data_safe = np.copy(t_data)
        I_data_safe = np.copy(I_data)

        # جایگزینی مقادیر غیرمثبت در t_data با یک مقدار کوچک مثبت
        t_data_safe[t_data_safe <= 0] = 1e-6

        # تعریف تابع نفوذ کوستیاکوف-لوئیس
        def kostiakov_lewis(t, a, b, f0):
            return a * t**b + f0 * t

        # برازش منحنی برای یافتن پارامترهای a، b و f0
        popt, _ = curve_fit(kostiakov_lewis, t_data_safe, I_data_safe, bounds=(0, np.inf))
        a, b, f0 = popt

        # تعریف تابع برای محاسبه Tn_prime
        def func(t):
            return (a * t**b + f0 * t) * P_W - I_Inff

        # یافتن Tn_prime با استفاده از fsolve
        Tn_prime = fsolve(func, x0=1)[0]

        # محاسبه نفوذ تجمعی براساس پارامترهای به‌دست‌آمده
        Ie = kostiakov_lewis(t_data_safe, a, b, f0)

        return a, b, f0, Tn_prime, Ie

    def calculate_infiltration_depth(self, infiltration_type, params, P_W, W, I_Inff, AI, X_data, Ta_data, Tr_prime, Tn_prime, q_date1):
        # محاسبه اندیس AI
        index_AII = np.max(X_data) * (AI / 100)
        desired_index = np.ceil(index_AII)
        index_AI = (X_data == desired_index)

        if not np.any(index_AI):
            QMessageBox.critical(self.gui, 'Error', 'Index for AI not found. Check input data.')
            raise ValueError("Index for AI not found.")

        Ta_index = Ta_data[index_AI][0]
        Tr_prime_index = Tr_prime[index_AI][0]

        Tco = Ta_index + Tn_prime - Tr_prime_index
        Tn = Tco - Ta_data + Tr_prime
        Tn[Tn < 0] = 0

        # محاسبه عمق نفوذ (I_In)
        I_In = self.compute_infiltration_in(Tn, infiltration_type, params, P_W)
        return Tco, Tn, I_In

    def compute_infiltration_in(self, Tn, infiltration_type, params, P_W):
        if infiltration_type == 'SCS':
            a, b, c = params
            return ((a * Tn ** b) + c) * P_W
        elif infiltration_type == 'PHILIP':
            S, A = params
            return (S * np.sqrt(Tn) + A * Tn) * P_W
        elif infiltration_type == 'KOSTIAKOV':
            C, a = params
            return (C * Tn ** a) * P_W
        elif infiltration_type == 'KOSTIAKOVLEWIS':
            a, b, f0 = params
            return (a * Tn ** b + f0 * Tn) * P_W
        else:
            raise ValueError("Invalid infiltration type.")

    def calculate_volumes_and_indices(self, infiltration_type, params, P_W, W, I_Inff, AI, X_data, Tco, Tn, I_In, q_date1):
        # محاسبه پارامترها
        I_prev = I_In[:-1]
        I_curr = I_In[1:]
        ΔX = np.diff(X_data)
        # محاسبه Vi
        Vi = ((I_prev + I_curr) / 2) * ΔX * W / 100
        I_In1 = I_curr

        V_I = np.sum(Vi)
        Amir = I_In1 <= I_Inff
        Vi_sum = Vi[Amir]

        if AI == 100:
            Vn = X_data[-1] * (I_Inff / 100) * W
        else:
            Vn = (X_data[-1] * AI / 100) * (I_Inff / 100) * W + np.sum(Vi_sum)
        Vn = max(Vn, 0)

        Vdp = max(V_I - Vn, 0)
        Vin = max(Tco * q_date1, 0)
        Vr = max(Vin - V_I, 0)

        # محاسبه Cu
        aveRage_I = np.mean(I_In1)
        Cu = (1 - np.sum(np.abs(I_In1 - aveRage_I)) / np.sum(I_In1)) * 100 if np.sum(I_In1) != 0 else 0
        Cu = max(Cu, 0)

        # محاسبه AE, TWR, DPR
        Ae = (Vn / Vin) * 100 if Vin != 0 else 0
        Twr = (Vr / Vin) * 100 if Vin != 0 else 0
        Dpr = (Vdp / Vin) * 100 if Vin != 0 else 0

        return Vn, Vdp, Vin, Vr, Cu, Ae, Twr, Dpr

    def display_results(self, Vn, Vdp, Vin, Vr, Cu, Ae, Twr, Dpr,Tco):
        self.gui.editBox_Vn.setText(f'{max(0, round(Vn, 2))} (m3)')
        self.gui.editBox_Vdp.setText(f'{max(0, round(Vdp, 2))} (m3)')
        self.gui.editBox_Vin.setText(f'{max(0, round(Vin, 2))} (m3)')
        self.gui.editBox_Vr.setText(f'{max(0, round(Vr, 2))} (m3)')
        self.gui.editBox_Cu.setText(f'{max(0, round(Cu, 2))} (%)')
        self.gui.editBox_Ae.setText(f'{max(0, round(Ae, 2))} (%)')
        self.gui.editBox_Twr.setText(f'{max(0, round(Twr, 2))} (%)')
        self.gui.editBox_Dpr.setText(f'{max(0, round(Dpr, 2))} (%)')
        self.gui.editBox_tco.setText(f'{max(0, round(Tco, 2))} (min)')

    def plot_infiltration_depth(self, X_data, I_In, I_Inff):
        self.gui.figure_tab2.clear()
        ax = self.gui.figure_tab2.add_subplot(111)
        ax.plot(X_data, I_In, 'b', linewidth=1.7)
        ax.plot(X_data, np.full_like(X_data, I_Inff), '--r', linewidth=1.7)
        ax.plot(X_data, np.zeros_like(X_data), '-k', linewidth=0.01)
        ax.grid(True)
        ax.set_xlabel('X(m)')
        ax.set_ylabel('I(cm)')
        ax.set_title('Infiltration Depth - Furrow Length')
        ax.invert_yaxis()
        self.gui.canvas_tab2.draw()

    def walker_method(self, X_data, Ta_data, Tr_prime):
        # روش Walker
        valid_indices = (Ta_data > 0) & (X_data > 0)
        p_Walker = np.log10(Ta_data[valid_indices])
        R_Walker = np.log10(X_data[valid_indices])

        if len(p_Walker) < 2 or len(R_Walker) < 2:
            QMessageBox.critical(self.gui, 'Error', 'Insufficient valid data points for Walker method.')
            raise ValueError("Insufficient data for Walker method.")

        slope, intercept = np.polyfit(p_Walker, R_Walker, 1)
        r = slope
        p = 10 ** intercept

        valid_indices_prime = (Tr_prime > 0) & (X_data > 0)
        p_prime_Walker = np.log10(Tr_prime[valid_indices_prime])
        R_prime_Walker = np.log10(X_data[valid_indices_prime])

        if len(p_prime_Walker) < 2 or len(R_prime_Walker) < 2:
            QMessageBox.critical(self.gui, 'Error', 'Insufficient valid data points for Walker method (recession).')
            raise ValueError("Insufficient data for Walker method (recession).")

        slope_prime, intercept_prime = np.polyfit(p_prime_Walker, R_prime_Walker, 1)
        r_prime = slope_prime
        p_prime = 10 ** intercept_prime

        self.gui.editBox_P_walker.setText(str(round(p,2)))
        self.gui.editBox_R_walker.setText(str(round(r,2)))
        self.gui.editBox_p_walker.setText(str(round(p_prime,2)))
        self.gui.editBox_r_walker.setText(str(round(r_prime,2)))

        return p, r, p_prime, r_prime

    def optimize_furrow_length(self, infiltration_type, params, P_W, W, I_Inff, AI, q_date1, Tn_prime, p, r, p_prime, r_prime, RE):
        # محاسبه Tco بهینه با استفاده از تابع calculate_Ae
        optimal_Tco = self.calculate_Ae(p, r, p_prime, r_prime, Tn_prime, AI, I_Inff, W, q_date1)

        # لیست‌ها برای ذخیره نتایج
        list_Vn = []
        list_Vdp = []
        list_Vin = []
        list_Vr = []
        list_Cu = []
        list_Ae = []
        list_Twr = []
        list_Dpr = []
        list_furrow_length = []
        list_I_In1_2 = []

        # محاسبه نتایج برای طول‌های مختلف جوی
        for furrow_length in range(1, 1000, 1):
            list_furrow_length.append(furrow_length)

            T_pishravi = (furrow_length / p) ** (1 / r)
            T_pasravi = (furrow_length / p_prime) ** (1 / r_prime)

            Tco1 = T_pishravi + Tn_prime - T_pasravi
            Tn1 = optimal_Tco - T_pishravi + T_pasravi
            Tn1 = np.maximum(Tn1, 0)

            # نفوذ برای طول جدید
            I_Tn11 = self.compute_infiltration_in(Tn1, infiltration_type, params, P_W)
            I_In1_2 = np.round(I_Tn11, 4)
            list_I_In1_2.append(I_In1_2)

            if len(list_I_In1_2) <= 2:
                # نیاز داریم حداقل 3 مقدار نفوذ داشته باشیم تا محاسبات بعدی دقیق باشد.
                continue

            # محاسبه Vi برای سناریو
            Vi_list = []
            for i in range(1, len(list_I_In1_2)):
                vi = ((list_I_In1_2[i - 1] + list_I_In1_2[i]) / 200) * 1 * P_W
                Vi_list.append(vi)

            # محاسبه Vn بر اساس AI
            if AI == 100:
                Vn1 = furrow_length * (I_Inff / 100) * W
            else:
                Vn1 = (furrow_length * AI / 100) * (I_Inff / 100) * W

            Vdp1 = np.sum(Vi_list) - Vn1
            Vin1 = Tco1 * q_date1
            Vr1 = Vin1 - np.sum(Vi_list)

            # محاسبه Cu
            aveRage_I1 = np.mean(list_I_In1_2)
            cumulative_I = np.sum(list_I_In1_2)
            I_diff = np.abs(list_I_In1_2 - aveRage_I1)
            Cu1 = (1 - (np.sum(I_diff) / cumulative_I)) * 100 if cumulative_I != 0 else 0

            Ae1 = (Vn1 / Vin1) * 100 if Vin1 != 0 else 0
            Twr1 = (Vr1 / Vin1) * 100 if Vin1 != 0 else 0
            Dpr1 = (Vdp1 / Vin1) * 100 if Vin1 != 0 else 0

            list_Vn.append(Vn1)
            list_Vdp.append(Vdp1)
            list_Vin.append(Vin1)
            list_Vr.append(Vr1)
            list_Cu.append(Cu1)
            list_Ae.append(Ae1)
            list_Twr.append(Twr1)
            list_Dpr.append(Dpr1)

        # یافتن طول بهینه
        max_index = np.argmax(list_Ae)

        # برای اطمینان از طول‌های برابر
        min_length = min(
            len(list_furrow_length),
            len(list_Vn),
            len(list_Vdp),
            len(list_Vin),
            len(list_Vr),
            len(list_Cu),
            len(list_Ae),
            len(list_Twr),
            len(list_Dpr)
        )

        # برش داده‌ها به طول min_length
        list_furrow_length = list_furrow_length[:min_length]
        list_Vn = list_Vn[:min_length]
        list_Vdp = list_Vdp[:min_length]
        list_Vin = list_Vin[:min_length]
        list_Vr = list_Vr[:min_length]
        list_Cu = list_Cu[:min_length]
        list_Ae = list_Ae[:min_length]
        list_Twr = list_Twr[:min_length]
        list_Dpr = list_Dpr[:min_length]

        try:
            optimal_result = {
                'X': list_furrow_length[max_index + 2], # baryeh inkeh do to item azf shodeh az list
                'Vn': list_Vn[max_index],
                'Vdp': list_Vdp[max_index],
                'Vin': list_Vin[max_index],
                'Vr': list_Vr[max_index],
                'CU': list_Cu[max_index],
                'AE': list_Ae[max_index],
                'TWR': list_Twr[max_index],
                'DPR': list_Dpr[max_index]
            }
        except:
                optimal_result = {
                'X': list_furrow_length[max_index],
                'Vn': list_Vn[max_index],
                'Vdp': list_Vdp[max_index],
                'Vin': list_Vin[max_index],
                'Vr': list_Vr[max_index],
                'CU': list_Cu[max_index],
                'AE': list_Ae[max_index],
                'TWR': list_Twr[max_index],
                'DPR': list_Dpr[max_index]
            }

        df = pd.DataFrame({
            'X': list_furrow_length,
            'Vn': list_Vn,
            'Vdp': list_Vdp,
            'Vin': list_Vin,
            'Vr': list_Vr,
            'CU': list_Cu,
            'AE': list_Ae,
            'TWR': list_Twr,
            'DPR': list_Dpr
        })

        self.show_optimal_results(optimal_result,optimal_Tco)
        self.plot_optimization_results(df, optimal_result, AI)

        # بررسی خطای مدل
        if optimal_result['X'] >= 1000 or RE > 22:
            QMessageBox.critical(self.gui, 'Error', 'Model is poor, please change your equation.')
            self.gui.output_data_button.setEnabled(False)
            self.gui.table1.setRowCount(0)
        else:
            max_X = optimal_result['X'] * (1 / (AI / 100)) + 0.25 * optimal_result['X']
            self.optimization_output = df[df['X'] <= max_X].values
            self.gui.table1.setRowCount(len(self.optimization_output))
            for i, row in enumerate(self.optimization_output):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(round(value,2)))
                    self.gui.table1.setItem(i, j, item)
            self.gui.output_data_button.setEnabled(True)

    def show_optimal_results(self, optimal_result,optimal_Tco):
        self.gui.editBox_Vn2.setText(f'{max(0, round(optimal_result["Vn"], 2))} (m3)')
        self.gui.editBox_Vdp2.setText(f'{max(0, round(optimal_result["Vdp"], 2))} (m3)')
        self.gui.editBox_Vin2.setText(f'{max(0, round(optimal_result["Vin"], 2))} (m3)')
        self.gui.editBox_Vr2.setText(f'{max(0, round(optimal_result["Vr"], 2))} (m3)')
        self.gui.editBox_Cu2.setText(f'{max(0, round(optimal_result["CU"], 2))} (%)')
        self.gui.editBox_Ae2.setText(f'{max(0, round(optimal_result["AE"], 2))} (%)')
        self.gui.editBox_Twr2.setText(f'{max(0, round(optimal_result["TWR"], 2))} (%)')
        self.gui.editBox_Dpr2.setText(f'{max(0, round(optimal_result["DPR"], 2))} (%)')
        self.gui.editBox_Tco.setText(f'{max(0, round(optimal_Tco))} (min)')

        self.gui.length_optim_value.setText(f'Optimal Furrow length: {str(optimal_result["X"])} (m)')
        self.gui.length_optim_value.setStyleSheet("""
            background-color: yellow;  /* رنگ پس‌زمینه زرد برای جلب توجه */
            color: black;              /* متن سیاه برای خوانایی */
            border: 2px solid orange;  /* حاشیه نارنجی */
            padding: 5px;              /* فاصله داخلی برای زیبایی */
            border-radius: 5px;        /* گوشه‌های گرد برای حاشیه */
            font-size: 13px;  /* اندازه فونت */

        """)

    def plot_optimization_results(self, df, optimal_result, AI):
        # محدود کردن داده‌ها برای نمودار
        optimal_length = optimal_result['X']
        max_length = 2 * optimal_length  # می‌توان بر اساس نیاز تغییر داد
        valid_indices = df['X'] <= max_length
        filtered_df = df[valid_indices]

        # نمودار AE
        self.gui.figure_AE_tab3.clear()
        ax = self.gui.figure_AE_tab3.add_subplot(111)
        ax.plot(filtered_df['X'], filtered_df['AE'])
        ax.plot(optimal_result['X'], optimal_result['AE'], 'ro')  # نقطه بهینه
        ax.set_xlabel('X(m)')
        ax.set_ylabel('AE(%)')

        widget_width = self.gui.canvas_AE_tab3.width()  # عرض ویجت به پیکسل
        dpi = self.gui.figure_AE_tab3.dpi  # تعداد پیکسل در هر اینچ (DPI)
        width_in_inches = widget_width / dpi
        height_in_inches = 2  # ارتفاع ثابت
        self.gui.figure_AE_tab3.set_size_inches(width_in_inches, height_in_inches)  # کاهش کل اندازه نمودار AE
        
        self.gui.canvas_AE_tab3.draw()



        # نمودار CU
        self.gui.figure_CU_tab3.clear()
        ax = self.gui.figure_CU_tab3.add_subplot(111)
        ax.plot(filtered_df['X'], filtered_df['CU'])
        ax.set_xlabel('X(m)')
        ax.set_ylabel('CU(%)')
        
        widget_width = self.gui.canvas_CU_tab3.width()  # عرض ویجت به پیکسل
        dpi = self.gui.figure_CU_tab3.dpi  # تعداد پیکسل در هر اینچ (DPI)
        width_in_inches = widget_width / dpi
        height_in_inches = 2  # ارتفاع ثابت
        self.gui.figure_CU_tab3.set_size_inches(width_in_inches, height_in_inches)  # کاهش کل اندازه نمودار AE

        self.gui.canvas_CU_tab3.draw()




        # نمودار AE-TWR-DPR
        self.gui.figure_TWR_tab3.clear()
        ax = self.gui.figure_TWR_tab3.add_subplot(111)
        ax.plot(filtered_df['X'], filtered_df['AE'], label='AE')
        ax.plot(filtered_df['X'], filtered_df['TWR'], label='TWR')
        ax.plot(filtered_df['X'], filtered_df['DPR'], label='DPR')
        ax.legend()
        ax.set_xlabel('X(m)')
        ax.set_ylabel('AE-TWR-DPR(%)')
        
        widget_width = self.gui.canvas_TWR_tab3.width()  # عرض ویجت به پیکسل
        dpi = self.gui.figure_TWR_tab3.dpi  # تعداد پیکسل در هر اینچ (DPI)
        width_in_inches = widget_width / dpi
        height_in_inches = 2  # ارتفاع ثابت
        self.gui.figure_TWR_tab3.set_size_inches(width_in_inches, height_in_inches)  # کاهش کل اندازه نمودار AE

        self.gui.canvas_TWR_tab3.draw()

    def calculate_Ae(self, p, r, p_prime, r_prime, Tn_prime, AI, I_Inff, W, q_date1):
        """محاسبه Tco بهینه جهت حداکثرسازی Ae."""
        list_Ae = []
        list_Tco = []

        for furrow_length in range(1, 1000, 1):
            T_pishravi = (furrow_length / p) ** (1 / r)
            T_pasravi = (furrow_length / p_prime) ** (1 / r_prime)
            Tco1 = T_pishravi + Tn_prime - T_pasravi
            list_Tco.append(Tco1)

            if AI == 100:
                Vn1 = furrow_length * (I_Inff / 100) * W
            else:
                Vn1 = (furrow_length * AI / 100) * (I_Inff / 100) * W

            Vin1 = Tco1 * q_date1
            Ae1 = (Vn1 / Vin1) * 100 if Vin1 != 0 else 0
            list_Ae.append(Ae1)

        max_index = np.argmax(list_Ae)
        return list_Tco[max_index]

