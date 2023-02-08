import argparse
import os
import pathlib
import subprocess
import sys
import tomllib

def get_config(filename: str) -> dict:
    """Parse toml config"""
    try:
        with open(filename, "rb") as fh: # tomllib needs binary rep
            return tomllib.load(fh)
    except OSError:
        print(
            f"Couldn't access file: {filename}\n"
            f"Ensure it is in the current directory: {pathlib.Path.cwd()} "
            "and has read permission"
        )
        sys.exit(1)
    except tomllib.TOMLDecodeError:
        print(
           f"Bad config file: {filename}"
            "Make sure its contents are valid toml"
        )
        sys.exit(1)

def vet_config(config: dict, required_keys: list[str]) -> None:
    """Ensure that config contains all required keys"""
    missing_keys = required_keys - config.keys()
    if missing_keys:
        raise ValueError(
            f"config missing required keys: {missing_keys}"
        )

class TextBlock:
    """Group lines of text with specified indentation"""
    def __init__(self, indentation: str =' '*4) -> None:
        self.indentation = indentation
        self.lines       = list()
        self.level       = 0 # indent level

    def write_line(self, line: str) -> None:
        self.lines.append((self.indentation * self.level) + line + '\n')

    def write_lines(self, lines: list[str]):
        if lines is None:
            return self

        for l in lines:
            self.write_line(l)
        return self

    def indent(self, lines: list[str] = None):
        """Lines written will now be indented one block futher in"""
        self.level += 1
        self.write_lines(lines)
        return self

    def outdent(self, lines: list[str] = None):
        """Lines written will now be indented one block back out"""
        if self.level > 0: 
            self.level -= 1
        self.write_lines(lines)
        return self

    def format(self, fstr_args: list[str]) -> str:
        """Apply fstr_args to each f-string in self.lines
        
        If lines in self.lines are not f-strings, no modifications are made.
        If lines in self.lines are f-strings but do not require the full array
        of f-string arguments provided, they will take from the array as
        many as are needed. If they require more than those provided, an
        error will be thrown (and not caught here).
        """
        new_lines = []
        for l in self.lines:
            new_lines.append(l.format(*fstr_args))
        return ''.join(new_lines)

    def __add__(self, other) -> str:
        return str(self) + str(other)

    def __str__(self) -> str:
        return ''.join(self.lines)

class Printer:
    def __init__(self, out=sys.stdout, mode="a"):
        self._out = out
        self._open_files = dict()
        if out != sys.stdout:
            self._out = self.open_file(out, mode)

    def __del__(self):
        for f in self._open_files.values():
            f.close()

    def open_file(self, file, mode='a'):
        try: # bad form to filter on type
            if type(str): # assume filename
                if file in self._open_files:
                    return
                self._out = open(file, mode)
            elif type(pathlib.Path):
                if file.name in self._open_files:
                    return
                self._out = file.open(mode)
        except OSError:
            print(f"Could not open file: {file}")

        # track open files to prevent reopens and/or premature closes
        self._open_files[self._out.name] = self._out

    def _print(out, text) -> None:
        # the idea here is to enable maximal flexibility in handling
        # a diversity of writing sources. by making no assumption
        # regarding what object "out" is, anything from a file,
        # to a simple string, or any other sink may be written to via "out"
        out(text)  
    
    def print(self, text='', append_nl=True) -> None:
        Printer._print(
            self._out.write, # assume out is a file handle; most common case
            str(text) + '\n' if append_nl else str(text)
        )

