# این کد، یک پروژه کامل است که شامل مراحل کراولینگ وب‌سایت، ذخیره‌سازی داده‌ها به صورت JSONL، و استفاده از OpenAI API برای Fine-Tuning مدل و ایجاد یک چت‌بات است.


import streamlit as st
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import openai
import time

# Initialize OpenAI API key ---------sadeghparsa
openai.api_key = 'your-api-key'

# Function to crawl the website and extract text data
def crawl_website(url):
    visited = set()
    to_visit = [url]
    data = []

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)

        response = requests.get(current_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        page_text = soup.get_text(separator=" ", strip=True)
        data.append({"url": current_url, "text": page_text})

        for link in soup.find_all('a', href=True):
            full_url = urljoin(url, link['href'])
            if full_url.startswith(url):
                to_visit.append(full_url)

    return data

# Function to save the crawled data to a JSONL file
def save_to_jsonl(data, filename):
    with open(filename, 'w') as outfile:
        for entry in data:
            json.dump(entry, outfile)
            outfile.write('\n')

# Function to fine-tune the model with the JSONL file
def fine_tune_model(jsonl_file):
    response = openai.File.create(file=open(jsonl_file, 'rb'), purpose='fine-tune')
    file_id = response['id']

    fine_tune_response = openai.FineTune.create(
        training_file=file_id,
        model="davinci"
    )
    return fine_tune_response['id']

# Function to ask questions to the fine-tuned model
def ask_question(model_id, question):
    response = openai.Completion.create(
        model=model_id,
        prompt=question,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Streamlit interface
st.title("Web Crawler and Chatbot")

url = st.text_input("Enter the website URL you want to crawl:")

if st.button("Start Crawling"):
    st.write("Crawling started for URL:", url)
    data = crawl_website(url)
    save_to_jsonl(data, "output.jsonl")
    st.write("Crawling completed. Fine-tuning the model...")

    model_id = fine_tune_model("output.jsonl")
    st.write(f"Fine-tuning completed. Model ID: {model_id}")

    # Wait for fine-tuning to complete
    st.write("Waiting for fine-tuning to complete. This may take some time...")
    while True:
        fine_tune_status = openai.FineTune.retrieve(id=model_id)
        status = fine_tune_status['status']
        if status == 'succeeded':
            st.write("Fine-tuning succeeded.")
            break
        elif status == 'failed':
            st.write("Fine-tuning failed.")
            break
        time.sleep(10)

    question = st.text_input("Ask a question:")
    if st.button("Ask"):
        answer = ask_question(model_id, question)
        st.write(f"Answer: {answer}")