
import csv
import sys
import cv2
import shutil
import argparse
import pickle


def loadCSV(filename, output_folder, image_height, image_width):
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

    best_crack_candidate = {}

    with open(output_folder+"/"+filename_escaped+".pkl", "wb") as f:

        for element in width_height_x_y:
            #print(element)
            if(element["ratio"] > 3 and element["fillratio"] < 0.6 and float(element["area"]) < maximum_allowed_crackarea):
                print(element)
                shutil.copyfile("images/"+element["id"]+".png", output_folder+"/"+element["id"]+".png")
                #f.write(str(element))
                pickle.dump(element,f)
        f.close()

if __name__ == '__main__':

    #if(len(sys.argv) < 2):
    #    print("Usage: script image_folder_with_csv_file/ output_folder")
    #    exit(1)

    parser = argparse.ArgumentParser(description='Process some integers.')

    parser.add_argument('--image_folder', help='folder of the images')
    parser.add_argument('--output_folder', help='folder for the result (crack length)')
    args = parser.parse_args()

    image_folder = args.image_folder
    output_folder = args.output_folder

    file = image_folder+"/metadata.csv"
    #image_height = sys.argv[2]

    im = cv2.imread(image_folder+'/0.png')
    h, w, c = im.shape
    image_height = h
    loadCSV(file,output_folder,image_height,w)
