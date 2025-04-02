import re
import functools
import hashlib
import warnings
import subprocess
from os import PathLike
from pathlib import Path


def _get_sha256_hash(file_path: str | Path) -> str:
    """Calculate the 256-bit SHA checksum of a file.

    Parameters
    ----------
    file_path: Path
       Path to the file whose checksum is to be calculated

    Returns
    -------
    file_hash: str
       The SHA-256 checksum of the file at file_path
    """

    file_path = Path(file_path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Error when calculating file hash: {file_path} is not a valid file"
        )

    sha256_hash = hashlib.sha256()
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            sha256_hash.update(chunk)

    file_hash = sha256_hash.hexdigest()
    return file_hash


def _update_user_dotenv(env_file_str) -> None:
    print("Updating environment in C-Star configuration file ~/.cstar.env")
    env_file = Path("~/.cstar.env").expanduser()
    if not env_file.exists():
        print(f"Updating environment in C-Star configuration file {env_file}")
        base_env_str = (
            "# This file was generated by C-Star and is specific to your machine. "
            + "# It contains environment information related to your cases & their dependencies. "
            + "# You can safely delete this file, but C-Star may prompt you to re-install things if so."
        )
        env_file_str = base_env_str + "\n" + env_file_str

    with open(Path("~/.cstar.env").expanduser(), "a") as F:
        F.write(env_file_str)


def _clone_and_checkout(
    source_repo: str, local_path: str | Path, checkout_target: str
) -> None:
    """Clone `source_repo` to `local_path` and checkout `checkout_target`."""
    clone_result = subprocess.run(
        f"git clone {source_repo} {local_path}",
        shell=True,
        capture_output=True,
        text=True,
    )
    if clone_result.returncode != 0:
        raise RuntimeError(
            f"Error {clone_result.returncode} when cloning repository "
            + f"{source_repo} to {local_path}. Error messages: "
            + f"\n{clone_result.stderr}"
        )
    print(f"Cloned repository {source_repo} to {local_path}")

    checkout_result = subprocess.run(
        f"git checkout {checkout_target}",
        cwd=local_path,
        shell=True,
        capture_output=True,
        text=True,
    )
    if checkout_result.returncode != 0:
        raise RuntimeError(
            f"Error {checkout_result.returncode} when checking out "
            + f"{checkout_target} in git repository {local_path}. Error messages: "
            + f"\n{checkout_result.stderr}"
        )
    print(f"Checked out {checkout_target} in git repository {local_path}")


