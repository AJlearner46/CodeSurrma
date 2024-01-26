# ---------------------------------------------------------------------------------------------
# All Imports 

import streamlit as st
# import json
import os
from openai import OpenAI 
#from streamlit_ace import st_ace
from github import Auth, Github

# ---------------------------------------------------------------------------------------------
# All helper Functionms


def fetch_file_path(repo, file_name):
    try:
        # contents of the repository root
        root_contents = repo.get_contents("")

        for content in root_contents:
            if content.name == file_name:
                return content.path 
    except Exception as e:
        raise RuntimeError(f"Error Fetching file path: {str(e)}")


# to fetch file contents from GitHub
def fetch_file_from_github(repo, file_path):
    contents = repo.get_contents(file_path)
    return contents.decoded_content.decode('utf-8')

# to list files in a GitHub repository
def list_files_in_repo(repo):
    files = []
    for content in repo.get_contents(""):
        if content.type == "file":
            files.append(content.path)
    return files

# to check if query is null or not
def check_if_not_null(query):
    if(query == ""):
        return 0
    else:
        return 1
    
# ---------------------------------------------------------------------------------------------
# Review Code
    
def prompt_to_llm_code_review(prompt):
    agent = """You are a helpful and experienced software engineer who is expert in explaning complex code in easy to understand terms."""

    client = OpenAI()

    response = client.chat.completions.create(
                
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": agent},
                         {"role": "user", "content": prompt}]
                )
    
    return response['choices'][0]['message']['content']

def review_code(query):
    # pass
    if(check_if_not_null(query)):
        #prompt_head = "\n\"\"\nHere's what the above code is doing:\n"
        #prompt = query + prompt_head
        #print(prompt)
        return prompt_to_llm_code_review(query)
    else:
        return "No Input"
    
# ---------------------------------------------------------------------------------------------
# Optimize Code  
      
def optimize_code(query, input_lang):
    if(check_if_not_null(query)):
        prompt_head = f"##### Improve the time complexity and memory usage for the below code\n   \n### Given {input_lang} code\n{query}\n   \n### Improved code"
        prompt = prompt_head
        print(prompt)
        return prompt_to_llm_optimize_code(prompt)
    else:
        return "No Input"
    
def prompt_to_llm_optimize_code(prompt):
    agent = """You are a helpful and experienced software engineer who is expert in optimising the time complexity and space complexity of code.
You also provide short explantion of how you optimised it with comments in code and return optimized code."""
    
    client = OpenAI()
    response = client.ChatCompletion.create(
                
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": agent},
                         {"role": "user", "content": prompt}]
                )
    
    return response['choices'][0]['message']['content']

# ---------------------------------------------------------------------------------------------
# Fix Bugs

def fix_bugs(query, input_lang):
    if(check_if_not_null(query)):
        prompt_head = f"##### Fix bugs in the below code\n \n### Buggy {input_lang}\n{query}\n \n### Fixed {input_lang}"
        prompt = prompt_head
        print(prompt)
        return prompt_to_llm_fix_bug(prompt)
    else:
        return "No Input"
    
def prompt_to_llm_fix_bug(prompt):
    agent = """You are a helpful and experienced software engineer who is expert in fixing errors and bugs in code.
You also provide short explantion of the errors that occoured witn comments in code and return code"""
    
    client = OpenAI()
    response = client.ChatCompletion.create(
                
                model="gpt-3.5-turbo",
                messages=[{"role": "system", "content": agent},
                         {"role": "user", "content": prompt}]
                )
    
    return response['choices'][0]['message']['content']

# ---------------------------------------------------------------------------------------------
# Chat with Code

def chat_code(query, chat_query):
    if(check_if_not_null(query)):
        client = OpenAI()
        response = client.ChatCompletion.create(
            model = "gpt-3.5-turbo",
            messages=[
            {"role": "system", "content": "You are a helpful and experienced software engineer who is expert in explaining code."},
            {"role": "user", "content": f"Code context: {query}\nUser: {chat_query}"}
        ]
        )
        return response['choices'][0]['message']['content']
    else:
        return "No Input"

