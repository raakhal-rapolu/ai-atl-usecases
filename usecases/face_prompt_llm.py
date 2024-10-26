import json
import requests


def generate_message_with_llm(image_path: str, context: dict) -> dict:
    """
    Generate a message using the LLM API based on the provided context and image.

    :param image_path: Path to the image file.
    :param context: Dictionary containing context about the person.
    :return: Response from the LLM API.
    """
    prompt_template = '''
System Instruction: You are assisting a dementia patient in identifying and recalling people they see. Given context about the person in front of them, provide a friendly, comforting message to help the patient recognize who it is.

Context:
{context}

Few-shot Examples:

1. Context: {{"name": "John", "relation": "son", "personal_information": "John visits you often and enjoys talking with you about gardening."}}
   Message: "This is John, your son, sitting with you. He visits you often and loves chatting about gardening with you."

2. Context: {{"name": "Mary", "relation": "daughter", "personal_information": "Mary loves baking with you on weekends and makes your favorite chocolate cake."}}
   Message: "Here with you is Mary, your daughter. She enjoys baking with you, especially your favorite chocolate cake."

3. Context: {{"name": "Michael", "relation": "friend", "personal_information": "You and Michael go way back. You both enjoy playing cards together."}}
   Message: "This is Michael, your friend from many years ago. You both share fond memories of playing cards together."

New Instance:
Given the context: {context}
Provide a comforting message that reminds the patient of the person's name, relationship, and something familiar about them.
'''
    # Inject the context into the prompt
    context_str = json.dumps(context)
    prompt = prompt_template.format(context=context_str)

    # LLM API endpoint
    llm_api_url = 'https://recallme-flask-service-1031256824093.us-central1.run.app/recall-svc/api/v1/reinforce_memory/gemini-image-inference'

    # Send the request to the LLM API with the image and prompt
    with open(image_path, 'rb') as img_file:
        files = {'file': img_file}
        data = {'input_text': prompt}
        response = requests.post(llm_api_url, files=files, data=data)

    if response.status_code == 200:
        return response.json()
    else:
        # Raise an exception to be handled by the calling function
        raise Exception(f"Failed to call LLM API: {response.status_code}, {response.text}")
