from transitions import *
from time import sleep
from sys import exit
from collections import defaultdict
from pprint import pprint


class Tokenizer():
    KEYWORDS = ['auto', 'int', 'const', 'short', 'break', 'long', 'continue', 'signed', 'double', 'struct','float', 'unsigned', 'else', 'switch', 'for', 'void', 'case', 'register', 'default', 'sizeof', 'char', 'return', 'do', 'static', 'enum', 'typedef', 'goto', 'volatile', 'extern', 'union', 'if', 'while']

    def __init__(self, filepath):
        with open(filepath) as stream:
            self.source_code = stream.read()
        self.position = 0
        self.tabela = defaultdict(list)

    def gettoken(self):
        dfa = Dfa(self.source_code[self.position:])

        # import ipdb; ipdb.set_trace()
        token_val, token_type, consumed_chars = dfa.run()
        self.position += consumed_chars

        MAPPER = {
            'CHARACTER_CAN_BE_FOLLOWED_BY_EQUAL': 'OPERATOR',
            'STRING_END': 'STRING',
            'CHAR_END': 'CHAR',
            'CHARACTER': 'OPERATOR',
            'GROUP_CHARACTER': 'GROUP_OPERATOR',
            'MULTI_LINE_COMMENT_END': 'MULTI_LINE_COMMENT',
        }

        if token_type in MAPPER:
            token_type = MAPPER[token_type]

        if token_type == 'IDENTIFIER':
            if token_val in self.KEYWORDS:
                token_type = 'KEYWORD'
        elif token_type == 'NEWLINE':
            token_val = len(token_val) - 1
            token_type = 'INDENTATION'
        elif token_type in ['COMMENT', 'SPACE']:
            return self.gettoken()

        self.tabela[(token_type, token_val)].append(self.position - consumed_chars)
        return self.position - consumed_chars


