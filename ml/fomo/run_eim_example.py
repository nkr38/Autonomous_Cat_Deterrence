# FROM https://colab.research.google.com/github/edgeimpulse/notebooks/blob/main/notebooks/object-counting-using-fomo.ipynb#scrollTo=57dPBIW6Wwsv
# IF you get an error saying "model not executable"
# run chmod u+x modelfile.eim


import cv2
import os
import time
import sys, getopt
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner


modelfile = '/home/raspi/Autonomous_Cat_Deterrence/ml/fomo/models/catfomo2-linux-aarch64-v6-large.eim'
videofile = '/home/raspi/Autonomous_Cat_Deterrence/data/benchmark_vids/cat_counter5.mp4'


runner = None
# if you don't want to see a video preview, set this to False
show_camera = True
if (sys.platform == 'linux' and not os.environ.get('DISPLAY')):
    show_camera = False
print('MODEL: ' + modelfile)

with ImageImpulseRunner(modelfile) as runner:
    try:
        model_info = runner.init()
        print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
        labels = model_info['model_parameters']['labels']
        count = 0
        vidcap = cv2.VideoCapture(videofile)
        sec = 0
        start_time = time.time()

        def getFrame(sec):
            vidcap.set(cv2.CAP_PROP_POS_MSEC,sec*1000)
            hasFrames,image = vidcap.read()
            if hasFrames:
                return image
            else:
                print('Failed to load frame', videofile)
                exit(1)


        img = getFrame(sec)
        
    
        # Define the top of the image and the number of columns
        TOP_Y = 30
        NUM_COLS = 5
        COL_WIDTH = int(vidcap.get(3) / NUM_COLS)
        # Define the factor of the width/height which determines the threshold
        # for detection of the object's movement between frames:
        DETECT_FACTOR = 1.5

        # Initialize variables
        count = [0] * NUM_COLS
        countsum = 0
        previous_blobs = [[] for _ in range(NUM_COLS)]
        
        while img.size != 0:
            # imread returns images in BGR format, so we need to convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (172,172))

            # get_features_from_image also takes a crop direction arguments in case you don't have square images
            features, cropped = runner.get_features_from_image(img)
            img2 = cropped
            COL_WIDTH = int(np.shape(cropped)[0]/NUM_COLS)

            # the image will be resized and cropped, save a copy of the picture here
            # so you can see what's being passed into the classifier
            cv2.imwrite('debug.jpg', cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))

            res = runner.classify(features)
            # Initialize list of current blobs
            current_blobs = [[] for _ in range(NUM_COLS)]
            
            if "bounding_boxes" in res["result"].keys():
                print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                for bb in res["result"]["bounding_boxes"]:
                    print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                    img2 = cv2.rectangle(cropped, (bb['x'], bb['y']), (bb['x'] + bb['width'], bb['y'] + bb['height']), (255, 0, 0), 1)

                        # Check which column the blob is in
                    col = int(bb['x'] / COL_WIDTH)

                    # Check if blob is within DETECT_FACTOR*h of a blob detected in the previous frame and treat as the same object
                    for blob in previous_blobs[col]:
                        if abs(bb['x'] - blob[0]) < DETECT_FACTOR * (bb['width'] + blob[2]) and abs(bb['y'] - blob[1]) < DETECT_FACTOR * (bb['height'] + blob[3]):
                        # Check this blob has "moved" across the Y threshold
                            if blob[1] >= TOP_Y and bb['y'] < TOP_Y:
                                # Increment count for this column if blob has left the top of the image
                                count[col] += 1
                                countsum += 1
                    # Add current blob to list
                    current_blobs[col].append((bb['x'], bb['y'], bb['width'], bb['height']))



            # Update previous blobs
            previous_blobs = current_blobs

            if (show_camera):
                im2 = cv2.resize(img2, dsize=(800,800))
                cv2.putText(im2, f'{countsum} items passed', (15,750), cv2.FONT_HERSHEY_COMPLEX, 1, (0,255,0), 2)
                cv2.imshow('edgeimpulse', cv2.cvtColor(im2, cv2.COLOR_RGB2BGR))
                print(f'{count}')
                if cv2.waitKey(1) == ord('q'):
                    break

            sec = time.time() - start_time
            sec = round(sec, 2)
            # print("Getting frame at: %.2f sec" % sec)
            img = getFrame(sec)
    finally:
        if (runner):
            print(f'{countsum} Items Left Conveyorbelt')
            runner.stop()