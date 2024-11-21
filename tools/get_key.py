from subprocess import run

def get_key(env_var):
    key = run(
        ['cmd.exe', '/c', f'echo %{env_var}%'],
        capture_output=True,
        text=True
    ).stdout.strip()
    return key