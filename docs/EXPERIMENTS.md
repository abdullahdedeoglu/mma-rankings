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
