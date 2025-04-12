class HTML:
    @staticmethod
    def b(text): return f"<b>{text}</b>"

    @staticmethod
    def i(text): return f"<i>{text}</i>"

    @staticmethod
    def u(text): return f"<u>{text}</u>"

    @staticmethod
    def code(text): return f"<code>{text}</code>"

    @staticmethod
    def pre(text): return f"<pre>{text}</pre>"

    @staticmethod
    def a(text, url): return f'<a href="{url}">{text}</a>'
