# MediaForge — Photo & Video Toolkit

A desktop toolkit for photo and video workflows. MediaForge can enhance and optimize image folders, remove EXIF metadata, edit and convert photos, batch-convert videos, manage file dates, download supported web images, and prepare a music data-DVD.

Copyright © 2026 Rickard Längkvist.

## Language and workspace modes

- Choose **English** or **Svenska** from the language selector in the app. The choice is saved for the next launch.
- Choose **All**, **Photo**, or **Video** in the workspace selector. **Photo** shows the photo-related tabs; **Video** shows video and music-DVD tabs. Shared date/metadata and activity-log tabs remain available in either mode.
- Language, workspace, theme, recent folders, and common processing settings are saved locally.
- The app opens in **View → Simple mode** with common tools visible; turn Simple mode off to reveal the full toolset. In the **Tabs** menu, check a tab to show it and uncheck it to hide it; **Show all tabs** and **Hide all tabs** are also available. Reorder visible tabs by dragging them. Tabs outside the selected Photo/Video mode are disabled in this menu. The **View** menu controls text size and theme. Window size, simple/advanced mode, tab visibility/order, and text size are remembered between launches.
- **Tools** keeps Python/package management, autostart, quiet update checks, and Ko-fi out of the main workspace. **Help → Check for updates…** checks the latest GitHub Release tag; **Help → Help & support** provides searchable quick guidance, an interactive step-by-step tutorial, a privacy-safe diagnostics summary, the error-log shortcut, and a link to the project issue tracker. Diagnostics are never uploaded automatically; see [SUPPORT.md](SUPPORT.md) for reporting guidance.
- The refreshed MediaForge icon is used in the app header, window/taskbar, tabs, buttons, Linux autostart, and Windows autostart shortcut. `fotoverktyg_icon.svg` is the scalable icon master and `mediaforge_logo.svg` is the horizontal vector wordmark. Keep both SVGs, `fotoverktyg_icon.png`, and the matching multi-size `fotoverktyg_icon.ico` beside the app; the PNG/ICO files are compatibility fallbacks for platforms that do not render SVG icons.

## Autostart

MediaForge starts minimized; restore it from the taskbar (or the system tray where available). **Tools → Close/minimize to system tray** makes the window close button and minimize button hide the app in the tray; use the tray menu to reopen or quit. Launching it again activates the existing window. Choose **Tools → Start automatically at sign-in** to turn per-user autostart on or off on Windows, macOS, or Linux. MediaForge uses a Windows Startup-folder shortcut, a macOS LaunchAgent, or Linux XDG autostart, each launching through the platform launcher rather than registering the `.pyw` file directly. **Tools → Register MediaForge as an image viewer** adds a current-user Open With entry without changing the default app; choose MediaForge manually in OS settings. Windows users can also add the Explorer right-click menu. **Keep the computer awake during jobs** is optional and disabled by default.

## Install and run

Python 3.10 or later (including 3.15) must already be installed as a system Python; MediaForge never installs a separate runtime. The launchers have no upper-version check, and pip resolves the current shared packages for the selected interpreter.

### Windows

Keep `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw`, and the icon files together. Start the app with `Starta_Fotoverktyg.vbs`. The launcher searches for an existing compatible system Python 3.10+ using the Python launcher, Windows Python registry entries, PATH, and common install folders. It never installs Python or creates an app-specific environment; if no compatible system runtime is found, it shows a clear error and exits. Required packages are installed into the current user's shared Python packages (`pip --user`) only if they are missing. Packages are not automatically updated at startup. Use **Update all Python packages (restart)** under Tools to update them manually; these shared packages may also affect other programs using that Python. The optional **Update system Python** action only updates an existing winget-managed runtime; it never installs a new one.

### macOS / Linux

Use the included launcher. It uses the detected compatible Python installation directly and starts MediaForge after checking and updating the shared user-level packages:

```bash
chmod +x start_mediaforge.sh   # one time, if needed
./start_mediaforge.sh
```

