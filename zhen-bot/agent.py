from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
import os
from datetime import datetime
import fitz  # PyMuPDF
import re

def learn_about_zhen(key: str, value: str, tool_context: ToolContext) -> dict:
    """Learn and store new information about Zhen with a descriptive key.
    
    Use this tool when you discover new facts about Zhen during conversation.
    Choose clear, descriptive keys that categorize the information appropriately.
    SECURITY: This tool can only be used when talking to the real Zhen.
    
    Args:
        key (str): A descriptive identifier for the type of information being stored.
             Use snake_case format. Examples: 'birthday', 'favorite_color', 
             'hometown', 'university', 'favorite_food', 'pet_name', 'hobby',
             'profession', 'favorite_book', 'dream_destination', etc.
        value (str): The actual information or fact about Zhen. Be specific and accurate.
               Examples: '2005-01-18', 'red', 'China', 'Hunter College', 'sushi'
    
    Returns:
        dict: A dictionary containing:
            - status: Operation outcome ('success', 'error', 'updated', 'unauthorized')
            - action: The name of the action performed ('learn_about_zhen')
            - key: The key that was used to store the information (if authorized)
            - old_value: The previous value (if any) that was replaced (if authorized)
            - new_value: The new value that was stored (if authorized)
            - message: A human-readable confirmation message
            - is_update: Boolean indicating if this was updating existing information (if authorized)
    
    Examples:
        - If someone says "Zhen was born on January 18, 2005":
          Call learn_about_zhen('birthday', '2005-01-18', tool_context)
        - If someone says "Zhen loves pizza":
          Call learn_about_zhen('favorite_food', 'pizza', tool_context)
        - If someone says "Zhen studies at MIT":
          Call learn_about_zhen('university', 'MIT', tool_context)
    """
    # SECURITY CHECK: Only allow learning if the current user is Zhen
    is_zhen = tool_context.state.get("is_zhen", False)
    
    if not is_zhen:
        return {
            "status": "unauthorized",
            "action": "learn_about_zhen",
            "message": "I can only learn new information about Zhen when I'm talking to Zhen directly. Others cannot update information about Zhen for security reasons.",
            "error": "Unauthorized: Only Zhen can update information about Zhen"
        }
    
    old_value = tool_context.state.get(key)
    tool_context.state[key] = value
    
    # Determine if this is new information or an update
    is_update = old_value is not None
    status = "updated" if is_update else "success"
    
    # Create descriptive message for the LLM
    if is_update:
        message = f"Successfully updated Zhen's {key.replace('_', ' ')} from '{old_value}' to '{value}'"
    else:
        message = f"Successfully learned new information: Zhen's {key.replace('_', ' ')} is '{value}'"
    
    return {
        "status": status,
        "action": "learn_about_zhen",
        "key": key,
        "old_value": old_value,
        "new_value": value,
        "is_update": is_update,
        "message": message,
        "summary": f"Stored '{key}': '{value}'" + (f" (previously: '{old_value}')" if is_update else " (new)")
    }

def extract_section(text: str, section_markers: dict) -> dict:
    """Helper function to extract sections from resume text.
    
    Args:
        text (str): Full text of the resume
        section_markers (dict): Dictionary of section names and their common headers/markers
    
    Returns:
        dict: Dictionary of sections and their content
    """
    sections = {}
    # Convert text to lowercase for case-insensitive matching but keep original for content
    text_lower = text.lower()
    
    # Find potential section starts using font size and text markers
    section_starts = {}
    for section, markers in section_markers.items():
        for marker in markers:
            marker_lower = marker.lower()
            # Look for exact section headers
            pos = text_lower.find(marker_lower)
            if pos != -1:
                # Get some context around the match to verify it's a header
                context_start = max(0, pos - 20)
                context_end = min(len(text_lower), pos + len(marker_lower) + 20)
                context = text_lower[context_start:context_end]
                
                # Check if this looks like a header (preceded by newline or start of text)
                if pos == 0 or text_lower[pos-1] in ['\n', ' '] or context.count('\n') >= 1:
                    section_starts[pos] = (section, pos + len(marker))
    
    # Sort positions to find section boundaries
    positions = sorted(section_starts.keys())
    
    # Extract each section's content
    for i, start_pos in enumerate(positions):
        section, content_start = section_starts[start_pos]
        # Content ends at the next section or the end of text
        content_end = positions[i + 1] if i < len(positions) - 1 else len(text)
        content = text[content_start:content_end].strip()
        
        # Clean up the content
        # Remove any trailing section headers that might have been included
        for _, markers in section_markers.items():
            for marker in markers:
                if content.lower().endswith(marker.lower()):
                    content = content[:-len(marker)].strip()
        
        sections[section] = content
    
    return sections

