# import os
# import openai
# openai.organization = "org-qY05qu67rxmfKaW0sKWJHyyR"
# openai.api_key = "org-qY05qu67rxmfKaW0sKWJHyyR"
# openai.Model.list()

import openai

# Set your OpenAI API key
api_key = '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'

# Initialize the OpenAI API client
openai.api_key = api_key

# Provide the PDF-extracted text as context
context = """
Common Machine Learning Algorithms for Beginners
Read this list of basic machine learning algorithms for beginners to get started with machine learning and learn about the popular ones with examples.
Last Updated: 15 Jul 2023
"""
# Ask a question to GPT-3
question = "What is the main topic of the document?"
response = openai.Completion.create(
    engine="text-davinci-002",
    prompt=f"Context: {context}\nQuestion: {question}\nAnswer:",
    max_tokens=50  # Adjust as needed
)
# Process and display the response
answer = response.choices[0].text.strip()
print(answer)
