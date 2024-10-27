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
    llm_api_url = 'https://recallme-flask-service-1031256824093.us-central1.run.app/recall-svc/api/v1/reinforce_memory/gemini-media-inference'

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


def assist_dementia_patient(image_path: str, context: dict) -> dict:
    """
    Generate assistance based on non-face image frames for a dementia patient,
    providing context or reminders based on the scene.

    :param image_path: Path to the image file.
    :param context: Dictionary containing context about the scene, e.g., detected objects or situational cues.
    :return: Response from the LLM API.
    """
    prompt_template = '''
System Instruction: You are assisting a dementia patient by providing reminders or helping them navigate their environment based on non-face image frames.

Context:
{context}

Few-shot Examples:

1. Context: {{"objects": ["keys", "door"], "activity": "leaving house"}}
   Message: "Hey, it looks like you are heading out. Don't forget to take your keys by the door."

2. Context: {{"objects": ["medication"], "activity": "morning routine"}}
   Message: "Good morning! It's time for your medication. Please take the pills from the table."

3. Context: {{"objects": ["grocery bag", "kitchen"], "activity": "after shopping"}}
   Message: "You just got back from shopping. Remember to put the groceries in the fridge in the kitchen."

4. Context: {{"objects": ["television remote", "sofa"], "activity": "relaxing"}}
   Message: "If you're looking to watch some TV, your remote is right there on the sofa."

5. Context: {{"objects": ["phone"], "activity": "receiving a call"}}
   Message: "Your phone is ringing. It's on the coffee table if you want to answer it."

6. Context: {{"objects": ["hat", "outdoor"], "activity": "sunny day"}}
   Message: "It's quite sunny outside today. Consider wearing your hat which is hanging by the door."

7. Context: {{"objects": ["book"], "activity": "reading"}}
   Message: "Feeling like reading? Your book is waiting for you on the nightstand."

8. Context: {{"objects": ["dog leash"], "activity": "walking the dog"}}
   Message: "Are you going out to walk the dog? The leash is on the hook next to the door."

9. Context: {{"objects": ["umbrella"], "activity": "rainy day"}}
   Message: "It's raining outside. Your umbrella is near the front door, don't forget it!"

10. Context: {{"objects": ["wallet", "table"], "activity": "planning to go out"}}
   Message: "Before you go out, remember to take your wallet from the table."

New Instance:
Given the context: {context}
Provide a useful reminder or assistance message that helps the patient navigate their immediate environment.
'''
    # Inject the context into the prompt
    context_str = json.dumps(context)
    prompt = prompt_template.format(context=context_str)

    # LLM API endpoint
    llm_api_url = 'https://recallme-flask-service-1031256824093.us-central1.run.app/recall-svc/api/v1/reinforce_memory/gemini-media-inference'

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
