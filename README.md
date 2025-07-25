# KI-Prototyp: Brautkleid-Empfehlung basierend auf Körperform

## Projektbeschreibung
Dieser Prototyp unterstützt Nutzer:innen bei der Auswahl eines passenden Brautkleides.  
Basierend auf einem hochgeladenen Ganzkörperbild wird die individuelle Körperform analysiert, um Empfehlungen für geeignete Brautkleidschnitte abzuleiten.

### 🔍 Funktionsweise
1. **Figurenerkennung mittels KI**  
   - Das hochgeladene Bild wird per OpenAI-API analysiert, um eine der fünf typischen Körperformen zu bestimmen:
     - Sanduhr
     - Birne
     - Apfel
     - Rechteck
     - Umgekehrtes Dreieck
2. **Expertenbasierte Kleidschnitt-Empfehlung**  
   - Basierend auf Interviews mit Stylist:innen werden geeignete Brautkleid-Schnitte vorgeschlagen.  
   - Empfehlungen werden als Balkendiagramm mit Plotly visualisiert (A-Linie, Prinzessin, Meerjungfrau, Empire).

### ⚙️ Technische Umsetzung
- **Backend:** Python  
- **Framework:** [Gradio](https://gradio.app/)  
- **KI:** OpenAI GPT-4 API  
- **Visualisierung:** Plotly  
- **Weitere Tools:** Pillow, Pandas, python-dotenv  

---
