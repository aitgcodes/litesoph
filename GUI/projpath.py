from pathlib import Path

def create_path(projpath,projname):
    path = Path(projpath)

    newpath = path / str(projname)

    Path.mkdir(newpath)

    try:
        newpath.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        print("Folder is created")
    else:
        print("Folder already exist")

