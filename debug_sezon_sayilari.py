import pandas as pd
import os

dosya = os.path.join("veri_cache", "Real_Madrid.csv")
df = pd.read_csv(dosya, dtype={"OyuncuID": str})

print("Real Madrid - sezon bazlı çekilen oyuncu sayısı:\n")
sezon_sayilari = df.groupby("Sezon").size().sort_index()
for sezon, sayi in sezon_sayilari.items():
    uyari = "  ⚠️ ÇOK DÜŞÜK / ŞÜPHELİ" if sayi < 15 else ""
    print(f"  {sezon}: {sayi} oyuncu{uyari}")

print(f"\nToplam farklı sezon sayısı: {df['Sezon'].nunique()}")
print(f"Beklenen sezon sayısı (1990-2024): 35")
