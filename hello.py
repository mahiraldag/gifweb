from flask import Flask, send_file, abort, request, after_this_request
from flask import jsonify
from PIL import Image
import urllib3, threading, numpy, os.path, shortuuid, time, requests
app = Flask(__name__)

listOfImages = []
extractedImagesNumpyArr = []
width = 0
height = 0

def extractFrames(url):
    r = requests.get(url, stream=True)
    r.raw.decode_content = True  # handle spurious Content-Encoding
    frame = Image.open(r.raw)
    global width
    global height
    width = frame.size[0]
    height = frame.size[1]
    nframes = 0
    while frame:
        extractedImagesNumpyArr.append(numpy.array(frame.convert('RGBA')))
        nframes += 1
        try:
            frame.seek( nframes )
        except EOFError:
            break
    return nframes

def addProgressbarToExtractedFramesTop(nFrames, outFilename, r, g, b, thickness):
    for i in range(nFrames ):
        # frame = frame.convert("RGBA")
        frame = Image.fromarray(numpy.uint8(extractedImagesNumpyArr[i]))
        if i is not 0:
            for x_pixel in range(int(width / (nFrames - 1) * i )):
                for y_pixel in range(int(thickness)):
                    frame.putpixel((x_pixel, y_pixel), (int(r), int(g), int(b)))
        if i is nFrames - 1:
            for x_pixel in range(width):  # for every pixel:
                for y_pixel in range(int(thickness)):
                    frame.putpixel((x_pixel, y_pixel), (int(r), int(g), int(b)))

        listOfImages.append(frame)
    Image.new(mode='RGBA', size=(width, height)).save(outFilename, save_all=True, loop=0, append_images=listOfImages )

def addProgressbarToExtractedFramesBottom(nFrames, outFilename, r, g, b, thickness):
    for i in range(nFrames ):
        # frame = frame.convert("RGBA")
        frame = Image.fromarray(numpy.uint8(extractedImagesNumpyArr[i]))
        if i is not 0:
            for x_pixel in range(int(width / (nFrames - 1) * i )):
                for y_pixel in range(int(thickness)):
                    frame.putpixel((x_pixel, height - y_pixel - 1), (int(r), int(g), int(b)))
        if i is nFrames - 1:
            for x_pixel in range(width):  # for every pixel:
                for y_pixel in range(int(thickness)):
                    frame.putpixel((x_pixel, height - y_pixel - 1), (int(r), int(g), int(b)))

        listOfImages.append(frame)
    Image.new(mode='RGBA', size=(width, height)).save(outFilename, save_all=True, loop=0, append_images=listOfImages )


@app.route('/makegiffromurl')
def hello_world():
    url = request.args.get('url')
    r = request.args.get('r')
    g = request.args.get('g')
    b = request.args.get('b')
    position = request.args.get('position')
    tickness = request.args.get('thickness')
    id = shortuuid.uuid()
    nFrames = extractFrames(url)
    file_path = 'output/{id}.gif'.format(id=id)
    if position == 'top':
        addProgressbarToExtractedFramesTop(nFrames, file_path, r, g, b, tickness)
    if position == 'bottom':
        addProgressbarToExtractedFramesBottom(nFrames, file_path, r, g, b, tickness)
    listOfImages[:] = []
    extractedImagesNumpyArr[:] = []
    width = 0
    height = 0
    file_handle = open(file_path, 'r')
    # @after_this_request
    # def remove_file(response):
    #     os.remove(file_path)
    #     file_handle.close()
    #     return response
    return send_file(file_path, mimetype='image/gif')

@app.route('/')
def summary():
    return 'HelloWorld'

if __name__ == '__main__':
    app.run()