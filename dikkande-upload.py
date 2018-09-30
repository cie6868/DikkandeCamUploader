import sys
import os
import time
import hashlib
import requests

class DikkandeUploader():

    BUFFER_SIZE = 65536

    def __init__(self, dir, endpoint):
        self.dir = dir
        self.endpoint = endpoint

    def watch(self):
        try:
            while True:
                self.walk()
                time.sleep(10);
        except KeyboardInterrupt:
            return

    def walk(self):
        files = []
        for (dirpath, dirnames, filenames) in os.walk(self.dir):
            files.extend(filenames)

        for file in files:
            filepath = os.path.join(dir, file)
            splitfile = os.path.splitext(file)

            # ignore files with no extension
            if len(splitfile) < 2:
                continue

            print('Processing ' + splitfile[0] + splitfile[1] + '...')

            videopath = False
            imagepath = False
            if splitfile[1] == '.mp4':
                videopath = filepath
                x = os.path.join(dir, splitfile[0] + '.jpg')
                if os.path.isfile(x):
                    imagepath = x
                    print('- image found')
                else:
                    print('- video only')
            elif splitfile[1] == '.jpg':
                imagepath = filepath
                x = os.path.join(dir, splitfile[0] + '.mp4')
                if os.path.isfile(x):
                    videopath = x
                    print('- video found')
                else:
                    print('- image only')
            else:
                # ignore files that are wrong type
                print('- invalid file type')
                continue

            if self.upload(splitfile[0], video = videopath, image = imagepath):
                print('- deleting');
                if videopath:
                    os.remove(videopath)
                if imagepath:
                    os.remove(imagepath)

            print('- done')

    def upload(self, name, video = False, image = False):
        print('- uploading')

        data = { 'name': name, hash: {} }
        files = {}

        if video:
            data['video_hash'] = self.hash(video)
            files['video'] = open(video, 'rb')
        if image:
            data['image_hash'] = self.hash(image)
            files['image'] = open(image, 'rb')

        response = requests.post(
            url = self.endpoint,
            data = data,
            files = files
        )

        if response.status_code != 200:
            print('- server is not happy (' + str(response.status_code) + ')')
            return False

        return response.json()['status'] == '1'

    def hash(self, file):
        sha = hashlib.sha1()
        with open(file, 'rb') as fd:
            while True:
                data = fd.read(self.BUFFER_SIZE)
                if not data:
                    break
                sha.update(data)
        return sha.hexdigest()


if __name__ == '__main__':
    dir = sys.argv[1]
    endpoint = sys.argv[2]
    dikk = DikkandeUploader(dir, endpoint)
    dikk.watch()
