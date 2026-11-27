# MediaForge — Photo & Video Toolkit

A desktop toolkit for photo and video workflows. MediaForge can enhance and optimize image folders, remove EXIF metadata, edit and convert photos, batch-convert videos, manage file dates, download supported web images, and prepare a music data-DVD.

Copyright © 2026 Rickard Längkvist.

## License

MediaForge is released under the MIT License, allowing private and commercial use, copying, modification, and redistribution as long as the copyright and license notice are retained. See [LICENSE](LICENSE) or **Help → License and usage rights** in the app.

## Language and workspace modes

- Choose **English** or **Svenska** from the language selector in the app. The choice is saved for the next launch.
- Choose **All**, **Photo**, or **Video** in the workspace selector. **Photo** shows the photo-related tabs; **Video** shows video and music-DVD tabs. Shared date/metadata and activity-log tabs remain available in either mode.
- Language, workspace, theme, recent folders, and common processing settings are saved locally.
- The app opens in **View → Simple mode** with common tools visible; turn Simple mode off to reveal the full toolset. In the **Tabs** menu, check a tab to show it and uncheck it to hide it; **Show all tabs** and **Hide all tabs** are also available. Reorder visible tabs by dragging them. Tabs outside the selected Photo/Video mode are disabled in this menu. The **View** menu controls text size and theme. Window size, simple/advanced mode, tab visibility/order, and text size are remembered between launches.
- **Tools** keeps Python/package management, autostart, and quiet update checks out of the main workspace. **Help → Support development · Donate** opens a dialog in the app with a Swish QR code (standard Swish C-format, number locked) with an amount selector (25/50/100/200 SEK or a custom amount) plus fixed Ko-fi and PayPal buttons; all destinations are maintainer-configured, never user-editable, and the Swish number is never shown in plain text. There is no separate donation page. **Help → Check for updates…** checks the latest GitHub Release tag; **Help → Help & support** provides searchable quick guidance, an interactive step-by-step tutorial, a privacy-safe diagnostics summary, the error-log shortcut, and a link to the project issue tracker. Diagnostics are never uploaded automatically; see [SUPPORT.md](SUPPORT.md) for reporting guidance.
- The refreshed, vivid MediaForge icon is used in the app header, window/taskbar, system tray, tabs, buttons, Linux autostart, and Windows autostart shortcut. `fotoverktyg_icon.svg` is the scalable icon master, `mediaforge_logo.svg` is the horizontal color wordmark, and `mediaforge_logo_print.svg` is a print-ready SVG with all lettering converted to vector outlines. Keep these SVGs, `fotoverktyg_icon.png`, and the matching multi-size `fotoverktyg_icon.ico` beside the app; PNG/ICO provide compatibility fallbacks for platforms that do not render SVG icons.
- **Keyboard shortcuts** are listed under **Help → Keyboard shortcuts…** (Ctrl+?). The **Image enhancement** tab can add a **watermark** (text, position, opacity) to enhanced images. In the **Image library**, **Before/after…** shows the original and an enhanced version side by side.

## Autostart

MediaForge starts minimized in the system tray when a tray is available (otherwise minimized to the taskbar); restore it from the tray icon or the taskbar. At sign-in the tray can be delayed, so the app keeps retrying in the background for up to two minutes and moves to the tray as soon as the icon becomes visible. **Tools → Close/minimize to system tray** makes the window close button and minimize button hide the app in the tray; use the tray menu to reopen or quit. Launching it again activates the existing window. System-tray behavior is available on Windows, macOS, and Linux desktop environments that provide a tray; when the desktop has no tray, the option is disabled and closing exits normally. Choose **Tools → Start automatically at sign-in** to turn per-user autostart on or off on Windows, macOS, or Linux. MediaForge uses a Windows Startup-folder shortcut, a macOS LaunchAgent, or Linux XDG autostart, each launching through the platform launcher rather than registering the `.pyw` file directly. **Tools → Register MediaForge as an image viewer** adds a current-user Open With entry without changing the default app; choose MediaForge manually in OS settings. Windows users can also add the Explorer right-click menu. **Keep the computer awake during jobs** is optional and disabled by default.

## Install and run

