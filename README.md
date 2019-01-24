# Landschaftsgenerator
Für Blender 2.7.9b
![Beispiel-Render einer Landschaft](/Landschaftsgenerator_Render.png)

## Installationsanleitung
1. [Landschaftsgenerator.zip](Landschaftsgenerator.zip) downloaden
2. Addon in Blender einfügen
3. Den Renderer auf Cycles umstellen
4. Unter Create befinden sich die neuen GUI-Elemente

## Bedienung
Die Schritte bitte in der korrekten Reihenfolge ausführen:

### Eine Landschaft generieren:
1. Koordinaten des Mittelpunktes des gewünschten Kartenausschnitts in die Felder `Lat` und `Long` eingeben.
2. Skalierungsfaktor eingeben (gibt die Größe des Ausschnitts in Grad an)
3. Höhenskalierung der Karte eingeben
4. Auf `Create Landscape` klicken

Das Erstellen der Lanschaft kann einige Momente (bis zu einigen Minuten) dauern, da die Daten erst aus dem Internet bezogen werden müssen. Wird der gleiche Ausschnitt nochmal ausgewählt geht es schneller, da die Daten zwischengespeichert werden.

###  Texturen erstellen:
1. Das erstellte Objekt auswählen
2. Auf `Create Texture` klicken
3. `Viewport Shading` auf `Material` stellen
4. Mit `Add Entry` können Layer hinzugefügt werden
5. Die Start- und Endhöhe sind Werte zwischen 0 und 1
6. Folgende Layernamen sind schon mit Default-Texturen hinterlegt:
    * `Sand`
    * `Grass`
    * `Gravel`
    * `Rock`
    * `Snow`
7. Es können auch eigene Namen eingegeben werden. So können eigene Texturen eingeladen werden. Siehe [Eigene Texturen einfügen](#own-textures)
8. `Layer Blending` gibt an, wie stark die Übergänge zwischen den Layern miteinander verschmelzen
9. `Steepness Layer Name` funktioniert wie ein normaler Layer, hier können auch die oben genannten Layernamen eingetragen werden
10. `Steepness Threshold` gibt die Flankensteilheit in Grad an, ab der der Steepness Layer genutzt werden soll
11. `Texture Scaling` gibt an, wie groß die Texturen skaliert werden sollen (die Default-Texturen sind 2048x2048 Pixel groß)

### <a name="own-textures"></a>Eigene Texturen einfügen
1. Wird ein Layer mit einem eigenen Namen benannt wird eine entsprechende Material-Node angelegt. Wird zum Beispiel ein Layer `Wasser` genannt, findet sich im Node-Editor die Node `Wasser` wieder. In diesem Node-Tree ist eine Node-Group mit dem Namen `LST_M_[Name]`.
2. Die Node-Group mit dem entsprechenden Namen öffnen
3. Hier ist ein Principled Shader mit Texture-Nodes angelegt. Diese können nun mit eigenen Texturen befüllt werden.