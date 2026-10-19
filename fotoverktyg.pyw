#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MediaForge: photo and video tools for editing, conversion, and metadata."""
import os
import shutil
import subprocess
import sys
import csv
import json
import hashlib
from fractions import Fraction
from datetime import datetime, timedelta
from pathlib import Path

import logging
from logging.handlers import RotatingFileHandler

APP_DIR = Path(__file__).resolve().parent
APP_DATA_DIR = APP_DIR / 'MediaForge_Data'
OUTPUT_DIR = APP_DATA_DIR / 'Output'
SETTINGS_DIR = APP_DATA_DIR / 'Settings'
LOG_DIR = APP_DATA_DIR / 'Logs'
LOG_FILE = LOG_DIR / 'mediaforge.log'
SETTINGS_FILE = SETTINGS_DIR / 'preferences.ini'
UPDATE_REMOTE_URL = 'https://github.com/Tokke2/MediaConverterPro.git'
UPDATE_BRANCH = 'main'



def is_app_owned_path(path):
    try:
        candidate = Path(path).expanduser().resolve(strict=False)
        relative = candidate.relative_to(APP_DIR)
        return bool(relative.parts)
    except (OSError, ValueError, TypeError):
        return False
LOGGER = logging.getLogger('fotoverktyg')
LOGGER.setLevel(logging.INFO)
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=5_000_000, backupCount=3, encoding='utf-8')
    handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-7s | %(threadName)s | %(message)s'))
    LOGGER.addHandler(handler)
except OSError:
    LOGGER.addHandler(logging.NullHandler())
LOGGER.info('Applikationen startar')

from PyQt6 import QtCore, QtGui, QtWidgets, QtPrintSupport
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

Image.MAX_IMAGE_PIXELS = 150_000_000
PHOTO = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp'}
MEDIA = PHOTO | {'.heic', '.heif', '.dng', '.cr2', '.cr3', '.nef', '.arw', '.raf', '.orf', '.rw2', '.mp4', '.mov', '.m4v', '.avi', '.mkv', '.mts', '.m2ts', '.ts', '.webm', '.wmv', '.3gp', '.mpeg', '.mpg', '.mxf', '.gif'}
VIDEO = {'.mp4', '.mov', '.m4v', '.avi', '.mkv', '.mts', '.m2ts', '.ts', '.webm', '.wmv', '.3gp', '.mpeg', '.mpg', '.mxf'}
AUDIO_FILE_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus', '.wma', '.aiff', '.aif'}
IMAGE_COLOR_PROFILES = {'sRGB': 'SRgb', 'Display P3': 'DisplayP3', 'Adobe RGB (1998)': 'AdobeRgb'}
UI_TRANSLATIONS = {'MEDIAFORGE': 'MEDIAFORGE',
 'Photo & Video Toolkit · Ett komplett arbetsflöde för foto och video – originalen förblir orörda.': 'Photo '
                                                                                                     '& '
                                                                                                     'Video '
                                                                                                     'Toolkit '
                                                                                                     '· A '
                                                                                                     'complete '
                                                                                                     'workflow '
                                                                                                     'for '
                                                                                                     'photos '
                                                                                                     'and '
                                                                                                     'video; '
                                                                                                     'originals '
                                                                                                     'stay '
                                                                                                     'untouched.',
 'Visa flikar:': 'Show tabs:',
 'Alla': 'All',
 'Foto': 'Photo',
 'Video': 'Video',
 'Språk:': 'Language:',
 'Svenska': 'Swedish',
 'Engelska': 'English',
 'Bildförbättring': 'Photo enhancement',
 'Datum & EXIF': 'Date & EXIF',
 'Bildoptimering': 'Image optimization',
 'Videokonvertering': 'Video conversion',
 'Skapa musik-DVD': 'Create music DVD',
 'Aktivitetslogg': 'Activity log',
 'Webbbilder → JPEG': 'Web images → JPEG',
 'Blocket → JPEG': 'Blocket → JPEG',
 'AVIF/HEIC → JPEG': 'AVIF/HEIC → JPEG',
 'Fotoredigerare': 'Photo editor',
 'Kontrollera/installera Python-tillägg…': 'Check/install Python packages…',
 'Installera/uppdatera senaste Python…': 'Install/update latest Python…',
 'Uppdatera alla Python-paket (starta om)…': 'Update all Python packages (restart)…',
 'Detta stänger MediaForge och uppdaterar paketen i appens privata Python-miljö. Fortsätta?': 'This closes MediaForge and updates packages in its private Python environment. Continue?',
 'Kontrollera GitHub main-uppdatering…': 'Check for GitHub main updates…',
 'Detta stänger MediaForge och startar Python-uppdateringen. Fortsätta?': 'This will close MediaForge and start the Python update flow. Continue?',
 'Kontrollerar GitHub main efter uppdateringar…': 'Checking GitHub main for updates…',
 'MediaForge är redan uppdaterat.': 'MediaForge is already up to date.',
 'Endast en Git-arbetskopia på grenen main kan uppdateras.': 'Only a Git checkout on the main branch can be updated.',
 'Git-arbetskopian innehåller ändringar. Spara, stash:a eller återställ dem innan uppdatering.': 'The Git worktree is not clean. Commit, stash, or discard changes before updating.',
 'Uppdatering tillgänglig: {local} → {remote}. Uppdatera nu? Endast snabbspolning tillåts.': 'Update available: {local} → {remote}. Update now? Only a fast-forward update is allowed.',
 'Uppdateringen är klar. Starta om MediaForge för att använda den nya versionen.': 'Update complete. Restart MediaForge to use the updated code.',
 'Git-uppdateringen misslyckades:': 'Git update failed:',
 'Python-uppdatering' : 'Python update',
 'GitHub-uppdatering': 'GitHub update',
 'En terminalemulator krävs för att uppdatera Python på Linux. Kör start_mediaforge.sh från en terminal.': 'A terminal emulator is required to update Python on this Linux system. Run start_mediaforge.sh from a terminal.',
 'Stöd utvecklingen · Ko-fi': 'Support development · Ko-fi',
 'Ange/ändra Ko-fi-länk': 'Set/change Ko-fi link',
 'Förstora, förbättra färger och skärp foton. Video kopieras utan bildförbättring.': 'Enlarge, enhance '
                                                                                     'colors and sharpen '
                                                                                     'photos. Videos are '
                                                                                     'copied without image '
                                                                                     'enhancement.',
 'Förbättra bilder (annars kopieras de oförändrade)': 'Enhance images (otherwise copy unchanged)',
 'Förstoring': 'Scale',
 'Skärpa': 'Sharpness',
 'Färgstyrka': 'Color',
 'Klarhet/kontrast': 'Clarity/contrast',
 'Behåll befintlig EXIF vid export (kan innehålla GPS/programnamn)': 'Keep existing EXIF on export (may '
                                                                     'include GPS/software name)',
 'Sätt samma datum på alla filer': 'Set the same date for all files',
 'Flytta varje fils befintliga datum': 'Shift each file’s existing date',
 'Ändra EXIF/video-datum': 'Change EXIF/video date',
 'Ändra filens tidsstämpel (skapad där det stöds)': 'Change file timestamps (creation time where supported)',
 'Ta bort programnamn i metadata': 'Remove software name from metadata',
 'Radera ALL befintlig EXIF/metadata (datum skrivs tillbaka om valt)': 'Remove ALL existing EXIF/metadata '
                                                                       '(date is restored if selected)',
 'ExifTool rekommenderas för HEIC, PNG, RAW och video. Utan det krävs piexif för JPEG/TIFF.': 'ExifTool is '
                                                                                              'recommended '
                                                                                              'for HEIC, '
                                                                                              'PNG, RAW and '
                                                                                              'video. '
                                                                                              'Without it, '
                                                                                              'piexif is '
                                                                                              'required for '
                                                                                              'JPEG/TIFF.',
 'Filer och arkiv (originalen ändras aldrig)': 'Files and archive (originals are never changed)',
 'Källmapp': 'Source folder',
 'Arkivmapp': 'Archive folder',
 'Välj…': 'Browse…',
 'Undermappar': 'Subfolders',
 'Bevara mappstruktur': 'Preserve folder structure',
 'Skriv över arkivfiler': 'Overwrite archive files',
 'Ljust/mörkt tema': 'Light/dark theme',
 'Exportera logg': 'Export log',
 'Bearbeta kopior': 'Process copies',
 'Avbryt': 'Cancel',
 'Starta automatiskt vid inloggning': 'Start automatically at sign-in',
 'Välj mapp…': 'Choose folder…',
 'Ta med undermappar': 'Include subfolders',
 'Rensa EXIF/metadata (GPS, kameradata m.m.)': 'Remove EXIF/metadata (GPS, camera data, etc.)',
 'Bildmapp': 'Image folder',
 'Spara kopior i': 'Save copies to',
 'Importera en hel mapp och skapa optimerade kopior. Originalen ändras aldrig.': 'Import an entire folder '
                                                                                 'and create optimized '
                                                                                 'copies. Originals are '
                                                                                 'never changed.',
 'JPG kopieras utan omkodning för att bevara bildkvaliteten; PNG/TIFF optimeras förlustfritt och WEBP kodas förlustfritt.': 'JPG '
                                                                                                                            'files '
                                                                                                                            'are '
                                                                                                                            'copied '
                                                                                                                            'without '
                                                                                                                            're-encoding '
                                                                                                                            'to '
                                                                                                                            'preserve '
                                                                                                                            'quality; '
                                                                                                                            'PNG/TIFF '
                                                                                                                            'are '
                                                                                                                            'optimized '
                                                                                                                            'losslessly '
                                                                                                                            'and '
                                                                                                                            'WEBP '
                                                                                                                            'uses '
                                                                                                                            'lossless '
                                                                                                                            'encoding.',
 'OBS: För JPG bevaras den ursprungliga bildströmmen, så storleken minskar främst genom att metadata rensas. PNG/TIFF kan bli mindre genom förlustfri optimering.': 'Note: '
                                                                                                                                                                    'JPG '
                                                                                                                                                                    'image '
                                                                                                                                                                    'data '
                                                                                                                                                                    'is '
                                                                                                                                                                    'preserved, '
                                                                                                                                                                    'so '
                                                                                                                                                                    'size '
                                                                                                                                                                    'reduction '
                                                                                                                                                                    'mainly '
                                                                                                                                                                    'comes '
                                                                                                                                                                    'from '
                                                                                                                                                                    'removing '
                                                                                                                                                                    'metadata. '
                                                                                                                                                                    'PNG/TIFF '
                                                                                                                                                                    'may '
                                                                                                                                                                    'shrink '
                                                                                                                                                                    'through '
                                                                                                                                                                    'lossless '
                                                                                                                                                                    'optimization.',
 'Optimera bildmapp': 'Optimize image folder',
 'Konvertera en mapp med videor till MP4/H.264 med FFmpeg. Källfilerna lämnas orörda.': 'Convert a folder of '
                                                                                        'videos to MP4/H.264 '
                                                                                        'with FFmpeg. Source '
                                                                                        'files remain '
                                                                                        'untouched.',
 'Videomapp': 'Video folder',
 'Högsta upplösning': 'Maximum resolution',
 'Kvalitet (CRF; lägre = bättre/större)': 'Quality (CRF; lower = better/larger)',
 'Kräver FFmpeg i PATH. Kodning använder H.264/AAC och kan minska filstorlek, men är en omkodning med viss kvalitetsförlust.': 'Requires '
                                                                                                                               'FFmpeg '
                                                                                                                               'in '
                                                                                                                               'PATH. '
                                                                                                                               'H.264/AAC '
                                                                                                                               'encoding '
                                                                                                                               'can '
                                                                                                                               'reduce '
                                                                                                                               'file '
                                                                                                                               'size, '
                                                                                                                               'but '
                                                                                                                               're-encoding '
                                                                                                                               'may '
                                                                                                                               'reduce '
                                                                                                                               'quality.',
 'Konvertera videomapp till MP4': 'Convert video folder to MP4',
 'Samla musikfiler i en DVD-5-kompatibel mapp och skapa en ISO-avbildning om ett ISO-verktyg finns installerat.': 'Collect '
                                                                                                                  'music '
                                                                                                                  'files '
                                                                                                                  'in '
                                                                                                                  'a '
                                                                                                                  'DVD-5-compatible '
                                                                                                                  'folder '
                                                                                                                  'and '
                                                                                                                  'create '
                                                                                                                  'an '
                                                                                                                  'ISO '
                                                                                                                  'image '
                                                                                                                  'if '
                                                                                                                  'an '
                                                                                                                  'ISO '
                                                                                                                  'tool '
                                                                                                                  'is '
                                                                                                                  'installed.',
 'Detta är en data-DVD med musikfiler – inte en DVD-Video för alla DVD-spelare. Välj/bränn ISO som skivavbildning, eller bränn mappen som data-DVD.': 'This '
                                                                                                                                                      'is '
                                                                                                                                                      'a '
                                                                                                                                                      'data '
                                                                                                                                                      'DVD '
                                                                                                                                                      'containing '
                                                                                                                                                      'music '
                                                                                                                                                      'files, '
                                                                                                                                                      'not '
                                                                                                                                                      'a '
                                                                                                                                                      'DVD-Video '
                                                                                                                                                      'for '
                                                                                                                                                      'all '
                                                                                                                                                      'DVD '
                                                                                                                                                      'players. '
                                                                                                                                                      'Burn '
                                                                                                                                                      'the '
                                                                                                                                                      'ISO '
                                                                                                                                                      'as '
                                                                                                                                                      'a '
                                                                                                                                                      'disc '
                                                                                                                                                      'image, '
                                                                                                                                                      'or '
                                                                                                                                                      'burn '
                                                                                                                                                      'the '
                                                                                                                                                      'folder '
                                                                                                                                                      'as '
                                                                                                                                                      'a '
                                                                                                                                                      'data '
                                                                                                                                                      'DVD.',
 'Musikmapp': 'Music folder',
 'Utmatningsmapp': 'Output folder',
 'Ta med undermappar (filer samlas i skivans rot)': 'Include subfolders (files are placed in the disc root)',
 'Stödjer MP3, WAV, FLAC, M4A, AAC, OGG, OPUS, WMA och AIFF. DVD-5 rymmer cirka 4,7 GB.': 'Supports MP3, '
                                                                                          'WAV, FLAC, M4A, '
                                                                                          'AAC, OGG, OPUS, '
                                                                                          'WMA and AIFF. A '
                                                                                          'DVD-5 holds about '
                                                                                          '4.7 GB.',
 'Händelser från alla flikar sparas också automatiskt till en roterande loggfil.': 'Events from all tabs are '
                                                                                   'also saved automatically '
                                                                                   'to a rotating log file.',
 'Exportera hela loggen…': 'Export full log…',
 'Direkta HTTPS-länkar till bildfiler. En länk per rad; stöder JPG, PNG, WEBP, AVIF och HEIC.': 'Direct '
                                                                                                'HTTPS links '
                                                                                                'to image '
                                                                                                'files. One '
                                                                                                'link per '
                                                                                                'line; '
                                                                                                'supports '
                                                                                                'JPG, PNG, '
                                                                                                'WEBP, AVIF '
                                                                                                'and HEIC.',
 'Basmapp:': 'Base folder:',
 'Bilderna sparas som JPEG i undermappen “Direkta bilder” i vald basmapp.': 'Images are saved as JPEG in a '
                                                                            '“Direct images” subfolder in '
                                                                            'the selected base folder.',
 'JPEG-kvalitet': 'JPEG quality',
 'Hämta webbbilder som JPEG': 'Download web images as JPEG',
 'Klistra in Blocket-annonser från /mobility/item/ eller /recommerce/forsale/item/, en per rad. Varje annons får en mapp med sin titel.': 'Paste '
                                                                                                                                          'Blocket '
                                                                                                                                          'ad '
                                                                                                                                          'links '
                                                                                                                                          '(/mobility/item/ '
                                                                                                                                          'or '
                                                                                                                                          '/recommerce/forsale/item/), '
                                                                                                                                          'one '
                                                                                                                                          'per '
                                                                                                                                          'line. '
                                                                                                                                          'Each '
                                                                                                                                          'ad '
                                                                                                                                          'gets '
                                                                                                                                          'a '
                                                                                                                                          'folder '
                                                                                                                                          'named '
                                                                                                                                          'after '
                                                                                                                                          'its '
                                                                                                                                          'title.',
 'Spara i:': 'Save to:',
 'Använd bara bilder du har rätt att spara/använda. Ingen inloggning eller åtkomstspärr kringgås.': 'Only '
                                                                                                    'download '
                                                                                                    'images '
                                                                                                    'you '
                                                                                                    'have '
                                                                                                    'permission '
                                                                                                    'to use. '
                                                                                                    'The app '
                                                                                                    'does '
                                                                                                    'not '
                                                                                                    'bypass '
                                                                                                    'logins '
                                                                                                    'or '
                                                                                                    'access '
                                                                                                    'restrictions.',
 'Hämta alla galleribilder som JPEG': 'Download all gallery images as JPEG',
 'Lägg till bilder…': 'Add images…',
 'Rensa listan': 'Clear list',
 'Konvertera till JPEG': 'Convert to JPEG',
 'Avbryt konvertering': 'Cancel conversion',
 'Konvertera AVIF, HEIC och HEIF till JPEG. Originalfilerna sparas oförändrade.': 'Convert AVIF, HEIC and '
                                                                                  'HEIF to JPEG. Original '
                                                                                  'files remain untouched.',
 'Spara JPEG-kopior i:': 'Save JPEG copies to:',
 'Bevara EXIF och färgprofil (kan innehålla GPS)': 'Keep EXIF and color profile (may include GPS)',
 'Genomskinliga områden får vit bakgrund. Samma filnamn får automatiskt nytt löpnummer.': 'Transparent areas '
                                                                                          'get a white '
                                                                                          'background. '
                                                                                          'Duplicate '
                                                                                          'filenames receive '
                                                                                          'an automatic '
                                                                                          'number.',
 'Öppna ett foto. Dra över förhandsvisningen för att markera ett område att klippa ut.': 'Open a photo. Drag '
                                                                                         'on the preview to '
                                                                                         'select an area to '
                                                                                         'crop.',
 'Spara kopia använder förstoring, skärpa, färg och klarhet från fliken Bildförbättring. Originalet påverkas inte.': 'Save '
                                                                                                                     'Copy '
                                                                                                                     'uses '
                                                                                                                     'scale, '
                                                                                                                     'sharpness, '
                                                                                                                     'color '
                                                                                                                     'and '
                                                                                                                     'clarity '
                                                                                                                     'from '
                                                                                                                     'Photo '
                                                                                                                     'Enhancement. '
                                                                                                                     'The '
                                                                                                                     'original '
                                                                                                                     'is '
                                                                                                                     'not '
                                                                                                                     'affected.',
 'Dra en mapp hit eller välj mapp…': 'Drop a folder here or choose one…',
 'Välj mapp med bilder…': 'Choose image folder…',
 'Välj mapp med videor…': 'Choose video folder…',
 'Välj mapp med musik…': 'Choose music folder…',
 'Välj en basmapp; varje annons får en undermapp med sin titel': 'Choose a base folder; each ad gets a '
                                                                 'subfolder named after its title',
 '1× (bara färg/skärpa)': '1× (color/sharpness only)',
 '+ Lägg till': '+ Add',
 '− Dra ifrån': '− Subtract',
 'Behåll originalstorlek': 'Keep original size',
 '1080p': '1080p',
 '720p': '720p',
 'Ko-fi-donationslänk': 'Ko-fi donation link',
 'Klistra in din personliga Ko-fi-länk (https://ko-fi.com/dittnamn):': 'Enter your personal Ko-fi link '
                                                                       '(https://ko-fi.com/yourname):',
 'Välj basmapp för webbbilder': 'Choose a base folder for web images',
 'Välj bildmapp': 'Choose image folder',
 'Välj AVIF/HEIC-bilder': 'Choose AVIF/HEIC images',
 'AVIF/HEIC (*.avif *.heic *.heif)': 'AVIF/HEIC (*.avif *.heic *.heif)',
 'Välj JPEG-mapp': 'Choose JPEG folder',
 'Öppna foto': 'Open photo',
 'Bilder (*.jpg *.jpeg *.png *.webp *.tif *.tiff *.bmp)': 'Images (*.jpg *.jpeg *.png *.webp *.tif *.tiff '
                                                          '*.bmp)',
 'Spara redigerad kopia': 'Save edited copy',
 'PNG (*.png);;JPEG (*.jpg);;WEBP (*.webp)': 'PNG (*.png);;JPEG (*.jpg);;WEBP (*.webp)',
 'Välj källmapp': 'Choose source folder',
 'Välj arkivmapp': 'Choose archive folder',
 'Spara logg': 'Save log',
 'Text (*.txt)': 'Text (*.txt)',
 'Ohanterat fel': 'Unhandled error',
 'Ogiltig mapp': 'Invalid folder',
 'Välj en giltig videomapp och en separat målmapp utanför källmappen.': 'Choose a valid video folder and a '
                                                                        'separate destination outside the '
                                                                        'source folder.',
 'Välj en giltig bildmapp och en separat målmapp utanför källmappen.': 'Choose a valid image folder and a '
                                                                       'separate destination outside the '
                                                                       'source folder.',
 'Välj en giltig musikmapp och en separat utmatningsmapp utanför källmappen.': 'Choose a valid music folder '
                                                                               'and a separate output folder '
                                                                               'outside the source folder.',
 'Ogiltig länk': 'Invalid link',
 'Ange en personlig Ko-fi-länk på domänen ko-fi.com, till exempel https://ko-fi.com/dittnamn.': 'Enter a '
                                                                                                'personal '
                                                                                                'Ko-fi link '
                                                                                                'on '
                                                                                                'ko-fi.com, '
                                                                                                'for example '
                                                                                                'https://ko-fi.com/yourname.',
 'Sparat': 'Saved',
 'Din Ko-fi-länk sparades lokalt i appens inställningsmapp.': 'Your Ko-fi link was saved locally in the app '
                                                              'settings folder.',
 'Kunde inte spara': 'Could not save',
 'Saknade tillägg': 'Missing packages',
 'Vill du installera saknade frivilliga Python-tillägg?\\n': 'Install missing optional Python packages?\\n',
 'Ingenting installeras utan ditt godkännande.': 'Nothing is installed without your approval.',
 'Python-tillägg': 'Python packages',
 'Installera/uppdatera Pillow, pillow-heif och piexif?\\nDetta använder samma Python-miljö som appen.\\nPyQt6 uppdateras inte medan appen körs; uppdatera det efter att appen stängts.': 'Install/update '
                                                                                                                                                                                         'Pillow, '
                                                                                                                                                                                         'pillow-heif '
                                                                                                                                                                                         'and '
                                                                                                                                                                                         'piexif?\\nThis '
                                                                                                                                                                                         'uses '
                                                                                                                                                                                         'the '
                                                                                                                                                                                         'same '
                                                                                                                                                                                         'Python '
                                                                                                                                                                                         'environment '
                                                                                                                                                                                         'as '
                                                                                                                                                                                         'the '
                                                                                                                                                                                         'app.\\nPyQt6 '
                                                                                                                                                                                         'cannot '
                                                                                                                                                                                         'be '
                                                                                                                                                                                         'safely '
                                                                                                                                                                                         'updated '
                                                                                                                                                                                         'while '
                                                                                                                                                                                         'the '
                                                                                                                                                                                         'app '
                                                                                                                                                                                         'is '
                                                                                                                                                                                         'running; '
                                                                                                                                                                                         'update '
                                                                                                                                                                                         'it '
                                                                                                                                                                                         'after '
                                                                                                                                                                                         'closing '
                                                                                                                                                                                         'the '
                                                                                                                                                                                         'app.',
 'Välj länkar': 'Choose links',
 'Ange bildlänkar och en basmapp.': 'Enter image links and a base folder.',
 'Fel länkar': 'Invalid links',
 'Använd direkta HTTPS-bildlänkar här. Blocket-annonser hör hemma i Blocket-fliken.': 'Use direct HTTPS '
                                                                                      'image links here. '
                                                                                      'Blocket ads belong in '
                                                                                      'the Blocket tab.',
 'Ange länkar': 'Enter links',
 'Ange minst en annonslänk.': 'Enter at least one ad link.',
 'Använd Blocket-annonslänkar här. Direkta bilder hör hemma i Webbbilder-fliken.': 'Use Blocket ad links '
                                                                                   'here. Direct image links '
                                                                                   'belong in the Web Images '
                                                                                   'tab.',
 'Kunde inte öppna mappen': 'Could not open folder',
 'Välj bilder': 'Choose images',
 'Välj bilder och målmapp först.': 'Choose images and a destination folder first.',
 'Klipp': 'Crop',
 'Dra en tydlig markering på bilden först.': 'Draw a clear selection on the image first.',
 'Välj foto': 'Choose photo',
 'Öppna ett foto först.': 'Open a photo first.',
 'Original': 'Original',
 'Välj ett annat filnamn så originalet inte skrivs över.': 'Choose a different filename so the original is '
                                                           'not overwritten.',
 'Klart': 'Done',
 'Sparad:': 'Saved:',
 'Fel': 'Error',
 'Skriv över?': 'Overwrite?',
 'Välj en giltig källmapp och arkivmapp.': 'Choose a valid source folder and archive folder.',
 'Inga filer': 'No files',
 'Inga bilder eller videor hittades.': 'No images or videos were found.',
 'Arkivmappen måste skilja sig från källmappen.': 'The archive folder must be different from the source '
                                                  'folder.',
 'Loggfel': 'Log error',
 'Autostart kunde inte ändras': 'Could not change startup setting',
 'Installationsfel': 'Installation error',
 'Installation': 'Installation',
 'Klart. Starta om appen för att aktivera tilläggen.': 'Done. Restart the app to activate the packages.',
 'Installationen misslyckades.': 'Installation failed.',
 'Installera saknade frivilliga Python-tillägg?': 'Install missing optional Python packages?',
 'Vill du installera/uppdatera Pillow, pillow-heif och piexif?': 'Install/update Pillow, pillow-heif and '
                                                                 'piexif?',
 '\nDetta använder samma Python-miljö som appen.\nPyQt6 uppdateras inte medan appen körs; uppdatera det efter att appen stängts.': '\n'
                                                                                                                                   'This '
                                                                                                                                   'uses '
                                                                                                                                   'the '
                                                                                                                                   'same '
                                                                                                                                   'Python '
                                                                                                                                   'environment '
                                                                                                                                   'as '
                                                                                                                                   'the '
                                                                                                                                   'app.\n'
                                                                                                                                   'PyQt6 '
                                                                                                                                   'cannot '
                                                                                                                                   'be '
                                                                                                                                   'safely '
                                                                                                                                   'updated '
                                                                                                                                   'while '
                                                                                                                                   'the '
                                                                                                                                   'app '
                                                                                                                                   'is '
                                                                                                                                   'running; '
                                                                                                                                   'update '
                                                                                                                                   'it '
                                                                                                                                   'after '
                                                                                                                                   'closing '
                                                                                                                                   'the '
                                                                                                                                   'app.',
 'Skriv över': 'Overwrite',
 ' dagar': ' days',
 ' timmar': ' hours',
 ' minuter': ' minutes',
 ' sekunder': ' seconds',
 'Installera/uppdatera Pillow, pillow-heif och piexif?\nDetta använder samma Python-miljö som appen.\nPyQt6 uppdateras inte medan appen körs; uppdatera det efter att appen stängts.': 'Install/update '
                                                                                                                                                                                       'Pillow, '
                                                                                                                                                                                       'pillow-heif '
                                                                                                                                                                                       'and '
                                                                                                                                                                                       'piexif?\n'
                                                                                                                                                                                       'This '
                                                                                                                                                                                       'uses '
                                                                                                                                                                                       'the '
                                                                                                                                                                                       'same '
                                                                                                                                                                                       'Python '
                                                                                                                                                                                       'environment '
                                                                                                                                                                                       'as '
                                                                                                                                                                                       'the '
                                                                                                                                                                                       'app.\n'
                                                                                                                                                                                       'PyQt6 '
                                                                                                                                                                                       'cannot '
                                                                                                                                                                                       'be '
                                                                                                                                                                                       'safely '
                                                                                                                                                                                       'updated '
                                                                                                                                                                                       'while '
                                                                                                                                                                                       'the '
                                                                                                                                                                                       'app '
                                                                                                                                                                                       'is '
                                                                                                                                                                                       'running; '
                                                                                                                                                                                       'update '
                                                                                                                                                                                       'it '
                                                                                                                                                                                       'after '
                                                                                                                                                                                       'closing '
                                                                                                                                                                                       'the '
                                                                                                                                                                                       'app.',
 'Autostart is supported on Windows, macOS and Linux only.': 'Autostart stöds bara på Windows, macOS och '
                                                             'Linux.',
 'Output folder restricted': 'Output folder restricted',
 'Utdata måste sparas under MediaForge-appens mapp.': 'All generated files must be saved inside the '
                                                      'MediaForge application folder.'}


