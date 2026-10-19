# MediaForge — Photo & Video Toolkit

A desktop toolkit for photo and video workflows. MediaForge can enhance and optimize image folders, remove EXIF metadata, edit and convert photos, batch-convert videos, manage file dates, download supported web images, and prepare a music data-DVD.

## Language and workspace modes

- Choose **English** or **Svenska** from the language selector in the app. The choice is saved for the next launch.
- Choose **All**, **Photo**, or **Video** in the workspace selector. **Photo** shows the photo-related tabs; **Video** shows video and music-DVD tabs. Shared date/metadata and activity-log tabs remain available in either mode.
- Language, workspace, theme, recent folders, and common processing settings are saved locally.
- The MediaForge logo is shown in the app header, window/taskbar, tabs, buttons, and Linux autostart. Keep `fotoverktyg_icon.png` and its matching multi-size `fotoverktyg_icon.ico` beside the app; the ICO can also be used for Windows shortcuts or EXE packaging.

## Autostart

Use **Start automatically at sign-in** in the app to turn autostart on or off for the current user. MediaForge uses the Windows per-user Run key, a macOS LaunchAgent, or the Linux XDG autostart directory. Autostart opens the app window only; it does not start a conversion or download job.

## Install and run

Python 3.10 or later is recommended.

### Windows

Keep `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw`, and the icon files together. Start the app with `Starta_Fotoverktyg.vbs`. The launcher checks for Python 3.10+ and the required packages before startup. It asks before installing packages, keeps the virtual environment and pip cache inside the app folder, and can install/update the latest stable Python available through winget for the current user. In the app, **Update all Python packages (restart)** safely updates PyQt6 and the other requirements after closing the running app.

### macOS / Linux

Use the included launcher. It creates a private virtual environment, asks before installing missing Python packages, and then starts MediaForge:

```bash
chmod +x start_mediaforge.sh   # one time, if needed
./start_mediaforge.sh
```

The launcher uses Python 3.10+ and stores the virtual environment, pip cache, temporary package files, settings and logs inside `MediaForge_Data/` next to the app. **Install/update latest Python** uses Homebrew on macOS or the detected system package manager on Linux; Linux repositories can lag upstream Python releases, and these managers may request administrator approval. **Update all Python packages (restart)** refreshes the private app environment, including PyQt6. PyQt6 may also require native desktop/Qt libraries.

### Optional system tools

- **ExifTool**: recommended for broad metadata handling, including video, HEIC, RAW, PNG, and WEBP.
- **FFmpeg** (including `ffprobe`): required for video conversion, stabilization, audio processing, and codec reports.
- **xorriso**, **genisoimage**, or **mkisofs**: enables creating an ISO image for the music data-DVD.

These are system programs, not Python packages, and are not installed by MediaForge.

## App-local storage and updates

MediaForge creates a `MediaForge_Data/` folder alongside the app. Settings and the Ko-fi link are in `Settings/`, app and launcher logs in `Logs/`, the private Python virtual environment in `PythonEnv/`, pip downloads in `PipCache/`, temporary package files in `Temp/`, and default exports in `Output/`. All chosen output destinations must remain inside the application folder; external source folders can still be selected and read. Keep the app folder writable and do not delete `MediaForge_Data/` if you want to retain settings or exports. OS autostart registration remains in the normal per-user OS location.

For a source-code checkout on branch `main`, **Check for GitHub main updates** fetches the configured GitHub repository. It refuses to update a dirty worktree or a checkout that is not the expected `main` branch/repository, shows the available revision, and requires confirmation. Updates are fast-forward-only; commit, stash, or back up work before checking. Restart the app after an update. Packaged/non-Git copies cannot self-update through Git.

## Photo tools

- **Photo library / browser** — open a folder in place, browse thumbnails, move between photos, view them full-screen, and print the selected image. Optional subfolder scanning is available. The folder is indexed for browsing only; source images are not copied or altered. HEIC/HEIF/AVIF previews require `pillow-heif`. Launching MediaForge with an image-file path opens its folder and selects that image; set it as the OS default viewer manually in system settings if desired.
- **Photo enhancement** — adjust scale, sharpness, color, and contrast; save copies without changing originals.
- **Image optimization** — import a folder, include subfolders, create optimized copies, and optionally remove EXIF/metadata. JPEG image data is copied without re-encoding; PNG/TIFF optimization and WEBP lossless encoding preserve image quality. File-size reductions depend on the source.
- **Photo editor** — rotate, crop, undo, and save a copy.
- **Color profiles** — convert between sRGB, Display P3, and Adobe RGB (1998); embedded profiles are honored and untagged images can be assigned an assumed source profile. Image metadata may not be retained by Qt when saving converted copies.
- **Duplicate finder** — finds exact duplicates by SHA-256 and visually similar images by perceptual hash. Compare a group side by side, then keep one image, keep all, or mark individual files. Unchecked files are moved—not permanently deleted—to an app-local quarantine folder after confirmation.
- **AVIF/HEIC → JPEG** — add one or more AVIF, HEIC, or HEIF files, select a destination and JPEG quality, and convert. Original files remain untouched. HEIC/AVIF support requires `pillow-heif`.
- **Web images / Blocket → JPEG** — download supported direct image links or public Blocket gallery images. Only download images you have permission to use.

