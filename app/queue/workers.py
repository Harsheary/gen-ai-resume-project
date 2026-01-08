from ..workflows.resume_analysis import create_resume_analysis_workflow
from bson import ObjectId
from pdf2image import convert_from_path
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()


def process_file(id: str, file_path: str, job_description: str):
    # Create synchronous MongoDB client for worker
    sync_mongo_client = MongoClient("mongodb://admin:admin@mongo:27017")
    sync_db = sync_mongo_client["mydb"]
    files_collection = sync_db["files"]
    
    try:
        # Update status to processing
        files_collection.update_one({"_id": ObjectId(id)}, {
            "$set": {
                "status": "processing"
            }
        })

        # Convert PDF to images
        pages = convert_from_path(file_path)
        images = []
        for i, page in enumerate(pages):
            image_save_path = f"/mnt/uploads/images/{id}/image-{i}.jpg"
            os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
            page.save(image_save_path, 'JPEG')
            images.append(image_save_path)

        files_collection.update_one({"_id": ObjectId(id)}, {
            "$set": {
                "status": "conversion complete"
            }
        })

        # Create and run LangGraph workflow
        files_collection.update_one({"_id": ObjectId(id)}, {
            "$set": {
                "status": "enhancing job description"
            }
        })
        
        # Initialize workflow
        workflow = create_resume_analysis_workflow()
        
        # Prepare initial state
        initial_state = {
            "file_id": id,
            "job_description": job_description,
            "enhanced_job_description": None,
            "resume_images": images,
            "match_score": None,
            "improvements": None,
            "weaknesses": None,
            "summary": None,
            "error": None
        }
        
        # Run the workflow
        final_state = workflow.invoke(initial_state)
        
        # Update status for analysis phase
        files_collection.update_one({"_id": ObjectId(id)}, {
            "$set": {
                "status": "analyzing resume match"
            }
        })
        
        # Store results in database
        analysis_result = {
            "match_score": final_state.get("match_score"),
            "improvements": final_state.get("improvements", []),
            "weaknesses": final_state.get("weaknesses", []),
            "summary": final_state.get("summary", "")
        }
        
        update_data = {
            "status": "completed",
            "enhanced_job_description": final_state.get("enhanced_job_description"),
            "analysis": analysis_result,
            "result": final_state.get("summary", "")
        }
        
        # Add error if present
        if final_state.get("error"):
            update_data["error"] = final_state["error"]
            update_data["status"] = "error"
        
        files_collection.update_one({"_id": ObjectId(id)}, {
            "$set": update_data
        })
        
        print(f"Analysis complete for file {id}")
        print(f"Match Score: {analysis_result['match_score']}")
        print(f"Summary: {analysis_result['summary']}")
        
    except Exception as e:
        # handle any errors and update database
        error_message = f"Error processing file: {str(e)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        try:
            files_collection.update_one({"_id": ObjectId(id)}, {
                "$set": {
                    "status": "error",
                    "error": error_message
                }
            })
        except Exception as db_error:
            print(f"Failed to update error status in database: {str(db_error)}")
        finally:
            # close MongoDB connection
            sync_mongo_client.close()
