def rewrite_author(commit):
    if commit.author_name == b"Cursor Agent":
        commit.author_name = b"Rav Kohli"
        commit.author_email = b"rav.kohli@live.co.uk"
    if commit.committer_name == b"Cursor Agent":
        commit.committer_name = b"Rav Kohli"
        commit.committer_email = b"rav.kohli@live.co.uk" 