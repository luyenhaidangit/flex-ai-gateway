# Current RAG Flow

Tai lieu nay mo ta luong RAG hien tai cua `flex-ai-gateway` theo code dang co, bao gom:

- luong index khi goi `POST /rag/index`
- luong query khi goi `POST /rag/query`
- gioi han hien tai cua pipeline ingest

## Tong quan

RAG hien tai dung:

- `docs/knowledge-base` lam thu muc nguon tai lieu
- Ollama de tao embedding va sinh cau tra loi
- Qdrant de luu vector va tim semantic search

Pipeline hien tai la:

1. Load tai lieu tu thu muc knowledge base
2. Doc text tu file ho tro
3. Chia text thanh chunk co overlap
4. Tao embedding cho tung chunk bang Ollama
5. Upsert vector vao Qdrant
6. Khi query, embedding cau hoi, search Qdrant, roi gui context vao chat model

## Luong `POST /rag/index`

Khi goi:

```http
POST /rag/index
Content-Type: application/json

{
  "recreate_collection": false
}
```

service se xu ly theo thu tu sau.

### 1. Validate cau hinh

He thong kiem tra:

- `OLLAMA_EMBED_MODEL` khong rong
- `QDRANT_URL` khong rong
- `QDRANT_VECTOR_SIZE` > 0
- `RAG_CHUNK_OVERLAP < RAG_CHUNK_SIZE`

Neu sai cau hinh, API tra ve `400 Bad Request`.

### 2. Load source documents

Service doc du lieu trong `RAG_SOURCE_DIR`, mac dinh la:

```text
docs/knowledge-base
```

Chi file co duoi sau moi duoc nap:

- `.md`
- `.txt`

Moi file hop le se duoc doc bang UTF-8 va luu thanh mot `SourceDocument` gom:

- `doc_id`
- `source`
- `title`
- `text`

Neu khong tim thay thu muc hoac khong co tai lieu hop le, API tra ve `404 Not Found`.

### 3. Chunk documents

Sau khi doc file, service:

- chuan hoa whitespace bang cach gom nhieu khoang trang/xuong dong thanh mot dau cach
- cat text theo `RAG_CHUNK_SIZE`
- dich cua so theo buoc `RAG_CHUNK_SIZE - RAG_CHUNK_OVERLAP`

Ket qua la danh sach `DocumentChunk` gom:

- `doc_id`
- `source`
- `title`
- `chunk_index`
- `text`

Neu khong tao duoc chunk, API tra ve `400 Bad Request`.

### 4. Dam bao collection Qdrant

Service kiem tra collection `QDRANT_COLLECTION_NAME`.

Hanh vi theo `recreate_collection`:

- `false`: neu collection da ton tai thi giu nguyen
- `true`: neu collection da ton tai thi xoa di va tao lai tu dau

Neu collection chua ton tai, service se tao moi.

Neu Qdrant khong truy cap duoc, API tra ve `503 Service Unavailable`.

### 5. Embed chunks bang Ollama

Moi chunk duoc goi den:

```text
POST {OLLAMA_BASE_URL}/api/embeddings
```

Payload chua:

- `model = OLLAMA_EMBED_MODEL`
- `prompt = chunk.text`

Vector tra ve phai co do dai bang `QDRANT_VECTOR_SIZE`.

Neu Ollama loi hoac embedding khong hop le, API tra ve `400` hoac `503` tuy truong hop.

### 6. Upsert vao Qdrant

Moi chunk duoc chuyen thanh mot point trong Qdrant gom:

- `id`: tao on dinh tu `source + chunk_index`
- `vector`: embedding cua chunk
- `payload`:
  - `doc_id`
  - `source`
  - `title`
  - `chunk_index`
  - `text`

Vi `id` duoc tao on dinh, chay lai index voi cung file va cung chunk index se co xu huong ghi de point cu thay vi tao point moi ngau nhien.

### 7. Response thanh cong

