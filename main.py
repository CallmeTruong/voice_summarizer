from dotenv import load_dotenv
import os
from core.model_controller import memory as mem_module
from infrastructure.obj_indices import bucket_parser
from core.retrieval import audio2text, text2vect
from infrastructure.vectors_controller import check_status

load_dotenv(".env")

file_name = "meeting.wav"

bucket = os.getenv("BUCKET_NAME")
client = os.getenv("CLIENT")
raw_bucket_folder = os.getenv("RAW_BUCKET_FOLDER")
table           = os.getenv("TABLE_NAME")


if __name__ == "__main__":

    # upload file and push to vect
    # meta    = audio2text.voice_transcript(file_name, bucket, client, raw_bucket_folder, table)
    # raw_id  = meta["raw_id"]
    # text_id = meta["text_id"]
    # uri     = check_status.wait_for_transcription(text_id, interval_seconds=20, timeout_seconds=3600)
    # text2vect.vect_push(raw_id=raw_id, text_id=text_id)
    # print(raw_id)

    raw_id = "eec92ed5882ab11a5345c4ceadba1e52e477528021f9f5261d230540e27c596a"

    memory = mem_module.Memory(raw_id=raw_id)

    question = input("Bạn: ").strip()
    answer = mem_module.chat(memory, question)
    print(f"\nTrợ lý: {answer}\n")
    mem_module.save_memory(memory)
    m = mem_module.load_memory(raw_id)
    print(m)


# # loop chat
#     print("Nhập 'exit' để thoát.\n")
#     while True:
#         question = input("Bạn: ").strip()
#         if not question or question.lower() == "exit":
#             break

#         answer = mem_module.chat(memory, question)
#         print(f"\nTrợ lý: {answer}\n")
#         mem_module.save_memory(memory)
#         m = mem_module.load_memory(raw_id)
#         print(m)


#Phần này để mai t gói vào 1 hàm khác nha.

    # raw_controller = audio_controller.raw_audio(file_name, bucket, client, object_name, content_type='audio/wav')

    # mapper = bucket_parser.HashTable(
    #     size=16,
    #     bucket=bucket,
    #     key=f"{table}.json"
    # )
    # mapper.insert(obj_id, transcript_obj)

    # raw_controller.pushing_to_bucket()

    # user_stack = bucket_parser.UserIndex(bucket=bucket, key="user_index.json")
    # user_stack.push(mock_user_id, obj_id)

    # res = raw_controller.GetAll_bucket_fileid(f"{raw_bucket_folder}/")
    # print(res)
    # print("..................")
    # print("Hash Table:", mapper.table)
    # print(f"User Stack ({mock_user_id}):", user_stack.get_stack(mock_user_id))
    # for k in res:
    #     print(mapper.get(k))