MediaForge uses a system Python 3.10 or later (including 3.15). If no Python installation is detected, the platform launcher asks before installing the latest version available through the OS package source. If any Python is already installed—even an older one—the launcher never offers or installs another; upgrade that installation manually if it is below 3.10. Python packages stay in the shared user environment, never an app-private environment.

### Windows

Keep `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw`, and the icon files together. Start the app with `Starta_Fotoverktyg.vbs`. The launcher searches the Python launcher, registry, PATH, and common install folders. If no Python installation is found, it asks before installing the latest stable package available through winget. If any Python is already installed, it never offers or installs another; an incompatible version must be upgraded manually. No standalone Python-update `.bat` is included. Required packages are installed into the current user's shared Python packages (`pip --user`) only if missing. Packages are not automatically updated at startup. Use **Update all Python packages (restart)** under Tools to update packages; these shared packages may also affect other programs using that Python.

### macOS / Linux

Use the included launcher. It uses the detected compatible Python installation directly and starts MediaForge after checking and updating the shared user-level packages:

```bash
chmod +x start_mediaforge.sh   # one time, if needed
./start_mediaforge.sh
```

The launcher uses a system Python 3.10+ directly, without an app-specific virtual environment. If no Python is detected, it asks before installing the newest package available from Homebrew or the Linux distribution's package manager. If any Python already exists, it will not offer or install another; an older incompatible version must be upgraded manually. It stores only the pip cache, temporary files and settings under `MediaForge_Data/`; app and launcher logs are in the app-folder `Logs/` subfolder. It installs `PyQt6`, `Pillow`, `pillow-heif` and `piexif` with `pip install --user --upgrade` only when required packages are missing. There is no automatic package update at startup. Use **Update all Python packages (restart)** in Tools to update them manually. These user-level packages are shared with other programs using the same Python account and can affect them. A manual update needs internet access. If package installation fails but all required packages are already available, MediaForge still launches and records the unresolved warning in `Logs/errors.log`; missing packages prevent startup. Linux package managers may require administrator approval and can lag behind the newest upstream Python release. Existing `MediaForge_Data/PythonEnv/` contents from earlier versions are left untouched and no longer used. PyQt6 may also require native desktop/Qt libraries.

### Optional system tools

- **ExifTool**: recommended for broad metadata handling, including video, HEIC, RAW, PNG, and WEBP.
- **FFmpeg** (including `ffprobe`): required for slideshow export, video conversion, stabilization, audio processing, and codec reports.
- **xorriso**, **genisoimage**, or **mkisofs**: enables creating an ISO image for the music data-DVD.

These are system programs, not Python packages, and are not installed by MediaForge. Their folders can be set under **Tools → External tools…**; otherwise MediaForge finds them via PATH.

## App-local storage and updates

MediaForge stores settings in `MediaForge_Data/Settings/`, pip downloads in `MediaForge_Data/PipCache/`, temporary package files in `MediaForge_Data/Temp/`, and default exports in `MediaForge_Data/Output/`. Python packages are installed in the current user's shared Python site, not in an app-specific environment; other programs using that Python may be affected. Any existing `MediaForge_Data/PythonEnv/` from an earlier version is retained but unused. App and launcher logs have their own subfolder, `Logs/`, directly inside the app folder. Previous-day `mediaforge.log` and `launcher.log` files are archived in `Logs/Archive/`. Warnings and errors are kept in the append-only `Logs/errors.log` until they are resolved; it is never rotated or deleted automatically. The Swish number and the Ko-fi/PayPal links are maintainer-configured, cannot be changed in the app, and the Swish number is only shown as a QR code. All chosen output destinations must remain inside the application folder; external source folders can still be selected and read. Keep the app folder writable. OS autostart registration remains in the normal per-user OS location.

The in-app updater checks the latest published GitHub Release and fetches its Git tag (currently **0.0.2**), not commits from `main` or release binary assets. Choose **Help → Check for updates…** or use the system-tray menu. It compares the updateable app files against the release (SHA-256) and asks before applying. A clean Git checkout is fast-forwarded when possible; if its branch has diverged from the release, the updater switches the working copy to the release tag in detached-HEAD mode while preserving the original branch and commits. If the checkout already contains the release commit, it will not downgrade it. Source-archive copies without `.git` can also update from the same release; only app files are replaced, existing files are backed up, and app data is kept. The enabled-by-default **Silently check for updates twice a day** option checks at most every 12 hours while MediaForge is open and stays quiet when no release is available. Checks do not run while the app is closed.

