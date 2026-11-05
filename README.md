# MediaForge — Photo & Video Toolkit

A desktop toolkit for photo and video workflows. MediaForge can enhance and optimize image folders, remove EXIF metadata, edit and convert photos, batch-convert videos, manage file dates, download supported web images, and prepare a music data-DVD.

Copyright © 2026 Rickard Längkvist.

## Language and workspace modes

- Choose **English** or **Svenska** from the language selector in the app. The choice is saved for the next launch.
- Choose **All**, **Photo**, or **Video** in the workspace selector. **Photo** shows the photo-related tabs; **Video** shows video and music-DVD tabs. Shared date/metadata and activity-log tabs remain available in either mode.
- Language, workspace, theme, recent folders, and common processing settings are saved locally.
- Tabs are hidden by default. In the **Tabs** menu, check a tab to show it and uncheck it to hide it; **Show all tabs** and **Hide all tabs** are also available. Reorder visible tabs by dragging them. Tabs outside the selected Photo/Video mode are disabled in this menu. The **View** menu controls text size and theme. Window size, tab visibility/order, and text size are remembered between launches.
- **Tools** keeps Python/package management, autostart, quiet update checks, and Ko-fi out of the main workspace. **Help → Check for updates…** checks the latest GitHub Release tag; **Help → Help & support** provides quick setup guidance, a privacy-safe diagnostics summary, the error-log shortcut, and a link to the project issue tracker. Diagnostics are never uploaded automatically; see [SUPPORT.md](SUPPORT.md) for reporting guidance.
- The MediaForge icon is used in the app header, window/taskbar, tabs, buttons, Linux autostart, and the Windows autostart shortcut. Keep `fotoverktyg_icon.png` and its matching multi-size `fotoverktyg_icon.ico` beside the app; the ICO can also be used for other Windows shortcuts or EXE packaging.

## Autostart

Choose **Tools → Start automatically at sign-in** to turn autostart on or off for the current user. MediaForge uses a Windows Startup-folder shortcut with the MediaForge ICO, a macOS LaunchAgent, or the Linux XDG autostart entry with the PNG icon. It launches through the platform launcher rather than registering the `.pyw` file directly, avoiding Python's file-association icon. Autostart opens the app window only; it does not start a conversion or download job.

## Install and run

Python 3.10 or later is recommended.

### Windows

Keep `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw`, and the icon files together. Start the app with `Starta_Fotoverktyg.vbs`. The launcher checks for Python 3.10+ and the required packages before startup. It checks for an existing compatible Python first, updates it through winget when that installation is winget-managed, and installs Python only when no compatible runtime is found. It checks and updates PyQt6, Pillow, pillow-heif and piexif in the current user's shared Python packages (`pip --user`) at most once per week, on the first launcher start on or after Monday at 08:00 local time. If the app is not started then, the check runs on its next start; no background task runs while the app is closed. These shared packages may also affect other programs using that Python. An existing unmanaged Python is left in place rather than duplicated; the launcher explains when it cannot update that installation automatically. The **Update all Python packages (restart)** action runs the same package refresh on demand.

### macOS / Linux

Use the included launcher. It uses the detected compatible Python installation directly and starts MediaForge after checking and updating the shared user-level packages:

```bash
chmod +x start_mediaforge.sh   # one time, if needed
./start_mediaforge.sh
```

The launcher uses Python 3.10+ directly, without an app-specific virtual environment. It stores only the pip cache, temporary files and settings under `MediaForge_Data/`; app and launcher logs are in the app-folder `Logs/` subfolder. It runs `pip install --user --upgrade` for PyQt6, Pillow, pillow-heif and piexif at most once per week, on the first launcher start on or after Monday at 08:00 local time. If MediaForge is not started then, the check runs on its next start; this is not a background scheduler. These user-level packages are shared with other programs using the same Python account and can affect them. The scheduled package update needs internet access when it runs. If a refresh fails but all required packages are already available, MediaForge still launches and records the unresolved warning in the persistent `Logs/errors.log`; missing packages prevent startup. **Update Python runtime** first checks for a compatible existing Python. If found, it updates that runtime through Homebrew or the detected system package manager on Linux; if none is found, it installs Python. An existing runtime not managed by the available package manager is left untouched rather than duplicated. Linux repositories can lag upstream Python releases, and these managers may request administrator approval. **Update all Python packages (restart)** runs the shared-package refresh on demand. Existing `MediaForge_Data/PythonEnv/` contents from earlier versions are left untouched and no longer used. PyQt6 may also require native desktop/Qt libraries.

### Optional system tools

