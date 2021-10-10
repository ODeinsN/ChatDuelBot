def get_word_set(filename: str) -> set[str]:
    file = open(filename, 'r')
    word_dict: set[str] = set()
    for line in file:
        line = line.replace('\n', '')
        word_dict.update({line})
    file.close()
    return word_dict
