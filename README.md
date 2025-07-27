# espanso-llm-ask-ai

An Espanso package that enables users to quickly send prompts to a local (e.g. Ollama or LM Studio) or remote LLM API calls (OpenAI standard) and insert the AI-generated response directly into any text field.

## Requirements

- [Espanso](https://espanso.org/) installed and running
- Python 3.9+ installed and available on your system path
- Required Python packages: `openai` and `python-dotenv` (see `requirements.txt`)
- Access to a local LLM (such as [Ollama](https://ollama.com/) or [LM Studio](https://lmstudio.ai/)) or a remote OpenAI compatible API (in this case, you will need to provide your API key in the `.env` file)

## Configuration

Edit the `.env` environment file inside the package directory () to set the `API_KEY`, `BASE_URL`and `MODEL`. Example:

```bash
API_KEY=ollama
BASE_URL=http://localhost:11434/v1
MODEL=llama3.2
```

> NOTE: don't forget to pull the Ollama model first. In the case above, just issue the command:
>
> `ollama pull llama3.2`

## Usage

- Type the Espanso trigger for this package (`:ask:ai`) in any text field.
- Enter your desired AI prompt when asked.
- The AI-generated response will be inserted automatically (this can take several seconds, so choose a small and low latency LLM model).

### Example

Type:

```
:ask:ai
```

Then enter:

```
Summarize the following text: ...
```

Press the "Submit" button or "CTRL + Enter" to send the request. The response from your configured LLM will appear in place.

## Troubleshooting

- Make sure Python is available globally on your system's PATH environment variable and that the required packages are installed.
- Check that your BASE_URL endpoint, MODEL and API_KEY are correctly set in the `.env` file (located in the Espanso config directory: `%CONFIG%/match/packages/espanso-llm-ask-ai/.env`).
- After sending the request, make sure the cursor doesn’t lose focus and remains blinking at the correct insertion point. If it doesn’t, just click to place it right after the trigger string like this **:ask:ai|**
- Review Espanso logs for errors.

## License

MIT

## Author

Bernhard Enders

## Links

- [Homepage](https://github.com/bgeneto/espanso-llm-ask-ai)
- [Espanso Documentation](https://espanso.org/docs/)

灵感来源：
<https://github.com/bgeneto/espanso-llm-ask-ai>
<https://github.com/MichielvanBeers/Flow.Launcher.Plugin.ChatGPT>

[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0iI2ZmZiIgZD0iTTE3IDE2VjdsLTYgNU0yIDlWOGwxLTFoMWw0IDMgOC04aDFsNCAyIDEgMXYxNGwtMSAxLTQgMmgtMWwtOC04LTQgM0gzbC0xLTF2LTFsMy0zIi8+PC9zdmc+)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/ChuckieChen945/espanso-llm-quick-translate) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new/ChuckieChen945/espanso-llm-quick-translate)

# espanso-llm-quick-translate

An Espanso package that enables users to quickly translate text using a local (e.g. Ollama or LM Studio) or remote LLM API (OpenAI-compatible), and insert the translated result directly into any text field.

## Installing

To install this package, run:

```sh
pip install espanso-llm-quick-translate
```

## Using

To view the CLI help information, run:

```sh
espanso-llm-quick-translate --help
```

## Contributing

<details>
<summary>Prerequisites</summary>

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:

    ```sh
    cat << EOF >> ~/.ssh/config
    
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
      ForwardAgent yes
    EOF
    ```

1. [Install Docker Desktop](https://www.docker.com/get-started).
1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
1. _Optional:_ install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use it.

</details>

<details open>
<summary>Development environments</summary>

The following development environments are supported:

1. ⭐️ _GitHub Codespaces_: click on [Open in GitHub Codespaces](https://github.com/codespaces/new/ChuckieChen945/espanso-llm-quick-translate) to start developing in your browser.
1. ⭐️ _VS Code Dev Container (with container volume)_: click on [Open in Dev Containers](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/ChuckieChen945/espanso-llm-quick-translate) to clone this repository in a container volume and create a Dev Container with VS Code.
1. ⭐️ _uv_: clone this repository and run the following from root of the repository:

    ```sh
    # Create and install a virtual environment
    uv sync --python 3.12 --all-extras

    # Activate the virtual environment
    source .venv/bin/activate

    # Install the pre-commit hooks
    pre-commit install --install-hooks
    ```

1. _VS Code Dev Container_: clone this repository, open it with VS Code, and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Dev Containers: Reopen in Container_.
1. _PyCharm Dev Container_: clone this repository, open it with PyCharm, [create a Dev Container with Mount Sources](https://www.jetbrains.com/help/pycharm/start-dev-container-inside-ide.html), and [configure an existing Python interpreter](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#widget) at `/opt/venv/bin/python`.

</details>

<details open>
<summary>Developing</summary>

- This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
- Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
- Run `uv add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `uv.lock`. Add `--dev` to install a development dependency.
- Run `uv sync --upgrade` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`. Add `--only-dev` to upgrade the development dependencies only.
- Run `cz bump` to bump the app's version, update the `CHANGELOG.md`, and create a git tag. Then push the changes and the git tag with `git push origin main --tags`.

</details>
