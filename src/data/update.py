import os
import shutil


def update_raw_data():
    os.chdir("../../data")
    if os.path.exists("raw"):
        shutil.rmtree("raw")
    print('Updating fpl data...')
    os.system("svn export https://github.com/vaastav/Fantasy-Premier-League/trunk/data")
    os.system("mv data raw")


if __name__ == '__main__':
    update_raw_data()
