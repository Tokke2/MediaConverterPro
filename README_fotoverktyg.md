# Fotoverktyg – bildförbättring + Datumfix + EXIF

En gemensam skrivbordsapp med flikarna **Bildförbättring**, **Fotoredigerare**, **AVIF/HEIC → JPEG**, **Annonsbilder → JPEG** och **Datum & EXIF**. Välj en källmapp och en separat arkivmapp. Originalen lämnas orörda; bearbetade kopior sparas i arkivmappen. Bilder kan förstoras 1×–4×, få starkare färg/kontrast och skärpas. Bilder och videor kan få nytt datum eller tidsförskjutning och programnamn/metadata kan rensas. Video bildförbättras inte.

## Installera och starta

Python 3.10+ rekommenderas.

```bash
python -m pip install PyQt6 Pillow pillow-heif piexif
pythonw fotoverktyg.pyw
```

Appen erbjuder installation av saknade frivilliga tillägg (`pillow-heif`, `piexif`) vid start och har en knapp för att installera/uppdatera Pillow, pillow-heif och piexif. **PyQt6 och Pillow behövs innan appen kan starta**; PyQt6 kan inte uppdateras säkert medan appen körs. Starta om efter installation.

Installera även **ExifTool** separat och se till att kommandot `exiftool` fungerar i terminalen. Det behövs för metadata i video, HEIC, RAW, PNG, WEBP och bred EXIF-rensning. Utan ExifTool kan `piexif` hantera JPEG/TIFF, men vissa metadatafunktioner fungerar inte. På Linux kan Qt kräva systembibliotek för grafiskt gränssnitt.

## Användning

1. Välj källmapp och arkivmapp. Dra och släpp en mapp på fältet om du vill.
2. På **Bildförbättring**: välj förstoring, skärpa, färgstyrka och klarhet. Avmarkera bildförbättring för att enbart arbeta med datum/metadata.
3. På **Fotoredigerare**: öppna ett enskilt foto, rotera med knapparna, dra en markering på förhandsvisningen och klicka **Klipp markering**. **Ångra** backar ett steg i taget. **Spara kopia** använder bildförbättringsreglagen och sparar PNG/JPEG/WEBP utan att ändra originalet.
4. På **AVIF/HEIC → JPEG**: lägg till AVIF-, HEIC- eller HEIF-filer, välj målmapp och JPEG-kvalitet (95 rekommenderas), och starta konvertering. Transparens ersätts av vitt; källfiler skrivs aldrig över. EXIF/färgprofil kan bevaras om du väljer det.
5. På **Annonsbilder → JPEG**: klistra in en eller flera offentliga Blocket-länkar av typen `https://www.blocket.se/recommerce/forsale/item/27022380` **eller** `https://www.blocket.se/mobility/item/24141675`, en per rad. Standardmappen är `out` bredvid appfilen; för varje annons skapas en undermapp med annonsens titel, till exempel `out/Chevrolet Suburban/`. Klicka **Välj mapp…** om du vill välja en annan basmapp och därefter **Hämta alla galleribilder som JPEG**. Även i en vald basmapp får varje annons en titel-undermapp. Filnamn som inte är tillåtna i Windows rensas automatiskt. Appen letar efter alla unika bild-ID:n i annonsens galleri, även bilder som bara syns som miniatyrer, och försöker med 1600w, sedan 1280w/960w/default om högsta storleken saknas. Loggen visar hur många som hittades och hur många som sparades. Den skriver aldrig över tidigare filer.
6. På **Datum & EXIF**: välj fast datum eller offset. Välj om datum i metadata och filsystem ska ändras. Kryssa i **Radera ALL befintlig EXIF/metadata** om du vill rensa metadata helt; om datumuppdatering är markerad skrivs nya datumtaggar efter rensningen.
7. Klicka **Bearbeta kopior** för mappbearbetning. Kontrollera loggen efteråt; `DELVIS` betyder att kopian skapades men en metadata- eller tidsåtgärd misslyckades.

**Viktigt:** Full metadatarensning kan även ta bort GPS, kamerainställningar, färgprofiler och annan information. Testa på kopior först. Om **Behåll befintlig EXIF** markeras vid bildexport kan gamla metadata följa med, om inte full rensning utförs efteråt. På Linux går filens skapandetid normalt inte att ändra; ändrings- och åtkomsttid uppdateras. Förlustfri förstoring ger fler pixlar men skapar inte verkliga detaljer som saknas i originalbilden. Arkivfiler skrivs inte över om du inte uttryckligen markerar det.

**Annonsbilder:** Jag har verifierat att exemplet med annons-ID 27022380 publicerar tre galleribilder och att en bild-URL svarar vid testtillfället. Blocket kan ändra sidans HTML eller begränsa hämtning, så det finns ingen garanti för varje annons eller över tid. Hämta bara bilder du har rätt att använda; appen kringgår inte inloggning eller spärrar. JPEG-kopior blir inte skarpare än annonsens källbilder.

## Design, ikon och autostart

