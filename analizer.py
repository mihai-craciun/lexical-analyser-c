from transitions import *

class LexicalAnalyzer():

    #Token Types Table
    TOKEN_TYPES_TABLE = ['IDENTIFIER', 'KEYWORD', 'STRING', 'CHAR', 'INTEGER', 'FLOAT', 'HEXADECIMAL',
                         'COMMENT', 'WHITESPACE', 'OPERATOR', 'SEPARATOR', 'ERROR']

    #Operators Table
    OPERATORS = [':', '?', '+', '++', '+=', '-', '--', '-=', '*', '*=', '/', '/=', '%', '%=', '=', '==',
                       '<', '<=', '>', '>=', '&', '&&', '&=', '!', '!=', '|', '|=', '^', '^=', '>>', '>>=', '<<', '<<=', '.']

    #Keywords Table
    KEYWORDS = ['auto', 'int', 'const', 'short', 'break', 'long', 'continue', 'signed', 'double', 'struct', 'float', 'unsigned', 'else', 'switch', 'for',
                      'void', 'case', 'register', 'default', 'sizeof', 'char', 'return', 'do', 'static', 'enum', 'typedef', 'goto', 'volatile', 'extern', 'union', 'if', 'while']

    def __init__(self, path):

        #String Table
        self.STRINGS = []  # Initially empty

        with open(path) as filestream:
            self.source = filestream.read()
        self.position = 0

    def is_eof(self):
        if self.position == len(self.source):
            return True
        return False

    def gettoken(self):

        if self.is_eof():
            return None

        #Creating the dfa with the current remaining code
        DFA = Dfa(self.source[self.position:])

        token_type, token_value, size = DFA.run()
        self.position += size

        STATES_MAPPER = {
            'STRING_END': 'STRING',
            'CHAR_END': 'CHAR',
            'MULTI_LINE_COMMENT_END': 'COMMENT',
            'SINGLE_LINE_COMMENT': 'COMMENT',
            'NON_TOKEN_SEPARATOR': 'WHITESPACE',
            'NUMBER': 'INTEGER',
            'NUMBER_U': 'INTEGER',
            'NUMBER_L': 'INTEGER',
            'NUMBER_UL': 'INTEGER',
            'ZERO': 'INTEGER',
            'HEXA': 'HEXADECIMAL',
            'FLOAT_NUMBER': 'FLOAT',
            'EXPONENT': 'FLOAT',
            'EXPONENT_VALUE': 'FLOAT',
            'FLOAT_NUMBER_L': 'FLOAT',
            '(': 'SEPARATOR',
            '[': 'SEPARATOR',
            '+': 'OPERATOR',
            '-': 'OPERATOR',
            '*': 'OPERATOR',
            '/': 'OPERATOR',
            '%': 'OPERATOR',
            '=': 'OPERATOR',
            '<': 'OPERATOR',
            '>': 'OPERATOR',
            '&': 'OPERATOR',
            '!': 'OPERATOR',
            '|': 'OPERATOR',
            '^': 'OPERATOR',
            '>>': 'OPERATOR',
            '<<': 'OPERATOR',
            '.': 'OPERATOR',
        }

        #Mapping states to token types
        if token_type in STATES_MAPPER.keys():
            token_type = STATES_MAPPER[token_type]
        
        #If error halt
        if token_type in ['ERROR']:
            #Show error and exit program
            print('ERROR - {0} at position {1}'.format(token_value, self.position))
            exit(0)
        
        if token_value in LexicalAnalyzer.KEYWORDS:
            token_type = 'KEYWORD'

        if token_type in ['COMMENT', 'WHITESPACE']:
            return self.gettoken()
        
        #Getting the index for the token type
        token_type_index = LexicalAnalyzer.TOKEN_TYPES_TABLE.index(token_type)

        #Creating index if not exists
        if token_value not in self.STRINGS:
            self.STRINGS.append(token_value)
        token_value_index = self.STRINGS.index(token_value)

        return Token(token_type_index, token_value_index)
            

class Token():

    def __init__(self, token_type, token_value):
        self.type = token_type
        self.value = token_value
    
    def write(self, context):
        print('{0} - {1}'.format(LexicalAnalyzer.TOKEN_TYPES_TABLE[token.type], context.STRINGS[token.value]))

