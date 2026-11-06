# Deney Kaydı

Her deney buraya, başarısız olanlar da dahil, yapıldığı sırayla yazılır. Kurallar için bkz. [PROTOCOL.md](PROTOCOL.md).

Biçim: kod · tarih · veri sürümü · amaç · yöntem · sonuç · durum (`ön-protokol`, `geliştirme`, `keşif`, `doğrulama`).

---

## E0 · Protokol öncesi bulgular

Aşağıdakiler protokol yazılmadan önce yapıldı. Hipotez üretmek için kullanılabilirler ama kanıt sayılmazlar.

### E0.1 · Sıklet değiştirenler

- **Tarih / veri:** 2026-11-05 · `db-2026-11-04-1837`
- **Amaç:** Global puan ölçeği ağır veya hafif sıkletler lehine sistematik olarak bozuk mu?
- **Yöntem:** Önceki etiketli sıkleti mevcut maçtan farklı olan dövüşçüler, rakipleri o sıkletin yerlisiyken
  (rakibin önceki sıkleti = maçın sıkleti), iki tarafın da ≥3 önceki maçı varsa. Kalıntı = gerçek galibiyet oranı − ortalama tahmin.
- **Sonuç:**

  | Durum | Maç | Ortalama tahmin | Galibiyet oranı | Kalıntı |
  |---|---|---|---|---|
  | 1 sıklet yukarı | 12.744 | 0,488 | 0,456 | −0,031 |
  | 1 sıklet aşağı | 14.058 | 0,454 | 0,425 | −0,029 |
  | 2+ yukarı | 1.473 | 0,447 | 0,381 | −0,066 |
  | 2+ aşağı | 1.533 | 0,418 | 0,350 | −0,068 |

- **Yorum:** Kalıntılar yönden bağımsız (simetrik), yani belirli bir sıklet yönünde ölçek sapması görülmüyor.
  Sıklet değiştirmenin kendisinin bir maliyeti (veya seçilim etkisi) var. Verinin neredeyse tamamı 2010 sonrası.
  → H4'ün kaynağı.
- **Durum:** ön-protokol

### E0.2 · Karar türü ağırlıkları

- **Tarih / veri:** 2026-11-05 · `db-2026-11-04-1837`
- **Amaç:** Karar türüne göre kesirli sonuç (UD 0,9 · MD 0,6 · SD 0,55) düz şemadan (tüm galibiyetler 1,0) daha iyi mi tahmin ediyor?
- **Yöntem:** Şema, daha önce ≤2015 eğitim döneminde 3 aday arasından seçilmişti. 2016+ birincil popülasyonda
  (iki taraf ≥3 önceki maç, n = 78.573) maç bazında eşleştirilmiş log loss farkı; etkinlik düzeyinde kümelenmiş bootstrap (B = 500).
- **Sonuç:** fark −0,00474, %95 GA [−0,00553, −0,00393]; maç bazında farkın standart sapması 0,114 (§4.3 güç hesabında kullanıldı).
- **Yorum:** Etki gerçek görünüyor ve §5'teki 0,001 eşiğinin üstünde. Ancak ağırlıklar veriden tahmin edilmedi;
  H1'de tahmin edilmiş değerlerle yeniden sınanacak.
- **Durum:** ön-protokol

---

## E1 · Aşama 2 hazırlığı

### E1.1 · Altyapının sentetik veriyle doğrulanması

- **Tarih / veri:** 2026-11-06 · yalnızca sentetik veri (`src/mmarank/research/synthetic.py`, tohum 1). Gerçek veride hiçbir model çalıştırılmadı.
- **Amaç:** Değerlendirme altyapısının (§6.1) doğru çalıştığını gerçek sonuçlara bakmadan göstermek.
- **Yöntem:**
  1. Modellerin güncelleme formülleri yayımlanmış sayısal örneklerle karşılaştırıldı: Glickman (1999) ve (2001) örnekleri,
     TrueSkill'in varsayılan ayarlarla bilinen değerleri.
  2. Sızıntı testi: her model için, *D* gününe kadarki tahminler sonraki maçlar silindiğinde birebir aynı kalıyor mu?
  3. Aynı gün içinde maç sırası Elo, Glicko-1 ve Glicko-2'nin tahminlerini değiştiriyor mu?
  4. Bilinen λ ve kalibrasyon eğimi simüle veriden geri kazanılıyor mu?
  5. Sentetik dünya: dövüşçüler gelir, gücü aylık rastgele yürüyüşle değişir, emekli olur. Eşleştirme gürültülü gerçek güce göre yapılır;
     P(A kazanır) = lojistik(güç farkı); maçların %1,4'ü beraberlik. 78.716 kararlı maç, 10.647 dövüşçü.
     Bütün ızgaralar (455 ayar) çalıştırılıp iç içe seçim yapıldı.
- **Sonuç:**
  - 1–4: hepsi geçti (`tests/test_research.py`, 16 test).
  - 5: birincil popülasyonda, 2008–2025 (n = 41.892):

    | | Kendi formülüyle | λ ile | λ (2025 penceresi) |
    |---|---|---|---|
    | Gerçek olasılıklar (kâhin) | 0,5977 | — | — |
    | M0 Elo | 0,6708 | 0,6680 | 0,50 |
    | M1 Glicko-1 | 0,6694 | 0,6611 | 0,43 |
    | M2 Glicko-2 | 0,6693 | 0,6611 | 0,43 |
    | M3 TrueSkill | 0,6697 | 0,6629 | 0,32 |

  - Durağan bir dünyada (güç değişmiyor, rastgele eşleştirme, 20'den fazla önceki maç) modeller kâhine yaklaşıyor
    (Glicko-1 0,566, kâhin 0,546). Aradaki fark, dövüşçü başına maç sayısının azlığından geliyor.
- **Yorum:**
  1. Altyapıda hata bulunmadı.
  2. **λ belirgin biçimde 1'in altında.** Bu dünyada eşleştirmeyi yapan taraf gerçek gücü derecelerden iyi biliyor. Eşleşen iki dövüşçünün gerçek
     farkı, derece farkının gösterdiğinden küçük; bu yüzden modeller aşırı özgüvenli. §6'daki λ yorumuna bir ekleme: **λ < 1 yalnızca tahmin
     gürültüsünden değil, bilgili eşleştirmeden de gelebilir.** Gerçek MMA'da maç yapımcıları derecelerin göremediği bilgiyi kullanır;
     gerçek verideki λ bu iki etkiyi ayırt edemez.
  3. Seçilen ayarlar sık sık ızgara sınırına dayandı (ör. λ'sız Glicko'da en küçük başlangıç RD'si: model, özgüvenini başka yoldan düşürüyor).
     Bu nedenle §6.1'deki genişletme kuralına üst sınır eklendi (protokol v0.9, deneyden önce).
  4. Sentetik sonuçlar gerçek MMA hakkında kanıt değildir.
- **Durum:** geliştirme (altyapı doğrulaması)

