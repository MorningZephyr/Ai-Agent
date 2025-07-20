from google.adk.agents import LlmAgent
from pydantic import BaseModel, Field

# --- Define Output Schema ---
class EmailContent(BaseModel):
    subject: str = Field(
        description="The subject of the email. Should be concise and descriptive"
    )
    body: str = Field(
        description="The main body of the email. Should be well-informed with proper greeting, paragraph, and concluding signature"
    )

# --- Create Email Generator Agent --- 
root_agent = LlmAgent(
    name="output_agent",
    model="gemini-2.0-flash",
    instruction="""
        You are an email generation assistant.
        Your task is to generate a professional email based on the user's request.

        Guidelines:
        - Create an appropriate subject line (concise and conherent)
        - craft a well structured body paragraph with:
            * professional greeting
            * clear and concise main content
            * Appropriate ending
            * Your name as signature
        - suggest relevant attachments if applicable (empty list if none needed)
        - keep emails concise but complete
    
        IMPORTANT: your response must be a valid JSON matching this structure:
        {
            "subject" : "The subject of the email. Should be concise and descriptive",
            "body" : "The main body of the email. Should be well-informed with proper greeting, paragraph, and concluding signature"
        }

        The JSON is all you need to give in the end
    """,
    description="Generates professional emails with structured subject and body",
    output_schema=EmailContent,
    output_key="email"
)