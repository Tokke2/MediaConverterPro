#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fotoverktyg: skärpa/färg/upscale + datumfix/EXIF-rensning på kopior."""
import os
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = Path.home() / '.fotoverktyg_studio' / 'logs'
LOG_FILE = LOG_DIR / 'fotoverktyg.log'
LOGGER = logging.getLogger('fotoverktyg')
LOGGER.setLevel(logging.INFO)
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(threadName)s | %(message)s'))
    LOGGER.addHandler(handler)
except OSError:
    # Still allow the GUI to run if the home directory is read-only.
    LOGGER.addHandler(logging.NullHandler())
LOGGER.info('Applikationen startar')


from PyQt6 import QtCore, QtGui, QtWidgets
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

Image.MAX_IMAGE_PIXELS = 150_000_000
PHOTO = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp'}
MEDIA = PHOTO | {'.heic', '.heif', '.dng', '.cr2', '.cr3', '.nef', '.arw', '.raf', '.orf', '.rw2', '.mp4', '.mov', '.m4v', '.avi', '.mkv', '.mts', '.gif'}
VIDEO = {'.mp4', '.mov', '.m4v', '.avi', '.mkv', '.mts'}
SOFTWARE_TAGS = ['-Software=', '-ProcessingSoftware=', '-XMP:CreatorTool=', '-XMP:Toolkit=', '-XMP:HistorySoftwareAgent=', '-EncodingTool=', '-Encoder=', '-WriterName=', '-QuickTime:Software=']


def exiftool(args, timeout=60):
    exe = shutil.which('exiftool')
    if not exe:
        raise RuntimeError('ExifTool saknas. Installera ExifTool för metadata i video, HEIC, PNG m.fl.')
    result = subprocess.run([exe, *args], capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or 'ExifTool misslyckades')
    return result.stdout.strip()


def file_date(path):
    try:
        value = exiftool(['-s3', '-DateTimeOriginal', '-CreateDate', '-d', '%Y:%m:%d %H:%M:%S', '--', str(path)], 20)
        for line in value.splitlines():
            try:
                return datetime.strptime(line.strip(), '%Y:%m:%d %H:%M:%S')
            except ValueError:
                pass
    except RuntimeError:
        pass
    return datetime.fromtimestamp(path.stat().st_mtime)


def set_dates(path, dt, write_meta, strip_software, remove_all=False):
    if not write_meta and not strip_software and not remove_all:
        return
    if shutil.which('exiftool'):
        args = ['-overwrite_original', '-P']
        if remove_all:
            args.append('-all=')
        if write_meta:
            ds = dt.strftime('%Y:%m:%d %H:%M:%S')
            if path.suffix.lower() in VIDEO:
                args += [f'-QuickTime:CreateDate={ds}', f'-QuickTime:ModifyDate={ds}', f'-TrackCreateDate={ds}', f'-TrackModifyDate={ds}', f'-MediaCreateDate={ds}', f'-MediaModifyDate={ds}']
            else:
                args += [f'-AllDates={ds}']
        if strip_software and not remove_all:
            args += SOFTWARE_TAGS
        exiftool([*args, '--', str(path)])
    elif path.suffix.lower() in {'.jpg', '.jpeg', '.tif', '.tiff'}:
        try:
            import piexif
        except ImportError as exc:
            raise RuntimeError('Installera piexif eller ExifTool för JPEG/TIFF-metadata') from exc
        if remove_all and not write_meta:
            piexif.remove(str(path))
            return
        data = piexif.load(str(path)) if not remove_all else {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "Interop": {}, "thumbnail": None}
        if write_meta:
            ds = dt.strftime('%Y:%m:%d %H:%M:%S').encode('ascii')
            data['Exif'][piexif.ExifIFD.DateTimeOriginal] = ds
            data['Exif'][piexif.ExifIFD.DateTimeDigitized] = ds
            data['0th'][piexif.ImageIFD.DateTime] = ds
        if strip_software:
            data['0th'].pop(piexif.ImageIFD.Software, None)
            data['0th'].pop(0x000B, None)
        piexif.insert(piexif.dump(data), str(path))
    else:
        raise RuntimeError('ExifTool krävs för metadata i detta format')


def set_fs_date(path, dt):
    ts = dt.timestamp()
    os.utime(path, (ts, ts))
    if sys.platform == 'win32':
        # ExifTool kan sätta även Windows skapandedatum.
        if shutil.which('exiftool'):
            exiftool(['-overwrite_original', f'-FileCreateDate={dt.strftime("%Y:%m:%d %H:%M:%S")}', '--', str(path)])
            os.utime(path, (ts, ts))
    elif sys.platform == 'darwin' and shutil.which('SetFile'):
        subprocess.run(['SetFile', '-d', dt.strftime('%m/%d/%Y %H:%M:%S'), str(path)], check=True, timeout=20)


def enhance(source, target, factor, sharp, color, clarity, keep_exif):
    with Image.open(source) as original:
        image = ImageOps.exif_transpose(original)
        w, h = image.size
        if w * h * factor * factor > 180_000_000:
            raise ValueError('Den färdiga bilden blir större än 180 megapixlar')
        exif = image.getexif() if keep_exif else None
        if exif:
            exif[274] = 1  # Pixels were already rotated by exif_transpose.
        alpha = image.getchannel('A') if 'A' in image.getbands() else None
        rgb = image.convert('RGB')
        if clarity:
            rgb = ImageOps.autocontrast(rgb, cutoff=min(.8, clarity / 180))
            rgb = ImageEnhance.Contrast(rgb).enhance(1 + clarity / 500)
        if color:
            rgb = ImageEnhance.Color(rgb).enhance(1 + color / 250)
        rgb = rgb.resize((w * factor, h * factor), Image.Resampling.LANCZOS)
        if sharp:
            y, cb, cr = rgb.convert('YCbCr').split()
            y = y.filter(ImageFilter.UnsharpMask(radius=1.8, percent=int(sharp * 1.25), threshold=4))
            y = y.filter(ImageFilter.UnsharpMask(radius=.65, percent=int(sharp * 1.75), threshold=2))
            rgb = Image.merge('YCbCr', (y, cb, cr)).convert('RGB')
        if alpha is not None and target.suffix.lower() != '.jpg':
            rgb.putalpha(alpha.resize(rgb.size, Image.Resampling.LANCZOS))
        kwargs = {}
        if target.suffix.lower() == '.jpg':
            kwargs.update(quality=95, subsampling=0)
        elif target.suffix.lower() == '.webp':
            kwargs.update(quality=95)
        if exif and target.suffix.lower() in {'.jpg', '.webp', '.png'}:
            kwargs['exif'] = exif.tobytes()
        rgb.save(target, **kwargs)


class Worker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()

    def __init__(self, items, settings):
        super().__init__()
        self.items, self.settings = items, settings
        self.cancelled = False

    def run(self):
        s = self.settings
        root, archive = Path(s['root']), Path(s['archive'])
        for i, source in enumerate(self.items, 1):
            if self.cancelled:
                self.message.emit('Avbrutet.')
                break
            try:
                relative = source.relative_to(root) if s['structure'] else Path(source.name)
                target = archive / relative
                if target.exists() and not s['overwrite']:
                    self.message.emit(f'HOPPADES ÖVER: {relative} finns redan')
                    continue
                # Offset must be calculated before altering metadata or filesystem timestamps.
                dt = file_date(source) + s['delta'] if s['offset'] else s['date']
                target.parent.mkdir(parents=True, exist_ok=True)
                if s['enhance'] and source.suffix.lower() in PHOTO:
                    if target.suffix.lower() not in {'.png', '.jpg', '.webp'}:
                        target = target.with_suffix('.png')
                    if target.exists() and not s['overwrite']:
                        self.message.emit(f'HOPPADES ÖVER: {target.name} finns redan')
                        continue
                    enhance(source, target, s['factor'], s['sharp'], s['color'], s['clarity'], s['keep_exif'])
                else:
                    shutil.copy2(source, target)
                errors = []
                try:
                    set_dates(target, dt, s['metadata'], s['strip'], s['remove_all'])
                except Exception as exc:
                    errors.append(f'metadata: {exc}')
                if s['filesystem']:
                    try:
                        set_fs_date(target, dt)
                    except Exception as exc:
                        errors.append(f'filsystem: {exc}')
                self.message.emit(f'{"DELVIS" if errors else "KLAR"}: {relative} → {target}\n  ' + '; '.join(errors) if errors else f'KLAR: {relative} → {target}')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            finally:
                self.progress.emit(i, len(self.items))
        self.completed.emit()


