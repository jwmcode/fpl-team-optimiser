import os
import shutil


def update_vastaav_data():
    os.chdir("../../data")
    if os.path.exists("vastaav_data"):
        shutil.rmtree("vastaav_data")
    os.system("svn export https://github.com/vaastav/Fantasy-Premier-League/trunk/data")
    os.system("mv data vastaav_data")