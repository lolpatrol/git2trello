

def choose_card():
    board_id = ""  # Set this to something, automate in the future in some nice way :)))
    cards = Trello.boards.get_card(board_id=board_id)
    print("\nCards on board: ")
    for i, card in enumerate(cards):
        print(i, " : ", card['name'])
    print()
    chosen_card = int(input("Choose card on board: "))
    print()
    return cards[chosen_card]


def set_comment(card_id, commit_url):
    msg = "URL to commit on GitHub: "
    trello.Cards(API_key, token=token).new_action_comment(card_id, msg + commit_url)


def check_token():
    if os.path.exists(os.getcwd()+"\\token.txt"):  # Eh, not used anymore
        token = open(os.getcwd() + "\\token.txt").read()
        Trello.set_token(token)
        return token
    else:
        print("Either first time running this script, or you have removed your token.")
        proceed = input("To proceed you need to get a new new token. [Yy/Nn] ")
        if proceed in "Yy":
            token_url = Trello.get_token_url("git2trello", expires="", write_access=True)
            webbrowser.open(token_url)
            token = input("Paste your token: ")
            file = open("token.txt", "w+")
            file.write(token)
            file.close()
            Trello.set_token(token)
            return token
        else:
            print("Can't use tool without token.")
            return None


def token_set(info, project_name):
    if "token" in info[project_name].keys():
        return info[project_name]['token']
    else:
        return None


def load_info(project_name):
    info = {project_name: dict()}
    if os.path.exists(path + "\\g2t.pickle"):
        info = pickle.load(open(path + "\\g2t.pickle", "rb"))
        if project_name not in info.keys():
            info[project_name] = dict()
    return info


def setup_hooks(project_name, project_path):
    # Meh
    prepare_commit_msg = "#!/bin/bash\nPROJECT_NAME=\"" + project_name + "\"\nSCRIPT_PATH=\"" + path.replace("\\", "/") + "git_to_trello.py" + "\"\ncat > temp" \
        "\ncur=$(pwd)\"/temp\"\npython $SCRIPT_PATH $PROJECT_NAME \"pre\" \"$cur\" < /dev/tty\nTASK_URL=$(cat temp)\n" \
        "rm temp\nCOMMIT_MSG=\"Task: \"\necho \"$COMMIT_MSG$TASK_URL\" > \"$1\""

    post_commit = "#!/bin/bash\nPROJECT_NAME=\"" + project_name + "\"\nHASH=$(git rev-parse --verify HEAD)\n" \
        "REMOTE_URL=$(git config --get remote.origin.url)\nURL_LEN=${#REMOTE_URL}\n" \
        "REMOTE_NEW=${REMOTE_URL:0:`expr $URL_LEN - 4`}\nGITHUB_URL=$REMOTE_NEW\"/commit/\"$HASH\n" \
        "SCRIPT_PATH=\"" + path.replace("\\", "/") + "git_to_trello.py" + "\"\npython $SCRIPT_PATH $PROJECT_NAME \"post\" $GITHUB_URL"

    pcm = open(project_path / ".git/hooks/prepare-commit-msg", "w")
    pcm.write(prepare_commit_msg)
    pcm.close()

    pc = open(project_path / ".git/hooks/post-commit", "w")
    pc.write(post_commit)
    pc.close()


if __name__ == "__main__":
    import sys
    import os
    from pathlib import Path
    path = os.path.abspath(__file__)[:-16]
    sys.path.append(path + "venv\Lib\site-packages")
    import trello
    import webbrowser
    import pickle

    Trello = None

    args = len(sys.argv)
    if args == 1:  # HC SVNT DRACONES
        first = input("New project? [Yy/Nn]")
        if first in "Yy":
            project_name = input("Please enter project name: ")
            project_path = input("Please enter project path: ")
            project_path.replace("\\", "/")
            project_path = Path(project_path)
            setup_hooks(project_name, project_path)
            API_key = input("Enter API key associated with project board on Trello: ")
            g2t = load_info(project_name)
            g2t[project_name]['api_key'] = API_key
            token = token_set(g2t, project_name)
            Trello = trello.TrelloApi(API_key)
            if not token:
                token_url = Trello.get_token_url("g2t", "", write_access=True)
                token = input("Please enter the token: ")
                Trello.set_token(token)
                webbrowser.open(token_url)
                g2t[project_name]['token'] = token
            g2t[project_name]['Trello'] = Trello
            pickle.dump(g2t, open(path+"\\g2t.pickle", "wb"))
        sys.exit(0)

    project_name = sys.argv[1]
    g2t = load_info(project_name)
    Trello = g2t[project_name]['Trello']
    API_key = g2t[project_name]['api_key']
    token = g2t[project_name]['token']

    if sys.argv[2] == "pre":
        card = choose_card()
        g2t[project_name]['card_id'] = card['id']
        pickle.dump(g2t, open(path + "\\g2t.pickle", "wb"))
        t = open(sys.argv[3], "w")
        t.write(card['url'])
        t.close()
        print(card['url'])
        sys.exit(0)
    elif sys.argv[2] == "post":
        commit_url = sys.argv[3]
        card_id = g2t[project_name]['card_id']
        set_comment(card_id, commit_url)

