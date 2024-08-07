import os
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import time
import re

app = FastAPI()

def clean_json(json_data):
    newline_pattern = re.compile(r"(\\n)+")
    
    def replace_newlines(match):
        
        newline_count = match.group(0).count('\\n')
        return '\n' * newline_count
    cleaned_text = newline_pattern.sub(replace_newlines, json_data['text'])
    json_data['text'] = cleaned_text
    
    return json_data

@app.post("/ocr/")
async def ocr_pdf(file: UploadFile = File(...)):
    start_time = time.time()  # Start timing
    try:
        contents = await file.read()
        images = convert_from_bytes(contents)
        
        ocr_text = []
        for image in images:
            text = pytesseract.image_to_string(image)
            ocr_text.append(text)
    
        full_text = "\n\n".join(ocr_text)
        
        print("OCR Output:\n", full_text)
        
        with open("output.txt", "w") as output_file:
            output_file.write(full_text)
        
        response_data = {"text": full_text}
        
        modified_response_data = clean_json(response_data)
        
        end_time = time.time()  # End timing
        ocr_time = end_time - start_time
        
        modified_response_data["ocr_time_seconds"] = ocr_time
        print(f"OCR processing time: {ocr_time} seconds")
        
        return JSONResponse(content=modified_response_data)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
