import streamlit as st
import pandas as pd
import numpy as np
from itertools import product
from sklearn.ensemble import RandomForestRegressor
import os


st.title("🧪 EPDM Reçete Tahmin Sistemi")

# kullanicilardan hedef degerleri al
target_hardness = st.slider("🎯 Sertlik (Shore A)", 50, 90, 80)
target_tensile = st.slider("🎯 Çekme Dayanımı (MPa)", 5, 20, 12)
target_elongation = st.slider("🎯 Uzama (%)", 100, 500, 330)

if st.button("🔍 En Uygun Reçeteyi Tahmin Et"):
    # verileri yukle
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_path = os.path.join(base_dir, "data", "datas.xlsx")
    df = pd.ExcelFile(data_path)

    input_cols = ['GPF Black (N-650)', 'SRF Black (N-762)', 'Sunpar 2280',
                  'Zinc Oxide', 'Stearic Acid', 'Sulfur']
    output_cols = ['Hardness, Shore A', 'Tensile Strength, MPa (psi)', 'Elongation, %']
    combined_df = []

    for sheet in df.sheet_names:
        temp = df.parse(sheet)
        if all(col in temp.columns for col in output_cols):
            exist_inputs = [col for col in input_cols if col in temp.columns]
            temp_df = temp[exist_inputs + output_cols].dropna()
            for missing in set(input_cols) - set(exist_inputs):
                temp_df[missing] = 0
            temp_df = temp_df[input_cols + output_cols]
            combined_df.append(temp_df)

    if combined_df:
        final_df = pd.concat(combined_df, ignore_index=True)

        def extract_numeric(s):
            try:
                return float(str(s).split('(')[0].strip())
            except:
                return None

        final_df['Tensile Strength, MPa (psi)'] = final_df['Tensile Strength, MPa (psi)'].apply(extract_numeric)
        final_df = final_df.dropna()

        if len(final_df) >= 2:
            X = final_df[input_cols]
            Y = final_df[output_cols]

            model = RandomForestRegressor(n_estimators=100, random_state=42)
            model.fit(X, Y)

            target = np.array([target_hardness, target_tensile, target_elongation])

            # Grid Search
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
                x_df = pd.DataFrame([combo_dict])
                y_pred = model.predict(x_df)[0]
                error = np.linalg.norm(y_pred - target)
                if error < min_error:
                    min_error = error
                    best_combo = combo
                    best_pred = y_pred

            # outputs
            st.success("✅ En Uygun Reçete Bulundu!")
            for key, val in zip(ranges.keys(), best_combo):
                st.write(f"**{key}**: {val}")

            st.markdown("---")
            st.subheader("📈 Modelin Tahmini")
            st.write(f"**Sertlik:** {round(best_pred[0], 2)}")
            st.write(f"**Çekme:** {round(best_pred[1], 2)} MPa")
            st.write(f"**Uzama:** {round(best_pred[2], 2)} %")
        else:
            st.error("Temiz verilerle model eğitilemedi.")
    else:
        st.error("Veri dosyası uygun sayfa içermiyor.")
