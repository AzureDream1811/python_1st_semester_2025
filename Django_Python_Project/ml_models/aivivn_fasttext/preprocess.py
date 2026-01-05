import re
import string
import os
import sys
import django
from django.conf import settings
from underthesea import word_tokenize, text_normalize
import emoji
from  emot import emot

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Django_Python_Project.config.settings")
django.setup()

class PreprocessText():
    """
    prepared to merge from preprocess
    """

    # Các từ viết tắt / slang → dạng chuẩn
    _replacements = {
        "laems": "lắm",
        "k dk": "không được",
        "ko": "không",
        "k": "không",
        "hok": "không",
        "khong": "không",
        "ko tl": "không trả lời",
        "khong xl": "không xin lỗi",
        "kp": "không phải",
        "hàg": "hàng",
        "thik": "thích",
        "xog": "xong",
        "e bé": "em bé",
        "tks": "cảm ơn",
        "thanks": "cảm ơn",
        "thank": "cảm ơn",
        "sp": "sản phẩm",
        "sx": "sản xuất",
        "meosddc": "méo được",
        "cg": "cũng",
        "cgiac": "cảm giác",
        "siu": "siêu",
        "dt": "điện thoại",
        "đc": "được",
        "dc": "được",
        "trc": "trước",
        "lhe": "liên hệ",
        "nt": "nhắn tin",
        "ntn": "như thế nào",
        "tl": "trả lời",
        "thj": "thì",
        "shopkhá": "cửa hàng khá",
        "phẩmkémvề": "phẩm kém về",
        "lắmmàu": "lắm màu",
        "êmda": "êm da",
        # Có thể thêm các từ khác
        "ok": "được",
        "oke": "được",
        "okê": "được",
        "vs": "với",
        "m": "mình",
        "mk": "mình",
        "t": "tôi",
        "r": "rồi",
        "đ": "đã",
        "cx": "cũng",
        "j": "gì",
        "bik": "biết",
        "bt": "biết",
        "nc": "nói chuyện",
        "sd": "sử dụng",
    }

    def _replace_slang(self, match):
        """
        Helper function để thay thế slang
        """
        matched_text = match.group().lower() # Lấy ra chuỗi được khớp

        # Tìm pattern nào match và trả về value tương ứng
        for pattern_key, replacement_value in self._replacements.items():
            # So khớp pattern với text
            if re.fullmatch(pattern_key, matched_text, re.IGNORECASE):
                return replacement_value

        return matched_text  # Nếu không tìm thấy thì giữ nguyên

    def _get_replacements_pattern(self):
        """
        Build các regex pattern dùng để:
        - thay thế slang → từ chuẩn
        """
        replacements = {}

        for k, v in PreprocessText._replacements.items():
            pattern_key = r'\b' + re.escape(k) + r'\b'
            replacements[pattern_key] = v

        replace_pattern = re.compile("|".join(replacements.keys()))
        """
        replace_pattern => Những pattern sẽ bị thay đổi
        replacements => Key có giá trị như replace_pattern, value là giá trị sẽ chuyển sang
        """
        return replace_pattern, replacements

    def __init__(self):
        (
            self._replacements_pattern,
            self._replacements
        ) = self._get_replacements_pattern()
        # Stopwords
        with open(settings.VIETNAMESE_STOPWORDS_FILE, "r", encoding="utf-8") as f:
            self._stopwords = set(f.read().splitlines())

    def forward(self, text: str) -> str:
        """
        Clean a text by:
        0. Lowering all string
        1. Remove url
        2. Normalizing
        3. Removing emoji
        4. Removing special strings
        5. Replacing slang
        6. Removing punctuation
        7. Tokenizing via underthesea
        8. Remove stopwords
        :param text: The text to clean
        :type text: str
        :return: The cleaned text
        :rtype: str
        """
        if not isinstance(text, str):
            return ""

        # 0. lower all string
        text = text.lower()

        # 1. remove url
        patternUrl = r'(http|https)?://\S+|www\.\S+'
        text = re.sub(patternUrl, ' ', text)

        # 2. normalize
        text = text_normalize(text)

        # 3. remove emoji (Xóa các emoji)
        text = emoji.replace_emoji(text, replace="")

        # 4. remove special strings (Xóa kí tự đặc biệt)
        try:
            emoticons = emot.emoticons(text)
            # Lấy ra các biểu tượng cảm xúc dạng text sau đó replace text chứa nó sang " "
            for emo in emoticons['value']:
                text = text.replace(emo, " ")
        except:
            pass

        # 5. replace slang (Thay các từ viết tắt sang từ chuẩn)
        #tìm các đoạn trong text khớp với các phần tử trong replacements_pattern, mỗi lần thấy thì gọi
        #hàm _replace_slang để tìm value thay thế tương ứng
        text = self._replacements_pattern.sub(self._replace_slang, text)

        # 6. remove any punctuation (Đảm bảo các slang có các dấu câu có thể được lọc trước khi xóa các dấu câu còn lại)
        # !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
        patternPunctuation = "[" + re.escape(string.punctuation) + "]"
        text = re.sub(patternPunctuation, "", text)

        # 7. tokenize via underthesea
        tokens = word_tokenize(text)

        # 8. remove stopwords (Những từ không có nhiều ý nghĩa trong câu)
        result = [token for token in tokens if token not in self._stopwords]

        if isinstance(result, list):
            text = " ".join(map(str, result))
        else:
            text = str(result)

        return text


if __name__ == "__main__":
    p = PreprocessText()
    s = "thik hoà thik so@@ ^-^Shop ơi^^ ,.sp này siu đẹp ko :)))))))))))tks ❤ \nAhihi😴\n Link: http://129 ://hac www.sdcd, xấu ơi là xấu nuôn"
    print(p.forward(s))
