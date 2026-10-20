"""Bounded CPU-only PDF page previews for registered engineering attachments.

Uses pypdfium2's bundled PDFium; no browser, Blender or system CLI is required.
API: https://pypdfium2.readthedocs.io/en/stable/python_api.html
"""
import math

MAX_PDF_BYTES = 100 * 1024 * 1024
MAX_PAGES = 60
MAX_EDGE = 2048
MAX_TOTAL_PIXELS = 100_000_000


def render_pdf_pages(source, directory):
    """Write actual PDF pages as PNG and return relative filenames.

    All dimensions and total raster budget are checked before rendering. Limits
    reject oversized input explicitly instead of silently dropping engineering
    pages. Password-protected or invalid PDFs fail without replacing a package.
    """
    if directory.exists() and (not directory.is_dir() or any(directory.iterdir())):
        raise ValueError('MEP PDF preview directory conflicts with existing artifacts')
    if source.stat().st_size > MAX_PDF_BYTES:
        raise ValueError('MEP PDF exceeds the 100 MB input limit')
    try:
        import pypdfium2 as pdfium
    except ImportError as error:
        raise ValueError('PDF previews require pypdfium2==5.14.0; install the skill scripts/requirements.txt in its Python environment') from error
    try:
        document = pdfium.PdfDocument(str(source))
    except Exception as error:
        raise ValueError('Cannot open MEP PDF (invalid or password protected)') from error
    pages = []
    try:
        if document.get_formtype() in (pdfium.raw.FORMTYPE_XFA_FULL, pdfium.raw.FORMTYPE_XFA_FOREGROUND):
            raise ValueError('XFA engineering PDF forms are unsupported; supply a flattened PDF')
        document.init_forms()
        count = len(document)
        if not 1 <= count <= MAX_PAGES:
            raise ValueError(f'MEP PDF requires 1–{MAX_PAGES} pages; received {count}')
        budget = 0
        for index in range(count):
            page = document[index]
            try:
                width, height = page.get_size()
            finally:
                page.close()
            if not all(math.isfinite(value) and value > 0 for value in (width, height)):
                raise ValueError('Invalid MEP PDF page dimensions')
            scale = min(2.0, (MAX_EDGE-1)/max(width, height))
            pixels = math.ceil(width*scale)*math.ceil(height*scale)
            budget += pixels
            if budget > MAX_TOTAL_PIXELS:
                raise ValueError('MEP PDF exceeds the 100 million pixel preview budget; split the attachment')
            pages.append((index, scale))
        directory.mkdir(parents=True, exist_ok=True)
        result = []
        for index, scale in pages:
            page = document[index]
            bitmap = None
            try:
                bitmap = page.render(scale=scale, may_draw_forms=True, draw_annots=True)
                image = bitmap.to_pil()
                name = f'page-{index+1:03d}.png'
                image.save(directory/name, format='PNG')
                image.close()
                result.append(name)
            except Exception as error:
                raise ValueError(f'Cannot rasterize MEP PDF page {index+1}') from error
            finally:
                if bitmap is not None:
                    bitmap.close()
                page.close()
        return result
    finally:
        document.close()
