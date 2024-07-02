import requests
import re
import textwrap


class linkedin_client:
    def __init__(self, **kwargs):
        self.api_base_url = kwargs.get("base_url", "https://matrix.org")
        self.organization_urn = f"urn:li:organization:{kwargs.get('org_id')}"
        self.headers = {
            "Authorization": f"Bearer {kwargs.get('access_token')}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202406",
        }
        self.max_content_length = kwargs.get("max_content_length", 3000)

    def content_in_chunks(self, content, max_chunk_length):
        paragraphs = content.split("\n\n\n")
        for p in paragraphs:
            for chunk in textwrap.wrap(
                p.strip("\n"), max_chunk_length, replace_whitespace=False
            ):
                yield chunk

    def wrap_text_with_index(self, content):
        if len(content) <= self.max_content_length:
            return [content]
        urls = re.findall(r"https?://\S+", content)
        placeholder_content = re.sub(
            r"https?://\S+", lambda m: "~" * len(m.group()), content
        )
        wrapped_lines = list(
            self.content_in_chunks(placeholder_content, self.max_content_length - 8)
        )
        final_lines = []
        url_index = 0
        for i, line in enumerate(wrapped_lines, 1):
            while "~~~~~~~~~~" in line and url_index < len(urls):
                placeholder = "~" * len(urls[url_index])
                line = line.replace(placeholder, urls[url_index], 1)
                url_index += 1
            final_lines.append(f"{line} ({i}/{len(wrapped_lines)})")
        return final_lines

    def format_content(self, content, mentions, hashtags, images, **kwargs):
        mentions = " ".join([f"@{v}" for v in mentions])
        hashtags = " ".join([f"#{v}" for v in hashtags])
        if len(images) > 4:
            warnings = f"A maximum of four images, not {len(images)}, can be included in a single bluesky post."
            images = images[:4]
        else:
            warnings = ""

        content += "\n"
        if mentions:
            content = f"{content}\n{mentions}"
        if hashtags:
            content = f"{content}\n{hashtags}"
        chunks = self.wrap_text_with_index(content.strip("\n"))

        formatted_content = {
            "body": "\n\n".join(chunks),
            "images": images,
            "chunks": chunks,
        }
        preview = formatted_content["body"]
        images_preview = "\n".join(
            [f'![{image.get("alt_text", "")}]({image["url"]})' for image in images]
        )
        preview += "\n\n" + images_preview
        return formatted_content, preview, warnings

    def linkedin_post(self, content):
        data = {
            "author": self.organization_urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        response = requests.post(
            f"{self.api_base_url}/posts", headers=self.headers, json=data
        )
        if response.status_code == 201:
            return True, response.headers.get("x-restli-id")
        else:
            return False, response.text

    def linkedin_post_with_images(self, content, images):
        # upload images
        data = {
            "author": self.organization_urn,
            "commentary": content,
            "visibility": "PUBLIC",
            "distribution": {
                "feedDistribution": "MAIN_FEED",
                "targetEntities": [],
                "thirdPartyDistributionChannels": [],
            },
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
            "media": [
                {
                    "status": "READY",
                    "media": images,
                    "title": "image",
                    "description": "image",
                    "mediaType": "IMAGE",
                }
            ],
        }
        response = requests.post(
            f"{self.api_base_url}/posts", headers=self.headers, json=data
        )
        if response.status_code == 201:
            return True, response.headers.get("x-restli-id")
        else:
            return False, response.text

    def create_post(self, content, **kwargs):
        for text in content["chunks"]:
            status, message = self.linkedin_post(text)
            if not status:
                return status, None
            link = f"https://www.linkedin.com/feed/update/{message}"
            return status, link
