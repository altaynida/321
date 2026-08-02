import streamlit as st
import pandas as pd
import os
import random
import base64

st.set_page_config(page_title="Ortak Topçular Bulucu & Oyunlar", page_icon="⚽", layout="wide")

# --- UI TASARIMI ---
st.markdown("""
<style>
    .player-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 18px;
        margin-bottom: 16px;
        border-left: 5px solid #ff4b4b;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    .player-name { font-size: 20px; font-weight: bold; color: #ffffff; margin-bottom: 8px; }
    .badge { display: inline-block; background-color: #333333; color: #dddddd; padding: 4px 10px; border-radius: 6px; font-size: 13px; margin-right: 6px; }
    .seasons { font-size: 13px; color: #aaaaaa; margin-top: 6px; }
    
    .game-box { 
        background-color: #171b26; 
        padding: 20px; 
        border-radius: 12px; 
        border: 2px solid #ff4b4b; 
        color: #f8f9fa !important; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .game-box h2, .game-box h3 {
        color: #ffffff !important; 
        margin-bottom: 0px;
    }
    .game-box p {
        color: #aaaaaa !important;
        margin-bottom: 0px;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- VERİ VE LOGO OKUMA FONKSİYONLARI ---
@st.cache_data
def takimlari_getir():
    takimlar = []
    hedef_klasor = "veri_cache"
    if os.path.exists(hedef_klasor):
        for dosya in os.listdir(hedef_klasor):
            if dosya.endswith(".csv"):
                takimlar.append(dosya.replace(".csv", ""))
    return sorted(takimlar)

@st.cache_data(show_spinner=False)
def butun_oyunculari_birlestir():
    takimlar = takimlari_getir()
    tum_veriler = []
    for takim in takimlar:
        dosya_yolu = f"veri_cache/{takim}.csv"
        try:
            df = pd.read_csv(dosya_yolu)
            df['Takim'] = takim
            if 'Pozisyon' not in df.columns: df['Pozisyon'] = '-'
            if 'Uyruk' not in df.columns: df['Uyruk'] = '-'
            
            sezon_col = 'Sezonlar' if 'Sezonlar' in df.columns else ('Sezon' if 'Sezon' in df.columns else None)
            if sezon_col:
                df['Ilk_Yil'] = df[sezon_col].astype(str).str.extract(r'(\d{4})').fillna(9999).astype(int)
            else:
                df['Ilk_Yil'] = 9999
                
            tum_veriler.append(df[['Oyuncu', 'Pozisyon', 'Uyruk', 'Takim', 'Ilk_Yil']])
        except:
            pass
            
    if not tum_veriler: return pd.DataFrame()
    
    master_df = pd.concat(tum_veriler, ignore_index=True)
    master_df = master_df.sort_values('Ilk_Yil')
    
    oyuncu_gruplu = master_df.groupby('Oyuncu').agg({
        'Takim': lambda x: list(dict.fromkeys(x)), 
        'Pozisyon': 'first',
        'Uyruk': 'first',
        'Ilk_Yil': 'min'
    }).reset_index()
    
    # Oyunlar için 2004 ve sonrasına başlayan oyuncu filtresi
    return oyuncu_gruplu[(oyuncu_gruplu['Takim'].apply(len) > 1) & (oyuncu_gruplu['Ilk_Yil'] >= 2004)]

@st.cache_data(show_spinner=False)
def logo_base64_getir(takim_adi):
    logo_yolu = f"logolar/{takim_adi}.png"
    if os.path.exists(logo_yolu):
        with open(logo_yolu, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

def get_logo_html(takim_adi, size=60):
    b64 = logo_base64_getir(takim_adi)
    if b64:
        return f"<img src='data:image/png;base64,{b64}' style='width:{size}px; height:{size}px; object-fit:contain;' title='{takim_adi}'>"
    return f"<div style='font-size:24px;' title='{takim_adi}'>🛡️</div>"

takim_listesi = takimlari_getir()
master_oyuncular = butun_oyunculari_birlestir()

# --- SOL MENÜ (SIDEBAR) NAVİGASYONU ---
st.sidebar.title("⚽ Menü")
sayfa = st.sidebar.radio("Gitmek istediğiniz bölümü seçin:", 
                         [
                             "🔍 Arama Motoru", 
                             "🕵️‍♂️ Oyun 1: Adım Adım Kimlik", 
                             "🔗 Oyun 2: Kayıp Halka", 
                             "🚀 Oyun 3: Kariyer Yolu",
                             "🏃‍♂️ Oyun 4: Kim Daha Gezgin?",
                             "🕸️ Oyun 5: Şifre Ağı (V2.0)",
                             "✖️ Oyun 6: Çapraz Ateş (V3.0)"
                         ])

# ==========================================
# 1. BÖLÜM: ARAMA MOTORU (Numaralandırılmış Liste)
# ==========================================
if sayfa == "🔍 Arama Motoru":
    st.title("⚽ Ortak Topçular Bulucu")
    st.caption("Karşılaştırmak istediğiniz iki takımı seçin, gelmiş geçmiş ortak oyuncuları listeleyelim!")

    # Takımların başına 1'den 100'e kadar numara ekleyip sözlük oluşturuyoruz
    numarali_takim_dict = {f"{idx+1}. {takim}": takim for idx, takim in enumerate(takim_listesi)}
    gorunen_takimlar = list(numarali_takim_dict.keys())

    col1, col2 = st.columns(2)
    with col1: 
        secilen_gosterge_1 = st.selectbox("1. Takım", gorunen_takimlar, index=None, placeholder="Bir takım seçin")
        input_takim_1 = numarali_takim_dict[secilen_gosterge_1] if secilen_gosterge_1 else None
        
    with col2: 
        kalan_gosterge_listesi = [t for t in gorunen_takimlar if numarali_takim_dict[t] != input_takim_1] if input_takim_1 else gorunen_takimlar
        secilen_gosterge_2 = st.selectbox("2. Takım", kalan_gosterge_listesi, index=None, placeholder="Bir takım seçin")
        input_takim_2 = numarali_takim_dict[secilen_gosterge_2] if secilen_gosterge_2 else None

    st.markdown("<br>", unsafe_allow_html=True)
    ara_butonu = st.button("Ortak Oyuncuları Ara", type="primary")

    @st.cache_data(show_spinner=False)
    def ortak_oyunculari_getir(t1, t2):
        dosya1, dosya2 = f"veri_cache/{t1}.csv", f"veri_cache/{t2}.csv"
        if not os.path.exists(dosya1) or not os.path.exists(dosya2): return pd.DataFrame()
        df1, df2 = pd.read_csv(dosya1), pd.read_csv(dosya2)
        ortak_df = pd.merge(df1, df2, on='Oyuncu', how='inner')
        if ortak_df.empty: return pd.DataFrame()

        sezon_x = 'Sezonlar_x' if 'Sezonlar_x' in ortak_df.columns else ('Sezon_x' if 'Sezon_x' in ortak_df.columns else None)
        sezon_y = 'Sezonlar_y' if 'Sezonlar_y' in ortak_df.columns else ('Sezon_y' if 'Sezon_y' in ortak_df.columns else None)
        
        agg_kurallari = {}
        if 'Pozisyon_x' in ortak_df.columns: agg_kurallari['Pozisyon_x'] = 'first'
        elif 'Pozisyon' in ortak_df.columns: agg_kurallari['Pozisyon'] = 'first'
        if 'Uyruk_x' in ortak_df.columns: agg_kurallari['Uyruk_x'] = 'first'
        elif 'Uyruk' in ortak_df.columns: agg_kurallari['Uyruk'] = 'first'

        if sezon_x:
            ortak_df[sezon_x] = ortak_df[sezon_x].astype(str)
            agg_kurallari[sezon_x] = lambda x: ', '.join(sorted(set(x)))
        if sezon_y:
            ortak_df[sezon_y] = ortak_df[sezon_y].astype(str)
            agg_kurallari[sezon_y] = lambda x: ', '.join(sorted(set(x)))

        ortak_df = ortak_df.groupby('Oyuncu').agg(agg_kurallari).reset_index()
        sonuc_df = pd.DataFrame()
        sonuc_df['Oyuncu'] = ortak_df['Oyuncu']
        sonuc_df['Pozisyon'] = ortak_df.get('Pozisyon_x', ortak_df.get('Pozisyon', '-'))
        sonuc_df['Uyruk'] = ortak_df.get('Uyruk_x', ortak_df.get('Uyruk', '-'))
        sonuc_df[f"{t1}_Sezonlari"] = ortak_df.get(sezon_x, '-') if sezon_x else '-'
        sonuc_df[f"{t2}_Sezonlari"] = ortak_df.get(sezon_y, '-') if sezon_y else '-'
        return sonuc_df

    if ara_butonu:
        if not input_takim_1 or not input_takim_2: st.warning("⚠️ Lütfen her iki takımı da seçin!")
        else:
            sonuc_df = ortak_oyunculari_getir(input_takim_1, input_takim_2)
            if sonuc_df.empty: st.info(f"ℹ️ **{input_takim_1}** ve **{input_takim_2}** forması giymiş ortak oyuncu bulunamadı.")
            else:
                st.success(f"🎯 **{input_takim_1}** ve **{input_takim_2}** forması giymiş **{len(sonuc_df)}** ortak futbolcu bulundu:")
                cols = st.columns(3)
                for idx, (_, row) in enumerate(sonuc_df.iterrows()):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="player-card">
                            <div class="player-name">🏃‍♂️ {row['Oyuncu']}</div>
                            <span class="badge">📍 {row['Pozisyon']}</span>
                            <span class="badge">🌍 {row['Uyruk']}</span>
                            <div class="seasons">
                                <b>{input_takim_1}:</b> {row[f"{input_takim_1}_Sezonlari"]}<br>
                                <b>{input_takim_2}:</b> {row[f"{input_takim_2}_Sezonlari"]}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

# ==========================================
# 2. BÖLÜM: OYUN 1 - ADIM ADIM KİMLİK
# ==========================================
elif sayfa == "🕵️‍♂️ Oyun 1: Adım Adım Kimlik":
    st.title("🕵️‍♂️ Adım Adım Kimlik (Who Am I?)")
    
    if 'g1_aktif' not in st.session_state: st.session_state.g1_aktif = False

    def yeni_oyun_baslat_g1():
        secilen = master_oyuncular.sample(1).iloc[0]
        takimlar = random.sample(secilen['Takim'], 2)
        st.session_state.g1_oyuncu = secilen['Oyuncu']
        st.session_state.g1_uyruk = secilen['Uyruk']
        st.session_state.g1_pozisyon = secilen['Pozisyon']
        st.session_state.g1_takimlar = takimlar
        st.session_state.g1_ipucu = 0
        st.session_state.g1_puan = 100
        st.session_state.g1_aktif = True

    if not st.session_state.g1_aktif:
        if st.button("🎮 Yeni Oyun Başlat", type="primary"):
            yeni_oyun_baslat_g1()
            st.rerun()

    if st.session_state.g1_aktif:
        t1, t2 = st.session_state.g1_takimlar
        st.markdown(f"""
        <div class='game-box' style='display:flex; justify-content:space-around; align-items:center;'>
            <div style='text-align:center;'>{get_logo_html(t1, 90)}<br><b>{t1}</b></div>
            <div style='font-size:50px; font-weight:bold; color:#ff4b4b;'>&</div>
            <div style='text-align:center;'>{get_logo_html(t2, 90)}<br><b>{t2}</b></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.metric("🏆 Mevcut Puan", st.session_state.g1_puan)
        if st.session_state.g1_ipucu > 0: st.info(f"🌍 **Uyruk:** {st.session_state.g1_uyruk}")
        if st.session_state.g1_ipucu > 1: st.info(f"📍 **Mevki:** {st.session_state.g1_pozisyon}")
        if st.session_state.g1_ipucu > 2: st.info(f"🔤 **Baş Harfi:** {st.session_state.g1_oyuncu[0]}...")

        col1, col2 = st.columns([3, 1])
        with col1: tahmin = st.text_input("Tahmininiz nedir?", placeholder="Futbolcunun adını yazın...", key="g1_tahmin")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💡 İpucu Ver (-20 Puan)") and st.session_state.g1_ipucu < 3:
                st.session_state.g1_ipucu += 1
                st.session_state.g1_puan -= 20
                st.rerun()

        if tahmin:
            if tahmin.lower().strip() == st.session_state.g1_oyuncu.lower().strip():
                st.success(f"🎉 TEBRİKLER! Doğru bildin: **{st.session_state.g1_oyuncu}**")
                st.balloons()
                st.session_state.g1_aktif = False
                st.button("🔄 Yeni Soruya Geç")
            else:
                st.error("❌ Yanlış tahmin, tekrar dene veya ipucu al!")

        if st.button("🏳️ Pes Ediyorum"):
            st.warning(f"Cevap: **{st.session_state.g1_oyuncu}**")
            st.session_state.g1_aktif = False

# ==========================================
# 3. BÖLÜM: OYUN 2 - KAYIP HALKA 
# ==========================================
elif sayfa == "🔗 Oyun 2: Kayıp Halka":
    st.title("🔗 Kayıp Halka (Transfer Zinciri)")
    
    if 'g2_aktif' not in st.session_state: st.session_state.g2_aktif = False

    def yeni_oyun_baslat_g2():
        uygun_oyuncular = master_oyuncular[master_oyuncular['Takim'].apply(len) >= 3]
        secilen = uygun_oyuncular.sample(1).iloc[0]
        tum_takimlari = secilen['Takim']
        baslangic = random.randint(0, len(tum_takimlari) - 3)
        gosterilen_takimlar = tum_takimlari[baslangic:baslangic+3]
        gizli_index = random.randint(0, 2)
        hedef_takim = gosterilen_takimlar[gizli_index]
        gosterilen_takimlar[gizli_index] = "❓❓❓"
        
        st.session_state.g2_oyuncu = secilen['Oyuncu']
        st.session_state.g2_pozisyon = secilen['Pozisyon']
        st.session_state.g2_zincir_liste = gosterilen_takimlar
        st.session_state.g2_hedef_takim = hedef_takim
        st.session_state.g2_aktif = True

    if not st.session_state.g2_aktif:
        if st.button("🎮 Yeni Zincir Başlat", type="primary"):
            yeni_oyun_baslat_g2()
            st.rerun()

    if st.session_state.g2_aktif:
        takimlar = st.session_state.g2_zincir_liste
        zincir_html = "<div class='game-box' style='display:flex; justify-content:center; align-items:center; flex-wrap:wrap; gap:15px;'>"
        
        for idx, takim in enumerate(takimlar):
            if takim == "❓❓❓":
                zincir_html += "<div style='text-align:center; font-size:60px; color:#ff4b4b; font-weight:bold; padding: 0 15px;'>?</div>"
            else:
                zincir_html += f"<div style='text-align:center;'>{get_logo_html(takim, 70)}<br><small style='color:#aaaaaa;'>{takim}</small></div>"
            
            if idx < len(takimlar) - 1:
                zincir_html += "<div style='font-size:30px; color:#ffffff; padding: 0 10px;'>➔</div>"
                
        zincir_html += "</div>"
        
        st.markdown(zincir_html, unsafe_allow_html=True)
        st.caption(f"**Oyuncu Bilgisi:** {st.session_state.g2_oyuncu} ({st.session_state.g2_pozisyon})")
        
        tahmin = st.text_input("Eksik takım hangisi?", placeholder="Takım adını yazın...", key="g2_tahmin")
        if tahmin:
            if tahmin.lower().strip() == st.session_state.g2_hedef_takim.lower().strip():
                st.success(f"🎯 HARİKA! Eksik takım **{st.session_state.g2_hedef_takim}** idi.")
                st.snow()
                st.session_state.g2_aktif = False
                st.button("🔄 Yeni Zincire Geç")
            else:
                st.error("❌ Yanlış takım, tekrar düşün!")
                
        if st.button("🏳️ Pes Ediyorum", key="g2_pes"):
            st.warning(f"Kayıp Halka: **{st.session_state.g2_hedef_takim}**")
            st.session_state.g2_aktif = False

# ==========================================
# 4. BÖLÜM: OYUN 3 - KARİYER YOLU 
# ==========================================
elif sayfa == "🚀 Oyun 3: Kariyer Yolu":
    st.title("🚀 Kariyer Yolu (Transfer Ustası)")
    
    if 'g3_aktif' not in st.session_state: st.session_state.g3_aktif = False

    def yeni_oyun_baslat_g3():
        uygun_oyuncular = master_oyuncular[master_oyuncular['Takim'].apply(len) >= 4]
        secilen = uygun_oyuncular.sample(1).iloc[0]
        st.session_state.g3_oyuncu = secilen['Oyuncu']
        st.session_state.g3_uyruk = secilen['Uyruk']
        st.session_state.g3_pozisyon = secilen['Pozisyon']
        st.session_state.g3_takimlar = secilen['Takim'] 
        st.session_state.g3_ipucu = 0
        st.session_state.g3_puan = 100
        st.session_state.g3_aktif = True

    if not st.session_state.g3_aktif:
        if st.button("🎮 Yeni Kariyere Başla", type="primary"):
            yeni_oyun_baslat_g3()
            st.rerun()

    if st.session_state.g3_aktif:
        takimlar = st.session_state.g3_takimlar
        st.markdown(f"<h4 style='text-align:center; color:#dddddd;'>Bu oyuncu kariyerinde tam <span style='color:#ff4b4b; font-size:32px;'>{len(takimlar)}</span> farklı takımın formasını terletti!</h4>", unsafe_allow_html=True)
        
        zincir_html = "<div class='game-box' style='display:flex; justify-content:center; align-items:center; flex-wrap:wrap; gap:10px; margin-bottom: 20px;'>"
        for idx, takim in enumerate(takimlar):
            zincir_html += f"<div style='text-align:center;'>{get_logo_html(takim, 60)}<br><small style='color:#aaaaaa; font-size:11px;'>{takim}</small></div>"
            if idx < len(takimlar) - 1:
                zincir_html += "<div style='font-size:24px; color:#ffffff; padding: 0 5px;'>➔</div>"
        zincir_html += "</div>"
        
        st.markdown(zincir_html, unsafe_allow_html=True)
        st.metric("🏆 Mevcut Puan", st.session_state.g3_puan)
        if st.session_state.g3_ipucu > 0: st.info(f"🌍 **Uyruk:** {st.session_state.g3_uyruk}")
        if st.session_state.g3_ipucu > 1: st.info(f"📍 **Mevki:** {st.session_state.g3_pozisyon}")
        if st.session_state.g3_ipucu > 2: st.info(f"🔤 **Baş Harfi:** {st.session_state.g3_oyuncu[0]}...")

        col1, col2 = st.columns([3, 1])
        with col1: tahmin = st.text_input("Bu kariyer yolu kime ait?", placeholder="Futbolcunun adını yazın...", key="g3_tahmin")
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💡 İpucu Ver (-20 Puan)", key="g3_ipucu_btn") and st.session_state.g3_ipucu < 3:
                st.session_state.g3_ipucu += 1
                st.session_state.g3_puan -= 20
                st.rerun()

        if tahmin:
            if tahmin.lower().strip() == st.session_state.g3_oyuncu.lower().strip():
                st.success(f"🎉 MÜTHİŞ BİR FUTBOL ZEKASI! Doğru cevap: **{st.session_state.g3_oyuncu}**")
                st.balloons()
                st.session_state.g3_aktif = False
                st.button("🔄 Yeni Soruya Geç", key="g3_yeni_soru")
            else:
                st.error("❌ Yanlış tahmin, tekrar dene veya ipucu al!")

        if st.button("🏳️ Pes Ediyorum", key="g3_pes"):
            st.warning(f"Doğru Cevap: **{st.session_state.g3_oyuncu}**")
            st.session_state.g3_aktif = False

# ==========================================
# 5. BÖLÜM: OYUN 4 - KİM DAHA GEZGİN?
# ==========================================
elif sayfa == "🏃‍♂️ Oyun 4: Kim Daha Gezgin?":
    st.title("🏃‍♂️ Kim Daha Gezgin? (Hız ve Refleks)")
    
    if 'g4_aktif' not in st.session_state: 
        st.session_state.g4_aktif = False
        st.session_state.g4_skor = 0
        st.session_state.g4_yanlis_mesaj = ""

    def siradaki_tur_g4(ilk_oyun=False):
        uygun_oyuncular = master_oyuncular[master_oyuncular['Takim'].apply(len) >= 2]
        if ilk_oyun or 'g4_p2' not in st.session_state:
            st.session_state.g4_p1 = uygun_oyuncular.sample(1).iloc[0]
        else:
            st.session_state.g4_p1 = st.session_state.g4_p2 

        p1_len = len(st.session_state.g4_p1['Takim'])
        p2_adaylari = uygun_oyuncular[uygun_oyuncular['Takim'].apply(len) != p1_len]
        st.session_state.g4_p2 = p2_adaylari.sample(1).iloc[0]

    if not st.session_state.g4_aktif:
        if st.session_state.g4_yanlis_mesaj:
            st.error(st.session_state.g4_yanlis_mesaj)
            st.warning(f"Toplam Yaptığın Doğru Sayısı: **{st.session_state.g4_skor}**")
        
        if st.button("🎮 Oyuna Başla", type="primary", key="start_g4"):
            st.session_state.g4_skor = 0
            st.session_state.g4_yanlis_mesaj = ""
            st.session_state.g4_aktif = True
            siradaki_tur_g4(ilk_oyun=True)
            st.rerun()

    if st.session_state.g4_aktif:
        st.metric("🔥 Mevcut Seri (Streak)", st.session_state.g4_skor)
        p1, p2 = st.session_state.g4_p1, st.session_state.g4_p2
        len1, len2 = len(p1['Takim']), len(p2['Takim'])

        col1, col2, col3 = st.columns([4, 2, 4])
        with col1:
            st.markdown(f"<div class='game-box'><h3>{p1['Oyuncu']}</h3><p>🌍 {p1['Uyruk']} <br> 📍 {p1['Pozisyon']}</p></div>", unsafe_allow_html=True)
            if st.button("👈 Bu Daha Gezgindir", use_container_width=True, key="btn_p1"):
                if len1 > len2:
                    st.session_state.g4_skor += 1
                    siradaki_tur_g4()
                    st.toast("✅ Doğru Bildin! Seri devam ediyor...", icon="🔥")
                else:
                    st.session_state.g4_yanlis_mesaj = f"❌ Maalesef seri bozuldu! {p1['Oyuncu']} ({len1} takım) oynarken, {p2['Oyuncu']} tam {len2} farklı takımda oynadı."
                    st.session_state.g4_aktif = False
                st.rerun()
                
        with col2: st.markdown("<div style='text-align:center; padding-top:40px;'><h1 style='color:#ff4b4b;'>VS</h1></div>", unsafe_allow_html=True)
            
        with col3:
            st.markdown(f"<div class='game-box'><h3>{p2['Oyuncu']}</h3><p>🌍 {p2['Uyruk']} <br> 📍 {p2['Pozisyon']}</p></div>", unsafe_allow_html=True)
            if st.button("Bu Daha Gezgindir 👉", use_container_width=True, key="btn_p2"):
                if len2 > len1:
                    st.session_state.g4_skor += 1
                    siradaki_tur_g4()
                    st.toast("✅ Doğru Bildin! Seri devam ediyor...", icon="🔥")
                else:
                    st.session_state.g4_yanlis_mesaj = f"❌ Maalesef seri bozuldu! {p2['Oyuncu']} ({len2} takım) oynarken, {p1['Oyuncu']} tam {len1} farklı takımda oynadı."
                    st.session_state.g4_aktif = False
                st.rerun()

# ==========================================
# 6. BÖLÜM: OYUN 5 - ŞİFRE AĞI (V2.0)
# ==========================================
elif sayfa == "🕸️ Oyun 5: Şifre Ağı (V2.0)":
    st.title("🕸️ Şifre Ağı (Köstebek Avı)")
    
    if 'g5_aktif' not in st.session_state: st.session_state.g5_aktif = False

    def yeni_oyun_baslat_g5():
        uygun_takim = False
        while not uygun_takim:
            hedef_takim = random.choice(takim_listesi)
            dogru_adaylar = master_oyuncular[master_oyuncular['Takim'].apply(lambda x: hedef_takim in x)]
            if len(dogru_adaylar) >= 4:
                uygun_takim = True

        hedef_sayi = random.randint(3, 4)
        dogru_secimler = dogru_adaylar.sample(hedef_sayi)
        yanlis_adaylar = master_oyuncular[master_oyuncular['Takim'].apply(lambda x: hedef_takim not in x)]
        yanlis_secimler = yanlis_adaylar.sample(16 - hedef_sayi)

        tum_kartlar = pd.concat([dogru_secimler, yanlis_secimler]).sample(frac=1).reset_index(drop=True)
        st.session_state.g5_hedef_takim = hedef_takim
        st.session_state.g5_hedef_sayi = hedef_sayi
        st.session_state.g5_kartlar = tum_kartlar.to_dict('records')
        st.session_state.g5_bulunanlar = []
        st.session_state.g5_durum = "devam" 
        st.session_state.g5_aktif = True

    if not st.session_state.g5_aktif:
        if st.button("🎮 Ağı Başlat", type="primary", key="start_g5"):
            yeni_oyun_baslat_g5()
            st.rerun()

    if st.session_state.g5_aktif:
        st.markdown(f"""
        <div class='game-box' style='background-color: #2b1717; border-color: #ff4b4b; margin-bottom: 25px;'>
            <h3 style='color: #aaaaaa;'>Hedef Şifre: <br><br>{get_logo_html(st.session_state.g5_hedef_takim, 50)}<span style='color: #ffffff; font-size: 34px;'>{st.session_state.g5_hedef_takim}</span></h3>
            <h4 style='color: #aaaaaa; margin-top: 15px;'>Bulman Gereken Kalan Oyuncu: <span style='color: #ff4b4b; font-size: 28px;'>{st.session_state.g5_hedef_sayi - len(st.session_state.g5_bulunanlar)}</span></h4>
        </div>
        """, unsafe_allow_html=True)

        if st.session_state.g5_durum == "kazandi":
            st.success("🎉 İNANILMAZ BİR ZİHİN! Şifre ağını hatasız çözdün ve tüm doğru ajanları buldun!")
            st.balloons()
            if st.button("🔄 Yeni Ağa Geç", key="btn_g5_win"):
                st.session_state.g5_aktif = False
                st.rerun()
        elif st.session_state.g5_durum == "kaybetti":
            st.error("💥 BOOM! Bir köstebeğe tıkladın ve ağ tamamen çöktü!")
            if st.button("🔄 Tekrar Dene", key="btn_g5_lose"):
                st.session_state.g5_aktif = False
                st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)
        for satir in range(4):
            kolonlar = st.columns(4)
            for sutun in range(4):
                idx = satir * 4 + sutun
                kart = st.session_state.g5_kartlar[idx]
                oyuncu_adi = kart['Oyuncu']

                with kolonlar[sutun]:
                    if oyuncu_adi in st.session_state.g5_bulunanlar:
                        st.button(f"✅ {oyuncu_adi}\n({kart['Uyruk']})", key=f"btn_found_{idx}", disabled=True, type="primary", use_container_width=True)
                    elif st.session_state.g5_durum != "devam":
                        if st.session_state.g5_hedef_takim in kart['Takim']:
                            st.button(f"🎯 {oyuncu_adi}\n(Doğruydu)", key=f"btn_locked_{idx}", disabled=True, use_container_width=True)
                        else:
                            st.button(f"❌ {oyuncu_adi}\n(Köstebek)", key=f"btn_locked_{idx}", disabled=True, use_container_width=True)
                    else:
                        if st.button(f"👤 {oyuncu_adi}\n({kart['Uyruk']})", key=f"btn_play_{idx}", use_container_width=True):
                            if st.session_state.g5_hedef_takim in kart['Takim']:
                                st.session_state.g5_bulunanlar.append(oyuncu_adi)
                                if len(st.session_state.g5_bulunanlar) == st.session_state.g5_hedef_sayi:
                                    st.session_state.g5_durum = "kazandi"
                                st.rerun()
                            else:
                                st.session_state.g5_durum = "kaybetti"
                                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 7. BÖLÜM: OYUN 6 - ÇAPRAZ ATEŞ (TÜM TAKIMLAR)
