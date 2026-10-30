# MediaForge — Photo & Video Toolkit

En gemensam skrivbordsapp för foton och video. Flikarna omfattar **Bildförbättring**, **Bildoptimering**, **Bildbibliotek**, **Fotoredigerare**, **Bildspel → MP4**, **Dubblettfinnare**, **Färgprofiler**, **Videokonvertering**, **Videostabilisering**, **Ljudförbättring**, **Codec-rapport**, **Ljud från video**, **Skapa musik-DVD**, **AVIF/HEIC → JPEG**, **Annonsbilder → JPEG**, **Webbbilder → JPEG**, **Blocket → JPEG**, **Datum & EXIF** och **Aktivitetslogg**. Originalen lämnas orörda; batchjobb sparar kopior i en separat målmapp. Programmet stöder bildbearbetning, metadata-/datumhantering och videokonvertering via FFmpeg.

## Installera och starta

Python 3.10 eller senare rekommenderas. Starta helst via projektets launcher så att venv, paketcache och loggar hamnar i appens datamapp.

- **Windows:** dubbelklicka `Starta_Fotoverktyg.vbs`. `Starta_Fotoverktyg.ps1` frågar innan paket installeras och kan installera/uppdatera senaste stabila Python via winget.
- **macOS/Linux:** kör `./start_mediaforge.sh` från Terminal. Den skapar en app-lokal virtuell miljö och ber om godkännande innan saknade paket installeras. Python-runtime uppdateras via Homebrew på macOS eller upptäckt systempakethanterare på Linux; Linux-distributionens förråd kan släpa efter senaste upstream-versionen.
- Appen har knappar för att kontrollera/installera tillägg, uppdatera alla paket (inklusive PyQt6 efter omstart), installera/uppdatera Python och kontrollera GitHub-uppdatering.

Installera även **ExifTool** separat för bred metadatahantering, **FFmpeg** för videokonvertering och `xorriso`, `genisoimage` eller `mkisofs` för att skapa ISO till musik-data-DVD. På Linux kan Qt även kräva systembibliotek för grafiskt gränssnitt.

## Appens data och uppdateringar

Allt som MediaForge skapar eller använder lokalt sparas i `MediaForge_Data/` bredvid appen: inställningar och Ko-fi-länk i `Settings/`, detaljerade app- och launcherloggar i `Logs/`, en roterande `Logs/errors.log` som samlar varningar och fel från appen och startarna, den privata Python-miljön i `PythonEnv/`, paketcache i `PipCache/`, temporära paketfiler i `Temp/` och standardutdata i `Output/`. Målmappar för utdata måste ligga under appmappen; externa källmappar kan väljas och läsas. Se till att appmappen är skrivbar. OS-autostartregistreringen sparas som vanligt på operativsystemets plats.

**Sök tyst efter nya versioner (2 ggr/dygn)** är aktiverat som standard och kontrollerar högst var tolfte timme medan appen är öppen. Uppdateraren jämför GitHub-commits och ändrade filer på `main`, inte versionsnumret eller GitHub Release-filer; en ny commit erbjuds även om versionsnumret är samma. Ändrade filer visas och du får bekräfta före snabbspolning. Efter godkännande startas appen om tyst. Ingen dialog visas när ingen ny commit finns. Funktionen kör inte när appen är stängd och fungerar inte i kopior utan Git.

## Användning

**Bildspel → MP4:** välj **Välj bilder…** för att lägga till foton och dra sedan raderna till önskad ordning. Ställ in visningstid och övergång (ingen, tona, svep eller skjut), välj Full HD/HD/kvadrat och lägg eventuellt till en musikfil. Välj en MP4-utdatafil under appmappen och klicka **Skapa bildspel**. Musik loopas om den är kortare än videon. Bilderna skalas så att hela bilden ryms; svarta kanter fyller ut bildformat som inte matchar videon. FFmpeg krävs; HEIC/HEIF/AVIF kräver även `pillow-heif`. Originalbilder och musikfil lämnas orörda.

