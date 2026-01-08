from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
import os
import json
import base64


class ResumeAnalysisState(TypedDict):
    """State schema for the resume analysis workflow"""
    file_id: str
    job_description: str
    enhanced_job_description: Optional[str]
    resume_images: List[str]
    match_score: Optional[int]
    improvements: Optional[List[str]]
    weaknesses: Optional[List[str]]
    summary: Optional[str]
    error: Optional[str]


def encode_image(file_path: str) -> str:
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode("utf-8")


def enhance_job_description_node(state: ResumeAnalysisState) -> ResumeAnalysisState:
    """
    Node 1: Enhance and structure the job description using OpenAI
    """
    try:
        llm = ChatOpenAI(
            model="gpt-4o-mini",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.3
        )
        
        system_prompt = """You are an expert recruiter and talent acquisition specialist. 
Your task is to enhance and structure job descriptions to make them comprehensive and well-organized.

When given a job description, you should:
1. Clearly identify and organize key requirements
2. List required technical skills and qualifications
3. Highlight important soft skills and competencies
4. Structure responsibilities in a clear manner
5. Identify must-have vs nice-to-have qualifications
6. Make the description comprehensive yet concise

Return the enhanced job description in a well-structured format."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Please enhance and structure this job description:\n\n{state['job_description']}"}
        ]
        
        response = llm.invoke(messages)
        enhanced_jd = response.content
        
        return {
            **state,
            "enhanced_job_description": enhanced_jd
        }
    except Exception as e:
        return {
            **state,
            "error": f"Error enhancing job description: {str(e)}"
        }


def analyze_resume_match_node(state: ResumeAnalysisState) -> ResumeAnalysisState:
    """
    Node 2: Analyze resume against enhanced job description using OpenAI Vision API
    """
    try:
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=os.getenv("OPENAI_API_KEY"),
            temperature=0.3
        )
        
        system_prompt = """You are an expert resume reviewer and career advisor.
Your task is to analyze a resume against a job description and provide comprehensive feedback.

You must provide your analysis in the following JSON format:
{
    "match_score": <integer between 0-100>,
    "improvements": [<list of specific improvements the candidate should make>],
    "weaknesses": [<list of gaps or weaknesses compared to the job requirements>],
    "summary": "<overall narrative assessment of the candidate's fit for the role>"
}

Be specific, constructive, and actionable in your feedback. Focus on:
1. How well the candidate's experience matches the job requirements
2. Missing qualifications or skills
3. Areas where the resume could be strengthened
4. Overall suitability for the position

Return ONLY the JSON object, no additional text."""

        # Encode resume images
        base64_images = [encode_image(img) for img in state['resume_images']]
        
        # Build content with images
        content = [
            {"type": "text", "text": f"Job Description:\n{state['enhanced_job_description']}\n\nPlease analyze the resume images below against this job description."}
        ]
        
        # Add all resume page images
        for base64_image in base64_images:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
        
        response = llm.invoke(messages)
        
        # Parse the JSON response
        try:
            analysis_result = json.loads(response.content)
            
            return {
                **state,
                "match_score": analysis_result.get("match_score"),
                "improvements": analysis_result.get("improvements", []),
                "weaknesses": analysis_result.get("weaknesses", []),
                "summary": analysis_result.get("summary", "")
            }
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract information from text
            return {
                **state,
                "match_score": None,
                "improvements": [],
                "weaknesses": [],
                "summary": response.content,
                "error": "Could not parse structured response, returning raw text"
            }
            
    except Exception as e:
        return {
            **state,
            "error": f"Error analyzing resume: {str(e)}"
        }


def create_resume_analysis_workflow() -> StateGraph:
    """
    Create and compile the LangGraph workflow for resume analysis
    """
    # Create the graph
    workflow = StateGraph(ResumeAnalysisState)
    
    # Add nodes
    workflow.add_node("enhance_job_description", enhance_job_description_node)
    workflow.add_node("analyze_resume_match", analyze_resume_match_node)
    
    # Define edges
    workflow.set_entry_point("enhance_job_description")
    workflow.add_edge("enhance_job_description", "analyze_resume_match")
    workflow.add_edge("analyze_resume_match", END)
    
    # Compile the workflow
    return workflow.compile()