Neu index thanh cong, API tra ve:

```json
{
  "collection_name": "rag_documents",
  "source_directory": "docs/knowledge-base",
  "documents_indexed": 2,
  "chunks_indexed": 8
}
```

## Luong `POST /rag/query`

Khi goi:

```http
POST /rag/query
Content-Type: application/json

{
  "question": "Qdrant dung de lam gi?",
  "top_k": 3
}
```

service se xu ly theo thu tu sau.

### 1. Validate cau hinh va kiem tra collection

Service kiem tra cau hinh RAG va dam bao:

- collection ton tai
- collection co du lieu da index

Neu collection rong hoac chua duoc tao, API tra ve `404 Not Found`.

### 2. Embed cau hoi

Cau hoi cua nguoi dung duoc gui sang Ollama embeddings API de tao `query_vector`.

### 3. Search Qdrant

Service goi Qdrant search voi:

- `collection_name = QDRANT_COLLECTION_NAME`
- `query_vector`
- `limit = top_k`
- `with_payload = true`

Ket qua tra ve la cac chunk lien quan nhat.

### 4. Build context prompt

Tu cac chunk tim duoc, service tao prompt theo dang:

- gom `Question`
- gom `Context`
- moi source co `title`, `source`, `text`

### 5. Goi Ollama chat

Prompt context duoc gui den:

```text
POST {OLLAMA_BASE_URL}/api/chat
```

System prompt hien tai yeu cau model:

- chi tra loi dua tren context da cung cap
- neu context khong du thi phai noi ro

### 6. Tra response

API tra ve:

- model da dung
- answer
- collection name
- danh sach source chunks

## Gioi han hien tai

Day la nhung gioi han quan trong cua luong hien tai.

### 1. Chua co extract text da dinh dang

He thong hien tai khong co extraction layer rieng cho:

- PDF
- DOCX
- HTML
- anh scan / OCR

No chi doc truc tiep text tu file `.md` va `.txt`.

### 2. Mat cau truc tai lieu khi chunk

Truoc khi chunk, service dang gom whitespace thanh mot dong text dai. Viec nay lam mat:

- heading
- paragraph boundary
- list structure
- code block boundary

Dieu nay co the lam retrieval kem chinh xac hon.

### 3. Metadata con it

Payload hien tai chua co cac metadata huu ich nhu:

- page number
- section
- element type
- checksum cua file
- extraction strategy

### 4. Chua co incremental indexing thuc su

He thong co ID on dinh theo `source + chunk_index`, nhung chua co co che:

- phat hien file thay doi
- bo chunk cu khong con ton tai
- skip file khong doi

## Y nghia cua `recreate_collection`

`recreate_collection` quyet dinh cach xu ly Qdrant collection truoc khi index:

- `false`: giu lai collection hien co, phu hop khi muon nap them hoac ghi de du lieu co cung ID
- `true`: xoa collection cu va tao lai toan bo, phu hop khi muon dong bo sach tu dau

Neu muon tranh du lieu cu ton tai sau nhieu lan thay doi source documents, cach an toan nhat hien tai la dung:

```json
{
  "recreate_collection": true
}
```

## Kiem tra nhanh sau khi chay

1. Goi `GET /rag/health` de xem:
   - Qdrant co ket noi duoc khong
   - collection co ton tai khong
   - co bao nhieu points da duoc index
2. Goi `POST /rag/query` voi mot cau hoi lien quan den file trong `docs/knowledge-base`
3. Kiem tra truong `sources` trong response de xem chunk nao da duoc truy hoi

## Huong cai tien de xuat

Neu can nang cap luong nay, thu tu uu tien hop ly la:

1. Bo whitespace flattening va chunk theo paragraph/section
2. Them extraction cho `.html` va `.docx`
3. Them extraction cho PDF text-based
4. Them OCR cho scanned PDF hoac image-based documents
5. Them metadata va incremental indexing
