"""Focused image regressions without requiring a desktop Qt installation."""
import ast
import tempfile
import unittest
from pathlib import Path
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

# Load just the production functions, substituting a minimal QImage. This lets
# the pixel/EXIF tests run on headless machines without Qt's native libraries.
source = Path(__file__).resolve().parents[1] / 'fotoverktyg.pyw'
tree = ast.parse(source.read_text(encoding='utf-8'))
functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)
             and node.name in ('enhance', 'image_file_to_qimage')]

class FakeQImage:
    class Format:
        Format_RGBA8888 = 'RGBA'
        Format_RGB888 = 'RGB'
    def __init__(self, data, width, height, stride, pixel_format):
        self.image = Image.frombytes(pixel_format, (width, height), data)
    def copy(self):
        return self

class FakeQtGui:
    QImage = FakeQImage

namespace = dict(Image=Image, ImageOps=ImageOps, ImageFilter=ImageFilter,
                 ImageEnhance=ImageEnhance, Path=Path, QtGui=FakeQtGui)
exec(compile(ast.Module(body=functions, type_ignores=[]), str(source), 'exec'), namespace)
enhance = namespace['enhance']
preview = namespace['image_file_to_qimage']

class ImageProcessingTests(unittest.TestCase):
    def test_oriented_jpeg_preview_reports_original_dimensions(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'source.jpg'
            image = Image.new('RGB', (800, 400), 'white')
            ImageDraw.Draw(image).rectangle((0, 0, 150, 150), fill='red')
            exif = Image.Exif()
            exif[274] = 6
            image.save(path, exif=exif)
            for bounds in ((100, 100), (400, 800), None):
                result, dimensions = preview(path, bounds)
                self.assertEqual(dimensions, (400, 800))
                self.assertLess(result.image.width, result.image.height)
                if bounds:
                    self.assertLessEqual(result.image.width, bounds[0])
                    self.assertLessEqual(result.image.height, bounds[1])

    def test_transparency_and_full_resolution_export(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / 'source.png'
            Image.new('RGBA', (80, 60), (255, 0, 0, 100)).save(source)
            for ext in ('jpg', 'jpeg', 'png'):
                target = folder / ('result.' + ext)
                enhance(source, target, 1, 65, 0, 0, False)
                with Image.open(target) as result:
                    self.assertEqual(result.mode, 'RGBA' if ext == 'png' else 'RGB')
                    self.assertEqual(result.size, (80, 60))

    def test_sharpening_and_upscale(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            source = folder / 'soft.png'
            image = Image.new('RGB', (80, 80), (90, 90, 90))
            ImageDraw.Draw(image).rectangle((20, 20, 60, 60), fill=(150, 150, 150))
            image.filter(ImageFilter.GaussianBlur(1)).save(source)
            enhance(source, folder / 'plain.png', 1, 0, 0, 0, False)
            enhance(source, folder / 'sharp.png', 1, 65, 0, 0, False)
            with Image.open(folder / 'plain.png') as plain, Image.open(folder / 'sharp.png') as sharp:
                self.assertGreater(sharp.getpixel((22, 40))[0], plain.getpixel((22, 40))[0])
                self.assertLess(sharp.getpixel((18, 40))[0], plain.getpixel((18, 40))[0])
            enhance(source, folder / 'large.png', 2, 0, 0, 0, False)
            with Image.open(folder / 'large.png') as large:
                self.assertEqual(large.size, (160, 160))

if __name__ == '__main__':
    unittest.main()
