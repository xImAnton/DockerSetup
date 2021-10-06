def confirmation(prompt: str = "Confirm? ") -> bool:
    return input(prompt).strip().lower() in ["yes", "y", "ja", "j"]


def build_container_command(docker_cmd: str, name: str, environment_vars: dict, volumes: dict, ports: dict, image: str) -> list:
    command = [docker_cmd, "run", "--name", name, "-d"]
    for key, val in environment_vars.items():
        command.append("-e")
        command.append(f"{key}={val}")

    for name, mnt in volumes.items():
        command.append("-v")
        command.append(f"{name}:{mnt}")

    for host, cont in ports.items():
        command.append("-p")
        command.append(f"{host}:{cont}")

    command.append(image)
    return command


def format_string_dict(d: dict, keys: bool = True, values: bool = True, **formats) -> dict:
    out = {}
    for key, val in d.items():
        if keys:
            key = key.format(**formats)
        if values:
            val = val.format(**formats)
        out[key] = val
    return out


def prompt_arguments(argument_config: dict) -> dict:
    arguments = {}
    for arg, data in argument_config.items():
        key = arg
        desc = None
        default = None

        if isinstance(data, str):
            desc = data
        if isinstance(data, dict):
            key = data.get("placeholder", arg)
            desc = data.get("description", None)
            default = data.get("default", None)

        prompt = desc or key
        prompt += ": "
        if default:
            prompt += f"({default}) "

        do = True
        while do:
            value = input(prompt.format(**arguments)).strip()
            if value == "" and default is not None:
                value = default.format(**arguments)
            do = value == ""
        arguments[arg] = value
    return arguments