class DropEdit(QtWidgets.QLineEdit):
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            path = Path(urls[0].toLocalFile())
            self.setText(str(path if path.is_dir() else path.parent))
            event.acceptProposedAction()



def register_modern_formats():
    try:
        from pillow_heif import register_heif_opener
        register_heif_opener()
        try:
            from pillow_heif import register_avif_opener
            register_avif_opener()
        except (ImportError, AttributeError):
            pass  # Some releases register AVIF through the HEIF opener.
        return True
    except ImportError:
        return False


class ConversionWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)

    def __init__(self, files, destination, quality, metadata):
        super().__init__()
        self.files = files
        self.destination = destination
        self.quality = quality
        self.metadata = metadata
        self.cancelled = False

    def run(self):
        if not register_modern_formats():
            self.message.emit('Installera pillow-heif: python -m pip install pillow-heif')
            return
        self.destination.mkdir(parents=True, exist_ok=True)
        for i, source in enumerate(self.files, 1):
            if self.cancelled:
                self.message.emit('Konvertering avbruten.')
                break
            try:
                target = self.destination / (source.stem + '.jpg')
                # Never overwrite either source or an earlier converted file.
                n = 2
                while target.exists() or target.resolve() == source.resolve():
                    target = self.destination / f'{source.stem}_{n}.jpg'
                    n += 1
                with Image.open(source) as original:
                    image = ImageOps.exif_transpose(original)
                    source_exif = image.getexif() if self.metadata else None
                    if image.mode in ('RGBA', 'LA') or 'transparency' in image.info:
                        rgba = image.convert('RGBA')
                        canvas = Image.new('RGB', image.size, 'white')
                        canvas.paste(rgba, mask=rgba.getchannel('A'))
                        image = canvas
                    else:
                        image = image.convert('RGB')
                    kwargs = dict(quality=self.quality, subsampling=0, optimize=True)
                    if self.metadata:
                        exif = source_exif
                        if exif:
                            exif[274] = 1
                            kwargs['exif'] = exif.tobytes()
                        icc = original.info.get('icc_profile')
                        if icc:
                            kwargs['icc_profile'] = icc
                    image.save(target, 'JPEG', **kwargs)
                self.message.emit(f'JPEG KLAR: {source.name} → {target.name}')
            except Exception as exc:
                self.message.emit(f'KONVERTERINGSFEL: {source.name}: {exc}')
            finally:
                self.progress.emit(i, len(self.files))


def find_blocket_images(page, item_id):
    """Find every unique gallery image ID for this ad, not just first preload."""
    import re
    from html import unescape
    text = unescape(page).replace(chr(92) + '/', '/')
    text = re.sub(r'\\u002[fF]', '/', text)
    # Images can appear as thumbnails (142w), srcsets (1600w), or in JSON.
    # Restrict matches to this exact item's CDN path to exclude recommendations.
    pattern = rf'(?:https?://images\.blocketcdn\.se)?/dynamic/[^/\s"<>]+/item/{re.escape(item_id)}/([a-zA-Z0-9-]{{16,}})'
    ids = list(dict.fromkeys(re.findall(pattern, text)))
    return [f'https://images.blocketcdn.se/dynamic/1600w/item/{item_id}/{image_id}' for image_id in ids]


def blocket_folder_name(page, item_id):
    """Read visible ad title; produce a single safe cross-platform folder name."""
    import re
    from html import unescape
    from html.parser import HTMLParser

    class HeadingParser(HTMLParser):
        def __init__(self):
            super().__init__()
            self.inside = False
            self.headings = []
            self.parts = []

        def handle_starttag(self, tag, attrs):
            if tag == 'h1':
                self.inside = True
                self.parts = []

        def handle_data(self, data):
            if self.inside:
                self.parts.append(data)

        def handle_endtag(self, tag):
            if tag == 'h1' and self.inside:
                self.headings.append(' '.join(self.parts))
                self.inside = False

    parser = HeadingParser()
    parser.feed(page)
    title = next((value for value in parser.headings if value.strip()), '')
    if not title:
        match = re.search(r'<meta[^>]+property=["\']og:title["\'][^>]+content=["\']([^"\']+)', page, re.I)
        title = match.group(1).split('|')[0] if match else f'Annons_{item_id}'
    title = unescape(title)
    title = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', title)
    title = re.sub(r'\s+', ' ', title).strip(' .-_')[:90].rstrip(' .')
    if not title or title.upper() in {'CON', 'PRN', 'AUX', 'NUL', *(f'COM{i}' for i in range(1, 10)), *(f'LPT{i}' for i in range(1, 10))}:
        title = f'Annons_{item_id}'
    return title


class BlocketWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)

    def __init__(self, urls, destination, quality):
        super().__init__()
        self.urls, self.destination, self.quality = urls, destination, quality
        self.cancelled = False
        self.saved_count = 0
        self.error_count = 0
        self.saved_folders = set()

    def run(self):
        import io
        import re
        import urllib.request
        headers = {'User-Agent': 'Mozilla/5.0 (compatible; PhotoTool/1.0)'}
        self.destination.mkdir(parents=True, exist_ok=True)
        register_modern_formats()
        for i, url in enumerate(self.urls, 1):
            if self.cancelled:
                break
            match = re.fullmatch(r'https://(?:www\.)?blocket\.se/(?:recommerce/forsale|mobility)/item/(\d+)(?:[/?#].*)?', url)
            if not match:
                # A standalone image link can be downloaded and converted to JPEG.
                from urllib.parse import urlparse, unquote
                parsed = urlparse(url)
                if parsed.scheme != 'https' or not parsed.netloc or not parsed.path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.avif', '.heic')):
                    self.message.emit(f'FEL: Ange en Blocket-annons eller en direkt HTTPS-bildlänk: {url}')
                    self.progress.emit(i, len(self.urls))
                    continue
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=30) as response:
                        if not response.headers.get('Content-Type', '').lower().startswith('image/'):
                            raise ValueError('Länken gav inte en bild')
                        data = response.read(35_000_001)
                    if len(data) > 35_000_000:
                        raise ValueError('Bilden är större än 35 MB')
                    filename = unquote(Path(parsed.path).name)
                    stem = filename
                    while Path(stem).suffix.lower() in {'.webp', '.jpg', '.jpeg', '.png', '.avif', '.heic'}:
                        stem = Path(stem).stem
                    stem = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '-', stem).strip(' .-_')[:90] or 'bild'
                    folder = self.destination / 'Direkta bilder'
                    folder.mkdir(parents=True, exist_ok=True)
                    target = folder / f'{stem}.jpg'
                    n = 2
                    while target.exists():
                        target = folder / f'{stem}_{n}.jpg'
                        n += 1
                    with Image.open(io.BytesIO(data)) as original:
                        original.load()
                        image = ImageOps.exif_transpose(original).convert('RGBA')
                        canvas = Image.new('RGB', image.size, 'white')
                        canvas.paste(image, mask=image.getchannel('A'))
                        canvas.save(target, 'JPEG', quality=self.quality, subsampling=0, optimize=True)
                    self.saved_count += 1
                    self.saved_folders.add(folder)
                    self.message.emit(f'Direktbild sparad: {target} ({canvas.width} × {canvas.height})')
                except Exception as exc:
                    self.error_count += 1
                    self.message.emit(f'BILDFEL direktlänk: {exc}')
                self.progress.emit(i, len(self.urls))
                continue
            item_id = match.group(1)
            try:
                request = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(request, timeout=25) as response:
                    page = response.read(4_000_001)
                if len(page) > 4_000_000:
                    raise ValueError('Annonssidan är för stor')
                html_page = page.decode('utf-8', 'replace')
                links = find_blocket_images(html_page, item_id)
                folder = self.destination / blocket_folder_name(html_page, item_id)
                folder.mkdir(parents=True, exist_ok=True)
                self.message.emit(f'Mapp för annons {item_id}: {folder}')
                if not links:
                    raise ValueError('Inga galleribilder hittades. Sidan kan ha ändrats eller kräva inloggning.')
                self.message.emit(f'Annons {item_id}: hittade {len(links)} unika galleribilder (hämtar samtliga)')
                saved = 0
                for index, image_url in enumerate(links, 1):
                    if self.cancelled:
                        break
                    try:
                        data = None
                        last_error = None
                        for size in ('1600w', '1280w', '960w', 'default'):
                            try:
                                candidate = image_url.replace('/1600w/', f'/{size}/')
                                req = urllib.request.Request(candidate, headers=headers)
                                with urllib.request.urlopen(req, timeout=30) as response:
                                    if not response.headers.get('Content-Type', '').lower().startswith('image/'):
                                        raise ValueError('Svaret är inte en bild')
                                    data = response.read(35_000_001)
                                break
                            except Exception as exc:
                                last_error = exc
                        if data is None:
                            raise RuntimeError(f'Ingen bildstorlek tillgänglig: {last_error}')
                        if len(data) > 35_000_000:
                            raise ValueError('Bilden är för stor')
                        target = folder / f'blocket_{item_id}_{index:02}.jpg'
                        n = 2
                        while target.exists():
                            target = folder / f'blocket_{item_id}_{index:02}_{n}.jpg'
                            n += 1
                        with Image.open(io.BytesIO(data)) as original:
                            original.load()
                            image = ImageOps.exif_transpose(original).convert('RGB')
                            image.save(target, 'JPEG', quality=self.quality, subsampling=0, optimize=True)
                        saved += 1
                        self.saved_count += 1
                        self.saved_folders.add(folder)
                        self.message.emit(f'Sparad {saved}/{len(links)}: {target.name} ({image.width} × {image.height})')
                    except Exception as exc:
                        self.error_count += 1
                        self.message.emit(f'BILDFEL annons {item_id}, bild {index}: {exc}')
                self.message.emit(f'Annons {item_id}: {saved} av {len(links)} bilder sparade')
            except Exception as exc:
                self.error_count += 1
                self.message.emit(f'ANNONSFEL {item_id}: {exc}')
            self.progress.emit(i, len(self.urls))


class PipWorker(QtCore.QThread):
    finished_install = QtCore.pyqtSignal(bool, str)

    def __init__(self, packages):
        super().__init__()
        self.packages = packages

    def run(self):
        import subprocess
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', *self.packages], capture_output=True, text=True, timeout=300)
            self.finished_install.emit(result.returncode == 0, (result.stdout + '\\n' + result.stderr)[-3500:])
        except Exception as exc:
            self.finished_install.emit(False, str(exc))


class PhotoCanvas(QtWidgets.QWidget):
    """Preview with a mouse-drag crop rectangle mapped to original pixels."""
    def __init__(self):
        super().__init__()
        self.image = None
        self.selection = None
        self.anchor = None
        self.setMinimumHeight(320)
        self.setMouseTracking(True)

    def set_image(self, image):
        self.image = image
        self.selection = None
        self.update()

    def image_rect(self):
        if self.image is None:
            return QtCore.QRectF()
        w, h = self.image.size
        scale = min(self.width() / w, self.height() / h)
        return QtCore.QRectF((self.width() - w * scale) / 2, (self.height() - h * scale) / 2, w * scale, h * scale)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), QtGui.QColor('#161a22'))
        if self.image is None:
            painter.setPen(QtGui.QColor('#ced6e3'))
            painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, 'Öppna ett foto för att börja redigera')
            return
        rgb = self.image.convert('RGB')
        data = rgb.tobytes()
        qimage = QtGui.QImage(data, rgb.width, rgb.height, rgb.width * 3, QtGui.QImage.Format.Format_RGB888)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform)
        painter.drawImage(self.image_rect(), qimage)
        if self.selection:
            painter.setPen(QtGui.QPen(QtGui.QColor('#50cbff'), 2))
            painter.setBrush(QtGui.QColor(80, 203, 255, 45))
            painter.drawRect(self.selection.normalized())

    def mousePressEvent(self, event):
        if self.image and event.button() == QtCore.Qt.MouseButton.LeftButton:
            self.anchor = event.position()
            self.selection = QtCore.QRectF(self.anchor, self.anchor)
            self.update()

    def mouseMoveEvent(self, event):
        if self.anchor is not None:
            self.selection = QtCore.QRectF(self.anchor, event.position())
            self.update()

    def mouseReleaseEvent(self, event):
        if self.anchor is not None:
            self.selection = QtCore.QRectF(self.anchor, event.position())
            self.anchor = None
            self.update()

    def crop_box(self):
        if not self.image or not self.selection:
            return None
        rect = self.selection.normalized().intersected(self.image_rect())
        preview = self.image_rect()
        if rect.width() < 4 or rect.height() < 4:
            return None
        w, h = self.image.size
        left = max(0, int((rect.left() - preview.left()) * w / preview.width()))
        top = max(0, int((rect.top() - preview.top()) * h / preview.height()))
        right = min(w, int((rect.right() - preview.left()) * w / preview.width()))
        bottom = min(h, int((rect.bottom() - preview.top()) * h / preview.height()))
        return (left, top, right, bottom) if right > left and bottom > top else None


def brand_icon():
    pix = QtGui.QPixmap(96, 96)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    p.setPen(QtCore.Qt.PenStyle.NoPen)
    p.setBrush(QtGui.QColor('#2563eb'))
    p.drawRoundedRect(2, 2, 92, 92, 20, 20)
    p.setBrush(QtGui.QColor('#dbeafe'))
    p.drawRoundedRect(17, 21, 62, 53, 8, 8)
    p.setBrush(QtGui.QColor('#60a5fa'))
    p.drawEllipse(57, 29, 13, 13)
    path = QtGui.QPainterPath()
    path.moveTo(22, 68)
    path.lineTo(39, 42)
    path.lineTo(52, 59)
    path.lineTo(63, 48)
    path.lineTo(77, 69)
    path.closeSubpath()
    p.setBrush(QtGui.QColor('#1d4ed8'))
    p.drawPath(path)
    p.end()
    return QtGui.QIcon(pix)


def startup_file():
    if sys.platform == 'darwin':
        return Path.home() / 'Library/LaunchAgents/se.fotoverktyg.studio.plist'
    return Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))) / 'autostart/fotoverktyg.desktop'


def autostart_enabled():
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
                winreg.QueryValueEx(key, 'Fotoverktyg')
            return True
        except OSError:
            return False
    return startup_file().exists()