## Video and media tools

- **Video conversion** — convert a folder of videos to MP4/H.264/AAC with optional 1080p/720p size limits and a quality setting. Re-encoding may reduce quality; originals are preserved. Requires FFmpeg.
- **Audio from video** — batch-extract the first audio track to MP3, WAV, or FLAC, or create a silent video copy by removing audio streams. The silent-copy operation stream-copies video without re-encoding. Originals remain untouched; requires FFmpeg.
- **Video stabilization** — stabilize clips with FFmpeg deshake and export H.264 copies; re-encoding can affect quality.
- **Audio enhancement** — normalize loudness or reduce steady background noise in audio/video folders. Audio is re-encoded while video streams are copied; requires FFmpeg.
- **Codec report** — inspect container, duration, video/audio codecs, resolution, frame rate, bitrates, sample rate, and channels; export a CSV. Requires ffprobe.
- **Create music DVD** — collect supported audio files into a DVD-5-sized data-disc folder and, when an ISO authoring tool is installed, create an ISO that can be burned as a disc image. This is a **data DVD**, not DVD-Video; compatibility with standalone DVD players varies.
- **Date & EXIF** — adjust dates and remove metadata on copies where supported.
- **Activity log** — review actions, job results, and errors.

## Safety and limitations

MediaForge keeps source files unchanged for its copy/export workflows. Duplicate cleanup moves unchecked files to a reversible app-local quarantine instead of permanently deleting them. Full metadata removal can delete GPS, camera settings, color profiles, and other information. Always test with copies. Lossless optimization does not guarantee a smaller file. Video conversion is lossy re-encoding. The music-DVD feature creates a data disc, not a DVD-Video authoring project.

---

# MediaForge — verktyg för foto och video

MediaForge är ett skrivbordsprogram för foto- och videoflöden. Programmet kan förbättra och optimera bildmappar, rensa EXIF, redigera och konvertera foton, batchkonvertera video, hantera fildatum, hämta vissa webbbilder och förbereda en musik-data-DVD.

## Språk och arbetslägen

- Välj **English** eller **Svenska** i språklistan i appen. Valet sparas till nästa start.
- Välj **Alla**, **Foto** eller **Video** i arbetsläget. **Foto** visar fotorelaterade flikar; **Video** visar video- och musik-DVD-flikar. Gemensamma flikar för datum/metadata och aktivitetslogg visas i båda lägena.
- Språk, arbetsläge, tema, senaste mappar och vanliga bearbetningsinställningar sparas lokalt.
- MediaForge-logotypen visas i apphuvudet, fönstret/aktivitetsfältet, flikarna, knapparna och Linux-autostart. Behåll `fotoverktyg_icon.png` och matchande ICO i flera storlekar bredvid appen; ICO-filen kan även användas för Windows-genvägar och EXE-paketering.

## Autostart

Kryssa i **Starta automatiskt vid inloggning** i appen för att aktivera autostart för ditt användarkonto, eller avmarkera för att stänga av. MediaForge använder Windows Run-nyckeln för användaren, en LaunchAgent på macOS eller Linux XDG-autostart. Autostart öppnar bara appfönstret – den startar inte konvertering eller nedladdning.

## Installera och starta

Python 3.10 eller senare rekommenderas.

### Windows

Ha `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw` och ikonfilerna i samma mapp. Starta appen med `Starta_Fotoverktyg.vbs`. Startaren kontrollerar Python 3.10+ och nödvändiga paket, frågar innan paket installeras och kan installera/uppdatera senaste stabila Python via winget. Knappen **Uppdatera alla Python-paket (starta om)** uppdaterar även PyQt6 först när appen har stängts.

### macOS / Linux

Använd den medföljande startaren. Den skapar en privat virtuell miljö, frågar innan saknade Python-paket installeras och startar sedan MediaForge:

```bash
chmod +x start_mediaforge.sh   # en gång vid behov
./start_mediaforge.sh
```

Startaren kräver Python 3.10+ och sparar virtuell miljö, paketcache, temporära paketfiler, inställningar och loggar i `MediaForge_Data/` bredvid appen. Knappen **Installera/uppdatera senaste Python** använder Homebrew på macOS eller upptäckt systempakethanterare på Linux. Linux-distributionens förråd kan släpa efter den senaste upstream-versionen; pakethanteraren kan begära administratörsgodkännande. **Uppdatera alla Python-paket (starta om)** uppdaterar även PyQt6. PyQt6 kan dessutom kräva inbyggda Qt-/skrivbordskomponenter.

### Valfria systemverktyg

- **ExifTool**: rekommenderas för bred metadatahantering, bland annat för video, HEIC, RAW, PNG och WEBP.
- **FFmpeg** (inklusive `ffprobe`): krävs för videokonvertering, stabilisering, ljudbearbetning och codec-rapporter.
- **xorriso**, **genisoimage** eller **mkisofs**: möjliggör skapande av ISO-avbild för musik-data-DVD.