**Maintainer release routine:** after every code update, move the `0.0.2` release tag to the new commit and refresh the release notes so the updater offers the latest code. Run `Uppdatera_Release.ps1` (Windows) or `./update_release.sh` (macOS/Linux), optionally with `--notes-file <notes.md>` (PowerShell: `-NotesFile <notes.md>`). The version stays `0.0.2`; only the tag target and notes change.

## Batch estimates and keyboard shortcuts

MediaForge allows one running app instance per user. Launching it again brings the existing window to the front instead of opening another one.

For the main folder-processing job, **Estimate time and disk space** scans the selected files and shows file count, total input size, approximate required space and free space on the destination drive. In overwrite mode the estimate is the largest temporary copy; in copy modes it uses the total source size. Actual output can vary. During processing, a remaining-time estimate appears after the first file and refines from observed throughput. The optional post-processing workflow can sort archived results into **Images** and **Videos** subfolders. Optional source-folder watching asks before it processes only newly added files; it never starts jobs without confirmation. Shortcuts are shown in the **File** and **View → Select tab** menus: **Ctrl/Cmd+O** choose source, **Ctrl/Cmd+Shift+O** choose archive, **Ctrl/Cmd+Enter** start the folder job, **F1** open Help & Support, **Ctrl/Cmd+Q** quit, and **Ctrl/Cmd+1–9** select one of the first nine visible tabs. **Ctrl+Tab** and **Ctrl+Shift+Tab** also switch tabs. Controls now expose accessible names and descriptions for screen readers, with labels associated to their inputs where possible. Processing errors include a context-based next-step suggestion in the activity and per-tool logs.

## Photo tools

- **Photo library / browser** — open a folder in place, browse thumbnails, move between photos, view them full-screen, and print the selected image. Crop/edit, sharpen, and compress each offer a choice to save a new copy or overwrite the original, with a separate confirmation before overwriting; processing uses a temporary file and will not replace a source that changed during processing. Compression overwrites only when the selected output format matches the original JPEG/WebP format, and only if the result is smaller; otherwise the original is unchanged. **Move to trash** requires confirmation and uses the OS trash so the file can be recovered. Optional subfolder scanning is available. SVG previews use QtSvg; HEIC/HEIF/AVIF previews require `pillow-heif`.
- **Photo enhancement** — choose Web, Social media, or Archive presets, then adjust scale, sharpness, color, and contrast; save copies without changing originals. Changing an individual setting switches the preset selector back to Manual.
- **Image optimization** — import a folder, include subfolders, create optimized copies, and optionally remove EXIF/metadata. JPEG image data is copied without re-encoding; PNG/TIFF optimization and WEBP lossless encoding preserve image quality. File-size reductions depend on the source.
- **Photo editor** — rotate, straighten the horizon, crop, undo, conservatively remove red-eye within a selection, or optionally blur a selected region (for example, a face or plate). Save a new copy or explicitly confirm overwriting the original.
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
- **Verktyg** samlar Python-/pakethantering, autostart och tyst uppdateringssökning utanför arbetsytan. **Hjälp → Stöd utvecklingen · Donationer** öppnar en dialog i appen med en Swish-QR-kod (Swish standardformat) samt fasta Ko-fi- och PayPal-knappar. Alla betalningsmål är fast inställda av utvecklaren och går inte att ändra i appen; Swish-numret visas bara som QR-kod. Det finns ingen separat doneringssida. **Hjälp → Sök efter uppdatering…** kontrollerar senaste GitHub-releasen. **Hjälp → Hjälp och support** innehåller snabbhjälp, integritetssäker diagnostik, genväg till felloggen och länk till projektets ärendehantering. Diagnostik laddas aldrig upp automatiskt; se [SUPPORT.md](SUPPORT.md) för rapporteringsråd.
- Den nya, färgstarka MediaForge-ikonen används i apphuvudet, fönstret/aktivitetsfältet, systemfältet, flikarna, knapparna, Linux-autostart och Windows-autostartgenvägen. `fotoverktyg_icon.svg` är skalbar ikonmaster, `mediaforge_logo.svg` är den horisontella färglogotypen och `mediaforge_logo_print.svg` är en tryckvänlig SVG med bokstäver omvandlade till vektorbanor. Behåll SVG-filerna, `fotoverktyg_icon.png` och flerupplöst `fotoverktyg_icon.ico` bredvid appen; PNG/ICO används som kompatibilitetsalternativ där SVG-ikoner inte visas. Windows aktivitetshanterares processvy visar fortfarande `pythonw.exe`-ikonen eftersom appen körs genom Python-tolken; själva appfönstret och aktivitetsfältet använder MediaForge-ikonen och app-ID:t.