def set_autostart(enabled):
    command = [sys.executable] if getattr(sys, 'frozen', False) else [sys.executable, str(Path(__file__).resolve())]
    if sys.platform == 'win32':
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
            if enabled:
                winreg.SetValueEx(key, 'Fotoverktyg', 0, winreg.REG_SZ, subprocess.list2cmdline(command))
            else:
                try:
                    winreg.DeleteValue(key, 'Fotoverktyg')
                except FileNotFoundError:
                    pass
    elif sys.platform == 'darwin':
        import plistlib
        path = startup_file()
        if enabled:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(plistlib.dumps({'Label': 'se.fotoverktyg.studio', 'ProgramArguments': command, 'RunAtLoad': True}))
        else:
            path.unlink(missing_ok=True)
    else:
        path = startup_file()
        if enabled:
            args = ' '.join('"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"' for arg in command)
            path.parent.mkdir(parents=True, exist_ok=True)
            icon = Path(__file__).resolve().with_name('fotoverktyg_icon.png')
            path.write_text('[Desktop Entry]\nType=Application\nName=Fotoverktyg Studio\nExec=' + args + '\nIcon=' + str(icon) + '\nTerminal=false\n', encoding='utf-8')
        else:
            path.unlink(missing_ok=True)


class LogBridge(QtCore.QObject):
    entry = QtCore.pyqtSignal(str)