UI_TRANSLATIONS.update({
    'Dubblettfinnare': 'Duplicate finder',
    'Ljud från video': 'Audio from video',
    'Hitta identiska filer med SHA-256 och visuellt liknande bilder med perceptuell hash. Inga filer ändras under skanningen.': 'Find identical files with SHA-256 and visually similar images with perceptual hashes. No files are changed during scanning.',
    'Välj mapp att skanna…': 'Choose a folder to scan…',
    'Skanna mapp': 'Folder to scan',
    'Välj skanningsmapp': 'Choose scan folder',
    'Likhetströskel (0–20; lägre = striktare)': 'Similarity threshold (0–20; lower is stricter)',
    'Välj minst en fil att behålla i varje grupp. Omarkerade kopior flyttas till appens karantänmapp; inget raderas permanent.': 'Choose at least one file to keep in each group. Unchecked copies are moved to the app quarantine; nothing is permanently deleted.',
    'Skanna efter dubbletter': 'Scan for duplicates',
    'Avbryt skanning': 'Cancel scan',
    'Flytta omarkerade till karantän…': 'Move unchecked files to quarantine…',
    'Avbryt flytt': 'Cancel move',
    'Skannar filer…': 'Scanning files…',
    'Skanningen avbröts.': 'Scan cancelled.',
    'Hittade {groups} grupper med {files} filer.': 'Found {groups} groups with {files} files.',
    'Inga dubbletter hittades.': 'No duplicates found.',
    'Välj filer att behålla': 'Choose files to keep',
    'Markera minst en fil att behålla i varje dubblettgrupp.': 'Select at least one file to keep in every duplicate group.',
    'Inga filer valda': 'No files selected',
    'Avmarkera kopior som ska flyttas till karantän först.': 'Uncheck copies to move to quarantine first.',
    'Flytta {count} omarkerade filer till karantän under MediaForge_Data/Output/Duplicates? Filerna kan återställas manuellt därifrån.': 'Move {count} unchecked files to quarantine under MediaForge_Data/Output/Duplicates? You can restore them manually from there.',
    'Bekräfta karantänflytt': 'Confirm quarantine move',
    'Flytt till karantän klar: {moved} flyttade, {failed} fel.': 'Quarantine move finished: {moved} moved, {failed} errors.',
    'Identiska filer': 'Exact duplicate files',
    'Visuellt liknande bilder': 'Visually similar images',
    'Grupp': 'Group',
    'Behåll': 'Keep',
    'Fil': 'File',
    'Matchning': 'Match type',
    'Välj mapp med videor…': 'Choose a video folder…',
    'Spara nya filer i': 'Save new files to',
    'Ljudformat': 'Audio format',
    'Extrahera ljud från videor': 'Extract audio from videos',
    'Ta bort ljudspår och spara videokopia': 'Remove audio and save a video copy',
    'Extrahera ljud till MP3, WAV eller FLAC, eller skapa en videokopia där ljudspåren tas bort. Originalfilerna lämnas orörda.': 'Extract audio to MP3, WAV, or FLAC, or create a video copy with its audio tracks removed. Original files are left untouched.',
    'Ljudextrahering konverterar ljudspåret till valt format. Borttagning kopierar videospåret utan omkodning och utan ljudspår. Kräver FFmpeg.': 'Audio extraction converts the audio track to the selected format. Removing audio copies the video stream without re-encoding or audio. Requires FFmpeg.',
    'Välj en giltig videomapp och en målmapp som inte innehåller källmappen och inte ligger inuti den.': 'Choose a valid video folder and a destination that neither contains nor is inside the source folder.',
    'Välj en giltig videomapp.': 'Choose a valid video folder.',
    'Välj en giltig mapp att skanna.': 'Choose a valid folder to scan.',
    'Extraherar ljud från': 'Extracting audio from',
    'Tar bort ljudspår från': 'Removing audio from',
    'Skanningen avbröts.': 'The scan was cancelled.',
    'Färgprofiler': 'Color profiles',
    'Konvertera bilder mellan sRGB, Display P3 och Adobe RGB (1998). Inbäddade profiler används automatiskt; för omärkta bilder väljer du antagen källprofil.': 'Convert images between sRGB, Display P3, and Adobe RGB (1998). Embedded profiles are used automatically; choose an assumed source profile for untagged images.',
    'Antagen profil för bilder utan inbäddad profil': 'Assumed profile for images without an embedded profile',
    'Konvertera till': 'Convert to',
    'Bilder sparas i samma filformat. Qt måste ha stöd för bildformatet. Konvertering kan ändra pixelvärden och metadata kanske inte följer med; originalfilerna behålls.': 'Images are saved in the same file format. Qt must support that image format. Pixel values may change and metadata might not be retained; originals are preserved.',
    'Konvertera färgprofiler': 'Convert color profiles',
    'Välj en giltig bildmapp.': 'Choose a valid image folder.',
    'Välj en giltig bildmapp och en målmapp som är skild från källmappen.': 'Choose a valid image folder and a destination separate from the source folder.',
    'Videostabilisering': 'Video stabilization',
    'Stabilisera skakiga videor med FFmpeg deshake och spara H.264-kopior. Omkodning kan påverka kvalitet och tar tid; originalen ändras inte.': 'Stabilize shaky videos with FFmpeg deshake and save H.264 copies. Re-encoding takes time and may affect quality; originals are unchanged.',
    'Styrka': 'Strength',
    'Mild': 'Mild',
    'Normal': 'Normal',
    'Stark': 'Strong',
    'Stabilisera videomapp': 'Stabilize video folder',
    'Ljudförbättring': 'Audio enhancement',
    'Normalisera ljudstyrka med EBU-loudness-normalisering eller minska konstant bakgrundsbrus. Ljud bearbetas med FFmpeg; videospåret kopieras utan omkodning.': 'Normalize loudness with EBU loudness normalization or reduce steady background noise. Audio is processed with FFmpeg; video streams are copied without re-encoding.',
    'Välj mapp med ljud eller video…': 'Choose an audio or video folder…',
    'Spara bearbetade kopior i': 'Save processed copies to',
    'Brusreducering kan påverka ljudkvaliteten. Resultat sparas som nya filer; originalen lämnas orörda.': 'Noise reduction can affect audio quality. Results are saved as new files; originals are left untouched.',
    'Normalisera ljudvolym': 'Normalize audio loudness',
    'Minska bakgrundsbrus': 'Reduce background noise',
    'Välj en giltig ljud- eller videomapp.': 'Choose a valid audio or video folder.',
    'Välj en giltig källmapp och en separat målmapp.': 'Choose a valid source folder and a separate destination folder.',
    'Codec-rapport': 'Codec report',
    'Läs teknisk information om ljud- och videofiler med ffprobe (installeras tillsammans med FFmpeg).': 'Inspect technical details of audio and video files using ffprobe (installed with FFmpeg).',
    'Välj mapp med mediafiler…': 'Choose a folder with media files…',
    'Skapa codec-rapport': 'Create codec report',
    'Exportera CSV…': 'Export CSV…',
    'Exportera codec-rapport': 'Export codec report',
    'Export klar': 'Export complete',
    'CSV sparad:': 'CSV saved:',
    'Exportfel': 'Export error',
    'Container': 'Container',
    'Längd': 'Duration',
    'Video-codec': 'Video codec',
    'Upplösning': 'Resolution',
    'Bildfrekvens': 'Frame rate',
    'Video-bitrate': 'Video bitrate',
    'Ljud-codec': 'Audio codec',
    'Ljudformat': 'Audio format',
    'Ljud-bitrate': 'Audio bitrate',
    'Fel': 'Error',
    'Videostabilisering avbruten.': 'Video stabilization cancelled.',
    'Ljudbearbetning avbruten.': 'Audio processing cancelled.',
    'Färgprofilkonvertering avbruten.': 'Color profile conversion cancelled.',
    'Inga stödda bilder hittades.': 'No supported images found.',
    'Inga ljud- eller videofiler hittades.': 'No audio or video files were found.',
    'Codec-rapport avbruten.': 'Codec report cancelled.',
    'Videostabilisering avbruten': 'Video stabilization cancelled',
    'Ljudbearbetning': 'Audio processing',
    'Codec-rapport klar.': 'Codec report complete.',
    'Stabiliserad kopia:': 'Stabilized copy:',
    'Normaliserad:': 'Normalized:',
    'Brusreducerad:': 'Noise reduced:',
})

UI_TRANSLATIONS.update({
    'Bildbibliotek': 'Photo library',
    'Öppna en bildmapp och bläddra bland originalen. Bilder kopieras eller ändras inte.': 'Open a folder and browse the originals. Images are not copied or modified.',
    'Bildmapp': 'Image folder',
    'Öppna bildmapp…': 'Open image folder…',
    'Uppdatera lista': 'Refresh list',
    'Inkludera undermappar': 'Include subfolders',
    'Föregående': 'Previous',
    'Nästa': 'Next',
    'Helskärm': 'Full screen',
    'Skriv ut…': 'Print…',
    'Välj en bildmapp att bläddra i.': 'Choose an image folder to browse.',
    'Skannar bildmappen…': 'Scanning image folder…',
    'Inga bilder hittades.': 'No images found.',
    'Bilder hittade: {count}': 'Images found: {count}',
    'Välj en bild från listan.': 'Select an image from the list.',
    'Bild {current} av {total} · {name} · {width} × {height}': 'Image {current} of {total} · {name} · {width} × {height}',
    'Bild {current} av {total} · {name} · ←/→ · Esc': 'Image {current} of {total} · {name} · ←/→ · Esc',
    'Kunde inte läsa mappen:': 'Could not read folder:',
    'Kunde inte visa bilden:': 'Could not display image:',
    'Välj en bild först.': 'Select an image first.',
    'Välj en bild': 'Choose an image',
    'Kunde inte starta vald skrivare.': 'Could not start the selected printer.',
    'Utskrift avbruten.': 'Printing cancelled.',
    'Kunde inte skriva ut bilden:': 'Could not print image:',
    'Skickat till skrivaren: {name}': 'Sent to printer: {name}',
    'Välj en giltig bildmapp.': 'Choose a valid image folder.',
    'Bildformat som stöds: JPEG, PNG, WEBP, TIFF, BMP, GIF och (med pillow-heif) HEIC/HEIF/AVIF.': 'Supported formats: JPEG, PNG, WEBP, TIFF, BMP, GIF, and (with pillow-heif) HEIC/HEIF/AVIF.',
})

UI_TRANSLATIONS.update({
    'Jämför vald grupp…': 'Compare selected group…',
    'Jämför dubbletter': 'Compare duplicates',
    'Dubblettgrupp {group} · {count} filer': 'Duplicate group {group} · {count} files',
    'Jämför filerna; bildgrupper visas sida vid sida. Markera vilka filer du vill behålla. Omarkerade flyttas till karantän först efter separat bekräftelse.': 'Compare files; image groups are shown side by side. Mark which files to keep. Unchecked files are moved to quarantine only after a separate confirmation.',
    'Behåll den här filen': 'Keep this file',
    'Behåll bara denna': 'Keep only this one',
    'Behåll alla i gruppen': 'Keep all in this group',
    'Klar': 'Done',
    'Ingen bildförhandsvisning för den här filtypen.': 'No image preview is available for this file type.',
    'Förhandsvisning kunde inte läsas:': 'Could not load preview:',
    '{size} byte · ändrad {date}': '{size} bytes · modified {date}',
    '{width} × {height} · {size} byte · ändrad {date}': '{width} × {height} · {size} bytes · modified {date}',
})

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


def image_file_to_qimage(path, maximum_size=None):
    """Load a Pillow-supported image into an owned QImage, respecting EXIF rotation."""
    with Image.open(path) as source:
        image = ImageOps.exif_transpose(source)
        image.load()
        dimensions = image.size
        if maximum_size:
            image.thumbnail(maximum_size, Image.Resampling.LANCZOS)
        has_alpha = 'A' in image.getbands() or image.info.get('transparency') is not None
        if has_alpha:
            image = image.convert('RGBA')
            pixel_format = QtGui.QImage.Format.Format_RGBA8888
            stride = image.width * 4
        else:
            image = image.convert('RGB')
            pixel_format = QtGui.QImage.Format.Format_RGB888
            stride = image.width * 3
        qimage = QtGui.QImage(image.tobytes(), image.width, image.height, stride, pixel_format).copy()
        return qimage, dimensions


class ImageLibraryScanWorker(QtCore.QThread):
    scan_completed = QtCore.pyqtSignal(object, bool)
    message = QtCore.pyqtSignal(str)

    IMAGE_EXTENSIONS = PHOTO | {'.gif', '.heic', '.heif', '.avif'}
    MODERN_EXTENSIONS = {'.heic', '.heif', '.avif'}
    SKIP_DIRS = {'.git', '.venv', '__pycache__', 'node_modules'}

    def __init__(self, source, recursive=True, modern_formats=True):
        super().__init__()
        self.source = Path(source)
        self.recursive = recursive
        self.modern_formats = modern_formats
        self.cancelled = False

    def run(self):
        files = []
        extensions = self.IMAGE_EXTENSIONS if self.modern_formats else self.IMAGE_EXTENSIONS - self.MODERN_EXTENSIONS
        try:
            if self.recursive:
                for current, directories, names in os.walk(self.source):
                    if self.cancelled:
                        self.scan_completed.emit([], True)
                        return
                    directories[:] = sorted(name for name in directories if name not in self.SKIP_DIRS)
                    files.extend(Path(current) / name for name in names if Path(name).suffix.lower() in extensions)
            else:
                files = [path for path in self.source.iterdir() if path.is_file() and path.suffix.lower() in extensions]
        except OSError as exc:
            self.message.emit(f'Kunde inte läsa mappen: {exc}')
            self.scan_completed.emit([], False)
            return
        files.sort(key=lambda path: (path.name.casefold(), str(path.parent).casefold()))
        self.scan_completed.emit(files, self.cancelled)


class FitImageLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.source_image = None
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(120, 100)

    def set_image(self, image):
        self.source_image = image
        self.refresh_image()

    def refresh_image(self):
        if self.source_image is None or self.source_image.isNull():
            self.setPixmap(QtGui.QPixmap())
            return
        pixmap = QtGui.QPixmap.fromImage(self.source_image).scaled(self.contentsRect().size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        self.setPixmap(pixmap)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.refresh_image()


class FullScreenImageViewer(QtWidgets.QDialog):
    def __init__(self, paths, start_index, parent=None):
        super().__init__(parent)
        self.paths = list(paths)
        self.index = max(0, min(start_index, len(self.paths) - 1))
        self.setWindowTitle('MediaForge')
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet('QDialog { background: #080b12; } QLabel { color: white; background: #080b12; }')
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.image_label = FitImageLabel()
        self.image_label.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
        layout.addWidget(self.image_label, 1)
        self.caption = QtWidgets.QLabel()
        self.caption.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.caption)
        self.show_current()
        self.showFullScreen()
        self.image_label.setFocus()

    def show_current(self):
        if not self.paths:
            return
        path = self.paths[self.index]
        try:
            screen = QtWidgets.QApplication.primaryScreen()
            available = screen.availableGeometry().size() if screen else QtCore.QSize(1600, 1000)
            qimage, _ = image_file_to_qimage(path, (available.width() * 2, available.height() * 2))
            self.image_label.set_image(qimage)
            caption = 'Bild {current} av {total} · {name} · ←/→ · Esc'
            translator = getattr(self.parent(), 'translated', lambda text: text)
            self.caption.setText(translator(caption).format(current=self.index + 1, total=len(self.paths), name=path.name))
        except Exception as exc:
            self.image_label.setText(str(exc))

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (QtCore.Qt.Key.Key_Right, QtCore.Qt.Key.Key_PageDown):
            self.index = min(len(self.paths) - 1, self.index + 1)
            self.show_current()
        elif event.key() in (QtCore.Qt.Key.Key_Left, QtCore.Qt.Key.Key_PageUp):
            self.index = max(0, self.index - 1)
            self.show_current()
        else:
            super().keyPressEvent(event)


class ImageOptimizeWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()

    FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff', '.bmp', '.heic', '.heif', '.avif'}

    def __init__(self, source, destination, recursive, clear_metadata):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.recursive = recursive
        self.clear_metadata = clear_metadata
        self.cancelled = False

    def run(self):
        if any(p.suffix.lower() in {'.heic', '.heif', '.avif'} for p in self.source.rglob('*') if p.is_file()) and not register_modern_formats():
            self.message.emit('INFO: HEIC/AVIF kräver pillow-heif. Övriga bildformat fortsätter att bearbetas.')
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        files = sorted(p for p in candidates if p.is_file() and p.suffix.lower() in self.FORMATS)
        if not files:
            self.message.emit('Inga stödda bilder hittades (JPG, PNG, WEBP, TIFF, BMP, HEIC/HEIF, AVIF).')
            self.completed.emit()
            return
        for i, source in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('Bildoptimering avbruten.')
                break
            try:
                target = self.destination / source.relative_to(self.source)
                if target.exists():
                    target = target.with_name(f'{target.stem}_2{target.suffix}')
                    n = 3
                    while target.exists():
                        target = target.with_name(f'{source.stem}_{n}{source.suffix}')
                        n += 1
                target.parent.mkdir(parents=True, exist_ok=True)
                ext = source.suffix.lower()
                if ext in {'.jpg', '.jpeg'}:
                    # Keep the existing JPEG bitstream: re-encoding would reduce quality.
                    shutil.copy2(source, target)
                    if self.clear_metadata:
                        set_dates(target, datetime.now(), False, False, True)
                else:
                    with Image.open(source) as original:
                        image = ImageOps.exif_transpose(original)
                        kwargs = {}
                        if not self.clear_metadata:
                            exif = image.getexif()
                            if exif:
                                exif[274] = 1
                                kwargs['exif'] = exif.tobytes()
                            if original.info.get('icc_profile'):
                                kwargs['icc_profile'] = original.info['icc_profile']
                        if ext == '.png':
                            kwargs['optimize'] = True
                        elif ext == '.webp':
                            kwargs.update(lossless=True, method=6)
                        elif ext in {'.tif', '.tiff'}:
                            kwargs.update(compression='tiff_adobe_deflate')
                        # Re-saving PNG/TIFF is lossless; WEBP uses its lossless encoder.
                        image.save(target, **kwargs)
                    if self.clear_metadata and ext in {'.bmp'}:
                        self.message.emit(f'INFO: metadata-rensning stöds inte i BMP: {source.name}')
                size_in = source.stat().st_size
                size_out = target.stat().st_size
                delta = (1 - size_out / size_in) * 100 if size_in else 0
                label = f'{delta:+.1f}%'
                self.message.emit(f'KLAR: {source.relative_to(self.source)} → {target.name} ({size_in:,} → {size_out:,} byte; {label})')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            finally:
                self.progress.emit(i, len(files))
        self.completed.emit()


class VideoConvertWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()

    def __init__(self, source, destination, recursive, crf, max_size):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.recursive = recursive
        self.crf = crf
        self.max_size = max_size
        self.cancelled = False
        self.process = None

    def run(self):
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            self.message.emit('FEL: FFmpeg saknas. Installera FFmpeg och se till att kommandot ffmpeg finns i PATH.')
            self.completed.emit()
            return
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        files = sorted(p for p in candidates if p.is_file() and p.suffix.lower() in VIDEO)
        if not files:
            self.message.emit('Inga videofiler hittades.')
            self.completed.emit()
            return
        for i, source in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('Videokonvertering avbruten.')
                break
            try:
                target = self.destination / source.relative_to(self.source).with_suffix('.mp4')
                if target.resolve() == source.resolve() or target.exists():
                    n = 2
                    candidate = target.with_name(f'{target.stem}_{n}{target.suffix}')
                    while candidate.exists():
                        n += 1
                        candidate = target.with_name(f'{target.stem}_{n}{target.suffix}')
                    target = candidate
                target.parent.mkdir(parents=True, exist_ok=True)
                args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source), '-map', '0:v:0', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(self.crf), '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart']
                if self.max_size:
                    args += ['-vf', f"scale=w='min({self.max_size[0]},iw)':h='min({self.max_size[1]},ih)':force_original_aspect_ratio=decrease:force_divisible_by=2"]
                args += ['-y', str(target)]
                self.process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                while self.process.poll() is None:
                    if self.cancelled:
                        self.process.terminate()
                        try:
                            self.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            self.process.kill()
                        break
                    self.msleep(200)
                code = self.process.wait()
                err = self.process.stderr.read()[-1800:] if self.process.stderr else ''
                self.process = None
                if self.cancelled:
                    if target.exists():
                        target.unlink()
                    self.message.emit('Videokonvertering avbruten.')
                    break
                if code:
                    if target.exists():
                        target.unlink()
                    raise RuntimeError(err.strip() or f'FFmpeg avslutades med kod {code}')
                self.message.emit(f'KLAR: {source.relative_to(self.source)} → {target} ({source.stat().st_size:,} → {target.stat().st_size:,} byte)')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            finally:
                self.progress.emit(i, len(files))
        self.completed.emit()

    def cancel(self):
        self.cancelled = True
        if self.process and self.process.poll() is None:
            self.process.terminate()


class VideoAudioWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()

    def __init__(self, source, destination, recursive, action, audio_format='mp3'):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.recursive = recursive
        self.action = action
        self.audio_format = audio_format.lower()
        self.cancelled = False
        self.process = None

    def run(self):
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            self.message.emit('FEL: FFmpeg saknas. Installera FFmpeg och se till att kommandot ffmpeg finns i PATH.')
            self.completed.emit()
            return
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        files = sorted(path for path in candidates if path.is_file() and path.suffix.lower() in VIDEO)
        if not files:
            self.message.emit('Inga videofiler hittades.')
            self.completed.emit()
            return
        codecs = {'mp3': ['-c:a', 'libmp3lame', '-q:a', '2'], 'wav': ['-c:a', 'pcm_s16le'], 'flac': ['-c:a', 'flac']}
        for index, source in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('Ljud/videojobb avbrutet.')
                break
            target = None
            try:
                relative = source.relative_to(self.source)
                if self.action == 'extract':
                    target = self.destination / relative.with_suffix('.' + self.audio_format)
                    args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source), '-map', '0:a:0', '-vn', '-map_metadata', '0', *codecs[self.audio_format]]
                else:
                    target = self.destination / relative.with_name(relative.stem + '_no_audio' + relative.suffix)
                    args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source), '-map', '0', '-c', 'copy', '-an', '-map_metadata', '0', '-map_chapters', '0']
                target.parent.mkdir(parents=True, exist_ok=True)
                stem, suffix = target.stem, target.suffix
                number = 2
                while target.exists():
                    target = target.with_name(f'{stem}_{number}{suffix}')
                    number += 1
                args += ['-n', str(target)]
                self.process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                while self.process.poll() is None:
                    if self.cancelled:
                        self.process.terminate()
                        try:
                            self.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            self.process.kill()
                        break
                    self.msleep(200)
                code = self.process.wait()
                error = self.process.stderr.read()[-1800:] if self.process.stderr else ''
                self.process = None
                if self.cancelled:
                    if target.exists():
                        target.unlink()
                    self.message.emit('Ljud/videojobb avbrutet.')
                    break
                if code:
                    if target.exists():
                        target.unlink()
                    raise RuntimeError(error.strip() or f'FFmpeg avslutades med kod {code}')
                action_text = 'Ljudspår extraherat' if self.action == 'extract' else 'Ljudspår borttaget; video kopierad utan omkodning'
                self.message.emit(f'KLAR: {action_text}: {source.relative_to(self.source)} → {target}')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            finally:
                self.progress.emit(index, len(files))
        self.completed.emit()

    def cancel(self):
        self.cancelled = True
        if self.process and self.process.poll() is None:
            self.process.terminate()


class ColorProfileWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()

    def __init__(self, source, destination, recursive, assumed_source, target_profile):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.recursive = recursive
        self.assumed_source = assumed_source
        self.target_profile = target_profile
        self.cancelled = False

    @staticmethod
    def qt_profile(name):
        enum_name = IMAGE_COLOR_PROFILES[name]
        named = getattr(QtGui.QColorSpace.NamedColorSpace, enum_name, None)
        if named is None:
            raise RuntimeError(f'This Qt version does not provide the {name} color space.')
        profile = QtGui.QColorSpace(named)
        if not profile.isValid():
            raise RuntimeError(f'Could not initialize the {name} color space.')
        return profile

    def run(self):
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        files = sorted(path for path in candidates if path.is_file() and path.suffix.lower() in PHOTO)
        if not files:
            self.message.emit('INFO: Inga stödda bilder hittades.')
            self.completed.emit()
            return
        try:
            assumed = self.qt_profile(self.assumed_source)
            target_space = self.qt_profile(self.target_profile)
        except Exception as exc:
            self.message.emit(f'FEL: {exc}')
            self.completed.emit()
            return
        for index, source in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('INFO: Färgprofilkonvertering avbruten.')
                break
            try:
                image = QtGui.QImage(str(source))
                if image.isNull():
                    raise RuntimeError('Qt could not decode this image format.')
                source_space = image.colorSpace()
                if not source_space.isValid():
                    image.setColorSpace(assumed)
                converted = image.convertedToColorSpace(target_space)
                if converted.isNull():
                    raise RuntimeError('Qt could not convert this image between the selected color spaces.')
                relative = source.relative_to(self.source)
                target = self.destination / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                stem, suffix = target.stem, target.suffix
                number = 2
                while target.exists():
                    target = target.with_name(f'{stem}_{number}{suffix}')
                    number += 1
                writer = QtGui.QImageWriter(str(target))
                if target.suffix.lower() in {'.jpg', '.jpeg'}:
                    writer.setQuality(95)
                if not writer.write(converted):
                    raise RuntimeError(writer.errorString() or 'Qt could not save this image format.')
                self.message.emit(f'KLAR: {source.relative_to(self.source)} → {target} ({self.assumed_source} → {self.target_profile})')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            self.progress.emit(index, len(files))
        self.completed.emit()

    def cancel(self):
        self.cancelled = True


class VideoStabilizeWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()

    def __init__(self, source, destination, recursive, radius):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.recursive = recursive
        self.radius = int(radius)
        self.cancelled = False
        self.process = None

    def run(self):
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            self.message.emit('FEL: FFmpeg saknas. Installera FFmpeg och se till att kommandot ffmpeg finns i PATH.')
            self.completed.emit()
            return
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        files = sorted(path for path in candidates if path.is_file() and path.suffix.lower() in VIDEO)
        if not files:
            self.message.emit('Inga videofiler hittades.')
            self.completed.emit()
            return
        for index, source in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('INFO: Videostabilisering avbruten.')
                break
            target = None
            try:
                relative = source.relative_to(self.source)
                target = self.destination / relative.with_name(relative.stem + '_stabilized.mp4')
                target.parent.mkdir(parents=True, exist_ok=True)
                stem, suffix = target.stem, target.suffix
                number = 2
                while target.exists():
                    target = target.with_name(f'{stem}_{number}{suffix}')
                    number += 1
                video_filter = f'deshake=rx={self.radius}:ry={self.radius}:edge=mirror'
                args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source), '-map', '0:v:0', '-map', '0:a?', '-vf', video_filter, '-c:v', 'libx264', '-preset', 'medium', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-map_metadata', '0', '-map_chapters', '0', '-movflags', '+faststart', '-n', str(target)]
                self.process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                while self.process.poll() is None:
                    if self.cancelled:
                        self.process.terminate()
                        try:
                            self.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            self.process.kill()
                        break
                    self.msleep(200)
                code = self.process.wait()
                error = self.process.stderr.read()[-1800:] if self.process.stderr else ''
                self.process = None
                if self.cancelled:
                    if target.exists():
                        target.unlink()
                    self.message.emit('INFO: Videostabilisering avbruten.')
                    break
                if code:
                    if target.exists():
                        target.unlink()
                    raise RuntimeError(error.strip() or f'FFmpeg avslutades med kod {code}')
                self.message.emit(f'KLAR: Stabiliserad kopia: {source.relative_to(self.source)} → {target}')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            self.progress.emit(index, len(files))
        self.completed.emit()

    def cancel(self):
        self.cancelled = True
        if self.process and self.process.poll() is None:
            self.process.terminate()


class AudioCleanupWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()

    AUDIO_CODECS = {
        '.mp3': ['-c:a', 'libmp3lame', '-q:a', '2'],
        '.wav': ['-c:a', 'pcm_s16le'],
        '.flac': ['-c:a', 'flac'],
        '.m4a': ['-c:a', 'aac', '-b:a', '192k'],
        '.aac': ['-c:a', 'aac', '-b:a', '192k'],
        '.ogg': ['-c:a', 'libvorbis', '-q:a', '5'],
        '.opus': ['-c:a', 'libopus', '-b:a', '160k'],
        '.wma': ['-c:a', 'wmav2', '-b:a', '192k'],
        '.aiff': ['-c:a', 'pcm_s16be'],
        '.aif': ['-c:a', 'pcm_s16be'],
    }

    def __init__(self, source, destination, recursive, action):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.recursive = recursive
        self.action = action
        self.cancelled = False
        self.process = None

    def run(self):
        ffmpeg = shutil.which('ffmpeg')
        if not ffmpeg:
            self.message.emit('FEL: FFmpeg saknas. Installera FFmpeg och se till att kommandot ffmpeg finns i PATH.')
            self.completed.emit()
            return
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        files = sorted(path for path in candidates if path.is_file() and (path.suffix.lower() in VIDEO or path.suffix.lower() in AUDIO_FILE_EXTENSIONS))
        if not files:
            self.message.emit('INFO: Inga ljud- eller videofiler hittades.')
            self.completed.emit()
            return
        audio_filter = 'loudnorm=I=-16:TP=-1.5:LRA=11' if self.action == 'normalize' else 'afftdn=nf=-25'
        for index, source in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('INFO: Ljudbearbetning avbruten.')
                break
            target = None
            try:
                extension = source.suffix.lower()
                is_video = extension in VIDEO
                relative = source.relative_to(self.source)
                if is_video:
                    suffix = '_normalized' if self.action == 'normalize' else '_denoised'
                    target = self.destination / relative.with_name(relative.stem + suffix + '.mkv')
                    args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source), '-map', '0:v?', '-map', '0:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-af', audio_filter, '-map_metadata', '0', '-map_chapters', '0']
                else:
                    target = self.destination / relative.with_name(relative.stem + ('_normalized' if self.action == 'normalize' else '_denoised') + extension)
                    args = [ffmpeg, '-hide_banner', '-loglevel', 'error', '-nostdin', '-i', str(source), '-map', '0:a:0', '-vn', '-af', audio_filter, *self.AUDIO_CODECS[extension], '-map_metadata', '0']
                target.parent.mkdir(parents=True, exist_ok=True)
                stem, suffix = target.stem, target.suffix
                number = 2
                while target.exists():
                    target = target.with_name(f'{stem}_{number}{suffix}')
                    number += 1
                args += ['-n', str(target)]
                self.process = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
                while self.process.poll() is None:
                    if self.cancelled:
                        self.process.terminate()
                        try:
                            self.process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            self.process.kill()
                        break
                    self.msleep(200)
                code = self.process.wait()
                error = self.process.stderr.read()[-1800:] if self.process.stderr else ''
                self.process = None
                if self.cancelled:
                    if target.exists():
                        target.unlink()
                    self.message.emit('INFO: Ljudbearbetning avbruten.')
                    break
                if code:
                    if target.exists():
                        target.unlink()
                    raise RuntimeError(error.strip() or f'FFmpeg avslutades med kod {code}')
                label = 'Normaliserad' if self.action == 'normalize' else 'Brusreducerad'
                self.message.emit(f'KLAR: {label}: {source.relative_to(self.source)} → {target}')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            self.progress.emit(index, len(files))
        self.completed.emit()

    def cancel(self):
        self.cancelled = True
        if self.process and self.process.poll() is None:
            self.process.terminate()


class CodecReportWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    report_ready = QtCore.pyqtSignal(object)

    def __init__(self, source, recursive):
        super().__init__()
        self.source = Path(source)
        self.recursive = recursive
        self.cancelled = False

    @staticmethod
    def rate(value):
        try:
            fraction = Fraction(value)
            return f'{float(fraction):.4g} fps' if fraction.denominator != 1 else f'{fraction.numerator} fps'
        except (ValueError, ZeroDivisionError, TypeError):
            return ''

    @staticmethod
    def bitrate(value):
        try:
            number = int(value)
            return f'{number / 1_000_000:.2f} Mb/s' if number >= 1_000_000 else f'{number / 1000:.0f} kb/s'
        except (ValueError, TypeError):
            return ''

    def run(self):
        ffprobe = shutil.which('ffprobe')
        if not ffprobe:
            self.message.emit('FEL: ffprobe saknas. Installera FFmpeg/ffprobe och se till att ffprobe finns i PATH.')
            self.report_ready.emit([])
            return
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        extensions = VIDEO | AUDIO_FILE_EXTENSIONS
        files = sorted(path for path in candidates if path.is_file() and path.suffix.lower() in extensions)
        if not files:
            self.message.emit('INFO: Inga mediafiler hittades i mappen.')
            self.report_ready.emit([])
            return
        rows = []
        for index, path in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('INFO: Codec-rapport avbruten.')
                self.report_ready.emit([])
                return
            row = {'Fil': str(path), 'Container': '', 'Längd': '', 'Video-codec': '', 'Upplösning': '', 'Bildfrekvens': '', 'Video-bitrate': '', 'Ljud-codec': '', 'Ljudformat': '', 'Ljud-bitrate': '', 'Fel': ''}
            try:
                result = subprocess.run([ffprobe, '-v', 'error', '-show_entries', 'format=duration,bit_rate:stream=codec_type,codec_name,width,height,avg_frame_rate,r_frame_rate,bit_rate,sample_rate,channels,channel_layout', '-of', 'json', str(path)], capture_output=True, text=True, timeout=120)
                if result.returncode:
                    raise RuntimeError(result.stderr.strip() or f'ffprobe exited with code {result.returncode}')
                data = json.loads(result.stdout or '{}')
                fmt = data.get('format', {})
                try:
                    row['Container'] = fmt.get('format_name', '')
                    row['Längd'] = f"{float(fmt.get('duration', 0)):.2f} s"
                except (TypeError, ValueError):
                    row['Längd'] = ''
                streams = data.get('streams', [])
                video = next((stream for stream in streams if stream.get('codec_type') == 'video'), {})
                audio = next((stream for stream in streams if stream.get('codec_type') == 'audio'), {})
                row['Video-codec'] = video.get('codec_name', '')
                if video.get('width') and video.get('height'):
                    row['Upplösning'] = f"{video['width']}×{video['height']}"
                row['Bildfrekvens'] = self.rate(video.get('avg_frame_rate') or video.get('r_frame_rate'))
                row['Video-bitrate'] = self.bitrate(video.get('bit_rate'))
                row['Ljud-codec'] = audio.get('codec_name', '')
                if audio:
                    row['Ljudformat'] = f"{audio.get('sample_rate', '')} Hz, {audio.get('channels', '')} ch"
                row['Ljud-bitrate'] = self.bitrate(audio.get('bit_rate')) or (self.bitrate(fmt.get('bit_rate')) if not video else '')
            except Exception as exc:
                row['Fel'] = str(exc)
            rows.append(row)
            self.progress.emit(index, len(files))
        self.message.emit(f'INFO: Codec-rapport klar. {len(rows)} filer analyserades.')
        self.report_ready.emit(rows)

    def cancel(self):
        self.cancelled = True


class DuplicateScanWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    scan_completed = QtCore.pyqtSignal(object, bool)

    IMAGE_EXTENSIONS = PHOTO | {'.heic', '.heif', '.avif', '.gif'}
    SKIP_DIRS = {'.git', '.venv', '__pycache__', 'MediaForge_Data', 'node_modules'}

    def __init__(self, source, recursive=True, threshold=6):
        super().__init__()
        self.source = Path(source)
        self.recursive = recursive
        self.threshold = int(threshold)
        self.cancelled = False

    @staticmethod
    def sha256(path, worker):
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            while True:
                if worker.cancelled:
                    return None
                block = stream.read(1024 * 1024)
                if not block:
                    break
                digest.update(block)
        return digest.digest()

    @staticmethod
    def difference(left, right):
        return (left ^ right).bit_count()

    def image_hash(self, path):
        with Image.open(path) as original:
            image = ImageOps.exif_transpose(original).convert('L').resize((9, 8), Image.Resampling.LANCZOS)
            pixels = list(image.getdata())
        value = 0
        bit = 0
        for row in range(8):
            for column in range(8):
                if pixels[row * 9 + column] > pixels[row * 9 + column + 1]:
                    value |= 1 << bit
                bit += 1
        # Add average brightness so unrelated flat images (e.g. black and white) don't all hash alike.
        average = sum(pixels) // len(pixels)
        return value | (average << 64)

    def run(self):
        files = []
        if self.recursive:
            for current, directories, names in os.walk(self.source):
                if self.cancelled:
                    self.scan_completed.emit([], True)
                    return
                directories[:] = sorted(name for name in directories if name not in self.SKIP_DIRS)
                files.extend(Path(current) / name for name in names)
        else:
            try:
                files = [path for path in self.source.iterdir() if path.is_file()]
            except OSError as exc:
                self.message.emit(f'FEL: Kunde inte läsa mappen: {exc}')
                self.scan_completed.emit([], False)
                return
        files = sorted(path for path in files if path.is_file())
        if not files:
            self.message.emit('INFO: Inga filer hittades i mappen.')
            self.scan_completed.emit([], False)
            return
        supports_modern = register_modern_formats()
        parent = list(range(len(files)))
        path_indices = {path: index for index, path in enumerate(files)}
        rank = [0] * len(files)
        def find(index):
            while parent[index] != index:
                parent[index] = parent[parent[index]]
                index = parent[index]
            return index
        def union(left, right):
            left, right = find(left), find(right)
            if left == right:
                return
            if rank[left] < rank[right]:
                left, right = right, left
            parent[right] = left
            if rank[left] == rank[right]:
                rank[left] += 1
        exact_seen = {}
        hashes = {}
        tree = None
        image_count = 0
        for index, path in enumerate(files, 1):
            if self.cancelled:
                self.scan_completed.emit([], True)
                return
            try:
                digest = self.sha256(path, self)
                if digest is None:
                    self.scan_completed.emit([], True)
                    return
                hashes[index - 1] = digest
                if digest in exact_seen:
                    union(index - 1, exact_seen[digest])
                else:
                    exact_seen[digest] = index - 1
                if path.suffix.lower() in self.IMAGE_EXTENSIONS and (supports_modern or path.suffix.lower() not in {'.heic', '.heif', '.avif'}):
                    try:
                        image_hash = self.image_hash(path)
                        image_count += 1
                        if tree is None:
                            tree = [image_hash, [index - 1], {}]
                        else:
                            node = tree
                            while True:
                                distance = self.difference(image_hash, node[0])
                                if distance <= self.threshold and node[1]:
                                    union(index - 1, node[1][0])
                                if distance == 0:
                                    node[1].append(index - 1)
                                    break
                                child = node[2].get(distance)
                                if child is None:
                                    node[2][distance] = [image_hash, [index - 1], {}]
                                    break
                                node = child
                            # Query the BK-tree for all previously inserted hashes within the threshold.
                            stack = [tree]
                            while stack:
                                candidate = stack.pop()
                                distance = self.difference(image_hash, candidate[0])
                                if distance <= self.threshold and candidate[1]:
                                    union(index - 1, candidate[1][0])
                                low, high = distance - self.threshold, distance + self.threshold
                                stack.extend(child for edge, child in candidate[2].items() if low <= edge <= high)
                    except Exception:
                        pass  # Unsupported/corrupt image: its exact hash still participates.
            except (OSError, PermissionError) as exc:
                self.message.emit(f'INFO: Hoppade över {path.name}: {exc}')
            self.progress.emit(index, len(files))
        if self.cancelled:
            self.scan_completed.emit([], True)
            return
        components = {}
        for index, path in enumerate(files):
            components.setdefault(find(index), []).append(path)
        groups = []
        for members in components.values():
            if len(members) < 2:
                continue
            digests = [hashes.get(path_indices[path]) for path in members]
            valid_digests = [digest for digest in digests if digest is not None]
            has_exact = len(set(valid_digests)) < len(valid_digests)
            groups.append({
                'kind': 'Identiska filer' if has_exact else 'Visuellt liknande bilder',
                'paths': members,
                'hashes': {str(path): hashes[path_indices[path]].hex() for path in members if path_indices[path] in hashes},
            })
        groups.sort(key=lambda group: (group['kind'], str(group['paths'][0]).casefold()))
        self.message.emit(f'INFO: Skanningen klar. {len(files)} filer och {image_count} bilder analyserades; {len(groups)} dubblettgrupper hittades.')
        self.scan_completed.emit(groups, False)

    def cancel(self):
        self.cancelled = True


class DuplicateQuarantineWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal(int, int)

    def __init__(self, source, paths, quarantine, expected_hashes=None):
        super().__init__()
        self.source = Path(source)
        self.paths = [Path(path) for path in paths]
        self.quarantine = Path(quarantine)
        self.expected_hashes = expected_hashes or {}
        self.cancelled = False
        self.moved = 0
        self.failed = 0

    def run(self):
        for index, source in enumerate(self.paths, 1):
            if self.cancelled:
                self.message.emit('INFO: Flytt till karantän avbröts.')
                break
            try:
                expected = self.expected_hashes.get(str(source))
                if expected:
                    digest = hashlib.sha256()
                    with source.open('rb') as stream:
                        for block in iter(lambda: stream.read(1024 * 1024), b''):
                            digest.update(block)
                    if digest.hexdigest() != expected:
                        raise RuntimeError('File changed since the duplicate scan; it was not moved.')
                relative = source.relative_to(self.source)
                target = self.quarantine / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                stem, suffix = target.stem, target.suffix
                number = 2
                while target.exists():
                    target = target.with_name(f'{stem}_{number}{suffix}')
                    number += 1
                shutil.move(str(source), str(target))
                self.moved += 1
                self.message.emit(f'KLAR: Flyttad till karantän: {source} → {target}')
            except Exception as exc:
                self.failed += 1
                self.message.emit(f'FEL: Kunde inte flytta {source}: {exc}')
            self.progress.emit(index, len(self.paths))
        self.completed.emit(self.moved, self.failed)

    def cancel(self):
        self.cancelled = True