Detta är systemprogram, inte Python-paket, och MediaForge installerar dem inte.

All lokalt skapad appdata och standardutdata sparas i `MediaForge_Data/` under appmappen. Utdata får inte sparas utanför appmappen; källmappar utanför appen kan fortfarande läsas. Håll appmappen skrivbar. OS-autostart ligger kvar på operativsystemets normala användarplats.

**Kontrollera GitHub main-uppdatering** fungerar bara i en ren Git-arbetskopia från rätt repository på grenen `main`. Appen hämtar från GitHub, frågar innan snabbspolning och avbryter om det finns ändringar eller grenen avviker. Starta om efter uppdatering.

## Fotofunktioner

- **Bildbibliotek / fotobläddrare** — öppna en mapp utan att kopiera bilderna, bläddra bland miniatyrer, gå mellan foton, visa i helskärm och skriv ut vald bild. Undermappar kan tas med. Bilderna ändras inte; HEIC/HEIF/AVIF-förhandsvisning kräver `pillow-heif`. Startar du MediaForge med en bildsökväg öppnas mappen och bilden markeras; välj själv MediaForge som standardapp i operativsystemets inställningar om du vill.
- **Bildförbättring** — justera förstoring, skärpa, färg och kontrast; spara kopior utan att ändra originalen.
- **Bildoptimering** — importera en mapp, ta med undermappar, skapa optimerade kopior och välj om EXIF/metadata ska rensas. JPEG-bilddata kopieras utan omkodning; PNG/TIFF optimeras och WEBP sparas förlustfritt. Hur mycket filstorleken minskar beror på originalet.
- **Fotoredigerare** — rotera, beskära, ångra och spara en kopia.
- **Färgprofiler** — konvertera mellan sRGB, Display P3 och Adobe RGB (1998). Inbäddade profiler används; för omärkta bilder kan en antagen källprofil väljas. Qt kan utelämna metadata i konverterade kopior.
- **Dubblettfinnare** — hittar identiska filer med SHA-256 och visuellt liknande bilder med perceptuell hash. Jämför bilder i en grupp sida vid sida och välj enkelt att behålla en bild, alla eller markera enskilda. Omarkerade kopior flyttas efter bekräftelse, inte raderas permanent, till appens karantänmapp.
- **AVIF/HEIC → JPEG** — lägg till en eller flera AVIF-, HEIC- eller HEIF-filer, välj målmapp och JPEG-kvalitet och konvertera. Originalfilerna ändras inte. HEIC/AVIF kräver `pillow-heif`.
- **Webbbilder / Blocket → JPEG** — hämta stödda direkta bildlänkar eller offentliga Blocket-galleribilder. Hämta bara bilder du har rätt att använda.

## Video- och mediafunktioner

- **Videokonvertering** — konvertera en mapp med videor till MP4/H.264/AAC, med valfri maxstorlek 1080p/720p och kvalitetsinställning. Omkodning kan försämra kvaliteten; originalen bevaras. Kräver FFmpeg.
- **Ljud från video** — extrahera första ljudspåret till MP3, WAV eller FLAC, eller skapa en ljudlös videokopia genom att ta bort ljudspåren. Ljudborttagning kopierar videoströmmen utan omkodning. Originalen ändras inte; kräver FFmpeg.
- **Videostabilisering** — stabilisera klipp med FFmpeg deshake och exportera H.264-kopior; omkodning kan påverka kvaliteten.
- **Ljudförbättring** — normalisera ljudstyrka eller minska konstant bakgrundsbrus i ljud-/videomappar. Ljudet kodas om medan videoströmmen kopieras; kräver FFmpeg.
- **Codec-rapport** — granska container, längd, ljud-/videocodec, upplösning, bildfrekvens, bitrate, samplingsfrekvens och kanaler; exportera CSV. Kräver ffprobe.
- **Skapa musik-DVD** — samla ljudfiler i en mapp som ryms på en DVD-5 och skapa, om ett ISO-verktyg finns installerat, en ISO som kan brännas som skivavbild. Detta är en **data-DVD**, inte DVD-Video; kompatibilitet med fristående DVD-spelare varierar.
- **Datum & EXIF** — ändra datum och rensa metadata på kopior där formatet stöds.
- **Aktivitetslogg** — granska åtgärder, jobbresultat och fel.

## Säkerhet och begränsningar

MediaForge lämnar källfiler orörda i kopierings- och exportflöden. Dubblettrensning flyttar omarkerade filer till en lokal karantän i stället för att radera dem permanent. Full metadatarensning kan ta bort GPS, kamerainställningar, färgprofiler och annan information. Testa alltid med kopior. Förlustfri optimering garanterar inte mindre filer. Videokonvertering är en omkodning med kvalitetsförlust. Musik-DVD-funktionen skapar en data-DVD, inte en DVD-Video.
