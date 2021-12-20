import os

from django.core.files.storage import FileSystemStorage

from iot import settings
from knx import xml
from knx.xml import SnomXMLFactory

def process_file(request):
    TARGET_NAME = {'.csv': 'ga', '.xml': 'knx'}

    if request.method == 'POST':
        uploaded_type = request.POST.get('file_type')

        if uploaded_type == '.csv':
            file = request.FILES.get('groupaddresses', False)
            post_request = HandleUploads(file)

            return post_request.handle_file(TARGET_NAME.get('.csv'), uploaded_type)

        if uploaded_type == '.xml':
            file = request.FILES.get('minibrowser', False)
            post_request = HandleUploads(file)

            return post_request.handle_file(TARGET_NAME['.xml'], uploaded_type)

        return 'Choose first a file'

    return ''


class HandleUploads():
    def __init__(self, file):
        self.file = file
        self.file_system = FileSystemStorage()

    def handle_file(self, file_name, file_type):
        TARGET_NAME = f"{ file_name }{ file_type }"

        if self.file and file_type in self.file.name:
            self.file.name = TARGET_NAME
            self.remove_file_if_exists()
            self.file_system.save(self.file.name, self.file)

            if file_type == '.csv':
                self.remove_file_if_exists('minibrowser.xml')
                SnomXMLFactory().create_deskphone_xml(TARGET_NAME)
                SnomXMLFactory().create_handset_xml(TARGET_NAME)

                return 'Groupaddresses were uploaded and Snom default XML was created.'

            return 'Snom XML was updated'

        return f'Choose first a { file_type } file'

    def remove_file_if_exists(self, file=None):
        if file:
            self.file.name = file

        if self.file_system.exists(self.file.name):
            os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
