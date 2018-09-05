import numpy as np
import cv2
import imageio
import tensorflow as tf

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import object_detection.object_detector as obj

def test_local_image():

    main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
    obj_detection_graph =  os.path.join(main_folder_path, 'object_detection/weights/batched_zoo/faster_rcnn_nas_coco_2018_01_28/batched_graph/frozen_inference_graph.pb')

    print("Loading object detection model at %s" % obj_detection_graph)

    Obj_Detector = obj.Object_Detector(obj_detection_graph)

    test_img_path = 'chase.png'
    print('Testing on %s' % test_img_path)
    test_img = cv2.imread(test_img_path)
    expanded_img = np.expand_dims(test_img, axis=0)
    detection_list = Obj_Detector.detect_objects_in_np(expanded_img)
    out_img = visualize_results(test_img, detection_list, display=False)
    #import pdb;pdb.set_trace()
    out_img_path = 'chase_out.jpg' 
    cv2.imwrite(out_img_path, out_img)
    print("Output image %s written!" % out_img_path)
    
def test_local_video():
    main_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
    obj_detection_graph =  os.path.join(main_folder_path, 'object_detection/weights/batched_zoo/faster_rcnn_nas_coco_2018_01_28/batched_graph/frozen_inference_graph.pb')

    print("Loading object detection model at %s" % obj_detection_graph)

    Obj_Detector = obj.Object_Detector(obj_detection_graph)

    test_vid_path = "chase1Person1View3Point0.mp4"
    print('Testing on %s' % test_vid_path)

    reader = imageio.get_reader(test_vid_path, 'ffmpeg')
    fps = reader.get_meta_data()['fps'] // 2

    out_vid_path = "chase1Person1View3Point0_out.mp4"
    writer = imageio.get_writer(out_vid_path, fps=fps)
    print("Writing output video on %s" %out_vid_path)

    frame_cnt = 0
    for test_img in reader:
        frame_cnt += 1
        if frame_cnt % 2 == 0:
            continue
        expanded_img = np.expand_dims(test_img, axis=0)
        detection_list = Obj_Detector.detect_objects_in_np(expanded_img)
        out_img = visualize_results(test_img, detection_list, display=False)
        writer.append_data(out_img)
        
    writer.close()
    

np.random.seed(10)
COLORS = np.random.randint(0, 255, [300, 3])
def visualize_results(img_np, detection_list, display=True):
    import cv2
    score_th = 0.30

    boxes,scores,classes,num_detections = [batched_term[0] for batched_term in detection_list]

    # copy the original image first
    disp_img = np.copy(img_np)
    H, W, C = img_np.shape
    for ii in range(num_detections):
        cur_box, cur_score, cur_class = boxes[ii], scores[ii], classes[ii]
        
        if cur_score < score_th: 
            continue

        top, left, bottom, right = cur_box


        left = int(W * left)
        right = int(W * right)

        top = int(H * top)
        bottom = int(H * bottom)

        conf = cur_score
        #label = bbox['class_str']
        # label = 'Class_%i' % cur_class
        label = obj.OBJECT_STRINGS[cur_class]['name']
        message = label + '%% %.2f' % conf

        color = COLORS[ii]


        cv2.rectangle(disp_img, (left,top), (right,bottom), color, 2)

        font_size =  max(0.5,(right - left)/50.0/float(len(message)))
        cv2.rectangle(disp_img, (left, top-int(font_size*40)), (right,top), color, -1)
        cv2.putText(disp_img, message, (left, top-12), 0, font_size, (255,255,255)-color, 1)

    if display: 
        cv2.imshow('results', disp_img)
        cv2.waitKey(0)
    return disp_img


if __name__ == '__main__':
    test_local_image()

