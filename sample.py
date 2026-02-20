import re

import pandas as pd
from fuzzywuzzy import process

# 1. Excelni yuklash. F ustunini tanlab olamiz (index 5)
file_name = 'data.xlsx'
# Agar sarlavha bo'lsa nomi bilan, bo'lmasa index bilan murojaat qilamiz
df = pd.read_excel(file_name)

# F ustunining haqiqiy nomini aniqlaymiz (agar u 6-ustun bo'lsa, indeksi 5 bo'ladi)
column_name = df.columns[5]
print(f"Ishlanayotgan ustun: {column_name}")


def clean_text_basic(text):
    if not isinstance(text, str):
        text = str(text) if pd.notna(text) else ""

    # Oxiridagi va boshidagi raqam hamda chiziqchalarni tozalash
    # regex: [\s\-\.]+\d+$ (bo'shliq/chiziqcha va raqam oxirida)
    text = re.sub(r'[\s\-\.]+\d+$', '', text)
    text = re.sub(r'^\d+[\s\-\.]+', '', text)

    # Qisqartmalarni birxillashtirish (ixtiyoriy)
    text = text.replace('Logistics', 'Log')

    return text.strip()


# 2. Nomlarni tozalash (Vaqtinchalik ustun yaratamiz)
df['cleaned_temp'] = df[column_name].apply(clean_text_basic)
unique_names = df['cleaned_temp'].unique()


def get_standard_mapping(names, threshold=85):
    standard_map = {}
    processed = set()

    for name in names:
        if not name or name in processed:
            continue

        # O'xshashlarni topish
        matches = process.extract(name, names, limit=10)

        # Birinchi uchragan toza nomni asosiy (master) nom deb olamiz
        master_name = name

        for match, score in matches:
            if score >= threshold:
                standard_map[match] = master_name
                processed.add(match)

    return standard_map


# 3. 85% o'xshashlik bo'yicha xarita yaratish
name_mapping = get_standard_mapping(unique_names, threshold=85)

# 4. Yangi ustunga yakuniy natijani yozish
df['standard_company_name'] = df['cleaned_temp'].map(name_mapping)

# Vaqtinchalik ustunni o'chirib tashlaymiz
df.drop(columns=['cleaned_temp'], inplace=True)

# 5. Natijani saqlash
output_name = 'cleaned_companies_F_column.xlsx'
df.to_excel(output_name, index=False)

print(f"Tayyor! Natija '{output_name}' fayliga saqlandi.")
