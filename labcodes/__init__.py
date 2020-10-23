import git
import time

def print_version_report(path):
    """ """
    # import pdb; pdb.set_trace()  # noqa BREAKPOINT
    git_repo = git.Repo(path, search_parent_directories=True)
    git_root = git_repo.git.rev_parse("--show-toplevel")

    print("Git root: ", git_root)
    print("last commit: ", time.asctime(time.localtime(git_repo.head.commit.committed_date)), ", ", git_repo.head.commit.hexsha)
    print("message: ", git_repo.head.commit.message)



print_version_report(__file__)
