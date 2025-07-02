from flask import Flask, render_template, request
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import CharacterTextSplitter
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.6, api_key=os.getenv("GOOGLE_API_KEY"))
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")


def load_resume_examples():
    """Loads resume section examples from a file or uses a default."""
    try:
        with open("resume_examples.txt", "r") as f:
            return f.read()
    except FileNotFoundError:
        print("Warning: resume_examples.txt not found. Using default examples.")
        return """
        [Professional Summary Example]
        Dynamic and results-oriented Software Engineer with 5+ years of experience in developing, testing, and maintaining scalable web applications. Proficient in Python, Django, and React. Seeking to leverage expertise in full-stack development to contribute to the innovative team at [Company Name].

        [Work Experience Example - Action Verbs]
        - Led the development of a new customer-facing feature using React and Redux, resulting in a 15% increase in user engagement.
        - Architected and implemented a RESTful API service with Python and Django, improving system response time by 30%.
        - Collaborated with a cross-functional team of 5 to define project requirements and deliver solutions ahead of schedule.
        - Optimized database queries and caching mechanisms, reducing server load by 20%.

        [Skills Section Example]
        - Languages: Python, JavaScript, SQL, HTML/CSS
        - Frameworks: Django, Flask, React, Node.js
        - Databases: PostgreSQL, MongoDB, Redis
        - Tools: Docker, Git, Jenkins, AWS

        [Project Section Example]
        - Personal Portfolio Website: Developed a fully responsive personal website using Flask and deployed on Heroku to showcase projects.
        - E-commerce Analytics Dashboard: Built a data visualization tool with Plotly Dash to track sales metrics and customer behavior for a mock e-commerce site.
        """

def create_vector_store():
    """Creates a FAISS vector store from the resume examples."""
    resume_text = load_resume_examples()
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    chunks = text_splitter.split_text(resume_text)
    return FAISS.from_texts(chunks, embedding=embeddings)

vector_store = create_vector_store()
retriever = vector_store.as_retriever(search_kwargs={"k": 3})


resume_prompt = PromptTemplate(
    input_variables=["context", "job_description", "user_details", "full_name", "contact_info"],
    template="""
    You are an expert resume writer and career coach. Your task is to create a professional, tailored resume based on the user's details and a specific job description.
    Use the following examples of well-written resume sections as a reference for tone, style, and use of action verbs:
    ---
    {context}
    ---

    Now, generate the key sections of a resume for the user.

    **User's Full Name:** {full_name}
    **User's Contact Info:** {contact_info}
    **Target Job Description:**
    {job_description}

    **User's Raw Details (Experience, Skills, Education):**
    {user_details}

    **Instructions:**
    1.  Write a "Professional Summary" that is concise (3-4 sentences) and highlights the user's most relevant qualifications for the target job.
    2.  Rewrite the user's "Work Experience" using strong action verbs. Focus on achievements and metrics (e.g., "increased sales by 15%") that align with the job description.
    3.  Create a "Skills" section that is clean and lists the most relevant technical and soft skills for the job.
    4.  Structure your entire response with the following clear separators. DO NOT add any other text before or after these sections.

    [--NAME--]
    [User's Full Name]

    [--CONTACT--]
    [User's Contact Info]

    [--SUMMARY--]
    [Generated Professional Summary Here]

    [--EXPERIENCE--]
    [Generated and Formatted Work Experience Here]

    [--SKILLS--]
    [Generated Skills List Here]
    """
)

resume_chain = resume_prompt | llm

def parse_section(text, start_marker, end_marker):
    """Safely extracts a section from the LLM's response."""
    try:
        start_index = text.index(start_marker) + len(start_marker)
        end_index = text.index(end_marker, start_index)
        return text[start_index:end_index].strip()
    except ValueError:
        return "" 

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        full_name = request.form['full_name']
        contact_info = request.form['contact_info']
        job_description = request.form['job_description']
        user_details = request.form['user_details']
        
        query_text = f"Job: {job_description}\nUser Info: {user_details}"
        relevant_docs = retriever.get_relevant_documents(query_text)
        context = "\n\n".join([doc.page_content for doc in relevant_docs])
        
        try:
            result_object = resume_chain.invoke({
                "context": context,
                "job_description": job_description,
                "user_details": user_details,
                "full_name": full_name,
                "contact_info": contact_info
            })
            result = result_object.content
            
            name = parse_section(result, '[--NAME--]', '[--CONTACT--]')
            contact = parse_section(result, '[--CONTACT--]', '[--SUMMARY--]')
            summary = parse_section(result, '[--SUMMARY--]', '[--EXPERIENCE--]')
            experience = parse_section(result, '[--EXPERIENCE--]', '[--SKILLS--]')
            
            skills = ""
            if '[--SKILLS--]' in result:
                skills = result.split('[--SKILLS--]')[-1].strip()

            resume_data = {
                'name': name,
                'contact': contact,
                'summary': summary,
                'experience': experience,
                'skills': skills
            }
            
            return render_template('index.html', resume=resume_data)
            
        except Exception as e:
            error = f"Error generating resume: {str(e)}"
            return render_template('index.html', error_message=error)
    
    return render_template('index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)