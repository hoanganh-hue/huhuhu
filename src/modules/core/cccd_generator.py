#!/usr/bin/env python3
"""
Feature-1: CCCD Generator
Tạo số CCCD (Căn cước Công dân) hợp lệ
"""

import random
import logging
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class CCCDData:
    """Dữ liệu CCCD"""
    cccd: str
    province_code: str
    gender: str
    birth_year: int
    birth_date: str
    full_name: str
    address: str

class CCCDGenerator:
    """Generator tạo CCCD hợp lệ"""
    
    # Mã tỉnh/thành phố (63 tỉnh/thành)
    PROVINCE_CODES = {
        "001": "Hà Nội", "002": "TP. Hồ Chí Minh", "003": "Hải Phòng",
        "004": "Đà Nẵng", "005": "Hà Giang", "006": "Cao Bằng",
        "007": "Lai Châu", "008": "Lào Cai", "009": "Tuyên Quang",
        "010": "Lạng Sơn", "011": "Bắc Kạn", "012": "Thái Nguyên",
        "013": "Yên Bái", "014": "Sơn La", "015": "Phú Thọ",
        "016": "Vĩnh Phúc", "017": "Bắc Ninh", "018": "Quảng Ninh",
        "019": "Bắc Giang", "020": "Lạng Sơn", "021": "Hà Nam",
        "022": "Hải Dương", "023": "Hưng Yên", "024": "Thái Bình",
        "025": "Hà Tĩnh", "026": "Quảng Bình", "027": "Quảng Trị",
        "028": "Thừa Thiên Huế", "029": "Quảng Nam", "030": "Quảng Ngãi",
        "031": "Bình Định", "032": "Phú Yên", "033": "Khánh Hòa",
        "034": "Ninh Thuận", "035": "Bình Thuận", "036": "Kon Tum",
        "037": "Gia Lai", "038": "Đắk Lắk", "039": "Đắk Nông",
        "040": "Lâm Đồng", "041": "Bình Phước", "042": "Tây Ninh",
        "043": "Bình Dương", "044": "Đồng Nai", "045": "Bà Rịa - Vũng Tàu",
        "046": "Long An", "047": "Tiền Giang", "048": "Bến Tre",
        "049": "Trà Vinh", "050": "Vĩnh Long", "051": "Đồng Tháp",
        "052": "An Giang", "053": "Kiên Giang", "054": "Cần Thơ",
        "055": "Hậu Giang", "056": "Sóc Trăng", "057": "Bạc Liêu",
        "058": "Cà Mau", "059": "Điện Biên", "060": "Lai Châu",
        "061": "Sơn La", "062": "Yên Bái", "063": "Hoà Bình"
    }
    
    # Danh sách họ tên phổ biến
    FIRST_NAMES = [
        "Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Phan", "Vũ", "Võ",
        "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý", "Đinh"
    ]
    
    MIDDLE_NAMES = [
        "Văn", "Thị", "Đức", "Minh", "Quang", "Hữu", "Công", "Đình",
        "Xuân", "Thu", "Hạ", "Đông", "Thanh", "Bình", "Hòa", "An"
    ]
    
    LAST_NAMES = [
        "An", "Bình", "Cường", "Dũng", "Đức", "Giang", "Hải", "Hoàng",
        "Hùng", "Khánh", "Linh", "Minh", "Nam", "Phong", "Quang", "Sơn",
        "Thành", "Tuấn", "Việt", "Xuân", "Yến", "Hương", "Lan", "Mai",
        "Nga", "Oanh", "Phương", "Quỳnh", "Thảo", "Uyên", "Vân", "Xoan"
    ]
    
    # Địa chỉ theo tỉnh
    ADDRESSES = {
        "001": "Hà Nội", "002": "TP. Hồ Chí Minh", "003": "Hải Phòng",
        "004": "Đà Nẵng", "005": "Hà Giang", "006": "Cao Bằng",
        "007": "Lai Châu", "008": "Lào Cai", "009": "Tuyên Quang",
        "010": "Lạng Sơn", "011": "Bắc Kạn", "012": "Thái Nguyên",
        "013": "Yên Bái", "014": "Sơn La", "015": "Phú Thọ",
        "016": "Vĩnh Phúc", "017": "Bắc Ninh", "018": "Quảng Ninh",
        "019": "Bắc Giang", "020": "Lạng Sơn", "021": "Hà Nam",
        "022": "Hải Dương", "023": "Hưng Yên", "024": "Thái Bình",
        "025": "Hà Tĩnh", "026": "Quảng Bình", "027": "Quảng Trị",
        "028": "Thừa Thiên Huế", "029": "Quảng Nam", "030": "Quảng Ngãi",
        "031": "Bình Định", "032": "Phú Yên", "033": "Khánh Hòa",
        "034": "Ninh Thuận", "035": "Bình Thuận", "036": "Kon Tum",
        "037": "Gia Lai", "038": "Đắk Lắk", "039": "Đắk Nông",
        "040": "Lâm Đồng", "041": "Bình Phước", "042": "Tây Ninh",
        "043": "Bình Dương", "044": "Đồng Nai", "045": "Bà Rịa - Vũng Tàu",
        "046": "Long An", "047": "Tiền Giang", "048": "Bến Tre",
        "049": "Trà Vinh", "050": "Vĩnh Long", "051": "Đồng Tháp",
        "052": "An Giang", "053": "Kiên Giang", "054": "Cần Thơ",
        "055": "Hậu Giang", "056": "Sóc Trăng", "057": "Bạc Liêu",
        "058": "Cà Mau", "059": "Điện Biên", "060": "Lai Châu",
        "061": "Sơn La", "062": "Yên Bái", "063": "Hoà Bình"
    }
    
    def __init__(self, config: Dict[str, Any]):
        """Khởi tạo generator"""
        self.config = config
        self.count = config.get('cccd_count', 1000)
        self.province_code = config.get('province_code', '001')
        self.gender = config.get('gender', 'Nam')
        self.birth_year_from = config.get('birth_year_from', 1990)
        self.birth_year_to = config.get('birth_year_to', 2000)
        
        logger.info("✅ CCCD Generator initialized")
        logger.info(f"📊 Count: {self.count}")
        logger.info(f"🏛️ Province: {self.PROVINCE_CODES.get(self.province_code, 'Unknown')}")
        logger.info(f"👤 Gender: {self.gender}")
        logger.info(f"📅 Birth year range: {self.birth_year_from}-{self.birth_year_to}")
    
    def generate_cccd(self) -> str:
        """Tạo số CCCD hợp lệ"""
        # Cấu trúc: 12 chữ số
        # 3 chữ số đầu: mã tỉnh/thành phố
        # 1 chữ số: giới tính (nam: 0-4, nữ: 5-9)
        # 2 chữ số: năm sinh (2 chữ số cuối)
        # 6 chữ số: số thứ tự
        
        # Mã tỉnh/thành phố
        province_part = self.province_code
        
        # Giới tính
        if self.gender == "Nam":
            gender_part = str(random.randint(0, 4))
        else:
            gender_part = str(random.randint(5, 9))
        
        # Năm sinh
        birth_year = random.randint(self.birth_year_from, self.birth_year_to)
        year_part = str(birth_year)[-2:]
        
        # Số thứ tự (6 chữ số)
        sequence_part = str(random.randint(100000, 999999))
        
        # Ghép thành CCCD
        cccd = province_part + gender_part + year_part + sequence_part
        
        return cccd
    
    def generate_name(self, gender: str) -> str:
        """Tạo tên đầy đủ"""
        first_name = random.choice(self.FIRST_NAMES)
        middle_name = random.choice(self.MIDDLE_NAMES)
        last_name = random.choice(self.LAST_NAMES)
        
        return f"{first_name} {middle_name} {last_name}"
    
    def generate_birth_date(self, birth_year: int) -> str:
        """Tạo ngày sinh"""
        month = random.randint(1, 12)
        day = random.randint(1, 28)  # Đơn giản hóa, lấy 28 để tránh lỗi tháng
        
        return f"{birth_year:04d}-{month:02d}-{day:02d}"
    
    def generate_address(self, province_code: str) -> str:
        """Tạo địa chỉ"""
        province_name = self.ADDRESSES.get(province_code, "Hà Nội")
        street_number = random.randint(1, 999)
        street_name = random.choice([
            "Đường Lê Lợi", "Đường Trần Hưng Đạo", "Đường Nguyễn Du",
            "Đường Lý Thường Kiệt", "Đường Hai Bà Trưng", "Đường Quang Trung"
        ])
        
        return f"{street_number} {street_name}, {province_name}"
    
    def generate_cccd_data(self) -> CCCDData:
        """Tạo dữ liệu CCCD đầy đủ"""
        cccd = self.generate_cccd()
        birth_year = random.randint(self.birth_year_from, self.birth_year_to)
        full_name = self.generate_name(self.gender)
        birth_date = self.generate_birth_date(birth_year)
        address = self.generate_address(self.province_code)
        
        return CCCDData(
            cccd=cccd,
            province_code=self.province_code,
            gender=self.gender,
            birth_year=birth_year,
            birth_date=birth_date,
            full_name=full_name,
            address=address
        )
    
    def generate_batch(self) -> List[CCCDData]:
        """Tạo batch CCCD"""
        logger.info(f"🔢 Generating {self.count} CCCD records...")
        
        cccd_list = []
        for i in range(self.count):
            cccd_data = self.generate_cccd_data()
            cccd_list.append(cccd_data)
            
            if (i + 1) % 100 == 0:
                logger.info(f"📊 Generated {i + 1}/{self.count} CCCD records")
        
        logger.info(f"✅ Generated {len(cccd_list)} CCCD records successfully")
        return cccd_list
    
    def save_to_file(self, cccd_list: List[CCCDData], filename: str = "cccd_data.txt"):
        """Lưu dữ liệu CCCD ra file"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("CCCD\tProvince\tGender\tBirth Year\tBirth Date\tFull Name\tAddress\n")
                for cccd_data in cccd_list:
                    f.write(f"{cccd_data.cccd}\t{cccd_data.province_code}\t{cccd_data.gender}\t"
                           f"{cccd_data.birth_year}\t{cccd_data.birth_date}\t"
                           f"{cccd_data.full_name}\t{cccd_data.address}\n")
            
            logger.info(f"💾 Saved {len(cccd_list)} CCCD records to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving CCCD data: {e}")
            return False

def main():
    """Test function"""
    config = {
        'cccd_count': 10,
        'province_code': '001',
        'gender': 'Nam',
        'birth_year_from': 1990,
        'birth_year_to': 2000
    }
    
    generator = CCCDGenerator(config)
    cccd_list = generator.generate_batch()
    
    print("KẾT QUẢ TẠO CCCD:")
    print("=" * 80)
    for i, cccd_data in enumerate(cccd_list, 1):
        print(f"{i:2d}. {cccd_data.cccd} | {cccd_data.full_name} | {cccd_data.birth_date} | {cccd_data.address}")

if __name__ == "__main__":
    main()