The launcher uses an existing system Python 3.10+ directly, without an app-specific virtual environment, and never installs a Python runtime. If none is detected, it reports that requirement and exits. It stores only the pip cache, temporary files and settings under `MediaForge_Data/`; app and launcher logs are in the app-folder `Logs/` subfolder. It installs `PyQt6`, `Pillow`, `pillow-heif` and `piexif` with `pip install --user --upgrade` only when required packages are missing. There is no automatic package update at startup. Use **Update all Python packages (restart)** in Tools to update them manually. These user-level packages are shared with other programs using the same Python account and can affect them. A manual update needs internet access. If package installation fails but all required packages are already available, MediaForge still launches and records the unresolved warning in `Logs/errors.log`; missing packages prevent startup. **Update system Python** only attempts to update an existing runtime managed by Homebrew or the detected system package manager on Linux; it never installs a replacement. An unmanaged runtime is left untouched. Linux repositories can lag upstream Python releases, and package managers may request administrator approval. Existing `MediaForge_Data/PythonEnv/` contents from earlier versions are left untouched and no longer used. PyQt6 may also require native desktop/Qt libraries.

### Optional system tools

- **ExifTool**: recommended for broad metadata handling, including video, HEIC, RAW, PNG, and WEBP.
- **FFmpeg** (including `ffprobe`): required for slideshow export, video conversion, stabilization, audio processing, and codec reports.
- **xorriso**, **genisoimage**, or **mkisofs**: enables creating an ISO image for the music data-DVD.

These are system programs, not Python packages, and are not installed by MediaForge.

## App-local storage and updates

MediaForge stores settings in `MediaForge_Data/Settings/`, pip downloads in `MediaForge_Data/PipCache/`, temporary package files in `MediaForge_Data/Temp/`, and default exports in `MediaForge_Data/Output/`. Python packages are installed in the current user's shared Python site, not in an app-specific environment; other programs using that Python may be affected. Any existing `MediaForge_Data/PythonEnv/` from an earlier version is retained but unused. App and launcher logs have their own subfolder, `Logs/`, directly inside the app folder. Previous-day `mediaforge.log` and `launcher.log` files are archived in `Logs/Archive/`. Warnings and errors are kept in the append-only `Logs/errors.log` until they are resolved; it is never rotated or deleted automatically. The Ko-fi destination is maintainer-configured and cannot be changed in the app. All chosen output destinations must remain inside the application folder; external source folders can still be selected and read. Keep the app folder writable. OS autostart registration remains in the normal per-user OS location.

The in-app updater checks the latest published GitHub Release and fetches its Git tag (currently **0.0.2**), not commits from `main` or release binary assets. Choose **Help → Check for updates…** or use the system-tray menu. It compares commit IDs and changed files and asks before applying. A clean Git checkout is fast-forwarded when possible; if its branch has diverged from the release, the updater switches the working copy to the release tag in detached-HEAD mode while preserving the original branch and commits. If the checkout already contains the release commit, it will not downgrade it. Source-archive copies without `.git` can also update from the same release; only app files are replaced, existing files are backed up, and app data is kept. The enabled-by-default **Silently check for updates twice a day** option checks at most every 12 hours while MediaForge is open and stays quiet when no release is available. Checks do not run while the app is closed.

## Batch estimates and keyboard shortcuts

MediaForge allows one running app instance per user. Launching it again brings the existing window to the front instead of opening another one.

For the main folder-processing job, **Estimate time and disk space** scans the selected files and shows file count, total input size, approximate required space and free space on the destination drive. In overwrite mode the estimate is the largest temporary copy; in copy modes it uses the total source size. Actual output can vary. During processing, a remaining-time estimate appears after the first file and refines from observed throughput. The optional post-processing workflow can sort archived results into **Images** and **Videos** subfolders. Optional source-folder watching asks before it processes only newly added files; it never starts jobs without confirmation. Shortcuts are shown in the **File** and **View → Select tab** menus: **Ctrl/Cmd+O** choose source, **Ctrl/Cmd+Shift+O** choose archive, **Ctrl/Cmd+Enter** start the folder job, **F1** open Help & Support, **Ctrl/Cmd+Q** quit, and **Ctrl/Cmd+1–9** select one of the first nine visible tabs. **Ctrl+Tab** and **Ctrl+Shift+Tab** also switch tabs. Controls now expose accessible names and descriptions for screen readers, with labels associated to their inputs where possible. Processing errors include a context-based next-step suggestion in the activity and per-tool logs.