class Dfa():

    STATES_LIST = [
        'INITIAL',
        #Identifiers
        'IDENTIFIER',
        #Nondeterministic prefixes
        '+',
        '-',
        '*',
        '/',
        '%',
        '=',
        '<',
        '>',
        '&',
        '!',
        '|',
        '^',
        '>>',
        '<<',
        '.',
        #Separators
        'NON_TOKEN_SEPARATOR',
        'SEPARATOR',
        # Comments
        'COMMENT',
        'SINGLE_LINE_COMMENT',
        'MULTI_LINE_COMMENT',
        'MULTI_LINE_COMMENT_STAR',
        'MULTI_LINE_COMMENT_END',
        # Literals
        'CHAR',
        'CHAR_ESCAPE',
        'CHAR_ESCAPE_X',
        'CHAR_ESCAPE_HEX1',
        'CHAR_ESCAPE_NUMBER',
        'CHAR_CHARACTER',
        'CHAR_END',
        'STRING',
        'STRING_ESCAPE',
        'STRING_END',
        'NUMBER',
        'NUMBER_U',
        'NUMBER_L',
        'NUMBER_UL',
        'ZERO',
        'HEXA',
        'FLOAT_NUMBER',
        'EXPONENT',
        'EXPONENT_VALUE',
        'FLOAT_NUMBER_L',
        # Operators
        'OPERATOR',
        # Special
        'END',
        'ERROR',
    ]
    

    def __init__(self, source):

        self.STATES = {}
        for index, state in enumerate(Dfa.STATES_LIST):
            self.STATES[state] = index

        self.position = 0;
        self.source = source;
        self.state = self.STATES['INITIAL'];

        self.TRANSITIONS = {

            # Initial State

            self.STATES['INITIAL']: [
                [lambda x: x == '0', self.STATES['ZERO']],
                [lambda x: x == '+', self.STATES['+']],
                [lambda x: x == '-', self.STATES['-']],
                [lambda x: x == '*', self.STATES['*']],
                [lambda x: x == '/', self.STATES['/']],
                [lambda x: x == '%', self.STATES['%']],
                [lambda x: x == '=', self.STATES['=']],
                [lambda x: x == '<', self.STATES['<']],
                [lambda x: x == '>', self.STATES['>']],
                [lambda x: x == '&', self.STATES['&']],
                [lambda x: x == '!', self.STATES['!']],
                [lambda x: x == '|', self.STATES['|']],
                [lambda x: x == '^', self.STATES['^']],
                [lambda x: x == '.', self.STATES['.']],
                [is_separator, self.STATES['SEPARATOR']],
                [is_operator, self.STATES['OPERATOR']],
                [is_non_token_separator, self.STATES['NON_TOKEN_SEPARATOR']],
                [is_allowed_first_char_for_id, self.STATES['IDENTIFIER']],
                [is_digit, self.STATES['NUMBER']],
                [is_single_quote, self.STATES['CHAR']],
                [is_double_quote, self.STATES['STRING']],
                [anything, self.STATES['ERROR']],
            ],

            # Identifiers

            self.STATES['IDENTIFIER']: [
                [is_allowed_char_for_id, self.STATES['IDENTIFIER']],
                [is_not_allowed_char_for_id, self.STATES['END']],
            ],

            # Nondeterministic Prefixes

            self.STATES['+']: [
                [lambda x: x == '+', self.STATES['OPERATOR']],
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']],
            ],
            self.STATES['-']: [
                [lambda x: x == '-', self.STATES['OPERATOR']],
                [lambda x: x == '>', self.STATES['OPERATOR']],
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [is_digit, self.STATES['NUMBER']],
                [anything, self.STATES['END']],
            ],
            self.STATES['*']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']]
            ],
            self.STATES['/']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [lambda x: x == '/', self.STATES['SINGLE_LINE_COMMENT']],
                [lambda x: x == '*', self.STATES['MULTI_LINE_COMMENT']],
                [anything, self.STATES['END']]
            ],
            self.STATES['%']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']]
            ],
            self.STATES['=']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']]
            ],
            self.STATES['<']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [lambda x: x == '<', self.STATES['<<']],
                [anything, self.STATES['END']],
            ],
            self.STATES['>']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [lambda x: x == '>', self.STATES['>>']],
                [anything, self.STATES['END']],
            ],
            self.STATES['<<']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']],
            ],
            self.STATES['>>']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']],
            ],
            self.STATES['&']: [
                [lambda x: x == '&', self.STATES['OPERATOR']],
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']],
            ],
            self.STATES['|']: [
                [lambda x: x == '|', self.STATES['OPERATOR']],
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']],
            ],
            self.STATES['!']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']],
            ],
            self.STATES['^']: [
                [lambda x: x == '=', self.STATES['OPERATOR']],
                [anything, self.STATES['END']],
            ],
            self.STATES['.']: [
                [is_digit, self.STATES['FLOAT_NUMBER']],
                [is_allowed_char_for_id, self.STATES['END']],
                [anything, self.STATES['ERROR']],
            ],

            # Separators

            self.STATES['SEPARATOR']: [
                [anything, self.STATES['END']],
            ],
            self.STATES['NON_TOKEN_SEPARATOR']: [
                [is_non_token_separator, self.STATES['NON_TOKEN_SEPARATOR']],
                [anything, self.STATES['END']],
            ],

            # Literals

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
                [is_digit, self.STATES['CHAR_ESCAPE_NUMBER']],
                [lambda c: c == 'x', self.STATES['CHAR_ESCAPE_X']],
                [is_char, self.STATES['CHAR_CHARACTER']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE_NUMBER']: [
                [is_digit, self.STATES['CHAR_ESCAPE_NUMBER']],
                [is_single_quote, self.STATES['CHAR_END']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE_X']: [
                [is_hexa_char, self.STATES['CHAR_ESCAPE_HEX1']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['CHAR_ESCAPE_HEX1']: [
                [is_hexa_char, self.STATES['CHAR_CHARACTER']],
                [is_single_quote, self.STATES['CHAR_END']],
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
                [is_newline, self.STATES['STRING']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['STRING_END']: [
                [anything, self.STATES['END']],
            ],
            self.STATES['NUMBER']: [
                [is_digit, self.STATES['NUMBER']],
                [is_point, self.STATES['FLOAT_NUMBER']],
                [lambda x: x == 'L', self.STATES['NUMBER_L']],
                [lambda x: x == 'U', self.STATES['NUMBER_U']],
                [is_e, self.STATES['EXPONENT']],
                [anything, self.STATES['END']],
            ],
            self.STATES['NUMBER_L']: [
                [lambda x: x == 'U', self.STATES['NUMBER_UL']],
                [anything, self.STATES['END']],
            ],
            self.STATES['NUMBER_U']: [
                [lambda x: x == 'L', self.STATES['NUMBER_UL']],
                [anything, self.STATES['END']],
            ],
            self.STATES['NUMBER_UL']: [
                [anything, self.STATES['END']],
            ],
            self.STATES['FLOAT_NUMBER']: [
                [is_digit, self.STATES['FLOAT_NUMBER']],
                [lambda x: x == 'L', self.STATES['FLOAT_NUMBER_L']],
                [is_e, self.STATES['EXPONENT']],
                [anything, self.STATES['END']],
            ],
            self.STATES['EXPONENT']: [
                [lambda x: x == '-', self.STATES['EXPONENT_VALUE']],
                [lambda x: x == '+', self.STATES['EXPONENT_VALUE']],
                [is_digit, self.STATES['EXPONENT_VALUE']],
                [anything, self.STATES['ERROR']],
            ],
            self.STATES['EXPONENT_VALUE']: [
                [is_digit, self.STATES['EXPONENT_VALUE']],
                [lambda x: x == 'L', self.STATES['FLOAT_NUMBER_L']],
                [anything, self.STATES['END']],
            ],
            self.STATES['FLOAT_NUMBER_L']: [
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

            # Comments

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
                [is_star, self.STATES['MULTI_LINE_COMMENT_STAR']],
                [anything, self.STATES['MULTI_LINE_COMMENT']]
            ],
            self.STATES['MULTI_LINE_COMMENT_END']: [
                [anything, self.STATES['END']]
            ],
            self.STATES['SINGLE_LINE_COMMENT']: [
                [is_newline, self.STATES['END']],
                [anything, self.STATES['SINGLE_LINE_COMMENT']]
            ],

            # Operators

            self.STATES['OPERATOR']: [
                [anything, self.STATES['END']],
            ],
        }

    def run(self):

        while True:

            #Checking for end of file
            if self.position == len(self.source):
                
                #Check if it is a valid identifier
                state_tranzitions = self.TRANSITIONS[self.state]

                is_valid_token = False
                for tranzition, state in state_tranzitions:
                    if state == self.STATES['END']:
                        is_valid_token = True
                
                if is_valid_token == True:
                    return Dfa.STATES_LIST[self.state], self.source[:self.position], self.position
                else:
                    return 'ERROR', self.source[:self.position], self.position

            #Getting the current character
            c = self.source[self.position];
            self.position += 1;

            state_tranzitions = self.TRANSITIONS[self.state]
            for tranzition, state in state_tranzitions:
                if tranzition(c):

                    if state == self.STATES['ERROR']:
                        return 'ERROR', self.source[:self.position], self.position

                    if state == self.STATES['END']:
                        return Dfa.STATES_LIST[self.state], self.source[:self.position-1], self.position-1
                    
                    self.state = state
                    break
        

# Main
analyzer = LexicalAnalyzer('./aici.txt')
while not analyzer.is_eof():
    token = analyzer.gettoken()
    if token is not None:
        # Avem un token
        token.write(analyzer)