from faker import Faker
from random import randint, choice


def prepare_data(
    file_name_pattern, key_words_file_name, files_number, lines_number_max
):
    """
    Generate fake data and write it to files based on the given parameters.

    Parameters:
        file_name_pattern (str): The pattern for generating file names.
        key_words_file_name (str): The name of the file to store the generated key words.
        files_number (int): The number of files to generate.
        lines_number_max (int): The maximum number of lines in each file.

    Returns:
        None
    """
    fake = Faker()
    kwords = []
    for i in range(files_number):
        data = [
            fake.text()
            for _ in range(randint(lines_number_max // 10, lines_number_max))
        ]
        with open(file_name_pattern.format(i), "w") as f:
            f.write("\n".join(data))

        for _ in range(randint(1, 10)):
            k_words = choice(data).split()
            while True:
                word = choice(k_words)
                if len(word) > 3:
                    kwords.append(word)
                    break

    with open(key_words_file_name, "w") as kwords_f:
        kwords_f.write(
            "\n".join((set(kwords))).replace(".", "").replace(",", "").lower()
        )


if __name__ == "__main__":
    file_name_pattern = "data_{}.txt"
    key_words_file_name = "key_words.txt"
    files_number = 4
    lines_number_max = 200
    prepare_data(
        file_name_pattern, key_words_file_name, files_number, lines_number_max
    )
