import os
import zlib
import bz2
import json
import struct
from typing import List, Dict, Tuple, Union
from PIL import Image
from io import BytesIO
import lzma
from pydub import AudioSegment

class DHC:
    def __init__(self):
        # Supported algorithms and corresponding compression methods
        self.algorithms = {
            'text': ['lz77', 'lz78', 'lzma'],
            'image': ['jpeg', 'png', 'webp'],
            'audio': ['mp3', 'flac', 'aac']
        }
        # Mapping compression and decompression methods
        self.compression_methods = {
            'lz77': self._compress_lz77,
            'lz78': self._compress_lz78,
            'lzma': self._compress_lzma,
            'jpeg': self._compress_jpeg,
            'png': self._compress_png,
            'webp': self._compress_webp,
            'mp3': self._compress_mp3,
            'flac': self._compress_flac,
            'aac': self._compress_aac
        }
        self.decompression_methods = {
            'lz77': self._decompress_lz77,
            'lz78': self._decompress_lz78,
            'lzma': self._decompress_lzma,
            'jpeg': self._decompress_jpeg,
            'png': self._decompress_png,
            'webp': self._decompress_webp,
            'mp3': self._decompress_mp3,
            'flac': self._decompress_flac,
            'aac': self._decompress_aac
        }

    def compress(self, input_path: str, output_path: str) -> None:
        """
        Compress the input file or folder using the Dynamic Hybrid Compression algorithm and save to output_path.
        """
        if os.path.isfile(input_path):
            self._compress_file(input_path, output_path)
        elif os.path.isdir(input_path):
            self._compress_folder(input_path, output_path)
        else:
            raise ValueError("Invalid input path. Must be a file or folder.")

    def decompress(self, input_path: str, output_path: str) -> None:
        """
        Decompress the .dhc file to the specified output path.
        """
        self._decompress_file(input_path, output_path)

    def _compress_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, 'rb') as f:
            data = f.read()

        data_type = self._analyze_data(data)
        best_algorithm = self._select_best_algorithm(data_type)
        compressed_data, metadata = self.compression_methods[best_algorithm](data)

        with open(output_path, 'wb') as f:
            metadata_json = json.dumps(metadata).encode('utf-8')
            f.write(struct.pack('I', len(metadata_json)))
            f.write(metadata_json)
            f.write(compressed_data)

    def _compress_folder(self, folder_path: str, output_path: str) -> None:
        compressed_files = {}
        for root, _, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                with open(file_path, 'rb') as f:
                    data = f.read()
                data_type = self._analyze_data(data)
                best_algorithm = self._select_best_algorithm(data_type)
                compressed_data, metadata = self.compression_methods[best_algorithm](data)
                relative_path = os.path.relpath(file_path, folder_path)
                compressed_files[relative_path] = (compressed_data, metadata)

        with open(output_path, 'wb') as f:
            metadata_json = json.dumps({k: v[1] for k, v in compressed_files.items()}).encode('utf-8')
            f.write(struct.pack('I', len(metadata_json)))
            f.write(metadata_json)
            for file_path, (compressed_data, _) in compressed_files.items():
                f.write(struct.pack('I', len(file_path)))
                f.write(file_path.encode('utf-8'))
                f.write(struct.pack('I', len(compressed_data)))
                f.write(compressed_data)

    def _decompress_file(self, input_path: str, output_path: str) -> None:
        with open(input_path, 'rb') as f:
            metadata_len = struct.unpack('I', f.read(4))[0]
            metadata_json = f.read(metadata_len)
            metadata = json.loads(metadata_json.decode('utf-8'))

            for file_path, meta in metadata.items():
                file_len = struct.unpack('I', f.read(4))[0]
                file_path = f.read(file_len).decode('utf-8')
                compressed_data_len = struct.unpack('I', f.read(4))[0]
                compressed_data = f.read(compressed_data_len)
                algorithm = meta['algorithm']
                decompressed_data = self.decompression_methods[algorithm](compressed_data)
                
                output_file_path = os.path.join(output_path, file_path)
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
                with open(output_file_path, 'wb') as output_file:
                    output_file.write(decompressed_data)

    def _analyze_data(self, data: bytes) -> str:
        # Basic data analysis based on file signature or content
        if data.startswith(b'\xFF\xD8'):
            return 'image'
        elif data.startswith(b'ID3') or data.startswith(b'\xFF\xFB'):
            return 'audio'
        else:
            return 'text'

    def _select_best_algorithm(self, data_type: str) -> str:
        # Simplified selection of the best algorithm
        return self.algorithms[data_type][0]  # Just select the first algorithm for now

    # Compression and decompression methods
    def _compress_lz77(self, data: bytes) -> Tuple[bytes, Dict]:
        compressed_data = zlib.compress(data)
        metadata = {'algorithm': 'lz77'}
        return compressed_data, metadata

    def _compress_lz78(self, data: bytes) -> Tuple[bytes, Dict]:
        compressed_data = bz2.compress(data)
        metadata = {'algorithm': 'lz78'}
        return compressed_data, metadata

    def _compress_lzma(self, data: bytes) -> Tuple[bytes, Dict]:
        compressed_data = lzma.compress(data)
        metadata = {'algorithm': 'lzma'}
        return compressed_data, metadata

    def _compress_jpeg(self, data: bytes) -> Tuple[bytes, Dict]:
        with BytesIO(data) as input_buffer:
            with Image.open(input_buffer) as img:
                output_buffer = BytesIO()
                img.save(output_buffer, format='JPEG')
                compressed_data = output_buffer.getvalue()
        metadata = {'algorithm': 'jpeg'}
        return compressed_data, metadata

    def _compress_png(self, data: bytes) -> Tuple[bytes, Dict]:
        with BytesIO(data) as input_buffer:
            with Image.open(input_buffer) as img:
                output_buffer = BytesIO()
                img.save(output_buffer, format='PNG')
                compressed_data = output_buffer.getvalue()
        metadata = {'algorithm': 'png'}
        return compressed_data, metadata

    def _compress_webp(self, data: bytes) -> Tuple[bytes, Dict]:
        with BytesIO(data) as input_buffer:
            with Image.open(input_buffer) as img:
                output_buffer = BytesIO()
                img.save(output_buffer, format='WEBP')
                compressed_data = output_buffer.getvalue()
        metadata = {'algorithm': 'webp'}
        return compressed_data, metadata

    def _compress_mp3(self, data: bytes) -> Tuple[bytes, Dict]:
        with BytesIO(data) as input_buffer:
            audio = AudioSegment.from_file(input_buffer)
            output_buffer = BytesIO()
            audio.export(output_buffer, format="mp3")
            compressed_data = output_buffer.getvalue()
        metadata = {'algorithm': 'mp3'}
        return compressed_data, metadata

    def _compress_flac(self, data: bytes) -> Tuple[bytes, Dict]:
        with BytesIO(data) as input_buffer:
            audio = AudioSegment.from_file(input_buffer)
            output_buffer = BytesIO()
            audio.export(output_buffer, format="flac")
            compressed_data = output_buffer.getvalue()
        metadata = {'algorithm': 'flac'}
        return compressed_data, metadata

    def _compress_aac(self, data: bytes) -> Tuple[bytes, Dict]:
        with BytesIO(data) as input_buffer:
            audio = AudioSegment.from_file(input_buffer)
            output_buffer = BytesIO()
            audio.export(output_buffer, format="aac")
            compressed_data = output_buffer.getvalue()
        metadata = {'algorithm': 'aac'}
        return compressed_data, metadata

    def _decompress_lz77(self, compressed_data: bytes) -> bytes:
        return zlib.decompress(compressed_data)

    def _decompress_lz78(self, compressed_data: bytes) -> bytes:
        return bz2.decompress(compressed_data)

    def _decompress_lzma(self, compressed_data: bytes) -> bytes:
        return lzma.decompress(compressed_data)

    def _decompress_jpeg(self, compressed_data: bytes) -> bytes:
        return compressed_data  # JPEG is natively viewable, no need for decompression

    def _decompress_png(self, compressed_data: bytes) -> bytes:
        return compressed_data  # PNG is natively viewable, no need for decompression

    def _decompress_webp(self, compressed_data: bytes) -> bytes:
        return compressed_data  # WebP is natively viewable, no need for decompression

    def _decompress_mp3(self, compressed_data: bytes) -> bytes:
        with BytesIO(compressed_data) as input_buffer:
            audio = AudioSegment.from_file(input_buffer, format="mp3")
            output_buffer = BytesIO()
            audio.export(output_buffer, format="wav")
            decompressed_data = output_buffer.getvalue()
        return decompressed_data

    def _decompress_flac(self, compressed_data: bytes) -> bytes:
        with BytesIO(compressed_data) as input_buffer:
            audio = AudioSegment.from_file(input_buffer, format="flac")
            output_buffer = BytesIO()
            audio.export(output_buffer, format="wav")
            decompressed_data = output_buffer.getvalue()
        return decompressed_data

    def _decompress_aac(self, compressed_data: bytes) -> bytes:
        with BytesIO(compressed_data) as input_buffer:
            audio = AudioSegment.from_file(input_buffer, format="aac")
            output_buffer = BytesIO()
            audio.export(output_buffer, format="wav")
            decompressed_data = output_buffer.getvalue()
        return decompressed_data

# Usage example
if __name__ == "__main__":
    dhc = DHC()
    dhc.compress("test_folder", "output.dhc")
    dhc.decompress("output.dhc", "output")