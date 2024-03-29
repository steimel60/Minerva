import argparse
import json
import os
import pathlib
import subprocess
import sys
import tomllib


def get_config(file_path: pathlib.Path) -> dict:
    """Parse toml config"""
    try:
        with file_path.open("rb") as fh:  # tomllib needs binary rep
            config = tomllib.load(fh)
            config["file path"] = file_path.resolve()  # for future reference
            return config
    except OSError:
        print(
            f"Couldn't access file: {file_path}\n"
            f"Ensure it is in the current directory: {pathlib.Path.cwd()} "
            "and has read permission"
        )
        sys.exit(1)
    except tomllib.TOMLDecodeError:
        print(f"Bad config file: {file_path}" "Make sure its contents are valid toml")
        sys.exit(1)


def vet_config(config: dict, required_keys: list[str]) -> None:
    """Ensure that config contains all required keys"""
    missing_keys = required_keys - config.keys()
    if missing_keys:
        raise ValueError(f"config missing required keys: {missing_keys}")


class TextBlock:
    """Group lines of text with specified indentation"""

    def __init__(self, indentation: str = " " * 4) -> None:
        self.indentation = indentation
        self.lines = list()
        self.level = 0  # indent level

    def write_line(self, line: str) -> None:
        self.lines.append((self.indentation * self.level) + line + "\n")

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
        return "".join(new_lines)

    def __add__(self, other) -> str:
        return str(self) + str(other)

    def __str__(self) -> str:
        return "".join(self.lines)


class Printer:
    """Print text to various files/sinks"""

    def __init__(self, out=sys.stdout, mode="w"):
        self._out = out
        self._open_files = dict()
        if out != sys.stdout:
            self._out = self.open_file(out, mode)

    def __del__(self):
        """Close files on exit

        This is not really needed given how short the program's lifespan is -
        the OS will automatically reclaim open file descriptors upon the
        program's termination. However, it is good practice to cleanup."""
        for f in self._open_files.values():
            f.close()

    def open_file(self, file, mode="w"):
        """Opens a file for subsequent writes"""
        try:  # bad form to filter on type, code to interface instead
            if type(str):  # assume filename
                if file in self._open_files:
                    return
                self._out = open(file, mode)
            elif type(pathlib.Path):
                if file.name in self._open_files:
                    return
                self._out = file.open(mode)
        except OSError:
            print(f"Could not open file: {file}")
            sys.exit(1)  # everything pivots on being able to write

        # track open files to prevent reopens and/or premature closes
        self._open_files[self._out.name] = self._out

    def _print(out, text) -> None:
        # the idea here is to enable maximal flexibility in handling
        # a diversity of writing sources. by making no assumption
        # regarding what object "out" is, anything from a file,
        # to a simple string, or any other sink may be written to via "out"
        try:
            out(text)
        except OSError:  # need better exception handling
            print("Could not write to:", out)

    def print(self, text="", append_nl=True) -> None:
        Printer._print(
            self._out.write,  # assume out is a file handle; most common case
            str(text) + "\n" if append_nl else str(text),
        )


PRINTER = Printer()


