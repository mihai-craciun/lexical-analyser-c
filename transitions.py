def is_allowed_first_char_for_id(c):
    return is_letter(c) or c in ['_']

def is_allowed_char_for_id(c):
    return is_allowed_first_char_for_id(c) or is_digit(c)

def is_not_allowed_char_for_id(c):
    return not is_allowed_char_for_id(c)

def is_letter(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z'

def is_digit(c):
    return c.isdigit()

def anything(c):
    return True

def is_space(c):
    return ' ' == c

def is_newline(c):
    return '\n' == c

def is_tab(c):
    return '\t' == c

def is_separator(c):
    return c in ['[',']','(',')','{','}',',',';']

def is_non_token_separator(c):
    return c in ['\n','\t',' ']

def is_character(c):
    return c in ['*', '+', '-', '(', ')', '[', ']', '{', '}', ':', '=', '.', ',', '>', '<', '!', ';']

def is_hash(c):
    return c == '#'

def is_single_quote(c):
    return c == "'"

def is_double_quote(c):
    return c == '"'

def is_negative_sign(c):
    return c == '-'

def is_point(c):
    return c == '.'

def is_escape(c):
    return c == '\\'

def is_slash(c):
    return c =='/'

def is_star(c):
    return c == '*'

def is_character_can_be_followed_by_equal(c):
    return c in ['+', '-', '*', '<', '>']

def is_equal(c):
    return c == '='

def is_e(c):
    return c == 'e'

def is_hexa_char(c):
    return is_digit(c) or 'a' <= c <= 'f'

def is_char(c):
    return ord(c) >= 32 and ord(c) <= 126