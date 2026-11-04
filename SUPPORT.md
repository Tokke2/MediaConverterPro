# MediaForge Support

## Get help in the app

Open **Help → Help & support** for quick setup guidance, dependency reminders, an error-log shortcut, and a privacy-safe diagnostic summary you can copy into a support request. The summary contains the MediaForge version, operating system, Python/Qt versions, and whether FFmpeg and ExifTool are available. It does not include your files, local paths, or log contents.

## Before reporting a problem

1. Update to the latest version available for your installation and restart MediaForge.
2. Note the operating system, what you were trying to do, the steps to reproduce it, and what you expected to happen.
3. Open `Logs/errors.log` in the app folder; it is append-only and retains warnings/errors until manually cleared after resolution. Consult `Logs/mediaforge.log` and `Logs/Archive/` for more context.
4. Review logs before sharing them. They can contain local file paths, listing URLs, and ad IDs. Remove private information first.
5. Include the copied diagnostic summary and, if useful, a short sanitized log excerpt in an issue at <https://github.com/Tokke2/MediaConverterPro/issues/new>.

MediaForge does not upload diagnostic information or logs automatically.

## Common requirements

- Start the app with the provided platform launcher. Python 3.10 or later is required.
- FFmpeg is required for video conversion, stabilization, audio tools, codec reports, and slideshow export.
- ExifTool is recommended for broad EXIF and media metadata support. Without it, metadata support is limited to supported JPEG/TIFF operations through `piexif`.

Settings, cache, and the private Python environment are stored under `MediaForge_Data/` next to the application. Logs are stored in the sibling `Logs/` subfolder. Keep both app-folder locations writable.
