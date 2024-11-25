import customtkinter as ctk
from tkinter import ttk, messagebox
from models.account import Account
from config.settings import ACCOUNT_TYPES
from .dialog import Dialog
from config.colors import *

class AccountsView:
    def __init__(self, parent):
        self.parent = parent
        self.tree = None
        
    def show(self):
        self.create_title()
        self.create_add_button()
        self.show_accounts_list()
        
    def create_title(self):
        title = ctk.CTkLabel(
            self.parent,
            text="Quản Lý Tài Khoản",
            font=("Helvetica", 24, "bold")
        )
        title.pack(pady=20)
        
    def create_add_button(self):
        button_frame = ctk.CTkFrame(self.parent)
        button_frame.pack(pady=10)
        
        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Thêm Tài Khoản Mới",
            command=self.show_add_dialog,
            font=("Helvetica", 13, "bold"),
            fg_color=SUCCESS['main'],
            hover_color=SUCCESS['hover'],
            text_color=TEXT['light']
        )
        add_btn.pack(side="left", padx=5)
        
        edit_btn = ctk.CTkButton(
            button_frame,
            text="✏️ Chỉnh Sửa",
            command=self.edit_selected_account,
            font=("Helvetica", 13, "bold"),
            fg_color=PRIMARY['main'],
            hover_color=PRIMARY['hover'],
            text_color=TEXT['light']
        )
        edit_btn.pack(side="left", padx=5)
        
        delete_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Xóa",
            command=self.delete_selected_account,
            font=("Helvetica", 13, "bold"),
            fg_color=DANGER['main'],
            hover_color=DANGER['hover'],
            text_color=TEXT['light']
        )
        delete_btn.pack(side="left", padx=5)
        
    def show_accounts_list(self):
        frame = ctk.CTkFrame(self.parent)
        frame.pack(fill="both", padx=20, pady=10, expand=True)
        
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        
        columns = ('ID', 'Tên Tài Khoản', 'Số Dư', 'Loại')
        self.tree = ttk.Treeview(frame, columns=columns, show='headings', 
                                yscrollcommand=scrollbar.set)
        
        scrollbar.config(command=self.tree.yview)
        
        self.tree.heading('ID', text='ID')
        self.tree.heading('Tên Tài Khoản', text='Tên Tài Khoản')
        self.tree.heading('Số Dư', text='Số Dư')
        self.tree.heading('Loại', text='Loại')
        
        self.tree.column('ID', width=50, minwidth=50)
        self.tree.column('Tên Tài Khoản', width=200, minwidth=200)
        self.tree.column('Số Dư', width=150, minwidth=150)
        self.tree.column('Loại', width=150, minwidth=150)
        
        style = ttk.Style()
        style.configure("Treeview",
                       font=('Helvetica', 11),
                       rowheight=35,
                       background=BACKGROUND['dark'],
                       foreground=TEXT_CONTRAST['light'],
                       fieldbackground=BACKGROUND['dark'])
        
        style.configure("Treeview.Heading",
                       font=('Helvetica', 12, 'bold'),
                       background=BACKGROUND['light'],
                       foreground=TEXT_CONTRAST['dark'])
        
        self.tree.tag_configure('bank', 
                              background=PRIMARY['main'],
                              foreground=TEXT_CONTRAST['light'])
        self.tree.tag_configure('cash', 
                              background=SUCCESS['main'],
                              foreground=TEXT_CONTRAST['light'])
        self.tree.tag_configure('ewallet', 
                              background=WARNING['main'],
                              foreground=TEXT_CONTRAST['light'])
        
        self.refresh_accounts_list()
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
    def refresh_accounts_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for account in Account.get_all():
            if account.type == "Tài khoản ngân hàng":
                icon = "🏦"
                tag = 'bank'
            elif account.type == "Tiền mặt":
                icon = "💵"
                tag = 'cash'
            else:
                icon = "💳"
                tag = 'ewallet'
            
            self.tree.insert('', 'end', values=(
                account.account_id,
                f"{icon} {account.name}",
                f"{account.balance:,.0f}",
                account.type
            ), tags=(tag,))
            
    def edit_selected_account(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản cần chỉnh sửa!")
            return
            
        item = selected_items[0]
        account_id = int(self.tree.item(item)['values'][0])
        
        # Tìm tài khoản được chọn
        accounts = Account.get_all()
        account = next((acc for acc in accounts if acc.account_id == account_id), None)
        
        if account:
            self.show_edit_dialog(account)
            
    def show_edit_dialog(self, account):
        dialog = Dialog(self.parent, "Chỉnh Sửa Tài Khoản")
        
        # Account Name
        ctk.CTkLabel(dialog.main_frame, text="Tên Tài Khoản:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog.main_frame)
        name_entry.insert(0, account.name)
        name_entry.pack(pady=5)
        
        # Account Type
        ctk.CTkLabel(dialog.main_frame, text="Loại Tài Khoản:").pack(pady=5)
        type_var = ctk.StringVar(value=account.type)
        type_menu = ctk.CTkOptionMenu(
            dialog.main_frame,
            values=ACCOUNT_TYPES,
            variable=type_var
        )
        type_menu.pack(pady=5)
        
        # Balance
        ctk.CTkLabel(dialog.main_frame, text="Số Dư:").pack(pady=5)
        balance_entry = ctk.CTkEntry(dialog.main_frame)
        balance_entry.insert(0, str(account.balance))
        balance_entry.pack(pady=5)
        
        def save_changes():
            try:
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror("Lỗi", "Vui lòng nhập tên tài khoản!")
                    return
                    
                try:
                    balance = float(balance_entry.get())
                    if balance < 0:
                        messagebox.showerror("Lỗi", "Số dư không thể âm!")
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Số dư không hợp lệ!")
                    return
                
                # Kiểm tra trùng lặp (trừ chính nó)
                account_type = type_var.get()
                existing_accounts = Account.get_all()
                for acc in existing_accounts:
                    if (acc.name.lower() == name.lower() and 
                        acc.type == account_type and 
                        acc.account_id != account.account_id):
                        messagebox.showerror(
                            "Lỗi",
                            f"Tài khoản '{name}' với loại '{account_type}' đã tồn tại!"
                        )
                        return
                
                # Cập nhật tài khoản
                account.name = name
                account.balance = balance
                account.type = account_type
                account.save()
                
                dialog.destroy()
                self.refresh_accounts_list()
                messagebox.showinfo("Thành công", "Đã cập nhật tài khoản thành công!")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")
                
        save_btn = ctk.CTkButton(dialog.main_frame, text="Lưu Thay Đổi", command=save_changes)
        save_btn.pack(pady=20)
        
    def delete_selected_account(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn tài khoản cần xóa!")
            return
            
        item = selected_items[0]
        account_id = int(self.tree.item(item)['values'][0])
        account_name = self.tree.item(item)['values'][1]
        
        # Xác nhận xóa
        if not messagebox.askyesno("Xác nhận", f"Bn có chắc muốn xóa tài khoản '{account_name}'?"):
            return
            
        # Xóa tài khoản
        try:
            Account.delete(account_id)
            self.refresh_accounts_list()
            messagebox.showinfo("Thành công", f"Đã xóa tài khoản '{account_name}'")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể xóa tài khoản: {str(e)}")
        
    def show_add_dialog(self):
        dialog = Dialog(self.parent, "Thêm Tài Khoản Mới")
        
        # Account Name
        ctk.CTkLabel(dialog.main_frame, text="Tên Tài Khoản:").pack(pady=5)
        name_entry = ctk.CTkEntry(dialog.main_frame)
        name_entry.pack(pady=5)
        
        # Account Type
        ctk.CTkLabel(dialog.main_frame, text="Loại Tài Khoản:").pack(pady=5)
        type_var = ctk.StringVar(value=ACCOUNT_TYPES[0])
        type_menu = ctk.CTkOptionMenu(
            dialog.main_frame,
            values=ACCOUNT_TYPES,
            variable=type_var
        )
        type_menu.pack(pady=5)
        
        # Initial Balance
        ctk.CTkLabel(dialog.main_frame, text="Số Dư Ban Đầu:").pack(pady=5)
        balance_entry = ctk.CTkEntry(dialog.main_frame)
        balance_entry.pack(pady=5)
        
        def save_account():
            try:
                # Kiểm tra tên tài khoản trống
                name = name_entry.get().strip()
                if not name:
                    messagebox.showerror("Lỗi", "Vui lòng nhập tên tài khoản!")
                    return
                
                # Kiểm tra số dư
                try:
                    balance = float(balance_entry.get())
                    if balance < 0:
                        messagebox.showerror("Lỗi", "Số dư không thể âm!")
                        return
                except ValueError:
                    messagebox.showerror("Lỗi", "Số dư không hợp lệ!")
                    return
                
                # Kiểm tra tài khoản trùng lặp
                account_type = type_var.get()
                existing_accounts = Account.get_all()
                for account in existing_accounts:
                    if account.name.lower() == name.lower() and account.type == account_type:
                        messagebox.showerror(
                            "Lỗi",
                            f"Tài khoản '{name}' với loại '{account_type}' đã tồn tại!"
                        )
                        return
                
                # Tạo tài khoản mới
                new_id = len(existing_accounts) + 1
                account = Account(
                    account_id=new_id,
                    name=name,
                    balance=balance,
                    type=account_type
                )
                account.save()
                
                dialog.destroy()
                self.refresh_accounts_list()
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {str(e)}")
                
        save_btn = ctk.CTkButton(dialog.main_frame, text="Lưu", command=save_account)
        save_btn.pack(pady=20) 