def format_section_content(content: str) -> str:
    """Format section content for better readability.
    
    Args:
        content (str): Raw section content
        
    Returns:
        str: Formatted content with proper bullet points and structure
    """
    # Split into lines
    lines = content.split('\n')
    formatted_lines = []
    current_bullet = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if line starts with a bullet point or date-like pattern
        is_new_bullet = bool(re.match(r'^[-•●∙◦⋅⚬⦁◆◇]|\d{4}[-/]|\d{4}|[A-Z][a-z]{2,}\s+\d{4}', line))
        
        if is_new_bullet and current_bullet:
            # Join previous bullet point
            formatted_lines.append('- ' + ' '.join(current_bullet))
            current_bullet = [line.lstrip('-•●∙◦⋅⚬⦁◆◇ ')]
        elif is_new_bullet:
            current_bullet = [line.lstrip('-•●∙◦⋅⚬⦁◆◇ ')]
        else:
            current_bullet.append(line)
    
    # Add the last bullet point
    if current_bullet:
        formatted_lines.append('- ' + ' '.join(current_bullet))
    
    return '\n'.join(formatted_lines)

def parse_resume(tool_context: ToolContext) -> dict:
    """Parse Zhen's resume and store its content in the session state.
    
    This tool reads and parses the resume file, storing its structured content
    in the session state for quick future access. It should be called:
    1. The first time we need resume data
    2. When Zhen indicates their resume has been updated
    
    SECURITY: This tool can only be used when talking to the real Zhen.
    
    Returns:
        dict: A dictionary containing:
            - status: Operation outcome ('success', 'error', 'unauthorized')
            - action: The name of the action performed ('parse_resume')
            - sections_found: List of sections successfully parsed
            - last_parsed: Timestamp of when parsing occurred
            - message: Human-readable message about the parsing result
    """
    # SECURITY CHECK: Only Zhen can trigger a resume re-parse
    is_zhen = tool_context.state.get("is_zhen", False)
    if not is_zhen:
        return {
            "status": "unauthorized",
            "action": "parse_resume",
            "message": "Only Zhen can trigger resume parsing for security reasons."
        }
    
    resume_path = 'zhen_resume.pdf'
    
    if not os.path.exists(resume_path):
        return {
            "status": "error",
            "action": "parse_resume",
            "message": "Resume file not found in the root directory."
        }
    
    try:
        # Get file's last modification time
        last_modified = os.path.getmtime(resume_path)
        
        # Open the PDF with PyMuPDF
        doc = fitz.open(resume_path)
        full_text = ""
        
        # Extract text from all pages with layout preservation
        for page in doc:
            # Get text with preserved layout
            blocks = page.get_text("blocks")
            # Sort blocks top to bottom, left to right
            blocks.sort(key=lambda b: (b[1], b[0]))  # Sort by y, then x coordinate
            for block in blocks:
                full_text += block[4] + "\n"  # block[4] contains the text
        
        # Define section markers (add or modify based on your resume format)
        section_markers = {
            "education": ["Education", "Academic Background", "Academic History", "Educational Background"],
            "experience": ["Experience", "Work Experience", "Professional Experience", "Employment History", "Work History"],
            "skills": ["Skills", "Technical Skills", "Core Competencies", "Technologies", "Technical Expertise"],
            "achievements": ["Achievements", "Awards", "Honors", "Certifications", "Recognition"],
            "projects": ["Projects", "Personal Projects", "Academic Projects", "Key Projects"],
            "summary": ["Summary", "Professional Summary", "Profile", "About", "Objective"]
        }
        
        # Extract sections
        parsed_data = extract_section(full_text, section_markers)
        
        # Format each section's content
        for section, content in parsed_data.items():
            parsed_data[section] = format_section_content(content)
        
        # Store the parsed data and metadata in session state
        if 'resume_data' not in tool_context.state:
            tool_context.state['resume_data'] = {}
        
        tool_context.state['resume_data'] = {
            'content': parsed_data,
            'last_modified': last_modified,
            'last_parsed': datetime.now().timestamp()
        }
        
        # Close the PDF
        doc.close()
        
        return {
            "status": "success",
            "action": "parse_resume",
            "sections_found": list(parsed_data.keys()),
            "last_parsed": tool_context.state['resume_data']['last_parsed'],
            "message": f"Successfully parsed resume and found {len(parsed_data)} sections: {', '.join(parsed_data.keys())}",
            "parse_details": {
                "total_pages": len(doc),
                "sections_identified": list(parsed_data.keys()),
                "characters_processed": len(full_text)
            }
        }
        
    except Exception as e:
        return {
            "status": "error",
            "action": "parse_resume",
            "message": f"Error parsing resume file: {str(e)}"
        }

