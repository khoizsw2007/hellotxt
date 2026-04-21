import customtkinter as ctk
import tkinter as tk
from tkinter import ttk

# ================= CAU HÌNH THEME =================
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# Bảng màu chuẩn Tailwind CSS (Giống Figma)
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

        self.title("SaaS Admin Dashboard")
        self.geometry("1300x800")
        self.configure(fg_color=BG_COLOR)
        
        # Cấu hình style cho bảng dữ liệu (Treeview)
        self.setup_table_style()

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= SIDEBAR (DARK THEME) =================
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SIDEBAR_COLOR)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="UberAdmin", font=ctk.CTkFont(family="Inter", size=24, weight="bold"), text_color="white")
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 40), sticky="w")

        self.create_nav_button("📊 Dashboard", 1, is_active=True)
        self.create_nav_button("💰 Revenue & Reports", 2)
        self.create_nav_button("🚨 Issue Analytics", 3)
        self.create_nav_button("🚗 Driver Profiles", 4)

        # ================= MAIN CONTENT =================
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=30, pady=30)
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.build_dashboard()

    def setup_table_style(self):
        # Làm phẳng (flat) bảng Treeview mặc định của Tkinter cho giống Figma
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", 
                        background=CARD_COLOR, 
                        foreground=TEXT_DARK, 
                        rowheight=35, 
                        fieldbackground=CARD_COLOR,
                        bordercolor=BG_COLOR,
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#E5E7EB')], foreground=[('selected', TEXT_DARK)])
        style.configure("Treeview.Heading", 
                        background=BG_COLOR, 
                        foreground=TEXT_GRAY, 
                        font=("Inter", 10, "bold"),
                        borderwidth=0,
                        padding=5)

    def create_nav_button(self, text, row, is_active=False):
        bg_color = "#374151" if is_active else "transparent"
        text_color = "white" if is_active else "#9CA3AF"
        btn = ctk.CTkButton(self.sidebar_frame, text=text, corner_radius=8, 
                            fg_color=bg_color, text_color=text_color, hover_color="#374151",
                            font=ctk.CTkFont(family="Inter", size=14, weight="bold"), anchor="w", height=40)
        btn.grid(row=row, column=0, padx=20, pady=5, sticky="ew")

    def build_dashboard(self):
        # --- 1. HEADER (Title + Filters + Export) ---
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 25))
        
        ctk.CTkLabel(header_frame, text="Dashboard Tổng Quan", font=ctk.CTkFont(family="Inter", size=26, weight="bold"), text_color=TEXT_DARK).pack(side="left")
        
        # Nút Export
        ctk.CTkButton(header_frame, text="📥 Export Report", fg_color="#3B82F6", hover_color="#2563EB", font=ctk.CTkFont(weight="bold")).pack(side="right", padx=(15, 0))
        
        # Segmented Button (Lọc thời gian giống iOS/Figma)
        time_filter = ctk.CTkSegmentedButton(header_frame, values=["Hôm nay", "Tuần này", "Tháng này"], selected_color="#FFFFFF", selected_hover_color="#F9FAFB", unselected_color="#E5E7EB", unselected_hover_color="#D1D5DB", text_color=TEXT_DARK)
        time_filter.pack(side="right")
        time_filter.set("Tuần này") # Chọn mặc định

        # --- 2. KPI CARDS ---
        kpi_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        kpi_frame.pack(fill="x", pady=(0, 25))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.create_kpi_card(kpi_frame, 0, "Total Rides", "150,000", "↑ 12.5% vs last week", GREEN_TREND, "📈")
        self.create_kpi_card(kpi_frame, 1, "Total Revenue", "₹ 24.5M", "↑ 8.2% vs last week", GREEN_TREND, "💵")
        self.create_kpi_card(kpi_frame, 2, "Completion Rate", "85.2%", "↓ 2.1% vs yesterday", RED_TREND, "🎯")
        self.create_kpi_card(kpi_frame, 3, "Avg Rating", "4.8 ⭐", "↑ 0.1 vs last week", GREEN_TREND, "👤")

        # --- 3. BOTTOM SECTION (Table + Charts) ---
        bottom_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        bottom_frame.pack(fill="both", expand=True)
        bottom_frame.grid_columnconfigure(0, weight=6) 
        bottom_frame.grid_columnconfigure(1, weight=4)

        # 3.1 BẢNG DỮ LIỆU (Bên trái)
        table_container = ctk.CTkFrame(bottom_frame, fg_color=CARD_COLOR, corner_radius=12)
        table_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        
        # Tiêu đề bảng
        ctk.CTkLabel(table_container, text="Recent Rides", font=ctk.CTkFont(family="Inter", size=16, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=(20, 10))

        # Khởi tạo Treeview
        columns = ("id", "date", "type", "status", "value")
        tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")
        tree.heading("id", text="BOOKING ID", anchor="w")
        tree.heading("date", text="DATE", anchor="w")
        tree.heading("type", text="VEHICLE TYPE", anchor="w")
        tree.heading("status", text="STATUS", anchor="w")
        tree.heading("value", text="VALUE", anchor="e")

        tree.column("id", width=120)
        tree.column("date", width=100)
        tree.column("type", width=120)
        tree.column("status", width=120)
        tree.column("value", width=100, anchor="e")
        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Thêm Data mẫu
        tree.insert("", tk.END, values=("CNR8494506", "2024-08-23", "Auto", "Completed", "₹ 627.0"))
        tree.insert("", tk.END, values=("CNR1326809", "2024-11-29", "Go Sedan", "Incomplete", "₹ 237.0"))
        tree.insert("", tk.END, values=("CNR5884300", "2024-03-23", "eBike", "No Driver", "-"))
        tree.insert("", tk.END, values=("CNR8906825", "2024-10-21", "Premier Sedan", "Completed", "₹ 416.0"))

        # 3.2 KHU VỰC BIỂU ĐỒ (Bên phải)
        charts_container = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        charts_container.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        charts_container.grid_rowconfigure((0, 1), weight=1)

        # Hộp chứa biểu đồ 1
        chart1 = ctk.CTkFrame(charts_container, fg_color=CARD_COLOR, corner_radius=12)
        chart1.grid(row=0, column=0, sticky="nsew", pady=(0, 10))
        ctk.CTkLabel(chart1, text="Ride Status Distribution\n[Nhúng Biểu đồ Tròn ở đây]", text_color=TEXT_GRAY).pack(expand=True)

        # Hộp chứa biểu đồ 2
        chart2 = ctk.CTkFrame(charts_container, fg_color=CARD_COLOR, corner_radius=12)
        chart2.grid(row=1, column=0, sticky="nsew", pady=(10, 0))
        ctk.CTkLabel(chart2, text="Revenue (Last 7 Days)\n[Nhúng Biểu đồ Đường ở đây]", text_color=TEXT_GRAY).pack(expand=True)

    def create_kpi_card(self, parent, col, title, value, trend, trend_color, icon):
        card = ctk.CTkFrame(parent, fg_color=CARD_COLOR, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=10)
        card.grid_columnconfigure(0, weight=1)

        # Dòng 1: Tiêu đề (Trái) + Icon (Phải)
        top_row = ctk.CTkFrame(card, fg_color="transparent")
        top_row.pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkLabel(top_row, text=title, font=ctk.CTkFont(family="Inter", size=13, weight="bold"), text_color=TEXT_GRAY).pack(side="left")
        ctk.CTkLabel(top_row, text=icon, font=ctk.CTkFont(size=16)).pack(side="right")

        # Dòng 2: Con số lớn
        ctk.CTkLabel(card, text=value, font=ctk.CTkFont(family="Inter", size=32, weight="bold"), text_color=TEXT_DARK).pack(anchor="w", padx=20, pady=5)
        
        # Dòng 3: Mũi tên và Xu hướng
        ctk.CTkLabel(card, text=trend, font=ctk.CTkFont(family="Inter", size=12, weight="bold"), text_color=trend_color).pack(anchor="w", padx=20, pady=(0, 20))

if __name__ == "__main__":
    app = UberDashboardApp()
    app.mainloop()