Gränssnittet har nu mörkt/ljust tema, större fönster, tydligare flikar, en gemensam ikon i fönster, flikar och knappar samt filen `fotoverktyg_icon.png` för genvägar. **Starta automatiskt vid inloggning** är frivilligt och avstängt om det inte aktiverats tidigare. Det registreras endast för ditt användarkonto: Windows `HKCU Run`, macOS `~/Library/LaunchAgents` eller Linux `~/.config/autostart`. Avmarkera kryssrutan för att ta bort autostart. Flyttar du appfilen senare behöver du slå av/på autostart igen. Autostart startar bara fönstret, **inte** filbearbetning eller nedladdning.

På Linux behövs även Qt:s systembibliotek, exempelvis `libxkbcommon.so.0`, för att starta PyQt6; dessa kan inte installeras genom appens pip-knapp.

På Windows kan du dubbelklicka `fotoverktyg.pyw` för att starta utan konsolfönster (Python måste vara installerat och `.pyw` associerat med Python). På macOS/Linux är `.pyw` inte en garanti för konsolfri start; använd en grafisk genväg/launcher eller autostart.

## Ikon

Den nya ljusa och tydliga ikonen `fotoverktyg_icon.png` används som applikationsikon, fönsterikon, flikikon, knappikon och Linux-autostartikon. Håll PNG-filen i samma mapp som `fotoverktyg.pyw`. `fotoverktyg_icon.ico` finns också för Windows-genvägar eller framtida paketering till EXE. Om du redan hade autostart i Linux, avmarkera och markera alternativet igen för att uppdatera skrivbordsfilens ikon.

## Starta även om Python saknas (Windows)

Dubbelklicka **`Starta_Fotoverktyg.vbs`** i stället för `.pyw` om du vill få hjälp att installera Python. Behåll `.vbs`, `.ps1`, `.pyw` och ikonfilen i samma mapp. Startaren körs utan konsolfönster. Om Python 3 saknas får du en fråga innan något installeras. Om `winget` finns kan den installera Python för ditt användarkonto; annars erbjuds en länk till python.org. Starta om startaren efter installationen (ibland behöver du logga ut/in). Python-installationen är inte samma sak som Python-paketen: installera därefter `PyQt6` och `Pillow` enligt kommandot ovan om de saknas.

**Begränsning:** En ensam `.pyw`-fil kan inte visa en installationsfråga när Python saknas, eftersom den då inte kan köras. Därför behövs de två separata Windows-startfilerna. VBS-startaren begär inte administratörsrättigheter; `winget`-installationen kräver användarens godkännande. På macOS/Linux behövs en separat installationsmetod via systemets pakethanterare.

## Loggning

Fliken **Aktivitetslogg** samlar händelser från alla delar av appen: användarklick, bildredigering, batchkörningar, annonsnedladdning, konvertering, installation/uppdatering, autostart, fel och avbrott. Varje filresultat loggas även i relevant arbetsflik. Logg sparas automatiskt i `~/.fotoverktyg_studio/logs/fotoverktyg.log` (på Windows i din användarprofil); upp till tre roterade äldre loggar behålls, med max 5 MB per fil. Windows-startaren använder `startare.log` i samma mapp, även om appen inte lyckas öppnas. Knappen **Exportera hela loggen…** sparar aktuell huvudlogg. Loggarna kan innehålla lokala filvägar och annons-ID: dela dem bara med personer du litar på. Om appen inte kan skriva i din användarprofil kan loggning till fil utebli.

**Mobility:** Länkar av typen `/mobility/item/ID` stöds nu. Jag verifierade att exempelannonsen `24141675` har 12 unika galleribilder i sidans HTML och att den första högupplösta bildlänken svarade.

**Direkta bildlänkar:** Fliken Bildlänkar → JPEG accepterar även direkta HTTPS-länkar till JPG/PNG/WEBP/AVIF/HEIC. Dessa sparas i `out/Direkta bilder/` som JPEG; dubbla filnamn får nummer. WEBP-exemplet från wermlandopera.com svarade vid testet med en bild på 2000 × 670 pixlar. AVIF/HEIC kräver `pillow-heif`. En direktlänk är ingen annons och får därför ingen annonstitelmapp.

## Separata nedladdningsflikar

**Blocket → JPEG** accepterar endast annonslänkar och skapar en mapp med annonsens titel. **Webbbilder → JPEG** accepterar endast direkta HTTPS-länkar till bildfiler och sparar dem i `out/Direkta bilder/` som standard. Flikarna har varsin länklista, målmapp, start/avbryt, status och logg. Tidigare hänvisningar till en gemensam flik ”Bildlänkar → JPEG” avser nu dessa två separata flikar.

## Efter hämtning

När Blocket- eller Webbbilder-hämtningen slutförts utan fel och minst en bild sparats rensas länkfältet automatiskt. Vid fel eller avbrott behålls länkarna så att du kan försöka igen. Om bilder sparats öppnas output-mappen automatiskt i filhanteraren: annonstitelns mapp för en annons, basmappen för flera annonser, eller `Direkta bilder` för webblänkar. Om filhanteraren inte kan öppnas finns sökvägen kvar i loggen.