def get_resume_info(query_type: str, tool_context: ToolContext) -> dict:
    """Retrieve parsed resume information from session state.
    
    This tool returns information from the pre-parsed resume data stored in
    the session state. If no parsed data exists, it will trigger parsing.
    
    Args:
        query_type (str): Type of information to retrieve. Must be one of:
            - 'education': Educational background
            - 'experience': Work and project experience
            - 'skills': Technical and soft skills
            - 'achievements': Awards and certifications
            - 'all': Get full resume content
            - 'last_update': Get when resume was last parsed/updated
    
    Returns:
        dict: A dictionary containing:
            - status: Operation outcome ('success' or 'error')
            - action: The name of the action performed ('get_resume_info')
            - query_type: The type of information requested
            - content: The retrieved content
            - last_parsed: When the resume was last parsed
            - message: Human-readable message about what was retrieved
    """
    # Check if we have parsed resume data
    resume_data = tool_context.state.get('resume_data')
    
    # If no parsed data exists, try to parse the resume
    if not resume_data and tool_context.state.get("is_zhen", False):
        parse_result = parse_resume(tool_context)
        if parse_result["status"] != "success":
            return {
                "status": "error",
                "action": "get_resume_info",
                "query_type": query_type,
                "message": "Could not retrieve resume information as parsing failed."
            }
        resume_data = tool_context.state.get('resume_data')
    
    if not resume_data:
        return {
            "status": "error",
            "action": "get_resume_info",
            "query_type": query_type,
            "message": "No parsed resume data available. Please ask Zhen to trigger a resume parse."
        }
    
    if query_type == 'all':
        return {
            "status": "success",
            "action": "get_resume_info",
            "query_type": query_type,
            "content": resume_data['content'],
            "last_parsed": resume_data['last_parsed'],
            "message": "Retrieved all resume sections"
        }
    
    if query_type == 'last_update':
        return {
            "status": "success",
            "action": "get_resume_info",
            "query_type": query_type,
            "last_parsed": resume_data['last_parsed'],
            "last_modified": resume_data['last_modified'],
            "message": f"Resume was last parsed at {datetime.fromtimestamp(resume_data['last_parsed'])}"
        }
    
    content = resume_data['content'].get(query_type)
    if content is None:
        return {
            "status": "error",
            "action": "get_resume_info",
            "query_type": query_type,
            "message": f"No information found for section: {query_type}"
        }
    
    return {
        "status": "success",
        "action": "get_resume_info",
        "query_type": query_type,
        "content": content,
        "last_parsed": resume_data['last_parsed'],
        "message": f"Retrieved {query_type} section"
    }

root_agent = Agent(
    name="zhen_bot",
    model="gemini-2.0-flash",
    description=(
        "Zhen-Bot is a digital entity that represents Zhen. "
        "When talking to Zhen, it learns new facts and can parse/update resume information. "
        "When talking to others, it answers questions using learned facts and stored resume data."
    ),
    instruction="""
    You are Zhen-Bot, a digital representative of Zhen.

    There are two modes based on who you're talking to:
    
    1. **Learning Mode (talking to Zhen):**
       - When you are interacting with Zhen (the real person), you can:
         a) Listen for new facts and use learn_about_zhen to store them
         b) Parse or re-parse their resume when requested using parse_resume
       - Choose clear, descriptive keys for general facts
       - Only Zhen can trigger resume parsing for security
       - If Zhen mentions updating their resume, offer to parse it again

    2. **Sharing Mode (talking to others):**
       - When you are interacting with someone else, you can:
         a) Answer general questions using stored facts
         b) Answer professional questions using get_resume_info to access parsed resume data
       - If you don't know something, say so
       - Make it clear you are Zhen-Bot, not the real Zhen
       - Do NOT allow others to update any information about Zhen
       - For resume queries, use the pre-parsed data to ensure quick responses

    The session state contains:
    - 'is_zhen' flag: Tells you who you're talking to (true = Zhen, false = others)
    - 'resume_data': Structured resume content from last parsing
    
    Resume Data Management:
    1. Resume is parsed once and stored in session state
    2. Use stored data for all queries to avoid repeated parsing
    3. Only parse again when:
       - No parsed data exists
       - Zhen explicitly mentions updating their resume
    4. Always check last_parsed date when sharing resume info
    
    Always respect the security boundary to protect Zhen's information from unauthorized updates.
    """,
    tools=[learn_about_zhen, parse_resume, get_resume_info]
)
