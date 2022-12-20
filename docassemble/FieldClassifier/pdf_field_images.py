import math

import formfyxer
from pdf2image import convert_from_path
import cv2
import tempfile
from pikepdf import Pdf

from docassemble.base.util import DAObject, path_and_mimetype

__all__ = [
    "PDFFieldViewer"
]

def expand_bbox(bbox, by=20):
    return [
        int(bbox[0]) - by,
        int(bbox[1]) + by,
        int(bbox[2]) - by,
        int(bbox[3]) + by,
    ]

class PDFFieldViewer(DAObject):
    def init(self, *pargs, **kwargs):
        super().init(*pargs, **kwargs)
        self._process_fields()
        self._create_field_images()
    
    def _process_fields(self):
        self.pdf = Pdf.open(self.filename)
        self.fields = [
            {
                "var_name": str(field.T),
                "type": str(field.FT),
                "field": field,
            }
            for field
            in self.pdf.Root.AcroForm.Fields
        ]
        self.images = convert_from_path(self.filename, dpi=250)
        self.pdf_images = [tempfile.NamedTemporaryFile() for i in range(len(self.images))]
        for file_obj, img in zip(self.pdf_images, self.images):
            img.save(file_obj, "JPEG")
            file_obj.flush()

    def _create_field_images(self):
        for field in self.fields:
            bbox = field["field"].Rect.as_list()
            field_page = self.pdf.pages.index(field["field"].P)
            opencv_bbox = formfyxer.img2pdf_coords(bbox, self.images[field_page].height)
            expanded_bbox = expand_bbox(opencv_bbox)
            img = cv2.imread(self.pdf_images[field_page].name)
            field["image"] = bytes(cv2.imencode('.png', 
                img[1:10,10:20]
                # img[
                #     expanded_bbox[0]:expanded_bbox[1], 
                #     expanded_bbox[2]:expanded_bbox[3]
                # ]
            )[1])
            del field["field"]

    def get_fields(self):
        return self.fields

if __name__ == "__main__":
    pdf_path = "/mnt/e/My Drive/Test Weaver Files/civil_docketing_statement_polished_repaired.pdf"
    my_pdf = PDFFieldViewer(filename=pdf_path)
    repr(my_pdf.fields)
    
    print("Hello")