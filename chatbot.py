import pandas as pd
from flask import Flask, request, jsonify, render_template, send_from_directory
import openai
import os

# Initialize Flask application
app = Flask(__name__, static_folder='static', template_folder='templates')

# Configure OpenAI API key from environment variable
openai.api_key = os.getenv('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')

# Initialize global data
data = pd.DataFrame()

def load_data_from_csv(file_path):
    global data
    data = pd.read_csv(file_path)

def search_data(query):
    column_name = 'keywords' 
    if column_name not in data.columns:
        return f"Error: '{column_name}' does not exist in the CSV file."

    result = data[data[column_name].str.contains(query, case=False, na=False)]
    return result

def generate_openai_response(prompt):
    try:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=100,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error calling OpenAI API: {e}"

def chatbot_response(user_input):
    search_result = search_data(user_input)
    
    if isinstance(search_result, str):
        return search_result
    
    if not search_result.empty:
        return search_result.to_dict(orient='records')
    else:
        return generate_openai_response(user_input)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'response': "Please provide a message."})
    
    response = chatbot_response(user_input)
    return jsonify({'response': response})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'response': "No file part."})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'response': "No selected file."})
    
    if file and file.filename.endswith('.csv'):
        file_path = os.path.join('uploads', file.filename)
        if not os.path.exists('uploads'):
            os.makedirs('uploads')
        file.save(file_path)
        load_data_from_csv(file_path)
        return jsonify({'response': f"File '{file.filename}' uploaded and data loaded."})
    
    return jsonify({'response': "Invalid file format. Please upload a CSV file."})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)
