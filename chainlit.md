# moce 🌺🤖

Greetings! 👋 

[I'm a local AI assistant](https://github.com/deadbits/moce) powered by Mixtral, Ollama, ChromaDB, Embedchain, and Chainlit.

## 💬 How to Get Started

Simply start a conversation with me by asking a question or sharing a document with `/add`.
```
/add https://huggingface.co/blog/shivance/illustrated-llm-os
```

### Chat Commands
| **command** | **action**                                       |
|-------------|--------------------------------------------------|
| /add        | add new document to the knowledge base           |
| /kb         | return last 25 documents added to knowledge base |
| *           | all other input is chat                          |

***

## Features
🗃️ **Knowledge Base:** I have access to a local Chroma database. You can add new documents with the `/add <url>` command or view the last 25 documents added to the database with the `/kb` command.

🌐 **Retrieval-Augmented-Generation:** My specialty is synthesizing answers from your data sources. Just provide me with the data or URLs you want to explore, and I'll find relevant information and provide comprehensive insights.

🔍 **Supported Data Types:** You can share data in formats like CSV, PDF, JSON, YouTube videos, text, documentation websites, DOCX, MDX, Notion, sitemaps, web pages, XML, OpenAPI specs, Gand even data from databases like Postgres, MySQL, Slack messages, Discourse forums, Discord conversations, Substack articles, files from a local directory, Dropbox files, and Beehiv data.

***

### Powered By
* https://ollama.ai/
* https://embedchain.ai/
* https://chainlit.io/