class Dfa():

    STATES_LIST = [
        'INITIAL',
        'IDENTIFIER',
        'SPACE',
        'NEWLINE',
        'CHARACTER',
        'NUMBER',
        'COMMENT',
        # Comments
        'SINGLE_LINE_COMMENT',
        'MULTI_LINE_COMMENT',
        'MULTI_LINE_COMMENT_STAR',
        'MULTI_LINE_COMMENT_END',
        # Char
        'CHAR',
        'CHAR_ESCAPE',
        'CHAR_ESCAPE_X',
        'CHAR_ESCAPE_HEX1',
        'CHAR_ESCAPE_OCTAL1',
        'CHAR_ESCAPE_OCTAL2',
        'CHAR_CHARACTER',
        'CHAR_END',
        # String
        'STRING',
        'STRING_ESCAPE',
        'STRING_END',
        'NEGATIVE_SIGN',
        'FLOAT_NUMBER',
        'ESCAPING',
        'CHARACTER_ESCAPED',
        'CHARACTER_CAN_BE_FOLLOWED_BY_EQUAL',
        'GROUP_CHARACTER',
        'EXPONENT',
        'ZERO',
        'HEXA',
        'END',
        'ERROR',
    ]

    STATES = {}
    for index, state in enumerate(STATES_LIST):
        STATES[state] = index

    NONPRODUCTING_STATES = [
        STATES['ESCAPING'],
        STATES['CHARACTER_ESCAPED'],
    ]

    def __init__(self, input_list):
        self.state = 0
        self.TRANSITIONS = {
            self.STATES['INITIAL']: [
                [is_negative_sign, self.STATES['NEGATIVE_SIGN']],
                [lambda x: x == '0', self.STATES['ZERO']],
                [is_allowed_first_char_for_id, self.STATES['IDENTIFIER']],
                [is_space, self.STATES['SPACE']],
                [is_newline, self.STATES['NEWLINE']],
                [is_digit, self.STATES['NUMBER']],
                [is_character_can_be_followed_by_equal, self.STATES['CHARACTER_CAN_BE_FOLLOWED_BY_EQUAL']],
                [is_character, self.STATES['CHARACTER']],
                [is_slash, self.STATES['COMMENT']],
                [is_single_quote, self.STATES['CHAR']],
                [is_double_quote, self.STATES['STRING']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['IDENTIFIER']: [
                [is_allowed_char_for_id, self.STATES['IDENTIFIER']],
                [is_not_allowed_char_for_id, self.STATES['END']],
            ],
            self.STATES['SPACE']: [
                [is_space, self.STATES['SPACE']],
                [anything, self.STATES['END']],
            ],
            self.STATES['NEWLINE']: [
                [is_tab, self.STATES['NEWLINE']],
                [anything, self.STATES['END']],
            ],
            self.STATES['CHARACTER']: [
                [anything, self.STATES['END']],
            ],
            self.STATES['CHAR']: [
                [is_escape, self.STATES['CHAR_ESCAPE']],
                [is_char, self.STATES['CHAR_CHARACTER']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_CHARACTER']: [
                [is_single_quote, self.STATES['CHAR_END']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE']: [
                [is_digit, self.STATES['CHAR_ESCAPE_OCTAL1']],
                [lambda c: c == 'x', self.STATES['CHAR_ESCAPE_X']],
                [is_char, self.STATES['CHAR_CHARACTER']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE_OCTAL1']: [
                [is_digit, self.STATES['CHAR_ESCAPE_OCTAL2']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE_OCTAL2']: [
                [is_digit, self.STATES['CHAR_CHARACTER']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE_X']: [
                [is_hexa_char, self.STATES['CHAR_ESCAPE_HEX1']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE_HEX1']: [
                [is_hexa_char, self.STATES['CHAR_CHARACTER']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_END']: [
                [anything, self.STATES['END']],
            ],
            self.STATES['STRING']: [
                [is_double_quote, self.STATES['STRING_END']],
                [is_escape, self.STATES['STRING_ESCAPE']],
                [is_char, self.STATES['STRING']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['STRING_ESCAPE']: [
                [is_char, self.STATES['STRING']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['STRING_END']: [
                [anything, self.STATES['END']],
            ],
            self.STATES['NUMBER']: [
                [is_digit, self.STATES['NUMBER']],
                [is_point, self.STATES['FLOAT_NUMBER']],
                [is_e, self.STATES['EXPONENT']],
                [anything, self.STATES['END']],
            ],
            self.STATES['FLOAT_NUMBER']: [
                [is_digit, self.STATES['NUMBER']],
                [anything, self.STATES['END']],
            ],
            self.STATES['COMMENT']: [
                [is_slash, self.STATES['SINGLE_LINE_COMMENT']],
                [is_star, self.STATES['MULTI_LINE_COMMENT']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['MULTI_LINE_COMMENT']: [
                [is_star, self.STATES['MULTI_LINE_COMMENT_STAR']],
                [anything, self.STATES['MULTI_LINE_COMMENT']]
            ],
            self.STATES['MULTI_LINE_COMMENT_STAR']: [
                [is_slash, self.STATES['MULTI_LINE_COMMENT_END']],
                [anything, self.STATES['MULTI_LINE_COMMENT']]
            ],
            self.STATES['MULTI_LINE_COMMENT_END']: [
                [anything, self.STATES['END']]
            ],
            self.STATES['SINGLE_LINE_COMMENT']: [
                [is_newline, self.STATES['END']],
                [anything, self.STATES['SINGLE_LINE_COMMENT']]
            ],
            self.STATES['NEGATIVE_SIGN']: [
                [is_digit, self.STATES['NUMBER']],
                [anything, self.STATES['CHARACTER']],
            ],
            self.STATES['CHARACTER_CAN_BE_FOLLOWED_BY_EQUAL']: [
                [is_equal, self.STATES['GROUP_CHARACTER']],
                [anything, self.STATES['END']],
            ],
            self.STATES['GROUP_CHARACTER']: [
                [anything, self.STATES['END']],
            ],
            self.STATES['EXPONENT']: [
                [is_negative_sign, self.STATES['NEGATIVE_SIGN']],
                [is_digit, self.STATES['NUMBER']],
                [anything, self.STATES['END']],
            ],
            self.STATES['ZERO']: [
                [lambda x: x == 'x', self.STATES['HEXA']],
                [is_digit, self.STATES['NUMBER']],
                [anything, self.STATES['END']],
            ],
            self.STATES['HEXA']: [
                [is_hexa_char, self.STATES['HEXA']],
                [anything, self.STATES['END']],
            ],
        }
        self.position = 0
        self.input = input_list
        self.states = []
        self.output = []

    def consume(self):
        if self.position == len(self.input):
            # pprint(tokenizer.tabela)
            exit(0)

        state = self.TRANSITIONS[self.state]
        for transition_function, transition_state in state:
            if transition_function(self.input[self.position]):
                self.states.append(self.state)
                if transition_state not in self.NONPRODUCTING_STATES:
                    self.output.append(self.input[self.position])

                self.state = transition_state
                self.position += 1
                return
        raise Exception('No transition function')

    def run(self):
        # if self.STATES['ERROR'] == self.state:
        # 	raise Exception('Error')
        while self.state != self.STATES['END']:
            self.consume()

        for key in self.STATES:
            if self.STATES[key] == max(self.states):
                return [''.join(self.output[:-1]), key, self.position-1]


tokenizer = Tokenizer('./test.c')
while True:
    try:
        pozitie_de_caracter = tokenizer.gettoken()
        # sleep(0.1)
    except Exception:
        print("Am ajuns la o eroare")
        exit(0)

    for key in tokenizer.tabela:
        if pozitie_de_caracter in tokenizer.tabela[key]:
            print("{0} - {1}".format(*key))