def _get_repo_remote(local_root: str | Path) -> str:
    """Take a local repository path string (local_root) and return as a string the
    remote URL."""
    return subprocess.run(
        f"git -C {local_root} remote get-url origin",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _get_repo_head_hash(local_root: str | Path) -> str:
    """Take a local repository path string (local_root) and return as a string the
    commit hash of HEAD."""
    return subprocess.run(
        f"git -C {local_root} rev-parse HEAD",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _get_hash_from_checkout_target(repo_url: str, checkout_target: str) -> str:
    """Take a git checkout target (any `arg` accepted by `git checkout arg`) and return
    a commit hash.

    This method parses the output of `git ls-remote {repo_url}` to create a dictionary
    of refs and hashes, returning the hash corresponding to `checkout_target` or
    raising an error listing available branches and tags if the target is not found.

    Parameters:
    -----------
    repo_url: str
        URL pointing to a git-controlled repository
    checkout_target: str
        Any valid argument that can be supplied to `git checkout`

    Returns:
    --------
    git_hash: str
        A git commit hash associated with the checkout target
    """

    # Get list of targets from git ls-remote
    ls_remote = subprocess.run(
        f"git ls-remote {repo_url}",
        shell=True,
        capture_output=True,
        text=True,
    ).stdout

    # Process the output into a `reference: hash` dictionary
    ref_dict = {
        ref: has for has, ref in (line.split() for line in ls_remote.splitlines())
    }

    # If the checkout target is a valid hash, return it
    if checkout_target in ref_dict.values():
        return checkout_target

    # Otherwise, see if it is listed as a branch or tag
    for ref, has in ref_dict.items():
        if (
            ref == f"refs/heads/{checkout_target}"
            or ref == f"refs/tags/{checkout_target}"
        ):
            return has

    # Lastly, if NOTA worked, see if the checkout target is a 7 or 40 digit hexadecimal string
    is_potential_hash = bool(re.fullmatch(r"^[0-9a-f]{7}$", checkout_target)) or bool(
        re.fullmatch(r"^[0-9a-f]{40}$", checkout_target)
    )
    if is_potential_hash:
        warnings.warn(
            f"C-STAR: The checkout target {checkout_target} appears to be a commit hash, "
            f"but it is not possible to verify that this hash is a valid checkout target of {repo_url}"
        )

        return checkout_target

    # If the target is still not found, raise an error listing branches and tags
    branches = [
        ref.replace("refs/heads/", "")
        for ref in ref_dict
        if ref.startswith("refs/heads/")
    ]
    tags = [
        ref.replace("refs/tags/", "")
        for ref in ref_dict
        if ref.startswith("refs/tags/")
    ]

    error_message = (
        f"Supplied checkout_target ({checkout_target}) does not appear "
        f"to be a valid reference for this repository ({repo_url}).\n"
    )
    if branches:
        error_message += (
            "Available branches:\n"
            + "\n".join(f" - {branch}" for branch in sorted(branches))
            + "\n"
        )
    if tags:
        error_message += (
            "Available tags:\n" + "\n".join(f" - {tag}" for tag in sorted(tags)) + "\n"
        )

    raise ValueError(error_message.strip())


def _replace_text_in_file(file_path: str | Path, old_text: str, new_text: str) -> bool:
    """Find and replace a string in a text file.

    This function creates a temporary file where the changes are written, then
    overwrites the original file.

    Parameters:
    -----------
    file_path: str | Path
        The local path to the text file
    old_text: str
        The text to be replaced
    new_text: str
        The text that will replace `old_text`

    Returns:
    --------
    text_replaced: bool
       True if text was found and replaced, False if not found
    """
    text_replaced = False
    file_path = Path(file_path).resolve()
    temp_file_path = Path(str(file_path) + ".tmp")

    with open(file_path, "r") as read_file, open(temp_file_path, "w") as write_file:
        for line in read_file:
            if old_text in line:
                text_replaced = True
            new_line = line.replace(old_text, new_text)
            write_file.write(new_line)

    temp_file_path.rename(file_path)

    return text_replaced


def _list_to_concise_str(
    input_list, item_threshold=4, pad=16, items_are_strs=True, show_item_count=True
):
    """Take a list and return a concise string representation of it.

    Parameters:
    -----------
    input_list (list of str):
       The list of to be represented
    item_threshold (int, default = 4):
       The number of items beyond which to truncate the str to item0,...itemN
    pad (int, default = 16):
       The number of whitespace characters to prepend newlines with
    items_are_strs (bool, default = True):
       Will use repr formatting ([item1,item2]->['item1','item2']) for lists of strings
    show_item_count (bool, default = True):
       Will add <N items> to the end of a truncated representation

    Returns:
    -------
    list_str: str
       The string representation of the list

    Examples:
    --------
    In: print("my_list: "+_list_to_concise_str(["myitem0","myitem1",
                             "myitem2","myitem3","myitem4"],pad=11))
    my_list: ['myitem0',
              'myitem1',
                  ...
              'myitem4']<5 items>
    """
    list_str = ""
    pad_str = " " * pad
    if show_item_count:
        count_str = f"<{len(input_list)} items>"
    else:
        count_str = ""
    if len(input_list) > item_threshold:
        list_str += f"[{repr(input_list[0]) if items_are_strs else input_list[0]},"
        list_str += (
            f"\n{pad_str}{repr(input_list[1]) if items_are_strs else input_list[1]},"
        )
        list_str += f"\n{pad_str}   ..."
        list_str += f"\n{pad_str}{repr(input_list[-1]) if items_are_strs else input_list[-1]}] {count_str}"
    else:
        list_str += "["
        list_str += f",\n{pad_str}".join(
            (repr(listitem) if items_are_strs else listitem) for listitem in input_list
        )
        list_str += "]"
    return list_str


def _dict_to_tree(input_dict: dict, prefix: str = "") -> str:
    """Recursively converts a dictionary into a tree-like string representation.

    Parameters:
    -----------
     input_dict (dict):
        The dictionary to convert. Takes the form of nested dictionaries with a list
        at the lowest level
    prefix (str, default=""):
        Used for internal recursion to maintain current branch position

    Returns:
    --------
    tree_str:
       A string representing the tree structure.

    Examples:
    ---------
    print(_dict_to_tree({'branch1': {'branch1a': ['twig1ai','twig1aii']},
                         'branch2': {'branch2a': ['twig2ai','twig2aii'],
                                     'branch2b': ['twig2bi',]}
                 }))

    ├── branch1
    │   └── branch1a
    │       ├── twig1ai
    │       └── twig1aii
    └── branch2
        ├── branch2a
        │   ├── twig2ai
        │   └── twig2aii
        └── branch2b
            └── twig2bi
    """
    tree_str = ""
    keys = list(input_dict.keys())

    for i, key in enumerate(keys):
        # Determine if this is the last key at this level
        branch = "└── " if i == len(keys) - 1 else "├── "
        sub_prefix = "    " if i == len(keys) - 1 else "│   "

        # If the value is a dictionary, recurse into it
        if isinstance(input_dict[key], dict):
            tree_str += f"{prefix}{branch}{key}\n"
            tree_str += _dict_to_tree(input_dict[key], prefix + sub_prefix)
        # If the value is a list, print each item in the list
        elif isinstance(input_dict[key], list):
            tree_str += f"{prefix}{branch}{key}\n"
            for j, item in enumerate(input_dict[key]):
                item_branch = "└── " if j == len(input_dict[key]) - 1 else "├── "
                tree_str += f"{prefix}{sub_prefix}{item_branch}{item}\n"

    return tree_str


def _run_cmd(
    cmd: str,
    cwd: PathLike | None = None,
    env: dict[str, str] | None = None,
    msg_pre: str | None = None,
    msg_post: str | None = None,
    msg_err: str | None = None,
    raise_on_error: bool = False,
) -> str:
    """Execute a subprocess using default configuration, blocking until it completes.

    Parameters:
    -----------
    cmd (str):
       The command to be executed as a separate process.
    cwd (PathLike, default = None):
       The working directory for the command. If None, use current working directory.
    env (Dict[str, str], default = None):
       A dictionary of environment variables to be passed to the command.
    msg_pre (str  | None), default = None):
       An overridden message logged before the command is executed.
    msg_post (str | None), default = None):
        An overridden message logged after the command is successfully executed.
    msg_err (str | None), default = None):
        An overridden message logged when a command returns a non-zero code.
    raise_on_error (bool, default = False):
        If True, raises a RuntimeError if the command returns a non-zero code.

    Returns:
    -------
    stdout: str
       The captured standard output of the process.

    Examples:
    --------
    In: _execute_cmd("python foo.py", "Running script", "Script completed")
    Out: Running script
         Script completed

    In: _execute_cmd("python foo.py")
    Out: Running command: python foo.py
         Command completed successfully. STDOUT: <output of foo.py>

    In: _execute_cmd("python return_nonzero.py")
    Out: Running command: python return_nonzero.py
         Command python return_nonzero.py failed: <stderror of foo.py>
    """
    print(msg_pre or f"Running command: {cmd}")
    stdout: str = ""

    fn = functools.partial(
        subprocess.run,
        cmd,
        shell=True,
        text=True,
        capture_output=True,
    )

    kwargs: dict[str, str | PathLike | dict[str, str]] = {}
    if cwd:
        kwargs["cwd"] = cwd
    if env:
        kwargs["env"] = env

    result: subprocess.CompletedProcess[str] = fn(**kwargs)
    stdout = str(result.stdout).strip() if result.stdout is not None else ""

    if result.returncode != 0:
        if msg_err:
            msg = msg_err.format(result=result)
        else:
            msg = f"Command `{cmd}` failed: {result.stderr.strip()}"

        if raise_on_error:
            raise RuntimeError(msg)

        print(msg)

    print(msg_post or f"Command completed successfully. STDOUT: {result.stdout}")
    return stdout
