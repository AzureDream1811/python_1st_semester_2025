from underthesea import word_tokenize, text_normalize
import re
import emoji


class preprocess_text(object):
    """
    Xử lý văn bản:
    - chuẩn hóa tiếng Việt
    - thay slang / viết tắt → từ đầy đủ
    - xóa emoji, mặt cười, ký hiệu
    - tokenize bằng underthesea
    """

    # Các từ viết tắt / slang → dạng chuẩn
    _replacements = {
        "laems": "lắm",
        "k dk": "không được",
        "ko": "không",
        "ko tl": "không trả lời",
        "hok": "không",
        "hàg": "hàng",
        "kp": "không phải",
        "khong xl": "không xin lỗi",
        "khong": "không",
        "k": "không",
        "thik": "thích",
        "xog": "xong",
        "e bé": "em bé",
        "tks": "cảm ơn",
        "thanks": "cảm ơn",
        "sp": "sản phẩm",
        "sx": "sản xuất",
        "meosddc": "méo được",
        "cg": "cũng",
        "cgiac": "cảm giác",
        "siu": "siêu",
        "dt": "điện thoại",
        "đc": "được",
        "trc": "trước",
        "lhe": "liên hệ",
        "nt": "nhắn tin",
        "ntn": "như thế nào",
        "thấy ntn": "thấy như thế này",
        "k bt ntn": "không biết như thế nào",
        "shopkhá": "cửa hàng khá",
        "phẩmkémvề ": "phẩm kém về ",
        "tl": "trả lời",
        "lắmmàu": "lắm màu",
        "êmda": "êm da",
        "thj": "thì",
    }

    # Các pattern mặt cười / symbol muốn xóa
    _remove_tokens = [
        "♡ ♡ ♡",
        "❤",
        r"\=\)\)\)",
        r"\=\)\)",
        r"\=\)",
        r"\:\)\)\)",
        r"\:\)\)",
        r"\:\)",
        r"\:\(",
        r"\:\(\(",
    ]

    def _get_replacements_pattern(self):
        """
        Build các regex pattern dùng để:
        - thay thế slang → từ chuẩn
        - xóa các chuỗi cảm xúc (_remove_tokens)
        """
        replacements = {}

        for k, v in preprocess_text._replacements.items():
            if k != "k bt ntn":
                replacements[f" {k} "] = f" {v} "
            else:
                replacements[f"{k} "] = f"{v} "

        replace_pattern = re.compile("|".join(replacements.keys()))
        remove_pattern = re.compile("|".join(preprocess_text._remove_tokens))

        return replace_pattern, replacements, remove_pattern

    def __init__(self):
        (
            self._replacements_pattern,  # regex thay slang
            self._replacements,  # dict map slang → từ chuẩn
            self._remove_pattern,  # regex xóa mặt cười / symbol
        ) = self._get_replacements_pattern()

    def forward(self, text: str) -> str:
        if not isinstance(text, str):
            return ""

        # 1. lower all string
        text = text.lower()

        # 2. normalize
        text = text_normalize(text)

        # 3. remove emoji
        text = emoji.replace_emoji(text, replace="")

        # 4. remove special strings
        text = self._remove_pattern.sub("", text)

        # 5. replace slang
        text = self._replacements_pattern.sub(
            lambda match: self._replacements[match.group()],
            text,
        )

        # 6. remove any ',' left after cleaning words
        text = re.sub(r",\s*", "", text)

        # 7. tokenize via underthesea
        result = word_tokenize(text, format="text")

        if isinstance(result, list):
            text = " ".join(map(str, result))
        else:
            text = str(result)

        return text


if __name__ == "__main__":
    p = preprocess_text()
    s = "Shop ơi sp này siu đẹp ko :))) tks ❤"
    print(p.forward(s))
