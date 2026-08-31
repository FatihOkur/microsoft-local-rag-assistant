import unittest
import numpy as np
from src.retrieval import cosine_similarity
from src.ingestion import read_and_chunk_file
import tempfile
import os

class TestRAGComponents(unittest.TestCase):
    def test_cosine_similarity(self):
        vec_a = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec_b = np.array([1.0, 0.0, 0.0], dtype=np.float32)
        vec_c = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        
        # Identical vectors should have similarity 1.0
        self.assertAlmostEqual(cosine_similarity(vec_a, vec_b), 1.0)
        
        # Orthogonal vectors should have similarity 0.0
        self.assertAlmostEqual(cosine_similarity(vec_a, vec_c), 0.0)

    def test_chunking_logic(self):
        # Create a temporary text file with known structure
        content = "This is the first sentence. This is the second sentence.\n\nThis is a new paragraph."
        
        with tempfile.NamedTemporaryFile(mode='w', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = f.name
            
        try:
            import src.ingestion as ingestion
            original_size = ingestion.CHUNK_SIZE
            original_overlap = ingestion.CHUNK_OVERLAP
            
            ingestion.CHUNK_SIZE = 40
            ingestion.CHUNK_OVERLAP = 10
            
            chunks = read_and_chunk_file(temp_path)
            
            self.assertTrue(len(chunks) > 0)
            # Ensure no chunk exceeds the max chunk size significantly
            for chunk in chunks:
                self.assertTrue(len(chunk) <= ingestion.CHUNK_SIZE + 5) 
                
            ingestion.CHUNK_SIZE = original_size
            ingestion.CHUNK_OVERLAP = original_overlap
        finally:
            os.remove(temp_path)

if __name__ == '__main__':
    unittest.main()
