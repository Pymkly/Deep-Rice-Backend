import pytesseract
from PIL import Image

from api.ragsystem.documents.main_process.processor.document_processor import DocumentProcessor
from config import IMAGE_EXTENSION


def image_to_text(_absolute_path):
    image = Image.open(_absolute_path)
    extracted_text = pytesseract.image_to_string(image)
    return extracted_text


class ImageProcessor(DocumentProcessor):
    def __init__(self, encoder):
        super(ImageProcessor, self).__init__(encoder=encoder, extension=IMAGE_EXTENSION)
        self.chunk_size = 1

    def extract_content(self, path_):
        _absolute_path = self.get_absolute_path(path_)
        content = image_to_text(_absolute_path)
        return [content]

    def extract_contents(self):
        files = self.get_files_on_folder()
        # On a décidé de ne pas couper les textes sur les images
        # le [[]] signifie qu on ne fait pas de split au niveau du resultat
        chunks = [[image_to_text(path_)] for path_ in files]
        return chunks