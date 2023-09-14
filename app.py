from flask import Flask, jsonify, request,send_file,send_from_directory
from pymongo import MongoClient
from bson import ObjectId
import uuid
import os
import PyPDF2

app = Flask(__name__)
# Define the UPLOAD_FOLDER configuration variable using os.path
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')

# Ensure the 'UPLOAD_FOLDER' directory exists, create it if necessary
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
client = MongoClient("mongodb+srv://userxyz:userxyz@cluster0.5be8y.mongodb.net/?retryWrites=true&w=majority")  # Update with your MongoDB URI
db = client["studyhacks"]
collection = db["chats"]
documents = db["documents"]
@app.route('/')
def index():
    return "<h1> hello world</h1>"

@app.route('/pdfs', methods=['POST'])
def upload_file():
    
    # Check if the 'file' key is in the request
    if 'file' not in request.files:
        return "No file part", 400
    
    file = request.files['file']
    
    # Check if the file is empty
    if file.filename == '':
        return "No selected file", 400
    
    # Save the file to the 'UPLOAD_FOLDER'
    unique_id = uuid.uuid4()
    pdf_loc=os.path.join(app.config['UPLOAD_FOLDER'],  str(unique_id)+".pdf")
    file.save(pdf_loc)
    # extract data from pdf file
    extracted_text = extract_text_from_pdf(pdf_loc)
    data = {}
    data['user_id']=request.form.get('user_id')
    data["extracted_text"]=extracted_text
    data["pdf_name"]=str(unique_id)+".pdf"
    document = documents.insert_one(data)
    print(request)
    return jsonify({"message": "Document processed successfully"}),201

@app.route('/pdfs', methods=['GET'])
def get_files():
    documents_list = list(documents.find())
    
    # Convert ObjectId fields to strings and create a list of file URLs
    files_list = []
    for document in documents_list:
        document["_id"] = str(document["_id"])
        file_url = f"/uplods/{document['pdf_name']}"  # Create a URL for each file
        files_list.append({"_id": document["_id"], "pdf_name": document["pdf_name"], "file_url": file_url})
    
    return jsonify(files_list), 200

@app.route('/pdfs/download/<file_id>', methods=['GET'])
def download_file(file_id):
    document = documents.find_one({"_id": ObjectId(file_id)})
    
    if document:
        # Get the filename from the document
        pdf_name = document["pdf_name"]
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_name)
        # Use the send_file function to send the file
        return send_file(file_path)
    else:
        return jsonify({"message": "File not found"}), 404
    
# Create a new chat
@app.route("/chats", methods=["POST"])
def create_chat():
    print(request.content_type)
    data = request.get_json()
    chat_id = collection.insert_one(data).inserted_id
    return jsonify({"message": "Chat created successfully", "chat_id": str(chat_id)}), 201


@app.route("/chats", methods=["GET"])
def get_chats():
    chats = list(collection.find())
    
    # Convert ObjectId fields to strings
    for chat in chats:
        chat["_id"] = str(chat["_id"])
    
    return jsonify(chats), 200


@app.route("/chats/<string:chat_id>", methods=["GET"])
def get_chat(chat_id):
    chat = collection.find_one({"_id": ObjectId(chat_id)})
    if chat:
        # Convert ObjectId to string
        chat["_id"] = str(chat["_id"])
        return jsonify({"chat": chat}), 200
    else:
        return jsonify({"message": "Chat not found"}), 404



# Update a chat by ID
@app.route("/chats/<string:chat_id>", methods=["PUT"])
def update_chat(chat_id):
    data = request.get_json()
    result = collection.update_one({"_id": ObjectId(chat_id)}, {"$set": data})
    if result.modified_count == 1:
        return jsonify({"message": "Chat updated successfully"}), 200
    else:
        return jsonify({"message": "Chat not found"}), 404

# Delete a chat by ID
@app.route("/chats/<string:chat_id>", methods=["DELETE"])
def delete_chat(chat_id):
    result = collection.delete_one({"_id": ObjectId(chat_id)})
    if result.deleted_count == 1:
        return jsonify({"message": "Chat deleted successfully"}), 200
    else:
        return jsonify({"message": "Chat not found"}), 404
    
    
def extract_text_from_pdf(pdf_file_path):
    try:
        text = ''
        # Open the PDF file
        with open(pdf_file_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            pages=pdf_reader.pages
            # Initialize an empty string to store the extracted text
            # text = ''
            
            # Iterate through each page and extract text
            for page_number in range(len(pages)):
                page = pdf_reader.pages[page_number]
                text += page.extract_text()
            return text
        
    except Exception as e:
        return text
if __name__ == "__main__":
    app.run(debug=True)
