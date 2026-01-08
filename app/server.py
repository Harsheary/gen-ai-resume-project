from fastapi import FastAPI, UploadFile, Path, Form
from .utils.file import save_to_disc
from .db.collections.files import files_collection, FileSchema
from .queue.q import q
from .queue.workers import process_file
from bson import ObjectId

app = FastAPI()


@app.get('/{id}')
async def get_file_by_id(id: str = Path(..., description="ID of the file")):
    db_file = await files_collection.find_one({"_id": ObjectId(id)})
    
    return {
        "_id": str(db_file["_id"]),
        "name": db_file["name"],
        "status": db_file["status"],
        "job_description": db_file.get("job_description"),
        "enhanced_job_description": db_file.get("enhanced_job_description"),
        "result": db_file.get("result"),
        "analysis": db_file.get("analysis")
    }


@app.get("/")
def hello():
    return {"status": "healthy"}


@app.post("/upload")
async def upload_file(file: UploadFile, job_description: str = Form(...)):
    # entry in mongo
    db_file = await files_collection.insert_one(
        document=FileSchema(
            name=file.filename,
            status="saving",
            job_description=job_description
        )
    )

    # save to disc
    file_path = f"/mnt/uploads/{str(db_file.inserted_id)}/{file.filename}"
    await save_to_disc(file=await file.read(), path=file_path)
    
    # push to queue
    q.enqueue(process_file, str(db_file.inserted_id), file_path=file_path, job_description=job_description)

    # mongo save
    await files_collection.update_one({"_id": db_file.inserted_id}, {
        "$set": {
            "status": "queued"
        }
    })
    return {"file_id": str(db_file.inserted_id)}
