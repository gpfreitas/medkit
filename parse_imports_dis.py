#!/usr/bin/env python3
"""
This script takes as input a list of Python source files and outputs the
top-level modules that are imported in those source files.

The script does this without executing any code. This is useful when you have
exercise code (that often has syntax errors / missing code) or if you want to
avoid any harmful side-effects of executing untrusted code.
"""

import dis
import sys
import io
import logging
from tokenize import tokenize, untokenize, ENCODING, NAME, NEWLINE, NL, TokenError
from itertools import takewhile, dropwhile, chain

class BaseParseImportsError(Exception):
    pass

class ModuleSyntaxError(BaseParseImportsError):
    pass

def tokenize_source(source):
    """Maps a string of Python source into an iterable of tokens.

    Note that your source can have syntax errors.
    """
    tokens = tokenize(io.BytesIO(source.encode('utf-8')).readline)
    return tokens

def is_not_physical_newline_token(token):
    "tokenize.TokenInfo -> True iff physical newline token."
    return token.type != NL
def is_not_logical_newline_token(token):
    "tokenize.TokenInfo -> True iff logical newline token."
    return token.type != NEWLINE 
def is_not_import_token(token):
    "tokenize.TokenInfo -> True iff not the beginning of an import statement."
    import_token_conditions = [(token.type == NAME and token.string == 'import'),
                               (token.type == NAME and token.string == 'from')]
    return not any(import_token_conditions)

def extract_import_logical_lines(source):
    "Filters out logical lines from source that are not import statements."
    tokens = tokenize_source(source)
    encoding_token = next(tokens)
    assert encoding_token.type == ENCODING
    for tok in tokens:
        tokens = chain([tok], tokens)
        start_import = dropwhile(is_not_import_token, tokens)
        import_tokens = takewhile(is_not_logical_newline_token, start_import)
        
        import_statement = untokenize(import_tokens) # a single logical line
        # For some reason the output of untokenize above contains various lines
        # with "\", the forwardslash character, used in Python for explicit
        # linebreaks. I think we obtain one "\" per line of source that we
        # ignored. I would prefer for those lines to be filtered out, and
        # I tried accomplishing that by filtering out the tokenize.NL tokens.
        # That did not work. I could of course eliminate these linebreaks in
        # the string ``import_statement``, but those line breaks are not a
        # problem that I can see by running the program, or by reading the
        # source, so I decided to not eliminate the linebreaks from
        # ``import_statement``.
        if not import_statement:
            continue
        yield import_statement

def imported_modules(import_statements):
    """Maps sequence of import statements into set of imported modules.

    The caller is responsible for passing import statements with correct
    syntax. If there are syntax errors in the import statements, a
    ``ModuleSyntaxError`` will be raised.
    """
    imports = set()
    for imp_statement in import_statements:
        try:
            instructions = dis.get_instructions(imp_statement)
        except SyntaxError as e:
            raise ModuleSyntaxError
        new_imports = {__.argval for __ in instructions if __.opname == 'IMPORT_NAME'}
        if new_imports:
            imports.update(new_imports)
    return imports

def module_dependencies(module_path):
    "Maps the path of a module into the set of modules it imports."
    with open(module_path) as f:
        source = f.read()
    import_statements = extract_import_logical_lines(source)
    imp_modules = imported_modules(import_statements)
    return imp_modules


if __name__ == "__main__":
    used_modules = set()
    if sys.argv[1].isdigit():
        maxdepth = int(sys.argv[1])
        first_module_pos = 2
    else:
        maxdepth = 2
        first_module_pos = 1
    for module_path in sys.argv[first_module_pos:]:
        try:
            this_module_deps = module_dependencies(module_path)
            used_modules.update(this_module_deps)
        except ModuleSyntaxError as e:
            logging.exception("Syntax error when processing module {}".format(module_path))
        except TokenError as e:
            logging.exception("Tokenization error when processing module {}".format(module_path))
    top_level_modules = {'.'.join(_.split('.')[:maxdepth]) for _ in used_modules}
    print('\n'.join(sorted(list(top_level_modules))))
