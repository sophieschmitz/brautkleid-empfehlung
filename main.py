from dotenv import load_dotenv
from openai import OpenAI
import os
import io
import base64
from PIL import Image
import gradio as gr
import json
import plotly.graph_objects as go
import random

# OpenAI client
load_dotenv() # .env laden
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # OpenAI API key


##########################################


# Empfehlungstabellen für Brautkleid-Schnitte basierend auf Figurform
empfehlungen = {
    "Sanduhr": {
        "A-Linie": 0.80,
        "Meerjungfrau": 0.95,
        "Empire": 0.45,
        "Prinzessin": 0.80
    },
    "Birne": {
        "A-Linie": 0.90,
        "Meerjungfrau": 0.35,
        "Empire": 0.70,
        "Prinzessin": 0.80
    },
    "Apfel": {
        "A-Linie": 0.80,
        "Meerjungfrau": 0.20,
        "Empire": 0.90,
        "Prinzessin": 0.6
    },
    "Rechteck": {
        "A-Linie": 0.90,
        "Meerjungfrau": 0.25,
        "Empire": 0.50,
        "Prinzessin": 0.80
    },
    "Umgekehrtes Dreieck": {
        "A-Linie": 0.90,
        "Meerjungfrau": 0.40,
        "Empire": 0.60,
        "Prinzessin": 0.80
    },
    "Unklar": {
        "Unklar": 100
    }
}

# GPT-Antwort verarbeiten
def parse_gpt_response(response_text):
    try:
        parsed = json.loads(response_text)
        return parsed.get("Figur", "Unbekannt")
    except:
        for figur in empfehlungen.keys():
            if figur.lower() in response_text.lower():
                return figur
        return "Unklar"

# GPT-Figurform-Erkennung
def erkenne_figurform(image):
    print("Button wurde geklickt. Beginne mit der Verarbeitung...")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_bytes = buffered.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    print("Bild wird verarbeitet...")

    try:
        # Define the request to OpenAI
        response = client.responses.create(
            model="gpt-4o", 
            instructions=(
                "Du bist ein Assistent, der basierend auf einem Ganzkörperbild eine von fünf typischen Körperformen erkennt: "
                "Sanduhr, Birne, Apfel, Rechteck und Umgekehrtes Dreieck. "
                "Rechteck ist eine valide Form und bedeutet, dass Schultern, Taille und Hüfte ungefähr gleich breit sind. "
                "Wenn die Proportionen neutral oder unscheinbar wirken, ist die Form sehr wahrscheinlich 'Rechteck' – und **nicht 'Unklar'**. "
                "Antworte **ausschließlich** in diesem JSON-Format: {\"Figur\": \"NameDerFigur\"}. "
                "Beispielhafte Zuordnung (nur intern, nicht mitausgeben): "
                "- Sanduhr: Schulter ≈ Hüfte, deutlich schmalere Taille "
                "- Birne: Hüfte deutlich breiter als Schulter "
                "- Apfel: Breiter Bauch/Mitte, wenig Taille "
                "- Rechteck: Alles etwa gleich breit, keine sichtbare Taille "
                "- Umgekehrtes Dreieck: Schulter deutlich breiter als Hüfte "
                "Nur für den absoluten Ausnahmefall, wenn du überhaupt keine Person erkennst, antworte mit {\"Figur\": \"Unklar\"}. Solange aber eine Person im Bild zu sehen ist, muss zwingend einer Figur geantwortet werden."
            ),
            input=(
                "Welche Figurform siehst du in diesem Bild? "
                f"data:image/jpeg;base64,{img_base64}"
            ),
        )

        # Extrahiere Antwort des assistants 
        result = response.output_text
        print("Antwort erhalten:", result)

        # Extrahiere die Form
        figurform = parse_gpt_response(result)
        return figurform
    except Exception as e:
        print("API-Fehler:", str(e))
    return "Fehler"


def reduce_image_size(image):
    '''
    Reduziere Bildgröße, um die Anzahl der übertragenen Tokens bei der Nutzung der OpenAI-API zu verringern
    '''
    max_size = 300
    width, height = image.size
    
    # Prüfen, ob Resize nötig ist
    if max(width, height) <= max_size:
        return image  # keine Änderung nötig
    
    # Berechne Skalierungsfaktor, um max Seite auf 300 zu setzen
    if width > height:
        new_width = max_size
        new_height = int(height * max_size / width)
    else:
        new_height = max_size
        new_width = int(width * max_size / height)
    
    # Proportional skalieren
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    return resized_image

def create_random_numbers(value):

    return random.uniform(max(0.26, value - 0.16), min(value + 0.16, 0.97))

 
