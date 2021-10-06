import json
import shlex
import subprocess
import sys
from util import confirmation, build_container_command, format_string_dict, prompt_arguments


_config = {
    "no_commands": False,
    "no_confirm": False,
    "list_and_exit": False
}


def run_command(cmd: list, confirm_prompt: str):
    print("> " + shlex.join(cmd))
    if not _config["no_commands"] and (_config["no_confirm"] or confirmation(confirm_prompt)):
        subprocess.call(cmd)


usage_info = f"Usage: {sys.argv[0]} <template-name> [OPTIONS]\nOptions:\n  --dry, -s           Don't execute commands\n  --no-confirm, -y    Execute commands without confirmation"


def main() -> int:
    if len(sys.argv) < 2:
        print(usage_info)
        return 1

    template_name = None

    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            template_name = arg
        if arg in ["--dry", "-s"]:
            _config["no_commands"] = True
        elif arg in ["--no-confirm", "-y"]:
            _config["no_confirm"] = True
        elif arg in ["-l", "--list"]:
            _config["list_and_exit"] = True

    with open("docker-setup.json") as f:
        data = json.loads(f.read())

    if _config["list_and_exit"]:
        templates = {t for t in data.keys() if not t.startswith("$")}
        print("\n".join(templates))
        return 0

    if template_name is None:
        print(usage_info)
        return 1

    docker_cmd = data.get("$docker_cmd", "docker")

    if template_name not in data:
        print(f"{sys.argv[0]}: invalid template name: \"{template_name}\"")
        return 1

    template = data[template_name]

    arguments = prompt_arguments(template.get("arguments", {}))
    print("")
    volumes = format_string_dict(template.get("volumes", {}), values=False, **arguments)
    environment_vars = format_string_dict(template.get("environment", {}), keys=False, **arguments)
    ports = format_string_dict(template.get("ports", {}), **arguments)

    name = template["name"].format(**arguments)
    image = template["image"]

    for volume in volumes:
        run_command([docker_cmd, "volume", "create", volume], f"Create volume {volume}? [y/n] ")
    print("")
    cmd = build_container_command(docker_cmd, name, environment_vars, volumes, ports, image)
    run_command(cmd, f"Create container {name}? [y/n] ")
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
    sys.exit(code)
