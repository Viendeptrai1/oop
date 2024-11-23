import customtkinter as ctk

class Dialog(ctk.CTkToplevel):
    def __init__(self, parent, title, size="400x500"):
        super().__init__(parent)
        self.title(title)
        self.geometry(size)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        # Căn chỉnh dialog vào giữa cửa sổ chính
        self.center_on_parent()
        
        # Tạo main frame với scroll
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
    def center_on_parent(self):
        """Căn chỉnh dialog vào giữa cửa sổ chính"""
        self.update_idletasks()
        
        # Lấy kích thước và vị trí cửa sổ chính
        parent = self.master
        parent_width = parent.winfo_width() 
        parent_height = parent.winfo_height()
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        
        # Tính toán vị trí cho dialog
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width - width) // 2
        y = parent_y + (parent_height - height) // 2
        
        # Đặt vị trí cho dialog
        self.geometry(f"+{x}+{y}")
        
    def destroy(self):
        """Đóng dialog"""
        # Xóa tham chiếu đến dialog trong parent
        if hasattr(self.master, 'dialog'):
            self.master.dialog = None
            
        # Gọi phương thức destroy của lớp cha
        super().destroy()