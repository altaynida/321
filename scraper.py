import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Referer": "https://www.transfermarkt.com.tr/"
}

import json

TAKIMLAR_DOSYASI = "takimlar.json"


def takimlari_yukle():
    """takimlar.json dosyasından takım bilgilerini okur. Dosya yoksa boş sözlük döner."""
    if not os.path.exists(TAKIMLAR_DOSYASI):
        print(f"⚠️ {TAKIMLAR_DOSYASI} bulunamadı, boş takım listesiyle başlanıyor.")
        return {}
    with open(TAKIMLAR_DOSYASI, "r", encoding="utf-8") as f:
        return json.load(f)


TAKIM_BILGI = takimlari_yukle()
# Not: Yeni takım eklemek için TAKIM_BILGI'yi elle değiştirmene gerek yok —
# takim_ekle.py scriptini çalıştırıp bir Transfermarkt takım URL'si yapıştırman yeterli.

BITIS_YIL = 2025  # güncel sezon (Transfermarkt'ta "saison_id=2025" -> 2025-26 sezonu)
# NOT: Zaman ilerledikçe bu değeri her yıl güncellemen gerekir (örn. 2026'da 2026 yap).
VERI_KLASORU = "veri_cache"


def _oyuncu_id_cek(a_etiketi):
    """Profil linkinden transfermarkt oyuncu ID'sini çıkarır. Örn: /profil/spieler/8198"""
    href = a_etiketi.get("href", "")
    eslesme = re.search(r"/spieler/(\d+)", href)
    return eslesme.group(1) if eslesme else None


def tek_sezon_kadrosu_cek(takim_adi, slug, takim_id, sezon_yili, max_deneme=3):
    url = f"https://www.transfermarkt.com.tr/{slug}/kader/verein/{takim_id}/saison_id/{sezon_yili}"

    for deneme in range(1, max_deneme + 1):
        oyuncular = []
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)

            if response.status_code in (403, 429):
                bekleme = 8 * deneme
                print(f"    ⛔ HTTP {response.status_code} (muhtemelen engellendik) — {bekleme}sn bekleyip tekrar denenecek ({deneme}/{max_deneme})")
                time.sleep(bekleme)
                continue

            if response.status_code != 200:
                return oyuncular, response.status_code

            soup = BeautifulSoup(response.content, "html.parser")
            kadro_tablosu = soup.find("table", {"class": "items"})
            if not kadro_tablosu:
                if deneme < max_deneme:
                    print(f"    ⚠️ Kadro tablosu bulunamadı (consent sayfası olabilir) — tekrar deneniyor ({deneme}/{max_deneme})")
                    time.sleep(5 * deneme)
                    continue
                return oyuncular, "TABLO_YOK"

            satirlar = kadro_tablosu.find_all("tr", class_=["odd", "even"])

            for satir in satirlar:
                isim_hucresi = satir.find("td", class_="hauptlink")
                if not (isim_hucresi and isim_hucresi.find("a")):
                    continue

                a_etiketi = isim_hucresi.find("a")
                oyuncu_adi = a_etiketi.text.strip()
                oyuncu_id = _oyuncu_id_cek(a_etiketi)

                if not oyuncu_id:
                    continue

                pozisyon = "Bilinmiyor"
                inline_table = satir.find("table", class_="inline-table")
                if inline_table:
                    inline_tr = inline_table.find_all("tr")
                    if len(inline_tr) > 1:
                        pozisyon = inline_tr[1].text.strip()

                uyruk_img = satir.find("img", class_="flaggenrahmen")
                uyruk = uyruk_img["alt"] if uyruk_img and "alt" in uyruk_img.attrs else "Bilinmiyor"

                oyuncular.append({
                    "OyuncuID": oyuncu_id,
                    "Oyuncu": oyuncu_adi,
                    "Takim": takim_adi,
                    "Sezon": sezon_yili,
                    "Pozisyon": pozisyon,
                    "Uyruk": uyruk
                })

            return oyuncular, response.status_code

        except Exception as e:
            print(f"    ⚠️ {takim_adi} - {sezon_yili} sezonu çekilirken hata: {e}")
            if deneme < max_deneme:
                time.sleep(5 * deneme)
                continue
            return [], "HATA"

    return [], "BASARISIZ"


