import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
from datetime import datetime
from models.transaction import Transaction
from models.account import Account
from models.loan import Loan
from models.saving import Saving
from config.colors import *
import numpy as np

class ReportsView:
    def __init__(self, parent):
        self.parent = parent
        
    def show(self):
        self.create_title()
        self.create_tabs()
        
    def create_title(self):
        title = ctk.CTkLabel(
            self.parent,
            text="Báo Cáo Tài Chính",
            font=("Helvetica", 24, "bold"),
            text_color=TEXT_CONTRAST['light']
        )
        title.pack(pady=20)
        
    def create_tabs(self):
        # Control Frame cho lựa chọn tài khoản và xuất báo cáo
        control_frame = ctk.CTkFrame(
            self.parent,
            fg_color=BACKGROUND['dark']
        )
        control_frame.pack(fill="x", padx=20, pady=10)
        
        # Left side - Account Selection
        account_frame = ctk.CTkFrame(
            control_frame, 
            fg_color="transparent"
        )
        account_frame.pack(side="left", fill="x", expand=True)
        
        account_label = ctk.CTkLabel(
            account_frame, 
            text="🏦 Chọn Tài Khoản:",
            font=("Helvetica", 14, "bold"),
            text_color=TEXT_CONTRAST['light']
        )
        account_label.pack(side="left", padx=10)
        
        accounts = Account.get_all()
        account_names = ["Tất cả tài khoản"] + [acc.name for acc in accounts]
        self.account_var = ctk.StringVar(value=account_names[0])
        self.account_menu = ctk.CTkOptionMenu(
            account_frame,
            values=account_names,
            variable=self.account_var,
            width=250,
            height=35,
            font=("Helvetica", 12),
            command=self.on_account_change,
            fg_color=PRIMARY['main'],
            button_color=PRIMARY['hover'],
            button_hover_color=PRIMARY['light'],
            text_color=TEXT_CONTRAST['light']
        )
        self.account_menu.pack(side="left", padx=10)
        
        # Right side - Export Button
        export_btn = ctk.CTkButton(
            control_frame,
            text="📊 Xuất Báo Cáo Excel",
            command=self.export_to_excel,
            width=180,
            height=35,
            font=("Helvetica", 12, "bold"),
            fg_color=SUCCESS['main'],
            hover_color=SUCCESS['hover'],
            text_color=TEXT_CONTRAST['light']
        )
        export_btn.pack(side="right", padx=20)
        
        # Tabview with custom style
        self.tabview = ctk.CTkTabview(
            self.parent,
            fg_color=BACKGROUND['dark']
        )
        self.tabview.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add tabs with icons
        self.tab_income_expense = self.tabview.add("💰 Thu Chi")
        self.tab_cashflow = self.tabview.add("📈 Dòng Tiền")
        self.tab_category = self.tabview.add("📊 Chi Tiêu Theo Danh Mục")
        self.tab_assets = self.tabview.add("💎 Tài Sản")
        
        # Style the tabs
        for tab in [self.tab_income_expense, self.tab_cashflow, 
                   self.tab_category, self.tab_assets]:
            tab.configure(fg_color=BACKGROUND['dark'])
        
        # Create content for each tab
        self.create_income_expense_report(self.tab_income_expense)
        self.create_cashflow_report(self.tab_cashflow)
        self.create_category_report(self.tab_category)
        self.create_assets_report(self.tab_assets)
        
    def on_account_change(self, account_name):
        """Xử lý khi thay đổi tài khoản"""
        # Xóa nội dung cũ của các tab
        for widget in self.tab_income_expense.winfo_children():
            widget.destroy()
        for widget in self.tab_cashflow.winfo_children():
            widget.destroy()
        for widget in self.tab_category.winfo_children():
            widget.destroy()
        for widget in self.tab_assets.winfo_children():
            widget.destroy()
            
        # Tạo lại nội dung mới với tài khoản đã chọn
        self.create_income_expense_report(self.tab_income_expense)
        self.create_cashflow_report(self.tab_cashflow)
        self.create_category_report(self.tab_category)
        self.create_assets_report(self.tab_assets)
        
    def get_filtered_transactions(self):
        """Lấy danh sách giao dịch theo tài khoản được chọn"""
        transactions = Transaction.get_all()
        
        if self.account_var.get() != "Tất cả tài khoản":
            try:
                account = next(acc for acc in Account.get_all() 
                             if acc.name == self.account_var.get())
                
                # Lọc các giao dịch liên quan đến tài khoản này
                filtered_transactions = []
                for t in transactions:
                    new_transaction = None
                    
                    # Giao dịch trực tiếp của tài khoản
                    if t.account_id == account.account_id:
                        if t.type == "Chuyển tiền":
                            # Kiểm tra xem là chuyển đi hay nhận vào
                            if f"từ {account.name}" in t.category:
                                # Chuyển tiền đi -> số tiền âm
                                new_transaction = Transaction(
                                    transaction_id=t.transaction_id,
                                    date=t.date,
                                    type="Chuyển tiền đi",
                                    amount=-abs(t.amount),  # Đảm bảo số âm
                                    category=t.category,
                                    account_id=t.account_id,
                                    note=t.note
                                )
                            elif f"đến {account.name}" in t.category:
                                # Nhận tiền -> số tiền dương
                                new_transaction = Transaction(
                                    transaction_id=t.transaction_id,
                                    date=t.date,
                                    type="Chuyển tiền đến",
                                    amount=abs(t.amount),  # Đảm bảo số dương
                                    category=t.category,
                                    account_id=t.account_id,
                                    note=t.note
                                )
                        else:
                            # Thu nhập -> dương, chi tiêu và tiết kiệm -> âm
                            amount = abs(t.amount) if t.type == "Thu nhập" else -abs(t.amount)
                            new_transaction = Transaction(
                                transaction_id=t.transaction_id,
                                date=t.date,
                                type=t.type,
                                amount=amount,
                                category=t.category,
                                account_id=t.account_id,
                                note=t.note
                            )
                    
                    # Giao dịch chuyển khoản từ tài khoản khác đến tài khoản này
                    elif t.type == "Chuy���n tiền" and f"đến {account.name}" in t.category:
                        new_transaction = Transaction(
                            transaction_id=t.transaction_id,
                            date=t.date,
                            type="Chuyển tiền đến",
                            amount=abs(t.amount),  # Đảm bảo số dương
                            category=t.category,
                            account_id=account.account_id,
                            note=t.note
                        )
                    
                    if new_transaction:
                        filtered_transactions.append(new_transaction)
                
                transactions = filtered_transactions
                
            except StopIteration:
                return []
            
        # Sắp xếp theo ngày
        transactions.sort(key=lambda x: datetime.strptime(x.date, "%Y-%m-%d"))
        return transactions
        
    def create_chart_frame(self, parent, title):
        """Helper function to create consistent chart frames"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=BACKGROUND['dark']
        )
        frame.pack(fill="x", padx=10, pady=5)
        
        # Title with background
        title_frame = ctk.CTkFrame(
            frame,
            fg_color=PRIMARY['main']
        )
        title_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text=title,
            font=("Helvetica", 16, "bold"),
            text_color=TEXT_CONTRAST['light']
        ).pack(pady=5)
        
        return frame

    def create_summary_frame(self, parent, title, content):
        """Helper function to create consistent summary frames"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=BACKGROUND['dark']
        )
        frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            frame,
            text=title,
            font=("Helvetica", 14, "bold"),
            text_color=TEXT_CONTRAST['light']
        ).pack(pady=5)
        
        ctk.CTkLabel(
            frame,
            text=content,
            font=("Helvetica", 12),
            text_color=TEXT_CONTRAST['light'],
            justify="left"
        ).pack(pady=5)
        
        return frame

    def create_income_expense_report(self, parent):
        """Tạo báo cáo thu chi"""
        transactions = self.get_filtered_transactions()
        if not transactions:
            self.show_no_data_message(parent, "thu chi")
            return
            
        # Tính toán thu chi theo tháng
        df = pd.DataFrame([{
            'date': pd.to_datetime(t.date),
            'type': t.type,
            'amount': abs(t.amount)  # Sử dụng giá trị tuyệt đối cho biểu đồ
        } for t in transactions])
        
        # Thêm cột tháng và năm
        df['month'] = df['date'].dt.strftime('%Y-%m')
        
        # Tính tổng theo loại giao dịch và tháng
        monthly_stats = pd.pivot_table(
            df,
            index='month',
            columns='type',
            values='amount',
            aggfunc='sum',
            fill_value=0
        ).reset_index()
        
        # Đảm bảo có đủ các cột cần thiết
        required_columns = ['Thu nhập', 'Chi tiêu', 'Gửi tiết kiệm', 'Chuyển tiền']
        for col in required_columns:
            if col not in monthly_stats.columns:
                monthly_stats[col] = 0
            
        # Tạo biểu đồ
        self.create_monthly_chart(parent, monthly_stats)
        
        # Tạo bảng thống kê chi tiết
        self.create_transaction_details(parent, transactions)

    def show_no_data_message(self, parent, report_type):
        """Hiển thị thông báo khi không có dữ liệu"""
        message_frame = ctk.CTkFrame(parent, fg_color=BACKGROUND['dark'])
        message_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            message_frame,
            text=f"❌ Không có dữ liệu {report_type}",
            font=("Helvetica", 16, "bold"),
            text_color=TEXT_CONTRAST['danger']
        ).pack(pady=5)
        
        # Thêm hướng dẫn cụ thể
        if report_type == "thu chi":
            guide_text = "Vui lòng thêm giao dịch thu/chi để xem báo cáo."
        elif report_type == "dòng tiền":
            guide_text = "Vui lòng thêm các giao dịch để xem dòng tiền."
        elif report_type == "danh mục":
            guide_text = "Vui lòng thêm giao dịch có danh mục để xem phân tích."
        else:
            guide_text = "Vui lòng thêm dữ liệu để xem báo cáo."
        
        ctk.CTkLabel(
            message_frame,
            text=f"Tài khoản {self.account_var.get()} chưa có dữ liệu.\n{guide_text}",
            font=("Helvetica", 14),
            text_color=TEXT_CONTRAST['muted']
        ).pack(pady=5)

    def create_transaction_details(self, parent, transactions):
        """Tạo bảng chi tiết giao dịch"""
        details_frame = ctk.CTkFrame(parent, fg_color=BACKGROUND['dark'])
        details_frame.pack(fill="x", padx=10, pady=5)
        
        # Tạo Treeview cho chi tiết giao dịch
        columns = ('Ngày', 'Loại', 'Số Tiền', 'Danh Mục', 'Ghi Chú')
        tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=5)
        
        # Cấu hình cột
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Style cho Treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=BACKGROUND['dark'],
            foreground=TEXT_CONTRAST['light'],
            fieldbackground=BACKGROUND['dark']
        )
        
        # Tags cho các loại giao dịch
        tree.tag_configure('income', foreground=TRANSACTION_CONTRAST['income'])
        tree.tag_configure('expense', foreground=TRANSACTION_CONTRAST['expense'])
        tree.tag_configure('transfer_in', foreground=TRANSACTION_CONTRAST['transfer'])
        tree.tag_configure('transfer_out', foreground=DANGER['main'])
        tree.tag_configure('saving', foreground=TRANSACTION_CONTRAST['saving'])
        
        # Thêm dữ liệu vào bảng
        for t in transactions:
            # Xác định tag dựa vào loại giao dịch
            if t.type == "Thu nhập":
                tag = 'income'
            elif t.type == "Chi tiêu":
                tag = 'expense'
            elif t.type == "Chuyển tiền đến":
                tag = 'transfer_in'
            elif t.type == "Chuyển tiền đi":
                tag = 'transfer_out'
            else:  # Tiết kiệm
                tag = 'saving'
            
            tree.insert('', 'end', values=(
                t.date,
                t.type,
                f"{abs(t.amount):,.0f}",
                t.category,
                t.note
            ), tags=(tag,))
        
        tree.pack(fill="x", padx=5, pady=5)
        
    def create_cashflow_report(self, parent):
        """Tạo báo cáo dòng tiền"""
        transactions = self.get_filtered_transactions()
        if not transactions:
            # Hiển thị thông báo nếu không có dữ liệu
            message_frame = ctk.CTkFrame(parent, fg_color=BACKGROUND['dark'])
            message_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                message_frame,
                text="❌ Không có dữ liệu dòng tiền",
                font=("Helvetica", 16, "bold"),
                text_color=TEXT_CONTRAST['danger']
            ).pack(pady=5)
            
            ctk.CTkLabel(
                message_frame,
                text=f"Tài khoản {self.account_var.get()} chưa có giao dịch nào.\nKhông thể tạo báo cáo dòng tiền.",
                font=("Helvetica", 14),
                text_color=TEXT_CONTRAST['muted']
            ).pack(pady=5)
            return
            
        # Calculate cumulative cash flow
        df = pd.DataFrame([{
            'date': t.date,
            'amount': (t.amount if t.type == 'Thu nhập' else 
                      -t.amount if t.type == 'Chi tiêu' else 
                      -t.amount if t.type == 'Gửi tiết kiệm' else 
                      t.amount)  # Đã xử lý dấu trong get_filtered_transactions
        } for t in transactions])
        
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        df['cumulative'] = df['amount'].cumsum()
        
        # Điều chỉnh kích thước biểu đồ
        fig, ax = plt.subplots(figsize=(10, 3.5), facecolor=BACKGROUND['dark'])
        
        # Tạo gradient fill dưới đường
        z = np.polyfit(range(len(df['cumulative'])), df['cumulative'], 1)
        p = np.poly1d(z)
        ax.fill_between(df['date'], df['cumulative'], alpha=0.2, 
                       color=PRIMARY['light'])
        
        # Vẽ đường dòng tiền với style mới
        line = ax.plot(df['date'], df['cumulative'], 
                      color=PRIMARY['main'],
                      marker='o', markersize=3,
                      linewidth=1.5,
                      markerfacecolor=PRIMARY['light'],
                      markeredgecolor=PRIMARY['main'])
        
        # Thêm điểm bắt đầu và kết thúc
        ax.plot(df['date'].iloc[0], df['cumulative'].iloc[0], 
               'o', color=SUCCESS['main'], markersize=5,
               label='Bắt đầu')
        ax.plot(df['date'].iloc[-1], df['cumulative'].iloc[-1], 
               'o', color=WARNING['main'], markersize=5,
               label='Hiện tại')
        
        # Style cho biểu đồ
        ax.set_title('Dòng Tiền Tích Lũy', 
                    fontsize=9, color=TEXT_CONTRAST['light'], pad=10)
        ax.set_facecolor(BACKGROUND['dark'])
        ax.tick_params(axis='both', colors=TEXT_CONTRAST['light'], labelsize=7)
        
        # Thêm lưới với style mới
        ax.grid(True, linestyle='--', alpha=0.1, color=TEXT_CONTRAST['light'])
        
        # Legend với font size nhỏ
        ax.legend(fontsize=7, loc='upper left',
                 facecolor=BACKGROUND['dark'],
                 labelcolor=TEXT_CONTRAST['light'])
        
        plt.tight_layout(pad=2.0)
        
        # Thêm biểu đồ vào frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=10, pady=(5, 15))
        
        # Add summary text
        summary_text = (
            f"🏦 Số dư ban đầu: {df['cumulative'].iloc[0]:,.0f} VND\n"
            f"💰 Số dư cuối kỳ: {df['cumulative'].iloc[-1]:,.0f} VND\n"
            f"📊 Thay đổi: {(df['cumulative'].iloc[-1] - df['cumulative'].iloc[0]):,.0f} VND"
        )
        self.create_summary_frame(parent, "📑 Tổng Kết", summary_text)
        
    def create_category_report(self, parent):
        """Tạo báo cáo theo danh mục"""
        transactions = self.get_filtered_transactions()
        if not transactions:
            self.show_no_data_message(parent, "danh mục")
            return
            
        # Calculate totals by category
        expense_by_category = {}
        income_by_category = {}
        savings_by_category = {}
        
        for t in transactions:
            amount = abs(t.amount)  # Sử dụng giá trị tuyệt đối
            if t.type == 'Chi tiêu':
                expense_by_category[t.category] = expense_by_category.get(t.category, 0) + amount
            elif t.type == 'Thu nhập':
                income_by_category[t.category] = income_by_category.get(t.category, 0) + amount
            elif t.type == 'Gửi tiết kiệm':
                savings_by_category[t.category] = savings_by_category.get(t.category, 0) + amount
                
        # Tạo biểu đồ
        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 5), facecolor=BACKGROUND['dark'])
        
        # Style chung cho các biểu đồ
        for ax in [ax1, ax2, ax3]:
            ax.set_facecolor(BACKGROUND['dark'])
            for spine in ax.spines.values():
                spine.set_color(TEXT_CONTRAST['muted'])
        
        # Chi tiêu theo danh mục
        if expense_by_category:
            categories = list(expense_by_category.keys())
            amounts = list(expense_by_category.values())
            if sum(amounts) > 0:  # Chỉ vẽ khi có giá trị dương
                colors = [TRANSACTION_CONTRAST['expense']] * len(categories)
                ax1.pie(amounts, labels=categories, colors=colors, autopct='%1.1f%%',
                        textprops={'color': TEXT_CONTRAST['light']})
            ax1.set_title('Chi Tiêu Theo Danh Mục', 
                         fontsize=10, color=TEXT_CONTRAST['light'])
            
        # Thu nhập theo danh mục
        if income_by_category:
            categories = list(income_by_category.keys())
            amounts = list(income_by_category.values())
            if sum(amounts) > 0:  # Chỉ vẽ khi có giá trị dương
                colors = [TRANSACTION_CONTRAST['income']] * len(categories)
                ax2.pie(amounts, labels=categories, colors=colors, autopct='%1.1f%%',
                        textprops={'color': TEXT_CONTRAST['light']})
            ax2.set_title('Thu Nhập Theo Danh Mục', 
                         fontsize=10, color=TEXT_CONTRAST['light'])
            
        # Tiết kiệm theo mục tiêu
        if savings_by_category:
            categories = list(savings_by_category.keys())
            amounts = list(savings_by_category.values())
            if sum(amounts) > 0:  # Chỉ vẽ khi có giá trị dương
                colors = [TRANSACTION_CONTRAST['saving']] * len(categories)
                ax3.pie(amounts, labels=categories, colors=colors, autopct='%1.1f%%',
                        textprops={'color': TEXT_CONTRAST['light']})
            ax3.set_title('Tiết Kiệm Theo Mục Tiêu', 
                         fontsize=10, color=TEXT_CONTRAST['light'])
        
        plt.tight_layout()
        
        # Add to frame
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Add summary text
        total_expense = sum(expense_by_category.values())
        total_income = sum(income_by_category.values())
        total_savings = sum(savings_by_category.values())
        
        summary_text = (
            f"💸 Tổng chi tiêu: {total_expense:,.0f} VND\n"
            f"💵 Tổng thu nhập: {total_income:,.0f} VND\n"
            f"💰 Tổng tiết kiệm: {total_savings:,.0f} VND"
        )
        self.create_summary_frame(parent, "📑 Tổng Kết", summary_text)
        
    def create_assets_report(self, parent):
        """Tạo báo cáo tài sản"""
        # Get data for selected account
        if self.account_var.get() == "Tất cả tài khoản":
            accounts = Account.get_all()
        else:
            try:
                accounts = [next(acc for acc in Account.get_all() 
                               if acc.name == self.account_var.get())]
            except StopIteration:
                # Hiển thị thông báo nếu không tìm thấy tài khoản
                message_frame = ctk.CTkFrame(parent, fg_color=BACKGROUND['dark'])
                message_frame.pack(fill="both", expand=True, padx=20, pady=20)
                
                ctk.CTkLabel(
                    message_frame,
                    text="❌ Không tìm thấy tài khoản",
                    font=("Helvetica", 16, "bold"),
                    text_color=TEXT_CONTRAST['danger']
                ).pack(pady=5)
                
                ctk.CTkLabel(
                    message_frame,
                    text=f"Không tìm thấy tài khoản {self.account_var.get()}.\nVui lòng kiểm tra lại.",
                    font=("Helvetica", 14),
                    text_color=TEXT_CONTRAST['muted']
                ).pack(pady=5)
                return
            
        loans = Loan.get_all()
        savings = Saving.get_all()
        
        # Filter loans and savings for selected account
        if self.account_var.get() != "Tất cả tài khoản":
            account = accounts[0]
            # Lọc khoản vay dựa trên người vay/cho vay
            loans = [loan for loan in loans 
                    if (loan.type == "Vay tiền" and loan.borrower_name == account.name) or
                       (loan.type == "Cho vay" and loan.lender_name == account.name)]
            savings = [saving for saving in savings 
                      if saving.account_id == account.account_id]
        
        # Kiểm tra nếu không có dữ liệu
        if not accounts and not loans and not savings:
            message_frame = ctk.CTkFrame(parent, fg_color=BACKGROUND['dark'])
            message_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            ctk.CTkLabel(
                message_frame,
                text="❌ Không có dữ liệu tài sản",
                font=("Helvetica", 16, "bold"),
                text_color=TEXT_CONTRAST['danger']
            ).pack(pady=5)
            
            ctk.CTkLabel(
                message_frame,
                text=f"Tài khoản {self.account_var.get()} chưa có dữ liệu tài sản nào.\nVui lòng thêm tài khoản, khoản vay hoặc tiết kiệm.",
                font=("Helvetica", 14),
                text_color=TEXT_CONTRAST['muted']
            ).pack(pady=5)
            return
        
        # Calculate totals
        total_assets = sum(acc.balance for acc in accounts)
        total_loans = sum(loan.remaining_principal for loan in loans if loan.type == 'Cho vay')
        total_debts = sum(loan.remaining_principal for loan in loans if loan.type == 'Vay tiền')
        total_savings = sum(saving.current_amount for saving in savings)
        
        net_worth = total_assets + total_loans - total_debts + total_savings
        
        # Tạo biểu đồ chỉ khi có dữ liệu
        if total_assets > 0 or total_loans > 0 or total_debts > 0 or total_savings > 0:
            # Tạo biểu đồ
            fig, ax = plt.subplots(figsize=(12, 5), facecolor=BACKGROUND['dark'])
            
            # Chuẩn bị dữ liệu cho biểu đồ
            labels = ['Tài khoản', 'Cho vay', 'Nợ', 'Tiết kiệm']
            sizes = [total_assets, total_loans, total_debts, total_savings]
            colors = [PRIMARY['main'], SUCCESS['main'], DANGER['main'], WARNING['main']]
            
            # Vẽ biểu đồ tròn
            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                colors=colors,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'color': TEXT_CONTRAST['light']}
            )
            
            # Style cho biểu đồ
            ax.set_facecolor(BACKGROUND['dark'])
            ax.set_title(
                f'Phân Bổ Tài Sản ({self.account_var.get()})',
                fontsize=12,
                color=TEXT_CONTRAST['light'],
                pad=20
            )
            
            # Thêm chú thích
            ax.legend(
                wedges,
                labels,
                title="Thành phần",
                loc="center left",
                bbox_to_anchor=(1, 0, 0.5, 1),
                facecolor=BACKGROUND['dark'],
                labelcolor=TEXT_CONTRAST['light']
            )
            
            plt.tight_layout()
            
            # Add to frame
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
        else:
            ctk.CTkLabel(
                parent,
                text="Không đủ dữ liệu để tạo biểu đồ",
                font=("Helvetica", 14),
                text_color=TEXT_CONTRAST['muted']
            ).pack(pady=20)
        
        # Luôn hiển thị summary text
        summary_text = (
            f"💰 Số dư tài khoản: {total_assets:,.0f} VND\n"
            f"💸 Cho vay: {total_loans:,.0f} VND\n"
            f"💳 Nợ: {total_debts:,.0f} VND\n"
            f"🏦 Tiết kiệm: {total_savings:,.0f} VND\n"
            f"📈 Giá trị ròng: {net_worth:,.0f} VND"
        )
        self.create_summary_frame(parent, "📑 Tổng Kết", summary_text)
        
    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(pady=10)
        
        export_btn = ctk.CTkButton(
            button_frame,
            text="Xuất Excel",
            command=self.export_to_excel,
            width=120
        )
        export_btn.pack(side="right", padx=10)
        
    def export_to_excel(self):
        try:
            # Chọn nơi lưu file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                title="Lưu báo cáo Excel"
            )
            
            if not file_path:
                return

            # Tạo workbook Excel
            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                workbook = writer.book
                
                # Định dạng chung
                header_format = workbook.add_format({
                    'bold': True,
                    'align': 'center',
                    'bg_color': '#D3D3D3'
                })
                
                money_format = workbook.add_format({
                    'num_format': '#,##0',
                    'align': 'right'
                })

                # 1. Sheet Giao Dịch
                transactions = self.get_filtered_transactions()
                account_map = {acc.account_id: acc.name for acc in Account.get_all()}
                
                trans_data = []
                for trans in transactions:
                    trans_data.append({
                        'Ngày': trans.date,
                        'Loại': trans.type,
                        'Số Tiền': trans.amount,
                        'Danh Mục': trans.category,
                        'Tài Khoản': account_map.get(trans.account_id, ""),
                        'Ghi Chú': trans.note
                    })
                
                df_trans = pd.DataFrame(trans_data)
                df_trans.to_excel(writer, sheet_name='Giao Dịch', index=False)
                
                # Định dạng Sheet Giao Dịch
                worksheet = writer.sheets['Giao Dịch']
                for col_num, value in enumerate(df_trans.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('C:C', 15, money_format)
                worksheet.set_column('A:A', 15)
                worksheet.set_column('B:B', 15)
                worksheet.set_column('D:D', 20)
                worksheet.set_column('E:E', 20)
                worksheet.set_column('F:F', 30)

                # 2. Sheet Thống Kê Thu Chi
                total_income = sum(t.amount for t in transactions if t.type == 'Thu nhập')
                total_expense = sum(t.amount for t in transactions if t.type == 'Chi tiêu')
                total_savings = sum(t.amount for t in transactions if t.type == 'Gửi tiết kiệm')
                
                summary_data = {
                    'Chỉ số': ['Tổng thu nhập', 'Tổng chi tiêu', 'Tổng tiết kiệm', 'Chênh lệch'],
                    'Số tiền (VND)': [
                        total_income,
                        total_expense,
                        total_savings,
                        total_income - total_expense - total_savings
                    ]
                }
                df_summary = pd.DataFrame(summary_data)
                df_summary.to_excel(writer, sheet_name='Thống Kê Thu Chi', index=False)
                
                # Định dạng Sheet Thống Kê Thu Chi
                worksheet = writer.sheets['Thống Kê Thu Chi']
                for col_num, value in enumerate(df_summary.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('B:B', 20, money_format)
                worksheet.set_column('A:A', 20)

                # 3. Sheet Chi Tiêu Theo Danh Mục
                expense_by_category = {}
                income_by_category = {}
                savings_by_category = {}
                
                for t in transactions:
                    if t.type == 'Chi tiêu':
                        expense_by_category[t.category] = expense_by_category.get(t.category, 0) + t.amount
                    elif t.type == 'Thu nhập':
                        income_by_category[t.category] = income_by_category.get(t.category, 0) + t.amount
                    elif t.type == 'Gửi tiết kiệm':
                        savings_by_category[t.category] = savings_by_category.get(t.category, 0) + t.amount
                
                category_data = []
                # Chi tiêu theo danh mục
                for category, amount in expense_by_category.items():
                    category_data.append({
                        'Loại': 'Chi tiêu',
                        'Danh Mục': category,
                        'Số Tiền': amount,
                        'Tỷ Lệ': amount/total_expense*100 if total_expense > 0 else 0
                    })
                # Thu nhập theo danh mục
                for category, amount in income_by_category.items():
                    category_data.append({
                        'Loại': 'Thu nhập',
                        'Danh Mục': category,
                        'Số Tiền': amount,
                        'Tỷ Lệ': amount/total_income*100 if total_income > 0 else 0
                    })
                # Tiết kiệm theo mục tiêu
                for category, amount in savings_by_category.items():
                    category_data.append({
                        'Loại': 'Tiết kiệm',
                        'Danh Mục': category,
                        'Số Tiền': amount,
                        'Tỷ Lệ': amount/total_savings*100 if total_savings > 0 else 0
                    })
                
                df_category = pd.DataFrame(category_data)
                df_category.to_excel(writer, sheet_name='Chi Tiêu Theo Danh Mục', index=False)
                
                # Định dạng Sheet Chi Tiêu Theo Danh Mục
                worksheet = writer.sheets['Chi Tiêu Theo Danh Mục']
                for col_num, value in enumerate(df_category.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('C:C', 15, money_format)
                worksheet.set_column('D:D', 10)
                worksheet.set_column('A:B', 20)

                # 4. Sheet Tài Sản
                if self.account_var.get() == "Tất cả tài khoản":
                    accounts = Account.get_all()
                else:
                    accounts = [next(acc for acc in Account.get_all() 
                               if acc.name == self.account_var.get())]
                
                loans = Loan.get_all()
                savings = Saving.get_all()
                
                # Filter loans and savings for selected account
                if self.account_var.get() != "Tất cả tài khoản":
                    account = accounts[0]
                    loans = [loan for loan in loans 
                            if loan.from_account_id == account.account_id 
                            or loan.to_account_id == account.account_id]
                    savings = [saving for saving in savings 
                             if saving.account_id == account.account_id]
                
                # Tài khoản
                account_data = [{
                    'Loại': 'Tài khoản',
                    'Tên': acc.name,
                    'Số Dư': acc.balance
                } for acc in accounts]
                
                # Khoản vay
                loan_data = [{
                    'Loại': loan.type,
                    'Tên': f"{loan.lender_name} -> {loan.borrower_name}",
                    'Số Dư': loan.remaining_principal
                } for loan in loans]
                
                # Tiết kiệm
                saving_data = [{
                    'Loại': 'Tiết kiệm',
                    'Tên': saving.name,
                    'Số Dư': saving.current_amount
                } for saving in savings]
                
                df_assets = pd.DataFrame(account_data + loan_data + saving_data)
                df_assets.to_excel(writer, sheet_name='Ti Sản', index=False)
                
                # Định dạng Sheet Tài Sản
                worksheet = writer.sheets['Ti Sản']
                for col_num, value in enumerate(df_assets.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                worksheet.set_column('C:C', 15, money_format)
                worksheet.set_column('A:B', 30)

            # Thông báo thành công
            messagebox.showinfo("Thành công", f"Đã xuất báo cáo Excel thành công!\nĐường dẫn: {file_path}")
            
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xuất Excel: {str(e)}")

    def create_monthly_chart(self, parent, monthly_stats):
        """Tạo biểu đồ thu chi theo tháng"""
        # Tạo biểu đồ với kích thước nhỏ hơn và nền tối
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.5), facecolor=BACKGROUND['dark'])
        
        # Tăng khoảng cách giữa các subplot và thêm padding
        plt.subplots_adjust(wspace=0.3, left=0.1, right=0.9, bottom=0.15, top=0.85)
        
        # Biểu đồ cột thu chi theo tháng
        months = monthly_stats['month'].tolist()
        x = range(len(months))
        width = 0.2  # Giảm độ rộng của cột
        
        # Đảm bảo có đủ các cột dữ liệu
        for col in ['Thu nhập', 'Chi tiêu', 'Gửi tiết kiệm', 'Chuyển tiền đến', 'Chuyển tiền đi']:
            if col not in monthly_stats.columns:
                monthly_stats[col] = 0
        
        # Vẽ các cột với độ rộng nhỏ hơn và màu sắc tương phản
        bars = []
        positions = [-width*1.5, -width/2, width/2, width*1.5]
        colors = [TRANSACTION_CONTRAST['income'], 
                 TRANSACTION_CONTRAST['expense'],
                 TRANSACTION_CONTRAST['saving'],
                 TRANSACTION_CONTRAST['transfer']]
        labels = ['Thu nhập', 'Chi tiêu', 'Tiết kiệm', 'Chuyển khoản']
        
        # Vẽ biểu đồ cột
        for i, (pos, col, color, label) in enumerate(zip(positions, 
                                                    ['Thu nhập', 'Chi tiêu', 'Gửi tiết kiệm', 
                                                     'Chuyển tiền đến'],
                                                    colors, labels)):
            data = monthly_stats[col].tolist()
            bar = ax1.bar([i + pos for i in x], data, width*0.8, 
                         label=label, color=color)
            bars.append(bar)
        
        # Style cho biểu đồ cột
        ax1.set_title('Thu Chi Theo Tháng', fontsize=9, color=TEXT_CONTRAST['light'], pad=10)
        ax1.set_facecolor(BACKGROUND['dark'])
        ax1.tick_params(axis='both', colors=TEXT_CONTRAST['light'], labelsize=7)
        ax1.set_xticks(x)
        ax1.set_xticklabels(months, rotation=45, ha='right')
        
        # Thêm lưới với style mới
        ax1.grid(True, linestyle='--', alpha=0.1, color=TEXT_CONTRAST['light'])
        
        # Legend với font size nhỏ hơn và vị trí tốt hơn
        ax1.legend(fontsize=7, 
                  loc='upper right',
                  bbox_to_anchor=(1, 1),
                  facecolor=BACKGROUND['dark'],
                  labelcolor=TEXT_CONTRAST['light'])
        
        # Biểu đồ tròn
        totals = [
            monthly_stats['Thu nhập'].sum(),
            monthly_stats['Chi tiêu'].sum(),
            monthly_stats['Gửi tiết kiệm'].sum(),
            monthly_stats['Chuyển tiền đến'].sum()
        ]
        
        if sum(totals) > 0:
            ax2.pie(totals,
                    labels=labels,
                    colors=colors,
                    autopct='%1.1f%%',
                    textprops={'color': TEXT_CONTRAST['light'], 'fontsize': 7})
            ax2.set_title('Tỷ Lệ Thu Chi', 
                         fontsize=9, 
                         color=TEXT_CONTRAST['light'],
                         pad=10)
        
        ax2.set_facecolor(BACKGROUND['dark'])
        
        # Thêm padding cho toàn bộ figure
        plt.tight_layout()
        
        # Thêm biểu đồ vào frame với padding nhỏ hơn
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=5, pady=5)