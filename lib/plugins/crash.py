"""TEST ENVIRONMENT ONLY: a platform that always crashes while posting."""


class crash_client:
    def __init__(self, **kwargs):
        pass

    def format_content(self, content, mentions, hashtags, images, **kwargs):
        return content, content, ""

    def create_post(self, content, **kwargs):
        raise RuntimeError("simulated crash in the crash-test platform")