def takim_tum_gecmis_cek(takim_adi, zorla_yenile=False):
    """Bir takımın belirlenen yıl aralığındaki TÜM sezon kadrolarını çeker
    ve tekrar tekrar internete gitmemek için diske (CSV) kaydeder."""

    os.makedirs(VERI_KLASORU, exist_ok=True)
    cache_yolu = os.path.join(VERI_KLASORU, f"{takim_adi.replace(' ', '_')}.csv")

    if os.path.exists(cache_yolu) and not zorla_yenile:
        print(f"📂 {takim_adi} verisi cache'ten okunuyor ({cache_yolu})")
        return pd.read_csv(cache_yolu, dtype={"OyuncuID": str})

    bilgi = TAKIM_BILGI[takim_adi]
    tum_oyuncular = []

    print(f"🚀 {takim_adi} için {bilgi['baslangic_yil']}-{BITIS_YIL} arası taranıyor...")

    for yil in range(bilgi["baslangic_yil"], BITIS_YIL + 1):
        sezon_verisi, durum = tek_sezon_kadrosu_cek(takim_adi, bilgi["slug"], bilgi["id"], yil)
        tum_oyuncular.extend(sezon_verisi)

        if len(sezon_verisi) == 0:
            print(f"  ❌ {takim_adi} - {yil}: 0 oyuncu bulundu (durum: {durum}) — BU SEZON EKSİK KALDI")
        else:
            print(f"  ✅ {takim_adi} - {yil}: {len(sezon_verisi)} oyuncu")

        time.sleep(3)  # Transfermarkt'ı yormamak ve engellenmemek için

    df = pd.DataFrame(tum_oyuncular)
    if not df.empty:
        df.to_csv(cache_yolu, index=False, encoding="utf-8-sig")
        print(f"✅ {takim_adi}: {df['OyuncuID'].nunique()} farklı oyuncu, {len(df)} kayıt kaydedildi.")
    return df


def ortak_oyunculari_bul(takim1_adi, takim2_adi, zorla_yenile=False):
    """İki takımın gelmiş geçmiş tüm oyuncularını çekip ortak oynayanları bulur."""

    df1 = takim_tum_gecmis_cek(takim1_adi, zorla_yenile)
    df2 = takim_tum_gecmis_cek(takim2_adi, zorla_yenile)

    if df1.empty or df2.empty:
        print("❌ Veri çekilemedi, karşılaştırma yapılamıyor.")
        return pd.DataFrame()

    ortak_id = set(df1["OyuncuID"]) & set(df2["OyuncuID"])

    if not ortak_id:
        print(f"\nℹ️ {takim1_adi} ile {takim2_adi} arasında ortak oyuncu bulunamadı.")
        return pd.DataFrame()

    sonuc = []
    for oid in ortak_id:
        adi = df1[df1["OyuncuID"] == oid]["Oyuncu"].iloc[0]
        sezonlar_1 = sorted(df1[df1["OyuncuID"] == oid]["Sezon"].unique().tolist())
        sezonlar_2 = sorted(df2[df2["OyuncuID"] == oid]["Sezon"].unique().tolist())
        uyruk = df1[df1["OyuncuID"] == oid]["Uyruk"].iloc[0]
        pozisyon = df1[df1["OyuncuID"] == oid]["Pozisyon"].iloc[0]

        sonuc.append({
            "Oyuncu": adi,
            "OyuncuID": oid,
            "Uyruk": uyruk,
            "Pozisyon": pozisyon,
            f"{takim1_adi}_Sezonlari": ", ".join(map(str, sezonlar_1)),
            f"{takim2_adi}_Sezonlari": ", ".join(map(str, sezonlar_2)),
        })

    sonuc_df = pd.DataFrame(sonuc).sort_values("Oyuncu")
    print(f"\n🎉 {takim1_adi} ile {takim2_adi} arasında {len(sonuc_df)} ortak oyuncu bulundu.")
    return sonuc_df


if __name__ == "__main__":
    # Örnek kullanım
    sonuc = ortak_oyunculari_bul("Galatasaray", "Fenerbahçe")
    print(sonuc.to_string(index=False))
    sonuc.to_csv("ortak_oyuncular.csv", index=False, encoding="utf-8-sig")
