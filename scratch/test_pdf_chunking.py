import sys
import os
sys.path.append(os.getcwd())

from api.routes.knowledge import split_text_into_chunks

def test_chunking():
    text = "A" * 100000
    chunks = split_text_into_chunks(text, chunk_size=30000)
    print(f"Text length: {len(text)}")
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i} length: {len(chunk)}")
    
    assert len(chunks) == 4
    assert len(chunks[0]) == 30000
    assert len(chunks[3]) == 10000
    print("Chunking test passed!")

if __name__ == "__main__":
    test_chunking()