**Bildbibliotek:** välj **Öppna bildmapp…** och bläddra bland miniatyrerna i mappen. Välj en bild för stor förhandsvisning, använd **Föregående/Nästa** eller öppna **Helskärm** (piltangenter, Esc för att stänga), och klicka **Skriv ut…** för att välja skrivare och utskriftsinställningar. Markera **Inkludera undermappar** vid behov. Mappen läses på plats; MediaForge kopierar eller ändrar inte bilderna. HEIC/HEIF/AVIF-förhandsvisning kräver `pillow-heif`. Startas MediaForge med en bildfil som argument öppnas dess mapp och fotot markeras. Välj MediaForge manuellt som standardapp för bildformat i operativsystemets inställningar; programmet ändrar inte filassociationer automatiskt.

1. Välj källmapp och arkivmapp. Dra och släpp en mapp på fältet om du vill.
2. På **Bildförbättring**: välj förstoring, skärpa, färgstyrka och klarhet. Avmarkera bildförbättring för att enbart arbeta med datum/metadata.
3. På **Fotoredigerare**: öppna ett enskilt foto, rotera med knapparna, dra en markering på förhandsvisningen och klicka **Klipp markering**. **Ångra** backar ett steg i taget. **Spara kopia** använder bildförbättringsreglagen och sparar PNG/JPEG/WEBP utan att ändra originalet.
4. På **AVIF/HEIC → JPEG**: lägg till AVIF-, HEIC- eller HEIF-filer, välj målmapp och JPEG-kvalitet (95 rekommenderas), och starta konvertering. Transparens ersätts av vitt; källfiler skrivs aldrig över. EXIF/färgprofil kan bevaras om du väljer det.
5. På **Annonsbilder → JPEG**: klistra in en eller flera offentliga Blocket-länkar av typen `https://www.blocket.se/recommerce/forsale/item/27022380` **eller** `https://www.blocket.se/mobility/item/24141675`, en per rad. Standardmappen ligger under `MediaForge_Data/Output/`; för varje annons skapas en undermapp med annonsens titel, till exempel `MediaForge_Data/Output/Downloads/Blocket/Chevrolet Suburban/`. Klicka **Välj mapp…** om du vill välja en annan basmapp och därefter **Hämta alla galleribilder som JPEG**. Även i en vald basmapp får varje annons en titel-undermapp. Filnamn som inte är tillåtna i Windows rensas automatiskt. Appen letar efter alla unika bild-ID:n i annonsens galleri, även bilder som bara syns som miniatyrer, och försöker med 1600w, sedan 1280w/960w/default om högsta storleken saknas. Loggen visar hur många som hittades och hur många som sparades. Den skriver aldrig över tidigare filer.
6. På **Datum & EXIF**: välj fast datum eller offset. Välj om datum i metadata och filsystem ska ändras. Kryssa i **Radera ALL befintlig EXIF/metadata** om du vill rensa metadata helt; om datumuppdatering är markerad skrivs nya datumtaggar efter rensningen.
7. Klicka **Bearbeta kopior** för mappbearbetning. Kontrollera loggen efteråt; `DELVIS` betyder att kopian skapades men en metadata- eller tidsåtgärd misslyckades.
8. På **Bildoptimering**: välj en mapp, mål och om EXIF/metadata ska rensas. JPG kopieras utan omkodning (så bildens komprimerade innehåll och kvalitet bevaras); PNG/TIFF optimeras förlustfritt och WEBP kodas med förlustfri komprimering. Storleken kan därför variera beroende på originalet.
9. På **Videokonvertering**: välj mapp, upplösning och CRF. Fliken konverterar batchvis till MP4/H.264/AAC med FFmpeg. Detta är en omkodning och kan ge viss kvalitetsförlust; källfilerna skrivs aldrig över.
10. På **Skapa musik-DVD**: välj musikmapp och utmatningsmapp. Appen samlar ljudfiler (upp till ca 4,5 GB) i `MUSIK_DVD` och skapar även en ISO om `xorriso`, `genisoimage` eller `mkisofs` finns installerat. Bränn ISO-filen som skivavbildning. Detta är en **data-DVD med musikfiler**, inte en DVD-Video; kompatibiliteten med fristående DVD-spelare beror på spelaren.
11. På **Dubblettfinnare**: välj mapp och skanna. Identiska filer jämförs med SHA-256; bilder jämförs perceptuellt. Granska grupperna och klicka **Jämför vald grupp…** (eller dubbelklicka på en rad) för att se bilderna sida vid sida. Välj **Behåll bara denna**, **Behåll alla i gruppen** eller kryssa i de bilder som ska sparas. Omarkerade kopior flyttas efter bekräftelse till `MediaForge_Data/Output/Duplicates/Quarantine/`; inget raderas permanent.
12. På **Ljud från video**: välj videomapp och mål. Extrahera första ljudspåret som MP3/WAV/FLAC eller välj **Ta bort ljudspår** för en ny ljudlös videokopia. FFmpeg krävs. Originalvideorna lämnas orörda; ljudborttagning kopierar videon utan omkodning.
13. På **Färgprofiler**: välj antagen profil för omärkta bilder och målprofil (sRGB, Display P3 eller Adobe RGB). Inbäddade profiler används automatiskt; kopior sparas i valt mål.
14. På **Videostabilisering**: välj mapp och stabiliseringsstyrka. FFmpeg skapar H.264-kopior med deshake; omkodning tar tid och kan påverka kvaliteten.
15. På **Ljudförbättring**: normalisera ljudstyrkan eller minska bakgrundsbrus. Funktionen stöder ljud- och videofiler och lämnar originalen orörda.
16. På **Codec-rapport**: skanna en mapp med ffprobe för container, codec, upplösning, bildfrekvens, bitrate och ljudinformation. Rapporten kan exporteras som CSV under appmappen.
17. Knappen **Stöd utvecklingen · Ko-fi** frågar efter din personliga Ko-fi-länk första gången. Länken kontrolleras mot ko-fi.com och sparas lokalt i appens inställningsmapp; knappen öppnar sedan länken i webbläsaren.

