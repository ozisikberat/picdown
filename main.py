import os
import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image
import shutil

# .env dosyasını yükle
load_dotenv()

# API anahtarını .env dosyasından al
API_KEY = os.getenv('PIXABAY_API_KEY')


# Pixabay API ile görsel arama fonksiyonu
def pixabay_arsiv_sorgula(anahtar_kelime, kategori, sayfa=1):
    url = f'https://pixabay.com/api/?key={API_KEY}&q={anahtar_kelime}&image_type=photo&orientation=horizontal&page={sayfa}&per_page=10&category={kategori}'
    response = requests.get(url)
    try:
        response.raise_for_status()  # Hata durumunda exception fırlatır
        data = response.json()
        return data['hits']
    except requests.exceptions.RequestException as e:
        st.error(f'Hata: {e}')
        return []
    except ValueError as e:
        st.error(f'Yanıtın çözülmesinde bir hata oluştu: {e}')
        return []


# Görseli göster ve indir fonksiyonu
def gorsel_goster_ve_indir(gorsel_url, gorsel_basligi):
    try:
        # URL'den görseli indir
        img_data = requests.get(gorsel_url).content
        klasor_adi = gorsel_basligi.split()[0]  # İlk kelimeden klasör ismi oluştur
        klasor_yolu = f"downloads/{klasor_adi}"

        # Eğer klasör yoksa oluştur
        if not os.path.exists(klasor_yolu):
            os.makedirs(klasor_yolu)

        # Görseli kaydet
        with open(f"{klasor_yolu}/{gorsel_basligi}.jpg", 'wb') as f:
            f.write(img_data)

        st.image(img_data, caption=gorsel_basligi, use_column_width=True)
        st.success(f"Görsel {klasor_yolu}/{gorsel_basligi}.jpg olarak kaydedildi.")
    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")


# Streamlit arayüzü
def main():
    st.title("Pixabay Görsel Arama ve İndirme Uygulaması")

    # Kullanıcıdan anahtar kelime ve kategori al
    anahtar_kelime = st.text_input("Aramak istediğiniz görseli yazın:")
    kategori_sec = st.selectbox("Kategori seçin:",
                                ["Tüm Kategoriler", "Araba", "Doğa", "Meyve", "Hayvanlar", "İnsanlar"])

    if anahtar_kelime:
        st.write(f"Arama sonuçları: {anahtar_kelime}")

        kategori_map = {
            "Tüm Kategoriler": "",
            "Araba": "transportation",
            "Doğa": "nature",
            "Meyve": "food",
            "Hayvanlar": "animals",
            "İnsanlar": "people"
        }

        kategori = kategori_map[kategori_sec]

        # Görselleri al
        gorseller = pixabay_arsiv_sorgula(anahtar_kelime, kategori)

        # Görselleri göster
        if gorseller:
            for gorsel in gorseller:
                gorsel_url = gorsel['webformatURL']
                gorsel_basligi = gorsel['tags']

                col1, col2 = st.columns([4, 1])
                with col1:
                    st.image(gorsel_url, caption=gorsel_basligi, use_column_width=True)
                with col2:
                    if st.button(f"Görseli indir: {gorsel_basligi}", key=gorsel_basligi):
                        gorsel_goster_ve_indir(gorsel_url, gorsel_basligi)


if __name__ == "__main__":
    main()