# ==========================================
elif sayfa == "✖️ Oyun 6: Çapraz Ateş (V3.0)":
    st.title("✖️ Çapraz Ateş (Matrix)")
    st.write("Sadece gerçek futbol gurmelerinin bitirebileceği 3x3'lük efsanevi ızgara! Kesişimdeki iki takımda da forma giymiş bir oyuncuyu bul.")

    if 'g6_aktif' not in st.session_state:
        st.session_state.g6_aktif = False

    def yeni_oyun_baslat_g6():
        tum_kullanimlar = []
        for t_list in master_oyuncular['Takim']: tum_kullanimlar.extend(t_list)
        populer_takimlar = pd.Series(tum_kullanimlar).value_counts().index.tolist()
        
        en_iyi_matris = None
        en_iyi_skor = -1
        
        for _ in range(50):
            random.shuffle(populer_takimlar)
            satir_takimlari = populer_takimlar[0:3]
            sutun_takimlari = populer_takimlar[3:6]
            
            cevaplar = {}
            kilit_grid = {}
            gecerli_hucre = 0
            
            for r in range(3):
                for c in range(3):
                    t1, t2 = satir_takimlari[r], sutun_takimlari[c]
                    ortaklar = master_oyuncular[master_oyuncular['Takim'].apply(lambda x: t1 in x and t2 in x)]
                    
                    if len(ortaklar) > 0:
                        cevaplar[(r,c)] = [oy.lower().strip() for oy in ortaklar['Oyuncu']]
                        st.session_state[f"g6_gercek_isim_{r}_{c}"] = {oy.lower().strip(): oy for oy in ortaklar['Oyuncu']}
                        gecerli_hucre += 1
                    else:
                        cevaplar[(r,c)] = []
                    kilit_grid[(r,c)] = None 
            
            if gecerli_hucre > en_iyi_skor:
                en_iyi_skor = gecerli_hucre
                en_iyi_matris = (satir_takimlari, sutun_takimlari, cevaplar, kilit_grid)
                
            if gecerli_hucre >= 6: 
                break

        st.session_state.g6_satirlar, st.session_state.g6_sutunlar, st.session_state.g6_cevaplar, st.session_state.g6_grid = en_iyi_matris
        st.session_state.g6_aktif_hucre = None
        st.session_state.g6_kalan = en_iyi_skor
        st.session_state.g6_aktif = True

    if not st.session_state.g6_aktif:
        if st.button("🎮 Yeni Matris Oluştur", type="primary", key="start_g6"):
            yeni_oyun_baslat_g6()
            st.rerun()

    if st.session_state.g6_aktif:
        st.markdown(f"**Hedef:** Oynanabilir <span style='color:#ff4b4b; font-weight:bold;'>{st.session_state.g6_kalan}</span> kesişim hücresini doldur!", unsafe_allow_html=True)
        
        satirlar = st.session_state.g6_satirlar
        sutunlar = st.session_state.g6_sutunlar
        
        cols = st.columns([1, 2, 2, 2])
        for c in range(3):
            with cols[c+1]:
                st.markdown(f"<div style='text-align:center;'>{get_logo_html(sutunlar[c], 60)}</div>", unsafe_allow_html=True)
                
        for r in range(3):
            st.markdown("<br>", unsafe_allow_html=True)
            cols = st.columns([1, 2, 2, 2])
            with cols[0]:
                st.markdown(f"<div style='text-align:center; padding-top:5px;'>{get_logo_html(satirlar[r], 60)}<br><small>{satirlar[r]}</small></div>", unsafe_allow_html=True)
            
            for c in range(3):
                with cols[c+1]:
                    cevap_listesi = st.session_state.g6_cevaplar[(r,c)]
                    doldurulan = st.session_state.g6_grid[(r,c)]
                    
                    if len(cevap_listesi) == 0:
                        st.button("⬛ Yok", key=f"grid_{r}_{c}", disabled=True, use_container_width=True)
                    elif doldurulan:
                        st.button(f"✅ {doldurulan}", key=f"grid_{r}_{c}", disabled=True, type="primary", use_container_width=True)
                    else:
                        if st.button("❓ Seç", key=f"grid_{r}_{c}", use_container_width=True):
                            st.session_state.g6_aktif_hucre = (r,c)
                            st.rerun()

        st.markdown("<hr>", unsafe_allow_html=True)

        if st.session_state.g6_kalan == 0:
            st.success("🏆 İNANILMAZ! Matristeki tüm kesişimleri başarıyla doldurdun, sen tam bir futbol profesörüsün!")
            st.balloons()
            if st.button("🔄 Yeni Matrise Geç"):
                st.session_state.g6_aktif = False
                st.rerun()
        elif st.session_state.g6_aktif_hucre:
            r, c = st.session_state.g6_aktif_hucre
            st.info(f"Hedef: **{satirlar[r]}** ve **{sutunlar[c]}** takımlarının ikisinde de oynamış bir futbolcu gir.")
            
            tahmin = st.text_input("Oyuncu adı:", key="g6_tahmin_input")
            col_a, col_b = st.columns([1, 5])
            with col_a:
                if st.button("Kutuyu Onayla", type="primary"):
                    tahmin_temiz = tahmin.lower().strip()
                    if tahmin_temiz in st.session_state.g6_cevaplar[(r,c)]:
                        gercek_isim = st.session_state[f"g6_gercek_isim_{r}_{c}"][tahmin_temiz]
                        st.session_state.g6_grid[(r,c)] = gercek_isim
                        st.session_state.g6_aktif_hucre = None
                        st.session_state.g6_kalan -= 1
                        st.toast(f"Harika! {gercek_isim} doğru cevap.", icon="🔥")
                        st.rerun()
                    else:
                        st.error("❌ Yanlış tahmin, bu oyuncu iki takımda birden forma giymemiş!")
                        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🏳️ Matrisi Temizle ve Pes Et", key="g6_pes"):
            st.session_state.g6_aktif = False
            st.rerun()
