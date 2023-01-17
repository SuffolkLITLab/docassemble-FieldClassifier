import math

from formfyxer import pdf_wrangling
from pdf2image import convert_from_path
import cv2
import tempfile
from pikepdf import Pdf

#from docassemble.base.util import DAObject, path_and_mimetype

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

#class PDFFieldViewer(DAObject):
#    def init(self, *pargs, **kwargs):
#        super().init(*pargs, **kwargs)
#        self._process_fields()
    
def _process_fields(filename):
        pdf = Pdf.open(filename)
        fields = [
            {
                "var_name": str(field.T),
                "type": str(field.FT),
                "field": field,
            }
            for field
            in pdf.Root.AcroForm.Fields
        ]
        images = convert_from_path(filename, dpi=250)
        pdf_images = [tempfile.NamedTemporaryFile() for _ in range(len(images))]
        for file_obj, img in zip(pdf_images, images):
            img.save(file_obj, "JPEG")
            file_obj.flush()

        for field in fields:
            bbox = field["field"].Rect.as_list()
            print(f"{field} bbox: {bbox}")
            field_page = pdf.pages.index(field["field"].P)
            opencv_bbox = pdf_wrangling.pdf2img_coords(bbox, images[field_page].height)
            expanded_bbox = expand_bbox(opencv_bbox)
            img = cv2.imread(pdf_images[field_page].name)
            print(expanded_bbox)
            cv2.imshow("detected field", img[
                     expanded_bbox[0]:expanded_bbox[1], 
                     expanded_bbox[2]:expanded_bbox[3]
                 ])
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            field["image"] = bytes(cv2.imencode('.png', 
                #img[1:100,150:200]
                 img[
                     expanded_bbox[0]:expanded_bbox[1], 
                     expanded_bbox[2]:expanded_bbox[3]
                 ]
            )[1])
            del field["field"]
        return fields

if __name__ == "__main__":
    # pdf_path = "/mnt/e/My Drive/Test Weaver Files/civil_docketing_statement_polished_repaired.pdf"
    pdf_path = "civil_docketing_statement.pdf"
    my_pdf = _process_fields(filename=pdf_path)
    print(repr(my_pdf))