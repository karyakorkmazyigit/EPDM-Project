import subprocess
import os
import sys

def run_multi_model():

    path = os.path.join("models", "multi_model.py")
    if os.path.exists(path):
        print("📊 Model dosyası çalıştırılıyor...\n")
        subprocess.run([sys.executable, path])
    else:
        print("❌ models/multi_model.py bulunamadı.")

def run_streamlit_app():

    path = os.path.join("app", "streamlit_app.py")
    if os.path.exists(path):
        print("🌐 Streamlit arayüzü başlatılıyor...\n")
        subprocess.run(["streamlit", "run", path])
    else:
        print("❌ app/streamlit_app.py bulunamadı.")

def main():
    print("\n🧪 EPDM Reçete Tahmin Paneli")
    print("1 - Modeli çalıştır (multi_model.py)")
    print("2 - Streamlit arayüzünü başlat")
    print("3 - Çıkış")

    secim = input("Seçiminiz: ")

    if secim == "1":
        run_multi_model()
    elif secim == "2":
        run_streamlit_app()
    elif secim == "3":
        print("👋 Çıkış yapılıyor.")
    else:
        print("❗ Geçersiz seçim. Lütfen 1, 2 ya da 3 girin.")

if __name__ == "__main__":
    main()