class QtLogHandler(logging.Handler):
    def __init__(self, bridge):
        super().__init__()
        self.bridge = bridge
        self.setFormatter(logging.Formatter('%(asctime)s  %(levelname)s  %(message)s', '%H:%M:%S'))

    def emit(self, record):
        self.bridge.entry.emit(self.format(record))


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Fotoverktyg · Studio')
        self.log_bridge = LogBridge()
        self.log_bridge.entry.connect(self.append_activity_log)
        self.qt_log_handler = QtLogHandler(self.log_bridge)
        LOGGER.addHandler(self.qt_log_handler)
        icon_file = Path(__file__).resolve().with_name('fotoverktyg_icon.png')
        self.brand = QtGui.QIcon(str(icon_file)) if icon_file.exists() else brand_icon()
        self.setWindowIcon(self.brand)
        self.resize(1100, 850)
        self.setMinimumSize(850, 700)
        self.worker = None
        self.dark = False
        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        main = QtWidgets.QVBoxLayout(central)
        main.setContentsMargins(22, 18, 22, 18)
        main.setSpacing(12)
        title = QtWidgets.QLabel('FOTOVERKTYG  /  STUDIO')
        title.setObjectName('heroTitle')
        main.addWidget(title)
        subtitle = QtWidgets.QLabel('Redigera, konvertera och organisera – originalen förblir orörda.')
        subtitle.setObjectName('subtitle')
        main.addWidget(subtitle)
        self.tabs = QtWidgets.QTabWidget()
        main.addWidget(self.tabs)
        self.deps_button = QtWidgets.QPushButton('Kontrollera/installera Python-tillägg…')
        self.deps_button.clicked.connect(self.manage_dependencies)
        main.addWidget(self.deps_button)
        QtCore.QTimer.singleShot(200, self.offer_missing_dependencies)
        image_tab = QtWidgets.QWidget()
        self.tabs.addTab(image_tab, 'Bildförbättring')
        self.editor_image = None
        self.editor_source = None
        self.editor_history = []
        self.build_editor_tab()
        self.build_conversion_tab()
        self.build_blocket_tab()
        self.build_web_tab()
        self.build_log_tab()
        iv = QtWidgets.QVBoxLayout(image_tab)
        iv.addWidget(QtWidgets.QLabel('Förstora, förbättra färger och skärp foton. Video kopieras utan bildförbättring.'))
        self.enhance_box = QtWidgets.QCheckBox('Förbättra bilder (annars kopieras de oförändrade)')
        self.enhance_box.setChecked(True)
        iv.addWidget(self.enhance_box)
        self.factor = QtWidgets.QComboBox()
        self.factor.addItems(['1× (bara färg/skärpa)', '2×', '3×', '4×'])
        self.factor.setCurrentIndex(1)
        iv.addWidget(QtWidgets.QLabel('Förstoring'))
        iv.addWidget(self.factor)
        self.sliders = {}
        for label, default in [('Skärpa', 65), ('Färgstyrka', 55), ('Klarhet/kontrast', 45)]:
            row = QtWidgets.QHBoxLayout()
            row.addWidget(QtWidgets.QLabel(label))
            slider = QtWidgets.QSlider(QtCore.Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(default)
            row.addWidget(slider)
            number = QtWidgets.QLabel(str(default))
            slider.valueChanged.connect(lambda value, n=number: n.setText(str(value)))
            row.addWidget(number)
            iv.addLayout(row)
            self.sliders[label] = slider
        self.keep_exif = QtWidgets.QCheckBox('Behåll befintlig EXIF vid export (kan innehålla GPS/programnamn)')
        iv.addWidget(self.keep_exif)
        iv.addStretch()

        date_tab = QtWidgets.QWidget()
        self.tabs.addTab(date_tab, 'Datum & EXIF')
        dv = QtWidgets.QVBoxLayout(date_tab)
        self.absolute = QtWidgets.QRadioButton('Sätt samma datum på alla filer')
        self.absolute.setChecked(True)
        self.offset = QtWidgets.QRadioButton('Flytta varje fils befintliga datum')
        dv.addWidget(self.absolute)
        dv.addWidget(self.offset)
        self.date_edit = QtWidgets.QDateTimeEdit(QtCore.QDateTime.currentDateTime())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat('yyyy-MM-dd HH:mm:ss')
        dv.addWidget(self.date_edit)
        row = QtWidgets.QHBoxLayout()
        self.sign = QtWidgets.QComboBox()
        self.sign.addItems(['+ Lägg till', '− Dra ifrån'])
        row.addWidget(self.sign)
        self.offset_spins = []
        for label, maximum in [('dagar', 9999), ('timmar', 23), ('minuter', 59), ('sekunder', 59)]:
            spin = QtWidgets.QSpinBox()
            spin.setRange(0, maximum)
            spin.setSuffix(' ' + label)
            row.addWidget(spin)
            self.offset_spins.append(spin)
        dv.addLayout(row)
        self.meta = QtWidgets.QCheckBox('Ändra EXIF/video-datum')
        self.meta.setChecked(True)
        self.fs = QtWidgets.QCheckBox('Ändra filens tidsstämpel (skapad där det stöds)')
        self.fs.setChecked(True)
        self.strip = QtWidgets.QCheckBox('Ta bort programnamn i metadata')
        self.strip.setChecked(True)
        self.remove_all = QtWidgets.QCheckBox('Radera ALL befintlig EXIF/metadata (datum skrivs tillbaka om valt)')
        for box in (self.meta, self.fs, self.strip, self.remove_all):
            dv.addWidget(box)
        dv.addWidget(QtWidgets.QLabel('ExifTool rekommenderas för HEIC, PNG, RAW och video. Utan det krävs piexif för JPEG/TIFF.'))
        dv.addStretch()

        common = QtWidgets.QGroupBox('Filer och arkiv (originalen ändras aldrig)')
        main.addWidget(common)
        form = QtWidgets.QGridLayout(common)
        self.source = DropEdit()
        self.source.setPlaceholderText('Dra en mapp hit eller välj mapp…')
        form.addWidget(QtWidgets.QLabel('Källmapp'), 0, 0)
        form.addWidget(self.source, 0, 1)
        browse = QtWidgets.QPushButton('Välj…')
        browse.clicked.connect(self.browse)
        form.addWidget(browse, 0, 2)
        self.archive = QtWidgets.QLineEdit(str(Path.home() / 'Ändrat datum'))
        form.addWidget(QtWidgets.QLabel('Arkivmapp'), 1, 0)
        form.addWidget(self.archive, 1, 1)
        dest = QtWidgets.QPushButton('Välj…')
        dest.clicked.connect(self.browse_archive)
        form.addWidget(dest, 1, 2)
        self.recursive = QtWidgets.QCheckBox('Undermappar')
        self.recursive.setChecked(True)
        self.structure = QtWidgets.QCheckBox('Bevara mappstruktur')
        self.structure.setChecked(True)
        self.overwrite = QtWidgets.QCheckBox('Skriv över arkivfiler')
        for x, box in enumerate((self.recursive, self.structure, self.overwrite)):
            form.addWidget(box, 2, x)
        buttons = QtWidgets.QHBoxLayout()
        main.addLayout(buttons)
        theme = QtWidgets.QPushButton('Ljust/mörkt tema')
        theme.clicked.connect(self.toggle_theme)
        buttons.addWidget(theme)
        export = QtWidgets.QPushButton('Exportera logg')
        export.clicked.connect(self.export_log)
        buttons.addWidget(export)
        buttons.addStretch()
        self.go = QtWidgets.QPushButton('Bearbeta kopior')
        self.go.clicked.connect(self.start)
        buttons.addWidget(self.go)
        self.stop = QtWidgets.QPushButton('Avbryt')
        self.stop.setEnabled(False)
        self.stop.clicked.connect(self.cancel)
        buttons.addWidget(self.stop)
        self.progress = QtWidgets.QProgressBar()
        main.addWidget(self.progress)
        self.log = QtWidgets.QPlainTextEdit()
        self.log.setReadOnly(True)
        main.addWidget(self.log, 1)
        for index in range(self.tabs.count()):
            self.tabs.setTabIcon(index, self.brand)
        self.autostart = QtWidgets.QCheckBox('Starta automatiskt vid inloggning')
        self.autostart.setChecked(autostart_enabled())
        self.autostart.toggled.connect(self.change_autostart)
        main.addWidget(self.autostart)
        for button in self.findChildren(QtWidgets.QPushButton):
            button.setIcon(self.brand)
            button.setIconSize(QtCore.QSize(16, 16))
            button.clicked.connect(lambda checked=False, b=button: LOGGER.info('Knapp: %s', b.text()))
        self.toggle_theme()
        LOGGER.info('Fönstret öppnat; loggfil: %s', LOG_FILE)

    def build_log_tab(self):
        tab = QtWidgets.QWidget()
        self.tabs.addTab(tab, 'Aktivitetslogg')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Händelser från alla flikar sparas också automatiskt till en roterande loggfil.'))
        self.activity_log = QtWidgets.QPlainTextEdit()
        self.activity_log.setReadOnly(True)
        self.activity_log.document().setMaximumBlockCount(3000)
        layout.addWidget(self.activity_log)
        layout.addWidget(QtWidgets.QLabel(f'Loggfil: {LOG_FILE}'))
        export = QtWidgets.QPushButton('Exportera hela loggen…')
        export.clicked.connect(self.export_log)
        layout.addWidget(export)

    def append_activity_log(self, text):
        if hasattr(self, 'activity_log'):
            self.activity_log.appendPlainText(text)

    def record(self, text):
        if text.startswith(('FEL', 'BILDFEL', 'ANNONSFEL', 'KONVERTERINGSFEL')) or 'DELVIS' in text:
            LOGGER.error(text)
        else:
            LOGGER.info(text)

    def change_autostart(self, enabled):
        try:
            set_autostart(enabled)
            LOGGER.info('Autostart: %s', 'på' if enabled else 'av')
        except Exception as exc:
            LOGGER.exception('Autostart kunde inte ändras')
            self.autostart.blockSignals(True)
            self.autostart.setChecked(not enabled)
            self.autostart.blockSignals(False)
            QtWidgets.QMessageBox.warning(self, 'Autostart kunde inte ändras', str(exc))

    def offer_missing_dependencies(self):
        import importlib.util
        missing = [name for module, name in [('pillow_heif', 'pillow-heif'), ('piexif', 'piexif')] if importlib.util.find_spec(module) is None]
        if missing:
            reply = QtWidgets.QMessageBox.question(self, 'Saknade tillägg', 'Vill du installera saknade frivilliga Python-tillägg?\n' + ', '.join(missing) + '\nIngenting installeras utan ditt godkännande.')
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.install_packages(missing)

    def manage_dependencies(self):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle('Python-tillägg')
        dialog.setText('Installera/uppdatera Pillow, pillow-heif och piexif?\nDetta använder samma Python-miljö som appen.\nPyQt6 uppdateras inte medan appen körs; uppdatera det efter att appen stängts.')
        dialog.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        if dialog.exec() == QtWidgets.QMessageBox.StandardButton.Yes:
            self.install_packages(['Pillow', 'pillow-heif', 'piexif'])

    def install_packages(self, packages):
        if getattr(self, 'pip_worker', None) and self.pip_worker.isRunning():
            return
        self.deps_button.setEnabled(False)
        LOGGER.info('Installation/uppdatering startad: %s', ', '.join(packages))
        self.pip_worker = PipWorker(packages)
        self.pip_worker.finished_install.connect(self.install_finished)
        self.pip_worker.start()

    def install_finished(self, ok, output):
        self.deps_button.setEnabled(True)
        LOGGER.info('Pip-resultat: %s; %s', 'lyckades' if ok else 'misslyckades', output[-1000:])
        QtWidgets.QMessageBox.information(self, 'Installation' if ok else 'Installationsfel', ('Klart. Starta om appen för att aktivera tilläggen.\n\n' if ok else 'Installationen misslyckades.\n\n') + output)

    def build_web_tab(self):
        tab = QtWidgets.QWidget()
        self.tabs.addTab(tab, 'Webbbilder → JPEG')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Direkta HTTPS-länkar till bildfiler. En länk per rad; stöder JPG, PNG, WEBP, AVIF och HEIC.'))
        self.web_urls = QtWidgets.QPlainTextEdit()
        self.web_urls.setPlaceholderText('https://www.wermlandopera.com/wp-content/smush-webp/2026/05/wo_doing_toppbild_2000x670.jpg.webp')
        layout.addWidget(self.web_urls)
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        row.addWidget(QtWidgets.QLabel('Basmapp:'))
        self.web_destination = QtWidgets.QLineEdit(str(Path(__file__).resolve().parent / 'out'))
        row.addWidget(self.web_destination)
        browse = QtWidgets.QPushButton('Välj mapp…')
        browse.clicked.connect(self.browse_web_destination)
        row.addWidget(browse)
        layout.addWidget(QtWidgets.QLabel('Bilderna sparas som JPEG i undermappen “Direkta bilder” i vald basmapp.'))
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        row.addWidget(QtWidgets.QLabel('JPEG-kvalitet'))
        self.web_quality = QtWidgets.QSpinBox()
        self.web_quality.setRange(50, 100)
        self.web_quality.setValue(95)
        row.addWidget(self.web_quality)
        row.addStretch()
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        self.web_go = QtWidgets.QPushButton('Hämta webbbilder som JPEG')
        self.web_go.clicked.connect(self.start_web_download)
        row.addWidget(self.web_go)
        self.web_stop = QtWidgets.QPushButton('Avbryt')
        self.web_stop.setEnabled(False)
        self.web_stop.clicked.connect(self.cancel_web_download)
        row.addWidget(self.web_stop)
        self.web_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.web_progress)
        self.web_log = QtWidgets.QPlainTextEdit()
        self.web_log.setReadOnly(True)
        layout.addWidget(self.web_log)
        self.web_worker = None

    def browse_web_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Välj basmapp för webbbilder')
        if path:
            self.web_destination.setText(path)

    def start_web_download(self):
        import re
        from urllib.parse import urlparse
        if self.web_worker and self.web_worker.isRunning():
            return
        urls = list(dict.fromkeys(x.strip() for x in self.web_urls.toPlainText().splitlines() if x.strip()))
        if not urls or not self.web_destination.text().strip():
            QtWidgets.QMessageBox.information(self, 'Välj länkar', 'Ange bildlänkar och en basmapp.')
            return
        if any(urlparse(u).scheme != 'https' or not urlparse(u).path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.avif', '.heic')) or re.search(r'blocket\.se/(?:mobility|recommerce)/item/', u) for u in urls):
            QtWidgets.QMessageBox.warning(self, 'Fel länkar', 'Använd direkta HTTPS-bildlänkar här. Blocket-annonser hör hemma i Blocket-fliken.')
            return
        self.web_worker = BlocketWorker(urls, Path(self.web_destination.text()).expanduser(), self.web_quality.value())
        self.web_worker.message.connect(self.web_log.appendPlainText)
        self.web_worker.message.connect(self.record)
        self.web_worker.progress.connect(lambda done, total: (self.web_progress.setMaximum(total), self.web_progress.setValue(done)))
        self.web_worker.finished.connect(self.web_finished)
        self.web_progress.setValue(0)
        self.web_go.setEnabled(False)
        self.web_stop.setEnabled(True)
        LOGGER.info('Webbbilder startade: %d länkar till %s', len(urls), self.web_destination.text())
        self.web_worker.start()

    def cancel_web_download(self):
        if self.web_worker:
            self.web_worker.cancelled = True
            self.web_stop.setEnabled(False)
            LOGGER.info('Webbbilder: avbrott begärt')

    def web_finished(self):
        self.web_go.setEnabled(True)
        self.web_stop.setEnabled(False)
        count = self.web_worker.saved_count
        if count:
            if not self.web_worker.cancelled and not self.web_worker.error_count:
                self.web_urls.clear()
            self.open_output_folder(self.web_worker.destination / 'Direkta bilder')
        self.web_log.appendPlainText(f'Hämtning avslutad: {count} bilder sparade.')
        LOGGER.info('Webbbilder: %d bilder sparade, %d fel', count, self.web_worker.error_count)

    def build_blocket_tab(self):
        tab = QtWidgets.QWidget()
        self.tabs.addTab(tab, 'Blocket → JPEG')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Klistra in Blocket-annonser från /mobility/item/ eller /recommerce/forsale/item/, en per rad. Varje annons får en mapp med sin titel.'))
        self.ad_urls = QtWidgets.QPlainTextEdit()
        self.ad_urls.setPlaceholderText('https://www.blocket.se/mobility/item/24141675\nhttps://www.blocket.se/recommerce/forsale/item/27022380')
        layout.addWidget(self.ad_urls)
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        row.addWidget(QtWidgets.QLabel('Spara i:'))
        self.ad_destination = QtWidgets.QLineEdit(str(Path(__file__).resolve().parent / 'out'))
        self.ad_destination.setPlaceholderText('Välj en basmapp; varje annons får en undermapp med sin titel')
        row.addWidget(self.ad_destination)
        browse = QtWidgets.QPushButton('Välj mapp…')
        browse.clicked.connect(self.browse_ad_destination)
        row.addWidget(browse)
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        row.addWidget(QtWidgets.QLabel('JPEG-kvalitet'))
        self.ad_quality = QtWidgets.QSpinBox()
        self.ad_quality.setRange(50, 100)
        self.ad_quality.setValue(95)
        row.addWidget(self.ad_quality)
        row.addStretch()
        layout.addWidget(QtWidgets.QLabel('Använd bara bilder du har rätt att spara/använda. Ingen inloggning eller åtkomstspärr kringgås.'))
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        self.ad_go = QtWidgets.QPushButton('Hämta alla galleribilder som JPEG')
        self.ad_go.clicked.connect(self.start_ad_download)
        row.addWidget(self.ad_go)
        self.ad_stop = QtWidgets.QPushButton('Avbryt')
        self.ad_stop.setEnabled(False)
        self.ad_stop.clicked.connect(self.cancel_ad_download)
        row.addWidget(self.ad_stop)
        self.ad_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.ad_progress)
        self.ad_log = QtWidgets.QPlainTextEdit()
        self.ad_log.setReadOnly(True)
        layout.addWidget(self.ad_log)
        self.ad_worker = None

    def browse_ad_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Välj bildmapp')
        if path:
            self.ad_destination.setText(path)

    def start_ad_download(self):
        if self.ad_worker and self.ad_worker.isRunning():
            return
        urls = list(dict.fromkeys(x.strip() for x in self.ad_urls.toPlainText().splitlines() if x.strip()))
        if not urls:
            QtWidgets.QMessageBox.information(self, 'Ange länkar', 'Ange minst en annonslänk.')
            return
        import re
        if any(not re.fullmatch(r'https://(?:www\.)?blocket\.se/(?:mobility|recommerce/forsale)/item/\d+(?:[/?#].*)?', u) for u in urls):
            QtWidgets.QMessageBox.warning(self, 'Fel länkar', 'Använd Blocket-annonslänkar här. Direkta bilder hör hemma i Webbbilder-fliken.')
            return
        if not self.ad_destination.text().strip():
            self.browse_ad_destination()
            if not self.ad_destination.text().strip():
                return
        self.ad_worker = BlocketWorker(urls, Path(self.ad_destination.text()).expanduser(), self.ad_quality.value())
        self.ad_worker.message.connect(self.ad_log.appendPlainText)
        self.ad_worker.message.connect(self.record)
        self.ad_worker.progress.connect(lambda done, total: (self.ad_progress.setMaximum(total), self.ad_progress.setValue(done)))
        self.ad_worker.finished.connect(self.ad_finished)
        self.ad_progress.setValue(0)
        self.ad_go.setEnabled(False)
        self.ad_stop.setEnabled(True)
        LOGGER.info('Annonsnedladdning startad: %d länkar till %s', len(urls), self.ad_destination.text())
        self.ad_worker.start()

    def cancel_ad_download(self):
        if self.ad_worker:
            self.ad_worker.cancelled = True
            LOGGER.info('Annonsnedladdning: avbrott begärt')
            self.ad_stop.setEnabled(False)

    def ad_finished(self):
        self.ad_go.setEnabled(True)
        self.ad_stop.setEnabled(False)
        count = self.ad_worker.saved_count
        if count:
            if not self.ad_worker.cancelled and not self.ad_worker.error_count:
                self.ad_urls.clear()
            folders = self.ad_worker.saved_folders
            self.open_output_folder(next(iter(folders)) if len(folders) == 1 else self.ad_worker.destination)
        self.ad_log.appendPlainText(f'Nedladdning avslutad: {count} bilder sparade.')
        LOGGER.info('Annonsnedladdning: %d bilder sparade, %d fel', count, self.ad_worker.error_count)

    def open_output_folder(self, folder):
        if not QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(folder.resolve()))):
            LOGGER.warning('Kunde inte öppna output-mapp: %s', folder)
            QtWidgets.QMessageBox.warning(self, 'Kunde inte öppna mappen', f'Bilderna sparades i: {folder}')
        else:
            LOGGER.info('Output-mapp öppnad: %s', folder)

    def build_conversion_tab(self):
        tab = QtWidgets.QWidget()
        self.tabs.addTab(tab, 'AVIF/HEIC → JPEG')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Konvertera AVIF, HEIC och HEIF till JPEG. Originalfilerna sparas oförändrade.'))
        self.conversion_list = QtWidgets.QListWidget()
        layout.addWidget(self.conversion_list, 1)
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        add = QtWidgets.QPushButton('Lägg till bilder…')
        add.clicked.connect(self.add_conversion_files)
        row.addWidget(add)
        clear = QtWidgets.QPushButton('Rensa listan')
        clear.clicked.connect(self.conversion_list.clear)
        row.addWidget(clear)
        layout.addWidget(QtWidgets.QLabel('Spara JPEG-kopior i:'))
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        self.conversion_destination = QtWidgets.QLineEdit(str(Path.home() / 'Konverterade JPEG'))
        row.addWidget(self.conversion_destination)
        browse = QtWidgets.QPushButton('Välj mapp…')
        browse.clicked.connect(self.browse_conversion_destination)
        row.addWidget(browse)
        quality_row = QtWidgets.QHBoxLayout()
        layout.addLayout(quality_row)
        quality_row.addWidget(QtWidgets.QLabel('JPEG-kvalitet'))
        self.jpeg_quality = QtWidgets.QSpinBox()
        self.jpeg_quality.setRange(50, 100)
        self.jpeg_quality.setValue(95)
        quality_row.addWidget(self.jpeg_quality)
        quality_row.addStretch()
        self.conversion_metadata = QtWidgets.QCheckBox('Bevara EXIF och färgprofil (kan innehålla GPS)')
        layout.addWidget(self.conversion_metadata)
        layout.addWidget(QtWidgets.QLabel('Genomskinliga områden får vit bakgrund. Samma filnamn får automatiskt nytt löpnummer.'))
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        self.convert_button = QtWidgets.QPushButton('Konvertera till JPEG')
        self.convert_button.clicked.connect(self.start_conversion)
        row.addWidget(self.convert_button)
        self.cancel_conversion_button = QtWidgets.QPushButton('Avbryt konvertering')
        self.cancel_conversion_button.setEnabled(False)
        self.cancel_conversion_button.clicked.connect(self.cancel_conversion)
        row.addWidget(self.cancel_conversion_button)
        self.conversion_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.conversion_progress)
        self.conversion_log = QtWidgets.QPlainTextEdit()
        self.conversion_log.setReadOnly(True)
        layout.addWidget(self.conversion_log)
        self.conversion_worker = None

    def add_conversion_files(self):
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, 'Välj AVIF/HEIC-bilder', '', 'AVIF/HEIC (*.avif *.heic *.heif)')
        existing = {self.conversion_list.item(i).text() for i in range(self.conversion_list.count())}
        for path in paths:
            if path not in existing:
                self.conversion_list.addItem(path)

    def browse_conversion_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Välj JPEG-mapp')
        if path:
            self.conversion_destination.setText(path)

    def start_conversion(self):
        if self.conversion_worker and self.conversion_worker.isRunning():
            return
        files = [Path(self.conversion_list.item(i).text()) for i in range(self.conversion_list.count())]
        if not files or not self.conversion_destination.text().strip():
            QtWidgets.QMessageBox.information(self, 'Välj bilder', 'Välj bilder och målmapp först.')
            return
        self.conversion_worker = ConversionWorker(files, Path(self.conversion_destination.text()).expanduser(), self.jpeg_quality.value(), self.conversion_metadata.isChecked())
        self.conversion_worker.message.connect(self.conversion_log.appendPlainText)
        self.conversion_worker.message.connect(self.record)
        self.conversion_worker.progress.connect(lambda done, total: (self.conversion_progress.setMaximum(total), self.conversion_progress.setValue(done)))
        self.conversion_worker.finished.connect(self.conversion_finished)
        self.conversion_progress.setValue(0)
        self.convert_button.setEnabled(False)
        self.cancel_conversion_button.setEnabled(True)
        LOGGER.info('Konvertering startad: %d bilder till %s', len(files), self.conversion_destination.text())
        self.conversion_worker.start()

    def cancel_conversion(self):
        if self.conversion_worker:
            self.conversion_worker.cancelled = True
            LOGGER.info('Konvertering: avbrott begärt')
            self.cancel_conversion_button.setEnabled(False)

    def conversion_finished(self):
        self.convert_button.setEnabled(True)
        self.cancel_conversion_button.setEnabled(False)
        self.conversion_log.appendPlainText('Konverteringen avslutad.')
        LOGGER.info('Konvertering avslutad')

    def build_editor_tab(self):
        tab = QtWidgets.QWidget()
        self.tabs.addTab(tab, 'Fotoredigerare')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Öppna ett foto. Dra över förhandsvisningen för att markera ett område att klippa ut.'))
        self.canvas = PhotoCanvas()
        layout.addWidget(self.canvas, 1)
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        for text, action in [('Öppna foto…', self.open_editor), ('↶ Rotera vänster', lambda: self.rotate_editor(90)), ('↷ Rotera höger', lambda: self.rotate_editor(-90)), ('Klipp markering', self.crop_editor), ('Ångra', self.undo_editor), ('Spara kopia…', self.save_editor)]:
            button = QtWidgets.QPushButton(text)
            button.clicked.connect(action)
            row.addWidget(button)
        layout.addWidget(QtWidgets.QLabel('Spara kopia använder förstoring, skärpa, färg och klarhet från fliken Bildförbättring. Originalet påverkas inte.'))

    def show_editor_image(self):
        self.canvas.set_image(self.editor_image)

    def open_editor(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Öppna foto', '', 'Bilder (*.jpg *.jpeg *.png *.webp *.tif *.tiff *.bmp)')
        if not path:
            return
        try:
            with Image.open(path) as source:
                self.editor_image = ImageOps.exif_transpose(source).copy()
            self.editor_source = Path(path)
            self.editor_history.clear()
            self.show_editor_image()
            self.log.appendPlainText(f'Öppnade foto: {path}')
            LOGGER.info('Fotoredigerare öppnade: %s', path)
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, 'Fel', str(exc))

    def rotate_editor(self, angle):
        if self.editor_image is None:
            return
        self.editor_history.append(self.editor_image)
        self.editor_image = self.editor_image.rotate(angle, expand=True)
        LOGGER.info('Foto roterat %s grader: %s', angle, self.editor_source)
        self.show_editor_image()

    def crop_editor(self):
        if self.editor_image is None:
            return
        box = self.canvas.crop_box()
        if box is None:
            QtWidgets.QMessageBox.information(self, 'Klipp', 'Dra en tydlig markering på bilden först.')
            return
        self.editor_history.append(self.editor_image)
        self.editor_image = self.editor_image.crop(box)
        LOGGER.info('Foto beskuret: %s, område %s', self.editor_source, box)
        self.show_editor_image()

    def undo_editor(self):
        if self.editor_history:
            self.editor_image = self.editor_history.pop()
            LOGGER.info('Ångra fotoredigering: %s', self.editor_source)
            self.show_editor_image()

    def save_editor(self):
        if self.editor_image is None:
            QtWidgets.QMessageBox.information(self, 'Välj foto', 'Öppna ett foto först.')
            return
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Spara redigerad kopia', str(self.editor_source.with_name(self.editor_source.stem + '_redigerad.png')), 'PNG (*.png);;JPEG (*.jpg);;WEBP (*.webp)')
        if not path:
            return
        target = Path(path)
        if target.resolve() == self.editor_source.resolve():
            QtWidgets.QMessageBox.warning(self, 'Original', 'Välj ett annat filnamn så originalet inte skrivs över.')
            return
        if target.suffix.lower() not in {'.png', '.jpg', '.webp'}:
            target = target.with_suffix('.png')
        if target.exists() and QtWidgets.QMessageBox.question(self, 'Skriv över?', f'Skriva över {target}?') != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            # Save the current crop/rotation to an in-memory buffer, then use the same
            # enhancement pipeline as batch mode. No temporary file is created.
            import io
            buffer = io.BytesIO()
            self.editor_image.save(buffer, format='PNG')
            buffer.seek(0)
            enhance(buffer, target, self.factor.currentIndex() + 1, self.sliders['Skärpa'].value(), self.sliders['Färgstyrka'].value(), self.sliders['Klarhet/kontrast'].value(), False)
            self.log.appendPlainText(f'Redigerad kopia sparad: {target}')
            LOGGER.info('Redigerad kopia sparad: %s', target)
            QtWidgets.QMessageBox.information(self, 'Klart', f'Sparad: {target}')
        except Exception as exc:
            QtWidgets.QMessageBox.warning(self, 'Fel', str(exc))

    def toggle_theme(self):
        self.dark = not self.dark
        if self.dark:
            c = dict(bg='#101726', panel='#192439', field='#243147', border='#394b65', text='#f2f6fd', muted='#a3b5ce', accent='#3b82f6', hover='#2563eb')
        else:
            c = dict(bg='#f1f5fb', panel='#ffffff', field='#f8fafc', border='#cbd5e1', text='#182437', muted='#52637d', accent='#2563eb', hover='#1d4ed8')
        self.setStyleSheet('''
            QMainWindow, QWidget {background:%(bg)s; color:%(text)s; font-family:"Segoe UI",Arial,sans-serif; font-size:12px}
            QLabel#heroTitle {font-size:25px; font-weight:800; color:%(text)s}
            QLabel#subtitle {font-size:13px; color:%(muted)s}
            QTabWidget::pane, QGroupBox {border:1px solid %(border)s; border-radius:10px; background:%(panel)s}
            QGroupBox {font-weight:700; margin-top:12px; padding:12px}
            QGroupBox::title {subcontrol-origin:margin; left:15px; padding:0 6px}
            QTabBar::tab {background:%(panel)s; color:%(muted)s; border:1px solid %(border)s; padding:9px 13px; margin-right:3px; border-top-left-radius:7px; border-top-right-radius:7px}
            QTabBar::tab:selected {background:%(accent)s; color:white; font-weight:700}
            QLineEdit,QPlainTextEdit,QListWidget,QDateTimeEdit,QSpinBox,QComboBox {background:%(field)s; color:%(text)s; border:1px solid %(border)s; border-radius:6px; padding:6px; selection-background-color:%(accent)s}
            QLineEdit:focus,QPlainTextEdit:focus {border:2px solid %(accent)s}
            QPushButton {background:%(accent)s; color:white; border:0; border-radius:7px; padding:7px 11px; font-weight:600; min-height:20px}
            QPushButton:hover {background:%(hover)s}
            QPushButton:disabled {background:%(border)s; color:%(muted)s}
            QProgressBar {background:%(field)s; border:1px solid %(border)s; border-radius:5px; text-align:center; min-height:15px}
            QProgressBar::chunk {background:%(accent)s; border-radius:4px}
            QCheckBox {spacing:8px}
        ''' % c)

    def browse(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Välj källmapp')
        if path:
            self.source.setText(path)

    def browse_archive(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, 'Välj arkivmapp')
        if path:
            self.archive.setText(path)

    def export_log(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Spara logg', 'fotoverktyg_logg.txt', 'Text (*.txt)')
        if path:
            try:
                for h in LOGGER.handlers:
                    h.flush()
                parts = [f.read_text(encoding='utf-8') for f in [Path(str(LOG_FILE) + f'.{n}') for n in (3, 2, 1)] + [LOG_FILE] if f.exists()]
                content = '\n'.join(parts) if parts else self.activity_log.toPlainText()
                Path(path).write_text(content, encoding='utf-8')
                LOGGER.info('Logg exporterad: %s', path)
            except Exception as exc:
                LOGGER.exception('Loggexport misslyckades')
                QtWidgets.QMessageBox.warning(self, 'Loggfel', str(exc))

    def start(self):
        if self.worker and self.worker.isRunning():
            return
        root, archive = Path(self.source.text()).expanduser().resolve(), Path(self.archive.text()).expanduser().resolve()
        if not self.source.text() or not root.is_dir() or not self.archive.text():
            QtWidgets.QMessageBox.warning(self, 'Fel', 'Välj en giltig källmapp och arkivmapp.')
            return
        if root == archive or (root in archive.parents and not self.recursive.isChecked()):
            if root == archive:
                QtWidgets.QMessageBox.warning(self, 'Fel', 'Arkivmappen måste skilja sig från källmappen.')
                return
        candidates = root.rglob('*') if self.recursive.isChecked() else root.iterdir()
        items = sorted(p for p in candidates if p.is_file() and p.suffix.lower() in MEDIA and archive not in (p, *p.parents) and not any(part.startswith('.') for part in p.relative_to(root).parts))
        if not items:
            QtWidgets.QMessageBox.information(self, 'Inga filer', 'Inga bilder eller videor hittades.')
            return
        days, hours, minutes, seconds = [spin.value() for spin in self.offset_spins]
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        if self.sign.currentIndex():
            delta = -delta
        settings = dict(root=root, archive=archive, structure=self.structure.isChecked(), overwrite=self.overwrite.isChecked(), enhance=self.enhance_box.isChecked(), factor=self.factor.currentIndex()+1, sharp=self.sliders['Skärpa'].value(), color=self.sliders['Färgstyrka'].value(), clarity=self.sliders['Klarhet/kontrast'].value(), keep_exif=self.keep_exif.isChecked(), offset=self.offset.isChecked(), delta=delta, date=self.date_edit.dateTime().toPyDateTime(), metadata=self.meta.isChecked(), filesystem=self.fs.isChecked(), strip=self.strip.isChecked(), remove_all=self.remove_all.isChecked())
        self.worker = Worker(items, settings)
        self.worker.message.connect(self.log.appendPlainText)
        self.worker.message.connect(self.record)
        self.worker.progress.connect(lambda done, total: (self.progress.setMaximum(total), self.progress.setValue(done)))
        self.worker.completed.connect(self.finished)
        self.go.setEnabled(False)
        self.stop.setEnabled(True)
        self.progress.setValue(0)
        self.log.appendPlainText(f'Bearbetar {len(items)} filer → {archive}')
        LOGGER.info('Mappbearbetning startad: %d filer från %s', len(items), root)
        self.worker.start()

    def cancel(self):
        if self.worker:
            self.worker.cancelled = True
            LOGGER.info('Mappbearbetning: avbrott begärt')
            self.stop.setEnabled(False)

    def finished(self):
        self.go.setEnabled(True)
        self.stop.setEnabled(False)
        self.log.appendPlainText('Bearbetningen avslutad. Kontrollera eventuella DELVIS/FEL ovan.')
        LOGGER.info('Mappbearbetning avslutad')

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.cancel()
            self.worker.wait()
        if self.conversion_worker and self.conversion_worker.isRunning():
            self.cancel_conversion()
            self.conversion_worker.wait()
        if self.ad_worker and self.ad_worker.isRunning():
            self.cancel_ad_download()
            self.ad_worker.wait()
        if self.web_worker and self.web_worker.isRunning():
            self.cancel_web_download()
            self.web_worker.wait()
        if getattr(self, 'pip_worker', None) and self.pip_worker.isRunning():
            self.pip_worker.wait()
        LOGGER.info('Applikationen stängs')
        LOGGER.removeHandler(self.qt_log_handler)
        event.accept()


if __name__ == '__main__':
    def log_uncaught(exc_type, exc_value, exc_tb):
        LOGGER.critical('Ohanterat fel', exc_info=(exc_type, exc_value, exc_tb))
        QtWidgets.QMessageBox.critical(None, 'Fotoverktyg - fel', f'{exc_value}\n\nSe loggen: {LOG_FILE}')
    sys.excepthook = log_uncaught
    app = QtWidgets.QApplication(sys.argv)
    icon_file = Path(__file__).resolve().with_name('fotoverktyg_icon.png')
    app.setWindowIcon(QtGui.QIcon(str(icon_file)) if icon_file.exists() else brand_icon())
    window = Window()
    window.show()
    sys.exit(app.exec())
