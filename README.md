# oop
hehe
# Ứng dụng Quản lý Tài chính Cá nhân

Ứng dụng desktop giúp quản lý tài chính cá nhân được viết bằng Python với giao diện đồ họa CustomTkinter.

## Tính năng chính

- 📊 Theo dõi thu chi
- 💰 Quản lý nhiều tài khoản 
- 💸 Quản lý các khoản vay
- 🎯 Thiết lập mục tiêu tiết kiệm
- 📈 Báo cáo và thống kê
- 🔮 Dự báo tài chính

## Yêu cầu hệ thống

- Python 3.8 trở lên
- Các thư viện được liệt kê trong file requirements.txt

## Cấu trúc dự án
├── finance_manager
│   ├── config
│   │   ├── colors.py
│   │   └── settings.py
│   ├── data
│   │   ├── accounts.csv
│   │   ├── loan_payments.csv
│   │   ├── loans.csv
│   │   ├── savings.csv
│   │   └── transactions.csv
│   ├── main.py
│   ├── models
│   │   ├── account.py
│   │   ├── loan.py
│   │   ├── saving.py
│   │   └── transaction.py
│   ├── utils
│   │   ├── database.py
│   │   ├── loan_manager.py
│   │   └── migrate_loans.py
│   └── views
│       ├── accounts.py
│       ├── dashboard.py
│       ├── dialog.py
│       ├── forecast_view.py
│       ├── loan_view.py
│       ├── loans.py
│       ├── main_window.py
│       ├── reports.py
│       ├── savings.py
│       └── transactions.py
└── requirements.txt
