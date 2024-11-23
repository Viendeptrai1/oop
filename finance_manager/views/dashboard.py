import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from models.transaction import Transaction
from models.account import Account
from models.loan import Loan
from models.saving import Saving
from datetime import datetime

class DashboardView:
    def __init__(self, parent):
        self.parent = parent
        
    def show(self):
        # Tạo main scrollable frame với padding lớn hơn
        self.main_frame = ctk.CTkScrollableFrame(
            self.parent,
            fg_color=("gray95", "gray10")
        )
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Tạo layout 2 cột với tỷ lệ 6:4
        self.main_frame.grid_columnconfigure(0, weight=6)  # Cột trái rộng hơn
        self.main_frame.grid_columnconfigure(1, weight=4)  # Cột phải hẹp hơn
        
        # Định nghĩa các màu sắc gradient cho từng section
        COLORS = {
            'overview': ("#3498db", "#2980b9"),  # Xanh dương gradient
            'savings': ("#2ecc71", "#27ae60"),   # Xanh lá gradient
            'loans': ("#e74c3c", "#c0392b"),     # Đỏ gradient
            'transactions': ("#9b59b6", "#8e44ad") # Tím gradient
        }
        
        # Tổng quan tài chính (bên trái trên)
        overview_frame = ctk.CTkFrame(self.main_frame)
        overview_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.create_financial_overview(overview_frame, COLORS['overview'])
        
        # Giao dịch gần đây (bên trái dưới)
        transactions_frame = ctk.CTkFrame(self.main_frame)
        transactions_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.create_recent_transactions(transactions_frame, COLORS['transactions'])
        
        # Frame bên phải
        right_frame = ctk.CTkFrame(self.main_frame)
        right_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        # Danh sách tiết kiệm (bên phải trên)
        self.create_savings_list(right_frame, COLORS['savings'])
        
        # Danh sách khoản vay (bên phải dưới)
        self.create_loans_list(right_frame, COLORS['loans'])

    def create_section_title(self, parent, text, icon, color):
        """Helper function để tạo tiêu đề section với style gradient"""
        title_frame = ctk.CTkFrame(
            parent,
            fg_color=color[0],  # Màu gradient chính
            corner_radius=10
        )
        title_frame.pack(fill="x", padx=15, pady=(10, 5))
        
        # Tạo hiệu ứng gradient bằng frame con
        gradient_frame = ctk.CTkFrame(
            title_frame,
            fg_color=color[1],  # Màu gradient phụ
            corner_radius=10
        )
        gradient_frame.pack(fill="x", padx=2, pady=2)
        
        # Icon và text
        title_label = ctk.CTkLabel(
            gradient_frame,
            text=f"{icon} {text}",
            font=("Helvetica", 18, "bold"),
            text_color="white",
            padx=15,
            pady=10
        )
        title_label.pack(side="left")
        
        return title_frame

    def create_info_box(self, parent, label, value, color):
        """Helper function để tạo box thông tin với style mới"""
        frame = ctk.CTkFrame(
            parent,
            fg_color=("gray90", "gray15"),
            corner_radius=8
        )
        frame.pack(fill="x", padx=15, pady=3)
        
        label_frame = ctk.CTkFrame(frame, fg_color="transparent")
        label_frame.pack(side="left", padx=10, pady=5)
        
        ctk.CTkLabel(
            label_frame,
            text=label,
            font=("Helvetica", 12),
            text_color=("gray20", "gray80")
        ).pack()
        
        value_frame = ctk.CTkFrame(frame, fg_color="transparent")
        value_frame.pack(side="right", padx=10, pady=5)
        
        ctk.CTkLabel(
            value_frame,
            text=value,
            font=("Helvetica", 12, "bold"),
            text_color=color
        ).pack()
        
        return frame

    def create_financial_overview(self, parent, color):
        # Tạo tiêu đề section với màu tương ứng
        self.create_section_title(parent, "Tổng Quan Tài Chính", "💰", color)
        
        # Frame tổng quan với viền và shadow
        overview_frame = ctk.CTkFrame(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        overview_frame.pack(fill="x", padx=10, pady=5)
        
        # Tạo layout 2 cột với tỷ lệ 7:3 (left:right)
        left_col = ctk.CTkFrame(overview_frame, fg_color="transparent")
        left_col.pack(side="left", fill="both", expand=True, padx=10, pady=10, anchor="n")
        
        right_col = ctk.CTkFrame(overview_frame, fg_color="transparent", width=300)
        right_col.pack(side="right", fill="y", padx=10, pady=10, anchor="n")
        right_col.pack_propagate(False)  # Giữ nguyên width đã set
        
        # Tính toán các số liệu
        accounts = Account.get_all()
        total_balance = sum(acc.balance for acc in accounts)
        
        # Lấy dữ liệu giao dịch trong tháng hiện tại
        transactions = Transaction.get_all()
        current_month = datetime.now().strftime("%Y-%m")
        monthly_transactions = [t for t in transactions if t.date.startswith(current_month)]
        
        total_income = sum(t.amount for t in monthly_transactions if t.type == "Thu nhập")
        total_expense = sum(t.amount for t in monthly_transactions if t.type == "Chi tiêu")
        total_savings = sum(t.amount for t in monthly_transactions if t.type == "Gửi tiết kiệm")
        
        # Tạo biểu đồ tròn với kích thước lớn hơn
        fig, ax = plt.subplots(figsize=(4.5, 4.5), facecolor='none')  # Tăng từ 3.2 lên 4.5
        ax.set_facecolor('none')
        
        # Data cho biểu đồ
        data = [total_income, total_expense, total_savings]
        labels = ['Thu', 'Chi', 'Tiết kiệm']
        colors = ['#2ecc71', '#e74c3c', '#3498db']
        
        # Tính toán vị trí tốt nhất cho text
        def make_autopct(values):
            def my_autopct(pct):
                if pct > 1:
                    return f'{pct:.0f}%'  # Bỏ khoảng trắng trước %
                return ''
            return my_autopct
        
        # Vẽ biểu đồ tròn với font size nhỏ hơn
        wedges, texts, autotexts = ax.pie(
            data,
            labels=labels,
            colors=colors,
            autopct=make_autopct(data),
            pctdistance=0.75,
            labeldistance=1.1,
            textprops={
                'fontsize': 4,  # Giảm từ 6 xuống 4
                'color': 'white',
                'weight': 'bold'
            }
        )
        
        # Tùy chỉnh style cho text phần trăm
        plt.setp(autotexts, 
            size=5,  # Giảm từ 7 xuống 5
            weight='bold',
            color='white',
            bbox=dict(
                boxstyle='round,pad=0.2',
                fc='#2c3e50',
                ec='#34495e',
                alpha=0.8
            )
        )
        
        # Tùy chỉnh style cho labels
        plt.setp(texts, 
            size=4,  # Giảm từ 6 xuống 4
            weight='bold',
            color='white'
        )
        
        # Thêm tiêu đề nhỏ hơn
        ax.set_title(
            "Thu Chi " + datetime.now().strftime("%m/%Y"), 
            pad=2,
            fontsize=5,  # Giảm từ 7 xuống 5
            color='white',
            weight='bold'
        )
        
        # Thêm biểu đồ vào frame với padding lớn hơn và màu nền phù hợp
        canvas = FigureCanvasTkAgg(fig, master=right_col)
        canvas.draw()
        widget = canvas.get_tk_widget()
        widget.configure(bg='#2c3e50')  # Đặt màu nền cho widget chứa biểu đồ
        widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Thông tin số dư bên trái
        self.create_info_box(
            left_col,
            "💵 Tổng số dư:",
            f"{total_balance:,.0f} VND",
            "#2ecc71"
        )
        
        # Divider
        ctk.CTkFrame(
            left_col,
            height=1,
            fg_color=("gray80", "gray30")
        ).pack(fill="x", pady=8)
        
        # Thông tin thu chi tháng
        monthly_stats = [
            ("📈 Thu nhập:", total_income, "#2ecc71"),
            ("📉 Chi tiêu:", total_expense, "#e74c3c"),
            ("💰 Tiết kiệm:", total_savings, "#3498db"),
            ("⚖️ Chênh lệch:", total_income - total_expense - total_savings, 
             "#2ecc71" if total_income > (total_expense + total_savings) else "#e74c3c")
        ]
        
        for label, amount, color in monthly_stats:
            self.create_info_box(left_col, label, f"{amount:,.0f} VND", color)
        
        # Divider
        ctk.CTkFrame(
            left_col,
            height=1,
            fg_color=("gray80", "gray30")
        ).pack(fill="x", pady=8)
        
        # Chi tiết tài khoản
        account_label = ctk.CTkLabel(
            left_col,
            text="🏦 Chi tiết tài khoản",
            font=("Helvetica", 12, "bold"),
            anchor="w"
        )
        account_label.pack(fill="x", pady=(5, 8))
        
        for acc in accounts:
            acc_frame = ctk.CTkFrame(
                left_col,
                fg_color=("gray95", "gray20"),
                corner_radius=6
            )
            acc_frame.pack(fill="x", pady=2)
            
            # Chọn icon dựa vào loại tài khoản
            if acc.type == "Tài khoản ngân hàng":
                icon = "🏦"
                bg_color = "#3498db"  # Màu xanh dương cho ngân hàng
            elif acc.type == "Tiền mặt":
                icon = "💵"
                bg_color = "#2ecc71"  # Màu xanh lá cho tiền mặt
            else:  # Ví điện tử
                icon = "💳"
                bg_color = "#9b59b6"  # Màu tím cho ví điện tử
            
            # Cập nhật màu nền cho frame tài khoản
            acc_frame.configure(fg_color=bg_color)
            
            name_label = ctk.CTkLabel(
                acc_frame,
                text=f"{icon} {acc.name}",
                font=("Helvetica", 11),
                text_color="white",  # Đổi màu chữ thành trắng để tương phản với nền
                anchor="w"
            )
            name_label.pack(side="left", padx=8, pady=5)
            
            balance_label = ctk.CTkLabel(
                acc_frame,
                text=f"{acc.balance:,.0f} VND",
                font=("Helvetica", 11, "bold"),
                text_color="white",  # Đổi màu chữ thành trắng
            )
            balance_label.pack(side="right", padx=8, pady=5)

    def create_savings_list(self, parent, color):
        # Tạo tiêu đề section v��i màu tương ứng
        self.create_section_title(parent, "Mục Tiêu Tiết Kiệm", "🎯", color)
        
        # Frame tiết kiệm
        savings_frame = ctk.CTkFrame(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        savings_frame.pack(fill="x", padx=10, pady=5)
        
        # Danh sách tiết kiệm
        savings = Saving.get_all()
        
        if not savings:
            ctk.CTkLabel(
                savings_frame,
                text="Chưa có mục tiêu tiết kiệm nào",
                font=("Helvetica", 14)
            ).pack(pady=10)
        else:
            for saving in savings:
                goal_frame = ctk.CTkFrame(
                    savings_frame,
                    fg_color=("gray90", "gray15"),
                    corner_radius=8
                )
                goal_frame.pack(fill="x", padx=15, pady=5)
                
                # Tên mục tiêu với style mới
                name_label = ctk.CTkLabel(
                    goal_frame,
                    text=saving.name,
                    font=("Helvetica", 14, "bold"),
                    anchor="w"
                )
                name_label.pack(fill="x", padx=10, pady=(10, 5))
                
                # Progress bar với style mới
                progress = ctk.CTkProgressBar(
                    goal_frame,
                    progress_color=color[0],
                    height=15,
                    corner_radius=5
                )
                progress.pack(fill="x", padx=10, pady=5)
                progress.set(saving.progress / 100)
                
                # Thông tin với layout mới
                info_frame = ctk.CTkFrame(goal_frame, fg_color="transparent")
                info_frame.pack(fill="x", padx=10, pady=(5, 10))
                
                amount_text = f"{saving.current_amount:,.0f} / {saving.target_amount:,.0f} VND"
                progress_text = f"{saving.progress:.1f}%"
                deadline_text = f"Hạn: {saving.deadline}"
                
                ctk.CTkLabel(
                    info_frame,
                    text=amount_text,
                    font=("Helvetica", 12)
                ).pack(side="left")
                
                ctk.CTkLabel(
                    info_frame,
                    text=progress_text,
                    font=("Helvetica", 12, "bold"),
                    text_color=color[0]
                ).pack(side="right")
                
                ctk.CTkLabel(
                    info_frame,
                    text=deadline_text,
                    font=("Helvetica", 12),
                    text_color=("gray40", "gray60")
                ).pack(side="right", padx=20)

    def create_loans_list(self, parent, color):
        # Tạo tiêu đề section với màu tương ứng
        self.create_section_title(parent, "Khoản Vay & Cho Vay", "💸", color)
        
        # Frame khoản vay
        loans_frame = ctk.CTkFrame(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        loans_frame.pack(fill="x", padx=10, pady=5)
        
        # Lấy danh sách khoản vay sắp đến hạn và quá hạn
        loans = Loan.get_all()
        due_loans = []
        overdue_loans = []
        
        for loan in loans:
            loan.check_due_status()  # Cập nhật trạng thái
            if loan.status == "Quá hạn":
                overdue_loans.append(loan)
            else:
                # Kiểm tra khoản vay sắp đến hạn (còn 7 ngày)
                due_date = datetime.strptime(loan.due_date, "%Y-%m-%d")
                days_remaining = (due_date - datetime.now()).days
                if 0 < days_remaining <= 7:
                    due_loans.append((loan, days_remaining))

        # Hiển thị thông báo khoản vay quá hạn
        if overdue_loans:
            overdue_frame = ctk.CTkFrame(
                loans_frame, 
                fg_color="#c0392b",  # Màu đỏ đậm cho cảnh báo
                corner_radius=8
            )
            overdue_frame.pack(fill="x", padx=10, pady=5)
            
            overdue_label = ctk.CTkLabel(
                overdue_frame,
                text="🚨 KHOẢN VAY QUÁ HẠN",
                font=("Helvetica", 14, "bold"),
                text_color="white"
            )
            overdue_label.pack(pady=(10, 5))
            
            for loan in overdue_loans:
                loan_info = ctk.CTkFrame(
                    overdue_frame,
                    fg_color="#e74c3c",  # Màu đỏ nhạt hơn
                    corner_radius=5
                )
                loan_info.pack(fill="x", padx=10, pady=2)
                
                icon = "💸" if loan.type == "Vay tiền" else "💰"
                
                ctk.CTkLabel(
                    loan_info,
                    text=f"{icon} {loan.type}: {loan.lender_name} → {loan.borrower_name}",
                    font=("Helvetica", 12, "bold"),
                    text_color="white"
                ).pack(anchor="w", padx=10, pady=(5, 0))
                
                ctk.CTkLabel(
                    loan_info,
                    text=f"💵 Còn nợ: {loan.remaining_principal:,.0f} VND",
                    font=("Helvetica", 11),
                    text_color="white"
                ).pack(anchor="w", padx=10, pady=(0, 5))
                
                ctk.CTkLabel(
                    loan_info,
                    text=f"⚠️ Đã quá hạn từ: {loan.due_date}",
                    font=("Helvetica", 11),
                    text_color="#ffd700"  # Màu vàng cho cảnh báo
                ).pack(anchor="w", padx=10, pady=(0, 5))

        # Hiển thị thông báo khoản vay sắp đến hạn
        if due_loans:
            due_frame = ctk.CTkFrame(
                loans_frame,
                fg_color="#d35400",  # Màu cam đậm
                corner_radius=8
            )
            due_frame.pack(fill="x", padx=10, pady=5)
            
            due_label = ctk.CTkLabel(
                due_frame,
                text="⏰ KHOẢN VAY SẮP ĐẾN HẠN",
                font=("Helvetica", 14, "bold"),
                text_color="white"
            )
            due_label.pack(pady=(10, 5))
            
            for loan, days in due_loans:
                loan_info = ctk.CTkFrame(
                    due_frame,
                    fg_color="#e67e22",  # Màu cam nhạt hơn
                    corner_radius=5
                )
                loan_info.pack(fill="x", padx=10, pady=2)
                
                icon = "💸" if loan.type == "Vay tiền" else "💰"
                
                ctk.CTkLabel(
                    loan_info,
                    text=f"{icon} {loan.type}: {loan.lender_name} → {loan.borrower_name}",
                    font=("Helvetica", 12, "bold"),
                    text_color="white"
                ).pack(anchor="w", padx=10, pady=(5, 0))
                
                ctk.CTkLabel(
                    loan_info,
                    text=f"💵 Còn nợ: {loan.remaining_principal:,.0f} VND",
                    font=("Helvetica", 11),
                    text_color="white"
                ).pack(anchor="w", padx=10, pady=(0, 5))
                
                ctk.CTkLabel(
                    loan_info,
                    text=f"⏳ Còn {days} ngày (đến {loan.due_date})",
                    font=("Helvetica", 11),
                    text_color="#ffd700"  # Màu vàng cho thời gian
                ).pack(anchor="w", padx=10, pady=(0, 5))

        # Hiển thị khi không có khoản vay nào cần chú ý
        if not overdue_loans and not due_loans:
            no_alert_frame = ctk.CTkFrame(
                loans_frame,
                fg_color="#27ae60",  # Màu xanh lá
                corner_radius=8
            )
            no_alert_frame.pack(fill="x", padx=10, pady=5)
            
            ctk.CTkLabel(
                no_alert_frame,
                text="✅ Không có khoản vay nào cần chú ý",
                font=("Helvetica", 14, "bold"),
                text_color="white"
            ).pack(pady=10)

        # Danh sách khoản vay
        if not loans:
            ctk.CTkLabel(
                loans_frame,
                text="Không có khoản vay nào",
                font=("Helvetica", 14)
            ).pack(pady=10)
        else:
            for loan in loans:
                loan_frame = ctk.CTkFrame(loans_frame)
                loan_frame.pack(fill="x", padx=10, pady=5)
                
                # Header với loại và trạng thái
                header_frame = ctk.CTkFrame(loan_frame, fg_color="transparent")
                header_frame.pack(fill="x", padx=5, pady=2)
                
                # Chọn icon và màu sắc dựa trên loại và trạng thái
                if loan.type == "Vay tiền":
                    icon = "💸"
                    bg_color = "#e74c3c"  # Đỏ cho khoản vay
                else:  # Cho vay
                    icon = "💰"
                    bg_color = "#2ecc71"  # Xanh lá cho cho vay
                    
                if loan.status == "Quá hạn":
                    status_icon = "⚠️"
                    status_color = "#c0392b"  # Đỏ đậm
                elif loan.status == "Đã trả":
                    status_icon = "✅"
                    status_color = "#27ae60"  # Xanh lá đậm
                else:
                    status_icon = "⏳"
                    status_color = "#f39c12"  # Cam
                
                loan_frame.configure(fg_color=bg_color)
                
                ctk.CTkLabel(
                    header_frame,
                    text=f"{icon} {loan.type}: {loan.lender_name} → {loan.borrower_name}",
                    font=("Helvetica", 12, "bold"),
                    text_color="white"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    header_frame,
                    text=f"{status_icon} {loan.status}",
                    font=("Helvetica", 12),
                    text_color="white"
                ).pack(side="right")
                
                # Thông tin chi tiết
                info_frame = ctk.CTkFrame(loan_frame, fg_color="transparent")
                info_frame.pack(fill="x", padx=5)
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"💵 Còn nợ: {loan.remaining_principal:,.0f} VND",
                    font=("Helvetica", 11),
                    text_color="white"
                ).pack(side="left")
                
                ctk.CTkLabel(
                    info_frame,
                    text=f"📅 Đến hạn: {loan.due_date}",
                    font=("Helvetica", 11),
                    text_color="white"
                ).pack(side="right")

    def create_recent_transactions(self, parent, color):
        # Tạo tiêu đề section với màu tương ứng
        self.create_section_title(parent, "Giao Dịch Gần Đây", "📝", color)
        
        # Frame giao dịch
        trans_frame = ctk.CTkFrame(
            parent,
            corner_radius=10,
            border_width=1,
            border_color=("gray70", "gray30")
        )
        trans_frame.pack(fill="x", padx=10, pady=5)
        
        # Tạo Treeview với style mới
        columns = ('Ngày', 'Loại', 'Số Tiền', 'Danh Mục', 'Tài Khoản')
        tree = ttk.Treeview(trans_frame, columns=columns, show='headings', height=5)
        
        # Định dạng cột
        tree.column('Ngày', width=100, anchor='center')
        tree.column('Loại', width=100, anchor='center')
        tree.column('Số Tiền', width=150, anchor='e')  # Căn phải cho số tiền
        tree.column('Danh Mục', width=200)
        tree.column('Tài Khoản', width=150)
        
        for col in columns:
            tree.heading(col, text=col)
        
        # Style cho Treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            font=('Helvetica', 11),
            rowheight=30,
            background="#2c3e50",
            foreground="white",
            fieldbackground="#2c3e50"
        )
        
        style.configure(
            "Treeview.Heading",
            font=('Helvetica', 12, 'bold'),
            background="#34495e",
            foreground="white"
        )
        
        # Tạo tags cho các loại giao dịch
        tree.tag_configure('income', foreground='#2ecc71')    # Xanh lá cho thu nhập
        tree.tag_configure('expense', foreground='#e74c3c')   # Đỏ cho chi tiêu
        tree.tag_configure('transfer', foreground='#3498db')  # Xanh dương cho chuyển khoản
        tree.tag_configure('saving', foreground='#f1c40f')    # Vàng cho tiết kiệm
        tree.tag_configure('even_row', background='#2c3e50')  # Màu nền cho dòng chẵn
        tree.tag_configure('odd_row', background='#34495e')   # Màu nền cho dòng lẻ
        
        # Thêm dữ liệu
        transactions = Transaction.get_recent(limit=5)
        accounts = {acc.account_id: acc.name for acc in Account.get_all()}
        
        for i, trans in enumerate(transactions):
            values = (
                trans.date,
                trans.type,
                f"{trans.amount:,.0f}",
                trans.category,
                accounts.get(trans.account_id, "")
            )
            
            # Xác định tags cho từng dòng
            tags = []
            if trans.type == 'Thu nhập':
                tags.append('income')
            elif trans.type == 'Chi tiêu':
                tags.append('expense')
            elif trans.type == 'Chuyển tiền':
                tags.append('transfer')
            elif trans.type == 'Gửi tiết kiệm':
                tags.append('saving')
            
            # Thêm tag cho dòng chẵn/lẻ
            tags.append('even_row' if i % 2 == 0 else 'odd_row')
            
            # Thêm dòng vào bảng với tags
            tree.insert('', 'end', values=values, tags=tags)
        
        tree.pack(fill="x", padx=10, pady=10)
        
        # Thêm chú thích màu
        legend_frame = ctk.CTkFrame(trans_frame, fg_color="transparent")
        legend_frame.pack(fill="x", padx=10, pady=5)
        
        # Thu nhập
        income_label = ctk.CTkLabel(
            legend_frame,
            text="● Thu nhập",
            text_color="#2ecc71",
            font=("Helvetica", 12, "bold")
        )
        income_label.pack(side="left", padx=10)
        
        # Chi tiêu
        expense_label = ctk.CTkLabel(
            legend_frame,
            text="● Chi tiêu",
            text_color="#e74c3c",
            font=("Helvetica", 12, "bold")
        )
        expense_label.pack(side="left", padx=10)
        
        # Chuyển khoản
        transfer_label = ctk.CTkLabel(
            legend_frame,
            text="● Chuyển khoản",
            text_color="#3498db",
            font=("Helvetica", 12, "bold")
        )
        transfer_label.pack(side="left", padx=10)
        
        # Tiết kiệm
        saving_label = ctk.CTkLabel(
            legend_frame,
            text="● Tiết kiệm",
            text_color="#f1c40f",
            font=("Helvetica", 12, "bold")
        )
        saving_label.pack(side="left", padx=10) 