class FlaskFiller:
    _SEP = " "
    _INDENT = _SEP * 4
    _BLUEPRINT_CREATE = 'bp = Blueprint("{0}", __name__, url_prefix="/{0}")'
    _BLUEPRINT_IMPORT = "from . import {0}"
    _BLUEPRINT_REGISTER = "app.register_blueprint({0}.bp)"
    _ROUTE_DECORATOR = '@bp.route("/{0}", methods={1})'
    _ROUTE_FUNC = "def {0}():"

    _INIT_HEADER = (
        TextBlock(_INDENT)
        .write_lines(
            [
                "import tomllib",
                "import flask",
                "",
                "def factory(config):",
            ]
        )
        .indent(
            [
                "app = flask.Flask(__name__)",
                'with open(config, "rb") as fh:',
            ]
        )
        .indent(
            [
                "app.config.from_mapping(tomllib.load(fh))",
            ]
        )
    )

    _INIT_BODY = TextBlock(_INDENT).indent(
        [
            _BLUEPRINT_IMPORT,
            _BLUEPRINT_REGISTER,
        ]
    )

    _INIT_FOOTER = TextBlock(_INDENT).indent(
        [
            "return app",
        ]
    )

    _API_FILE_HEADER = (
        TextBlock(_INDENT)
        .write_lines(
            [
                "from flask import (",
            ]
        )
        .indent(
            [
                "Blueprint,",
                "url_for,",
                "request,",
                "render_template,",
                "flash, g, redirect, session",
            ]
        )
        .outdent(
            [
                ")",
            ]
        )
    )

    def __init__(self, api, flask_dir=pathlib.Path.cwd()):
        self.api = api
        self.flask_dir = flask_dir
        self.printer = PRINTER  # assumes all writes are sequential (they are)
        self.print = self.printer.print

    def fill(self):
        self._write_init_file()
        self._write_api_files()

    def _write_init_file(self):
        try:
            self.printer.open_file((self.flask_dir / "__init__.py"))
            self.print(FlaskFiller._INIT_HEADER)
            for module in self.api:
                # format method below expects list arg, hence [module]
                self.print(FlaskFiller._INIT_BODY.format([module]))
            self.print(FlaskFiller._INIT_FOOTER)
        except OSError:
            print("Error writing __init__.py")

    def _write_endpoint(self, endpoint, props):
        self.print(
            FlaskFiller._ROUTE_DECORATOR.format(
                props["path"], '[ "' + '", "'.join(props["methods"]) + '" ]'
            )
        )
        self.print(FlaskFiller._ROUTE_FUNC.format(endpoint))

        # TODO: generalize below
        if "POST" in props["methods"]:
            self.print(
                TextBlock(FlaskFiller._INDENT)
                .indent(['if request.method == "POST":'])
                .indent(["pass"])
            )

        # print get TODO: put a more meaningful message
        self.print(
            TextBlock(FlaskFiller._INDENT)
            .indent(['return "{0}", 200'])
            .format([endpoint])
        )

    def _write_api_files(self):
        for module, props in self.api.items():
            try:
                self.printer.open_file((self.flask_dir / props["filename"]))
                self.print(FlaskFiller._API_FILE_HEADER)
                self.print(FlaskFiller._BLUEPRINT_CREATE.format(module))
                self.print()  # newline
                for ep in props["endpoints"].items():
                    self._write_endpoint(*ep)
            except OSError:
                print("Error writing __init__.py")


