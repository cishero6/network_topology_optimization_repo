import os
import tempfile
import unittest
from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from app.core.storage_manager import StorageManager

class StorageManagerTestCase(TestCase):
    def setUp(self):
        # Создаем временную директорию
        self.temp_media = tempfile.TemporaryDirectory()
        self.custom_settings = override_settings(
            MEDIA_ROOT=self.temp_media.name,
            MEDIA_URL='/test-media/'
        )
        self.custom_settings.enable()
        
        self.storage = StorageManager()
        self.query_id = "test_query_123"
        self.sample_content = b"test file content"

    def tearDown(self):
        self.custom_settings.disable()
        self.temp_media.cleanup()

    def test_save_and_retrieve_file(self):
        """Тестирование сохранения и получения файла"""
        # Сохраняем тестовый файл
        test_file = SimpleUploadedFile(
            "test.xxx", 
            self.sample_content,
            content_type="application/octet-stream"
        )
        
        saved_name = self.storage.save_uploaded_file(test_file, self.query_id)
        self.assertTrue(saved_name.startswith(self.query_id))
        
        # Проверяем существование файла
        full_path = os.path.join(
            self.storage.uploads_storage.location, 
            saved_name
        )
        self.assertTrue(os.path.exists(full_path))
        
    def test_stage_processing_flow(self):
        """Тестирование полного цикла обработки"""
        # Stage 1
        stage1_result = self.storage.save_stage_result(
            b"stage1_data", 
            self.query_id, 
            1
        )
        self.assertIn("stage1_result", stage1_result)
        
        # Stage 2
        stage2_result = self.storage.save_stage_result(
            b"stage2_data", 
            self.query_id, 
            2
        )
        self.assertIn("stage2_result", stage2_result)
        
        # Проверка изоляции хранилищ
        self.assertNotEqual(
            self.storage.stage1_storage.location,
            self.storage.stage2_storage.location
        )

    def test_cleanup_functionality(self):
        """Тестирование очистки файлов"""
        # Создаем тестовые файлы во всех хранилищах
        test_file = SimpleUploadedFile("cleanup_test.xxx", self.sample_content)
        
        # Сохраняем файлы в разных хранилищах
        self.storage.save_uploaded_file(test_file, self.query_id)
        self.storage.save_stage_result(b"stage1", self.query_id, 1)
        self.storage.save_stage_result(b"stage2", self.query_id, 2)
        
        # Проверяем, что файлы созданы
        self.assertTrue(len(os.listdir(self.storage.uploads_storage.location)) > 0)
        self.assertTrue(len(os.listdir(self.storage.stage1_storage.location)) > 0)
        self.assertTrue(len(os.listdir(self.storage.stage2_storage.location)) > 0)
        
        # Выполняем очистку
        self.storage.cleanup_query_files(self.query_id)
        
        # Проверяем отсутствие файлов во ВСЕХ хранилищах
        self.assertEqual(len(os.listdir(self.storage.uploads_storage.location)), 0)
        self.assertEqual(len(os.listdir(self.storage.stage1_storage.location)), 0)
        self.assertEqual(len(os.listdir(self.storage.stage2_storage.location)), 0)

    def test_invalid_stage_handling(self):
        """Тестирование обработки неверного номера этапа"""
        with self.assertRaises(ValueError):
            self.storage.get_stage_input(self.query_id, 3)

    def test_file_versioning(self):
        """Тестирование версионирования файлов"""
        # Первое сохранение
        file1 = SimpleUploadedFile("test.xxx", b"v1")
        name1 = self.storage.save_uploaded_file(file1, self.query_id)
        
        # Искусственная задержка для гарантированного различия timestamp
        import time
        time.sleep(0.1)
        
        # Второе сохранение с тем же query_id
        file2 = SimpleUploadedFile("test.xxx", b"v2")
        name2 = self.storage.save_uploaded_file(file2, self.query_id)
        
        # Извлекаем timestamp из имен файлов
        timestamp1 = int(name1.split('_')[-1].split('.')[0])
        timestamp2 = int(name2.split('_')[-1].split('.')[0])
        
        # Проверяем что timestamp увеличился
        self.assertLess(timestamp1, timestamp2)
        
        # Проверяем что остальные части имени совпадают
        prefix1 = '_'.join(name1.split('_')[:-1])
        prefix2 = '_'.join(name2.split('_')[:-1])
        self.assertEqual(prefix1, prefix2)

if __name__ == '__main__':
    unittest.main()