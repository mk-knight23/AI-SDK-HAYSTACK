# AI-SDK-HAYSTACK

[![AI-SDK Ecosystem](https://img.shields.io/badge/AI--SDK-ECOSYSTEM-part%20of-blue)](https://github.com/mk-knight23/AI-SDK-ECOSYSTEM)
[![Haystack](https://img.shields.io/badge/Haystack-2.0-11a36a8)](https://haystack.deepset.ai/)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3.15-green)](https://nuxt.com/)
[![Django](https://img.shields.io/badge/Django-5.1-green)](https://www.djangoproject.com/)

> **Framework**: Haystack (Document AI & Extractive QA)
> **Stack**: Nuxt 3 + Django

---

## 🎯 Project Overview

**AI-SDK-HAYSTACK** demonstrates industrial document AI with extractive question answering and hybrid retrieval. It showcases Haystack 2.0 for building production search systems, RAG pipelines, and document intelligence applications.

### Key Features

- 🔍 **Extractive QA** - Pinpoint answers in large documents
- 📄 **Document Processing** - PDF, DOCX, TXT parsing
- 🎯 **Hybrid Retrieval** - BM25 + DPR for optimal results
- 🔗 **Elasticsearch** - Scalable document storage
- 🔄 **RAG Pipeline** - Production retrieval-augmented generation

---

## 🛠 Tech Stack

| Technology | Purpose |
|-------------|---------|
| Nuxt 3 | Frontend framework |
| Django | Backend API |
| Haystack 2.0 | AI framework |
| Elasticsearch | Document search |
| Naive UI | Components |
| Celery | Background tasks |

---

## 🚀 Quick Start

```bash
# Frontend
cd frontend && npm install && npm run dev

# Backend
cd backend && python manage.py migrate && python manage.py runserver
```

---

## 🔌 API Integrations

| Provider | Usage |
|----------|-------|
| Mistral | Embeddings |
| Deepgram | Audio input |
| iLovePDF | PDF conversion |
| ConvertAPI | Document processing |

---

## 📦 Deployment

**Render** (Backend) + **Netlify** (Frontend)

```bash
railway up  # backend
netlify deploy  # frontend
```

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

**Part of the [AI-SDK Ecosystem](https://github.com/mk-knight23/AI-SDK-ECOSYSTEM)**
