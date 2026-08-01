"""
Bu script, Transfermarkt'tan bir takım URL'si yapıştırarak takimlar.json
dosyasına yeni takım eklemeni sağlar. scraper.py'ı hiç değiştirmene gerek yok.

Nasıl kullanılır:
1. Transfermarkt'ta eklemek istediğin takımın sayfasına git (herhangi bir
   sayfası olabilir: kadro, transferler, ana sayfa vs.)
   Örnek: https://www.transfermarkt.com.tr/atletico-madrid/startseite/verein/13
2. Adres çubuğundaki URL'yi kopyala
3. Bu scripti çalıştır: python takim_ekle.py
4. İstenen bilgileri gir
"""

import json
import re
import os

TAKIMLAR_DOSYASI = "takimlar.json"


def takimlari_yukle():
    if os.path.exists(TAKIMLAR_DOSYASI):
        with open(TAKIMLAR_DOSYASI, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def takimlari_kaydet(veri):
    with open(TAKIMLAR_DOSYASI, "w", encoding="utf-8") as f:
        json.dump(veri, f, ensure_ascii=False, indent=4)


def url_coz(url):
    """Transfermarkt URL'sinden slug ve takım ID'sini çıkarır.
    Örnek URL: https://www.transfermarkt.com.tr/atletico-madrid/startseite/verein/13
    -> slug: atletico-madrid, id: 13
    """
    eslesme = re.search(r"transfermarkt\.[a-z.]+/([a-z0-9\-]+)/[a-z]+/verein/(\d+)", url)
    if not eslesme:
        return None, None
    slug = eslesme.group(1)
    takim_id = int(eslesme.group(2))
    return slug, takim_id


def takim_ekle():
    print("=== Yeni Takım Ekleme Aracı ===\n")
    url = input("Transfermarkt takım URL'sini yapıştır: ").strip()

    slug, takim_id = url_coz(url)
    if not slug:
        print("\n❌ URL'den takım bilgisi çıkarılamadı. URL'nin şu formatta olduğundan emin ol:")
        print("   https://www.transfermarkt.com.tr/TAKIM-ADI/HERHANGI-BIR-SAYFA/verein/ID")
        return

    takim_adi = input("Bu takıma uygulamada verilecek isim (örn: Atletico Madrid): ").strip()
    if not takim_adi:
        print("❌ Takım adı boş olamaz.")
        return

    baslangic_str = input("Hangi yıldan itibaren taransın? (varsayılan: 1990, Enter'a basabilirsin): ").strip()
    baslangic_yil = int(baslangic_str) if baslangic_str else 1990

    takimlar = takimlari_yukle()

    if takim_adi in takimlar:
        onay = input(f"⚠️ '{takim_adi}' zaten listede var. Üzerine yazılsın mı? (e/h): ").strip().lower()
        if onay != "e":
            print("İptal edildi.")
            return

    takimlar[takim_adi] = {
        "slug": slug,
        "id": takim_id,
        "baslangic_yil": baslangic_yil
    }

    takimlari_kaydet(takimlar)
    print(f"\n✅ '{takim_adi}' başarıyla eklendi! (slug: {slug}, id: {takim_id}, başlangıç: {baslangic_yil})")
    print(f"📄 Toplam takım sayısı: {len(takimlar)}")
    print("\nUygulamayı (app.py) yeniden başlatırsan yeni takım seçim kutusunda görünecek.")


if __name__ == "__main__":
    takim_ekle()