- **ExifTool**: recommended for broad metadata handling, including video, HEIC, RAW, PNG, and WEBP.
- **FFmpeg** (including `ffprobe`): required for slideshow export, video conversion, stabilization, audio processing, and codec reports.
- **xorriso**, **genisoimage**, or **mkisofs**: enables creating an ISO image for the music data-DVD.

These are system programs, not Python packages, and are not installed by MediaForge.

## App-local storage and updates

MediaForge stores settings in `MediaForge_Data/Settings/`, pip downloads in `MediaForge_Data/PipCache/`, temporary package files in `MediaForge_Data/Temp/`, and default exports in `MediaForge_Data/Output/`. Python packages are installed in the current user's shared Python site, not in an app-specific environment; other programs using that Python may be affected. Any existing `MediaForge_Data/PythonEnv/` from an earlier version is retained but unused. App and launcher logs have their own subfolder, `Logs/`, directly inside the app folder. Previous-day `mediaforge.log` and `launcher.log` files are archived in `Logs/Archive/`. Warnings and errors are kept in the append-only `Logs/errors.log` until they are resolved; it is never rotated or deleted automatically. The Ko-fi destination is maintainer-configured and cannot be changed in the app. All chosen output destinations must remain inside the application folder; external source folders can still be selected and read. Keep the app folder writable. OS autostart registration remains in the normal per-user OS location.

The in-app updater checks the latest published GitHub Release and fetches its Git tag (currently **0.0.2**), not commits from `main` or release binary assets. Choose **Help → Check for updates…** or use the system-tray menu. It compares commit IDs and changed files and asks before applying. A clean Git checkout is fast-forwarded when possible; if its branch has diverged from the release, the updater switches the working copy to the release tag in detached-HEAD mode while preserving the original branch and commits. If the checkout already contains the release commit, it will not downgrade it. Source-archive copies without `.git` can also update from the same release; only app files are replaced, existing files are backed up, and app data is kept. The enabled-by-default **Silently check for updates twice a day** option checks at most every 12 hours while MediaForge is open and stays quiet when no release is available. Checks do not run while the app is closed.

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

- **Slideshow → MP4** — select and reorder images, set the display duration, choose no transition/fade/wipe/slide, optionally add music, and export H.264/AAC video. Images are not cropped; black bars pad mismatched aspect ratios. Requires FFmpeg; HEIC/HEIF/AVIF also require `pillow-heif`.
- **Video conversion** — convert a folder of videos to MP4/H.264/AAC with optional 1080p/720p size limits and a quality setting. Re-encoding may reduce quality; originals are preserved. Requires FFmpeg.
- **Audio from video** — batch-extract the first audio track to MP3, WAV, or FLAC, or create a silent video copy by removing audio streams. The silent-copy operation stream-copies video without re-encoding. Originals remain untouched; requires FFmpeg.
- **Video stabilization** — stabilize clips with FFmpeg deshake and export H.264 copies; re-encoding can affect quality.
- **Audio enhancement** — normalize loudness or reduce steady background noise in audio/video folders. Audio is re-encoded while video streams are copied; requires FFmpeg.
- **Codec report** — inspect container, duration, video/audio codecs, resolution, frame rate, bitrates, sample rate, and channels; export a CSV. Requires ffprobe.
- **Create music DVD** — collect supported audio files into a DVD-5-sized data-disc folder and, when an ISO authoring tool is installed, create an ISO that can be burned as a disc image. This is a **data DVD**, not DVD-Video; compatibility with standalone DVD players varies.
- **Date & EXIF** — adjust dates and remove metadata. Choose archive copies, new `_rensad` copies beside the source files, or explicitly overwrite originals after a confirmation; same-folder modes require full metadata removal and leave originals untouched if a file fails.
- **Activity log** — review actions, job results, and errors.

## Safety and limitations

MediaForge keeps source files unchanged for its copy/export workflows. Duplicate cleanup moves unchecked files to a reversible app-local quarantine instead of permanently deleting them. Full metadata removal can delete GPS, camera settings, color profiles, and other information. Always test with copies. Lossless optimization does not guarantee a smaller file. Video conversion is lossy re-encoding. The music-DVD feature creates a data disc, not a DVD-Video authoring project.

---

# MediaForge — verktyg för foto och video

MediaForge är ett skrivbordsprogram för foto- och videoflöden. Programmet kan förbättra och optimera bildmappar, rensa EXIF, redigera och konvertera foton, batchkonvertera video, hantera fildatum, hämta vissa webbbilder och förbereda en musik-data-DVD.

Copyright © 2026 Rickard Längkvist.

## Språk och arbetslägen

