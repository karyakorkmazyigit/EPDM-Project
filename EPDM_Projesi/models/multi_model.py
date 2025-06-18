import pandas as pd
import numpy as np
from itertools import product
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import os

# dinamik excel yolu
base_dir = os.path.dirname(os.path.dirname(__file__))
excel_path = os.path.join(base_dir, "data", "datas.xlsx")
xls = pd.ExcelFile(excel_path)

# input-output sütunları
input_cols = ['GPF Black (N-650)', 'SRF Black (N-762)', 'Sunpar 2280',
              'Zinc Oxide', 'Stearic Acid', 'Sulfur']
output_cols = ['Hardness, Shore A', 'Tensile Strength, MPa (psi)', 'Elongation, %']

combined_df = []

# veriler cekiliyor
for sheet_name in xls.sheet_names:
    df = xls.parse(sheet_name)

    if all(col in df.columns for col in output_cols):
        existing_inputs = [col for col in input_cols if col in df.columns]
        temp_df = df[existing_inputs + output_cols].dropna()

        for missing in set(input_cols) - set(existing_inputs):
            temp_df[missing] = 0

        temp_df = temp_df[input_cols + output_cols]

        if not temp_df.empty:
            combined_df.append(temp_df)

# birlestirilip tensile temizle
if combined_df:
    final_df = pd.concat(combined_df, ignore_index=True)
    print(f"Toplam veri sayısı: {len(final_df)}")


    def extract_numeric(s):
        try:
            return float(str(s).split('(')[0].strip())
        except:
            return None


    final_df['Tensile Strength, MPa (psi)'] = final_df['Tensile Strength, MPa (psi)'].apply(extract_numeric)
    final_df = final_df.dropna()

    if len(final_df) >= 2:
        # model egitimi
        X = final_df[input_cols]
        Y = final_df[output_cols]

        X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)
        model = RandomForestRegressor(n_estimators=100, random_state=42)
        model.fit(X_train, Y_train)

        print("✅ Model başarıyla eğitildi.")

        # kullanıcı hedefi
        target = np.array([80, 12.0, 330])

        # grid search aralıkları (performansa göre degisebilir)
        ranges = {
            'GPF Black (N-650)': np.arange(70, 111, 10),
            'SRF Black (N-762)': np.arange(70, 111, 10),
            'Sunpar 2280': np.arange(90, 121, 10),
            'Zinc Oxide': np.arange(3, 6.1, 0.5),
            'Stearic Acid': [1.0],
            'Sulfur': np.arange(0.4, 0.7, 0.05)
        }

        best_combo = None
        min_error = float("inf")
        best_pred = None

        for combo in product(*ranges.values()):
            combo_dict = dict(zip(ranges.keys(), combo))
            x_input_df = pd.DataFrame([combo_dict])
            y_pred = model.predict(x_input_df)[0]
            error = np.linalg.norm(y_pred - target)
            if error < min_error:
                min_error = error
                best_combo = combo
                best_pred = y_pred

        # sonuclari yazdir
        print("\n🎯 Kullanıcı Hedefleri:")
        print(f"  Sertlik : {target[0]}")
        print(f"  Çekme   : {target[1]}")
        print(f"  Uzama   : {target[2]}")

        print("\n📋 Önerilen Reçete:")
        for key, val in zip(ranges.keys(), best_combo):
            print(f"  {key}: {val}")

        print("\n📈 Modelin Tahmini:")
        print(f"  Sertlik : {round(best_pred[0], 2)}")
        print(f"  Çekme   : {round(best_pred[1], 2)}")
        print(f"  Uzama   : {round(best_pred[2], 2)}")

    else:
        print("❗ Yeterli temiz veri yok. Model eğitilemedi.")
else:
    print("❗ Uygun sayfalardan veri alınamadı.")
