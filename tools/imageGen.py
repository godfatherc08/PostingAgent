import os
import dotenv
import requests
import asyncio
import aiohttp
from langchain.tools import tool


dotenv.load_dotenv()
API_KEY = os.getenv("LEONARDO_AI_API_KEY")

HEADERS = {
    "accept": "application/json",
    "authorization": f'Bearer {API_KEY}',
    "content-type": "application/json"
}

def create_image(prompt: str):
    url = "https://cloud.leonardo.ai/api/rest/v1/generations"
    payload = {
        "alchemy": False,
        "height": 1080,
        "modelId": "7b592283-e8a7-4c5a-9ba6-d18c31f258b9",
        "contrast": 3.5,
        "num_images": 1,
        "styleUUID": "111dc692-d470-4eec-b791-3475abac4c46",
        "prompt": prompt,
        "width": 1920,
        "ultra": False
    }

    response = requests.post(url, json=payload, headers=HEADERS)
    data = response.json()
    print(data)
    generation_id = data["sdGenerationJob"]["generationId"]
    return generation_id


async def wait_for_image(generation_id, interval=2.0, timeout=60.0):
    url = f"https://cloud.leonardo.ai/api/rest/v1/generations/{generation_id}"

    start_time = asyncio.get_event_loop().time()
    async with aiohttp.ClientSession(headers=HEADERS) as session:
        while True:
            async with session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()

                    gen_obj = data["generations_by_pk"]
                    gen_images = gen_obj.get("generated_images", [])

                    if gen_images:
                        first_image = gen_images[0]
                        image_url = first_image.get("url")
                        print("Generated image URL:", image_url)
                        return image_url

                        # Optional: check variation URLs
                        variations = first_image.get("generated_image_variation_generics", [])
                        for v in variations:
                            print("Variation URL:", v.get("url"))

            # Timeout check
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise TimeoutError("Timed out waiting for image generation")

            await asyncio.sleep(interval)

@tool
async def imageGen(prompt: str):
    """
    Generating Images from summarized prompt

    Args:
        prompt : Summarized text from summarize-one_line in llmsummary.py
    Returns:
        imageURL
    """
    print("Creating image...")
    gen_id = create_image(prompt)

    print("Waiting for image to be ready...")
    image_url = await wait_for_image(gen_id)
    print("Image URL:", image_url)
    return image_url


