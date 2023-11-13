import base64
import os, sys
import requests
import argparse

def parse_img_path() -> str:
    parser = argparse.ArgumentParser(
        prog="SnapLabel",
        description="Renames screenshots with a sensible title.",
        epilog="And @sama said, Let their be light; and their was gpt4-vision"
    )

    parser.add_argument("image")
    args = parser.parse_args()

    if os.path.exists(args.image):
        return args.image

    raise ValueError("Could not find image file supplied.")

def encode_image(image_path: str):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def generate_file_name(base64_image, OPENAI_API_KEY):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    
    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
          {
            "role": "user",
            "content": [
              {
                "type": "text",
                "text": """
                    You are a GPT model with vision capabilities. I am developing an app
                    to rename screenshots with a much more meaningful name. I will
                    send you the screenshot clicked by the user and you will reply with a short name that
                    makes sense for the image. Reply only with the name for the image and no other text.
                """
              },
              {
                "type": "image_url",
                "image_url": {
                  "url": f"data:image/jpeg;base64,{base64_image}",
                  "detail": "low"
                }
              }
            ]
          }
        ],
        "max_tokens": 10
    }
    
    print("Generating file name...")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    res = response.json()
    
    suggested_file_name = res["choices"][0]["message"]["content"]
    print("Suggested file name:", suggested_file_name)
    
    response.close
    return str(suggested_file_name);


if __name__ == "__main__":
    OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

    original_fullpath = ""

    try:
        original_fullpath = parse_img_path()
    except ValueError as err:
        print(err)
        sys.exit(1)

    b64_img = encode_image(original_fullpath)
    suggested_file_name = generate_file_name(b64_img, OPENAI_API_KEY)

    new_path = os.path.join(os.path.dirname(original_fullpath), suggested_file_name + os.path.splitext(original_fullpath)[1])
    while os.path.exists(new_path):
        print("Suggested file name already exist, regenerating...")
        suggested_file_name = generate_file_name(b64_img, OPENAI_API_KEY)
        new_path = os.path.join(os.path.dirname(original_fullpath), suggested_file_name + os.path.splitext(original_fullpath)[1])

    os.rename(original_fullpath, new_path)
    print("Saved file as ", os.path.basename(new_path), " in ", os.path.dirname(new_path) if len(os.path.dirname(new_path)) > 0 else "./")
