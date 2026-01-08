from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os
from openai import OpenAI
import base64


def encode_image(file_path: str):
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode("utf-8")


client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)


async def process_file(id: str, file_path: str):
    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "processing"
        }
    })

    # convert pdf to image
    pages = convert_from_path(file_path)
    images = []
    for i, page in enumerate(pages):
        image_save_path = f"/mnt/uploads/images/{id}/image-{i}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, 'JPEG')
        images.append(image_save_path)

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "conversion complete"
        }
    })

    # ai call
    base64_images = [encode_image(img) for img in images]

    result = client.responses.create(
        model="gpt-4.1",
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "this is a resume, you need to roast this person based on that"},
                    {
                        "type": "input_image",
                        "image_url":
                            f"data:image/jpeg;base64,{base64_images[0]}",
                    },
                ],
            }
        ],
    )
    
    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "api call done",
            "result": result.output_text
        }
    })
    print(result.output_text)
