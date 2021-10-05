import json
import shlex
import subprocess
import sys

config = {
    "noCommands": False,
    "noConfirm": False
}


def run_command(cmd: list, confirm_prompt: str):
    print("> " + shlex.join(cmd))
    if not config["noCommands"] and (config["noConfirm"] or confirmation(confirm_prompt)):
        subprocess.call(cmd)


def confirmation(prompt: str = "Confirm? ") -> bool:
    return input(prompt).strip().lower() in ["yes", "y", "ja", "j"]


def build_command(docker_cmd: str, name: str, environment_vars: dict, volumes: dict, ports: dict, image: str) -> list:
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


def main() -> int:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <template-name> [OPTIONS]")
        print("Options:")
        print("  --dry, -s           Don't execute commands")
        print("  --no-confirm, -y    Execute commands without confirmation")
        return 1

    for arg in sys.argv[2:]:
        if arg in ["--dry", "-s"]:
            config["noCommands"] = True
        elif arg in ["--no-confirm", "-y"]:
            config["noConfirm"] = True

    template_name = sys.argv[1]

    with open("docker-setup.json") as f:
        data = json.loads(f.read())

    docker_cmd = data.get("$docker_cmd", "docker")

    if template_name not in data:
        print(f"{sys.argv[0]}: invalid template name: \"{template_name}\"")
        return 1

    template = data[template_name]

    arguments = prompt_arguments(template.get("arguments", {}))
    volumes = format_string_dict(template.get("volumes", {}), values=False, **arguments)
    environment_vars = format_string_dict(template.get("environment", {}), keys=False, **arguments)
    ports = format_string_dict(template.get("ports", {}), **arguments)
    name = template["name"].format(**arguments)
    image = template["image"]

    for volume in volumes:
        run_command([docker_cmd, "volume", "create", volume], f"Create Volume {volume}? ")

    cmd = build_command(docker_cmd, name, environment_vars, volumes, ports, image)
    run_command(cmd, f"Create Container {name}? ")
    return 0


if __name__ == '__main__':
    code = 1
    try:
        code = main()
    except KeyboardInterrupt:
        code = 0
    except KeyError as e:
        print(f"error getting config key: {e.args[0]}")
        code = 1
    if code == 0:
        print("\nThank you for using docker-setup.py")
    exit(code)
