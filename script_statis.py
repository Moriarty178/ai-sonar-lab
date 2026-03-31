import pandas as pd
import psycopg2
from psycopg2 import Error
import os
from datetime import datetime

# ====================== CẤU HÌNH ======================
EXCEL_PATH = r"C:\Users\Moriarty\Documents\thong_ke_user.xlsx"

# Thông tin kết nối PostgreSQL - BẠN PHẢI SỬA
DB_CONFIG = {
    "dbname": "litellm",
    "user": "your_username",  # ← Thay bằng username của bạn
    "password": "your_password",  # ← Thay bằng password
    "host": "localhost",  # ← Thường là "localhost" hoặc IP server
    "port": "5432"
}

TABLE_NAME = "litellm_user_talbe"
DATE_THRESHOLD = "2026-03-10"  # updated_at >= ngày này


# =====================================================

def main():
    try:
        # 1. Kết nối Database
        print("🔌 Đang kết nối đến PostgreSQL...")
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Kết nối database thành công!")

        # 2. Đọc file Excel
        if not os.path.exists(EXCEL_PATH):
            print(f"❌ Không tìm thấy file: {EXCEL_PATH}")
            return

        df = pd.read_excel(EXCEL_PATH)
        print(f"📊 Đã đọc file Excel với {len(df)} dòng.")

        # Đảm bảo có các cột cần thiết
        if "Email" not in df.columns:
            print("❌ File phải có cột 'Email'!")
            return

        # Tạo cột nếu chưa tồn tại
        for col in ["Spend cũ", "Spend mới", "Spend sử dụng trong ngày"]:
            if col not in df.columns:
                df[col] = None

        # ====================== BƯỚC 1: Ghi đè Cột B = Cột C (nếu có) ======================
        print("🔄 Bước 1: Ghi đè Spend cũ (Cột B) = Spend mới (Cột C) của lần trước...")
        if "Spend mới" in df.columns:
            df["Spend cũ"] = df["Spend mới"].copy()  # Ghi đè B = C
        else:
            df["Spend cũ"] = 0.0

        # Reset cột Spend mới và Spend sử dụng trong ngày để chuẩn bị ghi dữ liệu mới
        df["Spend mới"] = None
        df["Spend sử dụng trong ngày"] = None

        # ====================== BƯỚC 2 & 3: Duyệt từng email và lấy Spend mới từ DB ======================
        print(f"🚀 Bắt đầu cập nhật Spend mới cho {len(df)} email...")

        updated_count = 0

        for idx, row in df.iterrows():
            email = str(row["Email"]).strip() if pd.notna(row["Email"]) else ""

            if not email or email.lower() in ["nan", ""]:
                continue

            # Query lấy spend mới nhất theo điều kiện
            query = f"""
                SELECT spend 
                FROM {TABLE_NAME}
                WHERE user_email = %s 
                  AND updated_at >= %s 
                  AND spend > 0
                ORDER BY updated_at DESC
                LIMIT 1
            """

            try:
                with conn.cursor() as cur:
                    cur.execute(query, (email, DATE_THRESHOLD))
                    result = cur.fetchone()

                    spend_moi = float(result[0]) if result and result[0] is not None else 0.0

                    # Ghi vào cột C
                    df.at[idx, "Spend mới"] = spend_moi

                    # Tính Spend sử dụng trong ngày = C - B
                    spend_cu = float(row["Spend cũ"]) if pd.notna(row["Spend cũ"]) else 0.0
                    spend_ngay = spend_moi - spend_cu

                    df.at[idx, "Spend sử dụng trong ngày"] = round(spend_ngay, 4)  # làm tròn 4 chữ số

                    updated_count += 1
                    print(f"   ✅ {email} | Cũ: {spend_cu} → Mới: {spend_moi} | Dùng hôm nay: {spend_ngay}")

            except Exception as e:
                print(f"   ❌ Lỗi khi xử lý {email}: {e}")
                df.at[idx, "Spend mới"] = 0.0
                df.at[idx, "Spend sử dụng trong ngày"] = 0.0

        # ====================== LƯU FILE ======================
        df.to_excel(EXCEL_PATH, index=False)

        print("\n🎉 HOÀN THÀNH!")
        print(f"   - Đã xử lý {updated_count} người dùng.")
        print(f"   - File được cập nhật tại: {EXCEL_PATH}")
        print("   Cấu trúc hiện tại: Email | Spend cũ | Spend mới | Spend sử dụng trong ngày")

    except Error as db_error:
        print(f"❌ Lỗi database: {db_error}")
    except Exception as e:
        print(f"❌ Lỗi: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()
            print("🔌 Đã đóng kết nối database.")


if __name__ == "__main__":
    main()