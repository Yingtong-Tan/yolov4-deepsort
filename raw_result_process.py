import pandas as pd
import os
from absl import app, flags, logging
from absl.flags import FLAGS
from xml.etree import ElementTree as ET

flags.DEFINE_string('raw_csv', './outputs/raw_result.csv', 'path to output raw csv result')
flags.DEFINE_string('processed_csv', './outputs/processed_result.csv', 'path to output processed csv result')
flags.DEFINE_string('processed_xml', './outputs/processed_result.xml', 'path to output processed xml result')

def main(_argv):

    if os.path.exists(FLAGS.raw_csv):
        # read raw csv file
        raw_csv_data = pd.read_csv(FLAGS.raw_csv)
        print("total rows: ", raw_csv_data.shape[0], "total columns: ", raw_csv_data.shape[1])

        # convert to dataframe
        raw_csv_df = pd.DataFrame(raw_csv_data)
        raw_csv_df.sort_values(by = ['object_id', 'frame_id'], inplace = True)

        # calculate width and height
        raw_csv_df['width'] = raw_csv_df.xmax - raw_csv_df.xmin
        raw_csv_df['height'] = raw_csv_df.ymax - raw_csv_df.ymin

        # create xml
        root = ET.Element('vehicles')
        iter_index = 0
        for object_id, group_by_object_id in raw_csv_df.groupby("object_id"):
            length_of_group = len(group_by_object_id)
            sub1 = ET.SubElement(root, 'vehicle', {'vehicle_id': str(object_id),
                                                   'vehicle_type': str(group_by_object_id.iloc[0].class_name),
                                                   'vehicle_width': '0',
                                                   'start_frame_index': str(group_by_object_id.iloc[0].frame_id),
                                                   'end_frame_index': str(group_by_object_id.iloc[-1].frame_id),
                                                   'vehicle_index': str(iter_index),
                                                   'number_of_annotated_frames': str(length_of_group)})
            iter_index = iter_index + 1
            sub2 = ET.SubElement(sub1, 'frames')
            for i in range(length_of_group):
                sub3 = ET.SubElement(sub2, 'frame', {'frame_index': str(group_by_object_id.iloc[i].frame_id - 1),
                                                     'x_top_left': str(group_by_object_id.iloc[i].xmin),
                                                     'y_top_left': str(group_by_object_id.iloc[i].ymin),
                                                     'width': str(group_by_object_id.iloc[i].width),
                                                     'height': str(group_by_object_id.iloc[i].height),
                                                     'following_vehicle_id': '0',
                                                     'lane_index': '0'})

        # write xml file
        print(ET.dump(root))
        xml_string = ET.tostring(root)
        from xml.dom import minidom
        dom = minidom.parseString(xml_string)
        with open(FLAGS.processed_xml, 'w', encoding='utf-8') as f:
            dom.writexml(f, addindent='\t', newl='\n', encoding='utf-8')

        # write csv file
        raw_csv_df.to_csv(FLAGS.processed_csv, index = False, header = True)


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