class APIGenerator:
    """Given a config file that specifies the parameters of a barebones flask
       api, create a skeleton for its development.
    """
    # CONFIG #################################################################

    SUPPORTED_MODES = {"create", "write", "script"} # only public class constant
    _CONFIG_KEYS = { # required keys in global table of toml file
        "name", "api", "file", "script", "python dependencies"
    }

    # FILE GENERATION STRINGS ################################################

    _SEP                = " "
    _INDENT             = _SEP*4
    _BLUEPRINT_CREATE   = 'bp = Blueprint("{0}", __name__, url_prefix="/{0}")'
    _BLUEPRINT_IMPORT   = 'from . import {0}'
    _BLUEPRINT_REGISTER = 'app.register_blueprint({0}.bp)'
    _ROUTE_DECORATOR    = '@bp.route("/{0}", methods={1})'
    _ROUTE_FUNC         = 'def {0}():'

    _INIT_HEADER = TextBlock(_INDENT).write_lines([
        'import tomllib',
        'import flask',
        '',
        'def api(config=None):',
    ]).indent([
            'app = flask.Flask(__name__)',
            'with open(config, "rb") as fh:',
    ]).indent([
                'app.config.from_mapping(tomllib.load(fh))',
    ])

    _INIT_BODY = TextBlock(_INDENT).indent([
            _BLUEPRINT_IMPORT,
            _BLUEPRINT_REGISTER,
    ])

    _INIT_FOOTER = TextBlock(_INDENT).indent([
            'return app',
    ])

    _API_FILE_HEADER = TextBlock(_INDENT).write_lines([
        'from flask import (',
    ]).indent([
            'Blueprint,',
            'url_for,',
            'request,',
            'render_template,',
            'flash, g, redirect, session',
    ]).outdent([
        ')',
    ])

    ###########################################################################

    def __init__(self, config):
        # TODO: update instance variables to reflect access

        # will raise ValueError on bad config
        vet_config(config, APIGenerator._CONFIG_KEYS) 

        # path creation 
        self.base_dir     = pathlib.Path.cwd()
        self.flask_dir    = self.base_dir / config["name"]
        self.config_file  = self.base_dir / config["file"]
        self.shell_script = self.base_dir / config["script"]

        # python gunicorn/flask
        self.api          = config["api"]
        self.gunicorn     = config["gunicorn"]
        self.dependencies = config["python dependencies"]

        # writing
        self.printer      = Printer()
        self.print        = self.printer.print

        # state
        self.env_setup    = False
        self.complete     = False

    # sole point of interface; only public method
    # to understand class, follow flow of "create"
    def do_task(self, task=None):
        match task:
            case "create":
                self._setup_environment()
                self._write_files()
                self._write_executable()
            case "write": # destructive, be careful
                self._write_files()
                self._write_executable()
            case "script":
                self._write_executable()
            case "teardown":
                pass
            case _:
                pass
            
    def _write_files(self):
        self._write_init_file()
        self._write_api_files()

    def _install_dependencies(self):
        # Assumes that subprocess will pick up whatever is in $env:COMSPEC to
        # use as the shell when shell=True on windows systems, and that this is
        # cmd.exe. Note that pathlib will format the file correctly regardless
        # of operating system.
        #
        # TODO: Analyze other production build scripts to see how they
        #       handle multiplatform installation.
        cmd_info = {
            "posix" : {
                "source"           : "source ", # notice space
                "path_to_activate" : pathlib.Path(".venv/bin/activate"),
                "join on"          : "&&"
            },
            "nt" : {
                "source"          : "",
                "path_to_activate" : pathlib.Path(".venv/Scripts/activate.bat"),
                "join on"          : "&&"
            }
        }[os.name] # don't miss this

        # let any exception in run to propogate up to caller
        subprocess.run(
            cmd_info["join on"].join([
                f'{cmd_info["source"]}{cmd_info["path_to_activate"]}',
                *[
                    f"python -m pip install {d}"
                    for d in self.dependencies
                ],
                "deactivate",
            ]), 
            shell="True", check=True
        )

    def _setup_venv(self) -> bool:
        # make venv, will clobber existing one
        #
        # TODO: if venv is present, check for required dependencies
        #       if present leave alone, if missing install after prompt
        try:
            subprocess.run(
                # sys.executable is the path of the interpreter used to
                # execute this script
                [sys.executable, "-m", "venv", ".venv"],
                check=True, # raises exception on nonzero rc
            )
            self._install_dependencies()
        except subprocess.CalledProcessError:
            print(
                f"Failed to create virtual environment in {self.base_dir}"
            )
            return False

        return True

    def _setup_dir_structure(self) -> bool:
        try:
            # dont allow overwrite
            self.flask_dir.mkdir(exist_ok=False)

            # make files
            (self.flask_dir / "__init__.py").touch()
            for _, props in self.api.items():
                (self.flask_dir / props["filename"]).touch()
        except OSError: # could try out exception groups here
            print("Failed to create necessary directory structure")
            return False
        
        return True

    def _setup_environment(self):
        self.env_setup = self._setup_venv() and self._setup_dir_structure()

    def _write_init_file(self):
        try:
            self.printer.open_file((self.flask_dir / "__init__.py"))
            self.print(APIGenerator._INIT_HEADER)
            for module in self.api:
                # format method below expects list arg, hence [module]
                self.print(APIGenerator._INIT_BODY.format([module]))
            self.print(APIGenerator._INIT_FOOTER)
        except OSError:
            print("Error writing __init__.py")

    def _write_endpoint(self, endpoint, props):
        self.print(
            APIGenerator._ROUTE_DECORATOR.format(
                props["path"],
                '[ "' + '", "'.join(props["methods"]) + '" ]'
        ))
        self.print(APIGenerator._ROUTE_FUNC.format(endpoint))

        # write if else ladder for methods, generalize eventually
        if "POST" in props["methods"]:
            self.print(TextBlock(APIGenerator._INDENT).indent([
                'if request.method == "POST":'
            ]).indent([
                    'pass'
            ]))

        # print get
        self.print(TextBlock(APIGenerator._INDENT).indent([
            'return "{0}", 200'
        ]).format([endpoint]))

    def _write_api_files(self):
        for module, props in self.api.items():
            try:
                self.printer.open_file((self.flask_dir / props["filename"]))
                self.print(APIGenerator._API_FILE_HEADER)
                self.print(APIGenerator._BLUEPRINT_CREATE.format(module))
                self.print()
                for ep in props["endpoints"].items():
                    self._write_endpoint(*ep)
            except OSError:
                print("Error writing __init__.py")

    def _write_executable(self):
        # TODO: Need to write script for cmd.exe
        bash_script = TextBlock(indentation=" "*2).write_lines([
            '#!/usr/bin/env bash',
            '',
            'declare -r \\',
        ]).indent([
                "CONFIG='{}'".format(self.config_file),
                "HOST='{}'".format(self.gunicorn["host"]),
        ]).outdent([
            "declare -ir PORT={} NUM_WORKERS={} # 8000 is default port".format(
                self.gunicorn["port"], 
                self.gunicorn["workers"]
            ),
        ]).write_lines([
            "while getopts 'sq' ARG; do",
        ]).indent([
                'case "${ARG}" in'
        ]).indent([
                    's)',
        ]).indent([
                        '. .venv/bin/activate',
                        'gunicorn \\',
                        r' --bind "${HOST}":${PORT} ''\\',
                        r' --workers ${NUM_WORKERS} ''\\',
                        # TODO: below f-string is unreadable - fix
                        f"'{self.flask_dir.name}:api(\"'"
                        "\"${CONFIG}\"" "'\")' &",
                        ';;',
        ]).outdent([
                    'q) pkill -f gunicorn ;;',
                    '?) echo "Bad args"; return 1 ;;',
        ]).outdent([
                'esac',
        ]).outdent([
            'done',
        ])

        try:
            if os.name == "posix":
                self.printer.open_file(self.shell_script)
                self.print(bash_script)
                self.shell_script.chmod(0o755) # make executable
            elif os.name == "nt": pass
        except: pass
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config")
    parser.add_argument("action", choices=APIGenerator.SUPPORTED_MODES)
    args = parser.parse_args()

    APIGenerator(get_config(
        args.config if args.config is not None else "api.toml"
    )).do_task(args.action)