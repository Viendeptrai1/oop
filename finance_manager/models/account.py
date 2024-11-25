import pandas as pd
from dataclasses import dataclass
from config.settings import ACCOUNTS_FILE

@dataclass
class Account:
    account_id: int
    name: str
    balance: float
    type: str
    
    @classmethod
    def get_all(cls):
        try:
            df = pd.read_csv(ACCOUNTS_FILE)
            return [cls(**row) for _, row in df.iterrows()]
        except FileNotFoundError:
            return []
    
    @classmethod
    def get_by_id(cls, account_id: int):
        try:
            df = pd.read_csv(ACCOUNTS_FILE)
            account_data = df[df['account_id'] == account_id].iloc[0]
            return cls(**account_data)
        except (FileNotFoundError, IndexError):
            return None
            
    def save(self):
        try:
            df = pd.read_csv(ACCOUNTS_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=['account_id', 'name', 'balance', 'type'])
        
        new_data = pd.DataFrame([{
            'account_id': self.account_id,
            'name': self.name,
            'balance': self.balance,
            'type': self.type
        }])
        
        # Nếu tài khoản đã tồn tại, cập nhật thông tin
        if self.account_id in df['account_id'].values:
            df = df[df['account_id'] != self.account_id]  # Xóa dòng cũ
            df = pd.concat([df, new_data], ignore_index=True)  # Thêm dòng mới
        else:
            # Nếu là tài khoản mới, thêm vào cuối
            df = pd.concat([df, new_data], ignore_index=True)
            
        # Sắp xếp theo account_id để duy trì thứ tự
        df = df.sort_values('account_id').reset_index(drop=True)
        df.to_csv(ACCOUNTS_FILE, index=False)
        
    @classmethod
    def delete(cls, account_id: int):
        try:
            df = pd.read_csv(ACCOUNTS_FILE)
            if account_id in df['account_id'].values:
                df = df[df['account_id'] != account_id]
                # Reset và cập nhật lại các account_id
                df = df.reset_index(drop=True)
                df['account_id'] = df.index + 1
                df.to_csv(ACCOUNTS_FILE, index=False)
                return True
            return False
        except FileNotFoundError:
            return False 
