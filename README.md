# MMA Rankings

Şeffaf, yeniden üretilebilir ve tarihsel olarak sorgulanabilir MMA derecelendirmeleri.
Her aylık liste yalnızca o ayın sonuna kadar yapılmış maçlarla hesaplanır.

## Çalıştırma

```bash
uv sync
uv run mmarank build            # en son Fight Canon sürümünü indirir, build/site üretir
uv run mmarank build --tag db-2026-11-04-1837   # belirli bir sürüm
uv run mmarank backtest         # tahmin başarısı raporu
uv run mmarank tune             # parametre taraması (yalnızca <=2015 verisiyle)
uv run pytest
python3 -m http.server 8765 --directory build/site
```

## Veri akışı

1. **Kaynak:** [Fight Canon](https://github.com/jadevit/fight-canon-db) SQLite sürümü (`data/raw/<tag>/`, git'e girmez).
   Kullanılan her ayın ilk sürümü bu deponun Releases bölümüne arşivlenir.
2. **Temizlik** (`data.py`): yalnızca profesyonel maçlar; NC, DQ, iptal edilen ve sonucu
   bilinmeyen maçlar çıkarılır. Aynı iki dövüşçünün 30 gün içinde farklı etkinliklerde aynı
   sonuçla görünen kayıtlarından yalnızca en detaylısı tutulur (`build/site/data/duplicates_removed.json`).
3. **Cinsiyet:** Fight Canon + Wikidata (`data/external/wikidata_sherdog_sex.csv`, CC0) başlangıç
   etiketleri, sonra rakipler üzerinden yayılım. Çelişkiler `sex_conflicts.json` dosyasına yazılır.
4. **Sıklet** (`divisions.py`, `mappings/weight_class_overrides.csv`): etiket metni kanonik sıklete
   çevrilir; PRIDE, DREAM ve 2001 öncesi UFC gibi farklı limit kullanan dönemler için elle eşleme.
5. **Model** (`glicko.py`, `engine.py`): Glicko-1, tek global havuz, bitiş yöntemine göre ağırlıklı
   sonuç. Aynı gündeki maçlar eşzamanlı güncellenir. Yeni dövüşçünün başlangıç puanı, ilk maçını
   yaptığı organizasyonun son 24 aydaki deneyimli dövüşçülerinin ortalamasından (k=10 ile 1500'e
   çekilerek) 100 eksiktir; yalnızca o tarihe kadarki puanlar kullanılır.
6. **Listeler** (`export.py`): ay sonu anlık görüntüleri, sıralama puanı μ − 2·RD.

Tüm parametreler `config.py` içinde; sitedeki `params_hash` onların özetidir.

## Bilinen sınırlamalar

- 2000'ler bölgesel maçlarının çoğunda sıklet etiketi yok; bazı dövüşçülerin sıkleti sonraki
  bir maçlarından çıkarılır (sitede ≈ ile işaretli).
- Organizasyon önceliği küçük organizasyon şişirmesini azaltır ama tamamen yok etmez; ilk maçı
  bilinmeyen kayıtlar (eksik erken dönem verisi) yine 1500 civarından başlar.
- 2001 öncesi UFC'de unvan maçı olmayan "Lightweight" etiketleri belirsiz olduğu için yok sayılır.
- Kadın listeleri ve P4P yerine düşünülen "sıklet içi üstünlük endeksi" sonraki aşamada.
- Resmî bir sıralama değildir.
