
import csv
import sys
import cv2
import shutil
import argparse
import pickle


def getScore(dict_element,image_height,image_width):
    score = 0
    score_height = image_height / (image_height + int(dict_element["height"])) * dict_element["ratio"] #smaller cracks are better
    score_center = score - abs((int(dict_element["y"]) + float(dict_element["height"])/2) - (image_height/2)) #cracks which are closer to the middle are better
    score_fillrate = score + dict_element["ratio"]*(image_height*image_width / (image_height*image_width/10) / int(dict_element["area"])) # smaller cracks with high x to y ration are long and good

    score = score_center + score_height + dict_element["ratio"] + (score_fillrate / abs(score_fillrate / score_center + score_height))
    return score


def loadCSV(filename, output_folder, image_height, image_width,fileid=""):
    # Use a breakpoint in the code line below to debug your script.
    width_row = 0.0
    height_row = 0.0
    image_number_of_pixels = image_width*image_height
    maximum_allowed_crackarea = image_number_of_pixels * 0.4

    namedict = {}
    width_height_x_y = []
    with open(filename, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        counter = 0
        for row in csvreader:
            if(counter == 0):
                localcounter = 0
                for element in row:
                    namedict[localcounter] = element
                    localcounter = localcounter+1

            else:
                localcounter = 0
                localdict = {}
                for element in row:
                    column_name = namedict[localcounter]
                    localcounter  = localcounter+1
                    if(column_name == "bbox_x0"):
                        localdict["x"] = element
                    elif(column_name == "bbox_y0"):
                        localdict["y"] = element
                    elif(column_name == "bbox_w"):
                        localdict["width"] = element
                    elif(column_name == "bbox_h"):
                        localdict["height"] = element
                    elif(column_name == "area"):
                        localdict["area"] = element
                    elif(column_name == "id"):
                        localdict["id"] = element
                localdict["ratio"] = float(localdict["width"]) / float(localdict["height"])
                localdict["fillratio"] = float(localdict["height"]) / float(image_height)

                width_height_x_y.append(localdict)

            counter = counter+1

    filename_escaped = filename.replace("/", "_")
    filename_escaped = filename_escaped.replace("\\", "_")
    #f = open(output_folder+"/"+filename_escaped+".pkl", "wb")

    #print(localdict)

    best_score = 0
    best_id = -1
    best_element = {}

    for element in width_height_x_y:
        if (element["ratio"] > 3 and element["fillratio"] < 0.6 and float(element["area"]) < maximum_allowed_crackarea):
            score = getScore(element,image_height,image_width)
            #print(str(element) + ": "+ str(score))
            if(score > best_score):
                best_score = score
                best_id = element["id"]

        for element in width_height_x_y:
            if(element["id"] == best_id):
                best_element = element

    if not best_element:
        print("There is no best element in metadata file. Skipping the file " + filename)
        return

    with open(output_folder+"/"+filename_escaped+fileid+".pkl", "wb") as f:
        print(best_element)
        shutil.copyfile("images/"+best_element["id"]+".png", output_folder+"/"+best_element["id"]+fileid+".png")
        pickle.dump(best_element,f)
        f.close()

if __name__ == '__main__':

    #if(len(sys.argv) < 2):
    #    print("Usage: script image_folder_with_csv_file/ output_folder")
    #    exit(1)

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--image_folder', help='folder of the images', required=True)
    parser.add_argument('--output_folder', help='folder for the result (crack length)', required=True)
    parser.add_argument('--id', help='id to append to the filename', required=False)
    args = parser.parse_args()

    image_folder = args.image_folder
    output_folder = args.output_folder

    fileid = ""

    if(args.id is not None):
        fileid = "_" + str(args.id)

    file = image_folder+"/metadata.csv"
    #image_height = sys.argv[2]

    im = cv2.imread(image_folder+'/0.png')
    h, w, c = im.shape
    image_height = h

    print("loadCSV("+file+","+output_folder+","+str(image_height)+","+str(w)+", " + fileid+")")

    loadCSV(file,output_folder,image_height,w, fileid)
