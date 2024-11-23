import customtkinter as ctk
from views.dashboard import DashboardView
from views.accounts import AccountsView
from views.transactions import TransactionsView
from views.loans import LoansView
from views.savings import SavingsView
from views.reports import ReportsView
from views.forecast_view import ForecastView
from config.colors import *

class MainWindow:
    def __init__(self):
        self.window = ctk.CTk()
        self.window.title("Quản Lý Tài Chính Cá Nhân")
        self.window.geometry("1600x900")
        
        self.window.minsize(1200, 700)
        
        self.setup_theme()
        self.create_main_container()
        self.create_sidebar()
        self.create_content_frame()
        
        # Initialize views
        self.dashboard = DashboardView(self.content_frame)
        self.accounts = AccountsView(self.content_frame)
        self.transactions = TransactionsView(self.content_frame)
        self.loans = LoansView(self.content_frame)
        self.savings = SavingsView(self.content_frame)
        self.reports = ReportsView(self.content_frame)
        self.forecast = ForecastView(self.content_frame)
        
        # Show dashboard by default
        self.show_dashboard()
        
    def setup_theme(self):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        
    def create_main_container(self):
        self.main_container = ctk.CTkFrame(self.window)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
    def create_sidebar(self):
        # Tạo sidebar với màu nền tối hơn
        self.sidebar = ctk.CTkFrame(
            self.main_container, 
            width=250,
            fg_color="#0a0f1a"  # Màu nền tối hơn
        )
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        # Logo với style mới
        logo_frame = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent"
        )
        logo_frame.pack(pady=(20, 30))
        
        logo_label = ctk.CTkLabel(
            logo_frame, 
            text="Finance Manager",
            font=("Helvetica", 24, "bold"),
            text_color="#ffffff"  # Màu chữ trắng hoàn toàn
        )
        logo_label.pack()
        
        # Navigation buttons với màu tương phản cao hơn
        buttons = [
            ("🏠 Dashboard", self.show_dashboard, "#1d4ed8"),    # Xanh dương đậm
            ("💳 Tài Khoản", self.show_accounts, "#0369a1"),    # Xanh ngọc đậm
            ("💰 Giao Dịch", self.show_transactions, "#047857"), # Xanh lục đậm
            ("💸 Vay & Cho Vay", self.show_loans, "#6d28d9"),   # Tím đậm
            ("🏦 Tiết Kiệm", self.show_savings, "#be185d"),     # Hồng đậm
            ("📊 Báo Cáo", self.show_reports, "#9f1239"),       # Đỏ hồng đậm
            ("🔮 Dự Báo", self.show_forecast, "#991b1b")        # Đỏ đậm
        ]
        
        for text, command, color in buttons:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                width=220,
                height=45,
                font=("Helvetica", 14, "bold"),
                anchor="w",
                fg_color="transparent",
                hover_color=color,      # Màu hover đậm hơn
                text_color="#ffffff",   # Màu chữ trắng hoàn toàn
                corner_radius=8         # Bo góc ít hơn để tăng độ tương phản
            )
            btn.pack(pady=6)
            
            # Hiệu ứng hover với độ tương phản cao hơn
            def on_enter(e, button=btn, hover_color=color):
                button.configure(
                    fg_color=hover_color,
                    text_color="#ffffff"  # Giữ màu chữ trắng khi hover
                )
                
            def on_leave(e, button=btn):
                button.configure(
                    fg_color="transparent",
                    text_color="#ffffff"  # Giữ màu chữ trắng khi không hover
                )
                
            btn.bind("<Enter>", on_enter)
            btn.bind("<Leave>", on_leave)
        
        # Version tag với màu tương phản thấp
        version_label = ctk.CTkLabel(
            self.sidebar,
            text="v1.0.0",
            font=("Helvetica", 10),
            text_color="#64748b"  # Màu chữ xám nhạt hơn
        )
        version_label.pack(side="bottom", pady=20)
        
    def create_content_frame(self):
        # Content frame với màu nền sáng hơn
        self.content_frame = ctk.CTkFrame(
            self.main_container,
            fg_color="#ffffff"  # Màu nền trắng cho content
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
    def show_dashboard(self):
        self.clear_content()
        self.dashboard.show()
        
    def show_accounts(self):
        self.clear_content()
        self.accounts.show()
        
    def show_transactions(self):
        self.clear_content()
        self.transactions.show()
        
    def show_loans(self):
        self.clear_content()
        self.loans.show()
        
    def show_savings(self):
        self.clear_content()
        self.savings.show()
        
    def show_reports(self):
        self.clear_content()
        self.reports.show()
        
    def show_forecast(self):
        self.clear_content()
        self.forecast.show()
        
    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def run(self):
        self.window.mainloop() 