**Viktigt:** Full metadatarensning kan även ta bort GPS, kamerainställningar, färgprofiler och annan information. Testa på kopior först. Om **Behåll befintlig EXIF** markeras vid bildexport kan gamla metadata följa med, om inte full rensning utförs efteråt. På Linux går filens skapandetid normalt inte att ändra; ändrings- och åtkomsttid uppdateras. Förlustfri förstoring ger fler pixlar men skapar inte verkliga detaljer som saknas i originalbilden. Arkivfiler skrivs inte över om du inte uttryckligen markerar det.

**Annonsbilder:** Jag har verifierat att exemplet med annons-ID 27022380 publicerar tre galleribilder och att en bild-URL svarar vid testtillfället. Blocket kan ändra sidans HTML eller begränsa hämtning, så det finns ingen garanti för varje annons eller över tid. Hämta bara bilder du har rätt att använda; appen kringgår inte inloggning eller spärrar. JPEG-kopior blir inte skarpare än annonsens källbilder.

## Design, ikon och autostart

Gränssnittet har mörkt/ljust tema, tydliga flikar och den nya MediaForge-symbolen i apphuvudet, fönstret/aktivitetsfältet, flikarna och knapparna. `fotoverktyg_icon.png` används i appen och Linux-autostart; den matchande flerupplösta `fotoverktyg_icon.ico` används i Windows-autostartgenvägen och kan även användas för andra genvägar/paketering. Behåll båda ikonfilerna bredvid appen. **Starta automatiskt vid inloggning** är frivilligt och avstängt om det inte aktiverats tidigare. Det registreras för ditt användarkonto i Windows Start-mapp, macOS `~/Library/LaunchAgents` eller Linux `~/.config/autostart`. Windows-autostart använder MediaForge-startaren och en genväg med appens ikon, aldrig `.pyw` direkt. Avmarkera kryssrutan för att ta bort autostart. Flyttar du appfilen senare behöver du slå av/på autostart igen. Autostart startar bara fönstret, **inte** filbearbetning eller nedladdning.

På Linux behövs även Qt:s systembibliotek, exempelvis `libxkbcommon.so.0`, för att starta PyQt6; dessa kan inte installeras genom appens paketknapp.

På Windows används helst `Starta_Fotoverktyg.vbs`, som hjälper till med Python och nödvändiga paket. På macOS/Linux används `./start_mediaforge.sh`; den skapar en separat virtuell Python-miljö och frågar innan paket installeras. På macOS/Linux startar du shell-filen från Terminal. `README.md` innehåller den fullständiga engelska och svenska guiden.

## Ikon