# Plot Erstellung (Balkendiagramm)
def plot_brautkleid_vorschläge(score_dict):

    # Zuerst Werte randomisieren 
    randomized_dict = {key: create_random_numbers(value) for key, value in score_dict.items()}

    # Randomisierten Werte sortieren
    sorted_items = sorted(randomized_dict.items(), key=lambda x: x[1], reverse=False)
    labels = [item[0] for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    colors = [
    "#d2cfc5",  # hellster Ton
    "#a8aca4",
    "#94938a",
    "#606060"   # dunkelster Ton
]

    #starte leeres Plotly Programm  
    fig = go.Figure()
    bar_height = 5.5  # Doppelt so dick wie zuvor (2.4 * 2)
    y_gap = 0.3  # Sehr geringer Abstand zwischen den Balken

    for i, (label, value) in enumerate(zip(labels, values)):
        y_pos = i * (bar_height + y_gap)

        # Hintergrundbalken
        fig.add_trace(go.Bar(
            y=[y_pos],
            x=[1],
            orientation='h',
            marker=dict(color="rgba(200, 200, 200, 0.2)"),
            width=bar_height,
            hoverinfo='skip',
            showlegend=False
        ))

        # Hauptbalken
        fig.add_trace(go.Bar(
            y=[y_pos],
            x=[value],
            orientation='h',
            marker=dict(color=colors[i % len(colors)]),
            width=bar_height,
            hoverinfo='skip',
            showlegend=False
        ))

        # Label links im Balken
        fig.add_trace(go.Scatter(
            x=[0.08],
            y=[y_pos],
            text=[label],
            mode="text",
            textfont=dict(color='white', size=24, family="Segoe UI, sans-serif"),
            showlegend=False,
            hoverinfo='skip'
        ))


        # Prozentzahl rechts im Balken
        fig.add_trace(go.Scatter(
            x=[value - 0.05],
            y=[y_pos],
            text=[f"{int(value * 100)}%"],
            mode="text",
            textfont=dict(color='white', size=24, family="Segoe UI, sans-serif"),
            showlegend=False,
            hoverinfo='skip'
        ))

    # Layout
    fig.update_layout(
        height=len(labels) * (bar_height + y_gap) * 25,  # Angepasste Höhe des Diagramms
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(visible=False, range=[0, 1.08]),
        yaxis=dict(
            tickvals=[],
            range=[-bar_height/2, len(labels) * (bar_height + y_gap) - y_gap]  # Angepasster y-Achsenbereich
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        barmode="overlay"
    )
    
    # Save plot
    folder = "tmp"
    os.makedirs(folder, exist_ok=True)  # Ordner erstellen, falls nicht vorhanden
    fig.write_image(os.path.join(folder, "plot_temp.png"), width=1300, height=600)

    return fig


css = """
html, body, .gradio-container {
    height: 100% !important;
}
.gradio-container { 
font-size: 18px !important; 
}
.gr-blocks {
    height: 100% !important;
    display: flex;
    flex-direction: column;
    justify-content: center;
}
"""


with gr.Blocks(css=css) as demo:
    gr.Markdown("## 👰🏼‍♀️ Finde das perfekte Brautkleid – mit KI!")
    gr.Markdown("Lade ein Ganzkörperbild hoch – die KI erkennt deine Figur und zeigt passende Brautkleid-Schnitte an.")

    with gr.Row():
        with gr.Column(scale=1):
            bild = gr.Image(type="pil", label="📸 Ganzkörperbild hochladen", height=600)
            button = gr.Button("💬 Figur analysieren & Vorschläge anzeigen")

        with gr.Column(scale=2):
            ausgabe_plot = gr.Image(label="📷 Lokales Bild", visible=True, height=550)
            ausgabe_text = gr.Textbox(label="📢 Status / Fehler", lines=2, max_lines=4)

    def verarbeite_bild(image):
        
        # Bild-Größe beschränken -> weniger Kosten bei API Nutzung
        image = reduce_image_size(image)
        
        # Figur Erkennung mit ChatGPT (über OpenAI API)
        figurform = erkenne_figurform(image)

        # Error Handling: LLM hat keine oder keine bekannte Figurform erkannt
        if figurform == "Fehler":
            chart_data = {"Schnitt": ["Fehler"], "Prozent": [100]}
            status = "⚠️ Fehler bei der Verarbeitung. Versuche es erneut."
        elif figurform not in empfehlungen:
            chart_data = {"Schnitt": ["Unbekannt"], "Prozent": [100]}
            status = f"🤔 Figurform nicht erkennbar: '{figurform}'"
            
        # LLM hat eine bekannte Figurform erkannt -> Erstelle einen Plot
        else:
            status = "Erkannte Figurform: " + figurform + str(empfehlungen[figurform])
            print(empfehlungen[figurform])
            plot_brautkleid_vorschläge(empfehlungen[figurform])
        # Erstellten Plot laden und 
        try:
            new_plot = Image.open(os.path.join("tmp", "plot_temp.png"))
        except Exception as e:
            new_plot = None
            status += f"\n⚠️ Lokales Bild konnte nicht geladen werden: {e}"

        return new_plot

    button.click(fn=verarbeite_bild, inputs=bild, outputs=[ausgabe_plot])

demo.launch()