## Photo tools

- **Photo library / browser** — open a folder in place, browse thumbnails, move between photos, view them full-screen, and print the selected image. Optional subfolder scanning is available. The folder is indexed for browsing only; source images are not copied or altered. SVG previews use QtSvg; HEIC/HEIF/AVIF previews require `pillow-heif`. Register MediaForge as an Open With viewer in **Tools**, then choose it as the OS default manually if desired.
- **Photo enhancement** — choose Web, Social media, or Archive presets, then adjust scale, sharpness, color, and contrast; save copies without changing originals. Changing an individual setting switches the preset selector back to Manual.
- **Image optimization** — import a folder, include subfolders, create optimized copies, and optionally remove EXIF/metadata. JPEG image data is copied without re-encoding; PNG/TIFF optimization and WEBP lossless encoding preserve image quality. File-size reductions depend on the source.
- **Photo editor** — rotate, straighten the horizon, crop, undo, conservatively remove red-eye within a selection, or optionally blur a selected region (for example, a face or plate). Save a copy; the source is never overwritten.
- **Color profiles** — convert between sRGB, Display P3, and Adobe RGB (1998); embedded profiles are honored and untagged images can be assigned an assumed source profile. Image metadata may not be retained by Qt when saving converted copies.
- **Duplicate finder** — finds exact duplicates by SHA-256 and visually similar images by perceptual hash. Scan a selected folder or all available computer drives for images and videos; video matching is exact-file SHA-256. Compare groups and choose which copies to keep. Unchecked files are moved—not permanently deleted—to an app-local quarantine folder after confirmation.
- **AVIF/HEIC → JPEG** — add one or more AVIF, HEIC, or HEIF files, select a destination and JPEG quality, and convert. Original files remain untouched. HEIC/AVIF support requires `pillow-heif`.
- **Web images / Blocket → JPEG** — download supported direct image links or public Blocket gallery images. Only download images you have permission to use.

## Video and media tools

- **Slideshow → MP4** — select and reorder images, set the display duration, choose no transition/fade/wipe/slide, optionally add music, and export H.264/AAC video. Images are not cropped; black bars pad mismatched aspect ratios. Requires FFmpeg; HEIC/HEIF/AVIF also require `pillow-heif`.
- **Video conversion** — convert a folder of videos to MP4/H.264/AAC using Web (720p/smaller file), Social media (1080p), or Archive (source resolution/high quality) presets. Resolution and quality remain adjustable; changing either switches the selector back to Manual. Re-encoding may reduce quality; originals are preserved. Requires FFmpeg.
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
- Appen öppnas i **Visa → Enkelt läge** med vanliga verktyg synliga; stäng av Enkelt läge för att visa hela verktygsutbudet. I menyn **Flikar** kryssar du i en flik för att visa den och avmarkerar för att dölja den; **Visa alla flikar** och **Dölj alla flikar** finns också. Dra synliga flikar för att ändra ordningen. Flikar utanför valt foto-/videoarbetsläge är inaktiverade i menyn. Menyn **Visa** styr textstorlek och tema. Fönsterstorlek, enkelt/avancerat läge, flikval och textstorlek sparas mellan starter.
- **Verktyg** samlar Python-/pakethantering, autostart, tyst uppdateringssökning och Ko-fi utanför arbetsytan. **Hjälp → Sök efter uppdatering…** kontrollerar senaste GitHub-releasen. **Hjälp → Hjälp och support** innehåller snabbhjälp, integritetssäker diagnostik, genväg till felloggen och länk till projektets ärendehantering. Diagnostik laddas aldrig upp automatiskt; se [SUPPORT.md](SUPPORT.md) för rapporteringsråd.
- Den uppdaterade MediaForge-ikonen används i apphuvudet, fönstret/aktivitetsfältet, systemfältet, flikarna, knapparna, Linux-autostart och Windows-autostartgenvägen. `fotoverktyg_icon.svg` är skalbar ikonmaster och `mediaforge_logo.svg` är den horisontella vektorlogotypen. Behåll båda SVG-filerna, `fotoverktyg_icon.png` och flerupplöst `fotoverktyg_icon.ico` bredvid appen; PNG/ICO är kompatibilitetsalternativ för system som inte visar SVG-ikoner. Windows aktivitetshanterares processvy visar fortfarande `pythonw.exe`-ikonen eftersom appen körs genom Python-tolken; själva appfönstret och aktivitetsfältet använder MediaForge-ikonen och app-ID:t.

