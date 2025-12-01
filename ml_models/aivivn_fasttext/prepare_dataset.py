import pandas as pd

from .preprocess import PreprocessText
from .config import DATASET_DIR, FASTESTTEXT_DATA_DIR


class FastTextDatasetBuilder:
    """
    Read CSV, process text, build file .txt for FastText
    """

    def __init__(self, text_col: str = "comment", label_col: str = "label"):
        self.text_col = text_col
        self.label_col = label_col
        self._preprocess = PreprocessText()

    def _load_CSV(self, filename: str) -> pd.DataFrame:
        """
        Load a CSV file from DATASET_DIR and return the DataFrame.

        Parameters
        ----------
        filename : str
            The name of the CSV file to load.

        Returns
        -------
        pd.DataFrame
            The loaded DataFrame.

        Raises
        ------
        FileNotFoundError
            If the file is not found.
        """
        path = DATASET_DIR / filename

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        df = pd.read_csv(path)

        df = df[[self.text_col, self.label_col]].dropna()
        return df

    def _preprocess_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess a DataFrame by applying the forward method of the preprocess_text instance to the text column.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame to preprocess

        Returns
        -------
        pd.DataFrame
            The preprocessed DataFrame
        """
        df[self.text_col] = df[self.text_col].astype(str).map(self._preprocess.forward)

        return df

    @staticmethod
    def _to_fasttext_line(label, text) -> str:
        return f"__label__{label} {text}"

    def _build_ft_lines(self, df: pd.DataFrame) -> pd.Series:
        """
        Build a pandas Series of lines in the format expected by fastText.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame containing the text and label columns

        Returns
        -------
        pd.Series
            A pandas Series of lines in the format expected by fastText
        """
        return pd.Series(
            [
                self._to_fasttext_line(label, text)
                for label, text in zip(df[self.label_col], df[self.text_col])
            ]
        )

    def _build_train_test_txt(
        self,
        train_csv: str = "train.csv",
        test_csv: str = "test.csv",
        train_text_name: str = "train.txt",
        test_text_name: str = "test.txt",
    ):
        """
        Build the FastText data from the given CSV files.

        Parameters
        ----------
        train_csv : str, optional
            The name of the train CSV file. Defaults to "train.csv".
        test_csv : str, optional
            The name of the test CSV file. Defaults to "test.csv".
        train_text_name : str, optional
            The name of the train text file. Defaults to "train.txt".
        test_text_name : str, optional
            The name of the test text file. Defaults to "test.txt".

        Returns
        -------
        None
        """

        train_df = self._load_CSV(train_csv)
        test_df = self._load_CSV(test_csv)

        train_df = self._preprocess_df(train_df)
        test_df = self._preprocess_df(test_df)

        train_lines = self._build_ft_lines(train_df)
        test_lines = self._build_ft_lines(test_df)

        train_lines.to_csv(FASTESTTEXT_DATA_DIR / train_text_name, index=False, header= False)
        test_lines.to_csv(FASTESTTEXT_DATA_DIR / test_text_name, index=False, header= False)

        print("Done building FastText data")

if __name__ == "__main__":
    builder = FastTextDatasetBuilder(
        text_col="comment",  # sửa theo cột thực của bạn
        label_col="label",   # sửa theo cột thực của bạn
    )
    builder._build_train_test_txt(
        train_csv="train.csv",   # nằm trong DATASET_DIR
        test_csv="test.csv",
    )