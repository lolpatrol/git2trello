# git2trello

Tools used:
- Git (git-hooks/bash)
- Trello
- Python

Forcing a user to link a commit to a task/an issue on Trello, to maintain traceability in the workflow.

## How can you accomplish this?

Probably in many really clever ways, but here's how I did it.

### git-hooks

Using `git-hooks` to trigger `python` script and other things.

#### prepare-commit-msg

Here I call the `python` script, which triggers a sequence of events leading up to the user to choosing a card available on a `Trello` board. The URL of the card is then appended to the commit message.

#### post-commit

Here the `git-hook` script first builds the `GitHub URL` where the commit will live after it has been pushed. The `python` script is again called, and the `GitHub URL` is passed into it, and then added as a comment to the previously chosen card on `Trello`.

### git_to_trello.py

The `python` script handles all things related to `Trello` (_yikes_). You can perform a "setup" by just running the script without arguments, and following the instructions to add `API-key` and generate a `token`, specifying project and its path, etc. During the setup, the script will also modify the two `git-hook`s in the specified project, so save your current ones if you want to keep them, consider this a warning :)

After a (successful) setup, you should be able to start working normally, not having to care about running anything else.


## TODO

- The current version requires a specific `board id` to collect cards from, so add that in the script.
    - I should probably fix this
- I probably handle `API-key`s and `token`s like a madman, so beware. But for personal use/testing, it should be fine (famous last words?).
    - Should look into this
- Pretty much zero error handling right now, very exciting.