class MusicDVDWorker(QtCore.QThread):
    message = QtCore.pyqtSignal(str)
    progress = QtCore.pyqtSignal(int, int)
    completed = QtCore.pyqtSignal()
    AUDIO = {'.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg', '.opus', '.wma', '.aiff', '.aif'}
    DVD_LIMIT = 4_500_000_000

    def __init__(self, source, destination, recursive):
        super().__init__()
        self.source = Path(source)
        self.destination = Path(destination)
        self.recursive = recursive
        self.cancelled = False

    def run(self):
        candidates = self.source.rglob('*') if self.recursive else self.source.iterdir()
        files = sorted(p for p in candidates if p.is_file() and p.suffix.lower() in self.AUDIO)
        if not files:
            self.message.emit('Inga ljudfiler hittades (MP3, WAV, FLAC, M4A, AAC, OGG, OPUS, WMA, AIFF).')
            self.completed.emit()
            return
        total = sum(p.stat().st_size for p in files)
        if total > self.DVD_LIMIT:
            self.message.emit(f'FEL: Ljudfilerna är {total / 1_000_000_000:.2f} GB och ryms inte på en DVD-5 (ca 4,7 GB).')
            self.completed.emit()
            return
        package = self.destination / 'MUSIK_DVD'
        suffix = 2
        while package.exists():
            package = self.destination / f'MUSIK_DVD_{suffix}'
            suffix += 1
        package.mkdir(parents=True, exist_ok=True)
        used = set()
        for i, source in enumerate(files, 1):
            if self.cancelled:
                self.message.emit('Skapandet avbröts. Ofärdig mapp finns kvar: ' + str(package))
                self.completed.emit()
                return
            try:
                base = source.name
                candidate = base
                n = 2
                while candidate.casefold() in used or (package / candidate).exists():
                    candidate = f'{source.stem}_{n}{source.suffix}'
                    n += 1
                used.add(candidate.casefold())
                shutil.copy2(source, package / candidate)
                self.message.emit(f'Kopierad: {source.name} → {candidate}')
            except Exception as exc:
                self.message.emit(f'FEL: {source.name}: {exc}')
            finally:
                self.progress.emit(i, len(files))
        (package / 'LAS_MIG.txt').write_text(
            'Musik-DVD (data-DVD)\n\nDen här skivan innehåller vanliga musikfiler. Den är redo att brännas som en data-DVD, men är inte DVD-Video och kan därför inte spelas i alla DVD-spelare.\n',
            encoding='utf-8')
        tool = next((shutil.which(name) for name in ('xorriso', 'genisoimage', 'mkisofs') if shutil.which(name)), None)
        if tool and not self.cancelled:
            iso = self.destination / f'{package.name}.iso'
            args = [tool, '-V', 'MUSIK_DVD', '-o', str(iso), '-J', '-R', str(package)]
            # xorriso has mkisofs-compatible arguments when called as xorriso -as mkisofs.
            if Path(tool).name == 'xorriso':
                args.insert(1, '-as')
                args.insert(2, 'mkisofs')
            try:
                result = subprocess.run(args, capture_output=True, text=True, timeout=900)
                if result.returncode:
                    raise RuntimeError(result.stderr.strip() or 'ISO-skapandet misslyckades')
                self.message.emit(f'ISO klar: {iso} (bränn filen som skivavbildning).')
            except Exception as exc:
                self.message.emit(f'INFO: Mapp redo att brännas, men ISO kunde inte skapas: {exc}')
        else:
            self.message.emit('Mapp MUSIK_DVD är klar att brännas som data-DVD. För ISO-installera xorriso, genisoimage eller mkisofs.')
        self.message.emit(f'KLART: {len(files)} musikfiler, {total / 1_000_000_000:.2f} GB → {package}')
        self.completed.emit()


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
        self.empty_text = 'Öppna ett foto för att börja redigera'
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
            painter.drawText(self.rect(), QtCore.Qt.AlignmentFlag.AlignCenter, self.empty_text)
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
    """Draw a compact fallback mark matching the MediaForge photo/video logo."""
    pix = QtGui.QPixmap(96, 96)
    pix.fill(QtCore.Qt.GlobalColor.transparent)
    p = QtGui.QPainter(pix)
    p.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
    p.setPen(QtCore.Qt.PenStyle.NoPen)
    p.setBrush(QtGui.QColor('#101b31'))
    p.drawRoundedRect(2, 2, 92, 92, 22, 22)
    p.setBrush(QtGui.QColor('#13d5d0'))
    p.drawRoundedRect(13, 23, 70, 50, 12, 12)
    p.setBrush(QtGui.QColor('#101b31'))
    p.drawRoundedRect(22, 31, 52, 34, 7, 7)
    path = QtGui.QPainterPath()
    path.moveTo(40, 37)
    path.lineTo(62, 48)
    path.lineTo(40, 60)
    path.closeSubpath()
    p.setBrush(QtGui.QColor('#ffb323'))
    p.drawPath(path)
    p.end()
    return QtGui.QIcon(pix)


def autostart_supported():
    return sys.platform in {'win32', 'darwin'} or sys.platform.startswith('linux')


def startup_file():
    if sys.platform == 'darwin':
        return Path.home() / 'Library/LaunchAgents/se.fotoverktyg.studio.plist'
    if sys.platform.startswith('linux'):
        config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config'))).expanduser()
        return config_home / 'autostart' / 'fotoverktyg.desktop'
    raise RuntimeError(f'Autostart is not supported on platform: {sys.platform}')


def autostart_enabled():
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
                for value_name in ('MediaForge', 'Fotoverktyg'):
                    try:
                        winreg.QueryValueEx(key, value_name)
                        return True
                    except FileNotFoundError:
                        continue
            return False
        except OSError:
            return False
    if not autostart_supported():
        return False
    return startup_file().exists()