- Välj **English** eller **Svenska** i språklistan i appen. Valet sparas till nästa start.
- Välj **Alla**, **Foto** eller **Video** i arbetsläget. **Foto** visar fotorelaterade flikar; **Video** visar video- och musik-DVD-flikar. Gemensamma flikar för datum/metadata och aktivitetslogg visas i båda lägena.
- Språk, arbetsläge, tema, senaste mappar och vanliga bearbetningsinställningar sparas lokalt.
- Flikar är dolda som standard. I menyn **Flikar** kryssar du i en flik för att visa den och avmarkerar för att dölja den; **Visa alla flikar** och **Dölj alla flikar** finns också. Dra synliga flikar för att ändra ordningen. Flikar utanför valt foto-/videoarbetsläge är inaktiverade i menyn. Menyn **Visa** styr textstorlek och tema. Fönsterstorlek, flikval och textstorlek sparas mellan starter.
- **Verktyg** samlar Python-/pakethantering, autostart, tyst uppdateringssökning och Ko-fi utanför arbetsytan. **Hjälp → Sök efter uppdatering…** kontrollerar senaste GitHub-releasen. **Hjälp → Hjälp och support** innehåller snabbhjälp, integritetssäker diagnostik, genväg till felloggen och länk till projektets ärendehantering. Diagnostik laddas aldrig upp automatiskt; se [SUPPORT.md](SUPPORT.md) för rapporteringsråd.
- MediaForge-ikonen används i apphuvudet, fönstret/aktivitetsfältet, flikarna, knapparna, Linux-autostart och Windows-autostartgenvägen. Behåll `fotoverktyg_icon.png` och matchande flerupplöst ICO bredvid appen; ICO-filen kan även användas för andra Windows-genvägar och EXE-paketering.

## Autostart

Välj **Verktyg → Starta automatiskt vid inloggning** för att slå på eller av autostart för ditt användarkonto. MediaForge använder en genväg i Windows Start-mappen med MediaForge-ICO, en LaunchAgent på macOS eller Linux XDG-autostart med PNG-ikonen. Appen startas via plattformsstartaren, inte genom direktregistrering av `.pyw`, så Python-filassociationens ikon används inte. Autostart öppnar bara appfönstret – den startar inte konvertering eller nedladdning.

## Installera och starta

Python 3.10 eller senare rekommenderas.

### Windows

Ha `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw` och ikonfilerna i samma mapp. Starta appen med `Starta_Fotoverktyg.vbs`. Startaren söker först efter en kompatibel Python och uppdaterar den via winget om den hanteras där. Python installeras bara om ingen kompatibel runtime hittas; en befintlig installation som inte hanteras av winget lämnas orörd i stället för att skapa en sidoinstallation. PyQt6, Pillow, pillow-heif och piexif kontrolleras och uppdateras i användarkontots gemensamma Python-paket (`pip --user`) högst en gång per vecka, vid första start från startaren på eller efter måndag kl. 08:00 lokal tid. Om appen inte startas då sker kontrollen vid nästa start; ingen schemalagd bakgrundsprocess körs när appen är stängd. Andra program som använder samma Python kan också påverkas. Knappen **Uppdatera alla Python-paket (starta om)** kör samma uppdatering manuellt.

### macOS / Linux

Använd den medföljande startaren. Den använder den kompatibla Python-installationen direkt och startar MediaForge efter kontroll och uppdatering av de gemensamma användarpaketen:

```bash
chmod +x start_mediaforge.sh   # en gång vid behov
./start_mediaforge.sh
```

Startaren använder Python 3.10+ direkt utan app-specifik virtuell miljö. Paketcache, temporära paketfiler och inställningar sparas i `MediaForge_Data/` bredvid appen. App- och startloggar sparas separat i `Logs/` direkt i appmappen; loggar från föregående dagar arkiveras i `Logs/Archive/`, medan olösta fel ligger kvar i `Logs/errors.log`. Knappen **Uppdatera Python-runtime** söker först efter en kompatibel befintlig Python. Om den hittas uppdateras den via Homebrew eller upptäckt systempakethanterare på Linux; om ingen hittas installeras Python. En befintlig runtime som inte hanteras av pakethanteraren lämnas orörd i stället för att skapa en sidoinstallation. Linux-distributionens förråd kan släpa efter den senaste upstream-versionen; pakethanteraren kan begära administratörsgodkännande. PyQt6, Pillow, pillow-heif och piexif kontrolleras och uppdateras via `pip --user` i användarkontots gemensamma Python-installation högst en gång per vecka, vid första start på eller efter måndag kl. 08:00 lokal tid. Om appen inte startas då sker kontrollen vid nästa start; ingen schemalagd bakgrundsprocess körs när appen är stängd. Andra program som använder samma Python kan påverkas. Den schemalagda paketuppdateringen behöver internetåtkomst när den körs. **Uppdatera alla Python-paket (starta om)** kör samma uppdatering manuellt. En gammal `MediaForge_Data/PythonEnv/` lämnas kvar men används inte. PyQt6 kan dessutom kräva inbyggda Qt-/skrivbordskomponenter.