class APIGenerator:
    """Given a config file that specifies the parameters of a barebones flask
    api, create a skeleton for its development.
    """

    SUPPORTED_MODES = {"api", "artifacts"}  # only public class constant
    _CONFIG_KEYS = {  # required keys in global table of toml file
        "name",
        "api",
        "python",
        "wsgi",
        "docker",
    }

    def __init__(self, config, workdir=None):
        # TODO: update instance variables to reflect access

        # will raise ValueError on bad config
        vet_config(config, APIGenerator._CONFIG_KEYS)

        # path specification
        self.config_file = config["file path"]
        self.base_dir = pathlib.Path.cwd()
        self.script = self.base_dir / config["wsgi"]["script"]
        self.dockerfile = self.base_dir / "Dockerfile"
        self.requirements = self.base_dir / "requirements.txt"
        self.work_dir = work_dir if work_dir is not None else self.base_dir
        self.flask_dir = self.work_dir / config["name"]

        # python waitress/gunicorn/flask
        self.api = config["api"]
        self.wsgi = config["wsgi"]
        self.dependencies = set(config["python"]["dependencies"])
        self.dependencies.add("flask")  # ensure that flask is in dependencies

        # docker
        self.docker = config["docker"]

        # writers
        self.printer = PRINTER  # all writes made are sync
        self.print = self.printer.print
        self.flask_filler = FlaskFiller(self.api, self.flask_dir)

        # state: not yet used
        self.env_setup = False
        self.complete = False

    # sole point of interface; only public method
    def do_task(self, task=None):
        match task:
            case "api":
                self._setup_dir_structure()  # persist to git
                self.do_task("flask")  # persist to git
            case "artifacts":
                self._setup_venv()  # .gitignore
                self.do_task("docker")  # persist to git
                self.do_task("script")  # .gitignore
            case "flask":
                self.flask_filler.fill()
            case "docker":
                self._write_dockerfile()
            case "script":
                self._write_executable()
            case "clean":
                pass
            case _:
                pass

    def _install_dependencies(self):
        # Assumes that subprocess will pick up whatever is in $env:COMSPEC to
        # use as the shell when shell=True on windows systems, and that this is
        # cmd.exe. Note that pathlib will format the file correctly regardless
        # of operating system.
        #
        # TODO: Analyze other production build scripts to see how they
        #       handle multiplatform installation.
        # might just replace this by writing a requirements file
        cmd_info = {
            "posix": {
                "source": "source ",  # notice space
                "path_to_activate": pathlib.Path(".venv/bin/activate"),
                "join on": "&&",
            },
            "nt": {
                "source": "",
                "path_to_activate": pathlib.Path(".venv/Scripts/activate.bat"),
                "join on": "&&",
            },
        }[os.name]

        # let any exception in subprocess.run propagate up to caller
        subprocess.run(
            cmd_info["join on"].join(
                [
                    f'{cmd_info["source"]}{cmd_info["path_to_activate"]}',
                    *[
                        f"python -m pip install {d}"
                        for d in list(self.dependencies)  # self.dep is a set
                    ],
                    "pip freeze >requirements.txt",
                    "deactivate",
                ]
            ),
            shell=True,
            check=True,
        )

    def _setup_venv(self):
        # make venv, will clobber existing one
        #
        # TODO: if venv is present, check for required dependencies
        #       if dependencies are present leave alone, if missing install
        try:
            subprocess.run(
                # sys.executable is the path of the interpreter used to
                # execute this script
                [sys.executable, "-m", "venv", ".venv"],
                check=True,  # raises exception on nonzero rc
            )
            self._install_dependencies()
        except subprocess.CalledProcessError:
            print(f"Couldn't make virtual environment in {self.base_dir}\n")

    def _setup_dir_structure(self):
        try:
            # dont allow overwrite
            self.flask_dir.mkdir(exist_ok=False)

            # make files
            (self.flask_dir / "__init__.py").touch()
            for _, props in self.api.items():
                (self.flask_dir / props["filename"]).touch()
        except OSError:  # could try out exception groups here
            print("Failed to create necessary directory structure")

    def _write_executable(self):
        # leave this func in case docker is not available
        try:
            # specify python interpreter in venv so that it doesnt need to be
            # activated
            venv_python = (
                self.base_dir
                / ".venv"
                / {
                    "posix": "bin/python",
                    "nt": "Scripts/python.exe",
                }[os.name]
            )

            if os.name == "nt":  # make it a py file so shebang can work
                self.script = self.script.with_suffix(".py")

            self.printer.open_file(self.script)
            self.print(
                TextBlock(indentation=" " * 2).write_lines(
                    [
                        f"#!{venv_python}",
                        "",
                        "import os",
                        "import pathlib",
                        "import sys",
                        "import waitress",
                        "",
                        f'sys.path.append(str(pathlib.Path("{self.work_dir.as_posix()}")))',
                        "",
                        f"import {self.flask_dir.name}.__init__ as app",
                        "",
                        'waitress.serve(app.factory("{0}"), host="{1}", port={2})'.format(
                            self.config_file.as_posix(),
                            self.wsgi["host"],
                            self.wsgi["port"],
                        ),
                    ]
                )
            )

            if os.name == "posix":  # need to make executable
                self.script.chmod(0o755)
        except Exception as e:
            print(f"Failed to write to {self.script}: {e}")

    def _write_dockerfile(self):
        try:
            # assumes all src code is present in parent folder to flask_dir
            self.printer.open_file(self.dockerfile)
            self.print(
                TextBlock().write_lines(
                    [
                        f'FROM {self.docker["image"]}',
                        f'WORKDIR {self.docker["workdir"]}',
                        f"COPY {self.config_file.name} requirements.txt ./",
                        "RUN pip install --no-cache-dir -r requirements.txt",
                        *[
                            f"COPY {e.relative_to(self.base_dir)} {e.name}/"
                            for e in self.flask_dir.parent.iterdir()
                            if e.is_dir()
                        ],
                        "CMD {}".format(
                            json.dumps(
                                [
                                    "gunicorn",
                                    "--bind",
                                    f'0.0.0.0:{self.wsgi["port"]}',
                                    f'{self.flask_dir.name}:factory("{self.config_file.name}")',
                                ]
                            )
                        ),
                        f'EXPOSE {self.wsgi["port"]}',
                    ]
                )
            )
        except:
            print(f"Failed to write to {self.dockerfile}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default="config.toml")
    parser.add_argument("-w", "--workdir", default=".")
    parser.add_argument("action", choices=APIGenerator.SUPPORTED_MODES)
    args = parser.parse_args()

    # get absolute paths ahead of directory switch, defaults set in args
    config = pathlib.Path(args.config).resolve()
    work_dir = pathlib.Path(args.workdir).resolve()

    APIGenerator(get_config(config), work_dir).do_task(args.action)

    # NOTE:
    # Functions/classes are, approximately, written in order of use. If there
    # is any interest in learning this program's operation, working from top
    # to bottom won't lead you astray. But to hit the sights see:
    #   get_config
    #   (then pass over, but do not spend too much time on:
    #       TextBlock
    #       Printer)
    #   ApiGenerator:
    #       __init__.py
    #       do_task <------------main entry point to program after init
    #
    # Also, don't bother trying to understand, from the code alone, any of the
    # writing operations and their gnarly string productions. Unless of course
    # you are already very familiar with flask apps and string concat/subst.
    # Instead, work backward from the contents of the files produced to the
    # functions that produce it.