## Autostart

MediaForge startar alltid minimerat i systemfältet när ett systemfält finns (annars minimerat till aktivitetsfältet); återställ fönstret från systemfältsikonen eller aktivitetsfältet. Vid inloggning kan systemfältet vara fördröjt, så appen försöker i bakgrunden i upp till två minuter och flyttar sig till systemfältet så snart ikonen blir synlig. **Verktyg → Stäng/minimera till systemfältet** gör att stäng- och minimera-knapparna gömmer appen i systemfältet; använd systemfältsmenyn för att öppna eller avsluta den. Om appen startas igen aktiveras det befintliga fönstret. **Verktyg → Starta automatiskt vid inloggning** slår på eller av autostart för användarkontot på Windows, macOS eller Linux. MediaForge använder Windows Start-mapp, en LaunchAgent på macOS eller Linux XDG-autostart och startas via plattformsstartaren, inte genom direktregistrering av `.pyw`. Autostart startar inte konvertering eller nedladdning.

## Installera och starta

MediaForge använder systemets Python 3.10 eller senare (även 3.15). Om ingen Python hittas frågar startaren innan den installerar den senaste versionen som finns via operativsystemets pakethanterare. Om någon Python redan finns—även en äldre—erbjuder eller installerar startaren aldrig en ny; uppgradera den befintliga installationen manuellt om den är äldre än 3.10. Python-paket installeras i användarens gemensamma miljö, aldrig i en app-privat miljö.

### Windows

Ha `Starta_Fotoverktyg.vbs`, `Starta_Fotoverktyg.ps1`, `fotoverktyg.pyw` och ikonfilerna i samma mapp. Starta appen med `Starta_Fotoverktyg.vbs`. Startaren söker via Python-startaren, registerposter, PATH och vanliga installationsmappar. Om ingen Python alls hittas frågar den innan den installerar den senaste stabila versionen via winget. Om någon Python redan finns erbjuder eller installerar den aldrig en till; en version äldre än 3.10 måste uppgraderas manuellt. Ingen separat Python-uppdateringsfil `.bat` ingår. Nödvändiga paket installeras i användarkontots gemensamma Python-paket (`pip --user`) endast om de saknas. Paket uppdateras inte automatiskt vid start. Använd **Uppdatera alla Python-paket (starta om)** under Verktyg för att uppdatera Python-paketen manuellt.

### macOS / Linux

Använd den medföljande startaren. Den använder den kompatibla Python-installationen direkt och startar MediaForge efter kontroll och uppdatering av de gemensamma användarpaketen:

```bash
chmod +x start_mediaforge.sh   # en gång vid behov
./start_mediaforge.sh
```

Startaren använder systemets Python 3.10+ utan app-specifik virtuell miljö. Om ingen Python hittas frågar den innan installation via Homebrew eller Linux-distributionens pakethanterare. Om någon Python redan finns installeras aldrig en till; en äldre inkompatibel version måste uppgraderas manuellt. Paketcache, temporära paketfiler och inställningar sparas i `MediaForge_Data/` bredvid appen. App- och startloggar sparas separat i `Logs/` direkt i appmappen; loggar från föregående dagar arkiveras i `Logs/Archive/`, medan olösta fel ligger kvar i `Logs/errors.log`. Linux-pakethanterare kan kräva administratörsgodkännande och deras Python-version kan ligga efter senaste upstream-versionen.

### Valfria systemverktyg

- **ExifTool**: rekommenderas för bred metadatahantering, bland annat för video, HEIC, RAW, PNG och WEBP.
- **FFmpeg** (inklusive `ffprobe`): krävs för bildspel, videokonvertering, stabilisering, ljudbearbetning och codec-rapporter.
- **xorriso**, **genisoimage** eller **mkisofs**: möjliggör skapande av ISO-avbild för musik-data-DVD.