## Autostart

MediaForge startar alltid minimerat; återställ fönstret från aktivitetsfältet (eller systemfältet där det finns). **Verktyg → Stäng/minimera till systemfältet** gör att stäng- och minimera-knapparna gömmer appen i systemfältet; använd systemfältsmenyn för att öppna eller avsluta den. Om appen startas igen aktiveras det befintliga fönstret. **Verktyg → Starta automatiskt vid inloggning** slår på eller av autostart för användarkontot på Windows, macOS eller Linux. MediaForge använder Windows Start-mapp, en LaunchAgent på macOS eller Linux XDG-autostart och startas via plattformsstartaren, inte genom direktregistrering av `.pyw`. Autostart startar inte konvertering eller nedladdning.

## Installera och starta

Python 3.10 eller senare (även 3.15) måste redan finnas som systemets Python; MediaForge installerar ingen egen runtime. Startarna har ingen övre versionsgräns, och pip väljer aktuella gemensamma paket för den hittade tolken.

### Windows

Ha `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw` och ikonfilerna i samma mapp. Starta appen med `Starta_Fotoverktyg.vbs`. Startaren söker efter befintlig system-Python 3.10+ via Python-startaren, Windows registerposter, PATH och vanliga installationsmappar. Den installerar aldrig Python eller skapar en app-specifik miljö; om ingen kompatibel runtime hittas visas ett tydligt fel och appen avslutas. Nödvändiga paket installeras i användarkontots gemensamma Python-paket (`pip --user`) endast om de saknas. Paket uppdateras inte automatiskt vid start. Använd **Uppdatera alla Python-paket (starta om)** under Verktyg för att uppdatera dem manuellt. Andra program som använder samma Python kan påverkas. **Uppdatera systemets Python** uppdaterar endast en befintlig winget-hanterad runtime; ingen ny Python installeras.

### macOS / Linux

Använd den medföljande startaren. Den använder den kompatibla Python-installationen direkt och startar MediaForge efter kontroll och uppdatering av de gemensamma användarpaketen:

```bash
chmod +x start_mediaforge.sh   # en gång vid behov
./start_mediaforge.sh
```

Startaren använder befintlig system-Python 3.10+ direkt, utan app-specifik virtuell miljö, och installerar aldrig en Python-runtime. Om ingen kompatibel Python hittas visas ett tydligt fel och appen avslutas. Paketcache, temporära paketfiler och inställningar sparas i `MediaForge_Data/` bredvid appen. App- och startloggar sparas separat i `Logs/` direkt i appmappen; loggar från föregående dagar arkiveras i `Logs/Archive/`, medan olösta fel ligger kvar i `Logs/errors.log`. **Uppdatera systemets Python** försöker bara uppdatera en befintlig runtime via Homebrew eller upptäckt systempakethanterare på Linux; om den inte hanteras av pakethanteraren lämnas den orörd. Ingen ersättnings-Python installeras. Linux-distributionens förråd kan släpa efter den senaste upstream-versionen; pakethanteraren kan begära administratörsgodkännande. PyQt6, Pillow, pillow-heif och piexif installeras via `pip --user` endast om de saknas. Ingen automatisk paketuppdatering körs vid start. **Uppdatera alla Python-paket (starta om)** kör uppdateringen manuellt; den behöver internetåtkomst. Andra program som använder samma Python kan påverkas. En gammal `MediaForge_Data/PythonEnv/` lämnas kvar men används inte. PyQt6 kan dessutom kräva inbyggda Qt-/skrivbordskomponenter.

