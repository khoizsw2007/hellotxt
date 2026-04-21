import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ================= CẤU HÌNH THEME =================
ctk.set_appearance_mode("Light")
BG_COLOR = "#F4F6F9"
CARD_COLOR = "#FFFFFF"
SIDEBAR_COLOR = "#111827"
TEXT_DARK = "#1F2937"
TEXT_GRAY = "#6B7280"
GREEN_TREND = "#10B981"
RED_TREND = "#EF4444"

class UberDashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("SaaS Admin Dashboard - Final Version")
        self.geometry("1350x850")
        self.configure(fg_color=BG_COLOR)
        
        # 1. LOAD DỮ LIỆU
        self.load_data()

        # 2. CẤU HÌNH LAYOUT
        self.setup_table_style()
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 3. XÂY DỰNG GIAO DIỆN
        self.build_sidebar()
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
        # Khởi tạo các biến lưu trữ Widget để cập nhật sau này
        self.kpi_labels = {}
        self.chart_canvas_list = []
        
        self.build_dashboard()
        
        # 4. KÍCH HOẠT LỌC DỮ LIỆU LẦN ĐẦU
        self.update_dashboard_data("Tuần này")

    # ================= 1. XỬ LÝ DỮ LIỆU (PANDAS) =================
    def load_data(self):
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(current_dir, 'ncr_ride_bookings.csv')
            self.df = pd.read_csv(csv_path)
            
            # Tiền xử lý
            self.df['Booking Value'] = self.df['Booking Value'].fillna(0)
            self.df['Date'] = pd.to_datetime(self.df['Date']) # Ép kiểu ngày tháng
            
            # Tìm ngày mới nhất trong Data làm "Hôm nay"
            self.max_date = self.df['Date'].max()
        except Exception as e:
            messagebox.showerror("Lỗi Data", f"Không đọc được CSV:\n{e}")
            self.destroy()

    def filter_data_by_time(self, timeframe):
        if timeframe == "Hôm nay":
            return self.df[self.df['Date'] == self.max_date]
        elif timeframe == "Tuần này":
            start_date = self.max_date - pd.Timedelta(days=7)
            return self.df[(self.df['Date'] > start_date) & (self.df['Date'] <= self.max_date)]
        elif timeframe == "Tháng này":
            start_date = self.max_date - pd.Timedelta(days=30)
            return self.df[(self.df['Date'] > start_date) & (self.df['Date'] <= self.max_date)]
        return self.df # Toàn thời gian

    # ================= 2. XÂY DỰNG GIAO DIỆN (UI) =================
    def setup_table_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=CARD_COLOR, foreground=TEXT_DARK, 
                        rowheight=35, fieldbackground=CARD_COLOR, borderwidth=0)
        style.map('Treeview', background=[('selected', '#E5E7EB')], foreground=[('selected', TEXT_DARK)])
        style.configure("Treeview.Heading", background=BG_COLOR, foreground=TEXT_GRAY, 
                        font=("Inter", 10, "bold"), borderwidth=0, padding=5)

    def build_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        ctk.CTkLabel(self.sidebar_frame, text="UberAdmin", font=ctk.CTkFont("Inter", 24, "bold"), text_color="white").grid(row=0, column=0, padx=20, pady=(30, 40), sticky="w")
        self.create_nav_button("📊 Dashboard", 1, is_active=True)
        self.create_nav_button("💰 Revenue & Reports", 2)

    def create_nav_button(self, text, row, is_active=False):
        bg_color = "#374151" if is_active else "transparent"
        btn = ctk.CTkButton(self.sidebar_frame, text=text, corner_radius=8, fg_color=bg_color, 
                            text_color="white" if is_active else "#9CA3AF", hover_color="#374151",
                            font=ctk.CTkFont("Inter", 14, "bold"), anchor="w", height=40)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")

    def build_dashboard(self):
        # HEADER & BỘ LỌC
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        ctk.CTkLabel(header_frame, text="Dashboard Tổng Quan", font=ctk.CTkFont("Inter", 26, "bold"), text_color=TEXT_DARK).pack(side="left")
        
        ctk.CTkButton(header_frame, text="📥 Export Report", fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=(15, 0))
        
        self.time_filter = ctk.CTkSegmentedButton(header_frame, values=["Hôm nay", "Tuần này", "Tháng này", "Tất cả"], 
                                                  command=self.update_dashboard_data, # Kích hoạt hàm khi bấm
                                                  selected_color="#FFFFFF", selected_hover_color="#F9FAFB", 
                                                  unselected_color="#E5E7EB", text_color=TEXT_DARK)
        self.time_filter.pack(side="right")
        self.time_filter.set("Tuần này")

        # KHU VỰC 4 KPI
        kpi_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 25))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.kpi_labels['rides'] = self.create_kpi_card(kpi_frame, 0, "Total Rides", "0", "📈")
        self.kpi_labels['revenue'] = self.create_kpi_card(kpi_frame, 1, "Total Revenue", "₹ 0", "💵")
        self.kpi_labels['rate'] = self.create_kpi_card(kpi_frame, 2, "Completion Rate", "0%", "🎯")
        self.kpi_labels['rating'] = self.create_kpi_card(kpi_frame, 3, "Avg Rating", "0.0 ⭐", "👤")

        # KHU VỰC BẢNG & BIỂU ĐỒ
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=5) 
        bottom_frame.grid_columnconfigure(1, weight=5)

        # Bảng dữ liệu (Bên trái)
        table_container = ctk.CTkFrame(bottom_frame, fg_color=CARD_COLOR, corner_radius=12)
        table_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(table_container, text="Recent Rides (Top 50)", font=ctk.CTkFont("Inter", 16, "bold"), text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=(20, 10))

        self.tree = ttk.Treeview(table_container, columns=("id", "date", "type", "status", "value"), show="headings", selectmode="browse")
        for col, txt, wid, anc in [("id", "BOOKING ID", 110, "w"), ("date", "DATE", 90, "w"), 
                                   ("type", "VEHICLE", 110, "w"), ("status", "STATUS", 110, "w"), ("value", "VALUE", 80, "e")]:
            self.tree.heading(col, text=txt, anchor=anc)
            self.tree.column(col, width=wid, anchor=anc)
        self.tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Khung chứa Biểu đồ (Bên phải)
        self.charts_container = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        self.charts_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        self.charts_container.grid_rowconfigure((0, 1), weight=1)

    def create_kpi_card(self, parent, col, title, default_val, icon):
        card = ctk.CTkFrame(parent, fg_color=CARD_COLOR, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=10)
        
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(top_row, text=title, font=ctk.CTkFont("Inter", 13, "bold"), text_color=TEXT_GRAY).pack(side="left")
        ctk.CTkLabel(top_row, text=icon, font=ctk.CTkFont(size=16)).pack(side="right")

        value_label = ctk.CTkLabel(card, text=default_val, font=ctk.CTkFont("Inter", 30, "bold"), text_color=TEXT_DARK)
        value_label.pack(anchor="w", padx=20, pady=(5, 20))
        return value_label # Trả về label này để cập nhật số sau

    # ================= 3. LOGIC CẬP NHẬT ĐỘNG =================
    def update_dashboard_data(self, selected_timeframe):
        # 1. Lấy Data đã lọc
        df_filtered = self.filter_data_by_time(selected_timeframe)
        
        if df_filtered.empty:
            return # Bỏ qua nếu không có dữ liệu

        # 2. Cập nhật con số KPI
        total_rides = len(df_filtered)
        total_revenue = df_filtered['Booking Value'].sum()
        completed = len(df_filtered[df_filtered['Booking Status'] == 'Completed'])
        comp_rate = (completed / total_rides * 100) if total_rides > 0 else 0
        avg_rating = df_filtered[df_filtered['Driver Ratings'] > 0]['Driver Ratings'].mean()

        self.kpi_labels['rides'].configure(text=f"{total_rides:,}")
        self.kpi_labels['revenue'].configure(text=f"₹ {total_revenue:,.0f}")
        self.kpi_labels['rate'].configure(text=f"{comp_rate:.1f}%")
        self.kpi_labels['rating'].configure(text=f"{avg_rating:.1f} ⭐" if pd.notna(avg_rating) else "N/A")

        # 3. Cập nhật Bảng (Xóa cũ, Thêm mới top 50 dòng)
        self.tree.delete(*self.tree.get_children())
        top_50 = df_filtered.sort_values(by='Date', ascending=False).head(50)
        for _, row in top_50.iterrows():
            val = f"₹ {row['Booking Value']}" if row['Booking Value'] > 0 else "-"
            date_str = row['Date'].strftime('%Y-%m-%d')
            self.tree.insert("", tk.END, values=(row['Booking ID'], date_str, row['Vehicle Type'], row['Booking Status'], val))

        # 4. Vẽ lại 2 Biểu đồ
        self.draw_charts(df_filtered)

    def draw_charts(self, df_filtered):
        # Xóa biểu đồ cũ để tránh lag/tràn bộ nhớ
        for widget in self.charts_container.winfo_children():
            widget.destroy()

        # Biểu đồ 1: Pie Chart (Trạng thái)
        frame1 = ctk.CTkFrame(self.charts_container, fg_color=CARD_COLOR, corner_radius=12)
        frame1.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        
        fig1 = Figure(figsize=(5, 2.5), dpi=100)
        ax1 = fig1.add_subplot(111)
        status_counts = df_filtered['Booking Status'].value_counts()
        ax1.pie(status_counts, labels=status_counts.index, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 8})
        ax1.set_title("Phân bổ Trạng thái Chuyến xe", fontsize=10, fontweight='bold', color=TEXT_DARK)
        
        canvas1 = FigureCanvasTkAgg(fig1, master=frame1)
        canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        # Biểu đồ 2: Line Chart (Doanh thu theo ngày)
        frame2 = ctk.CTkFrame(self.charts_container, fg_color=CARD_COLOR, corner_radius=12)
        frame2.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        
        fig2 = Figure(figsize=(5, 2.5), dpi=100)
        ax2 = fig2.add_subplot(111)
        daily_rev = df_filtered.groupby(df_filtered['Date'].dt.date)['Booking Value'].sum()
        
        ax2.plot(daily_rev.index, daily_rev.values, marker='o', color='#3B82F6', linewidth=2)
        ax2.set_title("Biến động Doanh thu", fontsize=10, fontweight='bold', color=TEXT_DARK)
        ax2.tick_params(axis='x', rotation=15, labelsize=8)
        ax2.tick_params(axis='y', labelsize=8)
        fig2.tight_layout()

        canvas2 = FigureCanvasTkAgg(fig2, master=frame2)
        canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

if __name__ == "__main__":
    app = UberDashboardApp()
    app.mainloop()