### Valfria systemverktyg

- **ExifTool**: rekommenderas för bred metadatahantering, bland annat för video, HEIC, RAW, PNG och WEBP.
- **FFmpeg** (inklusive `ffprobe`): krävs för bildspel, videokonvertering, stabilisering, ljudbearbetning och codec-rapporter.
- **xorriso**, **genisoimage** eller **mkisofs**: möjliggör skapande av ISO-avbild för musik-data-DVD.

Detta är systemprogram, inte Python-paket, och MediaForge installerar dem inte.

All lokalt skapad appdata och standardutdata sparas i `MediaForge_Data/` under appmappen. Utdata får inte sparas utanför appmappen; källmappar utanför appen kan fortfarande läsas. Håll appmappen skrivbar. OS-autostart ligger kvar på operativsystemets normala användarplats.

Den inbyggda uppdateraren kontrollerar den senaste publicerade GitHub-releasen och hämtar dess Git-tagg (för närvarande **0.0.2**), inte commits från `main` eller binärfiler från releasen. Välj **Hjälp → Sök efter uppdatering…** eller använd systemfältsmenyn. Uppdateraren jämför commit-ID och ändrade filer och frågar före installation. En ren Git-kopia snabbspolas när det går; om grenen skiljer sig från releasen växlar uppdateraren arbetskopian till releasetaggen i frikopplat läge, medan den ursprungliga grenen och dess commits behålls. Om kopian redan innehåller release-committen görs ingen nedgradering. Källkodsarkiv utan `.git` kan också uppdateras från samma release; endast appfiler ersätts, befintliga filer säkerhetskopieras och appdata lämnas orörd. **Sök tyst efter nya versioner (2 ggr/dygn)** är aktiverat som standard, kontrollerar högst var tolfte timme medan MediaForge är öppet och är tyst när ingen ny release finns. Kontroller körs inte när appen är stängd.

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

- **Bildspel → MP4** — välj och sortera bilder, ställ in visningstid, välj ingen övergång/toning/svep/skjutning, lägg till valfri musik och exportera H.264/AAC-video. Bilder beskärs inte; svarta kanter fyller ut olika bildformat. Kräver FFmpeg.
- **Videokonvertering** — konvertera en mapp med videor till MP4/H.264/AAC, med valfri maxstorlek 1080p/720p och kvalitetsinställning. Omkodning kan försämra kvaliteten; originalen bevaras. Kräver FFmpeg.
- **Ljud från video** — extrahera första ljudspåret till MP3, WAV eller FLAC, eller skapa en ljudlös videokopia genom att ta bort ljudspåren. Ljudborttagning kopierar videoströmmen utan omkodning. Originalen ändras inte; kräver FFmpeg.
- **Videostabilisering** — stabilisera klipp med FFmpeg deshake och exportera H.264-kopior; omkodning kan påverka kvaliteten.
- **Ljudförbättring** — normalisera ljudstyrka eller minska konstant bakgrundsbrus i ljud-/videomappar. Ljudet kodas om medan videoströmmen kopieras; kräver FFmpeg.
- **Codec-rapport** — granska container, längd, ljud-/videocodec, upplösning, bildfrekvens, bitrate, samplingsfrekvens och kanaler; exportera CSV. Kräver ffprobe.
- **Skapa musik-DVD** — samla ljudfiler i en mapp som ryms på en DVD-5 och skapa, om ett ISO-verktyg finns installerat, en ISO som kan brännas som skivavbild. Detta är en **data-DVD**, inte DVD-Video; kompatibilitet med fristående DVD-spelare varierar.
- **Datum & EXIF** — ändra datum och rensa metadata. Välj arkivkopior, nya `_rensad`-kopior bredvid källfilerna eller bekräfta att originalen ska skrivas över; källmappslägena kräver full metadatarensning och lämnar originalet orört om en fil misslyckas.
- **Aktivitetslogg** — granska åtgärder, jobbresultat och fel.

## Säkerhet och begränsningar

MediaForge lämnar källfiler orörda i kopierings- och exportflöden. Dubblettrensning flyttar omarkerade filer till en lokal karantän i stället för att radera dem permanent. Full metadatarensning kan ta bort GPS, kamerainställningar, färgprofiler och annan information. Testa alltid med kopior. Förlustfri optimering garanterar inte mindre filer. Videokonvertering är en omkodning med kvalitetsförlust. Musik-DVD-funktionen skapar en data-DVD, inte en DVD-Video.