### Valfria systemverktyg

- **ExifTool**: rekommenderas för bred metadatahantering, bland annat för video, HEIC, RAW, PNG och WEBP.
- **FFmpeg** (inklusive `ffprobe`): krävs för bildspel, videokonvertering, stabilisering, ljudbearbetning och codec-rapporter.
- **xorriso**, **genisoimage** eller **mkisofs**: möjliggör skapande av ISO-avbild för musik-data-DVD.

Detta är systemprogram, inte Python-paket, och MediaForge installerar dem inte.

All lokalt skapad appdata och standardutdata sparas i `MediaForge_Data/` under appmappen. Utdata får inte sparas utanför appmappen; källmappar utanför appen kan fortfarande läsas. Håll appmappen skrivbar. OS-autostart ligger kvar på operativsystemets normala användarplats.

Den inbyggda uppdateraren kontrollerar den senaste publicerade GitHub-releasen och hämtar dess Git-tagg (för närvarande **0.0.2**), inte commits från `main` eller binärfiler från releasen. Välj **Hjälp → Sök efter uppdatering…** eller använd systemfältsmenyn. Uppdateraren jämför commit-ID och ändrade filer och frågar före installation. En ren Git-kopia snabbspolas när det går; om grenen skiljer sig från releasen växlar uppdateraren arbetskopian till releasetaggen i frikopplat läge, medan den ursprungliga grenen och dess commits behålls. Om kopian redan innehåller release-committen görs ingen nedgradering. Källkodsarkiv utan `.git` kan också uppdateras från samma release; endast appfiler ersätts, befintliga filer säkerhetskopieras och appdata lämnas orörd. **Sök tyst efter nya versioner (2 ggr/dygn)** är aktiverat som standard, kontrollerar högst var tolfte timme medan MediaForge är öppet och är tyst när ingen ny release finns. Kontroller körs inte när appen är stängd.

## Uppskattning av mappjobb och tangentbordsgenvägar

MediaForge kör endast en programinstans per användare. Om du startar igen aktiveras det redan öppna fönstret i stället för att öppna ett till.

I huvudfönstrets mappjobb visar **Beräkna tid och diskutrymme** antal filer, total indatastorlek, uppskattat utrymmesbehov och ledigt utrymme på målenheten. Vid överskrivning räknas ungefär största temporära filen; i kopieringslägen används källornas totala storlek. Verklig utdata kan avvika. Under bearbetning visas en återstående tidsprognos efter första filen och den justeras efter uppmätt hastighet. Genvägarna visas även i menyerna **Fil** och **Visa → Välj flik**: **Ctrl/Cmd+O** välj källmapp, **Ctrl/Cmd+Shift+O** välj arkivmapp, **Ctrl/Cmd+Enter** starta mappjobbet, **F1** öppna Hjälp och support, **Ctrl/Cmd+Q** avsluta och **Ctrl/Cmd+1–9** välj en av de första nio synliga flikarna. **Ctrl+Tab** och **Ctrl+Shift+Tab** byter också flik. Kontroller har tillgängliga namn och beskrivningar för skärmläsare, och etiketter kopplas till inmatningsfält där det går. Bearbetningsfel får ett kontextanpassat råd om nästa steg i aktivitets- och verktygsloggarna.

## Fotofunktioner