# ---------------------------------------------------------------------------------------------
# Global space
       
# first,second = st.columns((1,1))
api_key = os.environ.get('OPENAI_API_KEY')
OpenAI.api_key = api_key



# extension to language dictionary
ext_to_lang = {".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
    ".cpp": "C++",
    ".html": "HTML",
    ".css": "CSS",
    ".r":"R"
    }

# ---------------------------------------------------------------------------------------------
# Streamlit App

def main():

    st.title("CodeSurma")

    # ---------------------------------------------------------------------------------------------

    #st.sidebar.header("Authentication")    # Sidebar for authentication
    #github_token = st.sidebar.text_input("Enter GitHub Token")
    
    g = Github()
    #g = authenticate_github(github_token)   # Authenticate GitHub

    #st.sidebar.header("Choose GitHub Repository")
    repo_url = st.sidebar.text_input("Enter GitHub Repository URL")  # Choose GitHub repository
    
    # ---------------------------------------------------------------------------------------------
    # Repo -> files -> file -> extension -> launguage
    code_to_analyze = []

    if repo_url:
        try:
            github_owner = repo_url.split("/")[-2]
            github_repo_name = repo_url.split("/")[-1]
            repo = g.get_repo(f"{github_owner}/{github_repo_name}")
            
                              
                              
            files = list_files_in_repo(repo)
            st.success("Files listed successfully!")
            selected_file = st.sidebar.selectbox("Select a file to analyze", files, index=0)
            file_ext = selected_file.split(".")[-1] # selceted file to file extension
            code_lang = ext_to_lang.get(file_ext, "Unknown")   # from file extension to code language

            

            
            # file path : https://github.com/AJlearner46/Algorithms-Architectures-and-Models-from-scratch/blob/main/Sudoku_Slover.cpp
            selected_file_path = fetch_file_path(repo, selected_file)
            code_to_analyze = fetch_file_from_github(repo, selected_file_path)
            #st.success("File fetched successfully!")
            st.code(code_to_analyze, language="python")
            

        except Exception as e:
            st.error(f"Error extracting repository details: {str(e)}")

    else:
        st.warning("Enter valid repo url")
    

    # ---------------------------------------------------------------------------------------------
    # Main features
            
    st.header("CodeSurma's Features")

    features = st.selectbox("Choose an option", ["Review Code", "Optimize Code",  "Fix Bugs", "Chat with Code"])   
    
    # ---------------------------------------------------------------------------------------------
    # Feature 1: Review Code
        
    #code_to_review = st.text_area("Enter code to review:")
    if features == "Review Code":
        # code review logic
        review_suggestions = review_code(code_to_analyze)
        st.success("Code reviewed successfully!")
        st.write("Review suggestions:\n", review_suggestions)
    

    # ---------------------------------------------------------------------------------------------
    # Feature 2: Optimize Code

    if features == "Optimize Code":
        #  code optimization logic
        optimized_code = optimize_code(code_to_analyze, code_lang)
        st.success("Code optimized successfully!")
        st.code(optimized_code, language="python")
    
    # ---------------------------------------------------------------------------------------------
    # Feature 3: Identify Bugs
        
    #code_to_identify_bugs = st.text_area("Enter code to identify bugs:")
    if features == "Fix Bugs":
        #  bug identification logic
        identified_bugs = fix_bugs(code_to_analyze, code_lang)
        st.success("Bugs identified successfully!")
        st.write("Identified bugs:", identified_bugs)

    # ---------------------------------------------------------------------------------------------
    # Feature 4: Chat with Code
        
    if features == "Chat with Code":
         # chat with code logic
        user_query = st.text_input("Ask question abouto the code: ")
        if user_query:
            response = chat_code(code_to_analyze)
            st.write("CodeSurma: ", response)
        
# ---------------------------------------------------------------------------------------------

if __name__ == "__main__":
    main()


