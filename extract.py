import os
import zipfile
import tarfile
import rarfile
import py7zr

class FileCompressor:

    def compress(self, folder_path, output_path, format='zip'):
        if format == 'zip':
            self._compress_zip(folder_path, output_path)
        elif format == 'tar':
            self._compress_tar(folder_path, output_path, mode='w')
        elif format == 'gztar':
            self._compress_tar(folder_path, output_path, mode='w:gz')
        elif format == 'bztar':
            self._compress_tar(folder_path, output_path, mode='w:bz2')
        elif format == '7z':
            self._compress_7z(folder_path, output_path)
        else:
            raise ValueError(f"Unsupported compression format: {format}")

    def _compress_zip(self, folder_path, output_path):
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zipf.write(file_path, os.path.relpath(file_path, folder_path))

    def _compress_tar(self, folder_path, output_path, mode='w'):
        with tarfile.open(output_path, mode) as tarf:
            tarf.add(folder_path, arcname=os.path.basename(folder_path))

    def _compress_7z(self, folder_path, output_path):
        with py7zr.SevenZipFile(output_path, 'w') as archive:
            archive.writeall(folder_path, arcname=os.path.basename(folder_path))

    def extract(self, file_path, output_folder):
        if file_path.endswith('.zip'):
            self._extract_zip(file_path, output_folder)
        elif file_path.endswith('.tar'):
            self._extract_tar(file_path, output_folder)
        elif file_path.endswith('.tar.gz') or file_path.endswith('.tgz'):
            self._extract_tar(file_path, output_folder, mode='r:gz')
        elif file_path.endswith('.tar.bz2') or file_path.endswith('.tbz'):
            self._extract_tar(file_path, output_folder, mode='r:bz2')
        elif file_path.endswith('.rar'):
            self._extract_rar(file_path, output_folder)
        elif file_path.endswith('.7z'):
            self._extract_7z(file_path, output_folder)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")

    def _extract_zip(self, file_path, output_folder):
        with zipfile.ZipFile(file_path, 'r') as zipf:
            zipf.extractall(output_folder)

    def _extract_tar(self, file_path, output_folder, mode='r'):
        with tarfile.open(file_path, mode) as tarf:
            tarf.extractall(output_folder)

    def _extract_rar(self, file_path, output_folder):
        with rarfile.RarFile(file_path) as rarf:
            rarf.extractall(output_folder)

    def _extract_7z(self, file_path, output_folder):
        with py7zr.SevenZipFile(file_path, 'r') as archive:
            archive.extractall(output_folder)

# 사용 예시
compressor = FileCompressor()
compressor.compress('test', 'output.7z', format='7z')
compressor.extract('output.7z', 'extracted_folder')
