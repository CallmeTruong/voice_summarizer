from dataclasses import dataclass, field
from collections import deque
from . import router 
from . import model_caller
import os
import boto3

WORKING_WINDOW = 10
SUMMARY_MAX_LINES = 30
SOURCE_HISTORY = 50
SOURCE_MAX_CHARS = 50
CHAT_HISTORY = 200

DEBUG = str(os.getenv("DEBUG"))
REGION = str(os.getenv("REGION"))

dynamodb = boto3.resource("dynamodb", REGION)
table = dynamodb.Table(str(os.getenv("MEMORY_TABLE")))

@dataclass
class Memory:
    raw_id:  str
    text_id: str | None = None
    summary: str        = ""
    working: deque      = field(default_factory=lambda: deque(maxlen=WORKING_WINDOW))
    chat_history: deque = field(default_factory=lambda: deque(maxlen = CHAT_HISTORY))
    sources:      deque      = field(default_factory=lambda: deque(maxlen=SOURCE_HISTORY))


_BASE_SYSTEM = """Bạn là trợ lý phân tích nội dung file âm thanh đã được chuyển thành văn bản.
Toàn bộ nội dung file đã được chia thành các đoạn nhỏ và lưu vào cơ sở dữ liệu.
Mỗi câu hỏi của người dùng, hệ thống sẽ tự động tìm và cung cấp các đoạn liên quan cho bạn.

Nguyên tắc:
- LUÔN trả lời dựa trên ngữ cảnh được cung cấp bên trong thẻ <context>
- Không bao giờ nhắc đến "<context>", "[Ngữ cảnh tài liệu]", "id:", "chunk", "đoạn số" trong câu trả lời
- Nếu ngữ cảnh trống, hãy nói: "Tôi không tìm thấy thông tin liên quan trong file"
- Không nói "bạn chưa cung cấp tài liệu" — tài liệu luôn có sẵn trong hệ thống
- Nếu người dùng hỏi "phần nào / đoạn nào / lúc nào", hãy mô tả bằng ngôn ngữ tự nhiên dựa vào nội dung, ví dụ: "Điều này được đề cập trong phần thảo luận về chiến lược nội dung"
- Nếu câu hỏi là chào hỏi hoặc không liên quan tài liệu, trả lời tự nhiên ngắn gọn
- Cuối mỗi câu trả lời có nội dung tài liệu, thêm: SUMMARY_UPDATE: <tóm tắt 1 câu>"""


def _build_messages(memory: Memory, question: str, doc_context: str) -> list[dict]:
    system_parts = [_BASE_SYSTEM]

    if memory.summary:
        system_parts.append(f"\n[Tóm tắt hội thoại trước]\n{memory.summary}")

    messages = [{"role": "system", "content": "\n".join(system_parts)}]
    messages.extend(list(memory.working))

    if doc_context:
        user_content = f"<context>\n{doc_context}\n</context>\n\n{question}"
    else:
        user_content = question

    messages.append({"role": "user", "content": user_content})
    return messages

def _extract_and_update_summary(memory: Memory, raw_answer: str) -> str:

    if "SUMMARY_UPDATE:" not in raw_answer:
        return raw_answer

    parts = raw_answer.split("SUMMARY_UPDATE:", 1)
    clean_answer   = parts[0].strip()
    new_summary_line = parts[1].strip().splitlines()[0].strip()

    lines = memory.summary.splitlines() if memory.summary else []
    lines.append(new_summary_line)
    if len(lines) > SUMMARY_MAX_LINES:
        lines = lines[-SUMMARY_MAX_LINES:]
    memory.summary = "\n".join(lines)

    return clean_answer

def chat(memory: Memory, question: str) -> str:
    search_result = router.route_and_search(question, memory.raw_id, memory.text_id)
    chunks = search_result.get("vectors", []) if search_result else []
    doc_context = "\n\n".join(
        c.get("metadata", {}).get("source_text", "") for c in chunks
    )
    source_meta = [
        {
            "topic_label": c.get("metadata", {}).get("topic_label", ""),
            "segment_idx": c.get("metadata", {}).get("segment_idx", ""),
            "text":        c.get("metadata", {}).get("source_text", "")[:SOURCE_MAX_CHARS] + "..."
                           if len(c.get("metadata", {}).get("source_text", "")) > SOURCE_MAX_CHARS
                           else c.get("metadata", {}).get("source_text", ""),
        }
        for c in chunks[:15]
    ]

    if DEBUG == "True":
        print(f"[DEBUG] raw_id={memory.raw_id} | text_id={memory.text_id}")
        print(f"[DEBUG] search_result={search_result}")
        print(f"[DEBUG] chunks count={len(chunks)}")

    messages = _build_messages(memory, question, doc_context)
    raw_answer = model_caller.get_model_response(messages)
    answer = _extract_and_update_summary(memory, raw_answer)

    memory.working.append({"role": "user",      "content": question})
    memory.working.append({"role": "assistant",  "content": answer})

    memory.chat_history.append({"role": "user",      "content": question})
    memory.chat_history.append({"role": "assistant",  "content": answer})
    memory.sources.append({
        "question": question,
        "sources":  source_meta,
    })

    return answer

def memory_to_item(memory: Memory) -> dict:
    return {
        "raw_id": memory.raw_id,
        "text_id": memory.text_id,
        "summary": memory.summary,
        "working": list(memory.working),
        "chat_history": list(memory.chat_history),
        "sources": list(memory.sources)
    }

def item_to_memory(item: dict) -> Memory:
    mem = Memory(
        raw_id=item["raw_id"],
        text_id=item.get("text_id"),
        summary=item.get("summary", "")
    )
    mem.working = deque(item.get("working", []), maxlen=WORKING_WINDOW)
    mem.chat_history = deque(item.get("chat_history", []), maxlen=CHAT_HISTORY)
    mem.sources = deque(item.get("sources", []), maxlen=SOURCE_HISTORY)

    return mem

def save_memory(memory: Memory):
    item = memory_to_item(memory)
    table.put_item(Item=item)

def load_memory(raw_id) -> Memory | None:
    res = table.get_item(Key={"raw_id": raw_id})
    item = res.get("Item")
    if not item:
        return None
    return item_to_memory(item)