Detta är systemprogram, inte Python-paket, och MediaForge installerar dem inte.

All lokalt skapad appdata och standardutdata sparas i `MediaForge_Data/` under appmappen. Utdata får inte sparas utanför appmappen; källmappar utanför appen kan fortfarande läsas. Håll appmappen skrivbar. OS-autostart ligger kvar på operativsystemets normala användarplats.

**Automatisk uppdatering kl. 00:00** kontrollerar senaste GitHub-releasen när appen är igång, eller efter nästa start om kontrollen missades. Finns en ändring installeras den automatiskt när inga jobb pågår, följt av omstart; pågående jobb skjuter upp kontrollen. Manuell kontroll via **Hjälp → Sök efter uppdatering…** visar ändrade filer och frågar först. Uppdateraren jämför appfiler och skyddar appdata. För en ren Git-kopia är `main`, `master` och frikopplat läge spärrade; bara en release som är en snabbspolning och finns i motsvarande ursprungsgren installeras, utan merge eller grenbyte. Andra fall hoppas över. För arkivinstallationer verifieras installerade filer och tillfällig säkerhetskopia tas bort först efter lyckad verifiering; fel utlöser återställning. Ingen kontroll sker medan appen är stängd.

## Uppskattning av mappjobb och tangentbordsgenvägar

MediaForge kör endast en programinstans per användare. Om du startar igen aktiveras det redan öppna fönstret i stället för att öppna ett till.

I huvudfönstrets mappjobb visar **Beräkna tid och diskutrymme** antal filer, total indatastorlek, uppskattat utrymmesbehov och ledigt utrymme på målenheten. Vid överskrivning räknas ungefär största temporära filen; i kopieringslägen används källornas totala storlek. Verklig utdata kan avvika. Under bearbetning visas en återstående tidsprognos efter första filen och den justeras efter uppmätt hastighet. Genvägarna visas även i menyerna **Fil** och **Visa → Välj flik**: **Ctrl/Cmd+O** välj källmapp, **Ctrl/Cmd+Shift+O** välj arkivmapp, **Ctrl/Cmd+Enter** starta mappjobbet, **F1** öppna Hjälp och support, **Ctrl/Cmd+Q** avsluta och **Ctrl/Cmd+1–9** välj en av de första nio synliga flikarna. **Ctrl+Tab** och **Ctrl+Shift+Tab** byter också flik. Kontroller har tillgängliga namn och beskrivningar för skärmläsare, och etiketter kopplas till inmatningsfält där det går. Bearbetningsfel får ett kontextanpassat råd om nästa steg i aktivitets- och verktygsloggarna.

## Fotofunktioner

- **Bildbibliotek / fotobläddrare** — öppna en mapp, bläddra bland miniatyrer, visa i helskärm och skriv ut. Beskärning/redigering, skärpning och komprimering erbjuder vart och ett valet att spara en ny kopia eller skriva över originalet, med separat bekräftelse före överskrivning. Bearbetningen använder en temporär fil och ersätter inte en källfil som ändrats under tiden. Komprimering kan bara skriva över när valt utdataformat matchar originalets JPEG/WebP-format, och endast om resultatet blir mindre; annars lämnas originalet orört. **Flytta till papperskorgen** kräver bekräftelse och använder systempapperskorgen så filen kan återställas. Undermappar kan tas med. HEIC/HEIF/AVIF-förhandsvisning kräver `pillow-heif`. Startar du MediaForge med en bildsökväg öppnas mappen och bilden markeras; välj själv MediaForge som standardapp i operativsystemets inställningar om du vill.
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

**Skärm och prestanda:** Qt hanterar operativsystemets DPI-skalning. Bildförhandsvisningar och miniatyrer renderas för skärmens pixeltäthet, och fönstret samt jämförelsedialogen anpassas till tillgängligt skärmutrymme. JPEG-miniatyrer kan avkodas i lägre upplösning för att minska minnesåtgång och arbete; vanliga exporter behåller full upplösning. Skärpan arbetar på ljushetskanalen med en finare radie för att minska färgkanter och breda glorior. Resultatet beror på original och valda reglage.

Loggarkiv för apploggen som är äldre än sju dygn rensas vid start och rotation. Felloggen kan rensas efter att användaren bekräftat att alla fel är åtgärdade; appen avgör inte detta automatiskt.
