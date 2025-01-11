import io
import json
import aiohttp
from dotenv import dotenv_values
from os import listdir, environ
from PIL import Image


check_local = ".env.local" in listdir()

config = {
    **environ,
    **dotenv_values(".env" + ["", ".local"][check_local]),
}


async def send_post_request(url, file_bytes, metadata):
    try:
        img = Image.open(io.BytesIO(file_bytes))
        max_size = 680
        W, H = img.size
        scale = min(max_size / W, max_size / H)

        new_width = int(W * scale)
        new_height = int(H * scale)
        img = img.resize((new_width, new_height), Image.LANCZOS)

        file_bytes = io.BytesIO()
        img.save(file_bytes, "png")
        file_bytes = file_bytes.getvalue()
        headers = {
            "accept": "application/json",
        }

        extras = {
            "sam_prompt": [

                {
                    "type": "point",
                    "data": [W >> 1, H >> 1],
                    "label": 1
                },


            ]
        }
        query_parameters = {
            "extras": json.dumps(extras)
        }

        form = aiohttp.FormData()
        form.add_field('file', file_bytes, filename=metadata["filename"],
                       content_type="image/png")
        form.add_field('model', config.get("MODEL"))

        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=form, params=query_parameters, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Request failed with status: {response.status}")
                    return None
    except Exception as e:
        print(f"Error in send_post_request: {e}")
        return None


async def remove_bg(file_bytes, metadata):
    try:
        url = "http://" + config.get("REM_HOST") + f":7001/api/remove"

        img = await send_post_request(url, file_bytes, metadata)

        if img:
            return img
        else:
            raise Exception("Image processing failed")
    except Exception as e:
        print(f"Error in remove_bg: {e}")
        return b""
