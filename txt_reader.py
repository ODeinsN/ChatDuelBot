def get_word_dict(filename) -> set[str]:
    file = open(filename, 'r')
    word_dict: set[str] = set()
    for line in file:
        word_dict.update({line})
    file.close()
    return word_dict