- **Bildbibliotek / fotobläddrare** — öppna en mapp utan att kopiera bilderna, bläddra bland miniatyrer, gå mellan foton, visa i helskärm och skriv ut vald bild. Undermappar kan tas med. Bilderna ändras inte; HEIC/HEIF/AVIF-förhandsvisning kräver `pillow-heif`. Startar du MediaForge med en bildsökväg öppnas mappen och bilden markeras; välj själv MediaForge som standardapp i operativsystemets inställningar om du vill.
- **Bildförbättring** — välj förinställningen Webb, Sociala medier eller Arkiv och justera sedan förstoring, skärpa, färg och kontrast. Ändrar du en enskild inställning växlar väljaren till Manuell. Kopior sparas utan att originalen ändras.
- **Bildoptimering** — importera en mapp, ta med undermappar, skapa optimerade kopior och välj om EXIF/metadata ska rensas. JPEG-bilddata kopieras utan omkodning; PNG/TIFF optimeras och WEBP sparas förlustfritt. Hur mycket filstorleken minskar beror på originalet.
- **Fotoredigerare** — rotera, beskära, ångra och spara en kopia.
- **Färgprofiler** — konvertera mellan sRGB, Display P3 och Adobe RGB (1998). Inbäddade profiler används; för omärkta bilder kan en antagen källprofil väljas. Qt kan utelämna metadata i konverterade kopior.
- **Dubblettfinnare** — hittar identiska filer med SHA-256 och visuellt liknande bilder med perceptuell hash. Jämför bilder i en grupp sida vid sida och välj enkelt att behålla en bild, alla eller markera enskilda. Omarkerade kopior flyttas efter bekräftelse, inte raderas permanent, till appens karantänmapp.
- **AVIF/HEIC → JPEG** — lägg till en eller flera AVIF-, HEIC- eller HEIF-filer, välj målmapp och JPEG-kvalitet och konvertera. Originalfilerna ändras inte. HEIC/AVIF kräver `pillow-heif`.
- **Webbbilder / Blocket → JPEG** — hämta stödda direkta bildlänkar eller offentliga Blocket-galleribilder. Hämta bara bilder du har rätt att använda.

## Video- och mediafunktioner

- **Bildspel → MP4** — välj och sortera bilder, ställ in visningstid, välj ingen övergång/toning/svep/skjutning, lägg till valfri musik och exportera H.264/AAC-video. Bilder beskärs inte; svarta kanter fyller ut olika bildformat. Kräver FFmpeg.
- **Videokonvertering** — konvertera videor till MP4/H.264/AAC med förinställningarna Webb (720p/mindre fil), Sociala medier (1080p) eller Arkiv (originalupplösning/hög kvalitet). Upplösning och kvalitet kan justeras; väljaren går tillbaka till Manuell om du ändrar enskilda värden. Omkodning kan påverka kvaliteten; originalen bevaras. Kräver FFmpeg.
- **Ljud från video** — extrahera första ljudspåret till MP3, WAV eller FLAC, eller skapa en ljudlös videokopia genom att ta bort ljudspåren. Ljudborttagning kopierar videoströmmen utan omkodning. Originalen ändras inte; kräver FFmpeg.
- **Videostabilisering** — stabilisera klipp med FFmpeg deshake och exportera H.264-kopior; omkodning kan påverka kvaliteten.
- **Ljudförbättring** — normalisera ljudstyrka eller minska konstant bakgrundsbrus i ljud-/videomappar. Ljudet kodas om medan videoströmmen kopieras; kräver FFmpeg.
- **Codec-rapport** — granska container, längd, ljud-/videocodec, upplösning, bildfrekvens, bitrate, samplingsfrekvens och kanaler; exportera CSV. Kräver ffprobe.
- **Skapa musik-DVD** — samla ljudfiler i en mapp som ryms på en DVD-5 och skapa, om ett ISO-verktyg finns installerat, en ISO som kan brännas som skivavbild. Detta är en **data-DVD**, inte DVD-Video; kompatibilitet med fristående DVD-spelare varierar.
- **Datum & EXIF** — ändra datum och rensa metadata. Välj arkivkopior, nya `_rensad`-kopior bredvid källfilerna eller bekräfta att originalen ska skrivas över; källmappslägena kräver full metadatarensning och lämnar originalet orört om en fil misslyckas.
- **Aktivitetslogg** — granska åtgärder, jobbresultat och fel.

## Säkerhet och begränsningar

MediaForge lämnar källfiler orörda i kopierings- och exportflöden. Dubblettrensning flyttar omarkerade filer till en lokal karantän i stället för att radera dem permanent. Full metadatarensning kan ta bort GPS, kamerainställningar, färgprofiler och annan information. Testa alltid med kopior. Förlustfri optimering garanterar inte mindre filer. Videokonvertering är en omkodning med kvalitetsförlust. Musik-DVD-funktionen skapar en data-DVD, inte en DVD-Video.