Den gemensamma MediaForge-symbolen är en turkos bländare/filmram med en varm play-markör. PNG-versionen används i apphuvudet, fönsterikonen, flikar, knappar och Linux-autostart; ICO-versionen innehåller flera storlekar för Windows-genvägar eller framtida EXE-paketering. Håll båda filerna i samma mapp som `fotoverktyg.pyw`. Om du redan hade Linux-autostart, avmarkera och markera alternativet igen för att uppdatera skrivbordsfilens ikon.

## Starta även om Python saknas (Windows)

Dubbelklicka **`Starta_Fotoverktyg.vbs`** i stället för `.pyw`. Behåll `.vbs`, `.ps1`, `.pyw` och ikonfilen i samma mapp. Startaren körs utan konsolfönster. Om Python 3.10+ saknas får du en fråga innan installation; via winget installeras senaste stabila Python för ditt användarkonto och därefter en app-lokal virtuell miljö med nödvändiga paket. Om winget saknas öppnas python.org och du behöver installera Python manuellt och starta om startaren.

**Begränsning:** En ensam `.pyw`-fil kan inte visa en installationsfråga när Python saknas, eftersom den då inte kan köras. Därför behövs de två separata Windows-startfilerna. VBS-startaren begär inte administratörsrättigheter; `winget`-installationen kräver användarens godkännande. På macOS/Linux behövs en separat installationsmetod via systemets pakethanterare.

## Loggning

Fliken **Aktivitetslogg** samlar händelser från alla delar av appen: användarklick, bildredigering, batchkörningar, annonsnedladdning, konvertering, installation/uppdatering, autostart, fel och avbrott. Varje filresultat loggas även i relevant arbetsflik. Logg sparas automatiskt i `MediaForge_Data/Logs/mediaforge.log`; upp till tre roterade äldre loggar behålls, med max 5 MB per fil. Varningar och fel från appen speglas i den roterande `MediaForge_Data/Logs/errors.log`-filen (max 2 MB och tre säkerhetskopior). Startarna skriver också sina uppstartsproblem dit; Windows-startaren skriver dessutom till `MediaForge_Data/Logs/launcher.log`. Fliken visar sökvägen och knappen **Öppna fellogg** öppnar felloggen. Knappen **Exportera hela loggen…** sparar aktuell huvudlogg. Loggarna kan innehålla lokala filvägar och annons-ID: dela dem bara med personer du litar på. Om appen inte kan skriva i sin program-/appmapp kan loggning till fil utebli.

**Mobility:** Länkar av typen `/mobility/item/ID` stöds nu. Jag verifierade att exempelannonsen `24141675` har 12 unika galleribilder i sidans HTML och att den första högupplösta bildlänken svarade.

**Direkta bildlänkar:** Fliken Bildlänkar → JPEG accepterar även direkta HTTPS-länkar till JPG/PNG/WEBP/AVIF/HEIC. Dessa sparas i `MediaForge_Data/Output/Downloads/WebImages/` som JPEG; dubbla filnamn får nummer. WEBP-exemplet från wermlandopera.com svarade vid testet med en bild på 2000 × 670 pixlar. AVIF/HEIC kräver `pillow-heif`. En direktlänk är ingen annons och får därför ingen annonstitelmapp.

## Separata nedladdningsflikar

**Blocket → JPEG** accepterar endast annonslänkar och skapar en mapp med annonsens titel. **Webbbilder → JPEG** accepterar endast direkta HTTPS-länkar till bildfiler och sparar dem i `MediaForge_Data/Output/Downloads/WebImages/` som standard. Flikarna har varsin länklista, målmapp, start/avbryt, status och logg. Tidigare hänvisningar till en gemensam flik ”Bildlänkar → JPEG” avser nu dessa två separata flikar.

## Efter hämtning

När Blocket- eller Webbbilder-hämtningen slutförts utan fel och minst en bild sparats rensas länkfältet automatiskt. Vid fel eller avbrott behålls länkarna så att du kan försöka igen. Om bilder sparats öppnas output-mappen automatiskt i filhanteraren: annonstitelns mapp för en annons, basmappen för flera annonser, eller `Direkta bilder` för webblänkar. Om filhanteraren inte kan öppnas finns sökvägen kvar i loggen.