def set_autostart(enabled):
    if not autostart_supported():
        raise RuntimeError(f'Autostart is not supported on platform: {sys.platform}')
    app_dir = Path(__file__).resolve().parent
    if getattr(sys, 'frozen', False):
        command = [sys.executable]
    elif sys.platform == 'win32' and (app_dir / 'Starta_Fotoverktyg.vbs').is_file():
        command = ['wscript.exe', str(app_dir / 'Starta_Fotoverktyg.vbs')]
    elif sys.platform in {'darwin', 'linux'} and (app_dir / 'start_mediaforge.sh').is_file():
        command = ['/bin/bash', str(app_dir / 'start_mediaforge.sh')]
    else:
        interpreter = Path(sys.executable)
        if sys.platform == 'win32' and interpreter.name.lower() == 'python.exe':
            gui_interpreter = interpreter.with_name('pythonw.exe')
            if gui_interpreter.exists():
                interpreter = gui_interpreter
        command = [str(interpreter), str(Path(__file__).resolve())]
    if sys.platform == 'win32':
        import winreg
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run') as key:
            if enabled:
                winreg.SetValueEx(key, 'MediaForge', 0, winreg.REG_SZ, subprocess.list2cmdline(command))
                try:
                    winreg.DeleteValue(key, 'Fotoverktyg')
                except FileNotFoundError:
                    pass
            else:
                for value_name in ('MediaForge', 'Fotoverktyg'):
                    try:
                        winreg.DeleteValue(key, value_name)
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
    else:  # Linux: XDG autostart entry for the current user.
        path = startup_file()
        if enabled:
            args = ' '.join('"' + arg.replace('\\', '\\\\').replace('"', '\\"') + '"' for arg in command)
            path.parent.mkdir(parents=True, exist_ok=True)
            icon = Path(__file__).resolve().with_name('fotoverktyg_icon.png')
            path.write_text('[Desktop Entry]\nType=Application\nName=MediaForge\nExec=' + args + '\nIcon=' + str(icon) + '\nTerminal=false\nX-GNOME-Autostart-enabled=true\n', encoding='utf-8')
            try:
                path.chmod(0o755)
            except OSError:
                pass
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
        self.setWindowTitle('MediaForge')
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
        brand_header = QtWidgets.QHBoxLayout()
        brand_image = QtWidgets.QLabel()
        brand_image.setPixmap(self.brand.pixmap(QtCore.QSize(56, 56)))
        brand_image.setFixedSize(60, 60)
        brand_image.setToolTip('MediaForge')
        brand_image.setAccessibleName('MediaForge logo')
        brand_header.addWidget(brand_image, 0, QtCore.Qt.AlignmentFlag.AlignVCenter)
        brand_text = QtWidgets.QVBoxLayout()
        title = QtWidgets.QLabel('MEDIAFORGE')
        title.setObjectName('heroTitle')
        brand_text.addWidget(title)
        subtitle = QtWidgets.QLabel('Photo & Video Toolkit · Ett komplett arbetsflöde för foto och video – originalen förblir orörda.')
        subtitle.setObjectName('subtitle')
        brand_text.addWidget(subtitle)
        brand_header.addLayout(brand_text, 1)
        main.addLayout(brand_header)
        APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
        SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        self.ui_settings = QtCore.QSettings(str(SETTINGS_FILE), QtCore.QSettings.Format.IniFormat)
        if not SETTINGS_FILE.exists():
            # Move prior OS-level preferences into the app-local settings file.
            legacy_settings = QtCore.QSettings('Tokke2', 'MediaForge')
            for key in legacy_settings.allKeys():
                self.ui_settings.setValue(key, legacy_settings.value(key))
            self.ui_settings.sync()
            legacy_settings.clear()
            legacy_settings.sync()
        self.ui_language = self.ui_settings.value('language', 'sv')
        self.media_mode = self.ui_settings.value('mediaMode', 'all')
        saved_dark = self.ui_settings.value('darkTheme', True, type=bool)
        self.dark = not saved_dark
        if self.ui_language not in {'sv', 'en'}:
            self.ui_language = 'sv'
        if self.media_mode not in {'all', 'photo', 'video'}:
            self.media_mode = 'all'
        preferences = QtWidgets.QHBoxLayout()
        self.mode_label = QtWidgets.QLabel('Visa flikar:')
        preferences.addWidget(self.mode_label)
        self.mode_combo = QtWidgets.QComboBox()
        for label, value in [('Alla', 'all'), ('Foto', 'photo'), ('Video', 'video')]:
            self.mode_combo.addItem(label, value)
        self.mode_combo.setCurrentIndex(max(0, self.mode_combo.findData(self.media_mode)))
        preferences.addWidget(self.mode_combo)
        self.language_label = QtWidgets.QLabel('Språk:')
        preferences.addWidget(self.language_label)
        self.language_combo = QtWidgets.QComboBox()
        self.language_combo.addItem('Svenska', 'sv')
        self.language_combo.addItem('English', 'en')
        self.language_combo.setCurrentIndex(max(0, self.language_combo.findData(self.ui_language)))
        preferences.addWidget(self.language_combo)
        preferences.addStretch()
        main.addLayout(preferences)
        self.tabs = QtWidgets.QTabWidget()
        main.addWidget(self.tabs)
        action_row = QtWidgets.QHBoxLayout()
        self.deps_button = QtWidgets.QPushButton('Kontrollera/installera Python-tillägg…')
        self.deps_button.clicked.connect(self.manage_dependencies)
        action_row.addWidget(self.deps_button)
        self.donate_button = QtWidgets.QPushButton('Stöd utvecklingen · Ko-fi')
        self.donate_button.clicked.connect(self.open_donation)
        action_row.addWidget(self.donate_button)
        self.donation_settings_button = QtWidgets.QPushButton('Ange/ändra Ko-fi-länk')
        self.donation_settings_button.clicked.connect(self.configure_donation)
        action_row.addWidget(self.donation_settings_button)
        main.addLayout(action_row)
        maintenance_row = QtWidgets.QHBoxLayout()
        self.python_update_button = QtWidgets.QPushButton('Installera/uppdatera senaste Python…')
        self.python_update_button.clicked.connect(self.update_python_runtime)
        maintenance_row.addWidget(self.python_update_button)
        self.packages_update_button = QtWidgets.QPushButton('Uppdatera alla Python-paket (starta om)…')
        self.packages_update_button.clicked.connect(self.update_all_python_packages)
        maintenance_row.addWidget(self.packages_update_button)
        self.git_update_button = QtWidgets.QPushButton('Kontrollera GitHub main-uppdatering…')
        self.git_update_button.clicked.connect(self.check_git_update)
        maintenance_row.addWidget(self.git_update_button)
        main.addLayout(maintenance_row)
        QtCore.QTimer.singleShot(200, self.offer_missing_dependencies)
        image_tab = QtWidgets.QWidget()
        image_tab.setProperty('mediaMode', 'photo')
        self.tabs.addTab(image_tab, 'Bildförbättring')
        self.editor_image = None
        self.editor_source = None
        self.editor_history = []
        self.library_paths = []
        self.library_scan_worker = None
        self.library_thumbnail_indices = []
        self.library_thumbnail_timer_pending = False
        self.library_populate_cursor = 0
        self.library_current_qimage = None
        self.library_pending_selection = None
        self.build_library_tab()
        self.build_editor_tab()
        self.build_conversion_tab()
        self.build_image_optimize_tab()
        self.build_duplicate_tab()
        self.build_color_profile_tab()
        self.build_video_tab()
        self.build_video_audio_tab()
        self.build_video_stabilize_tab()
        self.build_audio_cleanup_tab()
        self.build_codec_report_tab()
        self.build_music_dvd_tab()
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
        date_tab.setProperty('mediaMode', 'both')
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
        self.source.setText(str(self.ui_settings.value('sourceFolder', '')))
        self.source.setPlaceholderText('Dra en mapp hit eller välj mapp…')
        form.addWidget(QtWidgets.QLabel('Källmapp'), 0, 0)
        form.addWidget(self.source, 0, 1)
        browse = QtWidgets.QPushButton('Välj…')
        browse.clicked.connect(self.browse)
        form.addWidget(browse, 0, 2)
        self.archive = QtWidgets.QLineEdit(self.load_output_setting('archiveFolder', OUTPUT_DIR / 'Processed'))
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
        self.mode_combo.currentIndexChanged.connect(self.change_media_mode)
        self.language_combo.currentIndexChanged.connect(self.change_ui_language)
        self.apply_media_mode()
        last_tab = int(self.ui_settings.value('lastTab', 0))
        if 0 <= last_tab < self.tabs.count() and self.tabs.isTabVisible(last_tab):
            self.tabs.setCurrentIndex(last_tab)
        self.autostart = QtWidgets.QCheckBox('Starta automatiskt vid inloggning')
        self.autostart.setChecked(autostart_enabled())
        self.autostart.setEnabled(autostart_supported())
        if not autostart_supported():
            self.autostart.setToolTip(self.translated('Autostart is supported on Windows, macOS and Linux only.'))
        self.autostart.toggled.connect(self.change_autostart)
        main.addWidget(self.autostart)
        self.restore_preferences()
        self.apply_language()
        for button in self.findChildren(QtWidgets.QPushButton):
            button.setIcon(self.brand)
            button.setIconSize(QtCore.QSize(16, 16))
            button.clicked.connect(lambda checked=False, b=button: LOGGER.info('Knapp: %s', b.text()))
        self.toggle_theme()
        LOGGER.info('Fönstret öppnat; loggfil: %s', LOG_FILE)

    def require_app_output(self, path):
        candidate = Path(path).expanduser().resolve(strict=False)
        if not is_app_owned_path(candidate):
            self.show_message('warning', 'Output folder restricted', 'Utdata måste sparas under MediaForge-appens mapp.')
            return None
        return candidate

    def load_output_setting(self, key, default):
        default = Path(default)
        value = Path(str(self.ui_settings.value(key, str(default)))).expanduser()
        if not is_app_owned_path(value):
            return str(default)
        return str(value)

    def build_image_optimize_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'photo')
        self.tabs.addTab(tab, 'Bildoptimering')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Importera en hel mapp och skapa optimerade kopior. Originalen ändras aldrig.'))
        layout.addWidget(QtWidgets.QLabel('JPG kopieras utan omkodning för att bevara bildkvaliteten; PNG/TIFF optimeras förlustfritt och WEBP kodas förlustfritt.'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.image_source = QtWidgets.QLineEdit(str(self.ui_settings.value('imageSourceFolder', '')))
        self.image_source.setPlaceholderText('Välj mapp med bilder…')
        self.image_source.setAcceptDrops(True)
        form.addWidget(QtWidgets.QLabel('Bildmapp'), 0, 0)
        form.addWidget(self.image_source, 0, 1)
        choose_source = QtWidgets.QPushButton('Välj mapp…')
        choose_source.clicked.connect(lambda: self.choose_directory(self.image_source, 'Välj bildmapp'))
        form.addWidget(choose_source, 0, 2)
        self.image_destination = QtWidgets.QLineEdit(self.load_output_setting('imageOutputFolder', OUTPUT_DIR / 'Images' / 'Optimized'))
        form.addWidget(QtWidgets.QLabel('Spara kopior i'), 1, 0)
        form.addWidget(self.image_destination, 1, 1)
        choose_dest = QtWidgets.QPushButton('Välj mapp…')
        choose_dest.clicked.connect(lambda: self.choose_directory(self.image_destination, 'Välj målmapp'))
        form.addWidget(choose_dest, 1, 2)
        self.image_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.image_recursive.setChecked(True)
        self.image_strip = QtWidgets.QCheckBox('Rensa EXIF/metadata (GPS, kameradata m.m.)')
        self.image_strip.setChecked(True)
        layout.addWidget(self.image_recursive)
        layout.addWidget(self.image_strip)
        layout.addWidget(QtWidgets.QLabel('OBS: För JPG bevaras den ursprungliga bildströmmen, så storleken minskar främst genom att metadata rensas. PNG/TIFF kan bli mindre genom förlustfri optimering.'))
        row = QtWidgets.QHBoxLayout()
        self.image_go = QtWidgets.QPushButton('Optimera bildmapp')
        self.image_go.clicked.connect(self.start_image_optimization)
        row.addWidget(self.image_go)
        self.image_stop = QtWidgets.QPushButton('Avbryt')
        self.image_stop.setEnabled(False)
        self.image_stop.clicked.connect(self.cancel_image_optimization)
        row.addWidget(self.image_stop)
        layout.addLayout(row)
        self.image_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.image_progress)
        self.image_log = QtWidgets.QPlainTextEdit()
        self.image_log.setReadOnly(True)
        layout.addWidget(self.image_log, 1)

    def build_duplicate_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'photo')
        self.tabs.addTab(tab, 'Dubblettfinnare')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Hitta identiska filer med SHA-256 och visuellt liknande bilder med perceptuell hash. Inga filer ändras under skanningen.'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.duplicate_source = QtWidgets.QLineEdit(str(self.ui_settings.value('duplicateSourceFolder', '')))
        self.duplicate_source.setPlaceholderText('Välj mapp att skanna…')
        form.addWidget(QtWidgets.QLabel('Skanna mapp'), 0, 0)
        form.addWidget(self.duplicate_source, 0, 1)
        choose_source = QtWidgets.QPushButton('Välj mapp…')
        choose_source.clicked.connect(lambda: self.choose_directory(self.duplicate_source, 'Välj skanningsmapp'))
        form.addWidget(choose_source, 0, 2)
        options = QtWidgets.QHBoxLayout()
        self.duplicate_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.duplicate_recursive.setChecked(True)
        options.addWidget(self.duplicate_recursive)
        options.addWidget(QtWidgets.QLabel('Likhetströskel (0–20; lägre = striktare)'))
        self.duplicate_threshold = QtWidgets.QSpinBox()
        self.duplicate_threshold.setRange(0, 20)
        self.duplicate_threshold.setValue(int(self.ui_settings.value('duplicateThreshold', 6)))
        options.addWidget(self.duplicate_threshold)
        options.addStretch()
        layout.addLayout(options)
        layout.addWidget(QtWidgets.QLabel('Välj minst en fil att behålla i varje grupp. Omarkerade kopior flyttas till appens karantänmapp; inget raderas permanent.'))
        row = QtWidgets.QHBoxLayout()
        self.duplicate_scan_button = QtWidgets.QPushButton('Skanna efter dubbletter')
        self.duplicate_scan_button.clicked.connect(self.start_duplicate_scan)
        row.addWidget(self.duplicate_scan_button)
        self.duplicate_cancel_button = QtWidgets.QPushButton('Avbryt skanning')
        self.duplicate_cancel_button.setEnabled(False)
        self.duplicate_cancel_button.clicked.connect(self.cancel_duplicate_scan)
        row.addWidget(self.duplicate_cancel_button)
        self.duplicate_compare_button = QtWidgets.QPushButton('Jämför vald grupp…')
        self.duplicate_compare_button.setEnabled(False)
        self.duplicate_compare_button.clicked.connect(self.show_duplicate_comparison)
        row.addWidget(self.duplicate_compare_button)
        self.duplicate_move_button = QtWidgets.QPushButton('Flytta omarkerade till karantän…')
        self.duplicate_move_button.setEnabled(False)
        self.duplicate_move_button.clicked.connect(self.move_unselected_duplicates)
        row.addWidget(self.duplicate_move_button)
        self.duplicate_cancel_move_button = QtWidgets.QPushButton('Avbryt flytt')
        self.duplicate_cancel_move_button.setEnabled(False)
        self.duplicate_cancel_move_button.clicked.connect(self.cancel_duplicate_move)
        row.addWidget(self.duplicate_cancel_move_button)
        layout.addLayout(row)
        self.duplicate_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.duplicate_progress)
        self.duplicate_status = QtWidgets.QLabel('')
        layout.addWidget(self.duplicate_status)
        self.duplicate_table = QtWidgets.QTableWidget(0, 4)
        self.duplicate_table.setHorizontalHeaderLabels([self.translated(label) for label in ('Grupp', 'Behåll', 'Fil', 'Matchning')])
        self.duplicate_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.duplicate_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.duplicate_table.currentCellChanged.connect(self.duplicate_selection_changed)
        self.duplicate_table.itemDoubleClicked.connect(lambda _item: self.show_duplicate_comparison())
        self.duplicate_table.horizontalHeader().setStretchLastSection(True)
        self.duplicate_table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.duplicate_table, 1)
        self.duplicate_log = QtWidgets.QPlainTextEdit()
        self.duplicate_log.setReadOnly(True)
        self.duplicate_log.setMaximumHeight(90)
        layout.addWidget(self.duplicate_log)
        self.duplicate_groups = []

    def start_duplicate_scan(self):
        if not self.duplicate_source.text().strip():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig mapp att skanna.')
            return
        source = Path(self.duplicate_source.text()).expanduser().resolve()
        if not source.is_dir():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig mapp att skanna.')
            return
        if getattr(self, 'duplicate_scan_worker', None) and self.duplicate_scan_worker.isRunning():
            return
        self.duplicate_groups = []
        self.duplicate_table.setRowCount(0)
        self.duplicate_compare_button.setEnabled(False)
        self.duplicate_move_button.setEnabled(False)
        self.duplicate_scan_button.setEnabled(False)
        self.duplicate_cancel_button.setEnabled(True)
        self.duplicate_progress.setValue(0)
        self.duplicate_status.setText(self.translated('Skannar filer…'))
        self.duplicate_log.appendPlainText(f'Skannar {source}')
        self.duplicate_scan_worker = DuplicateScanWorker(source, self.duplicate_recursive.isChecked(), self.duplicate_threshold.value())
        self.duplicate_scan_worker.message.connect(self.append_duplicate_message)
        self.duplicate_scan_worker.message.connect(self.record)
        self.duplicate_scan_worker.progress.connect(lambda done, total: (self.duplicate_progress.setMaximum(total), self.duplicate_progress.setValue(done)))
        self.duplicate_scan_worker.scan_completed.connect(self.duplicate_scan_finished)
        self.duplicate_scan_worker.start()

    def cancel_duplicate_scan(self):
        worker = getattr(self, 'duplicate_scan_worker', None)
        if worker and worker.isRunning():
            worker.cancelled = True
            self.duplicate_cancel_button.setEnabled(False)

    def duplicate_scan_finished(self, groups, cancelled):
        self.duplicate_scan_button.setEnabled(True)
        self.duplicate_cancel_button.setEnabled(False)
        self.duplicate_table.setRowCount(0)
        if cancelled:
            self.duplicate_groups = []
            self.duplicate_compare_button.setEnabled(False)
            self.duplicate_status.setText(self.translated('Skanningen avbröts.'))
            self.duplicate_log.appendPlainText(self.translated('Skanningen avbröts.'))
            return
        self.duplicate_groups = groups
        row = 0
        for group_index, group in enumerate(groups):
            for member_index, path in enumerate(group['paths']):
                self.duplicate_table.insertRow(row)
                group_item = QtWidgets.QTableWidgetItem(str(group_index + 1))
                self.duplicate_table.setItem(row, 0, group_item)
                keep_item = QtWidgets.QTableWidgetItem('')
                keep_item.setFlags(keep_item.flags() | QtCore.Qt.ItemFlag.ItemIsUserCheckable)
                keep_item.setCheckState(QtCore.Qt.CheckState.Checked if member_index == 0 else QtCore.Qt.CheckState.Unchecked)
                self.duplicate_table.setItem(row, 1, keep_item)
                path_item = QtWidgets.QTableWidgetItem(str(path))
                path_item.setData(QtCore.Qt.ItemDataRole.UserRole, str(path))
                path_item.setToolTip(str(path))
                self.duplicate_table.setItem(row, 2, path_item)
                self.duplicate_table.setItem(row, 3, QtWidgets.QTableWidgetItem(self.translated(group['kind'])))
                row += 1
        file_count = sum(len(group['paths']) for group in groups)
        self.duplicate_status.setText(self.translated('Hittade {groups} grupper med {files} filer.').format(groups=len(groups), files=file_count))
        self.duplicate_move_button.setEnabled(bool(groups))
        self.duplicate_compare_button.setEnabled(bool(groups))
        if groups:
            self.duplicate_table.setCurrentCell(0, 2)
            self.duplicate_log.appendPlainText(self.duplicate_status.text())
        else:
            self.duplicate_log.appendPlainText(self.translated('Inga dubbletter hittades.'))

    def duplicate_selection_changed(self, current_row, *_args):
        self.duplicate_compare_button.setEnabled(0 <= current_row < self.duplicate_table.rowCount())

    def show_duplicate_comparison(self):
        row = self.duplicate_table.currentRow()
        if row < 0 or not self.duplicate_groups:
            return
        group_index = int(self.duplicate_table.item(row, 0).text()) - 1
        group = self.duplicate_groups[group_index]
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(self.translated('Jämför dubbletter'))
        dialog.resize(980, 620)
        layout = QtWidgets.QVBoxLayout(dialog)
        heading = QtWidgets.QLabel(self.translated('Dubblettgrupp {group} · {count} filer').format(group=group_index + 1, count=len(group['paths'])))
        layout.addWidget(heading)
        layout.addWidget(QtWidgets.QLabel(self.translated('Jämför filerna; bildgrupper visas sida vid sida. Markera vilka filer du vill behålla. Omarkerade flyttas till karantän först efter separat bekräftelse.')))

        scroll = QtWidgets.QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        cards_panel = QtWidgets.QWidget()
        cards_layout = QtWidgets.QHBoxLayout(cards_panel)
        cards_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        cards = []
        for member_index, path in enumerate(group['paths']):
            table_row = next((candidate for candidate in range(self.duplicate_table.rowCount())
                if int(self.duplicate_table.item(candidate, 0).text()) == group_index + 1
                and Path(self.duplicate_table.item(candidate, 2).data(QtCore.Qt.ItemDataRole.UserRole)) == path), None)
            if table_row is None:
                continue
            card = QtWidgets.QFrame()
            card.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
            card.setMinimumWidth(250)
            card_layout = QtWidgets.QVBoxLayout(card)
            preview = FitImageLabel()
            preview.setFixedSize(224, 158)
            preview.setStyleSheet('background: #0b1220; border-radius: 6px;')
            dimensions = None
            try:
                if path.suffix.lower() in DuplicateScanWorker.IMAGE_EXTENSIONS:
                    qimage, dimensions = image_file_to_qimage(path, (448, 316))
                    preview.set_image(qimage)
                else:
                    preview.setText(self.translated('Ingen bildförhandsvisning för den här filtypen.'))
            except Exception as exc:
                preview.setText(f"{self.translated('Förhandsvisning kunde inte läsas:')} {exc}")
            card_layout.addWidget(preview, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)
            name = QtWidgets.QLabel(path.name)
            name.setWordWrap(True)
            name.setToolTip(str(path))
            card_layout.addWidget(name)
            try:
                info = path.stat()
                date = datetime.fromtimestamp(info.st_mtime).strftime('%Y-%m-%d %H:%M')
                if dimensions:
                    details = self.translated('{width} × {height} · {size} byte · ändrad {date}').format(width=dimensions[0], height=dimensions[1], size=f'{info.st_size:,}', date=date)
                else:
                    details = self.translated('{size} byte · ändrad {date}').format(size=f'{info.st_size:,}', date=date)
            except OSError:
                details = str(path.parent)
            detail_label = QtWidgets.QLabel(details)
            detail_label.setWordWrap(True)
            detail_label.setToolTip(str(path))
            card_layout.addWidget(detail_label)
            keep = QtWidgets.QCheckBox(self.translated('Behåll den här filen'))
            keep.setChecked(self.duplicate_table.item(table_row, 1).checkState() == QtCore.Qt.CheckState.Checked)
            keep.toggled.connect(lambda checked, target=table_row: self.duplicate_table.item(target, 1).setCheckState(QtCore.Qt.CheckState.Checked if checked else QtCore.Qt.CheckState.Unchecked))
            card_layout.addWidget(keep)
            keep_only = QtWidgets.QPushButton(self.translated('Behåll bara denna'))
            card_layout.addWidget(keep_only)
            cards_layout.addWidget(card)
            cards.append((table_row, keep))

        def set_kept_members(member_indices):
            for member_index, (table_row, checkbox) in enumerate(cards):
                keep = member_index in member_indices
                blocker = QtCore.QSignalBlocker(checkbox)
                checkbox.setChecked(keep)
                del blocker
                item = self.duplicate_table.item(table_row, 1)
                item.setCheckState(QtCore.Qt.CheckState.Checked if keep else QtCore.Qt.CheckState.Unchecked)

        for member_index, (_, _checkbox) in enumerate(cards):
            card = cards_layout.itemAt(member_index).widget()
            keep_only = card.findChild(QtWidgets.QPushButton)
            keep_only.clicked.connect(lambda _checked=False, selected=member_index: set_kept_members({selected}))

        scroll.setWidget(cards_panel)
        layout.addWidget(scroll, 1)
        actions = QtWidgets.QHBoxLayout()
        keep_all = QtWidgets.QPushButton(self.translated('Behåll alla i gruppen'))
        keep_all.clicked.connect(lambda: set_kept_members(set(range(len(cards)))))
        actions.addWidget(keep_all)
        actions.addStretch()
        close = QtWidgets.QPushButton(self.translated('Klar'))
        close.clicked.connect(dialog.accept)
        actions.addWidget(close)
        layout.addLayout(actions)
        dialog.exec()

    def move_unselected_duplicates(self):
        keep_by_group = {}
        remove = []
        remove_hashes = {}
        for row in range(self.duplicate_table.rowCount()):
            group_index = int(self.duplicate_table.item(row, 0).text()) - 1
            keep = self.duplicate_table.item(row, 1).checkState() == QtCore.Qt.CheckState.Checked
            keep_by_group[group_index] = keep_by_group.get(group_index, False) or keep
            if not keep:
                path = Path(self.duplicate_table.item(row, 2).data(QtCore.Qt.ItemDataRole.UserRole))
                remove.append(path)
                expected_hash = self.duplicate_groups[group_index].get('hashes', {}).get(str(path))
                if expected_hash:
                    remove_hashes[str(path)] = expected_hash
        if any(not keep_by_group.get(index, False) for index in range(len(self.duplicate_groups))):
            self.show_message('warning', 'Välj filer att behålla', 'Markera minst en fil att behålla i varje dubblettgrupp.')
            return
        if not remove:
            self.show_message('information', 'Inga filer valda', 'Avmarkera kopior som ska flyttas till karantän först.')
            return
        target = OUTPUT_DIR / 'Duplicates' / 'Quarantine' / datetime.now().strftime('%Y%m%d_%H%M%S')
        prompt = self.translated('Flytta {count} omarkerade filer till karantän under MediaForge_Data/Output/Duplicates? Filerna kan återställas manuellt därifrån.').format(count=len(remove))
        if QtWidgets.QMessageBox.question(self, self.translated('Bekräfta karantänflytt'), prompt,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No) != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        source = Path(self.duplicate_source.text()).expanduser().resolve()
        self.duplicate_move_button.setEnabled(False)
        self.duplicate_scan_button.setEnabled(False)
        self.duplicate_cancel_move_button.setEnabled(True)
        self.duplicate_progress.setValue(0)
        self.duplicate_move_worker = DuplicateQuarantineWorker(source, remove, target, remove_hashes)
        self.duplicate_move_worker.message.connect(self.append_duplicate_message)
        self.duplicate_move_worker.message.connect(self.record)
        self.duplicate_move_worker.progress.connect(lambda done, total: (self.duplicate_progress.setMaximum(total), self.duplicate_progress.setValue(done)))
        self.duplicate_move_worker.completed.connect(self.duplicate_move_finished)
        self.duplicate_move_worker.start()

    def cancel_duplicate_move(self):
        worker = getattr(self, 'duplicate_move_worker', None)
        if worker and worker.isRunning():
            worker.cancel()
            self.duplicate_cancel_move_button.setEnabled(False)

    def duplicate_move_finished(self, moved, failed):
        self.duplicate_cancel_move_button.setEnabled(False)
        self.duplicate_scan_button.setEnabled(True)
        self.duplicate_move_button.setEnabled(False)
        text = self.translated('Flytt till karantän klar: {moved} flyttade, {failed} fel.').format(moved=moved, failed=failed)
        self.duplicate_status.setText(text)
        self.duplicate_log.appendPlainText(text)
        if moved:
            QtCore.QTimer.singleShot(150, self.start_duplicate_scan)

    def build_video_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'video')
        self.tabs.addTab(tab, 'Videokonvertering')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Konvertera en mapp med videor till MP4/H.264 med FFmpeg. Källfilerna lämnas orörda.'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.video_source = QtWidgets.QLineEdit(str(self.ui_settings.value('videoSourceFolder', '')))
        self.video_source.setPlaceholderText('Välj mapp med videor…')
        form.addWidget(QtWidgets.QLabel('Videomapp'), 0, 0)
        form.addWidget(self.video_source, 0, 1)
        source_button = QtWidgets.QPushButton('Välj mapp…')
        source_button.clicked.connect(lambda: self.choose_directory(self.video_source, 'Välj videomapp'))
        form.addWidget(source_button, 0, 2)
        self.video_destination = QtWidgets.QLineEdit(self.load_output_setting('videoOutputFolder', OUTPUT_DIR / 'Videos' / 'Converted'))
        form.addWidget(QtWidgets.QLabel('Spara kopior i'), 1, 0)
        form.addWidget(self.video_destination, 1, 1)
        destination_button = QtWidgets.QPushButton('Välj mapp…')
        destination_button.clicked.connect(lambda: self.choose_directory(self.video_destination, 'Välj målmapp'))
        form.addWidget(destination_button, 1, 2)
        self.video_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.video_recursive.setChecked(True)
        layout.addWidget(self.video_recursive)
        options = QtWidgets.QHBoxLayout()
        options.addWidget(QtWidgets.QLabel('Högsta upplösning'))
        self.video_size = QtWidgets.QComboBox()
        self.video_size.addItems(['Behåll originalstorlek', '1080p', '720p'])
        options.addWidget(self.video_size)
        options.addWidget(QtWidgets.QLabel('Kvalitet (CRF; lägre = bättre/större)'))
        self.video_crf = QtWidgets.QSpinBox()
        self.video_crf.setRange(18, 28)
        self.video_crf.setValue(22)
        options.addWidget(self.video_crf)
        layout.addLayout(options)
        layout.addWidget(QtWidgets.QLabel('Kräver FFmpeg i PATH. Kodning använder H.264/AAC och kan minska filstorlek, men är en omkodning med viss kvalitetsförlust.'))
        row = QtWidgets.QHBoxLayout()
        self.video_go = QtWidgets.QPushButton('Konvertera videomapp till MP4')
        self.video_go.clicked.connect(self.start_video_conversion)
        row.addWidget(self.video_go)
        self.video_stop = QtWidgets.QPushButton('Avbryt')
        self.video_stop.setEnabled(False)
        self.video_stop.clicked.connect(self.cancel_video_conversion)
        row.addWidget(self.video_stop)
        layout.addLayout(row)
        self.video_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.video_progress)
        self.video_log = QtWidgets.QPlainTextEdit()
        self.video_log.setReadOnly(True)
        layout.addWidget(self.video_log, 1)

    def build_video_audio_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'video')
        self.tabs.addTab(tab, 'Ljud från video')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Extrahera ljud till MP3, WAV eller FLAC, eller skapa en videokopia där ljudspåren tas bort. Originalfilerna lämnas orörda.'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.audio_source = QtWidgets.QLineEdit(str(self.ui_settings.value('audioSourceFolder', '')))
        self.audio_source.setPlaceholderText('Välj mapp med videor…')
        form.addWidget(QtWidgets.QLabel('Videomapp'), 0, 0)
        form.addWidget(self.audio_source, 0, 1)
        source_button = QtWidgets.QPushButton('Välj mapp…')
        source_button.clicked.connect(lambda: self.choose_directory(self.audio_source, 'Välj videomapp'))
        form.addWidget(source_button, 0, 2)
        self.audio_destination = QtWidgets.QLineEdit(self.load_output_setting('audioOutputFolder', OUTPUT_DIR / 'Videos' / 'AudioTools'))
        form.addWidget(QtWidgets.QLabel('Spara nya filer i'), 1, 0)
        form.addWidget(self.audio_destination, 1, 1)
        destination_button = QtWidgets.QPushButton('Välj mapp…')
        destination_button.clicked.connect(lambda: self.choose_directory(self.audio_destination, 'Välj målmapp'))
        form.addWidget(destination_button, 1, 2)
        self.audio_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.audio_recursive.setChecked(True)
        layout.addWidget(self.audio_recursive)
        options = QtWidgets.QHBoxLayout()
        options.addWidget(QtWidgets.QLabel('Ljudformat'))
        self.audio_format = QtWidgets.QComboBox()
        self.audio_format.addItems(['MP3', 'WAV', 'FLAC'])
        options.addWidget(self.audio_format)
        options.addStretch()
        layout.addLayout(options)
        layout.addWidget(QtWidgets.QLabel('Ljudextrahering konverterar ljudspåret till valt format. Borttagning kopierar videospåret utan omkodning och utan ljudspår. Kräver FFmpeg.'))
        row = QtWidgets.QHBoxLayout()
        self.audio_extract_button = QtWidgets.QPushButton('Extrahera ljud från videor')
        self.audio_extract_button.clicked.connect(lambda: self.start_video_audio('extract'))
        row.addWidget(self.audio_extract_button)
        self.audio_remove_button = QtWidgets.QPushButton('Ta bort ljudspår och spara videokopia')
        self.audio_remove_button.clicked.connect(lambda: self.start_video_audio('remove'))
        row.addWidget(self.audio_remove_button)
        self.audio_cancel_button = QtWidgets.QPushButton('Avbryt')
        self.audio_cancel_button.setEnabled(False)
        self.audio_cancel_button.clicked.connect(self.cancel_video_audio)
        row.addWidget(self.audio_cancel_button)
        layout.addLayout(row)
        self.audio_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.audio_progress)
        self.audio_log = QtWidgets.QPlainTextEdit()
        self.audio_log.setReadOnly(True)
        layout.addWidget(self.audio_log, 1)

    def start_video_audio(self, action):
        if not self.audio_source.text().strip():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig videomapp.')
            return
        source = Path(self.audio_source.text()).expanduser().resolve()
        destination = self.require_app_output(self.audio_destination.text())
        if destination is None:
            return
        if not source.is_dir() or source == destination or source in destination.parents or destination in source.parents:
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig videomapp och en målmapp som inte innehåller källmappen och inte ligger inuti den.')
            return
        if getattr(self, 'audio_worker', None) and self.audio_worker.isRunning():
            return
        action_text = self.translated('Extraherar ljud från') if action == 'extract' else self.translated('Tar bort ljudspår från')
        self.audio_log.appendPlainText(f'{action_text} {source} → {destination}')
        audio_format = self.audio_format.currentText().lower()
        self.audio_worker = VideoAudioWorker(source, destination, self.audio_recursive.isChecked(), action, audio_format)
        self.audio_worker.message.connect(self.append_audio_message)
        self.audio_worker.message.connect(self.record)
        self.audio_worker.progress.connect(lambda done, total: (self.audio_progress.setMaximum(total), self.audio_progress.setValue(done)))
        self.audio_worker.completed.connect(self.video_audio_finished)
        self.audio_extract_button.setEnabled(False)
        self.audio_remove_button.setEnabled(False)
        self.audio_cancel_button.setEnabled(True)
        self.audio_progress.setValue(0)
        self.audio_worker.start()

    def cancel_video_audio(self):
        worker = getattr(self, 'audio_worker', None)
        if worker:
            worker.cancel()
        if hasattr(self, 'audio_cancel_button'):
            self.audio_cancel_button.setEnabled(False)

    def video_audio_finished(self):
        self.audio_extract_button.setEnabled(True)
        self.audio_remove_button.setEnabled(True)
        self.audio_cancel_button.setEnabled(False)

    def start_video_conversion(self):
        source = Path(self.video_source.text()).expanduser().resolve()
        destination = self.require_app_output(self.video_destination.text())
        if destination is None:
            return
        if not source.is_dir() or source == destination or source in destination.parents:
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig videomapp och en separat målmapp utanför källmappen.')
            return
        sizes = [None, (1920, 1080), (1280, 720)]
        self.video_worker = VideoConvertWorker(source, destination, self.video_recursive.isChecked(), self.video_crf.value(), sizes[self.video_size.currentIndex()])
        self.video_worker.message.connect(self.append_video_message)
        self.video_worker.message.connect(self.record)
        self.video_worker.progress.connect(lambda done, total: (self.video_progress.setMaximum(total), self.video_progress.setValue(done)))
        self.video_worker.completed.connect(lambda: (self.video_go.setEnabled(True), self.video_stop.setEnabled(False)))
        self.video_go.setEnabled(False)
        self.video_stop.setEnabled(True)
        self.video_progress.setValue(0)
        self.video_log.appendPlainText(f'Konverterar videor i {source} → {destination}')
        self.video_worker.start()

    def cancel_video_conversion(self):
        if getattr(self, 'video_worker', None):
            self.video_worker.cancel()
            self.video_stop.setEnabled(False)

    def build_color_profile_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'photo')
        self.tabs.addTab(tab, 'Färgprofiler')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Konvertera bilder mellan sRGB, Display P3 och Adobe RGB (1998). Inbäddade profiler används automatiskt; för omärkta bilder väljer du antagen källprofil.'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.color_source = QtWidgets.QLineEdit(str(self.ui_settings.value('colorSourceFolder', '')))
        self.color_source.setPlaceholderText('Välj mapp med bilder…')
        form.addWidget(QtWidgets.QLabel('Bildmapp'), 0, 0)
        form.addWidget(self.color_source, 0, 1)
        choose_source = QtWidgets.QPushButton('Välj mapp…')
        choose_source.clicked.connect(lambda: self.choose_directory(self.color_source, 'Välj bildmapp'))
        form.addWidget(choose_source, 0, 2)
        self.color_destination = QtWidgets.QLineEdit(self.load_output_setting('colorOutputFolder', OUTPUT_DIR / 'Images' / 'ColorProfiles'))
        form.addWidget(QtWidgets.QLabel('Spara kopior i'), 1, 0)
        form.addWidget(self.color_destination, 1, 1)
        choose_destination = QtWidgets.QPushButton('Välj mapp…')
        choose_destination.clicked.connect(lambda: self.choose_directory(self.color_destination, 'Välj målmapp'))
        form.addWidget(choose_destination, 1, 2)
        self.color_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.color_recursive.setChecked(True)
        layout.addWidget(self.color_recursive)
        options = QtWidgets.QHBoxLayout()
        options.addWidget(QtWidgets.QLabel('Antagen profil för bilder utan inbäddad profil'))
        self.color_source_profile = QtWidgets.QComboBox()
        self.color_source_profile.addItems(list(IMAGE_COLOR_PROFILES))
        options.addWidget(self.color_source_profile)
        options.addWidget(QtWidgets.QLabel('Konvertera till'))
        self.color_target_profile = QtWidgets.QComboBox()
        self.color_target_profile.addItems(list(IMAGE_COLOR_PROFILES))
        self.color_target_profile.setCurrentIndex(0)
        options.addWidget(self.color_target_profile)
        layout.addLayout(options)
        layout.addWidget(QtWidgets.QLabel('Bilder sparas i samma filformat. Qt måste ha stöd för bildformatet. Konvertering kan ändra pixelvärden och metadata kanske inte följer med; originalfilerna behålls.'))
        buttons = QtWidgets.QHBoxLayout()
        self.color_go = QtWidgets.QPushButton('Konvertera färgprofiler')
        self.color_go.clicked.connect(self.start_color_conversion)
        buttons.addWidget(self.color_go)
        self.color_cancel = QtWidgets.QPushButton('Avbryt')
        self.color_cancel.setEnabled(False)
        self.color_cancel.clicked.connect(self.cancel_color_conversion)
        buttons.addWidget(self.color_cancel)
        layout.addLayout(buttons)
        self.color_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.color_progress)
        self.color_log = QtWidgets.QPlainTextEdit()
        self.color_log.setReadOnly(True)
        layout.addWidget(self.color_log, 1)

    def start_color_conversion(self):
        if not self.color_source.text().strip():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig bildmapp.')
            return
        source = Path(self.color_source.text()).expanduser().resolve()
        destination = self.require_app_output(self.color_destination.text())
        if destination is None:
            return
        if not source.is_dir() or source == destination or source in destination.parents or destination in source.parents:
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig bildmapp och en målmapp som är skild från källmappen.')
            return
        self.color_worker = ColorProfileWorker(source, destination, self.color_recursive.isChecked(), self.color_source_profile.currentText(), self.color_target_profile.currentText())
        self.color_worker.message.connect(self.append_color_message)
        self.color_worker.message.connect(self.record)
        self.color_worker.progress.connect(lambda done, total: (self.color_progress.setMaximum(total), self.color_progress.setValue(done)))
        self.color_worker.completed.connect(self.color_conversion_finished)
        self.color_go.setEnabled(False)
        self.color_cancel.setEnabled(True)
        self.color_progress.setValue(0)
        self.color_log.appendPlainText(f'{source} → {destination}')
        self.color_worker.start()

    def cancel_color_conversion(self):
        worker = getattr(self, 'color_worker', None)
        if worker:
            worker.cancel()
        self.color_cancel.setEnabled(False)

    def color_conversion_finished(self):
        self.color_go.setEnabled(True)
        self.color_cancel.setEnabled(False)

    def build_video_stabilize_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'video')
        self.tabs.addTab(tab, 'Videostabilisering')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Stabilisera skakiga videor med FFmpeg deshake och spara H.264-kopior. Omkodning kan påverka kvalitet och tar tid; originalen ändras inte.'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.stabilize_source = QtWidgets.QLineEdit(str(self.ui_settings.value('stabilizeSourceFolder', '')))
        self.stabilize_source.setPlaceholderText('Välj mapp med videor…')
        form.addWidget(QtWidgets.QLabel('Videomapp'), 0, 0)
        form.addWidget(self.stabilize_source, 0, 1)
        choose_source = QtWidgets.QPushButton('Välj mapp…')
        choose_source.clicked.connect(lambda: self.choose_directory(self.stabilize_source, 'Välj videomapp'))
        form.addWidget(choose_source, 0, 2)
        self.stabilize_destination = QtWidgets.QLineEdit(self.load_output_setting('stabilizeOutputFolder', OUTPUT_DIR / 'Videos' / 'Stabilized'))
        form.addWidget(QtWidgets.QLabel('Spara kopior i'), 1, 0)
        form.addWidget(self.stabilize_destination, 1, 1)
        choose_destination = QtWidgets.QPushButton('Välj mapp…')
        choose_destination.clicked.connect(lambda: self.choose_directory(self.stabilize_destination, 'Välj målmapp'))
        form.addWidget(choose_destination, 1, 2)
        self.stabilize_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.stabilize_recursive.setChecked(True)
        layout.addWidget(self.stabilize_recursive)
        options = QtWidgets.QHBoxLayout()
        options.addWidget(QtWidgets.QLabel('Styrka'))
        self.stabilize_strength = QtWidgets.QComboBox()
        for label, radius in [('Mild', 8), ('Normal', 16), ('Stark', 24)]:
            self.stabilize_strength.addItem(label, radius)
        options.addWidget(self.stabilize_strength)
        options.addStretch()
        layout.addLayout(options)
        row = QtWidgets.QHBoxLayout()
        self.stabilize_go = QtWidgets.QPushButton('Stabilisera videomapp')
        self.stabilize_go.clicked.connect(self.start_video_stabilization)
        row.addWidget(self.stabilize_go)
        self.stabilize_cancel = QtWidgets.QPushButton('Avbryt')
        self.stabilize_cancel.setEnabled(False)
        self.stabilize_cancel.clicked.connect(self.cancel_video_stabilization)
        row.addWidget(self.stabilize_cancel)
        layout.addLayout(row)
        self.stabilize_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.stabilize_progress)
        self.stabilize_log = QtWidgets.QPlainTextEdit()
        self.stabilize_log.setReadOnly(True)
        layout.addWidget(self.stabilize_log, 1)

    def start_video_stabilization(self):
        if not self.stabilize_source.text().strip():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig videomapp.')
            return
        source = Path(self.stabilize_source.text()).expanduser().resolve()
        destination = self.require_app_output(self.stabilize_destination.text())
        if destination is None:
            return
        if not source.is_dir() or source == destination or source in destination.parents or destination in source.parents:
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig videomapp och en målmapp som är skild från källmappen.')
            return
        self.stabilize_worker = VideoStabilizeWorker(source, destination, self.stabilize_recursive.isChecked(), self.stabilize_strength.currentData())
        self.stabilize_worker.message.connect(self.append_stabilize_message)
        self.stabilize_worker.message.connect(self.record)
        self.stabilize_worker.progress.connect(lambda done, total: (self.stabilize_progress.setMaximum(total), self.stabilize_progress.setValue(done)))
        self.stabilize_worker.completed.connect(self.video_stabilization_finished)
        self.stabilize_go.setEnabled(False)
        self.stabilize_cancel.setEnabled(True)
        self.stabilize_progress.setValue(0)
        self.stabilize_log.appendPlainText(f'{source} → {destination}')
        self.stabilize_worker.start()

    def cancel_video_stabilization(self):
        worker = getattr(self, 'stabilize_worker', None)
        if worker:
            worker.cancel()
        self.stabilize_cancel.setEnabled(False)

    def video_stabilization_finished(self):
        self.stabilize_go.setEnabled(True)
        self.stabilize_cancel.setEnabled(False)

    def build_audio_cleanup_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'video')
        self.tabs.addTab(tab, 'Ljudförbättring')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Normalisera ljudstyrka med EBU-loudness-normalisering eller minska konstant bakgrundsbrus. Ljud bearbetas med FFmpeg; videospåret kopieras utan omkodning.'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.cleanup_source = QtWidgets.QLineEdit(str(self.ui_settings.value('cleanupSourceFolder', '')))
        self.cleanup_source.setPlaceholderText('Välj mapp med ljud eller video…')
        form.addWidget(QtWidgets.QLabel('Källmapp'), 0, 0)
        form.addWidget(self.cleanup_source, 0, 1)
        choose_source = QtWidgets.QPushButton('Välj mapp…')
        choose_source.clicked.connect(lambda: self.choose_directory(self.cleanup_source, 'Välj källmapp'))
        form.addWidget(choose_source, 0, 2)
        self.cleanup_destination = QtWidgets.QLineEdit(self.load_output_setting('cleanupOutputFolder', OUTPUT_DIR / 'Audio' / 'Processed'))
        form.addWidget(QtWidgets.QLabel('Spara bearbetade kopior i'), 1, 0)
        form.addWidget(self.cleanup_destination, 1, 1)
        choose_destination = QtWidgets.QPushButton('Välj mapp…')
        choose_destination.clicked.connect(lambda: self.choose_directory(self.cleanup_destination, 'Välj målmapp'))
        form.addWidget(choose_destination, 1, 2)
        self.cleanup_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.cleanup_recursive.setChecked(True)
        layout.addWidget(self.cleanup_recursive)
        layout.addWidget(QtWidgets.QLabel('Brusreducering kan påverka ljudkvaliteten. Resultat sparas som nya filer; originalen lämnas orörda.'))
        row = QtWidgets.QHBoxLayout()
        self.cleanup_normalize = QtWidgets.QPushButton('Normalisera ljudvolym')
        self.cleanup_normalize.clicked.connect(lambda: self.start_audio_cleanup('normalize'))
        row.addWidget(self.cleanup_normalize)
        self.cleanup_denoise = QtWidgets.QPushButton('Minska bakgrundsbrus')
        self.cleanup_denoise.clicked.connect(lambda: self.start_audio_cleanup('denoise'))
        row.addWidget(self.cleanup_denoise)
        self.cleanup_cancel = QtWidgets.QPushButton('Avbryt')
        self.cleanup_cancel.setEnabled(False)
        self.cleanup_cancel.clicked.connect(self.cancel_audio_cleanup)
        row.addWidget(self.cleanup_cancel)
        layout.addLayout(row)
        self.cleanup_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.cleanup_progress)
        self.cleanup_log = QtWidgets.QPlainTextEdit()
        self.cleanup_log.setReadOnly(True)
        layout.addWidget(self.cleanup_log, 1)

    def start_audio_cleanup(self, action):
        if not self.cleanup_source.text().strip():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig ljud- eller videomapp.')
            return
        source = Path(self.cleanup_source.text()).expanduser().resolve()
        destination = self.require_app_output(self.cleanup_destination.text())
        if destination is None:
            return
        if not source.is_dir() or source == destination or source in destination.parents or destination in source.parents:
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig källmapp och en separat målmapp.')
            return
        self.cleanup_worker = AudioCleanupWorker(source, destination, self.cleanup_recursive.isChecked(), action)
        self.cleanup_worker.message.connect(self.append_cleanup_message)
        self.cleanup_worker.message.connect(self.record)
        self.cleanup_worker.progress.connect(lambda done, total: (self.cleanup_progress.setMaximum(total), self.cleanup_progress.setValue(done)))
        self.cleanup_worker.completed.connect(self.audio_cleanup_finished)
        self.cleanup_normalize.setEnabled(False)
        self.cleanup_denoise.setEnabled(False)
        self.cleanup_cancel.setEnabled(True)
        self.cleanup_progress.setValue(0)
        self.cleanup_log.appendPlainText(f'{source} → {destination}')
        self.cleanup_worker.start()

    def cancel_audio_cleanup(self):
        worker = getattr(self, 'cleanup_worker', None)
        if worker:
            worker.cancel()
        self.cleanup_cancel.setEnabled(False)

    def audio_cleanup_finished(self):
        self.cleanup_normalize.setEnabled(True)
        self.cleanup_denoise.setEnabled(True)
        self.cleanup_cancel.setEnabled(False)

    def build_codec_report_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'video')
        self.tabs.addTab(tab, 'Codec-rapport')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Läs teknisk information om ljud- och videofiler med ffprobe (installeras tillsammans med FFmpeg).'))
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.codec_source = QtWidgets.QLineEdit(str(self.ui_settings.value('codecSourceFolder', '')))
        self.codec_source.setPlaceholderText('Välj mapp med mediafiler…')
        form.addWidget(QtWidgets.QLabel('Källmapp'), 0, 0)
        form.addWidget(self.codec_source, 0, 1)
        choose_source = QtWidgets.QPushButton('Välj mapp…')
        choose_source.clicked.connect(lambda: self.choose_directory(self.codec_source, 'Välj källmapp'))
        form.addWidget(choose_source, 0, 2)
        self.codec_recursive = QtWidgets.QCheckBox('Ta med undermappar')
        self.codec_recursive.setChecked(True)
        layout.addWidget(self.codec_recursive)
        row = QtWidgets.QHBoxLayout()
        self.codec_scan = QtWidgets.QPushButton('Skapa codec-rapport')
        self.codec_scan.clicked.connect(self.start_codec_report)
        row.addWidget(self.codec_scan)
        self.codec_cancel = QtWidgets.QPushButton('Avbryt')
        self.codec_cancel.setEnabled(False)
        self.codec_cancel.clicked.connect(self.cancel_codec_report)
        row.addWidget(self.codec_cancel)
        self.codec_export = QtWidgets.QPushButton('Exportera CSV…')
        self.codec_export.setEnabled(False)
        self.codec_export.clicked.connect(self.export_codec_report)
        row.addWidget(self.codec_export)
        layout.addLayout(row)
        self.codec_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.codec_progress)
        self.codec_log = QtWidgets.QPlainTextEdit()
        self.codec_log.setReadOnly(True)
        self.codec_log.setMaximumHeight(70)
        layout.addWidget(self.codec_log)
        headers = ('Fil', 'Container', 'Längd', 'Video-codec', 'Upplösning', 'Bildfrekvens', 'Video-bitrate', 'Ljud-codec', 'Ljudformat', 'Ljud-bitrate', 'Fel')
        self.codec_table = QtWidgets.QTableWidget(0, len(headers))
        self.codec_table.setHorizontalHeaderLabels([self.translated(header) for header in headers])
        self.codec_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.codec_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.codec_table, 1)
        self.codec_rows = []

    def start_codec_report(self):
        if not self.codec_source.text().strip():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig mapp att skanna.')
            return
        source = Path(self.codec_source.text()).expanduser().resolve()
        if not source.is_dir():
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig mapp att skanna.')
            return
        self.codec_rows = []
        self.codec_table.setRowCount(0)
        self.codec_export.setEnabled(False)
        self.codec_scan.setEnabled(False)
        self.codec_cancel.setEnabled(True)
        self.codec_progress.setValue(0)
        self.codec_worker = CodecReportWorker(source, self.codec_recursive.isChecked())
        self.codec_worker.message.connect(self.append_codec_message)
        self.codec_worker.message.connect(self.record)
        self.codec_worker.progress.connect(lambda done, total: (self.codec_progress.setMaximum(total), self.codec_progress.setValue(done)))
        self.codec_worker.report_ready.connect(self.codec_report_finished)
        self.codec_worker.start()

    def cancel_codec_report(self):
        worker = getattr(self, 'codec_worker', None)
        if worker:
            worker.cancel()
        self.codec_cancel.setEnabled(False)

    def codec_report_finished(self, rows):
        self.codec_rows = rows
        self.codec_scan.setEnabled(True)
        self.codec_cancel.setEnabled(False)
        self.codec_table.setRowCount(len(rows))
        headers = ('Fil', 'Container', 'Längd', 'Video-codec', 'Upplösning', 'Bildfrekvens', 'Video-bitrate', 'Ljud-codec', 'Ljudformat', 'Ljud-bitrate', 'Fel')
        for row_index, row in enumerate(rows):
            for column, key in enumerate(headers):
                item = QtWidgets.QTableWidgetItem(row.get(key, ''))
                item.setToolTip(row.get(key, ''))
                self.codec_table.setItem(row_index, column, item)
        self.codec_export.setEnabled(bool(rows))

    def export_codec_report(self):
        if not self.codec_rows:
            return
        default_path = OUTPUT_DIR / 'Reports' / 'media_codec_report.csv'
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.translated('Exportera codec-rapport'), str(default_path), 'CSV (*.csv)')
        if not path:
            return
        target = self.require_app_output(path)
        if target is None:
            return
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('w', newline='', encoding='utf-8-sig') as stream:
                keys = list(self.codec_rows[0])
                localized_keys = [self.translated(key) for key in keys]
                writer = csv.DictWriter(stream, fieldnames=localized_keys)
                writer.writeheader()
                writer.writerows({self.translated(key): value for key, value in row.items()} for row in self.codec_rows)
            self.show_message('information', 'Export klar', f'CSV sparad: {target}')
        except Exception as exc:
            self.show_message('warning', 'Exportfel', str(exc))

    def build_music_dvd_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'video')
        self.tabs.addTab(tab, 'Skapa musik-DVD')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Samla musikfiler i en DVD-5-kompatibel mapp och skapa en ISO-avbildning om ett ISO-verktyg finns installerat.'))
        warning = QtWidgets.QLabel('Detta är en data-DVD med musikfiler – inte en DVD-Video för alla DVD-spelare. Välj/bränn ISO som skivavbildning, eller bränn mappen som data-DVD.')
        warning.setWordWrap(True)
        layout.addWidget(warning)
        form = QtWidgets.QGridLayout()
        layout.addLayout(form)
        self.music_source = QtWidgets.QLineEdit(str(self.ui_settings.value('musicSourceFolder', '')))
        self.music_source.setPlaceholderText('Välj mapp med musik…')
        form.addWidget(QtWidgets.QLabel('Musikmapp'), 0, 0)
        form.addWidget(self.music_source, 0, 1)
        choose_source = QtWidgets.QPushButton('Välj mapp…')
        choose_source.clicked.connect(lambda: self.choose_directory(self.music_source, 'Välj musikmapp'))
        form.addWidget(choose_source, 0, 2)
        self.music_destination = QtWidgets.QLineEdit(self.load_output_setting('musicOutputFolder', OUTPUT_DIR / 'MusicDVD'))
        form.addWidget(QtWidgets.QLabel('Utmatningsmapp'), 1, 0)
        form.addWidget(self.music_destination, 1, 1)
        choose_dest = QtWidgets.QPushButton('Välj mapp…')
        choose_dest.clicked.connect(lambda: self.choose_directory(self.music_destination, 'Välj utmatningsmapp'))
        form.addWidget(choose_dest, 1, 2)
        self.music_recursive = QtWidgets.QCheckBox('Ta med undermappar (filer samlas i skivans rot)')
        self.music_recursive.setChecked(True)
        layout.addWidget(self.music_recursive)
        layout.addWidget(QtWidgets.QLabel('Stödjer MP3, WAV, FLAC, M4A, AAC, OGG, OPUS, WMA och AIFF. DVD-5 rymmer cirka 4,7 GB.'))
        row = QtWidgets.QHBoxLayout()
        self.music_go = QtWidgets.QPushButton('Skapa musik-DVD')
        self.music_go.clicked.connect(self.start_music_dvd)
        row.addWidget(self.music_go)
        self.music_stop = QtWidgets.QPushButton('Avbryt')
        self.music_stop.setEnabled(False)
        self.music_stop.clicked.connect(self.cancel_music_dvd)
        row.addWidget(self.music_stop)
        layout.addLayout(row)
        self.music_progress = QtWidgets.QProgressBar()
        layout.addWidget(self.music_progress)
        self.music_log = QtWidgets.QPlainTextEdit()
        self.music_log.setReadOnly(True)
        layout.addWidget(self.music_log, 1)

    def choose_directory(self, field, title):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, self.translated(title), field.text() or str(Path.home()))
        if path:
            field.setText(path)

    def start_image_optimization(self):
        source = Path(self.image_source.text()).expanduser().resolve()
        destination = self.require_app_output(self.image_destination.text())
        if destination is None:
            return
        if not source.is_dir() or source == destination or source in destination.parents:
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig bildmapp och en separat målmapp utanför källmappen.')
            return
        self.image_worker = ImageOptimizeWorker(source, destination, self.image_recursive.isChecked(), self.image_strip.isChecked())
        self.image_worker.message.connect(self.append_image_message)
        self.image_worker.message.connect(self.record)
        self.image_worker.progress.connect(lambda done, total: (self.image_progress.setMaximum(total), self.image_progress.setValue(done)))
        self.image_worker.completed.connect(lambda: (self.image_go.setEnabled(True), self.image_stop.setEnabled(False)))
        self.image_go.setEnabled(False)
        self.image_stop.setEnabled(True)
        self.image_progress.setValue(0)
        self.image_log.appendPlainText(f'Optimerar bilder i {source} → {destination}')
        self.image_worker.start()

    def cancel_image_optimization(self):
        if getattr(self, 'image_worker', None):
            self.image_worker.cancelled = True
            self.image_stop.setEnabled(False)

    def start_music_dvd(self):
        source = Path(self.music_source.text()).expanduser().resolve()
        destination = self.require_app_output(self.music_destination.text())
        if destination is None:
            return
        if not source.is_dir() or source == destination or source in destination.parents:
            self.show_message('warning', 'Ogiltig mapp', 'Välj en giltig musikmapp och en separat utmatningsmapp utanför källmappen.')
            return
        self.music_worker = MusicDVDWorker(source, destination, self.music_recursive.isChecked())
        self.music_worker.message.connect(self.append_music_message)
        self.music_worker.message.connect(self.record)
        self.music_worker.progress.connect(lambda done, total: (self.music_progress.setMaximum(total), self.music_progress.setValue(done)))
        self.music_worker.completed.connect(lambda: (self.music_go.setEnabled(True), self.music_stop.setEnabled(False)))
        self.music_go.setEnabled(False)
        self.music_stop.setEnabled(True)
        self.music_progress.setValue(0)
        self.music_log.appendPlainText(f'Samlar musik från {source} → {destination}')
        self.music_worker.start()

    def cancel_music_dvd(self):
        if getattr(self, 'music_worker', None):
            self.music_worker.cancelled = True
            self.music_stop.setEnabled(False)

    def build_log_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'both')
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
            self.activity_log.appendPlainText(self.localize_runtime_text(text))

    def append_worker_message(self, target, text):
        target.appendPlainText(self.localize_runtime_text(text))

    @QtCore.pyqtSlot(str)
    def append_video_message(self, text):
        self.append_worker_message(self.video_log, text)

    @QtCore.pyqtSlot(str)
    def append_audio_message(self, text):
        self.append_worker_message(self.audio_log, text)

    @QtCore.pyqtSlot(str)
    def append_duplicate_message(self, text):
        self.append_worker_message(self.duplicate_log, text)

    @QtCore.pyqtSlot(str)
    def append_color_message(self, text):
        self.append_worker_message(self.color_log, text)

    @QtCore.pyqtSlot(str)
    def append_stabilize_message(self, text):
        self.append_worker_message(self.stabilize_log, text)

    @QtCore.pyqtSlot(str)
    def append_cleanup_message(self, text):
        self.append_worker_message(self.cleanup_log, text)

    @QtCore.pyqtSlot(str)
    def append_codec_message(self, text):
        self.append_worker_message(self.codec_log, text)

    @QtCore.pyqtSlot(str)
    def append_image_message(self, text):
        self.append_worker_message(self.image_log, text)

    @QtCore.pyqtSlot(str)
    def append_music_message(self, text):
        self.append_worker_message(self.music_log, text)

    @QtCore.pyqtSlot(str)
    def append_web_message(self, text):
        self.append_worker_message(self.web_log, text)

    @QtCore.pyqtSlot(str)
    def append_ad_message(self, text):
        self.append_worker_message(self.ad_log, text)

    @QtCore.pyqtSlot(str)
    def append_conversion_message(self, text):
        self.append_worker_message(self.conversion_log, text)

    @QtCore.pyqtSlot(str)
    def append_batch_message(self, text):
        self.append_worker_message(self.log, text)

    def localize_runtime_text(self, text):
        if self.ui_language != 'en':
            return text
        exact = {
            'Avbrutet.': 'Cancelled.',
            'Bildoptimering avbruten.': 'Image optimization cancelled.',
            'Videokonvertering avbruten.': 'Video conversion cancelled.',
            'Konvertering avbruten.': 'Conversion cancelled.',
            'Inga videofiler hittades.': 'No video files found.',
            'Ljud/videojobb avbrutet.': 'Audio/video job cancelled.',
            'INFO: Inga filer hittades i mappen.': 'INFO: No files found in the folder.',
            'INFO: Flytt till karantän avbröts.': 'INFO: Quarantine move cancelled.',
            'INFO: Färgprofilkonvertering avbruten.': 'INFO: Color profile conversion cancelled.',
            'INFO: Videostabilisering avbruten.': 'INFO: Video stabilization cancelled.',
            'INFO: Ljudbearbetning avbruten.': 'INFO: Audio processing cancelled.',
            'INFO: Codec-rapport avbruten.': 'INFO: Codec report cancelled.',
            'INFO: Inga ljud- eller videofiler hittades.': 'INFO: No audio or video files were found.',
            'INFO: Inga mediafiler hittades i mappen.': 'INFO: No media files found in the folder.',
            'Inga stödda bilder hittades (JPG, PNG, WEBP, TIFF, BMP, HEIC/HEIF, AVIF).': 'No supported images found (JPG, PNG, WEBP, TIFF, BMP, HEIC/HEIF, AVIF).',
            'Konverteringen avslutad.': 'Conversion finished.',
            'Bearbetningen avslutad. Kontrollera eventuella DELVIS/FEL ovan.': 'Processing finished. Check any PARTIAL/ERROR messages above.',
            'Mapp MUSIK_DVD är klar att brännas som data-DVD. För ISO-installera xorriso, genisoimage eller mkisofs.': 'The MUSIK_DVD folder is ready to burn as a data DVD. Install xorriso, genisoimage or mkisofs to create an ISO.',
        }
        if text in exact:
            return exact[text]
        replacements = (
            ('KONVERTERINGSFEL:', 'CONVERSION ERROR:'), ('Ljudspår borttaget; video kopierad utan omkodning', 'Audio removed; video copied without re-encoding'), ('Ljudspår extraherat', 'Audio track extracted'), ('Flyttad till karantän:', 'Moved to quarantine:'), ('Kunde inte flytta', 'Could not move'), ('Skanningen klar.', 'Scan complete.'), ('dubblettgrupper hittades.', 'duplicate groups found.'), ('Stabiliserad kopia:', 'Stabilized copy:'), ('Normaliserad:', 'Normalized:'), ('Brusreducerad:', 'Noise reduced:'), ('Färgprofilkonvertering avbruten', 'Color profile conversion cancelled'), ('Videostabilisering avbruten', 'Video stabilization cancelled'), ('Ljudbearbetning avbruten', 'Audio processing cancelled'), ('Codec-rapport klar.', 'Codec report complete.'), ('filer analyserades.', 'files analyzed.'), ('ANNONSFEL', 'AD ERROR'), ('BILDFEL', 'IMAGE ERROR'),
            ('HOPPADES ÖVER:', 'SKIPPED:'), ('KLART:', 'DONE:'), ('KLAR:', 'DONE:'), ('FEL:', 'ERROR:'), ('INFO:', 'INFO:'),
            ('Kopierad:', 'Copied:'), ('Sparad:', 'Saved:'), ('Sparad ', 'Saved '), ('Annons ', 'Ad '),
            (' bilder sparade', ' images saved'), (' hittade ', ' found '), (' unika galleribilder (hämtar samtliga)', ' unique gallery images (downloading all)'),
            (' av ', ' of '), (' byte;', ' bytes;'), (' byte)', ' bytes)'), ('Ingen bildstorlek tillgänglig:', 'No image size available:'),
            ('Inga ljudfiler hittades', 'No audio files found'), ('Inga bilder eller videor hittades.', 'No images or videos found.'),
        )
        for old, new in replacements:
            text = text.replace(old, new)
        return text

    def record(self, text):
        if text.startswith(('FEL', 'BILDFEL', 'ANNONSFEL', 'KONVERTERINGSFEL')) or 'DELVIS' in text:
            LOGGER.error(text)
        else:
            LOGGER.info(text)

    def show_message(self, kind, title, text, *args):
        dialog_method = getattr(QtWidgets.QMessageBox, kind)
        return dialog_method(self, self.translated(title), self.translated(text), *args)

    def translated(self, text):
        if self.ui_language == 'en':
            return UI_TRANSLATIONS.get(text, text)
        inverse = getattr(self, '_inverse_ui_translations', None)
        if inverse is None:
            inverse = {value: key for key, value in UI_TRANSLATIONS.items()}
            self._inverse_ui_translations = inverse
        return inverse.get(text, text)

    def apply_language(self):
        self.setWindowTitle('MediaForge')
        for widget in self.findChildren(QtWidgets.QWidget):
            if isinstance(widget, (QtWidgets.QLabel, QtWidgets.QPushButton, QtWidgets.QCheckBox, QtWidgets.QRadioButton)):
                try:
                    current = widget.text()
                    changed = self.translated(current)
                    if changed != current:
                        widget.setText(changed)
                except (RuntimeError, TypeError):
                    pass
            if hasattr(widget, 'placeholderText') and hasattr(widget, 'setPlaceholderText'):
                current = widget.placeholderText()
                changed = self.translated(current)
                if changed != current:
                    widget.setPlaceholderText(changed)
            if isinstance(widget, QtWidgets.QGroupBox):
                current = widget.title()
                changed = self.translated(current)
                if changed != current:
                    widget.setTitle(changed)
            if isinstance(widget, QtWidgets.QSpinBox):
                current = widget.suffix()
                changed = self.translated(current)
                if changed != current:
                    widget.setSuffix(changed)
            if hasattr(widget, 'empty_text'):
                widget.empty_text = self.translated(widget.empty_text)
                widget.update()
            if isinstance(widget, QtWidgets.QComboBox):
                for index in range(widget.count()):
                    current = widget.itemText(index)
                    changed = self.translated(current)
                    if changed != current:
                        widget.setItemText(index, changed)
        for index in range(self.tabs.count()):
            current = self.tabs.tabText(index)
            self.tabs.setTabText(index, self.translated(current))
        if hasattr(self, 'duplicate_table'):
            self.duplicate_table.setHorizontalHeaderLabels([self.translated(label) for label in ('Grupp', 'Behåll', 'Fil', 'Matchning')])
            for row in range(self.duplicate_table.rowCount()):
                item = self.duplicate_table.item(row, 3)
                if item is not None:
                    item.setText(self.translated(item.text()))
        if hasattr(self, 'codec_table'):
            headers = ('Fil', 'Container', 'Längd', 'Video-codec', 'Upplösning', 'Bildfrekvens', 'Video-bitrate', 'Ljud-codec', 'Ljudformat', 'Ljud-bitrate', 'Fel')
            self.codec_table.setHorizontalHeaderLabels([self.translated(header) for header in headers])

    def change_ui_language(self, index):
        language = self.language_combo.itemData(index)
        if language and language != self.ui_language:
            self.ui_language = language
            self.ui_settings.setValue('language', language)
            self.apply_language()
            LOGGER.info('Interface language changed to %s', language)

    def change_media_mode(self, index):
        mode = self.mode_combo.itemData(index)
        if mode:
            self.media_mode = mode
            self.ui_settings.setValue('mediaMode', mode)
            self.apply_media_mode()
            LOGGER.info('Visible tab mode changed to %s', mode)

    def apply_media_mode(self):
        for index in range(self.tabs.count()):
            category = self.tabs.widget(index).property('mediaMode') or 'both'
            visible = self.media_mode == 'all' or category == 'both' or category == self.media_mode
            self.tabs.setTabVisible(index, visible)
        current = self.tabs.currentWidget()
        if current is not None and not self.tabs.isTabVisible(self.tabs.indexOf(current)):
            visible = [i for i in range(self.tabs.count()) if self.tabs.isTabVisible(i)]
            preferred = next((i for i in visible if self.tabs.widget(i).property('mediaMode') == self.media_mode), None)
            if preferred is None and visible:
                preferred = visible[0]
            if preferred is not None:
                self.tabs.setCurrentIndex(preferred)

    def donation_url(self):
        return SETTINGS_DIR / 'donation_url.txt'

    def configure_donation(self):
        from urllib.parse import urlparse
        current = ''
        try:
            current = self.donation_url().read_text(encoding='utf-8').strip()
        except OSError:
            pass
        value, ok = QtWidgets.QInputDialog.getText(self, self.translated('Ko-fi-donationslänk'), self.translated('Klistra in din personliga Ko-fi-länk (https://ko-fi.com/dittnamn):'), text=current)
        if not ok:
            return
        parsed = urlparse(value.strip())
        if parsed.scheme != 'https' or parsed.hostname not in {'ko-fi.com', 'www.ko-fi.com'} or not parsed.path.strip('/'):
            self.show_message('warning', 'Ogiltig länk', 'Ange en personlig Ko-fi-länk på domänen ko-fi.com, till exempel https://ko-fi.com/dittnamn.')
            return
        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
            self.donation_url().write_text(value.strip(), encoding='utf-8')
            LOGGER.info('Ko-fi-länk sparad lokalt')
            self.show_message('information', 'Sparat', 'Din Ko-fi-länk sparades lokalt i appens inställningsmapp.')
        except OSError as exc:
            self.show_message('warning', 'Kunde inte spara', str(exc))

    def open_donation(self):
        from urllib.parse import urlparse
        from PyQt6.QtGui import QDesktopServices
        try:
            value = self.donation_url().read_text(encoding='utf-8').strip()
        except OSError:
            value = ''
        parsed = urlparse(value)
        if parsed.scheme != 'https' or parsed.hostname not in {'ko-fi.com', 'www.ko-fi.com'}:
            self.configure_donation()
            try:
                value = self.donation_url().read_text(encoding='utf-8').strip()
            except OSError:
                return
        if value:
            QDesktopServices.openUrl(QtCore.QUrl(value))
            LOGGER.info('Ko-fi-donationslänk öppnad')

    def change_autostart(self, enabled):
        try:
            set_autostart(enabled)
            LOGGER.info('Autostart: %s', 'på' if enabled else 'av')
        except Exception as exc:
            LOGGER.exception('Autostart kunde inte ändras')
            self.autostart.blockSignals(True)
            self.autostart.setChecked(not enabled)
            self.autostart.blockSignals(False)
            self.show_message('warning', 'Autostart kunde inte ändras', str(exc))

    def launch_maintenance_launcher(self, windows_flags, unix_flags):
        if sys.platform == 'win32':
            launcher = APP_DIR / 'Starta_Fotoverktyg.ps1'
            if not launcher.is_file():
                raise FileNotFoundError(launcher)
            command = ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', str(launcher), *windows_flags, '-WaitForPid', str(os.getpid())]
            subprocess.Popen(command, cwd=APP_DIR, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        else:
            launcher = APP_DIR / 'start_mediaforge.sh'
            if not launcher.is_file():
                raise FileNotFoundError(launcher)
            command = ['/bin/bash', str(launcher), *unix_flags, '--wait-for-pid', str(os.getpid())]
            if sys.platform == 'darwin':
                import shlex
                SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
                helper = SETTINGS_DIR / 'python_maintenance.command'
                command_line = ' '.join(shlex.quote(part) for part in command)
                helper.write_text(
                    '#!/bin/bash\ncd -- ' + shlex.quote(str(APP_DIR)) + '\n' + command_line + '\n'
                    'status=$?\necho\nprintf "MediaForge updater finished (exit %s). Press Return to close this window." "$status"\n'
                    'read -r _\nexit "$status"\n',
                    encoding='utf-8',
                )
                helper.chmod(0o700)
                subprocess.Popen(['open', '-a', 'Terminal', str(helper)], cwd=APP_DIR)
            else:
                terminal_args = None
                for terminal, prefix in (
                    ('x-terminal-emulator', ['-e']),
                    ('gnome-terminal', ['--']),
                    ('konsole', ['-e']),
                    ('xterm', ['-e']),
                ):
                    executable = shutil.which(terminal)
                    if executable:
                        terminal_args = [executable, *prefix, *command]
                        break
                if terminal_args is None:
                    raise RuntimeError(self.translated('A terminal emulator is required to update Python on this Linux system. Run start_mediaforge.sh from a terminal.'))
                subprocess.Popen(terminal_args, cwd=APP_DIR)
        LOGGER.info('Maintenance task delegated to app-local launcher')
        self.close()

    def update_python_runtime(self):
        prompt = self.translated('Detta stänger MediaForge och startar Python-uppdateringen. Fortsätta?')
        if QtWidgets.QMessageBox.question(
            self, self.translated('Python-uppdatering'), prompt,
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        ) != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            self.launch_maintenance_launcher(['-InstallLatestPython'], ['--install-latest-python'])
        except Exception as exc:
            LOGGER.exception('Could not start Python runtime update')
            self.show_message('critical', 'Python-uppdatering', str(exc))

    def update_all_python_packages(self):
        prompt = self.translated('Detta stänger MediaForge och uppdaterar paketen i appens privata Python-miljö. Fortsätta?')
        if QtWidgets.QMessageBox.question(
            self, self.translated('Python-uppdatering'), prompt,
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        ) != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        try:
            self.launch_maintenance_launcher(['-UpdatePackages'], ['--update-packages'])
        except Exception as exc:
            LOGGER.exception('Could not start Python package update')
            self.show_message('critical', 'Python-uppdatering', str(exc))

    def check_git_update(self):
        self.git_update_button.setEnabled(False)
        self.git_update_button.setText(self.translated('Kontrollerar GitHub main efter uppdateringar…'))
        QtWidgets.QApplication.processEvents()
        try:
            def git(*args):
                return subprocess.run(
                    ['git', '-C', str(APP_DIR), *args], capture_output=True, text=True,
                    encoding='utf-8', errors='replace', timeout=180, check=True,
                ).stdout.strip()

            root = Path(git('rev-parse', '--show-toplevel')).resolve()
            if root != APP_DIR.resolve():
                raise RuntimeError(self.translated('Endast en Git-arbetskopia på grenen main kan uppdateras.'))
            branch = git('branch', '--show-current')
            if branch != UPDATE_BRANCH:
                raise RuntimeError(self.translated('Endast en Git-arbetskopia på grenen main kan uppdateras.'))
            origin = git('remote', 'get-url', 'origin').rstrip('/').removesuffix('.git')
            expected = UPDATE_REMOTE_URL.removesuffix('.git')
            if origin not in {expected, 'git@github.com:Tokke2/MediaConverterPro'}:
                raise RuntimeError(self.translated('Endast en Git-arbetskopia på grenen main kan uppdateras.'))
            if git('status', '--porcelain', '--untracked-files=all'):
                raise RuntimeError(self.translated('Git-arbetskopian innehåller ändringar. Spara, stash:a eller återställ dem innan uppdatering.'))
            local = git('rev-parse', 'HEAD')
            git('fetch', '--quiet', UPDATE_REMOTE_URL, UPDATE_BRANCH)
            remote = git('rev-parse', 'FETCH_HEAD')
            if git('status', '--porcelain', '--untracked-files=all'):
                raise RuntimeError(self.translated('Git-arbetskopian innehåller ändringar. Spara, stash:a eller återställ dem innan uppdatering.'))
            if local == remote:
                self.show_message('information', 'GitHub-uppdatering', 'MediaForge är redan uppdaterat.')
                return
            ancestry = subprocess.run(
                ['git', '-C', str(APP_DIR), 'merge-base', '--is-ancestor', 'HEAD', 'FETCH_HEAD'],
                capture_output=True, text=True, timeout=30,
            )
            if ancestry.returncode != 0:
                raise RuntimeError(self.translated('Endast en Git-arbetskopia på grenen main kan uppdateras.'))
            text = self.translated('Uppdatering tillgänglig: {local} → {remote}. Uppdatera nu? Endast snabbspolning tillåts.').format(local=local[:10], remote=remote[:10])
            reply = QtWidgets.QMessageBox.question(
                self, self.translated('GitHub-uppdatering'), text,
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if reply != QtWidgets.QMessageBox.StandardButton.Yes:
                return
            if git('status', '--porcelain', '--untracked-files=all'):
                raise RuntimeError(self.translated('Git-arbetskopian innehåller ändringar. Spara, stash:a eller återställ dem innan uppdatering.'))
            git('merge', '--ff-only', 'FETCH_HEAD')
            LOGGER.info('GitHub main update completed: %s -> %s', local, remote)
            self.show_message('information', 'GitHub-uppdatering', 'Uppdateringen är klar. Starta om MediaForge för att använda den nya versionen.')
        except Exception as exc:
            LOGGER.exception('GitHub update check failed')
            self.show_message('warning', 'GitHub-uppdatering', self.translated('Git-uppdateringen misslyckades:') + '\\n' + str(exc))
        finally:
            self.git_update_button.setEnabled(True)
            self.git_update_button.setText(self.translated('Kontrollera GitHub main-uppdatering…'))

    def offer_missing_dependencies(self):
        import importlib.util
        missing = [name for module, name in [('pillow_heif', 'pillow-heif'), ('piexif', 'piexif')] if importlib.util.find_spec(module) is None]
        if missing:
            reply = self.show_message('question', 'Saknade tillägg', self.translated('Installera saknade frivilliga Python-tillägg?') + '\n' + ', '.join(missing) + '\n' + self.translated('Ingenting installeras utan ditt godkännande.'))
            if reply == QtWidgets.QMessageBox.StandardButton.Yes:
                self.install_packages(missing)

    def manage_dependencies(self):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle(self.translated('Python-tillägg'))
        dialog.setText(self.translated('Installera/uppdatera Pillow, pillow-heif och piexif?\nDetta använder samma Python-miljö som appen.\nPyQt6 uppdateras inte medan appen körs; uppdatera det efter att appen stängts.'))
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
        self.show_message('information', 'Installation' if ok else 'Installationsfel', ('Klart. Starta om appen för att aktivera tilläggen.\n\n' if ok else 'Installationen misslyckades.\n\n') + output)

    def build_web_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'photo')
        self.tabs.addTab(tab, 'Webbbilder → JPEG')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Direkta HTTPS-länkar till bildfiler. En länk per rad; stöder JPG, PNG, WEBP, AVIF och HEIC.'))
        self.web_urls = QtWidgets.QPlainTextEdit()
        self.web_urls.setPlaceholderText('https://www.wermlandopera.com/wp-content/smush-webp/2026/05/wo_doing_toppbild_2000x670.jpg.webp')
        layout.addWidget(self.web_urls)
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        row.addWidget(QtWidgets.QLabel('Basmapp:'))
        self.web_destination = QtWidgets.QLineEdit(self.load_output_setting('webOutputFolder', OUTPUT_DIR / 'Downloads' / 'WebImages'))
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
        path = QtWidgets.QFileDialog.getExistingDirectory(self, self.translated('Välj basmapp för webbbilder'))
        if path:
            self.web_destination.setText(path)

    def start_web_download(self):
        import re
        from urllib.parse import urlparse
        if self.web_worker and self.web_worker.isRunning():
            return
        urls = list(dict.fromkeys(x.strip() for x in self.web_urls.toPlainText().splitlines() if x.strip()))
        if not urls or not self.web_destination.text().strip():
            self.show_message('information', 'Välj länkar', 'Ange bildlänkar och en basmapp.')
            return
        if any(urlparse(u).scheme != 'https' or not urlparse(u).path.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.avif', '.heic')) or re.search(r'blocket\.se/(?:mobility|recommerce)/item/', u) for u in urls):
            self.show_message('warning', 'Fel länkar', 'Använd direkta HTTPS-bildlänkar här. Blocket-annonser hör hemma i Blocket-fliken.')
            return
        destination = self.require_app_output(self.web_destination.text())
        if destination is None:
            return
        self.web_worker = BlocketWorker(urls, destination, self.web_quality.value())
        self.web_worker.message.connect(self.append_web_message)
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
        tab.setProperty('mediaMode', 'photo')
        self.tabs.addTab(tab, 'Blocket → JPEG')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Klistra in Blocket-annonser från /mobility/item/ eller /recommerce/forsale/item/, en per rad. Varje annons får en mapp med sin titel.'))
        self.ad_urls = QtWidgets.QPlainTextEdit()
        self.ad_urls.setPlaceholderText('https://www.blocket.se/mobility/item/24141675\nhttps://www.blocket.se/recommerce/forsale/item/27022380')
        layout.addWidget(self.ad_urls)
        row = QtWidgets.QHBoxLayout()
        layout.addLayout(row)
        row.addWidget(QtWidgets.QLabel('Spara i:'))
        self.ad_destination = QtWidgets.QLineEdit(self.load_output_setting('adOutputFolder', OUTPUT_DIR / 'Downloads' / 'Blocket'))
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
        path = QtWidgets.QFileDialog.getExistingDirectory(self, self.translated('Välj bildmapp'))
        if path:
            self.ad_destination.setText(path)

    def start_ad_download(self):
        if self.ad_worker and self.ad_worker.isRunning():
            return
        urls = list(dict.fromkeys(x.strip() for x in self.ad_urls.toPlainText().splitlines() if x.strip()))
        if not urls:
            self.show_message('information', 'Ange länkar', 'Ange minst en annonslänk.')
            return
        import re
        if any(not re.fullmatch(r'https://(?:www\.)?blocket\.se/(?:mobility|recommerce/forsale)/item/\d+(?:[/?#].*)?', u) for u in urls):
            self.show_message('warning', 'Fel länkar', 'Använd Blocket-annonslänkar här. Direkta bilder hör hemma i Webbbilder-fliken.')
            return
        if not self.ad_destination.text().strip():
            self.browse_ad_destination()
            if not self.ad_destination.text().strip():
                return
        destination = self.require_app_output(self.ad_destination.text())
        if destination is None:
            return
        self.ad_worker = BlocketWorker(urls, destination, self.ad_quality.value())
        self.ad_worker.message.connect(self.append_ad_message)
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
            self.show_message('warning', 'Kunde inte öppna mappen', f'Bilderna sparades i: {folder}')
        else:
            LOGGER.info('Output-mapp öppnad: %s', folder)

    def build_conversion_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'photo')
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
        self.conversion_destination = QtWidgets.QLineEdit(self.load_output_setting('conversionOutputFolder', OUTPUT_DIR / 'Images' / 'JPEG'))
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
        paths, _ = QtWidgets.QFileDialog.getOpenFileNames(self, self.translated('Välj AVIF/HEIC-bilder'), '', 'AVIF/HEIC (*.avif *.heic *.heif)')
        existing = {self.conversion_list.item(i).text() for i in range(self.conversion_list.count())}
        for path in paths:
            if path not in existing:
                self.conversion_list.addItem(path)

    def browse_conversion_destination(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, self.translated('Välj JPEG-mapp'))
        if path:
            self.conversion_destination.setText(path)

    def start_conversion(self):
        if self.conversion_worker and self.conversion_worker.isRunning():
            return
        files = [Path(self.conversion_list.item(i).text()) for i in range(self.conversion_list.count())]
        if not files or not self.conversion_destination.text().strip():
            self.show_message('information', 'Välj bilder', 'Välj bilder och målmapp först.')
            return
        destination = self.require_app_output(self.conversion_destination.text())
        if destination is None:
            return
        self.conversion_worker = ConversionWorker(files, destination, self.jpeg_quality.value(), self.conversion_metadata.isChecked())
        self.conversion_worker.message.connect(self.append_conversion_message)
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

    def build_library_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'photo')
        self.library_tab = tab
        self.tabs.addTab(tab, 'Bildbibliotek')
        layout = QtWidgets.QVBoxLayout(tab)
        layout.addWidget(QtWidgets.QLabel('Öppna en bildmapp och bläddra bland originalen. Bilder kopieras eller ändras inte.'))
        location = QtWidgets.QGridLayout()
        layout.addLayout(location)
        self.library_source = DropEdit()
        self.library_source.setText(str(self.ui_settings.value('libraryFolder', '')))
        self.library_source.setPlaceholderText('Bildmapp')
        location.addWidget(QtWidgets.QLabel('Bildmapp'), 0, 0)
        location.addWidget(self.library_source, 0, 1)
        self.library_open_button = QtWidgets.QPushButton('Öppna bildmapp…')
        self.library_open_button.clicked.connect(self.choose_image_library)
        location.addWidget(self.library_open_button, 0, 2)
        self.library_refresh_button = QtWidgets.QPushButton('Uppdatera lista')
        self.library_refresh_button.clicked.connect(self.scan_image_library)
        location.addWidget(self.library_refresh_button, 0, 3)
        self.library_recursive = QtWidgets.QCheckBox('Inkludera undermappar')
        self.library_recursive.setChecked(self.ui_settings.value('libraryRecursive', True, type=bool))
        layout.addWidget(self.library_recursive)

        splitter = QtWidgets.QSplitter(QtCore.Qt.Orientation.Horizontal)
        self.library_grid = QtWidgets.QListWidget()
        self.library_grid.setViewMode(QtWidgets.QListView.ViewMode.IconMode)
        self.library_grid.setResizeMode(QtWidgets.QListView.ResizeMode.Adjust)
        self.library_grid.setMovement(QtWidgets.QListView.Movement.Static)
        self.library_grid.setWrapping(True)
        self.library_grid.setWordWrap(True)
        self.library_grid.setIconSize(QtCore.QSize(144, 108))
        self.library_grid.setGridSize(QtCore.QSize(166, 148))
        self.library_grid.setMinimumWidth(230)
        self.library_grid.currentRowChanged.connect(self.show_library_image)
        self.library_grid.itemDoubleClicked.connect(lambda _item: self.show_library_fullscreen())
        splitter.addWidget(self.library_grid)

        preview_panel = QtWidgets.QWidget()
        preview_layout = QtWidgets.QVBoxLayout(preview_panel)
        self.library_preview = FitImageLabel()
        self.library_preview.setText('Välj en bild från listan.')
        self.library_preview.setStyleSheet('background: #0b1220; border-radius: 8px;')
        preview_layout.addWidget(self.library_preview, 1)
        self.library_image_info = QtWidgets.QLabel('')
        self.library_image_info.setWordWrap(True)
        preview_layout.addWidget(self.library_image_info)
        controls = QtWidgets.QHBoxLayout()
        self.library_previous_button = QtWidgets.QPushButton('Föregående')
        self.library_previous_button.clicked.connect(lambda: self.step_library_image(-1))
        controls.addWidget(self.library_previous_button)
        self.library_next_button = QtWidgets.QPushButton('Nästa')
        self.library_next_button.clicked.connect(lambda: self.step_library_image(1))
        controls.addWidget(self.library_next_button)
        self.library_fullscreen_button = QtWidgets.QPushButton('Helskärm')
        self.library_fullscreen_button.clicked.connect(self.show_library_fullscreen)
        controls.addWidget(self.library_fullscreen_button)
        self.library_print_button = QtWidgets.QPushButton('Skriv ut…')
        self.library_print_button.clicked.connect(self.print_library_image)
        controls.addWidget(self.library_print_button)
        preview_layout.addLayout(controls)
        splitter.addWidget(preview_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)
        splitter.splitterMoved.connect(self.schedule_library_thumbnail_batch)
        self.library_grid.verticalScrollBar().valueChanged.connect(self.schedule_library_thumbnail_batch)
        self.library_grid.horizontalScrollBar().valueChanged.connect(self.schedule_library_thumbnail_batch)
        layout.addWidget(splitter, 1)
        self.library_status = QtWidgets.QLabel('Bildformat som stöds: JPEG, PNG, WEBP, TIFF, BMP, GIF och (med pillow-heif) HEIC/HEIF/AVIF.')
        self.library_status.setWordWrap(True)
        layout.addWidget(self.library_status)
        self.library_previous_button.setEnabled(False)
        self.library_next_button.setEnabled(False)
        self.library_fullscreen_button.setEnabled(False)
        self.library_print_button.setEnabled(False)

    def choose_image_library(self):
        start = self.library_source.text().strip() or str(Path.home())
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, self.translated('Öppna bildmapp…'), start)
        if folder:
            self.library_source.setText(folder)
            self.scan_image_library()

    def scan_image_library(self):
        raw_folder = self.library_source.text().strip()
        if not raw_folder:
            self.show_message('warning', 'Fel', 'Välj en giltig bildmapp.')
            return
        folder = Path(raw_folder).expanduser().resolve()
        if not folder.is_dir():
            self.show_message('warning', 'Fel', 'Välj en giltig bildmapp.')
            return
        if self.library_scan_worker and self.library_scan_worker.isRunning():
            return
        self.library_source.setText(str(folder))
        self.library_grid.clear()
        self.library_paths = []
        self.library_thumbnail_indices = []
        self.library_current_qimage = None
        self.library_preview.set_image(None)
        self.library_image_info.clear()
        self.library_status.setText(self.translated('Skannar bildmappen…'))
        self.library_open_button.setEnabled(False)
        self.library_refresh_button.setEnabled(False)
        self.library_scan_worker = ImageLibraryScanWorker(folder, self.library_recursive.isChecked(), register_modern_formats())
        self.library_scan_worker.scan_completed.connect(self.image_library_scan_finished)
        self.library_scan_worker.message.connect(self.append_library_message)
        self.library_scan_worker.start()

    @QtCore.pyqtSlot(str)
    def append_library_message(self, message):
        if message.startswith('Kunde inte läsa mappen:'):
            message = self.translated('Kunde inte läsa mappen:') + message.split(':', 1)[-1]
        self.library_status.setText(message)
        LOGGER.warning(message)

    def image_library_scan_finished(self, paths, cancelled):
        self.library_open_button.setEnabled(True)
        self.library_refresh_button.setEnabled(True)
        if cancelled:
            self.library_status.setText(self.translated('Skanningen avbröts.'))
            return
        self.library_paths = list(paths)
        self.library_grid.clear()
        if not self.library_paths:
            self.library_status.setText(self.translated('Inga bilder hittades.'))
            self.library_image_info.clear()
            return
        self.library_status.setText(self.translated('Bilder hittade: {count}').format(count=len(self.library_paths)))
        self.library_populate_cursor = 0
        self.library_thumbnail_indices = []
        self.populate_library_items_batch()
        LOGGER.info('Bildbibliotek öppnat: %s (%d bilder)', self.library_source.text(), len(self.library_paths))

    def populate_library_items_batch(self):
        stop = min(self.library_populate_cursor + 250, len(self.library_paths))
        for path in self.library_paths[self.library_populate_cursor:stop]:
            item = QtWidgets.QListWidgetItem(path.name)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, str(path))
            item.setToolTip(str(path))
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter | QtCore.Qt.AlignmentFlag.AlignBottom)
            self.library_grid.addItem(item)
        self.library_populate_cursor = stop
        if stop < len(self.library_paths):
            QtCore.QTimer.singleShot(1, self.populate_library_items_batch)
            return
        selected_row = 0
        if self.library_pending_selection is not None:
            selected_path = self.library_pending_selection
            self.library_pending_selection = None
            selected_row = next((index for index, path in enumerate(self.library_paths) if path.resolve() == selected_path), 0)
        self.library_grid.setCurrentRow(selected_row)
        QtCore.QTimer.singleShot(0, self.load_library_thumbnail_batch)

    def schedule_library_thumbnail_batch(self, *_args):
        if not self.library_thumbnail_timer_pending and self.library_paths:
            self.library_thumbnail_timer_pending = True
            QtCore.QTimer.singleShot(0, self.load_library_thumbnail_batch)

    def load_library_thumbnail_batch(self):
        self.library_thumbnail_timer_pending = False
        count = min(self.library_grid.count(), len(self.library_paths))
        if count == 0:
            return
        viewport = self.library_grid.viewport()
        first_item = self.library_grid.itemAt(QtCore.QPoint(2, 2))
        last_item = self.library_grid.itemAt(QtCore.QPoint(max(2, viewport.width() - 2), max(2, viewport.height() - 2)))
        start = self.library_grid.row(first_item) if first_item is not None else max(0, self.library_grid.currentRow())
        stop = self.library_grid.row(last_item) + 1 if last_item is not None else min(count, start + 24)
        if stop <= start:
            stop = min(count, start + 24)
        stop = min(count, max(stop, start + 1))
        thumbnail_role = QtCore.Qt.ItemDataRole.UserRole + 1
        processed = 0
        for index in range(start, stop):
            if processed >= 24:
                break
            item = self.library_grid.item(index)
            if item is None or item.data(thumbnail_role):
                continue
            path = self.library_paths[index]
            try:
                qimage, _ = image_file_to_qimage(path, (144, 108))
                item.setIcon(QtGui.QIcon(QtGui.QPixmap.fromImage(qimage)))
                item.setData(thumbnail_role, True)
                self.library_thumbnail_indices.append(index)
            except Exception as exc:
                item.setToolTip(f'{path}\n{exc}')
                item.setData(thumbnail_role, True)
            processed += 1

        for _ in range(len(self.library_thumbnail_indices)):
            if len(self.library_thumbnail_indices) <= 300:
                break
            old_index = self.library_thumbnail_indices.pop(0)
            if start <= old_index < stop or old_index == self.library_grid.currentRow():
                self.library_thumbnail_indices.append(old_index)
                continue
            old_item = self.library_grid.item(old_index)
            if old_item is not None:
                old_item.setIcon(QtGui.QIcon())
                old_item.setData(thumbnail_role, False)

        needs_more = any(not self.library_grid.item(index).data(thumbnail_role) for index in range(start, stop) if self.library_grid.item(index) is not None)
        if needs_more:
            self.schedule_library_thumbnail_batch()

    def show_library_image(self, row):
        if not 0 <= row < len(self.library_paths):
            self.library_current_qimage = None
            self.library_preview.set_image(None)
            self.library_image_info.clear()
            self.library_previous_button.setEnabled(False)
            self.library_next_button.setEnabled(False)
            self.library_fullscreen_button.setEnabled(False)
            self.library_print_button.setEnabled(False)
            return
        path = self.library_paths[row]
        try:
            qimage, dimensions = image_file_to_qimage(path, (2400, 1800))
            self.library_current_qimage = qimage
            self.library_preview.set_image(qimage)
            self.library_image_info.setText(self.translated('Bild {current} av {total} · {name} · {width} × {height}').format(current=row + 1, total=len(self.library_paths), name=path.name, width=dimensions[0], height=dimensions[1]))
            self.library_previous_button.setEnabled(row > 0)
            self.library_next_button.setEnabled(row < len(self.library_paths) - 1)
            self.library_fullscreen_button.setEnabled(True)
            self.library_print_button.setEnabled(True)
        except Exception as exc:
            self.library_current_qimage = None
            self.library_preview.setText(f"{self.translated('Kunde inte visa bilden:')}\n{path.name}\n{exc}")
            self.library_image_info.setText(str(path))
            self.library_fullscreen_button.setEnabled(False)
            self.library_print_button.setEnabled(False)
            LOGGER.warning('Kunde inte läsa bild %s: %s', path, exc)

    def step_library_image(self, amount):
        row = self.library_grid.currentRow()
        if self.library_paths:
            self.library_grid.setCurrentRow(max(0, min(len(self.library_paths) - 1, row + amount)))

    def show_library_fullscreen(self):
        row = self.library_grid.currentRow()
        if 0 <= row < len(self.library_paths):
            FullScreenImageViewer(self.library_paths, row, self).exec()

    def print_library_image(self):
        row = self.library_grid.currentRow()
        if not 0 <= row < len(self.library_paths):
            self.show_message('information', 'Välj en bild', 'Välj en bild först.')
            return
        path = self.library_paths[row]
        try:
            qimage, _ = image_file_to_qimage(path)
        except Exception as exc:
            self.show_message('warning', 'Fel', str(exc))
            return
        printer = QtPrintSupport.QPrinter(QtPrintSupport.QPrinter.PrinterMode.HighResolution)
        printer.setDocName(path.name)
        orientation = QtGui.QPageLayout.Orientation.Landscape if qimage.width() > qimage.height() else QtGui.QPageLayout.Orientation.Portrait
        printer.setPageOrientation(orientation)
        dialog = QtPrintSupport.QPrintDialog(printer, self)
        dialog.setWindowTitle(self.translated('Skriv ut…'))
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            self.library_status.setText(self.translated('Utskrift avbruten.'))
            return
        painter = QtGui.QPainter()
        try:
            if not painter.begin(printer):
                raise RuntimeError(self.translated('Kunde inte starta vald skrivare.'))
            page = printer.pageLayout().paintRectPixels(printer.resolution())
            fitted = qimage.size().scaled(page.size(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
            target = QtCore.QRect(page.x() + (page.width() - fitted.width()) // 2, page.y() + (page.height() - fitted.height()) // 2, fitted.width(), fitted.height())
            painter.drawImage(target, qimage)
            painter.end()
            self.library_status.setText(self.translated('Skickat till skrivaren: {name}').format(name=path.name))
            LOGGER.info('Foto skickat till utskrift: %s', path)
        except Exception as exc:
            if painter.isActive():
                painter.end()
            self.library_status.setText(f"{self.translated('Kunde inte skriva ut bilden:')} {exc}")
            self.show_message('warning', 'Fel', str(exc))

    def build_editor_tab(self):
        tab = QtWidgets.QWidget()
        tab.setProperty('mediaMode', 'photo')
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
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, self.translated('Öppna foto'), '', 'Bilder (*.jpg *.jpeg *.png *.webp *.tif *.tiff *.bmp)')
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
            self.show_message('warning', 'Fel', str(exc))

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
            self.show_message('information', 'Klipp', 'Dra en tydlig markering på bilden först.')
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
            self.show_message('information', 'Välj foto', 'Öppna ett foto först.')
            return
        editor_output = OUTPUT_DIR / 'Images' / 'Edited'
        editor_output.mkdir(parents=True, exist_ok=True)
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.translated('Spara redigerad kopia'), str(editor_output / (self.editor_source.stem + '_edited.png')), 'PNG (*.png);;JPEG (*.jpg);;WEBP (*.webp)')
        if not path:
            return
        target = self.require_app_output(path)
        if target is None:
            return
        if target.resolve() == self.editor_source.resolve():
            self.show_message('warning', 'Original', 'Välj ett annat filnamn så originalet inte skrivs över.')
            return
        if target.suffix.lower() not in {'.png', '.jpg', '.webp'}:
            target = target.with_suffix('.png')
        if target.exists() and self.show_message('question', 'Skriv över?', f'Skriva över {target}?') != QtWidgets.QMessageBox.StandardButton.Yes:
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
            self.show_message('information', 'Klart', f'Sparad: {target}')
        except Exception as exc:
            self.show_message('warning', 'Fel', str(exc))

    def toggle_theme(self):
        self.dark = not self.dark
        self.ui_settings.setValue('darkTheme', self.dark)
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
        path = QtWidgets.QFileDialog.getExistingDirectory(self, self.translated('Välj källmapp'))
        if path:
            self.source.setText(path)

    def browse_archive(self):
        path = QtWidgets.QFileDialog.getExistingDirectory(self, self.translated('Välj arkivmapp'))
        if path:
            self.archive.setText(path)

    def export_log(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, self.translated('Spara logg'), str(LOG_DIR / 'MediaForge-log.txt'), 'Text (*.txt)')
        if path:
            path = self.require_app_output(path)
            if path is None:
                return
            try:
                for h in LOGGER.handlers:
                    h.flush()
                parts = [f.read_text(encoding='utf-8') for f in [Path(str(LOG_FILE) + f'.{n}') for n in (3, 2, 1)] + [LOG_FILE] if f.exists()]
                content = '\n'.join(parts) if parts else self.activity_log.toPlainText()
                Path(path).write_text(content, encoding='utf-8')
                LOGGER.info('Logg exporterad: %s', path)
            except Exception as exc:
                LOGGER.exception('Loggexport misslyckades')
                self.show_message('warning', 'Loggfel', str(exc))

    def start(self):
        if self.worker and self.worker.isRunning():
            return
        root = Path(self.source.text()).expanduser().resolve()
        archive = self.require_app_output(self.archive.text())
        if archive is None:
            return
        if not self.source.text() or not root.is_dir() or not self.archive.text():
            self.show_message('warning', 'Fel', 'Välj en giltig källmapp och arkivmapp.')
            return
        if root == archive or (root in archive.parents and not self.recursive.isChecked()):
            if root == archive:
                self.show_message('warning', 'Fel', 'Arkivmappen måste skilja sig från källmappen.')
                return
        candidates = root.rglob('*') if self.recursive.isChecked() else root.iterdir()
        items = sorted(p for p in candidates if p.is_file() and p.suffix.lower() in MEDIA and archive not in (p, *p.parents) and not any(part.startswith('.') for part in p.relative_to(root).parts))
        if not items:
            self.show_message('information', 'Inga filer', 'Inga bilder eller videor hittades.')
            return
        days, hours, minutes, seconds = [spin.value() for spin in self.offset_spins]
        delta = timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        if self.sign.currentIndex():
            delta = -delta
        settings = dict(root=root, archive=archive, structure=self.structure.isChecked(), overwrite=self.overwrite.isChecked(), enhance=self.enhance_box.isChecked(), factor=self.factor.currentIndex()+1, sharp=self.sliders['Skärpa'].value(), color=self.sliders['Färgstyrka'].value(), clarity=self.sliders['Klarhet/kontrast'].value(), keep_exif=self.keep_exif.isChecked(), offset=self.offset.isChecked(), delta=delta, date=self.date_edit.dateTime().toPyDateTime(), metadata=self.meta.isChecked(), filesystem=self.fs.isChecked(), strip=self.strip.isChecked(), remove_all=self.remove_all.isChecked())
        self.worker = Worker(items, settings)
        self.worker.message.connect(self.append_batch_message)
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

    def restore_preferences(self):
        checkbox_keys = {
            'enhanceImages': 'enhance_box', 'keepExifOnExport': 'keep_exif',
            'writeMetadataDates': 'meta', 'writeFileDates': 'fs', 'stripSoftwareMetadata': 'strip',
            'removeAllMetadata': 'remove_all', 'recursiveFolders': 'recursive',
            'preserveFolderStructure': 'structure', 'overwriteArchive': 'overwrite',
            'imageRecursive': 'image_recursive', 'imageStripMetadata': 'image_strip', 'libraryRecursive': 'library_recursive',
            'videoRecursive': 'video_recursive', 'audioRecursive': 'audio_recursive', 'duplicateRecursive': 'duplicate_recursive', 'colorRecursive': 'color_recursive', 'stabilizeRecursive': 'stabilize_recursive', 'cleanupRecursive': 'cleanup_recursive', 'codecRecursive': 'codec_recursive', 'musicRecursive': 'music_recursive',
            'conversionKeepMetadata': 'conversion_metadata',
        }
        for key, attribute in checkbox_keys.items():
            widget = getattr(self, attribute, None)
            if widget is not None:
                value = self.ui_settings.value(key, widget.isChecked(), type=bool)
                widget.setChecked(value)
        slider_keys = {'sharpness': 'Skärpa', 'colorStrength': 'Färgstyrka', 'clarity': 'Klarhet/kontrast'}
        for key, label in slider_keys.items():
            if label in self.sliders:
                self.sliders[label].setValue(int(self.ui_settings.value(key, self.sliders[label].value())))
        for key, attribute in {'scaleFactor': 'factor', 'videoSizeLimit': 'video_size', 'audioFormat': 'audio_format', 'colorSourceProfile': 'color_source_profile', 'colorTargetProfile': 'color_target_profile', 'stabilizeStrength': 'stabilize_strength', 'webQuality': 'web_quality', 'adQuality': 'ad_quality', 'jpegQuality': 'jpeg_quality', 'videoCrf': 'video_crf'}.items():
            widget = getattr(self, attribute, None)
            if widget is not None:
                value = int(self.ui_settings.value(key, widget.currentIndex() if isinstance(widget, QtWidgets.QComboBox) else widget.value()))
                if isinstance(widget, QtWidgets.QComboBox):
                    widget.setCurrentIndex(max(0, min(value, widget.count() - 1)))
                else:
                    widget.setValue(value)
        date_mode = self.ui_settings.value('dateMode', 'absolute')
        self.absolute.setChecked(date_mode != 'offset')
        self.offset.setChecked(date_mode == 'offset')
        self.sign.setCurrentIndex(int(self.ui_settings.value('dateOffsetSign', self.sign.currentIndex())))
        values = self.ui_settings.value('dateOffsetParts', [spin.value() for spin in self.offset_spins])
        try:
            for spin, value in zip(self.offset_spins, values):
                spin.setValue(int(value))
        except (TypeError, ValueError):
            pass

    def save_preferences(self):
        fields = {
            'sourceFolder': 'source', 'archiveFolder': 'archive',
            'imageSourceFolder': 'image_source', 'imageOutputFolder': 'image_destination', 'libraryFolder': 'library_source',
            'videoSourceFolder': 'video_source', 'videoOutputFolder': 'video_destination',
            'audioSourceFolder': 'audio_source', 'audioOutputFolder': 'audio_destination',
            'duplicateSourceFolder': 'duplicate_source',
            'colorSourceFolder': 'color_source', 'colorOutputFolder': 'color_destination',
            'stabilizeSourceFolder': 'stabilize_source', 'stabilizeOutputFolder': 'stabilize_destination',
            'cleanupSourceFolder': 'cleanup_source', 'cleanupOutputFolder': 'cleanup_destination',
            'codecSourceFolder': 'codec_source',
            'musicSourceFolder': 'music_source', 'musicOutputFolder': 'music_destination',
            'webOutputFolder': 'web_destination', 'adOutputFolder': 'ad_destination',
            'conversionOutputFolder': 'conversion_destination',
        }
        for key, attribute in fields.items():
            field = getattr(self, attribute, None)
            if field is not None:
                if key in {'sourceFolder', 'imageSourceFolder', 'libraryFolder', 'videoSourceFolder', 'audioSourceFolder', 'duplicateSourceFolder', 'colorSourceFolder', 'stabilizeSourceFolder', 'cleanupSourceFolder', 'codecSourceFolder', 'musicSourceFolder'} or is_app_owned_path(field.text()):
                    self.ui_settings.setValue(key, field.text())
        current = self.tabs.currentWidget()
        if current is not None:
            self.ui_settings.setValue('lastTab', self.tabs.indexOf(current))
        checkbox_keys = {
            'enhanceImages': 'enhance_box', 'keepExifOnExport': 'keep_exif',
            'writeMetadataDates': 'meta', 'writeFileDates': 'fs', 'stripSoftwareMetadata': 'strip',
            'removeAllMetadata': 'remove_all', 'recursiveFolders': 'recursive',
            'preserveFolderStructure': 'structure', 'overwriteArchive': 'overwrite',
            'imageRecursive': 'image_recursive', 'imageStripMetadata': 'image_strip', 'libraryRecursive': 'library_recursive',
            'videoRecursive': 'video_recursive', 'audioRecursive': 'audio_recursive', 'duplicateRecursive': 'duplicate_recursive', 'colorRecursive': 'color_recursive', 'stabilizeRecursive': 'stabilize_recursive', 'cleanupRecursive': 'cleanup_recursive', 'codecRecursive': 'codec_recursive', 'musicRecursive': 'music_recursive',
            'conversionKeepMetadata': 'conversion_metadata',
        }
        for key, attribute in checkbox_keys.items():
            widget = getattr(self, attribute, None)
            if widget is not None:
                self.ui_settings.setValue(key, widget.isChecked())
        for key, label in {'sharpness': 'Skärpa', 'colorStrength': 'Färgstyrka', 'clarity': 'Klarhet/kontrast'}.items():
            self.ui_settings.setValue(key, self.sliders[label].value())
        for key, attribute in {'scaleFactor': 'factor', 'videoSizeLimit': 'video_size', 'audioFormat': 'audio_format', 'colorSourceProfile': 'color_source_profile', 'colorTargetProfile': 'color_target_profile', 'stabilizeStrength': 'stabilize_strength', 'webQuality': 'web_quality', 'adQuality': 'ad_quality', 'jpegQuality': 'jpeg_quality', 'videoCrf': 'video_crf'}.items():
            widget = getattr(self, attribute, None)
            if widget is not None:
                self.ui_settings.setValue(key, widget.currentIndex() if isinstance(widget, QtWidgets.QComboBox) else widget.value())
        self.ui_settings.setValue('duplicateThreshold', self.duplicate_threshold.value())
        self.ui_settings.setValue('dateMode', 'offset' if self.offset.isChecked() else 'absolute')
        self.ui_settings.setValue('dateOffsetSign', self.sign.currentIndex())
        self.ui_settings.setValue('dateOffsetParts', [spin.value() for spin in self.offset_spins])
        self.ui_settings.sync()

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
        if getattr(self, 'library_scan_worker', None) and self.library_scan_worker.isRunning():
            self.library_scan_worker.cancelled = True
            self.library_scan_worker.wait()
        for worker_name, cancel_method in (('image_worker', self.cancel_image_optimization), ('video_worker', self.cancel_video_conversion), ('audio_worker', self.cancel_video_audio), ('color_worker', self.cancel_color_conversion), ('stabilize_worker', self.cancel_video_stabilization), ('cleanup_worker', self.cancel_audio_cleanup), ('codec_worker', self.cancel_codec_report), ('duplicate_scan_worker', self.cancel_duplicate_scan), ('duplicate_move_worker', self.cancel_duplicate_move), ('music_worker', self.cancel_music_dvd)):
            worker = getattr(self, worker_name, None)
            if worker and worker.isRunning():
                cancel_method()
                worker.wait()
        self.save_preferences()
        LOGGER.info('Applikationen stängs')
        LOGGER.removeHandler(self.qt_log_handler)
        event.accept()


if __name__ == '__main__':
    def log_uncaught(exc_type, exc_value, exc_tb):
        LOGGER.critical('Ohanterat fel', exc_info=(exc_type, exc_value, exc_tb))
        QtWidgets.QMessageBox.critical(None, 'MediaForge - error', f'{exc_value}\n\nLog: {LOG_FILE}')
    sys.excepthook = log_uncaught
    app = QtWidgets.QApplication(sys.argv)
    icon_file = Path(__file__).resolve().with_name('fotoverktyg_icon.png')
    app.setWindowIcon(QtGui.QIcon(str(icon_file)) if icon_file.exists() else brand_icon())
    window = Window()
    launch_path = None
    if len(sys.argv) > 1 and not sys.argv[1].startswith('-'):
        candidate = Path(sys.argv[1]).expanduser()
        if candidate.exists() and (candidate.is_dir() or candidate.suffix.lower() in ImageLibraryScanWorker.IMAGE_EXTENSIONS):
            launch_path = candidate.resolve()
    if launch_path is not None:
        photo_mode_index = window.mode_combo.findData('photo')
        if photo_mode_index >= 0:
            window.mode_combo.setCurrentIndex(photo_mode_index)
        if launch_path.is_dir():
            window.library_source.setText(str(launch_path))
        else:
            window.library_source.setText(str(launch_path.parent))
            window.library_pending_selection = launch_path
        window.tabs.setCurrentWidget(window.library_tab)
        window.scan_image_library()
    window.show()
    sys.exit(app.exec())
