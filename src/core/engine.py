
import os
import importlib
from shlex import split

class Engine:

    commands    =   {}
    aliases     =   {}
    completion  =   {}

    def __init__(self) -> None:
        ...

    def process(self, stdin: str) -> str:
        args = split(stdin)

        if args == []:
            return None
        
        pipeline = self._build_pipeline(args)
        stdout = self._process_pipeline(pipeline)

        return stdout

    def _build_pipeline(self, args: list) -> list:
        pipeline    =   []
        pipe        =   []

        for arg in args:
            if arg != "|":
                pipe.append(arg)
            else:
                pipeline.append(pipe)
                pipe = []
        
        pipeline.append(pipe)
        
        return pipeline

    def _process_pipeline(self, pipeline: list) -> list:
        stdout = None

        for pipe in pipeline:
            if pipe is not None:
                pipe.append(stdout)
            
            stdout = self._parse(pipe)
        
        return stdout

    def _parse(self, pipe: list) -> str:
        if pipe[0] in Engine.aliases:
            pipe = Engine.aliases[pipe[0]].split() + pipe[1:]   
        elif pipe[0] in Engine.commands:
            return self.run_command(pipe)       
        else:
            try:
                return self.run_python(" ".join(pipe))
            except Exception as e:
                print(e)
                return None

    def run_python(self, line: str) -> any:
        try:
            compile(line, '<stdin>', 'eval') # compile python with eval
        except SyntaxError as e: # if syntax error: either can't eval or not python syntax
            print(e)
            return exec # try exec python statement
        
        return eval # eval python expression

    def run_command(self, args: list) -> any:
        command = importlib.import_module(Engine.commands[args[0]])
        command = command.Command()

        if len(args) == 1:
            try:
                return command.default()
            except TypeError as e:
                try:
                    return command.default("")
                except Exception as e:
                    print(e)
        elif len(args) >= 2 and command.subcommands == {}:
            if args[1] == "help":
                return command.help()
            else:
                return command.default(*args[1:])
        elif len(args) >= 2 and command.subcommands != {}:
            try:
                if args[1] == "help":
                    return command.help()
                else:
                    return command.subcommands[args[1]](*args[2:])
            except TypeError as e:
                error = str(e).split()[1:]
                message = f"'{' '.join(args)}' {' '.join(error)}"
                return message
            except KeyError as e:
                try:
                    return command.default(*args[1:])
                except Exception as e:
                    return command.help()
        else:
            return args

    # def load_aliases(self) -> None:
    #     for key, value in alias.list_full():
    #         Engine.aliases[key] = value

    def load_commands(self) -> None:
        for name in os.listdir("commands"):
            path = f"commands/{name}"
            
            if os.path.isdir(path) and not name.startswith("__"):
                if os.path.isfile(f"{path}/{name}.py"):
                    path = f"{path}/{name}.py"
                    name = f"{name}.py"

            if os.path.isfile(path):
                basename = os.path.basename(path)
                base, extension = os.path.splitext(path)
                if extension == ".py" and not basename.startswith("_"):
                    Engine.commands[name[:-3]] = base.replace("/", ".")

    def load_completion(self) -> None:
        for name in Engine.commands:
            Engine.completion[name] = {}
            command = importlib.import_module(Engine.commands[name])
            command = command.Command()

            subcommands = Engine.completion[name]
            if hasattr(command, 'subcommands'):
                for subcommand in command.subcommands:
                    if subcommand != "default":
                        if hasattr(command, f"{subcommand}_completion"):
                            subcommands[subcommand] = getattr(command, f"{subcommand}_completion")
                        else:
                            subcommands[subcommand] = None
            
            subcommands["help"] = None # add a subcommand for help to all commands
            Engine.completion[name] = subcommands

            # add a list of all commands to the completion list for the help command
            if name == "help":
                help = Engine.completion[name]
                for name in Engine.commands:
                    help[name] = None

    def load(self) -> None:
        # config.load()
        # alias.load()
        # history.load()
        # session.load()
        self.load_aliases()
        self.load_commands()
        self.load_completion()

    def exit(self) -> None:
        # config.save()
        # alias.save()
        # history.save()
        # session.save()
        ...