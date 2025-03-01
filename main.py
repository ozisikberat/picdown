import os
import requests
import streamlit as st
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

# API anahtarını .env dosyasından al
API_KEY = os.getenv('PIXABAY_API_KEY')


# Pixabay API ile görsel arama fonksiyonu
def pixabay_arsiv_sorgula(anahtar_kelime, kategori, sayfa=1):
    url = f'https://pixabay.com/api/?key={API_KEY}&q={anahtar_kelime}&image_type=photo&orientation=horizontal&page={sayfa}&per_page=10'

    # Kategori parametresi varsa URL'ye ekle
    if kategori:
        url += f'&category={kategori}'

    response = requests.get(url)
    try:
        response.raise_for_status()  # Hata durumunda exception fırlatır
        data = response.json()

        # Eğer görsel bulunamazsa bilgi verelim
        if data['totalHits'] == 0:
            st.warning("Hiç görsel bulunamadı.")
            return []

        return data['hits']
    except requests.exceptions.RequestException as e:
        st.error(f'Hata: {e}')
        return []
    except ValueError as e:
        st.error(f'Yanıtın çözülmesinde bir hata oluştu: {e}')
        return []


# Görseli indir fonksiyonu
def gorsel_indir(gorsel_url, dosya_adi):
    try:
        # URL'den görseli indir
        img_data = requests.get(gorsel_url).content

        # Görseli kaydetmeden önce bir dosya adı oluştur
        dosya_yolu = f"downloads/{dosya_adi}.jpg"
        with open(dosya_yolu, 'wb') as f:
            f.write(img_data)

        return dosya_yolu
    except Exception as e:
        return f"Bir hata oluştu: {e}"


# Streamlit arayüzü
def main():
    st.title("Pixabay Görsel Arama ve İndirme Uygulaması")

    # Sidebar'a arama kısmı taşıyoruz
    st.sidebar.title("Arama Kriterleri")
    anahtar_kelime = st.sidebar.text_input("Aramak istediğiniz görseli yazın:")
    kategori_sec = st.sidebar.selectbox("Kategori seçin:",
                                        ["Tüm Kategoriler", "Araba", "Doğa", "Meyve", "Hayvanlar", "İnsanlar"])

    # Arama butonunu ekle
    arama_butonu = st.sidebar.button("Görsel Ara")

    # Görselleri session_state'ye kaydedelim
    if "gorseller" not in st.session_state:
        st.session_state.gorseller = []

    # Arama butonuna basıldığında yeni arama yapalım
    if arama_butonu and anahtar_kelime:
        st.sidebar.write(f"Arama sonuçları: {anahtar_kelime}")

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

        # Görselleri session_state'e kaydediyoruz
        if gorseller:
            st.session_state.gorseller = gorseller

    # Görselleri ekrana yerleştiriyoruz
    if st.session_state.gorseller:
        # Streamlit widget’ları ile görselleri 3 sütun halinde göstermek için
        cols = st.columns(3)  # 3 sütunlu düzen
        col_index = 0
        selected_images = []  # Seçilen görselleri tutmak için liste

        # Görselleri ekleyelim
        for index, gorsel in enumerate(st.session_state.gorseller):
            gorsel_url = gorsel['webformatURL']  # Görsel URL'sini al
            dosya_adi = f"{anahtar_kelime.replace(' ', '_')}_{index + 1}"  # Dosya adı, anahtar kelime + sıralama numarası

            with cols[col_index]:
                # Görseli gösteriyoruz
                st.image(gorsel_url, use_container_width =True)

                # "İndir" butonu ekleyelim, Streamlit'in dosya indirme butonu
                img_data = requests.get(gorsel_url).content  # Görseli indiriyoruz
                if st.download_button(
                        label="Görseli İndir",
                        data=img_data,
                        file_name=f"{dosya_adi}.jpg",
                        mime="image/jpeg"
                ):
                    selected_images.append(dosya_adi)  # İndirilen görselin dosya adı

            # Kolonları döngü ile sıralıyoruz
            col_index += 1
            if col_index == 3:  # Her 3 görselde bir yeni satıra geç
                col_index = 0
if __name__ == "__main__":
    main()
